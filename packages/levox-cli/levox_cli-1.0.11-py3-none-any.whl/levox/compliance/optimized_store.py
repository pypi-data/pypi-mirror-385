import logging
import sqlite3
import threading
import time
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from contextlib import contextmanager
from queue import Queue, Empty
from dataclasses import dataclass
import json
import gzip
import pickle
from pathlib import Path

from .models import ScanHistoryEntry, ViolationRecord, RemediationEvidence, CompanyProfile, EvidencePackage

@dataclass
class ConnectionPoolConfig:
    """Configuration for database connection pool."""
    min_connections: int = 2
    max_connections: int = 10
    connection_timeout: int = 30
    idle_timeout: int = 300
    check_interval: int = 60

@dataclass
class QueryStats:
    """Statistics for query performance monitoring."""
    query_type: str
    execution_time: float
    rows_affected: int
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

class OptimizedConnectionPool:
    """
    High-performance SQLite connection pool with prepared statements,
    batch operations, and performance monitoring.
    """
    
    def __init__(self, db_path: str, config: ConnectionPoolConfig = None):
        self.db_path = db_path
        self.config = config or ConnectionPoolConfig()
        self.logger = logging.getLogger(__name__)
        
        # Connection pool
        self._pool: Queue = Queue(maxsize=self.config.max_connections)
        self._active_connections: Dict[int, sqlite3.Connection] = {}
        self._connection_counter = 0
        self._lock = threading.RLock()
        
        # Prepared statements cache
        self._prepared_statements: Dict[str, str] = {}
        
        # Performance monitoring
        self._query_stats: List[QueryStats] = []
        self._stats_lock = threading.Lock()
        
        # Initialize pool
        self._initialize_pool()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_idle_connections, daemon=True)
        self._cleanup_thread.start()
        
        self.logger.info(f"Initialized connection pool for {db_path} with {self.config.max_connections} max connections")
    
    def _initialize_pool(self):
        """Initialize the connection pool with minimum connections."""
        for _ in range(self.config.min_connections):
            conn = self._create_connection()
            self._pool.put(conn)
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with optimizations."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.config.connection_timeout,
            check_same_thread=False
        )
        
        # Enable optimizations
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=268435456")  # 256MB
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys=ON")
        
        # Set row factory for named tuples
        conn.row_factory = sqlite3.Row
        
        return conn
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool with automatic cleanup."""
        conn_id = None
        conn = None
        
        try:
            # Try to get connection from pool
            try:
                conn = self._pool.get(timeout=5)
            except Empty:
                # Create new connection if pool is empty and under limit
                with self._lock:
                    if len(self._active_connections) < self.config.max_connections:
                        conn = self._create_connection()
                        conn_id = self._connection_counter
                        self._connection_counter += 1
                        self._active_connections[conn_id] = conn
                    else:
                        raise Exception("Connection pool exhausted")
            
            yield conn
            
        finally:
            if conn:
                if conn_id:
                    # Remove from active connections
                    with self._lock:
                        self._active_connections.pop(conn_id, None)
                else:
                    # Return to pool
                    try:
                        self._pool.put_nowait(conn)
                    except:
                        conn.close()
    
    def _cleanup_idle_connections(self):
        """Background thread to cleanup idle connections."""
        while True:
            try:
                time.sleep(self.config.check_interval)
                
                with self._lock:
                    current_time = time.time()
                    idle_connections = []
                    
                    for conn_id, conn in list(self._active_connections.items()):
                        # Check if connection is idle (simplified check)
                        if current_time - getattr(conn, '_last_used', current_time) > self.config.idle_timeout:
                            idle_connections.append(conn_id)
                    
                    for conn_id in idle_connections:
                        conn = self._active_connections.pop(conn_id, None)
                        if conn:
                            conn.close()
                            
            except Exception as e:
                self.logger.error(f"Error in cleanup thread: {e}")
    
    def execute_query(self, query: str, params: Tuple = (), fetch: bool = False) -> Any:
        """Execute a query with performance monitoring."""
        start_time = time.time()
        success = True
        error_message = None
        rows_affected = 0
        
        try:
            with self.get_connection() as conn:
                conn._last_used = time.time()
                
                if fetch:
                    cursor = conn.execute(query, params)
                    result = cursor.fetchall()
                    rows_affected = len(result)
                    return result
                else:
                    cursor = conn.execute(query, params)
                    conn.commit()
                    rows_affected = cursor.rowcount
                    return cursor.rowcount
                    
        except Exception as e:
            success = False
            error_message = str(e)
            self.logger.error(f"Query execution failed: {e}")
            raise
        finally:
            # Record performance stats
            execution_time = time.time() - start_time
            query_type = query.split()[0].upper()
            
            with self._stats_lock:
                self._query_stats.append(QueryStats(
                    query_type=query_type,
                    execution_time=execution_time,
                    rows_affected=rows_affected,
                    timestamp=datetime.now(),
                    success=success,
                    error_message=error_message
                ))
                
                # Keep only last 1000 stats
                if len(self._query_stats) > 1000:
                    self._query_stats = self._query_stats[-1000:]
    
    def execute_batch(self, queries: List[Tuple[str, Tuple]]) -> List[Any]:
        """Execute multiple queries in a single transaction for better performance."""
        start_time = time.time()
        results = []
        
        try:
            with self.get_connection() as conn:
                conn._last_used = time.time()
                
                # Begin transaction
                conn.execute("BEGIN TRANSACTION")
                
                try:
                    for query, params in queries:
                        cursor = conn.execute(query, params)
                        results.append(cursor.rowcount)
                    
                    # Commit transaction
                    conn.commit()
                    
                except Exception as e:
                    # Rollback on error
                    conn.rollback()
                    raise
                    
        except Exception as e:
            self.logger.error(f"Batch execution failed: {e}")
            raise
        finally:
            execution_time = time.time() - start_time
            self.logger.debug(f"Batch execution completed in {execution_time:.3f}s")
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring."""
        with self._stats_lock:
            if not self._query_stats:
                return {}
            
            recent_stats = [s for s in self._query_stats 
                          if (datetime.now() - s.timestamp).total_seconds() < 3600]  # Last hour
            
            if not recent_stats:
                return {}
            
            # Calculate statistics
            total_queries = len(recent_stats)
            successful_queries = len([s for s in recent_stats if s.success])
            avg_execution_time = sum(s.execution_time for s in recent_stats) / total_queries
            
            query_types = {}
            for stat in recent_stats:
                query_type = stat.query_type
                if query_type not in query_types:
                    query_types[query_type] = {'count': 0, 'avg_time': 0, 'total_time': 0}
                query_types[query_type]['count'] += 1
                query_types[query_type]['total_time'] += stat.execution_time
            
            for query_type in query_types:
                query_types[query_type]['avg_time'] = (
                    query_types[query_type]['total_time'] / query_types[query_type]['count']
                )
            
            return {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': successful_queries / total_queries if total_queries > 0 else 0,
                'avg_execution_time': avg_execution_time,
                'query_types': query_types,
                'pool_size': self._pool.qsize(),
                'active_connections': len(self._active_connections)
            }
    
    def close(self):
        """Close all connections in the pool."""
        with self._lock:
            # Close all connections in pool
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except Empty:
                    break
            
            # Close active connections
            for conn in self._active_connections.values():
                conn.close()
            self._active_connections.clear()

class OptimizedLocalEvidenceStore:
    """
    Optimized local evidence store with connection pooling, batch operations,
    and performance monitoring.
    """
    
    def __init__(self, base_path: Optional[str] = None, pool_config: ConnectionPoolConfig = None):
        self.logger = logging.getLogger(__name__)
        
        if base_path is None:
            base_path = Path.home() / ".levox" / "evidence"
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Database path
        self.db_path = self.base_path / "evidence.db"
        
        # Initialize connection pool
        self.pool = OptimizedConnectionPool(str(self.db_path), pool_config)
        
        # Initialize database schema
        self._initialize_schema()
        
        # Prepared statements
        self._prepare_statements()
        
        self.logger.info(f"OptimizedLocalEvidenceStore initialized at {self.db_path}")
    
    def _initialize_schema(self):
        """Initialize database schema with optimized indexes."""
        schema_sql = """
        -- Scan History Table
        CREATE TABLE IF NOT EXISTS scan_history (
            scan_id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            scan_timestamp TEXT NOT NULL,
            total_violations INTEGER NOT NULL DEFAULT 0,
            critical_violations INTEGER NOT NULL DEFAULT 0,
            high_violations INTEGER NOT NULL DEFAULT 0,
            medium_violations INTEGER NOT NULL DEFAULT 0,
            low_violations INTEGER NOT NULL DEFAULT 0,
            scan_path TEXT NOT NULL,
            scan_duration_seconds REAL,
            results_json TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        
        -- Violations Table
        CREATE TABLE IF NOT EXISTS violations (
            id TEXT PRIMARY KEY,
            scan_id TEXT NOT NULL,
            company_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            line_number INTEGER NOT NULL,
            column_number INTEGER,
            violation_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            matched_text TEXT,
            context_before TEXT,
            context_after TEXT,
            gdpr_articles TEXT,
            remediation_suggestions TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (scan_id) REFERENCES scan_history(scan_id) ON DELETE CASCADE
        );
        
        -- Remediations Table
        CREATE TABLE IF NOT EXISTS remediations (
            id TEXT PRIMARY KEY,
            violation_id TEXT NOT NULL,
            company_id TEXT NOT NULL,
            remediation_type TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            implemented_at TEXT,
            evidence_files TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (violation_id) REFERENCES violations(id) ON DELETE CASCADE
        );
        
        -- Company Profiles Table
        CREATE TABLE IF NOT EXISTS company_profiles (
            company_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            industry TEXT,
            size TEXT,
            contact_email TEXT,
            settings TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        
        -- Evidence Packages Table
        CREATE TABLE IF NOT EXISTS evidence_packages (
            package_id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            format TEXT NOT NULL,
            file_path TEXT,
            file_size_bytes INTEGER,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        
        -- Performance Optimized Indexes
        CREATE INDEX IF NOT EXISTS idx_scan_history_company_timestamp 
            ON scan_history(company_id, scan_timestamp);
        CREATE INDEX IF NOT EXISTS idx_scan_history_timestamp 
            ON scan_history(scan_timestamp);
        
        CREATE INDEX IF NOT EXISTS idx_violations_scan_id 
            ON violations(scan_id);
        CREATE INDEX IF NOT EXISTS idx_violations_company_id 
            ON violations(company_id);
        CREATE INDEX IF NOT EXISTS idx_violations_severity 
            ON violations(severity);
        CREATE INDEX IF NOT EXISTS idx_violations_type 
            ON violations(violation_type);
        CREATE INDEX IF NOT EXISTS idx_violations_file_path 
            ON violations(file_path);
        
        CREATE INDEX IF NOT EXISTS idx_remediations_violation_id 
            ON remediations(violation_id);
        CREATE INDEX IF NOT EXISTS idx_remediations_company_id 
            ON remediations(company_id);
        CREATE INDEX IF NOT EXISTS idx_remediations_status 
            ON remediations(status);
        
        CREATE INDEX IF NOT EXISTS idx_evidence_packages_company_id 
            ON evidence_packages(company_id);
        CREATE INDEX IF NOT EXISTS idx_evidence_packages_generated_at 
            ON evidence_packages(generated_at);
        """
        
        # Execute schema creation
        for statement in schema_sql.split(';'):
            statement = statement.strip()
            if statement:
                self.pool.execute_query(statement)
    
    def _prepare_statements(self):
        """Prepare commonly used SQL statements for better performance."""
        self._prepared_statements = {
            'insert_scan': """
                INSERT OR REPLACE INTO scan_history 
                (scan_id, company_id, scan_timestamp, total_violations, critical_violations, 
                 high_violations, medium_violations, low_violations, scan_path, 
                 scan_duration_seconds, results_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            'insert_violation': """
                INSERT OR REPLACE INTO violations 
                (id, scan_id, company_id, file_path, line_number, column_number, 
                 violation_type, severity, description, matched_text, context_before, 
                 context_after, gdpr_articles, remediation_suggestions, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            'insert_remediation': """
                INSERT OR REPLACE INTO remediations 
                (id, violation_id, company_id, remediation_type, description, status, 
                 implemented_at, evidence_files, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            'insert_company': """
                INSERT OR REPLACE INTO company_profiles 
                (company_id, name, description, industry, size, contact_email, 
                 settings, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            'insert_evidence_package': """
                INSERT OR REPLACE INTO evidence_packages 
                (package_id, company_id, generated_at, period_start, period_end, 
                 format, file_path, file_size_bytes, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        }
    
    def save_scan_result(self, scan_data: ScanHistoryEntry) -> bool:
        """Save scan result with optimized single query."""
        try:
            now = datetime.now().isoformat()
            
            query = self._prepared_statements['insert_scan']
            params = (
                scan_data.scan_id,
                scan_data.company_id,
                scan_data.scan_timestamp.isoformat(),
                scan_data.total_violations,
                scan_data.critical_violations,
                scan_data.high_violations,
                scan_data.medium_violations,
                scan_data.low_violations,
                scan_data.scan_path,
                scan_data.scan_duration_seconds,
                json.dumps(scan_data.results_json) if scan_data.results_json else None,
                now,
                now
            )
            
            self.pool.execute_query(query, params)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save scan result: {e}")
            return False
    
    def batch_save_violations(self, violations: List[ViolationRecord]) -> bool:
        """Save multiple violations in a single batch operation."""
        if not violations:
            return True
        
        try:
            now = datetime.now().isoformat()
            queries = []
            
            for violation in violations:
                query = self._prepared_statements['insert_violation']
                params = (
                    violation.id,
                    violation.scan_id,
                    violation.company_id,
                    violation.file_path,
                    violation.line_number,
                    violation.column_number,
                    violation.violation_type,
                    violation.severity,
                    violation.description,
                    violation.matched_text,
                    violation.context_before,
                    violation.context_after,
                    json.dumps(violation.gdpr_articles) if violation.gdpr_articles else None,
                    json.dumps(violation.remediation_suggestions) if violation.remediation_suggestions else None,
                    now,
                    now
                )
                queries.append((query, params))
            
            self.pool.execute_batch(queries)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to batch save violations: {e}")
            return False
    
    def get_scan_history(self, company_id: str, start_date: Optional[date] = None, 
                        end_date: Optional[date] = None) -> List[ScanHistoryEntry]:
        """Get scan history with optimized query."""
        try:
            query = """
                SELECT * FROM scan_history 
                WHERE company_id = ?
            """
            params = [company_id]
            
            if start_date:
                query += " AND scan_timestamp >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND scan_timestamp <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY scan_timestamp DESC"
            
            rows = self.pool.execute_query(query, tuple(params), fetch=True)
            
            scans = []
            for row in rows:
                scan = ScanHistoryEntry(
                    scan_id=row['scan_id'],
                    company_id=row['company_id'],
                    scan_timestamp=datetime.fromisoformat(row['scan_timestamp']),
                    total_violations=row['total_violations'],
                    critical_violations=row['critical_violations'],
                    high_violations=row['high_violations'],
                    medium_violations=row['medium_violations'],
                    low_violations=row['low_violations'],
                    scan_path=row['scan_path'],
                    scan_duration_seconds=row['scan_duration_seconds'],
                    results_json=json.loads(row['results_json']) if row['results_json'] else None
                )
                scans.append(scan)
            
            return scans
            
        except Exception as e:
            self.logger.error(f"Failed to get scan history: {e}")
            return []
    
    def get_violations(self, scan_id: Optional[str] = None, 
                      company_id: Optional[str] = None) -> List[ViolationRecord]:
        """Get violations with optimized query."""
        try:
            query = "SELECT * FROM violations WHERE 1=1"
            params = []
            
            if scan_id:
                query += " AND scan_id = ?"
                params.append(scan_id)
            
            if company_id:
                query += " AND company_id = ?"
                params.append(company_id)
            
            query += " ORDER BY severity DESC, line_number ASC"
            
            rows = self.pool.execute_query(query, tuple(params), fetch=True)
            
            violations = []
            for row in rows:
                violation = ViolationRecord(
                    id=row['id'],
                    scan_id=row['scan_id'],
                    company_id=row['company_id'],
                    file_path=row['file_path'],
                    line_number=row['line_number'],
                    column_number=row['column_number'],
                    violation_type=row['violation_type'],
                    severity=row['severity'],
                    description=row['description'],
                    matched_text=row['matched_text'],
                    context_before=row['context_before'],
                    context_after=row['context_after'],
                    gdpr_articles=json.loads(row['gdpr_articles']) if row['gdpr_articles'] else None,
                    remediation_suggestions=json.loads(row['remediation_suggestions']) if row['remediation_suggestions'] else None
                )
                violations.append(violation)
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Failed to get violations: {e}")
            return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get database performance statistics."""
        return self.pool.get_performance_stats()
    
    def close(self):
        """Close the database connection pool."""
        self.pool.close()
        self.logger.info("OptimizedLocalEvidenceStore closed")
