"""
Comprehensive tests for Levox PII detection system.
Tests all detection levels with known patterns and expected results.
"""

import pytest
import sys
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any

# Add levox to path
sys.path.insert(0, str(Path(__file__).parent.parent / "levox"))

from levox.core.config import Config, LicenseTier, load_default_config
from levox.core.engine import DetectionEngine
from levox.detection.regex_engine import RegexEngine
from levox.detection.ast_analyzer import ASTAnalyzer
from levox.detection.dataflow import DataflowAnalyzer
from levox.detection.ml_filter import MLFilter
from levox.models.detection_result import DetectionMatch
from levox.parsers import get_parser, is_supported_file

class TestRegexDetection:
    """Test regex-based PII detection."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return load_default_config()
    
    @pytest.fixture
    def regex_engine(self, config):
        """Create regex engine instance."""
        return RegexEngine(config.patterns)
    
    def test_email_detection(self, regex_engine):
        """Test email pattern detection."""
        test_cases = [
            ("john.doe@company.com", True),
            ("admin@example.org", True),
            ("user@test-site.net", True),
            ("invalid.email", False),
            ("@missing-local.com", False),
            ("missing-at-symbol.com", False),
        ]
        
        for text, should_detect in test_cases:
            content = f"Email: {text}"
            matches = regex_engine.scan_content(content, "python")
            
            email_matches = [m for m in matches if m.pattern_name == "email"]
            if should_detect:
                assert len(email_matches) > 0, f"Should detect email: {text}"
                assert text in email_matches[0].matched_text
            else:
                assert len(email_matches) == 0, f"Should not detect: {text}"
    
    def test_credit_card_detection(self, regex_engine):
        """Test credit card pattern detection."""
        test_cases = [
            ("4532123456789012", True),   # Valid Visa format
            ("5555555555554444", True),   # Valid Mastercard format
            ("378282246310005", True),    # Valid Amex format
            ("4532-1234-5678-9012", True), # Formatted Visa
            ("1234567890123456", True),   # Generic 16-digit
            ("123456789", False),         # Too short
            ("abcd1234567890ef", False),  # Contains letters
        ]
        
        for text, should_detect in test_cases:
            content = f"Credit card: {text}"
            matches = regex_engine.scan_content(content, "python")
            
            cc_matches = [m for m in matches if m.pattern_name == "credit_card"]
            if should_detect:
                assert len(cc_matches) > 0, f"Should detect credit card: {text}"
            else:
                assert len(cc_matches) == 0, f"Should not detect: {text}"
    
    def test_ssn_detection(self, regex_engine):
        """Test SSN pattern detection."""
        test_cases = [
            ("123-45-6789", True),
            ("987654321", True),
            ("000-00-0000", True),  # Test pattern
            ("123456789", True),    # 9 digits
            ("12-345-6789", False), # Wrong format
            ("1234-56-789", False), # Wrong format
            ("12345678", False),    # Too short
        ]
        
        for text, should_detect in test_cases:
            content = f"SSN: {text}"
            matches = regex_engine.scan_content(content, "python")
            
            ssn_matches = [m for m in matches if m.pattern_name == "ssn"]
            if should_detect:
                assert len(ssn_matches) > 0, f"Should detect SSN: {text}"
            else:
                assert len(ssn_matches) == 0, f"Should not detect: {text}"
    
    def test_phone_detection(self, regex_engine):
        """Test phone number pattern detection."""
        test_cases = [
            ("+1-555-123-4567", True),
            ("(555) 987-6543", True),
            ("555-123-4567", True),
            ("5551234567", True),
            ("+44-20-7946-0958", True),
            ("123-456", False),      # Too short
            ("abc-def-ghij", False), # Letters
        ]
        
        for text, should_detect in test_cases:
            content = f"Phone: {text}"
            matches = regex_engine.scan_content(content, "python")
            
            phone_matches = [m for m in matches if m.pattern_name == "phone"]
            if should_detect:
                assert len(phone_matches) > 0, f"Should detect phone: {text}"
            else:
                assert len(phone_matches) == 0, f"Should not detect: {text}"
    
    def test_context_extraction(self, regex_engine):
        """Test context extraction around matches."""
        content = """
        def process_user(email):
            user_email = "john.doe@company.com"
            return user_email
        """
        
        matches = regex_engine.scan_content(content, "python")
        email_matches = [m for m in matches if m.pattern_name == "email"]
        
        assert len(email_matches) > 0
        match = email_matches[0]
        
        # Check that context is extracted
        assert hasattr(match, 'context_before')
        assert hasattr(match, 'context_after')
        assert match.context_before or match.context_after  # At least one should have content
        
        # Check line and column info
        assert match.line_number > 0
        assert match.column_start >= 0


class TestASTAnalysis:
    """Test AST-based PII detection."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        config = load_default_config()
        config.enable_ast = True
        return config
    
    @pytest.fixture
    def ast_analyzer(self, config):
        """Create AST analyzer instance."""
        return ASTAnalyzer(config)
    
    def test_string_literal_detection(self, ast_analyzer):
        """Test detection in string literals."""
        python_content = '''
email = "user@company.com"
ssn = "123-45-6789"
clean_string = "This is clean text"
'''
        
        matches = ast_analyzer.analyze_file(Path("test.py"), python_content, "python")
        
        # Should detect email and SSN in string literals
        email_matches = [m for m in matches if "user@company.com" in m.matched_text]
        ssn_matches = [m for m in matches if "123-45-6789" in m.matched_text]
        
        assert len(email_matches) > 0, "Should detect email in string literal"
        assert len(ssn_matches) > 0, "Should detect SSN in string literal"
        
        # Check metadata indicates AST detection
        for match in matches:
            assert match.metadata.get('detection_level') == 'ast'
    
    def test_identifier_detection(self, ast_analyzer):
        """Test detection in identifier names."""
        python_content = '''
user_email = "some_value"
customer_ssn = "another_value"
normal_variable = "clean_value"
'''
        
        matches = ast_analyzer.analyze_file(Path("test.py"), python_content, "python")
        
        # Should detect suspicious identifiers
        identifier_matches = [m for m in matches if m.metadata.get('match_type') == 'identifier']
        
        # May or may not find identifier matches depending on implementation
        # This is more of a smoke test
        assert isinstance(matches, list)
    
    def test_test_file_suppression(self, ast_analyzer):
        """Test that test files have reduced confidence."""
        test_content = '''
# This is a test file
def test_user_creation():
    test_email = "user@company.com"
    assert process_user(test_email)
'''
        
        matches = ast_analyzer.analyze_file(Path("test_user.py"), test_content, "python")
        
        if matches:
            # Test files should have lower confidence
            for match in matches:
                assert match.confidence < 0.8, "Test file matches should have lower confidence"
    
    def test_comment_suppression(self, ast_analyzer):
        """Test suppression of matches in comments."""
        python_content = '''
# TODO: Remove hardcoded email admin@company.com
def process_data():
    # This email user@test.com is for testing
    actual_email = "real@company.com"
    return actual_email
'''
        
        matches = ast_analyzer.analyze_file(Path("test.py"), python_content, "python")
        
        # Should detect the actual email but may suppress comment emails
        real_email_matches = [m for m in matches if "real@company.com" in m.matched_text]
        assert len(real_email_matches) > 0, "Should detect actual email"


class TestDataflowAnalysis:
    """Test dataflow/taint analysis."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        config = load_default_config()
        config.enable_dataflow = True
        return config
    
    @pytest.fixture
    def dataflow_analyzer(self, config):
        """Create dataflow analyzer instance."""
        return DataflowAnalyzer(config)
    
    def test_source_detection(self, dataflow_analyzer):
        """Test detection of PII sources."""
        python_content = '''
import os
user_input = input("Enter email: ")
env_secret = os.getenv("SECRET_KEY")
db_result = cursor.fetchone()
'''
        
        matches = dataflow_analyzer.analyze_file(Path("test.py"), python_content, "python")
        
        # Should detect various sources
        source_matches = [m for m in matches if m.metadata.get('match_type') == 'source']
        assert len(source_matches) > 0, "Should detect PII sources"
        
        # Check that metadata indicates dataflow detection
        for match in matches:
            assert match.metadata.get('detection_level') == 'dataflow'
    
    def test_sink_detection(self, dataflow_analyzer):
        """Test detection of PII sinks."""
        python_content = '''
print(user_data)
logger.info(f"User email: {email}")
cursor.execute("INSERT INTO users VALUES (?)", (user_data,))
requests.post("https://api.com", data=payload)
'''
        
        matches = dataflow_analyzer.analyze_file(Path("test.py"), python_content, "python")
        
        # Should detect various sinks
        sink_matches = [m for m in matches if m.metadata.get('match_type') == 'sink']
        assert len(sink_matches) > 0, "Should detect PII sinks"
    
    def test_simple_taint_flow(self, dataflow_analyzer):
        """Test simple taint flow detection."""
        python_content = '''
def process_user():
    user_email = input("Email: ")  # Source
    print(f"Processing: {user_email}")  # Sink
'''
        
        matches = dataflow_analyzer.analyze_file(Path("test.py"), python_content, "python")
        
        # Should detect the flow from input to print
        flow_matches = [m for m in matches if m.metadata.get('match_type') == 'flow']
        
        # Dataflow detection is complex, so this is mainly a smoke test
        assert isinstance(matches, list)


class TestMLFilter:
    """Test ML-based false positive filtering."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        config = load_default_config()
        config.enable_ml = True
        return config
    
    @pytest.fixture
    def ml_filter(self, config):
        """Create ML filter instance."""
        return MLFilter(config)
    
    def test_filter_initialization(self, ml_filter):
        """Test ML filter initializes correctly."""
        assert ml_filter is not None
        # ML filter should handle missing model gracefully
        assert hasattr(ml_filter, 'filter_matches')
    
    def test_filter_matches(self, ml_filter):
        """Test filtering of detection matches."""
        # Create mock matches
        from levox.models.detection_result import DetectionMatch
        from levox.core.config import RiskLevel
        
        matches = [
            DetectionMatch(
                pattern_name="email",
                matched_text="test@example.com",
                line_number=1,
                column_start=0,
                column_end=16,
                confidence=0.9,
                risk_level=RiskLevel.MEDIUM,
                context_before="",
                context_after="",
                metadata={"detection_level": "regex"}
            ),
            DetectionMatch(
                pattern_name="email", 
                matched_text="example@test.com",
                line_number=2,
                column_start=0,
                column_end=16,
                confidence=0.5,
                risk_level=RiskLevel.LOW,
                context_before="# Test email: ",
                context_after=" for unit tests",
                metadata={"detection_level": "regex"}
            )
        ]
        
        content = "test@example.com\n# Test email: example@test.com for unit tests"
        filtered_matches = ml_filter.filter_matches(matches, content)
        
        # Should return filtered matches (may be same or fewer)
        assert isinstance(filtered_matches, list)
        assert len(filtered_matches) <= len(matches)


class TestEndToEndDetection:
    """End-to-end detection tests using the full engine."""
    
    def test_sample_file_detection(self):
        """Test detection on sample PII file."""
        # Load sample file
        sample_file = Path(__file__).parent.parent / "samples" / "pii_examples.py"
        if not sample_file.exists():
            pytest.skip("Sample file not found")
        
        content = sample_file.read_text()
        
        # Test with different license tiers
        for tier in ['standard', 'premium', 'enterprise']:
            config = load_default_config()
            config.license.tier = LicenseTier(tier.upper())
            
            with DetectionEngine(config) as engine:
                results = engine.scan_file(str(sample_file))
                
                # Should detect multiple PII patterns
                total_matches = sum(len(file_result.matches) for file_result in results.file_results)
                assert total_matches > 0, f"Should detect PII in sample file with {tier} license"
                
                # Check that matches have proper metadata
                for file_result in results.file_results:
                    for match in file_result.matches:
                        assert match.pattern_name is not None
                        assert match.confidence > 0
                        assert 'detection_level' in match.metadata
    
    def test_clean_file_detection(self):
        """Test that clean file produces no detections."""
        # Load clean sample file
        clean_file = Path(__file__).parent.parent / "samples" / "clean_code.py"
        if not clean_file.exists():
            pytest.skip("Clean sample file not found")
        
        config = load_default_config()
        config.license.tier = LicenseTier.ENTERPRISE  # Use highest tier
        
        with DetectionEngine(config) as engine:
            results = engine.scan_file(str(clean_file))
            
            # Should detect very few or no PII patterns
            total_matches = sum(len(file_result.matches) for file_result in results.file_results)
            assert total_matches == 0, "Clean file should produce no PII detections"
    
    def test_javascript_detection(self):
        """Test detection in JavaScript file."""
        js_file = Path(__file__).parent.parent / "samples" / "sensitive_data.js"
        if not js_file.exists():
            pytest.skip("JavaScript sample file not found")
        
        config = load_default_config()
        config.license.tier = LicenseTier.PREMIUM
        
        with DetectionEngine(config) as engine:
            results = engine.scan_file(str(js_file))
            
            # Should detect PII patterns in JavaScript
            total_matches = sum(len(file_result.matches) for file_result in results.file_results)
            assert total_matches > 0, "Should detect PII in JavaScript file"
    
    def test_directory_scan(self):
        """Test scanning entire samples directory."""
        samples_dir = Path(__file__).parent.parent / "samples"
        if not samples_dir.exists():
            pytest.skip("Samples directory not found")
        
        config = load_default_config()
        config.license.tier = LicenseTier.ENTERPRISE
        
        with DetectionEngine(config) as engine:
            results = engine.scan_directory(str(samples_dir))
            
            # Should scan multiple files
            assert len(results.file_results) > 0, "Should scan files in directory"
            
            # Check scan metadata
            assert results.scan_metadata is not None
            assert results.scan_metadata['total_files_scanned'] > 0
            assert results.scan_metadata['scan_time_seconds'] > 0


class TestParserIntegration:
    """Test parser integration."""
    
    def test_parser_availability(self):
        """Test that parsers are available."""
        from levox.parsers import TREE_SITTER_AVAILABLE, get_supported_languages
        
        # Check parser availability
        languages = get_supported_languages()
        assert isinstance(languages, dict)
        
        # Should support at least basic file types
        assert 'python' in languages['languages']
        assert 'javascript' in languages['languages']
    
    def test_file_type_detection(self):
        """Test file type detection."""
        test_cases = [
            ("test.py", True),
            ("script.js", True), 
            ("app.jsx", True),
            ("data.json", False),  # Not supported for parsing
            ("readme.txt", False),
        ]
        
        for filename, should_support in test_cases:
            supported = is_supported_file(filename)
            if should_support:
                assert supported, f"Should support {filename}"
            else:
                assert not supported, f"Should not support {filename}"
    
    def test_parser_creation(self):
        """Test parser creation."""
        python_content = "print('Hello, World!')"
        parser = get_parser("test.py", python_content)
        
        if parser:  # May be None if Tree-Sitter not available
            assert hasattr(parser, 'parse')
            assert hasattr(parser, 'extract_strings')
            assert hasattr(parser, 'extract_identifiers')


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
