"""
Java language parser for Levox using Tree-Sitter.
Provides AST analysis capabilities for Java source code to detect PII and GDPR violations.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from .base import BaseParser, ParsedNode, StringLiteral, Comment, ImportStatement, VariableDeclaration, FunctionDefinition, ClassDefinition

logger = logging.getLogger(__name__)


@dataclass
class JavaParsedNode(ParsedNode):
    """Java-specific parsed node with additional metadata."""
    modifiers: List[str] = None
    annotations: List[str] = None
    visibility: str = "package"  # public, private, protected, package
    
    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = []
        if self.annotations is None:
            self.annotations = []


class JavaParser(BaseParser):
    """Java language parser using Tree-Sitter grammar."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.language_name = "java"
        self.file_extensions = ['.java']
        
        # Initialize Tree-Sitter parser for Java
        self._initialize_parser()
        if self._init_tree_sitter():
            try:
                # Load Java grammar
                self._parser.set_language(self._get_java_language())
                logger.debug("Java parser initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Java parser: {e}")
                self._parser = None
        else:
            logger.warning("Tree-Sitter not available for Java parsing")
    
    def _get_java_language(self):
        """Get Java language grammar from tree-sitter-languages."""
        try:
            from tree_sitter_languages import get_language
            # Suppress deprecation warning for now until tree-sitter-languages is updated
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")
                return get_language("java")
        except ImportError:
            logger.error("tree-sitter-languages not available for Java")
            return None
        except Exception as e:
            logger.error(f"Failed to load Java language: {e}")
            return None
    
    def parse_file(self, file_path: Path, content: str) -> List[ParsedNode]:
        """Parse Java source file and return structured nodes."""
        if not self._parser:
            logger.warning("Java parser not available")
            return []
        
        try:
            # Parse the content
            tree = self._parser.parse(bytes(content, 'utf8'))
            if not tree.root_node:
                logger.warning(f"Failed to parse Java file: {file_path}")
                return []
            
            # Extract nodes
            nodes = []
            self._extract_nodes(tree.root_node, nodes, content)
            
            logger.debug(f"Parsed {len(nodes)} nodes from Java file: {file_path}")
            return nodes
            
        except Exception as e:
            logger.error(f"Error parsing Java file {file_path}: {e}")
            return []
    
    def _extract_nodes(self, node, nodes: List[ParsedNode], content: str):
        """Recursively extract nodes from the AST."""
        try:
            # Extract node information
            node_text = self._get_node_text(node, content)
            
            # Create parsed node
            parsed_node = JavaParsedNode(
                node_type=node.type,
                text=node_text,
                start_line=node.start_point[0] + 1,  # Tree-sitter uses 0-based
                start_col=node.start_point[1],
                end_line=node.end_point[0] + 1,
                end_col=node.end_point[1],
                modifiers=self._extract_modifiers(node, content),
                annotations=self._extract_annotations(node, content),
                visibility=self._extract_visibility(node, content)
            )
            
            # Add to nodes list if it's a significant node type
            if self._is_significant_node(node.type):
                nodes.append(parsed_node)
            
            # Recursively process children
            for child in node.children:
                self._extract_nodes(child, nodes, content)
                
        except Exception as e:
            logger.debug(f"Error extracting node: {e}")
    
    def _is_significant_node(self, node_type: str) -> bool:
        """Check if a node type is significant for analysis."""
        significant_types = {
            'class_declaration',
            'interface_declaration',
            'method_declaration',
            'constructor_declaration',
            'field_declaration',
            'variable_declarator',
            'string_literal',
            'comment',
            'import_declaration',
            'annotation',
            'enum_declaration',
            'package_declaration'
        }
        return node_type in significant_types
    
    def _extract_modifiers(self, node, content: str) -> List[str]:
        """Extract access modifiers and other modifiers from a node."""
        modifiers = []
        
        # Look for modifiers in the node's children
        for child in node.children:
            if child.type in ['public', 'private', 'protected', 'static', 'final', 'abstract', 'synchronized', 'volatile', 'transient', 'native']:
                modifier_text = self._get_node_text(child, content)
                if modifier_text:
                    modifiers.append(modifier_text)
        
        return modifiers
    
    def _extract_annotations(self, node, content: str) -> List[str]:
        """Extract annotations from a node."""
        annotations = []
        
        # Look for annotation nodes
        for child in node.children:
            if child.type == 'annotation':
                annotation_text = self._get_node_text(child, content)
                if annotation_text:
                    annotations.append(annotation_text)
        
        return annotations
    
    def _extract_visibility(self, node, content: str) -> str:
        """Extract visibility modifier from a node."""
        for child in node.children:
            if child.type in ['public', 'private', 'protected']:
                return child.type
        return "package"
    
    def extract_strings(self, file_path: Path, content: str) -> List[StringLiteral]:
        """Extract all string literals from Java source code."""
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
            
            return strings
            
        except Exception as e:
            logger.error(f"Error extracting strings from Java file {file_path}: {e}")
            return []
    

    
    def _extract_string_nodes(self, node, strings: List[StringLiteral], content: str):
        """Recursively extract string literal nodes."""
        try:
            if node.type == 'string_literal':
                # Extract string content
                string_text = self._get_node_text(node, content)
                if string_text:
                    # Remove quotes and handle escape sequences
                    raw_value = string_text
                    value = self._process_java_string(string_text)
                    
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
    
    def _process_java_string(self, string_text: str) -> str:
        """Process Java string literal, handling escape sequences."""
        if not string_text:
            return ""
        
        # Remove surrounding quotes
        if string_text.startswith('"') and string_text.endswith('"'):
            string_text = string_text[1:-1]
        elif string_text.startswith("'") and string_text.endswith("'"):
            string_text = string_text[1:-1]
        
        # Handle common Java escape sequences
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
                if parent.type == 'variable_declarator':
                    return 'variable_declaration'
                elif parent.type == 'method_declaration':
                    return 'method_body'
                elif parent.type == 'class_declaration':
                    return 'class_body'
                elif parent.type == 'annotation':
                    return 'annotation'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def extract_comments(self, file_path: Path, content: str) -> List[Comment]:
        """Extract all comments from Java source code."""
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
            logger.error(f"Error extracting comments from Java file {file_path}: {e}")
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
        """Determine the type of Java comment."""
        if comment_text.startswith('//'):
            return 'line'
        elif comment_text.startswith('/*') and comment_text.endswith('*/'):
            return 'block'
        elif comment_text.startswith('/**') and comment_text.endswith('*/'):
            return 'javadoc'
        else:
            return 'unknown'
    
    def extract_imports(self, file_path: Path, content: str) -> List[ImportStatement]:
        """Extract all import statements from Java source code."""
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
            logger.error(f"Error extracting imports from Java file {file_path}: {e}")
            return []
    
    def _extract_import_nodes(self, node, imports: List[ImportStatement], content: str):
        """Recursively extract import statement nodes."""
        try:
            if node.type == 'import_declaration':
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
        """Parse Java import statement to extract components."""
        try:
            # Remove 'import' keyword
            if import_text.startswith('import '):
                import_text = import_text[7:]
            
            # Handle static imports
            is_static = import_text.startswith('static ')
            if is_static:
                import_text = import_text[7:]
                import_type = 'static'
            else:
                import_type = 'standard'
            
            # Handle wildcard imports
            if import_text.endswith('.*'):
                module = import_text[:-2]
                name = '*'
                alias = ''
            else:
                # Regular import
                parts = import_text.split(' as ')
                if len(parts) > 1:
                    module = parts[0]
                    alias = parts[1]
                    name = module.split('.')[-1]
                else:
                    module = import_text
                    name = module.split('.')[-1]
                    alias = ''
            
            return {
                'module': module,
                'name': name,
                'alias': alias,
                'type': import_type
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
        """Extract variable declarations from Java source code."""
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
            logger.error(f"Error extracting variables from Java file {file_path}: {e}")
            return []
    
    def _extract_variable_nodes(self, node, variables: List[VariableDeclaration], content: str):
        """Recursively extract variable declaration nodes."""
        try:
            if node.type == 'variable_declarator':
                # Get variable name and type
                var_name = ""
                var_type = ""
                modifiers = []
                
                # Look for variable name
                for child in node.children:
                    if child.type == 'identifier':
                        var_name = self._get_node_text(child, content)
                        break
                
                # Look for parent field_declaration to get type and modifiers
                parent = node.parent
                if parent and parent.type == 'field_declaration':
                    for child in parent.children:
                        if child.type == 'primitive_type' or child.type == 'type_identifier':
                            var_type = self._get_node_text(child, content)
                        elif child.type in ['public', 'private', 'protected', 'static', 'final']:
                            modifier = self._get_node_text(child, content)
                            if modifier:
                                modifiers.append(modifier)
                
                if var_name:
                    variable = VariableDeclaration(
                        name=var_name,
                        var_type=var_type,
                        modifiers=modifiers,
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
                if parent.type == 'field_declaration':
                    return 'class_field'
                elif parent.type == 'local_variable_declaration':
                    return 'local_variable'
                elif parent.type == 'parameter':
                    return 'parameter'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def extract_functions(self, file_path: Path, content: str) -> List[FunctionDefinition]:
        """Extract function/method definitions from Java source code."""
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
            logger.error(f"Error extracting functions from Java file {file_path}: {e}")
            return []
    
    def _extract_function_nodes(self, node, functions: List[FunctionDefinition], content: str):
        """Recursively extract function definition nodes."""
        try:
            if node.type == 'method_declaration':
                # Extract method information
                method_name = ""
                return_type = ""
                modifiers = []
                parameters = []
                
                # Get method name
                for child in node.children:
                    if child.type == 'identifier':
                        method_name = self._get_node_text(child, content)
                    elif child.type == 'primitive_type' or child.type == 'type_identifier':
                        return_type = self._get_node_text(child, content)
                    elif child.type in ['public', 'private', 'protected', 'static', 'final', 'abstract', 'synchronized']:
                        modifier = self._get_node_text(child, content)
                        if modifier:
                            modifiers.append(modifier)
                    elif child.type == 'formal_parameters':
                        parameters = self._extract_parameters(child, content)
                
                if method_name:
                    function = FunctionDefinition(
                        name=method_name,
                        return_type=return_type,
                        parameters=parameters,
                        modifiers=modifiers,
                        start_line=node.start_point[0] + 1,
                        start_col=node.start_point[1],
                        end_line=node.end_point[0] + 1,
                        end_col=node.end_point[1],
                        context='class_method'
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
                if child.type == 'formal_parameter':
                    # Look for parameter name
                    for param_child in child.children:
                        if param_child.type == 'identifier':
                            param_name = self._get_node_text(param_child, content)
                            if param_name:
                                parameters.append(param_name)
                            break
        except Exception as e:
            logger.debug(f"Error extracting parameters: {e}")
        
        return parameters
    
    def extract_classes(self, file_path: Path, content: str) -> List[ClassDefinition]:
        """Extract class definitions from Java source code."""
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
            logger.error(f"Error extracting classes from Java file {file_path}: {e}")
            return []
    
    def _extract_class_nodes(self, node, classes: List[ClassDefinition], content: str):
        """Recursively extract class definition nodes."""
        try:
            if node.type == 'class_declaration':
                # Extract class information
                class_name = ""
                modifiers = []
                superclass = ""
                interfaces = []
                
                # Get class name
                for child in node.children:
                    if child.type == 'identifier':
                        class_name = self._get_node_text(child, content)
                    elif child.type in ['public', 'private', 'protected', 'abstract', 'final']:
                        modifier = self._get_node_text(child, content)
                        if modifier:
                            modifiers.append(modifier)
                    elif child.type == 'superclass':
                        superclass = self._get_node_text(child, content)
                    elif child.type == 'super_interfaces':
                        interfaces = self._extract_interfaces(child, content)
                
                if class_name:
                    class_def = ClassDefinition(
                        name=class_name,
                        modifiers=modifiers,
                        superclass=superclass,
                        interfaces=interfaces,
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
    
    def _extract_interfaces(self, interfaces_node, content: str) -> List[str]:
        """Extract interface names from super interfaces node."""
        interfaces = []
        
        try:
            for child in interfaces_node.children:
                if child.type == 'type_identifier':
                    interface_name = self._get_node_text(child, content)
                    if interface_name:
                        interfaces.append(interface_name)
        except Exception as e:
            logger.debug(f"Error extracting interfaces: {e}")
        
        return interfaces
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get information about the Java parser capabilities."""
        return {
            'language': 'java',
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
