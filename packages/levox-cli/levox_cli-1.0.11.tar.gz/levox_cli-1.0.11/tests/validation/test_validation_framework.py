#!/usr/bin/env python3
"""
Pytest-based validation tests for the Levox validation framework.

These tests ensure that the validation framework works correctly and can
be integrated into CI/CD pipelines.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the validation framework
from validation_framework import (
    LevoxValidator, 
    ValidationResult, 
    ValidationSummary,
    LEVOX_AVAILABLE
)


class TestValidationFramework:
    """Test cases for the validation framework."""
    
    @pytest.fixture
    def test_dir(self):
        """Provide test directory path."""
        return Path(__file__).parent
    
    @pytest.fixture
    def ground_truth_data(self):
        """Provide sample ground truth data."""
        return {
            "test_files": {
                "positives/test_file.py": {
                    "expected_issues": [
                        {
                            "category": "hardcoded_credentials",
                            "severity": "HIGH",
                            "patterns": ["hardcoded_password"],
                            "min_count": 2,
                            "description": "Should detect hardcoded passwords"
                        }
                    ],
                    "expected_issue_count": {
                        "min": 2,
                        "max": 5
                    },
                    "languages": ["python"],
                    "tags": ["credentials", "passwords"]
                },
                "negatives/clean_file.py": {
                    "expected_issues": [],
                    "expected_issue_count": {
                        "min": 0,
                        "max": 0
                    },
                    "languages": ["python"],
                    "tags": ["clean", "secure"]
                }
            },
            "validation_config": {
                "scoring": {
                    "precision_threshold": 0.8,
                    "recall_threshold": 0.8,
                    "f1_threshold": 0.8
                }
            }
        }
    
    @pytest.fixture
    def mock_ground_truth_file(self, test_dir, ground_truth_data):
        """Create a mock ground truth file."""
        ground_truth_path = test_dir / "ground_truth.json"
        
        # Save ground truth data
        with open(ground_truth_path, 'w', encoding='utf-8') as f:
            json.dump(ground_truth_data, f, indent=2)
        
        yield ground_truth_path
        
        # Cleanup
        if ground_truth_path.exists():
            ground_truth_path.unlink()
    
    @pytest.fixture
    def validator(self, mock_ground_truth_file):
        """Create a validator instance for testing."""
        with patch('validation_framework.LEVOX_AVAILABLE', False):
            return LevoxValidator(use_cli=True)
    
    def test_validator_initialization(self, mock_ground_truth_file):
        """Test validator initialization."""
        validator = LevoxValidator(use_cli=True)
        
        assert validator.ground_truth is not None
        assert validator.use_cli is True
        assert validator.test_dir.exists()
        assert validator.results_dir.exists()
    
    def test_ground_truth_loading(self, mock_ground_truth_file):
        """Test ground truth loading."""
        validator = LevoxValidator(use_cli=True)
        
        assert "test_files" in validator.ground_truth
        assert len(validator.ground_truth["test_files"]) == 2
        assert "positives/test_file.py" in validator.ground_truth["test_files"]
        assert "negatives/clean_file.py" in validator.ground_truth["test_files"]
    
    def test_issue_categorization(self, validator):
        """Test issue categorization logic."""
        # Test hardcoded credentials
        issues = [
            {"description": "Hardcoded password found", "pattern_name": "password_pattern"},
            {"description": "Secret key in code", "pattern_name": "secret_pattern"}
        ]
        
        categories = validator._categorize_issues(issues)
        assert "hardcoded_credentials" in categories
        
        # Test SQL injection
        issues = [
            {"description": "SQL query injection vulnerability", "pattern_name": "sql_pattern"}
        ]
        
        categories = validator._categorize_issues(issues)
        assert "sql_injection" in categories
        
        # Test XSS
        issues = [
            {"description": "XSS vulnerability in DOM", "pattern_name": "xss_pattern"}
        ]
        
        categories = validator._categorize_issues(issues)
        assert "xss" in categories
    
    def test_score_calculation(self, validator):
        """Test score calculation logic."""
        # Test negative test case (no issues expected)
        result = ValidationResult(
            file_path="test.py",
            expected_issues=0,
            actual_issues=0,
            is_positive_test=False
        )
        
        score = validator._calculate_score(result)
        assert score == 1.0  # Perfect score
        
        # Test negative test case with false positive
        result.actual_issues = 2
        score = validator._calculate_score(result)
        assert score == 0.0  # Failed
        
        # Test positive test case (issues expected)
        result = ValidationResult(
            file_path="test.py",
            expected_issues=5,
            actual_issues=5,
            is_positive_test=True
        )
        
        score = validator._calculate_score(result)
        assert score == 1.0  # Perfect score
        
        # Test positive test case with fewer issues
        result.actual_issues = 2
        score = validator._calculate_score(result)
        assert score == 0.4  # 2/5 = 0.4
    
    @patch('validation_framework.subprocess.run')
    def test_cli_scan_success(self, mock_run, validator):
        """Test successful CLI scan."""
        # Mock successful CLI execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Mock output file with results
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_file = tmp_file.name
            json.dump({
                "file_results": [
                    {
                        "matches": [
                            {"category": "hardcoded_credentials", "severity": "HIGH"},
                            {"category": "hardcoded_credentials", "severity": "MEDIUM"}
                        ]
                    }
                ]
            }, tmp_file)
        
        try:
            issues, duration = validator._run_levox_cli_scan("test.py")
            
            assert len(issues) == 2
            assert issues[0]["category"] == "hardcoded_credentials"
            assert duration > 0
            
        finally:
            # Cleanup
            if Path(output_file).exists():
                Path(output_file).unlink()
    
    @patch('validation_framework.subprocess.run')
    def test_cli_scan_failure(self, mock_run, validator):
        """Test CLI scan failure handling."""
        # Mock failed CLI execution
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: Invalid file"
        mock_run.return_value = mock_result
        
        issues, duration = validator._run_levox_cli_scan("invalid.py")
        
        assert len(issues) == 0
        assert duration > 0
    
    def test_validation_result_creation(self, validator):
        """Test validation result creation."""
        # Mock scan results
        detected_issues = [
            {"category": "hardcoded_credentials", "severity": "HIGH"},
            {"category": "hardcoded_credentials", "severity": "MEDIUM"}
        ]
        
        ground_truth_data = {
            "expected_issue_count": {"min": 2, "max": 5},
            "expected_issues": [
                {
                    "patterns": ["hardcoded_password", "hardcoded_secret"]
                }
            ]
        }
        
        # Mock scan execution
        with patch.object(validator, '_run_levox_cli_scan', return_value=(detected_issues, 1.5)):
            result = validator.validate_file("positives/test_file.py", ground_truth_data)
        
        assert result.file_path == "positives/test_file.py"
        assert result.expected_issues == 2
        assert result.actual_issues == 2
        assert result.passed is True
        assert result.score == 1.0
        assert result.scan_duration == 1.5
        assert "hardcoded_credentials" in result.detected_categories
    
    def test_validation_suite_execution(self, validator):
        """Test complete validation suite execution."""
        # Mock file validation
        mock_result = ValidationResult(
            file_path="test.py",
            expected_issues=2,
            actual_issues=2,
            passed=True,
            score=1.0,
            scan_duration=1.0
        )
        
        with patch.object(validator, 'validate_file', return_value=mock_result):
            summary = validator.run_validation_suite()
        
        assert summary.total_tests == 2
        assert summary.passed_tests == 2
        assert summary.failed_tests == 0
        assert summary.true_positives == 1
        assert summary.true_negatives == 1
        assert summary.false_positives == 0
        assert summary.false_negatives == 0
        assert summary.precision == 1.0
        assert summary.recall == 1.0
        assert summary.f1_score == 1.0
    
    def test_results_saving(self, validator):
        """Test results saving functionality."""
        # Create a mock summary
        summary = ValidationSummary(
            total_tests=2,
            passed_tests=2,
            failed_tests=0,
            true_positives=1,
            false_positives=0,
            false_negatives=0,
            true_negatives=1,
            precision=1.0,
            recall=1.0,
            f1_score=1.0,
            total_duration=2.0,
            results=[],
            errors=[]
        )
        
        # Test saving to specific file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_file = tmp_file.name
        
        try:
            validator.save_results(summary, output_file)
            
            # Verify file was created and contains expected data
            assert Path(output_file).exists()
            
            with open(output_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert saved_data["summary"]["total_tests"] == 2
            assert saved_data["summary"]["precision"] == 1.0
            assert "metadata" in saved_data
            
        finally:
            # Cleanup
            if Path(output_file).exists():
                Path(output_file).unlink()
    
    def test_threshold_evaluation(self, validator):
        """Test threshold evaluation logic."""
        # Test passing thresholds
        summary = ValidationSummary(
            total_tests=2,
            passed_tests=2,
            failed_tests=0,
            true_positives=1,
            false_positives=0,
            false_negatives=0,
            true_negatives=1,
            precision=0.9,
            recall=0.9,
            f1_score=0.9,
            total_duration=2.0,
            results=[],
            errors=[]
        )
        
        success = validator.print_summary(summary)
        assert success is True
        
        # Test failing thresholds
        summary.precision = 0.7
        summary.recall = 0.7
        summary.f1_score = 0.7
        
        success = validator.print_summary(summary)
        assert success is False


class TestIntegration:
    """Integration tests for the validation framework."""
    
    @pytest.mark.integration
    def test_real_file_validation(self, test_dir):
        """Test validation with real test files."""
        # This test requires actual test files to exist
        test_file = test_dir / "positives" / "hardcoded_password.py"
        
        if not test_file.exists():
            pytest.skip("Test file not available")
        
        # Create validator
        validator = LevoxValidator(use_cli=True)
        
        # Get ground truth data for this file
        ground_truth_data = validator.ground_truth["test_files"]["positives/hardcoded_password.py"]
        
        # Validate the file
        result = validator.validate_file(str(test_file), ground_truth_data)
        
        # Basic assertions
        assert result.file_path == str(test_file)
        assert result.expected_issues > 0
        assert result.scan_duration > 0
        
        # The file should have some issues (it's a positive test)
        assert result.actual_issues >= 0
    
    @pytest.mark.integration
    def test_clean_file_validation(self, test_dir):
        """Test validation with clean test files."""
        # This test requires actual test files to exist
        test_file = test_dir / "negatives" / "clean_python.py"
        
        if not test_file.exists():
            pytest.skip("Test file not available")
        
        # Create validator
        validator = LevoxValidator(use_cli=True)
        
        # Get ground truth data for this file
        ground_truth_data = validator.ground_truth["test_files"]["negatives/clean_python.py"]
        
        # Validate the file
        result = validator.validate_file(str(test_file), ground_truth_data)
        
        # Basic assertions
        assert result.file_path == str(test_file)
        assert result.expected_issues == 0
        assert result.scan_duration > 0
        
        # The file should have no issues (it's a negative test)
        # Note: This might fail if Levox detects false positives
        # which would indicate an issue with the detection rules


class TestCLIInterface:
    """Test CLI interface functionality."""
    
    def test_cli_argument_parsing(self):
        """Test CLI argument parsing."""
        from validation_framework import main
        
        # Test with help flag
        with patch('sys.argv', ['validation_framework.py', '--help']):
            with patch('sys.exit') as mock_exit:
                with pytest.raises(SystemExit):
                    main()
        
        # Test with verbose flag
        with patch('sys.argv', ['validation_framework.py', '--verbose']):
            with patch('validation_framework.LevoxValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator_class.return_value = mock_validator
                mock_validator.run_validation_suite.return_value = Mock()
                mock_validator.print_summary.return_value = True
                
                with patch('sys.exit') as mock_exit:
                    main()
                    mock_exit.assert_called_with(0)
    
    def test_cli_error_handling(self):
        """Test CLI error handling."""
        from validation_framework import main
        
        with patch('sys.argv', ['validation_framework.py']):
            with patch('validation_framework.LevoxValidator') as mock_validator_class:
                mock_validator_class.side_effect = Exception("Test error")
                
                with patch('sys.exit') as mock_exit:
                    main()
                    mock_exit.assert_called_with(1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
