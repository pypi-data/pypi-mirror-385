"""
Levox Pre-commit Integration

Provides pre-commit hook integration for Levox CLI with fast scanning
of staged files and git hook management.
"""

import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from ..core.config import Config, LicenseTier
from ..core.exceptions import LevoxException

logger = logging.getLogger(__name__)


@dataclass
class PreCommitConfig:
    """Configuration for pre-commit integration."""
    license_tier: LicenseTier
    scan_staged_only: bool = True
    fail_on_severity: str = "HIGH"  # HIGH, MEDIUM, LOW
    max_scan_time_seconds: int = 10
    exclude_patterns: List[str] = None
    custom_hook_name: str = "levox-security-scan"
    
    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                "*.min.js",
                "*.bundle.js", 
                "node_modules/**",
                "vendor/**",
                "*.lock",
                "*.log"
            ]


class PreCommitIntegration:
    """Handles pre-commit hook integration for Levox."""
    
    def __init__(self, config: Config):
        self.config = config
        self.hooks_dir = Path.home() / ".levox" / "hooks"
        self._ensure_hooks_dir()
    
    def _ensure_hooks_dir(self):
        """Ensure hooks directory exists."""
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_precommit_config(self, precommit_config: PreCommitConfig, output_path: Optional[str] = None) -> str:
        """
        Generate .pre-commit-config.yaml configuration.
        
        Args:
            precommit_config: Configuration for pre-commit hooks
            output_path: Optional path to save the configuration
            
        Returns:
            Generated pre-commit configuration content
        """
        try:
            # Validate license tier requirements
            self._validate_license_tier(precommit_config)
            
            # Generate pre-commit configuration
            config_content = self._generate_precommit_yaml(precommit_config)
            
            # Save configuration if output path specified
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(config_content)
                logger.info(f"Pre-commit configuration saved to: {output_file}")
            
            return config_content
            
        except Exception as e:
            logger.error(f"Failed to generate pre-commit configuration: {e}")
            raise LevoxException(f"Pre-commit configuration generation failed: {e}")
    
    def generate_git_hook(self, precommit_config: PreCommitConfig, hook_type: str = "pre-commit") -> str:
        """
        Generate a git hook script.
        
        Args:
            precommit_config: Configuration for the hook
            hook_type: Type of git hook (pre-commit, pre-push, etc.)
            
        Returns:
            Generated git hook script content
        """
        try:
            if hook_type == "pre-commit":
                return self._generate_precommit_hook(precommit_config)
            elif hook_type == "pre-push":
                return self._generate_prepush_hook(precommit_config)
            else:
                raise LevoxException(f"Unsupported hook type: {hook_type}")
                
        except Exception as e:
            logger.error(f"Failed to generate {hook_type} hook: {e}")
            raise LevoxException(f"Hook generation failed: {e}")
    
    def install_git_hook(self, precommit_config: PreCommitConfig, git_repo_path: str, hook_type: str = "pre-commit") -> bool:
        """
        Install git hook in a repository.
        
        Args:
            precommit_config: Configuration for the hook
            git_repo_path: Path to git repository
            hook_type: Type of git hook to install
            
        Returns:
            True if installation successful
        """
        try:
            repo_path = Path(git_repo_path)
            hooks_dir = repo_path / ".git" / "hooks"
            
            if not hooks_dir.exists():
                raise LevoxException(f"Not a git repository: {git_repo_path}")
            
            # Generate hook content
            hook_content = self.generate_git_hook(precommit_config, hook_type)
            
            # Write hook file
            hook_file = hooks_dir / hook_type
            hook_file.write_text(hook_content)
            hook_file.chmod(0o755)  # Make executable
            
            logger.info(f"Git {hook_type} hook installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install git hook: {e}")
            return False
    
    def _validate_license_tier(self, precommit_config: PreCommitConfig):
        """Validate that license tier supports requested features."""
        license_features = self.config.license.features
        
        # Pre-commit hooks are available in all tiers
        # But some features might be limited
        if precommit_config.max_scan_time_seconds > 30 and precommit_config.license_tier == LicenseTier.STARTER:
            precommit_config.max_scan_time_seconds = 30
            logger.warning("Max scan time limited to 30 seconds in Starter tier")
    
    def _generate_precommit_yaml(self, config: PreCommitConfig) -> str:
        """Generate .pre-commit-config.yaml content."""
        exclude_patterns = "|".join(config.exclude_patterns)
        
        yaml_content = f"""# Levox Pre-commit Configuration
# Generated for {config.license_tier.value} tier
# Max scan time: {config.max_scan_time_seconds}s

repos:
  - repo: local
    hooks:
      - id: {config.custom_hook_name}
        name: Levox Security Scan
        entry: levox scan
        language: system
        args: [
          "--format", "json",
          "--output", "levox-precommit-results.json",
          "--verbosity", "summary",
          "--max-file-size-mb", "5",
          "--exclude-patterns", "{exclude_patterns}",
          "--fail-on", "{config.fail_on_severity}"
        ]
        files: \\.(py|js|ts|java|go|rs|cpp|c|h|php|rb|swift|kt|scala|clj|hs|ml|fs|vb|cs|dart|r|m|pl|sh|bash|zsh|fish|ps1|bat|cmd)$
        exclude: |
          (?x)^(
            .*\\.min\\.(js|css)|
            .*\\.bundle\\.(js|css)|
            .*/node_modules/.*|
            .*/vendor/.*|
            .*\\.lock$|
            .*\\.log$|
            .*/dist/.*|
            .*/build/.*|
            .*/target/.*|
            .*\\.pyc$|
            .*/__pycache__/.*
          )$
        pass_filenames: true
        always_run: false
        verbose: true
        stages: [commit]
        minimum_pre_commit_version: 2.0.0

  # Additional security hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: check-executables-have-shebangs
      - id: check-shebang-scripts-are-executable

  # Python-specific hooks (if applicable)
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
        args: [--line-length=88]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  # JavaScript/TypeScript hooks (if applicable)
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.40.0
    hooks:
      - id: eslint
        files: \\.(js|jsx|ts|tsx)$
        types: [file]
        additional_dependencies: [eslint@8.40.0]

# Configuration for Levox-specific settings
ci:
  autofix_commit_msg: |
    [pre-commit.ci] auto fixes from pre-commit.com hooks

    for more information, see https://pre-commit.ci
  autofix_prs: true
  autoupdate_branch: ''
  autoupdate_commit_msg: '[pre-commit.ci] pre-commit autoupdate'
  autoupdate_schedule: weekly
  skip: []
  submodules: false
"""
        return yaml_content
    
    def _generate_precommit_hook(self, config: PreCommitConfig) -> str:
        """Generate pre-commit git hook script."""
        exclude_patterns = " ".join([f"'{pattern}'" for pattern in config.exclude_patterns])
        
        hook_script = f"""#!/bin/bash
# Levox Pre-commit Hook
# Generated for {config.license_tier.value} tier
# Max scan time: {config.max_scan_time_seconds}s

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Levox Pre-commit Security Scan${NC}"
echo -e "${BLUE}License tier: {config.license_tier.value}${NC}"
echo -e "${BLUE}Max scan time: {config.max_scan_time_seconds}s${NC}"
echo

# Check if Levox is installed
if ! command -v levox &> /dev/null; then
    echo -e "${RED}❌ Levox CLI not found. Please install Levox first.${NC}"
    echo -e "${YELLOW}Install with: pip install levox-cli${NC}"
    exit 1
fi

# Get staged files
if [ "$1" = "--staged-only" ]; then
    STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\\.(py|js|ts|java|go|rs|cpp|c|h|php|rb|swift|kt|scala|clj|hs|ml|fs|vb|cs|dart|r|m|pl|sh|bash|zsh|fish|ps1|bat|cmd)$' || true)
    
    if [ -z "$STAGED_FILES" ]; then
        echo -e "${GREEN}✅ No staged files to scan${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}📁 Scanning staged files:${NC}"
    echo "$STAGED_FILES" | sed 's/^/  /'
    echo
    
    # Create temporary file list
    TEMP_FILE_LIST=$(mktemp)
    echo "$STAGED_FILES" > "$TEMP_FILE_LIST"
    
    # Run Levox scan on staged files
    timeout {config.max_scan_time_seconds}s levox scan \\
        --file-list "$TEMP_FILE_LIST" \\
        --format json \\
        --output levox-precommit-results.json \\
        --verbosity summary \\
        --max-file-size-mb 5 \\
        --exclude-patterns {exclude_patterns} \\
        --fail-on {config.fail_on_severity} || SCAN_EXIT_CODE=$?
    
    # Clean up
    rm -f "$TEMP_FILE_LIST"
else
    # Scan entire repository (slower)
    echo -e "${BLUE}📁 Scanning entire repository${NC}"
    
    timeout {config.max_scan_time_seconds}s levox scan \\
        . \\
        --format json \\
        --output levox-precommit-results.json \\
        --verbosity summary \\
        --max-file-size-mb 5 \\
        --exclude-patterns {exclude_patterns} \\
        --fail-on {config.fail_on_severity} || SCAN_EXIT_CODE=$?
fi

# Check scan results
if [ -f levox-precommit-results.json ]; then
    VIOLATIONS=$(jq '.scan_results.violations | length' levox-precommit-results.json 2>/dev/null || echo "0")
    HIGH_VIOLATIONS=$(jq '.scan_results.violations | map(select(.severity == "HIGH")) | length' levox-precommit-results.json 2>/dev/null || echo "0")
    MEDIUM_VIOLATIONS=$(jq '.scan_results.violations | map(select(.severity == "MEDIUM")) | length' levox-precommit-results.json 2>/dev/null || echo "0")
    LOW_VIOLATIONS=$(jq '.scan_results.violations | map(select(.severity == "LOW")) | length' levox-precommit-results.json 2>/dev/null || echo "0")
    
    echo -e "${BLUE}📊 Scan Results:${NC}"
    echo -e "  Total violations: $VIOLATIONS"
    echo -e "  High severity: $HIGH_VIOLATIONS"
    echo -e "  Medium severity: $MEDIUM_VIOLATIONS"
    echo -e "  Low severity: $LOW_VIOLATIONS"
    echo
    
    # Determine if we should fail
    if [ "$SCAN_EXIT_CODE" = "124" ]; then
        echo -e "${YELLOW}⚠️ Scan timed out after {config.max_scan_time_seconds}s${NC}"
        echo -e "${YELLOW}Consider increasing max scan time or reducing scan scope${NC}"
        exit 1
    elif [ "$SCAN_EXIT_CODE" = "1" ]; then
        echo -e "${RED}❌ Security violations found!${NC}"
        echo -e "${RED}Commit blocked due to security issues.${NC}"
        echo -e "${YELLOW}Run 'levox scan' for detailed results.${NC}"
        exit 1
    elif [ "$HIGH_VIOLATIONS" -gt 0 ] && [ "{config.fail_on_severity}" = "HIGH" ]; then
        echo -e "${RED}❌ High severity violations found: $HIGH_VIOLATIONS${NC}"
        echo -e "${RED}Commit blocked due to high severity security issues.${NC}"
        echo -e "${YELLOW}Run 'levox scan' for detailed results.${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Security scan passed${NC}"
        if [ "$VIOLATIONS" -gt 0 ]; then
            echo -e "${YELLOW}⚠️ Found $VIOLATIONS violations (below failure threshold)${NC}"
        fi
    fi
else
    echo -e "${RED}❌ Scan failed - no results file generated${NC}"
    exit 1
fi

# Clean up results file
rm -f levox-precommit-results.json

echo -e "${GREEN}✅ Pre-commit security check completed${NC}"
"""
        return hook_script
    
    def _generate_prepush_hook(self, config: PreCommitConfig) -> str:
        """Generate pre-push git hook script."""
        exclude_patterns = " ".join([f"'{pattern}'" for pattern in config.exclude_patterns])
        
        hook_script = f"""#!/bin/bash
# Levox Pre-push Hook
# Generated for {config.license_tier.value} tier
# Max scan time: {config.max_scan_time_seconds}s

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Levox Pre-push Security Scan${NC}"
echo -e "${BLUE}License tier: {config.license_tier.value}${NC}"
echo -e "${BLUE}Max scan time: {config.max_scan_time_seconds}s${NC}"
echo

# Check if Levox is installed
if ! command -v levox &> /dev/null; then
    echo -e "${RED}❌ Levox CLI not found. Please install Levox first.${NC}"
    echo -e "${YELLOW}Install with: pip install levox-cli${NC}"
    exit 1
fi

# Get changed files in the push
CHANGED_FILES=$(git diff --name-only $1 $2 | grep -E '\\.(py|js|ts|java|go|rs|cpp|c|h|php|rb|swift|kt|scala|clj|hs|ml|fs|vb|cs|dart|r|m|pl|sh|bash|zsh|fish|ps1|bat|cmd)$' || true)

if [ -z "$CHANGED_FILES" ]; then
    echo -e "${GREEN}✅ No changed files to scan${NC}"
    exit 0
fi

echo -e "${BLUE}📁 Scanning changed files:${NC}"
echo "$CHANGED_FILES" | sed 's/^/  /'

echo

# Create temporary file list
TEMP_FILE_LIST=$(mktemp)
echo "$CHANGED_FILES" > "$TEMP_FILE_LIST"

# Run Levox scan on changed files
timeout {config.max_scan_time_seconds}s levox scan \\
    --file-list "$TEMP_FILE_LIST" \\
    --format json \\
    --output levox-prepush-results.json \\
    --verbosity summary \\
    --max-file-size-mb 10 \\
    --exclude-patterns {exclude_patterns} \\
    --fail-on {config.fail_on_severity} || SCAN_EXIT_CODE=$?

# Clean up
rm -f "$TEMP_FILE_LIST"

# Check scan results
if [ -f levox-prepush-results.json ]; then
    VIOLATIONS=$(jq '.scan_results.violations | length' levox-prepush-results.json 2>/dev/null || echo "0")
    HIGH_VIOLATIONS=$(jq '.scan_results.violations | map(select(.severity == "HIGH")) | length' levox-prepush-results.json 2>/dev/null || echo "0")
    
    echo -e "${BLUE}📊 Scan Results:${NC}"
    echo -e "  Total violations: $VIOLATIONS"
    echo -e "  High severity: $HIGH_VIOLATIONS"
    echo
    
    # Determine if we should fail
    if [ "$SCAN_EXIT_CODE" = "124" ]; then
        echo -e "${YELLOW}⚠️ Scan timed out after {config.max_scan_time_seconds}s${NC}"
        echo -e "${YELLOW}Consider increasing max scan time or reducing scan scope${NC}"
        exit 1
    elif [ "$SCAN_EXIT_CODE" = "1" ]; then
        echo -e "${RED}❌ Security violations found!${NC}"
        echo -e "${RED}Push blocked due to security issues.${NC}"
        echo -e "${YELLOW}Run 'levox scan' for detailed results.${NC}"
        exit 1
    elif [ "$HIGH_VIOLATIONS" -gt 0 ] && [ "{config.fail_on_severity}" = "HIGH" ]; then
        echo -e "${RED}❌ High severity violations found: $HIGH_VIOLATIONS${NC}"
        echo -e "${RED}Push blocked due to high severity security issues.${NC}"
        echo -e "${YELLOW}Run 'levox scan' for detailed results.${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Security scan passed${NC}"
        if [ "$VIOLATIONS" -gt 0 ]; then
            echo -e "${YELLOW}⚠️ Found $VIOLATIONS violations (below failure threshold)${NC}"
        fi
    fi
else
    echo -e "${RED}❌ Scan failed - no results file generated${NC}"
    exit 1
fi

# Clean up results file
rm -f levox-prepush-results.json

echo -e "${GREEN}✅ Pre-push security check completed${NC}"
"""
        return hook_script
    
    def validate_precommit_config(self, config: PreCommitConfig) -> Tuple[bool, List[str]]:
        """Validate pre-commit configuration."""
        errors = []
        
        # Check scan time limits
        if config.max_scan_time_seconds < 5:
            errors.append("Max scan time must be at least 5 seconds")
        elif config.max_scan_time_seconds > 300:
            errors.append("Max scan time should not exceed 300 seconds")
        
        # Check severity level
        if config.fail_on_severity not in ["HIGH", "MEDIUM", "LOW"]:
            errors.append("Fail on severity must be HIGH, MEDIUM, or LOW")
        
        # Check hook name
        if not config.custom_hook_name or len(config.custom_hook_name) < 3:
            errors.append("Custom hook name must be at least 3 characters")
        
        return len(errors) == 0, errors
    
    def test_precommit_hook(self, git_repo_path: str, hook_type: str = "pre-commit") -> bool:
        """Test pre-commit hook installation."""
        try:
            repo_path = Path(git_repo_path)
            hook_file = repo_path / ".git" / "hooks" / hook_type
            
            if not hook_file.exists():
                return False
            
            # Check if hook is executable
            if not os.access(hook_file, os.X_OK):
                return False
            
            # Check if hook contains Levox references
            hook_content = hook_file.read_text()
            return "Levox" in hook_content and "levox scan" in hook_content
            
        except Exception as e:
            logger.error(f"Failed to test pre-commit hook: {e}")
            return False
