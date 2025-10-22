#!/usr/bin/env python3
"""
Test file with clean Python code (no security issues).
Expected: Should NOT detect any security vulnerabilities.
"""

import os
import hashlib
import secrets
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configure logging without PII
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def secure_password_hash(password: str, salt: bytes) -> bytes:
    """Secure password hashing with proper salt and iterations."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,  # Secure number of iterations
    )
    return kdf.derive(password.encode())

def secure_random_generation() -> tuple:
    """Secure random generation using proper libraries."""
    # Using secrets for cryptographic operations
    secure_token = secrets.token_urlsafe(32)
    secure_bytes = secrets.token_bytes(16)
    
    # Using os.urandom for system-level randomness
    system_random = os.urandom(16)
    
    return secure_token, secure_bytes, system_random

def secure_encryption(data: str, key: bytes) -> bytes:
    """Secure encryption using Fernet."""
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def secure_decryption(encrypted_data: bytes, key: bytes) -> str:
    """Secure decryption using Fernet."""
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data.decode()

def secure_file_operations(file_path: str) -> str:
    """Secure file operations with proper path validation."""
    # Validate and sanitize file path
    path = Path(file_path).resolve()
    
    # Ensure path is within allowed directory
    allowed_dir = Path("/var/www/uploads").resolve()
    if not str(path).startswith(str(allowed_dir)):
        raise ValueError("File path outside allowed directory")
    
    # Safe file reading
    with open(path, 'r') as f:
        content = f.read()
    
    return content

def secure_sql_query(cursor, user_id: int) -> list:
    """Secure SQL query using parameterized statements."""
    # Using parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    
    # Fetch results
    results = cursor.fetchall()
    return results

def secure_logging(message: str, user_id: str = None):
    """Secure logging without PII."""
    if user_id:
        # Log only user ID, not sensitive data
        logger.info(f"Processing request for user ID: {user_id}")
    else:
        logger.info(message)

def secure_api_call(url: str, api_key: str) -> dict:
    """Secure API call with proper error handling."""
    import requests
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return {}

def secure_data_validation(user_input: str) -> str:
    """Secure input validation and sanitization."""
    import re
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', user_input)
    
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    return sanitized

def secure_config_loading() -> dict:
    """Secure configuration loading from environment variables."""
    config = {
        'database_url': os.getenv('DATABASE_URL'),
        'api_key': os.getenv('API_KEY'),
        'secret_key': os.getenv('SECRET_KEY'),
        'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    }
    
    # Validate required configuration
    required_keys = ['database_url', 'api_key', 'secret_key']
    for key in required_keys:
        if not config[key]:
            raise ValueError(f"Missing required configuration: {key}")
    
    return config

def secure_session_management(user_id: str) -> str:
    """Secure session management."""
    import uuid
    import time
    
    # Generate secure session token
    session_token = secrets.token_urlsafe(32)
    
    # Store session with expiration
    session_data = {
        'user_id': user_id,
        'created_at': time.time(),
        'expires_at': time.time() + 3600  # 1 hour expiration
    }
    
    # In a real application, this would be stored in a secure database
    # For this example, we just return the token
    return session_token

def secure_error_handling(operation: str):
    """Secure error handling without information disclosure."""
    try:
        # Some operation
        pass
    except Exception as e:
        # Log error without sensitive details
        logger.error(f"Operation '{operation}' failed: {type(e).__name__}")
        
        # Return generic error message
        return {"error": "Operation failed", "operation": operation}

# Example usage of secure functions
if __name__ == "__main__":
    # Generate secure salt
    salt = os.urandom(16)
    
    # Hash password securely
    password_hash = secure_password_hash("user_password", salt)
    
    # Generate secure random values
    token, random_bytes, system_random = secure_random_generation()
    
    # Secure logging
    secure_logging("Application started successfully")
    
    # Secure configuration
    try:
        config = secure_config_loading()
        print("Configuration loaded successfully")
    except ValueError as e:
        print(f"Configuration error: {e}")
    
    # Secure session
    session_token = secure_session_management("user123")
    
    print("All secure operations completed successfully")
