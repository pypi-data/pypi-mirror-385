"""
Enterprise-grade custom exceptions for Levox PII/GDPR detection CLI.

This module provides structured exception handling with automatic logging,
error codes, correlation tracking, and secure context management for
production environments.
"""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Union

# Configure structured logging for exceptions
logger = logging.getLogger("levox.exceptions")


class ErrorCode(Enum):
    """Structured error codes for monitoring and telemetry."""
    
    # Base errors (1000-1099)
    LEVOX_UNKNOWN = "LEVOX-1000"
    
    # Configuration errors (1100-1199)
    CONFIG_INVALID = "LEVOX-1100"
    CONFIG_MISSING = "LEVOX-1101"
    CONFIG_PARSE_FAILED = "LEVOX-1102"
    CONFIG_VALIDATION_FAILED = "LEVOX-1103"
    
    # Detection errors (1200-1299)
    DETECTION_FAILED = "LEVOX-1200"
    DETECTION_TIMEOUT = "LEVOX-1201"
    DETECTION_INVALID_INPUT = "LEVOX-1202"
    DETECTION_ENGINE_ERROR = "LEVOX-1203"
    
    # Parser errors (1300-1399)
    PARSE_FAILED = "LEVOX-1300"
    PARSE_UNSUPPORTED_FORMAT = "LEVOX-1301"
    PARSE_CORRUPTED_FILE = "LEVOX-1302"
    PARSE_ENCODING_ERROR = "LEVOX-1303"
    
    # Validation errors (1400-1499)
    VALIDATION_FAILED = "LEVOX-1400"
    VALIDATION_SCHEMA_ERROR = "LEVOX-1401"
    VALIDATION_TYPE_ERROR = "LEVOX-1402"
    VALIDATION_CONSTRAINT_ERROR = "LEVOX-1403"
    
    # License errors (1500-1599)
    LICENSE_INVALID = "LEVOX-1500"
    LICENSE_EXPIRED = "LEVOX-1501"
    LICENSE_QUOTA_EXCEEDED = "LEVOX-1502"
    LICENSE_FEATURE_UNAVAILABLE = "LEVOX-1503"
    RATE_LIMIT_EXCEEDED = "LEVOX-1504"
    
    # Performance errors (1600-1699)
    PERFORMANCE_TIMEOUT = "LEVOX-1600"
    PERFORMANCE_MEMORY_LIMIT = "LEVOX-1601"
    PERFORMANCE_CPU_LIMIT = "LEVOX-1602"
    PERFORMANCE_THROUGHPUT_LIMIT = "LEVOX-1603"
    
    # File errors (1700-1799)
    FILE_NOT_FOUND = "LEVOX-1700"
    FILE_PERMISSION_DENIED = "LEVOX-1701"
    FILE_TOO_LARGE = "LEVOX-1702"
    FILE_CORRUPTED = "LEVOX-1703"
    FILE_UNSUPPORTED_TYPE = "LEVOX-1704"
    
    # ML Model errors (1800-1899)
    MODEL_LOAD_FAILED = "LEVOX-1800"
    MODEL_INFERENCE_ERROR = "LEVOX-1801"
    MODEL_VERSION_MISMATCH = "LEVOX-1802"
    MODEL_MEMORY_ERROR = "LEVOX-1803"
    MODEL_TIMEOUT = "LEVOX-1804"


def _sanitize_details(details: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Sanitize sensitive information from error details before logging.
    
    Args:
        details: Raw details dictionary that may contain sensitive data
        
    Returns:
        Sanitized details safe for logging
    """
    if not details:
        return None
    
    # List of keys that may contain sensitive information
    sensitive_keys = {
        'password', 'token', 'api_key', 'secret', 'key', 'credential',
        'auth', 'authorization', 'session', 'cookie', 'pii_data',
        'personal_data', 'content', 'data', 'payload'
    }
    
    sanitized = {}
    for key, value in details.items():
        key_lower = key.lower()
        
        # Check if key contains sensitive terms
        if any(sensitive_term in key_lower for sensitive_term in sensitive_keys):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, str) and len(value) > 100:
            # Truncate long strings that might contain sensitive data
            sanitized[key] = f"{value[:50]}...[TRUNCATED]"
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = _sanitize_details(value)
        else:
            sanitized[key] = value
    
    return sanitized


class LevoxException(Exception):
    """
    Base exception for all Levox errors with enterprise-grade features.
    
    Provides structured error handling with automatic logging, correlation tracking,
    and sanitized context for production environments.
    """
    
    error_code: ErrorCode = ErrorCode.LEVOX_UNKNOWN
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        suppress_logging: bool = False
    ) -> None:
        """
        Initialize a Levox exception with structured context.
        
        Args:
            message: Human-readable error message
            details: Optional structured details for debugging (will be sanitized)
            correlation_id: Optional correlation ID for tracing across logs
            suppress_logging: If True, skip automatic logging (for sensitive contexts)
        """
        self.message = message
        self.details = details or {}
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc)
        self.sanitized_details = _sanitize_details(details)
        
        super().__init__(self.message)
        
        # Automatically log the exception unless suppressed
        if not suppress_logging:
            self._log_exception()
    
    def _log_exception(self) -> None:
        """Log the exception with structured data for monitoring."""
        log_data = {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.sanitized_details,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "exception_type": self.__class__.__name__
        }
        
        # Only include full traceback when explicit debug is enabled
        import os
        debug_enabled = os.getenv('LEVOX_DEBUG', '').lower() in ('1', 'true', 'yes')
        logger.error(
            f"Levox exception raised: {self.error_code.value}",
            extra={"structured_data": log_data},
            exc_info=debug_enabled
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for serialization.
        
        Returns:
            Dictionary representation with sanitized data
        """
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.sanitized_details,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "exception_type": self.__class__.__name__
        }
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.sanitized_details:
            return f"[{self.error_code.value}] {self.message} (ID: {self.correlation_id[:8]})"
        return f"[{self.error_code.value}] {self.message} (ID: {self.correlation_id[:8]})"
    
    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"error_code={self.error_code.value}, "
            f"message='{self.message}', "
            f"correlation_id='{self.correlation_id}'"
            f")"
        )


class ConfigurationError(LevoxException):
    """Raised when there's a configuration error."""
    
    error_code = ErrorCode.CONFIG_INVALID
    
    @classmethod
    def missing_config(
        cls,
        config_key: str,
        correlation_id: Optional[str] = None
    ) -> "ConfigurationError":
        """Create exception for missing configuration."""
        return cls(
            message=f"Required configuration '{config_key}' is missing",
            details={"config_key": config_key},
            correlation_id=correlation_id
        )
    
    @classmethod
    def invalid_config(
        cls,
        config_key: str,
        expected_type: str,
        actual_value: Any,
        correlation_id: Optional[str] = None
    ) -> "ConfigurationError":
        """Create exception for invalid configuration value."""
        return cls(
            message=f"Configuration '{config_key}' has invalid value",
            details={
                "config_key": config_key,
                "expected_type": expected_type,
                "actual_type": type(actual_value).__name__
            },
            correlation_id=correlation_id
        )


class DetectionError(LevoxException):
    """Raised when there's an error during PII/GDPR detection."""
    
    error_code = ErrorCode.DETECTION_FAILED
    
    @classmethod
    def timeout(
        cls,
        timeout_seconds: int,
        correlation_id: Optional[str] = None
    ) -> "DetectionError":
        """Create exception for detection timeout."""
        instance = cls(
            message=f"Detection timed out after {timeout_seconds} seconds",
            details={"timeout_seconds": timeout_seconds},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.DETECTION_TIMEOUT
        return instance
    
    @classmethod
    def invalid_input(
        cls,
        input_type: str,
        reason: str,
        correlation_id: Optional[str] = None
    ) -> "DetectionError":
        """Create exception for invalid input."""
        instance = cls(
            message=f"Invalid {input_type} input: {reason}",
            details={"input_type": input_type, "reason": reason},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.DETECTION_INVALID_INPUT
        return instance


class AnalysisTimeoutError(DetectionError):
    """Raised specifically when static analysis exceeds its allowed time."""
    
    error_code = ErrorCode.DETECTION_TIMEOUT
    
    @classmethod
    def exceeded(
        cls,
        timeout_seconds: int,
        correlation_id: Optional[str] = None
    ) -> "AnalysisTimeoutError":
        return cls(
            message=f"Analysis timed out after {timeout_seconds} seconds",
            details={"timeout_seconds": timeout_seconds},
            correlation_id=correlation_id
        )


class ParserError(LevoxException):
    """Raised when there's an error parsing files."""
    
    error_code = ErrorCode.PARSE_FAILED
    
    @classmethod
    def unsupported_format(
        cls,
        file_path: str,
        file_extension: str,
        correlation_id: Optional[str] = None
    ) -> "ParserError":
        """Create exception for unsupported file format."""
        instance = cls(
            message=f"Unsupported file format: {file_extension}",
            details={"file_extension": file_extension, "supported_formats": [".txt", ".csv", ".json", ".xml"]},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.PARSE_UNSUPPORTED_FORMAT
        return instance
    
    @classmethod
    def corrupted_file(
        cls,
        file_path: str,
        reason: str,
        correlation_id: Optional[str] = None
    ) -> "ParserError":
        """Create exception for corrupted file."""
        instance = cls(
            message=f"File appears to be corrupted: {reason}",
            details={"reason": reason},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.PARSE_CORRUPTED_FILE
        return instance


class ValidationError(LevoxException):
    """Raised when data validation fails."""
    
    error_code = ErrorCode.VALIDATION_FAILED
    
    @classmethod
    def schema_error(
        cls,
        field_name: str,
        expected_schema: str,
        correlation_id: Optional[str] = None
    ) -> "ValidationError":
        """Create exception for schema validation failure."""
        instance = cls(
            message=f"Schema validation failed for field '{field_name}'",
            details={"field_name": field_name, "expected_schema": expected_schema},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.VALIDATION_SCHEMA_ERROR
        return instance


class LicenseError(LevoxException):
    """Raised when license validation fails."""
    
    error_code = ErrorCode.LICENSE_INVALID
    
    @classmethod
    def expired(
        cls,
        expiry_date: datetime,
        correlation_id: Optional[str] = None
    ) -> "LicenseError":
        """Create exception for expired license."""
        instance = cls(
            message=f"License expired on {expiry_date.strftime('%Y-%m-%d')}",
            details={"expiry_date": expiry_date.isoformat()},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.LICENSE_EXPIRED
        return instance
    
    @classmethod
    def quota_exceeded(
        cls,
        current_usage: int,
        quota_limit: int,
        correlation_id: Optional[str] = None
    ) -> "LicenseError":
        """Create exception for quota exceeded."""
        instance = cls(
            message=f"License quota exceeded: {current_usage}/{quota_limit}",
            details={"current_usage": current_usage, "quota_limit": quota_limit},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.LICENSE_QUOTA_EXCEEDED
        return instance


class PerformanceError(LevoxException):
    """Raised when performance thresholds are exceeded."""
    
    error_code = ErrorCode.PERFORMANCE_TIMEOUT
    
    @classmethod
    def memory_limit(
        cls,
        current_memory_mb: float,
        limit_mb: float,
        correlation_id: Optional[str] = None
    ) -> "PerformanceError":
        """Create exception for memory limit exceeded."""
        instance = cls(
            message=f"Memory limit exceeded: {current_memory_mb:.1f}MB > {limit_mb}MB",
            details={"current_memory_mb": current_memory_mb, "limit_mb": limit_mb},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.PERFORMANCE_MEMORY_LIMIT
        return instance


class FileError(LevoxException):
    """Raised when there's an error handling files."""
    
    error_code = ErrorCode.FILE_NOT_FOUND
    
    @classmethod
    def permission_denied(
        cls,
        file_path: str,
        operation: str,
        correlation_id: Optional[str] = None
    ) -> "FileError":
        """Create exception for permission denied."""
        instance = cls(
            message=f"Permission denied for {operation} operation",
            details={"operation": operation},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.FILE_PERMISSION_DENIED
        return instance
    
    @classmethod
    def too_large(
        cls,
        file_path: str,
        size_mb: float,
        limit_mb: float,
        correlation_id: Optional[str] = None
    ) -> "FileError":
        """Create exception for file too large."""
        instance = cls(
            message=f"File too large: {size_mb:.1f}MB > {limit_mb}MB limit",
            details={"size_mb": size_mb, "limit_mb": limit_mb},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.FILE_TOO_LARGE
        return instance


class MLModelError(LevoxException):
    """Raised when there's an error with ML models."""
    
    error_code = ErrorCode.MODEL_LOAD_FAILED
    
    @classmethod
    def inference_error(
        cls,
        model_name: str,
        error_details: str,
        correlation_id: Optional[str] = None
    ) -> "MLModelError":
        """Create exception for model inference error."""
        instance = cls(
            message=f"Model inference failed: {error_details}",
            details={"model_name": model_name, "error_type": "inference"},
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.MODEL_INFERENCE_ERROR
        return instance
    
    @classmethod
    def version_mismatch(
        cls,
        model_name: str,
        expected_version: str,
        actual_version: str,
        correlation_id: Optional[str] = None
    ) -> "MLModelError":
        """Create exception for model version mismatch."""
        instance = cls(
            message=f"Model version mismatch for '{model_name}'",
            details={
                "model_name": model_name,
                "expected_version": expected_version,
                "actual_version": actual_version
            },
            correlation_id=correlation_id
        )
        instance.error_code = ErrorCode.MODEL_VERSION_MISMATCH
        return instance


class RateLimitExceededError(LevoxException):
    """Raised when the rate limit for API requests is exceeded."""
    
    error_code = ErrorCode.RATE_LIMIT_EXCEEDED
    
    @classmethod
    def exceeded(
        cls,
        limit_name: str,
        current_count: int,
        limit_count: int,
        correlation_id: Optional[str] = None
    ) -> "RateLimitExceededError":
        """Create exception for rate limit exceeded."""
        instance = cls(
            message=f"Rate limit '{limit_name}' exceeded: {current_count}/{limit_count}",
            details={
                "limit_name": limit_name,
                "current_count": current_count,
                "limit_count": limit_count
            },
            correlation_id=correlation_id
        )
        return instance


# Convenience function for exception handling
def handle_exception(
    exc: Exception,
    correlation_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> LevoxException:
    """
    Convert a generic exception to a LevoxException with proper context.
    
    Args:
        exc: The original exception
        correlation_id: Optional correlation ID for tracing
        context: Optional context information
        
    Returns:
        LevoxException with structured context
    """
    if isinstance(exc, LevoxException):
        return exc
    
    return LevoxException(
        message=f"Unexpected error: {str(exc)}",
        details={
            "original_exception": exc.__class__.__name__,
            "original_message": str(exc),
            **(context or {})
        },
        correlation_id=correlation_id
    )