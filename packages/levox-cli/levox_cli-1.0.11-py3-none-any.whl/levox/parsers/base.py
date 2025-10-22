"""
Enhanced base parser interface for language-specific parsing using Tree-Sitter.
Includes robust Windows support for loading Tree-Sitter DLLs by augmenting
the DLL search path when necessary, and provides advanced context detection
capabilities for all language parsers.
"""

import logging
import os
import sys
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING, Set
from pathlib import Path
from enum import Enum

if TYPE_CHECKING:
    from ..core.config import Config

try:
    import tree_sitter
    import tree_sitter_languages
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    tree_sitter = None
    tree_sitter_languages = None


class ContextType(Enum):
    """Types of code context for enhanced analysis."""
    PRODUCTION = "production"
    TEST = "test"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    EXAMPLE = "example"
    GENERATED = "generated"
    MOCK = "mock"
    FIXTURE = "fixture"


class RiskContext(Enum):
    """Risk contexts for code analysis."""
    SAFE = "safe"           # Test files, documentation, examples
    LOW_RISK = "low_risk"   # Development configs, localhost
    MEDIUM_RISK = "medium_risk"  # Production-like code
    HIGH_RISK = "high_risk"      # Production configs, live APIs
    CRITICAL = "critical"         # Production secrets, live credentials


# --- Windows DLL search path augmentation -----------------------------------
_WINDOWS_DLLS_CONFIGURED = False

def _configure_windows_dll_search_path(logger: logging.Logger) -> None:
    """On Windows, ensure directories containing Tree-Sitter DLLs are searchable.

    Many Python environments on Windows require explicit DLL directories via
    os.add_dll_directory for native extensions shipped as .dll files. This
    function makes a best-effort attempt to locate the relevant directories
    inside the installed packages and add them to the process DLL search path.
    """
    global _WINDOWS_DLLS_CONFIGURED
    if _WINDOWS_DLLS_CONFIGURED:
        return
    if sys.platform != "win32":
        return

    add_dir = getattr(os, "add_dll_directory", None)
    if add_dir is None:
        # Python < 3.8 will not have add_dll_directory; skip silently
        _WINDOWS_DLLS_CONFIGURED = True
        return

    try:
        candidate_dirs = []
        for mod in (tree_sitter, tree_sitter_languages):
            try:
                if mod and hasattr(mod, "__file__") and mod.__file__:
                    base_dir = Path(mod.__file__).parent
                    candidate_dirs.append(base_dir)
                    # Common subfolders used by packages to store native libs
                    for sub in ("build", "build\\languages", "bin", "lib"):
                        p = base_dir / sub
                        if p.exists():
                            candidate_dirs.append(p)
            except Exception:
                continue

        # Also scan one level deeper for any folder containing .dll files
        expanded_dirs: List[Path] = []
        for d in candidate_dirs:
            try:
                if d.exists():
                    expanded_dirs.append(d)
                    for child in d.iterdir():
                        if child.is_dir():
                            # Heuristic: if directory contains any .dll, add it
                            if any(grandchild.suffix.lower() == ".dll" for grandchild in child.glob("*.dll")):
                                expanded_dirs.append(child)
            except Exception:
                continue

        seen: set = set()
        for directory in expanded_dirs:
            try:
                dir_str = str(directory.resolve())
                if dir_str in seen:
                    continue
                seen.add(dir_str)
                add_dir(dir_str)
                logger.debug(f"Added DLL search directory: {dir_str}")
            except Exception:
                # Non-fatal; continue trying other directories
                continue
    finally:
        _WINDOWS_DLLS_CONFIGURED = True


@dataclass
class ParsedNode:
    """Structured representation of a parsed AST node."""
    node_type: str
    text: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    start_byte: int
    end_byte: int
    children: List['ParsedNode']
    metadata: Dict[str, Any]


@dataclass
class StringLiteral:
    """Represents a string literal with context."""
    value: str
    raw_value: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    context: str  # 'assignment', 'call', 'return', etc.
    parent_node_type: str


@dataclass
class Identifier:
    """Represents an identifier (variable/function/class name) with context."""
    name: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    context: str  # 'function_def', 'variable', 'parameter', etc.
    parent_node_type: str


@dataclass
class Comment:
    """Represents a comment in source code."""
    text: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    comment_type: str  # 'line', 'block', 'javadoc', etc.


@dataclass
class ImportStatement:
    """Represents an import statement in source code."""
    module: str
    name: str
    alias: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    import_type: str  # 'standard', 'from_import', 'require', etc.


@dataclass
class VariableDeclaration:
    """Represents a variable declaration in source code."""
    name: str
    var_type: str
    modifiers: List[str]
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    context: str  # 'class_field', 'local_variable', 'parameter', etc.


@dataclass
class FunctionDefinition:
    """Represents a function/method definition in source code."""
    name: str
    return_type: str
    parameters: List[str]
    modifiers: List[str]
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    context: str  # 'function', 'class_method', etc.


@dataclass
class ClassDefinition:
    """Represents a class definition in source code."""
    name: str
    modifiers: List[str]
    superclass: str
    interfaces: List[str]
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    context: str  # 'class', etc.


@dataclass
class ContextAnalysis:
    """Comprehensive context analysis for a file."""
    context_type: ContextType
    risk_context: RiskContext
    is_test_file: bool
    is_generated: bool
    has_suppressions: bool
    framework_hints: Set[str]
    language_confidence: float
    test_frameworks: Set[str]
    has_logging: bool
    has_sensitive_sinks: bool
    module_type: str  # 'es6', 'commonjs', 'mixed', 'unknown'
    business_context: Optional[str] = None
    encoding: str = "utf-8"


class BaseParser(ABC):
    """Enhanced base interface for language parsers using Tree-Sitter with advanced context detection."""
    
    def __init__(self, config: Optional['Config'] = None):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._parser = None
        self._language = None
        self.config = config
        
        # Common context detection patterns
        self._setup_common_patterns()
        
        # Configure Windows DLL search path before attempting to create parsers
        try:
            _configure_windows_dll_search_path(self.logger)
        except Exception:
            # Non-fatal; proceed with best-effort initialization
            pass
        # Note: Parser initialization is deferred to child classes
    
    def _setup_common_patterns(self):
        """Setup common patterns for context detection across all languages."""
        # Test file patterns
        self.test_file_patterns = {
            'test_directories': [
                'test', 'tests', '__tests__', 'spec', 'specs', '__specs__',
                'e2e', 'integration', 'unit', 'fixtures', 'mocks'
            ],
            'test_file_patterns': [
                r'\.test\.', r'\.spec\.', r'\.e2e\.', r'\.integration\.',
                r'\.unit\.', r'Test\.', r'Spec\.', r'Mock\.', r'Fixture\.'
            ],
            'test_framework_indicators': [
                'unittest', 'pytest', 'jest', 'mocha', 'vitest', 'cypress',
                'jasmine', 'karma', 'ava', 'tape', 'tap'
            ]
        }
        
        # Documentation patterns
        self.documentation_patterns = {
            'file_extensions': ['.md', '.rst', '.txt', '.adoc', '.tex'],
            'content_indicators': [
                'readme', 'changelog', 'license', 'contributing', 'docs',
                'documentation', 'api reference', 'tutorial', 'guide'
            ]
        }
        
        # Configuration patterns
        self.config_patterns = {
            'file_extensions': ['.config', '.conf', '.ini', '.cfg', '.properties'],
            'content_indicators': [
                'config', 'settings', 'environment', 'properties',
                'database', 'server', 'client', 'api'
            ]
        }
        
        # Generated code patterns
        self.generated_patterns = [
            'auto-generated', 'generated by', 'DO NOT EDIT', 'This file was generated',
            '<!-- Generated -->', '// Generated', '# Generated', '@generated'
        ]
        
        # Suppression patterns
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
            )
        }
        
        # Compile regex patterns
        self._compile_common_patterns()
    
    def _compile_common_patterns(self):
        """Compile regex patterns for common context detection."""
        self.compiled_test_file_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.test_file_patterns['test_file_patterns']
        ]
    
    def analyze_file_context(self, content: str, file_path: Path) -> ContextAnalysis:
        """Analyze file context using common patterns and language-specific heuristics."""
        context = {
            'context_type': self._determine_context_type(file_path, content),
            'risk_context': self._determine_risk_context(file_path, content),
            'is_test_file': self._is_test_file(file_path, content),
            'is_generated': self._is_generated_file(content),
            'has_suppressions': self._has_suppressions(content),
            'framework_hints': self._detect_frameworks(content),
            'language_confidence': self._calculate_language_confidence(content),
            'test_frameworks': self._detect_test_frameworks(content),
            'has_logging': self._detect_logging(content),
            'has_sensitive_sinks': self._detect_sensitive_sinks(content),
            'module_type': self._detect_module_type(content),
            'business_context': self._extract_business_context(content)
        }
        
        return ContextAnalysis(**context)
    
    def _determine_context_type(self, file_path: Path, content: str) -> ContextType:
        """Determine the primary context type of the file."""
        path_lower = str(file_path).lower()
        content_lower = content.lower()
        
        # Check for test files
        if self._is_test_file(file_path, content):
            return ContextType.TEST
        
        # Check for documentation
        if any(ext in path_lower for ext in self.documentation_patterns['file_extensions']):
            return ContextType.DOCUMENTATION
        
        if any(indicator in content_lower for indicator in self.documentation_patterns['content_indicators']):
            return ContextType.DOCUMENTATION
        
        # Check for configuration files
        if any(ext in path_lower for ext in self.config_patterns['file_extensions']):
            return ContextType.CONFIGURATION
        
        if any(indicator in content_lower for indicator in self.config_patterns['content_indicators']):
            return ContextType.CONFIGURATION
        
        # Check for example files
        if any(indicator in path_lower for indicator in ['example', 'sample', 'demo', 'tutorial']):
            return ContextType.EXAMPLE
        
        # Check for generated files
        if self._is_generated_file(content):
            return ContextType.GENERATED
        
        # Default to production
        return ContextType.PRODUCTION
    
    def _determine_risk_context(self, file_path: Path, content: str) -> RiskContext:
        """Determine the risk context of the file."""
        context_type = self._determine_context_type(file_path, content)
        
        # Safe contexts
        if context_type in [ContextType.TEST, ContextType.DOCUMENTATION, ContextType.EXAMPLE]:
            return RiskContext.SAFE
        
        # Generated code is generally safe
        if context_type == ContextType.GENERATED:
            return RiskContext.SAFE
        
        # Configuration files can vary in risk
        if context_type == ContextType.CONFIGURATION:
            if self._contains_production_indicators(content):
                return RiskContext.HIGH_RISK
            else:
                return RiskContext.LOW_RISK
        
        # Production code
        if context_type == ContextType.PRODUCTION:
            if self._contains_critical_indicators(content):
                return RiskContext.CRITICAL
            elif self._contains_production_indicators(content):
                return RiskContext.HIGH_RISK
            else:
                return RiskContext.MEDIUM_RISK
        
        return RiskContext.MEDIUM_RISK
    
    def _is_test_file(self, file_path: Path, content: str) -> bool:
        """Determine if a file is a test file."""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        # Check directory names
        for test_dir in self.test_file_patterns['test_directories']:
            if test_dir in path_str:
                return True
        
        # Check file patterns
        for pattern in self.compiled_test_file_patterns:
            if pattern.search(path_str):
                return True
        
        # Check content for test framework indicators
        for framework in self.test_file_patterns['test_framework_indicators']:
            if framework.lower() in content_lower:
                return True
        
        # Check for test function patterns
        test_function_patterns = [
            r'def\s+test_', r'function\s+test', r'it\s*\(', r'describe\s*\(',
            r'test\s*\(', r'@Test', r'@test', r'beforeEach', r'afterEach'
        ]
        
        for pattern in test_function_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _is_generated_file(self, content: str) -> bool:
        """Determine if a file contains generated code markers."""
        content_lower = content.lower()
        return any(marker.lower() in content_lower for marker in self.generated_patterns)
    
    def _has_suppressions(self, content: str) -> bool:
        """Check if the file contains suppression directives."""
        for pattern in self.suppression_patterns.values():
            if pattern.search(content):
                return True
        return False
    
    def _detect_frameworks(self, content: str) -> Set[str]:
        """Detect frameworks used in the code."""
        frameworks = set()
        content_lower = content.lower()
        
        # Common framework indicators
        framework_indicators = {
            'django': ['django', 'djangorestframework', '@app.route'],
            'flask': ['flask', 'werkzeug', '@app.route'],
            'fastapi': ['fastapi', 'uvicorn', '@app.get'],
            'react': ['react', 'jsx', 'useState', 'useEffect'],
            'vue': ['vue', 'vue-router', 'vuex'],
            'angular': ['@angular', 'ngOnInit', 'ngOnDestroy'],
            'express': ['express', 'express.js', 'app.get', 'app.post'],
            'next': ['next', 'getServerSideProps', 'getStaticProps'],
            'nuxt': ['nuxt', 'nuxt.config', 'pages/', 'layouts/']
        }
        
        for framework, indicators in framework_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                frameworks.add(framework)
        
        return frameworks
    
    def _detect_test_frameworks(self, content: str) -> Set[str]:
        """Detect test frameworks used in the code."""
        test_frameworks = set()
        content_lower = content.lower()
        
        for framework in self.test_file_patterns['test_framework_indicators']:
            if framework.lower() in content_lower:
                test_frameworks.add(framework)
        
        return test_frameworks
    
    def _detect_logging(self, content: str) -> bool:
        """Detect if the file contains logging statements."""
        logging_indicators = [
            'logging.', 'logger.', 'log.', 'console.log', 'console.info',
            'console.warn', 'console.error', 'print(', 'printf', 'syslog'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in logging_indicators)
    
    def _detect_sensitive_sinks(self, content: str) -> bool:
        """Detect if the file contains sensitive sink functions."""
        sensitive_sinks = [
            'fetch', 'XMLHttpRequest', 'requests.', 'urllib', 'subprocess',
            'eval', 'exec', 'os.system', 'localStorage', 'sessionStorage',
            'document.cookie', 'document.write'
        ]
        
        content_lower = content.lower()
        return any(sink in content_lower for sink in sensitive_sinks)
    
    def _detect_module_type(self, content: str) -> str:
        """Detect the module system used in the file."""
        content_lower = content.lower()
        
        if 'import ' in content_lower and 'from ' in content_lower:
            return 'es6'
        elif 'require(' in content_lower and 'module.exports' in content_lower:
            return 'commonjs'
        elif ('import ' in content_lower and 'require(' in content_lower) or \
             ('export ' in content_lower and 'module.exports' in content_lower):
            return 'mixed'
        else:
            return 'unknown'
    
    def _contains_production_indicators(self, content: str) -> bool:
        """Check if content contains production environment indicators."""
        production_indicators = [
            'production', 'prod', 'live', 'staging', 'aws', 'gcp', 'azure',
            'heroku', 'digitalocean', 'vps', 'server', 'database', 'api'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in production_indicators)
    
    def _contains_critical_indicators(self, content: str) -> bool:
        """Check if content contains critical security indicators."""
        critical_indicators = [
            'password', 'secret', 'key', 'token', 'credential', 'auth',
            'private_key', 'api_key', 'access_key', 'secret_key'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in critical_indicators)
    
    def _extract_business_context(self, content: str) -> Optional[str]:
        """Extract business context from file content."""
        # Look for business domain indicators
        business_domains = {
            'finance': ['bank', 'credit', 'payment', 'transaction', 'account'],
            'healthcare': ['patient', 'medical', 'health', 'diagnosis', 'treatment'],
            'ecommerce': ['product', 'order', 'cart', 'shopping', 'customer'],
            'education': ['student', 'course', 'grade', 'assignment', 'school'],
            'government': ['citizen', 'service', 'department', 'agency', 'public']
        }
        
        content_lower = content.lower()
        for domain, indicators in business_domains.items():
            if any(indicator in content_lower for indicator in indicators):
                return domain
        
        return None
    
    def _calculate_language_confidence(self, content: str) -> float:
        """Calculate confidence in language detection."""
        # This is a base implementation - language-specific parsers should override
        return 0.8
    
    def get_context_aware_confidence(self, base_confidence: float, context: ContextAnalysis) -> float:
        """Adjust confidence based on context analysis."""
        confidence = base_confidence
        
        # Context type modifiers
        context_modifiers = {
            ContextType.TEST: 0.3,           # Tests get reduced confidence
            ContextType.DOCUMENTATION: 0.1,  # Documentation gets very low confidence
            ContextType.EXAMPLE: 0.2,        # Examples get low confidence
            ContextType.GENERATED: 0.1,      # Generated code gets very low confidence
            ContextType.CONFIGURATION: 1.2,  # Config files get increased confidence
            ContextType.PRODUCTION: 1.0      # Production code gets base confidence
        }
        
        confidence *= context_modifiers.get(context.context_type, 1.0)
        
        # Risk context modifiers
        risk_modifiers = {
            RiskContext.SAFE: 0.2,           # Safe contexts get very low confidence
            RiskContext.LOW_RISK: 0.5,       # Low risk gets reduced confidence
            RiskContext.MEDIUM_RISK: 1.0,    # Medium risk gets base confidence
            RiskContext.HIGH_RISK: 1.3,      # High risk gets increased confidence
            RiskContext.CRITICAL: 1.5        # Critical gets highest confidence
        }
        
        confidence *= risk_modifiers.get(context.risk_context, 1.0)
        
        # Additional modifiers
        if context.is_generated:
            confidence *= 0.1
        
        if context.has_suppressions:
            confidence *= 0.5
        
        if context.is_test_file:
            confidence *= 0.4
        
        return max(0.0, min(1.0, confidence))
    
    def get_enhanced_context_analysis(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive context analysis for any language."""
        context_analysis = self.analyze_file_context(content, file_path)
        
        # Handle both ContextAnalysis objects and dictionaries
        if hasattr(context_analysis, 'context_type'):
            # ContextAnalysis object
            return {
                'context_type': context_analysis.context_type.value,
                'risk_context': context_analysis.risk_context.value,
                'is_test_file': context_analysis.is_test_file,
                'is_generated': context_analysis.is_generated,
                'has_suppressions': context_analysis.has_suppressions,
                'framework_hints': list(context_analysis.framework_hints),
                'language_confidence': context_analysis.language_confidence,
                'test_frameworks': list(context_analysis.test_frameworks),
                'has_logging': context_analysis.has_logging,
                'has_sensitive_sinks': context_analysis.has_sensitive_sinks,
                'module_type': context_analysis.module_type,
                'business_context': context_analysis.business_context,
                'recommended_confidence_adjustment': self.get_context_aware_confidence(0.8, context_analysis)
            }
        else:
            # Dictionary (from language-specific parsers)
            return {
                'context_type': context_analysis.get('context_type', 'unknown'),
                'risk_context': context_analysis.get('risk_context', 'unknown'),
                'is_test_file': context_analysis.get('is_test_file', False),
                'is_generated': context_analysis.get('is_generated', False),
                'has_suppressions': context_analysis.get('has_suppressions', False),
                'framework_hints': list(context_analysis.get('framework_hints', set())),
                'language_confidence': context_analysis.get('language_confidence', 0.5),
                'test_frameworks': list(context_analysis.get('test_frameworks', set())),
                'has_logging': context_analysis.get('has_logging', False),
                'has_sensitive_sinks': context_analysis.get('has_sensitive_sinks', False),
                'module_type': context_analysis.get('module_type', 'unknown'),
                'business_context': context_analysis.get('business_context', None),
                'recommended_confidence_adjustment': 0.0  # Default for dictionary case
            }

    def _init_tree_sitter(self) -> bool:
        """Initialize Tree-Sitter parser and return success status."""
        if not TREE_SITTER_AVAILABLE:
            self.logger.debug(f"Tree-Sitter not available for {self.language()}")
            return False
        
        try:
            if self._parser is None:
                self._initialize_parser()
            return self._parser is not None
        except Exception as e:
            self.logger.error(f"Failed to initialize Tree-Sitter parser: {e}")
            return False
    
    def _get_node_text(self, node, content: str) -> str:
        """Extract text content from a node."""
        try:
            start_byte = node.start_byte
            end_byte = node.end_byte
            return content[start_byte:end_byte]
        except Exception:
            return ""
    
    def _initialize_parser(self) -> None:
        """Initialize the Tree-Sitter parser for this language."""
        if not TREE_SITTER_AVAILABLE:
            self.logger.debug(f"Tree-Sitter not available for {self.language()}")
            # Set up fallback parser when Tree-Sitter is not available
            try:
                fallback_parser = self._create_mock_parser(self.language())
                if fallback_parser:
                    self._parser = fallback_parser
                    self.logger.info(f"Using fallback parser for {self.language()}")
                    return
            except Exception as e:
                self.logger.debug(f"Failed to create fallback parser: {e}")
            return
        
        try:
            language_name = self.language()

            # Try multiple aliases per language for better compatibility across wheel variants
            alias_map = {
                'python': ['python', 'py'],
                'javascript': ['javascript', 'js'],
                'typescript': ['typescript', 'ts', 'tsx'],
            }
            aliases = alias_map.get(language_name, [language_name])

            # 1) Try to acquire a ready parser from tree_sitter_languages
            for alias in aliases:
                try:
                    try:
                        from tree_sitter_languages import get_parser as tsl_get_parser
                    except Exception:
                        from tree_sitter_languages.core import get_parser as tsl_get_parser  # type: ignore
                    parser = tsl_get_parser(alias)
                    if parser and hasattr(parser, 'parse'):
                        self._parser = parser
                        # Capture language if exposed (optional)
                        self._language = getattr(parser, 'language', None)
                        self.logger.debug(f"Initialized Tree-Sitter parser via tree_sitter_languages for {alias}")
                        return
                except Exception as e:
                    self.logger.debug(f"get_parser failed for alias '{alias}': {e}")

            # 2) Try to get a Language object from tree_sitter_languages and set it on a Parser
            for alias in aliases:
                try:
                    try:
                        from tree_sitter_languages import get_language
                    except Exception:
                        from tree_sitter_languages.core import get_language  # type: ignore
                    
                    # Suppress deprecation warnings for tree_sitter_languages
                    import warnings
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")
                        lang_obj = get_language(alias)
                    
                    # Ensure it's a proper tree_sitter.Language
                    language_type = getattr(tree_sitter, 'Language', None)
                    if language_type is not None and isinstance(lang_obj, language_type):
                        self._language = lang_obj
                        parser = tree_sitter.Parser()
                        if hasattr(parser, 'set_language'):
                            parser.set_language(self._language)
                        else:
                            parser.language = self._language
                        self._parser = parser
                        self.logger.debug(f"Initialized Tree-Sitter parser via Language for {alias}")
                        return
                    else:
                        self.logger.debug(f"get_language returned non-Language object for {alias}; skipping")
                except Exception as e:
                    self.logger.debug(f"get_language failed for alias '{alias}': {e}")

            # 3) Fallback to individual language packages if available
            lang_fallback = self._load_fallback_grammar(language_name)
            language_type = getattr(tree_sitter, 'Language', None)
            if lang_fallback and language_type is not None and isinstance(lang_fallback, language_type):
                parser = tree_sitter.Parser()
                if hasattr(parser, 'set_language'):
                    parser.set_language(lang_fallback)
                else:
                    parser.language = lang_fallback
                self._language = lang_fallback
                self._parser = parser
                self.logger.debug(f"Initialized Tree-Sitter parser via module fallback for {language_name}")
                return

            # If we reach here, initialization failed
            self.logger.debug(f"Could not initialize Tree-Sitter parser for {language_name}")
            
            # Try to use fallback parser if Tree-Sitter is not available
            if not TREE_SITTER_AVAILABLE:
                try:
                    fallback_parser = self._create_mock_parser(language_name)
                    if fallback_parser:
                        self._parser = fallback_parser
                        self.logger.info(f"Using fallback parser for {language_name}")
                        return
                except Exception as e:
                    self.logger.debug(f"Failed to create fallback parser: {e}")

        except Exception as e:
            self.logger.error(f"Failed to initialize Tree-Sitter parser for {self.language()}: {e}")
            self._parser = None
            self._language = None
            
            # Try to use fallback parser if Tree-Sitter is not available
            if not TREE_SITTER_AVAILABLE:
                try:
                    fallback_parser = self._create_mock_parser(self.language())
                    if fallback_parser:
                        self._parser = fallback_parser
                        self.logger.info(f"Using fallback parser for {self.language()}")
                        return
                except Exception as e2:
                    self.logger.debug(f"Failed to create fallback parser: {e2}")
    
    def _load_fallback_grammar(self, language_name: str):
        """Fallback method to load language grammars from individual packages."""
        try:
            language_type = getattr(tree_sitter, 'Language', None)
            if language_name == 'python':
                import tree_sitter_python
                for attr in ('language', 'language_python'):
                    if hasattr(tree_sitter_python, attr):
                        candidate = getattr(tree_sitter_python, attr)()
                        if language_type is None or isinstance(candidate, language_type):
                            return candidate
                # Don't return fallback parser here - let _initialize_parser handle it
                return None
            elif language_name == 'javascript':
                import tree_sitter_javascript
                for attr in ('language', 'language_javascript'):
                    if hasattr(tree_sitter_javascript, attr):
                        candidate = getattr(tree_sitter_javascript, attr)()
                        if language_type is None or isinstance(candidate, language_type):
                            return candidate
                # Don't return fallback parser here - let _initialize_parser handle it
                return None
            elif language_name == 'typescript':
                import tree_sitter_typescript
                for attr in ('language', 'language_typescript', 'language_tsx'):
                    if hasattr(tree_sitter_typescript, attr):
                        try:
                            candidate = getattr(tree_sitter_typescript, attr)()
                            if language_type is None or isinstance(candidate, language_type):
                                return candidate
                        except Exception:
                            continue
                # Don't return fallback parser here - let _initialize_parser handle it
                return None
            else:
                self.logger.warning(f"No fallback grammar available for {language_name}")
                # Don't return fallback parser here - let _initialize_parser handle it
                return None
        except ImportError as e:
            self.logger.debug(f"Fallback grammar not available for {language_name}: {e}")
            # Don't return fallback parser here - let _initialize_parser handle it
            return None
    
    def _create_mock_parser(self, language_name: str):
        """Create a lightweight fallback parser when Tree-Sitter is unavailable."""
        # Check if fallback parsing is allowed
        if hasattr(self, 'config') and self.config and not self.config.allow_fallback_parsing:
            self.logger.error(f"Tree-Sitter parser unavailable for {language_name} and fallback parsing is disabled.")
            self.logger.error(f"Install tree-sitter-{language_name} or enable fallback parsing in configuration.")
            raise RuntimeError(f"Parser unavailable for {language_name} and fallback parsing disabled")
        
        # Check if full AST is required
        if hasattr(self, 'config') and self.config and self.config.require_full_ast:
            self.logger.error(f"Full AST required for {language_name} but Tree-Sitter parser unavailable.")
            self.logger.error(f"Install tree-sitter-{language_name} to enable full AST analysis.")
            raise RuntimeError(f"Full AST required for {language_name} but parser unavailable")
        
        # Log appropriate warnings based on configuration
        if hasattr(self, 'config') and self.config and self.config.fallback_parser_warnings:
            self.logger.warning(f"Tree-Sitter parser unavailable for {language_name}. Using lightweight fallback parser.")
            self.logger.info(f"Fallback parser provides basic tokenization. Install tree-sitter-{language_name} for full AST analysis.")
        else:
            self.logger.info(f"Using fallback parser for {language_name} (Tree-Sitter unavailable)")
        
        class FallbackParser:
            def __init__(self, language_name: str, logger: logging.Logger):
                self.language_name = language_name
                self.logger = logger
                self._setup_fallback_patterns()
            
            def _setup_fallback_patterns(self):
                """Setup regex patterns for basic tokenization."""
                if self.language_name == 'python':
                    self.patterns = {
                        'string_literal': r'([rfb]?"[^"]*"|\'[^\']*\'|"""[^"]*"""|\'\'\'[^\']*\'\'\')',
                        'comment': r'(#.*?)$',
                        'function_def': r'def\s+(\w+)\s*\([^)]*\)\s*:',
                        'class_def': r'class\s+(\w+)(?:\s*\([^)]*\))?\s*:',
                        'import_stmt': r'(?:from\s+(\w+(?:\.\w+)*)\s+import|import\s+(\w+(?:\.\w+)*))',
                        'assignment': r'(\w+)\s*=\s*[^#\n]+',
                        'variable': r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
                    }
                elif self.language_name == 'javascript':
                    self.patterns = {
                        'string_literal': r'([`"\'][^`"\']*[`"\']|`[^`]*`)',
                        'comment': r'(//.*?$|/\*.*?\*/)',
                        'function_def': r'(?:function\s+(\w+)|(\w+)\s*[:=]\s*function|(\w+)\s*[:=]\s*\([^)]*\)\s*=>)',
                        'class_def': r'class\s+(\w+)',
                        'import_stmt': r'(?:import\s+.*?from\s+[\'"]([^\'"]+)[\'"]|require\s*\(\s*[\'"]([^\'"]+)[\'"])',
                        'assignment': r'(\w+)\s*[:=]\s*[^;]+',
                        'variable': r'\b(?:const|let|var)\s+(\w+)'
                    }
                elif self.language_name == 'typescript':
                    self.patterns = {
                        'string_literal': r'([`"\'][^`"\']*[`"\']|`[^`]*`)',
                        'comment': r'(//.*?$|/\*.*?\*/)',
                        'function_def': r'(?:function\s+(\w+)|(\w+)\s*[:=]\s*function|(\w+)\s*[:=]\s*\([^)]*\)\s*=>)',
                        'class_def': r'class\s+(\w+)',
                        'import_stmt': r'(?:import\s+.*?from\s+[\'"]([^\'"]+)[\'"]|require\s*\(\s*[\'"]([^\'"]+)[\'"])',
                        'assignment': r'(\w+)\s*[:=]\s*[^;]+',
                        'variable': r'\b(?:const|let|var)\s+(\w+)'
                    }
                else:
                    # Generic fallback for unknown languages
                    self.patterns = {
                        'string_literal': r'([`"\'][^`"\']*[`"\']|`[^`]*`)',
                        'comment': r'(//.*?$|/\*.*?\*/|#.*?$)',
                        'function_def': r'\b(?:function|def|func)\s+(\w+)',
                        'class_def': r'\bclass\s+(\w+)',
                        'import_stmt': r'\b(?:import|require|using)\s+(\w+)',
                        'assignment': r'(\w+)\s*[:=]\s*[^;\n]+',
                        'variable': r'\b(\w+)\b'
                    }
            
            def parse(self, content):
                """Parse content using regex patterns and return a structured tree."""
                import re
                
                class FallbackTree:
                    def __init__(self, root_node):
                        self.root_node = root_node
                
                # Create root node
                root_node = self._create_fallback_root(content)
                
                # Extract tokens using patterns
                tokens = self._extract_tokens(content)
                
                # Build basic AST structure
                root_node.children = self._build_ast_structure(tokens, content)
                
                return FallbackTree(root_node)
            
            def _create_fallback_root(self, content):
                """Create a root node for the fallback parser."""
                class FallbackNode:
                    def __init__(self, node_type, text, start_line, start_col, end_line, end_col, start_byte, end_byte):
                        self.type = node_type
                        self.text = text
                        self.start_line = start_line
                        self.start_col = start_col
                        self.end_line = end_line
                        self.end_col = end_col
                        self.start_point = (start_line - 1, start_col - 1)  # Tree-sitter uses 0-based
                        self.end_point = (end_line - 1, end_col - 1)
                        self.start_byte = start_byte
                        self.end_byte = end_byte
                        self.children = []
                        self.node_type = node_type  # Add node_type for compatibility
                
                # Handle both string and bytes content
                if isinstance(content, str):
                    content_str = content
                    content_bytes = content.encode('utf-8')
                else:
                    content_str = content.decode('utf-8')
                    content_bytes = content
                
                return FallbackNode('program', content_str, 1, 1, len(content_str.splitlines()), 1, 0, len(content_bytes))
            
            def _extract_tokens(self, content):
                """Extract tokens using regex patterns."""
                import re
                tokens = []
                
                # Handle both string and bytes content
                if isinstance(content, bytes):
                    content_str = content.decode('utf-8')
                else:
                    content_str = content
                
                lines = content_str.splitlines()
                
                for line_num, line in enumerate(lines, 1):
                    line_start_col = 1
                    
                    # Extract string literals
                    for match in re.finditer(self.patterns['string_literal'], line):
                        tokens.append({
                            'type': 'string_literal',
                            'text': match.group(0),
                            'line': line_num,
                            'start_col': match.start() + 1,
                            'end_col': match.end() + 1,
                            'value': match.group(1) if len(match.groups()) > 0 else match.group(0)
                        })
                    
                    # Extract comments
                    for match in re.finditer(self.patterns['comment'], line):
                        tokens.append({
                            'type': 'comment',
                            'text': match.group(0),
                            'line': line_num,
                            'start_col': match.start() + 1,
                            'end_col': match.end() + 1,
                            'value': match.group(0)
                        })
                    
                    # Extract function definitions
                    for match in re.finditer(self.patterns['function_def'], line):
                        tokens.append({
                            'type': 'function_definition',
                            'text': match.group(0),
                            'line': line_num,
                            'start_col': match.start() + 1,
                            'end_col': match.end() + 1,
                            'name': next((g for g in match.groups() if g is not None), 'unknown')
                        })
                    
                    # Extract class definitions
                    for match in re.finditer(self.patterns['class_def'], line):
                        tokens.append({
                            'type': 'class_definition',
                            'text': match.group(0),
                            'line': line_num,
                            'start_col': match.start() + 1,
                            'end_col': match.end() + 1,
                            'name': match.group(1)
                        })
                    
                    # Extract import statements
                    for match in re.finditer(self.patterns['import_stmt'], line):
                        tokens.append({
                            'type': 'import_statement',
                            'text': match.group(0),
                            'line': line_num,
                            'start_col': match.start() + 1,
                            'end_col': match.end() + 1,
                            'module': next((g for g in match.groups() if g is not None), 'unknown')
                        })
                    
                    # Extract assignments
                    for match in re.finditer(self.patterns['assignment'], line):
                        tokens.append({
                            'type': 'assignment',
                            'text': match.group(0),
                            'line': line_num,
                            'start_col': match.start() + 1,
                            'end_col': match.end() + 1,
                            'name': match.group(1)
                        })
                    
                    # Extract identifiers (variables, function names, etc.)
                    for match in re.finditer(self.patterns['variable'], line):
                        # Skip if this identifier is already captured in other tokens
                        skip = False
                        for token in tokens:
                            if (token['type'] in ['function_definition', 'class_definition', 'assignment'] and 
                                token.get('name') == match.group(1)):
                                skip = True
                                break
                        
                        if not skip:
                            tokens.append({
                                'type': 'identifier',
                                'text': match.group(1),
                                'line': line_num,
                                'start_col': match.start() + 1,
                                'end_col': match.end() + 1,
                                'name': match.group(1)
                            })
                
                return tokens
            
            def _build_ast_structure(self, tokens, content):
                """Build basic AST structure from extracted tokens."""
                nodes = []
                
                for token in tokens:
                    node = self._create_fallback_node(token, content)
                    if node:
                        nodes.append(node)
                
                return nodes
            
            def _create_fallback_node(self, token, content):
                """Create a fallback node compatible with ParsedNode structure."""
                class FallbackNode:
                    def __init__(self, node_type, text, start_line, start_col, end_line, end_col, start_byte, end_byte):
                        self.type = node_type
                        self.text = text
                        self.start_line = start_line
                        self.start_col = start_col
                        self.end_line = end_line
                        self.end_col = end_col
                        self.start_point = (start_line - 1, start_col - 1)  # Tree-sitter uses 0-based
                        self.end_point = (end_line - 1, end_col - 1)
                        self.start_byte = start_byte
                        self.end_byte = end_byte
                        self.children = []
                        self.node_type = node_type  # Add node_type for compatibility
                
                # Calculate byte positions - handle both string and bytes content
                if isinstance(content, bytes):
                    content_str = content.decode('utf-8')
                else:
                    content_str = content
                
                lines_before = content_str.splitlines()[:token['line'] - 1]
                start_byte = sum(len(line.encode('utf-8')) + 1 for line in lines_before)  # +1 for newline
                start_byte += token['start_col'] - 1
                end_byte = start_byte + len(token['text'].encode('utf-8'))
                
                return FallbackNode(
                    token['type'],
                    token['text'],
                    token['line'],
                    token['start_col'],
                    token['line'],
                    token['end_col'],
                    start_byte,
                    end_byte
                )
        
        return FallbackParser(language_name, self.logger)
    
    def language(self) -> str:
        """Return the language name for Tree-Sitter."""
        return getattr(self, 'language_name', 'unknown')
    
    def parse(self, content: str, file_path: Optional[Path] = None) -> Optional[ParsedNode]:
        """Parse content and return structured representation."""
        if not self._parser:
            self.logger.warning(f"Parser not available for {self.language()}")
            # Return a basic parsed node instead of None
            return self._create_basic_parsed_node(content)
        
        try:
            # Parse the content - handle both string and bytes
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            tree = self._parser.parse(content_bytes)
            if not tree.root_node:
                # Return a basic parsed node instead of None
                return self._create_basic_parsed_node(content)
            
            # Convert to our structured format
            return self._convert_node(tree.root_node, content_bytes)
            
        except Exception as e:
            self.logger.error(f"Failed to parse content: {e}")
            if file_path:
                self.logger.error(f"File: {file_path}")
            # Return a basic parsed node instead of None
            return self._create_basic_parsed_node(content)
    
    def _create_basic_parsed_node(self, content: str) -> ParsedNode:
        """Create a basic parsed node when parsing fails."""
        # Handle both string and bytes content
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        
        return ParsedNode(
            node_type="parse_error",
            text=content[:100] + "..." if len(content) > 100 else content,
            start_line=1,
            start_col=1,
            end_line=1,
            end_col=1,
            start_byte=0,
            end_byte=len(content_bytes),
            children=[],
            metadata={'error': 'parsing_failed', 'fallback': True}
        )
    
    def _convert_node(self, node, source_bytes: bytes) -> ParsedNode:
        """Convert Tree-Sitter node to our ParsedNode format."""
        # Get node text safely
        try:
            text = source_bytes[node.start_byte:node.end_byte].decode('utf-8')
        except UnicodeDecodeError:
            text = source_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='replace')
        
        # Convert children
        children = []
        for child in node.children:
            children.append(self._convert_node(child, source_bytes))
        
        return ParsedNode(
            node_type=node.type,
            text=text,
            start_line=node.start_point[0] + 1,  # Tree-Sitter uses 0-based lines
            start_col=node.start_point[1] + 1,   # Tree-Sitter uses 0-based columns
            end_line=node.end_point[0] + 1,
            end_col=node.end_point[1] + 1,
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            children=children,
            metadata={}
        )
    
    def extract_strings(self, file_path: Path, content: str) -> List[StringLiteral]:
        """Extract string literals with context information."""
        print(f"DEBUG: extract_strings called with file_path: {file_path}")
        
        if not self._parser:
            print("DEBUG: No parser available, using basic extraction")
            # Return basic string extraction instead of empty list
            return self._extract_basic_strings(content)
        
        parsed = self.parse(content)
        print(f"DEBUG: Parse result: {parsed}")
        if not parsed:
            print("DEBUG: Parse failed, using basic extraction")
            # Return basic string extraction instead of empty list
            return self._extract_basic_strings(content)
        
        strings = []
        print(f"DEBUG: Starting recursive extraction with {len(parsed.children)} children")
        self._extract_strings_recursive(parsed, strings, content)
        print(f"DEBUG: Recursive extraction completed, found {len(strings)} strings")
        return strings
    
    def _extract_basic_strings(self, content: str) -> List[StringLiteral]:
        """Extract strings using basic regex when parsing fails."""
        import re
        strings = []
        # Basic string pattern matching
        string_pattern = r'["\']([^"\']*)["\']'
        for match in re.finditer(string_pattern, content):
            strings.append(StringLiteral(
                value=match.group(1),
                raw_value=match.group(0),
                start_line=content[:match.start()].count('\n') + 1,
                start_col=match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                end_line=content[:match.end()].count('\n') + 1,
                end_col=match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                context="", # No direct context from regex
                parent_node_type="" # No direct context from regex
            ))
        return strings
    
    def _extract_strings_recursive(self, node: ParsedNode, strings: List[StringLiteral], content: str) -> None:
        """Recursively extract string literals from AST."""
        print(f"DEBUG: _extract_strings_recursive called with node type: {node.node_type}")
        
        try:
            if self._is_string_node(node):
                print(f"DEBUG: Found string node: {node.node_type} with text: {node.text}")
                # Determine context
                try:
                    context = self._get_string_context(node, content)
                except TypeError:
                    # Fallback for parsers that don't need content parameter
                    context = self._get_string_context(node)
                
                # Extract string value (remove quotes)
                raw_value = node.text
                value = self._extract_string_value(raw_value)
                
                string_literal = StringLiteral(
                    value=value,
                    raw_value=raw_value,
                    start_line=node.start_line,
                    start_col=node.start_col,
                    end_line=node.end_line,
                    end_col=node.end_col,
                    context=context,
                    parent_node_type=node.node_type
                )
                strings.append(string_literal)
                print(f"DEBUG: Added string literal: {value}")
            
            # Recurse into children
            print(f"DEBUG: Processing {len(node.children)} children")
            for child in node.children:
                self._extract_strings_recursive(child, strings, content)
        except Exception as e:
            print(f"ERROR: Error in _extract_strings_recursive: {e}")
            import traceback
            print(f"ERROR: {traceback.format_exc()}")
    
    def extract_identifiers(self, content: str) -> List[Identifier]:
        """Extract identifiers with context information."""
        if not self._parser:
            # Return basic identifier extraction instead of empty list
            return self._extract_basic_identifiers(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic identifier extraction instead of empty list
            return self._extract_basic_identifiers(content)
        
        identifiers = []
        self._extract_identifiers_recursive(parsed, identifiers, content)
        return identifiers
    
    def _extract_basic_identifiers(self, content: str) -> List[Identifier]:
        """Extract identifiers using basic regex when parsing fails."""
        import re
        identifiers = []
        # Basic identifier pattern matching
        identifier_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        for match in re.finditer(identifier_pattern, content):
            # Skip common keywords
            if match.group(1) not in ['def', 'class', 'import', 'from', 'if', 'else', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'pass', 'break', 'continue', 'True', 'False', 'None']:
                identifiers.append(Identifier(
                    name=match.group(1),
                    start_line=content[:match.start()].count('\n') + 1,
                    start_col=match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                    end_line=content[:match.end()].count('\n') + 1,
                    end_col=match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                    context="variable", # Assume variable context
                    parent_node_type="unknown"
                ))
        return identifiers
    
    def _extract_identifiers_recursive(self, node: ParsedNode, identifiers: List[Identifier], content: str = "") -> None:
        """Recursively extract identifiers from AST."""
        if self._is_identifier_node(node):
            try:
                context = self._get_identifier_context(node, content)
            except (TypeError, NameError):
                # Fallback for parsers that don't need content parameter
                context = self._get_identifier_context(node)
            
            identifiers.append(Identifier(
                name=node.text,
                start_line=node.start_line,
                start_col=node.start_col,
                end_line=node.end_line,
                end_col=node.end_col,
                context=context,
                parent_node_type=node.node_type
            ))
        
        # Recurse into children
        for child in node.children:
            self._extract_identifiers_recursive(child, identifiers)
    
    def _is_string_node(self, node: ParsedNode) -> bool:
        """Check if node represents a string literal."""
        return node.node_type in ['string', 'string_literal']
    
    def _is_identifier_node(self, node: ParsedNode) -> bool:
        """Check if node represents an identifier."""
        return node.node_type in ['identifier', 'name']
    
    def _get_string_context(self, node: ParsedNode, content: str = "") -> str:
        """Get context for a string literal."""
        if node.parent_node_type:
            return node.parent_node_type
        return 'unknown'
    
    def _get_identifier_context(self, node: ParsedNode, content: str = "") -> str:
        """Get context for an identifier."""
        # For fallback parser nodes, we can infer context from node_type
        if node.node_type == 'assignment':
            return 'variable_assignment'
        elif node.node_type == 'function_definition':
            return 'function_definition'
        elif node.node_type == 'class_definition':
            return 'class_definition'
        elif node.node_type == 'identifier':
            return 'variable'
        else:
            return 'unknown'
    
    def _extract_string_value(self, raw_value: str) -> str:
        """Extract the actual string value from raw text (remove quotes, handle escapes)."""
        # Basic string extraction - remove surrounding quotes
        if raw_value.startswith('"') and raw_value.endswith('"'):
            return raw_value[1:-1]
        elif raw_value.startswith("'") and raw_value.endswith("'"):
            return raw_value[1:-1]
        elif raw_value.startswith('`') and raw_value.endswith('`'):
            return raw_value[1:-1]
        return raw_value
    
    def get_node_text_safe(self, node, source_bytes: bytes) -> str:
        """Safely extract text from a Tree-Sitter node."""
        try:
            return source_bytes[node.start_byte:node.end_byte].decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            return source_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='replace')
    
    def traverse_depth_first(self, node: ParsedNode, visitor_func) -> None:
        """Traverse AST depth-first and apply visitor function to each node."""
        visitor_func(node)
        for child in node.children:
            self.traverse_depth_first(child, visitor_func)
    
    def find_nodes_by_type(self, root: ParsedNode, node_types: List[str]) -> List[ParsedNode]:
        """Find all nodes of specified types."""
        found_nodes = []
        
        def visitor(node: ParsedNode):
            if node.node_type in node_types:
                found_nodes.append(node)
        
        self.traverse_depth_first(root, visitor)
        return found_nodes
    
    def get_line_column_from_byte_offset(self, content: str, byte_offset: int) -> Tuple[int, int]:
        """Convert byte offset to line and column numbers."""
        lines = content[:byte_offset].split('\n')
        line = len(lines)
        col = len(lines[-1]) + 1 if lines else 1
        return line, col

    def extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions with context."""
        if not self._parser:
            # Return basic function extraction instead of empty list
            return self._extract_basic_functions(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic function extraction instead of empty list
            return self._extract_basic_functions(content)
        
        functions = []
        self._extract_functions_recursive(parsed, functions, content)
        return functions
    
    def _extract_basic_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract functions using basic regex when parsing fails."""
        import re
        functions = []
        # Basic function pattern matching for Python
        if self.language() == 'python':
            function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\):'
        elif self.language() == 'javascript':
            function_pattern = r'(?:function\s+([a-zA-Z_][a-zA-Z0-9_]*)|const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\([^)]*\)\s*=>|let\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\([^)]*\)\s*=>)'
        else:
            function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        
        for match in re.finditer(function_pattern, content):
            func_name = match.group(1) or match.group(2) or match.group(3)
            if func_name:
                functions.append({
                    'name': func_name,
                    'start_line': content[:match.start()].count('\n') + 1,
                    'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                    'end_line': content[:match.end()].count('\n') + 1,
                    'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                    'context': 'function_def',
                    'parent_node_type': 'function'
                })
        return functions

    def extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract import statements with context."""
        if not self._parser:
            # Return basic import extraction instead of empty list
            return self._extract_basic_imports(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic import extraction instead of empty list
            return self._extract_basic_imports(content)
        
        imports = []
        self._extract_imports_recursive(parsed, imports, content)
        return imports
    
    def _extract_basic_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract imports using basic regex when parsing fails."""
        import re
        imports = []
        # Basic import pattern matching for Python
        if self.language() == 'python':
            import_pattern = r'(?:from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import\s+([a-zA-Z_][a-zA-Z0-9_,\s*]*)|import\s+([a-zA-Z_][a-zA-Z0-9_.]*))'
        elif self.language() == 'javascript':
            import_pattern = r'(?:import\s+(?:\{[^}]*\}|\*\s+as\s+[a-zA-Z_][a-zA-Z0-9_]*|[a-zA-Z_][a-zA-Z0-9_]*)\s+from\s+[\'"]([^\'"]*)[\'"]|import\s+[\'"]([^\'"]*)[\'"])'
        else:
            import_pattern = r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)'
        
        for match in re.finditer(import_pattern, content):
            module = match.group(1) or match.group(2) or match.group(3)
            if module:
                imports.append({
                    'module': module.strip(),
                    'start_line': content[:match.start()].count('\n') + 1,
                    'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                    'end_line': content[:match.end()].count('\n') + 1,
                    'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                    'context': 'import',
                    'parent_node_type': 'import'
                })
        return imports

    def extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions with context."""
        if not self._parser:
            # Return basic class extraction instead of empty list
            return self._extract_basic_classes(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic class extraction instead of empty list
            return self._extract_basic_classes(content)
        
        classes = []
        self._extract_classes_recursive(parsed, classes, content)
        return classes
    
    def _extract_basic_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract classes using basic regex when parsing fails."""
        import re
        classes = []
        # Basic class pattern matching for Python
        if self.language() == 'python':
            class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)(?:\s*\([^)]*\))?:'
        elif self.language() == 'javascript':
            class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)(?:\s+extends\s+[a-zA-Z_][a-zA-Z0-9_]*)?'
        else:
            class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            if class_name:
                classes.append({
                    'name': class_name,
                    'start_line': content[:match.start()].count('\n') + 1,
                    'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                    'end_line': content[:match.end()].count('\n') + 1,
                    'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                    'context': 'class_def',
                    'parent_node_type': 'class'
                })
        return classes

    def extract_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract variable assignments with context."""
        if not self._parser:
            # Return basic variable extraction instead of empty list
            return self._extract_basic_variables(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic variable extraction instead of empty list
            return self._extract_basic_variables(content)
        
        variables = []
        self._extract_variables_recursive(parsed, variables, content)
        return variables
    
    def _extract_basic_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract variables using basic regex when parsing fails."""
        import re
        variables = []
        # Basic variable pattern matching for Python
        if self.language() == 'python':
            variable_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*[^#\n]+'
        elif self.language() == 'javascript':
            variable_pattern = r'(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        else:
            variable_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        
        for match in re.finditer(variable_pattern, content):
            var_name = match.group(1)
            if var_name and var_name not in ['def', 'class', 'import', 'from', 'if', 'else', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'pass', 'break', 'continue', 'True', 'False', 'None']:
                variables.append({
                    'name': var_name,
                    'start_line': content[:match.start()].count('\n') + 1,
                    'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                    'end_line': content[:match.end()].count('\n') + 1,
                    'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                    'context': 'variable_assignment',
                    'parent_node_type': 'assignment'
                })
        return variables

    def extract_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract comments with context."""
        if not self._parser:
            # Return basic comment extraction instead of empty list
            return self._extract_basic_comments(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic comment extraction instead of empty list
            return self._extract_basic_comments(content)
        
        comments = []
        self._extract_comments_recursive(parsed, comments, content)
        return comments
    
    def _extract_basic_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract comments using basic regex when parsing fails."""
        import re
        comments = []
        # Basic comment pattern matching for Python
        if self.language() == 'python':
            comment_pattern = r'#\s*(.+)'
        elif self.language() == 'javascript':
            comment_pattern = r'(?://\s*(.+)|/\*[\s\S]*?\*/)'
        else:
            comment_pattern = r'#\s*(.+)'
        
        for match in re.finditer(comment_pattern, content):
            comment_text = match.group(1) or match.group(0)
            if comment_text:
                comments.append({
                    'text': comment_text.strip(),
                    'start_line': content[:match.start()].count('\n') + 1,
                    'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                    'end_line': content[:match.end()].count('\n') + 1,
                    'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                    'context': 'comment',
                    'parent_node_type': 'comment'
                })
        return comments

    def extract_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract function calls with context."""
        if not self._parser:
            # Return basic call extraction instead of empty list
            return self._extract_basic_calls(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic call extraction instead of empty list
            return self._extract_basic_calls(content)
        
        calls = []
        self._extract_calls_recursive(parsed, calls, content)
        return calls
    
    def _extract_basic_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract calls using basic regex when parsing fails."""
        import re
        calls = []
        # Basic call pattern matching for Python
        if self.language() == 'python':
            call_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)'
        elif self.language() == 'javascript':
            call_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)'
        else:
            call_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        
        for match in re.finditer(call_pattern, content):
            func_name = match.group(1)
            if func_name and func_name not in ['def', 'class', 'import', 'from', 'if', 'else', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'pass', 'break', 'continue', 'True', 'False', 'None']:
                calls.append({
                    'name': func_name,
                    'start_line': content[:match.start()].count('\n') + 1,
                    'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                    'end_line': content[:match.end()].count('\n') + 1,
                    'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                    'context': 'function_call',
                    'parent_node_type': 'call'
                })
        return calls

    def extract_assignments(self, content: str) -> List[Dict[str, Any]]:
        """Extract assignment statements with context."""
        if not self._parser:
            # Return basic assignment extraction instead of empty list
            return self._extract_basic_assignments(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic assignment extraction instead of empty list
            return self._extract_basic_assignments(content)
        
        assignments = []
        self._extract_assignments_recursive(parsed, assignments, content)
        return assignments
    
    def _extract_basic_assignments(self, content: str) -> List[Dict[str, Any]]:
        """Extract assignments using basic regex when parsing fails."""
        import re
        assignments = []
        # Basic assignment pattern matching for Python
        if self.language() == 'python':
            assignment_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^#\n]+)'
        elif self.language() == 'javascript':
            assignment_pattern = r'(?:const|let|var)?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^;]+)'
        else:
            assignment_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^;\n]+)'
        
        for match in re.finditer(assignment_pattern, content):
            var_name = match.group(1)
            value = match.group(2)
            if var_name and var_name not in ['def', 'class', 'import', 'from', 'if', 'else', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'pass', 'break', 'continue', 'True', 'False', 'None']:
                assignments.append({
                    'name': var_name,
                    'value': value.strip(),
                    'start_line': content[:match.start()].count('\n') + 1,
                    'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                    'end_line': content[:match.end()].count('\n') + 1,
                    'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                    'context': 'assignment',
                    'parent_node_type': 'assignment'
                })
        return assignments

    def extract_returns(self, content: str) -> List[Dict[str, Any]]:
        """Extract return statements with context."""
        if not self._parser:
            # Return basic return extraction instead of empty list
            return self._extract_basic_returns(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic return extraction instead of empty list
            return self._extract_basic_returns(content)
        
        returns = []
        self._extract_returns_recursive(parsed, returns, content)
        return returns
    
    def _extract_basic_returns(self, content: str) -> List[Dict[str, Any]]:
        """Extract returns using basic regex when parsing fails."""
        import re
        returns = []
        # Basic return pattern matching for Python
        if self.language() == 'python':
            return_pattern = r'return\s+([^#\n]*)'
        elif self.language() == 'javascript':
            return_pattern = r'return\s+([^;]*)'
        else:
            return_pattern = r'return\s+([^;\n]*)'
        
        for match in re.finditer(return_pattern, content):
            return_value = match.group(1)
            returns.append({
                'value': return_value.strip() if return_value else '',
                'start_line': content[:match.start()].count('\n') + 1,
                'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                'end_line': content[:match.end()].count('\n') + 1,
                'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                'context': 'return',
                'parent_node_type': 'return'
            })
        return returns

    def extract_conditionals(self, content: str) -> List[Dict[str, Any]]:
        """Extract conditional statements with context."""
        if not self._parser:
            # Return basic conditional extraction instead of empty list
            return self._extract_basic_conditionals(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic conditional extraction instead of empty list
            return self._extract_basic_conditionals(content)
        
        conditionals = []
        self._extract_conditionals_recursive(parsed, conditionals, content)
        return conditionals
    
    def _extract_basic_conditionals(self, content: str) -> List[Dict[str, Any]]:
        """Extract conditionals using basic regex when parsing fails."""
        import re
        conditionals = []
        # Basic conditional pattern matching for Python
        if self.language() == 'python':
            conditional_pattern = r'(?:if|elif|else)\s*([^:]*):'
        elif self.language() == 'javascript':
            conditional_pattern = r'(?:if|else\s+if|else)\s*\(([^)]*)\)'
        else:
            conditional_pattern = r'(?:if|elif|else)\s*([^:]*):'
        
        for match in re.finditer(conditional_pattern, content):
            condition = match.group(1)
            conditional_type = 'if' if match.group(0).startswith('if') else 'elif' if 'elif' in match.group(0) else 'else'
            conditionals.append({
                'type': conditional_type,
                'condition': condition.strip() if condition else '',
                'start_line': content[:match.start()].count('\n') + 1,
                'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                'end_line': content[:match.end()].count('\n') + 1,
                'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                'context': 'conditional',
                'parent_node_type': 'conditional'
            })
        return conditionals

    def extract_loops(self, content: str) -> List[Dict[str, Any]]:
        """Extract loop statements with context."""
        if not self._parser:
            # Return basic loop extraction instead of empty list
            return self._extract_basic_loops(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic loop extraction instead of empty list
            return self._extract_basic_loops(content)
        
        loops = []
        self._extract_loops_recursive(parsed, loops, content)
        return loops
    
    def _extract_basic_loops(self, content: str) -> List[Dict[str, Any]]:
        """Extract loops using basic regex when parsing fails."""
        import re
        loops = []
        # Basic loop pattern matching for Python
        if self.language() == 'python':
            loop_pattern = r'(?:for|while)\s+([^:]*):'
        elif self.language() == 'javascript':
            loop_pattern = r'(?:for|while)\s*\(([^)]*)\)'
        else:
            loop_pattern = r'(?:for|while)\s+([^:]*):'
        
        for match in re.finditer(loop_pattern, content):
            loop_condition = match.group(1)
            loop_type = 'for' if match.group(0).startswith('for') else 'while'
            loops.append({
                'type': loop_type,
                'condition': loop_condition.strip() if loop_condition else '',
                'start_line': content[:match.start()].count('\n') + 1,
                'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                'end_line': content[:match.end()].count('\n') + 1,
                'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                'context': 'loop',
                'parent_node_type': 'loop'
            })
        return loops

    def extract_try_except(self, content: str) -> List[Dict[str, Any]]:
        """Extract try-except blocks with context."""
        if not self._parser:
            # Return basic try-except extraction instead of empty list
            return self._extract_basic_try_except(content)
        
        parsed = self.parse(content)
        if not parsed:
            # Return basic try-except extraction instead of empty list
            return self._extract_basic_try_except(content)
        
        try_excepts = []
        self._extract_try_except_recursive(parsed, try_excepts, content)
        return try_excepts
    
    def _extract_basic_try_except(self, content: str) -> List[Dict[str, Any]]:
        """Extract try-except blocks using basic regex when parsing fails."""
        import re
        try_excepts = []
        # Basic try-except pattern matching for Python
        if self.language() == 'python':
            try_except_pattern = r'(?:try|except|finally)\s*([^:]*):'
        elif self.language() == 'javascript':
            try_except_pattern = r'(?:try|catch|finally)\s*\(?([^)]*)\)?'
        else:
            try_except_pattern = r'(?:try|except|finally)\s*([^:]*):'
        
        for match in re.finditer(try_except_pattern, content):
            block_type = 'try' if match.group(0).startswith('try') else 'except' if 'except' in match.group(0) or 'catch' in match.group(0) else 'finally'
            condition = match.group(1)
            try_excepts.append({
                'type': block_type,
                'condition': condition.strip() if condition else '',
                'start_line': content[:match.start()].count('\n') + 1,
                'start_col': match.start() - content.rfind('\n', 0, match.start()) if '\n' in content[:match.start()] else match.start() + 1,
                'end_line': content[:match.end()].count('\n') + 1,
                'end_col': match.end() - content.rfind('\n', 0, match.end()) if '\n' in content[:match.end()] else match.end(),
                'context': 'exception_handling',
                'parent_node_type': 'try_except'
            })
        return try_excepts
