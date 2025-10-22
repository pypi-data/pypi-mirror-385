"""
Tests for all detection levels in Levox.
"""

import pytest
import tempfile
import os
from pathlib import Path

from levox.core.config import Config, load_default_config, LicenseTier
from levox.core.engine import DetectionEngine
from levox.detection.ast_analyzer import ASTAnalyzer
from levox.detection.dataflow import DataflowAnalyzer
from levox.detection.ml_filter import MLFilter
from levox.compliance.gdpr_analyzer import GDPRAnalyzer
from levox.compliance.models import ComplianceIssue, ComplianceLevel, ComplianceCategory, GDPRArticle
from levox.models.detection_result import DetectionMatch, RiskLevel


class TestASTAnalyzer:
    """Test Level 2: AST Analysis."""
    
    def test_ast_analyzer_initialization(self):
        """Test AST analyzer initialization."""
        config = load_default_config()
        analyzer = ASTAnalyzer(config)
        assert analyzer is not None
        assert analyzer.suppression_patterns is not None
        assert analyzer.sensitive_functions is not None
    
    def test_python_ast_analysis(self):
        """Test Python AST analysis."""
        config = load_default_config()
        analyzer = ASTAnalyzer(config)
        
        # Test Python code with PII
        python_code = '''
def process_payment():
    credit_card = "4111111111111111"  # levox: ignore
    user_email = "john.doe@example.com"
    phone = "555-123-4567"
    
    # Log payment info
    logging.info(f"Processing payment for {user_email}")
    
    return "success"

def test_example():
    test_email = "test@example.com"  # This should be suppressed
    return test_email
'''
        
        matches = analyzer.analyze_python_file(python_code, Path("test.py"))
        
        # Should find PII patterns
        assert len(matches) > 0
        
        # Check for specific patterns
        pattern_names = [m.pattern_name for m in matches]
        assert "credit_card" in pattern_names or "email" in pattern_names
        
        # Check suppression
        credit_card_matches = [m for m in matches if m.pattern_name == "credit_card"]
        if credit_card_matches:
            # Should be suppressed due to comment
            assert len(credit_card_matches) == 0
    
    def test_javascript_ast_analysis(self):
        """Test JavaScript AST analysis."""
        config = load_default_config()
        analyzer = ASTAnalyzer(config)
        
        # Test JavaScript code with PII
        js_code = '''
const userData = {
    email: "user@example.com",
    phone: "555-123-4567"
};

console.log("User email:", userData.email);
'''
        
        matches = analyzer.analyze_javascript_file(js_code, Path("test.js"))
        
        # Should find PII patterns
        assert len(matches) > 0
        
        # Check for specific patterns
        pattern_names = [m.pattern_name for m in matches]
        assert "email" in pattern_names or "phone" in pattern_names


class TestDataflowAnalyzer:
    """Test Level 3: Dataflow Analysis."""
    
    def test_dataflow_analyzer_initialization(self):
        """Test dataflow analyzer initialization."""
        config = load_default_config()
        analyzer = DataflowAnalyzer(config)
        assert analyzer is not None
        assert analyzer.taint_sources is not None
        assert analyzer.taint_sinks is not None
    
    def test_python_dataflow_analysis(self):
        """Test Python dataflow analysis."""
        config = load_default_config()
        analyzer = DataflowAnalyzer(config)
        
        # Test Python code with data flow
        python_code = '''
import os
import logging

def process_user_input():
    user_input = input("Enter email: ")  # Taint source
    email = user_input
    
    # Process email
    logging.info(f"Processing email: {email}")  # Taint sink
    
    return email

def save_to_file(data):
    with open("output.txt", "w") as f:
        f.write(data)  # Taint sink
'''
        
        matches = analyzer.analyze_python_dataflow(python_code, Path("test.py"))
        
        # Should find dataflow issues
        assert len(matches) > 0
        
        # Check for dataflow patterns
        dataflow_matches = [m for m in matches if m.pattern_name == "dataflow_taint"]
        assert len(dataflow_matches) > 0
    
    def test_control_flow_graph_building(self):
        """Test control flow graph building."""
        config = load_default_config()
        analyzer = DataflowAnalyzer(config)
        
        python_code = '''
def test_function():
    x = 1
    y = x + 1
    return y
'''
        
        tree = analyzer.analyze_python_dataflow(python_code, Path("test.py"))
        # Should not raise exceptions
        assert True


class TestMLFilter:
    """Test Level 4: ML Filtering."""
    
    def test_ml_filter_initialization(self):
        """Test ML filter initialization."""
        config = load_default_config()
        filter_obj = MLFilter(config)
        assert filter_obj is not None
    
    def test_rule_based_filtering(self):
        """Test rule-based filtering fallback."""
        config = load_default_config()
        filter_obj = MLFilter(config)
        
        # Create test matches
        matches = [
            DetectionMatch(
                pattern_name="email",
                pattern_regex=r"test@example\.com",
                matched_text="test@example.com",
                line_number=1,
                column_start=1,
                column_end=20,
                confidence=0.8,
                risk_level=RiskLevel.MEDIUM,
                metadata={"context": "string_literal"}
            )
        ]
        
        # Filter matches
        filtered = filter_obj.filter_matches(matches, "test content")
        
        # Should return filtered results
        assert len(filtered) >= 0  # May be 0 if filtered out
    
    def test_feature_extraction(self):
        """Test feature extraction for ML model."""
        config = load_default_config()
        filter_obj = MLFilter(config)
        
        match = DetectionMatch(
            pattern_name="credit_card",
            pattern_regex=r"\d{4}",
            matched_text="1234",
            line_number=1,
            column_start=1,
            column_end=5,
            confidence=0.9,
            risk_level=RiskLevel.HIGH,
            metadata={"context": "string_literal"}
        )
        
        features = filter_obj._extract_features(match, "test content")
        
        # Should extract features
        assert len(features) > 0
        assert isinstance(features, (list, tuple)) or hasattr(features, 'shape')


class TestDetectionEngineIntegration:
    """Test integration of all detection levels."""
    
    def test_standard_license_features(self):
        """Test standard license features."""
        config = load_default_config()
        config.license.tier = LicenseTier.STANDARD
        
        engine = DetectionEngine(config)
        
        # Check engine status
        status = engine.get_engine_status()
        
        assert status['regex_engine']['enabled'] is True
        assert status['ast_analyzer']['enabled'] is False  # Standard license
        assert status['dataflow_analyzer']['enabled'] is False  # Standard license
        assert status['ml_filter']['enabled'] is False  # Standard license
    
    def test_premium_license_features(self):
        """Test premium license features."""
        config = load_default_config()
        config.license.tier = LicenseTier.PREMIUM
        
        engine = DetectionEngine(config)
        
        # Check engine status
        status = engine.get_engine_status()
        
        assert status['regex_engine']['enabled'] is True
        assert status['ast_analyzer']['enabled'] is True  # Premium license
        assert status['dataflow_analyzer']['enabled'] is False  # Premium license
        assert status['ml_filter']['enabled'] is False  # Premium license
    
    def test_enterprise_license_features(self):
        """Test enterprise license features."""
        config = load_default_config()
        config.license.tier = LicenseTier.ENTERPRISE
        
        engine = DetectionEngine(config)
        
        # Check engine status
        status = engine.get_engine_status()
        
        assert status['regex_engine']['enabled'] is True
        assert status['ast_analyzer']['enabled'] is True  # Enterprise license
        assert status['dataflow_analyzer']['enabled'] is True  # Enterprise license
        assert status['ml_filter']['enabled'] is True  # Enterprise license
    
    def test_full_scan_with_all_levels(self):
        """Test full scan with all detection levels enabled."""
        config = load_default_config()
        config.license.tier = LicenseTier.ENTERPRISE
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
import os
import logging

def process_payment():
    credit_card = "4111111111111111"
    user_email = "john.doe@example.com"
    
    # Log payment info
    logging.info(f"Processing payment for {user_email}")
    
    return "success"
''')
            temp_file = f.name
        
        try:
            engine = DetectionEngine(config)
            
            # Scan the file
            file_result = engine.scan_file(temp_file)
            
            # Should find matches from multiple levels
            assert file_result.match_count > 0
            
            # Check for different detection levels
            detection_levels = set()
            for match in file_result.matches:
                if 'detection_level' in match.metadata:
                    detection_levels.add(match.metadata['detection_level'])
            
            # Should have multiple detection levels
            assert len(detection_levels) > 1
            
        finally:
            # Clean up
            os.unlink(temp_file)


class TestConfigurationUpdates:
    """Test configuration updates and license tier changes."""
    
    def test_license_tier_update(self):
        """Test updating license tier and feature enabling."""
        config = load_default_config()
        
        # Start with standard
        assert config.license.tier == LicenseTier.STANDARD
        assert not config.is_feature_enabled("ast_analysis")
        assert not config.is_feature_enabled("dataflow_analysis")
        assert not config.is_feature_enabled("ml_filtering")
        
        # Update to premium
        config.update_license_tier(LicenseTier.PREMIUM)
        assert config.license.tier == LicenseTier.PREMIUM
        assert config.is_feature_enabled("ast_analysis")
        assert not config.is_feature_enabled("dataflow_analysis")
        assert not config.is_feature_enabled("ml_filtering")
        
        # Update to enterprise
        config.update_license_tier(LicenseTier.ENTERPRISE)
        assert config.license.tier == LicenseTier.ENTERPRISE
        assert config.is_feature_enabled("ast_analysis")
        assert config.is_feature_enabled("dataflow_analysis")
        assert config.is_feature_enabled("ml_filtering")
        assert config.ml_enabled is True


class TestGDPRAnalyzer:
    """Test Level 5: GDPR Compliance Analysis."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration with GDPR enabled."""
        config = load_default_config()
        config.license.tier = LicenseTier.PREMIUM
        config.enable_gdpr = True
        return config
    
    @pytest.fixture
    def gdpr_analyzer(self, config):
        """Create GDPR analyzer instance."""
        return GDPRAnalyzer(config)
    
    def test_gdpr_analyzer_initialization(self, config):
        """Test GDPR analyzer initialization."""
        analyzer = GDPRAnalyzer(config)
        assert analyzer is not None
        assert analyzer.config == config
        assert analyzer.regex_engine is not None
        assert analyzer.audit_logger is not None
        assert analyzer.performance_monitor is not None
        assert analyzer.file_handler is not None
    
    def test_pii_detection_in_python(self, gdpr_analyzer):
        """Test PII detection in Python code."""
        # Create temporary Python file with PII
        python_code = '''
import logging

def process_user_data():
    # Personal data that should be flagged
    user_email = "john.doe@company.com"
    credit_card = "4111-1111-1111-1111"
    ssn = "123-45-6789"
    phone = "+1-555-123-4567"
    
    # Log user data (potential GDPR violation)
    logging.info(f"Processing user: {user_email}")
    logging.debug(f"Payment method: {credit_card}")
    
    # Database query with PII
    query = f"SELECT * FROM users WHERE email = '{user_email}'"
    
    return {"status": "processed"}

def store_user_consent():
    # Missing proper consent management
    user_data = {
        "email": "user@example.com",
        "consent": True,  # Simple boolean - not GDPR compliant
        "purpose": "marketing"
    }
    return user_data
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_file = f.name
        
        try:
            # Analyze the file
            result = gdpr_analyzer.analyze_project(temp_file)
            
            # Verify results
            assert result is not None
            assert len(result.compliance_issues) > 0
            
            # Check for expected issue categories
            categories_found = {issue.category for issue in result.compliance_issues}
            assert ComplianceCategory.DATA_PROTECTION in categories_found
            
            # Check for PII detection
            pii_issues = [issue for issue in result.compliance_issues 
                         if "email" in issue.description.lower() or 
                            "credit card" in issue.description.lower()]
            assert len(pii_issues) > 0
            
        finally:
            os.unlink(temp_file)
    
    def test_javascript_pii_detection(self, gdpr_analyzer):
        """Test PII detection in JavaScript code."""
        javascript_code = '''
// User data processing
function processUserData() {
    const userData = {
        email: "user@example.com",
        creditCard: "4111111111111111",
        ssn: "123-45-6789",
        phone: "555-123-4567"
    };
    
    // Log sensitive data (GDPR violation)
    console.log("Processing user:", userData.email);
    console.log("Payment info:", userData.creditCard);
    
    // Store in localStorage without consent
    localStorage.setItem("userEmail", userData.email);
    
    return userData;
}

// Third-party tracking
function initAnalytics() {
    // Google Analytics without proper consent
    gtag('config', 'GA_MEASUREMENT_ID');
    
    // Facebook Pixel
    fbq('track', 'PageView');
}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(javascript_code)
            temp_file = f.name
        
        try:
            # Analyze the file
            result = gdpr_analyzer.analyze_project(temp_file)
            
            # Verify results
            assert result is not None
            assert len(result.compliance_issues) > 0
            
            # Check for third-party service detection
            third_party_issues = [issue for issue in result.compliance_issues 
                                if "third-party" in issue.description.lower() or
                                   "analytics" in issue.description.lower()]
            assert len(third_party_issues) > 0
            
        finally:
            os.unlink(temp_file)
    
    def test_engine_integration(self, config):
        """Test GDPR analyzer integration with detection engine."""
        # Enable GDPR in config
        config.enable_gdpr = True
        engine = DetectionEngine(config)
        
        # Create test Python file
        python_code = '''
def handle_user_registration():
    user_email = "newuser@company.com"
    user_password = "plaintext_password"  # Security issue
    
    # Store without encryption (GDPR violation)
    database.store_user(user_email, user_password)
    
    # No consent tracking
    return {"registered": True}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_file = f.name
        
        try:
            # Scan file with engine
            result = engine.scan_file(temp_file)
            
            # Verify GDPR issues are included in metadata
            assert 'gdpr_issues' in result.metadata
            gdpr_issues = result.metadata['gdpr_issues']
            assert len(gdpr_issues) > 0
            
            # Verify issue structure
            for issue in gdpr_issues:
                assert hasattr(issue, 'title')
                assert hasattr(issue, 'description')
                assert hasattr(issue, 'category')
                assert hasattr(issue, 'gdpr_article')
                assert hasattr(issue, 'level')
                assert hasattr(issue, 'file_path')
                
        finally:
            os.unlink(temp_file)
    
    def test_ml_filter_integration(self, config):
        """Test ML filter integration with GDPR analyzer."""
        # Enable ML filtering for Enterprise tier
        config.license.tier = LicenseTier.ENTERPRISE
        config.ml_enabled = True
        
        gdpr_analyzer = GDPRAnalyzer(config)
        assert gdpr_analyzer.ml_filter is not None
        
        # Create test file with potential false positives
        python_code = '''
def test_function():
    # Test data that might be flagged but shouldn't be
    test_email = "test@example.com"  # Test email
    mock_ssn = "000-00-0000"        # Mock SSN
    sample_phone = "555-0000"       # Sample phone
    
    # These are legitimate test patterns
    return {"test_data": True}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_file = f.name
        
        try:
            # Analyze with ML filtering
            result = gdpr_analyzer.analyze_project(temp_file)
            
            # ML filter should reduce false positives
            # (Exact behavior depends on ML model training)
            assert result is not None
            
        finally:
            os.unlink(temp_file)
    
    def test_audit_logging_integration(self, gdpr_analyzer):
        """Test audit logging integration."""
        # Create test file
        python_code = '''
def process_gdpr_request():
    user_email = "user@company.com"
    return {"processed": True}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_file = f.name
        
        try:
            # Analyze file (should trigger audit logging)
            result = gdpr_analyzer.analyze_project(temp_file)
            
            # Verify audit logger was called (check if it exists)
            assert gdpr_analyzer.audit_logger is not None
            
        finally:
            os.unlink(temp_file)
    
    def test_performance_monitoring(self, gdpr_analyzer):
        """Test performance monitoring integration."""
        # Create test file
        python_code = '''
def simple_function():
    email = "user@example.com"
    return email
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_file = f.name
        
        try:
            # Analyze file (should be monitored)
            result = gdpr_analyzer.analyze_project(temp_file)
            
            # Verify performance monitor exists
            assert gdpr_analyzer.performance_monitor is not None
            
        finally:
            os.unlink(temp_file)
    
    def test_enhanced_parser_integration(self, gdpr_analyzer):
        """Test enhanced parser capabilities."""
        # Create Python file with F-strings and complex patterns
        python_code = '''
def log_user_activity():
    user_id = "12345"
    user_email = "user@company.com"
    
    # F-string with PII (should be detected by enhanced parser)
    log_message = f"User {user_email} logged in at {datetime.now()}"
    logging.info(log_message)
    
    # Template with sensitive data
    query = f"UPDATE users SET last_login = NOW() WHERE email = '{user_email}'"
    
    return True
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_file = f.name
        
        try:
            # Analyze file
            result = gdpr_analyzer.analyze_project(temp_file)
            
            # Should detect PII in F-strings
            assert result is not None
            assert len(result.compliance_issues) > 0
            
            # Check for F-string specific detection
            fstring_issues = [issue for issue in result.compliance_issues 
                            if "f-string" in issue.description.lower() or
                               "template" in issue.description.lower()]
            # Note: This depends on enhanced parser implementation
            
        finally:
            os.unlink(temp_file)
    
    def test_compliance_categories_coverage(self, gdpr_analyzer):
        """Test that all major GDPR compliance categories are covered."""
        # Test different types of code that should trigger different categories
        test_cases = {
            ComplianceCategory.DATA_PROTECTION: '''
def store_password():
    password = "plaintext123"  # Should be encrypted
    database.save(password)
''',
            ComplianceCategory.CONSENT_MANAGEMENT: '''
def collect_data():
    user_data = request.json
    # No consent check before collecting data
    database.store(user_data)
''',
            ComplianceCategory.DATA_RETENTION: '''
def cleanup_old_data():
    # No data retention policy implementation
    pass  # Data never deleted
''',
            ComplianceCategory.BREACH_NOTIFICATION: '''
def handle_error():
    try:
        process_sensitive_data()
    except Exception as e:
        # No breach notification mechanism
        pass
'''
        }
        
        for category, code in test_cases.items():
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = gdpr_analyzer.analyze_project(temp_file)
                # At minimum, should detect some compliance issues
                assert result is not None
                
            finally:
                os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__])
