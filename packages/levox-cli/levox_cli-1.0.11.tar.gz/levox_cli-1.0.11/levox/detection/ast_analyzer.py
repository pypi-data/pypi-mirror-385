"""
Level 2: Production-grade AST-based context analysis for PII detection using Tree-Sitter.

This module provides enterprise-level PII detection capabilities with:
- High-performance parsing and analysis
- Advanced context-aware scoring with dynamic confidence calculation
- Comprehensive language support with enhanced context detection
- Robust error handling and recovery
- Extensive configurability and extensibility
- Multi-language context classification and risk assessment
"""

import re
import time
import logging
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Set, Tuple, Union, Callable, NamedTuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache, wraps
from contextlib import contextmanager

from ..core.config import Config, DetectionPattern, RiskLevel
from ..core.exceptions import DetectionError, ParserError, AnalysisTimeoutError
from ..models.detection_result import DetectionMatch
from ..parsers import get_parser, is_supported_file, detect_language
from ..parsers.base import StringLiteral, Identifier, ContextType, RiskContext
from ..parsers.python_parser import PythonParser, FStringExpression, LoggingContext, TestContext
from ..parsers.javascript_parser import JavaScriptParser, TemplateLiteralExpression, ConsoleLoggingContext, TestFrameworkContext, ES6ModuleContext
from .context_analyzer import ContextAnalyzer


class AnalysisMode(Enum):
    """Analysis modes for different performance/accuracy trade-offs."""
    FAST = "fast"           # Basic patterns, minimal context
    BALANCED = "balanced"   # Default mode, good balance
    THOROUGH = "thorough"   # Deep analysis, maximum accuracy
    PARANOID = "paranoid"   # Exhaustive analysis for critical code


@dataclass
class EnhancedAnalysisContext:
    """Enhanced context information for advanced detection."""
    file_type: ContextType
    risk_context: RiskContext
    is_test_file: bool
    is_generated: bool
    has_suppressions: bool
    language_confidence: float
    encoding: str = "utf-8"
    framework_hints: Set[str] = field(default_factory=set)
    test_frameworks: Set[str] = field(default_factory=set)
    has_logging: bool = False
    has_sensitive_sinks: bool = False
    module_type: str = "unknown"
    business_context: Optional[str] = None
    language_specific_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatternMetrics:
    """Metrics for pattern performance tracking."""
    matches: int = 0
    false_positives: int = 0
    processing_time: float = 0.0
    confidence_sum: float = 0.0
    
    @property
    def average_confidence(self) -> float:
        return self.confidence_sum / max(1, self.matches)
    
    @property
    def precision_estimate(self) -> float:
        if self.matches == 0:
            return 1.0
        return max(0.0, (self.matches - self.false_positives) / self.matches)


class CompiledPattern(NamedTuple):
    """Compiled regex pattern with metadata."""
    pattern: re.Pattern
    name: str
    risk_level: RiskLevel
    confidence_base: float
    language_specificity: Set[str]
    context_modifiers: Dict[str, float]


class ASTAnalyzer:
    """
    Production-grade AST-based context analysis for PII detection.
    
    This analyzer provides enterprise-level capabilities:
    - Multi-threaded analysis for performance
    - Advanced caching and memoization
    - Comprehensive pattern library with continuous learning
    - Sophisticated false positive reduction using context-aware detection
    - Extensive metrics and telemetry
    - Configurable analysis modes
    - Multi-language context classification
    """
    
    # Class-level pattern cache to share across instances
    _pattern_cache: Dict[str, CompiledPattern] = {}
    _cache_lock = threading.RLock()
    
    def __init__(self, config: Config, analysis_mode: AnalysisMode = AnalysisMode.BALANCED):
        """
        Initialize the AST analyzer.
        
        Args:
            config: Configuration object with detection patterns and settings
            analysis_mode: Analysis mode for performance/accuracy trade-off
        """
        self.config = config
        self.analysis_mode = analysis_mode
        self.logger = logging.getLogger(f"levox.ast_analyzer.{id(self)}")
        
        # Performance and metrics tracking
        self.pattern_metrics: Dict[str, PatternMetrics] = {}
        self.analysis_stats = {
            'files_analyzed': 0,
            'total_matches': 0,
            'false_positives_filtered': 0,
            'context_aware_detections': 0,
            'average_analysis_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Thread safety
        self._stats_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(
            max_workers=min(4, (config.max_workers or 2)),
            thread_name_prefix="ast_analyzer"
        )
        
        # Initialize pattern libraries
        self._initialize_patterns()
        self._initialize_context_analyzers()
        
        # Performance optimizations
        self._content_hash_cache: Dict[str, List[DetectionMatch]] = {}
        self._max_cache_size = getattr(config, 'cache_size', 1000)
        
        # Enhanced context analysis
        self._context_cache: Dict[str, EnhancedAnalysisContext] = {}
        self._max_context_cache_size = 500
        
        # Initialize context analyzer for enhanced analysis
        self.context_analyzer = ContextAnalyzer(config)
        
        self.logger.info(f"Initialized Enhanced AST analyzer in {analysis_mode.value} mode")

    def _initialize_patterns(self) -> None:
        """Initialize and compile all detection patterns with optimizations."""
        
        # Advanced PII patterns with international support
        self.pii_patterns_config = {
            # Email patterns with enhanced detection
            'email': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:[A-Z|a-z]{2,}|[0-9]{1,3})\b',
                'risk_level': RiskLevel.MEDIUM,
                'confidence_base': 0.85,
                'context_modifiers': {
                    'assignment': 1.2, 'call_argument': 1.1, 'comment': 0.1, 'docstring': 0.05,
                    'test_context': 0.3, 'f_string': 1.3, 'template_literal': 1.3
                }
            },
            
            # SSN patterns (US and international variations)
            'ssn_us': {
                # Require hyphenated SSN to reduce numeric-cluster false positives (e.g., WKT/geo data)
                'pattern': r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b',
                'risk_level': RiskLevel.HIGH,
                'confidence_base': 0.95,
                'context_modifiers': {'test': 0.1, 'example': 0.05, 'f_string': 1.2}
            },
            
            'sin_canada': {
                'pattern': r'\b\d{3}[-\s]?\d{3}[-\s]?\d{3}\b',
                'risk_level': RiskLevel.HIGH,
                'confidence_base': 0.85,
                'context_modifiers': {'test': 0.1, 'f_string': 1.2}
            },
            
            # Credit card patterns with Luhn algorithm consideration
            'credit_card': {
                'pattern': r'\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6011|65\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                'risk_level': RiskLevel.HIGH,
                'confidence_base': 0.90,
                'context_modifiers': {'test': 0.05, 'example': 0.02, 'f_string': 1.2}
            },
            
            # Phone patterns (international)
            'phone_us': {
                'pattern': r'\b(?:\+1[-\s]?)?\(?[2-9]\d{2}\)?[-\s]?[2-9]\d{2}[-\s]?\d{4}\b',
                'risk_level': RiskLevel.MEDIUM,
                'confidence_base': 0.75,
                'context_modifiers': {'test': 0.4, 'f_string': 1.1}
            },
            
            'phone_intl': {
                'pattern': r'\+(?:[1-9]\d{0,3}[-\s]?)?(?:\d{1,4}[-\s]?){1,4}\d{1,9}\b',
                'risk_level': RiskLevel.MEDIUM,
                'confidence_base': 0.70,
                'context_modifiers': {'test': 0.4, 'f_string': 1.1}
            },
            
            # Enhanced API key and token patterns
            'api_key_generic': {
                'pattern': r'\b[A-Za-z0-9]{32,}\b',
                'risk_level': RiskLevel.HIGH,
                'confidence_base': 0.60,
                'context_modifiers': {'variable_assignment': 1.5, 'config': 1.3, 'f_string': 1.4}
            },
            
            'jwt_token': {
                'pattern': r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b',
                'risk_level': RiskLevel.HIGH,
                'confidence_base': 0.98,
                'context_modifiers': {'f_string': 1.1, 'template_literal': 1.1}
            },
            
            # Cloud provider specific keys
            'aws_access_key': {
                'pattern': r'\bAKIA[0-9A-Z]{16}\b',
                'risk_level': RiskLevel.CRITICAL,
                'confidence_base': 0.99,
                'context_modifiers': {'f_string': 1.0, 'template_literal': 1.0}
            },
            
            'gcp_api_key': {
                'pattern': r'\bAIza[0-9A-Za-z_-]{35}\b',
                'risk_level': RiskLevel.CRITICAL,
                'confidence_base': 0.99,
                'context_modifiers': {'f_string': 1.0, 'template_literal': 1.0}
            },
            
            # Personal information patterns
            'ip_address': {
                'pattern': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                'risk_level': RiskLevel.LOW,
                'confidence_base': 0.85,
                'context_modifiers': {'config': 0.3, 'test': 0.2, 'f_string': 1.1}
            },
            
            # Passwords and secrets
            'password_hash': {
                'pattern': r'\$(?:2[aby]?|5|6)\$[0-9]{2}\$[A-Za-z0-9./]{53,}',
                'risk_level': RiskLevel.HIGH,
                'confidence_base': 0.95,
                'context_modifiers': {'f_string': 1.0, 'template_literal': 1.0}
            }
        }
        
        # Compile patterns with caching
        self._compile_patterns()
        
        # Sophisticated suppression patterns
        self.suppression_patterns = {
            'inline_comment': re.compile(
                r'(?:#|//|/\*)\s*(?:levox|pii|security):\s*(?:ignore|suppress|skip)(?:\s|$|\*/)',
                re.IGNORECASE
            ),
            'block_comment': re.compile(
                r'/\*[\s\S]*?(?:levox|pii|security):\s*(?:ignore|suppress)[\s\S]*?\*/',
                re.IGNORECASE
            ),
            'docstring_suppression': re.compile(
                r'(?:"""[\s\S]*?"""|\'\'\'\s*[\s\S]*?\'\'\')[\s\S]*?(?:levox|pii|security):\s*ignore',
                re.IGNORECASE
            ),
            'test_patterns': re.compile(
                r'\b(?:test|spec|mock|fake|dummy|example|demo|sample|fixture|stub)_',
                re.IGNORECASE
            ),
            'false_positive_markers': re.compile(
                r'\b(?:placeholder|template|example\.com|test\.com|localhost|127\.0\.0\.1|0\.0\.0\.0)\b',
                re.IGNORECASE
            )
        }

    def _compile_patterns(self) -> None:
        """Compile regex patterns with caching and optimization."""
        with self._cache_lock:
            for name, config in self.pii_patterns_config.items():
                cache_key = f"{name}_{hash(config['pattern'])}"
                
                if cache_key not in self._pattern_cache:
                    try:
                        compiled_pattern = re.compile(
                            config['pattern'], 
                            re.IGNORECASE | re.MULTILINE
                        )
                        
                        self._pattern_cache[cache_key] = CompiledPattern(
                            pattern=compiled_pattern,
                            name=name,
                            risk_level=config['risk_level'],
                            confidence_base=config['confidence_base'],
                            language_specificity=set(config.get('languages', [])),
                            context_modifiers=config.get('context_modifiers', {})
                        )
                        
                    except re.error as e:
                        self.logger.error(f"Failed to compile pattern {name}: {e}")
                        continue

    def _initialize_context_analyzers(self) -> None:
        """Initialize context analysis components."""
        
        # Enhanced sensitive function patterns by language and framework
        self.sensitive_functions = {
            'python': {
                'logging': {
                    'functions': ['info', 'debug', 'warning', 'error', 'critical', 'log', 'exception'],
                    'patterns': [r'logging\.\w+\s*\(', r'logger\.\w+\s*\(', r'log\.\w+\s*\('],
                    'risk_multiplier': 1.2
                },
                'print_output': {
                    'functions': ['print', 'pprint', 'pp'],
                    'patterns': [r'\bprint\s*\(', r'pprint\s*\('],
                    'risk_multiplier': 1.0
                },
                'network': {
                    'functions': ['get', 'post', 'put', 'delete', 'patch', 'urlopen', 'send'],
                    'patterns': [r'requests\.\w+\s*\(', r'urllib\.request\.\w+\s*\(', r'socket\.\w+\s*\('],
                    'risk_multiplier': 1.8
                },
                'database': {
                    'functions': ['execute', 'executemany', 'query', 'insert', 'update', 'delete'],
                    'patterns': [r'cursor\.\w+\s*\(', r'connection\.\w+\s*\('],
                    'risk_multiplier': 2.0
                },
                'file_operations': {
                    'functions': ['write', 'writelines', 'dump', 'dumps', 'save'],
                    'patterns': [r'open\s*\(.*["\'][wa]', r'\.\w*write\w*\s*\('],
                    'risk_multiplier': 1.5
                },
                'f_strings': {
                    'functions': ['f-string', 'format_string'],
                    'patterns': [r'f["\']', r'\.format\('],
                    'risk_multiplier': 1.4
                }
            },
            
            'javascript': {
                'console': {
                    'functions': ['log', 'info', 'warn', 'error', 'debug', 'trace'],
                    'patterns': [r'console\.\w+\s*\('],
                    'risk_multiplier': 1.0
                },
                'network': {
                    'functions': ['fetch', 'XMLHttpRequest', 'get', 'post'],
                    'patterns': [r'fetch\s*\(', r'axios\.\w+\s*\(', r'\.ajax\s*\('],
                    'risk_multiplier': 1.8
                },
                'storage': {
                    'functions': ['setItem', 'localStorage', 'sessionStorage'],
                    'patterns': [r'localStorage\.\w+\s*\(', r'sessionStorage\.\w+\s*\('],
                    'risk_multiplier': 1.4
                },
                'template_literals': {
                    'functions': ['template_literal', 'string_interpolation'],
                    'patterns': [r'`.*\$\{.*\}.*`'],
                    'risk_multiplier': 1.3
                }
            }
        }
        
        # Enhanced identifier patterns with context awareness
        self.suspicious_identifiers = {
            'credentials': {
                'pattern': re.compile(r'(?:password|passwd|pwd|pass|secret|key|token|auth|credential)s?', re.IGNORECASE),
                'risk_level': RiskLevel.HIGH,
                'confidence_base': 0.8,
                'context_modifiers': {'variable': 1.3, 'parameter': 1.2, 'function_name': 0.6}
            },
            'personal_info': {
                'pattern': re.compile(r'(?:email|mail|phone|mobile|ssn|sin|social|address|name|surname|firstname|lastname)', re.IGNORECASE),
                'risk_level': RiskLevel.MEDIUM,
                'confidence_base': 0.7,
                'context_modifiers': {'variable': 1.2, 'class_member': 1.1}
            },
            'financial': {
                'pattern': re.compile(r'(?:credit|card|cc|cvv|account|bank|routing|iban|sort)', re.IGNORECASE),
                'risk_level': RiskLevel.HIGH,
                'confidence_base': 0.85,
                'context_modifiers': {'variable': 1.4, 'parameter': 1.3}
            },
            'medical': {
                'pattern': re.compile(r'(?:patient|medical|health|diagnosis|prescription|dob|birth)', re.IGNORECASE),
                'risk_level': RiskLevel.HIGH,
                'confidence_base': 0.8
            }
        }

    def _get_enhanced_context(self, file_path: Path, content: str, language: str) -> EnhancedAnalysisContext:
        """Get enhanced context analysis using the new context system."""
        cache_key = f"{file_path}_{hash(content[:1000])}_{language}"
        
        if cache_key in self._context_cache:
            return self._context_cache[cache_key]
        
        # Get base context from parser
        parser = get_parser(file_path, content, self.config)
        if parser and hasattr(parser, 'get_enhanced_context_analysis'):
            base_context = parser.get_enhanced_context_analysis(content, file_path)
        else:
            # Fallback to basic context analysis
            base_context = self._analyze_basic_context(file_path, content)
        
        # Create enhanced context
        enhanced_context = EnhancedAnalysisContext(
            file_type=ContextType(base_context.get('context_type', 'production')),
            risk_context=RiskContext(base_context.get('risk_context', 'medium_risk')),
            is_test_file=base_context.get('is_test_file', False),
            is_generated=base_context.get('is_generated', False),
            has_suppressions=base_context.get('has_suppressions', False),
            language_confidence=base_context.get('language_confidence', 0.8),
            framework_hints=set(base_context.get('framework_hints', [])),
            test_frameworks=set(base_context.get('test_frameworks', [])),
            has_logging=base_context.get('has_logging', False),
            has_sensitive_sinks=base_context.get('has_sensitive_sinks', False),
            module_type=base_context.get('module_type', 'unknown'),
            business_context=base_context.get('business_context'),
            language_specific_context=self._get_language_specific_context(parser, content, language)
        )
        
        # Cache the context
        if len(self._context_cache) < self._max_context_cache_size:
            self._context_cache[cache_key] = enhanced_context
        
        return enhanced_context
    
    def _get_language_specific_context(self, parser, content: str, language: str) -> Dict[str, Any]:
        """Get language-specific context information."""
        if not parser:
            return {}
        
        try:
            if language == 'python' and hasattr(parser, 'get_enhanced_analysis'):
                return parser.get_enhanced_analysis(content, Path('temp.py'))
            elif language == 'javascript' and hasattr(parser, 'get_enhanced_analysis'):
                return parser.get_enhanced_analysis(content, Path('temp.js'))
            else:
                return {}
        except Exception as e:
            self.logger.debug(f"Failed to get language-specific context: {e}")
            return {}
    
    def _analyze_basic_context(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Fallback basic context analysis when enhanced analysis is not available."""
        path_lower = str(file_path).lower()
        content_lower = content[:1000].lower()
        
        is_test = any(marker in path_lower for marker in ['test', 'spec', '__tests__', '.test.', '.spec.'])
        is_generated = any(marker in content_lower for marker in ['auto-generated', 'generated by', 'DO NOT EDIT'])
        has_suppressions = any(pattern.search(content[:1000]) for pattern in self.suppression_patterns.values())
        
        return {
            'context_type': 'test' if is_test else 'production',
            'risk_context': 'safe' if is_test else 'medium_risk',
            'is_test_file': is_test,
            'is_generated': is_generated,
            'has_suppressions': has_suppressions,
            'framework_hints': [],
            'language_confidence': 0.8,
            'test_frameworks': [],
            'has_logging': False,
            'has_sensitive_sinks': False,
            'module_type': 'unknown',
            'business_context': None
        }

    @contextmanager
    def _performance_monitor(self, operation: str):
        """Context manager for performance monitoring."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self.logger.debug(f"{operation} completed in {duration:.3f}s")

    def _get_content_hash(self, content: str) -> str:
        """Generate hash for content caching."""
        return hashlib.sha256(content.encode('utf-8', errors='ignore')).hexdigest()[:16]

    @lru_cache(maxsize=1000)
    def _analyze_context_type(self, file_path: str, content_preview: str) -> EnhancedAnalysisContext:
        """
        Analyze and determine the context type of a file.
        
        Args:
            file_path: Path to the file
            content_preview: First 1000 characters of the file
            
        Returns:
            AnalysisContext with detailed context information
        """
        path_lower = file_path.lower()
        
        # Determine file type
        if any(marker in path_lower for marker in ['test', 'spec', '__tests__', '.test.', '.spec.']):
            file_type = ContextType.TEST
            is_test = True
        elif any(marker in path_lower for marker in ['doc', 'readme', 'example', 'sample']):
            file_type = ContextType.DOCUMENTATION
            is_test = False
        elif any(marker in path_lower for marker in ['config', 'settings', '.env', '.ini']):
            file_type = ContextType.CONFIGURATION
            is_test = False
        else:
            file_type = ContextType.PRODUCTION
            is_test = False
        
        # Check for generated code markers
        generated_markers = ['auto-generated', 'generated by', '# Generated', '// Generated', '@generated']
        is_generated = any(marker in content_preview for marker in generated_markers)
        
        # Check for suppression patterns
        has_suppressions = any(
            pattern.search(content_preview) 
            for pattern in self.suppression_patterns.values()
        )
        
        # Detect framework hints
        framework_hints = set()
        framework_patterns = {
            'django': ['from django', 'import django', 'django.'],
            'flask': ['from flask', 'import flask', '@app.route'],
            'fastapi': ['from fastapi', 'import fastapi', '@app.get'],
            'react': ['import React', 'from "react"', 'useState'],
            'vue': ['import Vue', 'new Vue', 'vue-'],
            'angular': ['@angular', 'import { Component }', 'ngOnInit']
        }
        
        for framework, patterns in framework_patterns.items():
            if any(pattern in content_preview for pattern in patterns):
                framework_hints.add(framework)
        
        return EnhancedAnalysisContext(
            file_type=file_type,
            risk_context=RiskContext.MEDIUM_RISK,
            is_test_file=is_test,
            is_generated=is_generated,
            has_suppressions=has_suppressions,
            language_confidence=0.9,  # Would be computed by language detector
            framework_hints=framework_hints,
            test_frameworks=set(),
            has_logging=False,
            has_sensitive_sinks=False,
            module_type="unknown"
        )

    def analyze_file(self, file_path: Path, content: str, language: str, 
                    timeout: Optional[float] = None) -> List[DetectionMatch]:
        """
        Analyze file using AST for context-aware detection.
        
        Args:
            file_path: Path to the file being analyzed
            content: File content as string
            language: Programming language of the file
            timeout: Optional timeout for analysis
            
        Returns:
            List of detection matches found in the file
            
        Raises:
            AnalysisTimeoutError: If analysis exceeds timeout
            DetectionError: If analysis fails critically
        """
        
        analysis_start = time.perf_counter()
        
        # Set default timeout based on analysis mode
        if timeout is None:
            timeout_map = {
                AnalysisMode.FAST: 5.0,
                AnalysisMode.BALANCED: 15.0,
                AnalysisMode.THOROUGH: 30.0,
                AnalysisMode.PARANOID: 60.0
            }
            timeout = timeout_map[self.analysis_mode]
        
        try:
            with self._performance_monitor(f"File analysis: {file_path.name}"):
                # Check cache first
                content_hash = self._get_content_hash(content)
                cache_key = f"{file_path}_{content_hash}_{language}_{self.analysis_mode.value}"
                
                if cache_key in self._content_hash_cache:
                    with self._stats_lock:
                        self.analysis_stats['cache_hits'] += 1
                    return self._content_hash_cache[cache_key].copy()
                
                with self._stats_lock:
                    self.analysis_stats['cache_misses'] += 1
                
                # Check if timeout exceeded
                if time.perf_counter() - analysis_start > timeout:
                    raise AnalysisTimeoutError(f"Analysis timeout for {file_path}")
                
                # Analyze file context
                context = self._analyze_context_type(str(file_path), content[:1000])
                
                # Check if file type is supported
                if not is_supported_file(file_path):
                    self.logger.debug(f"File type not supported for AST analysis: {file_path.suffix}")
                    return []
                
                # Get appropriate parser with error recovery
                try:
                    parser = get_parser(file_path, content, self.config)
                    if not parser:
                        # Quietly fall back when parsers are unavailable in the runtime
                        return self._fallback_regex_analysis(content, file_path, context)
                    
                    # Normalize modern Python syntax prior to parsing if needed
                    if str(file_path).endswith('.py'):
                        try:
                            from ..utils.python_syntax import normalize_modern_syntax
                            content = normalize_modern_syntax(content)
                        except Exception:
                            pass
                    parsed = parser.parse(content, file_path)
                    if not parsed:
                        self.logger.debug(f"Failed to parse {file_path}, falling back to regex")
                        return self._fallback_regex_analysis(content, file_path, context)
                        
                except Exception as e:
                    self.logger.debug(f"Parser error for {file_path}: {e}, using fallback")
                    return self._fallback_regex_analysis(content, file_path, context)
                
                # Perform multi-layered analysis
                all_matches = []
                
                # 1. String literal analysis (fallback if parser missing)
                if parser and self.analysis_mode in [AnalysisMode.BALANCED, AnalysisMode.THOROUGH, AnalysisMode.PARANOID]:
                    string_matches = self._analyze_string_literals(
                        parser, content, file_path, context, timeout - (time.perf_counter() - analysis_start)
                    )
                    if not string_matches:
                        # Fallback light string scan if parser yielded nothing
                        for m in re.finditer(r'"([^"]+)"|\'([^\']+)\'', content):
                            text = m.group(0).strip('"\'')
                            for _, compiled_pattern in self._pattern_cache.items():
                                if compiled_pattern.pattern.search(text):
                                    line_num = content[:m.start()].count('\n') + 1
                                    col_start = m.start() - (content.rfind('\n', 0, m.start()) + 1)
                                    col_end = col_start + len(m.group(0))
                                    string_matches.append(DetectionMatch(
                                        file=str(file_path),
                                        line=line_num,
                                        engine="ast",
                                        rule_id=compiled_pattern.name,
                                        severity=compiled_pattern.risk_level.value if hasattr(compiled_pattern.risk_level, 'value') else str(compiled_pattern.risk_level),
                                        confidence=min(1.0, compiled_pattern.confidence_base),
                                        snippet=text,
                                        description=f"AST-detected {compiled_pattern.name} pattern",
                                        pattern_name=(compiled_pattern.name if compiled_pattern.name in ['email','ssn_us','credit_card','phone_us','phone_intl'] else f"ast_{compiled_pattern.name}"),
                                        matched_text=text,
                                        column_start=col_start,
                                        column_end=col_end,
                                        risk_level=compiled_pattern.risk_level,
                                        context_before=self._safe_extract_context(content, m.start(), -50),
                                        context_after=self._safe_extract_context(content, m.end(), 50),
                                        metadata={'detection_level': 'ast', 'pattern_regex': compiled_pattern.pattern.pattern}
                                    ))
                    all_matches.extend(string_matches)
                elif not parser:
                    # Simple string literal scan when AST is unavailable
                    for m in re.finditer(r'"([^"]+)"|\'([^\']+)\'', content):
                        text = m.group(0).strip('"\'')
                        for _, compiled_pattern in self._pattern_cache.items():
                            if compiled_pattern.pattern.search(text):
                                line_num = content[:m.start()].count('\n') + 1
                                col_start = m.start() - (content.rfind('\n', 0, m.start()) + 1)
                                col_end = col_start + len(m.group(0))
                                all_matches.append(DetectionMatch(
                                    file=str(file_path),
                                    line=line_num,
                                    engine="ast",
                                    rule_id=compiled_pattern.name,
                                    severity=compiled_pattern.risk_level.value if hasattr(compiled_pattern.risk_level, 'value') else str(compiled_pattern.risk_level),
                                    confidence=min(1.0, compiled_pattern.confidence_base),
                                    snippet=text,
                                    description=f"AST-detected {compiled_pattern.name} pattern",
                                    pattern_name=(compiled_pattern.name if compiled_pattern.name in ['email','ssn_us','credit_card','phone_us','phone_intl'] else f"ast_{compiled_pattern.name}"),
                                    matched_text=text,
                                    column_start=col_start,
                                    column_end=col_end,
                                    risk_level=compiled_pattern.risk_level,
                                    context_before=self._safe_extract_context(content, m.start(), -50),
                                    context_after=self._safe_extract_context(content, m.end(), 50),
                                    metadata={'detection_level': 'ast', 'pattern_regex': compiled_pattern.pattern.pattern}
                                ))
                
                # 2. Identifier analysis
                if self.analysis_mode in [AnalysisMode.THOROUGH, AnalysisMode.PARANOID]:
                    identifier_matches = self._analyze_identifiers(
                        parser, content, file_path, context, timeout - (time.perf_counter() - analysis_start)
                    )
                    all_matches.extend(identifier_matches)
                
                # 3. Sensitive sink analysis
                if self.analysis_mode != AnalysisMode.FAST:
                    sink_matches = self._analyze_sensitive_sinks(
                        parser, content, file_path, language, context,
                        timeout - (time.perf_counter() - analysis_start)
                    )
                    all_matches.extend(sink_matches)
                
                # 4. Advanced pattern analysis for paranoid mode
                if self.analysis_mode == AnalysisMode.PARANOID:
                    advanced_matches = self._analyze_advanced_patterns(
                        content, file_path, context, timeout - (time.perf_counter() - analysis_start)
                    )
                    all_matches.extend(advanced_matches)
                
                # If AST-driven analysis found nothing, try regex fallback as safety net
                if not all_matches:
                    all_matches = self._fallback_regex_analysis(content, file_path, context)

                # Ensure we retain real code string detections even if comments are suppressed
                # Find non-comment string literals explicitly
                try:
                    lines = content.split('\n')
                    for m in re.finditer(r'"([^"]+)"|\'([^\']+)\'', content):
                        line_num = content[:m.start()].count('\n') + 1
                        line_text = lines[line_num - 1] if 0 < line_num <= len(lines) else ''
                        if line_text.strip().startswith('#'):
                            continue
                        text = m.group(0).strip('"\'')
                        for _, compiled_pattern in self._pattern_cache.items():
                            if compiled_pattern.pattern.search(text):
                                col_start = m.start() - (content.rfind('\n', 0, m.start()) + 1)
                                col_end = col_start + len(m.group(0))
                                all_matches.append(DetectionMatch(
                                    file=str(file_path),
                                    line=line_num,
                                    engine="ast",
                                    rule_id=compiled_pattern.name,
                                    severity=compiled_pattern.risk_level.value if hasattr(compiled_pattern.risk_level, 'value') else str(compiled_pattern.risk_level),
                                    confidence=min(1.0, compiled_pattern.confidence_base),
                                    snippet=text,
                                    description=f"AST-detected {compiled_pattern.name} pattern",
                                    pattern_name=(compiled_pattern.name if compiled_pattern.name in ['email','ssn_us','credit_card','phone_us','phone_intl'] else f"ast_{compiled_pattern.name}"),
                                    matched_text=text,
                                    column_start=col_start,
                                    column_end=col_end,
                                    risk_level=compiled_pattern.risk_level,
                                    context_before=self._safe_extract_context(content, m.start(), -50),
                                    context_after=self._safe_extract_context(content, m.end(), 50),
                                    metadata={'detection_level': 'ast', 'pattern_regex': compiled_pattern.pattern.pattern}
                                ))
                except Exception:
                    pass

                # Apply sophisticated filtering and ranking
                filtered_matches = self._apply_advanced_filtering(all_matches, content, file_path, context)
                
                # Cache results
                if len(self._content_hash_cache) < self._max_cache_size:
                    self._content_hash_cache[cache_key] = filtered_matches.copy()
                
                # Update statistics
                analysis_time = time.perf_counter() - analysis_start
                with self._stats_lock:
                    self.analysis_stats['files_analyzed'] += 1
                    self.analysis_stats['total_matches'] += len(filtered_matches)
                    # Update rolling average
                    total_files = self.analysis_stats['files_analyzed']
                    current_avg = self.analysis_stats['average_analysis_time']
                    self.analysis_stats['average_analysis_time'] = (
                        (current_avg * (total_files - 1) + analysis_time) / total_files
                    )
                
                self.logger.debug(
                    f"AST analysis of {file_path.name} completed in {analysis_time:.3f}s, "
                    f"found {len(filtered_matches)} high-confidence matches"
                )
                
                return filtered_matches
                
        except AnalysisTimeoutError:
            self.logger.error(f"Analysis timeout exceeded for {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Critical error in AST analysis for {file_path}: {e}")
            raise DetectionError(f"Analysis failed for {file_path}: {e}") from e

    def _fallback_regex_analysis(self, content: str, file_path: Path, 
                                context: EnhancedAnalysisContext) -> List[DetectionMatch]:
        """Fallback regex-based analysis when AST parsing fails."""
        matches = []
        lines = content.split('\n')
        
        for _cache_key, compiled_pattern in self._pattern_cache.items():
            for match in compiled_pattern.pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                current_line = lines[line_num - 1] if 0 < line_num <= len(lines) else ""
                prev_line = lines[line_num - 2] if line_num - 2 >= 0 else ""
                
                # Suppress explicit inline ignore directives
                if (self.suppression_patterns['inline_comment'].search(current_line) or
                    self.suppression_patterns['inline_comment'].search(prev_line)):
                    continue
                
                confidence = self._calculate_fallback_confidence(
                    compiled_pattern, match.group(), context
                )
                
                if confidence >= 0.5:
                    line_start = content.rfind('\n', 0, match.start())
                    if line_start == -1:
                        line_start = -1
                    col_start = match.start() - line_start
                    col_end = match.end() - line_start
                    
                    detection_match = DetectionMatch(
                        file=str(file_path),
                        line=line_num,
                        engine="ast",
                        rule_id=compiled_pattern.name,
                        severity=compiled_pattern.risk_level.value if hasattr(compiled_pattern.risk_level, 'value') else str(compiled_pattern.risk_level),
                        confidence=confidence,
                        snippet=match.group(),
                        description=f"Fallback regex-detected {compiled_pattern.name} pattern",
                        pattern_name=compiled_pattern.name if compiled_pattern.name in ['email','ssn_us','credit_card','phone_us','phone_intl'] else f"ast_{compiled_pattern.name}",
                        matched_text=match.group(),
                        column_start=col_start,
                        column_end=col_end,
                        risk_level=compiled_pattern.risk_level,
                        context_before=self._safe_extract_context(content, match.start(), -50),
                        context_after=self._safe_extract_context(content, match.end(), 50),
                        metadata={
                            'detection_level': 'ast',
                            'analysis_mode': self.analysis_mode.value,
                            'file_context': context.file_type.value,
                            'scan_timestamp': time.time(),
                            'pattern_regex': compiled_pattern.pattern.pattern
                        }
                    )
                    matches.append(detection_match)
        
        # Secondary fallback: use configured regex patterns if still no matches
        if not matches and getattr(self.config, 'patterns', None):
            try:
                for det_pattern in self.config.patterns:
                    try:
                        rx = re.compile(det_pattern.regex, re.IGNORECASE | re.MULTILINE)
                    except re.error:
                        continue
                    for match in rx.finditer(content):
                        line_num = content[:match.start()].count('\n') + 1
                        line_start = content.rfind('\n', 0, match.start())
                        if line_start == -1:
                            line_start = -1
                        col_start = match.start() - line_start
                        col_end = match.end() - line_start
                        current_line = lines[line_num - 1] if 0 < line_num <= len(lines) else ""
                        prev_line = lines[line_num - 2] if line_num - 2 >= 0 else ""
                        if (self.suppression_patterns['inline_comment'].search(current_line) or
                            self.suppression_patterns['inline_comment'].search(prev_line)):
                            continue
                        matches.append(DetectionMatch(
                            file=str(file_path),
                            line=line_num,
                            engine="ast",
                            rule_id=det_pattern.name,
                            severity=det_pattern.risk_level.value if hasattr(det_pattern.risk_level, 'value') else str(det_pattern.risk_level),
                            confidence=det_pattern.confidence,
                            snippet=match.group(),
                            description=f"Secondary fallback regex-detected {det_pattern.name} pattern",
                            pattern_name=det_pattern.name,
                            matched_text=match.group(),
                            column_start=col_start,
                            column_end=col_end,
                            risk_level=det_pattern.risk_level,
                            context_before=self._safe_extract_context(content, match.start(), -50),
                            context_after=self._safe_extract_context(content, match.end(), 50),
                            metadata={
                                'detection_level': 'ast',
                                'analysis_mode': self.analysis_mode.value,
                                'file_context': context.file_type.value,
                                'scan_timestamp': time.time(),
                                'pattern_regex': det_pattern.regex
                            }
                        ))
            except Exception:
                pass

        return matches

    def _analyze_string_literals(self, parser, content: str, file_path: Path, 
                               context: EnhancedAnalysisContext, remaining_timeout: float) -> List[DetectionMatch]:
        """Enhanced string literal analysis with advanced context awareness."""
        matches = []
        timeout_start = time.perf_counter()
        
        try:
            string_literals = parser.extract_strings(file_path, content)
            
            for string_literal in string_literals:
                # Check timeout
                if time.perf_counter() - timeout_start > remaining_timeout * 0.6:  # Use 60% of remaining time
                    self.logger.warning(f"String analysis timeout for {file_path}")
                    break
                
                # Enhanced PII detection with multiple patterns
                for pattern_key, compiled_pattern in self._pattern_cache.items():
                    pii_matches = compiled_pattern.pattern.finditer(string_literal.value)
                    
                    for pii_match in pii_matches:
                        # Advanced confidence calculation
                        confidence = self._calculate_enhanced_string_confidence(
                            string_literal, pii_match.group(), compiled_pattern, context
                        )
                        
                        # Dynamic threshold based on analysis mode
                        threshold_map = {
                            AnalysisMode.FAST: 0.7,
                            AnalysisMode.BALANCED: 0.5,
                            AnalysisMode.THOROUGH: 0.3,
                            AnalysisMode.PARANOID: 0.2
                        }
                        
                        if confidence >= threshold_map[self.analysis_mode]:
                            # Enhanced metadata collection
                            enhanced_metadata = {
                                'detection_level': 'ast_string',
                                'string_context': string_literal.context,
                                'parent_node_type': getattr(string_literal, 'parent_node_type', 'unknown'),
                                'analysis_mode': self.analysis_mode.value,
                                'file_context': context.file_type.value,
                                'is_test_file': context.is_test_file,
                                'is_generated': context.is_generated,
                                'framework_hints': list(context.framework_hints),
                                'pattern_type': compiled_pattern.name,
                                'string_length': len(string_literal.value),
                                'match_position': pii_match.start(),
                                'scan_timestamp': time.time()
                            }
                            
                            # Add context analysis if available
                            if self.context_analyzer:
                                try:
                                    # Create a mock node for context analysis
                                    mock_node = type('MockNode', (), {
                                        'name': pii_match.group(),
                                        'value': pii_match.group(),
                                        'start_line': string_literal.start_line,
                                        'start_col': string_literal.start_col + pii_match.start(),
                                        'end_col': string_literal.start_col + pii_match.end()
                                    })()
                                    
                                    # Analyze context
                                    context_info = {
                                        'is_test_file': context.is_test_file,
                                        'is_generated': context.is_generated,
                                        'file_context': context.file_type.value
                                    }
                                    
                                    # Check if this is legitimate usage
                                    legitimate_usage = self.context_analyzer.is_legitimate_usage(mock_node, context_info)
                                    enhanced_metadata['legitimate_usage'] = legitimate_usage
                                    
                                    # Check if this is test data
                                    is_test_data = self.context_analyzer.detect_test_data(mock_node)
                                    enhanced_metadata['is_test_data'] = is_test_data
                                    
                                    # Adjust confidence based on context
                                    if legitimate_usage:
                                        confidence *= 0.3
                                    if is_test_data:
                                        confidence *= 0.5
                                    
                                except Exception as e:
                                    self.logger.debug(f"Context analysis failed: {e}")
                            
                            # Additional validation for high-risk patterns
                            if compiled_pattern.risk_level == RiskLevel.CRITICAL:
                                enhanced_metadata['validation_result'] = self._validate_critical_match(
                                    pii_match.group(), compiled_pattern.name
                                )
                            
                            match = DetectionMatch(
                                file=str(file_path),
                                line=string_literal.start_line,
                                engine="ast",
                                rule_id=compiled_pattern.name,
                                severity=compiled_pattern.risk_level.value if hasattr(compiled_pattern.risk_level, 'value') else str(compiled_pattern.risk_level),
                                confidence=confidence,
                                snippet=pii_match.group(),
                                description=f"String literal analysis detected {compiled_pattern.name} pattern",
                                pattern_name=compiled_pattern.name,
                                matched_text=pii_match.group(),
                                column_start=string_literal.start_col + pii_match.start(),
                                column_end=string_literal.start_col + pii_match.end(),
                                risk_level=compiled_pattern.risk_level,
                                context_before=self._safe_extract_context(
                                    content, self._get_absolute_position(content, string_literal, pii_match.start()), -50
                                ),
                                context_after=self._safe_extract_context(
                                    content, self._get_absolute_position(content, string_literal, pii_match.end()), 50
                                ),
                                metadata=enhanced_metadata
                            )
                            matches.append(match)
                            
                            # Update pattern metrics
                            self._update_pattern_metrics(compiled_pattern.name, confidence)
        
        except Exception as e:
            self.logger.error(f"Failed to analyze string literals in {file_path}: {e}")
        
        return matches

    def _analyze_identifiers(self, parser, content: str, file_path: Path, 
                           context: EnhancedAnalysisContext, remaining_timeout: float) -> List[DetectionMatch]:
        """Enhanced identifier analysis with sophisticated naming pattern detection."""
        matches = []
        timeout_start = time.perf_counter()
        
        try:
            identifiers = parser.extract_identifiers(content)
            
            for identifier in identifiers:
                # Check timeout
                if time.perf_counter() - timeout_start > remaining_timeout * 0.3:  # Use 30% of remaining time
                    self.logger.warning(f"Identifier analysis timeout for {file_path}")
                    break
                
                # Enhanced suspicious identifier detection
                for category, config in self.suspicious_identifiers.items():
                    if config['pattern'].search(identifier.name):
                        # Advanced confidence calculation with context
                        confidence = self._calculate_identifier_confidence_advanced(
                            identifier, category, config, context
                        )
                        
                        # Apply stricter thresholds for identifiers
                        threshold_map = {
                            AnalysisMode.FAST: 0.8,
                            AnalysisMode.BALANCED: 0.6,
                            AnalysisMode.THOROUGH: 0.4,
                            AnalysisMode.PARANOID: 0.3
                        }
                        
                        if confidence >= threshold_map[self.analysis_mode]:
                            # Collect advanced metadata
                            enhanced_metadata = {
                                'detection_level': 'ast_identifier',
                                'identifier_category': category,
                                'identifier_context': identifier.context,
                                'parent_node_type': getattr(identifier, 'parent_node_type', 'unknown'),
                                'scope_type': getattr(identifier, 'scope_type', 'unknown'),
                                'is_declaration': getattr(identifier, 'is_declaration', False),
                                'analysis_mode': self.analysis_mode.value,
                                'file_context': context.file_type.value,
                                'is_test_file': context.is_test_file,
                                'framework_hints': list(context.framework_hints),
                                'identifier_length': len(identifier.name),
                                'naming_convention': self._analyze_naming_convention(identifier.name),
                                'scan_timestamp': time.time()
                            }
                            
                            # Add context analysis if available
                            if self.context_analyzer:
                                try:
                                    # Analyze variable context
                                    scope_info = {
                                        'is_test_function': context.is_test_file,
                                        'in_logging_call': 'log' in str(identifier.context).lower(),
                                        'in_test_assertion': context.is_test_file,
                                        'in_config': 'config' in str(identifier.context).lower()
                                    }
                                    
                                    variable_context = self.context_analyzer.analyze_variable_context(identifier, scope_info)
                                    enhanced_metadata['variable_context'] = variable_context
                                    
                                    # Check if this is legitimate usage
                                    context_info = {
                                        'is_test_file': context.is_test_file,
                                        'is_generated': context.is_generated,
                                        'file_context': context.file_type.value
                                    }
                                    
                                    legitimate_usage = self.context_analyzer.is_legitimate_usage(identifier, context_info)
                                    enhanced_metadata['legitimate_usage'] = legitimate_usage
                                    
                                    # Adjust confidence based on context
                                    if legitimate_usage:
                                        confidence *= 0.4
                                    if variable_context.context_type.value == 'test_mock':
                                        confidence *= 0.6
                                    
                                except Exception as e:
                                    self.logger.debug(f"Context analysis failed: {e}")
                            
                            match = DetectionMatch(
                                file=str(file_path),
                                line=identifier.start_line,
                                engine="ast",
                                rule_id=f"identifier_{category}",
                                severity=config['risk_level'].value if hasattr(config['risk_level'], 'value') else str(config['risk_level']),
                                confidence=confidence,
                                snippet=identifier.name,
                                description=f"AST identifier analysis detected suspicious {category} naming pattern",
                                pattern_name=f"ast_identifier_{category}",
                                matched_text=identifier.name,
                                column_start=identifier.start_col,
                                column_end=identifier.end_col,
                                risk_level=config['risk_level'],
                                context_before=self._safe_extract_context(
                                    content, self._get_absolute_position(content, identifier, 0), -50
                                ),
                                context_after=self._safe_extract_context(
                                    content, self._get_absolute_position(content, identifier, len(identifier.name)), 50
                                ),
                                metadata=enhanced_metadata
                            )
                            matches.append(match)
                            
                            # Update pattern metrics
                            self._update_pattern_metrics(f"identifier_{category}", confidence)
        
        except Exception as e:
            self.logger.error(f"Failed to analyze identifiers in {file_path}: {e}")
        
        return matches

    def _analyze_sensitive_sinks(self, parser, content: str, file_path: Path, language: str,
                               context: EnhancedAnalysisContext, remaining_timeout: float) -> List[DetectionMatch]:
        """Enhanced analysis of calls to sensitive functions that might leak PII."""
        matches = []
        timeout_start = time.perf_counter()
        
        try:
            language_sinks = self.sensitive_functions.get(language.lower(), {})
            
            for sink_category, sink_config in language_sinks.items():
                # Check timeout
                if time.perf_counter() - timeout_start > remaining_timeout * 0.4:  # Use 40% of remaining time
                    self.logger.warning(f"Sink analysis timeout for {file_path}")
                    break
                
                # Use both function names and patterns for detection
                all_patterns = []
                
                # Add explicit function patterns
                for func in sink_config['functions']:
                    all_patterns.append(rf'\b{re.escape(func)}\s*\(')
                
                # Add generic patterns
                all_patterns.extend(sink_config.get('patterns', []))
                
                for pattern_str in all_patterns:
                    try:
                        pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
                        
                        for match in pattern.finditer(content):
                            line_num = content[:match.start()].count('\n') + 1
                            
                            # Extract comprehensive function call context
                            call_context = self._extract_enhanced_function_context(content, match.start())
                            
                            # Multi-pattern PII detection in context
                            pii_indicators = self._detect_pii_in_context(call_context, context)
                            
                            if pii_indicators['has_pii']:
                                # Calculate sophisticated confidence score
                                confidence = self._calculate_sink_confidence(
                                    sink_category, sink_config, call_context, 
                                    pii_indicators, context
                                )
                                
                                if confidence >= 0.4:  # Reasonable threshold for sinks
                                    enhanced_metadata = {
                                        'detection_level': 'ast_sink',
                                        'sink_category': sink_category,
                                        'function_pattern': pattern_str,
                                        'risk_multiplier': sink_config.get('risk_multiplier', 1.0),
                                        'call_context': call_context[:300],  # Truncate for storage
                                        'pii_types_detected': pii_indicators['types'],
                                        'pii_confidence': pii_indicators['confidence'],
                                        'analysis_mode': self.analysis_mode.value,
                                        'file_context': context.file_type.value,
                                        'language': language,
                                        'framework_hints': list(context.framework_hints),
                                        'scan_timestamp': time.time()
                                    }
                                    
                                    # Add context analysis if available
                                    if self.context_analyzer:
                                        try:
                                            # Create a mock node for context analysis
                                            mock_node = type('MockNode', (), {
                                                'name': match.group(),
                                                'value': match.group(),
                                                'start_line': line_num,
                                                'start_col': match.start() - content.rfind('\n', 0, match.start()) - 1,
                                                'end_col': match.end() - content.rfind('\n', 0, match.start()) - 1
                                            })()
                                            
                                            # Analyze function purpose
                                            function_context = self.context_analyzer.analyze_function_purpose(mock_node, language)
                                            enhanced_metadata['function_purpose'] = function_context
                                            
                                            # Check if this is legitimate usage
                                            context_info = {
                                                'is_test_file': context.is_test_file,
                                                'is_generated': context.is_generated,
                                                'file_context': context.file_type.value,
                                                'function_purpose': function_context
                                            }
                                            
                                            legitimate_usage = self.context_analyzer.is_legitimate_usage(mock_node, context_info)
                                            enhanced_metadata['legitimate_usage'] = legitimate_usage
                                            
                                            # Adjust confidence based on context
                                            if legitimate_usage:
                                                confidence *= 0.5
                                            if function_context.purpose.value == 'sanitization':
                                                confidence *= 0.7
                                            
                                        except Exception as e:
                                            self.logger.debug(f"Context analysis failed: {e}")
                                    
                                    # Determine risk level based on sink type and PII detected
                                    risk_level = self._calculate_sink_risk_level(
                                        sink_category, pii_indicators, context
                                    )
                                    
                                    detection_match = DetectionMatch(
                                        file=str(file_path),
                                        line=line_num,
                                        engine="ast",
                                        rule_id=f"sink_{sink_category}",
                                        severity=risk_level.value if hasattr(risk_level, 'value') else str(risk_level),
                                        confidence=confidence,
                                        snippet=match.group(),
                                        description=f"AST sensitive sink analysis detected {sink_category} function call",
                                        pattern_name=f"ast_sink_{sink_category}",
                                        matched_text=match.group(),
                                        column_start=match.start() - content.rfind('\n', 0, match.start()) - 1,
                                        column_end=match.end() - content.rfind('\n', 0, match.start()) - 1,
                                        risk_level=risk_level,
                                        context_before=call_context[:100],
                                        context_after=call_context[100:200],
                                        metadata=enhanced_metadata
                                    )
                                    matches.append(detection_match)
                                    
                                    # Update pattern metrics
                                    self._update_pattern_metrics(f"sink_{sink_category}", confidence)
                    
                    except re.error as e:
                        self.logger.warning(f"Invalid regex pattern {pattern_str}: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Failed to analyze sensitive sinks in {file_path}: {e}")
        
        return matches

    def _analyze_advanced_patterns(self, content: str, file_path: Path, 
                                 context: EnhancedAnalysisContext, remaining_timeout: float) -> List[DetectionMatch]:
        """Advanced pattern analysis for paranoid mode - deep inspection techniques."""
        matches = []
        timeout_start = time.perf_counter()
        
        try:
            # 1. Entropy-based secret detection
            entropy_matches = self._entropy_based_detection(content, file_path, context)
            matches.extend(entropy_matches)
            
            if time.perf_counter() - timeout_start > remaining_timeout * 0.3:
                return matches
            
            # 2. Base64 encoded content analysis
            base64_matches = self._analyze_base64_content(content, file_path, context)
            matches.extend(base64_matches)
            
            if time.perf_counter() - timeout_start > remaining_timeout * 0.6:
                return matches
            
            # 3. URL and connection string analysis
            url_matches = self._analyze_urls_and_connections(content, context)
            matches.extend(url_matches)
            
            if time.perf_counter() - timeout_start > remaining_timeout * 0.9:
                return matches
            
            # 4. Configuration and environment variable analysis
            config_matches = self._analyze_configuration_patterns(content, file_path, context)
            matches.extend(config_matches)
        
        except Exception as e:
            self.logger.error(f"Advanced pattern analysis failed for {file_path}: {e}")
        
        return matches

    def _entropy_based_detection(self, content: str, file_path: Path, context: EnhancedAnalysisContext) -> List[DetectionMatch]:
        """Detect potential secrets using entropy analysis."""
        
        import math
        from collections import Counter
        
        matches = []
        
        # Look for high-entropy strings that might be secrets
        high_entropy_pattern = re.compile(r'\b[A-Za-z0-9+/=]{20,}\b')
        
        for match in high_entropy_pattern.finditer(content):
            text = match.group()
            
            # Calculate Shannon entropy
            if len(text) < 20:
                continue
                
            counter = Counter(text)
            length = len(text)
            entropy = -sum((count / length) * math.log2(count / length) for count in counter.values())
            
            # High entropy threshold (typical for random strings/keys)
            if entropy > 4.5:
                line_num = content[:match.start()].count('\n') + 1
                
                confidence = min(0.95, (entropy - 4.0) / 2.0)  # Scale entropy to confidence
                
                # Reduce confidence for test contexts
                if context.is_test_file:
                    confidence *= 0.3
                
                if confidence > 0.6:
                    detection_match = DetectionMatch(
                        file=str(file_path),
                        line=line_num,
                        engine="ast",
                        rule_id="high_entropy_string",
                        severity="HIGH",
                        confidence=confidence,
                        snippet=text,
                        description="AST entropy analysis detected high-entropy string that might be a secret",
                        pattern_name="ast_high_entropy_string",
                        matched_text=text,
                        column_start=match.start() - content.rfind('\n', 0, match.start()) - 1,
                        column_end=match.end() - content.rfind('\n', 0, match.start()) - 1,
                        risk_level=RiskLevel.HIGH,
                        context_before=self._safe_extract_context(content, match.start(), -50),
                        context_after=self._safe_extract_context(content, match.end(), 50),
                        metadata={
                            'detection_level': 'advanced_entropy',
                            'entropy_value': entropy,
                            'string_length': len(text),
                            'analysis_mode': self.analysis_mode.value,
                            'scan_timestamp': time.time(),
                            'pattern_regex': high_entropy_pattern.pattern
                        }
                    )
                    matches.append(detection_match)
        
        return matches

    def _analyze_base64_content(self, content: str, file_path: Path, context: EnhancedAnalysisContext) -> List[DetectionMatch]:
        """Analyze Base64 encoded content for potential secrets."""
        
        import base64
        
        matches = []
        
        # Look for Base64 patterns
        base64_pattern = re.compile(r'\b[A-Za-z0-9+/]{40,}={0,2}\b')
        
        for match in base64_pattern.finditer(content):
            text = match.group()
            
            try:
                # Attempt to decode
                decoded = base64.b64decode(text, validate=True).decode('utf-8', errors='ignore')
                
                # Check if decoded content contains PII patterns
                pii_found = []
                for pattern_key, compiled_pattern in self._pattern_cache.items():
                    if compiled_pattern.pattern.search(decoded):
                        pii_found.append(pattern_key)
                
                if pii_found:
                    line_num = content[:match.start()].count('\n') + 1
                    confidence = 0.8 * (0.3 if context.is_test_file else 1.0)
                    
                    detection_match = DetectionMatch(
                        file=str(file_path),
                        line=line_num,
                        engine="ast",
                        rule_id="base64_encoded_pii",
                        severity="HIGH",
                        confidence=confidence,
                        snippet=text[:100] + "..." if len(text) > 100 else text,
                        description="AST base64 analysis detected encoded PII content",
                        pattern_name="ast_base64_encoded_pii",
                        matched_text=text[:100] + "..." if len(text) > 100 else text,
                        column_start=match.start() - content.rfind('\n', 0, match.start()) - 1,
                        column_end=match.end() - content.rfind('\n', 0, match.start()) - 1,
                        risk_level=RiskLevel.HIGH,
                        context_before=self._safe_extract_context(content, match.start(), -50),
                        context_after=self._safe_extract_context(content, match.end(), 50),
                        metadata={
                            'detection_level': 'advanced_base64',
                            'decoded_length': len(decoded),
                            'pii_types_in_decoded': pii_found,
                            'analysis_mode': self.analysis_mode.value,
                            'scan_timestamp': time.time(),
                            'pattern_regex': base64_pattern.pattern
                        }
                    )
                    matches.append(detection_match)
            
            except Exception:
                # Not valid Base64 or couldn't decode
                continue
        
        return matches

    def _analyze_urls_and_connections(self, content: str, context: EnhancedAnalysisContext) -> List[DetectionMatch]:
        """Analyze URLs and connection strings for embedded credentials."""
        
        matches = []
        
        # Enhanced URL pattern with potential credentials
        url_with_creds_pattern = re.compile(
            r'(?:https?|ftp|jdbc|mongodb)://[^:\s]+:[^@\s]+@[^\s]+',
            re.IGNORECASE
        )
        
        for match in url_with_creds_pattern.finditer(content):
            url = match.group()
            line_num = content[:match.start()].count('\n') + 1
            
            # Extract potential username/password
            credential_part = url.split('@')[0].split('//')[-1]
            
            confidence = 0.9
            if context.is_test_file:
                confidence *= 0.2
            elif 'localhost' in url or '127.0.0.1' in url:
                confidence *= 0.4
            
            if confidence > 0.3:
                detection_match = DetectionMatch(
                    pattern_name="ast_url_with_credentials",
                    pattern_regex=url_with_creds_pattern.pattern,
                    matched_text=url,
                    line_number=line_num,
                    column_start=match.start() - content.rfind('\n', 0, match.start()) - 1,
                    column_end=match.end() - content.rfind('\n', 0, match.start()) - 1,
                    confidence=confidence,
                    risk_level=RiskLevel.HIGH,
                    context_before=self._safe_extract_context(content, match.start(), -50),
                    context_after=self._safe_extract_context(content, match.end(), 50),
                    metadata={
                        'detection_level': 'advanced_url_analysis',
                        'credential_part': credential_part,
                        'url_scheme': url.split('://')[0],
                        'analysis_mode': self.analysis_mode.value,
                        'scan_timestamp': time.time()
                    }
                )
                matches.append(detection_match)
        
        return matches

    def _analyze_configuration_patterns(self, content: str, file_path: Path, context: EnhancedAnalysisContext) -> List[DetectionMatch]:
        """Analyze configuration patterns and environment variables."""
        
        matches = []
        
        # Environment variable patterns with potential secrets
        env_patterns = [
            (r'\b[A-Z_]+(?:KEY|SECRET|TOKEN|PASSWORD|PASS|AUTH)[A-Z_]*\s*=\s*["\']?([^"\'\s]+)["\']?', 'env_secret'),
            (r'export\s+([A-Z_]+(?:KEY|SECRET|TOKEN|PASSWORD|PASS|AUTH)[A-Z_]*)\s*=\s*["\']?([^"\'\s]+)["\']?', 'export_secret'),
            (r'setenv\s+([A-Z_]+(?:KEY|SECRET|TOKEN|PASSWORD|PASS|AUTH)[A-Z_]*)\s+([^\s]+)', 'setenv_secret')
        ]
        
        for pattern_str, pattern_name in env_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
            
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                
                confidence = 0.8
                if context.is_test_file:
                    confidence *= 0.2
                elif context.file_type == ContextType.CONFIGURATION:
                    confidence *= 1.3
                
                if confidence > 0.3:
                    detection_match = DetectionMatch(
                        file=str(file_path),
                        line=line_num,
                        engine="ast",
                        rule_id=pattern_name,
                        severity="HIGH",
                        confidence=confidence,
                        snippet=match.group(),
                        description=f"AST configuration analysis detected {pattern_name} pattern",
                        pattern_name=f"ast_{pattern_name}",
                        matched_text=match.group(),
                        column_start=match.start() - content.rfind('\n', 0, match.start()) - 1,
                        column_end=match.end() - content.rfind('\n', 0, match.start()) - 1,
                        risk_level=RiskLevel.HIGH,
                        context_before=self._safe_extract_context(content, match.start(), -50),
                        context_after=self._safe_extract_context(content, match.end(), 50),
                        metadata={
                            'detection_level': 'advanced_config',
                            'config_type': pattern_name,
                            'variable_name': match.group(1) if match.groups() else '',
                            'analysis_mode': self.analysis_mode.value,
                            'scan_timestamp': time.time(),
                            'pattern_regex': pattern_str
                        }
                    )
                    matches.append(detection_match)
        
        return matches

    # Helper methods for enhanced analysis

    def _calculate_enhanced_string_confidence(self, string_literal: StringLiteral, 
                                           matched_text: str, compiled_pattern: CompiledPattern,
                                           context: EnhancedAnalysisContext) -> float:
        """Calculate sophisticated confidence score for string matches."""
        base_confidence = compiled_pattern.confidence_base
        
        # Context-based modifiers
        string_context = getattr(string_literal, 'context', 'unknown')
        context_modifier = compiled_pattern.context_modifiers.get(string_context, 1.0)
        base_confidence *= context_modifier
        
        # File context modifiers
        if context.is_test_file:
            # Keep detections in tests; only mildly reduce
            base_confidence *= 0.9
        elif context.is_generated:
            base_confidence *= 0.1
        elif context.file_type == ContextType.DOCUMENTATION:
            base_confidence *= 0.1
        elif context.file_type == ContextType.CONFIGURATION:
            base_confidence *= 1.2
        
        # Pattern-specific validations
        if compiled_pattern.name == 'credit_card':
            base_confidence *= self._validate_luhn_algorithm(matched_text)
        elif compiled_pattern.name.startswith('email'):
            base_confidence *= self._validate_email_format(matched_text)
        elif compiled_pattern.name.endswith('_us'):
            base_confidence *= self._validate_us_format(matched_text, compiled_pattern.name)
        
        # Framework-specific adjustments
        for framework in context.framework_hints:
            if framework in ['django', 'flask'] and 'email' in compiled_pattern.name:
                base_confidence *= 1.1  # Web frameworks often handle emails
        
        # String length and complexity factors
        if len(matched_text) > 50:  # Very long matches might be false positives
            base_confidence *= 0.9
        
        return min(1.0, max(0.0, base_confidence))

    def _calculate_identifier_confidence_advanced(self, identifier: Identifier, 
                                                category: str, config: Dict,
                                                context: EnhancedAnalysisContext) -> float:
        """Advanced confidence calculation for identifier matches."""
        base_confidence = config['confidence_base']
        
        # Context-based modifiers
        identifier_context = getattr(identifier, 'context', 'unknown')
        context_modifier = config.get('context_modifiers', {}).get(identifier_context, 1.0)
        base_confidence *= context_modifier
        
        # File context modifiers
        if context.is_test_file:
            base_confidence *= 0.85  # Slight reduction only
        elif context.file_type == ContextType.DOCUMENTATION:
            base_confidence *= 0.1
        
        # Naming convention analysis
        naming_style = self._analyze_naming_convention(identifier.name)
        if naming_style in ['snake_case', 'camelCase'] and category in ['credentials', 'personal_info']:
            base_confidence *= 1.2  # Proper naming suggests real variables
        
        # Scope and declaration context
        if hasattr(identifier, 'is_declaration') and identifier.is_declaration:
            base_confidence *= 1.3  # Declarations are more significant
        
        if hasattr(identifier, 'scope_type'):
            scope_modifiers = {
                'global': 1.4,
                'class': 1.2,
                'function': 1.0,
                'local': 0.8
            }
            base_confidence *= scope_modifiers.get(identifier.scope_type, 1.0)
        
        return min(1.0, max(0.0, base_confidence))

    def _calculate_sink_confidence(self, sink_category: str, sink_config: Dict,
                                 call_context: str, pii_indicators: Dict,
                                 context: EnhancedAnalysisContext) -> float:
        """Calculate confidence for sensitive sink detections."""
        base_confidence = 0.7
        
        # Apply risk multiplier from sink configuration
        risk_multiplier = sink_config.get('risk_multiplier', 1.0)
        base_confidence *= min(2.0, risk_multiplier)
        
        # PII confidence contributes
        base_confidence *= pii_indicators['confidence']
        
        # Multiple PII types increase confidence
        pii_type_count = len(pii_indicators['types'])
        if pii_type_count > 1:
            base_confidence *= (1.0 + (pii_type_count - 1) * 0.2)
        
        # Context modifiers
        if context.is_test_file:
            base_confidence *= 0.9
        elif context.file_type == ContextType.PRODUCTION:
            base_confidence *= 1.2
        
        # Sink-specific modifiers
        if sink_category == 'logging' and 'debug' in call_context.lower():
            base_confidence *= 0.8  # Debug logging might be less critical
        elif sink_category == 'network':
            base_confidence *= 1.3  # Network calls with PII are high risk
        elif sink_category == 'database':
            base_confidence *= 1.4  # Database operations with PII are very high risk
        
        return min(1.0, max(0.0, base_confidence))

    def _detect_pii_in_context(self, context_text: str, file_context: EnhancedAnalysisContext) -> Dict:
        """Detect PII patterns within a given context with confidence scoring."""
        pii_types = set()
        max_confidence = 0.0
        total_confidence = 0.0
        match_count = 0
        
        for pattern_key, compiled_pattern in self._pattern_cache.items():
            matches = compiled_pattern.pattern.finditer(context_text)
            
            for match in matches:
                pii_types.add(compiled_pattern.name)
                match_confidence = compiled_pattern.confidence_base
                
                # Adjust for context
                if file_context.is_test_file:
                    match_confidence *= 0.2
                
                max_confidence = max(max_confidence, match_confidence)
                total_confidence += match_confidence
                match_count += 1
        
        average_confidence = total_confidence / max(1, match_count)
        
        return {
            'has_pii': len(pii_types) > 0,
            'types': list(pii_types),
            'confidence': max_confidence,
            'average_confidence': average_confidence,
            'match_count': match_count
        }

    def _calculate_sink_risk_level(self, sink_category: str, pii_indicators: Dict,
                                 context: EnhancedAnalysisContext) -> RiskLevel:
        """Calculate risk level for sink detections."""
        # Start with medium risk
        base_risk = RiskLevel.MEDIUM
        
        # Upgrade based on PII types found
        critical_pii_types = {'aws_access_key', 'gcp_api_key', 'jwt_token', 'password_hash', 'credit_card'}
        high_pii_types = {'ssn_us', 'sin_canada', 'api_key_generic'}
        
        detected_types = set(pii_indicators['types'])
        
        if detected_types.intersection(critical_pii_types):
            base_risk = RiskLevel.CRITICAL
        elif detected_types.intersection(high_pii_types):
            base_risk = RiskLevel.HIGH
        
        # Sink category modifiers
        if sink_category in ['network', 'database'] and base_risk == RiskLevel.MEDIUM:
            base_risk = RiskLevel.HIGH
        elif sink_category == 'logging' and context.file_type == ContextType.PRODUCTION:
            if base_risk == RiskLevel.MEDIUM:
                base_risk = RiskLevel.HIGH
        
        # Context modifiers
        if context.is_test_file:
            # Downgrade risk for test files
            risk_map = {
                RiskLevel.CRITICAL: RiskLevel.HIGH,
                RiskLevel.HIGH: RiskLevel.MEDIUM,
                RiskLevel.MEDIUM: RiskLevel.LOW
            }
            base_risk = risk_map.get(base_risk, RiskLevel.LOW)
        
        return base_risk

    def _apply_advanced_filtering(self, matches: List[DetectionMatch], content: str,
                                file_path: Path, context: EnhancedAnalysisContext) -> List[DetectionMatch]:
        """Apply sophisticated filtering and ranking to reduce false positives."""
        if not matches:
            return matches
        
        filtered_matches = []
        
        # Group matches by line for contextual analysis
        matches_by_line = {}
        for match in matches:
            line_key = match.line_number
            if line_key not in matches_by_line:
                matches_by_line[line_key] = []
            matches_by_line[line_key].append(match)
        
        for line_num, line_matches in matches_by_line.items():
            # Apply line-level filtering
            line_filtered = self._filter_line_matches(line_matches, content, context)
            
            # Apply suppression rules
            suppression_filtered = self._apply_suppression_rules_advanced(
                line_filtered, content, line_num, context
            )
            
            # Apply confidence thresholds with dynamic adjustment
            confidence_filtered = self._apply_dynamic_confidence_filtering(
                suppression_filtered, context
            )
            
            filtered_matches.extend(confidence_filtered)
        
        # Remove duplicates and overlapping matches
        deduplicated = self._deduplicate_matches(filtered_matches)
        
        # Apply final ranking and selection
        final_matches = self._rank_and_select_matches(deduplicated, context)
        
        # Update statistics
        with self._stats_lock:
            self.analysis_stats['false_positives_filtered'] += (len(matches) - len(final_matches))
        
        return final_matches

    def _filter_line_matches(self, line_matches: List[DetectionMatch], content: str,
                           context: EnhancedAnalysisContext) -> List[DetectionMatch]:
        """Filter matches within a single line based on context."""
        if len(line_matches) <= 1:
            return line_matches
        
        # Sort by confidence descending
        line_matches.sort(key=lambda m: m.confidence, reverse=True)
        
        # Keep highest confidence match and any others that don't overlap significantly
        filtered = [line_matches[0]]
        
        for match in line_matches[1:]:
            # Check for overlap with existing matches
            overlapping = False
            for existing in filtered:
                if (abs(match.column_start - existing.column_start) < 10 and
                    match.pattern_name.split('_')[-1] == existing.pattern_name.split('_')[-1]):
                    overlapping = True
                    break
            
            if not overlapping:
                filtered.append(match)
        
        return filtered

    def _apply_suppression_rules_advanced(self, matches: List[DetectionMatch], content: str,
                                        line_num: int, context: EnhancedAnalysisContext) -> List[DetectionMatch]:
        """Apply advanced suppression rules with context awareness."""
        if not matches:
            return matches
        
        content_lines = content.split('\n')
        
        if line_num <= 0 or line_num > len(content_lines):
            return matches
        
        current_line = content_lines[line_num - 1]
        prev_line = content_lines[line_num - 2] if line_num > 1 else ""
        next_line = content_lines[line_num] if line_num < len(content_lines) else ""
        
        filtered_matches = []
        
        for match in matches:
            should_suppress = False
            suppression_reason = None
            
            # Check for inline suppression comments
            for pattern_name, pattern in self.suppression_patterns.items():
                # Only apply 'false_positive_markers' on comment/documentation lines
                if pattern_name == 'false_positive_markers':
                    comment_like = current_line.lstrip().startswith('#') or current_line.lstrip().startswith('//') or '/*' in current_line
                    if not comment_like and context.file_type not in (ContextType.DOCUMENTATION,):
                        continue
                if (pattern.search(current_line) or pattern.search(prev_line) or 
                    (pattern_name == 'block_comment' and pattern.search('\n'.join(content_lines[max(0, line_num-5):line_num+5])))):
                    should_suppress = True
                    suppression_reason = pattern_name
                    break
            
            # Advanced false positive detection
            if not should_suppress:
                false_positive_checks = [
                    self._is_example_data(match.matched_text, current_line, context),
                    self._is_test_fixture(match.matched_text, current_line, context),
                    self._is_documentation_example(match.matched_text, current_line, context),
                    self._is_configuration_template(match.matched_text, current_line, context),
                    self._is_known_false_positive(match.matched_text, match.pattern_name)
                ]
                
                if any(false_positive_checks):
                    should_suppress = True
                    suppression_reason = "false_positive_detection"
            
            # Context-aware suppression
            if not should_suppress and context.is_test_file:
                # Keep matches in tests unless confidence is extremely low
                if match.confidence < 0.2:
                    should_suppress = True
                    suppression_reason = "very_low_confidence_in_test"
            
            if not should_suppress:
                # Update metadata with suppression info
                if 'suppression_checked' not in match.metadata:
                    match.metadata['suppression_checked'] = True
                    match.metadata['suppression_reason'] = None
                
                filtered_matches.append(match)
            else:
                # Log suppression for analysis
                self.logger.debug(
                    f"Suppressed match '{match.matched_text}' in {match.pattern_name} "
                    f"due to {suppression_reason}"
                )
        
        return filtered_matches

    def _apply_dynamic_confidence_filtering(self, matches: List[DetectionMatch],
                                          context: EnhancedAnalysisContext) -> List[DetectionMatch]:
        """Apply dynamic confidence thresholds based on context and analysis mode."""
        if not matches:
            return matches
        
        # Calculate dynamic thresholds
        base_thresholds = {
            AnalysisMode.FAST: 0.8,
            AnalysisMode.BALANCED: 0.6,
            AnalysisMode.THOROUGH: 0.4,
            AnalysisMode.PARANOID: 0.3
        }
        
        base_threshold = base_thresholds[self.analysis_mode]
        
        # Adjust threshold based on context
        if context.is_test_file:
            # Slightly lower threshold in tests to avoid over-suppression
            base_threshold = max(0.2, base_threshold - 0.1)
        elif context.file_type == ContextType.DOCUMENTATION:
            base_threshold += 0.3  # Much higher threshold for docs
        elif context.file_type == ContextType.CONFIGURATION:
            base_threshold -= 0.1  # Lower threshold for config files
        
        # Pattern-specific threshold adjustments
        filtered_matches = []
        for match in matches:
            pattern_threshold = base_threshold
            
            # Critical patterns get lower thresholds
            if match.risk_level == RiskLevel.CRITICAL:
                pattern_threshold *= 0.7
            elif match.risk_level == RiskLevel.HIGH:
                pattern_threshold *= 0.85
            
            # Fallback/AST string-derived matches get a modest reduction
            det_level = match.metadata.get('detection_level') if isinstance(match.metadata, dict) else None
            if det_level in ('ast', 'fallback_regex', 'ast_string'):
                pattern_threshold *= 0.9
            
            # Sink detections get special treatment
            if 'sink' in match.pattern_name:
                pattern_threshold *= 0.9  # Slightly lower threshold for sinks
            
            # Advanced pattern detections
            if 'advanced' in match.pattern_name:
                pattern_threshold *= 1.1  # Higher threshold for advanced patterns
            
            if match.confidence >= min(0.95, max(0.1, pattern_threshold)):
                filtered_matches.append(match)
        
        return filtered_matches

    def _deduplicate_matches(self, matches: List[DetectionMatch]) -> List[DetectionMatch]:
        """Remove duplicate and overlapping matches intelligently."""
        if len(matches) <= 1:
            return matches
        
        # Sort matches by line number, then column, then confidence
        matches.sort(key=lambda m: (m.line_number, m.column_start, -m.confidence))
        
        deduplicated = []
        
        for current_match in matches:
            is_duplicate = False
            
            for existing_match in deduplicated:
                # Check for exact duplicates
                if (current_match.line_number == existing_match.line_number and
                    current_match.column_start == existing_match.column_start and
                    current_match.matched_text == existing_match.matched_text):
                    is_duplicate = True
                    break
                
                # Check for overlapping matches (keep the higher confidence one)
                if (current_match.line_number == existing_match.line_number and
                    self._matches_overlap(current_match, existing_match)):
                    
                    if current_match.confidence > existing_match.confidence:
                        # Replace existing with current
                        deduplicated.remove(existing_match)
                        break
                    else:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                deduplicated.append(current_match)
        
        return deduplicated

    def _matches_overlap(self, match1: DetectionMatch, match2: DetectionMatch) -> bool:
        """Check if two matches overlap significantly."""
        # Calculate overlap percentage
        start1, end1 = match1.column_start, match1.column_end
        start2, end2 = match2.column_start, match2.column_end
        
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        
        if overlap_end <= overlap_start:
            return False  # No overlap
        
        overlap_length = overlap_end - overlap_start
        min_length = min(end1 - start1, end2 - start2)
        
        # Consider overlapping if more than 50% of the smaller match overlaps
        return (overlap_length / min_length) > 0.5

    def _rank_and_select_matches(self, matches: List[DetectionMatch], 
                               context: EnhancedAnalysisContext) -> List[DetectionMatch]:
        """Rank matches and select the most relevant ones."""
        if not matches:
            return matches
        
        # Calculate composite scores for ranking
        for match in matches:
            score = self._calculate_composite_score(match, context)
            match.metadata['composite_score'] = score
        
        # Sort by composite score descending
        matches.sort(key=lambda m: m.metadata.get('composite_score', 0), reverse=True)
        
        # Apply limits based on analysis mode
        max_matches_per_file = {
            AnalysisMode.FAST: 10,
            AnalysisMode.BALANCED: 25,
            AnalysisMode.THOROUGH: 50,
            AnalysisMode.PARANOID: 100
        }
        
        limit = max_matches_per_file[self.analysis_mode]
        
        # Always include critical and high-risk matches
        critical_matches = [m for m in matches if m.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        other_matches = [m for m in matches if m.risk_level not in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        
        selected_matches = critical_matches[:limit]
        remaining_slots = limit - len(selected_matches)
        
        if remaining_slots > 0:
            selected_matches.extend(other_matches[:remaining_slots])
        
        return selected_matches

    def _calculate_composite_score(self, match: DetectionMatch, context: EnhancedAnalysisContext) -> float:
        """Calculate a composite score for ranking matches."""
        # Base score from confidence
        score = match.confidence
        
        # Risk level multiplier
        risk_multipliers = {
            RiskLevel.CRITICAL: 2.0,
            RiskLevel.HIGH: 1.5,
            RiskLevel.MEDIUM: 1.0,
            RiskLevel.LOW: 0.7
        }
        score *= risk_multipliers.get(match.risk_level, 1.0)
        
        # Pattern type bonuses
        if 'sink' in match.pattern_name:
            score *= 1.3  # Sink detections are important
        elif 'identifier' in match.pattern_name:
            score *= 0.8  # Identifiers are less certain
        elif any(critical in match.pattern_name for critical in ['aws', 'gcp', 'jwt', 'password']):
            score *= 1.4  # Critical patterns get bonus
        
        # Context penalties
        if context.is_test_file:
            score *= 0.3
        elif context.file_type == ContextType.DOCUMENTATION:
            score *= 0.2
        elif context.is_generated:
            score *= 0.1
        
        # Detection level bonuses
        detection_level = match.metadata.get('detection_level', '')
        if detection_level == 'ast_string':
            score *= 1.0  # Base score
        elif detection_level == 'ast_sink':
            score *= 1.2  # Sink analysis is valuable
        elif 'advanced' in detection_level:
            score *= 1.1  # Advanced analysis gets slight bonus
        elif 'fallback' in detection_level:
            score *= 0.7  # Fallback analysis is less reliable
        
        return score

    # Validation helper methods

    def _validate_luhn_algorithm(self, credit_card_number: str) -> float:
        """Validate credit card number using Luhn algorithm."""
        # Remove spaces and hyphens
        number = re.sub(r'[-\s]', '', credit_card_number)
        
        if not number.isdigit():
            return 0.5  # Invalid format
        
        # Luhn algorithm
        def luhn_check(number):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10 == 0
        
        if luhn_check(number):
            return 1.3  # Valid Luhn, high confidence
        else:
            # Check for common test credit card numbers
            test_numbers = {
                '4111111111111111', '5555555555554444', '4000000000000002',
                '3782822463100005', '6011111111111117'
            }
            if number in test_numbers:
                return 0.1  # Known test number
            return 0.6  # Invalid Luhn but matches pattern

    def _validate_email_format(self, email: str) -> float:
        """Enhanced email format validation."""
        # Basic format check
        if '@' not in email or email.count('@') != 1:
            return 0.3
        
        local, domain = email.split('@', 1)
        
        # Check for obvious test/example domains
        test_domains = {
            'example.com', 'test.com', 'example.org', 'test.org',
            'localhost', 'local', 'invalid'
        }
        
        if domain.lower() in test_domains:
            return 0.1
        
        # Check for valid TLD
        if '.' not in domain:
            return 0.4
        
        # Check for reasonable local part
        if len(local) < 1 or len(local) > 64:
            return 0.4
        
        # Check for valid characters (simplified)
        if re.match(r'^[a-zA-Z0-9._%+-]+$', local) and re.match(r'^[a-zA-Z0-9.-]+$', domain):
            return 1.2
        
        return 1.0

    def _validate_us_format(self, text: str, pattern_name: str) -> float:
        """Validate US-specific format patterns."""
        if pattern_name == 'ssn_us':
            # Remove formatting
            digits = re.sub(r'[-\s]', '', text)
            
            # Check for invalid SSN patterns
            invalid_patterns = [
                r'^000', r'^666', r'^9\d{2}',  # Invalid area numbers
                r'\d{3}00\d{4}',  # Invalid group numbers
                r'\d{5}0000'  # Invalid serial numbers
            ]
            
            for pattern in invalid_patterns:
                if re.match(pattern, digits):
                    return 0.2  # Likely invalid
            
            # Check for sequential or repeated digits (test data indicators)
            if digits in ['123456789', '111111111', '000000000']:
                return 0.1
            
            return 1.1  # Appears valid
        
        return 1.0  # No specific validation

    def _is_example_data(self, text: str, line_content: str, context: EnhancedAnalysisContext) -> bool:
        """Check if the text appears to be example data."""
        example_indicators = [
            'example', 'demo', 'sample', 'test', 'mock', 'fake', 'dummy',
            'placeholder', 'template', 'xxx', 'yyy', 'zzz'
        ]
        
        line_lower = line_content.lower()
        return any(indicator in line_lower for indicator in example_indicators)

    def _is_test_fixture(self, text: str, line_content: str, context: EnhancedAnalysisContext) -> bool:
        """Check if the text is part of test fixture data."""
        if not context.is_test_file:
            return False
        
        fixture_indicators = ['fixture', 'setUp', 'tearDown', 'before', 'after', 'mock']
        line_lower = line_content.lower()
        return any(indicator in line_lower for indicator in fixture_indicators)

    def _is_documentation_example(self, text: str, line_content: str, context: EnhancedAnalysisContext) -> bool:
        """Check if the text is part of documentation examples."""
        if context.file_type != ContextType.DOCUMENTATION:
            return False
        
        doc_indicators = ['"""', "'''", '/**', '<!--', '# Example', '## Example']
        return any(indicator in line_content for indicator in doc_indicators)

    def _is_configuration_template(self, text: str, line_content: str, context: EnhancedAnalysisContext) -> bool:
        """Check if the text is a configuration template placeholder."""
        template_patterns = [
            r'\{\{.*\}\}',  # Handlebars/Jinja2
            r'\$\{.*\}',    # Environment variables
            r'<.*>',        # XML-style placeholders
            r'%.*%'         # Batch-style variables
        ]
        
        return any(re.search(pattern, text) for pattern in template_patterns)

    def _is_known_false_positive(self, text: str, pattern_name: str) -> bool:
        """Check against known false positive patterns."""
        false_positive_map = {
            'credit_card': [
                '4111111111111111', '5555555555554444', '4000000000000000',
                '3782822463100005', '6011111111111117'
            ],
            'email': [
                'user@example.com', 'test@test.com', 'admin@localhost',
                'noreply@example.org'
            ],
            'ssn_us': [
                '123456789', '111111111', '000000000', '999999999'
            ]
        }
        
        known_fps = false_positive_map.get(pattern_name.split('_')[-1], [])
        return text in known_fps

    # Utility helper methods

    def _safe_extract_context(self, content: str, position: int, offset: int) -> str:
        """Safely extract context around a position."""
        try:
            start = max(0, position + offset) if offset < 0 else position
            end = min(len(content), position + offset) if offset > 0 else position
            
            if offset < 0:
                return content[start:position].strip()
            else:
                return content[position:end].strip()
        except (IndexError, TypeError):
            return ""

    def _get_absolute_position(self, content: str, item, relative_pos: int) -> int:
        """Get absolute position in content from line/column information."""
        try:
            lines = content.split('\n')
            if hasattr(item, 'start_line') and item.start_line <= len(lines):
                line_start = sum(len(line) + 1 for line in lines[:item.start_line - 1])
                return line_start + getattr(item, 'start_col', 0) + relative_pos
        except (AttributeError, IndexError):
            pass
        return 0

    def _extract_enhanced_function_context(self, content: str, start_pos: int) -> str:
        """Extract comprehensive function call context with proper parsing."""
        try:
            # Find the function call boundaries more accurately
            paren_pos = content.find('(', start_pos)
            if paren_pos == -1:
                return content[start_pos:start_pos + 200]
            
            # Find matching closing parenthesis with nested handling
            paren_count = 0
            quote_char = None
            escape_next = False
            pos = paren_pos
            
            while pos < len(content):
                char = content[pos]
                
                if escape_next:
                    escape_next = False
                elif char == '\\':
                    escape_next = True
                elif quote_char:
                    if char == quote_char:
                        quote_char = None
                elif char in ['"', "'"]:
                    quote_char = char
                elif char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        break
                
                pos += 1
                
                # Safety limit
                if pos - paren_pos > 1000:
                    break
            
            # Extract with some additional context
            context_start = max(0, start_pos - 50)
            context_end = min(len(content), pos + 50)
            
            return content[context_start:context_end].strip()
            
        except Exception:
            # Fallback to simple extraction
            return content[start_pos:start_pos + 200]

    def _analyze_naming_convention(self, identifier_name: str) -> str:
        """Analyze the naming convention used for an identifier."""
        if '_' in identifier_name and identifier_name.islower():
            return 'snake_case'
        elif re.match(r'^[a-z]+([A-Z][a-z]*)*$', identifier_name):
            return 'camelCase'
        elif re.match(r'^[A-Z]+([A-Z][a-z]*)*$', identifier_name):
            return 'PascalCase'
        elif identifier_name.isupper():
            return 'UPPER_CASE'
        elif '-' in identifier_name:
            return 'kebab-case'
        else:
            return 'mixed'

    def _update_pattern_metrics(self, pattern_name: str, confidence: float) -> None:
        """Update performance metrics for a pattern."""
        with self._stats_lock:
            if pattern_name not in self.pattern_metrics:
                self.pattern_metrics[pattern_name] = PatternMetrics()
            
            metrics = self.pattern_metrics[pattern_name]
            metrics.matches += 1
            metrics.confidence_sum += confidence

    def _calculate_fallback_confidence(self, compiled_pattern: CompiledPattern, 
                                     matched_text: str, context: EnhancedAnalysisContext) -> float:
        """Calculate confidence for fallback regex analysis."""
        base_confidence = compiled_pattern.confidence_base * 0.8  # Reduce for fallback
        
        # Apply context modifiers
        if context.is_test_file:
            # Only slight reduction for test files in fallback mode to keep detections
            base_confidence *= 0.8
        elif context.is_generated:
            base_confidence *= 0.1
        
        return min(1.0, max(0.0, base_confidence))

    def _validate_critical_match(self, matched_text: str, pattern_name: str) -> Dict[str, Any]:
        """Additional validation for critical pattern matches."""
        validation_result = {
            'is_valid': True,
            'validation_method': 'basic',
            'additional_checks': []
        }
        
        if pattern_name == 'credit_card':
            luhn_factor = self._validate_luhn_algorithm(matched_text)
            validation_result['luhn_valid'] = luhn_factor > 1.0
            validation_result['luhn_factor'] = luhn_factor
            validation_result['validation_method'] = 'luhn_algorithm'
            
        elif pattern_name.startswith('email'):
            email_factor = self._validate_email_format(matched_text)
            validation_result['format_valid'] = email_factor > 0.8
            validation_result['email_factor'] = email_factor
            validation_result['validation_method'] = 'email_format'
        
        elif pattern_name in ['aws_access_key', 'gcp_api_key']:
            # These patterns are highly specific, so basic match is validation
            validation_result['validation_method'] = 'pattern_specificity'
            validation_result['is_valid'] = True
        
        return validation_result

    # Public API methods for external integration

    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get comprehensive analysis statistics."""
        with self._stats_lock:
            stats = self.analysis_stats.copy()
        
        # Add pattern-specific metrics
        pattern_stats = {}
        for pattern_name, metrics in self.pattern_metrics.items():
            pattern_stats[pattern_name] = {
                'matches': metrics.matches,
                'average_confidence': metrics.average_confidence,
                'precision_estimate': metrics.precision_estimate
            }
        
        stats['pattern_metrics'] = pattern_stats
        stats['cache_size'] = len(self._content_hash_cache)
        stats['analysis_mode'] = self.analysis_mode.value
        
        return stats

    def clear_cache(self) -> None:
        """Clear analysis cache."""
        self._content_hash_cache.clear()
        with self._stats_lock:
            self.analysis_stats['cache_hits'] = 0
            self.analysis_stats['cache_misses'] = 0

    def update_configuration(self, new_config: Config) -> None:
        """Update analyzer configuration and recompile patterns if needed."""
        self.config = new_config
        self._initialize_patterns()  # Recompile with new config
        self.clear_cache()  # Clear cache to use new patterns

    def shutdown(self) -> None:
        """Gracefully shutdown the analyzer."""
        self._executor.shutdown(wait=True)
        self.logger.info("AST Analyzer shutdown complete")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
    
    def analyze_python_file(self, content: str, file_path: Path) -> List[DetectionMatch]:
        """Analyze Python file content for PII patterns.
        
        Args:
            content: Python source code content
            file_path: Path to the Python file
            
        Returns:
            List of detection matches found
        """
        return self.analyze_file(file_path, content, "python")
    
    def analyze_javascript_file(self, content: str, file_path: Path) -> List[DetectionMatch]:
        """Analyze JavaScript file content for PII patterns.
        
        Args:
            content: JavaScript source code content
            file_path: Path to the JavaScript file
            
        Returns:
            List of detection matches found
        """
        return self.analyze_file(file_path, content, "javascript")

    def scan_file(self, file_path: str) -> List[DetectionMatch]:
        """
        Unified interface for scanning a file - implements the standard scan_file method.
        
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
            
            # Detect language from file extension
            language = self._detect_language_from_extension(file_path_obj.suffix)
            
            # Use existing analyze_file method
            matches = self.analyze_file(file_path_obj, content, language)
            
            # Convert to unified DetectionMatch format
            unified_matches = self._convert_to_unified_matches(matches, file_path_obj, content, language)
            
            return unified_matches
            
        except Exception as e:
            self.logger.error(f"AST scan_file failed for {file_path}: {e}")
            return []
    
    def _detect_language_from_extension(self, extension: str) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust'
        }
        return extension_map.get(extension.lower(), 'unknown')
    
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
        """Convert AST matches to unified DetectionMatch format."""
        
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
                engine="ast",
                rule_id=match_dict.get('pattern_name', match_dict.get('rule_id', 'ast_detection')),
                severity=match_dict.get('severity', match_dict.get('risk_level', 'MEDIUM')),
                confidence=match_dict.get('confidence', match_dict.get('confidence_score', 0.8)),
                snippet=snippet,
                description=match_dict.get('description', 'AST-based detection'),
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


# Performance monitoring decorator
def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor method performance."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(self, *args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start_time
            if hasattr(self, 'logger'):
                self.logger.debug(f"{func.__name__} executed in {duration:.3f}s")
    return wrapper


# Exception classes for better error handling
class AnalysisTimeoutError(DetectionError):
    """Raised when analysis exceeds timeout."""
    pass


class ParserError(DetectionError):
    """Raised when AST parsing fails."""
    pass