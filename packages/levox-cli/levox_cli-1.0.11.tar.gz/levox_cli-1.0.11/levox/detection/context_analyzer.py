"""
Context-aware analyzer for PII detection with advanced variable context analysis.

This module provides sophisticated context analysis capabilities for Stage 2 of the Levox
detection pipeline, determining whether detected PII represents legitimate usage patterns
(test data, sanitized values, protected scopes) to reduce false positives.
"""

import re
import logging
import hashlib
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache

from ..core.config import Config, RiskLevel
from ..core.exceptions import DetectionError
from ..parsers.base import StringLiteral, Identifier, ContextType, RiskContext
from ..models.detection_result import DetectionMatch


class ContextCategory(Enum):
    """Primary context classifications for detected PII."""
    TEST_DATA = auto()
    SANITIZED = auto()
    ENCRYPTED = auto()
    LOGGED_DEBUG = auto()
    PRODUCTION = auto()
    UNKNOWN = auto()


class ContextConfidence(Enum):
    """Context confidence levels."""
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4
    NONE = 0.0


@dataclass
class ContextEvidence:
    """Evidence supporting a context classification."""
    category: ContextCategory
    confidence: float
    indicators: List[str] = field(default_factory=list)
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextAnalysisResult:
    """Comprehensive context analysis result for integration with detection pipeline."""
    primary_context: ContextCategory
    confidence_score: float
    legitimate_usage: bool
    evidence: List[ContextEvidence] = field(default_factory=list)
    suppression_markers: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DetectionMatch integration."""
        return {
            'context_type': self.primary_context.name,
            'confidence': self.confidence_score,
            'legitimate_usage': self.legitimate_usage,
            'evidence': [
                {
                    'category': e.category.name,
                    'confidence': e.confidence,
                    'indicators': e.indicators,
                    'source': e.source
                } for e in self.evidence
            ],
            'suppression_markers': self.suppression_markers,
            'risk_factors': self.risk_factors
        }


class PatternLibrary:
    """Centralized pattern library for context analysis."""
    
    def __init__(self):
        """Initialize compiled pattern library."""
        # Test data patterns
        self.test_patterns = self._compile_patterns({
            'variable_names': [
                r'\b(?:test|mock|fake|dummy|stub|example|sample|demo|placeholder|template|fixture)_\w+',
                r'\w+_(?:test|mock|fake|dummy|stub|example|sample|demo|placeholder|template|fixture)\b',
                r'\b(?:lorem|ipsum|placeholder|template|fixture|config|setting|option|param)\w*\b'
            ],
            'synthetic_data': [
                r'\b(?:test@example\.com|admin@localhost|user@test\.com|demo@test\.com)\b',
                r'\b(?:123-?45-?6789|000-?00-?0000|111-?11-?1111|999-?99-?9999)\b',
                r'\b(?:john\.?doe|jane\.?smith|test\.?user|demo\.?user|example\.?user)\b',
                r'\b4[0-9]{12}(?:[0-9]{3})?\b',  # Test credit cards
                r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',  # UUIDs
                r'\b(?:localhost|127\.0\.0\.1|0\.0\.0\.0|::1)\b',  # Local addresses
                r'\b(?:dummy|test|example|sample|placeholder|config_value_here)\b',
                r'\b(?:your_api_key_here|your_secret_here|your_password_here)\b'
            ],
            'file_indicators': [
                r'(?:test|spec|mock|fixture|example|sample)_\w+\.py$',
                r'\w+_(?:test|spec|mock|fixture|example|sample)\.py$',
                r'/tests?/',
                r'/__tests__/',
                r'/spec/',
                r'/fixtures?/',
                r'/examples?/',
                r'/samples?/'
            ]
        })
        
        # Sanitization patterns
        self.sanitization_patterns = self._compile_patterns({
            'function_names': [
                r'\b(?:escape|quote|sanitize|clean|validate|normalize)\w*\b',
                r'\b(?:mask|anonymize|pseudonymize|obfuscate|redact)\w*\b',
                r'\b(?:encrypt|hash|digest|encode|sign)\w*\b'
            ],
            'method_calls': [
                r'\.(?:escape|quote|sanitize|clean|validate)\s*\(',
                r'\.(?:mask|anonymize|hash|encrypt)\s*\(',
                r'\.(?:replace|sub|filter|strip)\s*\([^)]*(?:sensitive|pii|private)'
            ]
        })
        
        # Comment analysis patterns
        self.comment_patterns = self._compile_patterns({
            'suppression': [
                r'(?:levox|pii|security):\s*(?:ignore|suppress|skip|disable)',
                r'(?:TODO|FIXME|NOTE):\s*(?:remove|fix|sanitize)\s+(?:pii|sensitive)',
                r'(?:safe|ok|approved):\s*(?:contains|has)\s+(?:test|fake|mock)\s+data'
            ],
            'context_hints': [
                r'(?:test|mock|fake|dummy|example)\s+(?:data|values?|content)',
                r'(?:for\s+(?:testing|development|staging)\s+only)',
                r'(?:encrypted|hashed|masked|sanitized)\s+(?:before|value|data)'
            ]
        })
        
        # Security library patterns by language
        self.security_libraries = {
            'python': [
                r'\b(?:cryptography|pycryptodome|hashlib|bcrypt|passlib)\b',
                r'\b(?:bleach|markupsafe|html|secrets)\b',
                r'\bfrom\s+(?:cryptography|hashlib|secrets)\b'
            ],
            'javascript': [
                r'\b(?:crypto-js|bcrypt|argon2|node-crypto)\b',
                r'\b(?:dompurify|xss|sanitize-html)\b',
                r'\brequire\s*\(\s*["\'](?:crypto|bcrypt)["\']'
            ],
            'java': [
                r'\bimport\s+(?:javax\.crypto|java\.security)\b',
                r'\bimport\s+(?:org\.springframework\.security)\b',
                r'\bimport\s+(?:org\.owasp\.esapi)\b'
            ]
        }
    
    def _compile_patterns(self, pattern_dict: Dict[str, List[str]]) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns with error handling."""
        compiled = {}
        for category, patterns in pattern_dict.items():
            compiled[category] = []
            for pattern in patterns:
                try:
                    compiled[category].append(re.compile(pattern, re.IGNORECASE | re.MULTILINE))
                except re.error as e:
                    logging.getLogger(__name__).warning(f"Invalid regex pattern '{pattern}': {e}")
        return compiled
    
    def match_patterns(self, text: str, category: str, subcategory: str = None) -> List[Tuple[str, re.Match]]:
        """Match text against pattern categories."""
        if not text:
            return []
        
        matches = []
        patterns = self.test_patterns if category == 'test' else \
                  self.sanitization_patterns if category == 'sanitization' else \
                  self.comment_patterns if category == 'comment' else {}
        
        if subcategory and subcategory in patterns:
            for pattern in patterns[subcategory]:
                for match in pattern.finditer(text):
                    matches.append((pattern.pattern, match))
        elif not subcategory:
            for subcat, pattern_list in patterns.items():
                for pattern in pattern_list:
                    for match in pattern.finditer(text):
                        matches.append((pattern.pattern, match))
        
        return matches
    
    def is_safe_literal(self, text: str, config: 'Config') -> bool:
        """Check if a literal is considered safe/placeholder."""
        if not text or not config.enable_safe_literal_detection:
            return False
        
        text_lower = text.lower().strip()
        
        # Check against configured safe literals
        for safe_literal in config.safe_literals:
            if safe_literal.lower() in text_lower:
                return True
        
        # Check for common placeholder patterns
        placeholder_patterns = [
            r'^[0-9]+$',  # Just numbers
            r'^[a-z]+$',  # Just lowercase letters
            r'^[A-Z]+$',  # Just uppercase letters
            r'^[a-zA-Z]+$',  # Just letters
            r'^[0-9a-fA-F]+$',  # Hex strings
            r'^[0-9a-zA-Z]+$',  # Alphanumeric
            r'^[a-zA-Z_][a-zA-Z0-9_]*$',  # Valid identifier
        ]
        
        for pattern in placeholder_patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def is_safe_variable_name(self, var_name: str, config: 'Config') -> bool:
        """Check if a variable name follows safe patterns."""
        if not var_name or not config.enable_variable_heuristics:
            return False
        
        var_lower = var_name.lower()
        
        # Check against configured safe patterns
        for pattern in config.safe_variable_patterns:
            if self._matches_pattern(var_lower, pattern):
                return True
        
        # Additional safe patterns
        safe_patterns = [
            r'^[a-z_][a-z0-9_]*$',  # Valid Python identifier
            r'^[a-z][a-z0-9]*$',    # camelCase
            r'^[a-z_][a-z0-9_]*$',  # snake_case
            r'^[A-Z][a-z0-9]*$',    # PascalCase
        ]
        
        for pattern in safe_patterns:
            if re.match(pattern, var_name):
                return True
        
        return False
    
    def is_framework_safe_pattern(self, text: str, file_path: str, config: 'Config') -> bool:
        """
        Check if detected text matches framework-safe patterns that should be excluded.
        
        Args:
            text: The detected text
            file_path: Path to the file being analyzed
            config: Configuration object with framework patterns
            
        Returns:
            True if the pattern is framework-safe and should be excluded
        """
        if not hasattr(config, 'framework_safe_patterns'):
            return False
        
        text_lower = text.lower()
        file_path_lower = file_path.lower()
        
        # Check Django patterns
        django_patterns = config.framework_safe_patterns.get('django', [])
        for pattern in django_patterns:
            if pattern.lower() in text_lower:
                return True
        
        # Check SQLAlchemy patterns
        sqlalchemy_patterns = config.framework_safe_patterns.get('sqlalchemy', [])
        for pattern in sqlalchemy_patterns:
            if pattern.lower() in text_lower:
                return True
        
        # Check logging patterns
        logging_patterns = config.framework_safe_patterns.get('logging', [])
        for pattern in logging_patterns:
            if pattern.lower() in text_lower:
                return True
        
        # Check ORM generic patterns
        orm_patterns = config.framework_safe_patterns.get('orm_generic', [])
        for pattern in orm_patterns:
            if pattern.lower() in text_lower:
                return True
        
        # Check framework metadata patterns
        metadata_patterns = config.framework_safe_patterns.get('framework_metadata', [])
        for pattern in metadata_patterns:
            if pattern.lower() in text_lower:
                return True
        
        return False
    
    def detect_framework_context(self, file_path: str, file_content: str) -> Dict[str, Any]:
        """
        Detect the framework context of a file to adjust analysis accordingly.
        
        Args:
            file_path: Path to the file
            file_content: Content of the file
            
        Returns:
            Dictionary with framework detection results
        """
        framework_context = {
            'framework': 'unknown',
            'confidence': 0.0,
            'indicators': [],
            'is_test_file': False,
            'is_migration_file': False,
            'is_fixture_file': False,
            'is_framework_code': False
        }
        
        file_path_lower = file_path.lower()
        content_lower = file_content.lower()
        
        # Detect Django
        django_indicators = [
            'django.db.models', 'django.contrib', 'django.shortcuts',
            'django.http', 'django.urls', 'django.views', 'django.conf',
            'from django import', 'import django', 'django.db',
            'models.Model', 'models.CharField', 'models.IntegerField',
            'QuerySet', 'objects.create', 'objects.get', 'objects.filter'
        ]
        
        django_score = 0
        for indicator in django_indicators:
            if indicator in content_lower:
                django_score += 1
                framework_context['indicators'].append(indicator)
        
        if django_score >= 3:
            framework_context['framework'] = 'django'
            framework_context['confidence'] = min(0.9, django_score * 0.2)
            framework_context['is_framework_code'] = True
        
        # Detect SQLAlchemy
        sqlalchemy_indicators = [
            'from sqlalchemy import', 'import sqlalchemy', 'sqlalchemy.orm',
            'session.add', 'session.commit', 'session.query', 'session.execute',
            'Base.metadata', 'declarative_base', 'Column(', 'relationship('
        ]
        
        sqlalchemy_score = 0
        for indicator in sqlalchemy_indicators:
            if indicator in content_lower:
                sqlalchemy_score += 1
                framework_context['indicators'].append(indicator)
        
        if sqlalchemy_score >= 2:
            framework_context['framework'] = 'sqlalchemy'
            framework_context['confidence'] = min(0.9, sqlalchemy_score * 0.3)
            framework_context['is_framework_code'] = True
        
        # Detect test files
        test_indicators = [
            'import unittest', 'import pytest', 'from unittest import',
            'class Test', 'def test_', 'def test', 'assert ', 'self.assertEqual',
            'mock', 'patch', 'fixture', 'setup', 'teardown'
        ]
        
        test_score = 0
        for indicator in test_indicators:
            if indicator in content_lower:
                test_score += 1
                framework_context['indicators'].append(indicator)
        
        if test_score >= 2 or 'test' in file_path_lower:
            framework_context['is_test_file'] = True
            framework_context['confidence'] = max(framework_context['confidence'], 0.8)
        
        # Detect migration files
        migration_indicators = [
            'migrations/', 'migration', 'alembic', 'version', 'upgrade', 'downgrade',
            'op.create_table', 'op.drop_table', 'op.add_column', 'op.drop_column'
        ]
        
        migration_score = 0
        for indicator in migration_indicators:
            if indicator in file_path_lower or indicator in content_lower:
                migration_score += 1
                framework_context['indicators'].append(indicator)
        
        if migration_score >= 1:
            framework_context['is_migration_file'] = True
            framework_context['confidence'] = max(framework_context['confidence'], 0.9)
        
        # Detect fixture files
        fixture_indicators = [
            'fixture', 'factory', 'mock', 'dummy', 'example', 'sample',
            'test_data', 'seed_data', 'initial_data'
        ]
        
        fixture_score = 0
        for indicator in fixture_indicators:
            if indicator in file_path_lower or indicator in content_lower:
                fixture_score += 1
                framework_context['indicators'].append(indicator)
        
        if fixture_score >= 2:
            framework_context['is_fixture_file'] = True
            framework_context['confidence'] = max(framework_context['confidence'], 0.7)
        
        return framework_context
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches a wildcard pattern."""
        if '*' not in pattern:
            return text == pattern
        
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace('*', '.*')
        return bool(re.match(regex_pattern, text))


class ContextAnalyzer:
    """
    Production-grade context analyzer for Stage 2 of Levox PII detection pipeline.
    
    Analyzes detected PII instances to determine legitimate usage patterns,
    reducing false positives through sophisticated context analysis.
    """
    
    def __init__(self, config: Config):
        """
        Initialize context analyzer with configuration.
        
        Args:
            config: Levox configuration object
            
        Raises:
            DetectionError: If configuration is invalid
        """
        if not config:
            raise DetectionError("Context analyzer requires valid configuration")
        
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")
        self.patterns = PatternLibrary()
        
        # Analysis thresholds from config
        self.confidence_threshold = getattr(config, 'context_confidence_threshold', 0.6)
        self.test_data_threshold = getattr(config, 'test_data_confidence', 0.7)
        self.sanitization_threshold = getattr(config, 'sanitization_confidence', 0.8)
        
        self.logger.info("Context analyzer initialized with thresholds: "
                        f"confidence={self.confidence_threshold}, "
                        f"test_data={self.test_data_threshold}, "
                        f"sanitization={self.sanitization_threshold}")
    
    def analyze(self, ast_node: Any, file_context: Union[Dict[str, Any], Any]) -> ContextAnalysisResult:
        """
        Primary analysis method for integration with detection pipeline.
        
        Args:
            ast_node: AST node containing detected PII
            file_context: File-level context (path, language, scope info) or DetectionMatch object
            
        Returns:
            ContextAnalysisResult for integration with DetectionMatch
            
        Raises:
            DetectionError: If analysis fails critically
        """
        try:
            evidence = []
            suppression_markers = []
            risk_factors = []
            
            # Handle both dictionary and DetectionMatch objects
            if hasattr(file_context, 'get') and callable(getattr(file_context, 'get')):
                # Dictionary-like object
                file_path = file_context.get('file_path', '')
                language = file_context.get('language', 'unknown')
                content = file_context.get('content', '')
            else:
                # DetectionMatch or other object - extract what we can
                file_path = getattr(file_context, 'file_path', '')
                language = getattr(file_context, 'language', 'unknown')
                content = getattr(file_context, 'content', '')
            
            # Extract node info
            node_info = self._extract_node_info(ast_node)
            
            # Run context analysis stages
            test_evidence = self._analyze_test_context(node_info, file_path, content)
            if test_evidence:
                evidence.append(test_evidence)
            
            # Handle scope_info extraction safely
            scope_info = {}
            if hasattr(file_context, 'get') and callable(getattr(file_context, 'get')):
                scope_info = file_context.get('scope_info', {})
            else:
                scope_info = getattr(file_context, 'scope_info', {})
            
            sanitization_evidence = self._analyze_sanitization_context(
                node_info, scope_info, content, language
            )
            if sanitization_evidence:
                evidence.append(sanitization_evidence)
            
            comment_evidence = self._analyze_comment_context(
                content, node_info.get('line_number', 0)
            )
            if comment_evidence:
                evidence.append(comment_evidence)
                if comment_evidence.category == ContextCategory.TEST_DATA:
                    suppression_markers.extend(comment_evidence.indicators)
            
            import_evidence = self._analyze_security_imports(content, language)
            if import_evidence:
                evidence.append(import_evidence)
            
            # Production risk analysis
            production_risks = self._identify_production_risks(node_info, file_context)
            if production_risks:
                risk_factors.extend(production_risks)
            
            # Safe literal and variable analysis
            safe_evidence = self._analyze_safe_context(node_info, file_context)
            if safe_evidence:
                evidence.append(safe_evidence)
                if safe_evidence.category == ContextCategory.TEST_DATA:
                    suppression_markers.extend(safe_evidence.indicators)
            
            # Determine primary context and confidence
            primary_context, confidence = self._classify_primary_context(evidence)
            legitimate_usage = self._determine_legitimate_usage(primary_context, confidence, evidence)
            
            return ContextAnalysisResult(
                primary_context=primary_context,
                confidence_score=confidence,
                legitimate_usage=legitimate_usage,
                evidence=evidence,
                suppression_markers=suppression_markers,
                risk_factors=risk_factors
            )
            
        except Exception as e:
            # Safe file path extraction for error logging
            try:
                if hasattr(file_context, 'get') and callable(getattr(file_context, 'get')):
                    file_path_for_log = file_context.get('file_path', 'unknown')
                else:
                    file_path_for_log = getattr(file_context, 'file_path', 'unknown')
            except:
                file_path_for_log = 'unknown'
            
            self.logger.error(f"Context analysis failed for {file_path_for_log}: {e}")
            # Return safe fallback instead of crashing
            return ContextAnalysisResult(
                primary_context=ContextCategory.UNKNOWN,
                confidence_score=0.0,
                legitimate_usage=False,
                risk_factors=[f"Analysis failed: {str(e)}"]
            )
    
    def scan_file(self, file_path: str) -> List[DetectionMatch]:
        """
        Unified interface for scanning a file - implements the standard scan_file method.
        
        Note: Context analyzer is typically used as a post-processor for existing matches,
        but this method provides a unified interface for consistency.
        
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
            
            # For context analyzer, we typically don't do initial detection
            # Instead, we return an empty list as this is a post-processing step
            # The main detection engines (regex, AST, dataflow) should be called first
            
            self.logger.debug(f"Context analyzer scan_file called for {file_path} - returning empty list (post-processor)")
            return []
            
        except Exception as e:
            self.logger.error(f"Context analyzer scan_file failed for {file_path}: {e}")
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
        """Convert context analyzer matches to unified DetectionMatch format."""
        
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
                engine="context",
                rule_id=match_dict.get('pattern_name', match_dict.get('rule_id', 'context_analyzed')),
                severity=match_dict.get('severity', match_dict.get('risk_level', 'MEDIUM')),
                confidence=match_dict.get('confidence', match_dict.get('confidence_score', 0.8)),
                snippet=snippet,
                description=match_dict.get('description', 'Context-analyzed detection'),
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
    
    def _extract_node_info(self, node: Any) -> Dict[str, Any]:
        """Extract relevant information from AST node."""
        info = {
            'type': type(node).__name__,
            'value': None,
            'name': None,
            'line_number': getattr(node, 'lineno', 0),
            'col_offset': getattr(node, 'col_offset', 0)
        }
        
        # Extract value based on node type
        if hasattr(node, 'value'):
            info['value'] = str(node.value)
        elif hasattr(node, 's'):  # String literal
            info['value'] = str(node.s)
        elif hasattr(node, 'id'):  # Identifier
            info['name'] = str(node.id)
        elif hasattr(node, 'arg'):  # Function argument
            info['name'] = str(node.arg)
        
        return info
    
    def _analyze_test_context(self, node_info: Dict[str, Any], 
                            file_path: str, content: str) -> Optional[ContextEvidence]:
        """Analyze if PII appears in test context."""
        indicators = []
        confidence = 0.0
        
        # File path analysis
        file_matches = self.patterns.match_patterns(file_path, 'test', 'file_indicators')
        if file_matches:
            indicators.extend([f"test_file:{match[0]}" for match in file_matches])
            confidence += 0.4
        
        # Variable name analysis
        var_name = node_info.get('name', '')
        if var_name:
            name_matches = self.patterns.match_patterns(var_name, 'test', 'variable_names')
            if name_matches:
                indicators.extend([f"test_var:{match[0]}" for match in name_matches])
                confidence += 0.3
        
        # Value analysis for synthetic data
        value = node_info.get('value', '')
        if value:
            synthetic_matches = self.patterns.match_patterns(value, 'test', 'synthetic_data')
            if synthetic_matches:
                indicators.extend([f"synthetic_data:{match[0]}" for match in synthetic_matches])
                confidence += 0.5
            
            # Additional heuristics for test data
            if self._is_sequential_or_repeated(value):
                indicators.append("sequential_pattern")
                confidence += 0.2
        
        if confidence > 0.2:
            return ContextEvidence(
                category=ContextCategory.TEST_DATA,
                confidence=min(confidence, 1.0),
                indicators=indicators,
                source="test_context_analysis"
            )
        
        return None
    
    def _analyze_sanitization_context(self, node_info: Dict[str, Any], 
                                    scope_info: Dict[str, Any], 
                                    content: str, language: str) -> Optional[ContextEvidence]:
        """Analyze if PII is in sanitization context."""
        indicators = []
        confidence = 0.0
        
        # Function context analysis
        current_function = scope_info.get('current_function', '')
        if current_function:
            func_matches = self.patterns.match_patterns(current_function, 'sanitization', 'function_names')
            if func_matches:
                indicators.extend([f"sanitization_func:{match[0]}" for match in func_matches])
                confidence += 0.4
        
        # Method call analysis in surrounding context
        line_num = node_info.get('line_number', 0)
        context_window = self._extract_context_window(content, line_num, window_size=3)
        
        method_matches = self.patterns.match_patterns(context_window, 'sanitization', 'method_calls')
        if method_matches:
            indicators.extend([f"sanitization_call:{match[0]}" for match in method_matches])
            confidence += 0.3
        
        # Security library imports
        if language in self.patterns.security_libraries:
            for pattern in self.patterns.security_libraries[language]:
                if re.search(pattern, content, re.IGNORECASE):
                    indicators.append(f"security_import:{pattern}")
                    confidence += 0.2
                    break
        
        if confidence > 0.3:
            return ContextEvidence(
                category=ContextCategory.SANITIZED,
                confidence=min(confidence, 1.0),
                indicators=indicators,
                source="sanitization_analysis",
                metadata={'function_context': current_function}
            )
        
        return None
    
    def _analyze_comment_context(self, content: str, line_number: int) -> Optional[ContextEvidence]:
        """Analyze comments around PII location."""
        if line_number <= 0:
            return None
        
        # Extract comment context window
        lines = content.split('\n')
        start_line = max(0, line_number - 3)
        end_line = min(len(lines), line_number + 2)
        context_lines = lines[start_line:end_line]
        context_text = '\n'.join(context_lines)
        
        indicators = []
        confidence = 0.0
        category = ContextCategory.UNKNOWN
        
        # Check for suppression markers
        suppression_matches = self.patterns.match_patterns(context_text, 'comment', 'suppression')
        if suppression_matches:
            indicators.extend([f"suppression:{match[0]}" for match in suppression_matches])
            confidence += 0.6
            category = ContextCategory.TEST_DATA
        
        # Check for context hints
        hint_matches = self.patterns.match_patterns(context_text, 'comment', 'context_hints')
        if hint_matches:
            indicators.extend([f"context_hint:{match[0]}" for match in hint_matches])
            confidence += 0.3
            if 'test' in ' '.join(indicators) or 'mock' in ' '.join(indicators):
                category = ContextCategory.TEST_DATA
        
        if confidence > 0.2:
            return ContextEvidence(
                category=category,
                confidence=min(confidence, 1.0),
                indicators=indicators,
                source="comment_analysis",
                metadata={'context_lines': context_lines}
            )
        
        return None
    
    def _analyze_security_imports(self, content: str, language: str) -> Optional[ContextEvidence]:
        """Analyze security-related imports."""
        if language not in self.patterns.security_libraries:
            return None
        
        indicators = []
        confidence = 0.0
        
        for pattern_str in self.patterns.security_libraries[language]:
            pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
            matches = pattern.finditer(content)
            for match in matches:
                indicators.append(f"security_import:{match.group()}")
                confidence += 0.2
        
        if confidence > 0.1:
            return ContextEvidence(
                category=ContextCategory.ENCRYPTED,
                confidence=min(confidence, 1.0),
                indicators=indicators,
                source="import_analysis"
            )
        
        return None
    
    def _analyze_safe_context(self, node_info: Dict[str, Any], 
                             file_context: Dict[str, Any]) -> Optional[ContextEvidence]:
        """Analyze if PII is in safe/placeholder context."""
        indicators = []
        confidence = 0.0
        
        # Check if the value is a safe literal
        value = node_info.get('value', '')
        if value and self.patterns.is_safe_literal(value, self.config):
            indicators.append(f"safe_literal:{value}")
            confidence += 0.8
        
        # Check if the variable name follows safe patterns
        var_name = node_info.get('name', '')
        if var_name and self.patterns.is_safe_variable_name(var_name, self.config):
            indicators.append(f"safe_variable:{var_name}")
            confidence += 0.6
        
        # Check for framework-safe patterns
        file_path = file_context.get('file_path', '')
        if value and file_path and self.patterns.is_framework_safe_pattern(value, file_path, self.config):
            indicators.append(f"framework_safe:{value}")
            confidence += 0.9
        
        # Detect framework context and adjust confidence
        content = file_context.get('content', '')
        if file_path and content:
            framework_context = self.patterns.detect_framework_context(file_path, content)
            
            # Reduce confidence for test files
            if framework_context.get('is_test_file', False):
                indicators.append("test_file_context")
                confidence += 0.7
            
            # Reduce confidence for migration files
            if framework_context.get('is_migration_file', False):
                indicators.append("migration_file_context")
                confidence += 0.8
            
            # Reduce confidence for fixture files
            if framework_context.get('is_fixture_file', False):
                indicators.append("fixture_file_context")
                confidence += 0.7
            
            # Reduce confidence for framework code
            if framework_context.get('is_framework_code', False):
                indicators.append("framework_code_context")
                confidence += 0.6
        
        # Check for suppression comments
        line_num = node_info.get('line_number', 0)
        if line_num > 0:
            comment_context = self._extract_context_window(content, line_num, window_size=2)
            
            # Look for levox-ignore comments
            if re.search(r'#\s*levox-ignore', comment_context, re.IGNORECASE):
                indicators.append("levox_ignore_comment")
                confidence += 0.9
            
            # Look for other suppression patterns
            suppression_patterns = [
                r'#\s*(?:pii|security):\s*(?:ignore|suppress|skip|disable)',
                r'#\s*(?:TODO|FIXME|NOTE):\s*(?:remove|fix|sanitize)\s+(?:pii|sensitive)',
                r'#\s*(?:safe|ok|approved):\s*(?:contains|has)\s+(?:test|fake|mock)\s+data'
            ]
            
            for pattern in suppression_patterns:
                if re.search(pattern, comment_context, re.IGNORECASE):
                    indicators.append("suppression_comment")
                    confidence += 0.7
                    break
        
        if confidence > 0.5:
            return ContextEvidence(
                category=ContextCategory.TEST_DATA,
                confidence=min(confidence, 1.0),
                indicators=indicators,
                source="safe_context_analysis",
                metadata={
                    'framework_context': framework_context if 'framework_context' in locals() else {},
                    'file_path': file_path
                }
            )
        
        return None
    
    def _identify_production_risks(self, node_info: Dict[str, Any], 
                                 file_context: Dict[str, Any]) -> List[str]:
        """Identify potential production risks."""
        risks = []
        
        # Check for production-like file paths
        file_path = file_context.get('file_path', '')
        if any(path_part in file_path.lower() for path_part in ['prod', 'production', 'live', 'main']):
            risks.append("production_file_path")
        
        # Check for logging context
        scope_info = file_context.get('scope_info', {})
        if 'log' in scope_info.get('current_function', '').lower():
            risks.append("logging_context")
        
        # Check for database/API contexts
        content = file_context.get('content', '')
        if re.search(r'\b(?:database|db|api|endpoint|request|response)\b', content, re.IGNORECASE):
            risks.append("data_processing_context")
        
        return risks
    
    def _classify_primary_context(self, evidence: List[ContextEvidence]) -> Tuple[ContextCategory, float]:
        """Classify the primary context based on accumulated evidence."""
        if not evidence:
            return ContextCategory.UNKNOWN, 0.0
        
        # Weight evidence by confidence and category priority
        category_scores = {}
        for ev in evidence:
            current_score = category_scores.get(ev.category, 0.0)
            category_scores[ev.category] = max(current_score, ev.confidence)
        
        # Find highest confidence category
        if category_scores:
            primary = max(category_scores.items(), key=lambda x: x[1])
            return primary[0], primary[1]
        
        return ContextCategory.UNKNOWN, 0.0
    
    def _determine_legitimate_usage(self, primary_context: ContextCategory, 
                                  confidence: float, 
                                  evidence: List[ContextEvidence]) -> bool:
        """Determine if detected PII represents legitimate usage."""
        # High confidence test data or sanitized contexts are legitimate
        if primary_context == ContextCategory.TEST_DATA and confidence >= self.test_data_threshold:
            return True
        
        if primary_context == ContextCategory.SANITIZED and confidence >= self.sanitization_threshold:
            return True
        
        if primary_context == ContextCategory.ENCRYPTED and confidence >= 0.7:
            return True
        
        # Check for explicit suppression markers
        for ev in evidence:
            if any('suppression' in ind for ind in ev.indicators):
                return True
        
        return False
    
    @lru_cache(maxsize=256)
    def _is_sequential_or_repeated(self, value: str) -> bool:
        """Check if value contains sequential or repeated patterns (cached)."""
        if len(value) < 3:
            return False
        
        # Sequential digits
        if value.isdigit() and len(value) >= 3:
            sequential = all(int(value[i]) == int(value[i-1]) + 1 for i in range(1, len(value)))
            if sequential:
                return True
        
        # Repeated characters (>70% same character)
        for char in set(value):
            if value.count(char) > len(value) * 0.7:
                return True
        
        return False
    
    def _extract_context_window(self, content: str, line_number: int, window_size: int = 3) -> str:
        """Extract context window around specified line number."""
        if line_number <= 0:
            return ""
        
        lines = content.split('\n')
        start = max(0, line_number - window_size - 1)
        end = min(len(lines), line_number + window_size)
        
        return '\n'.join(lines[start:end])
    
    def validate_configuration(self) -> List[str]:
        """Validate analyzer configuration and return any issues."""
        issues = []
        
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            issues.append("confidence_threshold must be between 0.0 and 1.0")
        
        if self.test_data_threshold < 0.0 or self.test_data_threshold > 1.0:
            issues.append("test_data_threshold must be between 0.0 and 1.0")
        
        if self.sanitization_threshold < 0.0 or self.sanitization_threshold > 1.0:
            issues.append("sanitization_threshold must be between 0.0 and 1.0")
        
        return issues
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics for monitoring/debugging."""
        return {
            'pattern_categories': len(self.patterns.test_patterns) + 
                                len(self.patterns.sanitization_patterns) + 
                                len(self.patterns.comment_patterns),
            'supported_languages': list(self.patterns.security_libraries.keys()),
            'configuration': {
                'confidence_threshold': self.confidence_threshold,
                'test_data_threshold': self.test_data_threshold,
                'sanitization_threshold': self.sanitization_threshold
            }
        }
    
    def calculate_context_confidence(self, context_info: Dict[str, Any]) -> float:
        """Calculate confidence score based on context analysis."""
        if not context_info:
            return 0.0
        
        # Extract context components
        context_type = context_info.get('context_type', 'UNKNOWN')
        evidence = context_info.get('evidence', [])
        suppression_markers = context_info.get('suppression_markers', [])
        risk_factors = context_info.get('risk_factors', [])
        
        # Base confidence from context type
        base_confidence = {
            'TEST_DATA': 0.8,
            'SANITIZED': 0.7,
            'ENCRYPTED': 0.9,
            'LOGGED_DEBUG': 0.6,
            'PRODUCTION': 0.3,
            'UNKNOWN': 0.5
        }.get(context_type, 0.5)
        
        # Adjust based on evidence strength
        evidence_boost = min(0.2, len(evidence) * 0.05)
        
        # Adjust based on suppression markers
        suppression_boost = min(0.1, len(suppression_markers) * 0.02)
        
        # Adjust based on risk factors
        risk_penalty = min(0.3, len(risk_factors) * 0.1)
        
        # Calculate final confidence
        confidence = base_confidence + evidence_boost + suppression_boost - risk_penalty
        
        # Ensure confidence is within valid range
        return max(0.0, min(1.0, confidence))
    
    def is_legitimate_usage(self, context_info: Dict[str, Any], *args) -> bool:
        """Check if detected PII represents legitimate usage."""
        if not context_info:
            return False
        
        # Extract context type and confidence
        context_type = context_info.get('context_type', 'UNKNOWN')
        confidence = context_info.get('confidence', 0.0)
        
        # High confidence test data or sanitized contexts are legitimate
        if context_type == 'TEST_DATA' and confidence >= self.test_data_threshold:
            return True
        
        if context_type == 'SANITIZED' and confidence >= self.sanitization_threshold:
            return True
        
        if context_type == 'ENCRYPTED' and confidence >= 0.7:
            return True
        
        # Check for explicit suppression markers
        suppression_markers = context_info.get('suppression_markers', [])
        if suppression_markers:
            return True
        
        return False