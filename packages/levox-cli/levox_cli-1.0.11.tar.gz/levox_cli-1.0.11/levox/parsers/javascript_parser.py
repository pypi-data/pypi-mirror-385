"""
Enhanced JavaScript/TypeScript language parser for Levox using Tree-Sitter.
Provides advanced AST analysis capabilities for JavaScript/TypeScript source code to detect PII and GDPR violations
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
class JavaScriptParsedNode(ParsedNode):
    """JavaScript/TypeScript-specific parsed node with additional metadata."""
    is_async: bool = False
    is_generator: bool = False
    is_exported: bool = False
    is_default_export: bool = False
    is_test_function: bool = False
    is_test_file: bool = False
    framework_hints: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        pass


@dataclass
class TemplateLiteralExpression:
    """Represents a template literal expression with embedded variables."""
    expression: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    variable_name: str
    context: str
    is_sensitive: bool = False


@dataclass
class ConsoleLoggingContext:
    """Represents a console logging statement with context."""
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
class TestFrameworkContext:
    """Represents test framework related code context."""
    framework: str  # 'jest', 'mocha', 'vitest', 'cypress'
    test_type: str  # 'describe', 'it', 'test', 'beforeEach', 'afterEach'
    function_name: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    is_fixture: bool = False
    is_mock: bool = False


@dataclass
class ES6ModuleContext:
    """Represents ES6 module import/export context."""
    module_name: str
    import_type: str  # 'default', 'named', 'namespace', 'dynamic'
    exported_items: List[str]
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    is_sensitive_import: bool = False


class JavaScriptParser(BaseParser):
    """Enhanced JavaScript language parser using Tree-Sitter grammar with advanced context analysis."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.language_name = "javascript"
        self.file_extensions = ['.js', '.jsx', '.mjs']
        
        # Advanced context detection patterns
        self.test_patterns = {
            'jest': [
                r'import\s+.*\s+from\s+[\'"`]jest[\'"`]',
                r'describe\s*\(',
                r'it\s*\(',
                r'test\s*\(',
                r'beforeEach\s*\(',
                r'afterEach\s*\(',
                r'beforeAll\s*\(',
                r'afterAll\s*\(',
                r'jest\.',
                r'@jest/'
            ],
            'mocha': [
                r'import\s+.*\s+from\s+[\'"`]mocha[\'"`]',
                r'describe\s*\(',
                r'it\s*\(',
                r'before\s*\(',
                r'after\s*\(',
                r'beforeEach\s*\(',
                r'afterEach\s*\(',
                r'mocha\.'
            ],
            'vitest': [
                r'import\s+.*\s+from\s+[\'"`]vitest[\'"`]',
                r'import\s+.*\s+from\s+[\'"`]@vitest/ui[\'"`]',
                r'describe\s*\(',
                r'it\s*\(',
                r'test\s*\(',
                r'beforeEach\s*\(',
                r'afterEach\s*\(',
                r'vi\.'
            ],
            'cypress': [
                r'import\s+.*\s+from\s+[\'"`]cypress[\'"`]',
                r'cy\.',
                r'describe\s*\(',
                r'it\s*\(',
                r'before\s*\(',
                r'after\s*\(',
                r'beforeEach\s*\(',
                r'afterEach\s*\('
            ]
        }
        
        # Console logging patterns
        self.console_patterns = {
            'console_functions': [
                'console.log', 'console.info', 'console.warn', 'console.error', 'console.debug', 'console.trace'
            ],
            'sensitive_sinks': [
                'fetch', 'XMLHttpRequest', 'axios.', 'jQuery.ajax', '$.ajax',
                'localStorage.setItem', 'sessionStorage.setItem',
                'document.cookie', 'document.write', 'document.writeln',
                'eval', 'Function', 'setTimeout', 'setInterval'
            ]
        }
        
        # Compile regex patterns
        self._compile_test_patterns()
        
        # Initialize Tree-Sitter parser for JavaScript
        self._initialize_parser()
        if self._init_tree_sitter():
            try:
                # Load JavaScript grammar
                self._parser.set_language(self._get_javascript_language())
                logger.debug("Enhanced JavaScript parser initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize JavaScript parser: {e}")
                self._parser = None
        else:
            logger.warning("Tree-Sitter not available for JavaScript parsing")
    
    def _compile_test_patterns(self):
        """Compile regex patterns for test detection."""
        self.compiled_test_patterns = {}
        for test_type, patterns in self.test_patterns.items():
            self.compiled_test_patterns[test_type] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                for pattern in patterns
            ]
    
    def _get_javascript_language(self):
        """Get JavaScript language grammar from tree-sitter-languages."""
        try:
            from tree_sitter_languages import get_language
            # Suppress deprecation warning for now until tree-sitter-languages is updated
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")
                return get_language("javascript")
        except ImportError:
            logger.error("tree-sitter-languages not available for JavaScript")
            return None
        except Exception as e:
            logger.error(f"Failed to load JavaScript language: {e}")
            return None
    
    def analyze_file_context(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze file context to determine if it's a test file, contains console logging, etc."""
        context = {
            'is_test_file': False,
            'test_frameworks': set(),
            'has_console_logging': False,
            'has_sensitive_sinks': False,
            'framework_hints': set(),
            'is_generated': False,
            'module_type': 'unknown'  # 'es6', 'commonjs', 'mixed'
        }
        
        # Check for test patterns
        for test_type, patterns in self.compiled_test_patterns.items():
            for pattern in patterns:
                if pattern.search(content):
                    context['is_test_file'] = True
                    context['test_frameworks'].add(test_type)
        
        # Check for console logging patterns
        for console_func in self.console_patterns['console_functions']:
            if console_func in content:
                context['has_console_logging'] = True
                break
        
        # Check for sensitive sinks
        for sink in self.console_patterns['sensitive_sinks']:
            if sink in content:
                context['has_sensitive_sinks'] = True
                break
        
        # Check for framework hints
        framework_indicators = {
            'react': ['import React', 'from "react"', 'useState', 'useEffect', 'useContext', 'JSX.Element'],
            'vue': ['import Vue', 'new Vue', 'vue-', 'Vue.component', 'Vue.use'],
            'angular': ['@angular', 'import { Component }', 'ngOnInit', 'ngOnDestroy', 'Angular'],
            'node': ['require(', 'module.exports', 'exports.', 'process.env', 'Buffer('],
            'express': ['import express', 'const express', 'app.get', 'app.post', 'app.use'],
            'next': ['import { NextPage }', 'getServerSideProps', 'getStaticProps', 'pages/'],
            'nuxt': ['import { defineNuxtConfig }', 'pages/', 'layouts/', 'components/']
        }
        
        for framework, indicators in framework_indicators.items():
            if any(indicator in content for indicator in indicators):
                context['framework_hints'].add(framework)
        
        # Determine module type
        if 'import ' in content and 'from ' in content:
            context['module_type'] = 'es6'
        elif 'require(' in content and 'module.exports' in content:
            context['module_type'] = 'commonjs'
        elif ('import ' in content and 'require(' in content) or ('export ' in content and 'module.exports' in content):
            context['module_type'] = 'mixed'
        
        # Check for generated code markers
        generated_markers = [
            'auto-generated', 'generated by', '// Generated', '/* Generated */', 
            '@generated', 'DO NOT EDIT', 'This file was generated'
        ]
        if any(marker in content for marker in generated_markers):
            context['is_generated'] = True
        
        return context
    
    def extract_template_literals(self, content: str) -> List[TemplateLiteralExpression]:
        """Extract template literal expressions with embedded variables for PII detection."""
        template_literals = []
        
        # Pattern to match template literals with expressions
        template_pattern = r'`([^`]*(?:\$\{[^}]*\}[^`]*)*)`'
        
        for match in re.finditer(template_pattern, content):
            template_content = match.group(1)
            
            # Extract expressions within ${}
            expression_pattern = r'\$\{([^}]*)\}'
            for expr_match in re.finditer(expression_pattern, template_content):
                expression = expr_match.group(1)
                
                # Parse the expression to extract variable names
                variable_name = self._extract_variable_from_expression(expression)
                
                # Calculate positions
                start_pos = match.start() + template_content.find(expr_match.group(0)) + 2  # +2 for ${
                end_pos = start_pos + len(expr_match.group(0)) - 3  # -3 for ${}
                
                line_num = content[:start_pos].count('\n') + 1
                col_start = start_pos - content.rfind('\n', 0, start_pos) - 1
                col_end = end_pos - content.rfind('\n', 0, end_pos) - 1
                
                # Determine if this might contain sensitive data
                is_sensitive = self._is_sensitive_expression(expression, variable_name)
                
                template_expr = TemplateLiteralExpression(
                    expression=expression,
                    start_line=line_num,
                    start_col=col_start,
                    end_line=line_num,
                    end_col=col_end,
                    variable_name=variable_name,
                    context=self._get_template_literal_context(content, start_pos),
                    is_sensitive=is_sensitive
                )
                template_literals.append(template_expr)
        
        return template_literals
    
    def _extract_variable_from_expression(self, expression: str) -> str:
        """Extract the main variable name from a template literal expression."""
        # Remove common formatting and method calls
        cleaned = re.sub(r'[!:\d]*$', '', expression.strip())
        
        # Handle method calls like variable.method()
        if '.' in cleaned and '(' in cleaned:
            cleaned = cleaned.split('.')[0]
        
        # Handle attribute access like variable.attr
        if '.' in cleaned:
            cleaned = cleaned.split('.')[0]
        
        # Handle ternary operators
        if '?' in cleaned:
            cleaned = cleaned.split('?')[0]
        
        # Handle logical operators
        if '&&' in cleaned:
            cleaned = cleaned.split('&&')[0]
        elif '||' in cleaned:
            cleaned = cleaned.split('||')[0]
        
        return cleaned.strip()
    
    def _is_sensitive_expression(self, expression: str, variable_name: str) -> bool:
        """Determine if a template literal expression might contain sensitive data."""
        sensitive_indicators = [
            'email', 'password', 'secret', 'key', 'token', 'auth',
            'user', 'name', 'address', 'phone', 'ssn', 'credit',
            'account', 'bank', 'routing', 'iban', 'api', 'config'
        ]
        
        # Check variable name
        if any(indicator in variable_name.lower() for indicator in sensitive_indicators):
            return True
        
        # Check expression content
        if any(indicator in expression.lower() for indicator in sensitive_indicators):
            return True
        
        return False
    
    def _get_template_literal_context(self, content: str, position: int) -> str:
        """Get context around a template literal expression."""
        # Look for surrounding context (function, class, etc.)
        lines = content.split('\n')
        line_num = content[:position].count('\n')
        
        if line_num < len(lines):
            line = lines[line_num]
            
            # Check for common patterns
            if 'function ' in line or '=>' in line:
                return 'function_definition'
            elif 'class ' in line:
                return 'class_definition'
            elif '=' in line:
                return 'variable_assignment'
            elif '(' in line and ')' in line:
                return 'function_call'
            elif 'return ' in line:
                return 'return_statement'
        
        return 'unknown'
    
    def extract_console_logging_contexts(self, content: str) -> List[ConsoleLoggingContext]:
        """Extract console logging statements with context analysis."""
        console_contexts = []
        
        # Pattern for console statements
        console_pattern = r'console\.(log|info|warn|error|debug|trace)\s*\(([^)]*)\)'
        
        for match in re.finditer(console_pattern, content, re.IGNORECASE):
            level = match.group(1)
            arguments = match.group(2)
            
            # Parse arguments to detect PII
            pii_types = self._detect_pii_in_console_args(arguments)
            contains_pii = len(pii_types) > 0
            
            line_num = content[:match.start()].count('\n') + 1
            col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
            col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
            
            # Split arguments
            arg_list = [arg.strip() for arg in arguments.split(',') if arg.strip()]
            
            console_context = ConsoleLoggingContext(
                function_name=f"console.{level}",
                level=level,
                arguments=arg_list,
                start_line=line_num,
                start_col=col_start,
                end_line=line_num,
                end_col=col_end,
                contains_pii=contains_pii,
                pii_types=pii_types
            )
            console_contexts.append(console_context)
        
        # Also detect other logging patterns
        other_logging_patterns = [
            (r'console\.(log|info|warn|error|debug|trace)\s*\(([^)]*)\)', 'console'),
            (r'logger\.(log|info|warn|error|debug|trace)\s*\(([^)]*)\)', 'logger'),
            (r'log\.(log|info|warn|error|debug|trace)\s*\(([^)]*)\)', 'log')
        ]
        
        for pattern, logger_type in other_logging_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                level = match.group(1)
                arguments = match.group(2)
                
                pii_types = self._detect_pii_in_console_args(arguments)
                contains_pii = len(pii_types) > 0
                
                line_num = content[:match.start()].count('\n') + 1
                col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
                col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
                
                arg_list = [arg.strip() for arg in arguments.split(',') if arg.strip()]
                
                console_context = ConsoleLoggingContext(
                    function_name=f"{logger_type}.{level}",
                    level=level,
                    arguments=arg_list,
                    start_line=line_num,
                    start_col=col_start,
                    end_line=line_num,
                    end_col=col_end,
                    contains_pii=contains_pii,
                    pii_types=pii_types
                )
                console_contexts.append(console_context)
        
        return console_contexts
    
    def _detect_pii_in_console_args(self, arguments: str) -> List[str]:
        """Detect PII patterns in console logging arguments."""
        pii_types = []
        
        # Common PII patterns
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+1[-\s]?)?\(?[2-9]\d{2}\)?[-\s]?[2-9]\d{2}[-\s]?\d{4}\b',
            'ssn': r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
            'credit_card': r'\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
            'api_key': r'\b[A-Za-z0-9]{32,}\b'
        }
        
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, arguments):
                pii_types.append(pii_type)
        
        return pii_types
    
    def extract_test_framework_contexts(self, content: str) -> List[TestFrameworkContext]:
        """Extract test framework related code contexts."""
        test_contexts = []
        
        # Detect Jest test patterns
        jest_patterns = [
            (r'describe\s*\([\'"`]([^\'"`]+)[\'"`]', 'jest', 'describe'),
            (r'it\s*\([\'"`]([^\'"`]+)[\'"`]', 'jest', 'it'),
            (r'test\s*\([\'"`]([^\'"`]+)[\'"`]', 'jest', 'test'),
            (r'beforeEach\s*\(', 'jest', 'beforeEach'),
            (r'afterEach\s*\(', 'jest', 'afterEach'),
            (r'beforeAll\s*\(', 'jest', 'beforeAll'),
            (r'afterAll\s*\(', 'jest', 'afterAll')
        ]
        
        for pattern, framework, test_type in jest_patterns:
            for match in re.finditer(pattern, content):
                function_name = match.group(1) if match.groups() else test_type
                
                line_num = content[:match.start()].count('\n') + 1
                col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
                col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
                
                # Check if it's a fixture or mock
                is_fixture = 'fixture' in function_name.lower() if function_name else False
                is_mock = any(mock_indicator in content[:match.start()] for mock_indicator in ['jest.mock', 'jest.fn', 'jest.spyOn'])
                
                test_context = TestFrameworkContext(
                    framework=framework,
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
        
        # Detect Mocha test patterns
        mocha_patterns = [
            (r'describe\s*\([\'"`]([^\'"`]+)[\'"`]', 'mocha', 'describe'),
            (r'it\s*\([\'"`]([^\'"`]+)[\'"`]', 'mocha', 'it'),
            (r'before\s*\(', 'mocha', 'before'),
            (r'after\s*\(', 'mocha', 'after'),
            (r'beforeEach\s*\(', 'mocha', 'beforeEach'),
            (r'afterEach\s*\(', 'mocha', 'afterEach')
        ]
        
        for pattern, framework, test_type in mocha_patterns:
            for match in re.finditer(pattern, content):
                function_name = match.group(1) if match.groups() else test_type
                
                line_num = content[:match.start()].count('\n') + 1
                col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
                col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
                
                is_fixture = 'fixture' in function_name.lower() if function_name else False
                is_mock = any(mock_indicator in content[:match.start()] for mock_indicator in ['sinon.', 'chai.', 'proxyquire'])
                
                test_context = TestFrameworkContext(
                    framework=framework,
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
        
        return test_contexts
    
    def extract_es6_modules(self, content: str) -> List[ES6ModuleContext]:
        """Extract ES6 module import/export statements with context analysis."""
        es6_modules = []
        
        # Import patterns
        import_patterns = [
            (r'import\s+([^{}\s]+)\s+from\s+[\'"`]([^\'"`]+)[\'"`]', 'default'),
            (r'import\s+\{([^}]+)\}\s+from\s+[\'"`]([^\'"`]+)[\'"`]', 'named'),
            (r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"`]([^\'"`]+)[\'"`]', 'namespace'),
            (r'import\s+[\'"`]([^\'"`]+)[\'"`]', 'side_effect')
        ]
        
        for pattern, import_type in import_patterns:
            for match in re.finditer(pattern, content):
                if import_type == 'side_effect':
                    module_name = match.group(1)
                    exported_items = []
                elif import_type == 'named':
                    exported_items = [item.strip() for item in match.group(1).split(',')]
                    module_name = match.group(2)
                else:
                    exported_items = [match.group(1)]
                    module_name = match.group(2)
                
                line_num = content[:match.start()].count('\n') + 1
                col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
                col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
                
                # Check if this is a sensitive import
                is_sensitive = self._is_sensitive_module_import(module_name, exported_items)
                
                es6_module = ES6ModuleContext(
                    module_name=module_name,
                    import_type=import_type,
                    exported_items=exported_items,
                    start_line=line_num,
                    start_col=col_start,
                    end_line=line_num,
                    end_col=col_end,
                    is_sensitive_import=is_sensitive
                )
                es6_modules.append(es6_module)
        
        # Export patterns
        export_patterns = [
            (r'export\s+default\s+(\w+)', 'default'),
            (r'export\s+\{([^}]+)\}', 'named'),
            (r'export\s+(\w+)', 'named'),
            (r'export\s+class\s+(\w+)', 'class'),
            (r'export\s+function\s+(\w+)', 'function')
        ]
        
        for pattern, export_type in export_patterns:
            for match in re.finditer(pattern, content):
                if export_type == 'named' and '{' in match.group(0):
                    exported_items = [item.strip() for item in match.group(1).split(',')]
                else:
                    exported_items = [match.group(1)]
                
                line_num = content[:match.start()].count('\n') + 1
                col_start = match.start() - content.rfind('\n', 0, match.start()) - 1
                col_end = match.end() - content.rfind('\n', 0, match.end()) - 1
                
                es6_module = ES6ModuleContext(
                    module_name='current_module',
                    import_type=export_type,
                    exported_items=exported_items,
                    start_line=line_num,
                    start_col=col_start,
                    end_line=line_num,
                    end_col=col_end,
                    is_sensitive_import=False
                )
                es6_modules.append(es6_module)
        
        return es6_modules
    
    def _is_sensitive_module_import(self, module_name: str, exported_items: List[str]) -> bool:
        """Determine if a module import might contain sensitive functionality."""
        sensitive_modules = [
            'crypto', 'bcrypt', 'jsonwebtoken', 'passport', 'oauth',
            'stripe', 'paypal', 'braintree', 'square',
            'aws-sdk', 'google-cloud', 'azure', 'firebase',
            'database', 'db', 'sql', 'mongodb', 'redis'
        ]
        
        sensitive_exports = [
            'password', 'secret', 'key', 'token', 'auth', 'encrypt', 'decrypt',
            'hash', 'sign', 'verify', 'login', 'register', 'authenticate'
        ]
        
        # Check module name
        if any(sensitive in module_name.lower() for sensitive in sensitive_modules):
            return True
        
        # Check exported items
        if any(sensitive in export.lower() for sensitive in sensitive_exports for export in exported_items):
            return True
        
        return False
    
    def extract_strings(self, file_path: Path, content: str) -> List[StringLiteral]:
        """Enhanced string extraction with template literal and context analysis."""
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
            
            # Also extract template literals that might not be caught by Tree-Sitter
            template_literals = self.extract_template_literals(content)
            for template_lit in template_literals:
                # Convert template literal expressions to string literals for analysis
                string_literal = StringLiteral(
                    value=template_lit.expression,
                    raw_value=f"${{{template_lit.expression}}}",
                    start_line=template_lit.start_line,
                    start_col=template_lit.start_col,
                    end_line=template_lit.end_line,
                    end_col=template_lit.end_col,
                    context=template_lit.context,
                    parent_node_type="template_literal_expression"
                )
                strings.append(string_literal)
            
            return strings
            
        except Exception as e:
            logger.error(f"Error extracting strings from JavaScript file {file_path}: {e}")
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
                    value = self._process_javascript_string(string_text)
                    
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
    
    def _process_javascript_string(self, string_text: str) -> str:
        """Process JavaScript string literal, handling escape sequences."""
        if not string_text:
            return ""
        
        # Remove surrounding quotes
        if string_text.startswith('"') and string_text.endswith('"'):
            string_text = string_text[1:-1]
        elif string_text.startswith("'") and string_text.endswith("'"):
            string_text = string_text[1:-1]
        elif string_text.startswith('`') and string_text.endswith('`'):
            string_text = string_text[1:-1]
        
        # Handle common JavaScript escape sequences
        escape_map = {
            '\\n': '\n',
            '\\t': '\t',
            '\\r': '\r',
            '\\b': '\b',
            '\\f': '\f',
            '\\"': '"',
            "\\'": "'",
            '\\\\': '\\',
            '\\`': '`'
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
                if parent.type == 'variable_declaration':
                    return 'variable_declaration'
                elif parent.type == 'function_declaration':
                    return 'function_body'
                elif parent.type == 'class_declaration':
                    return 'class_body'
                elif parent.type == 'call_expression':
                    return 'function_call'
                elif parent.type == 'assignment_expression':
                    return 'assignment'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def extract_comments(self, file_path: Path, content: str) -> List[Comment]:
        """Extract all comments from JavaScript source code."""
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
            logger.error(f"Error extracting comments from JavaScript file {file_path}: {e}")
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
        """Determine the type of JavaScript comment."""
        if comment_text.startswith('//'):
            return 'line'
        elif comment_text.startswith('/*') and comment_text.endswith('*/'):
            return 'block'
        else:
            return 'unknown'
    
    def extract_imports(self, file_path: Path, content: str) -> List[ImportStatement]:
        """Extract all import statements from JavaScript source code."""
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
            logger.error(f"Error extracting imports from JavaScript file {file_path}: {e}")
            return []
    
    def _extract_import_nodes(self, node, imports: List[ImportStatement], content: str):
        """Recursively extract import statement nodes."""
        try:
            if node.type == 'import_statement':
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
                        import_type=import_parts.get('type', 'es6_import')
                    )
                    imports.append(import_stmt)
            
            # Recursively process children
            for child in node.children:
                self._extract_import_nodes(child, imports, content)
                
        except Exception as e:
            logger.debug(f"Error extracting import node: {e}")
    
    def _parse_import_statement(self, import_text: str) -> Dict[str, str]:
        """Parse JavaScript import statement to extract components."""
        try:
            # Remove 'import' keyword
            if import_text.startswith('import '):
                import_text = import_text[7:]
            
            # Handle default imports: import x from 'y'
            if ' from ' in import_text:
                import_part, module_part = import_text.split(' from ', 1)
                module = module_part.strip().strip("'\"`")
                
                # Handle default import
                if import_part.strip() and not import_part.startswith('{'):
                    name = import_part.strip()
                    alias = ''
                # Handle named imports: import {x} from 'y'
                elif import_part.startswith('{') and import_part.endswith('}'):
                    named_imports = import_part[1:-1].strip()
                    if ' as ' in named_imports:
                        name, alias = named_imports.split(' as ', 1)
                        name = name.strip()
                        alias = alias.strip()
                    else:
                        name = named_imports.strip()
                        alias = ''
                else:
                    name = ''
                    alias = ''
                
                return {
                    'module': module,
                    'name': name,
                    'alias': alias,
                    'type': 'es6_import'
                }
            
            # Handle require statements: const x = require('y')
            elif 'require(' in import_text:
                # This is a simplified parser for require statements
                module = import_text.strip().strip("'\"`")
                return {
                    'module': module,
                    'name': '',
                    'alias': '',
                    'type': 'require'
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
        """Extract variable declarations from JavaScript source code."""
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
            logger.error(f"Error extracting variables from JavaScript file {file_path}: {e}")
            return []
    
    def _extract_variable_nodes(self, node, variables: List[VariableDeclaration], content: str):
        """Recursively extract variable declaration nodes."""
        try:
            if node.type == 'variable_declaration':
                # Look for declarators
                for child in node.children:
                    if child.type == 'variable_declarator':
                        # Get variable name
                        for grandchild in child.children:
                            if grandchild.type == 'identifier':
                                var_name = self._get_node_text(grandchild, content)
                                if var_name:
                                    # Get variable type (let, const, var)
                                    var_type = ""
                                    for sibling in node.children:
                                        if sibling.type in ['let', 'const', 'var']:
                                            var_type = sibling.type
                                            break
                                    
                                    variable = VariableDeclaration(
                                        name=var_name,
                                        var_type=var_type,
                                        modifiers=[],
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
                if parent.type == 'function_declaration':
                    return 'function_local'
                elif parent.type == 'class_declaration':
                    return 'class_attribute'
                elif parent.type == 'program':
                    return 'module_global'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def extract_functions(self, file_path: Path, content: str) -> List[FunctionDefinition]:
        """Extract function definitions from JavaScript source code."""
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
            logger.error(f"Error extracting functions from JavaScript file {file_path}: {e}")
            return []
    
    def _extract_function_nodes(self, node, functions: List[FunctionDefinition], content: str):
        """Recursively extract function definition nodes."""
        try:
            if node.type in ['function_declaration', 'arrow_function', 'method_definition']:
                # Extract function information
                function_name = ""
                parameters = []
                is_async = False
                is_generator = False
                
                # Get function name
                for child in node.children:
                    if child.type == 'identifier':
                        function_name = self._get_node_text(child, content)
                    elif child.type == 'formal_parameters':
                        parameters = self._extract_parameters(child, content)
                
                # Check if async or generator
                is_async = self._is_async_node(node)
                is_generator = self._is_generator_node(node)
                
                if function_name:
                    function = FunctionDefinition(
                        name=function_name,
                        return_type="",  # JavaScript doesn't have explicit return types
                        parameters=parameters,
                        modifiers=[],
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
        """Extract parameter names from formal parameters node."""
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
        """Extract class definitions from JavaScript source code."""
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
            logger.error(f"Error extracting classes from JavaScript file {file_path}: {e}")
            return []
    
    def _extract_class_nodes(self, node, classes: List[ClassDefinition], content: str):
        """Recursively extract class definition nodes."""
        try:
            if node.type == 'class_declaration':
                # Extract class information
                class_name = ""
                superclass = ""
                
                # Get class name
                for child in node.children:
                    if child.type == 'identifier':
                        class_name = self._get_node_text(child, content)
                    elif child.type == 'class_heritage':
                        # Extract superclass
                        for heritage_child in child.children:
                            if heritage_child.type == 'identifier':
                                superclass = self._get_node_text(heritage_child, content)
                                break
                
                if class_name:
                    class_def = ClassDefinition(
                        name=class_name,
                        modifiers=[],
                        superclass=superclass,
                        interfaces=[],
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
        """Get information about the JavaScript parser capabilities."""
        return {
            'language': 'javascript',
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
        """Get comprehensive analysis including context, template literals, console logging, and test detection."""
        analysis = {
            'file_context': self.analyze_file_context(content, file_path),
            'template_literals': self.extract_template_literals(content),
            'console_logging_contexts': self.extract_console_logging_contexts(content),
            'test_framework_contexts': self.extract_test_framework_contexts(content),
            'es6_modules': self.extract_es6_modules(content),
            'strings': self.extract_strings(file_path, content),
            'comments': self.extract_comments(file_path, content),
            'imports': self.extract_imports(file_path, content),
            'functions': self.extract_functions(file_path, content),
            'classes': self.extract_classes(file_path, content)
        }
        
        return analysis


class TypeScriptParser(JavaScriptParser):
    """TypeScript language parser extending JavaScript parser."""
    
    def __init__(self):
        super().__init__()
        self.language_name = "typescript"
        self.file_extensions = ['.ts', '.tsx']
        
        # Initialize Tree-Sitter parser for TypeScript
        if self._init_tree_sitter():
            try:
                # Load TypeScript grammar
                self._parser.set_language(self._get_typescript_language())
                logger.debug("TypeScript parser initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize TypeScript parser: {e}")
                self._parser = None
        else:
            logger.warning("Tree-Sitter not available for TypeScript parsing")
    
    def _get_typescript_language(self):
        """Get TypeScript language grammar from tree-sitter-languages."""
        try:
            from tree_sitter_languages import get_language
            # Suppress deprecation warning for now until tree-sitter-languages is updated
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")
                return get_language("typescript")
        except ImportError:
            logger.error("tree-sitter-languages not available for TypeScript")
            return None
        except Exception as e:
            logger.error(f"Failed to load TypeScript language: {e}")
            return None
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get information about the TypeScript parser capabilities."""
        info = super().get_parser_info()
        info['language'] = 'typescript'
        info['capabilities'].extend([
            'type_annotation_analysis',
            'interface_analysis',
            'generic_type_analysis'
        ])
        return info

    def get_enhanced_analysis(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive analysis including context, template literals, console logging, and test detection."""
        analysis = {
            'file_context': self.analyze_file_context(content, file_path),
            'template_literals': self.extract_template_literals(content),
            'console_logging_contexts': self.extract_console_logging_contexts(content),
            'test_framework_contexts': self.extract_test_framework_contexts(content),
            'es6_modules': self.extract_es6_modules(content),
            'strings': self.extract_strings(file_path, content),
            'comments': self.extract_comments(file_path, content),
            'imports': self.extract_imports(file_path, content),
            'functions': self.extract_functions(file_path, content),
            'classes': self.extract_classes(file_path, content)
        }
        
        return analysis