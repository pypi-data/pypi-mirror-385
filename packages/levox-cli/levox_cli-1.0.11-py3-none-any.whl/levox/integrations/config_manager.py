"""
Levox Configuration Manager for CI/CD Integration

Manages configuration files, environment-specific settings, and integration
with existing Levox configuration system.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

from ..core.config import Config, LicenseTier
from ..core.exceptions import LevoxException

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Environment types for configuration."""
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"
    CI = "ci"
    LOCAL = "local"


@dataclass
class CIConfig:
    """CI/CD specific configuration."""
    environment: Environment = Environment.CI
    scan_profile: str = "balanced"
    fail_on_severity: str = "HIGH"
    enable_sarif: bool = True
    enable_caching: bool = True
    max_file_size_mb: int = 10
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*.min.js", "*.bundle.js", "node_modules/**", "vendor/**", "*.lock", "*.log"
    ])
    custom_rules: List[str] = field(default_factory=list)
    output_formats: List[str] = field(default_factory=lambda: ["json", "sarif"])
    timeout_seconds: int = 300
    parallel_jobs: int = 4
    memory_limit_mb: int = 2048


class ConfigManager:
    """Manages configuration files and environment-specific settings."""
    
    def __init__(self, config: Config):
        self.config = config
        self.config_dir = Path.home() / ".levox" / "config"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_levoxrc(self, ci_config: CIConfig, output_path: Optional[str] = None) -> str:
        """
        Generate .levoxrc configuration file.
        
        Args:
            ci_config: CI/CD configuration
            output_path: Optional path to save the configuration
            
        Returns:
            Generated .levoxrc content
        """
        try:
            # Validate configuration
            is_valid, errors = self.validate_ci_config(ci_config)
            if not is_valid:
                raise LevoxException(f"Invalid CI configuration: {', '.join(errors)}")
            
            # Generate configuration content
            config_content = self._generate_levoxrc_content(ci_config)
            
            # Save configuration if output path specified
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(config_content)
                logger.info(f"Configuration saved to: {output_file}")
            
            return config_content
            
        except Exception as e:
            logger.error(f"Failed to generate .levoxrc: {e}")
            raise LevoxException(f"Configuration generation failed: {e}")
    
    def generate_env_config(self, ci_config: CIConfig, environment: Environment, output_path: Optional[str] = None) -> str:
        """
        Generate environment-specific configuration.
        
        Args:
            ci_config: Base CI/CD configuration
            environment: Target environment
            output_path: Optional path to save the configuration
            
        Returns:
            Generated environment configuration content
        """
        try:
            # Adjust configuration for environment
            env_config = self._adjust_config_for_environment(ci_config, environment)
            
            # Generate configuration content
            config_content = self._generate_env_config_content(env_config, environment)
            
            # Save configuration if output path specified
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(config_content)
                logger.info(f"Environment configuration saved to: {output_file}")
            
            return config_content
            
        except Exception as e:
            logger.error(f"Failed to generate environment configuration: {e}")
            raise LevoxException(f"Environment configuration generation failed: {e}")
    
    def load_existing_config(self, config_path: str) -> Optional[CIConfig]:
        """
        Load existing configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Loaded CI configuration or None if failed
        """
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                return None
            
            if config_file.suffix == '.json':
                with open(config_file, 'r') as f:
                    data = json.load(f)
            elif config_file.suffix in ['.yml', '.yaml']:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f)
            else:
                # Try to parse as .levoxrc format
                content = config_file.read_text()
                data = self._parse_levoxrc_content(content)
            
            return self._dict_to_ci_config(data)
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return None
    
    def merge_configs(self, base_config: CIConfig, override_config: CIConfig) -> CIConfig:
        """
        Merge two configurations with override taking precedence.
        
        Args:
            base_config: Base configuration
            override_config: Override configuration
            
        Returns:
            Merged configuration
        """
        try:
            # Convert to dict for easier merging
            base_dict = self._ci_config_to_dict(base_config)
            override_dict = self._ci_config_to_dict(override_config)
            
            # Merge configurations
            merged_dict = {**base_dict, **override_dict}
            
            # Handle list fields specially
            if override_config.exclude_patterns:
                merged_dict['exclude_patterns'] = override_config.exclude_patterns
            if override_config.custom_rules:
                merged_dict['custom_rules'] = override_config.custom_rules
            if override_config.output_formats:
                merged_dict['output_formats'] = override_config.output_formats
            
            return self._dict_to_ci_config(merged_dict)
            
        except Exception as e:
            logger.error(f"Failed to merge configurations: {e}")
            return base_config
    
    def _generate_levoxrc_content(self, ci_config: CIConfig) -> str:
        """Generate .levoxrc configuration content."""
        exclude_patterns = " ".join(ci_config.exclude_patterns)
        custom_rules = " ".join(ci_config.custom_rules) if ci_config.custom_rules else ""
        output_formats = " ".join(ci_config.output_formats)
        
        content = f"""# Levox Configuration File
# Generated for {ci_config.environment.value} environment
# License tier: {self.config.license.tier.value}

# Environment settings
environment = {ci_config.environment.value}

# Scan configuration
scan_profile = {ci_config.scan_profile}
fail_on_severity = {ci_config.fail_on_severity}
max_file_size_mb = {ci_config.max_file_size_mb}
timeout_seconds = {ci_config.timeout_seconds}

# Performance settings
parallel_jobs = {ci_config.parallel_jobs}
memory_limit_mb = {ci_config.memory_limit_mb}

# Output configuration
output_formats = {output_formats}
enable_sarif = {str(ci_config.enable_sarif).lower()}
enable_caching = {str(ci_config.enable_caching).lower()}

# File patterns
exclude_patterns = {exclude_patterns}

# Custom rules
{custom_rules and f'custom_rules = {custom_rules}' or '# No custom rules defined'}

# License configuration
license_tier = {self.config.license.tier.value}
license_key = ${{LEVOX_LICENSE_KEY}}

# Logging configuration
log_level = INFO
debug_mode = false

# CI/CD specific settings
ci_mode = true
fail_fast = true
artifact_retention_days = 30

# Security settings
secret_verification = true
crypto_verification = {str(self.config.license.features.get('crypto_verification', False)).lower()}

# Advanced features (based on license tier)
ast_analysis = {str(self.config.license.features.get('ast_analysis', False)).lower()}
context_analysis = {str(self.config.license.features.get('context_analysis', False)).lower()}
cfg_analysis = {str(self.config.license.features.get('cfg_analysis', False)).lower()}
dataflow_analysis = {str(self.config.license.features.get('dataflow_analysis', False)).lower()}
ml_filtering = {str(self.config.license.features.get('ml_filtering', False)).lower()}
"""
        return content
    
    def _generate_env_config_content(self, ci_config: CIConfig, environment: Environment) -> str:
        """Generate environment-specific configuration content."""
        config_data = {
            "environment": environment.value,
            "scan_profile": ci_config.scan_profile,
            "fail_on_severity": ci_config.fail_on_severity,
            "enable_sarif": ci_config.enable_sarif,
            "enable_caching": ci_config.enable_caching,
            "max_file_size_mb": ci_config.max_file_size_mb,
            "exclude_patterns": ci_config.exclude_patterns,
            "custom_rules": ci_config.custom_rules,
            "output_formats": ci_config.output_formats,
            "timeout_seconds": ci_config.timeout_seconds,
            "parallel_jobs": ci_config.parallel_jobs,
            "memory_limit_mb": ci_config.memory_limit_mb,
            "license_tier": self.config.license.tier.value,
            "features": self.config.license.features
        }
        
        return yaml.dump(config_data, default_flow_style=False, sort_keys=False)
    
    def _adjust_config_for_environment(self, ci_config: CIConfig, environment: Environment) -> CIConfig:
        """Adjust configuration based on environment."""
        adjusted_config = CIConfig(
            environment=environment,
            scan_profile=ci_config.scan_profile,
            fail_on_severity=ci_config.fail_on_severity,
            enable_sarif=ci_config.enable_sarif,
            enable_caching=ci_config.enable_caching,
            max_file_size_mb=ci_config.max_file_size_mb,
            exclude_patterns=ci_config.exclude_patterns.copy(),
            custom_rules=ci_config.custom_rules.copy(),
            output_formats=ci_config.output_formats.copy(),
            timeout_seconds=ci_config.timeout_seconds,
            parallel_jobs=ci_config.parallel_jobs,
            memory_limit_mb=ci_config.memory_limit_mb
        )
        
        # Environment-specific adjustments
        if environment == Environment.DEVELOPMENT:
            adjusted_config.scan_profile = "quick"
            adjusted_config.fail_on_severity = "HIGH"
            adjusted_config.timeout_seconds = 60
            adjusted_config.parallel_jobs = 2
        elif environment == Environment.STAGING:
            adjusted_config.scan_profile = "balanced"
            adjusted_config.fail_on_severity = "HIGH"
            adjusted_config.timeout_seconds = 180
        elif environment == Environment.PRODUCTION:
            adjusted_config.scan_profile = "thorough"
            adjusted_config.fail_on_severity = "MEDIUM"
            adjusted_config.timeout_seconds = 600
            adjusted_config.parallel_jobs = 8
        elif environment == Environment.CI:
            adjusted_config.scan_profile = "balanced"
            adjusted_config.fail_on_severity = "HIGH"
            adjusted_config.timeout_seconds = 300
            adjusted_config.enable_caching = True
        elif environment == Environment.LOCAL:
            adjusted_config.scan_profile = "quick"
            adjusted_config.fail_on_severity = "HIGH"
            adjusted_config.timeout_seconds = 30
            adjusted_config.parallel_jobs = 1
        
        return adjusted_config
    
    def _parse_levoxrc_content(self, content: str) -> Dict[str, Any]:
        """Parse .levoxrc content into dictionary."""
        config_data = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle different value types
                    if value.lower() in ['true', 'false']:
                        config_data[key] = value.lower() == 'true'
                    elif value.isdigit():
                        config_data[key] = int(value)
                    elif value.startswith('[') and value.endswith(']'):
                        # Parse list values
                        list_content = value[1:-1]
                        config_data[key] = [item.strip() for item in list_content.split(',') if item.strip()]
                    else:
                        config_data[key] = value
        
        return config_data
    
    def _ci_config_to_dict(self, ci_config: CIConfig) -> Dict[str, Any]:
        """Convert CIConfig to dictionary."""
        return {
            "environment": ci_config.environment.value,
            "scan_profile": ci_config.scan_profile,
            "fail_on_severity": ci_config.fail_on_severity,
            "enable_sarif": ci_config.enable_sarif,
            "enable_caching": ci_config.enable_caching,
            "max_file_size_mb": ci_config.max_file_size_mb,
            "exclude_patterns": ci_config.exclude_patterns,
            "custom_rules": ci_config.custom_rules,
            "output_formats": ci_config.output_formats,
            "timeout_seconds": ci_config.timeout_seconds,
            "parallel_jobs": ci_config.parallel_jobs,
            "memory_limit_mb": ci_config.memory_limit_mb
        }
    
    def _dict_to_ci_config(self, data: Dict[str, Any]) -> CIConfig:
        """Convert dictionary to CIConfig."""
        return CIConfig(
            environment=Environment(data.get("environment", "ci")),
            scan_profile=data.get("scan_profile", "balanced"),
            fail_on_severity=data.get("fail_on_severity", "HIGH"),
            enable_sarif=data.get("enable_sarif", True),
            enable_caching=data.get("enable_caching", True),
            max_file_size_mb=data.get("max_file_size_mb", 10),
            exclude_patterns=data.get("exclude_patterns", []),
            custom_rules=data.get("custom_rules", []),
            output_formats=data.get("output_formats", ["json", "sarif"]),
            timeout_seconds=data.get("timeout_seconds", 300),
            parallel_jobs=data.get("parallel_jobs", 4),
            memory_limit_mb=data.get("memory_limit_mb", 2048)
        )
    
    def validate_ci_config(self, ci_config: CIConfig) -> Tuple[bool, List[str]]:
        """Validate CI configuration."""
        errors = []
        
        # Check environment
        if ci_config.environment not in Environment:
            errors.append(f"Invalid environment: {ci_config.environment}")
        
        # Check scan profile
        valid_profiles = ["quick", "balanced", "thorough", "security"]
        if ci_config.scan_profile not in valid_profiles:
            errors.append(f"Invalid scan profile: {ci_config.scan_profile}")
        
        # Check severity level
        if ci_config.fail_on_severity not in ["HIGH", "MEDIUM", "LOW"]:
            errors.append("Fail on severity must be HIGH, MEDIUM, or LOW")
        
        # Check file size limit
        if ci_config.max_file_size_mb < 1 or ci_config.max_file_size_mb > 1000:
            errors.append("Max file size must be between 1 and 1000 MB")
        
        # Check timeout
        if ci_config.timeout_seconds < 10 or ci_config.timeout_seconds > 3600:
            errors.append("Timeout must be between 10 and 3600 seconds")
        
        # Check parallel jobs
        if ci_config.parallel_jobs < 1 or ci_config.parallel_jobs > 16:
            errors.append("Parallel jobs must be between 1 and 16")
        
        # Check memory limit
        if ci_config.memory_limit_mb < 512 or ci_config.memory_limit_mb > 16384:
            errors.append("Memory limit must be between 512 and 16384 MB")
        
        # Check output formats
        valid_formats = ["json", "html", "pdf", "sarif"]
        for format_type in ci_config.output_formats:
            if format_type not in valid_formats:
                errors.append(f"Invalid output format: {format_type}")
        
        return len(errors) == 0, errors
    
    def get_default_config_for_tier(self, license_tier: LicenseTier) -> CIConfig:
        """Get default configuration based on license tier."""
        base_config = CIConfig()
        
        if license_tier == LicenseTier.STARTER:
            base_config.scan_profile = "quick"
            base_config.enable_sarif = False
            base_config.max_file_size_mb = 5
            base_config.timeout_seconds = 60
            base_config.parallel_jobs = 1
        elif license_tier == LicenseTier.PRO:
            base_config.scan_profile = "balanced"
            base_config.enable_sarif = False
            base_config.max_file_size_mb = 10
            base_config.timeout_seconds = 180
            base_config.parallel_jobs = 2
        elif license_tier == LicenseTier.BUSINESS:
            base_config.scan_profile = "balanced"
            base_config.enable_sarif = True
            base_config.max_file_size_mb = 25
            base_config.timeout_seconds = 300
            base_config.parallel_jobs = 4
        elif license_tier == LicenseTier.ENTERPRISE:
            base_config.scan_profile = "thorough"
            base_config.enable_sarif = True
            base_config.max_file_size_mb = 50
            base_config.timeout_seconds = 600
            base_config.parallel_jobs = 8
        
        return base_config
    
    def create_config_template(self, license_tier: LicenseTier, environment: Environment) -> str:
        """Create a configuration template for a specific tier and environment."""
        default_config = self.get_default_config_for_tier(license_tier)
        env_config = self._adjust_config_for_environment(default_config, environment)
        
        return self.generate_levoxrc(env_config)
