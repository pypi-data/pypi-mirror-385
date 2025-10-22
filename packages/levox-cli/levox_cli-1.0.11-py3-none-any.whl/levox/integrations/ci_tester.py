"""
Levox CI/CD Integration Tester

Provides testing framework for CI/CD integrations including template validation,
local CI simulation, and integration testing with popular CI platforms.
"""

import os
import json
import yaml
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

from ..core.config import Config, LicenseTier
from ..core.exceptions import LevoxException

logger = logging.getLogger(__name__)


class TestResultStatus(str, Enum):
    """Test result status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestCase:
    """Individual test case."""
    name: str
    description: str
    test_type: str  # template, integration, performance, validation
    expected_result: TestResultStatus
    timeout_seconds: int = 300
    dependencies: List[str] = field(default_factory=list)
    setup_commands: List[str] = field(default_factory=list)
    test_commands: List[str] = field(default_factory=list)
    cleanup_commands: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    expected_exit_code: int = 0


@dataclass
class TestSuite:
    """Test suite containing multiple test cases."""
    name: str
    description: str
    test_cases: List[TestCase]
    setup_commands: List[str] = field(default_factory=list)
    cleanup_commands: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Result of a test execution."""
    test_name: str
    result: TestResultStatus
    execution_time: float
    output: str
    error: Optional[str] = None
    exit_code: int = 0
    details: Dict[str, Any] = field(default_factory=dict)


class CITester:
    """Tests CI/CD integrations and validates templates."""
    
    def __init__(self, config: Config):
        self.config = config
        self.test_dir = Path.home() / ".levox" / "tests"
        self._ensure_test_dir()
    
    def _ensure_test_dir(self):
        """Ensure test directory exists."""
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    def run_template_validation_tests(self) -> List[TestResult]:
        """Run template validation tests."""
        test_suite = self._create_template_validation_suite()
        return self._run_test_suite(test_suite)
    
    def run_integration_tests(self) -> List[TestResult]:
        """Run integration tests."""
        test_suite = self._create_integration_test_suite()
        return self._run_test_suite(test_suite)
    
    def run_performance_tests(self) -> List[TestResult]:
        """Run performance tests."""
        test_suite = self._create_performance_test_suite()
        return self._run_test_suite(test_suite)
    
    def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """Run all test suites."""
        results = {}
        
        try:
            results["template_validation"] = self.run_template_validation_tests()
            results["integration"] = self.run_integration_tests()
            results["performance"] = self.run_performance_tests()
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to run all tests: {e}")
            return results
    
    def validate_template(self, template_path: str, platform: str) -> TestResult:
        """Validate a specific template."""
        try:
            template_file = Path(template_path)
            if not template_file.exists():
                return TestResult(
                test_name=f"validate_{platform}_template",
                result=TestResultStatus.FAILED,
                execution_time=0.0,
                output="",
                error=f"Template file not found: {template_path}",
                exit_code=1
            )
            
            # Read template content
            template_content = template_file.read_text()
            
            # Validate based on platform
            if platform == "github":
                return self._validate_github_template(template_content)
            elif platform == "gitlab":
                return self._validate_gitlab_template(template_content)
            elif platform == "jenkins":
                return self._validate_jenkins_template(template_content)
            elif platform == "azure":
                return self._validate_azure_template(template_content)
            elif platform == "bitbucket":
                return self._validate_bitbucket_template(template_content)
            elif platform == "circleci":
                return self._validate_circleci_template(template_content)
            else:
                return TestResult(
                    test_name=f"validate_{platform}_template",
                    result=TestResultStatus.FAILED,
                    execution_time=0.0,
                    output="",
                    error=f"Unsupported platform: {platform}",
                    exit_code=1
                )
                
        except Exception as e:
            logger.error(f"Failed to validate template: {e}")
            return TestResult(
                test_name=f"validate_{platform}_template",
                result=TestResultStatus.ERROR,
                execution_time=0.0,
                output="",
                error=str(e),
                exit_code=1
            )
    
    def simulate_ci_environment(self, template_path: str, platform: str) -> TestResult:
        """Simulate CI environment locally."""
        try:
            # Create temporary directory for simulation
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Copy template to temp directory
                template_file = Path(template_path)
                if template_file.exists():
                    shutil.copy2(template_file, temp_path / template_file.name)
                
                # Create mock repository structure
                self._create_mock_repository(temp_path)
                
                # Run simulation based on platform
                if platform == "github":
                    return self._simulate_github_actions(temp_path)
                elif platform == "gitlab":
                    return self._simulate_gitlab_ci(temp_path)
                elif platform == "jenkins":
                    return self._simulate_jenkins(temp_path)
                else:
                    return TestResult(
                        test_name=f"simulate_{platform}_ci",
                        result=TestResultStatus.SKIPPED,
                        execution_time=0.0,
                        output=f"Simulation not implemented for {platform}",
                        error=None,
                        exit_code=0
                    )
                    
        except Exception as e:
            logger.error(f"Failed to simulate CI environment: {e}")
            return TestResult(
                test_name=f"simulate_{platform}_ci",
                result=TestResultStatus.ERROR,
                execution_time=0.0,
                output="",
                error=str(e),
                exit_code=1
            )
    
    def _create_template_validation_suite(self) -> TestSuite:
        """Create template validation test suite."""
        test_cases = []
        
        # Test GitHub Actions template
        test_cases.append(TestCase(
            name="validate_github_template",
            description="Validate GitHub Actions template syntax and structure",
            test_type="template",
            expected_result=TestResultStatus.PASSED,
            test_commands=["python -c \"import yaml; yaml.safe_load(open('.github/workflows/levox-scan.yml'))\""],
            expected_outputs=[".github/workflows/levox-scan.yml"]
        ))
        
        # Test GitLab CI template
        test_cases.append(TestCase(
            name="validate_gitlab_template",
            description="Validate GitLab CI template syntax and structure",
            test_type="template",
            expected_result=TestResultStatus.PASSED,
            test_commands=["python -c \"import yaml; yaml.safe_load(open('.gitlab-ci.yml'))\""],
            expected_outputs=[".gitlab-ci.yml"]
        ))
        
        # Test Jenkins template
        test_cases.append(TestCase(
            name="validate_jenkins_template",
            description="Validate Jenkins pipeline template syntax",
            test_type="template",
            expected_result=TestResultStatus.PASSED,
            test_commands=["python -c \"import re; content=open('Jenkinsfile').read(); assert 'pipeline' in content\""],
            expected_outputs=["Jenkinsfile"]
        ))
        
        return TestSuite(
            name="Template Validation",
            description="Validate CI/CD template syntax and structure",
            test_cases=test_cases
        )
    
    def _create_integration_test_suite(self) -> TestSuite:
        """Create integration test suite."""
        test_cases = []
        
        # Test pre-commit hook installation
        test_cases.append(TestCase(
            name="test_precommit_installation",
            description="Test pre-commit hook installation",
            test_type="integration",
            expected_result=TestResultStatus.PASSED,
            setup_commands=["git init", "levox init-ci --precommit"],
            test_commands=["test -f .git/hooks/pre-commit", "test -x .git/hooks/pre-commit"],
            cleanup_commands=["rm -rf .git"]
        ))
        
        # Test configuration generation
        test_cases.append(TestCase(
            name="test_config_generation",
            description="Test configuration file generation",
            test_type="integration",
            expected_result=TestResultStatus.PASSED,
            test_commands=["levox generate-config --output .levoxrc"],
            expected_outputs=[".levoxrc"]
        ))
        
        return TestSuite(
            name="Integration Tests",
            description="Test CI/CD integration functionality",
            test_cases=test_cases
        )
    
    def _create_performance_test_suite(self) -> TestSuite:
        """Create performance test suite."""
        test_cases = []
        
        # Test scan performance
        test_cases.append(TestCase(
            name="test_scan_performance",
            description="Test scan performance with various file sizes",
            test_type="performance",
            expected_result=TestResultStatus.PASSED,
            setup_commands=["python -c \"import os; [open(f'test_{i}.py', 'w').write('print(\\\"test\\\")\\n') for i in range(100)]\""],
            test_commands=["time levox scan . --format json --output results.json"],
            cleanup_commands=["rm -f test_*.py results.json"],
            timeout_seconds=60
        ))
        
        # Test memory usage
        test_cases.append(TestCase(
            name="test_memory_usage",
            description="Test memory usage during scan",
            test_type="performance",
            expected_result=TestResultStatus.PASSED,
            test_commands=["levox scan . --memory-limit-mb 512 --format json"],
            timeout_seconds=120
        ))
        
        return TestSuite(
            name="Performance Tests",
            description="Test CI/CD performance and resource usage",
            test_cases=test_cases
        )
    
    def _run_test_suite(self, test_suite: TestSuite) -> List[TestResult]:
        """Run a test suite."""
        results = []
        
        try:
            # Run setup commands
            for cmd in test_suite.setup_commands:
                self._run_command(cmd)
            
            # Run test cases
            for test_case in test_suite.test_cases:
                result = self._run_test_case(test_case)
                results.append(result)
            
            # Run cleanup commands
            for cmd in test_suite.cleanup_commands:
                self._run_command(cmd)
            
        except Exception as e:
            logger.error(f"Failed to run test suite {test_suite.name}: {e}")
        
        return results
    
    def _run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case."""
        start_time = time.time()
        
        try:
            # Run setup commands
            for cmd in test_case.setup_commands:
                self._run_command(cmd)
            
            # Run test commands
            output = ""
            exit_code = 0
            
            for cmd in test_case.test_commands:
                result = self._run_command(cmd, timeout=test_case.timeout_seconds)
                output += result["output"]
                if result["exit_code"] != 0:
                    exit_code = result["exit_code"]
                    break
            
            # Check expected outputs
            for expected_output in test_case.expected_outputs:
                if not Path(expected_output).exists():
                    return TestResult(
                        test_name=test_case.name,
                        result=TestResultStatus.FAILED,
                        execution_time=time.time() - start_time,
                        output=output,
                        error=f"Expected output not found: {expected_output}",
                        exit_code=1
                    )
            
            # Determine result
            if exit_code == test_case.expected_exit_code:
                result_status = TestResultStatus.PASSED
            else:
                result_status = TestResultStatus.FAILED
            
            # Run cleanup commands
            for cmd in test_case.cleanup_commands:
                self._run_command(cmd)
            
            return TestResult(
                test_name=test_case.name,
                result=result_status,
                execution_time=time.time() - start_time,
                output=output,
                exit_code=exit_code
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_case.name,
                result=TestResultStatus.ERROR,
                execution_time=time.time() - start_time,
                output="",
                error=str(e),
                exit_code=1
            )
    
    def _run_command(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        """Run a command and return result."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "error": f"Command timed out after {timeout} seconds",
                "exit_code": 124
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "exit_code": 1
            }
    
    def _validate_github_template(self, content: str) -> TestResult:
        """Validate GitHub Actions template."""
        try:
            # Check for required sections
            required_sections = ["name:", "on:", "jobs:", "security-scan:"]
            for section in required_sections:
                if section not in content:
                    return TestResult(
                        test_name="validate_github_template",
                        result=TestResultStatus.FAILED,
                        execution_time=0.0,
                        output="",
                        error=f"Missing required section: {section}",
                        exit_code=1
                    )
            
            # Validate YAML syntax
            yaml.safe_load(content)
            
            return TestResult(
                test_name="validate_github_template",
                result=TestResultStatus.PASSED,
                execution_time=0.0,
                output="GitHub Actions template validation passed",
                exit_code=0
            )
            
        except yaml.YAMLError as e:
            return TestResult(
                test_name="validate_github_template",
                result=TestResultStatus.FAILED,
                execution_time=0.0,
                output="",
                error=f"YAML syntax error: {e}",
                exit_code=1
            )
    
    def _validate_gitlab_template(self, content: str) -> TestResult:
        """Validate GitLab CI template."""
        try:
            # Check for required sections
            required_sections = ["stages:", "variables:", "levox-security-scan:"]
            for section in required_sections:
                if section not in content:
                    return TestResult(
                        test_name="validate_gitlab_template",
                        result=TestResultStatus.FAILED,
                        execution_time=0.0,
                        output="",
                        error=f"Missing required section: {section}",
                        exit_code=1
                    )
            
            # Validate YAML syntax
            yaml.safe_load(content)
            
            return TestResult(
                test_name="validate_gitlab_template",
                result=TestResultStatus.PASSED,
                execution_time=0.0,
                output="GitLab CI template validation passed",
                exit_code=0
            )
            
        except yaml.YAMLError as e:
            return TestResult(
                test_name="validate_gitlab_template",
                result=TestResultStatus.FAILED,
                execution_time=0.0,
                output="",
                error=f"YAML syntax error: {e}",
                exit_code=1
            )
    
    def _validate_jenkins_template(self, content: str) -> TestResult:
        """Validate Jenkins pipeline template."""
        try:
            # Check for required sections
            required_sections = ["pipeline", "agent", "stages", "security-scan"]
            for section in required_sections:
                if section not in content:
                    return TestResult(
                        test_name="validate_jenkins_template",
                        result=TestResultStatus.FAILED,
                        execution_time=0.0,
                        output="",
                        error=f"Missing required section: {section}",
                        exit_code=1
                    )
            
            return TestResult(
                test_name="validate_jenkins_template",
                result=TestResultStatus.PASSED,
                execution_time=0.0,
                output="Jenkins pipeline template validation passed",
                exit_code=0
            )
            
        except Exception as e:
            return TestResult(
                test_name="validate_jenkins_template",
                result=TestResultStatus.FAILED,
                execution_time=0.0,
                output="",
                error=str(e),
                exit_code=1
            )
    
    def _validate_azure_template(self, content: str) -> TestResult:
        """Validate Azure DevOps template."""
        try:
            # Check for required sections
            required_sections = ["trigger:", "pool:", "stages:", "SecurityScan:"]
            for section in required_sections:
                if section not in content:
                    return TestResult(
                        test_name="validate_azure_template",
                        result=TestResultStatus.FAILED,
                        execution_time=0.0,
                        output="",
                        error=f"Missing required section: {section}",
                        exit_code=1
                    )
            
            return TestResult(
                test_name="validate_azure_template",
                result=TestResultStatus.PASSED,
                execution_time=0.0,
                output="Azure DevOps template validation passed",
                exit_code=0
            )
            
        except Exception as e:
            return TestResult(
                test_name="validate_azure_template",
                result=TestResultStatus.FAILED,
                execution_time=0.0,
                output="",
                error=str(e),
                exit_code=1
            )
    
    def _validate_bitbucket_template(self, content: str) -> TestResult:
        """Validate Bitbucket Pipelines template."""
        try:
            # Check for required sections
            required_sections = ["image:", "pipelines:", "levox-security-scan:"]
            for section in required_sections:
                if section not in content:
                    return TestResult(
                        test_name="validate_bitbucket_template",
                        result=TestResultStatus.FAILED,
                        execution_time=0.0,
                        output="",
                        error=f"Missing required section: {section}",
                        exit_code=1
                    )
            
            return TestResult(
                test_name="validate_bitbucket_template",
                result=TestResultStatus.PASSED,
                execution_time=0.0,
                output="Bitbucket Pipelines template validation passed",
                exit_code=0
            )
            
        except Exception as e:
            return TestResult(
                test_name="validate_bitbucket_template",
                result=TestResultStatus.FAILED,
                execution_time=0.0,
                output="",
                error=str(e),
                exit_code=1
            )
    
    def _validate_circleci_template(self, content: str) -> TestResult:
        """Validate CircleCI template."""
        try:
            # Check for required sections
            required_sections = ["version:", "jobs:", "security-scan:", "workflows:"]
            for section in required_sections:
                if section not in content:
                    return TestResult(
                        test_name="validate_circleci_template",
                        result=TestResultStatus.FAILED,
                        execution_time=0.0,
                        output="",
                        error=f"Missing required section: {section}",
                        exit_code=1
                    )
            
            # Validate YAML syntax
            yaml.safe_load(content)
            
            return TestResult(
                test_name="validate_circleci_template",
                result=TestResultStatus.PASSED,
                execution_time=0.0,
                output="CircleCI template validation passed",
                exit_code=0
            )
            
        except yaml.YAMLError as e:
            return TestResult(
                test_name="validate_circleci_template",
                result=TestResultStatus.FAILED,
                execution_time=0.0,
                output="",
                error=f"YAML syntax error: {e}",
                exit_code=1
            )
    
    def _create_mock_repository(self, temp_path: Path):
        """Create mock repository structure for testing."""
        try:
            # Create basic file structure
            (temp_path / "src").mkdir(exist_ok=True)
            (temp_path / "tests").mkdir(exist_ok=True)
            
            # Create sample files
            (temp_path / "src" / "main.py").write_text("print('Hello, World!')\n")
            (temp_path / "tests" / "test_main.py").write_text("def test_main():\n    assert True\n")
            (temp_path / "README.md").write_text("# Test Repository\n")
            
            # Initialize git repository
            subprocess.run(["git", "init"], cwd=temp_path, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=temp_path, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_path, capture_output=True)
            
        except Exception as e:
            logger.error(f"Failed to create mock repository: {e}")
    
    def _simulate_github_actions(self, temp_path: Path) -> TestResult:
        """Simulate GitHub Actions locally."""
        try:
            # Check if act is available
            result = subprocess.run(["which", "act"], capture_output=True)
            if result.returncode != 0:
                return TestResult(
                    test_name="simulate_github_actions",
                    result=TestResultStatus.SKIPPED,
                    execution_time=0.0,
                    output="act not available - install with: https://github.com/nektos/act",
                    error=None,
                    exit_code=0
                )
            
            # Run act simulation
            result = subprocess.run(
                ["act", "--dry-run"],
                cwd=temp_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return TestResult(
                test_name="simulate_github_actions",
                result=TestResultStatus.PASSED if result.returncode == 0 else TestResultStatus.FAILED,
                execution_time=0.0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                test_name="simulate_github_actions",
                result=TestResultStatus.FAILED,
                execution_time=0.0,
                output="",
                error="Simulation timed out",
                exit_code=124
            )
        except Exception as e:
            return TestResult(
                test_name="simulate_github_actions",
                result=TestResultStatus.ERROR,
                execution_time=0.0,
                output="",
                error=str(e),
                exit_code=1
            )
    
    def _simulate_gitlab_ci(self, temp_path: Path) -> TestResult:
        """Simulate GitLab CI locally."""
        try:
            # Check if gitlab-runner is available
            result = subprocess.run(["which", "gitlab-runner"], capture_output=True)
            if result.returncode != 0:
                return TestResult(
                    test_name="simulate_gitlab_ci",
                    result=TestResultStatus.SKIPPED,
                    execution_time=0.0,
                    output="gitlab-runner not available - install GitLab Runner",
                    error=None,
                    exit_code=0
                )
            
            # Run gitlab-runner simulation
            result = subprocess.run(
                ["gitlab-runner", "exec", "shell", "levox-security-scan"],
                cwd=temp_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return TestResult(
                test_name="simulate_gitlab_ci",
                result=TestResultStatus.PASSED if result.returncode == 0 else TestResultStatus.FAILED,
                execution_time=0.0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                test_name="simulate_gitlab_ci",
                result=TestResultStatus.FAILED,
                execution_time=0.0,
                output="",
                error="Simulation timed out",
                exit_code=124
            )
        except Exception as e:
            return TestResult(
                test_name="simulate_gitlab_ci",
                result=TestResultStatus.ERROR,
                execution_time=0.0,
                output="",
                error=str(e),
                exit_code=1
            )
    
    def _simulate_jenkins(self, temp_path: Path) -> TestResult:
        """Simulate Jenkins pipeline locally."""
        try:
            # Check if Jenkins CLI is available
            result = subprocess.run(["which", "jenkins-cli"], capture_output=True)
            if result.returncode != 0:
                return TestResult(
                    test_name="simulate_jenkins",
                    result=TestResultStatus.SKIPPED,
                    execution_time=0.0,
                    output="Jenkins CLI not available - install Jenkins CLI",
                    error=None,
                    exit_code=0
                )
            
            # For now, just validate the Jenkinsfile syntax
            jenkinsfile = temp_path / "Jenkinsfile"
            if jenkinsfile.exists():
                content = jenkinsfile.read_text()
                if "pipeline" in content and "stages" in content:
                    return TestResult(
                        test_name="simulate_jenkins",
                        result=TestResultStatus.PASSED,
                        execution_time=0.0,
                        output="Jenkinsfile syntax validation passed",
                        exit_code=0
                    )
                else:
                    return TestResult(
                        test_name="simulate_jenkins",
                        result=TestResultStatus.FAILED,
                        execution_time=0.0,
                        output="",
                        error="Invalid Jenkinsfile syntax",
                        exit_code=1
                    )
            else:
                return TestResult(
                    test_name="simulate_jenkins",
                    result=TestResultStatus.FAILED,
                    execution_time=0.0,
                    output="",
                    error="Jenkinsfile not found",
                    exit_code=1
                )
            
        except Exception as e:
            return TestResult(
                test_name="simulate_jenkins",
                result=TestResultStatus.ERROR,
                execution_time=0.0,
                output="",
                error=str(e),
                exit_code=1
            )
