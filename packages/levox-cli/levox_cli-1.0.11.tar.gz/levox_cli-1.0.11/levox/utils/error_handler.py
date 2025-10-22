"""
Error Handler for Levox CLI

Provides contextual error messages, recovery suggestions, and standardized
error handling with user-friendly guidance.
"""

import os
import sys
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ErrorType(str, Enum):
    """Types of errors that can occur in Levox."""
    # File and path errors
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    INVALID_PATH = "invalid_path"
    PATH_TOO_LONG = "path_too_long"
    
    # Network and connectivity errors
    NETWORK_ERROR = "network_error"
    CONNECTION_TIMEOUT = "connection_timeout"
    DNS_ERROR = "dns_error"
    SSL_ERROR = "ssl_error"
    
    # License and authentication errors
    LICENSE_EXPIRED = "license_expired"
    LICENSE_INVALID = "license_invalid"
    AUTHENTICATION_FAILED = "authentication_failed"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # Configuration errors
    CONFIG_ERROR = "config_error"
    MISSING_CONFIG = "missing_config"
    INVALID_CONFIG = "invalid_config"
    
    # Git and repository errors
    GIT_CLONE_FAILED = "git_clone_failed"
    GIT_AUTH_FAILED = "git_auth_failed"
    REPOSITORY_NOT_FOUND = "repository_not_found"
    REPOSITORY_TOO_LARGE = "repository_too_large"
    
    # ML and model errors
    ML_MODEL_NOT_FOUND = "ml_model_not_found"
    ML_MODEL_LOAD_FAILED = "ml_model_load_failed"
    ML_INFERENCE_FAILED = "ml_inference_failed"
    
    # Memory and performance errors
    OUT_OF_MEMORY = "out_of_memory"
    SCAN_TIMEOUT = "scan_timeout"
    TOO_MANY_FILES = "too_many_files"
    
    # Generic errors
    UNKNOWN_ERROR = "unknown_error"
    INTERNAL_ERROR = "internal_error"


@dataclass
class ErrorContext:
    """Context information for an error."""
    error_type: ErrorType
    original_error: Exception
    user_message: str
    recovery_suggestions: List[str]
    error_code: str
    documentation_url: Optional[str] = None
    can_retry: bool = False
    retry_delay: int = 0  # seconds
    severity: str = "error"  # info, warning, error, critical


class ErrorHandler:
    """Centralized error handling with contextual messages and recovery suggestions."""
    
    def __init__(self):
        """Initialize the error handler."""
        self.logger = logging.getLogger(__name__)
        self.error_patterns = self._build_error_patterns()
        self.recovery_strategies = self._build_recovery_strategies()
    
    def _build_error_patterns(self) -> Dict[str, ErrorType]:
        """Build patterns for error type detection."""
        return {
            # File and path errors
            "No such file or directory": ErrorType.FILE_NOT_FOUND,
            "FileNotFoundError": ErrorType.FILE_NOT_FOUND,
            "Permission denied": ErrorType.PERMISSION_DENIED,
            "PermissionError": ErrorType.PERMISSION_DENIED,
            "Access is denied": ErrorType.PERMISSION_DENIED,
            "Invalid path": ErrorType.INVALID_PATH,
            "Path too long": ErrorType.PATH_TOO_LONG,
            
            # Network errors
            "Connection refused": ErrorType.NETWORK_ERROR,
            "Connection timeout": ErrorType.CONNECTION_TIMEOUT,
            "TimeoutError": ErrorType.CONNECTION_TIMEOUT,
            "DNS resolution failed": ErrorType.DNS_ERROR,
            "SSL certificate": ErrorType.SSL_ERROR,
            "SSL: CERTIFICATE_VERIFY_FAILED": ErrorType.SSL_ERROR,
            
            # License errors
            "License expired": ErrorType.LICENSE_EXPIRED,
            "Invalid license": ErrorType.LICENSE_INVALID,
            "Authentication failed": ErrorType.AUTHENTICATION_FAILED,
            "Rate limit exceeded": ErrorType.RATE_LIMIT_EXCEEDED,
            
            # Git errors
            "Repository not found": ErrorType.REPOSITORY_NOT_FOUND,
            "Authentication failed for": ErrorType.GIT_AUTH_FAILED,
            "Clone failed": ErrorType.GIT_CLONE_FAILED,
            "Repository too large": ErrorType.REPOSITORY_TOO_LARGE,
            
            # ML errors
            "Model not found": ErrorType.ML_MODEL_NOT_FOUND,
            "Model load failed": ErrorType.ML_MODEL_LOAD_FAILED,
            "Inference failed": ErrorType.ML_INFERENCE_FAILED,
            
            # Memory errors
            "Out of memory": ErrorType.OUT_OF_MEMORY,
            "MemoryError": ErrorType.OUT_OF_MEMORY,
            "Scan timeout": ErrorType.SCAN_TIMEOUT,
            "Too many files": ErrorType.TOO_MANY_FILES,
        }
    
    def _build_recovery_strategies(self) -> Dict[ErrorType, List[str]]:
        """Build recovery strategies for each error type."""
        return {
            ErrorType.FILE_NOT_FOUND: [
                "Check if the file path is correct",
                "Use absolute path instead of relative path",
                "Verify the file exists: ls -la <path>",
                "Check if you have permission to access the file"
            ],
            ErrorType.PERMISSION_DENIED: [
                "Run with appropriate permissions (sudo if needed)",
                "Check file/directory permissions: chmod 755 <path>",
                "Verify you own the file: chown <user> <path>",
                "Try running from a different directory"
            ],
            ErrorType.INVALID_PATH: [
                "Check for special characters in the path",
                "Use forward slashes (/) instead of backslashes (\\)",
                "Avoid spaces in path names or use quotes",
                "Check if the path is too long"
            ],
            ErrorType.NETWORK_ERROR: [
                "Check your internet connection",
                "Try again in a few minutes",
                "Use a VPN if behind a corporate firewall",
                "Check if the service is down"
            ],
            ErrorType.CONNECTION_TIMEOUT: [
                "Increase timeout settings",
                "Check your internet connection speed",
                "Try again during off-peak hours",
                "Use a different network"
            ],
            ErrorType.LICENSE_EXPIRED: [
                "Renew your license: levox license --renew",
                "Upgrade to a higher tier: levox license --upgrade",
                "Contact support: support@levox.security",
                "Check license status: levox license --status"
            ],
            ErrorType.LICENSE_INVALID: [
                "Verify your license key: levox license --verify",
                "Re-register your license: levox license --register",
                "Contact support with your license details",
                "Check if you're using the correct license key"
            ],
            ErrorType.GIT_CLONE_FAILED: [
                "Check if the repository URL is correct",
                "Verify you have access to the repository",
                "Try using SSH instead of HTTPS",
                "Check your Git credentials: git config --list"
            ],
            ErrorType.GIT_AUTH_FAILED: [
                "Set up Git credentials: git config --global user.name",
                "Use personal access token for authentication",
                "Check SSH key setup: ssh -T git@github.com",
                "Try using HTTPS with token authentication"
            ],
            ErrorType.REPOSITORY_TOO_LARGE: [
                "Use shallow clone: --depth 1",
                "Try sparse checkout for specific files",
                "Scan only specific directories",
                "Use incremental scanning"
            ],
            ErrorType.ML_MODEL_NOT_FOUND: [
                "Download the model: levox models --download",
                "Check model cache directory",
                "Verify model installation",
                "Reinstall Levox with ML support"
            ],
            ErrorType.OUT_OF_MEMORY: [
                "Reduce concurrent workers: --max-workers 1",
                "Scan smaller directories at a time",
                "Increase system memory",
                "Use incremental scanning"
            ],
            ErrorType.SCAN_TIMEOUT: [
                "Increase timeout: --timeout 600",
                "Scan smaller directories",
                "Use incremental scanning",
                "Reduce file size limits"
            ],
            ErrorType.TOO_MANY_FILES: [
                "Use file filters: --include '*.py'",
                "Exclude large directories: --exclude 'node_modules'",
                "Scan specific subdirectories",
                "Use incremental scanning"
            ]
        }
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorContext:
        """
        Handle an error and provide contextual information.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            ErrorContext with user-friendly information
        """
        error_type = self._detect_error_type(error)
        user_message = self._create_user_message(error, error_type, context)
        recovery_suggestions = self._get_recovery_suggestions(error_type, context)
        error_code = self._generate_error_code(error_type)
        documentation_url = self._get_documentation_url(error_type)
        can_retry = self._can_retry(error_type)
        retry_delay = self._get_retry_delay(error_type)
        severity = self._get_severity(error_type)
        
        return ErrorContext(
            error_type=error_type,
            original_error=error,
            user_message=user_message,
            recovery_suggestions=recovery_suggestions,
            error_code=error_code,
            documentation_url=documentation_url,
            can_retry=can_retry,
            retry_delay=retry_delay,
            severity=severity
        )
    
    def _detect_error_type(self, error: Exception) -> ErrorType:
        """Detect the type of error based on the exception."""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Check patterns
        for pattern, error_type_enum in self.error_patterns.items():
            if pattern.lower() in error_str or pattern in error_type:
                return error_type_enum
        
        # Check specific exception types
        if isinstance(error, FileNotFoundError):
            return ErrorType.FILE_NOT_FOUND
        elif isinstance(error, PermissionError):
            return ErrorType.PERMISSION_DENIED
        elif isinstance(error, TimeoutError):
            return ErrorType.CONNECTION_TIMEOUT
        elif isinstance(error, MemoryError):
            return ErrorType.OUT_OF_MEMORY
        
        return ErrorType.UNKNOWN_ERROR
    
    def _create_user_message(self, error: Exception, error_type: ErrorType, context: Optional[Dict[str, Any]]) -> str:
        """Create a user-friendly error message."""
        base_messages = {
            ErrorType.FILE_NOT_FOUND: "The specified file or directory could not be found",
            ErrorType.PERMISSION_DENIED: "You don't have permission to access this file or directory",
            ErrorType.INVALID_PATH: "The specified path is invalid or malformed",
            ErrorType.NETWORK_ERROR: "A network error occurred while connecting to the service",
            ErrorType.CONNECTION_TIMEOUT: "The connection timed out while waiting for a response",
            ErrorType.LICENSE_EXPIRED: "Your license has expired and needs to be renewed",
            ErrorType.LICENSE_INVALID: "The provided license key is invalid or corrupted",
            ErrorType.GIT_CLONE_FAILED: "Failed to clone the Git repository",
            ErrorType.GIT_AUTH_FAILED: "Git authentication failed - check your credentials",
            ErrorType.REPOSITORY_NOT_FOUND: "The specified repository could not be found",
            ErrorType.REPOSITORY_TOO_LARGE: "The repository is too large to scan efficiently",
            ErrorType.ML_MODEL_NOT_FOUND: "The required machine learning model could not be found",
            ErrorType.ML_MODEL_LOAD_FAILED: "Failed to load the machine learning model",
            ErrorType.OUT_OF_MEMORY: "The scan requires more memory than is available",
            ErrorType.SCAN_TIMEOUT: "The scan took too long and was terminated",
            ErrorType.TOO_MANY_FILES: "The directory contains too many files to scan efficiently",
            ErrorType.UNKNOWN_ERROR: "An unexpected error occurred",
            ErrorType.INTERNAL_ERROR: "An internal error occurred in the application"
        }
        
        message = base_messages.get(error_type, "An error occurred")
        
        # Add context-specific information
        if context:
            if "scan_path" in context:
                message += f" while scanning '{context['scan_path']}'"
            if "file_count" in context:
                message += f" ({context['file_count']} files)"
            if "duration" in context:
                message += f" after {context['duration']:.1f} seconds"
        
        return message
    
    def _get_recovery_suggestions(self, error_type: ErrorType, context: Optional[Dict[str, Any]]) -> List[str]:
        """Get recovery suggestions for an error type."""
        suggestions = self.recovery_strategies.get(error_type, [
            "Check the error message for more details",
            "Try running the command again",
            "Contact support if the problem persists"
        ])
        
        # Add context-specific suggestions
        if context:
            if error_type == ErrorType.FILE_NOT_FOUND and "scan_path" in context:
                suggestions.insert(0, f"Verify the path exists: ls -la '{context['scan_path']}'")
            elif error_type == ErrorType.OUT_OF_MEMORY and "file_count" in context:
                suggestions.insert(0, f"Try scanning fewer files at once (currently {context['file_count']} files)")
            elif error_type == ErrorType.SCAN_TIMEOUT and "duration" in context:
                suggestions.insert(0, f"Try increasing the timeout (current: {context['duration']:.1f}s)")
        
        return suggestions
    
    def _generate_error_code(self, error_type: ErrorType) -> str:
        """Generate a standardized error code."""
        return f"LEVOX_{error_type.value.upper()}"
    
    def _get_documentation_url(self, error_type: ErrorType) -> Optional[str]:
        """Get documentation URL for an error type."""
        base_url = "https://docs.levox.security"
        
        urls = {
            ErrorType.LICENSE_EXPIRED: f"{base_url}/license-management",
            ErrorType.LICENSE_INVALID: f"{base_url}/license-management",
            ErrorType.GIT_CLONE_FAILED: f"{base_url}/repository-scanning",
            ErrorType.GIT_AUTH_FAILED: f"{base_url}/repository-scanning",
            ErrorType.ML_MODEL_NOT_FOUND: f"{base_url}/ml-models",
            ErrorType.OUT_OF_MEMORY: f"{base_url}/performance-tuning",
            ErrorType.SCAN_TIMEOUT: f"{base_url}/performance-tuning",
            ErrorType.TOO_MANY_FILES: f"{base_url}/performance-tuning"
        }
        
        return urls.get(error_type)
    
    def _can_retry(self, error_type: ErrorType) -> bool:
        """Determine if an error can be retried."""
        retryable_errors = {
            ErrorType.NETWORK_ERROR,
            ErrorType.CONNECTION_TIMEOUT,
            ErrorType.DNS_ERROR,
            ErrorType.RATE_LIMIT_EXCEEDED,
            ErrorType.GIT_CLONE_FAILED,
            ErrorType.ML_MODEL_LOAD_FAILED,
            ErrorType.SCAN_TIMEOUT
        }
        
        return error_type in retryable_errors
    
    def _get_retry_delay(self, error_type: ErrorType) -> int:
        """Get the recommended retry delay in seconds."""
        delays = {
            ErrorType.NETWORK_ERROR: 5,
            ErrorType.CONNECTION_TIMEOUT: 10,
            ErrorType.DNS_ERROR: 30,
            ErrorType.RATE_LIMIT_EXCEEDED: 60,
            ErrorType.GIT_CLONE_FAILED: 5,
            ErrorType.ML_MODEL_LOAD_FAILED: 10,
            ErrorType.SCAN_TIMEOUT: 30
        }
        
        return delays.get(error_type, 5)
    
    def _get_severity(self, error_type: ErrorType) -> str:
        """Get the severity level of an error."""
        critical_errors = {
            ErrorType.LICENSE_EXPIRED,
            ErrorType.LICENSE_INVALID,
            ErrorType.OUT_OF_MEMORY,
            ErrorType.INTERNAL_ERROR
        }
        
        warning_errors = {
            ErrorType.REPOSITORY_TOO_LARGE,
            ErrorType.TOO_MANY_FILES,
            ErrorType.SCAN_TIMEOUT
        }
        
        if error_type in critical_errors:
            return "critical"
        elif error_type in warning_errors:
            return "warning"
        else:
            return "error"
    
    def format_error_for_display(self, error_context: ErrorContext) -> str:
        """Format an error context for display to the user."""
        lines = []
        
        # Error message
        lines.append(f"❌ {error_context.user_message}")
        
        # Error code
        lines.append(f"Error Code: {error_context.error_code}")
        
        # Recovery suggestions
        if error_context.recovery_suggestions:
            lines.append("\n💡 Recovery Suggestions:")
            for i, suggestion in enumerate(error_context.recovery_suggestions, 1):
                lines.append(f"  {i}. {suggestion}")
        
        # Documentation link
        if error_context.documentation_url:
            lines.append(f"\n📚 Documentation: {error_context.documentation_url}")
        
        # Retry information
        if error_context.can_retry:
            lines.append(f"\n🔄 This error can be retried (wait {error_context.retry_delay}s)")
        
        return "\n".join(lines)
    
    def should_retry(self, error_context: ErrorContext, attempt: int, max_attempts: int = 3) -> bool:
        """Determine if an error should be retried."""
        if not error_context.can_retry:
            return False
        
        if attempt >= max_attempts:
            return False
        
        # Wait before retrying
        if error_context.retry_delay > 0:
            time.sleep(error_context.retry_delay)
        
        return True
    
    def log_error(self, error_context: ErrorContext, logger: Optional[logging.Logger] = None) -> None:
        """Log an error with appropriate level."""
        if logger is None:
            logger = self.logger
        
        log_message = f"{error_context.error_code}: {error_context.user_message}"
        
        if error_context.severity == "critical":
            logger.critical(log_message, exc_info=error_context.original_error)
        elif error_context.severity == "error":
            logger.error(log_message, exc_info=error_context.original_error)
        elif error_context.severity == "warning":
            logger.warning(log_message, exc_info=error_context.original_error)
        else:
            logger.info(log_message, exc_info=error_context.original_error)


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorContext:
    """Handle an error using the global error handler."""
    handler = get_error_handler()
    return handler.handle_error(error, context)


def format_error(error_context: ErrorContext) -> str:
    """Format an error context for display."""
    handler = get_error_handler()
    return handler.format_error_for_display(error_context)


def should_retry(error_context: ErrorContext, attempt: int, max_attempts: int = 3) -> bool:
    """Check if an error should be retried."""
    handler = get_error_handler()
    return handler.should_retry(error_context, attempt, max_attempts)
