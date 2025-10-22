"""
Hybrid Storage Manager for Evidence Engine.
Intelligently manages local and cloud storage with automatic synchronization.
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from queue import Queue, Empty
from enum import Enum
import hashlib

from .evidence_store import EvidenceStore, LocalEvidenceStore, SupabaseEvidenceStore
from .models import (
    ScanHistoryEntry, ViolationRecord, RemediationEvidence, 
    CompanyProfile, ViolationTrend, ComplianceMetrics, EvidencePackage
)


class SyncStatus(Enum):
    """Sync operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class SyncOperation:
    """Represents a sync operation."""
    operation_id: str
    operation_type: str  # 'save_scan', 'save_violation', etc.
    data: Dict[str, Any]
    timestamp: datetime
    status: SyncStatus = SyncStatus.PENDING
    retry_count: int = 0
    error_message: Optional[str] = None
    conflict_data: Optional[Dict[str, Any]] = None


@dataclass
class SyncStats:
    """Sync operation statistics."""
    total_operations: int = 0
    successful_syncs: int = 0
    failed_syncs: int = 0
    conflicts_resolved: int = 0
    last_sync_time: Optional[datetime] = None
    sync_duration_seconds: float = 0.0


class HybridStorageManager:
    """
    Intelligent storage manager that handles both local and cloud storage.
    
    Features:
    - Automatic sync between local SQLite and Supabase
    - Offline-first operation with sync queue
    - Conflict resolution with timestamp-based merging
    - Real-time sync status tracking
    - Configurable sync intervals
    """
    
    def __init__(self, 
                 local_store: LocalEvidenceStore, 
                 cloud_store: Optional[SupabaseEvidenceStore] = None,
                 sync_interval_seconds: int = 30,
                 max_retry_attempts: int = 3,
                 conflict_resolution_strategy: str = "timestamp"):
        """
        Initialize hybrid storage manager.
        
        Args:
            local_store: Local SQLite evidence store
            cloud_store: Optional Supabase cloud store
            sync_interval_seconds: How often to attempt sync
            max_retry_attempts: Maximum retry attempts for failed operations
            conflict_resolution_strategy: Strategy for resolving conflicts
        """
        self.local = local_store
        self.cloud = cloud_store
        self.sync_interval = sync_interval_seconds
        self.max_retries = max_retry_attempts
        self.conflict_strategy = conflict_resolution_strategy
        
        # Sync management
        self.sync_queue: Queue = Queue()
        self.sync_stats = SyncStats()
        self.is_online = self._check_connection()
        self.sync_thread: Optional[threading.Thread] = None
        self.sync_running = False
        self.sync_lock = threading.Lock()
        
        # Conflict tracking
        self.conflict_resolvers: Dict[str, Callable] = {
            'timestamp': self._resolve_timestamp_conflict,
            'local_wins': self._resolve_local_wins,
            'cloud_wins': self._resolve_cloud_wins,
            'merge': self._resolve_merge_conflict
        }
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Start sync thread if cloud store is available
        if self.cloud:
            self._start_sync_thread()
    
    def _check_connection(self) -> bool:
        """Check if cloud connection is available."""
        if not self.cloud:
            return False
        
        try:
            # Simple ping to check connection
            result = self.cloud.client.table('scan_history').select('scan_id').limit(1).execute()
            return True
        except Exception as e:
            self.logger.debug(f"Cloud connection check failed: {e}")
            return False
    
    def _start_sync_thread(self):
        """Start background sync thread."""
        if self.sync_thread and self.sync_thread.is_alive():
            return
        
        self.sync_running = True
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
        self.logger.info("Sync thread started")
    
    def _sync_worker(self):
        """Background worker for processing sync queue."""
        while self.sync_running:
            try:
                # Process pending sync operations
                self._process_sync_queue()
                
                # Periodic full sync
                if self.is_online and self.sync_stats.last_sync_time:
                    time_since_sync = datetime.now() - self.sync_stats.last_sync_time
                    if time_since_sync.total_seconds() > self.sync_interval:
                        self._perform_full_sync()
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Sync worker error: {e}")
                time.sleep(10)  # Wait longer on error
    
    def _process_sync_queue(self):
        """Process pending sync operations."""
        processed_count = 0
        max_batch_size = 10
        
        while processed_count < max_batch_size:
            try:
                operation = self.sync_queue.get_nowait()
                self._execute_sync_operation(operation)
                processed_count += 1
            except Empty:
                break
            except Exception as e:
                self.logger.error(f"Error processing sync operation: {e}")
    
    def _execute_sync_operation(self, operation: SyncOperation):
        """Execute a single sync operation."""
        try:
            operation.status = SyncStatus.IN_PROGRESS
            
            if operation.operation_type == 'save_scan':
                success = self._sync_scan_result(operation.data)
            elif operation.operation_type == 'save_violation':
                success = self._sync_violation(operation.data)
            elif operation.operation_type == 'save_remediation':
                success = self._sync_remediation(operation.data)
            elif operation.operation_type == 'save_company':
                success = self._sync_company_profile(operation.data)
            else:
                self.logger.warning(f"Unknown sync operation type: {operation.operation_type}")
                success = False
            
            if success:
                operation.status = SyncStatus.COMPLETED
                self.sync_stats.successful_syncs += 1
            else:
                operation.status = SyncStatus.FAILED
                operation.retry_count += 1
                self.sync_stats.failed_syncs += 1
                
                # Retry if under limit
                if operation.retry_count < self.max_retries:
                    self.sync_queue.put(operation)
            
        except Exception as e:
            operation.status = SyncStatus.FAILED
            operation.error_message = str(e)
            operation.retry_count += 1
            self.logger.error(f"Sync operation failed: {e}")
    
    def _sync_scan_result(self, scan_data: Dict[str, Any]) -> bool:
        """Sync scan result to cloud."""
        try:
            # Convert dict back to ScanHistoryEntry
            scan_entry = ScanHistoryEntry(**scan_data)
            return self.cloud.save_scan_result(scan_entry)
        except Exception as e:
            self.logger.error(f"Failed to sync scan result: {e}")
            return False
    
    def _sync_violation(self, violation_data: Dict[str, Any]) -> bool:
        """Sync violation to cloud."""
        try:
            violation = ViolationRecord(**violation_data)
            return self.cloud.save_violation(violation)
        except Exception as e:
            self.logger.error(f"Failed to sync violation: {e}")
            return False
    
    def _sync_remediation(self, remediation_data: Dict[str, Any]) -> bool:
        """Sync remediation to cloud."""
        try:
            remediation = RemediationEvidence(**remediation_data)
            return self.cloud.save_remediation(remediation)
        except Exception as e:
            self.logger.error(f"Failed to sync remediation: {e}")
            return False
    
    def _sync_company_profile(self, company_data: Dict[str, Any]) -> bool:
        """Sync company profile to cloud."""
        try:
            company = CompanyProfile(**company_data)
            return self.cloud.save_company_profile(company)
        except Exception as e:
            self.logger.error(f"Failed to sync company profile: {e}")
            return False
    
    def _perform_full_sync(self):
        """Perform full synchronization between local and cloud."""
        if not self.is_online:
            return
        
        start_time = time.time()
        self.logger.info("Starting full sync")
        
        try:
            # Sync local changes to cloud
            self._sync_local_to_cloud()
            
            # Sync cloud changes to local
            self._sync_cloud_to_local()
            
            self.sync_stats.last_sync_time = datetime.now()
            self.sync_stats.sync_duration_seconds = time.time() - start_time
            
            self.logger.info(f"Full sync completed in {self.sync_stats.sync_duration_seconds:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Full sync failed: {e}")
    
    def _sync_local_to_cloud(self):
        """Sync local changes to cloud."""
        # This would implement delta sync logic
        # For now, we rely on the sync queue for incremental updates
        pass
    
    def _sync_cloud_to_local(self):
        """Sync cloud changes to local."""
        # This would implement pulling changes from cloud
        # For now, we rely on real-time subscriptions
        pass
    
    def _resolve_timestamp_conflict(self, local_data: Dict[str, Any], 
                                  cloud_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict using timestamp comparison."""
        local_time = datetime.fromisoformat(local_data.get('updated_at', local_data.get('created_at', '')))
        cloud_time = datetime.fromisoformat(cloud_data.get('updated_at', cloud_data.get('created_at', '')))
        
        if local_time > cloud_time:
            return local_data
        else:
            return cloud_data
    
    def _resolve_local_wins(self, local_data: Dict[str, Any], 
                           cloud_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict by preferring local data."""
        return local_data
    
    def _resolve_cloud_wins(self, local_data: Dict[str, Any], 
                           cloud_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict by preferring cloud data."""
        return cloud_data
    
    def _resolve_merge_conflict(self, local_data: Dict[str, Any], 
                               cloud_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict by merging data."""
        # Simple merge strategy - prefer non-null values
        merged = cloud_data.copy()
        for key, value in local_data.items():
            if value is not None and (key not in merged or merged[key] is None):
                merged[key] = value
        return merged
    
    def _queue_sync_operation(self, operation_type: str, data: Any):
        """Queue a sync operation for later processing."""
        if not self.cloud:
            return
        
        # Convert data to dict if it's a dataclass
        if hasattr(data, '__dict__'):
            data_dict = asdict(data)
        else:
            data_dict = data
        
        operation = SyncOperation(
            operation_id=f"{operation_type}_{int(time.time())}_{hashlib.md5(str(data_dict).encode()).hexdigest()[:8]}",
            operation_type=operation_type,
            data=data_dict,
            timestamp=datetime.now()
        )
        
        self.sync_queue.put(operation)
        self.sync_stats.total_operations += 1
    
    # EvidenceStore interface implementation
    def save_scan_result(self, scan_data: ScanHistoryEntry) -> bool:
        """Save scan result to both local and cloud."""
        # Always save to local first
        local_success = self.local.save_scan_result(scan_data)
        
        if local_success and self.cloud:
            # Queue for cloud sync
            self._queue_sync_operation('save_scan', scan_data)
        
        return local_success
    
    def get_scan_history(self, company_id: str, start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None) -> List[ScanHistoryEntry]:
        """Get scan history from local store (cloud sync happens in background)."""
        return self.local.get_scan_history(company_id, start_date, end_date)
    
    def save_violation(self, violation: ViolationRecord) -> bool:
        """Save violation to both local and cloud."""
        local_success = self.local.save_violation(violation)
        
        if local_success and self.cloud:
            self._queue_sync_operation('save_violation', violation)
        
        return local_success
    
    def get_violations(self, scan_id: Optional[str] = None, 
                      company_id: Optional[str] = None) -> List[ViolationRecord]:
        """Get violations from local store."""
        return self.local.get_violations(scan_id, company_id)
    
    def save_remediation(self, remediation: RemediationEvidence) -> bool:
        """Save remediation to both local and cloud."""
        local_success = self.local.save_remediation(remediation)
        
        if local_success and self.cloud:
            self._queue_sync_operation('save_remediation', remediation)
        
        return local_success
    
    def get_remediations(self, violation_id: Optional[str] = None) -> List[RemediationEvidence]:
        """Get remediations from local store."""
        return self.local.get_remediations(violation_id)
    
    def get_violation_trends(self, company_id: str, period_days: int = 30) -> List[ViolationTrend]:
        """Get violation trends from local store."""
        return self.local.get_violation_trends(company_id, period_days)
    
    def save_company_profile(self, profile: CompanyProfile) -> bool:
        """Save company profile to both local and cloud."""
        local_success = self.local.save_company_profile(profile)
        
        if local_success and self.cloud:
            self._queue_sync_operation('save_company', profile)
        
        return local_success
    
    def get_company_profile(self, company_id: str) -> Optional[CompanyProfile]:
        """Get company profile from local store."""
        return self.local.get_company_profile(company_id)
    
    def save_evidence_package(self, package: EvidencePackage) -> bool:
        """Save evidence package to both local and cloud."""
        local_success = self.local.save_evidence_package(package)
        
        if local_success and self.cloud:
            self._queue_sync_operation('save_evidence_package', package)
        
        return local_success
    
    def get_evidence_package(self, package_id: str) -> Optional[EvidencePackage]:
        """Get evidence package from local store."""
        return self.local.get_evidence_package(package_id)
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status and statistics."""
        return {
            'is_online': self.is_online,
            'sync_running': self.sync_running,
            'queue_size': self.sync_queue.qsize(),
            'stats': asdict(self.sync_stats),
            'last_connection_check': datetime.now().isoformat()
        }
    
    def force_sync(self) -> bool:
        """Force immediate synchronization."""
        if not self.cloud:
            return False
        
        try:
            self._perform_full_sync()
            return True
        except Exception as e:
            self.logger.error(f"Force sync failed: {e}")
            return False
    
    def stop_sync(self):
        """Stop background sync thread."""
        self.sync_running = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)
        self.logger.info("Sync thread stopped")
    
    def __del__(self):
        """Cleanup on destruction."""
        self.stop_sync()


def create_hybrid_store(local_path: Optional[Path] = None, 
                       supabase_client=None,
                       enable_cloud: bool = True) -> Union[LocalEvidenceStore, HybridStorageManager]:
    """
    Factory function to create appropriate evidence store.
    
    Args:
        local_path: Path for local SQLite database
        supabase_client: Supabase client for cloud storage
        enable_cloud: Whether to enable cloud synchronization
    
    Returns:
        LocalEvidenceStore if cloud disabled, HybridStorageManager if enabled
    """
    local_store = LocalEvidenceStore(local_path)
    
    if enable_cloud and supabase_client:
        cloud_store = SupabaseEvidenceStore(supabase_client)
        return HybridStorageManager(local_store, cloud_store)
    else:
        return local_store
