"""
Data models for Levox detection results and confidence scoring.
"""

from .detection_result import DetectionResult, DetectionMatch, FileResult
from .confidence import ConfidenceScore, ConfidenceCalculator

__all__ = [
    "DetectionResult",
    "DetectionMatch", 
    "FileResult",
    "ConfidenceScore",
    "ConfidenceCalculator",
]
