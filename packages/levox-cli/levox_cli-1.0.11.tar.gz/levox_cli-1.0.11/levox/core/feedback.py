"""
Real feedback collection system for improving detection accuracy with SQLite storage.
"""

import json
import uuid
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import sqlite3
import threading

from .config import Config
from .exceptions import ConfigurationError
from ..models.detection_result import DetectionMatch


class FeedbackCollector:
    """Real feedback collection system with SQLite storage and export capabilities."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(f"levox.feedback.{id(self)}")
        self.feedback_db_path = self._get_feedback_db_path()
        self._migration_version = 1
        self._init_database()
        self._lock = threading.Lock()
    
    def _get_feedback_db_path(self) -> Path:
        """Get the path for the feedback database."""
        if hasattr(self.config, 'feedback_db_path') and self.config.feedback_db_path:
            return Path(self.config.feedback_db_path)
        
        # Default location in user's home directory
        import os
        home_dir = Path.home()
        levox_dir = home_dir / '.levox'
        levox_dir.mkdir(parents=True, exist_ok=True)
        
        return levox_dir / 'feedback.db'
    
    def _init_database(self) -> None:
        """Initialize the feedback database with proper schema and migrations."""
        try:
            with sqlite3.connect(self.feedback_db_path) as conn:
                cursor = conn.cursor()
                
                # Enable foreign key constraints
                cursor.execute('PRAGMA foreign_keys = ON')
                
                # Create main feedback table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feedback (
                        id TEXT PRIMARY KEY,
                        match_id TEXT NOT NULL,
                        pattern_name TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        line_number INTEGER NOT NULL,
                        column_start INTEGER,
                        column_end INTEGER,
                        matched_text TEXT NOT NULL,
                        verdict TEXT NOT NULL CHECK(verdict IN ('true_positive', 'false_positive', 'uncertain')),
                        notes TEXT,
                        context_hash TEXT,
                        confidence_original REAL,
                        risk_level TEXT,
                        detection_level TEXT,
                        user_id TEXT,
                        session_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create context table for storing match context
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feedback_context (
                        id TEXT PRIMARY KEY,
                        feedback_id TEXT NOT NULL,
                        context_before TEXT,
                        context_after TEXT,
                        full_line TEXT,
                        file_type TEXT,
                        FOREIGN KEY (feedback_id) REFERENCES feedback (id) ON DELETE CASCADE
                    )
                ''')
                
                # Create statistics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feedback_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        pattern_name TEXT NOT NULL,
                        verdict TEXT NOT NULL,
                        count INTEGER DEFAULT 1,
                        UNIQUE(date, pattern_name, verdict)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_pattern ON feedback(pattern_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_file ON feedback(file_path)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_verdict ON feedback(verdict)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_created ON feedback(created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_match_id ON feedback(match_id)')
                
                # Create version table for migrations
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER PRIMARY KEY,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Check and apply migrations
                self._apply_migrations(cursor)
                
                conn.commit()
                self.logger.info(f"Feedback database initialized at {self.feedback_db_path}")
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize feedback database: {e}")
            raise ConfigurationError(f"Feedback database initialization failed: {e}")
    
    def _apply_migrations(self, cursor: sqlite3.Cursor) -> None:
        """Apply database migrations."""
        try:
            # Check current version
            cursor.execute('SELECT MAX(version) FROM schema_version')
            result = cursor.fetchone()
            current_version = result[0] if result[0] is not None else 0
            
            if current_version < self._migration_version:
                # Apply migrations
                cursor.execute('INSERT OR REPLACE INTO schema_version (version) VALUES (?)', 
                              (self._migration_version,))
                self.logger.info(f"Applied database migration to version {self._migration_version}")
                
        except sqlite3.Error as e:
            self.logger.warning(f"Migration check failed: {e}")
    
    def submit_feedback(self, match_id: str, verdict: str, notes: Optional[str] = None,
                       file_path: Optional[str] = None, rule_id: Optional[str] = None,
                       hash_of_context: Optional[str] = None, 
                       detection_match: Optional[DetectionMatch] = None,
                       user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """
        Submit feedback for a detection match.
        
        Args:
            match_id: Unique identifier for the match
            verdict: 'true_positive', 'false_positive', or 'uncertain'
            notes: Optional user notes
            file_path: Path to the file where match was found
            rule_id: Rule/pattern ID that generated the match
            hash_of_context: Hash of the context for deduplication
            detection_match: Full detection match object
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            Feedback ID
        """
        if verdict not in ['true_positive', 'false_positive', 'uncertain']:
            raise ValueError(f"Invalid verdict: {verdict}. Must be one of: true_positive, false_positive, uncertain")
        
        with self._lock:
            try:
                feedback_id = str(uuid.uuid4())
                
                # Extract information from detection match if provided
                if detection_match:
                    pattern_name = detection_match.pattern_name
                    file_path = file_path or str(getattr(detection_match, 'file_path', ''))
                    line_number = detection_match.line_number
                    column_start = detection_match.column_start
                    column_end = detection_match.column_end
                    matched_text = detection_match.matched_text
                    confidence_original = detection_match.confidence
                    risk_level = detection_match.risk_level.value if hasattr(detection_match.risk_level, 'value') else str(detection_match.risk_level)
                    detection_level = detection_match.metadata.get('detection_level', 'unknown')
                    context_before = detection_match.context_before
                    context_after = detection_match.context_after
                else:
                    pattern_name = rule_id or 'unknown'
                    line_number = 0
                    column_start = 0
                    column_end = 0
                    matched_text = ''
                    confidence_original = 0.0
                    risk_level = 'unknown'
                    detection_level = 'unknown'
                    context_before = ''
                    context_after = ''
                
                # Generate context hash if not provided
                if not hash_of_context and detection_match:
                    context_str = f"{matched_text}:{context_before}:{context_after}"
                    hash_of_context = hashlib.sha256(context_str.encode()).hexdigest()[:16]
                
                with sqlite3.connect(self.feedback_db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Insert main feedback record
                    cursor.execute('''
                        INSERT INTO feedback (
                            id, match_id, pattern_name, file_path, line_number, 
                            column_start, column_end, matched_text, verdict, notes,
                            context_hash, confidence_original, risk_level, detection_level,
                            user_id, session_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        feedback_id, match_id, pattern_name, file_path or '', line_number,
                        column_start, column_end, matched_text, verdict, notes,
                        hash_of_context, confidence_original, risk_level, detection_level,
                        user_id, session_id
                    ))
                    
                    # Insert context information
                    if detection_match:
                        file_type = Path(file_path or '').suffix.lower() if file_path else ''
                        cursor.execute('''
                            INSERT INTO feedback_context (
                                id, feedback_id, context_before, context_after, 
                                full_line, file_type
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            str(uuid.uuid4()), feedback_id, context_before, context_after,
                            f"{context_before}{matched_text}{context_after}", file_type
                        ))
                    
                    # Update statistics
                    today = datetime.now().strftime('%Y-%m-%d')
                    cursor.execute('''
                        INSERT INTO feedback_stats (date, pattern_name, verdict, count)
                        VALUES (?, ?, ?, 1)
                        ON CONFLICT(date, pattern_name, verdict) 
                        DO UPDATE SET count = count + 1
                    ''', (today, pattern_name, verdict))
                    
                    conn.commit()
                
                self.logger.info(f"Feedback submitted: {feedback_id} for pattern {pattern_name} with verdict {verdict}")
                return feedback_id
                
            except sqlite3.Error as e:
                self.logger.error(f"Failed to submit feedback: {e}")
                raise ConfigurationError(f"Failed to submit feedback: {e}")
    
    def export_feedback_jsonl(self, output_path: str, limit: Optional[int] = None,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             verdict_filter: Optional[str] = None) -> int:
        """
        Export feedback data to JSONL format for ML training.
        
        Args:
            output_path: Path to output JSONL file
            limit: Maximum number of records to export
            start_date: Filter records after this date
            end_date: Filter records before this date
            verdict_filter: Filter by verdict type
            
        Returns:
            Number of records exported
        """
        try:
            with sqlite3.connect(self.feedback_db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with filters
                query = '''
                    SELECT f.*, fc.context_before, fc.context_after, fc.full_line, fc.file_type
                    FROM feedback f
                    LEFT JOIN feedback_context fc ON f.id = fc.feedback_id
                    WHERE 1=1
                '''
                params = []
                
                if start_date:
                    query += ' AND f.created_at >= ?'
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += ' AND f.created_at <= ?'
                    params.append(end_date.isoformat())
                
                if verdict_filter:
                    query += ' AND f.verdict = ?'
                    params.append(verdict_filter)
                
                query += ' ORDER BY f.created_at DESC'
                
                if limit:
                    query += ' LIMIT ?'
                    params.append(limit)
                
                cursor.execute(query, params)
                records = cursor.fetchall()
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Export to JSONL
                exported_count = 0
                with open(output_path, 'w', encoding='utf-8') as f:
                    for record in records:
                        record_dict = dict(zip(columns, record))
                        # Convert to training format
                        training_record = self._convert_to_training_format(record_dict)
                        f.write(json.dumps(training_record, ensure_ascii=False) + '\n')
                        exported_count += 1
                
                self.logger.info(f"Exported {exported_count} feedback records to {output_path}")
                return exported_count
                
        except Exception as e:
            self.logger.error(f"Failed to export feedback: {e}")
            raise ConfigurationError(f"Failed to export feedback: {e}")
    
    def _convert_to_training_format(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert database record to ML training format."""
        return {
            'pattern_type': record.get('pattern_name', ''),
            'matched_text': record.get('matched_text', ''),
            'context_before': record.get('context_before', ''),
            'context_after': record.get('context_after', ''),
            'full_line': record.get('full_line', ''),
            'file_type': record.get('file_type', ''),
            'line_number': record.get('line_number', 0),
            'confidence_original': record.get('confidence_original', 0.0),
            'risk_level': record.get('risk_level', ''),
            'detection_level': record.get('detection_level', ''),
            'verdict': record.get('verdict', ''),
            'is_true_positive': record.get('verdict') == 'true_positive',
            'created_at': record.get('created_at', ''),
            'user_notes': record.get('notes', ''),
            'source': 'user_feedback'
        }
    
    def get_feedback_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get feedback statistics for the last N days."""
        try:
            with sqlite3.connect(self.feedback_db_path) as conn:
                cursor = conn.cursor()
                
                # Date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Overall stats
                cursor.execute('''
                    SELECT verdict, COUNT(*) 
                    FROM feedback 
                    WHERE created_at >= ? 
                    GROUP BY verdict
                ''', (start_date.isoformat(),))
                
                verdict_counts = dict(cursor.fetchall())
                
                # Pattern stats
                cursor.execute('''
                    SELECT pattern_name, verdict, COUNT(*) 
                    FROM feedback 
                    WHERE created_at >= ? 
                    GROUP BY pattern_name, verdict
                    ORDER BY pattern_name, verdict
                ''', (start_date.isoformat(),))
                
                pattern_stats = {}
                for pattern, verdict, count in cursor.fetchall():
                    if pattern not in pattern_stats:
                        pattern_stats[pattern] = {}
                    pattern_stats[pattern][verdict] = count
                
                # Total feedback count
                cursor.execute('SELECT COUNT(*) FROM feedback')
                total_feedback = cursor.fetchone()[0]
                
                return {
                    'total_feedback': total_feedback,
                    'period_days': days,
                    'verdict_counts': verdict_counts,
                    'pattern_stats': pattern_stats,
                    'database_path': str(self.feedback_db_path)
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get feedback stats: {e}")
            return {}
    
    def get_feedback_by_id(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback record by ID."""
        try:
            with sqlite3.connect(self.feedback_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT f.*, fc.context_before, fc.context_after, fc.full_line, fc.file_type
                    FROM feedback f
                    LEFT JOIN feedback_context fc ON f.id = fc.feedback_id
                    WHERE f.id = ?
                ''', (feedback_id,))
                
                record = cursor.fetchone()
                if record:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, record))
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get feedback by ID: {e}")
        
        return None
    
    def update_feedback(self, feedback_id: str, verdict: Optional[str] = None, 
                       notes: Optional[str] = None) -> bool:
        """Update existing feedback record."""
        if verdict and verdict not in ['true_positive', 'false_positive', 'uncertain']:
            raise ValueError(f"Invalid verdict: {verdict}")
        
        try:
            with sqlite3.connect(self.feedback_db_path) as conn:
                cursor = conn.cursor()
                
                updates = []
                params = []
                
                if verdict:
                    updates.append('verdict = ?')
                    params.append(verdict)
                
                if notes is not None:
                    updates.append('notes = ?')
                    params.append(notes)
                
                if updates:
                    updates.append('updated_at = CURRENT_TIMESTAMP')
                    params.append(feedback_id)
                    
                    query = f"UPDATE feedback SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(query, params)
                    
                    if cursor.rowcount > 0:
                        conn.commit()
                        self.logger.info(f"Updated feedback {feedback_id}")
                        return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to update feedback: {e}")
        
        return False
    
    def delete_feedback(self, feedback_id: str) -> bool:
        """Delete feedback record."""
        try:
            with sqlite3.connect(self.feedback_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"Deleted feedback {feedback_id}")
                    return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to delete feedback: {e}")
        
        return False
