"""
Basic tests for Levox core functionality.
"""

import pytest
from pathlib import Path
import tempfile
import os

from levox.core.config import Config, load_default_config
from levox.core.engine import DetectionEngine
from levox.detection.regex_engine import RegexEngine
from levox.models.detection_result import DetectionResult, FileResult, DetectionMatch
from levox.core.config import DetectionPattern, RiskLevel


class TestConfig:
    """Test configuration management."""
    
    def test_load_default_config(self):
        """Test loading default configuration."""
        config = load_default_config()
        assert config is not None
        assert len(config.patterns) > 0
        assert config.license.tier.value == "standard"
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = load_default_config()
        config.validate()  # Should not raise exception
    
    def test_license_features(self):
        """Test license feature gates."""
        config = load_default_config()
        
        # Standard features should be enabled
        assert config.is_feature_enabled("regex_detection")
        assert config.is_feature_enabled("file_scanning")
        
        # Premium features should be disabled
        assert not config.is_feature_enabled("ast_analysis")
        assert not config.is_feature_enabled("ml_filtering")


class TestRegexEngine:
    """Test regex detection engine."""
    
    def test_regex_engine_initialization(self):
        """Test regex engine initialization."""
        config = load_default_config()
        engine = RegexEngine(config.patterns)
        assert engine is not None
        assert len(engine.compiled_patterns) > 0
    
    def test_pattern_validation(self):
        """Test regex pattern validation."""
        config = load_default_config()
        engine = RegexEngine(config.patterns)
        errors = engine.validate_patterns()
        assert len(errors) == 0  # All patterns should be valid
    
    def test_credit_card_detection(self):
        """Test credit card detection."""
        config = load_default_config()
        engine = RegexEngine(config.patterns)
        
        # Test with valid credit card number
        content = "card_number = '4111111111111111'"
        matches = engine.scan_content(content)
        
        # Should find at least one match
        assert len(matches) > 0
        
        # Check if it's a credit card match
        credit_card_matches = [m for m in matches if m.pattern_name == "credit_card"]
        assert len(credit_card_matches) > 0
    
    def test_email_detection(self):
        """Test email detection."""
        config = load_default_config()
        engine = RegexEngine(config.patterns)
        
        # Test with valid email
        content = "user_email = 'test@example.com'"
        matches = engine.scan_content(content)
        
        # Should find at least one match
        assert len(matches) > 0
        
        # Check if it's an email match
        email_matches = [m for m in matches if m.pattern_name == "email"]
        assert len(email_matches) > 0


class TestDetectionEngine:
    """Test main detection engine."""
    
    def test_engine_initialization(self):
        """Test detection engine initialization."""
        config = load_default_config()
        engine = DetectionEngine(config)
        assert engine is not None
    
    def test_engine_status(self):
        """Test engine status reporting."""
        config = load_default_config()
        engine = DetectionEngine(config)
        status = engine.get_engine_status()
        
        assert status['regex_engine']['enabled'] is True
        assert status['ast_analyzer']['enabled'] is False  # Standard license
        assert status['dataflow_analyzer']['enabled'] is False  # Standard license
        assert status['ml_filter']['enabled'] is False  # Standard license


class TestDataModels:
    """Test data model classes."""
    
    def test_detection_match_creation(self):
        """Test DetectionMatch creation."""
        match = DetectionMatch(
            pattern_name="test_pattern",
            pattern_regex=r"\d+",
            matched_text="123",
            line_number=1,
            column_start=1,
            column_end=4,
            confidence=0.8,
            risk_level=RiskLevel.MEDIUM
        )
        
        assert match.pattern_name == "test_pattern"
        assert match.confidence == 0.8
        assert match.risk_level == RiskLevel.MEDIUM
    
    def test_file_result_creation(self):
        """Test FileResult creation."""
        file_result = FileResult(
            file_path=Path("test.py"),
            file_size=100,
            language="python",
            total_lines=10,
            scan_time=0.1
        )
        
        assert file_result.file_path == Path("test.py")
        assert file_result.language == "python"
        assert file_result.match_count == 0
    
    def test_detection_result_creation(self):
        """Test DetectionResult creation."""
        result = DetectionResult(
            scan_id="test-123",
            scan_duration=1.0,
            license_tier="standard",
            files_scanned=0,
            files_with_matches=0,
            total_matches=0,
            total_scan_time=0.0,
            average_file_time=0.0,
            memory_peak_mb=0.0,
            false_positive_rate=0.0,
            confidence_average=0.0
        )
        
        assert result.scan_id == "test-123"
        assert result.license_tier == "standard"


class TestIntegration:
    """Test integration scenarios."""
    
    def test_simple_scan(self):
        """Test a simple file scan."""
        config = load_default_config()
        engine = DetectionEngine(config)
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
# Test file with PII
credit_card = "4111111111111111"
user_email = "john.doe@example.com"
phone_number = "555-123-4567"
            """)
            temp_file = f.name
        
        try:
            # Scan the file
            file_result = engine.scan_file(temp_file)
            
            # Should find some matches
            assert file_result.match_count > 0
            
            # Check for specific patterns
            pattern_names = [m.pattern_name for m in file_result.matches]
            assert "credit_card" in pattern_names
            assert "email" in pattern_names
            
        finally:
            # Clean up
            os.unlink(temp_file)


class TestCLI:
    """Test CLI functionality."""
    
    def test_cli_initialization(self):
        """Test CLI initialization."""
        from levox.cli import LevoxCLI
        
        cli = LevoxCLI()
        assert cli is not None
        assert cli.last_scan_results is None
        assert cli.last_scan_path is None
    
    def test_cli_scan_results_storage(self):
        """Test that CLI stores scan results for reporting."""
        from levox.cli import LevoxCLI
        from levox.models.detection_result import DetectionResult, FileResult, DetectionMatch
        from levox.core.config import RiskLevel
        
        cli = LevoxCLI()
        
        # Create mock scan results
        mock_match = DetectionMatch(
            file="test.py",
            line=10,
            engine="regex",
            rule_id="test_rule",
            severity="HIGH",
            confidence=0.8,
            snippet="test = 'sensitive_data'",
            description="Test detection",
            pattern_name="test_pattern",
            matched_text="sensitive_data",
            risk_level=RiskLevel.HIGH
        )
        
        mock_file_result = FileResult(
            file_path=Path("test.py"),
            file_size=100,
            language="python",
            total_lines=20,
            scan_time=0.1,
            matches=[mock_match]
        )
        
        mock_scan_result = DetectionResult(
            scan_id="test_scan",
            scan_duration=0.1,
            license_tier="enterprise",
            scan_path="/test/path",
            files_scanned=1,
            files_with_matches=1,
            total_matches=1,
            total_scan_time=0.1,
            average_file_time=0.1,
            memory_peak_mb=10.0,
            false_positive_rate=0.0,
            confidence_average=0.8,
            file_results=[mock_file_result]
        )
        
        # Simulate storing scan results
        cli.last_scan_results = mock_scan_result
        cli.last_scan_path = "/test/path"
        cli.last_scan_time = 0.1
        cli.last_license_tier = "enterprise"
        
        assert cli.last_scan_results is not None
        assert cli.last_scan_path == "/test/path"
        assert cli.last_scan_time == 0.1
        assert cli.last_license_tier == "enterprise"
    
    def test_cli_report_generation(self):
        """Test CLI report generation functionality."""
        from levox.cli import LevoxCLI
        from levox.models.detection_result import DetectionResult, FileResult, DetectionMatch
        from levox.core.config import RiskLevel
        
        cli = LevoxCLI()
        
        # Create mock scan results
        mock_match = DetectionMatch(
            file="test.py",
            line=10,
            engine="regex",
            rule_id="test_rule",
            severity="HIGH",
            confidence=0.8,
            snippet="test = 'sensitive_data'",
            description="Test detection",
            pattern_name="test_pattern",
            matched_text="sensitive_data",
            risk_level=RiskLevel.HIGH
        )
        
        mock_file_result = FileResult(
            file_path=Path("test.py"),
            file_size=100,
            language="python",
            total_lines=20,
            scan_time=0.1,
            matches=[mock_match]
        )
        
        mock_scan_result = DetectionResult(
            scan_id="test_scan",
            scan_duration=0.1,
            license_tier="enterprise",
            scan_path="/test/path",
            files_scanned=1,
            files_with_matches=1,
            total_matches=1,
            total_scan_time=0.1,
            average_file_time=0.1,
            memory_peak_mb=10.0,
            false_positive_rate=0.0,
            confidence_average=0.8,
            file_results=[mock_file_result]
        )
        
        # Store scan results
        cli.last_scan_results = mock_scan_result
        cli.last_scan_path = "/test/path"
        cli.last_scan_time = 0.1
        cli.last_license_tier = "enterprise"
        
        # Test report generation
        reports = cli.generate_reports(['json'], output_dir=None)
        assert 'json' in reports
        assert len(reports['json']) > 0
        
        # Test with output directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            saved_reports = cli.generate_reports(['json'], output_dir=temp_dir)
            assert 'json' in saved_reports
            assert Path(saved_reports['json']).exists()
    
    def test_cli_no_scan_results(self):
        """Test CLI behavior when no scan results are available."""
        from levox.cli import LevoxCLI
        
        cli = LevoxCLI()
        
        # Test report generation without scan results
        reports = cli.generate_reports(['json'])
        assert reports == {}
    
    def test_detection_result_file_operations(self):
        """Test DetectionResult file save/load operations."""
        from levox.models.detection_result import DetectionResult, FileResult, DetectionMatch
        from levox.core.config import RiskLevel
        import tempfile
        import os
        
        # Create mock detection result
        mock_match = DetectionMatch(
            file="test.py",
            line=10,
            engine="regex",
            rule_id="test_rule",
            severity="HIGH",
            confidence=0.8,
            snippet="test = 'sensitive_data'",
            description="Test detection",
            pattern_name="test_pattern",
            matched_text="sensitive_data",
            risk_level=RiskLevel.HIGH
        )
        
        mock_file_result = FileResult(
            file_path=Path("test.py"),
            file_size=100,
            language="python",
            total_lines=20,
            scan_time=0.1,
            matches=[mock_match]
        )
        
        original_result = DetectionResult(
            scan_id="test_scan",
            scan_duration=0.1,
            license_tier="enterprise",
            scan_path="/test/path",
            files_scanned=1,
            files_with_matches=1,
            total_matches=1,
            total_scan_time=0.1,
            average_file_time=0.1,
            memory_peak_mb=10.0,
            false_positive_rate=0.0,
            confidence_average=0.8,
            file_results=[mock_file_result]
        )
        
        # Test save and load
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Save to file
            original_result.save_to_file(temp_file)
            assert os.path.exists(temp_file)
            
            # Load from file
            loaded_result = DetectionResult.from_file(temp_file)
            
            # Verify key attributes are preserved
            assert loaded_result.scan_id == original_result.scan_id
            assert loaded_result.license_tier == original_result.license_tier
            assert loaded_result.scan_path == original_result.scan_path
            assert loaded_result.total_matches == original_result.total_matches
            assert len(loaded_result.file_results) == len(original_result.file_results)
            
            # Verify file result details
            loaded_file_result = loaded_result.file_results[0]
            original_file_result = original_result.file_results[0]
            assert str(loaded_file_result.file_path) == str(original_file_result.file_path)
            assert loaded_file_result.language == original_file_result.language
            assert loaded_file_result.total_lines == original_file_result.total_lines
            
            # Verify match details
            loaded_match = loaded_file_result.matches[0]
            original_match = original_file_result.matches[0]
            assert loaded_match.file == original_match.file
            assert loaded_match.line == original_match.line
            assert loaded_match.engine == original_match.engine
            assert loaded_match.severity == original_match.severity
            assert loaded_match.confidence == original_match.confidence
            assert loaded_match.pattern_name == original_match.pattern_name
            assert loaded_match.matched_text == original_match.matched_text
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__])
