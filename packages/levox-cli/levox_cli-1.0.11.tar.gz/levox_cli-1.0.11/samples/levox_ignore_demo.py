"""
Demo file showing how to use levox-ignore comments to suppress false positives.
This file contains intentionally safe/placeholder values that should not trigger PII alerts.
"""

import os
import json
from typing import Dict, Any

# Configuration with safe placeholder values
APP_CONFIG = {
    "app_name": "SampleApplication",  # levox-ignore: safe application name
    "version": "1.2.3",
    "debug": False,
    "max_retries": 5,
    "timeout_seconds": 30,
    "supported_formats": ["json", "xml", "csv"],
    "default_language": "en",
    "feature_flags": {
        "enable_caching": True,
        "enable_compression": True,
        "enable_analytics": False
    }
}

# Safe placeholder values that should not trigger alerts
PLACEHOLDER_CONFIG = {
    "api_key": "your_api_key_here",  # levox-ignore: placeholder value
    "secret": "your_secret_here",    # levox-ignore: placeholder value
    "password": "your_password_here", # levox-ignore: placeholder value
    "database_url": "localhost:5432", # levox-ignore: local development
    "email": "admin@localhost",       # levox-ignore: local development
    "phone": "555-123-4567",          # levox-ignore: placeholder phone
    "ssn": "000-00-0000",            # levox-ignore: placeholder SSN
    "credit_card": "4111-1111-1111-1111"  # levox-ignore: test card number
}

# Test data that should be suppressed
TEST_DATA = {
    "test_user": {
        "name": "John Doe",           # levox-ignore: test data
        "email": "john.doe@test.com", # levox-ignore: test email
        "phone": "555-987-6543",      # levox-ignore: test phone
        "ssn": "111-11-1111"          # levox-ignore: test SSN
    },
    "mock_data": {
        "user_id": "test123",         # levox-ignore: mock identifier
        "session_id": "sess_abc123",  # levox-ignore: mock session
        "token": "tok_xyz789"         # levox-ignore: mock token
    }
}

# Variables with safe naming patterns
user_id = "user_12345"        # levox-ignore: safe variable pattern
config_type = "development"    # levox-ignore: safe variable pattern
setting_flag = True            # levox-ignore: safe variable pattern
option_param = "default"       # levox-ignore: safe variable pattern

def process_user_data(user_input: str) -> Dict[str, Any]:
    """
    Process user data with safe handling.
    
    Args:
        user_input: User-provided input string
        
    Returns:
        Processed user data
    """
    # This function would normally process real PII, but here we're just
    # demonstrating the levox-ignore functionality
    
    # Safe configuration access
    max_retries = APP_CONFIG.get("max_retries", 3)
    
    # Process input (in real code, this would validate and sanitize)
    processed_data = {
        "input": user_input,
        "processed_at": "2024-01-01T00:00:00Z",
        "status": "success"
    }
    
    return processed_data

def generate_test_report() -> str:
    """Generate a test report with mock data."""
    # This function uses test data that should not trigger PII alerts
    
    report_data = {
        "report_id": "rpt_001",
        "generated_at": "2024-01-01T00:00:00Z",
        "test_results": {
            "total_tests": 100,
            "passed": 95,
            "failed": 5,
            "coverage": "95%"
        },
        "test_user": TEST_DATA["test_user"]  # levox-ignore: test data
    }
    
    return json.dumps(report_data, indent=2)

def main():
    """Main function demonstrating levox-ignore usage."""
    print("Levox Ignore Demo")
    print("=" * 50)
    
    # Show how placeholder values are safely handled
    print(f"API Key: {PLACEHOLDER_CONFIG['api_key']}")
    print(f"Database: {PLACEHOLDER_CONFIG['database_url']}")
    
    # Show test data processing
    test_report = generate_test_report()
    print(f"Test Report: {test_report[:100]}...")
    
    # Show safe variable usage
    print(f"User ID: {user_id}")
    print(f"Config Type: {config_type}")
    
    print("\nAll values above should be suppressed by levox-ignore comments!")

if __name__ == "__main__":
    main()
