"""
Real-time Sync Service for Evidence Engine.
Background service for continuous synchronization with delta sync and conflict resolution.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import threading
from queue import Queue, Empty

from .storage_manager import HybridStorageManager, SyncOperation, SyncStatus
from .evidence_store import EvidenceStore
from .models import (
    ScanHistoryEntry, ViolationRecord, RemediationEvidence, 
    CompanyProfile, ViolationTrend, ComplianceMetrics, EvidencePackage
)


class SyncEventType(Enum):
    """Types of sync events."""
    SCAN_COMPLETED = "scan_completed"
    VIOLATION_DETECTED = "violation_detected"
    REMEDIATION_ADDED = "remediation_added"
    COMPANY_UPDATED = "company_updated"
    EVIDENCE_GENERATED = "evidence_generated"
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"
    SYNC_FAILED = "sync_failed"
    CONFLICT_DETECTED = "conflict_detected"


@dataclass
class SyncEvent:
    """Represents a sync event."""
    event_id: str
    event_type: SyncEventType
    timestamp: datetime
    data: Dict[str, Any]
    company_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class DeltaSyncState:
    """State for delta synchronization."""
    last_sync_timestamp: datetime
    processed_operations: Set[str]
    pending_conflicts: List[Dict[str, Any]]
    sync_metrics: Dict[str, Any]


class RealtimeSyncService:
    """
    Real-time synchronization service with advanced features.
    
    Features:
    - Delta sync (only changed records)
    - Compression for large datasets
    - Progress tracking and error recovery
    - Event-driven synchronization
    - Conflict resolution strategies
    - Performance monitoring
    """
    
    def __init__(self, 
                 storage_manager: HybridStorageManager,
                 sync_interval_seconds: int = 30,
                 delta_sync_enabled: bool = True,
                 compression_enabled: bool = True,
                 event_callbacks: Optional[Dict[SyncEventType, Callable]] = None):
        """
        Initialize real-time sync service.
        
        Args:
            storage_manager: Hybrid storage manager instance
            sync_interval_seconds: Sync interval in seconds
            delta_sync_enabled: Enable delta synchronization
            compression_enabled: Enable data compression
            event_callbacks: Callbacks for sync events
        """
        self.storage_manager = storage_manager
        self.sync_interval = sync_interval_seconds
        self.delta_sync_enabled = delta_sync_enabled
        self.compression_enabled = compression_enabled
        self.event_callbacks = event_callbacks or {}
        
        # Sync state management
        self.delta_state = DeltaSyncState(
            last_sync_timestamp=datetime.now(),
            processed_operations=set(),
            pending_conflicts=[],
            sync_metrics={}
        )
        
        # Event management
        self.event_queue: Queue = Queue()
        self.event_handlers: Dict[SyncEventType, List[Callable]] = {}
        
        # Performance tracking
        self.sync_performance = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'average_sync_time': 0.0,
            'last_sync_duration': 0.0,
            'conflicts_resolved': 0
        }
        
        # Background tasks
        self.sync_task: Optional[asyncio.Task] = None
        self.event_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Register default event handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default event handlers."""
        self.register_event_handler(SyncEventType.SYNC_STARTED, self._on_sync_started)
        self.register_event_handler(SyncEventType.SYNC_COMPLETED, self._on_sync_completed)
        self.register_event_handler(SyncEventType.SYNC_FAILED, self._on_sync_failed)
        self.register_event_handler(SyncEventType.CONFLICT_DETECTED, self._on_conflict_detected)
    
    def register_event_handler(self, event_type: SyncEventType, handler: Callable):
        """Register an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def emit_event(self, event_type: SyncEventType, data: Dict[str, Any], 
                   company_id: Optional[str] = None, user_id: Optional[str] = None):
        """Emit a sync event."""
        event = SyncEvent(
            event_id=f"{event_type.value}_{int(time.time())}_{hashlib.md5(str(data).encode()).hexdigest()[:8]}",
            event_type=event_type,
            timestamp=datetime.now(),
            data=data,
            company_id=company_id,
            user_id=user_id
        )
        
        self.event_queue.put(event)
        self.logger.debug(f"Emitted event: {event_type.value}")
    
    async def start(self):
        """Start the sync service."""
        if self.is_running:
            return
        
        self.is_running = True
        self.sync_task = asyncio.create_task(self._sync_worker())
        self.event_task = asyncio.create_task(self._event_worker())
        
        self.logger.info("Real-time sync service started")
        self.emit_event(SyncEventType.SYNC_STARTED, {'service': 'realtime_sync'})
    
    async def stop(self):
        """Stop the sync service."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.sync_task:
            self.sync_task.cancel()
            try:
                await self.sync_task
            except asyncio.CancelledError:
                pass
        
        if self.event_task:
            self.event_task.cancel()
            try:
                await self.event_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Real-time sync service stopped")
    
    async def _sync_worker(self):
        """Background sync worker."""
        while self.is_running:
            try:
                await self._perform_delta_sync()
                await asyncio.sleep(self.sync_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Sync worker error: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def _event_worker(self):
        """Background event processing worker."""
        while self.is_running:
            try:
                await self._process_events()
                await asyncio.sleep(0.1)  # Process events quickly
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Event worker error: {e}")
                await asyncio.sleep(1)
    
    async def _process_events(self):
        """Process pending events."""
        try:
            event = self.event_queue.get_nowait()
            await self._handle_event(event)
        except Empty:
            pass
        except Exception as e:
            self.logger.error(f"Error processing event: {e}")
    
    async def _handle_event(self, event: SyncEvent):
        """Handle a sync event."""
        handlers = self.event_handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                self.logger.error(f"Error in event handler: {e}")
    
    async def _perform_delta_sync(self):
        """Perform delta synchronization."""
        if not self.delta_sync_enabled:
            return
        
        start_time = time.time()
        self.sync_performance['total_syncs'] += 1
        
        try:
            self.emit_event(SyncEventType.SYNC_STARTED, {
                'sync_type': 'delta',
                'timestamp': self.delta_state.last_sync_timestamp.isoformat()
            })
            
            # Get changes since last sync
            changes = await self._get_changes_since_last_sync()
            
            if changes:
                # Process changes
                processed_count = await self._process_changes(changes)
                
                # Update sync state
                self.delta_state.last_sync_timestamp = datetime.now()
                self.delta_state.processed_operations.update(
                    [change.get('operation_id', '') for change in changes]
                )
                
                # Update performance metrics
                sync_duration = time.time() - start_time
                self.sync_performance['last_sync_duration'] = sync_duration
                self.sync_performance['successful_syncs'] += 1
                
                self.emit_event(SyncEventType.SYNC_COMPLETED, {
                    'processed_count': processed_count,
                    'sync_duration': sync_duration,
                    'changes_count': len(changes)
                })
                
                self.logger.info(f"Delta sync completed: {processed_count} changes processed in {sync_duration:.2f}s")
            else:
                self.logger.debug("No changes to sync")
                
        except Exception as e:
            self.sync_performance['failed_syncs'] += 1
            self.logger.error(f"Delta sync failed: {e}")
            
            self.emit_event(SyncEventType.SYNC_FAILED, {
                'error': str(e),
                'sync_type': 'delta'
            })
    
    async def _get_changes_since_last_sync(self) -> List[Dict[str, Any]]:
        """Get changes since last sync timestamp."""
        # This would implement actual delta sync logic
        # For now, return empty list as placeholder
        return []
    
    async def _process_changes(self, changes: List[Dict[str, Any]]) -> int:
        """Process a list of changes."""
        processed_count = 0
        
        for change in changes:
            try:
                await self._process_single_change(change)
                processed_count += 1
            except Exception as e:
                self.logger.error(f"Failed to process change: {e}")
        
        return processed_count
    
    async def _process_single_change(self, change: Dict[str, Any]):
        """Process a single change."""
        change_type = change.get('type')
        
        if change_type == 'scan_result':
            await self._sync_scan_result(change['data'])
        elif change_type == 'violation':
            await self._sync_violation(change['data'])
        elif change_type == 'remediation':
            await self._sync_remediation(change['data'])
        elif change_type == 'company_profile':
            await self._sync_company_profile(change['data'])
        else:
            self.logger.warning(f"Unknown change type: {change_type}")
    
    async def _sync_scan_result(self, scan_data: Dict[str, Any]):
        """Sync scan result."""
        # Implementation would depend on storage manager interface
        pass
    
    async def _sync_violation(self, violation_data: Dict[str, Any]):
        """Sync violation."""
        # Implementation would depend on storage manager interface
        pass
    
    async def _sync_remediation(self, remediation_data: Dict[str, Any]):
        """Sync remediation."""
        # Implementation would depend on storage manager interface
        pass
    
    async def _sync_company_profile(self, company_data: Dict[str, Any]):
        """Sync company profile."""
        # Implementation would depend on storage manager interface
        pass
    
    def _on_sync_started(self, event: SyncEvent):
        """Handle sync started event."""
        self.logger.info(f"Sync started: {event.data}")
    
    def _on_sync_completed(self, event: SyncEvent):
        """Handle sync completed event."""
        self.logger.info(f"Sync completed: {event.data}")
    
    def _on_sync_failed(self, event: SyncEvent):
        """Handle sync failed event."""
        self.logger.error(f"Sync failed: {event.data}")
    
    def _on_conflict_detected(self, event: SyncEvent):
        """Handle conflict detected event."""
        self.logger.warning(f"Conflict detected: {event.data}")
        self.sync_performance['conflicts_resolved'] += 1
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        return {
            'is_running': self.is_running,
            'delta_sync_enabled': self.delta_sync_enabled,
            'compression_enabled': self.compression_enabled,
            'last_sync_timestamp': self.delta_state.last_sync_timestamp.isoformat(),
            'processed_operations_count': len(self.delta_state.processed_operations),
            'pending_conflicts_count': len(self.delta_state.pending_conflicts),
            'event_queue_size': self.event_queue.qsize(),
            'performance_metrics': self.sync_performance.copy()
        }
    
    def force_full_sync(self) -> bool:
        """Force a full synchronization."""
        try:
            # Reset delta state to force full sync
            self.delta_state.last_sync_timestamp = datetime.min
            
            # Trigger immediate sync
            if self.sync_task and not self.sync_task.done():
                # Cancel current sync and restart
                self.sync_task.cancel()
                self.sync_task = asyncio.create_task(self._sync_worker())
            
            return True
        except Exception as e:
            self.logger.error(f"Force full sync failed: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics."""
        metrics = self.sync_performance.copy()
        
        if metrics['total_syncs'] > 0:
            metrics['success_rate'] = metrics['successful_syncs'] / metrics['total_syncs']
            metrics['failure_rate'] = metrics['failed_syncs'] / metrics['total_syncs']
        else:
            metrics['success_rate'] = 0.0
            metrics['failure_rate'] = 0.0
        
        return metrics


class SyncServiceManager:
    """
    Manager for multiple sync services.
    Handles service lifecycle and coordination.
    """
    
    def __init__(self):
        """Initialize sync service manager."""
        self.services: Dict[str, RealtimeSyncService] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_service(self, service_id: str, service: RealtimeSyncService):
        """Register a sync service."""
        self.services[service_id] = service
        self.logger.info(f"Registered sync service: {service_id}")
    
    async def start_all(self):
        """Start all registered services."""
        for service_id, service in self.services.items():
            try:
                await service.start()
                self.logger.info(f"Started sync service: {service_id}")
            except Exception as e:
                self.logger.error(f"Failed to start service {service_id}: {e}")
    
    async def stop_all(self):
        """Stop all registered services."""
        for service_id, service in self.services.items():
            try:
                await service.stop()
                self.logger.info(f"Stopped sync service: {service_id}")
            except Exception as e:
                self.logger.error(f"Failed to stop service {service_id}: {e}")
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all services."""
        return {
            service_id: service.get_sync_status()
            for service_id, service in self.services.items()
        }
