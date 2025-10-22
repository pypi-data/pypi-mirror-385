"""
Large repository handler for memory-efficient scanning of extremely large repositories.
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import Iterator, Tuple, Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from ..models.repo_info import RepoMetadata, CloneProgress
from ..core.engine import DetectionEngine
from ..models.detection_result import DetectionResult, FileResult
from ..detection.regex_engine import RegexEngine
from ..core.exceptions import DetectionError


class LargeRepoHandler:
    """Handler for scanning extremely large repositories efficiently."""
    
    def __init__(self, config, max_workers: int = 4):
        """Initialize the large repository handler."""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.max_workers = max_workers
        self.regex_engine = RegexEngine(config)
    
    def scan_repository_stream(self, repo_metadata: RepoMetadata, 
                            file_iterator: Iterator[Tuple[str, bytes]],
                            progress_callback: Optional[callable] = None) -> DetectionResult:
        """
        Scan repository files as they're streamed without holding entire repo in memory.
        
        Args:
            repo_metadata: Repository metadata
            file_iterator: Iterator yielding (file_path, file_content_bytes)
            progress_callback: Optional callback for progress updates
            
        Returns:
            DetectionResult with scan results
        """
        start_time = time.time()
        
        # Create scan result container
        scan_result = DetectionResult(
            scan_id=f"repo_stream_{int(time.time())}",
            scan_duration=0.0,
            license_tier=self.config.license.tier.value,
            scan_path=f"streaming:{repo_metadata.full_name}",
            files_scanned=0,
            files_with_matches=0,
            total_matches=0,
            total_scan_time=0.0,
            average_file_time=0.0,
            memory_peak_mb=0.0,
            false_positive_rate=0.0,
            confidence_average=0.0
        )
        
        files_processed = 0
        total_matches = 0
        
        try:
            # Process files in batches for memory efficiency
            batch_size = 10
            file_batch = []
            
            for file_path, file_content in file_iterator:
                file_batch.append((file_path, file_content))
                
                # Process batch when it reaches batch_size
                if len(file_batch) >= batch_size:
                    batch_results = self._process_file_batch(file_batch)
                    
                    for file_result in batch_results:
                        scan_result.add_file_result(file_result)
                        if file_result.matches:
                            scan_result.files_with_matches += 1
                            total_matches += len(file_result.matches)
                    
                    files_processed += len(file_batch)
                    file_batch = []
                    
                    # Update progress
                    if progress_callback:
                        progress_callback(CloneProgress(
                            "scanning", 
                            (files_processed / max(files_processed, 1)) * 100,
                            f"Scanned {files_processed} files, found {total_matches} violations"
                        ))
            
            # Process remaining files in the last batch
            if file_batch:
                batch_results = self._process_file_batch(file_batch)
                
                for file_result in batch_results:
                    scan_result.add_file_result(file_result)
                    if file_result.matches:
                        scan_result.files_with_matches += 1
                        total_matches += len(file_result.matches)
                
                files_processed += len(file_batch)
            
            # Calculate final metrics
            scan_result.scan_duration = time.time() - start_time
            scan_result.total_scan_time = scan_result.scan_duration
            scan_result.files_scanned = files_processed
            scan_result.total_matches = total_matches
            scan_result.calculate_metrics()
            
            self.logger.info(f"Streaming scan completed: {files_processed} files, {total_matches} matches in {scan_result.scan_duration:.2f}s")
            
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Streaming scan failed: {e}")
            raise DetectionError(f"Failed to scan repository stream: {e}")
    
    def _process_file_batch(self, file_batch: List[Tuple[str, bytes]]) -> List[FileResult]:
        """Process a batch of files concurrently."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all file processing tasks
            future_to_file = {
                executor.submit(self._process_single_file, file_path, file_content): file_path
                for file_path, file_content in file_batch
            }
            
            # Collect results
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_result = future.result()
                    results.append(file_result)
                except Exception as e:
                    self.logger.error(f"Failed to process file {file_path}: {e}")
                    # Create empty result for failed file
                    from ..models.detection_result import FileResult
                    results.append(FileResult(
                        file_path=file_path,
                        matches=[],
                        scan_time=0.0,
                        language="unknown",
                        file_size_bytes=0,
                        lines_scanned=0,
                        confidence_score=0.0
                    ))
        
        return results
    
    def _process_single_file(self, file_path: str, file_content: bytes) -> FileResult:
        """Process a single file and return detection results."""
        try:
            # Decode file content
            try:
                content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = file_content.decode('latin-1')
                except UnicodeDecodeError:
                    content = file_content.decode('utf-8', errors='replace')
            
            # Determine language from file extension
            language = self._get_language_from_path(file_path)
            
            # Scan content for patterns
            matches = self.regex_engine.scan_content(
                content=content,
                language=language,
                context_name=f"streaming:{file_path}"
            )
            
            # Create file result
            from ..models.detection_result import FileResult
            return FileResult(
                file_path=file_path,
                matches=matches,
                scan_time=0.0,  # Not measured for streaming
                language=language,
                file_size_bytes=len(file_content),
                lines_scanned=len(content.splitlines()),
                confidence_score=sum(match.confidence for match in matches) / max(len(matches), 1)
            )
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def _get_language_from_path(self, file_path: str) -> str:
        """Determine programming language from file path."""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab',
            '.pl': 'perl',
            '.sh': 'shell',
            '.bat': 'batch',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'config',
            '.conf': 'config',
            '.properties': 'properties',
            '.env': 'env',
            '.dockerfile': 'dockerfile',
            '.md': 'markdown',
            '.txt': 'text',
            '.log': 'log'
        }
        
        return language_map.get(extension, 'unknown')
    
    def optimize_for_large_repo(self, repo_metadata: RepoMetadata) -> Dict[str, Any]:
        """
        Get optimization recommendations for scanning a large repository.
        
        Returns:
            Dictionary with optimization settings
        """
        size_mb = repo_metadata.size_mb
        
        optimizations = {
            'use_streaming': size_mb > 1000,  # Use streaming for repos > 1GB
            'batch_size': 5 if size_mb > 2000 else 10,
            'max_workers': 2 if size_mb > 5000 else 4,
            'skip_binary_files': True,
            'skip_large_files': True,
            'max_file_size_mb': 10 if size_mb > 2000 else 50,
            'memory_limit_mb': 512 if size_mb > 5000 else 1024
        }
        
        return optimizations
    
    def estimate_scan_time(self, repo_metadata: RepoMetadata, 
                          estimated_files: int) -> float:
        """
        Estimate scan time for a repository.
        
        Args:
            repo_metadata: Repository metadata
            estimated_files: Estimated number of files to scan
            
        Returns:
            Estimated scan time in seconds
        """
        # Base time per file (rough estimate)
        base_time_per_file = 0.1  # 100ms per file
        
        # Adjust based on repository size
        size_factor = 1.0
        if repo_metadata.size_mb > 1000:
            size_factor = 1.5  # Larger files take longer
        elif repo_metadata.size_mb > 5000:
            size_factor = 2.0  # Much larger files
        
        # Adjust based on file count
        file_factor = 1.0
        if estimated_files > 10000:
            file_factor = 1.2  # More files = more overhead
        
        estimated_time = estimated_files * base_time_per_file * size_factor * file_factor
        
        return estimated_time
