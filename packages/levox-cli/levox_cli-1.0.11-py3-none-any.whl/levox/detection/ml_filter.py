"""
Level 4: Enterprise ML-based false positive reduction for Levox PII/GDPR detection.

This module provides production-grade ML filtering capabilities with:
- Circuit breaker patterns for reliability
- Comprehensive feature extraction and caching
- Structured logging and telemetry
- Batch inference optimization
- Graceful fallback to rule-based filtering
- Model versioning and validation
"""

import json
import pickle
import hashlib
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import (
    List, Dict, Any, Optional, Tuple, Union, Set, Callable,
    NamedTuple, TypeVar, Generic
)
from datetime import datetime, timezone
from functools import lru_cache, wraps
from enum import Enum
import logging
import uuid

import numpy as np
import pandas as pd

from ..core.config import Config, DetectionPattern, RiskLevel
from ..core.exceptions import DetectionError, MLModelError
from ..models.detection_result import DetectionMatch

# ML imports with graceful degradation
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (
        classification_report, accuracy_score, precision_recall_fscore_support,
        confusion_matrix, roc_auc_score
    )
    from sklearn.pipeline import Pipeline
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    ML_IMPORT_ERROR = str(e)


class CircuitBreakerState(Enum):
    """Circuit breaker states for ML operations."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class FilteringStrategy(Enum):
    """Available filtering strategies."""
    ML_ONLY = "ml_only"
    RULE_BASED_ONLY = "rule_based_only"
    HYBRID = "hybrid"
    AUTO = "auto"


@dataclass
class ModelMetrics:
    """ML model performance metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float] = None
    confusion_matrix: Optional[List[List[int]]] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ModelInfo:
    """Comprehensive ML model information."""
    model_id: str
    model_type: str
    version: str
    training_date: str
    feature_version: str
    metrics: ModelMetrics
    training_samples: int
    validation_samples: int
    feature_names: List[str]
    model_hash: str
    created_by: str = "levox"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelInfo':
        """Create ModelInfo from dictionary."""
        metrics_data = data.get('metrics', {})
        if isinstance(metrics_data, dict):
            metrics = ModelMetrics(**metrics_data)
        else:
            metrics = metrics_data
        
        return cls(
            model_id=data['model_id'],
            model_type=data['model_type'],
            version=data['version'],
            training_date=data['training_date'],
            feature_version=data['feature_version'],
            metrics=metrics,
            training_samples=data['training_samples'],
            validation_samples=data['validation_samples'],
            feature_names=data['feature_names'],
            model_hash=data['model_hash'],
            created_by=data.get('created_by', 'levox')
        )


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    recovery_timeout: int = 300  # 5 minutes
    success_threshold: int = 3  # successes needed to close from half-open
    max_failures_window: int = 600  # 10 minutes


@dataclass
class InferenceContext:
    """Context for ML inference operations."""
    correlation_id: str
    file_path: Optional[str]
    pattern_type: str
    batch_size: int = 1
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class FilteringResult:
    """Result of ML filtering operation."""
    original_matches: int
    filtered_matches: int
    strategy_used: FilteringStrategy
    processing_time_ms: float
    confidence_adjustments: List[Tuple[str, float, float]]  # (match_id, old_conf, new_conf)
    errors: List[str]
    correlation_id: str


class FeatureExtractor:
    """Optimized feature extraction for PII detection patterns."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.FeatureExtractor")
        
        # Feature extractors
        self._text_vectorizer = None
        self._pattern_encoders = {}
        self._feature_cache = {}
        self._cache_lock = threading.RLock()
        
        # Initialize pattern encodings
        self._pattern_encodings = {
            'credit_card': 1.0,
            'email': 2.0,
            'ssn': 3.0,
            'phone': 4.0,
            'api_key': 5.0,
            'aws_key': 6.0,
            'dataflow_taint': 7.0,
            'regex_pattern': 8.0,
            'custom_pattern': 9.0
        }
        
        # Risk level encodings
        self._risk_encodings = {
            RiskLevel.LOW: 0.25,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.75,
            RiskLevel.CRITICAL: 1.0
        }
        
        self._initialize_extractors()
    
    def _initialize_extractors(self):
        """Initialize feature extraction components."""
        if ML_AVAILABLE:
            try:
                self._text_vectorizer = TfidfVectorizer(
                    max_features=50,
                    ngram_range=(1, 2),
                    stop_words='english',
                    lowercase=True,
                    token_pattern=r'\b\w+\b'
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize text vectorizer: {e}")
    
    @lru_cache(maxsize=10000)
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text with caching."""
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        text_length = len(text)
        for count in char_counts.values():
            probability = count / text_length
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return min(entropy, 8.0)  # Cap at 8 bits
    
    @lru_cache(maxsize=1000)
    def _extract_regex_features(self, text: str) -> Dict[str, float]:
        """Extract regex-based features with caching."""
        features = {}
        
        # Character type ratios
        features['digit_ratio'] = len([c for c in text if c.isdigit()]) / len(text) if text else 0
        features['alpha_ratio'] = len([c for c in text if c.isalpha()]) / len(text) if text else 0
        features['special_ratio'] = len([c for c in text if not c.isalnum()]) / len(text) if text else 0
        
        # Pattern-specific features
        features['has_dashes'] = 1.0 if '-' in text else 0.0
        features['has_dots'] = 1.0 if '.' in text else 0.0
        features['has_at_symbol'] = 1.0 if '@' in text else 0.0
        features['has_spaces'] = 1.0 if ' ' in text else 0.0
        
        # Length-based features
        features['length_log'] = np.log1p(len(text)) if text else 0
        features['is_long'] = 1.0 if len(text) > 20 else 0.0
        features['is_short'] = 1.0 if len(text) < 5 else 0.0
        
        return features
    
    def _extract_context_features(self, 
                                context_before: str, 
                                context_after: str,
                                file_path: Optional[str] = None) -> Dict[str, float]:
        """Extract features from surrounding context."""
        features = {}
        
        # Combine contexts
        full_context = f"{context_before} {context_after}".lower()
        
        # Context keywords that suggest real PII
        pii_keywords = {
            'user', 'customer', 'client', 'person', 'individual',
            'password', 'secret', 'key', 'token', 'credential',
            'email', 'phone', 'address', 'ssn', 'social',
            'card', 'payment', 'billing', 'account'
        }
        
        # Context keywords that suggest test/fake data
        test_keywords = {
            'test', 'example', 'sample', 'demo', 'mock', 'fake',
            'dummy', 'placeholder', 'template', 'default'
        }
        
        # Count keyword matches
        pii_score = sum(1 for keyword in pii_keywords if keyword in full_context)
        test_score = sum(1 for keyword in test_keywords if keyword in full_context)
        
        features['pii_context_score'] = min(pii_score / 3.0, 1.0)  # Normalize to [0,1]
        features['test_context_score'] = min(test_score / 3.0, 1.0)
        features['context_length'] = min(len(full_context) / 100.0, 1.0)  # Normalize
        
        # File path features
        if file_path:
            path_str = str(file_path).lower()
            features['is_test_file'] = 1.0 if any(test_word in path_str 
                                                for test_word in ['test', '_test.', '/test/']) else 0.0
            features['is_config_file'] = 1.0 if any(config_ext in path_str 
                                                   for config_ext in ['.conf', '.ini', '.yaml', '.yml', '.json']) else 0.0
            features['is_doc_file'] = 1.0 if any(doc_ext in path_str 
                                                for doc_ext in ['.md', '.txt', '.rst', 'readme']) else 0.0
        else:
            features['is_test_file'] = 0.0
            features['is_config_file'] = 0.0
            features['is_doc_file'] = 0.0
        
        return features
    
    def extract_features(self, 
                        match: DetectionMatch, 
                        content: str,
                        context: Optional[InferenceContext] = None) -> np.ndarray:
        """Extract comprehensive features for ML model."""
        
        # Create cache key
        cache_key = hashlib.md5(
            f"{match.matched_text}:{match.pattern_name}:{match.context_before}:{match.context_after}".encode()
        ).hexdigest()
        
        with self._cache_lock:
            if cache_key in self._feature_cache:
                return self._feature_cache[cache_key]
        
        features = {}
        
        # Basic match features
        features['original_confidence'] = match.confidence
        features['match_length'] = len(match.matched_text)
        features['line_number'] = match.line_number or 0
        # Backward-compatibility: use column_start as column_number feature
        features['column_number'] = getattr(match, 'column_start', 0) or 0
        
        # Pattern type encoding
        features['pattern_encoding'] = self._pattern_encodings.get(match.pattern_name, 0.0)
        
        # Risk level encoding
        features['risk_encoding'] = self._risk_encodings.get(match.risk_level, 0.5)
        
        # Text analysis features
        text_features = self._extract_regex_features(match.matched_text)
        features.update(text_features)
        
        # Entropy calculation
        features['entropy'] = self._calculate_entropy(match.matched_text)
        
        # Context features
        context_features = self._extract_context_features(
            match.context_before, 
            match.context_after,
            context.file_path if context else None
        )
        features.update(context_features)
        
        # Metadata features
        metadata = match.metadata or {}
        features['in_comment'] = 1.0 if metadata.get('context') == 'comment' else 0.0
        features['in_string'] = 1.0 if metadata.get('context') == 'string' else 0.0
        features['in_docstring'] = 1.0 if metadata.get('context') == 'docstring' else 0.0
        
        # Convert to numpy array with fixed order
        feature_names = sorted(features.keys())
        feature_vector = np.array([features[name] for name in feature_names], dtype=np.float32)
        
        # Cache the result
        with self._cache_lock:
            if len(self._feature_cache) > 10000:  # Limit cache size
                # Remove oldest entries
                keys_to_remove = list(self._feature_cache.keys())[:1000]
                for key in keys_to_remove:
                    del self._feature_cache[key]
            
            self._feature_cache[cache_key] = feature_vector
        
        return feature_vector
    
    def get_feature_names(self) -> List[str]:
        """Get ordered list of feature names."""
        # Return standard feature names in fixed order
        base_features = [
            'original_confidence', 'match_length', 'line_number', 'column_number',
            'pattern_encoding', 'risk_encoding', 'entropy'
        ]
        
        regex_features = [
            'digit_ratio', 'alpha_ratio', 'special_ratio',
            'has_dashes', 'has_dots', 'has_at_symbol', 'has_spaces',
            'length_log', 'is_long', 'is_short'
        ]
        
        context_features = [
            'pii_context_score', 'test_context_score', 'context_length',
            'is_test_file', 'is_config_file', 'is_doc_file'
        ]
        
        metadata_features = [
            'in_comment', 'in_string', 'in_docstring'
        ]
        
        return base_features + regex_features + context_features + metadata_features


class CircuitBreaker:
    """Circuit breaker for ML operations."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.failures_window = []
        self._lock = threading.RLock()
        self.logger = logging.getLogger(f"{__name__}.CircuitBreaker")
    
    def __call__(self, func):
        """Decorator to wrap functions with circuit breaker."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    raise MLModelError("Circuit breaker is OPEN - ML operations disabled")
            
            try:
                result = func(*args, **kwargs)
                self._record_success()
                return result
            
            except Exception as e:
                self._record_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if not self.last_failure_time:
            return False
        
        return (time.time() - self.last_failure_time) > self.config.recovery_timeout
    
    def _record_success(self):
        """Record successful operation."""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.failures_window.clear()
                    self.logger.info("Circuit breaker CLOSED after successful operations")
            else:
                self.failure_count = max(0, self.failure_count - 1)
    
    def _record_failure(self):
        """Record failed operation."""
        with self._lock:
            current_time = time.time()
            self.failure_count += 1
            self.last_failure_time = current_time
            self.success_count = 0
            
            # Add to failures window
            self.failures_window.append(current_time)
            
            # Clean old failures outside window
            window_start = current_time - self.config.max_failures_window
            self.failures_window = [t for t in self.failures_window if t >= window_start]
            
            # Check if should open circuit
            if (self.failure_count >= self.config.failure_threshold or 
                len(self.failures_window) >= self.config.failure_threshold):
                
                self.state = CircuitBreakerState.OPEN
                self.logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        with self._lock:
            return {
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure_time': self.last_failure_time,
                'failures_in_window': len(self.failures_window)
            }


class MLFilter:
    """Enterprise-grade ML filter for reducing false positives in PII detection."""
    
    def __init__(self, config: Config):
        self.config = config
        self.correlation_id = str(uuid.uuid4())
        
        # Initialize logging with correlation ID
        self.logger = logging.getLogger(f"{__name__}.MLFilter.{self.correlation_id[:8]}")
        self.logger = logging.LoggerAdapter(self.logger, {'correlation_id': self.correlation_id})
        
        # Initialize components
        self.feature_extractor = FeatureExtractor(config)
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=getattr(config, 'ml_failure_threshold', 5),
            recovery_timeout=getattr(config, 'ml_recovery_timeout', 300),
            success_threshold=getattr(config, 'ml_success_threshold', 3)
        ))
        
        # ML components
        self.model_pipeline = None
        self.model_info: Optional[ModelInfo] = None
        self.confidence_threshold = getattr(config, 'confidence_threshold', 0.7)
        
        # Threading with proper resource management
        self.executor = ThreadPoolExecutor(
            max_workers=getattr(config, 'ml_max_workers', 4),
            thread_name_prefix="ml_filter"
        )
        self._model_lock = threading.RLock()
        
        # Performance tracking with production monitoring
        self.inference_times = []
        self.batch_sizes = []
        self.filtering_stats = {
            'total_matches_processed': 0,
            'total_matches_filtered': 0,
            'ml_predictions': 0,
            'rule_based_fallbacks': 0,
            'circuit_breaker_trips': 0,
            'model_switches': 0,
            'errors_total': 0,
            'last_error_time': None,
            'uptime_start': time.time()
        }
        
        # Store last filtering report for introspection/auditing
        self.last_filtering_result: Optional[FilteringResult] = None
        
        # Production monitoring
        self._monitoring_enabled = getattr(config, 'enable_ml_monitoring', True)
        self._health_check_interval = getattr(config, 'ml_health_check_interval', 60)  # 1 minute
        self._last_health_check = time.time()
        self._health_verbose_logging = getattr(config, 'ml_health_verbose_logging', False)
        
        # Initialize ML system with proper error handling
        self._initialize_ml_system()
        
        # Start periodic model checking (only if monitoring enabled)
        if self._monitoring_enabled:
            self._start_model_monitoring()
        
        # Start health monitoring
        self._start_health_monitoring()
    
    def _start_model_monitoring(self):
        """Start background monitoring for better models."""
        try:
            # Check for better models every 5 minutes
            self._model_check_interval = 300  # 5 minutes
            self._last_model_check = time.time()
            
            # Start monitoring thread
            self._monitoring_thread = threading.Thread(
                target=self._model_monitoring_worker,
                daemon=True,
                name="MLModelMonitor"
            )
            self._monitoring_thread.start()
            
            self.logger.info("Started automatic model monitoring")
            
        except Exception as e:
            self.logger.warning(f"Failed to start model monitoring: {e}")
    
    def _start_health_monitoring(self):
        """Start production health monitoring."""
        try:
            # Start health monitoring thread
            self._health_thread = threading.Thread(
                target=self._health_monitoring_worker,
                daemon=True,
                name="MLHealthMonitor"
            )
            self._health_thread.start()
            
            self.logger.info("Started production health monitoring")
            
        except Exception as e:
            self.logger.warning(f"Failed to start health monitoring: {e}")
    
    def _model_monitoring_worker(self):
        """Background worker that periodically checks for better models."""
        while True:
            try:
                time.sleep(self._model_check_interval)
                
                # Check if we should look for better models
                if time.time() - self._last_model_check >= self._model_check_interval:
                    self._check_for_better_models()
                    self._last_model_check = time.time()
                    
            except Exception as e:
                self.logger.error(f"Model monitoring worker error: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def _health_monitoring_worker(self):
        """Background worker that periodically monitors system health."""
        while True:
            try:
                time.sleep(self._health_check_interval)
                
                # Perform health check
                health_status = self._perform_health_check()
                
                # Only log warnings for actual issues, not startup conditions
                if health_status['status'] == 'healthy':
                    self.logger.debug("Health check passed")
                elif health_status['status'] == 'degraded':
                    # Check if this is just a startup condition
                    uptime = health_status.get('uptime_seconds', 0)
                    if uptime < 300:  # Less than 5 minutes - likely startup
                        if self._health_verbose_logging:
                            self.logger.debug(f"Health check shows startup conditions: {health_status['issues']}")
                    else:
                        if self._health_verbose_logging:
                            self.logger.warning(f"Health check failed: {health_status['issues']}")
                        else:
                            self.logger.debug(f"Health check shows degraded status: {health_status['issues']}")
                else:  # unhealthy
                    # Always log critical health issues
                    self.logger.error(f"Health check critical: {health_status['issues']}")
                
                # Update last health check time
                self._last_health_check = time.time()
                
            except Exception as e:
                self.logger.error(f"Health monitoring worker error: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying
    
    def _check_for_better_models(self):
        """Check if there are better models available and switch to them."""
        try:
            models_dir = Path(__file__).parent.parent.parent / "configs" / "ml_models"
            if not models_dir.exists():
                return
            
            # Get current model score
            if not self.model_info:
                return
            
            current_score = self._calculate_model_score(self.model_info)
            
            # Find all available models
            available_models = []
            for model_file in models_dir.glob("*.pkl"):
                try:
                    model_info = self._peek_model_info(str(model_file))
                    if model_info and model_info.model_id != self.model_info.model_id:
                        score = self._calculate_model_score(model_info)
                        available_models.append({
                            'path': model_file,
                            'info': model_info,
                            'score': score
                        })
                except Exception as e:
                    self.logger.debug(f"Failed to evaluate model {model_file.name}: {e}")
                    continue
            
            if not available_models:
                return
            
            # Find the best available model
            best_model = max(available_models, key=lambda x: x['score'])
            
            # Check if there's a significantly better model (5% improvement threshold)
            improvement_threshold = getattr(self.config, 'ml_improvement_threshold', 0.05)
            if best_model['score'] > (current_score + improvement_threshold):
                self.logger.info(f"Better model found: {best_model['path'].name} "
                               f"(Score: {best_model['score']:.3f} vs current: {current_score:.3f})")
                
                # Switch to the better model with proper error handling
                if self._load_model(str(best_model['path'])):
                    self.logger.info(f"Successfully switched to better model: {best_model['path'].name}")
                    self.filtering_stats['model_switches'] += 1
                    
                    # Update latest pointer
                    self._update_latest_model_pointer(best_model['path'])
                else:
                    self.logger.warning(f"Failed to switch to better model: {best_model['path'].name}")
                    self._record_error("model_switch_failed")
            
        except Exception as e:
            self.logger.error(f"Failed to check for better models: {e}", exc_info=True)
            self._record_error("model_check_failed")
    
    def _initialize_ml_system(self):
        """Initialize the ML system with proper error handling."""
        try:
            if not ML_AVAILABLE:
                self.logger.warning(f"ML libraries not available: {ML_IMPORT_ERROR}")
                self._initialize_rule_based_fallback()
                return
            
            self.logger.info("Initializing ML system")
            self._load_or_train_model()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML system: {e}", exc_info=True)
            self._initialize_rule_based_fallback()
    
    def _initialize_rule_based_fallback(self):
        """Initialize rule-based filtering patterns."""
        self.rule_patterns = {
            'test_patterns': [
                re.compile(r'\btest[_\-]?\w*', re.IGNORECASE),
                re.compile(r'\bexample\b', re.IGNORECASE),
                re.compile(r'\bsample\b', re.IGNORECASE),
                re.compile(r'\bdemo\b', re.IGNORECASE),
                re.compile(r'\bmock\b', re.IGNORECASE),
                re.compile(r'\bfake\b', re.IGNORECASE),
                re.compile(r'\bdummy\b', re.IGNORECASE),
            ],
            
            'config_patterns': [
                re.compile(r'\.conf$', re.IGNORECASE),
                re.compile(r'\.ini$', re.IGNORECASE),
                re.compile(r'\.yaml$', re.IGNORECASE),
                re.compile(r'\.yml$', re.IGNORECASE),
                re.compile(r'config', re.IGNORECASE),
                re.compile(r'settings', re.IGNORECASE),
            ],
            
            'doc_patterns': [
                re.compile(r'README', re.IGNORECASE),
                re.compile(r'\.md$', re.IGNORECASE),
                re.compile(r'\.txt$', re.IGNORECASE),
                re.compile(r'docs?/', re.IGNORECASE),
            ]
        }
        
        self.logger.info("Initialized rule-based filtering fallback")
    
    def _load_or_train_model(self):
        """Load existing model or train a new one."""
        model_loaded = False
        
        # Try to load existing model from config path
        if hasattr(self.config, 'ml_model_path') and self.config.ml_model_path:
            model_loaded = self._load_model(self.config.ml_model_path)
        
        # Try to automatically select the best available model
        if not model_loaded:
            model_loaded = self._load_best_available_model()
        
        # Train default model if none loaded
        if not model_loaded:
            self.logger.info("No pre-trained model found, training default model")
            self._train_default_model()
    
    def _load_best_available_model(self) -> bool:
        """Automatically find and load the best available model based on performance metrics."""
        try:
            models_dir = Path(__file__).parent.parent.parent / "configs" / "ml_models"
            if not models_dir.exists():
                self.logger.warning(f"Models directory not found: {models_dir}")
                return False
            
            # Find all available models
            available_models = []
            
            # Look for different model file patterns
            model_patterns = [
                "levox_latest.pkl",
                "levox_xgb*.pkl",
                "levox_model*.pkl",
                "*.pkl"  # Catch any other pickle files
            ]
            
            for pattern in model_patterns:
                if "*" in pattern:
                    available_models.extend(models_dir.glob(pattern))
                else:
                    model_path = models_dir / pattern
                    if model_path.exists():
                        available_models.append(model_path)
            
            if not available_models:
                self.logger.warning("No model files found in models directory")
                return False
            
            # Remove duplicates and sort by modification time
            available_models = list(set(available_models))
            available_models.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            self.logger.info(f"Found {len(available_models)} available models")
            
            # Evaluate each model and find the best one
            best_model = None
            best_score = -1.0
            model_evaluations = []
            
            for model_path in available_models:
                try:
                    # Try to load model info without loading the full model
                    model_info = self._peek_model_info(str(model_path))
                    if model_info:
                        # Calculate composite score based on multiple metrics
                        score = self._calculate_model_score(model_info)
                        model_evaluations.append({
                            'path': model_path,
                            'info': model_info,
                            'score': score
                        })
                        
                        self.logger.debug(f"Model {model_path.name}: Score {score:.3f} "
                                        f"(Accuracy: {model_info.metrics.accuracy:.3f}, "
                                        f"F1: {model_info.metrics.f1_score:.3f})")
                        
                        if score > best_score:
                            best_score = score
                            best_model = model_path
                            
                except Exception as e:
                    self.logger.debug(f"Failed to evaluate model {model_path.name}: {e}")
                    continue
            
            if not best_model:
                self.logger.warning("No valid models found for evaluation")
                return False
            
            # Log model selection summary
            self.logger.info(f"Model evaluation completed:")
            for eval_info in sorted(model_evaluations, key=lambda x: x['score'], reverse=True):
                self.logger.info(f"  {eval_info['path'].name}: Score {eval_info['score']:.3f} "
                               f"(Accuracy: {eval_info['info'].metrics.accuracy:.3f}, "
                               f"F1: {eval_info['info'].metrics.f1_score:.3f})")
            
            self.logger.info(f"Selected best model: {best_model.name} (Score: {best_score:.3f})")
            
            # Load the best model
            return self._load_model(str(best_model))
            
        except Exception as e:
            self.logger.error(f"Failed to load best available model: {e}", exc_info=True)
            return False
    
    def _load_model(self, model_path: str) -> bool:
        """Load ML model from file with validation."""
        try:
            model_file = Path(model_path)
            if not model_file.exists():
                self.logger.warning(f"Model file not found: {model_path}")
                return False
            
            with open(model_file, 'rb') as f:
                # SECURITY: Use safe pickle loading with restrictions
                import pickle
                
                # Create a restricted unpickler that only allows safe classes
                class RestrictedUnpickler(pickle.Unpickler):
                    def find_class(self, module, name):
                        # Only allow safe built-in types and numpy/sklearn classes
                        safe_modules = {
                            'numpy', 'sklearn', 'scipy', 'pandas',
                            'builtins', '__builtin__'
                        }
                        safe_classes = {
                            'list', 'dict', 'tuple', 'set', 'str', 'int', 'float', 'bool',
                            'ndarray', 'DataFrame', 'Series'
                        }
                        
                        if module in safe_modules and name in safe_classes:
                            return super().find_class(module, name)
                        else:
                            raise pickle.UnpicklingError(f"Unsafe class: {module}.{name}")
                
                # Use restricted unpickler
                model_data = RestrictedUnpickler(f).load()
            
            # Validate model data structure
            required_keys = ['model', 'model_info', 'feature_names']
            if not all(key in model_data for key in required_keys):
                self.logger.error(f"Invalid model file structure: {model_path}")
                return False
            
            # Load model components
            with self._model_lock:
                self.model_pipeline = model_data['model']
                self.model_info = ModelInfo.from_dict(model_data['model_info'])
                
                # Validate model hash if present
                if hasattr(self.model_info, 'model_hash'):
                    current_hash = self._calculate_model_hash(self.model_pipeline)
                    if current_hash != self.model_info.model_hash:
                        self.logger.warning("Model hash mismatch - model may be corrupted")
            
            self.logger.info(f"Loaded ML model: {self.model_info.model_type} v{self.model_info.version}")
            self.logger.info(f"Model metrics - Accuracy: {self.model_info.metrics.accuracy:.3f}, "
                           f"Precision: {self.model_info.metrics.precision:.3f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model from {model_path}: {e}", exc_info=True)
            return False
    
    def _calculate_model_hash(self, model) -> str:
        """Calculate hash of model for integrity checking."""
        try:
            import hashlib
            model_bytes = pickle.dumps(model)
            return hashlib.sha256(model_bytes).hexdigest()
        except Exception:
            return "unknown"
    
    def _train_default_model(self):
        """Train a default model with embedded training data."""
        
        if not ML_AVAILABLE:
            self.logger.error("Cannot train model - ML libraries not available")
            return
        
        try:
            # Generate training data
            training_data = self._generate_training_data()
            
            if len(training_data) < 100:
                self.logger.error("Insufficient training data for model training")
                return
            
            # Train model
            self.logger.info(f"Training model with {len(training_data)} samples")
            self._train_model(training_data)
            
        except Exception as e:
            self.logger.error(f"Default model training failed: {e}", exc_info=True)
            raise MLModelError(f"Failed to train default model: {e}")
    
    def _generate_training_data(self) -> List[Dict[str, Any]]:
        """Generate comprehensive training data."""
        training_data = []
        
        # High-confidence true positives
        true_positives = [
            {
                'matched_text': '4532-1234-5678-9012',
                'pattern_name': 'credit_card',
                'context_before': 'payment card number',
                'context_after': 'for billing',
                'confidence': 0.95,
                'risk_level': RiskLevel.HIGH,
                'is_true_positive': True,
                'metadata': {'context': 'string'}
            },
            {
                'matched_text': 'john.doe@company.com',
                'pattern_name': 'email',
                'context_before': 'user email address',
                'context_after': 'contact information',
                'confidence': 0.9,
                'risk_level': RiskLevel.MEDIUM,
                'is_true_positive': True,
                'metadata': {'context': 'string'}
            },
            {
                'matched_text': '123-45-6789',
                'pattern_name': 'ssn',
                'context_before': 'social security number',
                'context_after': 'personal identification',
                'confidence': 0.95,
                'risk_level': RiskLevel.CRITICAL,
                'is_true_positive': True,
                'metadata': {'context': 'string'}
            }
        ]
        
        # False positives (test data, examples, etc.)
        false_positives = [
            {
                'matched_text': '4111-1111-1111-1111',
                'pattern_name': 'credit_card',
                'context_before': 'test card number',
                'context_after': 'for testing only',
                'confidence': 0.8,
                'risk_level': RiskLevel.HIGH,
                'is_true_positive': False,
                'metadata': {'context': 'comment'}
            },
            {
                'matched_text': 'test@example.com',
                'pattern_name': 'email',
                'context_before': 'example email',
                'context_after': 'demo purposes',
                'confidence': 0.7,
                'risk_level': RiskLevel.MEDIUM,
                'is_true_positive': False,
                'metadata': {'context': 'docstring'}
            },
            {
                'matched_text': '000-00-0000',
                'pattern_name': 'ssn',
                'context_before': 'invalid SSN',
                'context_after': 'placeholder value',
                'confidence': 0.6,
                'risk_level': RiskLevel.CRITICAL,
                'is_true_positive': False,
                'metadata': {'context': 'comment'}
            }
        ]
        
        # Convert to training format
        for examples, label in [(true_positives, True), (false_positives, False)]:
            for example in examples:
                # Create mock DetectionMatch
                match = DetectionMatch(
                    file="training_data",
                    line=1,
                    engine="ml",
                    rule_id=example['pattern_name'],
                    severity=example['risk_level'].value if hasattr(example['risk_level'], 'value') else str(example['risk_level']),
                    confidence=example['confidence'],
                    snippet=example['matched_text'],
                    description=f"Training data example for {example['pattern_name']}",
                    pattern_name=example['pattern_name'],
                    matched_text=example['matched_text'],
                    context_before=example['context_before'],
                    context_after=example['context_after'],
                    column_start=1,
                    column_end=2,
                    risk_level=example['risk_level'],
                    metadata=example['metadata']
                )
                
                # Extract features
                features = self.feature_extractor.extract_features(match, "")
                
                training_data.append({
                    'features': features.tolist(),
                    'label': 1 if label else 0,
                    'pattern_type': example['pattern_name']
                })
        
        # Replicate data to have sufficient samples
        replicated_data = []
        for _ in range(50):  # Create 50 copies with slight variations
            for sample in training_data:
                # Add small random noise to features
                features_array = np.array(sample['features'])
                noise = np.random.normal(0, 0.01, features_array.shape)
                noisy_features = features_array + noise
                
                replicated_data.append({
                    'features': noisy_features.tolist(),
                    'label': sample['label'],
                    'pattern_type': sample['pattern_type']
                })
        
        return training_data + replicated_data
    
    def _train_model(self, training_data: List[Dict[str, Any]]):
        """Train the ML model with comprehensive validation."""
        try:
            # Prepare features and labels
            X = np.array([sample['features'] for sample in training_data])
            y = np.array([sample['label'] for sample in training_data])
            
            # Split data with stratification
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Create and train XGBoost model
            model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='logloss'
            )
            
            # Train model with early stopping
            # Train model (compatible with older xgboost sklearn API)
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
            
            try:
                roc_auc = roc_auc_score(y_test, y_pred_proba)
            except ValueError:
                roc_auc = None
            
            conf_matrix = confusion_matrix(y_test, y_pred).tolist()
            
            # Create model info
            metrics = ModelMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                roc_auc=roc_auc,
                confusion_matrix=conf_matrix
            )
            
            model_id = f"levox_xgb_{int(time.time())}"
            model_hash = self._calculate_model_hash(model)
            
            self.model_info = ModelInfo(
                model_id=model_id,
                model_type="XGBClassifier",
                version="1.0.0",
                training_date=datetime.now(timezone.utc).isoformat(),
                feature_version="1.0",
                metrics=metrics,
                training_samples=len(X_train),
                validation_samples=len(X_test),
                feature_names=self.feature_extractor.get_feature_names(),
                model_hash=model_hash
            )
            
            # Store model
            with self._model_lock:
                self.model_pipeline = model
            
            self.logger.info(f"Model training completed - Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
            
            # Save model
            self._save_model()
            
        except Exception as e:
            raise MLModelError(f"Model training failed: {e}")
    
    def _save_model(self):
        """Save trained model with comprehensive metadata."""
        if not self.model_pipeline or not self.model_info:
            return
        
        try:
            # Create save directory
            save_dir = Path(__file__).parent.parent.parent / "configs" / "ml_models"
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Create model data
            model_data = {
                'model': self.model_pipeline,
                'model_info': asdict(self.model_info),
                'feature_names': self.feature_extractor.get_feature_names(),
                'config_snapshot': {
                    'confidence_threshold': self.confidence_threshold,
                    'safe_literals': getattr(self.config, 'safe_literals', []),
                    'safe_variable_patterns': getattr(self.config, 'safe_variable_patterns', []),
                    'test_file_indicators': getattr(self.config, 'test_file_indicators', [])
                }
            }
            
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_filename = f"levox_model_{timestamp}.pkl"
            model_path = save_dir / model_filename
            
            # Save model
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"Model saved to: {model_path}")
            
            # Update latest model pointer if this is the best model
            self._update_latest_model_pointer(model_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}", exc_info=True)
    
    def _update_latest_model_pointer(self, new_model_path: Path):
        """Update the latest model pointer to point to the best available model."""
        try:
            models_dir = new_model_path.parent
            
            # Find all models and determine the best one
            available_models = []
            for model_file in models_dir.glob("*.pkl"):
                try:
                    model_info = self._peek_model_info(str(model_file))
                    if model_info:
                        score = self._calculate_model_score(model_info)
                        available_models.append({
                            'path': model_file,
                            'info': model_info,
                            'score': score
                        })
                except Exception:
                    continue
            
            if not available_models:
                return
            
            # Sort by score (best first)
            available_models.sort(key=lambda x: x['score'], reverse=True)
            best_model = available_models[0]
            
            # Create or update latest pointer
            latest_pointer = models_dir / "levox_latest.pkl"
            
            # If the latest pointer exists, check if we need to update it
            if latest_pointer.exists():
                try:
                    current_latest_info = self._peek_model_info(str(latest_pointer))
                    if current_latest_info:
                        current_score = self._calculate_model_score(current_latest_info)
                        if best_model['score'] > current_score:
                            self.logger.info(f"New best model found: {best_model['path'].name} "
                                           f"(Score: {best_model['score']:.3f} vs {current_score:.3f})")
                        else:
                            self.logger.info(f"Current latest model remains best: {latest_pointer.name} "
                                           f"(Score: {current_score:.3f})")
                            return
                except Exception:
                    self.logger.warning("Failed to evaluate current latest model, updating anyway")
            
            # Create symlink or copy to latest
            try:
                # Try to create symlink first (more efficient)
                if latest_pointer.exists():
                    latest_pointer.unlink()
                latest_pointer.symlink_to(best_model['path'].name)
                self.logger.info(f"Updated latest model pointer to: {best_model['path'].name}")
            except OSError:
                # Fallback to copying the file
                import shutil
                shutil.copy2(best_model['path'], latest_pointer)
                self.logger.info(f"Copied best model to latest: {best_model['path'].name}")
                
        except Exception as e:
            self.logger.error(f"Failed to update latest model pointer: {e}", exc_info=True)
    
    def filter_matches(self, 
                      matches: List[DetectionMatch], 
                      content: str,
                      file_path: Optional[str] = None,
                      batch_size: int = 100) -> List[DetectionMatch]:
        """
        Filter matches using ML model with comprehensive error handling and telemetry.
        
        Args:
            matches: List of detection matches to filter
            content: Source content being analyzed
            file_path: Optional file path for context
            batch_size: Number of matches to process in each batch
            
        Returns:
            FilteringResult with filtered matches and metadata
        """
        start_time = time.time()
        correlation_id = str(uuid.uuid4())
        
        # Create inference context
        context = InferenceContext(
            correlation_id=correlation_id,
            file_path=file_path,
            pattern_type="mixed",
            batch_size=len(matches)
        )
        
        self.logger.info(f"Starting match filtering", extra={
            'correlation_id': correlation_id,
            'input_matches': len(matches),
            'file_path': file_path,
            'batch_size': batch_size
        })
        
        if not matches:
            empty_result = FilteringResult(
                original_matches=0,
                filtered_matches=0,
                strategy_used=FilteringStrategy.AUTO,
                processing_time_ms=0.0,
                confidence_adjustments=[],
                errors=[],
                correlation_id=correlation_id
            )
            # Persist report and return empty list for backward compatibility
            self.last_filtering_result = empty_result
            return []
        
        # Update stats
        self.filtering_stats['total_matches_processed'] += len(matches)
        
        # Determine filtering strategy with error handling
        try:
            strategy = self._determine_filtering_strategy()
        except Exception as e:
            self.logger.error(f"Failed to determine filtering strategy: {e}", exc_info=True)
            strategy = FilteringStrategy.RULE_BASED_ONLY
            self._record_error("strategy_determination_failed")
        
        # Apply filtering based on strategy with comprehensive error handling
        try:
            if strategy == FilteringStrategy.ML_ONLY:
                filtered_matches, adjustments, errors = self._apply_ml_filtering(
                    matches, content, context, batch_size
                )
            elif strategy == FilteringStrategy.RULE_BASED_ONLY:
                filtered_matches, adjustments, errors = self._apply_rule_based_filtering(
                    matches, content, context
                )
            else:  # HYBRID or AUTO
                filtered_matches, adjustments, errors = self._apply_hybrid_filtering(
                    matches, content, context, batch_size
                )
                
        except Exception as e:
            self.logger.error(f"Filtering failed: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
            self._record_error("filtering_failed")
            
            # Fallback to rule-based filtering
            try:
                filtered_matches, adjustments, errors = self._apply_rule_based_filtering(
                    matches, content, context
                )
                strategy = FilteringStrategy.RULE_BASED_ONLY
                errors.append(f"ML filtering failed, used rule-based fallback: {str(e)}")
            except Exception as fallback_error:
                self.logger.error(f"Fallback filtering also failed: {fallback_error}", exc_info=True)
                self._record_error("fallback_filtering_failed")
                # Last resort: return original matches
                filtered_matches = matches
                adjustments = []
                errors = [f"All filtering failed: {str(e)}", f"Fallback failed: {str(fallback_error)}"]
                strategy = FilteringStrategy.RULE_BASED_ONLY
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Update performance tracking
        self.inference_times.append(processing_time)
        self.batch_sizes.append(len(matches))
        self.filtering_stats['total_matches_filtered'] += len(matches) - len(filtered_matches)
        
        # Create result
        result = FilteringResult(
            original_matches=len(matches),
            filtered_matches=len(filtered_matches),
            strategy_used=strategy,
            processing_time_ms=processing_time,
            confidence_adjustments=adjustments,
            errors=errors,
            correlation_id=correlation_id
        )
        
        self.logger.info(f"Filtering completed", extra={
            'correlation_id': correlation_id,
            'original_matches': len(matches),
            'filtered_matches': len(filtered_matches),
            'strategy_used': strategy.value,
            'processing_time_ms': processing_time,
            'removal_rate': (len(matches) - len(filtered_matches)) / len(matches) if matches else 0
        })
        
        # Guardrail: never drop everything; preserve originals if ML/rules removed all
        safe_filtered = filtered_matches if filtered_matches else matches
        # Persist report and return filtered DetectionMatch list (backward compatible API)
        self.last_filtering_result = result
        return safe_filtered

    def filter_matches_with_report(self,
                                   matches: List[DetectionMatch],
                                   content: str,
                                   file_path: Optional[str] = None,
                                   batch_size: int = 100) -> Tuple[List[DetectionMatch], FilteringResult]:
        """Run filtering and return both filtered matches and a detailed report."""
        filtered = self.filter_matches(matches, content, file_path=file_path, batch_size=batch_size)
        return filtered, (self.last_filtering_result if self.last_filtering_result else FilteringResult(
            original_matches=len(matches),
            filtered_matches=len(filtered),
            strategy_used=self._determine_filtering_strategy(),
            processing_time_ms=0.0,
            confidence_adjustments=[],
            errors=[],
            correlation_id=str(uuid.uuid4())
        ))

    def scan_file(self, file_path: str) -> List[DetectionMatch]:
        """
        Unified interface for scanning a file - implements the standard scan_file method.
        
        Note: ML filter is typically used as a post-processor, but this method
        provides a unified interface for consistency.
        
        Args:
            file_path: Path to the file being analyzed
            
        Returns:
            List of detection matches in unified DetectionMatch format
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return []
            
            # Read file content
            with open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # For ML filter, we typically don't do initial detection
            # Instead, we return an empty list as this is a post-processing step
            # The main detection engines (regex, AST, dataflow) should be called first
            
            self.logger.debug(f"ML filter scan_file called for {file_path} - returning empty list (post-processor)")
            return []
            
        except Exception as e:
            self.logger.error(f"ML filter scan_file failed for {file_path}: {e}")
            return []
    
    def _get_risk_level(self, risk_level_value: Any) -> RiskLevel:
        """Safely convert risk level value to RiskLevel enum."""
        if risk_level_value is None:
            return RiskLevel.MEDIUM
        
        # If it's already a RiskLevel enum, return it
        if isinstance(risk_level_value, RiskLevel):
            return risk_level_value
        
        # If it has a 'value' attribute (like an enum), get the value
        if hasattr(risk_level_value, 'value'):
            try:
                return RiskLevel(risk_level_value.value)
            except (ValueError, TypeError):
                pass
        
        # Try to convert string/int to RiskLevel
        try:
            return RiskLevel(str(risk_level_value).lower())
        except (ValueError, TypeError):
            return RiskLevel.MEDIUM

    def _convert_to_unified_matches(self, matches: List, file_path: Path, 
                                   content: str, language: str) -> List[DetectionMatch]:
        """Convert ML filter matches to unified DetectionMatch format."""
        
        unified_matches = []
        
        for match in matches:
            # Handle different match formats
            if hasattr(match, 'to_dict'):
                match_dict = match.to_dict()
            elif hasattr(match, '__dict__'):
                match_dict = match.__dict__
            else:
                match_dict = match
            
            # Extract line number with fallbacks
            line_num = (match_dict.get('line_number') or 
                       match_dict.get('line') or 
                       match_dict.get('start_line') or 1)
            
            # Extract matched text with fallbacks
            matched_text = (match_dict.get('matched_text') or 
                           match_dict.get('text') or 
                           match_dict.get('value') or '')
            
            # Extract snippet (context around the match)
            snippet = self._extract_snippet(content, line_num, matched_text)
            
            # Create unified DetectionMatch
            unified_match = DetectionMatch(
                file=str(file_path),
                line=line_num,
                engine="ml_filter",
                rule_id=match_dict.get('pattern_name', match_dict.get('rule_id', 'ml_filtered')),
                severity=match_dict.get('severity', match_dict.get('risk_level', 'MEDIUM')),
                confidence=match_dict.get('confidence', match_dict.get('confidence_score', 0.8)),
                snippet=snippet,
                description=match_dict.get('description', 'ML-filtered detection'),
                pattern_name=match_dict.get('pattern_name', ''),
                matched_text=matched_text,
                column_start=match_dict.get('column_start', 0),
                column_end=match_dict.get('column_end', 0),
                risk_level=self._get_risk_level(match_dict.get('risk_level')),
                context_before=match_dict.get('context_before', ''),
                context_after=match_dict.get('context_after', ''),
                false_positive=match_dict.get('false_positive', False),
                validated=match_dict.get('validated', False),
                legitimate_usage_flag=match_dict.get('legitimate_usage_flag', False),
                metadata=match_dict.get('metadata', {}),
                context_info=match_dict.get('context_info', {}),
                confidence_score=match_dict.get('confidence_score', 0.0)
            )
            
            unified_matches.append(unified_match)
        
        return unified_matches
    
    def _extract_snippet(self, content: str, line_num: int, matched_text: str, 
                         context_lines: int = 2) -> str:
        """Extract code snippet around the matched line."""
        try:
            lines = content.splitlines()
            if line_num <= 0 or line_num > len(lines):
                return matched_text
            
            start_line = max(0, line_num - context_lines - 1)
            end_line = min(len(lines), line_num + context_lines)
            
            snippet_lines = []
            for i in range(start_line, end_line):
                line_content = lines[i]
                if i == line_num - 1:  # Current line (0-indexed)
                    snippet_lines.append(f"→ {line_content}")
                else:
                    snippet_lines.append(f"  {line_content}")
            
            return '\n'.join(snippet_lines)
        except Exception:
            return matched_text
    
    # Backward-compatibility wrapper for legacy tests/APIs
    def _extract_features(self, match: DetectionMatch, content: str):
        return self.feature_extractor.extract_features(match, content)
    
    def _determine_filtering_strategy(self) -> FilteringStrategy:
        """Determine the best filtering strategy based on current system state."""
        circuit_state = self.circuit_breaker.get_state()
        
        # If circuit breaker is open, use rule-based only
        if circuit_state['state'] == CircuitBreakerState.OPEN.value:
            self.filtering_stats['circuit_breaker_trips'] += 1
            return FilteringStrategy.RULE_BASED_ONLY
        
        # If ML not available, use rule-based only
        if not ML_AVAILABLE or not self.model_pipeline:
            return FilteringStrategy.RULE_BASED_ONLY
        
        # Use hybrid by default for best reliability
        return FilteringStrategy.HYBRID
    
    def _apply_ml_filtering(self, 
                           matches: List[DetectionMatch],
                           content: str,
                           context: InferenceContext,
                           batch_size: int) -> Tuple[List[DetectionMatch], List[Tuple[str, float, float]], List[str]]:
        """Apply ML-based filtering with batch processing."""
        filtered_matches = []
        confidence_adjustments = []
        errors = []
        
        try:
            # Process in batches for memory efficiency
            for i in range(0, len(matches), batch_size):
                batch = matches[i:i + batch_size]
                batch_features = []
                
                # Extract features for batch
                for match in batch:
                    try:
                        features = self.feature_extractor.extract_features(match, content, context)
                        batch_features.append(features)
                    except Exception as e:
                        self.logger.warning(f"Feature extraction failed for match: {e}")
                        batch_features.append(np.zeros(len(self.feature_extractor.get_feature_names())))
                        errors.append(f"Feature extraction error: {str(e)}")
                
                # Batch prediction
                if batch_features:
                    X_batch = np.array(batch_features)
                    
                    # Get predictions
                    predictions = self.model_pipeline.predict_proba(X_batch)[:, 1]
                    
                    # Filter based on predictions
                    for j, (match, prediction) in enumerate(zip(batch, predictions)):
                        original_confidence = match.confidence
                        
                        # Adjust confidence based on ML prediction
                        adjusted_confidence = self._calculate_adjusted_confidence(
                            original_confidence, prediction
                        )
                        
                        # Keep match if above threshold
                        if adjusted_confidence >= self.confidence_threshold:
                            # Update match confidence
                            updated_match = DetectionMatch(
                                file=match.file,
                                line=match.line,
                                engine="ml_filter",
                                rule_id=match.pattern_name,
                                severity=match.severity,
                                confidence=adjusted_confidence,
                                snippet=match.snippet,
                                description=match.description,
                                pattern_name=match.pattern_name,
                                matched_text=match.matched_text,
                                context_before=match.context_before,
                                context_after=match.context_after,
                                column_start=getattr(match, 'column_start', 0),
                                column_end=getattr(match, 'column_end', getattr(match, 'column_start', 0)),
                                risk_level=match.risk_level,
                                metadata={
                                    **(match.metadata or {}),
                                    'ml_prediction': float(prediction),
                                    'original_confidence': original_confidence,
                                    'ml_model_version': self.model_info.version if self.model_info else 'unknown',
                                    'filtering_strategy': 'ml_only'
                                }
                            )
                            
                            filtered_matches.append(updated_match)
                        
                        # Record adjustment
                        match_id = f"{match.pattern_name}:{match.line_number}:{getattr(match, 'column_start', 0)}"
                        confidence_adjustments.append((match_id, original_confidence, adjusted_confidence))
            
            self.filtering_stats['ml_predictions'] += len(matches)
            
        except Exception as e:
            self.logger.error(f"ML filtering batch processing failed: {e}")
            raise
        
        return filtered_matches, confidence_adjustments, errors
    
    def _apply_rule_based_filtering(self,
                                  matches: List[DetectionMatch],
                                  content: str,
                                  context: InferenceContext) -> Tuple[List[DetectionMatch], List[Tuple[str, float, float]], List[str]]:
        """Apply rule-based filtering as fallback."""
        filtered_matches = []
        confidence_adjustments = []
        errors = []
        
        for match in matches:
            try:
                original_confidence = match.confidence
                should_keep, adjusted_confidence = self._evaluate_match_rules(match, context)
                
                if should_keep:
                    # Update match with rule-based metadata
                    updated_match = DetectionMatch(
                        file=match.file,
                        line=match.line,
                        engine="ml_filter",
                        rule_id=match.pattern_name,
                        severity=match.severity,
                        confidence=adjusted_confidence,
                        snippet=match.snippet,
                        description=match.description,
                        pattern_name=match.pattern_name,
                        matched_text=match.matched_text,
                        context_before=match.context_before,
                        context_after=match.context_after,
                        column_start=getattr(match, 'column_start', 0),
                        column_end=getattr(match, 'column_end', getattr(match, 'column_start', 0)),
                        risk_level=match.risk_level,
                        metadata={
                            **(match.metadata or {}),
                            'original_confidence': original_confidence,
                            'filtering_strategy': 'rule_based',
                            'rule_based_adjustment': True
                        }
                    )
                    
                    filtered_matches.append(updated_match)
                
                # Record adjustment
                match_id = f"{match.pattern_name}:{match.line_number}:{getattr(match, 'column_start', 0)}"
                confidence_adjustments.append((match_id, original_confidence, adjusted_confidence))
                
            except Exception as e:
                self.logger.warning(f"Rule-based evaluation failed for match: {e}")
                # Keep match with original confidence on error
                filtered_matches.append(match)
                errors.append(f"Rule evaluation error: {str(e)}")
        
        self.filtering_stats['rule_based_fallbacks'] += len(matches)
        
        return filtered_matches, confidence_adjustments, errors
    
    def _apply_hybrid_filtering(self,
                              matches: List[DetectionMatch],
                              content: str,
                              context: InferenceContext,
                              batch_size: int) -> Tuple[List[DetectionMatch], List[Tuple[str, float, float]], List[str]]:
        """Apply hybrid ML + rule-based filtering."""
        try:
            # Try ML filtering first
            ml_matches, ml_adjustments, ml_errors = self._apply_ml_filtering(
                matches, content, context, batch_size
            )
            
            # Apply rule-based validation on ML results
            final_matches, rule_adjustments, rule_errors = self._apply_rule_based_filtering(
                ml_matches, content, context
            )
            
            # Combine adjustments and errors
            all_adjustments = ml_adjustments + rule_adjustments
            all_errors = ml_errors + rule_errors
            
            return final_matches, all_adjustments, all_errors
            
        except Exception as e:
            # Fallback to rule-based only
            self.logger.warning(f"Hybrid filtering failed, using rule-based fallback: {e}")
            return self._apply_rule_based_filtering(matches, content, context)
    
    def _calculate_adjusted_confidence(self, original_confidence: float, ml_prediction: float) -> float:
        """Calculate adjusted confidence combining original and ML prediction."""
        # Weighted combination of original confidence and ML prediction
        ml_weight = 0.7  # Give more weight to ML prediction
        original_weight = 0.3
        
        adjusted = (ml_weight * ml_prediction) + (original_weight * original_confidence)
        
        # Ensure result is in valid range
        return max(0.0, min(1.0, adjusted))
    
    def _evaluate_match_rules(self, 
                            match: DetectionMatch,
                            context: InferenceContext) -> Tuple[bool, float]:
        """Evaluate match against rule-based criteria."""
        should_keep = True
        confidence_penalty = 0.0
        
        # Check file path patterns
        if context.file_path:
            file_path_lower = str(context.file_path).lower()
            
            # Test file patterns
            if any(pattern.search(file_path_lower) for pattern in self.rule_patterns['test_patterns']):
                confidence_penalty += 0.3
            
            # Config file patterns
            if any(pattern.search(file_path_lower) for pattern in self.rule_patterns['config_patterns']):
                confidence_penalty += 0.2
            
            # Documentation patterns
            if any(pattern.search(file_path_lower) for pattern in self.rule_patterns['doc_patterns']):
                confidence_penalty += 0.2
        
        # Check context metadata
        metadata = match.metadata or {}
        if metadata.get('context') in ['comment', 'docstring']:
            confidence_penalty += 0.25
        
        # Check for test function context
        function_name = metadata.get('function_name', '').lower()
        if function_name.startswith('test_') or 'test' in function_name:
            confidence_penalty += 0.3
        
        # Check match text patterns
        match_text_lower = match.matched_text.lower()
        test_indicators = ['test', 'example', 'sample', 'demo', 'mock', 'fake', 'dummy']
        if any(indicator in match_text_lower for indicator in test_indicators):
            confidence_penalty += 0.4
        
        # Framework-safe pattern rules (Enterprise-grade filtering)
        pattern_name = match.pattern_name.lower()
        
        # Dataflow sink specific filtering
        if pattern_name == 'dataflow_sink':
            # Check if it's a common framework pattern
            if self._is_framework_safe_sink(match, context.content):
                confidence_penalty += 0.5  # Aggressive reduction for framework patterns
            
            # Check for PII in arguments
            if not self._has_pii_in_context(match, context.content):
                confidence_penalty += 0.4  # Reduce confidence if no PII context
        
        # Framework-specific pattern detection
        if self._is_framework_safe_pattern(match, context.content):
            confidence_penalty += 0.4  # Reduce confidence for framework-safe patterns
        
        # ORM and database pattern detection
        if self._is_orm_operation(match, context.content):
            confidence_penalty += 0.35  # Reduce confidence for ORM operations
        
        # Route handler pattern detection
        if self._is_route_definition(match, context.content):
            confidence_penalty += 0.4  # Reduce confidence for route definitions
        
        # Parameterized query detection
        if self._is_parameterized_query(match, context.content):
            confidence_penalty += 0.4  # Reduce confidence for parameterized queries
        
        # Logging framework detection
        if self._is_logging_framework(match, context.content):
            confidence_penalty += 0.3  # Reduce confidence for logging
        
        # Apply penalties
        adjusted_confidence = match.confidence - confidence_penalty
        
        # Check if should keep based on threshold
        should_keep = adjusted_confidence >= self.confidence_threshold
        
        return should_keep, max(0.0, adjusted_confidence)
    
    def _is_framework_safe_sink(self, match: DetectionMatch, content: str) -> bool:
        """Detect if sink is a safe framework pattern."""
        try:
            line_num = match.line_number
            lines = content.split('\n')
            if line_num > len(lines):
                return False
            
            sink_context = lines[line_num - 1] if line_num > 0 else ""
            
            # Safe framework patterns
            safe_patterns = [
                r'cursor\.execute\([^,]+,\s*\([^)]+\)\)',  # Parameterized
                r'@app\.(get|post|put|delete)',  # Route decorators
                r'session\.query\(',  # SQLAlchemy ORM
                r'\.filter\(|\.get\(',  # Django ORM
                r'logger\.(info|debug|warning)',  # Logging
            ]
            
            for pattern in safe_patterns:
                if re.search(pattern, sink_context, re.IGNORECASE):
                    return True
            
            return False
        except Exception:
            return False
    
    def _has_pii_in_context(self, match: DetectionMatch, content: str) -> bool:
        """Check if match has PII context in arguments."""
        try:
            line_num = match.line_number
            lines = content.split('\n')
            if line_num > len(lines):
                return False
            
            context_line = lines[line_num - 1] if line_num > 0 else ""
            
            # PII patterns to look for
            pii_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            ]
            
            for pattern in pii_patterns:
                if re.search(pattern, context_line, re.IGNORECASE):
                    return True
            
            return False
        except Exception:
            return False
    
    def _is_framework_safe_pattern(self, match: DetectionMatch, content: str) -> bool:
        """Detect if match is a framework-safe pattern."""
        try:
            line_num = match.line_number
            lines = content.split('\n')
            if line_num > len(lines):
                return False
            
            context_line = lines[line_num - 1] if line_num > 0 else ""
            
            # Framework-safe patterns
            safe_patterns = [
                r'@app\.route',  # Flask routes
                r'@router\.',  # FastAPI routes
                r'def (get|post|put|delete)_',  # HTTP methods
                r'Model\.objects\.',  # Django ORM
                r'QuerySet\.',  # Django QuerySet
                r'session\.',  # SQLAlchemy session
                r'logger\.',  # Logging
                r'cursor\.execute\([^,]+,\s*%s',  # Parameterized queries
            ]
            
            for pattern in safe_patterns:
                if re.search(pattern, context_line, re.IGNORECASE):
                    return True
            
            return False
        except Exception:
            return False
    
    def _is_orm_operation(self, match: DetectionMatch, content: str) -> bool:
        """Detect if match is an ORM operation."""
        try:
            line_num = match.line_number
            lines = content.split('\n')
            if line_num > len(lines):
                return False
            
            context_line = lines[line_num - 1] if line_num > 0 else ""
            
            # ORM operation patterns
            orm_patterns = [
                r'\.save\(\)', r'\.create\(\)', r'\.update\(\)', r'\.delete\(\)',
                r'\.get\(\)', r'\.filter\(\)', r'\.all\(\)', r'\.first\(\)',
                r'Model\.objects\.', r'QuerySet\.', r'session\.query\(',
                r'\.objects\.(create|get|filter|update|delete)'
            ]
            
            for pattern in orm_patterns:
                if re.search(pattern, context_line, re.IGNORECASE):
                    return True
            
            return False
        except Exception:
            return False
    
    def _is_route_definition(self, match: DetectionMatch, content: str) -> bool:
        """Detect if match is a route definition."""
        try:
            line_num = match.line_number
            lines = content.split('\n')
            if line_num > len(lines):
                return False
            
            context_line = lines[line_num - 1] if line_num > 0 else ""
            
            # Route definition patterns
            route_patterns = [
                r'@app\.(get|post|put|delete|patch)',
                r'@router\.(get|post|put|delete|patch)',
                r'@bp\.(get|post|put|delete|patch)',
                r'def (get|post|put|delete|patch)_',
                r'@app\.route\(',
                r'@router\.route\(',
            ]
            
            for pattern in route_patterns:
                if re.search(pattern, context_line, re.IGNORECASE):
                    return True
            
            return False
        except Exception:
            return False
    
    def _is_parameterized_query(self, match: DetectionMatch, content: str) -> bool:
        """Detect if match is a parameterized query."""
        try:
            line_num = match.line_number
            lines = content.split('\n')
            if line_num > len(lines):
                return False
            
            context_line = lines[line_num - 1] if line_num > 0 else ""
            
            # Parameterized query indicators
            param_indicators = ['%s', '?', ':', 'format(', 'f"', 'f\'']
            if any(indicator in context_line for indicator in param_indicators):
                return True
            
            # Parameterized query patterns
            param_patterns = [
                r'cursor\.execute\([^,]+,\s*\([^)]+\)\)',
                r'cursor\.execute\([^,]+,\s*\[[^\]]+\]\)',
                r'\.execute\([^,]+,\s*%s\)',
                r'\.execute\([^,]+,\s*\?\)',
            ]
            
            for pattern in param_patterns:
                if re.search(pattern, context_line, re.IGNORECASE):
                    return True
            
            return False
        except Exception:
            return False
    
    def _is_logging_framework(self, match: DetectionMatch, content: str) -> bool:
        """Detect if match is a logging framework call."""
        try:
            line_num = match.line_number
            lines = content.split('\n')
            if line_num > len(lines):
                return False
            
            context_line = lines[line_num - 1] if line_num > 0 else ""
            
            # Logging framework patterns
            logging_patterns = [
                r'logger\.(info|debug|warning|error|critical)',
                r'logging\.(info|debug|warning|error|critical)',
                r'log\.(info|debug|warning|error|critical)',
                r'console\.(log|info|warn|error)',
                r'print\(',
            ]
            
            for pattern in logging_patterns:
                if re.search(pattern, context_line, re.IGNORECASE):
                    return True
            
            return False
        except Exception:
            return False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        with self._model_lock:
            circuit_state = self.circuit_breaker.get_state()
            
            # Calculate average inference times
            avg_inference_time = np.mean(self.inference_times) if self.inference_times else 0
            avg_batch_size = np.mean(self.batch_sizes) if self.batch_sizes else 0
            
            return {
                'filtering_stats': self.filtering_stats.copy(),
                'performance_metrics': {
                    'average_inference_time_ms': avg_inference_time,
                    'average_batch_size': avg_batch_size,
                    'total_inferences': len(self.inference_times),
                    'cache_hit_rate': self._calculate_cache_hit_rate()
                },
                'circuit_breaker_state': circuit_state,
                'model_info': asdict(self.model_info) if self.model_info else None,
                'ml_availability': {
                    'libraries_available': ML_AVAILABLE,
                    'model_loaded': self.model_pipeline is not None,
                    'feature_extractor_ready': self.feature_extractor is not None
                }
            }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate feature extraction cache hit rate."""
        try:
            with self.feature_extractor._cache_lock:
                total_requests = len(self.feature_extractor._feature_cache) + 1000  # Estimate
                cache_hits = len(self.feature_extractor._feature_cache)
                return cache_hits / total_requests if total_requests > 0 else 0.0
        except Exception:
            return 0.0
    
    def retrain_model(self, 
                     feedback_data: List[Dict[str, Any]],
                     validation_data: Optional[List[Dict[str, Any]]] = None) -> ModelMetrics:
        """Retrain model with user feedback data."""
        if not ML_AVAILABLE:
            raise MLModelError("Cannot retrain model - ML libraries not available")
        
        try:
            self.logger.info(f"Retraining model with {len(feedback_data)} feedback samples")
            
            # Combine with existing training data
            existing_data = self._generate_training_data()
            all_training_data = existing_data + feedback_data
            
            # Train new model
            self._train_model(all_training_data)
            
            # Evaluate on validation data if provided
            if validation_data:
                metrics = self._evaluate_model(validation_data)
                self.logger.info(f"Model validation - Accuracy: {metrics.accuracy:.3f}")
                return metrics
            
            return self.model_info.metrics if self.model_info else ModelMetrics(0, 0, 0, 0)
            
        except Exception as e:
            raise MLModelError(f"Model retraining failed: {e}")
    
    def _evaluate_model(self, test_data: List[Dict[str, Any]]) -> ModelMetrics:
        """Evaluate model performance on test data."""
        if not self.model_pipeline:
            return ModelMetrics(0, 0, 0, 0)
        
        try:
            # Prepare test data
            X_test = np.array([sample['features'] for sample in test_data])
            y_test = np.array([sample['label'] for sample in test_data])
            
            # Make predictions
            y_pred = self.model_pipeline.predict(X_test)
            y_pred_proba = self.model_pipeline.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
            
            try:
                roc_auc = roc_auc_score(y_test, y_pred_proba)
            except ValueError:
                roc_auc = None
            
            conf_matrix = confusion_matrix(y_test, y_pred).tolist()
            
            return ModelMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                roc_auc=roc_auc,
                confusion_matrix=conf_matrix
            )
            
        except Exception as e:
            self.logger.error(f"Model evaluation failed: {e}")
            return ModelMetrics(0, 0, 0, 0)
    
    def __del__(self):
        """Clean up resources."""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
        except Exception:
            pass
    
    def shutdown(self, timeout: int = 30):
        """Graceful shutdown with timeout."""
        try:
            self.logger.info("Starting graceful shutdown of ML filter")
            
            # Stop monitoring threads
            if hasattr(self, '_monitoring_thread') and self._monitoring_thread.is_alive():
                self.logger.info("Stopping model monitoring thread")
                # Note: We can't easily stop the monitoring thread, but it's daemon so it will exit
            
            if hasattr(self, '_health_thread') and self._health_thread.is_alive():
                self.logger.info("Stopping health monitoring thread")
                # Note: We can't easily stop the health thread, but it's daemon so it will exit
            
            # Shutdown thread pool executor
            if hasattr(self, 'executor'):
                self.logger.info("Shutting down thread pool executor")
                self.executor.shutdown(wait=True, timeout=timeout)
            
            # Clear caches to free memory
            if hasattr(self, 'feature_extractor') and hasattr(self.feature_extractor, '_feature_cache'):
                with self.feature_extractor._cache_lock:
                    self.feature_extractor._feature_cache.clear()
            
            # Clear performance tracking arrays
            self.inference_times.clear()
            self.batch_sizes.clear()
            
            self.logger.info("ML filter shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", exc_info=True)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status for production monitoring."""
        try:
            health_status = self._perform_health_check()
            
            # Add additional production metrics
            health_status.update({
                'circuit_breaker': self.circuit_breaker.get_state(),
                'model_info': {
                    'loaded': self.model_pipeline is not None,
                    'model_id': self.model_info.model_id if self.model_info else None,
                    'version': self.model_info.version if self.model_info else None,
                    'last_switch': self.filtering_stats.get('model_switches', 0)
                } if self.model_info else None,
                'performance': {
                    'total_processed': self.filtering_stats['total_matches_processed'],
                    'total_filtered': self.filtering_stats['total_matches_filtered'],
                    'ml_predictions': self.filtering_stats['ml_predictions'],
                    'rule_fallbacks': self.filtering_stats['rule_based_fallbacks'],
                    'avg_inference_time': np.mean(self.inference_times) if self.inference_times else 0,
                    'uptime_seconds': time.time() - self.filtering_stats['uptime_start']
                },
                'errors': {
                    'total': self.filtering_stats['errors_total'],
                    'last_error_time': self.filtering_stats['last_error_time'],
                    'error_rate': (self.filtering_stats['errors_total'] / 
                                 max(self.filtering_stats['total_matches_processed'], 1))
                }
            })
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Failed to get health status: {e}", exc_info=True)
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }

    def _calculate_model_score(self, model_info: ModelInfo) -> float:
        """Calculate a composite score for model selection based on multiple metrics."""
        try:
            metrics = model_info.metrics
            
            # Base score from accuracy and F1 (most important metrics)
            base_score = (metrics.accuracy * 0.4) + (metrics.f1_score * 0.4)
            
            # Bonus for precision and recall
            if metrics.precision and metrics.recall:
                precision_recall_bonus = (metrics.precision + metrics.recall) * 0.1
                base_score += precision_recall_bonus
            
            # Bonus for ROC AUC if available
            if metrics.roc_auc:
                auc_bonus = metrics.roc_auc * 0.1
                base_score += auc_bonus
            
            # Recency bonus (newer models get slight preference)
            try:
                training_date = datetime.fromisoformat(model_info.training_date.replace('Z', '+00:00'))
                days_old = (datetime.now(timezone.utc) - training_date).days
                recency_bonus = max(0, (365 - days_old) / 365) * 0.05  # Max 5% bonus for very recent models
                base_score += recency_bonus
            except Exception:
                pass  # Ignore recency bonus if date parsing fails
            
            # Training data size bonus (more data = better model)
            total_samples = model_info.training_samples + model_info.validation_samples
            if total_samples > 0:
                data_size_bonus = min(1.0, total_samples / 1000) * 0.05  # Max 5% bonus for large datasets
                base_score += data_size_bonus
            
            # Ensure score is within [0, 1] range
            return max(0.0, min(1.0, base_score))
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate model score: {e}")
            # Return a default score based on basic metrics
            try:
                return (metrics.accuracy + metrics.f1_score) / 2
            except Exception:
                return 0.5  # Fallback score

    def _perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of the ML system."""
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'uptime_seconds': time.time() - self.filtering_stats['uptime_start'],
            'issues': [],
            'metrics': {}
        }
        
        try:
            # Check ML model availability
            if not self.model_pipeline:
                health_status['status'] = 'degraded'
                health_status['issues'].append('ML model not loaded')
            
            # Check circuit breaker state
            circuit_state = self.circuit_breaker.get_state()
            if circuit_state['state'] == 'open':
                health_status['status'] = 'degraded'
                health_status['issues'].append('Circuit breaker is open')
            
            # Check performance metrics
            if self.inference_times:
                avg_inference = sum(self.inference_times) / len(self.inference_times)
                if avg_inference > 1000:  # More than 1 second
                    health_status['status'] = 'degraded'
                    health_status['issues'].append('High inference latency')
                health_status['metrics']['avg_inference_time_ms'] = avg_inference
            
            # Check error rates
            total_operations = self.filtering_stats['total_matches_processed']
            if total_operations > 0:
                error_rate = self.filtering_stats['errors_total'] / total_operations
                if error_rate > 0.1:  # More than 10% error rate
                    health_status['status'] = 'degraded'
                    health_status['issues'].append('High error rate')
                health_status['metrics']['error_rate'] = error_rate
            
            # Check resource usage
            if hasattr(self.executor, '_threads'):
                active_threads = len([t for t in self.executor._threads if t.is_alive()])
                # Only warn about low thread availability after system has been running for a while
                if active_threads < 2 and health_status['uptime_seconds'] > 300:  # 5 minutes
                    health_status['status'] = 'degraded'
                    health_status['issues'].append('Low thread availability')
                health_status['metrics']['active_threads'] = active_threads
            
            # Check memory usage (if available)
            try:
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                if memory_mb > 1000:  # More than 1GB
                    health_status['status'] = 'degraded'
                    health_status['issues'].append('High memory usage')
                health_status['metrics']['memory_mb'] = memory_mb
            except ImportError:
                pass  # psutil not available
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['issues'].append(f'Health check failed: {str(e)}')
            self.logger.error(f"Health check error: {e}", exc_info=True)
        
        return health_status