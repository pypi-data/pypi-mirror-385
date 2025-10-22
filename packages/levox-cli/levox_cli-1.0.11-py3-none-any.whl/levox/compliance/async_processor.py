import logging
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from queue import Queue, Empty, PriorityQueue
import json
import pickle
from concurrent.futures import ThreadPoolExecutor, Future
import asyncio
from pathlib import Path

class JobStatus(Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobPriority(Enum):
    """Job priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Job:
    """Represents an async job."""
    id: str
    name: str
    function_name: str
    args: tuple
    kwargs: dict
    priority: JobPriority
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, JobPriority):
                data[key] = value.value
            elif isinstance(value, JobStatus):
                data[key] = value.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create job from dictionary."""
        # Convert ISO strings back to datetime objects
        for key in ['created_at', 'started_at', 'completed_at']:
            if key in data and data[key]:
                data[key] = datetime.fromisoformat(data[key])
        
        # Convert enum values
        if 'priority' in data:
            data['priority'] = JobPriority(data['priority'])
        if 'status' in data:
            data['status'] = JobStatus(data['status'])
        
        return cls(**data)

class JobQueue:
    """
    Priority-based job queue with persistence and retry logic.
    """
    
    def __init__(self, max_size: int = 10000, persistence_path: Optional[str] = None):
        self.max_size = max_size
        self.persistence_path = persistence_path
        self.logger = logging.getLogger(__name__)
        
        # Priority queue (higher priority first)
        self._queue: PriorityQueue = PriorityQueue(maxsize=max_size)
        
        # Job tracking
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.RLock()
        
        # Persistence
        if persistence_path:
            self._load_jobs()
    
    def _load_jobs(self):
        """Load jobs from persistent storage."""
        try:
            path = Path(self.persistence_path)
            if path.exists():
                with open(path, 'rb') as f:
                    jobs_data = pickle.load(f)
                
                with self._lock:
                    for job_data in jobs_data:
                        job = Job.from_dict(job_data)
                        self._jobs[job.id] = job
                        
                        # Re-queue pending jobs
                        if job.status == JobStatus.PENDING:
                            self._queue.put((job.priority.value, job.created_at, job))
                
                self.logger.info(f"Loaded {len(jobs_data)} jobs from persistence")
        except Exception as e:
            self.logger.error(f"Failed to load jobs from persistence: {e}")
    
    def _save_jobs(self):
        """Save jobs to persistent storage."""
        if not self.persistence_path:
            return
        
        try:
            with self._lock:
                jobs_data = [job.to_dict() for job in self._jobs.values()]
            
            path = Path(self.persistence_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'wb') as f:
                pickle.dump(jobs_data, f)
        except Exception as e:
            self.logger.error(f"Failed to save jobs to persistence: {e}")
    
    def submit_job(self, name: str, func: Callable, *args, 
                   priority: JobPriority = JobPriority.NORMAL,
                   max_retries: int = 3,
                   timeout_seconds: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   **kwargs) -> str:
        """Submit a new job to the queue."""
        job_id = str(uuid.uuid4())
        
        job = Job(
            id=job_id,
            name=name,
            function_name=func.__name__,
            args=args,
            kwargs=kwargs,
            priority=priority,
            status=JobStatus.PENDING,
            created_at=datetime.now(),
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._jobs[job_id] = job
            
            try:
                # Add to priority queue (priority, timestamp, job)
                self._queue.put((priority.value, job.created_at, job), timeout=1)
            except:
                # Queue is full
                del self._jobs[job_id]
                raise Exception("Job queue is full")
        
        self._save_jobs()
        self.logger.info(f"Submitted job {job_id}: {name}")
        return job_id
    
    def get_next_job(self, timeout: float = 1.0) -> Optional[Job]:
        """Get the next job from the queue."""
        try:
            priority, timestamp, job = self._queue.get(timeout=timeout)
            return job
        except Empty:
            return None
    
    def mark_job_running(self, job_id: str) -> bool:
        """Mark a job as running."""
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job.status = JobStatus.RUNNING
                job.started_at = datetime.now()
                self._save_jobs()
                return True
        return False
    
    def mark_job_completed(self, job_id: str, result: Any = None) -> bool:
        """Mark a job as completed."""
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now()
                job.result = result
                self._save_jobs()
                return True
        return False
    
    def mark_job_failed(self, job_id: str, error: str) -> bool:
        """Mark a job as failed."""
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job.error = error
                job.retry_count += 1
                
                if job.retry_count < job.max_retries:
                    job.status = JobStatus.RETRYING
                    # Re-queue for retry
                    self._queue.put((job.priority.value, job.created_at, job))
                else:
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.now()
                
                self._save_jobs()
                return True
        return False
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        with self._lock:
            return self._jobs.get(job_id)
    
    def get_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """Get all jobs with a specific status."""
        with self._lock:
            return [job for job in self._jobs.values() if job.status == status]
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                if job.status == JobStatus.PENDING:
                    job.status = JobStatus.CANCELLED
                    job.completed_at = datetime.now()
                    self._save_jobs()
                    return True
        return False
    
    def cleanup_old_jobs(self, days: int = 7) -> int:
        """Remove old completed/failed jobs."""
        cutoff_date = datetime.now() - timedelta(days=days)
        removed_count = 0
        
        with self._lock:
            jobs_to_remove = []
            for job_id, job in self._jobs.items():
                if (job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED] 
                    and job.completed_at and job.completed_at < cutoff_date):
                    jobs_to_remove.append(job_id)
            
            for job_id in jobs_to_remove:
                del self._jobs[job_id]
                removed_count += 1
        
        if removed_count > 0:
            self._save_jobs()
            self.logger.info(f"Cleaned up {removed_count} old jobs")
        
        return removed_count
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with self._lock:
            status_counts = {}
            for job in self._jobs.values():
                status = job.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'total_jobs': len(self._jobs),
                'queue_size': self._queue.qsize(),
                'status_counts': status_counts,
                'max_size': self.max_size
            }

class AsyncProcessor:
    """
    High-performance async processor with job queue and worker pool.
    """
    
    def __init__(self, max_workers: int = 4, queue_max_size: int = 10000,
                 persistence_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.max_workers = max_workers
        
        # Job queue
        self.job_queue = JobQueue(queue_max_size, persistence_path)
        
        # Worker pool
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.workers: Dict[str, Future] = {}
        
        # Worker management
        self._shutdown_event = threading.Event()
        self._worker_threads: List[threading.Thread] = []
        
        # Start workers
        self._start_workers()
        
        # Cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_old_jobs, daemon=True)
        self._cleanup_thread.start()
        
        self.logger.info(f"AsyncProcessor initialized with {max_workers} workers")
    
    def _start_workers(self):
        """Start worker threads."""
        for i in range(self.max_workers):
            worker_thread = threading.Thread(
                target=self._worker_loop,
                name=f"AsyncWorker-{i}",
                daemon=True
            )
            worker_thread.start()
            self._worker_threads.append(worker_thread)
    
    def _worker_loop(self):
        """Main worker loop."""
        while not self._shutdown_event.is_set():
            try:
                # Get next job
                job = self.job_queue.get_next_job(timeout=1.0)
                if job is None:
                    continue
                
                # Mark as running
                self.job_queue.mark_job_running(job.id)
                
                # Execute job
                self._execute_job(job)
                
            except Exception as e:
                self.logger.error(f"Error in worker loop: {e}")
    
    def _execute_job(self, job: Job):
        """Execute a single job."""
        try:
            self.logger.info(f"Executing job {job.id}: {job.name}")
            
            # Import and get function
            func = self._get_function(job.function_name)
            
            # Execute with timeout if specified
            if job.timeout_seconds:
                future = self.executor.submit(func, *job.args, **job.kwargs)
                result = future.result(timeout=job.timeout_seconds)
            else:
                result = func(*job.args, **job.kwargs)
            
            # Mark as completed
            self.job_queue.mark_job_completed(job.id, result)
            self.logger.info(f"Job {job.id} completed successfully")
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Job {job.id} failed: {error_msg}")
            self.job_queue.mark_job_failed(job.id, error_msg)
    
    def _get_function(self, function_name: str) -> Callable:
        """Get function by name (simplified implementation)."""
        # In a real implementation, you'd have a registry of available functions
        # For now, we'll use a simple mapping
        function_registry = {
            'generate_evidence_package': self._generate_evidence_package,
            'calculate_trends': self._calculate_trends,
            'run_ml_analysis': self._run_ml_analysis,
            'export_data': self._export_data,
            'sync_to_cloud': self._sync_to_cloud
        }
        
        if function_name not in function_registry:
            raise ValueError(f"Unknown function: {function_name}")
        
        return function_registry[function_name]
    
    def submit_job(self, name: str, func: Callable, *args, 
                   priority: JobPriority = JobPriority.NORMAL,
                   max_retries: int = 3,
                   timeout_seconds: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   **kwargs) -> str:
        """Submit a job for async execution."""
        return self.job_queue.submit_job(
            name, func, *args,
            priority=priority,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            metadata=metadata,
            **kwargs
        )
    
    def get_job_status(self, job_id: str) -> Optional[Job]:
        """Get job status."""
        return self.job_queue.get_job(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        return self.job_queue.cancel_job(job_id)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        queue_stats = self.job_queue.get_queue_stats()
        queue_stats.update({
            'max_workers': self.max_workers,
            'active_workers': len(self.workers),
            'executor_threads': len(self.executor._threads) if hasattr(self.executor, '_threads') else 0
        })
        return queue_stats
    
    def _cleanup_old_jobs(self):
        """Background cleanup of old jobs."""
        while not self._shutdown_event.is_set():
            try:
                time.sleep(3600)  # Run every hour
                self.job_queue.cleanup_old_jobs(days=7)
            except Exception as e:
                self.logger.error(f"Error in cleanup thread: {e}")
    
    # Example job functions
    def _generate_evidence_package(self, company_id: str, format: str, **kwargs):
        """Generate evidence package (placeholder)."""
        time.sleep(2)  # Simulate work
        return f"Generated {format} package for company {company_id}"
    
    def _calculate_trends(self, company_id: str, days: int = 30, **kwargs):
        """Calculate compliance trends (placeholder)."""
        time.sleep(1)  # Simulate work
        return f"Calculated trends for company {company_id} over {days} days"
    
    def _run_ml_analysis(self, company_id: str, analysis_type: str, **kwargs):
        """Run ML analysis (placeholder)."""
        time.sleep(3)  # Simulate work
        return f"Completed {analysis_type} analysis for company {company_id}"
    
    def _export_data(self, company_id: str, format: str, **kwargs):
        """Export data (placeholder)."""
        time.sleep(1)  # Simulate work
        return f"Exported {format} data for company {company_id}"
    
    def _sync_to_cloud(self, company_id: str, data_type: str, **kwargs):
        """Sync data to cloud (placeholder)."""
        time.sleep(2)  # Simulate work
        return f"Synced {data_type} to cloud for company {company_id}"
    
    def shutdown(self, wait: bool = True):
        """Shutdown the processor."""
        self.logger.info("Shutting down AsyncProcessor")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Wait for workers to finish
        for thread in self._worker_threads:
            thread.join(timeout=5)
        
        # Shutdown executor
        self.executor.shutdown(wait=wait)
        
        self.logger.info("AsyncProcessor shutdown complete")
