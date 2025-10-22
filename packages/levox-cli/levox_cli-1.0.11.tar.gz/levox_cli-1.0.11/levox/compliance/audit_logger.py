"""
Compliance Audit Logger - Comprehensive audit trail system for GDPR compliance.

Extends existing monitoring in performance.py with compliance-specific audit trails,
cryptographic integrity verification, and safe file I/O operations.
"""

import os
import json
import hashlib
import logging
import gzip
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import threading
import time
import uuid

from ..core.config import Config, LicenseTier
from ..core.exceptions import DetectionError
from ..utils.file_handler import FileHandler
from ..utils.performance import PerformanceMonitor
from .models import ComplianceResult, ComplianceIssue, ComplianceLevel
from ..models.detection_result import DetectionResult


logger = logging.getLogger(__name__)


@dataclass
class AuditLogEntry:
    """Individual audit log entry with cryptographic integrity."""
    
    timestamp: datetime
    entry_id: str
    operation: str
    project_path: str
    compliance_score: float
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    license_tier: str
    check_duration: float
    status: str  # success, warning, error
    details: Dict[str, Any]
    previous_hash: Optional[str] = None
    current_hash: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.current_hash is None:
            self.current_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash of this entry."""
        # Create a deterministic representation for hashing
        hash_data = {
            'timestamp': self.timestamp.isoformat(),
            'entry_id': self.entry_id,
            'operation': self.operation,
            'project_path': self.project_path,
            'compliance_score': self.compliance_score,
            'total_issues': self.total_issues,
            'status': self.status,
            'previous_hash': self.previous_hash or ''
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=2)


class ComplianceAuditLogger:
    """
    Production-grade compliance audit logger with cryptographic integrity verification.
    
    Extends existing monitoring capabilities with compliance-specific audit trails,
    log rotation, compression, and cryptographic verification.
    """
    
    def __init__(self, config: Config):
        """Initialize the compliance audit logger."""
        self.config = config
        self.license_tier = config.license.tier
        
        # Initialize file handler for safe I/O operations
        self.file_handler = FileHandler(config)
        
        # Performance monitoring integration
        self.performance_monitor = PerformanceMonitor()
        
        # Audit log configuration
        self.log_dir = Path(config.log_file).parent if config.log_file else Path("logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Compliance-specific log files
        self.compliance_log_file = self.log_dir / "compliance_audit.log"
        self.compliance_json_file = self.log_dir / "compliance_audit.json"
        self.compliance_summary_file = self.log_dir / "compliance_summary.json"
        
        # Log retention settings
        self.retention_days = getattr(config, 'audit_log_retention_days', 90)
        self.max_log_size_mb = 100
        self.enable_compression = True
        self.enable_crypto_verification = self.license_tier == LicenseTier.ENTERPRISE
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Hash chain for integrity verification
        self.last_hash = None
        
        # Initialize log files
        self._initialize_log_files()
        
        logger.info("Compliance Audit Logger initialized successfully")
    
    def _initialize_log_files(self) -> None:
        """Initialize audit log files with proper headers."""
        try:
            # Create compliance audit log
            if not self.compliance_log_file.exists():
                header = f"""# Levox Compliance Audit Log
# Generated: {datetime.now().isoformat()}
# License Tier: {self.license_tier}
# Format: Timestamp | Entry ID | Operation | Project | Score | Issues | Status | Hash
# {'='*100}
"""
                self.file_handler._write_file_safe(self.compliance_log_file, header)
            
            # Create JSON audit log
            if not self.compliance_json_file.exists():
                initial_data = {
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "license_tier": self.license_tier,
                        "version": "1.0.0"
                    },
                    "audit_entries": [],
                    "hash_chain": []
                }
                self._write_json_log(initial_data)
            
            # Create compliance summary
            if not self.compliance_summary_file.exists():
                summary_data = {
                    "last_updated": datetime.now().isoformat(),
                    "total_audits": 0,
                    "compliance_trends": [],
                    "license_tier": self.license_tier
                }
                self._write_summary_file(summary_data)
                
        except Exception as e:
            logger.error(f"Failed to initialize log files: {e}")
    
    def log_compliance_audit(self, compliance_result: ComplianceResult) -> None:
        """
        Log a complete compliance audit result.
        
        Args:
            compliance_result: The compliance audit result to log
        """
        start_time = time.time()
        
        try:
            # Create audit log entry
            entry = AuditLogEntry(
                timestamp=datetime.now(),
                entry_id=f"audit_{int(time.time())}_{hash(compliance_result.project_path) % 10000}",
                operation="compliance_audit",
                project_path=compliance_result.project_path,
                compliance_score=compliance_result.compliance_score,
                total_issues=compliance_result.total_issues,
                critical_issues=compliance_result.issues_by_severity.get(ComplianceLevel.CRITICAL, 0),
                high_issues=compliance_result.issues_by_severity.get(ComplianceLevel.HIGH, 0),
                medium_issues=compliance_result.issues_by_severity.get(ComplianceLevel.MEDIUM, 0),
                low_issues=compliance_result.issues_by_severity.get(ComplianceLevel.LOW, 0),
                license_tier=self.license_tier.value,
                check_duration=compliance_result.audit_duration,
                status="success" if compliance_result.is_compliant else "warning",
                details={
                    "articles_checked": list(compliance_result.issues_by_article.keys()),
                    "categories_found": list(set(issue.category for issue in compliance_result.compliance_issues)),
                    "audit_options": asdict(compliance_result.audit_options) if hasattr(compliance_result, 'audit_options') else {}
                },
                previous_hash=self.last_hash,
                metadata={
                    "license_tier": self.license_tier.value,
                    "audit_version": "1.0.0"
                }
            )
            
            # Update hash chain
            if self.enable_crypto_verification:
                entry.previous_hash = self.last_hash
                self.last_hash = entry.current_hash
            
            # Log to different formats
            self._log_to_text_file(entry)
            self._log_to_json_file(entry)
            self._update_summary(entry)
            
            # Performance monitoring
            duration = time.time() - start_time
            self.performance_monitor.record_operation(
                "compliance_audit_logging",
                duration,
                metadata={
                    "project_path": compliance_result.project_path,
                    "total_issues": compliance_result.total_issues,
                    "compliance_score": compliance_result.compliance_score
                }
            )
            
            logger.info(f"Compliance audit logged successfully: {entry.entry_id}")
            
        except Exception as e:
            logger.error(f"Failed to log compliance audit: {e}")
            self.log_audit_error(compliance_result.project_path, str(e))
    
    def log_audit_error(self, project_path: str, error_message: str) -> None:
        """
        Log an audit error.
        
        Args:
            project_path: Path to the project that caused the error
            error_message: Description of the error
        """
        try:
            entry = AuditLogEntry(
                timestamp=datetime.now(),
                entry_id=f"error_{int(time.time())}_{hash(project_path) % 10000}",
                operation="audit_error",
                project_path=project_path,
                compliance_score=0.0,
                total_issues=0,
                critical_issues=0,
                high_issues=0,
                medium_issues=0,
                low_issues=0,
                license_tier=self.license_tier.value,
                check_duration=0.0,
                status="error",
                details={"error": error_message},
                previous_hash=self.last_hash,
                metadata={"error_type": "audit_failure"}
            )
            
            # Update hash chain
            if self.enable_crypto_verification:
                entry.previous_hash = self.last_hash
                self.last_hash = entry.current_hash
            
            # Log error
            self._log_to_text_file(entry)
            self._log_to_json_file(entry)
            
            logger.error(f"Audit error logged: {entry.entry_id}")
            
        except Exception as e:
            logger.error(f"Failed to log audit error: {e}")
    
    def _log_to_text_file(self, entry: AuditLogEntry) -> None:
        """Log entry to human-readable text file."""
        try:
            with self.lock:
                # Format: Timestamp | Entry ID | Operation | Project | Score | Issues | Status | Hash
                log_line = (
                    f"{entry.timestamp.isoformat()} | "
                    f"{entry.entry_id} | "
                    f"{entry.operation} | "
                    f"{entry.project_path} | "
                    f"{entry.compliance_score:.1f} | "
                    f"{entry.total_issues} | "
                    f"{entry.status} | "
                    f"{entry.current_hash[:16] if entry.current_hash else 'N/A'}"
                )
                
                # Append to log file
                with open(self.compliance_log_file, 'a', encoding='utf-8') as f:
                    f.write(log_line + '\n')
                
                # Check log rotation
                self._check_log_rotation()
                
        except Exception as e:
            logger.error(f"Failed to write to text log file: {e}")
    
    def _log_to_json_file(self, entry: AuditLogEntry) -> None:
        """Log entry to structured JSON file."""
        try:
            with self.lock:
                # Read existing data
                if self.compliance_json_file.exists():
                    with open(self.compliance_json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    data = {"audit_entries": [], "hash_chain": []}
                
                # Add new entry
                data["audit_entries"].append(entry.to_dict())
                
                # Add to hash chain if verification is enabled
                if self.enable_crypto_verification and entry.current_hash:
                    data["hash_chain"].append({
                        "entry_id": entry.entry_id,
                        "timestamp": entry.timestamp.isoformat(),
                        "hash": entry.current_hash,
                        "previous_hash": entry.previous_hash
                    })
                
                # Write updated data
                self._write_json_log(data)
                
        except Exception as e:
            logger.error(f"Failed to write to JSON log file: {e}")
    
    def _write_json_log(self, data: Dict[str, Any]) -> None:
        """Write data to JSON log file with atomic operation."""
        try:
            # Write to temporary file first
            temp_file = self.compliance_json_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Atomic move
            shutil.move(str(temp_file), str(self.compliance_json_file))
            
        except Exception as e:
            logger.error(f"Failed to write JSON log: {e}")
    
    def _update_summary(self, entry: AuditLogEntry) -> None:
        """Update compliance summary file."""
        try:
            with self.lock:
                # Read existing summary
                if self.compliance_summary_file.exists():
                    with open(self.compliance_summary_file, 'r', encoding='utf-8') as f:
                        summary = json.load(f)
                else:
                    summary = {
                        "last_updated": "",
                        "total_audits": 0,
                        "compliance_trends": [],
                        "license_tier": self.license_tier.value
                    }
                
                # Update summary
                summary["last_updated"] = entry.timestamp.isoformat()
                summary["total_audits"] += 1
                
                # Add trend data
                trend_entry = {
                    "timestamp": entry.timestamp.isoformat(),
                    "compliance_score": entry.compliance_score,
                    "total_issues": entry.total_issues,
                    "critical_issues": entry.critical_issues,
                    "high_issues": entry.high_issues
                }
                summary["compliance_trends"].append(trend_entry)
                
                # Keep only last 100 trend entries
                if len(summary["compliance_trends"]) > 100:
                    summary["compliance_trends"] = summary["compliance_trends"][-100:]
                
                # Write updated summary
                self._write_summary_file(summary)
                
        except Exception as e:
            logger.error(f"Failed to update summary: {e}")
    
    def _write_summary_file(self, data: Dict[str, Any]) -> None:
        """Write data to summary file with atomic operation."""
        try:
            temp_file = self.compliance_summary_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            shutil.move(str(temp_file), str(self.compliance_summary_file))
            
        except Exception as e:
            logger.error(f"Failed to write summary file: {e}")
    
    def _check_log_rotation(self) -> None:
        """Check and perform log rotation if needed."""
        try:
            if not self.compliance_log_file.exists():
                return
            
            file_size = self.compliance_log_file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size_mb > self.max_log_size_mb:
                self._rotate_log_file()
                
        except Exception as e:
            logger.error(f"Log rotation check failed: {e}")
    
    def _rotate_log_file(self) -> None:
        """Rotate the compliance log file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_file = self.compliance_log_file.with_suffix(f".{timestamp}.log")
            
            # Move current log to rotated file
            shutil.move(str(self.compliance_log_file), str(rotated_file))
            
            # Compress if enabled
            if self.enable_compression:
                compressed_file = rotated_file.with_suffix('.log.gz')
                with open(rotated_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                rotated_file.unlink()
                rotated_file = compressed_file
            
            # Create new log file with header
            header = f"""# Levox Compliance Audit Log (Rotated)
# Generated: {datetime.now().isoformat()}
# License Tier: {self.license_tier}
# Format: Timestamp | Entry ID | Operation | Project | Score | Issues | Status | Hash
# {'='*100}
"""
            with open(self.compliance_log_file, 'w', encoding='utf-8') as f:
                f.write(header)
            
            logger.info(f"Log file rotated: {rotated_file}")
            
        except Exception as e:
            logger.error(f"Log rotation failed: {e}")
    
    def cleanup_old_logs(self) -> None:
        """Clean up old log files based on retention policy."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            # Clean up rotated log files
            for log_file in self.log_dir.glob("compliance_audit.*.log*"):
                try:
                    # Try to extract timestamp from filename
                    if log_file.suffix == '.gz':
                        base_name = log_file.stem
                    else:
                        base_name = log_file.name
                    
                    # Look for timestamp pattern
                    if '_' in base_name and '.' in base_name:
                        timestamp_str = base_name.split('_')[-1].split('.')[0]
                        try:
                            file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                            if file_date < cutoff_date:
                                log_file.unlink()
                                logger.info(f"Removed old log file: {log_file}")
                        except ValueError:
                            # Skip files with unrecognized timestamp format
                            continue
                            
                except Exception as e:
                    logger.warning(f"Failed to process log file {log_file}: {e}")
                    continue
            
            logger.info("Log cleanup completed")
            
        except Exception as e:
            logger.error(f"Log cleanup failed: {e}")
    
    def get_audit_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get audit history for the specified number of days."""
        try:
            if not self.compliance_json_file.exists():
                return []
            
            with open(self.compliance_json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter entries by date
            recent_entries = []
            for entry in data.get("audit_entries", []):
                try:
                    entry_date = datetime.fromisoformat(entry["timestamp"])
                    if entry_date >= cutoff_date:
                        recent_entries.append(entry)
                except ValueError:
                    continue
            
            return recent_entries
            
        except Exception as e:
            logger.error(f"Failed to get audit history: {e}")
            return []
    
    def verify_log_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of the audit log hash chain."""
        if not self.enable_crypto_verification:
            return {"status": "disabled", "message": "Cryptographic verification not enabled for this license tier"}
        
        try:
            if not self.compliance_json_file.exists():
                return {"status": "error", "message": "No audit log file found"}
            
            with open(self.compliance_json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            hash_chain = data.get("hash_chain", [])
            if not hash_chain:
                return {"status": "warning", "message": "No hash chain found"}
            
            # Verify hash chain
            verification_results = []
            previous_hash = None
            
            for entry in hash_chain:
                if previous_hash and entry.get("previous_hash") != previous_hash:
                    verification_results.append({
                        "entry_id": entry["entry_id"],
                        "status": "broken_chain",
                        "expected": previous_hash,
                        "actual": entry.get("previous_hash")
                    })
                else:
                    verification_results.append({
                        "entry_id": entry["entry_id"],
                        "status": "valid"
                    })
                
                previous_hash = entry.get("hash")
            
            broken_links = [r for r in verification_results if r["status"] == "broken_chain"]
            
            return {
                "status": "success" if not broken_links else "broken",
                "total_entries": len(hash_chain),
                "broken_links": len(broken_links),
                "verification_results": verification_results,
                "last_hash": previous_hash
            }
            
        except Exception as e:
            logger.error(f"Log integrity verification failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def export_audit_log(self, output_path: str, format: str = "json") -> bool:
        """
        Export audit log to specified format and location.
        
        Args:
            output_path: Path to export the log
            format: Export format (json, csv, text)
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            if not self.compliance_json_file.exists():
                logger.error("No audit log file to export")
                return False
            
            with open(self.compliance_json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
            
            elif format.lower() == "csv":
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Write header
                    writer.writerow([
                        "Timestamp", "Entry ID", "Operation", "Project Path", 
                        "Compliance Score", "Total Issues", "Status"
                    ])
                    # Write data
                    for entry in data.get("audit_entries", []):
                        writer.writerow([
                            entry.get("timestamp", ""),
                            entry.get("entry_id", ""),
                            entry.get("operation", ""),
                            entry.get("project_path", ""),
                            entry.get("compliance_score", ""),
                            entry.get("total_issues", ""),
                            entry.get("status", "")
                        ])
            
            elif format.lower() == "text":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("Levox Compliance Audit Log Export\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for entry in data.get("audit_entries", []):
                        f.write(f"Entry ID: {entry.get('entry_id', 'N/A')}\n")
                        f.write(f"Timestamp: {entry.get('timestamp', 'N/A')}\n")
                        f.write(f"Project: {entry.get('project_path', 'N/A')}\n")
                        f.write(f"Score: {entry.get('compliance_score', 'N/A')}\n")
                        f.write(f"Issues: {entry.get('total_issues', 'N/A')}\n")
                        f.write(f"Status: {entry.get('status', 'N/A')}\n")
                        f.write("-" * 30 + "\n")
            
            logger.info(f"Audit log exported successfully to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export audit log: {e}")
            return False
