#!/usr/bin/env python3
"""
Compliance Workflow End-to-End Tests

Tests for the complete compliance workflow including:
- Scan with compliance enabled
- Compliance data attachment to results
- Alerts generation
- Score calculation
- Framework analysis (GDPR, CCPA)
- Natural language insights generation
"""

import os
import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add the Levox package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from levox.core.engine import DetectionEngine
from levox.core.config import Config, LicenseTier
from levox.cli.services import ScanService
from levox.compliance.framework_engine import ComplianceFrameworkEngine
from levox.compliance.compliance_alerter import ComplianceAlerter
from levox.compliance.compliance_scoring import ComplianceScorer
from levox.compliance.nl_insights import NLInsightsGenerator


class TestComplianceWorkflow:
    """Test end-to-end compliance workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.config.license.tier = LicenseTier.ENTERPRISE
        
        # Create temporary test files
        self.test_dir = tempfile.mkdtemp()
        self.test_files = self._create_test_files()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_test_files(self) -> List[Path]:
        """Create test files with various PII patterns."""
        test_files = []
        
        # Python file with email and API key
        python_file = Path(self.test_dir) / "main.py"
        python_content = '''
import os

# User configuration
user_email = "john.doe@example.com"
admin_email = "admin@company.com"

# API configuration
api_key = "sk-1234567890abcdef1234567890abcdef"
database_url = "postgresql://user:password@localhost:5432/db"

def send_notification(email, message):
    """Send notification to user."""
    print(f"Sending to {email}: {message}")

if __name__ == "__main__":
    send_notification(user_email, "Welcome!")
'''
        python_file.write_text(python_content)
        test_files.append(python_file)
        
        # JavaScript file with phone number
        js_file = Path(self.test_dir) / "app.js"
        js_content = '''
const config = {
    phoneNumber: "+1-555-123-4567",
    contactEmail: "support@example.com",
    apiEndpoint: "https://api.example.com/v1"
};

function validatePhone(phone) {
    const phoneRegex = /^\\+?[1-9]\\d{1,14}$/;
    return phoneRegex.test(phone);
}

module.exports = { config, validatePhone };
'''
        js_file.write_text(js_content)
        test_files.append(js_file)
        
        # Java file with SSN
        java_file = Path(self.test_dir) / "UserService.java"
        java_content = '''
public class UserService {
    private String userSSN = "123-45-6789";
    private String userEmail = "user@example.com";
    
    public void processUser(String email, String ssn) {
        // Process user data
        System.out.println("Processing user: " + email);
    }
    
    public String getUserSSN() {
        return this.userSSN;
    }
}
'''
        java_file.write_text(java_content)
        test_files.append(java_file)
        
        return test_files
    
    def test_scan_with_compliance_enabled(self):
        """Test scanning with compliance mode enabled."""
        scan_service = ScanService(self.config)
        
        # Configure scan options with compliance enabled
        scan_options = {
            'compliance_mode': True,
            'compliance_frameworks': ['gdpr', 'ccpa'],
            'compliance_alerts': 'detailed',
            'alert_threshold': 'low',
            'executive_summary': True
        }
        
        # Perform scan
        results = scan_service.scan_directory(
            self.test_dir,
            scan_options
        )
        
        # Verify results
        assert results is not None
        assert hasattr(results, 'compliance_data')
        assert results.compliance_data is not None
        
        # Check compliance data structure
        compliance_data = results.compliance_data
        assert 'alerts' in compliance_data
        assert 'score' in compliance_data
        assert 'frameworks' in compliance_data
        assert 'unified_violations' in compliance_data
        
        # Verify frameworks were analyzed
        frameworks = compliance_data['frameworks']
        assert 'gdpr' in frameworks or 'ccpa' in frameworks
        
        # Verify alerts were generated
        alerts = compliance_data['alerts']
        assert len(alerts) > 0
        
        # Verify score was calculated
        score = compliance_data['score']
        assert 'overall_score' in score
        assert isinstance(score['overall_score'], (int, float))
    
    def test_compliance_framework_engine(self):
        """Test compliance framework engine directly."""
        # Create mock detection results
        from levox.models.detection_result import DetectionResult, FileResult, DetectionMatch
        
        matches = [
            DetectionMatch(
                pattern_name="email_address",
                matched_text="test@example.com",
                line_number=10,
                confidence=0.95,
                risk_level="HIGH"
            ),
            DetectionMatch(
                pattern_name="api_key",
                matched_text="sk-test123",
                line_number=20,
                confidence=0.88,
                risk_level="CRITICAL"
            )
        ]
        
        file_result = FileResult(
            file_path=Path("test.py"),
            matches=matches,
            scan_time=0.5,
            language="python"
        )
        
        detection_result = DetectionResult(
            scan_id="test_001",
            scan_duration=1.0,
            file_results=[file_result],
            scan_path="test",
            license_tier="enterprise"
        )
        
        # Test framework engine
        framework_engine = ComplianceFrameworkEngine(self.config)
        compliance_result = framework_engine.analyze_compliance(
            detection_result,
            ['gdpr', 'ccpa']
        )
        
        # Verify compliance result
        assert compliance_result is not None
        assert len(compliance_result.frameworks_analyzed) > 0
        assert len(compliance_result.unified_violations) > 0
        
        # Check for GDPR violations
        gdpr_violations = [v for v in compliance_result.unified_violations 
                          if 'gdpr' in v.get('frameworks', [])]
        assert len(gdpr_violations) > 0
    
    def test_compliance_alerter(self):
        """Test compliance alerter."""
        # Create mock violations
        violations = [
            {
                'type': 'data_exposure',
                'severity': 'high',
                'gdpr_article': 'Article 32',
                'description': 'Sensitive data exposed in source code',
                'frameworks': ['gdpr']
            },
            {
                'type': 'consent_management',
                'severity': 'medium',
                'ccpa_section': 'Section 1798.105',
                'description': 'Missing consent management',
                'frameworks': ['ccpa']
            }
        ]
        
        alerter = ComplianceAlerter(self.config)
        alerts = alerter.generate_alerts(violations)
        
        # Verify alerts
        assert len(alerts) > 0
        
        for alert in alerts:
            assert 'title' in alert
            assert 'description' in alert
            assert 'severity' in alert
            assert 'framework' in alert
    
    def test_compliance_scorer(self):
        """Test compliance scorer."""
        # Create mock violations
        violations = [
            {
                'type': 'data_exposure',
                'severity': 'high',
                'frameworks': ['gdpr']
            },
            {
                'type': 'consent_management',
                'severity': 'medium',
                'frameworks': ['ccpa']
            }
        ]
        
        scorer = ComplianceScorer(self.config)
        score_result = scorer.calculate_compliance_score(violations)
        
        # Verify score result
        assert 'overall_score' in score_result
        assert 'framework_scores' in score_result
        assert 'description' in score_result
        
        # Score should be between 0 and 100
        assert 0 <= score_result['overall_score'] <= 100
    
    def test_nl_insights_generation(self):
        """Test natural language insights generation."""
        # Create mock scan results
        scan_results = {
            'total_matches': 15,
            'severity_distribution': {
                'CRITICAL': 2,
                'HIGH': 5,
                'MEDIUM': 6,
                'LOW': 2
            },
            'file_results': [
                {
                    'file_path': 'src/main.py',
                    'matches': [
                        {
                            'pattern_name': 'email_address',
                            'matched_text': 'test@example.com',
                            'severity': 'HIGH'
                        }
                    ]
                }
            ]
        }
        
        nl_generator = NLInsightsGenerator(self.config)
        insights = nl_generator.generate_insights(scan_results)
        
        # Verify insights
        assert len(insights) > 0
        
        for insight in insights:
            assert 'title' in insight
            assert 'description' in insight
            assert 'action' in insight
    
    def test_compliance_workflow_integration(self):
        """Test complete compliance workflow integration."""
        # Initialize components
        scan_service = ScanService(self.config)
        framework_engine = ComplianceFrameworkEngine(self.config)
        alerter = ComplianceAlerter(self.config)
        scorer = ComplianceScorer(self.config)
        nl_generator = NLInsightsGenerator(self.config)
        
        # Perform scan
        scan_options = {
            'compliance_mode': True,
            'compliance_frameworks': ['gdpr', 'ccpa'],
            'compliance_alerts': 'detailed',
            'alert_threshold': 'low'
        }
        
        results = scan_service.scan_directory(
            self.test_dir,
            scan_options
        )
        
        # Verify compliance data is attached
        assert results.compliance_data is not None
        
        compliance_data = results.compliance_data
        
        # Verify all components worked together
        assert 'alerts' in compliance_data
        assert 'score' in compliance_data
        assert 'frameworks' in compliance_data
        assert 'unified_violations' in compliance_data
        assert 'cross_framework_insights' in compliance_data
        
        # Verify NL insights in scan metadata
        assert results.scan_metadata is not None
        assert 'nl_insights' in results.scan_metadata
        
        nl_insights = results.scan_metadata['nl_insights']
        assert len(nl_insights) > 0
        
        # Verify insights have required fields
        for insight in nl_insights:
            assert 'title' in insight
            assert 'description' in insight
            assert 'action' in insight
    
    def test_compliance_with_different_frameworks(self):
        """Test compliance analysis with different framework combinations."""
        scan_service = ScanService(self.config)
        
        # Test GDPR only
        scan_options_gdpr = {
            'compliance_mode': True,
            'compliance_frameworks': ['gdpr'],
            'compliance_alerts': 'detailed'
        }
        
        results_gdpr = scan_service.scan_directory(
            self.test_dir,
            scan_options_gdpr
        )
        
        assert results_gdpr.compliance_data is not None
        gdpr_frameworks = results_gdpr.compliance_data['frameworks']
        assert 'gdpr' in gdpr_frameworks
        
        # Test CCPA only
        scan_options_ccpa = {
            'compliance_mode': True,
            'compliance_frameworks': ['ccpa'],
            'compliance_alerts': 'detailed'
        }
        
        results_ccpa = scan_service.scan_directory(
            self.test_dir,
            scan_options_ccpa
        )
        
        assert results_ccpa.compliance_data is not None
        ccpa_frameworks = results_ccpa.compliance_data['frameworks']
        assert 'ccpa' in ccpa_frameworks
    
    def test_compliance_error_handling(self):
        """Test compliance error handling."""
        # Test with invalid framework
        scan_service = ScanService(self.config)
        
        scan_options_invalid = {
            'compliance_mode': True,
            'compliance_frameworks': ['invalid_framework'],
            'compliance_alerts': 'detailed'
        }
        
        results = scan_service.scan_directory(
            self.test_dir,
            scan_options_invalid
        )
        
        # Should still complete scan but with error in metadata
        assert results is not None
        
        if results.scan_metadata:
            assert 'compliance_error' in results.scan_metadata or 'compliance_note' in results.scan_metadata


def test_compliance_components_initialization():
    """Test that all compliance components can be initialized."""
    config = Config()
    config.license.tier = LicenseTier.ENTERPRISE
    
    # Test framework engine
    framework_engine = ComplianceFrameworkEngine(config)
    assert framework_engine is not None
    
    # Test alerter
    alerter = ComplianceAlerter(config)
    assert alerter is not None
    
    # Test scorer
    scorer = ComplianceScorer(config)
    assert scorer is not None
    
    # Test NL insights generator
    nl_generator = NLInsightsGenerator(config)
    assert nl_generator is not None


def test_compliance_with_different_license_tiers():
    """Test compliance features with different license tiers."""
    for tier in [LicenseTier.PRO, LicenseTier.BUSINESS, LicenseTier.ENTERPRISE]:
        config = Config()
        config.license.tier = tier
        
        # All these tiers should support compliance
        framework_engine = ComplianceFrameworkEngine(config)
        assert framework_engine is not None


if __name__ == "__main__":
    # Run tests
    import pytest
    pytest.main([__file__, "-v"])
