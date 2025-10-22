"""
Levox - Production-grade PII/GDPR Detection CLI

A high-performance, enterprise-grade CLI application for detecting
Personally Identifiable Information (PII) and ensuring GDPR compliance
in codebases.
"""

__version__ = "1.0.11"
__author__ = "Levox Team"
__email__ = "team@levox.ai"
__license__ = "MIT"

from .cli import cli
from .core.engine import DetectionEngine
from .core.config import Config

__all__ = [
    "cli",
    "DetectionEngine", 
    "Config",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]
