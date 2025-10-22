"""
Sample Python file with various PII patterns for testing detection capabilities.
This file contains real PII patterns that should be detected by all detection levels.
"""

import os
import json
import hashlib
from datetime import datetime

# Email addresses - should be detected by regex
USER_EMAIL = "john.doe@company.com"
ADMIN_EMAIL = "admin@example.org"
support_email = "support@testsite.net"

# Credit card numbers - should be detected with Luhn validation
VISA_CARD = "4532-1234-5678-9012"  # Valid Luhn checksum
MASTERCARD = "5555555555554444"    # Valid Luhn checksum
AMEX_CARD = "378282246310005"      # Valid Luhn checksum

# Social Security Numbers - should be detected
SSN_EXAMPLE = "123-45-6789"
ssn_alt_format = "987654321"

# API Keys and Secrets - should be detected
STRIPE_KEY = "sk_live_51H7QjKLEHYG8vX8uFqPmr2x3kL5nM8oP9qR1sT2uV3wX4yZ5"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF36POk6yJV_adQssw5c"

# Phone numbers
PHONE_US = "+1-555-123-4567"
PHONE_FORMATTED = "(555) 987-6543"
PHONE_INTERNATIONAL = "+44-20-7946-0958"

# Passwords and sensitive data
DATABASE_PASSWORD = "MySecretPassword123!"
API_SECRET = "super_secret_api_key_12345"

class UserDataProcessor:
    """Class that processes user PII - should be detected by AST analysis."""
    
    def __init__(self):
        self.db_config = {
            "host": "production-db.company.com",
            "username": "admin",
            "password": "prod_password_2023!",  # Should be flagged
            "database": "user_data"
        }
    
    def process_user_registration(self, email, ssn, credit_card):
        """
        Process user registration with PII.
        This function creates a dataflow from parameters to logging/storage.
        """
        # Validate email format
        if "@" not in email:
            raise ValueError("Invalid email")
        
        # Store user data (potential PII sink)
        user_record = {
            "email": email,           # PII flows to storage
            "ssn": ssn,              # PII flows to storage  
            "payment_method": credit_card,  # PII flows to storage
            "created_at": datetime.now().isoformat()
        }
        
        # Log user creation (potential PII leak)
        print(f"Creating user account for: {email}")  # PII flows to stdout
        print(f"SSN hash: {hashlib.md5(ssn.encode()).hexdigest()}")
        
        # Save to database (PII sink)
        self._save_to_database(user_record)
        
        return user_record
    
    def _save_to_database(self, user_data):
        """Save user data to database - PII sink."""
        # Simulate database save
        query = f"INSERT INTO users (email, ssn) VALUES ('{user_data['email']}', '{user_data['ssn']}')"
        # This would execute the query in real code
        pass
    
    def send_notification(self, user_email, message):
        """Send notification - potential PII in transit."""
        # This creates a taint flow from user_email parameter to external service
        notification_payload = {
            "to": user_email,        # PII flows to external service
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Simulate sending to external service (PII sink)
        self._send_to_notification_service(notification_payload)
    
    def _send_to_notification_service(self, payload):
        """Send to external notification service - PII sink."""
        # In real code, this would send to external API
        print(f"Sending notification to: {payload['to']}")

# Configuration with embedded secrets
CONFIG = {
    "database_url": "postgresql://user:secret123@db.example.com:5432/prod",
    "redis_url": "redis://:password123@redis.example.com:6379/0",
    "email_service": {
        "api_key": "sg.1234567890abcdef",
        "sender": "noreply@company.com"
    },
    "oauth": {
        "client_id": "oauth_client_12345",
        "client_secret": "oauth_secret_abcdef67890"
    }
}

# Function that processes environment variables (potential source)
def load_secrets_from_env():
    """Load secrets from environment variables - PII source."""
    secrets = {
        "db_password": os.getenv("DB_PASSWORD", "fallback_password"),
        "api_key": os.getenv("API_KEY", "fallback_api_key"),
        "jwt_secret": os.getenv("JWT_SECRET", "fallback_jwt_secret")
    }
    
    # Log loaded secrets (bad practice - PII leak)
    for key, value in secrets.items():
        print(f"Loaded {key}: {value}")  # PII flows to stdout
    
    return secrets

# Example of PII in comments and strings
def example_function():
    """
    Example function with PII in documentation.
    
    Example usage:
    >>> process_user("john.doe@example.com", "123-45-6789")
    """
    # TODO: Remove hardcoded email admin@company.com from config
    # FIXME: SSN 987-65-4321 should not be in test data
    
    test_data = {
        "sample_email": "test@example.com",  # Should be detected
        "sample_ssn": "000-00-0000",        # Test pattern
        "sample_phone": "555-0123"          # Should be detected
    }
    
    return test_data

if __name__ == "__main__":
    # Example usage that creates data flows
    processor = UserDataProcessor()
    
    # This creates a complete data flow from input to multiple sinks
    user_data = processor.process_user_registration(
        email="new.user@example.com",       # PII source
        ssn="456-78-9012",                  # PII source
        credit_card="4111111111111111"      # PII source
    )
    
    # Send notification (another data flow)
    processor.send_notification(
        user_email=user_data["email"],      # PII flows from storage to notification
        message="Welcome to our service!"
    )
    
    # Load and use environment secrets
    secrets = load_secrets_from_env()
    
    print("Processing complete")
