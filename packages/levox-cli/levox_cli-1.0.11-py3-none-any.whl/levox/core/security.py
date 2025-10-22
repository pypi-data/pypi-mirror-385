"""
Security configuration and utilities for Levox.

This module provides centralized security settings, validation functions,
and security-related utilities to ensure safe operation of the application.
"""

import os
import re
import logging
from typing import List, Set, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    
    # File handling security
    max_file_size_mb: int = 100
    max_config_file_size_mb: int = 1
    max_regex_pattern_length: int = 10000
    max_nesting_level: int = 10
    max_quantifiers: int = 50
    
    # Path validation
    allowed_file_extensions: Set[str] = None
    blocked_path_patterns: List[str] = None
    
    # Logging security
    enable_pii_redaction: bool = True
    enable_debug_mode: bool = False
    log_sanitization_patterns: List[str] = None
    
    # Import security
    allowed_libraries: Set[str] = None
    blocked_imports: Set[str] = None
    
    # Error handling
    hide_error_details: bool = True
    enable_security_logging: bool = True
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = {
                '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
                '.go', '.rs', '.php', '.rb', '.cs', '.swift', '.kt',
                '.json', '.yaml', '.yml', '.xml', '.csv', '.txt', '.md',
                '.env', '.ini', '.cfg', '.conf', '.properties'
            }
        
        if self.blocked_path_patterns is None:
            self.blocked_path_patterns = [
                '..', '~', '//', '\\\\', '/etc/', '/proc/', '/sys/',
                'C:\\Windows\\', 'C:\\System32\\', '/usr/bin/', '/bin/'
            ]
        
        if self.log_sanitization_patterns is None:
            self.log_sanitization_patterns = [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',  # Phone
                r'\b[A-Za-z0-9+/=]{20,}\b',  # Base64-like strings
                r'\b[A-Z]{2}\d{6,9}\b',  # Passport
                r'\b[A-Z]\d{7}\b',  # Driver license
            ]
        
        if self.allowed_libraries is None:
            self.allowed_libraries = {
                'numpy', 'pandas', 'sklearn', 'scipy', 'matplotlib', 'seaborn',
                'requests', 'urllib3', 'json', 'yaml', 'csv', 'xml', 're',
                'datetime', 'time', 'os', 'sys', 'pathlib', 'collections',
                'itertools', 'functools', 'operator', 'math', 'statistics',
                'hashlib', 'base64', 'uuid', 'logging', 'threading', 'asyncio'
            }
        
        if self.blocked_imports is None:
            self.blocked_imports = {
                'subprocess', 'os.system', 'eval', 'exec', 'compile',
                '__import__', 'importlib.import_module', 'imp', 'pkgutil'
            }


class SecurityValidator:
    """Security validation utilities."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def validate_file_path(self, file_path: Path) -> bool:
        """Validate file path for security issues."""
        try:
            path_str = str(file_path.resolve())
            
            # Check for blocked patterns
            for pattern in self.config.blocked_path_patterns:
                if pattern in path_str:
                    logger.warning(f"Blocked path pattern detected: {pattern}")
                    return False
            
            # Check file extension
            if file_path.suffix.lower() not in self.config.allowed_file_extensions:
                logger.warning(f"Blocked file extension: {file_path.suffix}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return False
    
    def validate_regex_pattern(self, pattern: str) -> bool:
        """Validate regex pattern for security issues."""
        try:
            # Check length
            if len(pattern) > self.config.max_regex_pattern_length:
                logger.warning(f"Regex pattern too long: {len(pattern)} characters")
                return False
            
            # Check for dangerous patterns
            dangerous_patterns = [
                r'\(\?\=.*\*',  # Positive lookahead with quantifier
                r'\(\?\=.*\+',  # Positive lookahead with quantifier
                r'\(\?\=.*\{',  # Positive lookahead with quantifier
                r'\(\?\=.*\?',  # Positive lookahead with quantifier
            ]
            
            for dangerous_pattern in dangerous_patterns:
                if re.search(dangerous_pattern, pattern):
                    logger.warning(f"Dangerous regex pattern detected: {dangerous_pattern}")
                    return False
            
            # Check nesting level
            nesting_level = 0
            for char in pattern:
                if char == '(':
                    nesting_level += 1
                    if nesting_level > self.config.max_nesting_level:
                        logger.warning(f"Regex nesting too deep: {nesting_level} levels")
                        return False
                elif char == ')':
                    nesting_level -= 1
                    if nesting_level < 0:
                        logger.warning("Unbalanced parentheses in regex")
                        return False
            
            # Check quantifier count
            quantifier_count = len(re.findall(r'[\*\+\?\{]', pattern))
            if quantifier_count > self.config.max_quantifiers:
                logger.warning(f"Too many quantifiers: {quantifier_count}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Regex validation error: {e}")
            return False
    
    def validate_import(self, module_name: str) -> bool:
        """Validate module import for security."""
        try:
            # Check if module is in blocked list
            if module_name in self.config.blocked_imports:
                logger.warning(f"Blocked import detected: {module_name}")
                return False
            
            # Check if module is in allowed list
            base_module = module_name.split('.')[0]
            if base_module not in self.config.allowed_libraries:
                logger.warning(f"Module not in allowed list: {base_module}")
                return False
            
            # Validate module name format
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', module_name):
                logger.warning(f"Invalid module name format: {module_name}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Import validation error: {e}")
            return False
    
    def sanitize_for_logging(self, text: str) -> str:
        """Sanitize text for logging to prevent PII exposure."""
        if not self.config.enable_pii_redaction:
            return text
        
        sanitized = text
        for pattern in self.config.log_sanitization_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        return sanitized


class SecurityLogger:
    """Secure logging utilities."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.validator = SecurityValidator(config)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], level: SecurityLevel = SecurityLevel.MEDIUM):
        """Log a security-related event."""
        if not self.config.enable_security_logging:
            return
        
        # Sanitize details
        sanitized_details = {}
        for key, value in details.items():
            if isinstance(value, str):
                sanitized_details[key] = self.validator.sanitize_for_logging(value)
            else:
                sanitized_details[key] = value
        
        log_message = f"SECURITY: {event_type} - {level.value}"
        logger.warning(log_message, extra={
            'security_event': True,
            'event_type': event_type,
            'security_level': level.value,
            'details': sanitized_details
        })
    
    def log_file_access(self, file_path: Path, operation: str, success: bool):
        """Log file access events."""
        if not self.config.enable_security_logging:
            return
        
        level = SecurityLevel.LOW if success else SecurityLevel.MEDIUM
        self.log_security_event(
            "file_access",
            {
                'file_path': str(file_path),
                'operation': operation,
                'success': success
            },
            level
        )
    
    def log_pattern_compilation(self, pattern_name: str, success: bool, error: Optional[str] = None):
        """Log regex pattern compilation events."""
        if not self.config.enable_security_logging:
            return
        
        level = SecurityLevel.LOW if success else SecurityLevel.MEDIUM
        details = {
            'pattern_name': pattern_name,
            'success': success
        }
        
        if error:
            details['error'] = self.validator.sanitize_for_logging(error)
        
        self.log_security_event("pattern_compilation", details, level)
    
    def log_import_attempt(self, module_name: str, success: bool):
        """Log module import attempts."""
        if not self.config.enable_security_logging:
            return
        
        level = SecurityLevel.LOW if success else SecurityLevel.HIGH
        self.log_security_event(
            "import_attempt",
            {
                'module_name': module_name,
                'success': success
            },
            level
        )


def get_security_config() -> SecurityConfig:
    """Get security configuration from environment variables."""
    config = SecurityConfig()
    
    # Override with environment variables
    if os.getenv('LEVOX_DEBUG', '').lower() in ('1', 'true', 'yes'):
        config.enable_debug_mode = True
        config.hide_error_details = False
    
    if os.getenv('LEVOX_SECURE_MODE', '').lower() in ('1', 'true', 'yes'):
        config.enable_pii_redaction = True
        config.enable_security_logging = True
        config.hide_error_details = True
    
    # File size limits
    max_file_size = os.getenv('LEVOX_MAX_FILE_SIZE_MB')
    if max_file_size:
        try:
            config.max_file_size_mb = int(max_file_size)
        except ValueError:
            logger.warning(f"Invalid LEVOX_MAX_FILE_SIZE_MB: {max_file_size}")
    
    return config


# Global security configuration
_security_config = get_security_config()
_security_logger = SecurityLogger(_security_config)
_security_validator = SecurityValidator(_security_config)


def get_security_logger() -> SecurityLogger:
    """Get the global security logger instance."""
    return _security_logger


def get_security_validator() -> SecurityValidator:
    """Get the global security validator instance."""
    return _security_validator


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return _security_config.enable_debug_mode


def should_hide_error_details() -> bool:
    """Check if error details should be hidden."""
    return _security_config.hide_error_details
