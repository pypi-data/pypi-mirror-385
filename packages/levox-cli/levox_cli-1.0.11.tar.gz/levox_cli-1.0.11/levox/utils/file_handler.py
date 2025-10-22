"""
File handling utilities for Levox with memory-mapped operations.
"""

import os
import mmap
from pathlib import Path
from typing import Optional, List, Dict, Any, Iterator, Callable, Tuple, Set
import fnmatch
import hashlib
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core.exceptions import FileError


class FileHandler:
    """Handles file operations with memory mapping for large files."""
    
    def __init__(self, config):
        self.config = config
        self.max_file_size_mb = config.performance.max_file_size_mb
        self.memory_limit_mb = config.performance.memory_limit_mb
    
    def read_file(self, file_path: Path) -> Optional[str]:
        """Read file content with memory mapping for large files."""
        try:
            # SECURITY: Validate file path to prevent path traversal
            self._validate_file_path(file_path)
            
            file_size = file_path.stat().st_size
            file_size_mb = file_size / 1024 / 1024
            
            # Check file size limits
            if file_size_mb > self.max_file_size_mb:
                raise FileError(f"File too large: {file_size_mb:.2f}MB > {self.max_file_size_mb}MB")
            
            # Use memory mapping for files larger than 1MB
            if file_size_mb > 1:
                return self._read_with_mmap(file_path)
            else:
                return self._read_standard(file_path)
                
        except Exception as e:
            raise FileError(f"Failed to read file {file_path}: {e}")
    
    def _validate_file_path(self, file_path: Path) -> None:
        """Validate file path to prevent path traversal attacks."""
        import os
        
        # Resolve the path to get absolute path
        try:
            resolved_path = file_path.resolve()
        except (OSError, RuntimeError):
            raise FileError(f"Invalid file path: {file_path}")
        
        # Check for path traversal patterns
        path_str = str(resolved_path)
        
        # Check for directory traversal patterns
        if '..' in path_str:
            raise FileError(f"Potentially dangerous path pattern detected: ..")
        
        # Check for double slashes (potential path manipulation)
        if '//' in path_str or '\\\\' in path_str:
            raise FileError(f"Potentially dangerous path pattern detected: // or \\\\")
        
        # Check for home directory expansion (only if ~ appears at the beginning of a path component)
        # This is more specific than just checking for ~ anywhere in the path
        # Only flag if it's exactly "~" or starts with "~/" which indicates home directory expansion
        path_parts = path_str.replace('\\', '/').split('/')
        for part in path_parts:
            if part == '~' or (part.startswith('~') and '/' in part):
                raise FileError(f"Potentially dangerous path pattern detected: {part}")
        
        # Check if path is within allowed directories (if configured)
        # This is a basic check - in production, you might want more sophisticated path validation
        if not os.path.exists(resolved_path):
            raise FileError(f"File does not exist: {resolved_path}")
        
        # Check file permissions
        if not os.access(resolved_path, os.R_OK):
            raise FileError(f"Permission denied reading file: {resolved_path}")
    
    def _read_with_mmap(self, file_path: Path) -> str:
        """Read file using memory mapping."""
        try:
            # Open in binary to allow mmap without decoding first
            with open(file_path, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    # Attempt UTF-8 decode first, then fallbacks
                    try:
                        return mm.read().decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            return mm.read().decode('utf-16')
                        except UnicodeDecodeError:
                            return mm.read().decode('latin-1', errors='replace')
        except Exception as e:
            # Fallback to standard reading
            return self._read_standard(file_path)
    
    def _read_standard(self, file_path: Path) -> str:
        """Read file using standard file operations."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encodings
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            # Last resort: read as bytes and decode with replacement
            with open(file_path, 'rb') as f:
                return f.read().decode('utf-8', errors='replace')
    
    def is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary by examining its content."""
        try:
            with open(file_path, 'rb') as f:
                # Read first 1024 bytes to check for binary content
                chunk = f.read(1024)
                if not chunk:
                    return False
                
                # Check for null bytes (common in binary files)
                if b'\x00' in chunk:
                    return True
                
                # Check for high percentage of non-printable characters
                non_printable = sum(1 for byte in chunk if byte < 32 and byte not in (9, 10, 13))
                if non_printable > len(chunk) * 0.3:  # More than 30% non-printable
                    return True
                
                return False
        except Exception:
            # If we can't read the file, assume it's not binary
            return False
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive file information."""
        try:
            stat = file_path.stat()
            return {
                'path': str(file_path),
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / 1024 / 1024,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
                'is_executable': os.access(file_path, os.X_OK),
                'extension': file_path.suffix.lower(),
                'name': file_path.name,
                'parent': str(file_path.parent)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def validate(self) -> None:
        """Validate file handler configuration."""
        if self.max_file_size_mb <= 0:
            raise FileError("max_file_size_mb must be positive")
        
        if self.memory_limit_mb <= 0:
            raise FileError("memory_limit_mb must be positive")
    
    def get_directory_stats(self, directory: Path) -> Dict[str, Any]:
        """Get statistics about a directory."""
        try:
            total_files = 0
            total_size = 0
            file_types = {}
            large_files = []
            
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        file_size = stat.st_size
                        total_files += 1
                        total_size += file_size
                        
                        # Count file types
                        ext = file_path.suffix.lower()
                        file_types[ext] = file_types.get(ext, 0) + 1
                        
                        # Track large files
                        if file_size > 10 * 1024 * 1024:  # > 10MB
                            large_files.append({
                                'path': str(file_path),
                                'size_mb': file_size / 1024 / 1024
                            })
                    
                    except OSError:
                        # Skip files we can't access
                        continue
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / 1024 / 1024,
                'file_types': file_types,
                'large_files': large_files
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def find_files_by_pattern(self, directory: Path, pattern: str) -> List[Path]:
        """Find files matching a pattern."""
        try:
            return list(directory.rglob(pattern))
        except Exception as e:
            raise FileError(f"Failed to find files with pattern {pattern}: {e}")
    
    def get_file_encoding(self, file_path: Path) -> str:
        """Detect file encoding."""
        try:
            # Try to read a small sample to detect encoding
            with open(file_path, 'rb') as f:
                sample = f.read(1024)
            
            # Check for BOM (Byte Order Mark)
            if sample.startswith(b'\xef\xbb\xbf'):
                return 'utf-8-sig'
            elif sample.startswith(b'\xff\xfe'):
                return 'utf-16-le'
            elif sample.startswith(b'\xfe\xff'):
                return 'utf-16-be'
            
            # Try to decode as UTF-8
            try:
                sample.decode('utf-8')
                return 'utf-8'
            except UnicodeDecodeError:
                pass
            
            # Fallback to latin-1 (always works)
            return 'latin-1'
            
        except Exception:
            return 'utf-8'  # Default fallback
    
    def _write_file_safe(self, file_path, content: str, mode: str = 'w') -> None:
        """Safely write content to a file with atomic operation."""
        import tempfile
        import os
        
        try:
            path = Path(file_path) if not isinstance(file_path, Path) else file_path
            
            # SECURITY: Validate file path to prevent path traversal
            self._validate_file_path_for_write(path)
            
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # SECURITY: Use secure temporary file creation
            temp_fd, temp_path = tempfile.mkstemp(
                suffix=path.suffix + '.tmp',
                prefix='levox_',
                dir=path.parent,
                text=True
            )
            
            try:
                # Write to temporary file
                with os.fdopen(temp_fd, mode, encoding='utf-8') as f:
                    f.write(content)
                    f.flush()
                    os.fsync(f.fileno())  # Ensure data is written to disk
                
                # Set secure permissions on temp file
                os.chmod(temp_path, 0o600)  # Read/write for owner only
                
                # Atomic rename (this is atomic on most filesystems)
                os.replace(temp_path, path)
                
            except Exception:
                # Clean up temp file if it exists
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
                raise
                
        except Exception as e:
            raise FileError(f"Failed to write file {file_path}: {e}")
    
    def _validate_file_path_for_write(self, file_path: Path) -> None:
        """Validate file path for write operations to prevent path traversal."""
        import os
        
        # Resolve the path to get absolute path
        try:
            resolved_path = file_path.resolve()
        except (OSError, RuntimeError):
            raise FileError(f"Invalid file path: {file_path}")
        
        # Check for path traversal patterns
        path_str = str(resolved_path)
        
        # Check for directory traversal patterns
        if '..' in path_str:
            raise FileError(f"Potentially dangerous path pattern detected: ..")
        
        # Check for double slashes (potential path manipulation)
        if '//' in path_str or '\\\\' in path_str:
            raise FileError(f"Potentially dangerous path pattern detected: // or \\\\")
        
        # Check for home directory expansion (only if ~ appears at the beginning of a path component)
        # This is more specific than just checking for ~ anywhere in the path
        # Only flag if it's exactly "~" or starts with "~/" which indicates home directory expansion
        path_parts = path_str.replace('\\', '/').split('/')
        for part in path_parts:
            if part == '~' or (part.startswith('~') and '/' in part):
                raise FileError(f"Potentially dangerous path pattern detected: {part}")
        
        # Check if parent directory exists and is writable
        parent_dir = resolved_path.parent
        if not parent_dir.exists():
            raise FileError(f"Parent directory does not exist: {parent_dir}")
        
        if not os.access(parent_dir, os.W_OK):
            raise FileError(f"Permission denied writing to directory: {parent_dir}")
    
    def write_file(self, file_path, content: str, mode: str = 'w') -> None:
        """Write content to a file (alias for _write_file_safe)."""
        self._write_file_safe(file_path, content, mode)


class FileProcessor:
    """High-performance file processing for enterprise-scale repositories.

    Responsibilities:
    - Efficient file discovery with intelligent filtering and gitignore support
    - Memory-mapped reading, streaming lines, and chunked processing
    - Change detection (git, mtime, checksum)
    - Parallel file processing with progress reporting and graceful shutdown
    """

    # File extension categories for enhanced discovery
    DEFAULT_SCANNABLE_EXTENSIONS = {
        '.py', '.js', '.java', '.go', '.ts', '.rb', '.php', '.cs', '.cpp', '.c', '.h', '.hpp',
        '.swift', '.kt', '.scala', '.rs', '.dart', '.vue', '.jsx', '.tsx', '.svelte'
    }
    
    DEFAULT_SECRET_HEAVY_FILES = {
        '.env', '.log', '.ini', '.cfg', '.conf', '.config', '.properties', '.yml', '.yaml',
        '.toml', '.json', '.xml', '.sql', '.sh', '.bat', '.ps1', '.bash', '.zsh'
    }
    
    OPTIONAL_EXTENSIONS = {
        '.txt', '.md', '.rst', '.adoc', '.tex', '.html', '.htm', '.css', '.scss', '.less',
        '.csv', '.tsv', '.xml', '.svg'
    }
    
    # Commonly skipped binary/media/archive extensions
    SKIP_EXTENSIONS = {
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico',
        '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar', '.xz', '.tgz',
        '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
        '.exe', '.dll', '.so', '.dylib', '.class', '.jar', '.war',
        '.mp3', '.mp4', '.mov', '.avi', '.mkv', '.webm', '.ogg',
        '.wasm', '.psd'
    }

    SKIP_DIR_NAMES = {
        '.git', '.svn', '.hg', 'node_modules', '__pycache__', '.venv', 'venv',
        'build', 'dist', 'target', 'bin', 'obj', '.idea', '.vscode', 'logs', 'tmp', 'temp',
        'vendor', 'coverage', 'static', 'assets', '.cache'
    }

    def __init__(self, config, logger: Optional[Any] = None):
        self.config = config
        self.logger = logger
        self.file_handler = FileHandler(config)
        self.stop_event = threading.Event()
        self.gitignore_patterns: List[str] = []
        self._load_gitignore(Path.cwd())
    
    def get_scannable_extensions(self) -> Set[str]:
        """Get the set of file extensions that should be scanned based on configuration."""
        scannable_extensions = set()
        
        # Always include default scannable extensions (source code)
        scannable_extensions.update(self.DEFAULT_SCANNABLE_EXTENSIONS)
        
        # Always include secret-heavy files (configs, logs, etc.)
        scannable_extensions.update(self.DEFAULT_SECRET_HEAVY_FILES)
        
        # Include optional extensions only if configured
        if getattr(self.config, 'scan_optional', False):
            scannable_extensions.update(self.OPTIONAL_EXTENSIONS)
        
        return scannable_extensions

    # --------------- Discovery and Filtering ---------------
    def _load_gitignore(self, root: Path) -> None:
        try:
            gitignore_path = root / '.gitignore'
            if gitignore_path.exists():
                patterns: List[str] = []
                for line in gitignore_path.read_text(encoding='utf-8', errors='ignore').splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    patterns.append(line)
                self.gitignore_patterns = patterns
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Failed to load .gitignore: {e}")

    def _is_ignored_by_gitignore(self, root: Path, path: Path) -> bool:
        try:
            # Convert to posix-style relative path for matching
            rel = path.relative_to(root).as_posix()
            for pat in self.gitignore_patterns:
                # Basic glob matching; not full .gitignore semantics but effective
                if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch('/' + rel, pat):
                    return True
            return False
        except Exception:
            return False

    def should_scan_file(self, root: Path, file_path: Path) -> bool:
        try:
            # Skip by directory name
            if any(part in self.SKIP_DIR_NAMES for part in file_path.parts):
                if self.logger:
                    self.logger.debug(f"Skipping {file_path}: contains skipped directory name")
                return False

            # Size filter
            try:
                size_mb = file_path.stat().st_size / 1024 / 1024
                if size_mb > self.config.performance.max_file_size_mb:
                    if self.logger:
                        self.logger.debug(f"Skipping {file_path}: too large ({size_mb:.2f}MB > {self.config.performance.max_file_size_mb}MB)")
                    return False
            except OSError:
                if self.logger:
                    self.logger.debug(f"Skipping {file_path}: cannot access file stats")
                return False

            # Extension filtering using enhanced categorization
            ext = file_path.suffix.lower()
            
            # Skip known binary/media/archive extensions
            if ext in self.SKIP_EXTENSIONS:
                if self.logger:
                    self.logger.debug(f"Skipping {file_path}: binary extension {ext}")
                return False
            
            # Check if extension is in scannable extensions
            scannable_extensions = self.get_scannable_extensions()
            if ext not in scannable_extensions:
                if self.logger:
                    self.logger.debug(f"Skipping {file_path}: extension {ext} not in scannable extensions")
                return False

            # Skip minified or bundled JS if configured
            if ext in {'.js', '.css'} and getattr(self.config.performance, 'skip_minified_js', True):
                name = file_path.name
                if '.min.' in name or name.endswith('.bundle.js') or name.endswith('.min.js') or name.endswith('.min.css'):
                    if self.logger:
                        self.logger.debug(f"Skipping {file_path}: minified/bundled asset")
                    return False

            # Binary sniffing
            if self.file_handler.is_binary_file(file_path):
                if self.logger:
                    self.logger.debug(f"Skipping {file_path}: detected as binary file")
                return False

            # Include patterns
            include_patterns = getattr(self.config, 'include_patterns', [])
            if include_patterns:
                if not any(fnmatch.fnmatch(str(file_path), pat) for pat in include_patterns):
                    if self.logger:
                        self.logger.debug(f"Skipping {file_path}: doesn't match include patterns")
                    return False

            # Exclude patterns
            exclude_patterns = getattr(self.config, 'exclude_patterns', [])
            if exclude_patterns:
                file_str = str(file_path)
                norm_str = file_str.replace('\\', '/')
                if any(fnmatch.fnmatch(file_str, pat) or fnmatch.fnmatch(norm_str, pat) for pat in exclude_patterns):
                    if self.logger:
                        self.logger.debug(f"Skipping {file_path}: matches exclude pattern")
                    return False

            # Smart test file detection
            if self._is_test_file(file_path):
                if self.logger:
                    self.logger.debug(f"Skipping {file_path}: detected as test file")
                return False

            # Gitignore-style patterns
            if self._is_ignored_by_gitignore(root, file_path):
                if self.logger:
                    self.logger.debug(f"Skipping {file_path}: ignored by gitignore")
                return False

            return True
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Error checking {file_path}: {e}")
            return False

    def _is_test_file(self, file_path: Path) -> bool:
        """
        Detect if a file is a test file using smart detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is detected as a test file
        """
        file_str = str(file_path).lower()
        file_name = file_path.name.lower()
        
        # Check file name patterns
        test_name_patterns = [
            'test_', '_test', 'spec_', '_spec', 'mock_', '_mock',
            'fixture_', '_fixture', 'example_', '_example', 'sample_', '_sample',
            'dummy_', '_dummy', 'stub_', '_stub', 'fake_', '_fake'
        ]
        
        for pattern in test_name_patterns:
            if pattern in file_name:
                return True
        
        # Check directory patterns
        test_dir_patterns = [
            '/test/', '/tests/', '/testing/', '/spec/', '/specs/',
            '/fixture/', '/fixtures/', '/mock/', '/mocks/',
            '/example/', '/examples/', '/sample/', '/samples/',
            '/dummy/', '/dummies/', '/stub/', '/stubs/',
            '/fake/', '/fakes/', '/demo/', '/demos/',
            '/sandbox/', '/playground/', '/scaffold/', '/scaffolds/'
        ]
        
        for pattern in test_dir_patterns:
            if pattern in file_str:
                return True
        
        # Check for test file extensions
        test_extensions = ['.test.py', '.spec.js', '.spec.ts', '.test.js', '.test.ts']
        for ext in test_extensions:
            if file_str.endswith(ext):
                return True
        
        # Check file content for test indicators (if file is small enough)
        try:
            file_size = file_path.stat().st_size
            if file_size < 1024 * 1024:  # Only check files < 1MB
                content = self.read_text(file_path)
                if content:
                    content_lower = content.lower()
                    
                    # Test framework imports
                    test_imports = [
                        'import unittest', 'import pytest', 'from unittest import',
                        'import jest', 'import mocha', 'import chai', 'import sinon',
                        'import mock', 'from mock import', 'import factory_boy',
                        'import factory', 'from factory import'
                    ]
                    
                    for test_import in test_imports:
                        if test_import in content_lower:
                            return True
                    
                    # Test class/function patterns
                    test_patterns = [
                        'class test', 'def test_', 'def test(', 'it(', 'describe(',
                        'test(', 'assert ', 'expect(', 'should ', 'given(',
                        'when(', 'then(', 'setup(', 'teardown(', 'before(',
                        'after(', 'fixture(', 'mock(', 'stub(', 'spy('
                    ]
                    
                    test_pattern_count = 0
                    for pattern in test_patterns:
                        if pattern in content_lower:
                            test_pattern_count += 1
                    
                    # If multiple test patterns found, likely a test file
                    if test_pattern_count >= 3:
                        return True
                        
        except Exception:
            # If we can't read the file, continue with other checks
            pass
        
        return False

    def discover_files(self, root: Path, max_files: Optional[int] = None) -> Iterator[Path]:
        count = 0
        total_checked = 0
        skipped_by_filter = 0
        skipped_by_extension = 0
        
        if self.logger:
            self.logger.debug(f"Starting file discovery in {root}")
        
        # Get scannable extensions for logging
        scannable_extensions = self.get_scannable_extensions()
        if self.logger:
            self.logger.debug(f"Scannable extensions: {sorted(scannable_extensions)}")
            if getattr(self.config, 'scan_optional', False):
                self.logger.debug("Optional file types (.txt, .md) are enabled")
            else:
                self.logger.debug("Optional file types (.txt, .md) are disabled")
        
        for file_path in root.rglob('*'):
            if self.stop_event.is_set():
                break
            if not file_path.is_file():
                continue
                
            total_checked += 1
            
            if self.should_scan_file(root, file_path):
                yield file_path
                count += 1
                if self.logger:
                    self.logger.debug(f"Discovered file: {file_path}")
                if max_files and count >= max_files:
                    break
            else:
                skipped_by_filter += 1
                # Count extension-based skips separately for better debugging
                ext = file_path.suffix.lower()
                if ext not in scannable_extensions and ext not in self.SKIP_EXTENSIONS:
                    skipped_by_extension += 1
                if self.logger:
                    self.logger.debug(f"Skipped file: {file_path}")
        
        if self.logger:
            self.logger.info(f"File discovery complete: checked {total_checked} files, found {count} scannable files, skipped {skipped_by_filter} files (including {skipped_by_extension} by extension)")
            self.logger.info(f"Extension breakdown: {len(scannable_extensions)} scannable extensions, {len(self.SKIP_EXTENSIONS)} skipped extensions")

    # --------------- Reading APIs ---------------
    def read_text(self, file_path: Path) -> Optional[str]:
        try:
            return self.file_handler.read_file(file_path)
        except Exception:
            return None

    def stream_lines(self, file_path: Path, encoding: Optional[str] = None) -> Iterator[str]:
        try:
            enc = encoding or self.file_handler.get_file_encoding(file_path)
            with open(file_path, 'r', encoding=enc, errors='ignore') as f:
                for line in f:
                    yield line
        except Exception:
            # Fallback: attempt binary read and decode by chunks
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    try:
                        yield chunk.decode('utf-8')
                    except UnicodeDecodeError:
                        yield chunk.decode('latin-1', errors='replace')

    def read_chunks(self, file_path: Path, chunk_size: int = 1024 * 1024) -> Iterator[bytes]:
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b''):
                    yield chunk
        except Exception:
            return

    # --------------- Change Detection ---------------
    def _md5_checksum(self, file_path: Path) -> str:
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def get_modified_files(self, root: Path, last_scan_time: Optional[float], checksum_cache: Dict[str, str]) -> List[Path]:
        modified: List[Path] = []
        since_ts = last_scan_time or 0
        for file_path in root.rglob('*'):
            if not file_path.is_file():
                continue
            if not self.should_scan_file(root, file_path):
                continue
            try:
                # Timestamp based
                if since_ts and file_path.stat().st_mtime <= since_ts:
                    continue
                # Checksum based
                path_str = str(file_path)
                current = self._md5_checksum(file_path)
                if path_str not in checksum_cache or checksum_cache.get(path_str) != current:
                    modified.append(file_path)
            except OSError:
                continue
        return modified

    # --------------- Parallel Processing ---------------
    def parallel_process(
        self,
        files: List[Path],
        func: Callable[[Path], Any],
        max_workers: Optional[int] = None,
        progress_cb: Optional[Callable[[int, int, float], None]] = None
    ) -> Iterator[Tuple[Path, Any, Optional[BaseException]]]:
        if not files:
            return iter(())
        total = len(files)
        processed = 0
        start = time.time()
        workers = max_workers or os.cpu_count() or 4
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_file = {executor.submit(func, f): f for f in files}
            for future in as_completed(future_to_file):
                fpath = future_to_file[future]
                err: Optional[BaseException] = None
                res: Any = None
                try:
                    res = future.result()
                except BaseException as e:  # Include KeyboardInterrupt
                    err = e
                processed += 1
                # Progress/ETA
                if progress_cb:
                    elapsed = max(1e-6, time.time() - start)
                    rate = processed / elapsed
                    remaining = max(0, total - processed)
                    eta = remaining / rate if rate > 0 else float('inf')
                    try:
                        progress_cb(processed, total, eta)
                    except Exception:
                        pass
                yield (fpath, res, err)

    def stop(self) -> None:
        self.stop_event.set()
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """Create a backup of a file."""
        try:
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            import shutil
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            raise FileError(f"Failed to create backup: {e}")
    
    def cleanup_backups(self, directory: Path, max_backups: int = 5) -> int:
        """Clean up old backup files."""
        try:
            backup_files = []
            for file_path in directory.rglob('*.backup'):
                backup_files.append((file_path, file_path.stat().st_mtime))
            
            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda x: x[1])
            
            # Remove old backups
            removed_count = 0
            for backup_path, _ in backup_files[:-max_backups]:
                try:
                    backup_path.unlink()
                    removed_count += 1
                except Exception:
                    continue
            
            return removed_count
            
        except Exception as e:
            raise FileError(f"Failed to cleanup backups: {e}")
