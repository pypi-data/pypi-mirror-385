"""
Production-grade detection engine orchestrator for Levox.
Implements multi-level PII detection pipeline with streaming, parallel processing,
incremental scanning, licensing integration, circuit breaker pattern, and telemetry.
"""

import os
import sys
import time
import uuid
import mmap
import json
import yaml
import asyncio
import logging
import hashlib
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, AsyncIterator, Iterator, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from contextlib import contextmanager
import threading
import queue
import signal
import subprocess
import psutil

# Core imports
from .config import Config, LicenseTier, RiskLevel, load_default_config, ThreadSafeConfig
from .exceptions import DetectionError, PerformanceError, LicenseError, MLModelError, RateLimitExceededError
from .license_client import get_license_client, validate_license, LicenseInfo
from .rate_limiter import get_rate_limiter, check_feature_usage, use_feature

# Detection engines
from ..detection.regex_engine import RegexEngine
from ..detection.ast_analyzer import ASTAnalyzer
from ..detection.context_analyzer import ContextAnalyzer
from ..detection.dataflow import DataflowAnalyzer
from ..detection.cfg_analyzer import CFGAnalyzer
from ..detection.ml_filter import MLFilter

# Compliance engine
from ..compliance.gdpr_analyzer import GDPRAnalyzer

# Parser integration
from ..parsers import get_parser, detect_language

# Models and utilities
from ..models.detection_result import DetectionResult, FileResult, DetectionMatch
from ..utils.file_handler import FileHandler, FileProcessor
from ..utils.performance import PerformanceMonitor
from ..utils.validators import Validator
from ..utils.progress_manager import ProgressManager, ProgressInfo


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for ML model calls."""
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open
    success_count: int = 0


@dataclass
class TelemetryData:
    """Telemetry data for audit logging."""
    timestamp: datetime
    operation: str
    duration: float
    file_count: int
    match_count: int
    detection_levels_used: List[str]
    license_tier: str
    memory_usage_mb: float
    cpu_usage_percent: float
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DetectionEngine:
    """Production-grade detection engine orchestrator with full feature set."""
    
    def __init__(self, config: Optional[Config] = None, config_path: Optional[str] = None):
        """Initialize the detection engine with comprehensive configuration."""
        # Load configuration with hot-reload support
        if config_path:
            base_config = Config.from_file(config_path)
            self.config_wrapper = ThreadSafeConfig(base_config, Path(config_path))
        elif config:
            self.config_wrapper = ThreadSafeConfig(config)
        else:
            self.config_wrapper = ThreadSafeConfig(load_default_config())
        
        # Register config change callback
        self.config_wrapper.register_change_callback(self._on_config_changed)
        
        # Core components
        self.performance_monitor = PerformanceMonitor()
        self.file_handler = FileHandler(self.config_wrapper.get_config())
        self.validator = Validator()
        
        # Initialize logging
        self._setup_logging()
        # Initialize file processor after logger is set
        self.file_processor = FileProcessor(self.config_wrapper.get_config(), logger=self.logger)
        
        # License validation and storage
        self._license_info: Optional[LicenseInfo] = None
        
        # Validate license before initializing engines
        self._validate_license()
        
        # Initialize detection engines based on license tier
        self._initialize_engines()
        
        # Circuit breaker for ML model calls
        self.ml_circuit_breaker = CircuitBreakerState()
        self.circuit_breaker_threshold = 5  # failures before opening
        self.circuit_breaker_timeout = timedelta(minutes=5)
        
        # Telemetry and audit logging
        self.telemetry_data: List[TelemetryData] = []
        self.audit_logger = self._setup_audit_logger()
        
        # Performance tracking
        self.start_time = None
        self.memory_start = None
        # CI env flag
        self.is_ci_environment = self._detect_ci_environment()
        
        # Incremental scanning state
        self.file_checksums: Dict[str, str] = {}
        self.last_scan_time: Optional[datetime] = None
        
        # Config watching
        self.config_watch_thread = None
        
        # Streaming results queue
        self.results_queue = queue.Queue()
        self.streaming_enabled = False
        
        # Graceful shutdown handling
        self._shutdown_event = threading.Event()
        self._setup_signal_handlers()
    
    def _on_config_changed(self, old_config: Config, new_config: Config):
        """Handle configuration changes during hot-reload."""
        self.logger.info("Configuration changed - reinitializing engines")
        
        try:
            # Update file handler
            self.file_handler = FileHandler(new_config)
            self.file_processor = FileProcessor(new_config, logger=self.logger)
            
            # Reinitialize detection engines if license tier changed
            if old_config.license.tier != new_config.license.tier:
                self.logger.info(f"License tier changed: {old_config.license.tier} -> {new_config.license.tier}")
                self._initialize_engines()
            
            # Update patterns if they changed
            if old_config.patterns != new_config.patterns:
                self.logger.info("Detection patterns updated")
                if hasattr(self, 'regex_engine'):
                    self.regex_engine = RegexEngine(new_config)
                if hasattr(self, 'ast_analyzer'):
                    self.ast_analyzer = ASTAnalyzer(new_config)
                if hasattr(self, 'dataflow_analyzer'):
                    self.dataflow_analyzer = DataflowAnalyzer(new_config)
            
            # Update ML filter if ML settings changed
            if (hasattr(old_config, 'ml_enabled') and hasattr(new_config, 'ml_enabled') and 
                old_config.ml_enabled != new_config.ml_enabled):
                self.logger.info("ML settings updated")
                if hasattr(self, 'ml_filter'):
                    self.ml_filter = MLFilter(new_config)
            
            # Update GDPR analyzer if GDPR settings changed
            if (hasattr(old_config, 'enable_gdpr') and hasattr(new_config, 'enable_gdpr') and 
                old_config.enable_gdpr != new_config.enable_gdpr):
                self.logger.info("GDPR settings updated")
                if hasattr(self, 'gdpr_analyzer'):
                    self.gdpr_analyzer = GDPRAnalyzer(new_config)
            
        except Exception as e:
            self.logger.error(f"Failed to handle config change: {e}")
    
    @property
    def config(self) -> Config:
        """Get current configuration (for backward compatibility)."""
        return self.config_wrapper.get_config()
    
    def shutdown(self):
        """Shutdown the engine and cleanup resources."""
        self.logger.info("Shutting down DetectionEngine")
        
        # Stop config watching
        if hasattr(self, 'config_wrapper'):
            self.config_wrapper.stop_watching()
        
        # Set shutdown event
        self._shutdown_event.set()
        
        self.logger.info("DetectionEngine shutdown complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
    
    def _initialize_engines(self) -> None:
        """Initialize detection engines based on license features."""
        try:
            # Level 1: Regex Engine (always available)
            self.regex_engine = RegexEngine(self.config.patterns)
            
            # Level 2: AST Analyzer (Premium+)
            self.ast_analyzer = None
            if self.config.is_feature_enabled("ast_analysis") or getattr(self.config, 'enable_ast', False):
                try:
                    self.ast_analyzer = ASTAnalyzer(self.config)
                except Exception as e:
                    # If parsers cannot initialize in environment, degrade gracefully
                    self.logger.warning(f"AST analyzer unavailable: {e}. Continuing with regex-only.")
                    self.ast_analyzer = None
            
            # Context Analyzer (Premium+)
            self.context_analyzer = None
            if getattr(self.config, 'enable_context_analysis', True):
                try:
                    self.context_analyzer = ContextAnalyzer(self.config)
                    self.logger.info("Context Analyzer initialized successfully")
                except Exception as e:
                    self.logger.warning(f"Context Analyzer initialization failed: {e}")
                    self.context_analyzer = None
            
            # Level 3: Dataflow Analyzer (Enterprise)
            self.dataflow_analyzer = None
            if self.config.is_feature_enabled("dataflow_analysis") or getattr(self.config, 'enable_dataflow', False):
                self.dataflow_analyzer = DataflowAnalyzer(self.config)
            
            # Level 4: CFG Analyzer (Premium+)
            self.cfg_analyzer = None
            if self.config.is_feature_enabled("cfg_analysis"):
                try:
                    self.cfg_analyzer = CFGAnalyzer(self.config)
                    self.logger.info("CFG Analyzer initialized successfully")
                except Exception as e:
                    self.logger.warning(f"CFG Analyzer initialization failed: {e}")
                    self.cfg_analyzer = None
            
            # Level 5: ML Filter (Enterprise)
            self.ml_filter = None
            if (self.config.is_feature_enabled("ml_filtering") or 
                getattr(self.config, 'enable_ml', False) or 
                getattr(self.config, 'ml_enabled', False) or
                self.config.license.tier.value == 'enterprise'):
                try:
                    self.ml_filter = MLFilter(self.config)
                    self.logger.info("ML Filter initialized successfully")
                except Exception as e:
                    self.logger.warning(f"ML Filter initialization failed: {e}")
                    self.ml_filter = None
            
            # Level 6: GDPR Compliance Analyzer (Premium+)
            self.gdpr_analyzer = None
            if (self.config.is_feature_enabled("gdpr_compliance") or 
                getattr(self.config, 'enable_gdpr', False) or
                self.config.license.tier.value in ['premium', 'enterprise']):
                try:
                    self.gdpr_analyzer = GDPRAnalyzer(self.config)
                    self.logger.info("GDPR Analyzer initialized successfully")
                except Exception as e:
                    self.logger.warning(f"GDPR Analyzer initialization failed: {e}")
                    self.gdpr_analyzer = None
                
        except Exception as e:
            raise DetectionError(f"Failed to initialize detection engines: {e}")
    
    def _setup_logging(self) -> None:
        """Setup comprehensive logging system."""
        self.logger = logging.getLogger(f"levox.engine.{id(self)}")
        
        # Don't set a specific level - inherit from root logger
        # This allows the interactive CLI to control logging globally
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _setup_audit_logger(self) -> logging.Logger:
        """Setup audit logging for compliance."""
        audit_logger = logging.getLogger(f"levox.audit.{id(self)}")
        audit_logger.setLevel(logging.INFO)
        
        # File handler for audit logs
        if self.config.log_file:
            try:
                # Ensure the log directory exists
                log_path = Path(self.config.log_file).parent
                log_path.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(f"{self.config.log_file}.audit")
                formatter = logging.Formatter(
                    '%(asctime)s - AUDIT - %(message)s'
                )
                file_handler.setFormatter(formatter)
                audit_logger.addHandler(file_handler)
            except Exception as e:
                # Fallback to console logging if file logging fails
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                audit_logger.addHandler(console_handler)
                self.logger.warning(f"Failed to setup audit file logging: {e}")
        
        return audit_logger
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown")
            self._shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _validate_license(self) -> None:
        """Validate license configuration against license server."""
        try:
            # Get license information from server
            license_info = validate_license()
            
            if not license_info.is_valid:
                self.logger.warning("Using demo mode - no valid license found")
                # Update config to standard tier for demo
                self.config.update_license_tier(LicenseTier.STARTER)
                return
            
            # Update config with validated license tier
            self.config.update_license_tier(license_info.tier)
            self.config.license.license_key = license_info.license_key
            self.config.license.expiry_date = license_info.expires_at.isoformat()
            
            self.logger.info(f"License validated: {license_info.tier.value} (expires: {license_info.expires_at.strftime('%Y-%m-%d')})")
            
            # Store license info for feature validation
            self._license_info = license_info
            
        except Exception as e:
            self.logger.error(f"License validation failed: {e}")
            # Fall back to standard tier
            self.config.update_license_tier(LicenseTier.STARTER)
            self._license_info = None
    
    def _detect_ci_environment(self) -> bool:
        """Detect if running in CI environment."""
        ci_indicators = [
            'CI', 'CONTINUOUS_INTEGRATION', 'BUILD_NUMBER',
            'JENKINS_URL', 'GITHUB_ACTIONS', 'GITLAB_CI',
            'TRAVIS', 'CIRCLECI', 'BAMBOO_BUILD_NUMBER'
        ]
        
        return any(os.getenv(indicator) for indicator in ci_indicators)
    
    def _start_config_watcher(self) -> None:
        """Start configuration file watcher for hot-reload."""
        if not hasattr(self.config, 'config_file_path'):
            return
            
        def watch_config():
            while not self._shutdown_event.is_set():
                try:
                    if hasattr(self.config, 'config_file_path'):
                        config_path = Path(self.config.config_file_path)
                        if config_path.exists():
                            current_modified = config_path.stat().st_mtime
                            if (self.config_last_modified and 
                                current_modified > self.config_last_modified):
                                self.logger.info("Configuration file changed, reloading...")
                                self.reload_configuration()
                            self.config_last_modified = current_modified
                    
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    self.logger.error(f"Config watcher error: {e}")
                    time.sleep(10)
        
        self.config_watch_thread = threading.Thread(target=watch_config, daemon=True)
        self.config_watch_thread.start()
    
    def _log_telemetry(self, operation: str, duration: float, file_count: int, 
                      match_count: int, detection_levels: List[str]) -> None:
        """Log telemetry data for monitoring and analytics."""
        try:
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            cpu_usage = process.cpu_percent()
            
            telemetry = TelemetryData(
                timestamp=datetime.utcnow(),
                operation=operation,
                duration=duration,
                file_count=file_count,
                match_count=match_count,
                detection_levels_used=detection_levels,
                license_tier=self.config.license.tier.value,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage
            )
            
            self.telemetry_data.append(telemetry)
            
            # Keep only last 1000 telemetry entries
            if len(self.telemetry_data) > 1000:
                self.telemetry_data = self.telemetry_data[-1000:]
            
            # Audit log
            self.audit_logger.info(json.dumps({
                'operation': operation,
                'duration': duration,
                'file_count': file_count,
                'match_count': match_count,
                'license_tier': self.config.license.tier.value,
                'timestamp': telemetry.timestamp.isoformat()
            }))
            
        except Exception as e:
            self.logger.warning(f"Failed to log telemetry: {e}")
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate file checksum for incremental scanning."""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""
    
    # MAIN SCANNING METHODS
    
    def scan_repository(self, repository_path: str, max_files: Optional[int] = None) -> DetectionResult:
        """Full repository scan with all applicable detection levels."""
        return self.scan_directory(repository_path, max_files)
    
    def scan_directory(self, directory_path: str, max_workers: Optional[int] = None) -> DetectionResult:
        """Scan a directory with concurrent file processing."""
        try:
            directory = Path(directory_path)
            if not directory.exists() or not directory.is_dir():
                raise DetectionError(f"Directory does not exist or is not a directory: {directory}")
            
            # Determine number of workers (autoscale)
            if max_workers is None:
                cpu = os.cpu_count() or 4
                desired = self.config.performance.concurrent_workers
                if not desired or desired <= 0:
                    desired = max(4, min(16, cpu * 2))
                max_workers = min(desired, 32)
            
            self.logger.info(f"Starting concurrent directory scan with {max_workers} workers: {directory}")
            
            # Discover files
            files_to_scan = list(self._discover_files_streaming(directory))
            total_files = len(files_to_scan)
            
            if total_files == 0:
                self.logger.warning(f"No files found to scan in directory: {directory}")
                return self._create_empty_scan_result(directory_path)
            
            # Create scan result container
            scan_result = DetectionResult(
                scan_id=str(uuid.uuid4()),
                scan_duration=0.0,
                license_tier=self.config.license.tier.value,
                scan_path=str(directory),
                files_scanned=0,
                files_with_matches=0,
                total_matches=0,
                total_scan_time=0.0,
                average_file_time=0.0,
                memory_peak_mb=0.0,
                false_positive_rate=0.0,
                confidence_average=0.0
            )
            
            start_time = time.time()
            
            # Use progress manager for file scanning
            progress_manager = ProgressManager(quiet=False, theme='smooth')
            
            with progress_manager.file_scanning(total_files, "Scanning") as progress_callback:
                # Process files concurrently
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all file scan tasks
                    future_to_file = {
                        executor.submit(self._scan_file_with_cache, file_path): file_path 
                        for file_path in files_to_scan
                    }
                    
                    # Process completed scans
                    completed_files = 0
                    for future in as_completed(future_to_file):
                        file_path = future_to_file[future]
                        try:
                            file_result = future.result()
                            scan_result.add_file_result(file_result)
                            completed_files += 1
                            
                            # Update progress
                            progress_info = ProgressInfo(
                                current=completed_files,
                                total=total_files,
                                percentage=(completed_files / total_files) * 100,
                                message=f"Scanning {Path(file_path).name}",
                                stage="Processing",
                                findings_count=len(file_result.matches) if file_result.matches else 0
                            )
                            progress_callback(progress_info)
                            
                            # Log progress
                            if completed_files % 10 == 0 or completed_files == total_files:
                                self.logger.info(f"Scan progress: {completed_files}/{total_files} files processed")
                            
                        except Exception as e:
                            self.logger.error(f"Failed to scan file {file_path}: {e}")
                            scan_result.scan_errors.append(f"File {file_path}: {e}")
                            completed_files += 1
                            
                            # Update progress even for failed files
                            progress_info = ProgressInfo(
                                current=completed_files,
                                total=total_files,
                                percentage=(completed_files / total_files) * 100,
                                message=f"Error in {Path(file_path).name}",
                                stage="Error",
                                findings_count=0
                            )
                            progress_callback(progress_info)
            
            # Calculate final metrics
            scan_result.scan_duration = time.time() - start_time
            scan_result.total_scan_time = scan_result.scan_duration
            scan_result.calculate_metrics()
            
            # Record memory usage
            try:
                process = psutil.Process()
                scan_result.memory_peak_mb = process.memory_info().rss / 1024 / 1024
            except Exception:
                scan_result.memory_peak_mb = 0.0
            
            self.logger.info(f"Directory scan completed: {total_files} files, {scan_result.total_matches} matches in {scan_result.scan_duration:.2f}s")
            
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Directory scan failed: {directory_path}: {e}")
            raise DetectionError(f"Directory scan failed: {directory_path}: {e}")
    
    def scan_repository_stream(self, repo_metadata, file_iterator, progress_callback=None):
        """
        Scan repository files as they're streamed without holding entire repo in memory.
        
        Args:
            repo_metadata: Repository metadata
            file_iterator: Iterator yielding (file_path, file_content_bytes)
            progress_callback: Optional callback for progress updates
            
        Returns:
            DetectionResult with scan results
        """
        try:
            from ..utils.large_repo_handler import LargeRepoHandler
            
            # Initialize large repo handler
            handler = LargeRepoHandler(self.config, max_workers=self.config.performance.concurrent_workers)
            
            # Use the handler to perform streaming scan
            return handler.scan_repository_stream(repo_metadata, file_iterator, progress_callback)
            
        except Exception as e:
            self.logger.error(f"Repository stream scan failed: {e}")
            raise DetectionError(f"Repository stream scan failed: {e}")
    
    def _scan_file_with_cache(self, file_path: Path) -> FileResult:
        """Scan a single file with caching support."""
        try:
            # Check cache first
            cache_key = self._get_file_cache_key(file_path)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result and not self._is_cache_expired(cached_result):
                self.logger.debug(f"Using cached result for {file_path}")
                return cached_result
            
            # Perform actual scan using internal method
            file_result = self._scan_file_internal(file_path)
            
            # Cache the result
            self._cache_result(cache_key, file_result)
            
            return file_result
            
        except Exception as e:
            self.logger.error(f"File scan with cache failed: {file_path}: {e}")
            raise
    
    def _get_file_cache_key(self, file_path: Path) -> str:
        """Generate cache key for a file based on path, size, and modification time."""
        try:
            stat = file_path.stat()
            cache_data = f"{file_path}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.sha256(cache_data.encode()).hexdigest()
        except Exception:
            # Fallback to path-based key
            return hashlib.sha256(str(file_path).encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[FileResult]:
        """Retrieve cached scan result."""
        try:
            if hasattr(self, '_scan_cache') and cache_key in self._scan_cache:
                return self._scan_cache[cache_key]
        except Exception:
            pass
        return None
    
    def _cache_result(self, cache_key: str, file_result: FileResult) -> None:
        """Cache scan result."""
        try:
            if not hasattr(self, '_scan_cache'):
                self._scan_cache = {}
            
            # Limit cache size
            if len(self._scan_cache) > 1000:
                # Remove oldest entries
                oldest_keys = sorted(self._scan_cache.keys())[:100]
                for key in oldest_keys:
                    del self._scan_cache[key]
            
            self._scan_cache[cache_key] = file_result
            
        except Exception as e:
            self.logger.debug(f"Failed to cache result: {e}")
    
    def _is_cache_expired(self, cached_result: FileResult) -> bool:
        """Check if cached result is expired."""
        try:
            # Cache expires after 1 hour
            cache_age = time.time() - cached_result.metadata.get('scan_timestamp', 0)
            return cache_age > 3600
        except Exception:
            return True
    
    def _create_empty_scan_result(self, scan_path: str) -> DetectionResult:
        """Create an empty scan result for directories with no files."""
        return DetectionResult(
            scan_id=str(uuid.uuid4()),
            scan_duration=0.0,
            license_tier=self.config.license.tier.value,
            scan_path=scan_path,
            files_scanned=0,
            files_with_matches=0,
            total_matches=0,
            total_scan_time=0.0,
            average_file_time=0.0,
            memory_peak_mb=0.0,
            false_positive_rate=0.0,
            confidence_average=0.0
        )
    
    def scan_incremental(self, directory_path: str) -> DetectionResult:
        """Perform incremental scan of modified files with CI optimization."""
        start_time = time.time()
        self.start_time = start_time
        
        detection_levels_used = ["incremental"]
        
        # Add GDPR compliance if enabled
        if self.config.is_feature_enabled("gdpr_compliance"):
            detection_levels_used.append("gdpr_compliance")
        
        try:
            self.logger.info(f"Starting incremental scan of {directory_path}")
            
            # Find modified files
            modified_files = self._find_modified_files_advanced(directory_path)
            
            if not modified_files:
                self.logger.info("No modified files found for incremental scan")
                return self._create_empty_result(start_time)
            
            self.logger.info(f"Found {len(modified_files)} modified files")
            
            # Create result container
            results = self._create_result_container(start_time)
            
            # Scan only modified files
            self._scan_files_parallel(modified_files, results)
            
            # Update file checksums
            for file_path in modified_files:
                self.file_checksums[str(file_path)] = self._calculate_file_checksum(file_path)
            
            # Update last scan time
            self.last_scan_time = datetime.utcnow()
            
            # Finalize results
            self._finalize_results(results, start_time)
            
            # Log telemetry
            self._log_telemetry("scan_incremental", time.time() - start_time, 
                              len(modified_files), results.total_matches, detection_levels_used)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Incremental scan failed: {e}")
            self._log_telemetry("scan_incremental_error", time.time() - start_time, 
                              0, 0, detection_levels_used)
            raise DetectionError(f"Incremental scan failed: {e}")
    
    async def scan_directory_async(self, directory_path: str, max_files: Optional[int] = None) -> AsyncIterator[FileResult]:
        """Async streaming scan that yields results as they're found."""
        start_time = time.time()
        
        try:
            path = Path(directory_path)
            if not path.exists():
                raise DetectionError(f"Path does not exist: {directory_path}")
            
            # Stream file discovery and scanning
            async for file_path in self._discover_files_async(path, max_files):
                try:
                    file_result = await self._scan_file_async(file_path)
                    yield file_result
                except Exception as e:
                    self.logger.warning(f"Failed to scan {file_path}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Async scan failed: {e}")
            raise DetectionError(f"Async scan failed: {e}")
    
    def scan_file(self, file_path: str) -> DetectionResult:
        """Scan a single file through the complete detection pipeline.

        Returns a DetectionResult containing the file scan results.
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise DetectionError(f"File does not exist: {file_path}")
            
            self.logger.debug(f"Scanning file: {file_path}")
            
            # Read file content with memory mapping for large files
            content = self.file_handler.read_file(file_path)
            if content is None:
                raise DetectionError(f"Failed to read file: {file_path}")
            
            # Detect language
            language = self._detect_language(file_path)
            
            # Create file result
            file_result = FileResult(
                file_path=file_path,
                file_size=file_path.stat().st_size,
                language=language,
                total_lines=len(content.splitlines()),
                scan_time=0.0
            )
            
            # Multi-level detection pipeline with unified interfaces
            start_time = time.time()
            stage_times = {}
            stage_counts = {}
            stage_metadata = {}
            pipeline_stages = []
            
            # Track pipeline execution metadata
            pipeline_metadata = {
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'language': language,
                'total_lines': len(content.splitlines()),
                'stages_executed': [],
                'stages_failed': [],
                'stages_skipped': [],
                'confidence_adjustments': {},
                'fallback_used': False
            }
            
            # STAGE 1: Regex Detection (always available)
            stage_start = time.time()
            stage_name = "regex"
            pipeline_stages.append(stage_name)
            
            try:
                regex_matches = self.regex_engine.scan_file(file_path, content, language)
                # Convert to unified DetectionMatch format
                unified_regex_matches = self._convert_to_unified_matches(
                    regex_matches, file_path, content, "regex", language
                )
                for match in unified_regex_matches:
                    file_result.add_match(match)
                
                stage_times[stage_name] = time.time() - stage_start
                stage_counts[stage_name] = len(unified_regex_matches)
                stage_metadata[stage_name] = {
                    'matches_found': len(unified_regex_matches),
                    'execution_time': stage_times[stage_name],
                    'status': 'success',
                    'engine': 'regex_engine'
                }
                pipeline_metadata['stages_executed'].append(stage_name)
                
                self.logger.debug(f"STAGE 1 - Regex: Found {len(unified_regex_matches)} matches in {stage_times[stage_name]:.3f}s")
            except Exception as e:
                self.logger.warning(f"STAGE 1 - Regex failed for {file_path}: {e}")
                file_result.add_warning(f"Regex detection failed: {e}")
                stage_times[stage_name] = 0.0
                stage_counts[stage_name] = 0
                stage_metadata[stage_name] = {
                    'matches_found': 0,
                    'execution_time': 0.0,
                    'status': 'failed',
                    'error': str(e),
                    'engine': 'regex_engine'
                }
                pipeline_metadata['stages_failed'].append(stage_name)
            
            # STAGE 2: AST Analysis (Premium+)
            ast_matches = []
            stage_name = "ast"
            pipeline_stages.append(stage_name)
            
            if self.config.is_feature_enabled("ast_analysis"):
                try:
                    stage_start = time.time()
                    ast_matches = self.ast_analyzer.scan_file(str(file_path))
                    # Convert to unified format
                    unified_ast_matches = self._convert_to_unified_matches(
                        ast_matches, file_path, content, "ast", language
                    )
                    for match in unified_ast_matches:
                        file_result.add_match(match)
                    
                    stage_times[stage_name] = time.time() - stage_start
                    stage_counts[stage_name] = len(unified_ast_matches)
                    stage_metadata[stage_name] = {
                        'matches_found': len(unified_ast_matches),
                        'execution_time': stage_times[stage_name],
                        'status': 'success',
                        'engine': 'ast_analyzer'
                    }
                    pipeline_metadata['stages_executed'].append(stage_name)
                    
                    self.logger.debug(f"STAGE 2 - AST Analysis: Found {len(unified_ast_matches)} matches in {stage_times[stage_name]:.3f}s")
                except Exception as e:
                    self.logger.warning(f"STAGE 2 - AST Analysis failed for {file_path}: {e}")
                    file_result.add_warning(f"AST analysis failed: {e}")
                    stage_times[stage_name] = 0.0
                    stage_counts[stage_name] = 0
                    stage_metadata[stage_name] = {
                        'matches_found': 0,
                        'execution_time': 0.0,
                        'status': 'failed',
                        'error': str(e),
                        'engine': 'ast_analyzer'
                    }
                    pipeline_metadata['stages_failed'].append(stage_name)
            else:
                stage_times[stage_name] = 0.0
                stage_counts[stage_name] = 0
                stage_metadata[stage_name] = {
                    'matches_found': 0,
                    'execution_time': 0.0,
                    'status': 'skipped',
                    'reason': 'feature_disabled',
                    'engine': 'ast_analyzer'
                }
                pipeline_metadata['stages_skipped'].append(stage_name)
            
            # STAGE 3: Context Analysis (Premium+)
            stage_name = "context"
            pipeline_stages.append(stage_name)
            
            if self.context_analyzer and getattr(self.config, 'enable_context_analysis', True):
                try:
                    stage_start = time.time()
                    
                    # Detect test context for the file
                    test_context_info = self._detect_test_context(file_path, content)
                    
                    # Apply context analysis to all matches found so far
                    all_matches = file_result.matches
                    confidence_adjustments = {}
                    
                    for match in all_matches:
                        # Enrich match with context information
                        context_info = self._analyze_match_context(match, content, file_path, language)
                        match.context_info = context_info
                        match.confidence_score = self.context_analyzer.calculate_context_confidence(context_info)
                        match.legitimate_usage_flag = self.context_analyzer.is_legitimate_usage(context_info)
                        
                        # Add test context metadata
                        match.metadata.update(test_context_info)
                        
                        # Apply confidence adjustments based on context
                        confidence_multiplier = 1.0
                        
                        # Reduce confidence for test context
                        if test_context_info.get('in_test_context', False):
                            confidence_multiplier *= 0.5
                            self.logger.debug(f"Reduced confidence for test context in {file_path}")
                        
                        # Reduce confidence for framework-safe patterns
                        if test_context_info.get('framework_safe', False):
                            confidence_multiplier *= 0.3
                            self.logger.debug(f"Reduced confidence for framework-safe pattern in {file_path}")
                        
                        # Reduce confidence for legitimate usage
                        if match.legitimate_usage_flag:
                            confidence_multiplier *= 0.3
                            self.logger.debug(f"Reduced confidence for legitimate usage in {file_path}")
                        
                        # Apply confidence adjustment
                        original_confidence = match.confidence
                        match.confidence *= confidence_multiplier
                        
                        # Track confidence adjustments
                        confidence_adjustments[match.rule_id] = {
                            'original': original_confidence,
                            'adjusted': match.confidence,
                            'multiplier': confidence_multiplier,
                            'reasons': []
                        }
                        
                        if test_context_info.get('in_test_context', False):
                            confidence_adjustments[match.rule_id]['reasons'].append('test_context')
                        if test_context_info.get('framework_safe', False):
                            confidence_adjustments[match.rule_id]['reasons'].append('framework_safe')
                        if match.legitimate_usage_flag:
                            confidence_adjustments[match.rule_id]['reasons'].append('legitimate_usage')
                        
                        # Log significant confidence reductions
                        if confidence_multiplier < 0.8:
                            self.logger.debug(f"Confidence adjusted: {original_confidence:.2f} -> {match.confidence:.2f} (x{confidence_multiplier:.2f}) in {file_path}")
                    
                    stage_times[stage_name] = time.time() - stage_start
                    stage_counts[stage_name] = len(all_matches)
                    stage_metadata[stage_name] = {
                        'matches_processed': len(all_matches),
                        'execution_time': stage_times[stage_name],
                        'status': 'success',
                        'engine': 'context_analyzer',
                        'confidence_adjustments': confidence_adjustments,
                        'test_context_detected': test_context_info.get('in_test_context', False),
                        'framework_safe_detected': test_context_info.get('framework_safe', False)
                    }
                    pipeline_metadata['stages_executed'].append(stage_name)
                    pipeline_metadata['confidence_adjustments'].update(confidence_adjustments)
                    
                    self.logger.debug(f"STAGE 3 - Context Analysis: Processed {len(all_matches)} matches in {stage_times[stage_name]:.3f}s")
                except Exception as e:
                    self.logger.warning(f"Context Analysis failed for {file_path}: {e}")
                    file_result.add_warning(f"Context analysis failed: {e}")
                    stage_times[stage_name] = 0.0
                    stage_counts[stage_name] = 0
                    stage_metadata[stage_name] = {
                        'matches_processed': 0,
                        'execution_time': 0.0,
                        'status': 'failed',
                        'error': str(e),
                        'engine': 'context_analyzer'
                    }
                    pipeline_metadata['stages_failed'].append(stage_name)
            else:
                stage_times[stage_name] = 0.0
                stage_counts[stage_name] = 0
                stage_metadata[stage_name] = {
                    'matches_processed': 0,
                    'execution_time': 0.0,
                    'status': 'skipped',
                    'reason': 'feature_disabled',
                    'engine': 'context_analyzer'
                }
                pipeline_metadata['stages_skipped'].append(stage_name)
            
            # STAGE 4: Dataflow Analysis (Enterprise)
            stage_name = "dataflow"
            pipeline_stages.append(stage_name)
            
            if self.dataflow_analyzer and self.config.is_feature_enabled("dataflow_analysis"):
                try:
                    stage_start = time.time()
                    
                    # Check file size for dataflow analysis
                    file_size_mb = len(content.encode('utf-8')) / 1024 / 1024
                    if file_size_mb > 50:  # Skip very large files
                        self.logger.debug(f"Skipping dataflow analysis for large file: {file_path} ({file_size_mb:.1f}MB)")
                        stage_times[stage_name] = 0.0
                        stage_counts[stage_name] = 0
                        stage_metadata[stage_name] = {
                            'matches_found': 0,
                            'execution_time': 0.0,
                            'status': 'skipped',
                            'reason': 'file_too_large',
                            'file_size_mb': file_size_mb,
                            'engine': 'dataflow_analyzer'
                        }
                        pipeline_metadata['stages_skipped'].append(stage_name)
                    else:
                        try:
                            dataflow_matches = self.dataflow_analyzer.scan_file(str(file_path))
                            # Convert to unified format
                            unified_dataflow_matches = self._convert_to_unified_matches(
                                dataflow_matches, file_path, content, "dataflow", language
                            )
                            for match in unified_dataflow_matches:
                                file_result.add_match(match)
                            
                            stage_times[stage_name] = time.time() - stage_start
                            stage_counts[stage_name] = len(unified_dataflow_matches)
                            stage_metadata[stage_name] = {
                                'matches_found': len(unified_dataflow_matches),
                                'execution_time': stage_times[stage_name],
                                'status': 'success',
                                'engine': 'dataflow_analyzer',
                                'file_size_mb': file_size_mb
                            }
                            pipeline_metadata['stages_executed'].append(stage_name)
                            
                            self.logger.debug(f"STAGE 4 - Dataflow: Found {len(unified_dataflow_matches)} matches in {stage_times[stage_name]:.3f}s")
                            
                        except Exception as dataflow_error:
                            # Check if this is a timeout error
                            if "timeout" in str(dataflow_error).lower() or "timed out" in str(dataflow_error).lower():
                                self.logger.warning(f"STAGE 4 - Dataflow timeout for {file_path}, falling back to AST+Context analysis")
                                
                                # Fallback to AST+Context analysis
                                fallback_matches = self._perform_fallback_analysis(file_path, content, language)
                                for match in fallback_matches:
                                    file_result.add_match(match)
                                
                                stage_times[stage_name] = time.time() - stage_start
                                stage_counts[stage_name] = len(fallback_matches)
                                stage_metadata[stage_name] = {
                                    'matches_found': len(fallback_matches),
                                    'execution_time': stage_times[stage_name],
                                    'status': 'fallback',
                                    'fallback_reason': 'timeout',
                                    'original_error': str(dataflow_error),
                                    'engine': 'dataflow_analyzer',
                                    'fallback_engine': 'ast_fallback',
                                    'file_size_mb': file_size_mb
                                }
                                pipeline_metadata['stages_executed'].append(stage_name)
                                pipeline_metadata['fallback_used'] = True
                                
                                self.logger.debug(f"STAGE 4 - Dataflow Fallback: Found {len(fallback_matches)} matches in {stage_times[stage_name]:.3f}s")
                            else:
                                raise dataflow_error
                                
                except Exception as e:
                    self.logger.warning(f"STAGE 4 - Dataflow Analysis failed for {file_path}: {e}")
                    file_result.add_warning(f"Dataflow analysis failed: {e}")
                    stage_times[stage_name] = 0.0
                    stage_counts[stage_name] = 0
                    stage_metadata[stage_name] = {
                        'matches_found': 0,
                        'execution_time': 0.0,
                        'status': 'failed',
                        'error': str(e),
                        'engine': 'dataflow_analyzer'
                    }
                    pipeline_metadata['stages_failed'].append(stage_name)
            else:
                stage_times[stage_name] = 0.0
                stage_counts[stage_name] = 0
                stage_metadata[stage_name] = {
                    'matches_found': 0,
                    'execution_time': 0.0,
                    'status': 'skipped',
                    'reason': 'feature_disabled',
                    'engine': 'dataflow_analyzer'
                }
                pipeline_metadata['stages_skipped'].append(stage_name)
            
            # STAGE 5: CFG Analysis (Premium+)
            cfg_matches = []
            if (self.cfg_analyzer and self.config.is_feature_enabled("cfg_analysis") and
                self.config.license.tier.value in ['premium', 'enterprise']):
                try:
                    stage_start = time.time()
                    
                    # Get all matches from previous stages for CFG analysis
                    previous_matches = file_result.matches
                    
                    # Run CFG analysis on files with high-confidence PII detections
                    cfg_matches = self.cfg_analyzer.scan_file(str(file_path), previous_matches)
                    
                    # Convert to unified format and add to results
                    unified_cfg_matches = self._convert_to_unified_matches(
                        cfg_matches, file_path, content, "cfg", language
                    )
                    for match in unified_cfg_matches:
                        file_result.add_match(match)
                    
                    stage_times['cfg_analysis'] = time.time() - stage_start
                    stage_counts['cfg_analysis'] = len(unified_cfg_matches)
                    self.logger.debug(f"STAGE 5 - CFG Analysis: Found {len(unified_cfg_matches)} matches in {stage_times['cfg_analysis']:.3f}s")
                except Exception as e:
                    self.logger.warning(f"STAGE 5 - CFG Analysis failed for {file_path}: {e}")
                    file_result.add_warning(f"CFG analysis failed: {e}")
                    stage_times['cfg_analysis'] = 0.0
                    stage_counts['cfg_analysis'] = 0
            
            # STAGE 6: ML Filtering (Enterprise)
            if (self.ml_filter and self.config.is_feature_enabled("ml_filtering") and 
                self._check_ml_circuit_breaker()):
                try:
                    # Check rate limit for freemium users
                    if self.config.license.tier == LicenseTier.STARTER:
                        can_use, remaining = check_feature_usage("ml_filtering")
                        if not can_use:
                            self.logger.warning(f"ML Filtering rate limit exceeded. Remaining: {remaining}")
                            file_result.add_warning("ML Filtering: Monthly usage limit exceeded (25 scans/month)")
                            stage_times['ml_filter'] = 0.0
                            stage_counts['ml_filter'] = len(file_result.matches)
                        else:
                            # Mark feature as used and proceed
                            use_feature("ml_filtering")
                            self.logger.debug(f"ML Filtering: {remaining} uses remaining this month")
                            
                            # Perform ML filtering
                            stage_start = time.time()
                            
                            # Pre-filter obvious false positives before ML processing
                            pre_filtered_matches = self._pre_filter_false_positives(file_result.matches, content)
                            
                            # Apply ML filtering - FINAL OUTPUT
                            filtered_matches = self.ml_filter.filter_matches(
                                pre_filtered_matches, content, file_path=str(file_path)
                            )
                            file_result.matches = filtered_matches
                            stage_times['ml_filter'] = time.time() - stage_start
                            stage_counts['ml_filter'] = len(filtered_matches)
                            self._record_ml_success()
                            
                            self.logger.info(f"STAGE 5 - ML Filtering: {len(pre_filtered_matches)} → {len(filtered_matches)} matches in {stage_times['ml_filter']:.3f}s")
                    else:
                        # Premium/Enterprise users have unlimited usage
                        stage_start = time.time()
                        
                        # Pre-filter obvious false positives before ML processing
                        pre_filtered_matches = self._pre_filter_false_positives(file_result.matches, content)
                        
                        # Apply ML filtering - FINAL OUTPUT
                        filtered_matches = self.ml_filter.filter_matches(
                            pre_filtered_matches, content, file_path=str(file_path)
                        )
                        file_result.matches = filtered_matches
                        stage_times['ml_filter'] = time.time() - stage_start
                        stage_counts['ml_filter'] = len(filtered_matches)
                        self._record_ml_success()
                        
                        self.logger.info(f"STAGE 5 - ML Filtering: {len(pre_filtered_matches)} → {len(filtered_matches)} matches in {stage_times['ml_filter']:.3f}s")
                        
                except RateLimitExceededError as e:
                    self.logger.warning(f"ML Filtering rate limit exceeded: {e}")
                    file_result.add_warning(f"ML Filtering: {e}")
                    stage_times['ml_filter'] = 0.0
                    stage_counts['ml_filter'] = len(file_result.matches)
                except Exception as e:
                    self.logger.warning(f"STAGE 5 - ML Filtering failed for {file_path}: {e}")
                    file_result.add_warning(f"ML filtering failed: {e}")
                    self._record_ml_failure()
                    stage_times['ml_filter'] = 0.0
                    stage_counts['ml_filter'] = len(file_result.matches)
            
            # STAGE 7: GDPR Compliance Analysis (Premium+)
            if (self.gdpr_analyzer and self.config.is_feature_enabled("gdpr_compliance") and
                self.config.license.tier.value in ['premium', 'enterprise']):
                try:
                    stage_start = time.time()
                    
                    # Create a mock DetectionResult for GDPR analysis
                    mock_detection_result = type('MockDetectionResult', (), {
                        'file_results': [file_result]
                    })()
                    
                    # Run GDPR compliance analysis
                    gdpr_issues = self.gdpr_analyzer.analyze_project(
                        project_path=file_path.parent,
                        detection_result=mock_detection_result,
                        options=type('MockOptions', (), {
                            'include_security_checks': True,
                            'include_dsar_checks': True,
                            'include_deletion_checks': True,
                            'include_transfer_checks': True
                        })()
                    )
                    
                    # Add GDPR issues to metadata for reporting
                    if gdpr_issues:
                        file_result.metadata['gdpr_compliance_issues'] = [
                            {
                                'id': issue.id,
                                'severity': issue.severity.value,
                                'article': issue.article_ref.value,
                                'category': issue.category.value,
                                'description': issue.description,
                                'remediation': issue.remediation_suggestion
                            } for issue in gdpr_issues
                        ]
                        file_result.metadata['gdpr_compliance_score'] = self.gdpr_analyzer._calculate_compliance_score(gdpr_issues)
                    
                    stage_times['gdpr_compliance'] = time.time() - stage_start
                    stage_counts['gdpr_compliance'] = len(gdpr_issues) if 'gdpr_issues' in locals() else 0
                    self.logger.info(f"STAGE 6 - GDPR Compliance: Found {stage_counts['gdpr_compliance']} issues in {stage_times['gdpr_compliance']:.3f}s")
                except Exception as e:
                    self.logger.warning(f"STAGE 6 - GDPR Compliance failed for {file_path}: {e}")
                    file_result.add_warning(f"GDPR compliance analysis failed: {e}")
                    stage_times['gdpr_compliance'] = 0.0
                    stage_counts['gdpr_compliance'] = 0
            
            # Update scan time
            file_result.scan_time = time.time() - start_time
            
            # Apply final confidence threshold filtering (Enterprise-grade)
            pre_filter_count = len(file_result.matches)
            file_result.matches = self._apply_confidence_threshold_filter(file_result.matches)
            post_filter_count = len(file_result.matches)
            
            # Debug logging for filtering verification
            self.logger.info(f"Final confidence filtering: {pre_filter_count} → {post_filter_count} matches")
            if pre_filter_count > post_filter_count:
                self.logger.info(f"Filtered out {pre_filter_count - post_filter_count} low-confidence matches")
            
            # Deduplicate matches before finalizing
            file_result.matches = self._deduplicate_matches(file_result.matches)
            
            # Add metadata with stage timings and counts
            file_result.metadata.update({
                'detection_levels_used': self._get_active_detection_levels(),
                'scan_timestamp': datetime.utcnow().isoformat(),
                'license_tier': self.config.license.tier.value,
                'stage_times': stage_times,
                'stage_counts': stage_counts,
                'stage_metadata': stage_metadata,
                'pipeline_stages': pipeline_stages,
                'pipeline_metadata': pipeline_metadata,
                'sequential_execution': True,
                'data_flow_enabled': True,
                'filtering_stats': {
                    'matches_before_confidence_filter': pre_filter_count,
                    'matches_after_confidence_filter': post_filter_count,
                    'confidence_threshold_applied': self.config.tier_specific_thresholds.get(
                        self.config.license.tier.value, 0.75
                    ),
                    'false_positive_reduction_rate': (
                        (pre_filter_count - post_filter_count) / max(pre_filter_count, 1) * 100
                    ) if pre_filter_count > 0 else 0.0
                }
            })
            
            # Create DetectionResult containing the file result
            import uuid
            
            detection_result = DetectionResult(
                scan_id=str(uuid.uuid4()),
                scan_duration=file_result.scan_time,
                license_tier=self.config.license.tier.value,
                scan_path=str(file_path),
                files_scanned=1,
                files_with_matches=1 if file_result.match_count > 0 else 0,
                total_matches=file_result.match_count,
                total_scan_time=file_result.scan_time,
                average_file_time=file_result.scan_time,
                memory_peak_mb=0.0,
                false_positive_rate=0.0,
                confidence_average=0.0
            )
            
            # Add the file result to the detection result
            detection_result.add_file_result(file_result)
            
            # Calculate metrics
            detection_result.calculate_metrics()
            
            return detection_result
            
        except Exception as e:
            self.logger.error(f"File scan failed: {file_path}: {e}")
            raise DetectionError(f"File scan failed: {file_path}: {e}")
    
    def _scan_file_internal(self, file_path: Path) -> FileResult:
        """Internal method to scan a file and return FileResult (for caching)."""
        try:
            if not file_path.exists():
                raise DetectionError(f"File does not exist: {file_path}")
            
            self.logger.debug(f"Internal scanning file: {file_path}")
            
            # Read file content with memory mapping for large files
            content = self.file_handler.read_file(file_path)
            if content is None:
                raise DetectionError(f"Failed to read file: {file_path}")
            
            # Detect language
            language = self._detect_language(file_path)
            
            # Create file result
            file_result = FileResult(
                file_path=file_path,
                file_size=file_path.stat().st_size,
                language=language,
                total_lines=len(content.splitlines()),
                scan_time=0.0
            )
            
            # Multi-level detection pipeline with unified interfaces
            start_time = time.time()
            stage_times = {}
            stage_counts = {}
            stage_metadata = {}
            pipeline_stages = []
            
            # Track pipeline execution metadata
            pipeline_metadata = {
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'language': language,
                'total_lines': len(content.splitlines()),
                'stages_executed': [],
                'stages_failed': [],
                'stages_skipped': [],
                'confidence_adjustments': {},
                'fallback_used': False
            }
            
            # STAGE 1: Regex Detection (always available)
            stage_start = time.time()
            stage_name = "regex"
            pipeline_stages.append(stage_name)
            
            try:
                regex_matches = self.regex_engine.scan_file(file_path, content, language)
                # Convert to unified DetectionMatch format
                unified_regex_matches = self._convert_to_unified_matches(
                    regex_matches, file_path, content, "regex", language
                )
                for match in unified_regex_matches:
                    file_result.add_match(match)
                
                stage_times[stage_name] = time.time() - stage_start
                stage_counts[stage_name] = len(unified_regex_matches)
                stage_metadata[stage_name] = {
                    'matches_found': len(unified_regex_matches),
                    'execution_time': stage_times[stage_name],
                    'status': 'success',
                    'engine': 'regex_engine'
                }
                pipeline_metadata['stages_executed'].append(stage_name)
                
                self.logger.debug(f"STAGE 1 - Regex: Found {len(unified_regex_matches)} matches in {stage_times[stage_name]:.3f}s")
            except Exception as e:
                self.logger.warning(f"STAGE 1 - Regex failed for {file_path}: {e}")
                file_result.add_warning(f"Regex detection failed: {e}")
                stage_times[stage_name] = 0.0
                stage_counts[stage_name] = 0
                stage_metadata[stage_name] = {
                    'matches_found': 0,
                    'execution_time': 0.0,
                    'status': 'failed',
                    'error': str(e),
                    'engine': 'regex_engine'
                }
                pipeline_metadata['stages_failed'].append(stage_name)
            
            # STAGE 2: AST Analysis (Premium+)
            ast_matches = []
            stage_name = "ast"
            pipeline_stages.append(stage_name)
            
            if self.config.is_feature_enabled("ast_analysis"):
                try:
                    stage_start = time.time()
                    ast_matches = self.ast_analyzer.scan_file(str(file_path))
                    # Convert to unified format
                    unified_ast_matches = self._convert_to_unified_matches(
                        ast_matches, file_path, content, "ast", language
                    )
                    for match in unified_ast_matches:
                        file_result.add_match(match)
                    
                    stage_times[stage_name] = time.time() - stage_start
                    stage_counts[stage_name] = len(unified_ast_matches)
                    stage_metadata[stage_name] = {
                        'matches_found': len(unified_ast_matches),
                        'execution_time': stage_times[stage_name],
                        'status': 'success',
                        'engine': 'ast_analyzer'
                    }
                    pipeline_metadata['stages_executed'].append(stage_name)
                    
                    self.logger.debug(f"STAGE 2 - AST Analysis: Found {len(unified_ast_matches)} matches in {stage_times[stage_name]:.3f}s")
                except Exception as e:
                    self.logger.warning(f"STAGE 2 - AST Analysis failed for {file_path}: {e}")
                    file_result.add_warning(f"AST analysis failed: {e}")
                    stage_times[stage_name] = 0.0
                    stage_counts[stage_name] = 0
                    stage_metadata[stage_name] = {
                        'matches_found': 0,
                        'execution_time': 0.0,
                        'status': 'failed',
                        'error': str(e),
                        'engine': 'ast_analyzer'
                    }
                    pipeline_metadata['stages_failed'].append(stage_name)
            else:
                stage_times[stage_name] = 0.0
                stage_counts[stage_name] = 0
                stage_metadata[stage_name] = {
                    'matches_found': 0,
                    'execution_time': 0.0,
                    'status': 'skipped',
                    'reason': 'feature_disabled',
                    'engine': 'ast_analyzer'
                }
                pipeline_metadata['stages_skipped'].append(stage_name)
            
            # STAGE 3: Context Analysis (Premium+)
            stage_name = "context"
            pipeline_stages.append(stage_name)
            
            if self.context_analyzer and getattr(self.config, 'enable_context_analysis', True):
                try:
                    stage_start = time.time()
                    
                    # Detect test context for the file
                    test_context_info = self._detect_test_context(file_path, content)
                    
                    # Apply context analysis to all matches found so far
                    all_matches = file_result.matches
                    confidence_adjustments = {}
                    
                    for match in all_matches:
                        # Enrich match with context information
                        context_info = self._analyze_match_context(match, content, file_path, language)
                        match.context_info = context_info
                        match.confidence_score = self.context_analyzer.calculate_context_confidence(context_info)
                        match.legitimate_usage_flag = self.context_analyzer.is_legitimate_usage(context_info)
                        
                        # Add test context metadata
                        match.metadata.update(test_context_info)
                        
                        # Apply confidence adjustments based on context
                        confidence_multiplier = 1.0
                        
                        # Reduce confidence for test context
                        if test_context_info.get('in_test_context', False):
                            confidence_multiplier *= 0.5
                            self.logger.debug(f"Reduced confidence for test context in {file_path}")
                        
                        # Reduce confidence for framework-safe patterns
                        if test_context_info.get('framework_safe', False):
                            confidence_multiplier *= 0.3
                            self.logger.debug(f"Reduced confidence for framework-safe pattern in {file_path}")
                        
                        # Reduce confidence for legitimate usage
                        if match.legitimate_usage_flag:
                            confidence_multiplier *= 0.3
                            self.logger.debug(f"Reduced confidence for legitimate usage in {file_path}")
                        
                        # Apply confidence adjustment
                        original_confidence = match.confidence
                        match.confidence *= confidence_multiplier
                        
                        # Track confidence adjustments
                        confidence_adjustments[match.rule_id] = {
                            'original': original_confidence,
                            'adjusted': match.confidence,
                            'multiplier': confidence_multiplier,
                            'reasons': []
                        }
                        
                        if test_context_info.get('in_test_context', False):
                            confidence_adjustments[match.rule_id]['reasons'].append('test_context')
                        if test_context_info.get('framework_safe', False):
                            confidence_adjustments[match.rule_id]['reasons'].append('framework_safe')
                        if match.legitimate_usage_flag:
                            confidence_adjustments[match.rule_id]['reasons'].append('legitimate_usage')
                        
                        # Log significant confidence reductions
                        if confidence_multiplier < 0.8:
                            self.logger.debug(f"Confidence adjusted: {original_confidence:.2f} -> {match.confidence:.2f} (x{confidence_multiplier:.2f}) in {file_path}")
                    
                    stage_times[stage_name] = time.time() - stage_start
                    stage_counts[stage_name] = len(all_matches)
                    stage_metadata[stage_name] = {
                        'matches_processed': len(all_matches),
                        'execution_time': stage_times[stage_name],
                        'status': 'success',
                        'engine': 'context_analyzer',
                        'confidence_adjustments': confidence_adjustments,
                        'test_context_detected': test_context_info.get('in_test_context', False),
                        'framework_safe_detected': test_context_info.get('framework_safe', False)
                    }
                    pipeline_metadata['stages_executed'].append(stage_name)
                    pipeline_metadata['confidence_adjustments'].update(confidence_adjustments)
                    
                    self.logger.debug(f"STAGE 3 - Context Analysis: Processed {len(all_matches)} matches in {stage_times[stage_name]:.3f}s")
                except Exception as e:
                    self.logger.warning(f"Context Analysis failed for {file_path}: {e}")
                    file_result.add_warning(f"Context analysis failed: {e}")
                    stage_times[stage_name] = 0.0
                    stage_counts[stage_name] = 0
                    stage_metadata[stage_name] = {
                        'matches_processed': 0,
                        'execution_time': 0.0,
                        'status': 'failed',
                        'error': str(e),
                        'engine': 'context_analyzer'
                    }
                    pipeline_metadata['stages_failed'].append(stage_name)
            else:
                stage_times[stage_name] = 0.0
                stage_counts[stage_name] = 0
                stage_metadata[stage_name] = {
                    'matches_processed': 0,
                    'execution_time': 0.0,
                    'status': 'skipped',
                    'reason': 'feature_disabled',
                    'engine': 'context_analyzer'
                }
                pipeline_metadata['stages_skipped'].append(stage_name)
            
            # STAGE 4: Dataflow Analysis (Enterprise)
            stage_name = "dataflow"
            pipeline_stages.append(stage_name)
            
            if self.dataflow_analyzer and self.config.is_feature_enabled("dataflow_analysis"):
                try:
                    stage_start = time.time()
                    
                    # Check file size for dataflow analysis
                    file_size_mb = len(content.encode('utf-8')) / 1024 / 1024
                    if file_size_mb > 50:  # Skip very large files
                        self.logger.debug(f"Skipping dataflow analysis for large file: {file_path} ({file_size_mb:.1f}MB)")
                        stage_times[stage_name] = 0.0
                        stage_counts[stage_name] = 0
                        stage_metadata[stage_name] = {
                            'matches_found': 0,
                            'execution_time': 0.0,
                            'status': 'skipped',
                            'reason': 'file_too_large',
                            'file_size_mb': file_size_mb,
                            'engine': 'dataflow_analyzer'
                        }
                        pipeline_metadata['stages_skipped'].append(stage_name)
                    else:
                        try:
                            dataflow_matches = self.dataflow_analyzer.scan_file(str(file_path))
                            # Convert to unified format
                            unified_dataflow_matches = self._convert_to_unified_matches(
                                dataflow_matches, file_path, content, "dataflow", language
                            )
                            for match in unified_dataflow_matches:
                                file_result.add_match(match)
                            
                            stage_times[stage_name] = time.time() - stage_start
                            stage_counts[stage_name] = len(unified_dataflow_matches)
                            stage_metadata[stage_name] = {
                                'matches_found': len(unified_dataflow_matches),
                                'execution_time': stage_times[stage_name],
                                'status': 'success',
                                'engine': 'dataflow_analyzer',
                                'file_size_mb': file_size_mb
                            }
                            pipeline_metadata['stages_executed'].append(stage_name)
                            
                            self.logger.debug(f"STAGE 4 - Dataflow: Found {len(unified_dataflow_matches)} matches in {stage_times[stage_name]:.3f}s")
                            
                        except Exception as dataflow_error:
                            # Check if this is a timeout error
                            if "timeout" in str(dataflow_error).lower() or "timed out" in str(dataflow_error).lower():
                                self.logger.warning(f"STAGE 4 - Dataflow timeout for {file_path}, falling back to AST+Context analysis")
                                
                                # Fallback to AST+Context analysis
                                fallback_matches = self._perform_fallback_analysis(file_path, content, language)
                                for match in fallback_matches:
                                    file_result.add_match(match)
                                
                                stage_times[stage_name] = time.time() - stage_start
                                stage_counts[stage_name] = len(fallback_matches)
                                stage_metadata[stage_name] = {
                                    'matches_found': len(fallback_matches),
                                    'execution_time': stage_times[stage_name],
                                    'status': 'fallback',
                                    'fallback_reason': 'timeout',
                                    'original_error': str(dataflow_error),
                                    'engine': 'dataflow_analyzer',
                                    'fallback_engine': 'ast_fallback',
                                    'file_size_mb': file_size_mb
                                }
                                pipeline_metadata['stages_executed'].append(stage_name)
                                pipeline_metadata['fallback_used'] = True
                                
                                self.logger.debug(f"STAGE 4 - Dataflow Fallback: Found {len(fallback_matches)} matches in {stage_times[stage_name]:.3f}s")
                            else:
                                raise dataflow_error
                                
                except Exception as e:
                    self.logger.warning(f"STAGE 4 - Dataflow Analysis failed for {file_path}: {e}")
                    file_result.add_warning(f"Dataflow analysis failed: {e}")
                    stage_times[stage_name] = 0.0
                    stage_counts[stage_name] = 0
                    stage_metadata[stage_name] = {
                        'matches_found': 0,
                        'execution_time': 0.0,
                        'status': 'failed',
                        'error': str(e),
                        'engine': 'dataflow_analyzer'
                    }
                    pipeline_metadata['stages_failed'].append(stage_name)
            else:
                stage_times[stage_name] = 0.0
                stage_counts[stage_name] = 0
                stage_metadata[stage_name] = {
                    'matches_found': 0,
                    'execution_time': 0.0,
                    'status': 'skipped',
                    'reason': 'feature_disabled',
                    'engine': 'dataflow_analyzer'
                }
                pipeline_metadata['stages_skipped'].append(stage_name)
            
            # STAGE 5: CFG Analysis (Premium+)
            cfg_matches = []
            if self.cfg_analyzer and self.config.is_feature_enabled("cfg_analysis"):
                try:
                    stage_start = time.time()
                    # Get previous matches for CFG analysis
                    previous_matches = file_result.matches
                    
                    # Run CFG analysis
                    cfg_matches = self.cfg_analyzer.scan_file(str(file_path), previous_matches)
                    
                    # Convert to unified format
                    unified_cfg_matches = self._convert_to_unified_matches(
                        cfg_matches, file_path, content, "cfg", language
                    )
                    for match in unified_cfg_matches:
                        file_result.add_match(match)
                    stage_times['cfg'] = time.time() - stage_start
                    stage_counts['cfg'] = len(unified_cfg_matches)
                    self.logger.debug(f"STAGE 5 - CFG Analysis: Found {len(unified_cfg_matches)} matches in {stage_times['cfg']:.3f}s")
                except Exception as e:
                    self.logger.warning(f"STAGE 5 - CFG Analysis failed for {file_path}: {e}")
                    file_result.add_warning(f"CFG analysis failed: {e}")
                    stage_times['cfg'] = 0.0
                    stage_counts['cfg'] = 0
            
            # STAGE 6: ML Filtering (Enterprise)
            if self.ml_filter and self.config.is_feature_enabled("ml_filtering"):
                try:
                    stage_start = time.time()
                    # Pre-filter false positives
                    pre_filtered_matches = self._pre_filter_false_positives(file_result.matches, content)
                    
                    # Apply ML filtering
                    filtered_matches = self.ml_filter.filter_matches(
                        pre_filtered_matches, content, file_path=str(file_path)
                    )
                    
                    # Replace matches with filtered results
                    file_result.matches = filtered_matches
                    
                    stage_times['ml_filter'] = time.time() - stage_start
                    stage_counts['ml_filter'] = len(filtered_matches)
                    self.logger.debug(f"STAGE 6 - ML Filtering: Processed {len(filtered_matches)} matches in {stage_times['ml_filter']:.3f}s")
                except Exception as e:
                    self.logger.warning(f"STAGE 6 - ML Filtering failed for {file_path}: {e}")
                    file_result.add_warning(f"ML filtering failed: {e}")
                    stage_times['ml_filter'] = 0.0
                    stage_counts['ml_filter'] = 0
            
            # STAGE 7: GDPR Compliance (Premium+)
            if self.gdpr_analyzer and self.config.is_feature_enabled("gdpr_compliance"):
                try:
                    stage_start = time.time()
                    gdpr_matches = self.gdpr_analyzer.scan_file(str(file_path))
                    
                    # Convert to unified format
                    unified_gdpr_matches = self._convert_to_unified_matches(
                        gdpr_matches, file_path, content, "gdpr", language
                    )
                    for match in unified_gdpr_matches:
                        file_result.add_match(match)
                    stage_times['gdpr'] = time.time() - stage_start
                    stage_counts['gdpr'] = len(unified_gdpr_matches)
                    self.logger.debug(f"STAGE 7 - GDPR Compliance: Found {len(unified_gdpr_matches)} matches in {stage_times['gdpr']:.3f}s")
                except Exception as e:
                    self.logger.warning(f"STAGE 7 - GDPR Compliance failed for {file_path}: {e}")
                    file_result.add_warning(f"GDPR compliance failed: {e}")
                    stage_times['gdpr'] = 0.0
                    stage_counts['gdpr'] = 0
            
            # Update scan time
            file_result.scan_time = time.time() - start_time
            
            # Add metadata
            file_result.metadata.update({
                'stage_times': stage_times,
                'stage_counts': stage_counts,
                'scan_timestamp': datetime.utcnow().isoformat(),
                'license_tier': self.config.license.tier.value
            })
            
            return file_result
            
        except Exception as e:
            self.logger.error(f"Internal file scan failed: {file_path}: {e}")
            raise DetectionError(f"Internal file scan failed: {file_path}: {e}")
    
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

    def _convert_to_unified_matches(self, matches: List, file_path: Path, content: str, 
                                   engine: str, language: str) -> List[DetectionMatch]:
        """Convert engine-specific matches to unified DetectionMatch format."""
        unified_matches = []
        
        for match in matches:
            # Handle different match formats from various engines
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
                engine=engine,
                rule_id=match_dict.get('pattern_name', match_dict.get('rule_id', 'unknown')),
                severity=match_dict.get('severity', match_dict.get('risk_level', 'MEDIUM')),
                confidence=match_dict.get('confidence', match_dict.get('confidence_score', 0.8)),
                snippet=snippet,
                description=match_dict.get('description', f'{engine.upper()} detection'),
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
    
    # HELPER METHODS FOR SCANNING
    
    def _should_skip_directory(self, directory: Path) -> bool:
        """Early exit heuristics for low-risk directories."""
        skip_patterns = [
            '.git', '.svn', '.hg',  # Version control
            'node_modules', '__pycache__', '.venv', 'venv',  # Dependencies/cache
            'build', 'dist', 'target', 'bin', 'obj',  # Build artifacts
            '.idea', '.vscode',  # IDE files
            'logs', 'tmp', 'temp'  # Temporary files
        ]
        
        should_skip = any(pattern in directory.name.lower() for pattern in skip_patterns)
        if should_skip:
            self.logger.debug(f"Skipping directory {directory} due to skip pattern")
        return should_skip
    
    def _discover_files_streaming(self, directory: Path, max_files: Optional[int] = None) -> Iterator[Path]:
        """Stream file discovery via FileProcessor to minimize memory usage."""
        try:
            self.logger.debug(f"Starting file discovery in {directory}")
            file_count = 0
            for file_path in self.file_processor.discover_files(directory, max_files=max_files):
                if self._shutdown_event.is_set():
                    break
                file_count += 1
                self.logger.debug(f"Discovered file: {file_path}")
                yield file_path
            
            self.logger.info(f"File discovery complete: found {file_count} files in {directory}")
        except Exception as e:
            self.logger.error(f"File discovery failed: {e}")
            raise DetectionError(f"File discovery failed: {e}")
    
    async def _discover_files_async(self, directory: Path, max_files: Optional[int] = None) -> AsyncIterator[Path]:
        """Async file discovery for streaming scans."""
        file_count = 0
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and self._should_scan_file(file_path):
                yield file_path
                file_count += 1
                
                if max_files and file_count >= max_files:
                    break
                
                # Yield control to allow other coroutines to run
                await asyncio.sleep(0)
    
    async def _scan_file_async(self, file_path: Path) -> FileResult:
        """Async version of scan_file."""
        # Run the synchronous scan_file in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.scan_file, str(file_path))
    
    def _scan_files_parallel(self, files: List[Path], results: DetectionResult) -> None:
        """Scan multiple files using parallel processing with performance monitoring."""
        max_workers = min(self.config.performance.concurrent_workers, max(1, len(files)))

        def _scan(fpath: Path) -> FileResult:
            return self.scan_file(str(fpath))

        def _progress(processed: int, total: int, eta: float) -> None:
            # Progress logging disabled to avoid typewriter effect
            pass

        for fpath, res, err in self.file_processor.parallel_process(
            files,
            _scan,
            max_workers=max_workers,
            progress_cb=_progress
        ):
            if self._shutdown_event.is_set():
                break
            if err is None and isinstance(res, FileResult):
                results.add_file_result(res)
                # Check performance limits
                self._check_performance_limits()
                if self.streaming_enabled:
                    self.results_queue.put(res)
            else:
                error_result = FileResult(
                    file_path=fpath,
                    file_size=0,
                    language='unknown',
                    total_lines=0,
                    scan_time=0.0
                )
                error_result.add_error(str(err) if err else 'Unknown error')
                results.add_file_result(error_result)
                self.logger.error(f"Failed to scan {fpath}: {err}")
    
    def _find_modified_files_advanced(self, directory_path: str) -> List[Path]:
        """Advanced modified file detection using git, checksums, and timestamps."""
        directory = Path(directory_path)
        modified_files = []
        
        # Method 1: Git-based detection (if in git repo)
        if self._is_git_repository(directory):
            git_modified = self._get_git_modified_files(directory)
            modified_files.extend(git_modified)
        
        # Method 2: Checksum-based detection
        checksum_modified = self._get_checksum_modified_files(directory)
        modified_files.extend(checksum_modified)
        
        # Method 3: Timestamp-based detection
        if self.last_scan_time:
            timestamp_modified = self._get_timestamp_modified_files(directory, self.last_scan_time)
            modified_files.extend(timestamp_modified)
        
        # Remove duplicates and filter
        unique_files = list(set(modified_files))
        return [f for f in unique_files if self._should_scan_file(f)]
    
    def _is_git_repository(self, directory: Path) -> bool:
        """Check if directory is a git repository."""
        return (directory / '.git').exists()
    
    def _get_git_modified_files(self, directory: Path) -> List[Path]:
        """Get modified files from git."""
        try:
            # Get modified files from git
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                files = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        file_path = directory / line
                        if file_path.exists() and file_path.is_file():
                            files.append(file_path)
                return files
                
        except Exception as e:
            self.logger.debug(f"Git modified files detection failed: {e}")
        
        return []
    
    def _get_checksum_modified_files(self, directory: Path) -> List[Path]:
        """Get files with changed checksums."""
        modified_files = []
        for file_path in self.file_processor.discover_files(directory):
            file_path_str = str(file_path)
            current_checksum = self._calculate_file_checksum(file_path)
            if file_path_str in self.file_checksums:
                if self.file_checksums[file_path_str] != current_checksum:
                    modified_files.append(file_path)
            else:
                modified_files.append(file_path)
        return modified_files
    
    def _get_timestamp_modified_files(self, directory: Path, since: datetime) -> List[Path]:
        """Get files modified since timestamp."""
        modified_files = []
        since_timestamp = since.timestamp()
        for file_path in self.file_processor.discover_files(directory):
            try:
                if file_path.stat().st_mtime > since_timestamp:
                    modified_files.append(file_path)
            except OSError:
                continue
        
        return modified_files
    
    # CIRCUIT BREAKER AND ML METHODS
    
    def _check_ml_circuit_breaker(self) -> bool:
        """Check if ML circuit breaker allows calls."""
        now = datetime.utcnow()
        
        if self.ml_circuit_breaker.state == "open":
            # Check if timeout has passed
            if (self.ml_circuit_breaker.last_failure_time and 
                now - self.ml_circuit_breaker.last_failure_time > self.circuit_breaker_timeout):
                self.ml_circuit_breaker.state = "half_open"
                self.ml_circuit_breaker.success_count = 0
                self.logger.info("ML circuit breaker moved to half-open state")
                return True
            return False
        
        elif self.ml_circuit_breaker.state == "half_open":
            # Allow limited calls to test if service is recovered
            return True
        
        else:  # closed
            return True
    
    def _record_ml_success(self) -> None:
        """Record ML model success."""
        if self.ml_circuit_breaker.state == "half_open":
            self.ml_circuit_breaker.success_count += 1
            if self.ml_circuit_breaker.success_count >= 3:  # Success threshold
                self.ml_circuit_breaker.state = "closed"
                self.ml_circuit_breaker.failure_count = 0
                self.logger.info("ML circuit breaker closed - service recovered")
        elif self.ml_circuit_breaker.state == "closed":
            self.ml_circuit_breaker.failure_count = 0  # Reset failure count on success
    
    def _record_ml_failure(self) -> None:
        """Record ML model failure."""
        self.ml_circuit_breaker.failure_count += 1
        self.ml_circuit_breaker.last_failure_time = datetime.utcnow()
        
        if self.ml_circuit_breaker.failure_count >= self.circuit_breaker_threshold:
            self.ml_circuit_breaker.state = "open"
            self.logger.warning(f"ML circuit breaker opened after {self.ml_circuit_breaker.failure_count} failures")
    
    def _get_active_detection_levels(self) -> List[str]:
        """Get list of active detection levels."""
        levels = ["regex"]
        
        # Add parser level if parser analysis is available
        if self.config.is_feature_enabled("ast_analysis"):
            levels.append("parser")
        
        if self.ast_analyzer and self.config.is_feature_enabled("ast_analysis"):
            levels.append("ast")
        if self.dataflow_analyzer and self.config.is_feature_enabled("dataflow_analysis"):
            levels.append("dataflow")
        if self.ml_filter and self.config.is_feature_enabled("ml_filtering"):
            levels.append("ml_filter")
        if self.gdpr_analyzer and self.config.is_feature_enabled("gdpr_compliance"):
            levels.append("gdpr_compliance")
        
        return levels
    
    def _deduplicate_matches(self, matches: List[DetectionMatch]) -> List[DetectionMatch]:
        """Remove duplicate matches while preserving the best detection method with context-aware filtering."""
        if not matches:
            return matches
        
        # Group matches by location and content (more aggressive grouping)
        match_groups = {}
        for match in matches:
            # Create a key based on file location and matched content
            # Use a more flexible grouping to catch more duplicates
            matched_text = match.matched_text.strip()
            
            # Normalize the text for better grouping
            normalized_text = self._normalize_text_for_grouping(matched_text)
            
            # Group by line number and normalized text
            key = (match.line_number, normalized_text)
            
            if key not in match_groups:
                match_groups[key] = []
            match_groups[key].append(match)
        
        # For each group, keep the best match with context-aware filtering
        deduplicated = []
        for key, group in match_groups.items():
            if len(group) == 1:
                # Single match, keep it
                deduplicated.append(group[0])
            else:
                # Multiple matches, apply context-aware filtering
                filtered_group = self._apply_context_based_filtering(group)
                if filtered_group:
                    best_match = self._select_best_match(filtered_group)
                    deduplicated.append(best_match)
        
        self.logger.info(f"Context-aware deduplication: {len(matches)} -> {len(deduplicated)} matches")
        return deduplicated

    def _apply_context_based_filtering(self, matches: List[DetectionMatch]) -> List[DetectionMatch]:
        """
        Apply context-based filtering to a group of duplicate matches.
        
        Args:
            matches: List of duplicate matches to filter
            
        Returns:
            Filtered list of matches
        """
        if not matches:
            return matches
        
        # Filter out matches that are clearly legitimate usage
        legitimate_matches = [m for m in matches if getattr(m, 'legitimate_usage_flag', False)]
        non_legitimate_matches = [m for m in matches if not getattr(m, 'legitimate_usage_flag', False)]
        
        # If we have legitimate usage matches, prefer them (they're safer to keep)
        if legitimate_matches:
            # Keep legitimate matches with higher confidence
            legitimate_matches.sort(key=lambda m: getattr(m, 'confidence_score', 0.0), reverse=True)
            return legitimate_matches[:1]  # Keep only the best legitimate match
        
        # Enhanced duplicate filtering for non-legitimate matches
        if len(non_legitimate_matches) > 1:
            # Group by pattern type to avoid multiple similar detections
            pattern_groups = {}
            for match in non_legitimate_matches:
                pattern_name = match.pattern_name.lower()
                if pattern_name not in pattern_groups:
                    pattern_groups[pattern_name] = []
                pattern_groups[pattern_name].append(match)
            
            # For each pattern type, keep only the best match
            filtered_matches = []
            for pattern_name, pattern_matches in pattern_groups.items():
                if len(pattern_matches) == 1:
                    filtered_matches.append(pattern_matches[0])
                else:
                    # Multiple matches of same pattern, keep the best one
                    best_match = max(pattern_matches, key=lambda m: m.confidence)
                    filtered_matches.append(best_match)
            
            return filtered_matches
        
        return non_legitimate_matches
    
    def _normalize_text_for_grouping(self, text: str) -> str:
        """Normalize text for better duplicate detection."""
        if not text:
            return ""
        
        # Convert to lowercase
        normalized = text.lower()
        
        # Remove common prefixes/suffixes that don't affect PII detection
        prefixes_to_remove = [
            'f"', 'f\'', 'r"', 'r\'', '"', "'",  # String literals
            '// ', '# ', '/* ', ' *', '*/',  # Comments
            'function ', 'class ', 'var ', 'const ', 'let ',  # Code keywords
        ]
        
        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break
        
        # Remove trailing punctuation
        normalized = normalized.rstrip('.,;:!?')
        
        # Truncate to reasonable length for comparison
        return normalized[:100]
    
    def _select_best_match(self, matches: List[DetectionMatch]) -> DetectionMatch:
        """Select the best match from a group of duplicates."""
        if not matches:
            return matches[0]
        
        # Priority order: ML > AST > Parser > Regex
        priority = {
            'ml_filter': 4,
            'ast': 3,
            'parser': 2,
            'regex': 1
        }
        
        # Get detection level for each match
        def get_priority(match):
            detection_level = match.metadata.get('detection_level', 'regex')
            return priority.get(detection_level, 0)
        
        # Sort by priority, then by confidence
        best_match = max(matches, key=lambda m: (get_priority(m), m.confidence))
        
        # Update metadata to show this was deduplicated
        best_match.metadata['deduplicated_from'] = len(matches)
        best_match.metadata['original_detection_methods'] = [
            m.metadata.get('detection_level', 'unknown') for m in matches
        ]
        
        return best_match
    
    def _pre_filter_false_positives(self, matches: List[DetectionMatch], content: str) -> List[DetectionMatch]:
        """Pre-filter obvious false positives before ML processing."""
        if not matches:
            return matches
        
        filtered_matches = []
        
        for match in matches:
            # Skip if it's an obvious false positive
            if self._is_obvious_false_positive(match, content):
                continue
            
            filtered_matches.append(match)
        
        self.logger.info(f"Pre-filtering removed {len(matches) - len(filtered_matches)} obvious false positives")
        return filtered_matches
    
    def _is_obvious_false_positive(self, match: DetectionMatch, content: str) -> bool:
        """Check if a match is an obvious false positive."""
        matched_text = match.matched_text.lower()
        pattern_name = match.pattern_name.lower()
        
        # Skip very short matches (likely not real PII)
        if len(matched_text.strip()) < 5:
            return True
        
        # Skip obvious test data
        if self._is_likely_test_data(matched_text):
            return True
        
        # Use context analyzer for better false positive detection
        if hasattr(self, 'context_analyzer') and self.context_analyzer:
            try:
                # Create a mock node info for context analysis
                node_info = {
                    'value': match.matched_text,
                    'name': getattr(match, 'variable_name', ''),
                    'line_number': match.line_number,
                    'col_offset': 0
                }
                
                # Create file context for analysis
                file_context = {
                    'file_path': str(match.file_path) if hasattr(match, 'file_path') else '',
                    'content': content,
                    'language': getattr(match, 'language', 'unknown'),
                    'scope_info': {}
                }
                
                # Analyze context
                context_result = self.context_analyzer.analyze(node_info, file_context)
                
                # If context analysis indicates legitimate usage, mark as false positive
                if context_result.legitimate_usage:
                    return True
                    
            except Exception as e:
                self.logger.debug(f"Context analysis failed for false positive check: {e}")
                # Continue with other checks if context analysis fails
        
        # Skip obvious code patterns - much more comprehensive
        code_patterns = [
            # Logging and output
            'console.log', 'print', 'logger', 'logging', 'log',
            'system.out', 'system.err', 'stdout', 'stderr',
            
            # Code keywords
            'function', 'class', 'method', 'def ', 'async', 'await',
            'import ', 'from ', 'require', 'include', 'using',
            'var ', 'const ', 'let ', 'public', 'private', 'protected',
            'static', 'final', 'abstract', 'interface', 'enum',
            
            # HTTP and networking
            'http://', 'https://', 'www.', 'localhost', '127.0.0.1',
            'fetch', 'axios', 'request', 'response', 'api',
            
            # File system and I/O
            'fs', 'file', 'read', 'write', 'open', 'close',
            'path', 'dir', 'directory', 'folder',
            
            # Database
            'sql', 'insert', 'select', 'update', 'delete',
            'database', 'db', 'table', 'schema', 'query',
            
            # Common programming patterns
            'try', 'catch', 'finally', 'throw', 'throws',
            'if ', 'else', 'switch', 'case', 'default',
            'for ', 'while', 'do ', 'break', 'continue',
            'return', 'yield', 'throw', 'assert'
        ]
        
        for pattern in code_patterns:
            if pattern in matched_text:
                return True
        
        # Skip obvious comment patterns that don't contain real PII
        if 'parser_comment_analysis' in pattern_name:
            comment_indicators = [
                # Code annotations
                'todo:', 'fixme:', 'hack:', 'note:', 'warning:', 'bug:',
                'deprecated:', 'obsolete:', 'legacy:', 'temporary:',
                
                # Code structure
                'function', 'class', 'method', 'api', 'endpoint', 'route',
                'controller', 'service', 'repository', 'dao',
                
                # Configuration and setup
                'configuration', 'config', 'setting', 'option', 'parameter',
                'environment', 'env', 'profile', 'mode', 'debug',
                
                # Database and infrastructure
                'database', 'table', 'schema', 'migration', 'index',
                'cache', 'redis', 'queue', 'job', 'worker',
                
                # Generic development terms
                'development', 'production', 'staging', 'testing',
                'build', 'deploy', 'release', 'version', 'update'
            ]
            
            if any(indicator in matched_text for indicator in comment_indicators):
                return True
            
            # Check for levox-ignore comments
            if self._has_levox_ignore_comment(match, content):
                return True
        
        # Skip obvious variable patterns that don't contain real PII
        if 'parser_variable_analysis' in pattern_name:
            var_indicators = [
                # Loop and iterator variables
                'i', 'j', 'k', 'x', 'y', 'z', 'n', 'm', 'p', 'q',
                'index', 'idx', 'counter', 'count', 'size', 'length',
                
                # Generic variables
                'temp', 'tmp', 'var', 'val', 'item', 'element', 'obj',
                'data', 'result', 'output', 'input', 'param', 'arg',
                
                # Boolean and flag variables
                'flag', 'bool', 'is_', 'has_', 'can_', 'should_', 'will_',
                'enabled', 'disabled', 'active', 'inactive', 'valid', 'invalid',
                
                # Configuration variables
                'config', 'setting', 'option', 'param', 'property', 'attribute',
                'mode', 'level', 'type', 'status', 'state'
            ]
            
            if any(indicator in matched_text for indicator in var_indicators):
                return True
        
        # Skip obvious string patterns that don't contain real PII
        if 'parser_string_analysis' in pattern_name:
            string_indicators = [
                # Code structure
                'function', 'class', 'method', 'api', 'endpoint', 'route',
                'controller', 'service', 'repository', 'dao', 'util', 'helper',
                
                # Configuration and setup
                'configuration', 'config', 'setting', 'option', 'parameter',
                'environment', 'env', 'profile', 'mode', 'debug', 'test',
                
                # Database and infrastructure
                'database', 'table', 'schema', 'migration', 'index',
                'cache', 'redis', 'queue', 'job', 'worker', 'server',
                
                # Generic development terms
                'development', 'production', 'staging', 'testing',
                'build', 'deploy', 'release', 'version', 'update', 'fix',
                
                # Common programming patterns
                'error', 'exception', 'warning', 'info', 'debug',
                'success', 'failure', 'complete', 'pending', 'processing'
            ]
            
            if any(indicator in matched_text for indicator in string_indicators):
                return True
        
        # Skip dataflow patterns that are just common programming constructs
        if 'dataflow' in pattern_name:
            dataflow_indicators = [
                'fs', 'file', 'console', 'print', 'log', 'logger',
                'stdout', 'stderr', 'system.out', 'system.err',
                'fetch', 'request', 'response', 'http', 'api',
                'json.dump', 'json.load', 'pickle.dump', 'pickle.load',
                'yaml.dump', 'yaml.load', 'xml.dump', 'xml.load',
                'csv.writer', 'csv.reader', 'sqlite', 'mysql', 'postgresql',
                'redis', 'memcached', 'elasticsearch', 'mongodb'
            ]
            
            if any(indicator in matched_text for indicator in dataflow_indicators):
                return True
        
        # Skip SQL templates and common database patterns
        sql_patterns = [
            'insert into', 'select from', 'update set', 'delete from',
            'create table', 'alter table', 'drop table', 'create index',
            'values (', 'where ', 'order by', 'group by', 'having ',
            'join ', 'left join', 'right join', 'inner join',
            'union ', 'intersect', 'except', 'subquery'
        ]
        
        if any(sql_pattern in matched_text for sql_pattern in sql_patterns):
            return True
        
        # Skip common programming template strings
        template_patterns = [
            'f"', 'f\'', 'r"', 'r\'', 'b"', 'b\'',  # String prefixes
            'template', 'format', 'placeholder', 'variable',
            'string interpolation', 'string formatting'
        ]
        
        if any(template_pattern in matched_text for template_pattern in template_patterns):
            return True
        
        # Skip log message templates and common patterns
        log_patterns = [
            'creating', 'created', 'failed to', 'successfully', 'sending',
            'processing', 'updating', 'deleting', 'saving', 'loading',
            'starting', 'stopping', 'initializing', 'configuring',
            'connecting to', 'disconnected from', 'authenticating',
            'validating', 'checking', 'verifying', 'testing'
        ]
        
        if any(log_pattern in matched_text for log_pattern in log_patterns):
            return True
        
        # Skip integration and system messages
        system_patterns = [
            'integration', 'service', 'api', 'endpoint', 'connection',
            'database', 'cache', 'queue', 'worker', 'job', 'task',
            'configuration', 'setting', 'option', 'parameter'
        ]
        
        if any(system_pattern in matched_text for system_pattern in system_patterns):
            return True
        
        # Skip security and compliance comments that aren't actual PII
        security_patterns = [
            'handling', 'storing', 'encryption', 'decryption', 'hashing',
            'violation', 'exposure', 'breach', 'leak', 'security',
            'compliance', 'gdpr', 'hipaa', 'pci', 'sox', 'audit',
            'contains multiple', 'multiple violations', 'security issue'
        ]
        
        if any(security_pattern in matched_text for security_pattern in security_patterns):
            return True
        
        return False
    
    def _check_ml_circuit_breaker(self) -> bool:
        """Check if ML operations are allowed based on circuit breaker state."""
        # For now, always allow ML operations
        # In production, this would check failure rates and circuit breaker state
        return True
    
    def _record_ml_success(self) -> None:
        """Record successful ML operation."""
        # In production, this would update circuit breaker metrics
        pass
    
    def _record_ml_failure(self) -> None:
        """Record failed ML operation."""
        # In production, this would update circuit breaker metrics
        pass
    
    # CONFIGURATION AND MANAGEMENT METHODS
    
    def reload_configuration(self) -> None:
        """Hot-reload configuration from file."""
        try:
            if hasattr(self.config, 'config_file_path'):
                new_config = Config.from_file(self.config.config_file_path)
                self.config = new_config
                self._initialize_engines()
                self.logger.info("Configuration reloaded successfully")
            else:
                self.logger.warning("No config file path available for hot reload")
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
    
    def configure_rules(self, rules_config: Dict[str, Any]) -> None:
        """Load/update rules dynamically."""
        try:
            # Update patterns
            if 'patterns' in rules_config:
                self.config.patterns = rules_config['patterns']
                self.regex_engine = RegexEngine(self.config.patterns)
            
            # Update performance settings
            if 'performance' in rules_config:
                for key, value in rules_config['performance'].items():
                    if hasattr(self.config.performance, key):
                        setattr(self.config.performance, key, value)
            
            # Update license tier if provided
            if 'license' in rules_config and 'tier' in rules_config['license']:
                new_tier = LicenseTier(rules_config['license']['tier'])
                self.config.update_license_tier(new_tier)
                self._initialize_engines()  # Reinitialize with new license
            
            # Update GDPR settings if provided
            if 'gdpr' in rules_config:
                gdpr_config = rules_config['gdpr']
                if 'enabled' in gdpr_config:
                    self.config.enable_gdpr = gdpr_config['enabled']
                if 'patterns' in gdpr_config and self.gdpr_analyzer:
                    # Update GDPR patterns if analyzer is available
                    self.logger.info("GDPR patterns updated")
            
            self.logger.info("Rules configuration updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to configure rules: {e}")
            raise DetectionError(f"Failed to configure rules: {e}")
    
    def get_results(self) -> Iterator[FileResult]:
        """Retrieve structured scan results from streaming queue."""
        while not self.results_queue.empty():
            try:
                yield self.results_queue.get_nowait()
            except queue.Empty:
                break
    
    def enable_streaming(self) -> None:
        """Enable streaming results."""
        self.streaming_enabled = True
        self.logger.info("Streaming results enabled")
    
    def disable_streaming(self) -> None:
        """Disable streaming results."""
        self.streaming_enabled = False
        # Clear queue
        while not self.results_queue.empty():
            try:
                self.results_queue.get_nowait()
            except queue.Empty:
                break
        self.logger.info("Streaming results disabled")
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Determine if a file should be scanned."""
        # Check file size
        try:
            file_size_mb = file_path.stat().st_size / 1024 / 1024
            if file_size_mb > self.config.performance.max_file_size_mb:
                return False
        except OSError:
            return False
        
        # Check include patterns
        if self.config.include_patterns:
            if not any(file_path.match(pattern) for pattern in self.config.include_patterns):
                return False
        
        # Check exclude patterns
        if self.config.exclude_patterns:
            if any(file_path.match(pattern) for pattern in self.config.exclude_patterns):
                return False
        
        # Check exclude directories
        for exclude_dir in self.config.exclude_dirs:
            if exclude_dir in file_path.parts:
                return False
        
        return True
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension using parser factory."""
        # Use the parser factory for language detection
        detected_language = detect_language(file_path)
        if detected_language:
            return detected_language
        
        # Fallback to extension-based detection for unsupported languages
        extension = file_path.suffix.lower()
        fallback_language_map = {
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
        }
        
        return fallback_language_map.get(extension, 'unknown')
    
    def _analyze_with_parser(self, file_path: Path, content: str, language: str) -> List[DetectionMatch]:
        """Analyze file using the appropriate language parser."""
        try:
            # Get parser for the file
            parser = get_parser(file_path, content, self.config)
            if not parser:
                self.logger.debug(f"No parser available for {language} file: {file_path}")
                return []
            
            # Extract structured information using the parser
            matches = []
            
            # Extract strings for PII detection
            self.logger.debug(f"Calling extract_strings on parser {type(parser).__name__}")
            strings = parser.extract_strings(file_path, content)
            for string_literal in strings:
                # Check if string contains potential PII patterns
                if self._contains_pii_pattern(string_literal.value):
                    match = DetectionMatch(
                        file=str(file_path),
                        line=string_literal.start_line,
                        engine="parser",
                        rule_id="parser_string_analysis",
                        severity="MEDIUM",
                        confidence=0.8,
                        snippet=string_literal.value[:100],
                        description="Parser string analysis detected potential PII",
                        pattern_name="parser_string_analysis",
                        matched_text=string_literal.value[:100],
                        column_start=string_literal.start_col,
                        column_end=string_literal.end_col,
                        risk_level=RiskLevel.MEDIUM,
                        context_before="",
                        context_after="",
                        metadata={
                            'parser_language': language,
                            'string_context': string_literal.context,
                            'raw_value': string_literal.raw_value,
                            'rule_name': "Parser String Analysis",
                            'message': f"Potential PII found in {string_literal.context}: {string_literal.value[:100]}...",
                            'detection_level': 'parser'
                        }
                    )
                    matches.append(match)
            
            # Enhanced AST Analysis Features (if available)
            if hasattr(parser, 'get_enhanced_analysis'):
                try:
                    enhanced_analysis = parser.get_enhanced_analysis(content, file_path)
                    
                    # F-String and Template Literal Analysis
                    if 'f_strings' in enhanced_analysis:
                        for f_string in enhanced_analysis['f_strings']:
                            if f_string.is_sensitive:
                                match = DetectionMatch(
                                    file=str(file_path),
                                    line=f_string.start_line,
                                    engine="parser",
                                    rule_id="enhanced_f_string_analysis",
                                    severity="HIGH",
                                    confidence=0.9,
                                    snippet=f_string.expression[:100],
                                    description="Enhanced F-string analysis detected sensitive variable",
                                    pattern_name="enhanced_f_string_analysis",
                                    matched_text=f_string.expression[:100],
                                    column_start=f_string.start_col,
                                    column_end=f_string.end_col,
                                    risk_level=RiskLevel.HIGH,
                                    context_before="",
                                    context_after="",
                                    metadata={
                                        'parser_language': language,
                                        'variable_name': f_string.variable_name,
                                        'context': f_string.context,
                                        'rule_name': "Enhanced F-String Analysis",
                                        'message': f"F-string with sensitive variable: {f_string.variable_name}",
                                        'detection_level': 'enhanced_ast'
                                    }
                                )
                                matches.append(match)
                    
                    if 'template_literals' in enhanced_analysis:
                        for template_lit in enhanced_analysis['template_literals']:
                            if template_lit.is_sensitive:
                                match = DetectionMatch(
                                    file=str(file_path),
                                    line=template_lit.start_line,
                                    engine="parser",
                                    rule_id="enhanced_template_literal_analysis",
                                    severity="HIGH",
                                    confidence=0.9,
                                    snippet=template_lit.expression[:100],
                                    description="Enhanced template literal analysis detected sensitive variable",
                                    pattern_name="enhanced_template_literal_analysis",
                                    matched_text=template_lit.expression[:100],
                                    column_start=template_lit.start_col,
                                    column_end=template_lit.end_col,
                                    risk_level=RiskLevel.HIGH,
                                    context_before="",
                                    context_after="",
                                    metadata={
                                        'parser_language': language,
                                        'variable_name': template_lit.variable_name,
                                        'context': template_lit.context,
                                        'rule_name': "Enhanced Template Literal Analysis",
                                        'message': f"Template literal with sensitive variable: {template_lit.variable_name}",
                                        'detection_level': 'enhanced_ast'
                                    }
                                )
                                matches.append(match)
                    
                    # Logging Context Analysis
                    if 'logging_contexts' in enhanced_analysis:
                        for log_context in enhanced_analysis['logging_contexts']:
                            if log_context.contains_pii:
                                match = DetectionMatch(
                                    pattern_name="enhanced_logging_analysis",
                                    matched_text=f"logging.{log_context.function_name}",
                                    line_number=log_context.start_line,
                                    column_start=log_context.start_col,
                                    column_end=log_context.end_col,
                                    confidence=0.85,
                                    risk_level=RiskLevel.HIGH,
                                    context_before="",
                                    context_after="",
                                    metadata={
                                        'parser_language': language,
                                        'function_name': log_context.function_name,
                                        'level': log_context.level,
                                        'pii_types': log_context.pii_types,
                                        'rule_name': "Enhanced Logging Analysis",
                                        'message': f"Logging with PII detected: {log_context.pii_types}",
                                        'detection_level': 'enhanced_ast'
                                    }
                                )
                                matches.append(match)
                    
                    # Test Context Analysis
                    if 'test_contexts' in enhanced_analysis:
                        for test_context in enhanced_analysis['test_contexts']:
                            if test_context.is_fixture or test_context.is_mock:
                                # Mark test fixtures with lower confidence
                                for existing_match in matches:
                                    if (existing_match.line_number == test_context.start_line and 
                                        existing_match.metadata.get('detection_level') == 'parser'):
                                        existing_match.confidence *= 0.3  # Reduce confidence for test fixtures
                                        existing_match.metadata['test_context'] = test_context.test_type
                                        existing_match.metadata['is_fixture'] = test_context.is_fixture
                                        existing_match.metadata['is_mock'] = test_context.is_mock
                    
                    self.logger.debug(f"Enhanced AST analysis completed for {file_path}")
                    
                except Exception as e:
                    self.logger.debug(f"Enhanced AST analysis failed for {file_path}: {e}")
                    # Continue with basic analysis
            
            # Extract comments for additional context
            comments = parser.extract_comments(file_path, content)
            for comment in comments:
                # Only analyze comments that are likely to contain real PII
                if self._is_comment_worth_analyzing(comment.text):
                    if self._contains_pii_pattern(comment.text):
                        match = DetectionMatch(
                            file=str(file_path),
                            line=comment.start_line,
                            engine="parser",
                            rule_id="parser_comment_analysis",
                            severity="MEDIUM",
                            confidence=0.7,
                            snippet=comment.text[:100],
                            description="Parser comment analysis detected potential PII",
                            pattern_name="parser_comment_analysis",
                            matched_text=comment.text[:100],
                            column_start=comment.start_col,
                            column_end=comment.end_col,
                            risk_level=RiskLevel.MEDIUM,
                            context_before="",
                            context_after="",
                            metadata={
                                'parser_language': language,
                                'comment_type': comment.comment_type,
                                'rule_name': "Parser Comment Analysis",
                                'message': f"Potential PII found in comment: {comment.text[:100]}...",
                                'detection_level': 'parser'
                            }
                        )
                        matches.append(match)
            
            # Extract variable declarations for context analysis
            variables = parser.extract_variables(file_path, content)
            for variable in variables:
                # Only analyze variables that are likely to contain PII
                if self._is_variable_worth_analyzing(variable.name, variable.context):
                    if self._contains_pii_pattern(variable.name):
                        match = DetectionMatch(
                            file=str(file_path),
                            line=variable.start_line,
                            engine="parser",
                            rule_id="parser_variable_analysis",
                            severity="MEDIUM",
                            confidence=0.6,
                            snippet=variable.name,
                            description="Parser variable analysis detected potential PII",
                            pattern_name="parser_variable_analysis",
                            matched_text=variable.name,
                            column_start=variable.start_col,
                            column_end=variable.end_col,
                            risk_level=RiskLevel.MEDIUM,
                            context_before="",
                            context_after="",
                            metadata={
                                'parser_language': language,
                                'variable_type': variable.var_type,
                                'modifiers': variable.modifiers,
                                'context': variable.context,
                                'rule_name': "Parser Variable Analysis",
                                'message': f"Variable name suggests PII: {variable.name}",
                                'detection_level': 'parser'
                            }
                        )
                        matches.append(match)
            
            # Enhanced Context Analysis
            if hasattr(parser, 'analyze_file_context'):
                try:
                    context_analysis = parser.analyze_file_context(content, file_path)
                    
                    # Apply context-based confidence adjustments
                    for match in matches:
                        if context_analysis.is_test_file:
                            match.confidence *= 0.7  # Reduce confidence for test files
                            match.metadata['context_type'] = 'test'
                        elif context_analysis.has_suppressions:
                            match.confidence *= 0.5  # Reduce confidence for files with suppressions
                            match.metadata['context_type'] = 'suppressed'
                        elif context_analysis.is_generated:
                            match.confidence *= 0.3  # Reduce confidence for generated files
                            match.metadata['context_type'] = 'generated'
                        else:
                            match.metadata['context_type'] = 'production'
                        
                        # Add framework hints
                        if context_analysis.framework_hints:
                            match.metadata['framework_hints'] = list(context_analysis.framework_hints)
                        
                        # Add risk context
                        match.metadata['risk_context'] = context_analysis.risk_context.value
                    
                    self.logger.debug(f"Enhanced context analysis completed for {file_path}")
                    
                except Exception as e:
                    self.logger.debug(f"Enhanced context analysis failed for {file_path}: {e}")
                    # Continue with basic analysis
            
            self.logger.debug(f"Parser analysis found {len(matches)} potential matches for {file_path}")
            return matches
            
        except Exception as e:
            self.logger.warning(f"Parser analysis failed for {file_path}: {e}")
            return []

    def _detect_test_context(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        Detect if a file is in a test context and determine confidence adjustments.
        
        Args:
            file_path: Path to the file being analyzed
            content: Content of the file
            
        Returns:
            Dictionary with test context information and confidence adjustments
        """
        test_context_info = {
            'in_test_context': False,
            'framework_safe': False,
            'test_file_type': None,
            'confidence_adjustment': 1.0
        }
        
        try:
            file_str = str(file_path).lower()
            file_name = file_path.name.lower()
            content_lower = content.lower()
            
            # Check file name patterns
            test_name_patterns = [
                'test_', '_test', 'spec_', '_spec', 'mock_', '_mock',
                'fixture_', '_fixture', 'example_', '_example', 'sample_', '_sample',
                'dummy_', '_dummy', 'stub_', '_stub', 'fake_', '_fake'
            ]
            
            for pattern in test_name_patterns:
                if pattern in file_name:
                    test_context_info['in_test_context'] = True
                    test_context_info['test_file_type'] = 'filename_pattern'
                    test_context_info['confidence_adjustment'] = 0.5
                    break
            
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
                    test_context_info['in_test_context'] = True
                    test_context_info['test_file_type'] = 'directory_pattern'
                    test_context_info['confidence_adjustment'] = 0.5
                    break
            
            # Check for test framework imports
            test_imports = [
                'import unittest', 'import pytest', 'from unittest import',
                'import jest', 'import mocha', 'import chai', 'import sinon',
                'import mock', 'from mock import', 'import factory_boy',
                'import factory', 'from factory import'
            ]
            
            test_import_count = 0
            for test_import in test_imports:
                if test_import in content_lower:
                    test_import_count += 1
            
            if test_import_count >= 1:
                test_context_info['in_test_context'] = True
                test_context_info['test_file_type'] = 'test_framework_import'
                test_context_info['confidence_adjustment'] = 0.5
            
            # Check for test class/function patterns
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
                test_context_info['in_test_context'] = True
                test_context_info['test_file_type'] = 'test_patterns'
                test_context_info['confidence_adjustment'] = 0.5
            
            # Check for framework-safe patterns
            framework_patterns = [
                'cursor.execute', 'obj.save', 'Model.objects.create', 'Model.objects.get',
                'session.add', 'session.commit', 'session.query', 'session.execute',
                'logger.info', 'logger.debug', 'logger.warning', 'logger.error',
                'console.log', 'console.info', 'console.warn', 'console.error',
                'System.out.println', 'System.out.print', 'System.err.println'
            ]
            
            framework_pattern_count = 0
            for pattern in framework_patterns:
                if pattern in content_lower:
                    framework_pattern_count += 1
            
            if framework_pattern_count >= 2:
                test_context_info['framework_safe'] = True
                test_context_info['confidence_adjustment'] *= 0.3
            
            # Check for migration files
            migration_patterns = [
                'migrations/', 'migration', 'alembic', 'version', 'upgrade', 'downgrade',
                'op.create_table', 'op.drop_table', 'op.add_column', 'op.drop_column'
            ]
            
            migration_count = 0
            for pattern in migration_patterns:
                if pattern in file_str or pattern in content_lower:
                    migration_count += 1
            
            if migration_count >= 1:
                test_context_info['in_test_context'] = True
                test_context_info['test_file_type'] = 'migration_file'
                test_context_info['confidence_adjustment'] = 0.2  # Very low confidence for migrations
            
            return test_context_info
            
        except Exception as e:
            self.logger.debug(f"Test context detection failed for {file_path}: {e}")
            return test_context_info

    def _perform_fallback_analysis(self, file_path: Path, content: str, language: str) -> List[DetectionMatch]:
        """
        Perform fallback analysis when dataflow analysis times out.
        Uses AST + Context analysis with reduced confidence.
        
        Args:
            file_path: Path to the file being analyzed
            content: Content of the file
            language: Programming language of the file
            
        Returns:
            List of DetectionMatch objects from fallback analysis
        """
        fallback_matches = []
        
        try:
            self.logger.debug(f"Performing fallback analysis for {file_path}")
            
            # Use AST analysis as fallback
            if self.ast_analyzer and self.config.is_feature_enabled("ast_analysis"):
                try:
                    ast_matches = self.ast_analyzer.scan_file(str(file_path))
                    # Convert to unified format with reduced confidence
                    unified_ast_matches = self._convert_to_unified_matches(
                        ast_matches, file_path, content, "ast_fallback", language
                    )
                    
                    # Reduce confidence for fallback results
                    for match in unified_ast_matches:
                        match.confidence *= 0.85  # 15% confidence reduction for fallback
                        match.metadata.update({
                            'analysis_method': 'fallback',
                            'fallback_reason': 'dataflow_timeout',
                            'original_engine': 'dataflow'
                        })
                        fallback_matches.append(match)
                    
                    self.logger.debug(f"Fallback AST analysis found {len(unified_ast_matches)} matches")
                    
                except Exception as e:
                    self.logger.warning(f"Fallback AST analysis failed for {file_path}: {e}")
            
            # If no AST matches, create a basic timeout detection
            if not fallback_matches:
                timeout_match = DetectionMatch(
                    file=str(file_path),
                    line=1,
                    engine="fallback",
                    rule_id="dataflow_timeout_fallback",
                    severity="LOW",
                    confidence=0.3,
                    snippet="Dataflow analysis timeout - fallback analysis",
                    description="Dataflow analysis timed out, using fallback analysis",
                    pattern_name='dataflow_timeout_fallback',
                    matched_text='Analysis timeout',
                    column_start=1,
                    column_end=1,
                    risk_level=RiskLevel.LOW,
                    context_before='',
                    context_after='',
                    metadata={
                        'detection_level': 'fallback',
                        'match_type': 'timeout_fallback',
                        'analysis_method': 'fallback',
                        'fallback_reason': 'dataflow_timeout',
                        'original_engine': 'dataflow'
                    }
                )
                fallback_matches.append(timeout_match)
            
            return fallback_matches
            
        except Exception as e:
            self.logger.error(f"Fallback analysis failed for {file_path}: {e}")
            return []

    def _analyze_match_context(self, match: DetectionMatch, content: str, file_path: Path, language: str) -> Dict[str, Any]:
        """
        Analyze the context of a detection match to provide additional insights.
        
        Args:
            match: The detection match to analyze
            content: File content for context extraction
            file_path: Path to the file being analyzed
            language: Programming language of the file
            
        Returns:
            Dictionary containing context information
        """
        try:
            context_info = {
                'file_path': str(file_path),
                'language': language,
                'line_number': match.line_number,
                'detection_timestamp': datetime.utcnow().isoformat()
            }
            
            if not self.context_analyzer:
                return context_info
            
            # Extract comment context around the match
            comment_context = self.context_analyzer.extract_comment_context(content, match.line_number)
            context_info['comment_context'] = comment_context
            
            # Analyze imports for security libraries
            import_contexts = self.context_analyzer.analyze_imports(content, language)
            context_info['import_context'] = import_contexts
            
            # Check if the match appears to be test data
            is_test_data = self.context_analyzer.detect_test_data(match)
            context_info['is_test_data'] = is_test_data
            
            # Analyze variable context if this is a variable-related match
            if 'variable' in match.pattern_name.lower() or 'identifier' in match.pattern_name.lower():
                # Create a mock node for variable analysis
                mock_node = type('MockNode', (), {
                    'name': match.matched_text,
                    'value': match.matched_text,
                    'start_line': match.line_number,
                    'start_col': match.column_start,
                    'end_col': match.column_end
                })()
                
                # Mock scope information
                scope_info = {
                    'is_test_function': 'test' in str(file_path).lower() or 'test' in content.lower()[:1000],
                    'in_logging_call': 'log' in match.context_before.lower() or 'log' in match.context_after.lower(),
                    'in_test_assertion': 'assert' in match.context_before.lower() or 'assert' in match.context_after.lower(),
                    'in_config': 'config' in match.context_before.lower() or 'config' in match.context_after.lower()
                }
                
                variable_context = self.context_analyzer.analyze_variable_context(mock_node, scope_info)
                context_info['variable_context'] = variable_context
            
            # Analyze function context if this appears to be in a function
            if 'function' in match.context_before.lower() or 'function' in match.context_after.lower():
                # Create a mock node for function analysis
                mock_func_node = type('MockFuncNode', (), {
                    'name': 'unknown_function',
                    'body': content[max(0, match.line_number - 10):match.line_number + 10]
                })()
                
                function_context = self.context_analyzer.analyze_function_purpose(mock_func_node, language)
                context_info['function_purpose'] = function_context
            
            # Add file-level context
            context_info['file_context'] = {
                'is_test_file': 'test' in str(file_path).lower() or 'test' in content.lower()[:1000],
                'has_security_imports': any(ic.is_security_library for ic in import_contexts),
                'security_libraries': [ic.module_name for ic in import_contexts if ic.is_security_library]
            }
            
            return context_info
            
        except Exception as e:
            self.logger.debug(f"Failed to analyze match context: {e}")
            return {
                'file_path': str(file_path),
                'language': language,
                'line_number': match.line_number,
                'error': str(e)
            }
    
    def _contains_pii_pattern(self, text: str) -> bool:
        """Check if text contains potential PII patterns with context awareness."""
        if not text or len(text.strip()) < 5:
            return False
        
        # Skip obvious non-PII patterns
        text_lower = text.lower()
        skip_patterns = [
            'http://', 'https://', 'www.',  # URLs (but not emails)
            'function', 'class', 'var ', 'const ', 'let ',  # Code keywords
            'import ', 'from ', 'require', 'include',  # Import statements
            'console.log', 'print', 'logger',  # Logging
            '000-00-0000', '999-99-9999',  # Only skip obvious test SSNs
            '4111-1111-1111-1111', '5555-5555-5555-4444',  # Only skip obvious test credit cards
        ]
        
        for skip_pattern in skip_patterns:
            if skip_pattern in text_lower:
                return False
        
        # Common PII patterns with stricter matching
        pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
            r'\b\d{5}(-\d{4})?\b',     # ZIP code
            r'\b[A-Z]{2}\s\d{2}\s\d{4}\b',  # License plate
            r'\b\d{16}\b',             # Credit card
            r'\b[A-Za-z]+\s[A-Za-z]+\s[A-Za-z]+\b',  # Full name pattern
        ]
        
        for pattern in pii_patterns:
            if re.search(pattern, text):
                # Additional context check - avoid obvious test data
                if not self._is_likely_test_data(text):
                    return True
        
        return False
    
    def _apply_confidence_threshold_filter(self, matches: List[DetectionMatch], threshold: Optional[float] = None) -> List[DetectionMatch]:
        """
        Apply tier-aware confidence threshold filtering to matches.
        
        Args:
            matches: List of detection matches to filter
            threshold: Optional override threshold, uses tier-specific default if None
            
        Returns:
            Filtered list of matches above confidence threshold
        """
        if not matches:
            return matches
        
        # Get tier-specific threshold
        if threshold is None:
            tier = self.config.license.tier.value
            threshold = self.config.tier_specific_thresholds.get(tier, 0.75)
        
        filtered_matches = []
        critical_matches = []
        
        for match in matches:
            # Preserve CRITICAL risk level matches at lower threshold (0.65+)
            if (hasattr(match, 'risk_level') and 
                match.risk_level == RiskLevel.CRITICAL and 
                match.confidence >= 0.65):
                critical_matches.append(match)
                continue
            
            # Apply standard threshold filtering
            if match.confidence >= threshold:
                filtered_matches.append(match)
        
        # Add critical matches to results
        filtered_matches.extend(critical_matches)
        
        # Log filtering statistics
        original_count = len(matches)
        filtered_count = len(filtered_matches)
        critical_count = len(critical_matches)
        
        self.logger.info(
            f"Confidence threshold filtering: {original_count} → {filtered_count} matches "
            f"(threshold={threshold:.2f}, critical_preserved={critical_count})"
        )
        
        return filtered_matches
    
    def _is_likely_test_data(self, text: str) -> bool:
        """Check if text is likely test data rather than real PII."""
        text_lower = text.lower()
        
        # Test data indicators - only flag obvious test data
        test_indicators = [
            '000-00-0000', '999-99-9999', '111-11-1111',
            '4111-1111-1111-1111', '5555-5555-5555-4444',
            'test123', 'demo123', 'fake123'
        ]
        
        # Only skip if it's an exact match to obvious test data
        if any(test_indicator in text_lower for test_indicator in test_indicators):
            return True
        
        # Check against configuration safe literals
        if hasattr(self, 'config') and self.config:
            for safe_literal in getattr(self.config, 'safe_literals', []):
                if safe_literal.lower() in text_lower:
                    return True
        
        # Check for common placeholder patterns
        placeholder_patterns = [
            r'^[0-9]+$',  # Just numbers
            r'^[a-z]+$',  # Just lowercase letters
            r'^[A-Z]+$',  # Just uppercase letters
            r'^[a-zA-Z]+$',  # Just letters
            r'^[0-9a-fA-F]+$',  # Hex strings
            r'^[0-9a-zA-Z]+$',  # Alphanumeric
            r'^[a-zA-Z_][a-zA-Z0-9_]*$',  # Valid identifier
        ]
        
        for pattern in placeholder_patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def _is_comment_worth_analyzing(self, comment_text: str) -> bool:
        """Check if a comment is worth analyzing for PII."""
        if not comment_text or len(comment_text.strip()) < 10:
            return False
        
        text_lower = comment_text.lower()
        
        # Skip obvious non-PII comments
        skip_patterns = [
            'todo:', 'fixme:', 'hack:', 'note:', 'warning:',  # Code annotations
            'function', 'class', 'method', 'api', 'endpoint',  # Code documentation
            'test', 'example', 'sample', 'demo', 'mock',  # Test documentation
            'configuration', 'config', 'setting', 'option',  # Config documentation
            'database', 'table', 'schema', 'migration',  # Database documentation
            'authentication', 'authorization', 'security',  # Security documentation
        ]
        
        for pattern in skip_patterns:
            if pattern in text_lower:
                return False
        
        # Only analyze comments that might contain real PII
        pii_indicators = [
            'user', 'customer', 'client', 'patient', 'employee',
            'email', 'phone', 'address', 'ssn', 'credit card',
            'password', 'secret', 'key', 'token', 'credential'
        ]
        
        # Must contain at least one PII indicator to be worth analyzing
        return any(indicator in text_lower for indicator in pii_indicators)
    
    def _is_variable_worth_analyzing(self, var_name: str, var_context: str) -> bool:
        """Check if a variable is worth analyzing for PII."""
        if not var_name or len(var_name.strip()) < 3:
            return False
        
        var_lower = var_name.lower()
        context_lower = var_context.lower() if var_context else ""
        
        # Skip obvious non-PII variables
        skip_patterns = [
            'i', 'j', 'k', 'x', 'y', 'z',  # Loop variables
            'temp', 'tmp', 'var', 'val', 'item',  # Generic variables
            'index', 'count', 'size', 'length',  # Array/size variables
            'flag', 'bool', 'is_', 'has_', 'can_',  # Boolean variables
            'test', 'example', 'sample', 'demo',  # Test variables
        ]
        
        # More specific checks for configuration variables
        if var_lower in ['config', 'setting', 'option', 'param']:
            return False
        
        # Only analyze variables that might contain PII
        pii_indicators = [
            'user', 'customer', 'client', 'patient', 'employee',
            'email', 'phone', 'address', 'ssn', 'credit_card',
            'password', 'secret', 'key', 'token', 'credential',
            'name', 'first', 'last', 'middle', 'full',
            'birth', 'dob', 'age', 'gender', 'race'
        ]
        
        # Must contain at least one PII indicator to be worth analyzing
        # Use underscore-separated matching for better accuracy
        for indicator in pii_indicators:
            if indicator in var_lower or f"{indicator}_" in var_lower or f"_{indicator}" in var_lower:
                return True
        
        return False
    
    def _has_levox_ignore_comment(self, match: DetectionMatch, content: str) -> bool:
        """Check if there's a levox-ignore comment near the match."""
        try:
            line_num = match.line_number
            if line_num <= 0:
                return False
            
            lines = content.split('\n')
            start = max(0, line_num - 2)  # Check 2 lines before
            end = min(len(lines), line_num + 1)  # Check current line
            
            # Look for levox-ignore comments in the context window
            for i in range(start, end):
                if i < len(lines):
                    line = lines[i].strip()
                    if re.search(r'#\s*levox-ignore', line, re.IGNORECASE):
                        return True
                    if re.search(r'//\s*levox-ignore', line, re.IGNORECASE):
                        return True
                    if re.search(r'/\*\s*levox-ignore', line, re.IGNORECASE):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking for levox-ignore comment: {e}")
            return False
    
    def _check_performance_limits(self) -> None:
        """Check if performance limits are exceeded."""
        if self.start_time is None:
            return
        
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.config.performance.max_scan_time_seconds:
            raise PerformanceError(f"Scan timeout exceeded: {elapsed_time:.2f}s")
        
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_used = current_memory - (self.memory_start or 0)
        if memory_used > self.config.performance.memory_limit_mb:
            raise PerformanceError(f"Memory limit exceeded: {memory_used:.2f}MB")
    
    def _create_result_container(self, start_time: float, scan_path: str = "") -> DetectionResult:
        """Create a new result container."""
        return DetectionResult(
            scan_id=str(uuid.uuid4()),
            scan_duration=0.0,
            license_tier=self.config.license.tier.value,
            scan_path=scan_path,
            files_scanned=0,
            files_with_matches=0,
            total_matches=0,
            total_scan_time=0.0,
            average_file_time=0.0,
            memory_peak_mb=0.0,
            false_positive_rate=0.0,
            confidence_average=0.0
        )
    
    def _create_empty_result(self, start_time: float, scan_path: str = "") -> DetectionResult:
        """Create an empty result for no files found."""
        results = self._create_result_container(start_time, scan_path)
        self._finalize_results(results, start_time)
        return results
    
    def _finalize_results(self, results: DetectionResult, start_time: float) -> None:
        """Finalize results with calculated metrics."""
        # Calculate scan duration
        results.scan_duration = time.time() - start_time
        
        # Calculate performance metrics
        if self.memory_start:
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            results.memory_peak_mb = max(current_memory, self.memory_start)
        
        # Calculate derived metrics
        results.calculate_metrics()
        
        # Record performance metrics
        self.performance_monitor.record_operation(
            'full_scan',
            results.scan_duration,
            results.files_scanned
        )
        
        # Record GDPR compliance metrics if enabled
        if hasattr(self, 'gdpr_analyzer') and self.gdpr_analyzer:
            total_gdpr_issues = sum(
                len(file_result.metadata.get('gdpr_compliance_issues', []))
                for file_result in results.file_results
            )
            if total_gdpr_issues > 0:
                self.performance_monitor.record_operation(
                    'gdpr_compliance_scan',
                    results.scan_duration,
                    total_gdpr_issues
                )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        stats = self.performance_monitor.get_stats()
        
        # Add engine-specific stats
        stats.update({
            'circuit_breaker': {
                'ml_state': self.ml_circuit_breaker.state,
                'ml_failures': self.ml_circuit_breaker.failure_count,
                'ml_successes': self.ml_circuit_breaker.success_count
            },
            'telemetry_entries': len(self.telemetry_data),
            'streaming_enabled': self.streaming_enabled,
            'is_ci_environment': self.is_ci_environment
        })
        
        return stats
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all detection engines."""
        engines = {
            'regex_engine': {
                'enabled': True,
                'patterns': len(self.regex_engine.patterns) if self.regex_engine else 0,
                'compiled_patterns': len(self.regex_engine.compiled_patterns) if self.regex_engine else 0
            },
            'ast_analyzer': {
                'enabled': self.ast_analyzer is not None,
                'available': self.config.is_feature_enabled("ast_analysis") or getattr(self.config, 'enable_ast', False)
            },
            'dataflow_analyzer': {
                'enabled': self.dataflow_analyzer is not None,
                'available': self.config.is_feature_enabled("dataflow_analysis") or getattr(self.config, 'enable_dataflow', False)
            },
            'ml_filter': {
                'enabled': self.ml_filter is not None,
                'available': self.config.is_feature_enabled("ml_filtering") or getattr(self.config, 'enable_ml', False) or getattr(self.config, 'ml_enabled', False),
                'circuit_breaker_state': self.ml_circuit_breaker.state
            },
            'gdpr_analyzer': {
                'enabled': self.gdpr_analyzer is not None,
                'available': self.config.is_feature_enabled("gdpr_compliance") or getattr(self.config, 'enable_gdpr', False),
                'license_tier_required': 'premium'
            }
        }

        status = {
            'detection_engines': engines,
            'license': {
                'tier': self.config.license.tier.value,
                'features': self.config.license.features
            },
            'performance': {
                'memory_usage_mb': psutil.Process().memory_info().rss / 1024 / 1024,
                'uptime_seconds': time.time() - (self.start_time or time.time()),
                'streaming_enabled': self.streaming_enabled
            },
            'configuration': {
                'hot_reload_enabled': getattr(self, 'config_watch_thread', None) is not None,
                'audit_logging_enabled': getattr(self, 'audit_logger', None) is not None,
                'ci_environment': getattr(self, 'is_ci_environment', False)
            }
        }

        # Backward compatibility: expose engine sections at top-level
        status.update(engines)
        
        # Add GDPR analyzer status
        if hasattr(self, 'gdpr_analyzer'):
            status['gdpr_analyzer'] = {
                'enabled': self.gdpr_analyzer is not None,
                'available': self.config.is_feature_enabled("gdpr_compliance"),
                'patterns_loaded': len(self.gdpr_analyzer.gdpr_patterns) if self.gdpr_analyzer else 0
            }

        return status
    
    def validate_configuration(self) -> List[str]:
        """Comprehensive configuration validation."""
        errors = []
        
        # Validate regex patterns
        if self.regex_engine:
            regex_errors = self.regex_engine.validate_patterns()
            errors.extend(regex_errors)
        
        # Validate file handler
        try:
            self.file_handler.validate()
        except Exception as e:
            errors.append(f"File handler validation failed: {e}")
        
        # Validate performance settings
        try:
            self.config.validate()
        except Exception as e:
            errors.append(f"Configuration validation failed: {e}")
        
        # Validate ML model if enabled
        if self.ml_filter and self.config.is_feature_enabled("ml_filtering"):
            try:
                model_info = self.ml_filter.get_model_info()
                if not model_info.get('model_loaded', False):
                    errors.append("ML model not loaded but ML filtering is enabled")
            except Exception as e:
                errors.append(f"ML model validation failed: {e}")
        
        # Validate GDPR analyzer if enabled
        if self.gdpr_analyzer and self.config.is_feature_enabled("gdpr_compliance"):
            try:
                if not hasattr(self.gdpr_analyzer, 'gdpr_patterns') or not self.gdpr_analyzer.gdpr_patterns:
                    errors.append("GDPR analyzer patterns not loaded but GDPR compliance is enabled")
            except Exception as e:
                errors.append(f"GDPR analyzer validation failed: {e}")
        
        return errors
    
    def get_telemetry_summary(self) -> Dict[str, Any]:
        """Get comprehensive telemetry summary."""
        if not self.telemetry_data:
            return {'error': 'No telemetry data available'}
        
        # Calculate aggregates
        total_operations = len(self.telemetry_data)
        total_duration = sum(t.duration for t in self.telemetry_data)
        total_files = sum(t.file_count for t in self.telemetry_data)
        total_matches = sum(t.match_count for t in self.telemetry_data)
        
        # Group by operation
        operations = {}
        for telemetry in self.telemetry_data:
            op = telemetry.operation
            if op not in operations:
                operations[op] = {'count': 0, 'total_duration': 0, 'total_files': 0, 'total_matches': 0}
            operations[op]['count'] += 1
            operations[op]['total_duration'] += telemetry.duration
            operations[op]['total_files'] += telemetry.file_count
            operations[op]['total_matches'] += telemetry.match_count
        
        return {
            'summary': {
                'total_operations': total_operations,
                'total_duration': total_duration,
                'total_files_processed': total_files,
                'total_matches_found': total_matches,
                'average_duration_per_operation': total_duration / total_operations if total_operations > 0 else 0,
                'average_files_per_operation': total_files / total_operations if total_operations > 0 else 0
            },
            'operations': operations,
            'license_tier': self.config.license.tier.value,
            'recent_errors': [t.errors for t in self.telemetry_data[-10:] if t.errors]
        }
    
    def shutdown(self) -> None:
        """Graceful shutdown of the detection engine."""
        self.logger.info("Initiating graceful shutdown...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Wait for config watcher thread to finish
        if hasattr(self, 'config_watch_thread') and self.config_watch_thread and self.config_watch_thread.is_alive():
            self.config_watch_thread.join(timeout=5)
        
        # Clear streaming queue
        self.disable_streaming()
        
        # Log final telemetry
        self._log_telemetry("engine_shutdown", 0.0, 0, 0, ["shutdown"])
        
        self.logger.info("Detection engine shutdown complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with graceful shutdown."""
        self.shutdown()
