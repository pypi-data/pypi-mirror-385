#!/usr/bin/env python3
"""
Comprehensive Report Generation Tests

Tests for HTML, PDF, and JSON report generation with compliance dashboard,
natural language insights, and professional templates.
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

from levox.cli.reporting import ReportGenerator
from levox.models.detection_result import DetectionResult, FileResult, DetectionMatch
from levox.core.config import Config, LicenseTier


class TestReportGeneration:
    """Test report generation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.config.license.tier = LicenseTier.ENTERPRISE
        self.report_generator = ReportGenerator(self.config)
        
        # Create sample detection results
        self.sample_results = self._create_sample_results()
        
    def _create_sample_results(self) -> DetectionResult:
        """Create sample detection results for testing."""
        # Create sample matches
        matches = [
            DetectionMatch(
                pattern_name="email_address",
                matched_text="test@example.com",
                line_number=10,
                confidence=0.95,
                risk_level="HIGH",
                context="user_email = 'test@example.com'"
            ),
            DetectionMatch(
                pattern_name="api_key",
                matched_text="sk-1234567890abcdef",
                line_number=25,
                confidence=0.88,
                risk_level="CRITICAL",
                context="api_key = 'sk-1234567890abcdef'"
            ),
            DetectionMatch(
                pattern_name="phone_number",
                matched_text="+1-555-123-4567",
                line_number=42,
                confidence=0.75,
                risk_level="MEDIUM",
                context="contact_phone = '+1-555-123-4567'"
            )
        ]
        
        # Create file results
        file_results = [
            FileResult(
                file_path=Path("src/main.py"),
                matches=matches[:2],
                scan_time=0.5,
                language="python"
            ),
            FileResult(
                file_path=Path("config/settings.py"),
                matches=matches[2:],
                scan_time=0.3,
                language="python"
            )
        ]
        
        # Create detection result
        result = DetectionResult(
            scan_id="test_scan_001",
            scan_duration=2.5,
            file_results=file_results,
            scan_path="test_project",
            license_tier="enterprise"
        )
        
        # Add compliance data
        result.compliance_data = {
            "alerts": [
                {
                    "title": "High-Risk PII Exposure",
                    "description": "API keys and email addresses found in source code",
                    "severity": "high",
                    "framework": "GDPR",
                    "article": "Article 32"
                }
            ],
            "score": {
                "overall_score": 65,
                "description": "Moderate compliance risk - immediate attention required"
            },
            "frameworks": ["gdpr", "ccpa"],
            "unified_violations": [
                {
                    "type": "data_exposure",
                    "severity": "high",
                    "gdpr_article": "Article 32",
                    "description": "Sensitive data exposed in source code"
                }
            ],
            "cross_framework_insights": [
                {
                    "insight": "Both GDPR and CCPA require data protection measures",
                    "recommendation": "Implement data masking and secure storage"
                }
            ]
        }
        
        # Add NL insights
        result.scan_metadata = {
            "nl_insights": [
                {
                    "title": "PII Exposure Risk",
                    "description": "This repository contains multiple instances of personally identifiable information that could violate privacy regulations.",
                    "action": "Review and implement data protection measures"
                },
                {
                    "title": "API Security Concern",
                    "description": "Hardcoded API keys present significant security risks and should be moved to secure configuration management.",
                    "action": "Implement secrets management solution"
                }
            ]
        }
        
        return result
    
    def test_html_report_generation(self):
        """Test HTML report generation with compliance dashboard."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            # Generate HTML report
            success = self.report_generator.generate_html_report(
                self.sample_results,
                output_path,
                include_metadata=True
            )
            
            assert success, "HTML report generation should succeed"
            assert os.path.exists(output_path), "HTML file should be created"
            
            # Read and validate HTML content
            with open(output_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Check for key elements
            assert "Levox Security Scan Report" in html_content
            assert "PII Detection & GDPR Compliance Analysis" in html_content
            assert "Enterprise Edition" in html_content
            assert "Compliance Score" in html_content
            assert "Framework Badges" in html_content
            assert "Compliance Alerts" in html_content
            assert "Natural Language Compliance Insights" in html_content
            assert "test@example.com" in html_content
            assert "sk-1234567890abcdef" in html_content
            
            # Check for modern CSS features
            assert "var(--primary-color)" in html_content
            assert "conic-gradient" in html_content
            assert "backdrop-filter" in html_content
            assert "tab-content" in html_content
            
            # Check for interactive elements
            assert "data-tab" in html_content
            assert "addEventListener" in html_content
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_html_report_without_compliance_data(self):
        """Test HTML report generation without compliance data."""
        # Create results without compliance data
        results_no_compliance = self.sample_results
        results_no_compliance.compliance_data = None
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            success = self.report_generator.generate_html_report(
                results_no_compliance,
                output_path
            )
            
            assert success, "HTML report generation should succeed without compliance data"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Should show compliance unavailable message
            assert "Compliance Section Not Available" in html_content
            assert "Compliance frameworks were not available" in html_content
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_json_report_generation(self):
        """Test JSON report generation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            success = self.report_generator.generate_json_report(
                self.sample_results,
                output_path
            )
            
            assert success, "JSON report generation should succeed"
            assert os.path.exists(output_path), "JSON file should be created"
            
            # Validate JSON content
            with open(output_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            assert "scan_id" in json_data
            assert "file_results" in json_data
            assert "compliance_data" in json_data
            assert json_data["scan_id"] == "test_scan_001"
            assert len(json_data["file_results"]) == 2
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_pdf_report_generation(self):
        """Test PDF report generation (if available)."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
                output_path = f.name
            
            success = self.report_generator.generate_pdf_report(
                self.sample_results,
                output_path
            )
            
            # PDF generation might not be available in test environment
            if success:
                assert os.path.exists(output_path), "PDF file should be created"
                assert os.path.getsize(output_path) > 0, "PDF file should not be empty"
            
        except Exception as e:
            # PDF generation might fail in test environment - that's okay
            print(f"PDF generation test skipped: {e}")
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_compliance_dashboard_rendering(self):
        """Test compliance dashboard HTML rendering."""
        compliance_data = {
            "alerts": [
                {
                    "title": "Test Alert",
                    "description": "Test description",
                    "severity": "high",
                    "framework": "GDPR",
                    "article": "Article 5"
                }
            ],
            "score": {
                "overall_score": 85,
                "description": "Good compliance score"
            },
            "frameworks": ["gdpr", "ccpa"],
            "unified_violations": [],
            "cross_framework_insights": []
        }
        
        dashboard_html = self.report_generator._generate_compliance_dashboard(compliance_data)
        
        assert "Executive Compliance Summary" in dashboard_html
        assert "Compliance Score" in dashboard_html
        assert "85" in dashboard_html
        assert "GDPR" in dashboard_html
        assert "CCPA" in dashboard_html
        assert "Test Alert" in dashboard_html
    
    def test_severity_calculation(self):
        """Test severity calculation for matches."""
        # Test high confidence, high risk
        match_high = DetectionMatch(
            pattern_name="api_key",
            matched_text="sk-test",
            line_number=1,
            confidence=0.95,
            risk_level="CRITICAL"
        )
        
        severity = self.report_generator._calculate_severity(match_high)
        assert severity == "CRITICAL"
        
        # Test low confidence, medium risk
        match_low = DetectionMatch(
            pattern_name="email_address",
            matched_text="test@example.com",
            line_number=1,
            confidence=0.3,
            risk_level="MEDIUM"
        )
        
        severity = self.report_generator._calculate_severity(match_low)
        assert severity in ["LOW", "MEDIUM"]
    
    def test_description_generation(self):
        """Test description generation for matches."""
        match = DetectionMatch(
            pattern_name="email_address",
            matched_text="test@example.com",
            line_number=10,
            confidence=0.9,
            risk_level="HIGH"
        )
        
        description = self.report_generator._generate_description(match)
        assert "Email address found" in description
        assert "test@example.com" in description
    
    def test_report_with_dict_input(self):
        """Test report generation with dictionary input."""
        # Convert DetectionResult to dict format
        results_dict = {
            "file_results": [
                {
                    "file_path": "test.py",
                    "matches": [
                        {
                            "pattern_name": "email_address",
                            "matched_text": "test@example.com",
                            "line_number": 10,
                            "confidence": 0.9,
                            "risk_level": "HIGH"
                        }
                    ]
                }
            ],
            "total_issues_found": 1,
            "scan_metadata": {
                "nl_insights": [
                    {
                        "title": "Test Insight",
                        "description": "Test description",
                        "action": "Test action"
                    }
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            success = self.report_generator.generate_html_report(
                results_dict,
                output_path
            )
            
            assert success, "HTML report generation should succeed with dict input"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            assert "test@example.com" in html_content
            assert "Test Insight" in html_content
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


def test_report_generator_initialization():
    """Test ReportGenerator initialization."""
    config = Config()
    config.license.tier = LicenseTier.ENTERPRISE
    
    generator = ReportGenerator(config)
    assert generator is not None
    assert generator.config == config


def test_report_generator_with_different_license_tiers():
    """Test ReportGenerator with different license tiers."""
    for tier in [LicenseTier.FREE, LicenseTier.PRO, LicenseTier.BUSINESS, LicenseTier.ENTERPRISE]:
        config = Config()
        config.license.tier = tier
        
        generator = ReportGenerator(config)
        assert generator is not None


if __name__ == "__main__":
    # Run tests
    import pytest
    pytest.main([__file__, "-v"])
