#!/usr/bin/env python3
"""
Test file with hardcoded password issues.
Expected: Should detect hardcoded passwords and credentials.
"""

import os
import base64

# Hardcoded password in variable
password = "admin123"
secret_key = "my_secret_key_12345"

# Hardcoded password in dictionary
config = {
    "username": "admin",
    "password": "password123",
    "api_key": "sk-1234567890abcdef"
}

# Hardcoded password in function
def authenticate_user(username, user_password):
    # Hardcoded admin password
    if username == "admin" and user_password == "admin123":
        return True
    return False

# Hardcoded credentials in string
connection_string = "postgresql://user:password123@localhost:5432/db"

# Base64 encoded password (should still be detected)
encoded_password = base64.b64encode(b"secret123").decode()

# Hardcoded API key
API_KEY = "pk_live_1234567890abcdef"

# Hardcoded database password
DB_PASSWORD = "db_password_123"
