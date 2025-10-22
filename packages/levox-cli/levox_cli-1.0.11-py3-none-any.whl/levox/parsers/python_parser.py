"""
Enhanced Python language parser for Levox using Tree-Sitter.
Provides advanced AST analysis capabilities for Python source code to detect PII and GDPR violations
with context-aware detection and reduced false positives.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field

from .base import BaseParser, ParsedNode, StringLiteral, Comment, ImportStatement, VariableDeclaration, FunctionDefinition, ClassDefinition

logger = logging.getLogger(__name__)


@dataclass
class PythonParsedNode(ParsedNode):
    """Python-specific parsed node with additional metadata."""
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    is_async: bool = False
    is_generator: bool = False
    is_test_function: bool = False
    is_test_file: bool = False
    framework_hints: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []


@dataclass
class FStringExpression:
    """Represents an f-string expression with embedded variables."""
    expression: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    variable_name: str
    context: str
    is_sensitive: bool = False


@dataclass
class LoggingContext:
    """Represents a logging statement with context."""
    function_name: str
    level: str
    arguments: List[str]
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    contains_pii: bool = False
    pii_types: List[str] = field(default_factory=list)


@dataclass
class TestContext:
    """Represents test-related code context."""
    test_type: str  # 'unittest', 'pytest', 'test_function'
    function_name: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    is_fixture: bool = False
    is_mock: bool = False


class PythonParser(BaseParser):
    """Enhanced Python language parser using Tree-Sitter grammar with advanced context analysis."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.language_name = "python"
        self.file_extensions = ['.py', '.pyw']
        
        # Advanced context detection patterns
        self.test_patterns = {
            'unittest': [
                r'import\s+unittest',
                r'class\s+\w+Test\w*\(unittest\.TestCase\)',
                r'def\s+test_\w+',
                r'self\.assert'
            ],
            'pytest': [
                r'import\s+pytest',
                r'@pytest\.',
                r'def\s+test_\w+',
                r'pytest\.'
            ],
            'test_functions': [
                r'def\s+test_\w+',
                r'def\s+Test\w+',
                r'def\s+test\w+'
            ]
        }
        
        # Logging context patterns
        self.logging_patterns = {
            'logging_functions': [
                'logging.info', 'logging.debug', 'logging.warning', 'logging.error', 'logging.critical',
                'logger.info', 'logger.debug', 'logger.warning', 'logger.error', 'logger.critical',
                'log.info', 'log.debug', 'log.warning', 'log.error', 'log.critical'
            ],
            'print_functions': ['print', 'pprint', 'pp'],
            'sensitive_sinks': [
                'requests.get', 'requests.post', 'requests.put', 'requests.delete',
                'urllib.request.urlopen', 'urllib2.urlopen',
                'subprocess.run', 'subprocess.call', 'subprocess.Popen',
                'os.system', 'os.popen'
            ]
        }
        
        # Compile regex patterns
        self._compile_test_patterns()
        
        # Initialize Tree-Sitter parser for Python
        self._initialize_parser()
        if self._init_tree_sitter():
            try:
                # Load Python grammar
                self._parser.set_language(self._get_python_language())
                logger.debug("Enhanced Python parser initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Python parser: {e}")
                self._parser = None
        else:
            logger.warning("Tree-Sitter not available for Python parsing")
            # The fallback parser should have been set by BaseParser._initialize_parser()
            if not self._parser:
                logger.warning("No fallback parser available")
    
    def _compile_test_patterns(self):
        """Compile regex patterns for test detection."""
        self.compiled_test_patterns = {}
        for test_type, patterns in self.test_patterns.items():
            self.compiled_test_patterns[test_type] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                for pattern in patterns
            ]
    
    def _get_python_language(self):
        """Get Python language grammar from tree-sitter-languages."""
        try:
            from tree_sitter_languages import get_language
            # Suppress deprecation warning for now until tree-sitter-languages is updated
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")
                return get_language("python")
        except ImportError:
            logger.error("tree-sitter-languages not available for Python")
            return None
        except Exception as e:
            logger.error(f"Failed to load Python language: {e}")
            return None
    
    def analyze_file_context(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze file context to determine if it's a test file, contains logging, etc."""
        context = {
            'is_test_file': False,
            'test_frameworks': set(),
            'has_logging': False,
            'has_sensitive_sinks': False,
            'framework_hints': set(),
            'is_generated': False
        }
        
        # Check for test patterns
        for test_type, patterns in self.compiled_test_patterns.items():
            for pattern in patterns:
                if pattern.search(content):
                    context['is_test_file'] = True
                    context['test_frameworks'].add(test_type)
        
        # Check for logging patterns
        for logging_func in self.logging_patterns['logging_functions']:
            if logging_func in content:
                context['has_logging'] = True
                break
        
        # Check for print statements
        for print_func in self.logging_patterns['print_functions']:
            if f"{print_func}(" in content:
                context['has_logging'] = True
                break
        
        # Check for sensitive sinks
        for sink in self.logging_patterns['sensitive_sinks']:
            if sink in content:
                context['has_sensitive_sinks'] = True
                break
        
        # Check for framework hints
        framework_indicators = {
            'django': ['from django', 'import django', 'django.', '@app.route'],
            'flask': ['from flask', 'import flask', '@app.route', 'Flask('],
            'fastapi': ['from fastapi', 'import fastapi', '@app.get', 'FastAPI('],
            'pandas': ['import pandas', 'pd.', 'DataFrame('],
            'numpy': ['import numpy', 'np.', 'array('],
            'tensorflow': ['import tensorflow', 'tf.', 'keras.'],
            'pytorch': ['import torch', 'torch.', 'nn.']
        }
        
        for framework, indicators in framework_indicators.items():
            if any(indicator in content for indicator in indicators):
                context['framework_hints'].add(framework)
        
        # Check for generated code markers
        generated_markers = [
            'auto-generated', 'generated by', '# Generated', '// Generated', 
            '@generated', 'DO NOT EDIT', 'This file was generated'
        ]
        if any(marker in content for marker in generated_markers):
            context['is_generated'] = True
        
        return context
    
    def extract_f_strings(self, content: str) -> List[FStringExpression]:
        """Extract f-string expressions with embedded variables for PII detection."""
        f_strings = []
        
        # Pattern to match f-strings with expressions
        f_string_pattern = r'f["\']([^"\']*(?:\{[^}]*\}[^"\']*)*)["\']'
        
        for match in re.finditer(f_string_pattern, content):
            f_string_content = match.group(1)
            
            # Extract expressions within braces
            expression_pattern = r'\{([^}]*)\}'
            for expr_match in re.finditer(expression_pattern, f_string_content):
                expression = expr_match.group(1)
                
                # Parse the expression to extract variable names
                variable_name = self._extract_variable_from_expression(expression)
                
                # Calculate positions
                start_pos = match.start() + f_string_content.find(expr_match.group(0)) + 1
                end_pos = start_pos + len(expr_match.group(0)) - 2
                
                line_num = content[:start_pos].count('\n') + 1
                col_start = start_pos - content.rfind('\n', 0, start_pos) - 1
                col_end = end_pos - content.rfind('\n', 0, end_pos) - 1
                
                # Determine if this might contain sensitive data
                is_sensitive = self._is_sensitive_expression(expression, variable_name)
                
                f_string_expr = FStringExpression(
                    expression=expression,
                    start_line=line_num,
                    start_col=col_start,
                    end_line=line_num,
                    end_col=col_end,
                    variable_name=variable_name,
                    context=self._get_f_string_context(content, start_pos),
                    is_sensitive=is_sensitive
                )
                f_strings.append(f_string_expr)
        
        return f_strings
    
    def _extract_variable_from_expression(self, expression: str) -> str:
        """Extract the main variable name from an f-string expression."""
        # Remove common formatting and method calls
        cleaned = re.sub(r'[!:\d]*$', '', expression.strip())
        
        # Handle method calls like variable.method()
        if '.' in cleaned and '(' in cleaned:
            cleaned = cleaned.split('.')[0]
        
        # Handle attribute access like variable.attr
        if '.' in cleaned:
            cleaned = cleaned.split('.')[0]
        
        return cleaned.strip()
    
    def _is_sensitive_expression(self, expression: str, variable_name: str) -> bool:
        """Determine if an f-string expression might contain sensitive data."""
        sensitive_indicators = [
            'email', 'password', 'secret', 'key', 'token', 'auth',
            'user', 'name', 'address', 'phone', 'ssn', 'credit',
            'account', 'bank', 'routing', 'iban'
        ]
        
        # Check variable name
        if any(indicator in variable_name.lower() for indicator in sensitive_indicators):
            return True
        
        # Check expression content
        if any(indicator in expression.lower() for indicator in sensitive_indicators):
            return True
        
        return False
    
    def _get_f_string_context(self, content: str, position: int) -> str:
        """Get context around an f-string expression."""
        # Look for surrounding context (function, class, etc.)
        lines = content.split('\n')
        line_num = content[:position].count('\n')
        
        if line_num < len(lines):
            line = lines[line_num]
            
            # Check for common patterns
            if 'def ' in line:
                return 'function_definition'
            elif 'class ' in line:
                return 'class_definition'
            elif '=' in line:
                return 'variable_assignment'
            elif '(' in line and ')' in line:
                return 'function_call'
        
        return 'unknown'
    
    def extract_logging_contexts(self, content: str) -> List[LoggingContext]:
        """Extract logging statements with context analysis."""
        logging_contexts = []
        
        # Pattern for logging statements
        logging_pattern = r'(logging|logger|log)\.(info|debug|warning|error|critical|log|exception)\s*\(([^)]*)\)'
        
        for match in re.finditer(logging_pattern, content, re.IGNORECASE):
            function_name = match.group(1)
            level = match.group(2)
            arguments = match.group(3)
            
            # Parse arguments to detect PII
            pii_types = self._detect_pii_in_logging_args(arguments)
            contains_pii = len(pii_types) > 0
            
            line_num = content[:match.start()].count('\n') + 1
            col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
            col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
            
            # Split arguments
            arg_list = [arg.strip() for arg in arguments.split(',') if arg.strip()]
            
            logging_context = LoggingContext(
                function_name=f"{function_name}.{level}",
                level=level,
                arguments=arg_list,
                start_line=line_num,
                start_col=col_start,
                end_line=line_num,
                end_col=col_end,
                contains_pii=contains_pii,
                pii_types=pii_types
            )
            logging_contexts.append(logging_context)
        
        # Also detect print statements
        print_pattern = r'print\s*\(([^)]*)\)'
        for match in re.finditer(print_pattern, content):
            arguments = match.group(1)
            pii_types = self._detect_pii_in_logging_args(arguments)
            contains_pii = len(pii_types) > 0
            
            line_num = content[:match.start()].count('\n') + 1
            col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
            col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
            
            arg_list = [arg.strip() for arg in arguments.split(',') if arg.strip()]
            
            logging_context = LoggingContext(
                function_name="print",
                level="print",
                arguments=arg_list,
                start_line=line_num,
                start_col=col_start,
                end_line=line_num,
                end_col=col_end,
                contains_pii=contains_pii,
                pii_types=pii_types
            )
            logging_contexts.append(logging_context)
        
        return logging_contexts
    
    def _detect_pii_in_logging_args(self, arguments: str) -> List[str]:
        """Detect PII patterns in logging arguments."""
        pii_types = []
        
        # Common PII patterns
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+1[-\s]?)?\(?[2-9]\d{2}\)?[-\s]?[2-9]\d{2}[-\s]?\d{4}\b',
            'ssn': r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
            'credit_card': r'\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        }
        
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, arguments):
                pii_types.append(pii_type)
        
        return pii_types
    
    def extract_test_contexts(self, content: str) -> List[TestContext]:
        """Extract test-related code contexts."""
        test_contexts = []
        
        # Detect test functions
        test_function_pattern = r'def\s+(test_\w+)\s*\([^)]*\):'
        for match in re.finditer(test_function_pattern, content):
            function_name = match.group(1)
            
            line_num = content[:match.start()].count('\n') + 1
            col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
            col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
            
            # Determine test type
            test_type = 'test_function'
            if 'unittest' in content[:match.start()]:
                test_type = 'unittest'
            elif 'pytest' in content[:match.start()]:
                test_type = 'pytest'
            
            # Check if it's a fixture or mock
            is_fixture = '@pytest.fixture' in content[:match.start()]
            is_mock = any(mock_indicator in content[:match.start()] for mock_indicator in ['@mock', 'unittest.mock', 'patch'])
            
            test_context = TestContext(
                test_type=test_type,
                function_name=function_name,
                start_line=line_num,
                start_col=col_start,
                end_line=line_num,
                end_col=col_end,
                is_fixture=is_fixture,
                is_mock=is_mock
            )
            test_contexts.append(test_context)
        
        # Detect test classes
        test_class_pattern = r'class\s+(\w+Test\w*)\s*\([^)]*\):'
        for match in re.finditer(test_class_pattern, content):
            class_name = match.group(1)
            
            line_num = content[:match.start()].count('\n') + 1
            col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
            col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
            
            test_context = TestContext(
                test_type='test_class',
                function_name=class_name,
                start_line=line_num,
                start_col=col_start,
                end_line=line_num,
                end_col=col_end,
                is_fixture=False,
                is_mock=False
            )
            test_contexts.append(test_context)
        
        return test_contexts
    
    def extract_variable_assignments_with_flow(self, content: str) -> List[Dict[str, Any]]:
        """Extract variable assignments with data flow tracking."""
        assignments = []
        
        # Pattern for variable assignments
        assignment_pattern = r'(\w+)\s*=\s*([^#\n]+)'
        
        for match in re.finditer(assignment_pattern, content):
            var_name = match.group(1)
            value = match.group(2)
            
            # Skip Python keywords
            if var_name in ['def', 'class', 'import', 'from', 'if', 'else', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'pass', 'break', 'continue', 'True', 'False', 'None']:
                continue
            
            line_num = content[:match.start()].count('\n') + 1
            col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
            col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
            
            # Analyze the value for potential PII
            pii_indicators = self._analyze_assignment_value(value)
            
            # Get context
            context = self._get_assignment_context(content, match.start())
            
            assignment = {
                'variable_name': var_name,
                'value': value.strip(),
                'start_line': line_num,
                'start_col': col_start,
                'end_line': line_num,
                'end_col': col_end,
                'context': context,
                'pii_indicators': pii_indicators,
                'is_sensitive': len(pii_indicators) > 0
            }
            assignments.append(assignment)
        
        return assignments
    
    def _analyze_assignment_value(self, value: str) -> List[str]:
        """Analyze assignment value for potential PII indicators."""
        indicators = []
        
        # Check for sensitive patterns in the value
        sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+1[-\s]?)?\(?[2-9]\d{2}\)?[-\s]?[2-9]\d{2}[-\s]?\d{4}\b',
            'ssn': r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
            'credit_card': r'\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'api_key': r'\b[A-Za-z0-9]{32,}\b',
            'url_with_auth': r'(?:https?|ftp)://[^:\s]+:[^@\s]+@[^\s]+'
        }
        
        for indicator, pattern in sensitive_patterns.items():
            if re.search(pattern, value):
                indicators.append(indicator)
        
        return indicators
    
    def _get_assignment_context(self, content: str, position: int) -> str:
        """Get context for a variable assignment."""
        # Look for surrounding context
        lines = content.split('\n')
        line_num = content[:position].count('\n')
        
        if line_num < len(lines):
            line = lines[line_num]
            
            # Check for function definition
            if 'def ' in line:
                return 'function_local'
            elif 'class ' in line:
                return 'class_attribute'
            elif 'if ' in line or 'for ' in line or 'while ' in line:
                return 'control_flow'
            elif 'try:' in line or 'except ' in line:
                return 'exception_handling'
            elif 'with ' in line:
                return 'context_manager'
        
        return 'module_global'
    
    def extract_strings(self, file_path: Path, content: str) -> List[StringLiteral]:
        """Enhanced string extraction with f-string and context analysis."""
        if not self._parser:
            return []
        
        # Check if we're using a fallback parser
        if hasattr(self._parser, 'language_name'):
            # This is a fallback parser, use the base parser's method
            return super().extract_strings(file_path, content)
        
        try:
            tree = self._parser.parse(bytes(content, 'utf8'))
            if not tree.root_node:
                return []
            
            strings = []
            self._extract_string_nodes(tree.root_node, strings, content)
            
            # Also extract f-strings that might not be caught by Tree-Sitter
            f_strings = self.extract_f_strings(content)
            for f_string in f_strings:
                # Convert f-string expressions to string literals for analysis
                string_literal = StringLiteral(
                    value=f_string.expression,
                    raw_value=f"f'{{{f_string.expression}}}'",
                    start_line=f_string.start_line,
                    start_col=f_string.start_col,
                    end_line=f_string.end_line,
                    end_col=f_string.end_col,
                    context=f_string.context,
                    parent_node_type="f_string_expression"
                )
                strings.append(string_literal)
            
            return strings
            
        except Exception as e:
            logger.error(f"Error extracting strings from Python file {file_path}: {e}")
            return []
    
    def _extract_string_nodes(self, node, strings: List[StringLiteral], content: str):
        """Recursively extract string literal nodes."""
        try:
            if node.type == 'string':
                # Extract string content
                string_text = self._get_node_text(node, content)
                if string_text:
                    # Remove quotes and handle escape sequences
                    raw_value = string_text
                    value = self._process_python_string(string_text)
                    
                    string_literal = StringLiteral(
                        value=value,
                        raw_value=raw_value,
                        start_line=node.start_point[0] + 1,
                        start_col=node.start_point[1],
                        end_line=node.end_point[0] + 1,
                        end_col=node.end_point[1],
                        context=self._get_string_context(node, content),
                        parent_node_type=node.type
                    )
                    strings.append(string_literal)
            
            # Recursively process children
            for child in node.children:
                self._extract_string_nodes(child, strings, content)
                
        except Exception as e:
            logger.debug(f"Error extracting string node: {e}")
    
    def _process_python_string(self, string_text: str) -> str:
        """Process Python string literal, handling escape sequences."""
        if not string_text:
            return ""
        
        # Remove surrounding quotes (handle triple quotes)
        if string_text.startswith('"""') and string_text.endswith('"""'):
            string_text = string_text[3:-3]
        elif string_text.startswith("'''") and string_text.endswith("'''"):
            string_text = string_text[3:-3]
        elif string_text.startswith('"') and string_text.endswith('"'):
            string_text = string_text[1:-1]
        elif string_text.startswith("'") and string_text.endswith("'"):
            string_text = string_text[1:-1]
        
        # Handle common Python escape sequences
        escape_map = {
            '\\n': '\n',
            '\\t': '\t',
            '\\r': '\r',
            '\\b': '\b',
            '\\f': '\f',
            '\\"': '"',
            "\\'": "'",
            '\\\\': '\\'
        }
        
        for escape, replacement in escape_map.items():
            string_text = string_text.replace(escape, replacement)
        
        return string_text
    
    def _get_string_context(self, node, content: str = "") -> str:
        """Get context around a string literal for better analysis."""
        try:
            # Look for parent node context
            parent = node.parent
            if parent:
                if parent.type == 'assignment':
                    return 'variable_assignment'
                elif parent.type == 'function_definition':
                    return 'function_body'
                elif parent.type == 'class_definition':
                    return 'class_body'
                elif parent.type == 'decorator':
                    return 'decorator'
                elif parent.type == 'call':
                    return 'function_call'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def extract_comments(self, file_path: Path, content: str) -> List[Comment]:
        """Extract all comments from Python source code."""
        if not self._parser:
            return []
        
        try:
            tree = self._parser.parse(bytes(content, 'utf8'))
            if not tree.root_node:
                return []
            
            comments = []
            self._extract_comment_nodes(tree.root_node, comments, content)
            
            return comments
            
        except Exception as e:
            logger.error(f"Error extracting comments from Python file {file_path}: {e}")
            return []
    
    def _extract_comment_nodes(self, node, comments: List[Comment], content: str):
        """Recursively extract comment nodes."""
        try:
            if node.type == 'comment':
                comment_text = self._get_node_text(node, content)
                if comment_text:
                    comment = Comment(
                        text=comment_text,
                        start_line=node.start_point[0] + 1,
                        start_col=node.start_point[1],
                        end_line=node.end_point[0] + 1,
                        end_col=node.end_point[1],
                        comment_type=self._get_comment_type(comment_text)
                    )
                    comments.append(comment)
            
            # Recursively process children
            for child in node.children:
                self._extract_comment_nodes(child, comments, content)
                
        except Exception as e:
            logger.debug(f"Error extracting comment node: {e}")
    
    def _get_comment_type(self, comment_text: str) -> str:
        """Determine the type of Python comment."""
        if comment_text.startswith('#'):
            return 'line'
        else:
            return 'unknown'
    
    def extract_imports(self, file_path: Path, content: str) -> List[ImportStatement]:
        """Extract all import statements from Python source code."""
        if not self._parser:
            return []
        
        try:
            tree = self._parser.parse(bytes(content, 'utf8'))
            if not tree.root_node:
                return []
            
            imports = []
            self._extract_import_nodes(tree.root_node, imports, content)
            
            return imports
            
        except Exception as e:
            logger.error(f"Error extracting imports from Python file {file_path}: {e}")
            return []
    
    def _extract_import_nodes(self, node, imports: List[ImportStatement], content: str):
        """Recursively extract import statement nodes."""
        try:
            if node.type in ['import_statement', 'import_from_statement']:
                import_text = self._get_node_text(node, content)
                if import_text:
                    # Parse import statement
                    import_parts = self._parse_import_statement(import_text)
                    
                    import_stmt = ImportStatement(
                        module=import_parts.get('module', ''),
                        name=import_parts.get('name', ''),
                        alias=import_parts.get('alias', ''),
                        start_line=node.start_point[0] + 1,
                        start_col=node.start_point[1],
                        end_line=node.end_point[0] + 1,
                        end_col=node.end_point[1],
                        import_type=import_parts.get('type', 'standard')
                    )
                    imports.append(import_stmt)
            
            # Recursively process children
            for child in node.children:
                self._extract_import_nodes(child, imports, content)
                
        except Exception as e:
            logger.debug(f"Error extracting import node: {e}")
    
    def _parse_import_statement(self, import_text: str) -> Dict[str, str]:
        """Parse Python import statement to extract components."""
        try:
            # Handle import statements
            if import_text.startswith('import '):
                import_text = import_text[7:]
                # Handle "import x as y"
                if ' as ' in import_text:
                    module, alias = import_text.split(' as ', 1)
                    return {
                        'module': module.strip(),
                        'name': module.strip().split('.')[-1],
                        'alias': alias.strip(),
                        'type': 'standard'
                    }
                else:
                    module = import_text.strip()
                    return {
                        'module': module,
                        'name': module.split('.')[-1],
                        'alias': '',
                        'type': 'standard'
                    }
            
            # Handle from ... import statements
            elif import_text.startswith('from '):
                import_text = import_text[5:]
                if ' import ' in import_text:
                    module_part, names_part = import_text.split(' import ', 1)
                    module = module_part.strip()
                    
                    # Handle "from x import y as z"
                    if ' as ' in names_part:
                        name, alias = names_part.split(' as ', 1)
                        return {
                            'module': module,
                            'name': name.strip(),
                            'alias': alias.strip(),
                            'type': 'from_import'
                        }
                    else:
                        name = names_part.strip()
                        return {
                            'module': module,
                            'name': name,
                            'alias': '',
                            'type': 'from_import'
                        }
            
            return {
                'module': import_text,
                'name': '',
                'alias': '',
                'type': 'unknown'
            }
            
        except Exception as e:
            logger.debug(f"Error parsing import statement '{import_text}': {e}")
            return {
                'module': import_text,
                'name': '',
                'alias': '',
                'type': 'unknown'
            }
    
    def extract_variables(self, file_path: Path, content: str) -> List[VariableDeclaration]:
        """Extract variable declarations from Python source code."""
        if not self._parser:
            return []
        
        try:
            tree = self._parser.parse(bytes(content, 'utf8'))
            if not tree.root_node:
                return []
            
            variables = []
            self._extract_variable_nodes(tree.root_node, variables, content)
            
            return variables
            
        except Exception as e:
            logger.error(f"Error extracting variables from Python file {file_path}: {e}")
            return []
    
    def _extract_variable_nodes(self, node, variables: List[VariableDeclaration], content: str):
        """Recursively extract variable declaration nodes."""
        try:
            if node.type == 'assignment':
                # Look for target names
                for child in node.children:
                    if child.type == 'identifier':
                        var_name = self._get_node_text(child, content)
                        if var_name:
                            # Try to get type annotation if present
                            var_type = ""
                            # Look for type annotation in the assignment
                            for sibling in node.children:
                                if sibling.type == 'type':
                                    var_type = self._get_node_text(sibling, content)
                                    break
                            
                            variable = VariableDeclaration(
                                name=var_name,
                                var_type=var_type,
                                modifiers=[],  # Python doesn't have explicit modifiers like Java
                                start_line=node.start_point[0] + 1,
                                start_col=node.start_point[1],
                                end_line=node.end_point[0] + 1,
                                end_col=node.end_point[1],
                                context=self._get_variable_context(node, content)
                            )
                            variables.append(variable)
            
            # Recursively process children
            for child in node.children:
                self._extract_variable_nodes(child, variables, content)
                
        except Exception as e:
            logger.debug(f"Error extracting variable node: {e}")
    
    def _get_variable_context(self, node, content: str) -> str:
        """Get context for a variable declaration."""
        try:
            parent = node.parent
            if parent:
                if parent.type == 'function_definition':
                    return 'function_local'
                elif parent.type == 'class_definition':
                    return 'class_attribute'
                elif parent.type == 'module':
                    return 'module_global'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def extract_functions(self, file_path: Path, content: str) -> List[FunctionDefinition]:
        """Extract function definitions from Python source code."""
        if not self._parser:
            return []
        
        try:
            tree = self._parser.parse(bytes(content, 'utf8'))
            if not tree.root_node:
                return []
            
            functions = []
            self._extract_function_nodes(tree.root_node, functions, content)
            
            return functions
            
        except Exception as e:
            logger.error(f"Error extracting functions from Python file {file_path}: {e}")
            return []
    
    def _extract_function_nodes(self, node, functions: List[FunctionDefinition], content: str):
        """Recursively extract function definition nodes."""
        try:
            if node.type == 'function_definition':
                # Extract function information
                function_name = ""
                parameters = []
                decorators = []
                is_async = False
                
                # Get function name
                for child in node.children:
                    if child.type == 'identifier':
                        function_name = self._get_node_text(child, content)
                    elif child.type == 'parameters':
                        parameters = self._extract_parameters(child, content)
                    elif child.type == 'decorator':
                        decorator_text = self._get_node_text(child, content)
                        if decorator_text:
                            decorators.append(decorator_text)
                
                # Check if async
                is_async = self._is_async_node(node)
                
                if function_name:
                    function = FunctionDefinition(
                        name=function_name,
                        return_type="",  # Python doesn't have explicit return types in function def
                        parameters=parameters,
                        modifiers=decorators,
                        start_line=node.start_point[0] + 1,
                        start_col=node.start_point[1],
                        end_line=node.end_point[0] + 1,
                        end_col=node.end_point[1],
                        context='function'
                    )
                    functions.append(function)
            
            # Recursively process children
            for child in node.children:
                self._extract_function_nodes(child, functions, content)
                
        except Exception as e:
            logger.debug(f"Error extracting function node: {e}")
    
    def _extract_parameters(self, params_node, content: str) -> List[str]:
        """Extract parameter names from parameters node."""
        parameters = []
        
        try:
            for child in params_node.children:
                if child.type == 'identifier':
                    param_name = self._get_node_text(child, content)
                    if param_name:
                        parameters.append(param_name)
        except Exception as e:
            logger.debug(f"Error extracting parameters: {e}")
        
        return parameters
    
    def extract_classes(self, file_path: Path, content: str) -> List[ClassDefinition]:
        """Extract class definitions from Python source code."""
        if not self._parser:
            return []
        
        try:
            tree = self._parser.parse(bytes(content, 'utf8'))
            if not tree.root_node:
                return []
            
            classes = []
            self._extract_class_nodes(tree.root_node, classes, content)
            
            return classes
            
        except Exception as e:
            logger.error(f"Error extracting classes from Python file {file_path}: {e}")
            return []
    
    def _extract_class_nodes(self, node, classes: List[ClassDefinition], content: str):
        """Recursively extract class definition nodes."""
        try:
            if node.type == 'class_definition':
                # Extract class information
                class_name = ""
                decorators = []
                bases = []
                
                # Get class name
                for child in node.children:
                    if child.type == 'identifier':
                        class_name = self._get_node_text(child, content)
                    elif child.type == 'decorator':
                        decorator_text = self._get_node_text(child, content)
                        if decorator_text:
                            decorators.append(decorator_text)
                    elif child.type == 'argument_list':
                        # Extract base classes
                        for arg_child in child.children:
                            if arg_child.type == 'identifier':
                                base_name = self._get_node_text(arg_child, content)
                                if base_name:
                                    bases.append(base_name)
                
                if class_name:
                    class_def = ClassDefinition(
                        name=class_name,
                        modifiers=decorators,
                        superclass=bases[0] if bases else "",
                        interfaces=bases[1:] if len(bases) > 1 else [],
                        start_line=node.start_point[0] + 1,
                        start_col=node.start_point[1],
                        end_line=node.end_point[0] + 1,
                        end_col=node.end_point[1],
                        context='class'
                    )
                    classes.append(class_def)
            
            # Recursively process children
            for child in node.children:
                self._extract_class_nodes(child, classes, content)
                
        except Exception as e:
            logger.debug(f"Error extracting class node: {e}")
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get information about the Python parser capabilities."""
        return {
            'language': 'python',
            'file_extensions': self.file_extensions,
            'tree_sitter_available': self._parser is not None,
            'capabilities': [
                'ast_parsing',
                'string_extraction',
                'comment_extraction',
                'import_analysis',
                'variable_declaration_analysis',
                'function_definition_analysis',
                'class_definition_analysis'
            ],
            'version': '1.0.0'
        }

    def get_enhanced_analysis(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive analysis including context, f-strings, logging, and test detection."""
        analysis = {
            'file_context': self.analyze_file_context(content, file_path),
            'f_strings': self.extract_f_strings(content),
            'logging_contexts': self.extract_logging_contexts(content),
            'test_contexts': self.extract_test_contexts(content),
            'variable_assignments': self.extract_variable_assignments_with_flow(content),
            'strings': self.extract_strings(file_path, content),
            'comments': self.extract_comments(file_path, content),
            'imports': self.extract_imports(file_path, content),
            'functions': self.extract_functions(file_path, content),
            'classes': self.extract_classes(file_path, content)
        }
        
        return analysis