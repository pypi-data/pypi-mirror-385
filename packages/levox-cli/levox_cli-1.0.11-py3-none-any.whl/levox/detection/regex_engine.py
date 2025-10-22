"""
Enterprise-grade optimized regex detection engine for PII patterns.
Provides high-performance scanning with comprehensive logging, telemetry, and security features.
"""

import asyncio
import re
import time
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Iterator, Union, Set
from threading import Lock

from ..core.config import DetectionPattern, RiskLevel
from ..core.exceptions import DetectionError
from ..models.detection_result import DetectionMatch
from ..utils.performance import PerformanceMonitor
from ..utils.validators import Validator


@dataclass
class RegexMatch:
    """Raw regex match result with enhanced metadata."""
    pattern_name: str
    matched_text: str
    start_pos: int
    end_pos: int
    line_number: int
    column_start: int
    column_end: int
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    detection_timestamp: float = field(default_factory=time.time)


@dataclass 
class ScanContext:
    """Context information for a scan operation."""
    correlation_id: str
    file_path: Optional[Path]
    language: str
    scan_start_time: float
    active_patterns: List[str]
    content_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            'correlation_id': self.correlation_id,
            'file_path': str(self.file_path) if self.file_path else None,
            'language': self.language,
            'scan_start_time': self.scan_start_time,
            'active_patterns': self.active_patterns,
            'content_size': self.content_size
        }


@dataclass
class PatternMetadata:
    """Metadata for compiled patterns."""
    pattern: DetectionPattern
    compiled_regex: re.Pattern
    version: str
    compilation_time: float
    usage_count: int = 0
    last_used: Optional[float] = None
    
    def update_usage(self) -> None:
        """Update usage statistics."""
        self.usage_count += 1
        self.last_used = time.time()


class RegexEngine:
    """
    High-performance regex detection engine with enterprise features.
    
    Provides concurrent scanning, comprehensive logging, performance monitoring,
    and secure handling of PII data with proper sanitization.
    """
    
    def __init__(
        self, 
        patterns: List[DetectionPattern],
        max_workers: int = 4,
        max_file_size: int = 50 * 1024 * 1024,  # 50MB
        enable_async: bool = True
    ) -> None:
        """
        Initialize the regex engine with enterprise features.
        
        Args:
            patterns: List of detection patterns to compile
            max_workers: Maximum number of concurrent workers
            max_file_size: Maximum file size to process (bytes)
            enable_async: Enable asynchronous processing
        """
        self.patterns = patterns
        self.max_workers = max_workers
        self.max_file_size = max_file_size
        self.enable_async = enable_async
        
        # Thread-safe storage for compiled patterns
        self.compiled_patterns: Dict[str, PatternMetadata] = {}
        self._pattern_lock = Lock()
        
        # Performance and monitoring
        self.performance_monitor = PerformanceMonitor()
        self._scan_history: List[Dict[str, Any]] = []
        self._audit_trail: List[Dict[str, Any]] = []
        self._validator = Validator()
        
        # Logging setup
        self.logger = logging.getLogger(f"{__name__}.RegexEngine")
        
        # Initialize engine
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize the engine with pattern compilation and validation."""
        start_time = time.time()
        
        try:
            self.logger.info("Initializing RegexEngine", extra={
                'pattern_count': len(self.patterns),
                'max_workers': self.max_workers,
                'async_enabled': self.enable_async
            })
            
            # Validate and compile patterns
            validation_errors = self._validate_and_compile_patterns()
            
            if validation_errors:
                error_msg = f"Pattern validation failed: {len(validation_errors)} errors"
                self.logger.error(error_msg, extra={'errors': validation_errors})
                raise DetectionError(error_msg)
            
            init_time = time.time() - start_time
            self.logger.info("RegexEngine initialized successfully", extra={
                'initialization_time': init_time,
                'compiled_patterns': len(self.compiled_patterns)
            })
            
        except Exception as e:
            self.logger.error("Failed to initialize RegexEngine", extra={'error': str(e)})
            raise DetectionError(f"Engine initialization failed: {e}")
    
    def _validate_and_compile_patterns(self) -> List[str]:
        """
        Validate and compile all regex patterns with comprehensive error handling.
        
        Returns:
            List of validation errors (empty if all patterns are valid)
        """
        validation_errors = []
        compiled_count = 0
        
        for pattern in self.patterns:
            try:
                if not pattern.enabled:
                    continue
                
                # SECURITY: Validate regex pattern to prevent ReDoS attacks
                self._validate_regex_pattern(pattern.regex)
                
                # Validate regex syntax
                compiled_regex = re.compile(
                    pattern.regex,
                    flags=re.MULTILINE | re.IGNORECASE
                )
                
                # Create pattern metadata
                pattern_metadata = PatternMetadata(
                    pattern=pattern,
                    compiled_regex=compiled_regex,
                    version=getattr(pattern, 'version', '1.0'),
                    compilation_time=time.time()
                )
                
                with self._pattern_lock:
                    self.compiled_patterns[pattern.name] = pattern_metadata
                
                compiled_count += 1
                
                self.logger.debug("Pattern compiled successfully", extra={
                    'pattern_name': pattern.name,
                    'pattern_version': pattern_metadata.version,
                    'risk_level': pattern.risk_level.name,
                    'confidence': pattern.confidence
                })
                
            except re.error as e:
                error_msg = f"Pattern '{pattern.name}': Invalid regex - {e}"
                validation_errors.append(error_msg)
                # SECURITY: Sanitize regex pattern for logging to prevent PII exposure
                sanitized_regex = self._sanitize_for_logging(pattern.regex)
                self.logger.warning("Pattern compilation failed", extra={
                    'pattern_name': pattern.name,
                    'error': str(e),
                    'regex': sanitized_regex[:100]  # Truncate for logging
                })
                
            except Exception as e:
                error_msg = f"Pattern '{pattern.name}': Compilation error - {e}"
                validation_errors.append(error_msg)
                self.logger.error("Unexpected pattern error", extra={
                    'pattern_name': pattern.name,
                    'error': str(e)
                })
        
        self.logger.info("Pattern compilation completed", extra={
            'total_patterns': len(self.patterns),
            'compiled_patterns': compiled_count,
            'validation_errors': len(validation_errors)
        })
        
        return validation_errors
    
    async def scan_file_async(
        self, 
        file_path: Path, 
        content: str,
        language: str = "unknown",
        correlation_id: Optional[str] = None
    ) -> List[DetectionMatch]:
        """
        Asynchronously scan a single file for PII patterns.
        
        Args:
            file_path: Path to the file being scanned
            content: File content to scan
            language: Programming language for pattern filtering
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            List of detection matches found in the file
        """
        if not self.enable_async:
            return self.scan_file(file_path, content, language, correlation_id)
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.scan_file,
            file_path,
            content,
            language,
            correlation_id
        )
    
    def scan_file(
        self, 
        file_path: Path, 
        content: str,
        language: str = "unknown",
        correlation_id: Optional[str] = None
    ) -> List[DetectionMatch]:
        """
        Scan a single file for PII patterns with comprehensive logging.
        
        Args:
            file_path: Path to the file being scanned
            content: File content to scan
            language: Programming language for pattern filtering
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            List of detection matches found in the file
            
        Raises:
            DetectionError: If scanning fails or file is too large
        """
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Validate file size
        content_size = len(content.encode('utf-8'))
        if content_size > self.max_file_size:
            raise DetectionError(
                f"File {file_path} too large: {content_size} bytes "
                f"(max: {self.max_file_size} bytes)"
            )
        
        # Create scan context
        scan_context = ScanContext(
            correlation_id=correlation_id,
            file_path=file_path,
            language=language,
            scan_start_time=time.time(),
            active_patterns=self._get_active_pattern_names(language),
            content_size=content_size
        )
        
        self.logger.info("Starting file scan", extra=scan_context.to_dict())
        
        try:
            matches = self._perform_scan(content, language, scan_context)
            
            # Convert to unified DetectionMatch format
            unified_matches = self._convert_to_unified_matches(matches, file_path, content, language)
            # Enrich secrets if configured via environment/configurable flags later in pipeline
            
            scan_duration = time.time() - scan_context.scan_start_time
            
            # Log scan completion
            self.logger.info("File scan completed", extra={
                **scan_context.to_dict(),
                'matches_found': len(unified_matches),
                'scan_duration': scan_duration,
                'matches_per_kb': len(unified_matches) / (content_size / 1024) if content_size > 0 else 0
            })
            
            # Record scan history
            self._record_scan_history(scan_context, unified_matches, scan_duration)
            
            # Update performance metrics
            self.performance_monitor.record_operation(
                'file_scan', scan_duration, len(unified_matches)
            )
            
            return unified_matches
            
        except Exception as e:
            error_msg = f"Failed to scan file {file_path}: {e}"
            self.logger.error("File scan failed", extra={
                **scan_context.to_dict(),
                'error': str(e),
                'error_type': type(e).__name__
            })
            raise DetectionError(error_msg) from e
    
    def _convert_to_unified_matches(self, matches: List[Dict], file_path: Path, 
                                   content: str, language: str) -> List[DetectionMatch]:
        """Convert regex matches to unified DetectionMatch format."""
        
        unified_matches = []
        
        # Heuristics: path-based severity downgrades and suppression for false-positive heavy domains
        file_path_str = str(file_path).lower() if file_path else ''
        is_test_like = any(part in file_path_str for part in ['/test', '\\test', '/tests', '\\tests', '/fixtures', '\\fixtures', '/samples', '\\samples', '/docs', '\\docs'])
        geo_like_ext = any(file_path_str.endswith(ext) for ext in ['.wkt', '.srs', '.prj'])

        for match in matches:
            # Extract line number
            line_num = match.get('line_number', 1)
            
            # Extract snippet (context around the match)
            snippet = self._extract_snippet(content, line_num, match.get('matched_text', ''))
            
            # Create unified DetectionMatch
            unified_match = DetectionMatch(
                file=str(file_path),
                line=line_num,
                engine="regex",
                rule_id=match.get('pattern_name', 'unknown'),
                severity=match.get('risk_level', 'MEDIUM'),
                confidence=match.get('confidence', 0.8),
                snippet=snippet,
                description=match.get('description', 'Regex pattern detection'),
                pattern_name=match.get('pattern_name', ''),
                matched_text=match.get('matched_text', ''),
                column_start=match.get('column_start', 0),
                column_end=match.get('column_end', 0),
                risk_level=match.get('risk_level', RiskLevel.MEDIUM),
                context_before=match.get('context_before', ''),
                context_after=match.get('context_after', ''),
                false_positive=match.get('false_positive', False),
                validated=match.get('validated', False),
                legitimate_usage_flag=match.get('legitimate_usage_flag', False),
                metadata=match.get('metadata', {}),
                context_info=match.get('context_info', {}),
                confidence_score=match.get('confidence_score', 0.0)
            )
            
            # Apply ssn_us-specific context suppression
            if unified_match.pattern_name in ('ssn_us', 'ssn'):
                line_lower = snippet.lower()
                negative_tokens = ['geogcs', 'datum', 'spheroid', 'wgs', 'epsg']
                if geo_like_ext or any(tok in line_lower for tok in negative_tokens):
                    # Suppress clearly geo-context false positives
                    continue
                # Downgrade severity in test-like paths unless explicitly labeled
                if is_test_like and unified_match.severity.upper() in ['HIGH', 'CRITICAL']:
                    unified_match.severity = 'LOW'

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
    
    def scan_content(
        self, 
        content: str, 
        language: str = "unknown",
        correlation_id: Optional[str] = None,
        context_name: str = "content"
    ) -> List[DetectionMatch]:
        """
        Scan content string for PII patterns.
        
        Args:
            content: Content to scan
            language: Programming language for pattern filtering
            correlation_id: Optional correlation ID for tracking
            context_name: Name/description of the content being scanned
            
        Returns:
            List of detection matches found in the content
        """
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        scan_context = ScanContext(
            correlation_id=correlation_id,
            file_path=None,
            language=language,
            scan_start_time=time.time(),
            active_patterns=self._get_active_pattern_names(language),
            content_size=len(content.encode('utf-8'))
        )
        
        self.logger.info("Starting content scan", extra={
            **scan_context.to_dict(),
            'context_name': context_name
        })
        
        try:
            matches = self._perform_scan(content, language, scan_context)
            
            scan_duration = time.time() - scan_context.scan_start_time
            
            self.logger.info("Content scan completed", extra={
                **scan_context.to_dict(),
                'context_name': context_name,
                'matches_found': len(matches),
                'scan_duration': scan_duration
            })
            
            return matches
            
        except Exception as e:
            self.logger.error("Content scan failed", extra={
                **scan_context.to_dict(),
                'context_name': context_name,
                'error': str(e)
            })
            raise DetectionError(f"Failed to scan content: {e}") from e
    
    def scan_multiple_files(
        self, 
        file_contents: List[Tuple[Path, str]], 
        language: str = "unknown"
    ) -> Dict[Path, List[DetectionMatch]]:
        """
        Scan multiple files concurrently for improved performance.
        
        Args:
            file_contents: List of (file_path, content) tuples
            language: Programming language for pattern filtering
            
        Returns:
            Dictionary mapping file paths to their detection matches
        """
        correlation_id = str(uuid.uuid4())
        results = {}
        
        self.logger.info("Starting concurrent file scan", extra={
            'correlation_id': correlation_id,
            'file_count': len(file_contents),
            'language': language,
            'max_workers': self.max_workers
        })
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scan tasks
            future_to_path = {
                executor.submit(
                    self.scan_file, 
                    file_path, 
                    content, 
                    language, 
                    f"{correlation_id}-{i}"
                ): file_path
                for i, (file_path, content) in enumerate(file_contents)
            }
            
            # Collect results
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                try:
                    matches = future.result()
                    results[file_path] = matches
                except Exception as e:
                    self.logger.error("Concurrent scan failed for file", extra={
                        'file_path': str(file_path),
                        'correlation_id': correlation_id,
                        'error': str(e)
                    })
                    results[file_path] = []
        
        total_duration = time.time() - start_time
        total_matches = sum(len(matches) for matches in results.values())
        
        self.logger.info("Concurrent scan completed", extra={
            'correlation_id': correlation_id,
            'files_processed': len(results),
            'total_matches': total_matches,
            'total_duration': total_duration,
            'avg_duration_per_file': total_duration / len(file_contents) if file_contents else 0
        })
        
        return results
    
    def _perform_scan(
        self, 
        content: str, 
        language: str, 
        scan_context: ScanContext
    ) -> List[DetectionMatch]:
        """
        Perform the actual pattern matching scan.
        
        Args:
            content: Content to scan
            language: Programming language for filtering
            scan_context: Context information for the scan
            
        Returns:
            List of detection matches
        """
        matches = []
        lines = content.splitlines()
        
        # Get patterns filtered by language
        patterns_to_use = self._get_active_patterns(language)
        
        # Update audit trail
        self._update_audit_trail(scan_context, patterns_to_use)
        
        # Process each pattern
        for pattern_name, pattern_metadata in patterns_to_use.items():
            try:
                pattern_matches = self._find_pattern_matches(
                    pattern_metadata.compiled_regex,
                    pattern_metadata.pattern,
                    content,
                    lines,
                    scan_context
                )
                
                # Convert to DetectionMatch objects
                for match in pattern_matches:
                    detection_match = self._create_detection_match(
                        match, 
                        pattern_metadata, 
                        content
                    )
                    matches.append(detection_match)
                
                # Update pattern usage statistics
                pattern_metadata.update_usage()
                
                # Log pattern execution
                self.logger.debug("Pattern executed", extra={
                    'correlation_id': scan_context.correlation_id,
                    'pattern_name': pattern_name,
                    'matches_found': len(pattern_matches),
                    'pattern_version': pattern_metadata.version
                })
                
            except Exception as e:
                self.logger.warning("Pattern execution failed", extra={
                    'correlation_id': scan_context.correlation_id,
                    'pattern_name': pattern_name,
                    'error': str(e)
                })
                continue
        
        return matches
    
    def _find_pattern_matches(
        self, 
        regex: re.Pattern, 
        pattern: DetectionPattern,
        content: str, 
        lines: List[str], 
        scan_context: ScanContext
    ) -> List[RegexMatch]:
        """
        Find all matches for a specific pattern with error handling.
        
        Args:
            regex: Compiled regex pattern
            pattern: Detection pattern configuration
            content: Content to search
            lines: Content split into lines
            scan_context: Scan context information
            
        Returns:
            List of regex matches
        """
        matches = []
        
        try:
            # Find all matches in the content
            for match_obj in regex.finditer(content):
                start_pos = match_obj.start()
                end_pos = match_obj.end()
                matched_text = match_obj.group()
                
                # Calculate line and column information
                line_number, column_start, column_end = self._calculate_position(
                    content, start_pos, end_pos
                )
                
                # Create regex match object
                regex_match = RegexMatch(
                    pattern_name=pattern.name,
                    matched_text=matched_text,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    line_number=line_number,
                    column_start=column_start,
                    column_end=column_end,
                    correlation_id=scan_context.correlation_id
                )
                
                matches.append(regex_match)
                
                # Log individual detection
                self.logger.info("PII detection found", extra={
                    'correlation_id': scan_context.correlation_id,
                    'pattern_name': pattern.name,
                    'line_number': line_number,
                    'column_start': column_start,
                    'risk_level': pattern.risk_level.name,
                    'confidence': pattern.confidence,
                    'matched_length': len(matched_text),
                    'file_path': str(scan_context.file_path) if scan_context.file_path else None
                })
        
        except Exception as e:
            self.logger.error("Pattern matching failed", extra={
                'correlation_id': scan_context.correlation_id,
                'pattern_name': pattern.name,
                'error': str(e)
            })
            
        return matches
    
    def _calculate_position(self, content: str, start_pos: int, end_pos: int) -> Tuple[int, int, int]:
        """
        Calculate line number and column positions efficiently.
        
        Args:
            content: Full content string
            start_pos: Start position of match
            end_pos: End position of match
            
        Returns:
            Tuple of (line_number, column_start, column_end)
        """
        # Count newlines before start position
        line_number = content.count('\n', 0, start_pos) + 1
        
        # Find the start of the current line
        line_start = content.rfind('\n', 0, start_pos)
        if line_start == -1:
            line_start = 0
        else:
            line_start += 1
        
        # Calculate column positions (1-based)
        column_start = start_pos - line_start + 1
        column_end = end_pos - line_start + 1
        
        return line_number, column_start, column_end
    
    def _create_detection_match(
        self, 
        regex_match: RegexMatch, 
        pattern_metadata: PatternMetadata, 
        content: str
    ) -> DetectionMatch:
        """
        Convert regex match to detection match with enhanced metadata.
        
        Args:
            regex_match: Raw regex match result
            pattern_metadata: Pattern metadata including version
            content: Original content for context extraction
            
        Returns:
            DetectionMatch with full metadata
        """
        
        # Get context around the match
        context_before, context_after = self._extract_context(
            content, 
            regex_match.start_pos, 
            regex_match.end_pos
        )
        
        return DetectionMatch(
            file="content_scan",
            line=regex_match.line_number,
            engine="regex",
            rule_id=regex_match.pattern_name,
            severity=pattern_metadata.pattern.risk_level.value if hasattr(pattern_metadata.pattern.risk_level, 'value') else str(pattern_metadata.pattern.risk_level),
            confidence=pattern_metadata.pattern.confidence,
            snippet=regex_match.matched_text,
            description=f"Regex pattern detection for {regex_match.pattern_name}",
            pattern_name=regex_match.pattern_name,
            matched_text=regex_match.matched_text,
            column_start=regex_match.column_start,
            column_end=regex_match.column_end,
            risk_level=pattern_metadata.pattern.risk_level,
            context_before=context_before,
            context_after=context_after,
            metadata={
                'detection_level': 'regex',
                'pattern_type': 'regex',
                'pattern_version': pattern_metadata.version,
                'scan_timestamp': regex_match.detection_timestamp,
                'correlation_id': regex_match.correlation_id,
                'usage_count': pattern_metadata.usage_count,
                'languages': pattern_metadata.pattern.languages or [],
                'sanitized': False,
                'pattern_regex': pattern_metadata.pattern.regex
            }
        )
    
    def _extract_context(
        self, 
        content: str, 
        start_pos: int, 
        end_pos: int,
        before_chars: int = 60, 
        after_chars: int = 60
    ) -> Tuple[str, str]:
        """
        Extract and sanitize context around a match for security.
        
        Args:
            content: Full content string
            start_pos: Start position of match
            end_pos: End position of match
            before_chars: Characters to include before match
            after_chars: Characters to include after match
            
        Returns:
            Tuple of (context_before, context_after)
        """
        try:
            # Extract context before match
            context_before_start = max(0, start_pos - before_chars)
            context_before = content[context_before_start:start_pos]
            
            # Extract context after match  
            context_after_end = min(len(content), end_pos + after_chars)
            context_after = content[end_pos:context_after_end]
            
            # Sanitize contexts for security
            context_before = self._sanitize_context(context_before)
            context_after = self._sanitize_context(context_after)
            
            return context_before, context_after
            
        except Exception as e:
            self.logger.warning("Failed to extract context", extra={'error': str(e)})
            return "[context unavailable]", "[context unavailable]"
    
    def _sanitize_context(self, context: str) -> str:
        """
        Sanitize context string to prevent exposure of sensitive data.
        
        Args:
            context: Raw context string
            
        Returns:
            Sanitized context string
        """
        if not context:
            return "[empty]"
        
        # Replace tabs with spaces and normalize whitespace
        context = re.sub(r'\s+', ' ', context.replace('\t', ' '))
        
        # Mask potential secrets and PII
        context = self._mask_secrets_in_context(context)
        
        # Truncate if too long
        max_context_length = 80
        if len(context) > max_context_length:
            context = context[:max_context_length - 3] + "..."
        
        return context.strip() or "[whitespace]"
    
    def _mask_secrets_in_context(self, context: str) -> str:
        """
        Mask potential secrets in context to prevent data exposure.
        
        Args:
            context: Context string to mask
            
        Returns:
            Masked context string
        """
        # Patterns for common secret formats
        masking_patterns = [
            # Long alphanumeric strings (API keys, tokens)
            (r'[A-Za-z0-9]{16,}', lambda m: f"{m.group()[:3]}***{m.group()[-3:]}"),
            # Base64-like strings
            (r'[A-Za-z0-9+/]{20,}={0,2}', lambda m: f"{m.group()[:4]}***{m.group()[-4:]}"),
            # Hexadecimal strings
            (r'[0-9a-fA-F]{16,}', lambda m: f"{m.group()[:4]}***{m.group()[-4:]}"),
            # Email addresses (partial masking)
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
             lambda m: f"{m.group()[:2]}***@{m.group().split('@')[1]}"),
        ]
        
        for pattern, replacer in masking_patterns:
            context = re.sub(pattern, replacer, context)
        
        return context
    
    def _sanitize_matched_text(self, matched_text: str) -> str:
        """
        Sanitize matched text to prevent full exposure of sensitive data.
        
        Args:
            matched_text: Original matched text
            
        Returns:
            Sanitized matched text
        """
        # For very long matches, show only partial content
        if len(matched_text) > 50:
            return f"{matched_text[:10]}***{matched_text[-10:]} (length: {len(matched_text)})"
        
        # For shorter matches, apply basic masking
        if len(matched_text) > 8:
            return f"{matched_text[:3]}***{matched_text[-3:]}"
        
        return f"***{matched_text[-2:]}" if len(matched_text) > 2 else "***"
    
    def _get_active_patterns(self, language: str) -> Dict[str, PatternMetadata]:
        """
        Get active patterns filtered by language.
        
        Args:
            language: Programming language to filter by
            
        Returns:
            Dictionary of active pattern metadata
        """
        with self._pattern_lock:
            if language == "unknown":
                return self.compiled_patterns.copy()
            
            filtered_patterns = {}
            for name, metadata in self.compiled_patterns.items():
                pattern_languages = metadata.pattern.languages
                if not pattern_languages or language in pattern_languages:
                    filtered_patterns[name] = metadata
            
            return filtered_patterns
    
    def _get_active_pattern_names(self, language: str) -> List[str]:
        """Get list of active pattern names for a language."""
        return list(self._get_active_patterns(language).keys())
    
    def _update_audit_trail(
        self, 
        scan_context: ScanContext, 
        patterns_used: Dict[str, PatternMetadata]
    ) -> None:
        """
        Update audit trail with scan information.
        
        Args:
            scan_context: Context of the current scan
            patterns_used: Patterns used in this scan
        """
        audit_entry = {
            'timestamp': time.time(),
            'correlation_id': scan_context.correlation_id,
            'file_path': str(scan_context.file_path) if scan_context.file_path else None,
            'language': scan_context.language,
            'patterns_used': [
                {
                    'name': name,
                    'version': metadata.version,
                    'risk_level': metadata.pattern.risk_level.name,
                    'confidence': metadata.pattern.confidence
                }
                for name, metadata in patterns_used.items()
            ],
            'content_size': scan_context.content_size
        }
        
        self._audit_trail.append(audit_entry)
        
        # Keep audit trail size manageable
        if len(self._audit_trail) > 10000:
            self._audit_trail = self._audit_trail[-5000:]
    
    def _record_scan_history(
        self, 
        scan_context: ScanContext, 
        matches: List[DetectionMatch], 
        duration: float
    ) -> None:
        """
        Record scan history for performance analysis.
        
        Args:
            scan_context: Context of the completed scan
            matches: Matches found during scan
            duration: Scan duration in seconds
        """
        history_entry = {
            'timestamp': scan_context.scan_start_time,
            'correlation_id': scan_context.correlation_id,
            'duration': duration,
            'content_size': scan_context.content_size,
            'matches_found': len(matches),
            'patterns_used': len(scan_context.active_patterns),
            'language': scan_context.language,
            'file_path': str(scan_context.file_path) if scan_context.file_path else None,
            'performance_ratio': len(matches) / duration if duration > 0 else 0
        }
        
        self._scan_history.append(history_entry)
        
        # Keep history size manageable
        if len(self._scan_history) > 10000:
            self._scan_history = self._scan_history[-5000:]
    
    # Pattern Management Methods
    
    def add_pattern(self, pattern: DetectionPattern) -> None:
        """
        Add a new detection pattern with validation.
        
        Args:
            pattern: Detection pattern to add
            
        Raises:
            DetectionError: If pattern is invalid
        """
        try:
            # Validate pattern
            compiled_regex = re.compile(
                pattern.regex,
                flags=re.MULTILINE | re.IGNORECASE
            )
            
            # Add to patterns list
            self.patterns.append(pattern)
            
            # Compile if enabled
            if pattern.enabled:
                pattern_metadata = PatternMetadata(
                    pattern=pattern,
                    compiled_regex=compiled_regex,
                    version=getattr(pattern, 'version', '1.0'),
                    compilation_time=time.time()
                )
                
                with self._pattern_lock:
                    self.compiled_patterns[pattern.name] = pattern_metadata
            
            self.logger.info("Pattern added successfully", extra={
                'pattern_name': pattern.name,
                'enabled': pattern.enabled,
                'risk_level': pattern.risk_level.name
            })
            
        except re.error as e:
            error_msg = f"Invalid regex pattern '{pattern.name}': {e}"
            self.logger.error("Failed to add pattern", extra={
                'pattern_name': pattern.name,
                'error': str(e)
            })
            raise DetectionError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Failed to add pattern '{pattern.name}': {e}"
            self.logger.error("Pattern addition failed", extra={
                'pattern_name': pattern.name,
                'error': str(e)
            })
            raise DetectionError(error_msg) from e
    
    def remove_pattern(self, pattern_name: str) -> bool:
        """
        Remove a detection pattern.
        
        Args:
            pattern_name: Name of pattern to remove
            
        Returns:
            True if pattern was removed, False if not found
        """
        # Remove from patterns list
        original_count = len(self.patterns)
        self.patterns = [p for p in self.patterns if p.name != pattern_name]
        
        # Remove from compiled patterns
        with self._pattern_lock:
            if pattern_name in self.compiled_patterns:
                del self.compiled_patterns[pattern_name]
        
        removed = len(self.patterns) < original_count
        
        if removed:
            self.logger.info("Pattern removed successfully", extra={
                'pattern_name': pattern_name
            })
        else:
            self.logger.warning("Pattern not found for removal", extra={
                'pattern_name': pattern_name
            })
        
        return removed
    
    def enable_pattern(self, pattern_name: str) -> bool:
        """
        Enable a detection pattern.
        
        Args:
            pattern_name: Name of pattern to enable
            
        Returns:
            True if pattern was enabled, False if not found
        """
        for pattern in self.patterns:
            if pattern.name == pattern_name:
                pattern.enabled = True
                
                # Compile if not already compiled
                if pattern_name not in self.compiled_patterns:
                    try:
                        compiled_regex = re.compile(
                            pattern.regex,
                            flags=re.MULTILINE | re.IGNORECASE
                        )
                        
                        pattern_metadata = PatternMetadata(
                            pattern=pattern,
                            compiled_regex=compiled_regex,
                            version=getattr(pattern, 'version', '1.0'),
                            compilation_time=time.time()
                        )
                        
                        with self._pattern_lock:
                            self.compiled_patterns[pattern_name] = pattern_metadata
                        
                        self.logger.info("Pattern enabled successfully", extra={
                            'pattern_name': pattern_name
                        })
                        return True
                        
                    except re.error as e:
                        self.logger.error("Failed to enable pattern", extra={
                            'pattern_name': pattern_name,
                            'error': str(e)
                        })
                        pattern.enabled = False
                        return False
        
        self.logger.warning("Pattern not found for enabling", extra={
            'pattern_name': pattern_name
        })
        return False
    
    def disable_pattern(self, pattern_name: str) -> bool:
        """
        Disable a detection pattern.
        
        Args:
            pattern_name: Name of pattern to disable
            
        Returns:
            True if pattern was disabled, False if not found
        """
        for pattern in self.patterns:
            if pattern.name == pattern_name:
                pattern.enabled = False
                
                # Remove from compiled patterns
                with self._pattern_lock:
                    if pattern_name in self.compiled_patterns:
                        del self.compiled_patterns[pattern_name]
                
                self.logger.info("Pattern disabled successfully", extra={
                    'pattern_name': pattern_name
                })
                return True
        
        self.logger.warning("Pattern not found for disabling", extra={
            'pattern_name': pattern_name
        })
        return False
    
    def update_pattern(self, pattern_name: str, updated_pattern: DetectionPattern) -> bool:
        """
        Update an existing pattern with validation.
        
        Args:
            pattern_name: Name of pattern to update
            updated_pattern: New pattern configuration
            
        Returns:
            True if pattern was updated, False if not found
            
        Raises:
            DetectionError: If updated pattern is invalid
        """
        # Find and update the pattern
        for i, pattern in enumerate(self.patterns):
            if pattern.name == pattern_name:
                # Validate new pattern
                try:
                    compiled_regex = re.compile(
                        updated_pattern.regex,
                        flags=re.MULTILINE | re.IGNORECASE
                    )
                    
                    # Update pattern in list
                    self.patterns[i] = updated_pattern
                    
                    # Update compiled pattern if enabled
                    if updated_pattern.enabled:
                        pattern_metadata = PatternMetadata(
                            pattern=updated_pattern,
                            compiled_regex=compiled_regex,
                            version=getattr(updated_pattern, 'version', '1.0'),
                            compilation_time=time.time()
                        )
                        
                        with self._pattern_lock:
                            self.compiled_patterns[pattern_name] = pattern_metadata
                    else:
                        # Remove from compiled if disabled
                        with self._pattern_lock:
                            if pattern_name in self.compiled_patterns:
                                del self.compiled_patterns[pattern_name]
                    
                    self.logger.info("Pattern updated successfully", extra={
                        'pattern_name': pattern_name,
                        'enabled': updated_pattern.enabled,
                        'risk_level': updated_pattern.risk_level.name
                    })
                    return True
                    
                except re.error as e:
                    error_msg = f"Invalid updated regex pattern '{pattern_name}': {e}"
                    self.logger.error("Pattern update failed", extra={
                        'pattern_name': pattern_name,
                        'error': str(e)
                    })
                    raise DetectionError(error_msg) from e
        
        self.logger.warning("Pattern not found for update", extra={
            'pattern_name': pattern_name
        })
        return False
    
    def validate_patterns(self) -> List[str]:
        """
        Validate all regex patterns and return any errors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        for pattern in self.patterns:
            try:
                re.compile(pattern.regex)
            except re.error as e:
                error_msg = f"Pattern '{pattern.name}': {e}"
                errors.append(error_msg)
                self.logger.warning("Pattern validation failed", extra={
                    'pattern_name': pattern.name,
                    'error': str(e)
                })
        
        self.logger.info("Pattern validation completed", extra={
            'total_patterns': len(self.patterns),
            'validation_errors': len(errors)
        })
        
        return errors
    
    # Statistics and Monitoring Methods
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        base_stats = self.performance_monitor.get_stats()
        
        # Calculate additional metrics from scan history
        if self._scan_history:
            recent_scans = self._scan_history[-100:]  # Last 100 scans
            
            avg_duration = sum(s['duration'] for s in recent_scans) / len(recent_scans)
            avg_matches_per_scan = sum(s['matches_found'] for s in recent_scans) / len(recent_scans)
            avg_content_size = sum(s['content_size'] for s in recent_scans) / len(recent_scans)
            
            throughput_stats = {
                'recent_avg_duration': avg_duration,
                'recent_avg_matches_per_scan': avg_matches_per_scan,
                'recent_avg_content_size': avg_content_size,
                'recent_throughput_mb_per_sec': (avg_content_size / (1024 * 1024)) / avg_duration if avg_duration > 0 else 0,
                'total_scans_completed': len(self._scan_history)
            }
            
            base_stats.update(throughput_stats)
        
        return base_stats
    
    def _validate_regex_pattern(self, pattern: str) -> None:
        """Validate regex pattern to prevent ReDoS attacks and other security issues."""
        import re
        
        # Check pattern length
        if len(pattern) > 10000:  # Reasonable limit
            raise ValueError("Regex pattern too long (max 10000 characters)")
        
        # Check for dangerous patterns that can cause ReDoS
        dangerous_patterns = [
            r'\(\?\=.*\*',  # Positive lookahead with quantifier
            r'\(\?\=.*\+',  # Positive lookahead with quantifier
            r'\(\?\=.*\{',  # Positive lookahead with quantifier
            r'\(\?\=.*\?',  # Positive lookahead with quantifier
            r'\(\?\=.*\*.*\*',  # Nested quantifiers
            r'\(\?\=.*\+.*\+',  # Nested quantifiers
            r'\(\?\=.*\{.*\{',  # Nested quantifiers
            r'\(\?\=.*\?.*\?',  # Nested quantifiers
            r'\(\?\=.*\*.*\+',  # Nested quantifiers
            r'\(\?\=.*\+.*\*',  # Nested quantifiers
            r'\(\?\=.*\{.*\*',  # Nested quantifiers
            r'\(\?\=.*\*.*\{',  # Nested quantifiers
            r'\(\?\=.*\+.*\{',  # Nested quantifiers
            r'\(\?\=.*\{.*\+',  # Nested quantifiers
            r'\(\?\=.*\?.*\*',  # Nested quantifiers
            r'\(\?\=.*\*.*\?',  # Nested quantifiers
            r'\(\?\=.*\?.*\+',  # Nested quantifiers
            r'\(\?\=.*\+.*\?',  # Nested quantifiers
            r'\(\?\=.*\?.*\{',  # Nested quantifiers
            r'\(\?\=.*\{.*\?',  # Nested quantifiers
        ]
        
        for dangerous_pattern in dangerous_patterns:
            if re.search(dangerous_pattern, pattern):
                raise ValueError(f"Potentially dangerous regex pattern detected: {dangerous_pattern}")
        
        # Check for excessive nesting
        nesting_level = 0
        max_nesting = 10
        
        for char in pattern:
            if char == '(':
                nesting_level += 1
                if nesting_level > max_nesting:
                    raise ValueError(f"Regex pattern nesting too deep (max {max_nesting} levels)")
            elif char == ')':
                nesting_level -= 1
                if nesting_level < 0:
                    raise ValueError("Unbalanced parentheses in regex pattern")
        
        # Check for excessive quantifiers
        quantifier_count = len(re.findall(r'[\*\+\?\{]', pattern))
        if quantifier_count > 50:  # Reasonable limit
            raise ValueError(f"Too many quantifiers in regex pattern (max 50, found {quantifier_count})")
        
        # Check for potential catastrophic backtracking patterns
        backtracking_patterns = [
            r'\([^)]*\)\*.*\([^)]*\)\*',  # Multiple quantified groups
            r'\([^)]*\)\+.*\([^)]*\)\+',  # Multiple quantified groups
            r'\([^)]*\)\?.*\([^)]*\)\?',  # Multiple quantified groups
            r'\([^)]*\)\{[^}]*\}.*\([^)]*\)\{[^}]*\}',  # Multiple quantified groups
        ]
        
        for backtracking_pattern in backtracking_patterns:
            if re.search(backtracking_pattern, pattern):
                self.logger.warning(f"Potentially problematic regex pattern detected: {backtracking_pattern}")
                # Don't raise exception, just warn
    
    def _sanitize_for_logging(self, text: str) -> str:
        """Sanitize text for logging to prevent PII exposure."""
        import re
        
        # Remove potential PII patterns from text before logging
        pii_patterns = [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',  # Phone
            r'\b[A-Za-z0-9+/=]{20,}\b',  # Base64-like strings
        ]
        
        sanitized = text
        for pattern in pii_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        return sanitized
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about patterns.
        
        Returns:
            Dictionary containing pattern statistics
        """
        total_patterns = len(self.patterns)
        enabled_patterns = len([p for p in self.patterns if p.enabled])
        
        with self._pattern_lock:
            compiled_patterns = len(self.compiled_patterns)
            
            # Usage statistics
            usage_stats = {}
            if self.compiled_patterns:
                for name, metadata in self.compiled_patterns.items():
                    usage_stats[name] = {
                        'usage_count': metadata.usage_count,
                        'last_used': metadata.last_used,
                        'version': metadata.version,
                        'risk_level': metadata.pattern.risk_level.name,
                        'confidence': metadata.pattern.confidence,
                        'languages': metadata.pattern.languages or []
                    }
        
        # Risk level distribution
        risk_distribution = {}
        for pattern in self.patterns:
            risk_level = pattern.risk_level.name
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        
        return {
            'total_patterns': total_patterns,
            'enabled_patterns': enabled_patterns,
            'compiled_patterns': compiled_patterns,
            'disabled_patterns': total_patterns - enabled_patterns,
            'pattern_names': [p.name for p in self.patterns],
            'enabled_pattern_names': [p.name for p in self.patterns if p.enabled],
            'risk_level_distribution': risk_distribution,
            'usage_statistics': usage_stats,
            'languages_supported': list(set(
                lang for p in self.patterns 
                for lang in (p.languages or [])
            ))
        }
    
    def get_scan_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about completed scans.
        
        Returns:
            Dictionary containing scan statistics
        """
        if not self._scan_history:
            return {'message': 'No scans completed yet'}
        
        total_scans = len(self._scan_history)
        total_matches = sum(s['matches_found'] for s in self._scan_history)
        total_content_size = sum(s['content_size'] for s in self._scan_history)
        total_duration = sum(s['duration'] for s in self._scan_history)
        
        # Language distribution
        language_stats = {}
        for scan in self._scan_history:
            lang = scan['language']
            language_stats[lang] = language_stats.get(lang, 0) + 1
        
        # Performance metrics
        avg_duration = total_duration / total_scans if total_scans > 0 else 0
        avg_matches_per_scan = total_matches / total_scans if total_scans > 0 else 0
        throughput_mb_per_sec = (total_content_size / (1024 * 1024)) / total_duration if total_duration > 0 else 0
        
        return {
            'total_scans': total_scans,
            'total_matches_found': total_matches,
            'total_content_processed_mb': total_content_size / (1024 * 1024),
            'total_processing_time': total_duration,
            'average_scan_duration': avg_duration,
            'average_matches_per_scan': avg_matches_per_scan,
            'throughput_mb_per_second': throughput_mb_per_sec,
            'language_distribution': language_stats,
            'match_rate': total_matches / total_scans if total_scans > 0 else 0
        }
    
    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get audit trail entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of audit trail entries
        """
        return self._audit_trail[-limit:] if self._audit_trail else []
    
    def export_detection_report(self, correlation_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export a comprehensive detection report.
        
        Args:
            correlation_ids: Optional list of correlation IDs to filter by
            
        Returns:
            Comprehensive detection report
        """
        report = {
            'report_timestamp': time.time(),
            'report_id': str(uuid.uuid4()),
            'engine_info': {
                'max_workers': self.max_workers,
                'max_file_size': self.max_file_size,
                'async_enabled': self.enable_async
            },
            'pattern_statistics': self.get_pattern_stats(),
            'performance_statistics': self.get_performance_stats(),
            'scan_statistics': self.get_scan_statistics()
        }
        
        # Filter audit trail if correlation IDs provided
        if correlation_ids:
            filtered_audit = [
                entry for entry in self._audit_trail
                if entry['correlation_id'] in correlation_ids
            ]
            report['filtered_audit_trail'] = filtered_audit
        else:
            report['recent_audit_trail'] = self.get_audit_trail(50)
        
        return report
    
    # Health and Diagnostics
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the regex engine.
        
        Returns:
            Health check results
        """
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {}
        }
        
        try:
            # Check pattern compilation
            validation_errors = self.validate_patterns()
            health_status['checks']['pattern_validation'] = {
                'status': 'pass' if not validation_errors else 'fail',
                'errors': validation_errors
            }
            
            # Check compiled patterns
            with self._pattern_lock:
                compiled_count = len(self.compiled_patterns)
                enabled_count = len([p for p in self.patterns if p.enabled])
            
            health_status['checks']['pattern_compilation'] = {
                'status': 'pass' if compiled_count == enabled_count else 'warn',
                'compiled_patterns': compiled_count,
                'enabled_patterns': enabled_count
            }
            
            # Check memory usage of audit trail and scan history
            audit_size = len(self._audit_trail)
            history_size = len(self._scan_history)
            
            health_status['checks']['memory_usage'] = {
                'status': 'pass' if audit_size < 8000 and history_size < 8000 else 'warn',
                'audit_trail_size': audit_size,
                'scan_history_size': history_size
            }
            
            # Overall health determination
            failed_checks = sum(1 for check in health_status['checks'].values() 
                              if check['status'] == 'fail')
            
            if failed_checks > 0:
                health_status['status'] = 'unhealthy'
            elif any(check['status'] == 'warn' for check in health_status['checks'].values()):
                health_status['status'] = 'degraded'
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
            self.logger.error("Health check failed", extra={'error': str(e)})
        
        return health_status
    
    @contextmanager
    def performance_monitoring(self, operation_name: str):
        """
        Context manager for monitoring operation performance.
        
        Args:
            operation_name: Name of the operation being monitored
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.performance_monitor.record_operation(operation_name, duration)
            
            self.logger.debug("Operation completed", extra={
                'operation': operation_name,
                'duration': duration
            })
    
    def clear_history(self, keep_recent: int = 100) -> None:
        """
        Clear scan history and audit trail, optionally keeping recent entries.
        
        Args:
            keep_recent: Number of recent entries to keep
        """
        if keep_recent > 0:
            self._scan_history = self._scan_history[-keep_recent:] if self._scan_history else []
            self._audit_trail = self._audit_trail[-keep_recent:] if self._audit_trail else []
        else:
            self._scan_history.clear()
            self._audit_trail.clear()
        
        self.logger.info("History cleared", extra={
            'scan_history_remaining': len(self._scan_history),
            'audit_trail_remaining': len(self._audit_trail)
        })
    
    def shutdown(self) -> None:
        """
        Gracefully shutdown the regex engine.
        """
        self.logger.info("Shutting down RegexEngine", extra={
            'total_scans_completed': len(self._scan_history),
            'total_patterns': len(self.patterns)
        })
        
        # Clear resources
        with self._pattern_lock:
            self.compiled_patterns.clear()
        
        self._scan_history.clear()
        self._audit_trail.clear()
        
        self.logger.info("RegexEngine shutdown completed")


# Utility functions for enterprise features

def create_regex_engine_from_config(
    config: Dict[str, Any], 
    patterns: List[DetectionPattern]
) -> RegexEngine:
    """
    Create a RegexEngine instance from configuration.
    
    Args:
        config: Configuration dictionary
        patterns: List of detection patterns
        
    Returns:
        Configured RegexEngine instance
    """
    return RegexEngine(
        patterns=patterns,
        max_workers=config.get('max_workers', 4),
        max_file_size=config.get('max_file_size', 50 * 1024 * 1024),
        enable_async=config.get('enable_async', True)
    )


async def scan_repository_async(
    engine: RegexEngine,
    file_paths_and_contents: List[Tuple[Path, str]],
    language: str = "unknown",
    batch_size: int = 10
) -> Dict[Path, List[DetectionMatch]]:
    """
    Scan an entire repository asynchronously in batches.
    
    Args:
        engine: RegexEngine instance
        file_paths_and_contents: List of (path, content) tuples
        language: Programming language for filtering
        batch_size: Number of files to process per batch
        
    Returns:
        Dictionary mapping file paths to detection matches
    """
    results = {}
    
    # Process files in batches to avoid overwhelming the system
    for i in range(0, len(file_paths_and_contents), batch_size):
        batch = file_paths_and_contents[i:i + batch_size]
        
        # Create async tasks for this batch
        tasks = [
            engine.scan_file_async(file_path, content, language)
            for file_path, content in batch
        ]
        
        # Wait for batch completion
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for (file_path, _), result in zip(batch, batch_results):
            if isinstance(result, Exception):
                engine.logger.error("Batch scan failed for file", extra={
                    'file_path': str(file_path),
                    'error': str(result)
                })
                results[file_path] = []
            else:
                results[file_path] = result
    
    return results