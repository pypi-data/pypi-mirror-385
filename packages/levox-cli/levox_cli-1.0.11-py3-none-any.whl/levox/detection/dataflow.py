"""
Level 3: Enterprise-grade dataflow/taint analysis for PII detection with 
comprehensive source-to-sink tracking, multi-hop flows, and production reliability.
"""

import ast
import re
import time
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import (
    List, Dict, Any, Optional, Set, Tuple, NamedTuple, Union, Iterator,
    DefaultDict, Callable, Type
)
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
from abc import ABC, abstractmethod

from ..core.config import Config, DetectionPattern, RiskLevel
from ..core.exceptions import DetectionError, ParserError
from ..models.detection_result import DetectionMatch
from ..parsers import get_parser, is_supported_file


class FlowDirection(Enum):
    """Direction of data flow in taint analysis."""
    FORWARD = "forward"
    BACKWARD = "backward"


class ScopeType(Enum):
    """Types of variable scopes in code."""
    GLOBAL = "global"
    FUNCTION = "function"
    CLASS = "class"
    BLOCK = "block"


@dataclass(frozen=True)
class Variable:
    """Represents a variable in the code with scope information."""
    name: str
    scope: str
    line: int
    column: int
    scope_type: ScopeType = ScopeType.GLOBAL


@dataclass
class TaintSource:
    """Represents a source of potentially tainted data with enhanced metadata."""
    name: str
    line: int
    column: int
    source_type: str  # 'user_input', 'file_read', 'network', 'env_var', 'db_query'
    confidence: float
    variable: Optional[Variable] = None
    context: Dict[str, Any] = field(default_factory=dict)
    pii_indicators: Set[str] = field(default_factory=set)


@dataclass
class TaintSink:
    """Represents a sink where tainted data might be leaked with detailed context."""
    name: str
    line: int
    column: int
    sink_type: str  # 'logging', 'file_write', 'network_send', 'console_output'
    arguments: List[str]
    argument_positions: List[int] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"


@dataclass
class FlowNode:
    """Represents a node in the dataflow graph."""
    variable: Variable
    operation: str  # 'def', 'use', 'modify'
    line: int
    context: str
    confidence: float = 1.0
    predecessors: Set['FlowNode'] = field(default_factory=set)
    successors: Set['FlowNode'] = field(default_factory=set)


@dataclass
class TaintFlow:
    """Represents a complete flow of tainted data from source to sink."""
    source: TaintSource
    sink: TaintSink
    path: List[FlowNode]
    confidence: float
    flow_distance: int
    risk_factors: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LanguageAnalyzer(ABC):
    """Abstract base class for language-specific taint analysis."""
    
    def __init__(self, config: Config):
        """Initialize the language analyzer with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"levox.dataflow.{self.__class__.__name__.lower()}")
        
        # Common taint source patterns across languages
        self.common_taint_sources = {
            'user_input': {
                'input': 0.95, 'prompt': 0.95, 'getpass': 0.95,
                'argv': 0.85, 'args': 0.80, 'parameters': 0.75
            },
            'file_read': {
                'read': 0.70, 'load': 0.75, 'parse': 0.70,
                'open': 0.70, 'file': 0.65
            },
            'network': {
                'get': 0.80, 'post': 0.85, 'request': 0.80,
                'fetch': 0.80, 'urlopen': 0.80, 'recv': 0.90
            },
            'env_var': {
                'env': 0.75, 'environment': 0.75, 'config': 0.70,
                'settings': 0.65, 'getenv': 0.75
            },
            'db_query': {
                'query': 0.80, 'execute': 0.85, 'fetch': 0.90,
                'find': 0.75, 'select': 0.80
            }
        }
        
        # Common taint sink patterns across languages
        self.common_taint_sinks = {
            'logging': {
                'log': 'low', 'print': 'medium', 'console': 'medium',
                'debug': 'low', 'info': 'low', 'error': 'medium'
            },
            'file_write': {
                'write': 'high', 'save': 'high', 'dump': 'high',
                'output': 'high', 'export': 'high'
            },
            'network_send': {
                'post': 'high', 'put': 'high', 'send': 'high',
                'upload': 'high', 'transmit': 'high'
            },
            'console_output': {
                'print': 'medium', 'echo': 'medium', 'display': 'medium',
                'show': 'medium', 'output': 'medium'
            }
        }
    
    @abstractmethod
    def parse_ast(self, content: str, file_path: Path) -> Any:
        """Parse content into AST for the specific language.
        
        Args:
            content: Source code content as string
            file_path: Path to the source file
            
        Returns:
            Parsed AST representation (language-specific)
            
        Raises:
            ParserError: If parsing fails
        """
        pass
    
    @abstractmethod
    def extract_variables(self, ast_node: Any) -> List[Variable]:
        """Extract variables with comprehensive scope information.
        
        Args:
            ast_node: Parsed AST node
            
        Returns:
            List of variables with scope, line, and column information
        """
        pass
    
    @abstractmethod
    def identify_sources(self, ast_node: Any) -> List[TaintSource]:
        """Identify taint sources in the AST.
        
        Args:
            ast_node: Parsed AST node
            
        Returns:
            List of identified taint sources with confidence scores
        """
        pass
    
    @abstractmethod
    def identify_sinks(self, ast_node: Any) -> List[TaintSink]:
        """Identify taint sinks in the AST.
        
        Args:
            ast_node: Parsed AST node
            
        Returns:
            List of identified taint sinks with severity levels
        """
        pass
    
    @abstractmethod
    def build_def_use_chains(self, ast_node: Any, variables: List[Variable]) -> Dict[Variable, List[FlowNode]]:
        """Build definition-use chains for variables.
        
        Args:
            ast_node: Parsed AST node
            variables: List of variables to analyze
            
        Returns:
            Dictionary mapping variables to their definition-use chains
        """
        pass
    
    def get_language_name(self) -> str:
        """Get the name of the language this analyzer supports.
        
        Returns:
            Language name as string
        """
        return self.__class__.__name__.replace('Analyzer', '').lower()
    
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if this analyzer supports the given file type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file type is supported
        """
        supported_extensions = self.get_supported_extensions()
        return file_path.suffix.lower() in supported_extensions
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of file extensions supported by this analyzer.
        
        Returns:
            List of supported file extensions
        """
        raise NotImplementedError("Subclasses must implement get_supported_extensions")
    
    def validate_content(self, content: str) -> bool:
        """Validate that the content can be parsed by this analyzer.
        
        Args:
            content: Source code content
            
        Returns:
            True if content appears valid for this language
        """
        try:
            # Basic validation - check if content is not empty and has reasonable length
            if not content or not content.strip():
                return False
            
            # Check for language-specific indicators
            return self._has_language_indicators(content)
        except Exception:
            return False
    
    def _has_language_indicators(self, content: str) -> bool:
        """Check if content has indicators of the target language.
        
        Args:
            content: Source code content
            
        Returns:
            True if content appears to be in the target language
        """
        raise NotImplementedError("Subclasses must implement _has_language_indicators")
    
    def get_analysis_metadata(self) -> Dict[str, Any]:
        """Get metadata about this analyzer's capabilities.
        
        Returns:
            Dictionary with analyzer metadata
        """
        return {
            'language': self.get_language_name(),
            'supported_extensions': self.get_supported_extensions(),
            'taint_source_types': list(self.common_taint_sources.keys()),
            'taint_sink_types': list(self.common_taint_sinks.keys()),
            'analyzer_class': self.__class__.__name__,
            'config_loaded': self.config is not None
        }
    
    def preprocess_content(self, content: str) -> str:
        """Preprocess content before parsing (e.g., remove comments, normalize).
        
        Args:
            content: Raw source code content
            
        Returns:
            Preprocessed content ready for parsing
        """
        # Default implementation - no preprocessing
        return content
    
    def postprocess_results(self, results: List[DetectionMatch]) -> List[DetectionMatch]:
        """Postprocess analysis results (e.g., filter, sort, enhance).
        
        Args:
            results: Raw analysis results
            
        Returns:
            Postprocessed results
        """
        # Default implementation - no postprocessing
        return results
    
    def get_taint_source_patterns(self) -> Dict[str, Dict[str, float]]:
        """Get taint source patterns for this language.
        
        Returns:
            Dictionary of taint source patterns with confidence scores
        """
        return self.taint_sources if hasattr(self, 'taint_sources') else self.common_taint_sources
    
    def get_taint_sink_patterns(self) -> Dict[str, Dict[str, str]]:
        """Get taint sink patterns for this language.
        
        Returns:
            Dictionary of taint sink patterns with severity levels
        """
        return self.taint_sinks if hasattr(self, 'taint_sinks') else self.common_taint_sinks
    
    def validate_taint_flow(self, source: TaintSource, sink: TaintSink) -> bool:
        """Validate if a taint flow from source to sink is valid.
        
        Args:
            source: Taint source
            sink: Taint sink
            
        Returns:
            True if the flow is valid
        """
        # Basic validation - check if source and sink are in the same file
        if hasattr(source, 'file_path') and hasattr(sink, 'file_path'):
            if source.file_path != sink.file_path:
                return False
        
        # Check if source line comes before sink line
        if source.line > sink.line:
            return False
        
        return True
    
    def get_analysis_complexity(self) -> str:
        """Get the complexity level of this analyzer.
        
        Returns:
            Complexity level ('basic', 'intermediate', 'advanced')
        """
        if hasattr(self, 'parse_ast') and 'ast.parse' in str(self.parse_ast.__code__):
            return 'advanced'
        elif hasattr(self, 'extract_variables') and 'regex' in str(self.extract_variables.__code__):
            return 'intermediate'
        else:
            return 'basic'


class PythonAnalyzer(LanguageAnalyzer):
    """Python-specific taint analysis using AST."""
    
    def __init__(self, config: Config):
        super().__init__(config)
        
        # Python-specific taint sources with confidence weights
        self.taint_sources = {
            'user_input': {
                'input': 0.95, 'raw_input': 0.95, 'sys.argv': 0.85,
                'click.prompt': 0.90, 'getpass.getpass': 0.95,
                'argparse.parse_args': 0.80
            },
            'file_read': {
                'open': 0.70, 'pathlib.Path.read_text': 0.70,
                'json.load': 0.75, 'yaml.load': 0.80, 'pickle.load': 0.85,
                'csv.reader': 0.65, 'configparser.read': 0.75
            },
            'network': {
                'requests.get': 0.80, 'requests.post': 0.85, 'urllib.request.urlopen': 0.80,
                'socket.recv': 0.90, 'http.client.getresponse': 0.80,
                'aiohttp.get': 0.80, 'httpx.get': 0.80
            },
            'env_var': {
                'os.environ.get': 0.75, 'os.getenv': 0.75,
                'config.get': 0.70, 'settings': 0.65
            },
            'db_query': {
                'cursor.execute': 0.85, 'cursor.fetchone': 0.90, 'cursor.fetchall': 0.90,
                'query': 0.80, 'session.execute': 0.85, 'model.objects.get': 0.80
            }
        }
        
        # Python-specific taint sinks with severity levels
        self.taint_sinks = {
            'logging': {
                'print': 'medium', 'logging.info': 'low', 'logging.debug': 'low',
                'logging.error': 'medium', 'logging.warning': 'medium',
                'logger.info': 'low', 'logger.error': 'medium'
            },
            'file_write': {
                'write': 'high', 'writelines': 'high', 'json.dump': 'high',
                'yaml.dump': 'high', 'pickle.dump': 'high', 'csv.writer': 'medium'
            },
            'network_send': {
                'requests.post': 'high', 'requests.put': 'high',
                'socket.send': 'high', 'urllib.request.urlopen': 'high'
            },
            'console_output': {
                'print': 'medium', 'pprint.pprint': 'medium', 'sys.stdout.write': 'medium'
            }
        }
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of file extensions supported by this analyzer."""
        return ['.py', '.pyw', '.pyi']
    
    def _has_language_indicators(self, content: str) -> bool:
        """Check if content has Python language indicators."""
        python_indicators = [
            'def ', 'class ', 'import ', 'from ', 'if __name__',
            'print(', 'def __init__', 'self.', 'return ',
            'try:', 'except:', 'with ', 'as ', 'lambda '
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in python_indicators)
    
    def parse_ast(self, content: str, file_path: Path) -> ast.AST:
        """Parse Python content into AST."""
        try:
            # Normalize modern syntax (e.g., PEP 695 generics) for Python 3.11 compatibility
            try:
                from ..utils.python_syntax import normalize_modern_syntax
                content = normalize_modern_syntax(content)
            except Exception:
                pass
            return ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            raise ParserError.corrupted_file(
                str(file_path), 
                f"Python syntax error: {e.msg} at line {e.lineno}"
            )
        except Exception as e:
            raise ParserError(
                f"Failed to parse Python file: {e}",
                details={'file_path': str(file_path), 'error_type': type(e).__name__}
            )
    
    def extract_variables(self, ast_node: ast.AST) -> List[Variable]:
        """Extract variables with comprehensive scope information."""
        variables = []
        scope_stack = [("global", ScopeType.GLOBAL)]
        
        class VariableVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                scope_stack.append((node.name, ScopeType.FUNCTION))
                
                # Add function parameters
                for arg in node.args.args:
                    variables.append(Variable(
                        name=arg.arg,
                        scope=f"{'.'.join(s[0] for s in scope_stack)}.{node.name}",
                        line=getattr(arg, 'lineno', node.lineno),
                        column=getattr(arg, 'col_offset', 0),
                        scope_type=ScopeType.FUNCTION
                    ))
                
                self.generic_visit(node)
                scope_stack.pop()
            
            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                scope_stack.append((node.name, ScopeType.CLASS))
                self.generic_visit(node)
                scope_stack.pop()
            
            def visit_Assign(self, node: ast.Assign) -> None:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        current_scope = '.'.join(s[0] for s in scope_stack)
                        variables.append(Variable(
                            name=target.id,
                            scope=current_scope,
                            line=node.lineno,
                            column=node.col_offset,
                            scope_type=scope_stack[-1][1]
                        ))
                self.generic_visit(node)
            
            def visit_AugAssign(self, node: ast.AugAssign) -> None:
                if isinstance(node.target, ast.Name):
                    current_scope = '.'.join(s[0] for s in scope_stack)
                    variables.append(Variable(
                        name=node.target.id,
                        scope=current_scope,
                        line=node.lineno,
                        column=node.col_offset,
                        scope_type=scope_stack[-1][1]
                    ))
                self.generic_visit(node)
        
        visitor = VariableVisitor()
        visitor.visit(ast_node)
        return variables
    
    def identify_sources(self, ast_node: ast.AST) -> List[TaintSource]:
        """Identify taint sources with enhanced context detection."""
        sources = []
        
        class SourceVisitor(ast.NodeVisitor):
            def __init__(self, analyzer_instance):
                super().__init__()
                self.analyzer = analyzer_instance
            
            def visit_Assign(self, node: ast.Assign) -> None:
                # Handle function call assignments (existing logic)
                if isinstance(node.value, ast.Call):
                    func_name = self._get_function_name(node.value)
                    source_info = self._get_source_info(func_name)
                    
                    if source_info:
                        source_type, base_confidence = source_info
                        pii_indicators = self._detect_pii_context(node)
                        
                        # Adjust confidence based on context
                        confidence = self._adjust_confidence(base_confidence, pii_indicators, node)
                        
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                sources.append(TaintSource(
                                    name=target.id,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    source_type=source_type,
                                    confidence=confidence,
                                    variable=Variable(
                                        name=target.id,
                                        scope="global",  # Simplified for now
                                        line=node.lineno,
                                        column=node.col_offset
                                    ),
                                    context={
                                        'function_call': func_name,
                                        'arguments': [ast.unparse(arg) for arg in node.value.args],
                                        'line_content': self._get_line_content(node.lineno)
                                    },
                                    pii_indicators=pii_indicators
                                ))
                
                # Handle simple assignments with PII content
                elif isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    # Check if the string contains PII patterns
                    pii_indicators = self._detect_pii_context(node)
                    
                    if pii_indicators:
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                sources.append(TaintSource(
                                    name=target.id,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    source_type="hardcoded_pii",
                                    confidence=0.8,
                                    variable=Variable(
                                        name=target.id,
                                        scope="global",
                                        line=node.lineno,
                                        column=node.col_offset
                                    ),
                                    context={
                                        'assignment_type': 'string_constant',
                                        'value_preview': node.value.value[:50],
                                        'line_content': self._get_line_content(node.lineno)
                                    },
                                    pii_indicators=pii_indicators
                                ))
                
                self.generic_visit(node)
            
            def _get_function_name(self, call_node: ast.Call) -> str:
                """Extract function name from call node."""
                if isinstance(call_node.func, ast.Name):
                    return call_node.func.id
                elif isinstance(call_node.func, ast.Attribute):
                    return f"{ast.unparse(call_node.func.value)}.{call_node.func.attr}"
                return "unknown"
            
            def _get_source_info(self, func_name: str) -> Optional[Tuple[str, float]]:
                """Get source type and confidence for function."""
                for source_type, funcs in self.analyzer.taint_sources.items():
                    if func_name in funcs:
                        return source_type, funcs[func_name]
                
                # Return default source info instead of None
                if any(keyword in func_name.lower() for keyword in ['input', 'read', 'get', 'fetch']):
                    return "user_input", 0.7
                elif any(keyword in func_name.lower() for keyword in ['config', 'env', 'setting']):
                    return "configuration", 0.6
                elif any(keyword in func_name.lower() for keyword in ['file', 'load', 'parse']):
                    return "file_input", 0.8
                
                return None
            
            def _detect_pii_context(self, node: ast.AST) -> Set[str]:
                """Detect PII-related context indicators."""
                indicators = set()
                content = ast.unparse(node).lower()
                
                pii_keywords = {
                    'email', 'password', 'ssn', 'social_security', 'credit_card',
                    'phone', 'address', 'name', 'personal', 'private', 'secret',
                    'token', 'key', 'credential', 'auth', 'user', 'account'
                }
                
                for keyword in pii_keywords:
                    if keyword in content:
                        indicators.add(keyword)
                
                return indicators
            
            def _adjust_confidence(self, base_confidence: float, 
                                 pii_indicators: Set[str], node: ast.AST) -> float:
                """Adjust confidence based on context."""
                confidence = base_confidence
                
                # Increase confidence if PII indicators are present
                if pii_indicators:
                    confidence = min(1.0, confidence * (1.0 + len(pii_indicators) * 0.1))
                
                # Decrease confidence for indirect assignments
                if isinstance(node.value, ast.Call) and len(node.value.args) == 0:
                    confidence *= 0.9
                
                return confidence
            
            def _get_line_content(self, line_num: int) -> str:
                """Get the content of a specific line."""
                try:
                    # Try to get actual line content from the source
                    if hasattr(self.analyzer, 'source_lines') and line_num <= len(self.analyzer.source_lines):
                        return self.analyzer.source_lines[line_num - 1]
                    else:
                        # Fallback to line number if source not available
                        return f"line_{line_num}"
                except (IndexError, AttributeError):
                    return f"line_{line_num}"
        
        visitor = SourceVisitor(self)
        visitor.visit(ast_node)
        return sources
    
    def identify_sinks(self, ast_node: ast.AST) -> List[TaintSink]:
        """Identify taint sinks with comprehensive argument analysis."""
        sinks = []
        
        class SinkVisitor(ast.NodeVisitor):
            def __init__(self, analyzer_instance):
                super().__init__()
                self.analyzer = analyzer_instance
            
            def visit_Call(self, node: ast.Call) -> None:
                func_name = self._get_function_name(node)
                sink_info = self._get_sink_info(func_name)
                
                if sink_info:
                    sink_type, severity = sink_info
                    arguments, positions = self._extract_arguments(node)
                    
                    sinks.append(TaintSink(
                        name=func_name,
                        line=node.lineno,
                        column=node.col_offset,
                        sink_type=sink_type,
                        arguments=arguments,
                        argument_positions=positions,
                        context={
                            'function_call': func_name,
                            'total_args': len(node.args),
                            'has_keywords': len(node.keywords) > 0
                        },
                        severity=severity
                    ))
                
                self.generic_visit(node)
            
            def _get_function_name(self, call_node: ast.Call) -> str:
                """Extract function name from call node."""
                if isinstance(call_node.func, ast.Name):
                    return call_node.func.id
                elif isinstance(call_node.func, ast.Attribute):
                    return f"{ast.unparse(call_node.func.value)}.{call_node.func.attr}"
                return "unknown"
            
            def _get_sink_info(self, func_name: str) -> Optional[Tuple[str, str]]:
                """Get sink type and severity for function."""
                for sink_type, funcs in self.analyzer.taint_sinks.items():
                    if func_name in funcs:
                        return sink_type, funcs[func_name]
                
                # Return default sink info instead of None
                if any(keyword in func_name.lower() for keyword in ['print', 'log', 'debug', 'info']):
                    return "logging", "low"
                elif any(keyword in func_name.lower() for keyword in ['write', 'save', 'store', 'insert']):
                    return "data_storage", "medium"
                elif any(keyword in func_name.lower() for keyword in ['send', 'post', 'request', 'http']):
                    return "network", "high"
                elif any(keyword in func_name.lower() for keyword in ['exec', 'eval', 'system', 'shell']):
                    return "code_execution", "critical"
                
                return None
            
            def _extract_arguments(self, call_node: ast.Call) -> Tuple[List[str], List[int]]:
                """Extract arguments and their positions."""
                arguments = []
                positions = []
                
                for i, arg in enumerate(call_node.args):
                    arg_str = ast.unparse(arg)
                    arguments.append(arg_str)
                    positions.append(i)
                
                return arguments, positions
        
        visitor = SinkVisitor(self)
        visitor.visit(ast_node)
        return sinks
    
    def build_def_use_chains(self, ast_node: ast.AST, variables: List[Variable]) -> Dict[Variable, List[FlowNode]]:
        """Build comprehensive definition-use chains."""
        def_use_chains: Dict[Variable, List[FlowNode]] = defaultdict(list)
        variable_map = {(var.name, var.scope): var for var in variables}
        
        class DefUseVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_scope = "global"
            
            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                old_scope = self.current_scope
                self.current_scope = f"{self.current_scope}.{node.name}"
                self.generic_visit(node)
                self.current_scope = old_scope
            
            def visit_Assign(self, node: ast.Assign) -> None:
                # Handle definitions
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_key = (target.id, self.current_scope)
                        if var_key in variable_map:
                            var = variable_map[var_key]
                            flow_node = FlowNode(
                                variable=var,
                                operation='def',
                                line=node.lineno,
                                context=ast.unparse(node)
                            )
                            def_use_chains[var].append(flow_node)
                
                # Handle uses in the value
                self._visit_uses_in_node(node.value, def_use_chains, variable_map)
                self.generic_visit(node)
            
            def visit_Name(self, node: ast.Name) -> None:
                if isinstance(node.ctx, ast.Load):
                    var_key = (node.id, self.current_scope)
                    if var_key in variable_map:
                        var = variable_map[var_key]
                        flow_node = FlowNode(
                            variable=var,
                            operation='use',
                            line=node.lineno,
                            context=f"use of {node.id}"
                        )
                        def_use_chains[var].append(flow_node)
            
            def _visit_uses_in_node(self, node: ast.AST, chains: Dict[Variable, List[FlowNode]], 
                                  var_map: Dict[Tuple[str, str], Variable]) -> None:
                """Visit uses within a node."""
                for child in ast.walk(node):
                    if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                        var_key = (child.id, self.current_scope)
                        if var_key in var_map:
                            var = var_map[var_key]
                            flow_node = FlowNode(
                                variable=var,
                                operation='use',
                                line=child.lineno,
                                context=f"use in assignment"
                            )
                            chains[var].append(flow_node)
        
        visitor = DefUseVisitor()
        visitor.visit(ast_node)
        return def_use_chains


class JavaScriptAnalyzer(LanguageAnalyzer):
    """JavaScript-specific taint analysis using regex patterns (simplified)."""
    
    def __init__(self, config: Config):
        super().__init__(config)
        
        # JavaScript taint sources
        self.taint_sources = {
            'user_input': {
                'prompt': 0.95, 'process.argv': 0.85, 'document.getElementById': 0.80,
                'document.querySelector': 0.75, 'window.location': 0.80
            },
            'file_read': {
                'fs.readFile': 0.75, 'fs.readFileSync': 0.75, 'require': 0.70
            },
            'network': {
                'fetch': 0.80, 'XMLHttpRequest': 0.80, 'axios.get': 0.80, 'axios.post': 0.85
            },
            'env_var': {
                'process.env': 0.75, 'config.get': 0.70
            },
            'db_query': {
                'query': 0.80, 'execute': 0.85, 'find': 0.75, 'findOne': 0.80
            }
        }
        
        # JavaScript taint sinks
        self.taint_sinks = {
            'logging': {
                'console.log': 'medium', 'console.info': 'low', 'console.error': 'medium',
                'console.debug': 'low', 'console.warn': 'medium'
            },
            'file_write': {
                'fs.writeFile': 'high', 'fs.writeFileSync': 'high'
            },
            'network_send': {
                'fetch': 'high', 'XMLHttpRequest.send': 'high', 'axios.post': 'high'
            },
            'console_output': {
                'console.log': 'medium', 'alert': 'medium', 'document.write': 'high'
            }
        }
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of file extensions supported by this analyzer."""
        return ['.js', '.jsx', '.mjs', '.ts', '.tsx']
    
    def _has_language_indicators(self, content: str) -> bool:
        """Check if content has JavaScript/TypeScript language indicators."""
        js_indicators = [
            'function ', 'var ', 'let ', 'const ', '=>', '=>',
            'console.', 'document.', 'window.', 'process.',
            'import ', 'export ', 'require(', 'module.exports',
            'class ', 'extends ', 'super(', 'this.', 'new '
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in js_indicators)
    
    def parse_ast(self, content: str, file_path: Path) -> str:
        """JavaScript doesn't have native AST in Python, return content."""
        return content
    
    def extract_variables(self, content: str) -> List[Variable]:
        """Extract JavaScript variables using regex patterns."""
        variables = []
        lines = content.split('\n')
        
        # Regex patterns for variable declarations
        var_patterns = [
            r'(?:var|let|const)\s+(\w+)\s*=',
            r'function\s+(\w+)\s*\(',
            r'(\w+)\s*=\s*function',
            r'(\w+)\s*:\s*function'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in var_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    var_name = match.group(1)
                    variables.append(Variable(
                        name=var_name,
                        scope="global",  # Simplified scope
                        line=line_num,
                        column=match.start(),
                        scope_type=ScopeType.GLOBAL
                    ))
        
        return variables
    
    def identify_sources(self, content: str) -> List[TaintSource]:
        """Identify JavaScript taint sources."""
        sources = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Look for variable assignments with taint sources
            assign_match = re.search(r'(?:var|let|const)?\s*(\w+)\s*=\s*([^;]+)', line)
            if assign_match:
                var_name = assign_match.group(1)
                value_expr = assign_match.group(2)
                
                for source_type, funcs in self.taint_sources.items():
                    for func, confidence in funcs.items():
                        if func in value_expr:
                            sources.append(TaintSource(
                                name=var_name,
                                line=line_num,
                                column=assign_match.start(1),
                                source_type=source_type,
                                confidence=confidence,
                                context={'value_expression': value_expr}
                            ))
                            break
        
        return sources
    
    def identify_sinks(self, content: str) -> List[TaintSink]:
        """Identify JavaScript taint sinks."""
        sinks = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for sink_type, funcs in self.taint_sinks.items():
                for func, severity in funcs.items():
                    if func in line:
                        # Extract arguments using regex
                        func_match = re.search(rf'{re.escape(func)}\s*\((.*?)\)', line)
                        arguments = []
                        if func_match:
                            args_str = func_match.group(1)
                            arguments = [arg.strip() for arg in args_str.split(',') if arg.strip()]
                        
                        sinks.append(TaintSink(
                            name=func,
                            line=line_num,
                            column=line.find(func),
                            sink_type=sink_type,
                            arguments=arguments,
                            severity=severity
                        ))
        
        return sinks
    
    def build_def_use_chains(self, content: str, variables: List[Variable]) -> Dict[Variable, List[FlowNode]]:
        """Build JavaScript def-use chains using regex analysis."""
        def_use_chains: Dict[Variable, List[FlowNode]] = defaultdict(list)
        lines = content.split('\n')
        
        for var in variables:
            for line_num, line in enumerate(lines, 1):
                # Check for definitions
                if re.search(rf'\b{var.name}\s*=', line):
                    flow_node = FlowNode(
                        variable=var,
                        operation='def',
                        line=line_num,
                        context=line.strip()
                    )
                    def_use_chains[var].append(flow_node)
                
                # Check for uses
                elif re.search(rf'\b{var.name}\b', line) and '=' not in line:
                    flow_node = FlowNode(
                        variable=var,
                        operation='use',
                        line=line_num,
                        context=line.strip()
                    )
                    def_use_chains[var].append(flow_node)
        
        return def_use_chains


class JavaAnalyzer(LanguageAnalyzer):
    """Java-specific taint analysis using regex patterns and basic parsing."""
    
    def __init__(self, config: Config):
        super().__init__(config)
        
        # Java taint sources
        self.taint_sources = {
            'user_input': {
                'Scanner.nextLine': 0.95, 'BufferedReader.readLine': 0.90,
                'System.in': 0.85, 'args': 0.80, 'getParameter': 0.90
            },
            'file_read': {
                'Files.readAllLines': 0.75, 'Files.readString': 0.75,
                'BufferedReader.read': 0.70, 'FileInputStream': 0.70
            },
            'network': {
                'HttpURLConnection': 0.80, 'Socket.getInputStream': 0.85,
                'URL.openConnection': 0.80, 'HttpClient.send': 0.80
            },
            'env_var': {
                'System.getenv': 0.75, 'System.getProperty': 0.70,
                'Properties.getProperty': 0.70
            },
            'db_query': {
                'Statement.executeQuery': 0.85, 'PreparedStatement.execute': 0.85,
                'ResultSet.next': 0.90, 'EntityManager.find': 0.80
            }
        }
        
        # Java taint sinks
        self.taint_sinks = {
            'logging': {
                'System.out.println': 'medium', 'System.err.println': 'medium',
                'Logger.info': 'low', 'Logger.error': 'medium', 'Logger.debug': 'low'
            },
            'file_write': {
                'Files.write': 'high', 'FileOutputStream.write': 'high',
                'PrintWriter.println': 'high', 'BufferedWriter.write': 'high'
            },
            'network_send': {
                'HttpURLConnection.getOutputStream': 'high',
                'Socket.getOutputStream': 'high', 'OutputStream.write': 'high'
            },
            'console_output': {
                'System.out.print': 'medium', 'System.err.print': 'medium',
                'PrintStream.print': 'medium'
            }
        }
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of file extensions supported by this analyzer."""
        return ['.java', '.jav']
    
    def _has_language_indicators(self, content: str) -> bool:
        """Check if content has Java language indicators."""
        java_indicators = [
            'public class', 'private ', 'public ', 'protected ',
            'static ', 'void ', 'int ', 'String ', 'boolean ',
            'import ', 'package ', 'extends ', 'implements ',
            'try {', 'catch (', 'finally {', 'new ', 'this.'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in java_indicators)
    
    def parse_ast(self, content: str, file_path: Path) -> str:
        """Java doesn't have native AST in Python, return content."""
        return content
    
    def extract_variables(self, content: str) -> List[Variable]:
        """Extract Java variables using regex patterns."""
        variables = []
        lines = content.split('\n')
        
        # Regex patterns for Java variable declarations
        var_patterns = [
            r'(?:public|private|protected)?\s*(?:static|final)?\s*(?:\w+)\s+(\w+)\s*=',
            r'(?:public|private|protected)?\s*(?:static|final)?\s*(?:\w+)\s+(\w+)\s*;',
            r'for\s*\(\s*(?:\w+)\s+(\w+)\s*:',
            r'catch\s*\(\s*(?:\w+)\s+(\w+)\s*\)',
            r'(\w+)\s*=\s*new\s+'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in var_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    var_name = match.group(1)
                    variables.append(Variable(
                        name=var_name,
                        scope="global",  # Simplified scope
                        line=line_num,
                        column=match.start(),
                        scope_type=ScopeType.GLOBAL
                    ))
        
        return variables
    
    def identify_sources(self, content: str) -> List[TaintSource]:
        """Identify Java taint sources."""
        sources = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Look for variable assignments with taint sources
            assign_match = re.search(r'(\w+)\s*=\s*([^;]+)', line)
            if assign_match:
                var_name = assign_match.group(1)
                value_expr = assign_match.group(2)
                
                for source_type, funcs in self.taint_sources.items():
                    for func, confidence in funcs.items():
                        if func in value_expr:
                            sources.append(TaintSource(
                                name=var_name,
                                line=line_num,
                                column=assign_match.start(1),
                                source_type=source_type,
                                confidence=confidence,
                                context={'value_expression': value_expr}
                            ))
                            break
        
        return sources
    
    def identify_sinks(self, content: str) -> List[TaintSink]:
        """Identify Java taint sinks."""
        sinks = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for sink_type, funcs in self.taint_sinks.items():
                for func, severity in funcs.items():
                    if func in line:
                        # Extract arguments using regex
                        func_match = re.search(rf'{re.escape(func)}\s*\((.*?)\)', line)
                        arguments = []
                        if func_match:
                            args_str = func_match.group(1)
                            arguments = [arg.strip() for arg in args_str.split(',') if arg.strip()]
                        
                        sinks.append(TaintSink(
                            name=func,
                            line=line_num,
                            column=line.find(func),
                            sink_type=sink_type,
                            arguments=arguments,
                            severity=severity
                        ))
        
        return sinks
    
    def build_def_use_chains(self, content: str, variables: List[Variable]) -> Dict[Variable, List[FlowNode]]:
        """Build Java def-use chains using regex analysis."""
        def_use_chains: Dict[Variable, List[FlowNode]] = defaultdict(list)
        lines = content.split('\n')
        
        for var in variables:
            for line_num, line in enumerate(lines, 1):
                # Check for definitions
                if re.search(rf'\b{var.name}\s*=', line):
                    flow_node = FlowNode(
                        variable=var,
                        operation='def',
                        line=line_num,
                        context=line.strip()
                    )
                    def_use_chains[var].append(flow_node)
                
                # Check for uses
                elif re.search(rf'\b{var.name}\b', line) and '=' not in line:
                    flow_node = FlowNode(
                        variable=var,
                        operation='use',
                        line=line_num,
                        context=line.strip()
                    )
                    def_use_chains[var].append(flow_node)
        
        return def_use_chains


class DataflowAnalyzer:
    """Enterprise-grade dataflow/taint analysis with comprehensive flow tracking."""
    
    def __init__(self, config: Config, correlation_id: Optional[str] = None):
        self.config = config
        self.correlation_id = correlation_id
        self.logger = logging.getLogger("levox.dataflow")
        
        # Language-specific analyzers
        self.analyzers: Dict[str, LanguageAnalyzer] = {
            'python': PythonAnalyzer(config),
            'javascript': JavaScriptAnalyzer(config),
            'java': JavaAnalyzer(config)
        }
        
        # Performance settings
        self.max_flow_distance = config.get('max_flow_distance', 10)
        self.max_concurrent_files = config.get('max_concurrent_files', 4)
        # Prefer performance-config override
        perf_timeout = getattr(getattr(config, 'performance', None), 'dataflow_timeout_seconds', None)
        self.analysis_timeout = perf_timeout if perf_timeout is not None else config.get('analysis_timeout_seconds', 30.0)
        
        # Initialize taint sources and sinks
        self.taint_sources = {}
        self.taint_sinks = {}
    
    def analyze_file(self, file_path: Path, content: str, language: str) -> List[DetectionMatch]:
        """
        Analyze a single file for dataflow/taint violations.
        
        Args:
            file_path: Path to the file being analyzed
            content: File content as string
            language: Programming language ('python', 'javascript', etc.)
            
        Returns:
            List of detection matches representing taint flows
            
        Raises:
            DetectionError: If analysis fails due to parsing or processing errors
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not file_path or not content.strip():
                self.logger.debug(f"Skipping empty file: {file_path}")
                return []
            
            if not is_supported_file(file_path):
                self.logger.debug(f"File type not supported for dataflow analysis: {file_path.suffix}")
                return []
            
            # Get language-specific analyzer
            analyzer = self.analyzers.get(language.lower())
            if not analyzer:
                self.logger.debug(f"No analyzer available for language: {language}")
                return []
            
            # Perform analysis with timeout
            try:
                matches = self._analyze_with_timeout(analyzer, file_path, content)
                
                analysis_time = time.time() - start_time
                self._log_analysis_results(file_path, language, len(matches), analysis_time)
                
                return matches
                
            except TimeoutError:
                raise DetectionError.timeout(
                    int(self.analysis_timeout),
                    correlation_id=self.correlation_id
                )
            
        except Exception as e:
            if isinstance(e, (DetectionError, ParserError)):
                raise
            
            self.logger.error(
                f"Dataflow analysis failed for {file_path}: {e}",
                extra={
                    'structured_data': {
                        'file_path': str(file_path),
                        'language': language,
                        'error_type': type(e).__name__,
                        'correlation_id': self.correlation_id
                    }
                }
            )
            
            raise DetectionError(
                f"Dataflow analysis failed: {e}",
                details={
                    'file_path': str(file_path),
                    'language': language,
                    'error_type': type(e).__name__
                },
                correlation_id=self.correlation_id
            )
    
    def analyze_files_concurrent(self, file_specs: List[Tuple[Path, str, str]]) -> List[DetectionMatch]:
        """
        Analyze multiple files concurrently for better performance.
        
        Args:
            file_specs: List of (file_path, content, language) tuples
            
        Returns:
            Combined list of all detection matches
        """
        all_matches = []
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent_files) as executor:
            # Submit all analysis tasks
            future_to_file = {
                executor.submit(self.analyze_file, file_path, content, language): file_path
                for file_path, content, language in file_specs
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    matches = future.result()
                    all_matches.extend(matches)
                except Exception as e:
                    self.logger.warning(f"Failed to analyze {file_path}: {e}")
        
        return all_matches

    def analyze_python_dataflow(self, content: str, file_path: Path) -> List[DetectionMatch]:
        """Analyze Python code snippet/file for dataflow analysis.
        This is a convenience wrapper used by tests.
        """
        return self.analyze_file(file_path, content, "python")
    
    def _analyze_with_timeout(self, analyzer: LanguageAnalyzer, file_path: Path, content: str) -> List[DetectionMatch]:
        """Run analysis with progressive timeout strategy and fallback logic."""
        file_size_mb = len(content.encode('utf-8')) / 1024 / 1024
        
        # Skip files that are too large for dataflow analysis
        if file_size_mb > 50:  # 50MB limit
            self.logger.warning(f"Skipping dataflow analysis for large file: {file_path} ({file_size_mb:.1f}MB)")
            return self._create_fallback_result(file_path, "file_too_large", file_size_mb)
        
        # Progressive timeout strategy
        timeout_stages = [
            (self.analysis_timeout, "full_analysis"),
            (self.analysis_timeout * 0.5, "reduced_scope"),
            (10.0, "ast_only")
        ]
        
        for timeout, stage in timeout_stages:
            try:
                result = self._run_analysis_stage(analyzer, file_path, content, timeout, stage)
                if result:
                    return result
            except TimeoutError:
                self.logger.warning(f"Dataflow analysis timeout at {stage} stage for {file_path}")
                continue
            except Exception as e:
                self.logger.error(f"Dataflow analysis error at {stage} stage for {file_path}: {e}")
                continue
        
        # Final fallback - return timeout result
        return self._create_fallback_result(file_path, "analysis_timeout", self.analysis_timeout)
    
    def _run_analysis_stage(self, analyzer: LanguageAnalyzer, file_path: Path, content: str, 
                           timeout: float, stage: str) -> List[DetectionMatch]:
        """Run analysis at a specific stage with timeout."""
        result_container = []
        exception_container = []
        
        def analysis_worker():
            try:
                if stage == "full_analysis":
                    result = self._perform_analysis(analyzer, file_path, content)
                elif stage == "reduced_scope":
                    result = self._perform_reduced_analysis(analyzer, file_path, content)
                elif stage == "ast_only":
                    result = self._perform_ast_only_analysis(analyzer, file_path, content)
                else:
                    result = []
                
                result_container.append(result)
            except Exception as e:
                exception_container.append(e)
        
        thread = threading.Thread(target=analysis_worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Analysis timeout exceeded: {timeout}s")
        
        if exception_container:
            raise exception_container[0]
        
        return result_container[0] if result_container else []
    
    def _perform_reduced_analysis(self, analyzer: LanguageAnalyzer, file_path: Path, content: str) -> List[DetectionMatch]:
        """Perform reduced scope analysis focusing on function-level flows."""
        
        try:
            # Parse AST
            ast_or_content = analyzer.parse_ast(content, file_path)
            
            # Extract only function-level variables and sources/sinks
            variables = analyzer.extract_variables(ast_or_content)
            sources = analyzer.identify_sources(ast_or_content)
            sinks = analyzer.identify_sinks(ast_or_content)
            
            # Early exit if no sources detected
            if not sources:
                return []
            
            # Build simplified def-use chains (function scope only)
            def_use_chains = analyzer.build_def_use_chains(ast_or_content, variables)
            
            # Create matches with reduced confidence
            matches = []
            for src in sources:
                matches.append(DetectionMatch(
                    file=str(file_path),
                    line=src.line,
                    engine="dataflow",
                    rule_id="dataflow_source",
                    severity="MEDIUM",
                    confidence=src.confidence * 0.85,  # Reduce confidence for fallback
                    snippet=src.name,
                    description="Dataflow analysis detected taint source (reduced scope)",
                    pattern_name='dataflow_source',
                    matched_text=src.name,
                    column_start=src.column,
                    column_end=src.column + len(src.name),
                    risk_level=RiskLevel.MEDIUM,
                    context_before='',
                    context_after='',
                    metadata={
                        'detection_level': 'dataflow',
                        'match_type': 'source',
                        'analysis_method': 'reduced_scope',
                        'source_type': src.source_type,
                        'confidence_reduction': 0.85
                    }
                ))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Reduced analysis failed for {file_path}: {e}")
            return []
    
    def _perform_ast_only_analysis(self, analyzer: LanguageAnalyzer, file_path: Path, content: str) -> List[DetectionMatch]:
        """Perform AST-only analysis without complex dataflow tracking."""
        
        try:
            # Parse AST
            ast_or_content = analyzer.parse_ast(content, file_path)
            
            # Extract sources and sinks only
            sources = analyzer.identify_sources(ast_or_content)
            sinks = analyzer.identify_sinks(ast_or_content)
            
            # Early exit if no sources detected
            if not sources:
                return []
            
            # Create matches with further reduced confidence
            matches = []
            for src in sources:
                matches.append(DetectionMatch(
                    file=str(file_path),
                    line=src.line,
                    engine="dataflow",
                    rule_id="dataflow_source",
                    severity="MEDIUM",
                    confidence=src.confidence * 0.7,  # Further reduce confidence
                    snippet=src.name,
                    description="Dataflow analysis detected taint source (AST only)",
                    pattern_name='dataflow_source',
                    matched_text=src.name,
                    column_start=src.column,
                    column_end=src.column + len(src.name),
                    risk_level=RiskLevel.MEDIUM,
                    context_before='',
                    context_after='',
                    metadata={
                        'detection_level': 'dataflow',
                        'match_type': 'source',
                        'analysis_method': 'ast_only',
                        'source_type': src.source_type,
                        'confidence_reduction': 0.7
                    }
                ))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"AST-only analysis failed for {file_path}: {e}")
            return []
    
    def _create_fallback_result(self, file_path: Path, reason: str, value: float) -> List[DetectionMatch]:
        """Create a fallback result when analysis fails."""
        
        return [DetectionMatch(
            file=str(file_path),
            line=1,
            engine="dataflow",
            rule_id="dataflow_timeout",
            severity="LOW",
            confidence=0.3,
            snippet=f"Analysis {reason}",
            description=f"Dataflow analysis {reason}: {value}",
            pattern_name='dataflow_timeout',
            matched_text=f'Analysis {reason}',
            column_start=1,
            column_end=1,
            risk_level=RiskLevel.LOW,
            context_before='',
            context_after='',
            metadata={
                'detection_level': 'dataflow',
                'match_type': 'timeout',
                'analysis_method': 'fallback',
                'reason': reason,
                'value': value,
                'pattern_regex': 'dataflow_timeout'
            }
        )]
    
    def _perform_analysis(self, analyzer: LanguageAnalyzer, file_path: Path, content: str) -> List[DetectionMatch]:
        """Perform the core dataflow analysis."""
        
        try:
            # Parse the file
            ast_or_content = analyzer.parse_ast(content, file_path)
            
            # Extract program structure
            variables = analyzer.extract_variables(ast_or_content)
            sources = analyzer.identify_sources(ast_or_content)
            sinks = analyzer.identify_sinks(ast_or_content)
            
            self.logger.debug(
                f"Analysis extracted: {len(variables)} variables, {len(sources)} sources, {len(sinks)} sinks",
                extra={
                    'structured_data': {
                        'file_path': str(file_path),
                        'variables_count': len(variables),
                        'sources_count': len(sources),
                        'sinks_count': len(sinks),
                        'correlation_id': self.correlation_id
                    }
                }
            )
            
            # Even if we have only sources or only sinks, surface them for visibility
            if not sources and not sinks:
                # Return empty list when no taint flows are detected
                # This is NOT a violation - it's just no dataflow issues found
                return []
            
            # Build def-use chains
            def_use_chains = analyzer.build_def_use_chains(ast_or_content, variables)
            
            # Emit source and sink matches directly
            matches: List[DetectionMatch] = []
            for src in sources:
                matches.append(DetectionMatch(
                    file=str(file_path),
                    line=src.line,
                    engine="dataflow",
                    rule_id="dataflow_source",
                    severity="MEDIUM",
                    confidence=src.confidence,
                    snippet=src.name,
                    description="Dataflow analysis detected taint source",
                    pattern_name='dataflow_source',
                    matched_text=src.name,
                    column_start=src.column,
                    column_end=src.column + len(src.name),
                    risk_level=RiskLevel.MEDIUM,
                    context_before='',
                    context_after='',
                    metadata={'detection_level': 'dataflow', 'match_type': 'source', 'source_type': src.source_type, 'pattern_regex': 'dataflow_source'}
                ))
            for sk in sinks:
                matches.append(DetectionMatch(
                    file=str(file_path),
                    line=sk.line,
                    engine="dataflow",
                    rule_id="dataflow_sink",
                    severity="MEDIUM",
                    confidence=0.7,
                    snippet=sk.name,
                    description="Dataflow analysis detected taint sink",
                    pattern_name='dataflow_sink',
                    matched_text=sk.name,
                    column_start=sk.column,
                    column_end=sk.column + len(sk.name),
                    risk_level=RiskLevel.MEDIUM,
                    context_before='',
                    context_after='',
                    metadata={'detection_level': 'dataflow', 'match_type': 'sink', 'sink_type': sk.sink_type, 'pattern_regex': 'dataflow_sink'}
                ))

            # Find taint flows
            taint_flows = self._find_comprehensive_flows(def_use_chains, sources, sinks)
            
            # Convert to detection matches
            matches.extend(self._create_detection_matches(taint_flows, file_path))
            
            return matches
            
        except Exception as e:
            # Soft-fallback: do not abort the entire analysis on parser failures.
            # This commonly occurs on intentionally invalid test files in large repos.
            try:
                self.logger.debug(f"Parser/analysis error for {file_path}: {e}. Falling back to regex-only heuristics")
                fallback_matches = []
                # Heuristic: if content looks like Python, emit low-confidence generic matches
                if str(file_path).endswith('.py'):
                    lines = content.splitlines()
                    for i, line in enumerate(lines, start=1):
                        if any(tok in line for tok in ["email", "password", "token", "key="]):
                            fallback_matches.append(DetectionMatch(
                                file=str(file_path),
                                line=i,
                                engine="dataflow",
                                rule_id="regex_fallback_indicator",
                                severity="LOW",
                                confidence=0.3,
                                snippet=line.strip()[:120],
                                description="Regex fallback indicator detected (parser failed)",
                                pattern_name='regex_fallback_indicator',
                                matched_text=line.strip()[:120],
                                column_start=1,
                                column_end=min(len(line.strip()), 120),
                                risk_level=RiskLevel.LOW,
                                context_before='',
                                context_after='',
                                metadata={'detection_level': 'dataflow', 'match_type': 'fallback', 'parser_error': str(type(e).__name__) }
                            ))
                return fallback_matches
            except Exception:
                # Final fallback: return empty on irrecoverable failures
                return []
    
    def _find_comprehensive_flows(self, def_use_chains: Dict[Variable, List[FlowNode]], 
                                sources: List[TaintSource], sinks: List[TaintSink]) -> List[TaintFlow]:
        """Find comprehensive taint flows using advanced path analysis."""
        flows = []
        
        for source in sources:
            for sink in sinks:
                # Find all possible paths from source to sink
                paths = self._find_all_paths(def_use_chains, source, sink)
                
                for path in paths:
                    if path and len(path) <= self.max_flow_distance:
                        # Calculate flow metrics
                        confidence = self._calculate_flow_confidence(source, sink, path)
                        risk_factors = self._identify_risk_factors(source, sink, path)
                        
                        flow = TaintFlow(
                            source=source,
                            sink=sink,
                            path=path,
                            confidence=confidence,
                            flow_distance=len(path),
                            risk_factors=risk_factors,
                            metadata={
                                'analysis_timestamp': time.time(),
                                'analyzer_version': '2.0',
                                'correlation_id': self.correlation_id
                            }
                        )
                        flows.append(flow)
                        
                        # Log the discovered flow
                        self._log_taint_flow(flow)
        
        return flows
    
    def _find_all_paths(self, def_use_chains: Dict[Variable, List[FlowNode]], 
                       source: TaintSource, sink: TaintSink) -> List[List[FlowNode]]:
        """Find all possible paths from source to sink using graph traversal."""
        paths = []
        
        # Find the source variable in def-use chains
        source_nodes = []
        for var, nodes in def_use_chains.items():
            if var.name == source.name and any(node.line >= source.line for node in nodes):
                source_nodes.extend([node for node in nodes if node.line >= source.line])
        
        if not source_nodes:
            return paths
        
        # For each source node, find paths to sink
        for source_node in source_nodes:
            sink_paths = self._bfs_path_search(def_use_chains, source_node, sink)
            paths.extend(sink_paths)
        
        return paths
    
    def _bfs_path_search(self, def_use_chains: Dict[Variable, List[FlowNode]], 
                        start_node: FlowNode, target_sink: TaintSink) -> List[List[FlowNode]]:
        """Use BFS to find paths from start node to target sink."""
        paths = []
        queue = deque([(start_node, [start_node])])
        visited = set()
        
        # Safety limit to prevent infinite loops
        max_iterations = 1000
        iteration_count = 0
        
        while queue and iteration_count < max_iterations:
            iteration_count += 1
            current_node, path = queue.popleft()
            
            if len(path) > self.max_flow_distance:
                continue
            
            node_key = (current_node.variable.name, current_node.line, current_node.operation)
            if node_key in visited:
                continue
            visited.add(node_key)
            
            # Check if we've reached the sink
            if self._node_reaches_sink(current_node, target_sink):
                paths.append(path)
                continue
            
            # Explore successors
            for var, nodes in def_use_chains.items():
                for node in nodes:
                    # Look for data flow relationships
                    if (node.line > current_node.line and 
                        node.variable.name == current_node.variable.name and
                        node not in path):
                        queue.append((node, path + [node]))
                    
                    # Look for assignment chains (def -> use relationships)
                    elif (node.line > current_node.line and 
                          current_node.operation == 'use' and 
                          node.operation == 'def' and
                          self._variables_connected(current_node.variable, node.variable)):
                        queue.append((node, path + [node]))
        
        # Log if we hit the safety limit
        if iteration_count >= max_iterations:
            self.logger.warning(f"BFS path search hit safety limit of {max_iterations} iterations")
        
        return paths
    
    def _node_reaches_sink(self, node: FlowNode, sink: TaintSink) -> bool:
        """Check if a flow node reaches the target sink."""
        # Check if the node's variable is used in the sink's arguments
        for arg in sink.arguments:
            if node.variable.name in arg and abs(node.line - sink.line) <= 5:
                return True
        return False
    
    def _variables_connected(self, var1: Variable, var2: Variable) -> bool:
        """Check if two variables are connected through assignments."""
        # Simplified connection check - in practice, this would be more sophisticated
        return (var1.scope == var2.scope or 
                'global' in [var1.scope, var2.scope])
    
    def _calculate_flow_confidence(self, source: TaintSource, sink: TaintSink, 
                                 path: List[FlowNode]) -> float:
        """Calculate confidence score for a taint flow."""
        base_confidence = source.confidence
        
        # Decrease confidence based on flow distance
        distance_factor = max(0.3, 1.0 - (len(path) - 1) * 0.1)
        confidence = base_confidence * distance_factor
        
        # Adjust based on sink severity
        severity_multipliers = {'low': 0.8, 'medium': 1.0, 'high': 1.2}
        severity_factor = severity_multipliers.get(sink.severity, 1.0)
        confidence *= severity_factor
        
        # Boost confidence for direct PII indicators
        if source.pii_indicators:
            confidence = min(1.0, confidence * (1.0 + len(source.pii_indicators) * 0.05))
        
        # Penalize complex flows
        complexity_penalty = len(set(node.operation for node in path)) * 0.05
        confidence = max(0.1, confidence - complexity_penalty)
        
        return round(confidence, 3)
    
    def _identify_risk_factors(self, source: TaintSource, sink: TaintSink, 
                             path: List[FlowNode]) -> Set[str]:
        """Identify risk factors for a taint flow."""
        risk_factors = set()
        
        # Source-based risks
        high_risk_sources = {'user_input', 'network', 'db_query'}
        if source.source_type in high_risk_sources:
            risk_factors.add('high_risk_source')
        
        # Sink-based risks
        high_risk_sinks = {'file_write', 'network_send'}
        if sink.sink_type in high_risk_sinks:
            risk_factors.add('high_risk_sink')
        
        # Flow-based risks
        if len(path) > 5:
            risk_factors.add('complex_flow')
        
        if sink.severity == 'high':
            risk_factors.add('high_severity_sink')
        
        # PII-specific risks
        if source.pii_indicators:
            risk_factors.add('pii_detected')
        
        # Cross-scope flows
        scopes_in_path = set(node.variable.scope for node in path)
        if len(scopes_in_path) > 1:
            risk_factors.add('cross_scope_flow')
        
        return risk_factors
    
    def _create_detection_matches(self, taint_flows: List[TaintFlow], file_path: Path) -> List[DetectionMatch]:
        """Convert taint flows to structured detection matches."""
        
        matches = []
        
        for flow in taint_flows:
            # Create detailed flow description
            path_description = self._create_flow_description(flow)
            
            # Determine risk level
            risk_level = self._determine_risk_level(flow)
            
            # Create rich context
            context_before = f"Source: {flow.source.name} ({flow.source.source_type}) at line {flow.source.line}"
            context_after = f"Sink: {flow.sink.name} ({flow.sink.sink_type}) at line {flow.sink.line}"
            
            # Build comprehensive metadata
            metadata = {
                'detection_level': 'dataflow',
                'source_type': flow.source.source_type,
                'sink_type': flow.sink.sink_type,
                'source_line': flow.source.line,
                'sink_line': flow.sink.line,
                'flow_distance': flow.flow_distance,
                'flow_path': [node.variable.name for node in flow.path],
                'flow_operations': [node.operation for node in flow.path],
                'risk_factors': list(flow.risk_factors),
                'pii_indicators': list(flow.source.pii_indicators) if flow.source.pii_indicators else [],
                'sink_severity': flow.sink.severity,
                'confidence_breakdown': {
                    'source_confidence': flow.source.confidence,
                    'flow_confidence': flow.confidence,
                    'distance_penalty': max(0, (flow.flow_distance - 1) * 0.1)
                },
                'scan_timestamp': time.time(),
                'correlation_id': self.correlation_id,
                **flow.metadata
            }
            
            match = DetectionMatch(
                file=str(file_path),
                line=flow.sink.line,
                engine="dataflow",
                rule_id=f"dataflow_{flow.source.source_type}_to_{flow.sink.sink_type}",
                severity=risk_level.value if hasattr(risk_level, 'value') else str(risk_level),
                confidence=flow.confidence,
                snippet=path_description,
                description=f"Dataflow analysis detected taint flow from {flow.source.source_type} to {flow.sink.sink_type}",
                pattern_name=f"dataflow_{flow.source.source_type}_to_{flow.sink.sink_type}",
                matched_text=path_description,
                column_start=flow.sink.column,
                column_end=flow.sink.column + len(flow.sink.name),
                risk_level=risk_level,
                context_before=context_before,
                context_after=context_after,
                metadata=metadata
            )
            
            matches.append(match)
        
        return matches
    
    def _create_flow_description(self, flow: TaintFlow) -> str:
        """Create a human-readable description of the taint flow."""
        if len(flow.path) <= 2:
            return f"{flow.source.name} -> {flow.sink.name}"
        
        path_names = [node.variable.name for node in flow.path]
        # Remove consecutive duplicates
        unique_path = [path_names[0]]
        for name in path_names[1:]:
            if name != unique_path[-1]:
                unique_path.append(name)
        
        return " -> ".join(unique_path) + f" -> {flow.sink.name}"
    
    def _determine_risk_level(self, flow: TaintFlow) -> RiskLevel:
        """Determine the risk level for a taint flow."""
        # High risk conditions
        high_risk_conditions = [
            flow.source.source_type == 'user_input' and flow.sink.sink_type in ['file_write', 'network_send'],
            'pii_detected' in flow.risk_factors and flow.sink.severity == 'high',
            flow.confidence > 0.8 and 'high_risk_source' in flow.risk_factors,
            len(flow.source.pii_indicators) >= 2
        ]
        
        if any(high_risk_conditions):
            return RiskLevel.HIGH
        
        # Medium risk conditions
        medium_risk_conditions = [
            flow.source.source_type in ['network', 'db_query'] and flow.sink.sink_type == 'logging',
            flow.confidence > 0.6 and flow.sink.severity in ['medium', 'high'],
            'cross_scope_flow' in flow.risk_factors,
            len(flow.risk_factors) >= 2
        ]
        
        if any(medium_risk_conditions):
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _log_analysis_results(self, file_path: Path, language: str, matches_count: int, analysis_time: float) -> None:
        """Log structured analysis results."""
        self.logger.info(
            f"Dataflow analysis completed for {file_path.name}",
            extra={
                'structured_data': {
                    'file_path': str(file_path),
                    'language': language,
                    'matches_found': matches_count,
                    'analysis_time_seconds': round(analysis_time, 3),
                    'correlation_id': self.correlation_id,
                    'timestamp': time.time()
                }
            }
        )
    
    def _log_taint_flow(self, flow: TaintFlow) -> None:
        """Log structured information about a discovered taint flow."""
        self.logger.info(
            f"Taint flow detected: {flow.source.source_type} -> {flow.sink.sink_type}",
            extra={
                'structured_data': {
                    'source_type': flow.source.source_type,
                    'sink_type': flow.sink.sink_type,
                    'source_line': flow.source.line,
                    'sink_line': flow.sink.line,
                    'confidence': flow.confidence,
                    'flow_distance': flow.flow_distance,
                    'risk_factors': list(flow.risk_factors),
                    'pii_indicators': list(flow.source.pii_indicators) if flow.source.pii_indicators else [],
                    'correlation_id': self.correlation_id
                }
            }
        )

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
            self.logger.error(f"Dataflow scan_file failed for {file_path}: {e}")
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

    def _validate_sink_pii_context(self, flow: TaintFlow, content: str) -> float:
        """
        Validate if a dataflow sink actually receives PII data.
        Returns adjusted confidence score (0.5 to 1.5).
        
        Args:
            flow: TaintFlow object containing source, sink, and path
            content: File content for context analysis
            
        Returns:
            Confidence multiplier based on PII context validation
        """
        try:
            # Extract sink line context
            sink_line = flow.sink.line
            lines = content.split('\n')
            if sink_line > len(lines):
                return 0.5  # Invalid line, reduce confidence
            
            sink_context = lines[sink_line - 1] if sink_line > 0 else ""
            
            # Check if sink arguments contain PII patterns
            pii_in_arguments = self._check_pii_in_sink_arguments(flow.sink, sink_context)
            
            # Check if source variables have PII indicators
            pii_in_source = self._check_pii_in_source_variables(flow.source, content)
            
            # Check for sanitization in flow path
            sanitization_present = self._check_sanitization_in_path(flow.path, content)
            
            # Calculate confidence multiplier
            confidence_multiplier = 1.0
            
            # Boost confidence if PII evidence exists
            if pii_in_arguments and pii_in_source:
                confidence_multiplier = 1.5  # Strong PII evidence
            elif pii_in_arguments or pii_in_source:
                confidence_multiplier = 1.2  # Moderate PII evidence
            else:
                confidence_multiplier = 0.5  # No PII evidence, reduce confidence
            
            # Reduce confidence if sanitization is present
            if sanitization_present:
                confidence_multiplier *= 0.7
            
            # Ensure multiplier is within bounds
            return max(0.5, min(1.5, confidence_multiplier))
            
        except Exception as e:
            self.logger.debug(f"PII context validation failed: {e}")
            return 0.5  # Default to reduced confidence on error
    
    def _check_pii_in_sink_arguments(self, sink: TaintSink, sink_context: str) -> bool:
        """Check if sink arguments contain PII patterns."""
        # PII patterns to look for in arguments
        pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b[A-Za-z]{2}\d{6}\b',  # Driver's license pattern
        ]
        
        # Check sink arguments for PII patterns
        for arg in sink.arguments:
            for pattern in pii_patterns:
                if re.search(pattern, arg, re.IGNORECASE):
                    return True
        
        # Check sink context line for PII patterns
        for pattern in pii_patterns:
            if re.search(pattern, sink_context, re.IGNORECASE):
                return True
        
        return False
    
    def _check_pii_in_source_variables(self, source: TaintSource, content: str) -> bool:
        """Check if source variables have PII indicators."""
        # Check PII indicators in source
        if source.pii_indicators:
            return True
        
        # Check source context for PII patterns
        source_line = source.line
        lines = content.split('\n')
        if source_line <= len(lines):
            source_context = lines[source_line - 1] if source_line > 0 else ""
            
            # Look for PII-related variable names
            pii_variable_patterns = [
                r'\b(email|phone|ssn|credit_card|driver_license|passport)\b',
                r'\b(user_|customer_|client_|person_|individual_)\w*\b',
                r'\b(personal_|private_|sensitive_)\w*\b'
            ]
            
            for pattern in pii_variable_patterns:
                if re.search(pattern, source_context, re.IGNORECASE):
                    return True
        
        return False
    
    def _check_sanitization_in_path(self, path: List[FlowNode], content: str) -> bool:
        """Check if sanitization functions are present in the flow path."""
        sanitization_functions = [
            'escape', 'sanitize', 'clean', 'validate', 'filter',
            'strip', 'encode', 'hash', 'encrypt', 'mask'
        ]
        
        for node in path:
            if any(func in node.operation.lower() for func in sanitization_functions):
                return True
        
        return False

    def _is_framework_safe_sink(self, match: DetectionMatch, content: str) -> bool:
        """
        Detect if sink is a safe framework pattern that shouldn't be flagged.
        
        Args:
            match: DetectionMatch object representing the sink
            content: File content for context analysis
            
        Returns:
            True if sink is a safe framework pattern, False otherwise
        """
        try:
            # Extract sink context
            line_num = match.line_number
            lines = content.split('\n')
            if line_num > len(lines):
                return False
            
            sink_context = lines[line_num - 1] if line_num > 0 else ""
            matched_text = match.matched_text.lower()
            
            # Safe framework patterns
            safe_patterns = [
                # Parameterized queries (safe)
                r'cursor\.execute\([^,]+,\s*\([^)]+\)\)',
                r'cursor\.execute\([^,]+,\s*\[[^\]]+\]\)',
                r'\.execute\([^,]+,\s*%s\)',  # Python %s parameterized
                r'\.execute\([^,]+,\s*\?\)',  # SQLite parameterized
                
                # Route decorators (safe)
                r'@app\.(get|post|put|delete|patch)',
                r'@router\.(get|post|put|delete|patch)',
                r'@bp\.(get|post|put|delete|patch)',
                
                # ORM operations (safe)
                r'session\.query\(',
                r'\.filter\(|\.get\(|\.all\(\)',
                r'Model\.objects\.(create|get|filter|update|delete)',
                r'QuerySet\.(filter|get|create|update|delete)',
                
                # Logging framework (safe)
                r'logger\.(info|debug|warning|error|critical)',
                r'logging\.(info|debug|warning|error|critical)',
                r'log\.(info|debug|warning|error|critical)',
                
                # Validation decorators (safe)
                r'@validate\w*',
                r'@sanitize\w*',
                r'@clean\w*',
                
                # Framework-specific safe patterns
                r'django\.db\.models\.Model',
                r'sqlalchemy\.orm\.session',
                r'flask\.app\.Flask',
                r'fastapi\.FastAPI',
            ]
            
            # Check if sink matches safe patterns
            for pattern in safe_patterns:
                if re.search(pattern, sink_context, re.IGNORECASE):
                    return True
            
            # Check for parameterized query indicators
            param_indicators = ['%s', '?', ':', 'format(', 'f"', 'f\'', 'format(']
            if any(indicator in sink_context for indicator in param_indicators):
                return True
            
            # Check for ORM method calls
            orm_methods = ['.save()', '.create()', '.update()', '.delete()', '.get()', '.filter()']
            if any(method in sink_context for method in orm_methods):
                return True
            
            # Check for route handler patterns
            route_patterns = ['@app.route', '@bp.route', '@router.route', 'def get_', 'def post_', 'def put_']
            if any(pattern in sink_context for pattern in route_patterns):
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Framework safe sink detection failed: {e}")
            return False

    def _convert_to_unified_matches(self, matches: List, file_path: Path, 
                                   content: str, language: str) -> List[DetectionMatch]:
        """Convert dataflow matches to unified DetectionMatch format."""
        
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
                engine="dataflow",
                rule_id=match_dict.get('pattern_name', match_dict.get('rule_id', 'dataflow_detection')),
                severity=match_dict.get('severity', match_dict.get('risk_level', 'MEDIUM')),
                confidence=match_dict.get('confidence', match_dict.get('confidence_score', 0.8)),
                snippet=snippet,
                description=match_dict.get('description', 'Dataflow analysis detection'),
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
            
            # Apply confidence adjustments based on PII context and framework safety
            original_confidence = unified_match.confidence
            
            # Check if this is a dataflow sink pattern
            if 'sink' in unified_match.pattern_name.lower():
                # Check if it's a framework-safe sink
                if self._is_framework_safe_sink(unified_match, content):
                    # Reduce confidence for framework-safe patterns
                    unified_match.confidence *= 0.5
                    unified_match.metadata['framework_safe'] = True
                    unified_match.metadata['confidence_adjustment'] = 'framework_safe_reduction'
                
                # Check PII context for dataflow sinks
                if hasattr(match, 'flow') and hasattr(match.flow, 'source'):
                    # This is a TaintFlow object, validate PII context
                    pii_multiplier = self._validate_sink_pii_context(match.flow, content)
                    unified_match.confidence *= pii_multiplier
                    unified_match.metadata['pii_context_multiplier'] = pii_multiplier
                    unified_match.metadata['pii_context_validated'] = True
                else:
                    # For non-TaintFlow matches, apply basic PII context check
                    if not self._check_pii_in_sink_arguments(
                        type('Sink', (), {'arguments': [matched_text], 'line': line_num})(), 
                        content.split('\n')[line_num - 1] if line_num > 0 else ""
                    ):
                        unified_match.confidence *= 0.6  # Reduce confidence if no PII context
                        unified_match.metadata['no_pii_context'] = True
            
            # Apply dataflow sink minimum confidence threshold
            if unified_match.confidence < self.config.dataflow_sink_min_confidence:
                unified_match.metadata['below_dataflow_threshold'] = True
                # Don't filter here, let the final confidence filter handle it
            
            # Log confidence adjustments
            if abs(unified_match.confidence - original_confidence) > 0.01:
                self.logger.debug(
                    f"Dataflow confidence adjusted: {original_confidence:.3f} → {unified_match.confidence:.3f} "
                    f"(pattern: {unified_match.pattern_name})"
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





# Factory function for creating language analyzers
def create_language_analyzer(language: str, config: Config) -> LanguageAnalyzer:
    """
    Factory function to create a language-specific analyzer.
    
    Args:
        language: Programming language name ('python', 'javascript', 'java')
        config: Levox configuration object
        
    Returns:
        Configured LanguageAnalyzer instance
        
    Raises:
        ValueError: If language is not supported
    """
    language = language.lower()
    
    if language == 'python':
        return PythonAnalyzer(config)
    elif language == 'javascript':
        return JavaScriptAnalyzer(config)
    elif language == 'java':
        return JavaAnalyzer(config)
    else:
        raise ValueError(f"Unsupported language: {language}. Supported: {get_supported_languages()}")


# Utility functions for external integration

def create_analyzer(config: Config, correlation_id: Optional[str] = None) -> DataflowAnalyzer:
    """
    Factory function to create a configured DataflowAnalyzer instance.
    
    Args:
        config: Levox configuration object
        correlation_id: Optional correlation ID for tracing
        
    Returns:
        Configured DataflowAnalyzer instance
    """
    return DataflowAnalyzer(config, correlation_id)


def analyze_code_snippet(code: str, language: str, config: Config, 
                        correlation_id: Optional[str] = None) -> List[DetectionMatch]:
    """
    Convenience function to analyze a code snippet for taint flows.
    
    Args:
        code: Source code to analyze
        language: Programming language ('python', 'javascript')
        config: Levox configuration
        correlation_id: Optional correlation ID for tracing
        
    Returns:
        List of detection matches
    """
    analyzer = create_analyzer(config, correlation_id)
    temp_path = Path(f"<snippet>.{language}")
    
    return analyzer.analyze_file(temp_path, code, language)


def get_supported_languages() -> List[str]:
    """
    Get list of programming languages supported by the dataflow analyzer.
    
    Returns:
        List of supported language names
    """
    return ['python', 'javascript', 'java']


def test_language_analyzers(config: Config) -> Dict[str, Any]:
    """
    Test function to validate all language analyzers.
    
    Args:
        config: Levox configuration object
        
    Returns:
        Dictionary with test results for each analyzer
    """
    results = {}
    
    # Test Python analyzer
    try:
        python_analyzer = PythonAnalyzer(config)
        python_code = """
def process_user_data():
    user_input = input("Enter data: ")
    print(f"Processing: {user_input}")
    return user_input
"""
        python_analyzer.validate_content(python_code)
        python_vars = python_analyzer.extract_variables(python_analyzer.parse_ast(python_code, Path("test.py")))
        python_sources = python_analyzer.identify_sources(python_analyzer.parse_ast(python_code, Path("test.py")))
        python_sinks = python_analyzer.identify_sinks(python_analyzer.parse_ast(python_code, Path("test.py")))
        
        results['python'] = {
            'status': 'success',
            'variables_count': len(python_vars),
            'sources_count': len(python_sources),
            'sinks_count': len(python_sinks),
            'metadata': python_analyzer.get_analysis_metadata(),
            'complexity': python_analyzer.get_analysis_complexity()
        }
    except Exception as e:
        results['python'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Test JavaScript analyzer
    try:
        js_analyzer = JavaScriptAnalyzer(config)
        js_code = """
function processData() {
    const userInput = prompt("Enter data:");
    console.log("Processing:", userInput);
    return userInput;
}
"""
        js_analyzer.validate_content(js_code)
        js_vars = js_analyzer.extract_variables(js_code)
        js_sources = js_analyzer.identify_sources(js_code)
        js_sinks = js_analyzer.identify_sinks(js_code)
        
        results['javascript'] = {
            'status': 'success',
            'variables_count': len(js_vars),
            'sources_count': len(js_sources),
            'sinks_count': len(js_sinks),
            'metadata': js_analyzer.get_analysis_metadata(),
            'complexity': js_analyzer.get_analysis_complexity()
        }
    except Exception as e:
        results['javascript'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Test Java analyzer
    try:
        java_analyzer = JavaAnalyzer(config)
        java_code = """
public class DataProcessor {
    public String processUserData() {
        Scanner scanner = new Scanner(System.in);
        String userInput = scanner.nextLine();
        System.out.println("Processing: " + userInput);
        return userInput;
    }
}
"""
        java_analyzer.validate_content(java_code)
        java_vars = java_analyzer.extract_variables(java_code)
        java_sources = java_analyzer.identify_sources(java_code)
        java_sinks = java_analyzer.identify_sinks(java_code)
        
        results['java'] = {
            'status': 'success',
            'variables_count': len(java_vars),
            'sources_count': len(java_sources),
            'sinks_count': len(java_sinks),
            'metadata': java_analyzer.get_analysis_metadata(),
            'complexity': java_analyzer.get_analysis_complexity()
        }
    except Exception as e:
        results['java'] = {
            'status': 'error',
            'error': str(e)
        }
    
    return results