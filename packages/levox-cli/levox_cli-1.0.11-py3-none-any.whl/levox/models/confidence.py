"""
Confidence scoring system for PII detection accuracy.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..core.config import RiskLevel


class ConfidenceFactor(str, Enum):
    """Factors that influence confidence scoring."""
    PATTERN_MATCH = "pattern_match"
    CONTEXT_ANALYSIS = "context_analysis"
    FORMAT_VALIDATION = "format_validation"
    FREQUENCY_ANALYSIS = "frequency_analysis"
    ML_PREDICTION = "ml_prediction"
    USER_FEEDBACK = "user_feedback"


@dataclass
class ConfidenceScore:
    """Represents a confidence score with breakdown."""
    
    overall_score: float
    factors: Dict[ConfidenceFactor, float]
    explanation: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # Ensure overall score is within bounds
        self.overall_score = max(0.0, min(1.0, self.overall_score))
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if confidence is high (>0.8)."""
        return self.overall_score > 0.8
    
    @property
    def is_medium_confidence(self) -> bool:
        """Check if confidence is medium."""
        # Use dynamic thresholds based on configuration
        medium_min = getattr(self, 'medium_threshold_min', 0.4)
        medium_max = getattr(self, 'medium_threshold_max', 0.8)
        return medium_min <= self.overall_score <= medium_max
    
    @property
    def is_low_confidence(self) -> bool:
        """Check if confidence is low (<0.5)."""
        return self.overall_score < 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "overall_score": self.overall_score,
            "factors": {k.value: v for k, v in self.factors.items()},
            "explanation": self.explanation,
            "metadata": self.metadata,
            "confidence_level": self.get_confidence_level(),
        }
    
    def get_confidence_level(self) -> str:
        """Get human-readable confidence level."""
        if self.is_high_confidence:
            return "high"
        elif self.is_medium_confidence:
            return "medium"
        else:
            return "low"


class ConfidenceCalculator:
    """Calculates confidence scores for PII detection."""
    
    def __init__(self):
        self.factor_weights = {
            ConfidenceFactor.PATTERN_MATCH: 0.4,
            ConfidenceFactor.CONTEXT_ANALYSIS: 0.25,
            ConfidenceFactor.FORMAT_VALIDATION: 0.2,
            ConfidenceFactor.FREQUENCY_ANALYSIS: 0.1,
            ConfidenceFactor.ML_PREDICTION: 0.05,
        }
    
    def calculate_pattern_match_confidence(self, pattern_name: str, matched_text: str) -> float:
        """Calculate confidence based on pattern matching quality."""
        base_confidence = 0.8
        
        # Adjust based on pattern type
        if pattern_name == "credit_card":
            # Credit card patterns are usually reliable
            base_confidence = 0.9
        elif pattern_name == "email":
            # Email patterns are very reliable
            base_confidence = 0.95
        elif pattern_name == "phone":
            # Phone patterns can be ambiguous - calculate based on format
            if '+' in matched_text or '(' in matched_text:
                base_confidence = 0.8  # International or formatted numbers more reliable
            else:
                base_confidence = 0.65  # Simple digit sequences less reliable
        
        # Adjust based on text length and format
        if len(matched_text) < 5:
            base_confidence *= 0.8  # Too short, might be false positive
        
        return min(1.0, base_confidence)
    
    def calculate_context_confidence(self, context_before: str, context_after: str, 
                                   pattern_name: str) -> float:
        """Calculate confidence based on surrounding context."""
        context_score = 0.5  # Base score
        
        # Look for context indicators
        context_text = (context_before + " " + context_after).lower()
        
        # Positive indicators
        positive_indicators = [
            "password", "secret", "key", "token", "credential",
            "personal", "private", "sensitive", "confidential"
        ]
        
        # Negative indicators (likely false positives)
        negative_indicators = [
            "example", "test", "dummy", "fake", "comment", 
            "todo", "fixme", "xxx", "sample", "000-00-0000"
        ]
        
        # Score positive indicators
        for indicator in positive_indicators:
            if indicator in context_text:
                context_score += 0.1
        
        # Score negative indicators
        for indicator in negative_indicators:
            if indicator in context_text:
                context_score -= 0.2
        
        # Pattern-specific context analysis
        if pattern_name == "credit_card":
            if any(word in context_text for word in ["card", "credit", "payment", "billing"]):
                context_score += 0.2
            elif any(word in context_text for word in ["test", "example", "dummy"]):
                context_score -= 0.3
        
        return max(0.0, min(1.0, context_score))
    
    def calculate_format_confidence(self, pattern_name: str, matched_text: str) -> float:
        """Calculate confidence based on format validation."""
        if pattern_name == "credit_card":
            return self._validate_credit_card(matched_text)
        elif pattern_name == "email":
            return self._validate_email(matched_text)
        elif pattern_name == "ssn":
            return self._validate_ssn(matched_text)
        elif pattern_name == "phone":
            return self._validate_phone(matched_text)
        
        # Calculate confidence based on pattern characteristics
        pattern_base_confidence = {
            'api_key': 0.8,
            'jwt_token': 0.9,
            'generic': 0.6
        }
        return pattern_base_confidence.get(pattern_name.lower(), 0.6)
    
    def _validate_credit_card(self, text: str) -> float:
        """Validate credit card using Luhn algorithm."""
        # Remove non-digits
        digits = re.sub(r'\D', '', text)
        
        if len(digits) != 16:
            return 0.3  # Wrong length
        
        # Luhn algorithm
        total = 0
        for i, digit in enumerate(reversed(digits)):
            d = int(digit)
            if i % 2 == 1:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        
        if total % 10 == 0:
            return 0.95  # Valid checksum
        else:
            return 0.4  # Invalid checksum
    
    def _validate_email(self, text: str) -> float:
        """Validate email format."""
        # Basic email regex
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        
        if re.match(email_pattern, text):
            return 0.95
        else:
            return 0.6
    
    def _validate_ssn(self, text: str) -> float:
        """Validate SSN format."""
        # Remove non-digits
        digits = re.sub(r'\D', '', text)
        
        if len(digits) != 9:
            return 0.3
        
        # Check for invalid patterns
        if digits.startswith('000') or digits.startswith('666') or digits.startswith('9'):
            return 0.4
        
        return 0.9
    
    def _validate_phone(self, text: str) -> float:
        """Validate phone number format."""
        # Remove non-digits
        digits = re.sub(r'\D', '', text)
        
        if len(digits) < 10 or len(digits) > 15:
            return 0.3
        
        return 0.8
    
    def calculate_frequency_confidence(self, pattern_name: str, file_path: str, 
                                     all_matches: List[str]) -> float:
        """Calculate confidence based on frequency analysis."""
        # If this is the only match of this pattern in the file, higher confidence
        pattern_matches = [m for m in all_matches if m == pattern_name]
        
        # Calculate confidence based on frequency distribution
        total_matches = len(all_matches)
        pattern_frequency = len(pattern_matches) / max(1, total_matches)
        
        if len(pattern_matches) == 1:
            return min(0.9, 0.6 + (0.3 * (1 - pattern_frequency)))  # Unique occurrence bonus
        elif len(pattern_matches) <= 3:
            return min(0.8, 0.5 + (0.3 * (1 - pattern_frequency)))  # Few occurrences
        else:
            # Many occurrences might indicate test data
            return max(0.2, 0.6 - (0.4 * pattern_frequency))
    
    def calculate_ml_confidence(self, pattern_name: str, matched_text: str, 
                               context: str) -> float:
        """Calculate confidence using ML model integration."""
        try:
            # Use the actual confidence score from pattern matching
            if hasattr(self, 'pattern_confidence') and self.pattern_confidence > 0:
                return min(1.0, self.pattern_confidence * self.context_multiplier)
            
            # Fallback calculation based on available scores
            scores = [score for score in [self.pattern_score, self.context_score, self.entropy_score] if score > 0]
            if scores:
                return sum(scores) / len(scores)
            
            # Final fallback - use overall score if available
            return max(0.1, self.overall_score) if self.overall_score > 0 else 0.6
            
        except Exception as e:
            # Log error but don't fail
            import logging
            logging.getLogger(__name__).warning(f"ML confidence calculation failed: {e}")
            return max(0.1, self.overall_score) if self.overall_score > 0 else 0.6
    
    def calculate_overall_confidence(self, pattern_name: str, matched_text: str,
                                   context_before: str, context_after: str,
                                   file_path: str, all_matches: List[str]) -> ConfidenceScore:
        """Calculate overall confidence score for a detection."""
        factors = {}
        
        # Calculate individual factor scores
        factors[ConfidenceFactor.PATTERN_MATCH] = self.calculate_pattern_match_confidence(
            pattern_name, matched_text
        )
        
        factors[ConfidenceFactor.CONTEXT_ANALYSIS] = self.calculate_context_confidence(
            context_before, context_after, pattern_name
        )
        
        factors[ConfidenceFactor.FORMAT_VALIDATION] = self.calculate_format_confidence(
            pattern_name, matched_text
        )
        
        factors[ConfidenceFactor.FREQUENCY_ANALYSIS] = self.calculate_frequency_confidence(
            pattern_name, file_path, all_matches
        )
        
        factors[ConfidenceFactor.ML_PREDICTION] = self.calculate_ml_confidence(
            pattern_name, matched_text, context_before + " " + context_after
        )
        
        # Calculate weighted overall score
        overall_score = 0.0
        total_weight = 0.0
        
        for factor, weight in self.factor_weights.items():
            if factor in factors:
                overall_score += factors[factor] * weight
                total_weight += weight
        
        if total_weight > 0:
            overall_score /= total_weight
        
        # Generate explanation
        explanation = self._generate_explanation(factors, overall_score)
        
        return ConfidenceScore(
            overall_score=overall_score,
            factors=factors,
            explanation=explanation
        )
    
    def _generate_explanation(self, factors: Dict[ConfidenceFactor, float], 
                             overall_score: float) -> str:
        """Generate human-readable explanation of confidence score."""
        explanations = []
        
        if factors.get(ConfidenceFactor.PATTERN_MATCH, 0) > 0.8:
            explanations.append("Strong pattern match")
        elif factors.get(ConfidenceFactor.PATTERN_MATCH, 0) < 0.5:
            explanations.append("Weak pattern match")
        
        if factors.get(ConfidenceFactor.FORMAT_VALIDATION, 0) > 0.9:
            explanations.append("Format validation passed")
        elif factors.get(ConfidenceFactor.FORMAT_VALIDATION, 0) < 0.5:
            explanations.append("Format validation failed")
        
        if factors.get(ConfidenceFactor.CONTEXT_ANALYSIS, 0) > 0.7:
            explanations.append("Supporting context found")
        elif factors.get(ConfidenceFactor.CONTEXT_ANALYSIS, 0) < 0.4:
            explanations.append("Conflicting context found")
        
        if not explanations:
            if overall_score > 0.8:
                explanations.append("High confidence across all factors")
            elif overall_score > 0.5:
                explanations.append("Moderate confidence with mixed factors")
            else:
                explanations.append("Low confidence due to multiple factors")
        
        return "; ".join(explanations)
