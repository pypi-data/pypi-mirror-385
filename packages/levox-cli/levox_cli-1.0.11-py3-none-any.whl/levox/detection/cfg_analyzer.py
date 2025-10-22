"""
Control Flow Graph (CFG) Analysis for Levox PII Detection

This module implements CFG analysis as STAGE 7 in the detection pipeline,
positioned between Dataflow Analysis and ML Filtering. It detects complex
PII flows through control structures that previous stages may miss.

License Tier: Premium+ (same as AST/Context/Dataflow)
Performance: Selective execution, ~10-20% overhead when triggered
"""

import os
import time
import logging
import ast
import hashlib
import threading
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import re
import networkx as nx

# Import existing Levox components
from ..models.detection_result import DetectionMatch
from ..core.config import Config, LicenseTier, RiskLevel
from ..core.exceptions import DetectionError, LicenseError, AnalysisTimeoutError
from ..parsers import get_parser, detect_language
from ..utils.cache import CacheManager


class CFGNodeType(str, Enum):
    """Types of nodes in the Control Flow Graph."""
    ENTRY = "entry"
    EXIT = "exit"
    STATEMENT = "statement"
    CONDITION = "condition"
    LOOP_HEADER = "loop_header"
    LOOP_BACK = "loop_back"
    FUNCTION_CALL = "function_call"
    ASSIGNMENT = "assignment"
    RETURN = "return"
    EXCEPTION_HANDLER = "exception_handler"
    BREAK = "break"
    CONTINUE = "continue"


class CFGEdgeType(str, Enum):
    """Types of edges in the Control Flow Graph."""
    SEQUENTIAL = "sequential"
    TRUE_BRANCH = "true_branch"
    FALSE_BRANCH = "false_branch"
    LOOP_ENTRY = "loop_entry"
    LOOP_BACK = "loop_back"
    FUNCTION_CALL = "function_call"
    RETURN = "return"
    EXCEPTION = "exception"
    BREAK = "break"
    CONTINUE = "continue"


@dataclass
class CFGNode:
    """Represents a node in the Control Flow Graph."""
    id: str
    node_type: CFGNodeType
    line_number: int
    content: str
    variables_read: Set[str] = field(default_factory=set)
    variables_written: Set[str] = field(default_factory=set)
    pii_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    complexity_score: int = 0
    
    def has_pii_context(self) -> bool:
        """Check if this node has PII context."""
        return bool(self.pii_context or 
                   any(self._is_pii_variable(var) for var in 
                       self.variables_read.union(self.variables_written)))
    
    def _is_pii_variable(self, var_name: str) -> bool:
        """Check if a variable name suggests PII content."""
        pii_indicators = {
            'ssn', 'social_security', 'tax_id', 'credit_card', 'cc_num', 
            'email', 'phone', 'address', 'dob', 'birth', 'password', 
            'passwd', 'pwd', 'api_key', 'secret', 'token', 'personal',
            'private', 'confidential', 'sensitive'
        }
        var_lower = var_name.lower()
        return any(indicator in var_lower for indicator in pii_indicators)


@dataclass
class CFGEdge:
    """Represents an edge in the Control Flow Graph."""
    source_id: str
    target_id: str
    edge_type: CFGEdgeType
    condition: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0


class CFGStatistics:
    """Statistics for CFG analysis performance tracking."""
    
    def __init__(self):
        self.files_analyzed = 0
        self.files_skipped = 0
        self.total_nodes_created = 0
        self.total_edges_created = 0
        self.analysis_time = 0.0
        self.matches_found = 0
        self.errors_encountered = 0
    
    def log_stats(self, logger: logging.Logger):
        """Log performance statistics."""
        logger.info(f"CFG Analysis Stats: {self.files_analyzed} analyzed, "
                   f"{self.files_skipped} skipped, {self.matches_found} matches, "
                   f"{self.analysis_time:.2f}s total")


class CFGBuilder:
    """Builds Control Flow Graphs from source code with performance optimizations."""
    
    def __init__(self, config: Config):
        """Initialize the CFG builder with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.supported_languages = {"python", "javascript", "typescript", "java", "c", "cpp"}
        self.cache_manager = CacheManager()
        self.stats = CFGStatistics()
        
        # Performance limits
        self.max_file_size = config.cfg_analysis.max_file_size_bytes
        self.max_cfg_nodes = config.cfg_analysis.max_cfg_nodes
        self.analysis_timeout = config.cfg_analysis.max_analysis_time_seconds
        self.confidence_threshold = config.cfg_analysis.confidence_threshold
        
    def should_analyze_file(self, file_path: str, previous_matches: List[DetectionMatch], 
                           file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Determine if a file should undergo CFG analysis with detailed reasoning.
        
        Returns:
            Tuple of (should_analyze: bool, skip_reason: Optional[str])
        """
        try:
            # License check
            if not self.config.is_feature_enabled("cfg_analysis"):
                return False, "cfg_analysis_disabled"
            
            # File size check
            if file_size > self.max_file_size:
                self.stats.files_skipped += 1
                return False, f"file_too_large_{file_size}"
            
            # Language support check
            language = detect_language(file_path)
            if language not in self.supported_languages:
                self.stats.files_skipped += 1
                return False, f"unsupported_language_{language}"
            
            # Previous matches check - require high confidence PII detections
            high_confidence_matches = [
                m for m in previous_matches 
                if (m.confidence >= self.confidence_threshold and 
                    m.engine in {'ast_analysis', 'context_analysis', 'dataflow_analysis'})
            ]
            
            if not high_confidence_matches:
                self.stats.files_skipped += 1
                return False, "no_high_confidence_pii"
            
            # Check for PII-related functions/variables in previous matches
            has_pii_functions = any(
                self._match_suggests_complex_pii_flow(match) 
                for match in high_confidence_matches
            )
            
            if not has_pii_functions:
                self.stats.files_skipped += 1
                return False, "no_complex_pii_patterns"
                
            return True, None
            
        except Exception as e:
            self.logger.warning(f"Error checking if file should be analyzed: {e}")
            self.stats.errors_encountered += 1
            return False, f"check_error_{str(e)[:50]}"
    
    def _match_suggests_complex_pii_flow(self, match: DetectionMatch) -> bool:
        """Check if a detection match suggests complex PII flow patterns."""
        complex_indicators = {
            'if', 'for', 'while', 'switch', 'case', 'function', 'method',
            'loop', 'condition', 'branch', 'iterate', 'process', 'transform'
        }
        
        snippet_lower = match.snippet.lower() if match.snippet else ""
        return any(indicator in snippet_lower for indicator in complex_indicators)
    
    def build_cfg_with_timeout(self, file_path: str, content: str, 
                              language: str) -> Tuple[List[CFGNode], List[CFGEdge]]:
        """Build CFG with timeout protection."""
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._build_cfg_internal, file_path, content, language)
                return future.result(timeout=self.analysis_timeout)
                
        except FutureTimeoutError:
            self.logger.warning(f"CFG building timed out for {file_path}")
            self.stats.errors_encountered += 1
            raise AnalysisTimeoutError.exceeded(self.analysis_timeout)
        except Exception as e:
            self.logger.error(f"CFG building failed for {file_path}: {e}")
            self.stats.errors_encountered += 1
            raise DetectionError(f"CFG construction failed: {e}")
    
    def _build_cfg_internal(self, file_path: str, content: str, 
                           language: str) -> Tuple[List[CFGNode], List[CFGEdge]]:
        """Internal CFG building with caching."""
        # Check cache first
        cache_key = self._get_cache_key(content, language)
        cached_result = self.cache_manager.get(f"cfg_{cache_key}")
        if cached_result:
            return cached_result
        
        # Build CFG based on language
        if language == "python":
            result = self._build_python_cfg(content, file_path)
        elif language in {"javascript", "typescript"}:
            result = self._build_javascript_cfg(content, file_path)
        else:
            raise DetectionError(f"Unsupported language for CFG: {language}")
        
        # Cache result
        self.cache_manager.set(f"cfg_{cache_key}", result, ttl=3600)  # 1 hour TTL
        
        return result
    
    def _get_cache_key(self, content: str, language: str) -> str:
        """Generate cache key for CFG."""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
        return f"{language}_{content_hash}"
    
    def _build_python_cfg(self, content: str, file_path: str) -> Tuple[List[CFGNode], List[CFGEdge]]:
        """Enhanced Python CFG builder with better error handling."""
        try:
            # Normalize modern syntax for Python 3.11 parser
            try:
                from ..utils.python_syntax import normalize_modern_syntax
                content = normalize_modern_syntax(content)
            except Exception:
                pass
            tree = ast.parse(content)
            nodes = []
            edges = []
            node_counter = [0]  # Use list for mutable counter
            
            # Create entry node
            entry_node = CFGNode(
                id=f"entry_{node_counter[0]}",
                node_type=CFGNodeType.ENTRY,
                line_number=1,
                content="ENTRY",
                metadata={"file_path": file_path}
            )
            nodes.append(entry_node)
            node_counter[0] += 1
            
            # Process module-level statements
            current_nodes = [entry_node]
            for stmt in tree.body:
                new_nodes, new_edges, current_nodes = self._process_python_statement(
                    stmt, node_counter, current_nodes, content
                )
                nodes.extend(new_nodes)
                edges.extend(new_edges)
                
                # Performance check
                if len(nodes) > self.max_cfg_nodes:
                    self.logger.warning(f"CFG too large for {file_path}, truncating at {len(nodes)} nodes")
                    break
            
            # Create exit node and connect final nodes
            exit_node = CFGNode(
                id=f"exit_{node_counter[0]}",
                node_type=CFGNodeType.EXIT,
                line_number=len(content.splitlines()),
                content="EXIT"
            )
            nodes.append(exit_node)
            
            # Connect all dangling nodes to exit
            for current_node in current_nodes:
                if current_node and current_node.node_type != CFGNodeType.EXIT:
                    edges.append(CFGEdge(
                        source_id=current_node.id,
                        target_id=exit_node.id,
                        edge_type=CFGEdgeType.SEQUENTIAL
                    ))
            
            # Update statistics
            self.stats.total_nodes_created += len(nodes)
            self.stats.total_edges_created += len(edges)
            
            return nodes, edges
            
        except SyntaxError as e:
            raise DetectionError(f"Python syntax error: {e}")
        except Exception as e:
            raise DetectionError(f"Python CFG construction failed: {e}")
    
    def _process_python_statement(self, stmt: ast.AST, node_counter: List[int], 
                                 current_nodes: List[CFGNode], 
                                 content: str) -> Tuple[List[CFGNode], List[CFGEdge], List[CFGNode]]:
        """Process Python statement with enhanced control flow handling."""
        nodes = []
        edges = []
        
        try:
            if isinstance(stmt, ast.If):
                new_nodes, new_edges, exit_nodes = self._process_python_if(
                    stmt, node_counter, current_nodes, content
                )
            elif isinstance(stmt, ast.For):
                new_nodes, new_edges, exit_nodes = self._process_python_for(
                    stmt, node_counter, current_nodes, content
                )
            elif isinstance(stmt, ast.While):
                new_nodes, new_edges, exit_nodes = self._process_python_while(
                    stmt, node_counter, current_nodes, content
                )
            elif isinstance(stmt, ast.FunctionDef):
                new_nodes, new_edges, exit_nodes = self._process_python_function(
                    stmt, node_counter, current_nodes, content
                )
            elif isinstance(stmt, ast.Try):
                new_nodes, new_edges, exit_nodes = self._process_python_try(
                    stmt, node_counter, current_nodes, content
                )
            elif isinstance(stmt, ast.With):
                new_nodes, new_edges, exit_nodes = self._process_python_with(
                    stmt, node_counter, current_nodes, content
                )
            else:
                # Simple statement
                new_node = self._create_simple_statement_node(stmt, node_counter, content)
                new_nodes = [new_node]
                new_edges = []
                
                # Connect from all current nodes
                for current_node in current_nodes:
                    if current_node:
                        new_edges.append(CFGEdge(
                            source_id=current_node.id,
                            target_id=new_node.id,
                            edge_type=CFGEdgeType.SEQUENTIAL
                        ))
                
                exit_nodes = [new_node]
            
            nodes.extend(new_nodes)
            edges.extend(new_edges)
            
            return nodes, edges, exit_nodes
            
        except Exception as e:
            self.logger.warning(f"Failed to process Python statement: {e}")
            # Return current nodes as exit nodes on error
            return [], [], current_nodes
    
    def _process_python_if(self, stmt: ast.If, node_counter: List[int], 
                          current_nodes: List[CFGNode], 
                          content: str) -> Tuple[List[CFGNode], List[CFGEdge], List[CFGNode]]:
        """Process Python if statement with proper branching."""
        nodes = []
        edges = []
        
        # Create condition node
        condition_node = CFGNode(
            id=f"if_{node_counter[0]}",
            node_type=CFGNodeType.CONDITION,
            line_number=stmt.lineno,
            content=self._get_source_segment(stmt, content),
            variables_read=self._extract_variables_from_node(stmt.test),
            complexity_score=1
        )
        nodes.append(condition_node)
        node_counter[0] += 1
        
        # Connect from current nodes
        for current_node in current_nodes:
            if current_node:
                edges.append(CFGEdge(
                    source_id=current_node.id,
                    target_id=condition_node.id,
                    edge_type=CFGEdgeType.SEQUENTIAL
                ))
        
        exit_nodes = []
        
        # Process true branch
        true_current_nodes = [condition_node]
        for true_stmt in stmt.body:
            true_nodes, true_edges, true_current_nodes = self._process_python_statement(
                true_stmt, node_counter, true_current_nodes, content
            )
            nodes.extend(true_nodes)
            edges.extend(true_edges)
            
            # Mark first edge as true branch
            if true_edges and true_edges[0].source_id == condition_node.id:
                true_edges[0].edge_type = CFGEdgeType.TRUE_BRANCH
        
        exit_nodes.extend(true_current_nodes)
        
        # Process false branch (else/elif)
        if stmt.orelse:
            false_current_nodes = [condition_node]
            for false_stmt in stmt.orelse:
                false_nodes, false_edges, false_current_nodes = self._process_python_statement(
                    false_stmt, node_counter, false_current_nodes, content
                )
                nodes.extend(false_nodes)
                edges.extend(false_edges)
                
                # Mark first edge as false branch
                if false_edges and false_edges[0].source_id == condition_node.id:
                    false_edges[0].edge_type = CFGEdgeType.FALSE_BRANCH
            
            exit_nodes.extend(false_current_nodes)
        else:
            # No else branch - condition node connects to exit
            exit_nodes.append(condition_node)
        
        return nodes, edges, exit_nodes
    
    def _process_python_for(self, stmt: ast.For, node_counter: List[int], 
                           current_nodes: List[CFGNode], 
                           content: str) -> Tuple[List[CFGNode], List[CFGEdge], List[CFGNode]]:
        """Process Python for loop with proper loop edges."""
        nodes = []
        edges = []
        
        # Create loop header
        loop_header = CFGNode(
            id=f"for_{node_counter[0]}",
            node_type=CFGNodeType.LOOP_HEADER,
            line_number=stmt.lineno,
            content=self._get_source_segment(stmt, content),
            variables_written=self._extract_variables_from_node(stmt.target),
            variables_read=self._extract_variables_from_node(stmt.iter),
            complexity_score=2
        )
        nodes.append(loop_header)
        node_counter[0] += 1
        
        # Connect from current nodes
        for current_node in current_nodes:
            if current_node:
                edges.append(CFGEdge(
                    source_id=current_node.id,
                    target_id=loop_header.id,
                    edge_type=CFGEdgeType.SEQUENTIAL
                ))
        
        # Process loop body
        body_current_nodes = [loop_header]
        for body_stmt in stmt.body:
            body_nodes, body_edges, body_current_nodes = self._process_python_statement(
                body_stmt, node_counter, body_current_nodes, content
            )
            nodes.extend(body_nodes)
            edges.extend(body_edges)
            
            # Mark first edge as loop entry
            if body_edges and body_edges[0].source_id == loop_header.id:
                body_edges[0].edge_type = CFGEdgeType.LOOP_ENTRY
        
        # Add loop back edges
        for body_exit_node in body_current_nodes:
            if body_exit_node:
                edges.append(CFGEdge(
                    source_id=body_exit_node.id,
                    target_id=loop_header.id,
                    edge_type=CFGEdgeType.LOOP_BACK
                ))
        
        # Process else clause (if any)
        exit_nodes = [loop_header]  # Loop can exit without entering body
        if stmt.orelse:
            else_current_nodes = [loop_header]
            for else_stmt in stmt.orelse:
                else_nodes, else_edges, else_current_nodes = self._process_python_statement(
                    else_stmt, node_counter, else_current_nodes, content
                )
                nodes.extend(else_nodes)
                edges.extend(else_edges)
            
            exit_nodes.extend(else_current_nodes)
        
        return nodes, edges, exit_nodes
    
    def _process_python_while(self, stmt: ast.While, node_counter: List[int], 
                             current_nodes: List[CFGNode], 
                             content: str) -> Tuple[List[CFGNode], List[CFGEdge], List[CFGNode]]:
        """Process Python while loop."""
        nodes = []
        edges = []
        
        # Create loop header with condition
        loop_header = CFGNode(
            id=f"while_{node_counter[0]}",
            node_type=CFGNodeType.LOOP_HEADER,
            line_number=stmt.lineno,
            content=self._get_source_segment(stmt, content),
            variables_read=self._extract_variables_from_node(stmt.test),
            complexity_score=2
        )
        nodes.append(loop_header)
        node_counter[0] += 1
        
        # Connect from current nodes
        for current_node in current_nodes:
            if current_node:
                edges.append(CFGEdge(
                    source_id=current_node.id,
                    target_id=loop_header.id,
                    edge_type=CFGEdgeType.SEQUENTIAL
                ))
        
        # Process loop body
        body_current_nodes = [loop_header]
        for body_stmt in stmt.body:
            body_nodes, body_edges, body_current_nodes = self._process_python_statement(
                body_stmt, node_counter, body_current_nodes, content
            )
            nodes.extend(body_nodes)
            edges.extend(body_edges)
        
        # Add loop back edges
        for body_exit_node in body_current_nodes:
            if body_exit_node:
                edges.append(CFGEdge(
                    source_id=body_exit_node.id,
                    target_id=loop_header.id,
                    edge_type=CFGEdgeType.LOOP_BACK
                ))
        
        # Process else clause and exit
        exit_nodes = [loop_header]  # Can exit when condition is false
        if stmt.orelse:
            else_current_nodes = [loop_header]
            for else_stmt in stmt.orelse:
                else_nodes, else_edges, else_current_nodes = self._process_python_statement(
                    else_stmt, node_counter, else_current_nodes, content
                )
                nodes.extend(else_nodes)
                edges.extend(else_edges)
            
            exit_nodes.extend(else_current_nodes)
        
        return nodes, edges, exit_nodes
    
    def _process_python_function(self, stmt: ast.FunctionDef, node_counter: List[int], 
                                current_nodes: List[CFGNode], 
                                content: str) -> Tuple[List[CFGNode], List[CFGEdge], List[CFGNode]]:
        """Process Python function definition."""
        nodes = []
        edges = []
        
        # Create function entry node
        func_entry = CFGNode(
            id=f"func_{stmt.name}_{node_counter[0]}",
            node_type=CFGNodeType.ENTRY,
            line_number=stmt.lineno,
            content=f"def {stmt.name}(...)",
            metadata={"function_name": stmt.name, "is_function_def": True}
        )
        nodes.append(func_entry)
        node_counter[0] += 1
        
        # Connect from current nodes
        for current_node in current_nodes:
            if current_node:
                edges.append(CFGEdge(
                    source_id=current_node.id,
                    target_id=func_entry.id,
                    edge_type=CFGEdgeType.SEQUENTIAL
                ))
        
        # Process function body
        body_current_nodes = [func_entry]
        for body_stmt in stmt.body:
            body_nodes, body_edges, body_current_nodes = self._process_python_statement(
                body_stmt, node_counter, body_current_nodes, content
            )
            nodes.extend(body_nodes)
            edges.extend(body_edges)
        
        return nodes, edges, body_current_nodes
    
    def _process_python_try(self, stmt: ast.Try, node_counter: List[int], 
                           current_nodes: List[CFGNode], 
                           content: str) -> Tuple[List[CFGNode], List[CFGEdge], List[CFGNode]]:
        """Process Python try-except statement."""
        nodes = []
        edges = []
        exit_nodes = []
        
        # Process try block
        try_current_nodes = current_nodes
        for try_stmt in stmt.body:
            try_nodes, try_edges, try_current_nodes = self._process_python_statement(
                try_stmt, node_counter, try_current_nodes, content
            )
            nodes.extend(try_nodes)
            edges.extend(try_edges)
        
        exit_nodes.extend(try_current_nodes)
        
        # Process except handlers
        for handler in stmt.handlers:
            handler_entry = CFGNode(
                id=f"except_{node_counter[0]}",
                node_type=CFGNodeType.EXCEPTION_HANDLER,
                line_number=handler.lineno,
                content=f"except {handler.type.id if handler.type else 'Exception'}",
                complexity_score=1
            )
            nodes.append(handler_entry)
            node_counter[0] += 1
            
            # Connect from original current nodes (exception can occur at any point)
            for current_node in current_nodes:
                if current_node:
                    edges.append(CFGEdge(
                        source_id=current_node.id,
                        target_id=handler_entry.id,
                        edge_type=CFGEdgeType.EXCEPTION
                    ))
            
            # Process handler body
            handler_current_nodes = [handler_entry]
            for handler_stmt in handler.body:
                handler_nodes, handler_edges, handler_current_nodes = self._process_python_statement(
                    handler_stmt, node_counter, handler_current_nodes, content
                )
                nodes.extend(handler_nodes)
                edges.extend(handler_edges)
            
            exit_nodes.extend(handler_current_nodes)
        
        return nodes, edges, exit_nodes
    
    def _process_python_with(self, stmt: ast.With, node_counter: List[int], 
                            current_nodes: List[CFGNode], 
                            content: str) -> Tuple[List[CFGNode], List[CFGEdge], List[CFGNode]]:
        """Process Python with statement."""
        nodes = []
        edges = []
        
        # Create with entry node
        with_entry = CFGNode(
            id=f"with_{node_counter[0]}",
            node_type=CFGNodeType.STATEMENT,
            line_number=stmt.lineno,
            content=f"with ...",
            complexity_score=1
        )
        nodes.append(with_entry)
        node_counter[0] += 1
        
        # Connect from current nodes
        for current_node in current_nodes:
            if current_node:
                edges.append(CFGEdge(
                    source_id=current_node.id,
                    target_id=with_entry.id,
                    edge_type=CFGEdgeType.SEQUENTIAL
                ))
        
        # Process with body
        body_current_nodes = [with_entry]
        for body_stmt in stmt.body:
            body_nodes, body_edges, body_current_nodes = self._process_python_statement(
                body_stmt, node_counter, body_current_nodes, content
            )
            nodes.extend(body_nodes)
            edges.extend(body_edges)
        
        return nodes, edges, body_current_nodes
    
    def _create_simple_statement_node(self, stmt: ast.AST, node_counter: List[int], 
                                     content: str) -> CFGNode:
        """Create a node for simple statements."""
        node_type = CFGNodeType.STATEMENT
        variables_read = set()
        variables_written = set()
        
        if isinstance(stmt, ast.Assign):
            node_type = CFGNodeType.ASSIGNMENT
            variables_written = self._extract_variables_from_node(stmt.targets[0])
            variables_read = self._extract_variables_from_node(stmt.value)
        elif isinstance(stmt, ast.Return):
            node_type = CFGNodeType.RETURN
            if stmt.value:
                variables_read = self._extract_variables_from_node(stmt.value)
        elif isinstance(stmt, ast.Call):
            node_type = CFGNodeType.FUNCTION_CALL
            variables_read = self._extract_variables_from_node(stmt)
        
        return CFGNode(
            id=f"stmt_{node_counter[0]}",
            node_type=node_type,
            line_number=getattr(stmt, 'lineno', 0),
            content=self._get_source_segment(stmt, content),
            variables_read=variables_read,
            variables_written=variables_written
        )
    
    def _extract_variables_from_node(self, node: ast.AST) -> Set[str]:
        """Extract variable names from AST node."""
        variables = set()
        
        try:
            if isinstance(node, ast.Name):
                variables.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    variables.add(f"{node.value.id}.{node.attr}")
            elif isinstance(node, list):
                for item in node:
                    variables.update(self._extract_variables_from_node(item))
            elif hasattr(node, '__dict__'):
                for child in ast.iter_child_nodes(node):
                    variables.update(self._extract_variables_from_node(child))
        except Exception:
            pass  # Ignore extraction errors
        
        return variables
    
    def _get_source_segment(self, node: ast.AST, content: str) -> str:
        """Get source code segment for AST node."""
        try:
            if hasattr(ast, 'unparse'):
                return ast.unparse(node)[:200]  # Limit length
            else:
                lines = content.splitlines()
                if hasattr(node, 'lineno') and node.lineno <= len(lines):
                    return lines[node.lineno - 1].strip()[:200]
                return str(type(node).__name__)
        except Exception:
            return str(type(node).__name__)
    
    def _build_javascript_cfg(self, content: str, file_path: str) -> Tuple[List[CFGNode], List[CFGEdge]]:
        """Build CFG for JavaScript/TypeScript (simplified implementation)."""
        # For now, return basic structure - full JS parsing would require additional dependencies
        self.logger.info(f"JavaScript CFG analysis not fully implemented, using simplified analysis")
        
        nodes = []
        edges = []
        node_counter = 0
        
        # Create basic entry/exit structure
        entry_node = CFGNode(
            id=f"js_entry_{node_counter}",
            node_type=CFGNodeType.ENTRY,
            line_number=1,
            content="JS_ENTRY",
            metadata={"file_path": file_path, "language": "javascript"}
        )
        nodes.append(entry_node)
        node_counter += 1
        
        # Simple line-by-line analysis for basic patterns
        lines = content.splitlines()
        current_node = entry_node
        
        for i, line in enumerate(lines[:100], 1):  # Limit to first 100 lines
            line = line.strip()
            if not line or line.startswith('//'):
                continue
                
            node_type = CFGNodeType.STATEMENT
            if 'if' in line or 'switch' in line:
                node_type = CFGNodeType.CONDITION
            elif 'for' in line or 'while' in line:
                node_type = CFGNodeType.LOOP_HEADER
            elif 'function' in line or '=>' in line:
                node_type = CFGNodeType.FUNCTION_CALL
            
            line_node = CFGNode(
                id=f"js_stmt_{node_counter}",
                node_type=node_type,
                line_number=i,
                content=line[:200],
                variables_read=self._extract_js_variables(line),
                complexity_score=1 if node_type == CFGNodeType.STATEMENT else 2
            )
            nodes.append(line_node)
            
            edges.append(CFGEdge(
                source_id=current_node.id,
                target_id=line_node.id,
                edge_type=CFGEdgeType.SEQUENTIAL
            ))
            
            current_node = line_node
            node_counter += 1
            
            if len(nodes) > self.max_cfg_nodes // 2:  # Limit JS analysis
                break
        
        # Create exit node
        exit_node = CFGNode(
            id=f"js_exit_{node_counter}",
            node_type=CFGNodeType.EXIT,
            line_number=len(lines),
            content="JS_EXIT"
        )
        nodes.append(exit_node)
        
        if current_node:
            edges.append(CFGEdge(
                source_id=current_node.id,
                target_id=exit_node.id,
                edge_type=CFGEdgeType.SEQUENTIAL
            ))
        
        return nodes, edges
    
    def _extract_js_variables(self, line: str) -> Set[str]:
        """Extract JavaScript variable names from a line."""
        variables = set()
        
        # Simple regex patterns for JS variables
        var_patterns = [
            r'\b(var|let|const)\s+(\w+)',
            r'\b(\w+)\s*=',
            r'\b(\w+)\.',
            r'(\w+)\s*\(',
        ]
        
        for pattern in var_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                if isinstance(match, tuple):
                    variables.add(match[-1])  # Last group
                else:
                    variables.add(match)
        
        return {var for var in variables if len(var) > 1 and var.isalnum()}


class CFGAnalyzer:
    """
    Enhanced Control Flow Graph Analyzer for detecting complex PII flows.
    
    This analyzer implements STAGE 7 of the detection pipeline with:
    - Performance optimizations and timeouts
    - Enhanced pattern detection
    - Better error handling and graceful degradation
    - Comprehensive logging and statistics
    """
    
    def __init__(self, config: Config):
        """Initialize the CFG analyzer with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cfg_builder = CFGBuilder(config)
        self.stats = CFGStatistics()
        
        # Validate license tier
        if not config.is_feature_enabled("cfg_analysis"):
            raise LicenseError("CFG analysis requires Premium+ license tier")
        
        # Pattern matchers for different PII flow types
        self.pii_patterns = self._initialize_pii_patterns()
        self.confidence_adjustments = self._initialize_confidence_adjustments()
    
    def _initialize_pii_patterns(self) -> Dict[str, List[str]]:
        """Initialize PII detection patterns for CFG analysis."""
        return {
            'sensitive_vars': [
                r'(ssn|social_security|tax_id)', r'(credit_card|cc_num|card_number)',
                r'(email|email_addr|user_email)', r'(phone|mobile|telephone)',
                r'(address|home_addr|billing)', r'(dob|birth_date|birthday)',
                r'(password|passwd|pwd|secret)', r'(api_key|auth_token|bearer)',
                r'(personal_data|pii|sensitive)', r'(medical|health|diagnosis)',
                r'(financial|bank|account)', r'(biometric|fingerprint|face_id)'
            ],
            'pii_operations': [
                r'(store|save|persist|write)', r'(send|transmit|post|upload)',
                r'(log|record|track|audit)', r'(encrypt|decrypt|hash|sign)',
                r'(validate|verify|check|confirm)', r'(process|transform|convert)',
                r'(export|backup|archive|sync)', r'(delete|remove|purge|wipe)'
            ],
            'risk_contexts': [
                r'(if|when|condition|check)', r'(loop|iterate|for|while)',
                r'(try|catch|error|exception)', r'(async|await|promise|callback)',
                r'(external|api|service|remote)', r'(public|expose|visible|access)'
            ]
        }
    
    def _initialize_confidence_adjustments(self) -> Dict[str, float]:
        """Initialize confidence score adjustments based on context."""
        return {
            'conditional_exposure': 0.85,
            'loop_accumulation': 0.75,
            'transformation_chain': 0.8,
            'implicit_flow': 0.95,
            'exception_handling': 0.7,
            'async_operation': 0.8,
            'external_service': 0.9,
            'public_access': 0.9
        }
    
    def scan_file(self, file_path: str, previous_matches: List[DetectionMatch] = None) -> List[DetectionMatch]:
        """
        Scan a file using CFG analysis with comprehensive error handling.
        """
        if not previous_matches:
            previous_matches = []
        
        start_time = time.time()
        
        try:
            # Pre-flight checks
            file_size = Path(file_path).stat().st_size
            should_analyze, skip_reason = self.cfg_builder.should_analyze_file(
                file_path, previous_matches, file_size
            )
            
            if not should_analyze:
                self.logger.debug(f"Skipping CFG analysis for {file_path}: {skip_reason}")
                return []
            
            self.logger.info(f"Starting CFG analysis for {file_path} ({file_size} bytes)")
            
            # Read and analyze file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            language = detect_language(file_path)
            
            # Build CFG with timeout protection
            nodes, edges = self.cfg_builder.build_cfg_with_timeout(file_path, content, language)
            
            if not nodes:
                self.logger.warning(f"Empty CFG generated for {file_path}")
                return []
            
            # Analyze CFG for PII patterns
            cfg_matches = self._analyze_cfg_comprehensive(
                nodes, edges, content, file_path, language, previous_matches
            )
            
            # Post-processing and validation
            validated_matches = self._validate_and_enhance_matches(cfg_matches, content, previous_matches)
            
            # Update statistics
            self.stats.files_analyzed += 1
            self.stats.matches_found += len(validated_matches)
            self.stats.analysis_time += time.time() - start_time
            
            self.logger.info(f"CFG analysis completed for {file_path}: "
                           f"{len(validated_matches)} matches in {time.time() - start_time:.3f}s")
            
            return validated_matches
            
        except AnalysisTimeoutError as e:
            self.logger.warning(f"CFG analysis timeout for {file_path}: {e}")
            self.stats.errors_encountered += 1
            return []
        except Exception as e:
            self.logger.error(f"CFG analysis failed for {file_path}: {e}")
            self.stats.errors_encountered += 1
            return []
    
    def _analyze_cfg_comprehensive(self, nodes: List[CFGNode], edges: List[CFGEdge], 
                                  content: str, file_path: str, language: str,
                                  previous_matches: List[DetectionMatch]) -> List[DetectionMatch]:
        """Comprehensive CFG analysis with multiple detection patterns."""
        all_matches = []
        
        try:
            # Build graph representation for advanced analysis
            cfg_graph = self._build_networkx_graph(nodes, edges)
            
            # Pattern 1: Conditional PII Exposure (Enhanced)
            conditional_matches = self._detect_conditional_pii_exposure_enhanced(
                nodes, edges, cfg_graph, content, file_path, previous_matches
            )
            all_matches.extend(conditional_matches)
            
            # Pattern 2: Loop PII Accumulation (Enhanced)
            loop_matches = self._detect_loop_pii_accumulation_enhanced(
                nodes, edges, cfg_graph, content, file_path, previous_matches
            )
            all_matches.extend(loop_matches)
            
            # Pattern 3: Complex Transformation Chains
            transformation_matches = self._detect_transformation_chains_enhanced(
                nodes, edges, cfg_graph, content, file_path
            )
            all_matches.extend(transformation_matches)
            
            # Pattern 4: Implicit Flow Dependencies
            implicit_matches = self._detect_implicit_flows_enhanced(
                nodes, edges, cfg_graph, content, file_path
            )
            all_matches.extend(implicit_matches)
            
            # Pattern 5: Exception-based PII Exposure
            exception_matches = self._detect_exception_pii_exposure(
                nodes, edges, cfg_graph, content, file_path
            )
            all_matches.extend(exception_matches)
            
            # Pattern 6: Async/Concurrent PII Operations
            async_matches = self._detect_async_pii_operations(
                nodes, edges, cfg_graph, content, file_path
            )
            all_matches.extend(async_matches)
            
        except Exception as e:
            self.logger.error(f"Error during comprehensive CFG analysis: {e}")
        
        return all_matches
    
    def _build_networkx_graph(self, nodes: List[CFGNode], edges: List[CFGEdge]) -> nx.DiGraph:
        """Build NetworkX graph for advanced analysis."""
        graph = nx.DiGraph()
        
        # Add nodes with attributes
        for node in nodes:
            graph.add_node(node.id, 
                          node_type=node.node_type.value,
                          line_number=node.line_number,
                          content=node.content,
                          has_pii=node.has_pii_context(),
                          complexity=node.complexity_score,
                          variables_read=node.variables_read,
                          variables_written=node.variables_written)
        
        # Add edges with attributes
        for edge in edges:
            graph.add_edge(edge.source_id, edge.target_id,
                          edge_type=edge.edge_type.value,
                          condition=edge.condition,
                          weight=edge.weight)
        
        return graph
    
    def _detect_conditional_pii_exposure_enhanced(self, nodes: List[CFGNode], edges: List[CFGEdge],
                                                 graph: nx.DiGraph, content: str, file_path: str,
                                                 previous_matches: List[DetectionMatch]) -> List[DetectionMatch]:
        """Enhanced conditional PII exposure detection."""
        
        matches = []
        
        try:
            condition_nodes = [n for n in nodes if n.node_type == CFGNodeType.CONDITION]
            
            for condition_node in condition_nodes:
                # Analyze paths from condition node
                true_paths = self._get_conditional_paths(graph, condition_node.id, CFGEdgeType.TRUE_BRANCH)
                false_paths = self._get_conditional_paths(graph, condition_node.id, CFGEdgeType.FALSE_BRANCH)
                
                # Check for PII exposure in conditional paths
                true_pii_exposure = self._analyze_paths_for_pii_exposure(true_paths, nodes, previous_matches)
                false_pii_exposure = self._analyze_paths_for_pii_exposure(false_paths, nodes, previous_matches)
                
                if true_pii_exposure or false_pii_exposure:
                    confidence = self._calculate_conditional_confidence(
                        condition_node, true_pii_exposure, false_pii_exposure, content
                    )
                    
                    if confidence >= 0.6:  # Minimum confidence threshold
                        match = DetectionMatch(
                            file=str(file_path),
                            line=condition_node.line_number,
                            engine="cfg_analysis",
                            rule_id="cfg_conditional_pii_enhanced",
                            severity="HIGH" if confidence > 0.8 else "MEDIUM",
                            confidence=confidence,
                            snippet=condition_node.content,
                            description=f"Enhanced conditional PII exposure: condition controls access to sensitive data",
                            pattern_name="conditional_pii_exposure_enhanced",
                            matched_text=self._extract_pii_variables_from_content(condition_node.content),
                            risk_level=RiskLevel.HIGH if confidence > 0.8 else RiskLevel.MEDIUM,
                            metadata={
                                "cfg_node_id": condition_node.id,
                                "cfg_node_type": condition_node.node_type.value,
                                "true_branch_pii": len(true_pii_exposure),
                                "false_branch_pii": len(false_pii_exposure),
                                "pattern_type": "conditional_exposure_enhanced",
                                "analysis_method": "cfg_path_analysis"
                            }
                        )
                        matches.append(match)
            
        except Exception as e:
            self.logger.warning(f"Error in enhanced conditional PII detection: {e}")
        
        return matches
    
    def _get_conditional_paths(self, graph: nx.DiGraph, condition_node_id: str, 
                              edge_type: CFGEdgeType) -> List[List[str]]:
        """Get all paths from a conditional node following specific edge type."""
        paths = []
        
        try:
            # Find immediate successors with the specified edge type
            successors = []
            for successor in graph.successors(condition_node_id):
                edge_data = graph.edges[condition_node_id, successor]
                if edge_data.get('edge_type') == edge_type.value:
                    successors.append(successor)
            
            # For each successor, get paths until convergence or end
            for successor in successors:
                try:
                    # Use simple DFS with depth limit to avoid infinite loops
                    path = list(nx.dfs_preorder_nodes(graph, successor, depth_limit=10))
                    if len(path) > 1:  # Only include meaningful paths
                        paths.append(path)
                except nx.NetworkXError:
                    continue
            
        except Exception as e:
            self.logger.debug(f"Error getting conditional paths: {e}")
        
        return paths
    
    def _analyze_paths_for_pii_exposure(self, paths: List[List[str]], nodes: List[CFGNode],
                                       previous_matches: List[DetectionMatch]) -> List[str]:
        """Analyze paths for potential PII exposure."""
        pii_exposures = []
        
        try:
            # Create node lookup for efficiency
            node_lookup = {node.id: node for node in nodes}
            
            for path in paths:
                for node_id in path:
                    node = node_lookup.get(node_id)
                    if not node:
                        continue
                    
                    # Check if node has PII context
                    if node.has_pii_context():
                        pii_exposures.append(node_id)
                        continue
                    
                    # Check if node content suggests PII operations
                    if self._node_suggests_pii_operation(node):
                        pii_exposures.append(node_id)
                        continue
                    
                    # Cross-reference with previous matches
                    if self._node_matches_previous_detections(node, previous_matches):
                        pii_exposures.append(node_id)
            
        except Exception as e:
            self.logger.debug(f"Error analyzing paths for PII exposure: {e}")
        
        return list(set(pii_exposures))  # Remove duplicates
    
    def _node_suggests_pii_operation(self, node: CFGNode) -> bool:
        """Check if a node suggests PII-related operations."""
        content_lower = node.content.lower()
        
        # Check for PII variable patterns
        for pattern_group in self.pii_patterns.values():
            for pattern in pattern_group:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    return True
        
        return False
    
    def _node_matches_previous_detections(self, node: CFGNode, previous_matches: List[DetectionMatch]) -> bool:
        """Check if node content matches previous detections."""
        try:
            for match in previous_matches:
                if (match.line == node.line_number or 
                    (match.matched_text and match.matched_text.lower() in node.content.lower())):
                    return True
        except Exception:
            pass
        
        return False
    
    def _calculate_conditional_confidence(self, condition_node: CFGNode, 
                                        true_exposures: List[str], false_exposures: List[str],
                                        content: str) -> float:
        """Calculate confidence score for conditional PII exposure."""
        base_confidence = 0.7
        
        # Adjust based on number of PII exposures
        exposure_count = len(true_exposures) + len(false_exposures)
        confidence_boost = min(exposure_count * 0.05, 0.2)
        
        # Adjust based on condition complexity
        condition_complexity = len(re.findall(r'(and|or|not|\&\&|\|\|)', condition_node.content.lower()))
        complexity_boost = min(condition_complexity * 0.03, 0.1)
        
        # Adjust based on PII variable presence in condition
        pii_vars_in_condition = len(self._extract_pii_variables_from_content(condition_node.content))
        pii_boost = min(pii_vars_in_condition * 0.08, 0.15)
        
        final_confidence = base_confidence + confidence_boost + complexity_boost + pii_boost
        return min(final_confidence, 0.95)  # Cap at 95%
    
    def _extract_pii_variables_from_content(self, content: str) -> List[str]:
        """Extract PII variables from content using enhanced patterns."""
        pii_variables = []
        
        try:
            for pattern_list in self.pii_patterns.values():
                for pattern in pattern_list:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        pii_variables.extend([match[0] if isinstance(match, tuple) else match 
                                            for match in matches])
        except Exception as e:
            self.logger.debug(f"Error extracting PII variables: {e}")
        
        return list(set(pii_variables))  # Remove duplicates
    
    def _detect_loop_pii_accumulation_enhanced(self, nodes: List[CFGNode], edges: List[CFGEdge],
                                              graph: nx.DiGraph, content: str, file_path: str,
                                              previous_matches: List[DetectionMatch]) -> List[DetectionMatch]:
        """Enhanced loop-based PII accumulation detection."""
        matches = []
        
        try:
            loop_nodes = [n for n in nodes if n.node_type == CFGNodeType.LOOP_HEADER]
            
            for loop_node in loop_nodes:
                # Analyze loop body for PII operations
                loop_body_nodes = self._get_loop_body_nodes(graph, loop_node.id)
                
                # Check for PII accumulation patterns
                accumulation_evidence = self._analyze_loop_for_pii_accumulation(
                    loop_body_nodes, nodes, graph, previous_matches
                )
                
                if accumulation_evidence:
                    confidence = self._calculate_loop_confidence(loop_node, accumulation_evidence, content)
                    
                    if confidence >= 0.6:
                        match = DetectionMatch(
                            file=str(file_path),
                            line=loop_node.line_number,
                            engine="cfg_analysis",
                            rule_id="cfg_loop_pii_enhanced",
                            severity="MEDIUM",
                            confidence=confidence,
                            snippet=loop_node.content,
                            description=f"Enhanced loop PII accumulation: loop processes sensitive data with potential external access",
                            pattern_name="loop_pii_accumulation_enhanced",
                            matched_text=f"Loop at line {loop_node.line_number}",
                            risk_level=RiskLevel.MEDIUM,
                            metadata={
                                "cfg_node_id": loop_node.id,
                                "cfg_node_type": loop_node.node_type.value,
                                "accumulation_evidence": len(accumulation_evidence),
                                "loop_complexity": loop_node.complexity_score,
                                "pattern_type": "loop_accumulation_enhanced"
                            }
                        )
                        matches.append(match)
            
        except Exception as e:
            self.logger.warning(f"Error in enhanced loop PII detection: {e}")
        
        return matches
    
    def _get_loop_body_nodes(self, graph: nx.DiGraph, loop_header_id: str) -> List[str]:
        """Get all nodes in a loop body."""
        body_nodes = []
        
        try:
            # Find nodes reachable from loop header via LOOP_ENTRY edges
            for successor in graph.successors(loop_header_id):
                edge_data = graph.edges[loop_header_id, successor]
                if edge_data.get('edge_type') == CFGEdgeType.LOOP_ENTRY.value:
                    # Get all nodes until we hit a LOOP_BACK edge back to header
                    visited = set()
                    stack = [successor]
                    
                    while stack:
                        current = stack.pop()
                        if current in visited or current == loop_header_id:
                            continue
                        
                        visited.add(current)
                        body_nodes.append(current)
                        
                        # Add successors, but stop at loop back edges
                        for next_node in graph.successors(current):
                            edge_data = graph.edges[current, next_node]
                            if edge_data.get('edge_type') != CFGEdgeType.LOOP_BACK.value:
                                stack.append(next_node)
            
        except Exception as e:
            self.logger.debug(f"Error getting loop body nodes: {e}")
        
        return body_nodes
    
    def _analyze_loop_for_pii_accumulation(self, loop_body_nodes: List[str], all_nodes: List[CFGNode],
                                          graph: nx.DiGraph, previous_matches: List[DetectionMatch]) -> List[str]:
        """Analyze loop body for PII accumulation evidence."""
        evidence = []
        
        try:
            node_lookup = {node.id: node for node in all_nodes}
            
            for node_id in loop_body_nodes:
                node = node_lookup.get(node_id)
                if not node:
                    continue
                
                # Look for accumulation patterns
                if self._node_shows_accumulation_pattern(node):
                    evidence.append(f"accumulation_{node_id}")
                
                # Look for external access patterns
                if self._node_shows_external_access_pattern(node):
                    evidence.append(f"external_access_{node_id}")
                
                # Look for PII processing
                if node.has_pii_context() or self._node_suggests_pii_operation(node):
                    evidence.append(f"pii_processing_{node_id}")
            
        except Exception as e:
            self.logger.debug(f"Error analyzing loop for PII accumulation: {e}")
        
        return evidence
    
    def _node_shows_accumulation_pattern(self, node: CFGNode) -> bool:
        """Check if node shows data accumulation patterns."""
        accumulation_indicators = [
            r'(append|add|push|insert|collect)',
            r'(list|array|collection|set|map)',
            r'(\+=|\.add\(|\.append\(|\.push\()',
            r'(store|save|cache|buffer|queue)'
        ]
        
        content_lower = node.content.lower()
        return any(re.search(pattern, content_lower, re.IGNORECASE) 
                  for pattern in accumulation_indicators)
    
    def _node_shows_external_access_pattern(self, node: CFGNode) -> bool:
        """Check if node shows external access patterns."""
        external_indicators = [
            r'(api|http|request|post|get)',
            r'(database|db|sql|query|insert)',
            r'(file|write|save|export|output)',
            r'(log|logger|print|console|debug)',
            r'(send|transmit|upload|publish|emit)'
        ]
        
        content_lower = node.content.lower()
        return any(re.search(pattern, content_lower, re.IGNORECASE) 
                  for pattern in external_indicators)
    
    def _calculate_loop_confidence(self, loop_node: CFGNode, evidence: List[str], content: str) -> float:
        """Calculate confidence for loop PII accumulation."""
        base_confidence = 0.6
        
        # Count different types of evidence
        accumulation_count = len([e for e in evidence if e.startswith('accumulation_')])
        external_access_count = len([e for e in evidence if e.startswith('external_access_')])
        pii_processing_count = len([e for e in evidence if e.startswith('pii_processing_')])
        
        # Boost confidence based on evidence
        confidence_boost = (
            accumulation_count * 0.08 +
            external_access_count * 0.1 +
            pii_processing_count * 0.06
        )
        
        # Additional boost for complex loops
        if loop_node.complexity_score > 1:
            confidence_boost += 0.05
        
        return min(base_confidence + confidence_boost, 0.9)
    
    def _detect_transformation_chains_enhanced(self, nodes: List[CFGNode], edges: List[CFGEdge],
                                              graph: nx.DiGraph, content: str, 
                                              file_path: str) -> List[DetectionMatch]:
        """Detect complex PII transformation chains."""
        matches = []
        
        try:
            # Find transformation chains through assignment nodes
            assignment_nodes = [n for n in nodes if n.node_type == CFGNodeType.ASSIGNMENT]
            
            # Build transformation chains by following variable dependencies
            chains = self._build_transformation_chains(assignment_nodes, graph)
            
            for chain in chains:
                if self._chain_involves_pii_transformation(chain, nodes, content):
                    confidence = self._calculate_transformation_confidence(chain, nodes, content)
                    
                    if confidence >= 0.65:
                        # Find the root node of the chain
                        root_node = next((n for n in nodes if n.id == chain[0]), None)
                        if root_node:
                            match = DetectionMatch(
                                file=str(file_path),
                                line=root_node.line_number,
                                engine="cfg_analysis",
                                rule_id="cfg_transformation_chain",
                                severity="HIGH",
                                confidence=confidence,
                                snippet=root_node.content,
                                description=f"Complex PII transformation chain detected across {len(chain)} operations",
                                pattern_name="complex_pii_transformation_chain",
                                matched_text=f"Chain: {' -> '.join(chain[:3])}{'...' if len(chain) > 3 else ''}",
                                risk_level=RiskLevel.HIGH,
                                metadata={
                                    "transformation_chain": chain,
                                    "chain_length": len(chain),
                                    "pattern_type": "transformation_chain"
                                }
                            )
                            matches.append(match)
            
        except Exception as e:
            self.logger.warning(f"Error detecting transformation chains: {e}")
        
        return matches
    
    def _build_transformation_chains(self, assignment_nodes: List[CFGNode], 
                                    graph: nx.DiGraph) -> List[List[str]]:
        """Build chains of variable transformations."""
        chains = []
        
        try:
            # For each assignment node, try to build a chain
            for start_node in assignment_nodes:
                if not start_node.variables_written:
                    continue
                
                chain = [start_node.id]
                visited = {start_node.id}
                current_vars = start_node.variables_written
                
                # Follow the chain through successive assignments
                while len(chain) < 10:  # Prevent infinite chains
                    next_node_id = self._find_next_transformation_node(
                        current_vars, assignment_nodes, visited, graph
                    )
                    
                    if not next_node_id:
                        break
                    
                    chain.append(next_node_id)
                    visited.add(next_node_id)
                    
                    # Update current variables for next iteration
                    next_node = next((n for n in assignment_nodes if n.id == next_node_id), None)
                    if next_node and next_node.variables_written:
                        current_vars = next_node.variables_written
                    else:
                        break
                
                # Only keep chains with meaningful length
                if len(chain) >= 3:
                    chains.append(chain)
        
        except Exception as e:
            self.logger.debug(f"Error building transformation chains: {e}")
        
        return chains
    
    def _find_next_transformation_node(self, current_vars: Set[str], assignment_nodes: List[CFGNode],
                                      visited: Set[str], graph: nx.DiGraph) -> Optional[str]:
        """Find the next node in a transformation chain."""
        try:
            for node in assignment_nodes:
                if node.id in visited:
                    continue
                
                # Check if this node uses any of our current variables
                if node.variables_read.intersection(current_vars):
                    return node.id
            
            return None
            
        except Exception:
            return None
    
    def _chain_involves_pii_transformation(self, chain: List[str], all_nodes: List[CFGNode], 
                                         content: str) -> bool:
        """Check if transformation chain involves PII data."""
        try:
            node_lookup = {node.id: node for node in all_nodes}
            
            pii_evidence_count = 0
            for node_id in chain:
                node = node_lookup.get(node_id)
                if not node:
                    continue
                
                # Check for PII indicators
                if (node.has_pii_context() or 
                    self._node_suggests_pii_operation(node) or
                    len(self._extract_pii_variables_from_content(node.content)) > 0):
                    pii_evidence_count += 1
            
            # Chain involves PII if at least 30% of nodes have PII evidence
            return pii_evidence_count >= max(1, len(chain) * 0.3)
            
        except Exception:
            return False
    
    def _calculate_transformation_confidence(self, chain: List[str], all_nodes: List[CFGNode], 
                                           content: str) -> float:
        """Calculate confidence for transformation chain."""
        base_confidence = 0.65
        
        # Boost based on chain length
        length_boost = min((len(chain) - 3) * 0.05, 0.15)
        
        # Boost based on PII evidence
        node_lookup = {node.id: node for node in all_nodes}
        pii_nodes = sum(1 for node_id in chain 
                       if node_lookup.get(node_id) and 
                       (node_lookup[node_id].has_pii_context() or 
                        self._node_suggests_pii_operation(node_lookup[node_id])))
        
        pii_boost = min(pii_nodes * 0.08, 0.2)
        
        return min(base_confidence + length_boost + pii_boost, 0.9)
    
    def _detect_implicit_flows_enhanced(self, nodes: List[CFGNode], edges: List[CFGEdge],
                                       graph: nx.DiGraph, content: str, 
                                       file_path: str) -> List[DetectionMatch]:
        """Detect implicit information flows through control dependencies."""
        matches = []
        
        try:
            # Find condition nodes that depend on potentially sensitive data
            condition_nodes = [n for n in nodes if n.node_type == CFGNodeType.CONDITION]
            
            for condition_node in condition_nodes:
                # Check if condition uses PII variables or sensitive operations
                if self._condition_has_implicit_pii_dependency(condition_node, content):
                    # Analyze what information might be leaked through control flow
                    leakage_risk = self._analyze_implicit_flow_leakage(condition_node, graph, nodes)
                    
                    if leakage_risk > 0.7:
                        match = DetectionMatch(
                            file=str(file_path),
                            line=condition_node.line_number,
                            engine="cfg_analysis",
                            rule_id="cfg_implicit_flow",
                            severity="CRITICAL",
                            confidence=min(0.85 + (leakage_risk - 0.7) * 0.5, 0.95),
                            snippet=condition_node.content,
                            description="Implicit information flow: control flow decision depends on sensitive data",
                            pattern_name="implicit_pii_flow",
                            matched_text=condition_node.content[:100],
                            risk_level=RiskLevel.CRITICAL,
                            metadata={
                                "cfg_node_id": condition_node.id,
                                "leakage_risk_score": leakage_risk,
                                "pattern_type": "implicit_flow"
                            }
                        )
                        matches.append(match)
            
        except Exception as e:
            self.logger.warning(f"Error detecting implicit flows: {e}")
        
        return matches
    
    def _condition_has_implicit_pii_dependency(self, condition_node: CFGNode, content: str) -> bool:
        """Check if condition has implicit PII dependency."""
        # Check if condition directly uses PII variables
        if condition_node.has_pii_context():
            return True
        
        # Check for PII variables in condition content
        pii_vars = self._extract_pii_variables_from_content(condition_node.content)
        if pii_vars:
            return True
        
        # Check for sensitive operations in condition
        sensitive_patterns = [
            r'(authenticate|authorize|permission|access)',
            r'(validate|verify|check|confirm).*?(user|account|id)',
            r'(compare|equals|matches).*?(password|secret|key|token)',
            r'(role|privilege|admin|owner|creator)'
        ]
        
        content_lower = condition_node.content.lower()
        return any(re.search(pattern, content_lower, re.IGNORECASE) 
                  for pattern in sensitive_patterns)
    
    def _analyze_implicit_flow_leakage(self, condition_node: CFGNode, graph: nx.DiGraph, 
                                     all_nodes: List[CFGNode]) -> float:
        """Analyze potential for implicit information leakage."""
        leakage_score = 0.0
        
        try:
            # Analyze what happens in different branches
            true_successors = self._get_branch_successors(graph, condition_node.id, CFGEdgeType.TRUE_BRANCH)
            false_successors = self._get_branch_successors(graph, condition_node.id, CFGEdgeType.FALSE_BRANCH)
            
            # Score based on different behaviors in branches
            if len(true_successors) != len(false_successors):
                leakage_score += 0.3  # Different path lengths can leak info
            
            # Check for observable differences (timing, outputs, errors)
            node_lookup = {node.id: node for node in all_nodes}
            
            true_observables = self._count_observable_operations(true_successors, node_lookup)
            false_observables = self._count_observable_operations(false_successors, node_lookup)
            
            if abs(true_observables - false_observables) > 0:
                leakage_score += min(abs(true_observables - false_observables) * 0.2, 0.4)
            
            # Check for exception throwing differences
            true_exceptions = self._count_exception_operations(true_successors, node_lookup)
            false_exceptions = self._count_exception_operations(false_successors, node_lookup)
            
            if true_exceptions != false_exceptions:
                leakage_score += 0.3
            
        except Exception as e:
            self.logger.debug(f"Error analyzing implicit flow leakage: {e}")
        
        return min(leakage_score, 1.0)
    
    def _get_branch_successors(self, graph: nx.DiGraph, condition_id: str, 
                              branch_type: CFGEdgeType) -> List[str]:
        """Get successor nodes for a specific branch type."""
        successors = []
        
        try:
            for successor in graph.successors(condition_id):
                edge_data = graph.edges[condition_id, successor]
                if edge_data.get('edge_type') == branch_type.value:
                    # Get all reachable nodes from this successor
                    reachable = list(nx.dfs_preorder_nodes(graph, successor, depth_limit=8))
                    successors.extend(reachable)
        
        except Exception:
            pass
        
        return successors
    
    def _count_observable_operations(self, node_ids: List[str], node_lookup: Dict[str, CFGNode]) -> int:
        """Count operations that produce observable effects."""
        observable_count = 0
        
        observable_patterns = [
            r'(print|log|write|output|display)',
            r'(send|transmit|post|put|emit)',
            r'(save|store|persist|record)',
            r'(return|yield|raise|throw)'
        ]
        
        for node_id in node_ids:
            node = node_lookup.get(node_id)
            if not node:
                continue
            
            content_lower = node.content.lower()
            if any(re.search(pattern, content_lower, re.IGNORECASE) 
                  for pattern in observable_patterns):
                observable_count += 1
        
        return observable_count
    
    def _count_exception_operations(self, node_ids: List[str], node_lookup: Dict[str, CFGNode]) -> int:
        """Count operations that might throw exceptions."""
        exception_count = 0
        
        exception_patterns = [
            r'(raise|throw|error|exception)',
            r'(assert|require|expect|validate)',
            r'(check|verify|ensure|guard)'
        ]
        
        for node_id in node_ids:
            node = node_lookup.get(node_id)
            if not node:
                continue
            
            content_lower = node.content.lower()
            if any(re.search(pattern, content_lower, re.IGNORECASE) 
                  for pattern in exception_patterns):
                exception_count += 1
        
        return exception_count
    
    def _detect_exception_pii_exposure(self, nodes: List[CFGNode], edges: List[CFGEdge],
                                      graph: nx.DiGraph, content: str, 
                                      file_path: str) -> List[DetectionMatch]:
        """Detect PII exposure through exception handling."""
        matches = []
        
        try:
            exception_nodes = [n for n in nodes if n.node_type == CFGNodeType.EXCEPTION_HANDLER]
            
            for exception_node in exception_nodes:
                # Check if exception handler exposes PII
                if self._exception_handler_exposes_pii(exception_node, graph, nodes):
                    confidence = self.confidence_adjustments.get('exception_handling', 0.7)
                    
                    match = DetectionMatch(
                        file=str(file_path),
                        line=exception_node.line_number,
                        engine="cfg_analysis",
                        rule_id="cfg_exception_pii",
                        severity="MEDIUM",
                        confidence=confidence,
                        snippet=exception_node.content,
                        description="Exception handler may expose PII in error messages or logs",
                        pattern_name="exception_pii_exposure",
                        matched_text=exception_node.content[:100],
                        risk_level=RiskLevel.MEDIUM,
                        metadata={
                            "cfg_node_id": exception_node.id,
                            "pattern_type": "exception_exposure"
                        }
                    )
                    matches.append(match)
        
        except Exception as e:
            self.logger.warning(f"Error detecting exception PII exposure: {e}")
        
        return matches
    
    def _exception_handler_exposes_pii(self, exception_node: CFGNode, graph: nx.DiGraph, 
                                      all_nodes: List[CFGNode]) -> bool:
        """Check if exception handler exposes PII."""
        # Check if the handler itself contains PII operations
        if self._node_suggests_pii_operation(exception_node):
            return True
        
        # Check successor nodes for PII exposure
        try:
            successors = list(graph.successors(exception_node.id))
            node_lookup = {node.id: node for node in all_nodes}
            
            for successor_id in successors[:5]:  # Limit check to first 5 successors
                successor_node = node_lookup.get(successor_id)
                if successor_node and self._node_suggests_pii_operation(successor_node):
                    return True
        
        except Exception:
            pass
        
        return False
    
    def _detect_async_pii_operations(self, nodes: List[CFGNode], edges: List[CFGEdge],
                                    graph: nx.DiGraph, content: str, 
                                    file_path: str) -> List[DetectionMatch]:
        """Detect PII operations in async/concurrent contexts."""
        matches = []
        
        try:
            # Look for async-related nodes
            async_nodes = [n for n in nodes if self._node_is_async_related(n)]
            
            for async_node in async_nodes:
                # Check if async operation involves PII
                if (async_node.has_pii_context() or 
                    self._node_suggests_pii_operation(async_node) or
                    self._async_context_suggests_pii_risk(async_node, graph, nodes)):
                    
                    confidence = self.confidence_adjustments.get('async_operation', 0.8)
                    
                    match = DetectionMatch(
                        file=str(file_path),
                        line=async_node.line_number,
                        engine="cfg_analysis",
                        rule_id="cfg_async_pii",
                        severity="HIGH",
                        confidence=confidence,
                        snippet=async_node.content,
                        description="Async operation may expose PII through concurrent access or timing",
                        pattern_name="async_pii_operation",
                        matched_text=async_node.content[:100],
                        risk_level=RiskLevel.HIGH,
                        metadata={
                            "cfg_node_id": async_node.id,
                            "pattern_type": "async_operation"
                        }
                    )
                    matches.append(match)
        
        except Exception as e:
            self.logger.warning(f"Error detecting async PII operations: {e}")
        
        return matches
    
    def _node_is_async_related(self, node: CFGNode) -> bool:
        """Check if node is related to async operations."""
        async_patterns = [
            r'(async|await|promise|future|thread)',
            r'(callback|then|catch|finally)',
            r'(setTimeout|setInterval|requestAnimationFrame)',
            r'(concurrent|parallel|background|queue)'
        ]
        
        content_lower = node.content.lower()
        return any(re.search(pattern, content_lower, re.IGNORECASE) 
                  for pattern in async_patterns)
    
    def _async_context_suggests_pii_risk(self, async_node: CFGNode, graph: nx.DiGraph, 
                                        all_nodes: List[CFGNode]) -> bool:
        """Check if async context suggests PII risk."""
        try:
            # Check surrounding nodes for PII context
            predecessors = list(graph.predecessors(async_node.id))
            successors = list(graph.successors(async_node.id))
            
            node_lookup = {node.id: node for node in all_nodes}
            
            # Check if nearby nodes involve PII
            nearby_nodes = predecessors[:3] + successors[:3]
            for node_id in nearby_nodes:
                node = node_lookup.get(node_id)
                if node and (node.has_pii_context() or self._node_suggests_pii_operation(node)):
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _validate_and_enhance_matches(self, matches: List[DetectionMatch], content: str,
                                     previous_matches: List[DetectionMatch]) -> List[DetectionMatch]:
        """Validate and enhance CFG matches before returning."""
        validated_matches = []
        
        try:
            for match in matches:
                # Skip if confidence is too low
                if match.confidence < 0.6:
                    continue
                
                # Enhance match with additional context
                enhanced_match = self._enhance_match_with_context(match, content, previous_matches)
                
                # Validate match doesn't duplicate existing detections
                if not self._match_duplicates_previous(enhanced_match, previous_matches):
                    validated_matches.append(enhanced_match)
        
        except Exception as e:
            self.logger.warning(f"Error validating matches: {e}")
            return matches  # Return original matches if validation fails
        
        return validated_matches
    
    def _enhance_match_with_context(self, match: DetectionMatch, content: str,
                                   previous_matches: List[DetectionMatch]) -> DetectionMatch:
        """Enhance match with additional context information."""
        try:
            # Add line context
            lines = content.splitlines()
            if 1 <= match.line <= len(lines):
                context_lines = []
                start_line = max(1, match.line - 2)
                end_line = min(len(lines), match.line + 2)
                
                for i in range(start_line, end_line + 1):
                    prefix = ">>> " if i == match.line else "    "
                    context_lines.append(f"{prefix}{i:4d}: {lines[i-1]}")
                
                match.metadata["context_lines"] = "\n".join(context_lines)
            
            # Add related previous matches
            related_matches = [
                m for m in previous_matches 
                if abs(m.line - match.line) <= 5 and m.confidence >= 0.6
            ]
            
            if related_matches:
                match.metadata["related_detections"] = len(related_matches)
                match.metadata["related_engines"] = list(set(m.engine for m in related_matches))
            
            # Enhance description based on pattern type
            pattern_type = match.metadata.get("pattern_type", "")
            if pattern_type and pattern_type in self.confidence_adjustments:
                base_desc = match.description
                match.description = f"{base_desc} (CFG pattern: {pattern_type})"
            
        except Exception as e:
            self.logger.debug(f"Error enhancing match context: {e}")
        
        return match
    
    def _match_duplicates_previous(self, match: DetectionMatch, 
                                  previous_matches: List[DetectionMatch]) -> bool:
        """Check if match duplicates a previous detection."""
        try:
            for prev_match in previous_matches:
                # Check for same line and similar content
                if (match.line == prev_match.line and 
                    match.matched_text and prev_match.matched_text and
                    match.matched_text.lower() in prev_match.matched_text.lower()):
                    return True
                
                # Check for very similar snippets
                if (match.snippet and prev_match.snippet and
                    len(match.snippet) > 20 and len(prev_match.snippet) > 20 and
                    match.snippet[:50].lower() == prev_match.snippet[:50].lower()):
                    return True
            
            return False
            
        except Exception:
            return False
    
    def get_statistics(self) -> CFGStatistics:
        """Get CFG analysis statistics."""
        # Combine stats from both builder and analyzer
        combined_stats = CFGStatistics()
        combined_stats.files_analyzed = self.stats.files_analyzed
        combined_stats.files_skipped = self.cfg_builder.stats.files_skipped
        combined_stats.total_nodes_created = self.cfg_builder.stats.total_nodes_created
        combined_stats.total_edges_created = self.cfg_builder.stats.total_edges_created
        combined_stats.analysis_time = self.stats.analysis_time
        combined_stats.matches_found = self.stats.matches_found
        combined_stats.errors_encountered = self.stats.errors_encountered + self.cfg_builder.stats.errors_encountered
        
        return combined_stats


# Factory function for easy integration
def create_cfg_analyzer(config: Config) -> CFGAnalyzer:
    """Factory function to create a configured CFG analyzer."""
    try:
        return CFGAnalyzer(config)
    except LicenseError as e:
        logging.getLogger(__name__).warning(f"CFG analyzer creation failed: {e}")
        raise
    except Exception as e:
        logging.getLogger(__name__).error(f"Unexpected error creating CFG analyzer: {e}")
        raise DetectionError(f"CFG analyzer creation failed: {e}")


# Integration helper for the main detection pipeline
class CFGStage:
    """
    CFG Analysis Stage for integration with Levox detection pipeline.
    
    This class provides the interface expected by the main detection engine
    and handles all CFG analysis workflow.
    """
    
    def __init__(self, config: Config):
        """Initialize CFG stage."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.analyzer = create_cfg_analyzer(config)
        self.stage_name = "cfg_analysis"
        
    def is_enabled(self) -> bool:
        """Check if CFG analysis is enabled."""
        return self.config.is_feature_enabled("cfg_analysis")
    
    def scan_file(self, file_path: str, previous_results: List[DetectionMatch] = None) -> List[DetectionMatch]:
        """
        Scan file using CFG analysis.
        
        This method is called by the main detection engine as part of the pipeline.
        """
        try:
            if not self.is_enabled():
                return []
            
            results = self.analyzer.scan_file(file_path, previous_results or [])
            
            # Tag all results with CFG stage identifier
            for result in results:
                if "stage" not in result.metadata:
                    result.metadata["stage"] = self.stage_name
                if "stage_order" not in result.metadata:
                    result.metadata["stage_order"] = 7  # CFG is stage 7
            
            return results
            
        except Exception as e:
            self.logger.error(f"CFG stage failed for {file_path}: {e}")
            return []  # Graceful degradation
    
    def get_stage_info(self) -> Dict[str, Any]:
        """Get information about this stage."""
        return {
            "stage_name": self.stage_name,
            "stage_order": 7,
            "description": "Control Flow Graph Analysis for complex PII flow detection",
            "license_required": "Premium+",
            "enabled": self.is_enabled(),
            "statistics": self.analyzer.get_statistics().__dict__ if self.is_enabled() else None
        } 