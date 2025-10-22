"""
Enhanced compliance models for evidence tracking and GDPR analysis.
Extends the existing compliance models with evidence-specific data structures.
"""

import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field
from ..core.config import RiskLevel


class ComplianceLevel(str, Enum):
    """Compliance issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    GDPR = "GDPR"
    CCPA = "CCPA"
    ALL = "ALL"


class ComplianceCategory(str, Enum):
    """Compliance issue categories."""
    SECURITY = "security"
    DATA_MINIMIZATION = "data_minimization"
    CONSENT = "consent"
    DATA_SUBJECT_RIGHTS = "data_subject_rights"
    DATA_RETENTION = "data_retention"
    DATA_TRANSFER = "data_transfer"
    PRIVACY_BY_DESIGN = "privacy_by_design"
    BREACH_NOTIFICATION = "breach_notification"
    CONSUMER_RIGHTS = "consumer_rights"
    OPT_OUT_MECHANISMS = "opt_out_mechanisms"
    NON_DISCRIMINATION = "non_discrimination"


class CCPAArticle(str, Enum):
    """CCPA articles with descriptions and requirements."""
    
    # Consumer Rights
    SECTION_1798_100 = "§1798.100"  # Right to Know
    SECTION_1798_105 = "§1798.105"  # Right to Delete
    SECTION_1798_110 = "§1798.110"  # Right to Opt-Out
    SECTION_1798_115 = "§1798.115"  # Right to Non-Discrimination
    SECTION_1798_120 = "§1798.120"  # Right to Opt-Out of Sale
    SECTION_1798_125 = "§1798.125"  # Non-Discrimination Rights
    
    # Business Obligations
    SECTION_1798_130 = "§1798.130"  # Notice Requirements
    SECTION_1798_135 = "§1798.135"  # Opt-Out Mechanisms
    SECTION_1798_140 = "§1798.140"  # Definitions
    SECTION_1798_145 = "§1798.145"  # Exceptions
    SECTION_1798_150 = "§1798.150"  # Data Security Requirements
    SECTION_1798_155 = "§1798.155"  # Enforcement
    
    @property
    def title(self) -> str:
        """Get article title."""
        titles = {
            self.SECTION_1798_100: "Right to Know",
            self.SECTION_1798_105: "Right to Delete",
            self.SECTION_1798_110: "Right to Opt-Out",
            self.SECTION_1798_115: "Right to Non-Discrimination",
            self.SECTION_1798_120: "Right to Opt-Out of Sale",
            self.SECTION_1798_125: "Non-Discrimination Rights",
            self.SECTION_1798_130: "Notice Requirements",
            self.SECTION_1798_135: "Opt-Out Mechanisms",
            self.SECTION_1798_140: "Definitions",
            self.SECTION_1798_145: "Exceptions",
            self.SECTION_1798_150: "Data Security Requirements",
            self.SECTION_1798_155: "Enforcement"
        }
        return titles.get(self, f"CCPA {self}")
    
    @property
    def description(self) -> str:
        """Get article description."""
        descriptions = {
            self.SECTION_1798_100: "Consumers have the right to know what personal information is collected, used, shared, or sold.",
            self.SECTION_1798_105: "Consumers have the right to request deletion of their personal information.",
            self.SECTION_1798_110: "Consumers have the right to opt-out of the sale of their personal information.",
            self.SECTION_1798_115: "Consumers have the right to non-discrimination for exercising their privacy rights.",
            self.SECTION_1798_120: "Consumers have the right to opt-out of the sale of personal information.",
            self.SECTION_1798_125: "Businesses cannot discriminate against consumers who exercise their privacy rights.",
            self.SECTION_1798_130: "Businesses must provide clear notices about data collection and use.",
            self.SECTION_1798_135: "Businesses must provide easy-to-use opt-out mechanisms.",
            self.SECTION_1798_140: "Definitions of key terms under CCPA.",
            self.SECTION_1798_145: "Exceptions to CCPA requirements.",
            self.SECTION_1798_150: "Businesses must implement reasonable security measures.",
            self.SECTION_1798_155: "Enforcement mechanisms and penalties."
        }
        return descriptions.get(self, f"CCPA {self} requirements")


@dataclass
class FrameworkMapping:
    """Cross-framework violation mapping."""
    violation_type: str
    gdpr_article: Optional[str] = None
    ccpa_article: Optional[str] = None
    description: str = ""
    shared_requirements: List[str] = field(default_factory=list)
    framework_specific_requirements: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DSARRequest:
    id: str
    data_subject_id: str
    request_type: str  # access, rectification, erasure, portability
    status: str  # pending, processing, completed
    created_at: datetime
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class SecurityCheck:
    """Security check result."""
    id: str
    check_type: str
    status: str  # passed, failed, warning
    details: str
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DataTransferInfo:
    """Data transfer information."""
    id: str
    source_country: str
    destination_country: str
    transfer_mechanism: str  # adequacy_decision, standard_contractual_clauses, etc.
    legal_basis: str
    safeguards: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class GDPRArticle(str, Enum):
    """GDPR articles with descriptions and requirements."""
    
    # Data Processing Principles
    ARTICLE_5_1_C = "5(1)(c)"  # Data Minimization
    ARTICLE_5_1_D = "5(1)(d)"  # Accuracy
    ARTICLE_5_1_E = "5(1)(e)"  # Storage Limitation
    
    # Lawful Basis
    ARTICLE_6 = "6"  # Lawful Basis for Processing
    ARTICLE_7 = "7"  # Conditions for Consent
    
    # Individual Rights
    ARTICLE_17 = "17"  # Right to Erasure
    ARTICLE_18 = "18"  # Right to Restriction
    ARTICLE_20 = "20"  # Right to Data Portability
    
    # Security
    ARTICLE_32 = "32"  # Security of Processing
    
    # Records
    ARTICLE_30 = "30"  # Records of Processing Activities
    
    # Breach Notification
    ARTICLE_33 = "33"  # Breach Notification to Supervisory Authority
    ARTICLE_34 = "34"  # Breach Notification to Data Subject
    
    @property
    def title(self) -> str:
        """Get article title."""
        titles = {
            self.ARTICLE_5_1_C: "Data Minimization",
            self.ARTICLE_5_1_D: "Accuracy of Personal Data",
            self.ARTICLE_5_1_E: "Storage Limitation",
            self.ARTICLE_6: "Lawful Basis for Processing",
            self.ARTICLE_7: "Conditions for Consent",
            self.ARTICLE_17: "Right to Erasure",
            self.ARTICLE_18: "Right to Restriction of Processing",
            self.ARTICLE_20: "Right to Data Portability",
            self.ARTICLE_32: "Security of Processing",
            self.ARTICLE_30: "Records of Processing Activities",
            self.ARTICLE_33: "Breach Notification to Supervisory Authority",
            self.ARTICLE_34: "Breach Notification to Data Subject"
        }
        return titles.get(self, f"Article {self}")
    
    @property
    def description(self) -> str:
        """Get article description."""
        descriptions = {
            self.ARTICLE_5_1_C: "Personal data shall be adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed.",
            self.ARTICLE_5_1_D: "Personal data shall be accurate and, where necessary, kept up to date.",
            self.ARTICLE_5_1_E: "Personal data shall be kept in a form which permits identification of data subjects for no longer than is necessary.",
            self.ARTICLE_6: "Processing shall be lawful only if and to the extent that at least one of the lawful bases applies.",
            self.ARTICLE_7: "The controller shall be able to demonstrate that the data subject has consented to processing of his or her personal data.",
            self.ARTICLE_17: "The data subject shall have the right to obtain from the controller the erasure of personal data concerning him or her.",
            self.ARTICLE_18: "The data subject shall have the right to obtain from the controller restriction of processing.",
            self.ARTICLE_20: "The data subject shall have the right to receive the personal data concerning him or her in a structured format.",
            self.ARTICLE_32: "The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk.",
            self.ARTICLE_30: "Each controller and, where applicable, the controller's representative, shall maintain a record of processing activities.",
            self.ARTICLE_33: "In the case of a personal data breach, the controller shall without undue delay and, where feasible, not later than 72 hours notify the supervisory authority.",
            self.ARTICLE_34: "When the personal data breach is likely to result in a high risk to the rights and freedoms of natural persons, the controller shall communicate the breach to the data subject."
        }
        return descriptions.get(self, f"Article {self} requirements")


class RemediationType(str, Enum):
    """Types of remediation actions."""
    FIXED = "fixed"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"
    MITIGATED = "mitigated"


class ViolationType(str, Enum):
    """Types of PII violations."""
    PII_IN_LOGS = "pii_in_logs"
    HARDCODED_CREDENTIALS = "hardcoded_credentials"
    UNENCRYPTED_PII = "unencrypted_pii"
    UNNECESSARY_PII = "unnecessary_pii"
    MISSING_CONSENT = "missing_consent"
    NO_DELETION_MECHANISM = "no_deletion_mechanism"
    PII_IN_COMMENTS = "pii_in_comments"
    PII_IN_CONFIG = "pii_in_config"
    PII_IN_TESTS = "pii_in_tests"
    PII_IN_DOCUMENTATION = "pii_in_documentation"


@dataclass
class ComplianceIssue:
    """A single compliance issue found during analysis."""
    id: str
    file_path: str
    line_number: int
    severity: ComplianceLevel
    article_ref: Union[GDPRArticle, CCPAArticle]
    category: str
    description: str
    evidence: str
    remediation: str
    confidence: float = 0.0
    check_type: str = "unknown"
    created_at: datetime = field(default_factory=datetime.utcnow)
    framework: ComplianceFramework = ComplianceFramework.GDPR
    cross_framework_mappings: Dict[ComplianceFramework, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ComplianceResult:
    """Result of a compliance audit."""
    project_path: str
    audit_timestamp: datetime
    completion_timestamp: datetime
    compliance_score: float
    total_issues: int
    issues_by_severity: Dict[ComplianceLevel, int]
    issues_by_article: Dict[Union[GDPRArticle, CCPAArticle], int]
    detection_result: Any  # DetectionResult
    compliance_issues: List[ComplianceIssue]
    audit_options: Any  # ComplianceAuditOptions
    report: Optional[Dict[str, Any]] = None
    frameworks_analyzed: List[ComplianceFramework] = field(default_factory=list)
    per_framework_scores: Dict[ComplianceFramework, float] = field(default_factory=dict)
    cross_framework_insights: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ComplianceReport:
    """Compliance report structure."""
    id: str
    company_id: str
    report_type: str  # audit, summary, evidence
    generated_at: datetime
    period_start: date
    period_end: date
    compliance_score: float
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    recommendations: List[str]
    executive_summary: str
    detailed_findings: Dict[str, Any]
    file_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CompanyProfile:
    """Company profile for compliance tracking."""
    id: str
    name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None  # small, medium, large, enterprise
    compliance_officer_email: Optional[str] = None
    headquarters_country: Optional[str] = None
    gdpr_applicable: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ScanHistoryEntry:
    """Entry in scan history for evidence tracking."""
    scan_id: str
    company_id: str
    scan_timestamp: datetime
    scan_path: str
    git_commit_hash: Optional[str] = None
    git_branch: Optional[str] = None
    git_author: Optional[str] = None
    total_files: int = 0
    total_violations: int = 0
    critical_violations: int = 0
    high_violations: int = 0
    medium_violations: int = 0
    low_violations: int = 0
    scan_duration_seconds: float = 0.0
    license_tier: str = "starter"
    results_json: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @property
    def violation_summary(self) -> Dict[str, int]:
        """Get violation summary by severity."""
        return {
            'critical': self.critical_violations,
            'high': self.high_violations,
            'medium': self.medium_violations,
            'low': self.low_violations,
            'total': self.total_violations
        }


@dataclass
class ViolationRecord:
    """Record of a specific violation for tracking and remediation."""
    id: str
    scan_id: str
    file_path: str
    line_number: int
    violation_type: ViolationType
    severity: str
    gdpr_article: Optional[GDPRArticle] = None
    description: str = ""
    matched_text: str = ""
    confidence: float = 0.0
    remediated: bool = False
    remediated_at: Optional[datetime] = None
    remediation_commit: Optional[str] = None
    remediation_type: Optional[RemediationType] = None
    remediation_notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class RemediationEvidence:
    """Evidence of remediation for a violation."""
    id: str
    violation_id: str
    remediation_type: RemediationType
    commit_hash: Optional[str] = None
    pr_url: Optional[str] = None
    committed_by: Optional[str] = None
    committed_at: Optional[datetime] = None
    verification_scan_id: Optional[str] = None
    notes: Optional[str] = None
    before_snippet: Optional[str] = None
    after_snippet: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ViolationTrend:
    """Trend analysis for violations over time."""
    period_start: date
    period_end: date
    total_violations: int
    new_violations: int
    remediated_violations: int
    violation_types: Dict[str, int]
    severity_distribution: Dict[str, int]
    gdpr_articles: Dict[str, int]
    improvement_percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ComplianceMetrics:
    """Overall compliance metrics for a company."""
    company_id: str
    period_start: date
    period_end: date
    total_scans: int
    total_violations: int
    critical_violations: int
    compliance_score: float  # 0-100
    trend_direction: str  # improving, stable, declining
    gdpr_article_compliance: Dict[str, float]  # article -> compliance percentage
    risk_level: str  # low, medium, high, critical
    last_scan_date: Optional[datetime] = None
    days_since_last_scan: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EvidencePackage:
    """Complete evidence package for audit."""
    package_id: str
    company_id: str
    generated_at: datetime
    period_start: date
    period_end: date
    executive_summary: Dict[str, Any]
    scan_history: List[ScanHistoryEntry]
    violations: List[ViolationRecord]
    remediations: List[RemediationEvidence]
    trends: List[ViolationTrend]
    compliance_metrics: ComplianceMetrics
    gdpr_article_mapping: Dict[str, List[str]]  # article -> violation_ids
    file_path: Optional[str] = None  # Path to generated PDF/HTML
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class EvidencePackageRequest(BaseModel):
    """Request for generating evidence package."""
    company_id: str
    start_date: date
    end_date: date
    include_remediation_proof: bool = True
    include_trend_analysis: bool = True
    include_gdpr_mapping: bool = True
    format: str = "pdf"  # pdf, html, json
    output_path: Optional[str] = None


class EvidencePackageResponse(BaseModel):
    """Response from evidence package generation."""
    package_id: str
    status: str  # generating, completed, failed
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_size_bytes: Optional[int] = None