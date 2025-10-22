"""
Evidence storage system for compliance tracking.
Supports both local (SQLite/JSON) and Supabase backends.
"""

import json
import sqlite3
import logging
from abc import ABC, abstractmethod
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import asdict

from .models import (
    ScanHistoryEntry, ViolationRecord, RemediationEvidence, 
    CompanyProfile, ViolationTrend, ComplianceMetrics, EvidencePackage
)


class EvidenceStore(ABC):
    """Abstract base class for evidence storage."""
    
    @abstractmethod
    def save_scan_result(self, scan_data: ScanHistoryEntry) -> bool:
        """Save scan result to storage."""
        pass
    
    @abstractmethod
    def get_scan_history(self, company_id: str, start_date: Optional[date] = None, 
                        end_date: Optional[date] = None) -> List[ScanHistoryEntry]:
        """Get scan history for a company."""
        pass
    
    @abstractmethod
    def save_violation(self, violation: ViolationRecord) -> bool:
        """Save violation record."""
        pass
    
    @abstractmethod
    def get_violations(self, scan_id: Optional[str] = None, 
                      company_id: Optional[str] = None) -> List[ViolationRecord]:
        """Get violations by scan or company."""
        pass
    
    @abstractmethod
    def save_remediation(self, remediation: RemediationEvidence) -> bool:
        """Save remediation evidence."""
        pass
    
    @abstractmethod
    def get_remediations(self, violation_id: Optional[str] = None) -> List[RemediationEvidence]:
        """Get remediation evidence."""
        pass
    
    @abstractmethod
    def get_violation_trends(self, company_id: str, period_days: int = 30) -> List[ViolationTrend]:
        """Get violation trends for analysis."""
        pass
    
    @abstractmethod
    def save_company_profile(self, profile: CompanyProfile) -> bool:
        """Save company profile."""
        pass
    
    @abstractmethod
    def get_company_profile(self, company_id: str) -> Optional[CompanyProfile]:
        """Get company profile."""
        pass
    
    @abstractmethod
    def list_company_profiles(self) -> List[CompanyProfile]:
        """List all company profiles."""
        pass
    
    @abstractmethod
    def save_evidence_package(self, package: EvidencePackage) -> bool:
        """Save generated evidence package."""
        pass
    
    @abstractmethod
    def get_evidence_package(self, package_id: str) -> Optional[EvidencePackage]:
        """Get evidence package by ID."""
        pass


class LocalEvidenceStore(EvidenceStore):
    """Local file-based evidence storage using SQLite and JSON."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize local evidence store."""
        self.logger = logging.getLogger(__name__)
        
        if base_path is None:
            base_path = Path.home() / ".levox" / "evidence"
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Database path
        self.db_path = self.base_path / "evidence.db"
        self.json_path = self.base_path / "scan_results"
        self.json_path.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Scan history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    scan_id TEXT PRIMARY KEY,
                    company_id TEXT,
                    scan_timestamp TEXT NOT NULL,
                    scan_path TEXT,
                    git_commit_hash TEXT,
                    git_branch TEXT,
                    git_author TEXT,
                    total_files INTEGER DEFAULT 0,
                    total_violations INTEGER DEFAULT 0,
                    critical_violations INTEGER DEFAULT 0,
                    high_violations INTEGER DEFAULT 0,
                    medium_violations INTEGER DEFAULT 0,
                    low_violations INTEGER DEFAULT 0,
                    scan_duration_seconds REAL DEFAULT 0.0,
                    license_tier TEXT DEFAULT 'starter',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Violations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS violations (
                    id TEXT PRIMARY KEY,
                    scan_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    violation_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    gdpr_article TEXT,
                    description TEXT,
                    matched_text TEXT,
                    confidence REAL DEFAULT 0.0,
                    remediated BOOLEAN DEFAULT FALSE,
                    remediated_at TEXT,
                    remediation_commit TEXT,
                    remediation_type TEXT,
                    remediation_notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scan_history(scan_id)
                )
            """)
            
            # Remediations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS remediations (
                    id TEXT PRIMARY KEY,
                    violation_id TEXT NOT NULL,
                    remediation_type TEXT NOT NULL,
                    commit_hash TEXT,
                    pr_url TEXT,
                    committed_by TEXT,
                    committed_at TEXT,
                    verification_scan_id TEXT,
                    notes TEXT,
                    before_snippet TEXT,
                    after_snippet TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (violation_id) REFERENCES violations(id)
                )
            """)
            
            # Company profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company_profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    industry TEXT,
                    company_size TEXT,
                    compliance_officer_email TEXT,
                    headquarters_country TEXT,
                    gdpr_applicable BOOLEAN DEFAULT TRUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Evidence packages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidence_packages (
                    package_id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    file_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_company ON scan_history(company_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_timestamp ON scan_history(scan_timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_violations_scan_id ON violations(scan_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_violations_type ON violations(violation_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_remediations_violation ON remediations(violation_id)")
            
            conn.commit()
    
    def save_scan_result(self, scan_data: ScanHistoryEntry) -> bool:
        """Save scan result to storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO scan_history 
                    (scan_id, company_id, scan_timestamp, scan_path, git_commit_hash, 
                     git_branch, git_author, total_files, total_violations, 
                     critical_violations, high_violations, medium_violations, 
                     low_violations, scan_duration_seconds, license_tier, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scan_data.scan_id, scan_data.company_id, 
                    scan_data.scan_timestamp.isoformat(), str(scan_data.scan_path),
                    scan_data.git_commit_hash, scan_data.git_branch, scan_data.git_author,
                    scan_data.total_files, scan_data.total_violations,
                    scan_data.critical_violations, scan_data.high_violations,
                    scan_data.medium_violations, scan_data.low_violations,
                    scan_data.scan_duration_seconds, scan_data.license_tier,
                    scan_data.created_at.isoformat()
                ))
                
                # Save detailed results as JSON
                if scan_data.results_json:
                    json_file = self.json_path / f"{scan_data.scan_id}.json"
                    with open(json_file, 'w') as f:
                        json.dump(scan_data.results_json, f, indent=2, default=str)
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save scan result: {e}")
            return False
    
    def get_scan_history(self, company_id: str, start_date: Optional[date] = None, 
                        end_date: Optional[date] = None) -> List[ScanHistoryEntry]:
        """Get scan history for a company."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM scan_history WHERE company_id = ?"
                params = [company_id]
                
                if start_date:
                    query += " AND DATE(scan_timestamp) >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND DATE(scan_timestamp) <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY scan_timestamp DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                history = []
                for row in rows:
                    # Load detailed results if available
                    results_json = None
                    json_file = self.json_path / f"{row[0]}.json"
                    if json_file.exists():
                        with open(json_file, 'r') as f:
                            results_json = json.load(f)
                    
                    entry = ScanHistoryEntry(
                        scan_id=row[0],
                        company_id=row[1],
                        scan_timestamp=datetime.fromisoformat(row[2]),
                        scan_path=row[3],
                        git_commit_hash=row[4],
                        git_branch=row[5],
                        git_author=row[6],
                        total_files=row[7],
                        total_violations=row[8],
                        critical_violations=row[9],
                        high_violations=row[10],
                        medium_violations=row[11],
                        low_violations=row[12],
                        scan_duration_seconds=row[13],
                        license_tier=row[14],
                        results_json=results_json,
                        created_at=datetime.fromisoformat(row[15])
                    )
                    history.append(entry)
                
                return history
                
        except Exception as e:
            self.logger.error(f"Failed to get scan history: {e}")
            return []
    
    def save_violation(self, violation: ViolationRecord) -> bool:
        """Save violation record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO violations 
                    (id, scan_id, file_path, line_number, violation_type, severity,
                     gdpr_article, description, matched_text, confidence, remediated,
                     remediated_at, remediation_commit, remediation_type, remediation_notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    violation.id, violation.scan_id, str(violation.file_path),
                    violation.line_number, violation.violation_type.value,
                    violation.severity, violation.gdpr_article.value if violation.gdpr_article else None,
                    violation.description, violation.matched_text, violation.confidence,
                    violation.remediated, violation.remediated_at.isoformat() if violation.remediated_at else None,
                    violation.remediation_commit, violation.remediation_type.value if violation.remediation_type else None,
                    violation.remediation_notes, violation.created_at.isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save violation: {e}")
            return False
    
    def get_violations(self, scan_id: Optional[str] = None, 
                      company_id: Optional[str] = None) -> List[ViolationRecord]:
        """Get violations by scan or company."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if scan_id:
                    cursor.execute("SELECT * FROM violations WHERE scan_id = ?", (scan_id,))
                elif company_id:
                    cursor.execute("""
                        SELECT v.* FROM violations v
                        JOIN scan_history s ON v.scan_id = s.scan_id
                        WHERE s.company_id = ?
                    """, (company_id,))
                else:
                    cursor.execute("SELECT * FROM violations")
                
                rows = cursor.fetchall()
                
                violations = []
                for row in rows:
                    violation = ViolationRecord(
                        id=row[0],
                        scan_id=row[1],
                        file_path=row[2],
                        line_number=row[3],
                        violation_type=row[4],
                        severity=row[5],
                        gdpr_article=row[6],
                        description=row[7],
                        matched_text=row[8],
                        confidence=row[9],
                        remediated=bool(row[10]),
                        remediated_at=datetime.fromisoformat(row[11]) if row[11] else None,
                        remediation_commit=row[12],
                        remediation_type=row[13],
                        remediation_notes=row[14],
                        created_at=datetime.fromisoformat(row[15])
                    )
                    violations.append(violation)
                
                return violations
                
        except Exception as e:
            self.logger.error(f"Failed to get violations: {e}")
            return []
    
    def save_remediation(self, remediation: RemediationEvidence) -> bool:
        """Save remediation evidence."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO remediations 
                    (id, violation_id, remediation_type, commit_hash, pr_url,
                     committed_by, committed_at, verification_scan_id, notes,
                     before_snippet, after_snippet, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    remediation.id, remediation.violation_id, remediation.remediation_type.value,
                    remediation.commit_hash, remediation.pr_url, remediation.committed_by,
                    remediation.committed_at.isoformat() if remediation.committed_at else None,
                    remediation.verification_scan_id, remediation.notes,
                    remediation.before_snippet, remediation.after_snippet,
                    remediation.created_at.isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save remediation: {e}")
            return False
    
    def get_remediations(self, violation_id: Optional[str] = None) -> List[RemediationEvidence]:
        """Get remediation evidence."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if violation_id:
                    cursor.execute("SELECT * FROM remediations WHERE violation_id = ?", (violation_id,))
                else:
                    cursor.execute("SELECT * FROM remediations")
                
                rows = cursor.fetchall()
                
                remediations = []
                for row in rows:
                    remediation = RemediationEvidence(
                        id=row[0],
                        violation_id=row[1],
                        remediation_type=row[2],
                        commit_hash=row[3],
                        pr_url=row[4],
                        committed_by=row[5],
                        committed_at=datetime.fromisoformat(row[6]) if row[6] else None,
                        verification_scan_id=row[7],
                        notes=row[8],
                        before_snippet=row[9],
                        after_snippet=row[10],
                        created_at=datetime.fromisoformat(row[11])
                    )
                    remediations.append(remediation)
                
                return remediations
                
        except Exception as e:
            self.logger.error(f"Failed to get remediations: {e}")
            return []
    
    def get_violation_trends(self, company_id: str, period_days: int = 30) -> List[ViolationTrend]:
        """Get violation trends for analysis."""
        # This is a simplified implementation
        # In a real implementation, you'd do complex time-series analysis
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get scans for the period
                cursor.execute("""
                    SELECT scan_timestamp, total_violations, critical_violations,
                           high_violations, medium_violations, low_violations
                    FROM scan_history 
                    WHERE company_id = ? 
                    AND scan_timestamp >= datetime('now', '-{} days')
                    ORDER BY scan_timestamp
                """.format(period_days), (company_id,))
                
                rows = cursor.fetchall()
                
                # Group by week and calculate trends
                trends = []
                # Implementation would group by time periods and calculate trends
                # This is a placeholder for the actual trend calculation
                
                return trends
                
        except Exception as e:
            self.logger.error(f"Failed to get violation trends: {e}")
            return []
    
    def save_company_profile(self, profile: CompanyProfile) -> bool:
        """Save company profile."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO company_profiles 
                    (id, name, industry, company_size, compliance_officer_email,
                     headquarters_country, gdpr_applicable, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.id, profile.name, profile.industry, profile.company_size,
                    profile.compliance_officer_email, profile.headquarters_country,
                    profile.gdpr_applicable, profile.created_at.isoformat(),
                    profile.updated_at.isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save company profile: {e}")
            return False
    
    def get_company_profile(self, company_id: str) -> Optional[CompanyProfile]:
        """Get company profile."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM company_profiles WHERE id = ?", (company_id,))
                row = cursor.fetchone()
                
                if row:
                    return CompanyProfile(
                        id=row[0],
                        name=row[1],
                        industry=row[2],
                        company_size=row[3],
                        compliance_officer_email=row[4],
                        headquarters_country=row[5],
                        gdpr_applicable=bool(row[6]),
                        created_at=datetime.fromisoformat(row[7]),
                        updated_at=datetime.fromisoformat(row[8])
                    )
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get company profile: {e}")
            return None
    
    def list_company_profiles(self) -> List[CompanyProfile]:
        """List all company profiles."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM company_profiles ORDER BY created_at DESC")
                rows = cursor.fetchall()
                
                companies = []
                for row in rows:
                    company = CompanyProfile(
                        id=row[0],
                        name=row[1],
                        industry=row[2],
                        company_size=row[3],
                        compliance_officer_email=row[4],
                        headquarters_country=row[5],
                        gdpr_applicable=bool(row[6]),
                        created_at=datetime.fromisoformat(row[7]),
                        updated_at=datetime.fromisoformat(row[8])
                    )
                    companies.append(company)
                
                return companies
                
        except Exception as e:
            self.logger.error(f"Failed to list company profiles: {e}")
            return []
    
    def save_evidence_package(self, package: EvidencePackage) -> bool:
        """Save generated evidence package."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO evidence_packages 
                    (package_id, company_id, generated_at, period_start, period_end, file_path, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    package.package_id, package.company_id, package.generated_at.isoformat(),
                    package.period_start.isoformat(), package.period_end.isoformat(),
                    package.file_path, datetime.utcnow().isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save evidence package: {e}")
            return False
    
    def get_evidence_package(self, package_id: str) -> Optional[EvidencePackage]:
        """Get evidence package by ID."""
        # This would need to reconstruct the full package from stored data
        # For now, return None as this is complex
        return None


class SupabaseEvidenceStore(EvidenceStore):
    """Supabase-based evidence storage for SaaS users with real-time support."""
    
    def __init__(self, supabase_client, enable_realtime: bool = True):
        """Initialize Supabase evidence store."""
        self.client = supabase_client
        self.enable_realtime = enable_realtime
        self.realtime_channel = None
        self.logger = logging.getLogger(__name__)
        
        if enable_realtime:
            self._setup_realtime_subscriptions()
    
    def _setup_realtime_subscriptions(self):
        """Subscribe to real-time updates for evidence tables."""
        try:
            # Subscribe to scan_history changes
            self.realtime_channel = self.client.channel('evidence_updates')
            
            self.realtime_channel.on(
                'postgres_changes',
                {
                    'event': '*',
                    'schema': 'public',
                    'table': 'scan_history'
                },
                self._handle_scan_history_change
            )
            
            self.realtime_channel.on(
                'postgres_changes',
                {
                    'event': '*',
                    'schema': 'public',
                    'table': 'violations'
                },
                self._handle_violation_change
            )
            
            self.realtime_channel.subscribe()
            self.logger.info("Real-time subscriptions established")
            
        except Exception as e:
            self.logger.error(f"Failed to setup real-time subscriptions: {e}")
    
    def _handle_scan_history_change(self, payload):
        """Handle real-time scan history changes."""
        self.logger.debug(f"Scan history change: {payload}")
        # Could trigger local cache updates or notifications
    
    def _handle_violation_change(self, payload):
        """Handle real-time violation changes."""
        self.logger.debug(f"Violation change: {payload}")
        # Could trigger local cache updates or notifications
    
    def save_scan_result(self, scan_data: ScanHistoryEntry) -> bool:
        """Save scan result to Supabase."""
        try:
            result = self.client.table('scan_history').insert({
                'scan_id': scan_data.scan_id,
                'company_id': scan_data.company_id,
                'scan_timestamp': scan_data.scan_timestamp.isoformat(),
                'scan_path': str(scan_data.scan_path),
                'git_commit_hash': scan_data.git_commit_hash,
                'git_branch': scan_data.git_branch,
                'git_author': scan_data.git_author,
                'total_files': scan_data.total_files,
                'total_violations': scan_data.total_violations,
                'critical_violations': scan_data.critical_violations,
                'high_violations': scan_data.high_violations,
                'medium_violations': scan_data.medium_violations,
                'low_violations': scan_data.low_violations,
                'scan_duration_seconds': scan_data.scan_duration_seconds,
                'license_tier': scan_data.license_tier,
                'results_json': scan_data.results_json
            }).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to save scan result to Supabase: {e}")
            return False
    
    def get_scan_history(self, company_id: str, start_date: Optional[date] = None, 
                        end_date: Optional[date] = None) -> List[ScanHistoryEntry]:
        """Get scan history from Supabase."""
        try:
            query = self.client.table('scan_history').select('*').eq('company_id', company_id)
            
            if start_date:
                query = query.gte('scan_timestamp', start_date.isoformat())
            
            if end_date:
                query = query.lte('scan_timestamp', end_date.isoformat())
            
            result = query.order('scan_timestamp', desc=True).execute()
            
            history = []
            for row in result.data:
                entry = ScanHistoryEntry(
                    scan_id=row['scan_id'],
                    company_id=row['company_id'],
                    scan_timestamp=datetime.fromisoformat(row['scan_timestamp'].replace('Z', '+00:00')),
                    scan_path=row['scan_path'],
                    git_commit_hash=row['git_commit_hash'],
                    git_branch=row['git_branch'],
                    git_author=row['git_author'],
                    total_files=row['total_files'],
                    total_violations=row['total_violations'],
                    critical_violations=row['critical_violations'],
                    high_violations=row['high_violations'],
                    medium_violations=row['medium_violations'],
                    low_violations=row['low_violations'],
                    scan_duration_seconds=row['scan_duration_seconds'],
                    license_tier=row['license_tier'],
                    results_json=row['results_json'],
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                )
                history.append(entry)
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get scan history from Supabase: {e}")
            return []
    
    def save_violation(self, violation: ViolationRecord) -> bool:
        """Save violation to Supabase."""
        try:
            result = self.client.table('violations').insert({
                'id': violation.id,
                'scan_id': violation.scan_id,
                'file_path': str(violation.file_path),
                'line_number': violation.line_number,
                'violation_type': violation.violation_type.value if hasattr(violation.violation_type, 'value') else str(violation.violation_type),
                'severity': violation.severity,
                'gdpr_article': violation.gdpr_article.value if violation.gdpr_article and hasattr(violation.gdpr_article, 'value') else violation.gdpr_article,
                'description': violation.description,
                'matched_text': violation.matched_text,
                'confidence': violation.confidence,
                'remediated': violation.remediated,
                'remediated_at': violation.remediated_at.isoformat() if violation.remediated_at else None,
                'remediation_commit': violation.remediation_commit,
                'remediation_type': violation.remediation_type.value if violation.remediation_type and hasattr(violation.remediation_type, 'value') else violation.remediation_type,
                'remediation_notes': violation.remediation_notes
            }).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to save violation to Supabase: {e}")
            return False
    
    def get_violations(self, scan_id: Optional[str] = None, 
                      company_id: Optional[str] = None) -> List[ViolationRecord]:
        """Get violations from Supabase."""
        try:
            if scan_id:
                result = self.client.table('violations').select('*').eq('scan_id', scan_id).execute()
            elif company_id:
                # Join with scan_history to filter by company
                result = self.client.table('violations').select(
                    '*, scan_history!inner(scan_id, company_id)'
                ).eq('scan_history.company_id', company_id).execute()
            else:
                result = self.client.table('violations').select('*').execute()
            
            violations = []
            for row in result.data:
                violation = ViolationRecord(
                    id=row['id'],
                    scan_id=row['scan_id'],
                    file_path=row['file_path'],
                    line_number=row['line_number'],
                    violation_type=row['violation_type'],
                    severity=row['severity'],
                    gdpr_article=row['gdpr_article'],
                    description=row['description'],
                    matched_text=row['matched_text'],
                    confidence=row['confidence'],
                    remediated=row['remediated'],
                    remediated_at=datetime.fromisoformat(row['remediated_at'].replace('Z', '+00:00')) if row['remediated_at'] else None,
                    remediation_commit=row['remediation_commit'],
                    remediation_type=row['remediation_type'],
                    remediation_notes=row['remediation_notes'],
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                )
                violations.append(violation)
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Failed to get violations from Supabase: {e}")
            return []
    
    def save_remediation(self, remediation: RemediationEvidence) -> bool:
        """Save remediation to Supabase."""
        try:
            result = self.client.table('remediations').insert({
                'id': remediation.id,
                'violation_id': remediation.violation_id,
                'remediation_type': remediation.remediation_type.value if hasattr(remediation.remediation_type, 'value') else str(remediation.remediation_type),
                'commit_hash': remediation.commit_hash,
                'pr_url': remediation.pr_url,
                'committed_by': remediation.committed_by,
                'committed_at': remediation.committed_at.isoformat() if remediation.committed_at else None,
                'verification_scan_id': remediation.verification_scan_id,
                'notes': remediation.notes,
                'before_snippet': remediation.before_snippet,
                'after_snippet': remediation.after_snippet
            }).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to save remediation to Supabase: {e}")
            return False
    
    def get_remediations(self, violation_id: Optional[str] = None) -> List[RemediationEvidence]:
        """Get remediations from Supabase."""
        try:
            if violation_id:
                result = self.client.table('remediations').select('*').eq('violation_id', violation_id).execute()
            else:
                result = self.client.table('remediations').select('*').execute()
            
            remediations = []
            for row in result.data:
                remediation = RemediationEvidence(
                    id=row['id'],
                    violation_id=row['violation_id'],
                    remediation_type=row['remediation_type'],
                    commit_hash=row['commit_hash'],
                    pr_url=row['pr_url'],
                    committed_by=row['committed_by'],
                    committed_at=datetime.fromisoformat(row['committed_at'].replace('Z', '+00:00')) if row['committed_at'] else None,
                    verification_scan_id=row['verification_scan_id'],
                    notes=row['notes'],
                    before_snippet=row['before_snippet'],
                    after_snippet=row['after_snippet'],
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                )
                remediations.append(remediation)
            
            return remediations
            
        except Exception as e:
            self.logger.error(f"Failed to get remediations from Supabase: {e}")
            return []
    
    def get_violation_trends(self, company_id: str, period_days: int = 30) -> List[ViolationTrend]:
        """Get violation trends from Supabase using database functions."""
        try:
            result = self.client.rpc('get_violation_trends', {
                'company_uuid': company_id,
                'days_back': period_days
            }).execute()
            
            trends = []
            for row in result.data:
                trend = ViolationTrend(
                    period_start=datetime.fromisoformat(row['period_start']).date(),
                    period_end=datetime.fromisoformat(row['period_end']).date(),
                    total_violations=row['total_violations'],
                    new_violations=row['total_violations'],  # Simplified
                    remediated_violations=0,  # Would need additional logic
                    violation_types={},
                    severity_distribution={},
                    gdpr_articles={},
                    improvement_percentage=row['improvement_percentage']
                )
                trends.append(trend)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to get violation trends from Supabase: {e}")
            return []
    
    def save_company_profile(self, profile: CompanyProfile) -> bool:
        """Save company profile to Supabase."""
        try:
            result = self.client.table('company_profiles').upsert({
                'id': profile.id,
                'company_name': profile.name,
                'industry': profile.industry,
                'company_size': profile.company_size,
                'compliance_officer_email': profile.compliance_officer_email,
                'headquarters_country': profile.headquarters_country,
                'gdpr_applicable': profile.gdpr_applicable
            }).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to save company profile to Supabase: {e}")
            return False
    
    def get_company_profile(self, company_id: str) -> Optional[CompanyProfile]:
        """Get company profile from Supabase."""
        try:
            result = self.client.table('company_profiles').select('*').eq('id', company_id).execute()
            
            if result.data:
                row = result.data[0]
                return CompanyProfile(
                    id=row['id'],
                    name=row['company_name'],
                    industry=row['industry'],
                    company_size=row['company_size'],
                    compliance_officer_email=row['compliance_officer_email'],
                    headquarters_country=row['headquarters_country'],
                    gdpr_applicable=row['gdpr_applicable'],
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(row['updated_at'].replace('Z', '+00:00'))
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get company profile from Supabase: {e}")
            return None
    
    def save_evidence_package(self, package: EvidencePackage) -> bool:
        """Save evidence package to Supabase."""
        try:
            result = self.client.table('evidence_packages').insert({
                'package_id': package.package_id,
                'company_id': package.company_id,
                'generated_at': package.generated_at.isoformat(),
                'period_start': package.period_start.isoformat(),
                'period_end': package.period_end.isoformat(),
                'file_path': package.file_path,
                'file_size_bytes': package.file_size_bytes if hasattr(package, 'file_size_bytes') else None,
                'format': package.format if hasattr(package, 'format') else 'json',
                'status': 'completed'
            }).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to save evidence package to Supabase: {e}")
            return False
    
    def get_evidence_package(self, package_id: str) -> Optional[EvidencePackage]:
        """Get evidence package from Supabase."""
        try:
            result = self.client.table('evidence_packages').select('*').eq('package_id', package_id).execute()
            
            if result.data:
                row = result.data[0]
                # This would need to reconstruct the full package from stored data
                # For now, return basic package info
                return EvidencePackage(
                    package_id=row['package_id'],
                    company_id=row['company_id'],
                    generated_at=datetime.fromisoformat(row['generated_at'].replace('Z', '+00:00')),
                    period_start=datetime.fromisoformat(row['period_start']).date(),
                    period_end=datetime.fromisoformat(row['period_end']).date(),
                    executive_summary={},
                    scan_history=[],
                    violations=[],
                    remediations=[],
                    trends=[],
                    compliance_metrics=None,
                    gdpr_article_mapping={}
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get evidence package from Supabase: {e}")
            return None
    
    def batch_save_violations(self, violations: List[ViolationRecord]) -> bool:
        """Batch save violations for better performance."""
        try:
            violation_data = []
            for violation in violations:
                violation_data.append({
                    'id': violation.id,
                    'scan_id': violation.scan_id,
                    'file_path': str(violation.file_path),
                    'line_number': violation.line_number,
                    'violation_type': violation.violation_type.value if hasattr(violation.violation_type, 'value') else str(violation.violation_type),
                    'severity': violation.severity,
                    'gdpr_article': violation.gdpr_article.value if violation.gdpr_article and hasattr(violation.gdpr_article, 'value') else violation.gdpr_article,
                    'description': violation.description,
                    'matched_text': violation.matched_text,
                    'confidence': violation.confidence,
                    'remediated': violation.remediated,
                    'remediated_at': violation.remediated_at.isoformat() if violation.remediated_at else None,
                    'remediation_commit': violation.remediation_commit,
                    'remediation_type': violation.remediation_type.value if violation.remediation_type and hasattr(violation.remediation_type, 'value') else violation.remediation_type,
                    'remediation_notes': violation.remediation_notes
                })
            
            result = self.client.table('violations').insert(violation_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to batch save violations to Supabase: {e}")
            return False
    
    def close(self):
        """Close real-time connections."""
        if self.realtime_channel:
            self.client.remove_channel(self.realtime_channel)


def get_evidence_store(store_type: str = "local", **kwargs) -> EvidenceStore:
    """Factory function to get evidence store instance."""
    if store_type == "local":
        return LocalEvidenceStore(kwargs.get('base_path'))
    elif store_type == "supabase":
        return SupabaseEvidenceStore(kwargs.get('supabase_client'), kwargs.get('enable_realtime', True))
    elif store_type == "hybrid":
        from .storage_manager import create_hybrid_store
        return create_hybrid_store(
            local_path=kwargs.get('base_path'),
            supabase_client=kwargs.get('supabase_client'),
            enable_cloud=kwargs.get('enable_cloud', True)
        )
    else:
        raise ValueError(f"Unknown store type: {store_type}")
