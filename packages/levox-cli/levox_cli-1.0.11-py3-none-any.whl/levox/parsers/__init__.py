"""
Parser factory and utilities for multi-language parsing.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.config import Config

from .base import BaseParser, TREE_SITTER_AVAILABLE
from .python_parser import PythonParser
from .javascript_parser import JavaScriptParser, TypeScriptParser
from .java_parser import JavaParser

logger = logging.getLogger(__name__)

# Language file extension mappings
LANGUAGE_EXTENSIONS = {
    '.py': 'python',
    '.pyw': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.mjs': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.java': 'java',
}

# Parser class mappings
PARSER_CLASSES = {
    'python': PythonParser,
    'javascript': JavaScriptParser,
    'typescript': TypeScriptParser,
    'java': JavaParser,
}


def get_parser(file_path: Path | str, content: Optional[str] = None, config: Optional['Config'] = None) -> Optional[BaseParser]:
    """
    Get appropriate parser for a file.
    
    Args:
        file_path: Path to the file
        content: Optional file content (not used currently but available for content-based detection)
        config: Optional configuration object for parser settings
    
    Returns:
        Parser instance or None if unsupported language
    """
    if not TREE_SITTER_AVAILABLE:
        # Tree-Sitter not available, but we can still create parsers with fallback
        logger.debug("Tree-Sitter not available, will use fallback parsers if enabled")
        # Continue to allow parser creation with fallback
    
    # Normalize to Path
    file_path = Path(file_path)
    # Determine language from file extension
    language = detect_language(file_path)
    if not language:
        logger.debug(f"Unsupported file type: {file_path.suffix}")
        return None
    
    # Get parser class
    parser_class = PARSER_CLASSES.get(language)
    if not parser_class:
        logger.debug(f"No parser available for language: {language}")
        return None
    
    try:
        # Create parser instance with config
        parser = parser_class(config)
        if parser._parser is None:
            # Reduce noise: this can be normal if grammars are not installed; fall back silently
            logger.debug(f"Parser unavailable for {language}; falling back to non-AST analysis")
            return None
        
        return parser
        
    except Exception as e:
        logger.error(f"Failed to create parser for {language}: {e}")
        return None


def detect_language(file_path: Path | str) -> Optional[str]:
    """
    Detect programming language from file path.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Language name or None if not detected
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    return LANGUAGE_EXTENSIONS.get(suffix)


def get_supported_languages() -> Dict[str, Any]:
    """
    Return supported languages and a best-effort availability probe without
    fully initializing parsers. This avoids noisy logs during status checks.
    """
    support_info = {
        'tree_sitter_available': TREE_SITTER_AVAILABLE,
        'languages': {},
        'extensions': LANGUAGE_EXTENSIONS
    }

    for language, parser_class in PARSER_CLASSES.items():
        available = False
        error: Optional[str] = None
        if TREE_SITTER_AVAILABLE:
            try:
                # Cheap probe: use tree_sitter_languages.get_language if present
                try:
                    from tree_sitter_languages import get_language as _get_lang
                except Exception:
                    _get_lang = None  # type: ignore

                if _get_lang is not None:
                    try:
                        # Map internal names to likely aliases
                        alias = 'py' if language == 'python' else 'js' if language == 'javascript' else 'ts' if language == 'typescript' else 'java' if language == 'java' else language
                        lang_obj = _get_lang(alias)
                        available = lang_obj is not None
                    except Exception as e:
                        error = str(e)
                
                # If that failed, try module fallbacks without constructing Parser
                if not available:
                    try:
                        if language == 'python':
                            import tree_sitter_python  # noqa: F401
                            available = True
                        elif language == 'javascript':
                            import tree_sitter_javascript  # noqa: F401
                            available = True
                        elif language == 'typescript':
                            import tree_sitter_typescript  # noqa: F401
                            available = True
                        elif language == 'java':
                            import tree_sitter_java  # noqa: F401
                            available = True
                    except Exception as e:
                        error = str(e)
            except Exception as e:
                error = str(e)

        support_info['languages'][language] = {
            'available': bool(available),
            'parser_class': parser_class.__name__,
            'extensions': [ext for ext, lang in LANGUAGE_EXTENSIONS.items() if lang == language],
            **({'error': error} if error else {})
        }

    return support_info


def is_supported_file(file_path: Path | str) -> bool:
    """
    Check if a file type is supported for parsing.
    
    Args:
        file_path: Path to the file
    
    Returns:
        True if file type is supported
    """
    return detect_language(file_path) is not None


__all__ = [
    'BaseParser',
    'PythonParser', 
    'JavaScriptParser',
    'TypeScriptParser',
    'JavaParser',
    'get_parser',
    'detect_language',
    'get_supported_languages',
    'is_supported_file',
    'TREE_SITTER_AVAILABLE'
]
