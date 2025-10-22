#!/usr/bin/env python3
"""
Test file with PII logging issues.
Expected: Should detect PII being logged (emails, phone numbers, SSNs, etc.).
"""

import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_user_data(user_data):
    """Process user data and log various PII."""
    
    # Logging email addresses
    logger.info(f"Processing user with email: {user_data['email']}")
    logger.warning(f"User {user_data['email']} has exceeded limit")
    
    # Logging phone numbers
    logger.info(f"Contacting user at {user_data['phone']}")
    logger.error(f"Failed to reach {user_data['phone']}")
    
    # Logging SSN
    logger.info(f"User SSN: {user_data['ssn']} verified")
    
    # Logging credit card (partial)
    logger.info(f"Payment processed for card ending in {user_data['card_last4']}")
    
    # Logging full credit card (should be detected)
    logger.info(f"Full card number: {user_data['card_number']}")
    
    # Logging address
    logger.info(f"Shipping to: {user_data['address']}")
    
    # Logging in JSON format
    logger.info(f"User data: {json.dumps(user_data)}")
    
    # Logging sensitive data in error messages
    try:
        # Some operation
        pass
    except Exception as e:
        logger.error(f"Error processing user {user_data['email']} with SSN {user_data['ssn']}: {e}")

def log_payment_info(payment_data):
    """Log payment information."""
    
    # Logging payment details
    logger.info(f"Payment received: ${payment_data['amount']} from {payment_data['customer_email']}")
    logger.info(f"Transaction ID: {payment_data['transaction_id']}")
    
    # Logging sensitive payment info
    logger.info(f"Payment method: {payment_data['payment_method']}")
    logger.info(f"Billing address: {payment_data['billing_address']}")

# Example usage
if __name__ == "__main__":
    user_data = {
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567",
        "ssn": "123-45-6789",
        "card_number": "4111-1111-1111-1111",
        "card_last4": "1111",
        "address": "123 Main St, Anytown, USA",
        "payment_method": "Visa ending in 1111"
    }
    
    process_user_data(user_data)
    log_payment_info({
        "amount": 99.99,
        "customer_email": "john.doe@example.com",
        "transaction_id": "txn_123456789",
        "payment_method": "Visa ending in 1111",
        "billing_address": "123 Main St, Anytown, USA"
    })
