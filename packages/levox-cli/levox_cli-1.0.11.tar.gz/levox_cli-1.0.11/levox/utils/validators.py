"""
Validation utilities for PII detection including Luhn algorithm.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    confidence: float
    reason: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Validator:
    """Validates various PII formats and patterns."""
    
    def __init__(self):
        # Common validation patterns
        self.patterns = {
            'credit_card': {
                'visa': r'^4[0-9]{12}(?:[0-9]{3})?$',
                'mastercard': r'^5[1-5][0-9]{14}$',
                'amex': r'^3[47][0-9]{13}$',
                'discover': r'^6(?:011|5[0-9]{2})[0-9]{12}$',
                'diners': r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$',
                'jcb': r'^(?:2131|1800|35\d{3})\d{11}$'
            },
            'ssn': r'^(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': {
                'us': r'^(\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})$',
                'international': r'^\+?[1-9]\d{1,14}$'
            },
            'ip_address': {
                'ipv4': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                'ipv6': r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
            }
        }
    
    def validate_credit_card(self, text: str) -> ValidationResult:
        """Validate credit card number using Luhn algorithm and format checks."""
        # Remove all non-digits
        digits = re.sub(r'\D', '', text)
        
        if not digits:
            return ValidationResult(False, 0.0, "No digits found")
        
        # Check length
        if len(digits) < 13 or len(digits) > 19:
            return ValidationResult(False, 0.0, f"Invalid length: {len(digits)}")
        
        # Check if it's a known card type
        card_type = self._identify_card_type(digits)
        
        # Validate with Luhn algorithm
        if not self._luhn_check(digits):
            return ValidationResult(False, 0.3, "Failed Luhn algorithm check")
        
        # Calculate confidence based on various factors
        confidence = self._calculate_credit_card_confidence(digits, card_type)
        
        return ValidationResult(
            is_valid=True,
            confidence=confidence,
            reason=f"Valid {card_type} card number",
            metadata={'card_type': card_type, 'length': len(digits)}
        )
    
    def _luhn_check(self, digits: str) -> bool:
        """Perform Luhn algorithm validation."""
        if not digits.isdigit():
            return False
        
        # Reverse the digits
        reversed_digits = digits[::-1]
        
        total = 0
        for i, digit in enumerate(reversed_digits):
            d = int(digit)
            if i % 2 == 1:  # Every second digit from right
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        
        return total % 10 == 0
    
    def _identify_card_type(self, digits: str) -> str:
        """Identify credit card type based on number pattern."""
        if digits.startswith('4'):
            return 'visa'
        elif digits.startswith('5') and digits[1] in '12345':
            return 'mastercard'
        elif digits.startswith('34') or digits.startswith('37'):
            return 'amex'
        elif digits.startswith('6'):
            if digits.startswith('6011') or (digits.startswith('65') and len(digits) == 16):
                return 'discover'
        elif digits.startswith('3'):
            if digits.startswith('30') or digits.startswith('36') or digits.startswith('38'):
                return 'diners'
        elif digits.startswith('35'):
            return 'jcb'
        
        return 'unknown'
    
    def _calculate_credit_card_confidence(self, digits: str, card_type: str) -> float:
        """Calculate confidence score for credit card validation."""
        confidence = 0.8  # Base confidence
        
        # Length confidence
        if len(digits) in [13, 15, 16]:  # Common lengths
            confidence += 0.1
        
        # Card type confidence
        if card_type != 'unknown':
            confidence += 0.1
        
        # Check for common test numbers
        test_numbers = ['4111111111111111', '5555555555554444', '378282246310005']
        if digits in test_numbers:
            confidence -= 0.2  # Reduce confidence for known test numbers
        
        return min(1.0, confidence)
    
    def validate_ssn(self, text: str) -> ValidationResult:
        """Validate Social Security Number."""
        # Remove non-digits
        digits = re.sub(r'\D', '', text)
        
        if len(digits) != 9:
            return ValidationResult(False, 0.0, f"Invalid length: {len(digits)}")
        
        # Check for invalid patterns
        if digits.startswith('000') or digits.startswith('666') or digits.startswith('9'):
            return ValidationResult(False, 0.3, "Invalid SSN pattern")
        
        # Check middle digits (group number)
        if digits[3:5] == '00':
            return ValidationResult(False, 0.3, "Invalid group number")
        
        # Check last 4 digits (serial number)
        if digits[5:] == '0000':
            return ValidationResult(False, 0.3, "Invalid serial number")
        
        return ValidationResult(True, 0.9, "Valid SSN format")
    
    def validate_email(self, text: str) -> ValidationResult:
        """Validate email address format."""
        if not re.match(self.patterns['email'], text):
            return ValidationResult(False, 0.0, "Invalid email format")
        
        # Additional checks
        parts = text.split('@')
        local_part = parts[0]
        domain_part = parts[1]
        
        # Check local part length
        if len(local_part) > 64:
            return ValidationResult(False, 0.5, "Local part too long")
        
        # Check domain part length
        if len(domain_part) > 253:
            return ValidationResult(False, 0.5, "Domain part too long")
        
        # Check for common disposable email domains
        disposable_domains = ['temp-mail.org', '10minutemail.com', 'guerrillamail.com']
        if domain_part.lower() in disposable_domains:
            return ValidationResult(True, 0.7, "Valid email (disposable domain)")
        
        return ValidationResult(True, 0.95, "Valid email format")
    
    def validate_phone(self, text: str, country: str = 'us') -> ValidationResult:
        """Validate phone number format."""
        # Remove all non-digits and non-plus
        cleaned = re.sub(r'[^\d+]', '', text)
        
        if country == 'us':
            pattern = self.patterns['phone']['us']
            if re.match(pattern, text):
                return ValidationResult(True, 0.8, "Valid US phone number")
        else:
            pattern = self.patterns['phone']['international']
            if re.match(pattern, cleaned):
                return ValidationResult(True, 0.7, "Valid international phone number")
        
        return ValidationResult(False, 0.3, "Invalid phone number format")
    
    def validate_ip_address(self, text: str) -> ValidationResult:
        """Validate IP address format."""
        # Check IPv4
        if re.match(self.patterns['ip_address']['ipv4'], text):
            # Additional IPv4 checks
            octets = text.split('.')
            for octet in octets:
                if int(octet) == 0 and text.startswith('0.'):
                    return ValidationResult(False, 0.5, "Invalid IPv4 (starts with 0)")
                if int(octet) == 255 and text.endswith('.255'):
                    return ValidationResult(False, 0.5, "Invalid IPv4 (ends with 255)")
            
            return ValidationResult(True, 0.9, "Valid IPv4 address")
        
        # Check IPv6
        if re.match(self.patterns['ip_address']['ipv6'], text):
            return ValidationResult(True, 0.9, "Valid IPv6 address")
        
        return ValidationResult(False, 0.0, "Invalid IP address format")
    
    def validate_date(self, text: str) -> ValidationResult:
        """Validate date formats."""
        # Common date patterns
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
            r'^\d{2}-\d{2}-\d{4}$',  # MM-DD-YYYY
            r'^\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}$',  # DD MMM YYYY
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                # Additional validation for YYYY-MM-DD
                if pattern == r'^\d{4}-\d{2}-\d{2}$':
                    try:
                        from datetime import datetime
                        datetime.strptime(text, '%Y-%m-%d')
                        return ValidationResult(True, 0.9, "Valid date (ISO format)")
                    except ValueError:
                        return ValidationResult(False, 0.5, "Invalid date values")
                
                return ValidationResult(True, 0.8, "Valid date format")
        
        return ValidationResult(False, 0.0, "Invalid date format")
    
    def validate_zip_code(self, text: str, country: str = 'us') -> ValidationResult:
        """Validate ZIP/postal code format."""
        if country == 'us':
            # US ZIP code: 5 digits or 5+4 format
            if re.match(r'^\d{5}(-\d{4})?$', text):
                return ValidationResult(True, 0.9, "Valid US ZIP code")
        elif country == 'ca':
            # Canadian postal code: A1A 1A1 format
            if re.match(r'^[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d$', text):
                return ValidationResult(True, 0.9, "Valid Canadian postal code")
        elif country == 'uk':
            # UK postcode: various formats
            if re.match(r'^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$', text, re.IGNORECASE):
                return ValidationResult(True, 0.9, "Valid UK postcode")
        
        return ValidationResult(False, 0.0, "Invalid postal code format")
    
    def validate_credit_card_expiry(self, text: str) -> ValidationResult:
        """Validate credit card expiry date."""
        # Common formats: MM/YY, MM/YYYY, MM-YY, MM-YYYY
        if re.match(r'^(0[1-9]|1[0-2])[/-](\d{2}|\d{4})$', text):
            parts = re.split(r'[/-]', text)
            month = int(parts[0])
            year = int(parts[1])
            
            # Convert 2-digit year to 4-digit
            if year < 100:
                year += 2000
            
            # Check if date is in the future
            from datetime import datetime
            current_date = datetime.now()
            expiry_date = datetime(year, month, 1)
            
            if expiry_date > current_date:
                return ValidationResult(True, 0.9, "Valid expiry date")
            else:
                return ValidationResult(False, 0.5, "Expired card")
        
        return ValidationResult(False, 0.0, "Invalid expiry date format")
    
    def get_validation_summary(self, text: str) -> Dict[str, ValidationResult]:
        """Get validation results for all supported formats."""
        results = {}
        
        # Try to validate as different types
        validation_methods = [
            ('credit_card', self.validate_credit_card),
            ('ssn', self.validate_ssn),
            ('email', self.validate_email),
            ('phone', self.validate_phone),
            ('ip_address', self.validate_ip_address),
            ('date', self.validate_date),
            ('zip_code', self.validate_zip_code),
        ]
        
        for name, validator in validation_methods:
            try:
                results[name] = validator(text)
            except Exception:
                results[name] = ValidationResult(False, 0.0, "Validation error")
        
        return results
    
    def is_likely_pii(self, text: str) -> Tuple[bool, float, str]:
        """Determine if text is likely to contain PII."""
        # Get all validation results
        validation_results = self.get_validation_summary(text)
        
        # Find the highest confidence valid result
        best_result = None
        best_confidence = 0.0
        
        for name, result in validation_results.items():
            if result.is_valid and result.confidence > best_confidence:
                best_result = result
                best_confidence = result.confidence
        
        if best_result:
            return True, best_confidence, f"Detected as {best_result.reason}"
        
        # Check for patterns that suggest PII even if not perfectly formatted
        pii_indicators = [
            (r'\b\d{3}-\d{2}-\d{4}\b', 0.6, "SSN-like pattern"),
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 0.5, "Credit card-like pattern"),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 0.7, "Email-like pattern"),
            (r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', 0.5, "Phone-like pattern"),
        ]
        
        for pattern, confidence, description in pii_indicators:
            if re.search(pattern, text):
                return True, confidence, description
        
        return False, 0.0, "No PII patterns detected"
