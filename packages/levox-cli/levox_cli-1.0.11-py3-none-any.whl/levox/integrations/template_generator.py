"""
Levox CI/CD Template Generator

Generates ready-to-use CI/CD templates for popular platforms with customizable
scan profiles, proper error handling, SARIF output, and license tier gating.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from ..core.config import Config, LicenseTier
from ..core.exceptions import LevoxException

logger = logging.getLogger(__name__)


class CIPlatform(str, Enum):
    """Supported CI/CD platforms."""
    GITHUB_ACTIONS = "github"
    GITLAB_CI = "gitlab"
    JENKINS = "jenkins"
    AZURE_DEVOPS = "azure"
    BITBUCKET_PIPELINES = "bitbucket"
    CIRCLE_CI = "circleci"


class ScanProfile(str, Enum):
    """Predefined scan profiles for different use cases."""
    QUICK_SCAN = "quick"      # Fast scan for pre-commit/pre-push
    BALANCED_SCAN = "balanced"  # Standard scan for PR/merge
    THOROUGH_SCAN = "thorough"  # Comprehensive scan for releases
    SECURITY_SCAN = "security"  # Security-focused scan with SARIF


@dataclass
class TemplateConfig:
    """Configuration for template generation."""
    platform: CIPlatform
    scan_profile: ScanProfile
    license_tier: LicenseTier
    fail_on_severity: str = "HIGH"  # HIGH, MEDIUM, LOW
    enable_sarif: bool = True
    enable_caching: bool = True
    enable_artifacts: bool = True
    custom_scan_path: Optional[str] = None
    exclude_patterns: List[str] = None
    max_file_size_mb: Optional[int] = None
    custom_env_vars: Dict[str, str] = None
    
    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = []
        if self.custom_env_vars is None:
            self.custom_env_vars = {}


class TemplateGenerator:
    """Generates CI/CD templates for various platforms."""
    
    def __init__(self, config: Config):
        self.config = config
        self.templates_dir = Path(__file__).parent / "templates"
        self._ensure_templates_dir()
    
    def _ensure_templates_dir(self):
        """Ensure templates directory exists."""
        self.templates_dir.mkdir(exist_ok=True)
    
    def generate_template(self, template_config: TemplateConfig, output_path: Optional[str] = None) -> str:
        """
        Generate a CI/CD template based on configuration.
        
        Args:
            template_config: Configuration for the template
            output_path: Optional path to save the template
            
        Returns:
            Generated template content
        """
        try:
            # Validate license tier requirements
            self._validate_license_tier(template_config)
            
            # Generate platform-specific template
            if template_config.platform == CIPlatform.GITHUB_ACTIONS:
                content = self._generate_github_actions_template(template_config)
                filename = ".github/workflows/levox-scan.yml"
            elif template_config.platform == CIPlatform.GITLAB_CI:
                content = self._generate_gitlab_ci_template(template_config)
                filename = ".gitlab-ci.yml"
            elif template_config.platform == CIPlatform.JENKINS:
                content = self._generate_jenkins_template(template_config)
                filename = "Jenkinsfile"
            elif template_config.platform == CIPlatform.AZURE_DEVOPS:
                content = self._generate_azure_devops_template(template_config)
                filename = "azure-pipelines.yml"
            elif template_config.platform == CIPlatform.BITBUCKET_PIPELINES:
                content = self._generate_bitbucket_template(template_config)
                filename = "bitbucket-pipelines.yml"
            elif template_config.platform == CIPlatform.CIRCLE_CI:
                content = self._generate_circleci_template(template_config)
                filename = ".circleci/config.yml"
            else:
                raise LevoxException(f"Unsupported platform: {template_config.platform}")
            
            # Save template if output path specified
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(content, encoding='utf-8')
                logger.info(f"Template saved to: {output_file}")
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate template: {e}")
            raise LevoxException(f"Template generation failed: {e}")
    
    def _validate_license_tier(self, template_config: TemplateConfig):
        """Validate that license tier supports requested features."""
        license_features = self.config.license.features
        
        # Check SARIF support
        if template_config.enable_sarif and not license_features.get("sarif_export", False):
            if template_config.license_tier == LicenseTier.STARTER:
                template_config.enable_sarif = False
                logger.warning("SARIF export not available in Starter tier, disabling")
            elif template_config.license_tier == LicenseTier.PRO:
                template_config.enable_sarif = False
                logger.warning("SARIF export not available in Pro tier, disabling")
        
        # Check advanced features
        if template_config.scan_profile == ScanProfile.SECURITY_SCAN:
            if not license_features.get("advanced_security", False):
                template_config.scan_profile = ScanProfile.BALANCED_SCAN
                logger.warning("Security scan profile requires Business+ tier, falling back to balanced")
    
    def _generate_github_actions_template(self, config: TemplateConfig) -> str:
        """Generate GitHub Actions workflow template."""
        scan_flags = self._get_scan_flags(config)
        sarif_step = self._get_sarif_step(config)
        artifact_step = self._get_artifact_step(config)
        cache_step = self._get_cache_step(config)
        
        template = f"""name: Levox Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    # Run security scan daily at 2 AM UTC
    - cron: '0 2 * * *'

env:
  LEVOX_LICENSE_KEY: ${{{{ secrets.LEVOX_LICENSE_KEY }}}}
  LEVOX_SCAN_PATH: "{config.custom_scan_path or '.'}"
  LEVOX_FAIL_ON: "{config.fail_on_severity}"
  LEVOX_MAX_FILE_SIZE: "{config.max_file_size_mb or 10}"

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
      actions: read
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for better analysis
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install Levox
      run: |
        pip install --upgrade levox
        levox --version
    
    {cache_step}
    
    - name: Run Levox Security Scan
      id: levox-scan
      run: |
        echo "🔍 Starting Levox security scan..."
        echo "Scan profile: {config.scan_profile.value}"
        echo "License tier: {config.license_tier.value}"
        
        levox scan ${{{{ env.LEVOX_SCAN_PATH }}}} \\
          {scan_flags} \\
          --format json \\
          --output levox-results.json \\
          --verbosity summary
        
        # Check scan results
        if [ -f levox-results.json ]; then
          echo "✅ Scan completed successfully"
          echo "scan-completed=true" >> $GITHUB_OUTPUT
        else
          echo "❌ Scan failed - no results file generated"
          echo "scan-completed=false" >> $GITHUB_OUTPUT
          exit 1
        fi
    
    {sarif_step}
    
    {artifact_step}
    
    - name: Comment PR with results
      if: github.event_name == 'pull_request' && steps.levox-scan.outputs.scan-completed == 'true'
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          if (fs.existsSync('levox-results.json')) {{
            const results = JSON.parse(fs.readFileSync('levox-results.json', 'utf8'));
            const violations = results.scan_results?.violations || [];
            const summary = results.scan_results?.summary || {{}};
            
            const comment = `## 🔍 Levox Security Scan Results
            
            **Scan Summary:**
            - Files scanned: ${{summary.files_scanned || 'N/A'}}
            - Violations found: ${{violations.length}}
            - Scan time: ${{summary.scan_time || 'N/A'}}s
            
            ${{violations.length > 0 ? '⚠️ **Security violations detected!** Please review the findings.' : '✅ **No security violations found!**'}}
            
            View detailed results in the Security tab or download artifacts.`;
            
            github.rest.issues.createComment({{
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            }});
          }}
    
    - name: Fail on security violations
      if: steps.levox-scan.outputs.scan-completed == 'true' && env.LEVOX_FAIL_ON == 'HIGH'
      run: |
        if [ -f levox-results.json ]; then
          violations=$(jq '.scan_results.violations | map(select(.severity == "HIGH")) | length' levox-results.json)
          if [ "$violations" -gt 0 ]; then
            echo "❌ High severity violations found: $violations"
            echo "Failing build due to high severity security issues"
            exit 1
          else
            echo "✅ No high severity violations found"
          fi
        fi
"""
        return template
    
    def _generate_gitlab_ci_template(self, config: TemplateConfig) -> str:
        """Generate GitLab CI template."""
        scan_flags = self._get_scan_flags(config)
        
        template = f"""# Levox Security Scan Pipeline
# Generated for {config.platform.value} with {config.scan_profile.value} profile

stages:
  - security-scan
  - report

variables:
  LEVOX_LICENSE_KEY: "$LEVOX_LICENSE_KEY"
  LEVOX_SCAN_PATH: "{config.custom_scan_path or '.'}"
  LEVOX_FAIL_ON: "{config.fail_on_severity}"
  LEVOX_MAX_FILE_SIZE: "{config.max_file_size_mb or 10}"

levox-security-scan:
  stage: security-scan
  image: python:3.9-slim
  before_script:
    - pip install --upgrade levox
    - levox --version
  script:
    - echo "🔍 Starting Levox security scan..."
    - echo "Scan profile: {config.scan_profile.value}"
    - echo "License tier: {config.license_tier.value}"
    - |
      levox scan $LEVOX_SCAN_PATH \\
        {scan_flags} \\
        --format json \\
        --output levox-results.json \\
        --verbosity summary
    - |
      if [ -f levox-results.json ]; then
        echo "✅ Scan completed successfully"
        violations=$(jq '.scan_results.violations | length' levox-results.json)
        echo "Violations found: $violations"
      else
        echo "❌ Scan failed - no results file generated"
        exit 1
      fi
  artifacts:
    when: always
    reports:
      junit: levox-results.json
    paths:
      - levox-results.json
    expire_in: 1 week
  cache:
    key: "$CI_COMMIT_REF_SLUG"
    paths:
      - .levox-cache/
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_PIPELINE_SOURCE == "schedule"

levox-security-report:
  stage: report
  image: python:3.9-slim
  dependencies:
    - levox-security-scan
  script:
    - |
      if [ -f levox-results.json ]; then
        violations=$(jq '.scan_results.violations | map(select(.severity == "$LEVOX_FAIL_ON")) | length' levox-results.json)
        if [ "$violations" -gt 0 ] && [ "$LEVOX_FAIL_ON" = "HIGH" ]; then
          echo "❌ High severity violations found: $violations"
          echo "Failing pipeline due to high severity security issues"
          exit 1
        else
          echo "✅ Security scan passed"
        fi
      fi
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
"""
        return template
    
    def _generate_jenkins_template(self, config: TemplateConfig) -> str:
        """Generate Jenkins pipeline template."""
        scan_flags = self._get_scan_flags(config)
        
        template = f"""pipeline {{
    agent any
    
    environment {{
        LEVOX_LICENSE_KEY = credentials('levox-license-key')
        LEVOX_SCAN_PATH = '{config.custom_scan_path or '.'}'
        LEVOX_FAIL_ON = '{config.fail_on_severity}'
        LEVOX_MAX_FILE_SIZE = '{config.max_file_size_mb or 10}'
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}
        
        stage('Setup Levox') {{
            steps {{
                sh '''
                    echo "🔧 Setting up Levox..."
                    pip install --upgrade levox
                    levox --version
                '''
            }}
        }}
        
        stage('Security Scan') {{
            steps {{
                sh '''
                    echo "🔍 Starting Levox security scan..."
                    echo "Scan profile: {config.scan_profile.value}"
                    echo "License tier: {config.license_tier.value}"
                    
                    levox scan $LEVOX_SCAN_PATH \\
                        {scan_flags} \\
                        --format json \\
                        --output levox-results.json \\
                        --verbosity summary
                '''
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'levox-results.json', fingerprint: true
                    publishTestResults testResultsPattern: 'levox-results.json'
                }}
            }}
        }}
        
        stage('Security Report') {{
            steps {{
                sh '''
                    if [ -f levox-results.json ]; then
                        violations=$(jq '.scan_results.violations | map(select(.severity == "$LEVOX_FAIL_ON")) | length' levox-results.json)
                        if [ "$violations" -gt 0 ] && [ "$LEVOX_FAIL_ON" = "HIGH" ]; then
                            echo "❌ High severity violations found: $violations"
                            echo "Failing build due to high severity security issues"
                            exit 1
                        else
                            echo "✅ Security scan passed"
                        fi
                    fi
                '''
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            echo "✅ Levox security scan completed successfully"
        }}
        failure {{
            echo "❌ Levox security scan failed"
        }}
    }}
}}
"""
        return template
    
    def _generate_azure_devops_template(self, config: TemplateConfig) -> str:
        """Generate Azure DevOps pipeline template."""
        scan_flags = self._get_scan_flags(config)
        
        template = f"""# Levox Security Scan Pipeline
# Generated for {config.platform.value} with {config.scan_profile.value} profile

trigger:
- main
- develop

pr:
- main
- develop

schedules:
- cron: "0 2 * * *"  # Daily at 2 AM UTC
  displayName: Daily security scan
  branches:
    include:
    - main

variables:
  LEVOX_SCAN_PATH: '{config.custom_scan_path or '.'}'
  LEVOX_FAIL_ON: '{config.fail_on_severity}'
  LEVOX_MAX_FILE_SIZE: '{config.max_file_size_mb or 10}'

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: SecurityScan
  displayName: 'Levox Security Scan'
  jobs:
  - job: LevoxScan
    displayName: 'Run Levox Security Scan'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.9'
      displayName: 'Use Python 3.9'
    
    - script: |
        echo "🔧 Installing Levox..."
        pip install --upgrade levox
        levox --version
      displayName: 'Install Levox'
    
    - script: |
        echo "🔍 Starting Levox security scan..."
        echo "Scan profile: {config.scan_profile.value}"
        echo "License tier: {config.license_tier.value}"
        
        levox scan $(LEVOX_SCAN_PATH) \\
          {scan_flags} \\
          --format json \\
          --output levox-results.json \\
          --verbosity summary
      displayName: 'Run Security Scan'
      env:
        LEVOX_LICENSE_KEY: $(LEVOX_LICENSE_KEY)
    
    - task: PublishTestResults@2
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: 'levox-results.json'
        testRunTitle: 'Levox Security Scan Results'
      condition: always()
      displayName: 'Publish Test Results'
    
    - task: PublishBuildArtifacts@1
      inputs:
        pathToPublish: 'levox-results.json'
        artifactName: 'levox-security-results'
      condition: always()
      displayName: 'Publish Security Results'
    
    - script: |
        if [ -f levox-results.json ]; then
          violations=$(jq '.scan_results.violations | map(select(.severity == "$(LEVOX_FAIL_ON)")) | length' levox-results.json)
          if [ "$violations" -gt 0 ] && [ "$(LEVOX_FAIL_ON)" = "HIGH" ]; then
            echo "❌ High severity violations found: $violations"
            echo "Failing build due to high severity security issues"
            exit 1
          else
            echo "✅ Security scan passed"
          fi
        fi
      displayName: 'Check Security Results'
"""
        return template
    
    def _generate_bitbucket_template(self, config: TemplateConfig) -> str:
        """Generate Bitbucket Pipelines template."""
        scan_flags = self._get_scan_flags(config)
        
        template = f"""# Levox Security Scan Pipeline
# Generated for {config.platform.value} with {config.scan_profile.value} profile

image: python:3.9

definitions:
  caches:
    levox-cache: ~/.levox-cache

pipelines:
  default:
    - step:
        name: Levox Security Scan
        caches:
          - levox-cache
        script:
          - echo "🔧 Installing Levox..."
          - pip install --upgrade levox
          - levox --version
          - |
            echo "🔍 Starting Levox security scan..."
            echo "Scan profile: {config.scan_profile.value}"
            echo "License tier: {config.license_tier.value}"
            
            levox scan {config.custom_scan_path or '.'} \\
              {scan_flags} \\
              --format json \\
              --output levox-results.json \\
              --verbosity summary
          - |
            if [ -f levox-results.json ]; then
              echo "✅ Scan completed successfully"
              violations=$(jq '.scan_results.violations | length' levox-results.json)
              echo "Violations found: $violations"
            else
              echo "❌ Scan failed - no results file generated"
              exit 1
            fi
        artifacts:
          - levox-results.json
        after-script:
          - |
            if [ -f levox-results.json ]; then
              violations=$(jq '.scan_results.violations | map(select(.severity == "HIGH")) | length' levox-results.json)
              if [ "$violations" -gt 0 ]; then
                echo "❌ High severity violations found: $violations"
                echo "Failing build due to high severity security issues"
                exit 1
              else
                echo "✅ Security scan passed"
              fi
            fi

  branches:
    main:
      - step:
          name: Levox Security Scan (Main Branch)
          caches:
            - levox-cache
          script:
            - echo "🔧 Installing Levox..."
            - pip install --upgrade levox
            - levox --version
            - |
              echo "🔍 Starting Levox security scan..."
              echo "Scan profile: {config.scan_profile.value}"
              echo "License tier: {config.license_tier.value}"
              
              levox scan {config.custom_scan_path or '.'} \\
                {scan_flags} \\
                --format json \\
                --output levox-results.json \\
                --verbosity summary
            - |
              if [ -f levox-results.json ]; then
                echo "✅ Scan completed successfully"
                violations=$(jq '.scan_results.violations | length' levox-results.json)
                echo "Violations found: $violations"
              else
                echo "❌ Scan failed - no results file generated"
                exit 1
              fi
          artifacts:
            - levox-results.json
          after-script:
            - |
              if [ -f levox-results.json ]; then
                violations=$(jq '.scan_results.violations | map(select(.severity == "HIGH")) | length' levox-results.json)
                if [ "$violations" -gt 0 ]; then
                  echo "❌ High severity violations found: $violations"
                  echo "Failing build due to high severity security issues"
                  exit 1
                else
                  echo "✅ Security scan passed"
                fi
              fi

  pull-requests:
    '**':
      - step:
          name: Levox Security Scan (PR)
          caches:
            - levox-cache
          script:
            - echo "🔧 Installing Levox..."
            - pip install --upgrade levox
            - levox --version
            - |
              echo "🔍 Starting Levox security scan..."
              echo "Scan profile: {config.scan_profile.value}"
              echo "License tier: {config.license_tier.value}"
              
              levox scan {config.custom_scan_path or '.'} \\
                {scan_flags} \\
                --format json \\
                --output levox-results.json \\
                --verbosity summary
            - |
              if [ -f levox-results.json ]; then
                echo "✅ Scan completed successfully"
                violations=$(jq '.scan_results.violations | length' levox-results.json)
                echo "Violations found: $violations"
              else
                echo "❌ Scan failed - no results file generated"
                exit 1
              fi
          artifacts:
            - levox-results.json
"""
        return template
    
    def _generate_circleci_template(self, config: TemplateConfig) -> str:
        """Generate CircleCI template."""
        scan_flags = self._get_scan_flags(config)
        
        template = f"""# Levox Security Scan Pipeline
# Generated for {config.platform.value} with {config.scan_profile.value} profile

version: 2.1

jobs:
  security-scan:
    docker:
      - image: cimg/python:3.9
    working_directory: ~/repo
    steps:
      - checkout
      - restore_cache:
          keys:
            - levox-cache-{{{{ .Branch }}}}-{{{{ checksum "requirements.txt" }}}}
            - levox-cache-{{{{ .Branch }}}}
            - levox-cache
      - run:
          name: Install Levox
          command: |
            echo "🔧 Installing Levox..."
            pip install --upgrade levox
            levox --version
      - run:
          name: Run Levox Security Scan
          command: |
            echo "🔍 Starting Levox security scan..."
            echo "Scan profile: {config.scan_profile.value}"
            echo "License tier: {config.license_tier.value}"
            
            levox scan {config.custom_scan_path or '.'} \\
              {scan_flags} \\
              --format json \\
              --output levox-results.json \\
              --verbosity summary
          environment:
            LEVOX_LICENSE_KEY: $LEVOX_LICENSE_KEY
      - run:
          name: Check Scan Results
          command: |
            if [ -f levox-results.json ]; then
              echo "✅ Scan completed successfully"
              violations=$(jq '.scan_results.violations | length' levox-results.json)
              echo "Violations found: $violations"
            else
              echo "❌ Scan failed - no results file generated"
              exit 1
            fi
      - save_cache:
          paths:
            - ~/.levox-cache
          key: levox-cache-{{{{ .Branch }}}}-{{{{ checksum "requirements.txt" }}}}
      - store_artifacts:
          path: levox-results.json
          destination: levox-security-results
      - run:
          name: Fail on High Severity
          command: |
            if [ -f levox-results.json ]; then
              violations=$(jq '.scan_results.violations | map(select(.severity == "HIGH")) | length' levox-results.json)
              if [ "$violations" -gt 0 ]; then
                echo "❌ High severity violations found: $violations"
                echo "Failing build due to high severity security issues"
                exit 1
              else
                echo "✅ Security scan passed"
              fi
            fi

workflows:
  version: 2
  security-scan:
    jobs:
      - security-scan:
          filters:
            branches:
              only:
                - main
                - develop
      - security-scan:
          filters:
            branches:
              ignore:
                - main
                - develop
"""
        return template
    
    def _get_scan_flags(self, config: TemplateConfig) -> str:
        """Get scan flags based on profile and configuration."""
        flags = []
        
        # Profile-specific flags
        if config.scan_profile == ScanProfile.QUICK_SCAN:
            flags.extend([
                "--max-file-size-mb 5",
                "--exclude-patterns '*.min.js' '*.bundle.js' 'node_modules/**' 'vendor/**'",
                "--verbosity summary"
            ])
        elif config.scan_profile == ScanProfile.BALANCED_SCAN:
            flags.extend([
                f"--max-file-size-mb {config.max_file_size_mb or 10}",
                "--verbosity summary"
            ])
        elif config.scan_profile == ScanProfile.THOROUGH_SCAN:
            flags.extend([
                f"--max-file-size-mb {config.max_file_size_mb or 50}",
                "--cfg",
                "--verbosity verbose"
            ])
        elif config.scan_profile == ScanProfile.SECURITY_SCAN:
            flags.extend([
                f"--max-file-size-mb {config.max_file_size_mb or 25}",
                "--cfg",
                "--secret-verify",
                "--verbosity verbose"
            ])
        
        # Add exclude patterns
        if config.exclude_patterns:
            exclude_str = " ".join([f"'{pattern}'" for pattern in config.exclude_patterns])
            flags.append(f"--exclude-patterns {exclude_str}")
        
        # Add custom environment variables
        for key, value in config.custom_env_vars.items():
            flags.append(f"--env {key}={value}")
        
        return " \\\n        ".join(flags)
    
    def _get_sarif_step(self, config: TemplateConfig) -> str:
        """Get SARIF upload step for GitHub Actions."""
        if not config.enable_sarif:
            return ""
        
        return """    - name: Upload SARIF results
      if: steps.levox-scan.outputs.scan-completed == 'true'
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: levox-results.sarif
      continue-on-error: true"""
    
    def _get_artifact_step(self, config: TemplateConfig) -> str:
        """Get artifact upload step."""
        if not config.enable_artifacts:
            return ""
        
        return """    - name: Upload scan artifacts
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: levox-security-results
        path: |
          levox-results.json
          levox-results.sarif
        retention-days: 30"""
    
    def _get_cache_step(self, config: TemplateConfig) -> str:
        """Get cache step for GitHub Actions."""
        if not config.enable_caching:
            return ""
        
        return """    - name: Cache Levox data
      uses: actions/cache@v4
      with:
        path: ~/.levox-cache
        key: ${{ runner.os }}-levox-${{ hashFiles('**/requirements.txt') }}-${{ hashFiles('**/package.json') }}
        restore-keys: |
          ${{ runner.os }}-levox-${{ hashFiles('**/requirements.txt') }}-
          ${{ runner.os }}-levox-"""
    
    def list_available_platforms(self) -> List[CIPlatform]:
        """List all available CI/CD platforms."""
        return list(CIPlatform)
    
    def list_available_profiles(self) -> List[ScanProfile]:
        """List all available scan profiles."""
        return list(ScanProfile)
    
    def validate_template_config(self, config: TemplateConfig) -> Tuple[bool, List[str]]:
        """Validate template configuration."""
        errors = []
        
        # Check license tier compatibility
        if config.enable_sarif and config.license_tier in [LicenseTier.STARTER, LicenseTier.PRO]:
            errors.append("SARIF export requires Business+ tier")
        
        if config.scan_profile == ScanProfile.SECURITY_SCAN and config.license_tier == LicenseTier.STARTER:
            errors.append("Security scan profile requires Pro+ tier")
        
        # Check scan path
        if config.custom_scan_path and not Path(config.custom_scan_path).exists():
            errors.append(f"Scan path does not exist: {config.custom_scan_path}")
        
        # Check file size limit
        if config.max_file_size_mb and (config.max_file_size_mb < 1 or config.max_file_size_mb > 1000):
            errors.append("Max file size must be between 1 and 1000 MB")
        
        return len(errors) == 0, errors
