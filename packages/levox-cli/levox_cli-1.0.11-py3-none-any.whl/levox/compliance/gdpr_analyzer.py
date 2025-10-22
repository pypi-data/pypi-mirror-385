"""
GDPR Analyzer - Comprehensive GDPR compliance analysis engine.

Implements granular GDPR analysis logic including:
- Article 32 Security Checks
- DSAR Automation detection
- Right to be Forgotten analysis
- Cross-border Data Transfer detection
"""

import re
import ast
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid
import hashlib
from collections import defaultdict

from ..core.config import Config, LicenseTier, DetectionPattern, RiskLevel
from ..core.exceptions import DetectionError
from ..models.detection_result import DetectionResult, FileResult
from ..utils.performance import PerformanceMonitor
from ..utils.file_handler import FileHandler
from ..detection.ast_analyzer import ASTAnalyzer
from ..detection.regex_engine import RegexEngine
from ..detection.context_analyzer import ContextAnalyzer
from ..detection.ml_filter import MLFilter
from ..parsers import get_parser, detect_language
from .models import (
    ComplianceIssue, ComplianceLevel, ComplianceCategory, GDPRArticle,
    DSARRequest, SecurityCheck, DataTransferInfo
)
from .audit_logger import ComplianceAuditLogger


logger = logging.getLogger(__name__)


@dataclass
class GDPRPattern:
    """GDPR-specific detection pattern with comprehensive metadata."""
    name: str
    regex: str
    article_ref: GDPRArticle
    category: ComplianceCategory
    severity: ComplianceLevel
    description: str
    remediation: str
    languages: List[str]
    confidence: float
    false_positive_indicators: List[str] = None


class GDPRAnalyzer:
    """
    Production-grade GDPR compliance analyzer with rule-driven and AST-driven analysis.
    
    Performs comprehensive GDPR compliance checks including security analysis,
    DSAR automation detection, data deletion flows, and cross-border transfer analysis.
    Designed for high-throughput enterprise environments with configurable severity thresholds.
    """
    
    # Critical security patterns that should always be flagged
    CRITICAL_SECURITY_PATTERNS = {
        'weak_crypto': r'\b(?:md5|sha1|des|rc4|rc2|blowfish)(?:\(|\s|$)',
        'hardcoded_secrets': r'(?:password|secret|key|token|api_key)\s*[:=]\s*[\'"][^\'"\s]{8,}[\'"]',
        'sql_injection_risk': r'(?:execute|query|sql)\s*\(\s*[\'"][^\'\"]*\+[^\'\"]*[\'"]',
        'unencrypted_protocols': r'\b(?:http://|ftp://|ws://|telnet://)\b'
    }
    
    # DSAR detection patterns with improved accuracy
    DSAR_PATTERNS = {
        'endpoint_patterns': r'\b(?:dsar|data_subject_access|export_user_data|get_personal_data)\b',
        'api_endpoints': r'(?:/api/)?(?:users?/)?(?:data|export|dsar|personal-data)\b',
        'function_patterns': r'def\s+(?:export_|get_|retrieve_)(?:user_|personal_|)data\s*\('
    }
    
    # Data deletion patterns for Article 17 compliance
    DELETION_PATTERNS = {
        'endpoint_patterns': r'\b(?:delete_user|erase_user|forget_user|purge_data)\b',
        'api_endpoints': r'(?:/api/)?users?/(?:delete|erase|forget|purge)\b',
        'cascade_deletion': r'(?:CASCADE|ON DELETE CASCADE|foreign_key_checks)',
        'soft_delete': r'(?:deleted_at|is_deleted|soft_delete|archived_at)\b'
    }
    
    def __init__(self, config: Config):
        """Initialize the GDPR analyzer with comprehensive pattern loading."""
        self.config = config
        self.license_tier = config.license.tier
        
        # Load GDPR-specific patterns
        self.gdpr_patterns = self._load_gdpr_patterns()
        
        # Initialize detection engines
        self.ast_analyzer = ASTAnalyzer(config)
        self.regex_engine = RegexEngine(self.gdpr_patterns)
        self.context_analyzer = ContextAnalyzer(config)
        
        # Initialize ML filter for false positive reduction (Enterprise tier)
        self.ml_filter = None
        if (self.license_tier == LicenseTier.ENTERPRISE and 
            getattr(config, 'enable_ml', False)):
            try:
                self.ml_filter = MLFilter(config)
                logger.info("ML Filter initialized for GDPR compliance analysis")
            except Exception as e:
                logger.warning(f"ML Filter initialization failed for GDPR analyzer: {e}")
                self.ml_filter = None
        
        # Initialize compliance check registry with proper error handling
        self.compliance_checks = self._initialize_compliance_checks()
        
        # Initialize result caching for performance optimization
        self._pattern_cache = {}
        self._ast_cache = {}
        
        # Initialize audit logger for compliance tracking
        try:
            self.audit_logger = ComplianceAuditLogger(config)
            logger.info("Compliance audit logger initialized successfully")
        except Exception as e:
            logger.warning(f"Compliance audit logger initialization failed: {e}")
            self.audit_logger = None
        
        # Initialize performance monitoring and file handling
        self.performance_monitor = PerformanceMonitor()
        self.file_handler = FileHandler(config)
        
        logger.info(f"GDPR Analyzer initialized with {len(self.gdpr_patterns)} patterns for tier: {self.license_tier}")
    
    def _load_gdpr_patterns(self) -> List[DetectionPattern]:
        """Load comprehensive GDPR-specific detection patterns with enhanced accuracy."""
        
        patterns = [
            # Article 32 - Security of processing (Critical patterns)
            DetectionPattern(
                name="weak_crypto",
                regex=self.CRITICAL_SECURITY_PATTERNS['weak_crypto'],
                confidence=0.95,
                risk_level=RiskLevel.CRITICAL,
                description="Weak cryptographic algorithm detected - violates Article 32 security requirements",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go", "rust", "scala", "kotlin"]
            ),
            DetectionPattern(
                name="hardcoded_secrets",
                regex=self.CRITICAL_SECURITY_PATTERNS['hardcoded_secrets'],
                confidence=0.98,
                risk_level=RiskLevel.CRITICAL,
                description="Hardcoded credentials in source code - severe Article 32 security violation",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go", "rust", "scala", "kotlin"]
            ),
            DetectionPattern(
                name="sql_injection_risk",
                regex=self.CRITICAL_SECURITY_PATTERNS['sql_injection_risk'],
                confidence=0.85,
                risk_level=RiskLevel.CRITICAL,
                description="SQL injection vulnerability detected - Article 32 data integrity violation",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go"]
            ),
            DetectionPattern(
                name="unencrypted_protocols",
                regex=self.CRITICAL_SECURITY_PATTERNS['unencrypted_protocols'],
                confidence=0.90,
                risk_level=RiskLevel.HIGH,
                description="Unencrypted communication protocol - Article 32 transmission security violation",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go", "rust"]
            ),
            
            # Article 15 - Right of access (DSAR) with enhanced detection
            DetectionPattern(
                name="dsar_endpoint",
                regex=self.DSAR_PATTERNS['endpoint_patterns'],
                confidence=0.80,
                risk_level=RiskLevel.MEDIUM,
                description="DSAR endpoint detected - ensure Article 15 compliance requirements are met",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go", "rust"]
            ),
            DetectionPattern(
                name="dsar_api_route",
                regex=self.DSAR_PATTERNS['api_endpoints'],
                confidence=0.75,
                risk_level=RiskLevel.MEDIUM,
                description="Data access API route detected - verify Article 15 implementation",
                languages=["python", "javascript", "java", "php", "ruby", "go"]
            ),
            
            # Article 17 - Right to erasure with comprehensive detection
            DetectionPattern(
                name="user_deletion_endpoint",
                regex=self.DELETION_PATTERNS['endpoint_patterns'],
                confidence=0.85,
                risk_level=RiskLevel.HIGH,
                description="User deletion functionality detected - ensure Article 17 complete erasure",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go", "rust"]
            ),
            DetectionPattern(
                name="cascade_deletion",
                regex=self.DELETION_PATTERNS['cascade_deletion'],
                confidence=0.70,
                risk_level=RiskLevel.MEDIUM,
                description="Database cascade deletion detected - verify Article 17 comprehensive erasure",
                languages=["sql", "python", "java", "php", "csharp"]
            ),
            DetectionPattern(
                name="soft_delete_pattern",
                regex=self.DELETION_PATTERNS['soft_delete'],
                confidence=0.60,
                risk_level=RiskLevel.MEDIUM,
                description="Soft deletion pattern detected - may not comply with Article 17 erasure requirements",
                languages=["python", "javascript", "java", "php", "ruby", "csharp"]
            ),
            
            # Article 44-49 - Cross-border data transfers with improved detection
            DetectionPattern(
                name="third_party_service",
                regex=r'\b(?:aws|azure|gcp|cloudflare|stripe|paypal|mailchimp|sendgrid)\.(?:com|net|io|org)\b',
                confidence=0.85,
                risk_level=RiskLevel.HIGH,
                description="Third-party cloud service detected - verify Article 44-49 transfer safeguards",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go", "rust"]
            ),
            DetectionPattern(
                name="international_api_call",
                regex=r'https?://(?:api\.)?[a-zA-Z0-9-]+\.(?:com|org|net|io)(?!/[a-zA-Z]{2}/)/',
                confidence=0.70,
                risk_level=RiskLevel.MEDIUM,
                description="International API endpoint detected - assess Article 44-49 compliance",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go", "rust"]
            ),
            
            # Article 25 - Data protection by design and default
            DetectionPattern(
                name="excessive_data_collection",
                regex=r'\b(?:collect_all|store_everything|log_all_data|track_everything|comprehensive_logging)\b',
                confidence=0.75,
                risk_level=RiskLevel.MEDIUM,
                description="Excessive data collection pattern - violates Article 25 data minimization",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go"]
            ),
            DetectionPattern(
                name="missing_data_minimization",
                regex=r'\b(?:SELECT \*|fetch_all|get_all_columns|complete_profile)\b',
                confidence=0.60,
                risk_level=RiskLevel.LOW,
                description="Potential data over-retrieval - review Article 25 minimization compliance",
                languages=["sql", "python", "javascript", "java", "php", "ruby"]
            ),
            
            # Article 30 - Records of processing activities
            DetectionPattern(
                name="audit_logging",
                regex=r'\b(?:audit_log|processing_log|gdpr_log|compliance_log|activity_tracker)\b',
                confidence=0.70,
                risk_level=RiskLevel.LOW,
                description="Audit logging detected - ensure Article 30 processing records compliance",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go"]
            ),
            
            # Article 35 - Data Protection Impact Assessment indicators
            DetectionPattern(
                name="high_risk_processing",
                regex=r'\b(?:biometric|genetic|location_tracking|profiling|automated_decision)\b',
                confidence=0.80,
                risk_level=RiskLevel.HIGH,
                description="High-risk processing detected - Article 35 DPIA may be required",
                languages=["python", "javascript", "java", "cpp", "csharp", "php", "ruby", "go"]
            ),
        ]
        
        # Apply license tier filtering with enhanced logic
        filtered_patterns = self._filter_patterns_by_tier(patterns)
        
        logger.info(f"Loaded {len(filtered_patterns)} GDPR patterns for license tier: {self.license_tier}")
        return filtered_patterns
    
    def _filter_patterns_by_tier(self, patterns: List[DetectionPattern]) -> List[DetectionPattern]:
        """Filter patterns based on license tier with comprehensive coverage."""
        if self.license_tier == LicenseTier.STANDARD:
            # Standard tier: Critical and High risk only
            return [p for p in patterns if p.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        elif self.license_tier == LicenseTier.PREMIUM:
            # Premium tier: All except Low risk
            return [p for p in patterns if p.risk_level != RiskLevel.LOW]
        else:
            # Enterprise tier: All patterns
            return patterns
    
    def _initialize_compliance_checks(self) -> Dict[str, callable]:
        """Initialize comprehensive compliance check registry."""
        return {
            "security_checks": self._perform_security_checks,
            "dsar_checks": self._perform_dsar_checks,
            "deletion_checks": self._perform_deletion_checks,
            "transfer_checks": self._perform_transfer_checks,
            "consent_checks": self._perform_consent_checks,
            "retention_checks": self._perform_retention_checks,
            "purpose_limitation_checks": self._perform_purpose_limitation_checks,
            "data_minimization_checks": self._perform_data_minimization_checks,
        }
    
    def analyze_project(self, project_path: Path, detection_result: DetectionResult, 
                       options: Any) -> List[ComplianceIssue]:
        """
        Perform comprehensive GDPR compliance analysis on a project.
        
        Args:
            project_path: Path to the project directory
            detection_result: Results from standard PII detection
            options: Compliance audit options with granular controls
            
        Returns:
            List of prioritized compliance issues found
        """
        logger.info(f"Starting GDPR compliance analysis for project: {project_path}")
        
        all_issues = []
        analysis_start = datetime.now()
        
        # Start performance monitoring
        perf_start = self.performance_monitor.start_operation("gdpr_compliance_analysis")
        
        # Log audit entry for compliance analysis start
        if self.audit_logger:
            try:
                self.audit_logger.log_compliance_analysis_start(
                    project_path=str(project_path),
                    license_tier=self.license_tier.value,
                    options=options
                )
            except Exception as e:
                logger.debug(f"Failed to log audit start: {e}")
        
        try:
            # Phase 1: Pattern-based analysis (always enabled)
            logger.debug("Running pattern-based compliance checks")
            pattern_issues = self._run_pattern_checks(project_path)
            all_issues.extend(pattern_issues)
            
            # Phase 2: AST-based analysis (premium+ tiers only)
            if (options.include_security_checks and 
                self.license_tier in [LicenseTier.PREMIUM, LicenseTier.ENTERPRISE]):
                logger.debug("Running AST-based compliance checks")
                ast_issues = self._run_ast_checks(project_path)
                all_issues.extend(ast_issues)
            
            # Phase 3: Context-aware analysis
            logger.debug("Running context-aware compliance checks")
            context_issues = self._run_context_checks(project_path, detection_result)
            all_issues.extend(context_issues)
            
            # Phase 4: Specific compliance domain checks
            check_mapping = [
                (options.include_security_checks, self._perform_security_checks),
                (options.include_dsar_checks, self._perform_dsar_checks),
                (options.include_deletion_checks, self._perform_deletion_checks),
                (options.include_transfer_checks, self._perform_transfer_checks),
                (getattr(options, 'include_consent_checks', True), self._perform_consent_checks),
                (getattr(options, 'include_retention_checks', True), self._perform_retention_checks),
            ]
            
            for should_run, check_func in check_mapping:
                if should_run:
                    try:
                        domain_issues = check_func(project_path)
                        all_issues.extend(domain_issues)
                    except Exception as e:
                        logger.error(f"Compliance check {check_func.__name__} failed: {e}")
                        continue
            
            # Phase 5: Issue processing and validation
            logger.debug("Processing and validating compliance issues")
            unique_issues = self._deduplicate_issues(all_issues)
            validated_issues = self._validate_issues(unique_issues)
            
            # Phase 6: ML-based false positive reduction (Enterprise only)
            ml_filtered_issues = validated_issues
            if self.ml_filter and self.license_tier == LicenseTier.ENTERPRISE:
                try:
                    logger.debug("Applying ML-based false positive reduction")
                    ml_filtered_issues = self._apply_ml_filtering(validated_issues, project_path)
                except Exception as e:
                    logger.warning(f"ML filtering failed for compliance issues: {e}")
                    ml_filtered_issues = validated_issues
            
            prioritized_issues = self._prioritize_issues(ml_filtered_issues)
            
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            
            # Complete performance monitoring
            self.performance_monitor.end_operation(perf_start)
            self.performance_monitor.record_operation("gdpr_compliance_analysis", analysis_duration, len(prioritized_issues))
            
            logger.info(f"GDPR compliance analysis completed in {analysis_duration:.2f}s. "
                       f"Found {len(prioritized_issues)} validated issues.")
            
            # Log audit entry for compliance analysis completion
            if self.audit_logger:
                try:
                    self.audit_logger.log_compliance_analysis_complete(
                        project_path=str(project_path),
                        total_issues=len(prioritized_issues),
                        critical_issues=len([i for i in prioritized_issues if i.severity == ComplianceLevel.CRITICAL]),
                        high_issues=len([i for i in prioritized_issues if i.severity == ComplianceLevel.HIGH]),
                        medium_issues=len([i for i in prioritized_issues if i.severity == ComplianceLevel.MEDIUM]),
                        low_issues=len([i for i in prioritized_issues if i.severity == ComplianceLevel.LOW]),
                        analysis_duration=analysis_duration,
                        license_tier=self.license_tier.value
                    )
                except Exception as e:
                    logger.debug(f"Failed to log audit completion: {e}")
            
            return prioritized_issues
            
        except DetectionError:
            # Re-raise DetectionError without wrapping
            raise
        except Exception as e:
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            
            # Complete performance monitoring even on failure
            try:
                self.performance_monitor.end_operation(perf_start)
                self.performance_monitor.record_operation("gdpr_compliance_analysis_error", analysis_duration, 0)
            except Exception:
                pass
            
            # Log audit entry for failure
            if self.audit_logger:
                try:
                    self.audit_logger.log_compliance_analysis_error(
                        project_path=str(project_path),
                        error_message=str(e),
                        analysis_duration=analysis_duration,
                        license_tier=self.license_tier.value
                    )
                except Exception:
                    pass
            
            logger.error(f"GDPR compliance analysis failed: {e}", exc_info=True)
            raise DetectionError(f"GDPR analysis failed: {str(e)}")
    
    def _run_pattern_checks(self, project_path: Path) -> List[ComplianceIssue]:
        """Run optimized pattern-based GDPR compliance checks."""
        issues = []
        
        for pattern in self.gdpr_patterns:
            try:
                # Use caching for performance optimization
                cache_key = f"{pattern.name}:{str(project_path)}"
                if cache_key in self._pattern_cache:
                    matches = self._pattern_cache[cache_key]
                else:
                    # Use the regex engine's scan method for pattern matching
                    matches = self._scan_project_for_pattern(project_path, pattern.regex)
                    self._pattern_cache[cache_key] = matches
                
                for match in matches:
                    # Map DetectionPattern to GDPRArticle and ComplianceCategory
                    article_ref, category = self._map_pattern_to_gdpr(pattern)
                    severity = self._map_risk_to_compliance_level(pattern.risk_level)
                    
                    issue = ComplianceIssue(
                        id=str(uuid.uuid4()),
                        severity=severity,
                        article_ref=article_ref,
                        category=category,
                        description=pattern.description,
                        location=match.get('file_path', ''),
                        line_number=match.get('line_number'),
                        column_start=match.get('column_start'),
                        column_end=match.get('column_end'),
                        file_path=match.get('file_path'),
                        remediation_suggestion=self._get_enhanced_remediation(pattern, match),
                        evidence=match.get('matched_text', ''),
                        metadata={
                            'pattern_name': pattern.name,
                            'confidence': pattern.confidence,
                            'detection_method': 'pattern_matching',
                            'languages': pattern.languages,
                            'match_context': match.get('context', '')
                        }
                    )
                    issues.append(issue)
                    
                    # Log individual compliance issue to audit trail
                    if self.audit_logger:
                        try:
                            self.audit_logger.log_compliance_issue_detected(issue)
                        except Exception as e:
                            logger.debug(f"Failed to log compliance issue to audit: {e}")
                    
            except Exception as e:
                logger.warning(f"Pattern check failed for {pattern.name}: {e}")
                continue
        
        return issues
    
    def _scan_project_for_pattern(self, project_path: Path, pattern: str) -> List[Dict]:
        """Scan entire project for a specific pattern with caching."""
        cache_key = f"{pattern}:{str(project_path)}"
        
        if cache_key in self._pattern_cache:
            return self._pattern_cache[cache_key]
        
        try:
            matches = self.regex_engine.scan_pattern_in_directory(
                str(project_path), 
                pattern, 
                "project_scan"
            )
            self._pattern_cache[cache_key] = matches
            return matches
        except Exception as e:
            logger.debug(f"Pattern scan failed for {pattern}: {e}")
            return []
    
    def _validate_issues(self, issues: List[ComplianceIssue]) -> List[ComplianceIssue]:
        """Validate and filter compliance issues to reduce false positives."""
        validated_issues = []
        
        for issue in issues:
            try:
                # Validate file existence
                if issue.file_path and not Path(issue.file_path).exists():
                    continue
                
                # Validate evidence quality
                if not issue.evidence or len(issue.evidence.strip()) < 3:
                    continue
                
                # Check for false positive indicators
                if self._is_likely_false_positive(issue):
                    logger.debug(f"Filtering likely false positive: {issue.description}")
                    continue
                
                # Enhance issue with additional context
                enhanced_issue = self._enhance_issue_context(issue)
                validated_issues.append(enhanced_issue)
                
            except Exception as e:
                logger.debug(f"Issue validation failed: {e}")
                continue
        
        return validated_issues
    
    def _is_likely_false_positive(self, issue: ComplianceIssue) -> bool:
        """Determine if an issue is likely a false positive."""
        false_positive_indicators = {
            'test_files': ['/test/', '/tests/', '_test.', '.test.', 'spec.'],
            'documentation': ['/docs/', '/doc/', 'readme', '.md', '.txt'],
            'examples': ['/example/', '/examples/', 'demo', 'sample'],
            'comments': ['#', '//', '/*', '<!--'],
            'mock_data': ['mock', 'fake', 'dummy', 'placeholder']
        }
        
        file_path_lower = issue.file_path.lower() if issue.file_path else ""
        evidence_lower = issue.evidence.lower() if issue.evidence else ""
        
        # Check if issue is in test or documentation files
        for category, indicators in false_positive_indicators.items():
            for indicator in indicators:
                if indicator in file_path_lower or indicator in evidence_lower:
                    return True
        
        return False
    
    def _enhance_issue_context(self, issue: ComplianceIssue) -> ComplianceIssue:
        """Enhance issue with additional contextual information."""
        try:
            # Add file context
            if issue.file_path and Path(issue.file_path).exists():
                file_size = Path(issue.file_path).stat().st_size
                issue.metadata['file_size'] = file_size
                issue.metadata['file_extension'] = Path(issue.file_path).suffix
            
            # Add timestamp
            issue.metadata['detection_timestamp'] = datetime.now().isoformat()
            
            # Add confidence scoring
            issue.metadata['confidence_score'] = self._calculate_confidence_score(issue)
            
        except Exception as e:
            logger.debug(f"Issue enhancement failed: {e}")
        
        return issue
    
    def _calculate_confidence_score(self, issue: ComplianceIssue) -> float:
        """Calculate confidence score for an issue based on multiple factors."""
        base_confidence = 0.7
        
        # Adjust based on detection method
        method_confidence = {
            'pattern_matching': 0.8,
            'ast_analysis': 0.9,
            'context_analysis': 0.7,
            'security_analysis': 0.85
        }
        
        detection_method = issue.metadata.get('detection_method', 'unknown')
        confidence = method_confidence.get(detection_method, base_confidence)
        
        # Adjust based on severity
        severity_multiplier = {
            ComplianceLevel.CRITICAL: 1.0,
            ComplianceLevel.HIGH: 0.95,
            ComplianceLevel.MEDIUM: 0.85,
            ComplianceLevel.LOW: 0.75
        }
        
        confidence *= severity_multiplier.get(issue.severity, 0.8)
        
        # Adjust based on evidence quality
        if issue.evidence:
            if len(issue.evidence) > 50:
                confidence += 0.05
            if any(keyword in issue.evidence.lower() for keyword in ['password', 'secret', 'key']):
                confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _prioritize_issues(self, issues: List[ComplianceIssue]) -> List[ComplianceIssue]:
        """Prioritize issues based on risk, confidence, and business impact."""
        def priority_score(issue: ComplianceIssue) -> float:
            # Base score from severity
            severity_scores = {
                ComplianceLevel.CRITICAL: 100,
                ComplianceLevel.HIGH: 75,
                ComplianceLevel.MEDIUM: 50,
                ComplianceLevel.LOW: 25
            }
            
            base_score = severity_scores.get(issue.severity, 25)
            
            # Adjust for article importance
            article_weights = {
                GDPRArticle.ARTICLE_32: 1.2,  # Security is critical
                GDPRArticle.ARTICLE_15: 1.1,  # DSAR is important
                GDPRArticle.ARTICLE_17: 1.1,  # Right to be forgotten
                GDPRArticle.ARTICLE_6: 1.05,  # Lawful basis
                GDPRArticle.ARTICLE_44: 1.0   # Data transfers
            }
            
            article_weight = article_weights.get(issue.article_ref, 1.0)
            
            # Adjust for confidence
            confidence = issue.metadata.get('confidence_score', 0.7)
            
            return base_score * article_weight * confidence
        
        # Sort by priority score (descending)
        return sorted(issues, key=priority_score, reverse=True)
    
    def _deduplicate_issues(self, issues: List[ComplianceIssue]) -> List[ComplianceIssue]:
        """Remove duplicate compliance issues using enhanced deduplication logic."""
        seen = set()
        unique_issues = []
        issue_groups = defaultdict(list)
        
        # Group similar issues
        for issue in issues:
            group_key = (
                issue.article_ref,
                issue.category,
                issue.severity,
                self._normalize_description(issue.description)
            )
            issue_groups[group_key].append(issue)
        
        # Select best representative from each group
        for group_key, group_issues in issue_groups.items():
            if len(group_issues) == 1:
                unique_issues.append(group_issues[0])
            else:
                # Select issue with highest confidence or most specific location
                best_issue = max(group_issues, key=lambda i: (
                    i.metadata.get('confidence_score', 0.5),
                    bool(i.line_number),
                    len(i.evidence) if i.evidence else 0
                ))
                
                # Aggregate metadata from similar issues
                best_issue.metadata['similar_issues_count'] = len(group_issues)
                best_issue.metadata['aggregated_locations'] = [
                    i.location for i in group_issues if i.location != best_issue.location
                ][:5]  # Limit to 5 for brevity
                
                unique_issues.append(best_issue)
        
        logger.debug(f"Deduplicated {len(issues)} issues to {len(unique_issues)} unique issues")
        return unique_issues
    
    def _normalize_description(self, description: str) -> str:
        """Normalize issue descriptions for better deduplication."""
        # Remove file-specific details and normalize whitespace
        normalized = re.sub(r'\b[a-zA-Z0-9_/\\.-]+\.(py|js|java|php|rb|go|rs)\b', '[FILE]', description)
        normalized = re.sub(r'\bline \d+\b', 'line [NUM]', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip().lower()
        return normalized
    
    def generate_compliance_report(self, issues: List[ComplianceIssue], 
                                 project_path: Path) -> Dict[str, Any]:
        """Generate comprehensive compliance report with metrics and recommendations."""
        report = {
            'project_path': str(project_path),
            'analysis_timestamp': datetime.now().isoformat(),
            'total_issues': len(issues),
            'license_tier': self.license_tier.value,
            'summary': self._generate_summary_metrics(issues),
            'issues_by_severity': self._group_issues_by_severity(issues),
            'issues_by_article': self._group_issues_by_article(issues),
            'issues_by_category': self._group_issues_by_category(issues),
            'compliance_score': self._calculate_compliance_score(issues),
            'recommendations': self._generate_recommendations(issues),
            'detailed_issues': [self._serialize_issue(issue) for issue in issues[:50]]  # Limit for size
        }
        
        return report
    
    def _generate_summary_metrics(self, issues: List[ComplianceIssue]) -> Dict[str, Any]:
        """Generate summary metrics for the compliance report."""
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for issue in issues:
            severity_counts[issue.severity.value] += 1
            category_counts[issue.category.value] += 1
        
        return {
            'severity_distribution': dict(severity_counts),
            'category_distribution': dict(category_counts),
            'most_common_severity': max(severity_counts.items(), key=lambda x: x[1])[0] if severity_counts else None,
            'most_common_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        }
    
    def _group_issues_by_severity(self, issues: List[ComplianceIssue]) -> Dict[str, List[str]]:
        """Group issues by severity level."""
        groups = defaultdict(list)
        for issue in issues:
            groups[issue.severity.value].append({
                'id': issue.id,
                'description': issue.description,
                'article': issue.article_ref.value,
                'location': issue.location
            })
        return dict(groups)
    
    def _group_issues_by_article(self, issues: List[ComplianceIssue]) -> Dict[str, int]:
        """Group and count issues by GDPR article."""
        article_counts = defaultdict(int)
        for issue in issues:
            article_counts[issue.article_ref.value] += 1
        return dict(article_counts)
    
    def _group_issues_by_category(self, issues: List[ComplianceIssue]) -> Dict[str, int]:
        """Group and count issues by compliance category."""
        category_counts = defaultdict(int)
        for issue in issues:
            category_counts[issue.category.value] += 1
        return dict(category_counts)
    
    def _calculate_compliance_score(self, issues: List[ComplianceIssue]) -> float:
        """Calculate overall compliance score (0-100)."""
        if not issues:
            return 100.0
        
        # Penalty weights by severity
        penalty_weights = {
            ComplianceLevel.CRITICAL: 25,
            ComplianceLevel.HIGH: 15,
            ComplianceLevel.MEDIUM: 8,
            ComplianceLevel.LOW: 3
        }
        
        total_penalty = sum(penalty_weights.get(issue.severity, 5) for issue in issues)
        
        # Calculate score with diminishing returns
        max_penalty = 100
        normalized_penalty = min(total_penalty, max_penalty)
        compliance_score = max(0, 100 - normalized_penalty)
        
        return round(compliance_score, 2)
    
    def _generate_recommendations(self, issues: List[ComplianceIssue]) -> List[str]:
        """Generate actionable recommendations based on detected issues."""
        recommendations = []
        
        # Analyze issue patterns
        severity_counts = defaultdict(int)
        article_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for issue in issues:
            severity_counts[issue.severity] += 1
            article_counts[issue.article_ref] += 1
            category_counts[issue.category] += 1
        
        # Generate priority recommendations
        if severity_counts[ComplianceLevel.CRITICAL] > 0:
            recommendations.append("🚨 URGENT: Address critical security vulnerabilities immediately - these pose immediate GDPR compliance risks")
        
        if article_counts[GDPRArticle.ARTICLE_32] > 5:
            recommendations.append("🔒 Implement comprehensive security framework including encryption, access controls, and audit logging")
        
        if article_counts[GDPRArticle.ARTICLE_15] > 0 and article_counts[GDPRArticle.ARTICLE_17] > 0:
            recommendations.append("👤 Establish complete data subject rights infrastructure (DSAR + Right to be Forgotten)")
        
        if category_counts[ComplianceCategory.DATA_TRANSFER] > 3:
            recommendations.append("🌍 Review and document all international data transfers with appropriate safeguards")
        
        if category_counts[ComplianceCategory.SECURITY] > 10:
            recommendations.append("🛡️ Conduct comprehensive security audit and implement defense-in-depth strategy")
        
        # General recommendations
        recommendations.extend([
            "📋 Document all personal data processing activities as required by Article 30",
            "🎯 Implement privacy by design principles in all data processing systems",
            "🔄 Establish regular GDPR compliance monitoring and assessment procedures"
        ])
        
        return recommendations[:8]  # Limit to most important recommendations
    
    def _serialize_issue(self, issue: ComplianceIssue) -> Dict[str, Any]:
        """Serialize compliance issue for report generation."""
        return {
            'id': issue.id,
            'severity': issue.severity.value,
            'article': issue.article_ref.value,
            'category': issue.category.value,
            'description': issue.description,
            'location': issue.location,
            'line_number': issue.line_number,
            'evidence': issue.evidence[:200] if issue.evidence else None,  # Truncate for size
            'remediation': issue.remediation_suggestion,
            'confidence_score': issue.metadata.get('confidence_score'),
            'detection_method': issue.metadata.get('detection_method')
        }
    
    def export_issues_csv(self, issues: List[ComplianceIssue], output_path: Path) -> None:
        """Export compliance issues to CSV format for external analysis."""
        try:
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'ID', 'Severity', 'Article', 'Category', 'Description',
                    'File Path', 'Line Number', 'Evidence', 'Remediation',
                    'Confidence Score', 'Detection Method'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for issue in issues:
                    writer.writerow({
                        'ID': issue.id,
                        'Severity': issue.severity.value,
                        'Article': issue.article_ref.value,
                        'Category': issue.category.value,
                        'Description': issue.description,
                        'File Path': issue.file_path,
                        'Line Number': issue.line_number,
                        'Evidence': issue.evidence,
                        'Remediation': issue.remediation_suggestion,
                        'Confidence Score': issue.metadata.get('confidence_score', ''),
                        'Detection Method': issue.metadata.get('detection_method', '')
                    })
            
            logger.info(f"Exported {len(issues)} compliance issues to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export issues to CSV: {e}")
            raise DetectionError(f"CSV export failed: {e}")
    
    def clear_caches(self) -> None:
        """Clear internal caches to free memory."""
        self._pattern_cache.clear()
        self._ast_cache.clear()
        logger.debug("GDPR Analyzer caches cleared")
    
    def _map_pattern_to_gdpr(self, pattern: DetectionPattern) -> Tuple[GDPRArticle, ComplianceCategory]:
        """Map detection patterns to specific GDPR articles and categories."""
        pattern_mappings = {
            'weak_crypto': (GDPRArticle.ARTICLE_32, ComplianceCategory.SECURITY),
            'hardcoded_secrets': (GDPRArticle.ARTICLE_32, ComplianceCategory.SECURITY),
            'sql_injection_risk': (GDPRArticle.ARTICLE_32, ComplianceCategory.SECURITY),
            'unencrypted_protocols': (GDPRArticle.ARTICLE_32, ComplianceCategory.SECURITY),
            'dsar_endpoint': (GDPRArticle.ARTICLE_15, ComplianceCategory.DATA_RIGHTS),
            'dsar_api_route': (GDPRArticle.ARTICLE_15, ComplianceCategory.DATA_RIGHTS),
            'user_deletion_endpoint': (GDPRArticle.ARTICLE_17, ComplianceCategory.DATA_RIGHTS),
            'cascade_deletion': (GDPRArticle.ARTICLE_17, ComplianceCategory.DATA_RIGHTS),
            'soft_delete_pattern': (GDPRArticle.ARTICLE_17, ComplianceCategory.DATA_RIGHTS),
            'third_party_service': (GDPRArticle.ARTICLE_44, ComplianceCategory.DATA_TRANSFER),
            'international_api_call': (GDPRArticle.ARTICLE_44, ComplianceCategory.DATA_TRANSFER),
            'excessive_data_collection': (GDPRArticle.ARTICLE_25, ComplianceCategory.DATA_PROTECTION_BY_DESIGN),
            'missing_data_minimization': (GDPRArticle.ARTICLE_25, ComplianceCategory.DATA_PROTECTION_BY_DESIGN),
            'audit_logging': (GDPRArticle.ARTICLE_30, ComplianceCategory.ACCOUNTABILITY),
            'high_risk_processing': (GDPRArticle.ARTICLE_35, ComplianceCategory.RISK_ASSESSMENT),
        }
        
        return pattern_mappings.get(pattern.name, (GDPRArticle.GENERAL, ComplianceCategory.GENERAL))
    
    def _map_risk_to_compliance_level(self, risk_level: RiskLevel) -> ComplianceLevel:
        """Map risk levels to compliance severity levels."""
        mapping = {
            RiskLevel.CRITICAL: ComplianceLevel.CRITICAL,
            RiskLevel.HIGH: ComplianceLevel.HIGH,
            RiskLevel.MEDIUM: ComplianceLevel.MEDIUM,
            RiskLevel.LOW: ComplianceLevel.LOW
        }
        return mapping.get(risk_level, ComplianceLevel.MEDIUM)
    
    def _get_enhanced_remediation(self, pattern: DetectionPattern, match: Dict) -> str:
        """Generate context-specific remediation suggestions."""
        base_suggestions = {
            'weak_crypto': "Replace with strong cryptographic algorithms (SHA-256, AES-256, RSA-2048+). Use established cryptographic libraries.",
            'hardcoded_secrets': "Move sensitive credentials to environment variables or secure key management systems (AWS KMS, HashiCorp Vault).",
            'sql_injection_risk': "Use parameterized queries, prepared statements, or ORM methods to prevent SQL injection vulnerabilities.",
            'unencrypted_protocols': "Replace with encrypted protocols (HTTPS, SFTP, WSS). Implement TLS 1.2+ for all data transmission.",
            'dsar_endpoint': "Ensure DSAR endpoint includes user authentication, comprehensive data export, and response within 30 days.",
            'user_deletion_endpoint': "Implement complete data erasure including backups, logs, and third-party systems. Verify cascade deletion.",
            'third_party_service': "Verify third-party has adequate safeguards (SCCs, BCRs, adequacy decision) for international transfers.",
            'excessive_data_collection': "Implement data minimization - collect only necessary data for specified purposes. Review data collection scope.",
        }
        
        base = base_suggestions.get(pattern.name, "Review implementation for GDPR compliance requirements.")
        
        # Add context-specific guidance
        file_extension = Path(match.get('file_path', '')).suffix
        if file_extension in ['.sql', '.py', '.js']:
            if 'database' in match.get('context', '').lower():
                base += " Ensure database-level security controls are implemented."
        
        return base
    
    def _run_ast_checks(self, project_path: Path) -> List[ComplianceIssue]:
        """Run comprehensive AST-based GDPR compliance checks."""
        issues = []
        
        try:
            # Analyze Python files
            python_files = list(project_path.rglob("*.py"))
            for py_file in python_files:
                try:
                    file_issues = self._analyze_python_file_ast(py_file)
                    issues.extend(file_issues)
                except Exception as e:
                    logger.debug(f"AST analysis failed for {py_file}: {e}")
                    continue
            
            # Analyze JavaScript files for enterprise tier
            if self.license_tier == LicenseTier.ENTERPRISE:
                js_files = list(project_path.rglob("*.js")) + list(project_path.rglob("*.ts"))
                for js_file in js_files:
                    try:
                        file_issues = self._analyze_javascript_file_ast(js_file)
                        issues.extend(file_issues)
                    except Exception as e:
                        logger.debug(f"JavaScript AST analysis failed for {js_file}: {e}")
                        continue
                        
        except Exception as e:
            logger.warning(f"AST analysis failed: {e}")
        
        return issues
    
    def _run_context_checks(self, project_path: Path, detection_result: DetectionResult) -> List[ComplianceIssue]:
        """Run sophisticated context-based GDPR compliance checks."""
        issues = []
        
        try:
            # Analyze PII context for compliance implications
            for file_result in detection_result.file_results:
                if file_result.matches:
                    context_issues = self._analyze_pii_context_comprehensive(file_result)
                    issues.extend(context_issues)
            
            # Cross-file analysis for data flow tracking
            if self.license_tier == LicenseTier.ENTERPRISE:
                flow_issues = self._analyze_data_flow_patterns(project_path, detection_result)
                issues.extend(flow_issues)
                    
        except Exception as e:
            logger.warning(f"Context analysis failed: {e}")
        
        return issues
    
    def _analyze_python_file_ast(self, file_path: Path) -> List[ComplianceIssue]:
        """Analyze Python file AST for GDPR compliance issues using enhanced parser."""
        issues = []
        
        try:
            # Use FileHandler for safe file reading
            content = self.file_handler.read_file(file_path)
            if content is None:
                logger.warning(f"Failed to read file for AST analysis: {file_path}")
                return []
            
            # Normalize modern Python syntax (e.g., PEP 695) for Python 3.11 compatibility
            try:
                from ..utils.python_syntax import normalize_modern_syntax
                content = normalize_modern_syntax(content)
            except Exception as e:
                logger.debug(f"Syntax normalization skipped due to error: {e}")
            
            # Try to use enhanced parser first
            parser = get_parser(file_path, content, self.config)
            if parser:
                enhanced_issues = self._analyze_with_enhanced_parser(parser, file_path, content)
                issues.extend(enhanced_issues)
            
            # Fallback to traditional AST analysis with safe error handling
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as se:
                logger.debug(f"Skipping file due to syntax error in fallback AST parse: {file_path}: {se}")
                return []
            except Exception as pe:
                logger.debug(f"Skipping file due to parser error in fallback AST parse: {file_path}: {pe}")
                return []
            
            class GDPRComplianceVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.issues = []
                    self.imports = set()
                    self.functions = {}
                    self.classes = {}
                
                def visit_Import(self, node):
                    for alias in node.names:
                        self.imports.add(alias.name)
                    self.generic_visit(node)
                
                def visit_ImportFrom(self, node):
                    if node.module:
                        self.imports.add(node.module)
                    self.generic_visit(node)
                
                def visit_FunctionDef(self, node):
                    self.functions[node.name] = node
                    
                    # DSAR function detection
                    if any(keyword in node.name.lower() for keyword in 
                          ['dsar', 'export', 'access', 'personal_data', 'user_data']):
                        if not self._has_security_checks(node):
                            self.issues.append(self._create_issue(
                                GDPRArticle.ARTICLE_15, ComplianceCategory.DATA_RIGHTS,
                                "DSAR function lacks proper authentication/authorization checks",
                                file_path, node.lineno,
                                f"Function '{node.name}' handles personal data without security validation",
                                "Implement user authentication, authorization, and request validation before data export"
                            ))
                    
                    # Deletion function detection
                    if any(keyword in node.name.lower() for keyword in 
                          ['delete', 'remove', 'erase', 'purge', 'forget']):
                        if not self._has_cascade_logic(node):
                            self.issues.append(self._create_issue(
                                GDPRArticle.ARTICLE_17, ComplianceCategory.DATA_RIGHTS,
                                "Deletion function may not ensure complete data erasure",
                                file_path, node.lineno,
                                f"Function '{node.name}' lacks comprehensive deletion logic",
                                "Implement cascade deletion for related data, including backups and logs"
                            ))
                    
                    self.generic_visit(node)
                
                def visit_Call(self, node):
                    # Check for insecure crypto usage
                    if isinstance(node.func, ast.Attribute):
                        if (hasattr(node.func.value, 'id') and 
                            node.func.value.id in ['hashlib', 'Crypto'] and
                            node.func.attr in ['md5', 'sha1']):
                            self.issues.append(self._create_issue(
                                GDPRArticle.ARTICLE_32, ComplianceCategory.SECURITY,
                                "Weak cryptographic function detected",
                                file_path, node.lineno,
                                f"Using {node.func.attr} which is cryptographically weak",
                                "Use SHA-256, SHA-512, or other strong hash functions"
                            ))
                    
                    # Check for external API calls
                    if isinstance(node.func, ast.Attribute) and node.func.attr in ['get', 'post', 'request']:
                        for arg in node.args:
                            if isinstance(arg, ast.Str) and ('://' in arg.s):
                                if not arg.s.startswith('https://'):
                                    self.issues.append(self._create_issue(
                                        GDPRArticle.ARTICLE_32, ComplianceCategory.SECURITY,
                                        "Unencrypted HTTP request detected",
                                        file_path, node.lineno,
                                        f"HTTP request to {arg.s[:50]}...",
                                        "Use HTTPS for all external communications"
                                    ))
                    
                    self.generic_visit(node)
                
                def _has_security_checks(self, func_node: ast.FunctionDef) -> bool:
                    """Check if function has basic security validation."""
                    security_keywords = ['authenticate', 'authorize', 'permission', 'token', 'login']
                    func_body = ast.dump(func_node)
                    return any(keyword in func_body.lower() for keyword in security_keywords)
                
                def _has_cascade_logic(self, func_node: ast.FunctionDef) -> bool:
                    """Check if deletion function has cascade deletion logic."""
                    cascade_keywords = ['cascade', 'related', 'foreign', 'reference', 'dependent']
                    func_body = ast.dump(func_node)
                    return any(keyword in func_body.lower() for keyword in cascade_keywords)
                
                def _create_issue(self, article: GDPRArticle, category: ComplianceCategory,
                                description: str, file_path: Path, line_number: int,
                                evidence: str, remediation: str) -> ComplianceIssue:
                    """Create a compliance issue from AST analysis."""
                    return ComplianceIssue(
                        id=str(uuid.uuid4()),
                        severity=ComplianceLevel.HIGH,
                        article_ref=article,
                        category=category,
                        description=description,
                        location=str(file_path),
                        line_number=line_number,
                        file_path=str(file_path),
                        remediation_suggestion=remediation,
                        evidence=evidence,
                        metadata={
                            'detection_method': 'ast_analysis',
                            'language': 'python',
                            'analysis_type': 'function_analysis'
                        }
                    )
            
            visitor = GDPRComplianceVisitor()
            visitor.visit(tree)
            issues.extend(visitor.issues)
            
        except SyntaxError as e:
            logger.debug(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.debug(f"AST analysis error for {file_path}: {e}")
        
        return issues

    def analyze_compliance(self, results: 'DetectionResult') -> List['ComplianceIssue']:
        """Analyze GDPR compliance using a DetectionResult entrypoint.

        This mirrors the internal analyze_project phases, but sources inputs
        from the provided detection results so the framework engine can call it.
        """
        try:
            all_issues: List[ComplianceIssue] = []

            # Derive a project path from detection results
            project_path: Path
            try:
                if getattr(results, 'scan_path', None):
                    project_path = Path(getattr(results, 'scan_path'))
                elif results.file_results:
                    project_path = Path(results.file_results[0].file_path).parent
                else:
                    project_path = Path('.')
            except Exception:
                project_path = Path('.')

            # Phase 1: Pattern-based analysis (always enabled)
            try:
                pattern_issues = self._run_pattern_checks(project_path)
                all_issues.extend(pattern_issues)
            except Exception as e:
                logger.error(f"Pattern checks failed: {e}")

            # Phase 2: AST-based analysis (Pro+/Enterprise)
            try:
                ast_issues = self._run_ast_checks(project_path)
                all_issues.extend(ast_issues)
            except Exception as e:
                logger.debug(f"AST checks skipped/failed: {e}")

            # Phase 3: Context-aware analysis using detection results
            try:
                context_issues = self._run_context_checks(project_path, results)
                all_issues.extend(context_issues)
            except Exception as e:
                logger.debug(f"Context checks failed: {e}")

            # Phase 4: Domain-specific checks (security, DSAR, deletion, transfers, consent, retention)
            domain_checks = [
                self._perform_security_checks,
                self._perform_dsar_checks,
                self._perform_deletion_checks,
                self._perform_transfer_checks,
                self._perform_consent_checks,
                self._perform_retention_checks,
            ]
            for check in domain_checks:
                try:
                    all_issues.extend(check(project_path))
                except Exception as e:
                    logger.debug(f"Domain check {check.__name__} failed: {e}")

            # Phase 5: Deduplicate and validate
            try:
                unique_issues = self._deduplicate_issues(all_issues)
                validated_issues = self._validate_issues(unique_issues)
            except Exception as e:
                logger.debug(f"Issue validation failed: {e}")
                validated_issues = all_issues

            # Phase 6: Enterprise ML-based false positive reduction when available
            final_issues = validated_issues
            try:
                if self.ml_filter and self.license_tier == LicenseTier.ENTERPRISE:
                    final_issues = self._apply_ml_filtering(validated_issues, project_path)
            except Exception as e:
                logger.debug(f"ML filtering failed: {e}")

            return final_issues

        except Exception as e:
            logger.error(f"Failed to analyze GDPR compliance from results: {e}")
            raise DetectionError(f"GDPR compliance analysis failed: {e}")
    
    def _analyze_javascript_file_ast(self, file_path: Path) -> List[ComplianceIssue]:
        """Analyze JavaScript/TypeScript files for GDPR compliance (enterprise tier only)."""
        issues = []
        
        try:
            # Use FileHandler for safe file reading
            content = self.file_handler.read_file(file_path)
            if content is None:
                logger.warning(f"Failed to read file for JavaScript analysis: {file_path}")
                return []
            
            # JavaScript security patterns analysis
            js_patterns = {
                'localStorage_usage': r'\blocalStorage\.[sg]etItem\s*\([^)]*(?:email|user|personal|profile)',
                'cookie_manipulation': r'document\.cookie\s*=.*(?:email|user|personal|profile)',
                'insecure_requests': r'(?:fetch|axios|xhr)\s*\(\s*[\'"]http://',
                'client_side_secrets': r'(?:api_key|secret|token)\s*[:=]\s*[\'"][a-zA-Z0-9]{8,}',
                'tracking_calls': r'(?:ga\(|gtag\(|analytics\.|tracker\.)',
            }
            
            line_number = 0
            for line in content.split('\n'):
                line_number += 1
                
                for pattern_name, pattern_regex in js_patterns.items():
                    if re.search(pattern_regex, line, re.IGNORECASE):
                        article, category, description, remediation = self._get_js_pattern_details(pattern_name)
                        
                        issues.append(ComplianceIssue(
                            id=str(uuid.uuid4()),
                            severity=ComplianceLevel.MEDIUM,
                            article_ref=article,
                            category=category,
                            description=description,
                            location=str(file_path),
                            line_number=line_number,
                            file_path=str(file_path),
                            remediation_suggestion=remediation,
                            evidence=line.strip()[:100],
                            metadata={
                                'detection_method': 'javascript_analysis',
                                'language': 'javascript',
                                'pattern_name': pattern_name
                            }
                        ))
                        
        except Exception as e:
            logger.debug(f"JavaScript analysis error for {file_path}: {e}")
        
        return issues
    
    def _get_js_pattern_details(self, pattern_name: str) -> Tuple[GDPRArticle, ComplianceCategory, str, str]:
        """Get GDPR details for JavaScript patterns."""
        details = {
            'localStorage_usage': (
                GDPRArticle.ARTICLE_32, ComplianceCategory.SECURITY,
                "Personal data stored in localStorage without encryption",
                "Encrypt sensitive data or use secure server-side storage"
            ),
            'cookie_manipulation': (
                GDPRArticle.ARTICLE_32, ComplianceCategory.SECURITY,
                "Personal data in cookies may lack proper security",
                "Use secure, httpOnly, sameSite cookie attributes"
            ),
            'insecure_requests': (
                GDPRArticle.ARTICLE_32, ComplianceCategory.SECURITY,
                "HTTP requests may expose personal data in transit",
                "Use HTTPS for all requests containing personal data"
            ),
            'client_side_secrets': (
                GDPRArticle.ARTICLE_32, ComplianceCategory.SECURITY,
                "API secrets exposed in client-side code",
                "Move secrets to server-side or use public API keys"
            ),
            'tracking_calls': (
                GDPRArticle.ARTICLE_6, ComplianceCategory.LAWFUL_BASIS,
                "Analytics tracking may require consent management",
                "Implement consent management for tracking and analytics"
            ),
        }
        
        return details.get(pattern_name, (
            GDPRArticle.GENERAL, ComplianceCategory.GENERAL,
            "JavaScript compliance issue detected",
            "Review code for GDPR compliance requirements"
        ))
    
    def _run_context_checks(self, project_path: Path, detection_result: DetectionResult) -> List[ComplianceIssue]:
        """Run sophisticated context-based GDPR compliance checks."""
        issues = []
        
        try:
            # Analyze PII context for compliance implications
            for file_result in detection_result.file_results:
                if file_result.matches:
                    context_issues = self._analyze_pii_context_comprehensive(file_result)
                    issues.extend(context_issues)
            
            # Cross-file analysis for data flow tracking
            if self.license_tier == LicenseTier.ENTERPRISE:
                flow_issues = self._analyze_data_flow_patterns(project_path, detection_result)
                issues.extend(flow_issues)
                    
        except Exception as e:
            logger.warning(f"Context analysis failed: {e}")
        
        return issues
    
    def _analyze_pii_context_comprehensive(self, file_result: FileResult) -> List[ComplianceIssue]:
        """Comprehensive PII context analysis for GDPR compliance."""
        issues = []
        
        # Group matches by risk level for analysis
        risk_groups = defaultdict(list)
        for match in file_result.matches:
            risk_groups[match.risk_level].extend([match])
        
        # Analyze high-risk PII concentrations
        if len(risk_groups.get('critical', [])) + len(risk_groups.get('high', [])) > 3:
            issues.append(ComplianceIssue(
                id=str(uuid.uuid4()),
                severity=ComplianceLevel.HIGH,
                article_ref=GDPRArticle.ARTICLE_32,
                category=ComplianceCategory.SECURITY,
                description="High concentration of sensitive PII without apparent security controls",
                location=str(file_result.file_path),
                file_path=str(file_result.file_path),
                remediation_suggestion="Implement encryption, access controls, and audit logging for sensitive PII handling",
                evidence=f"Found {len(risk_groups['critical']) + len(risk_groups['high'])} high-risk PII patterns",
                metadata={
                    'detection_method': 'context_analysis',
                    'pii_concentration': len(risk_groups.get('critical', [])) + len(risk_groups.get('high', [])),
                    'file_type': file_result.file_path.suffix
                }
            ))
        
        # Check for PII in configuration files
        config_extensions = {'.env', '.config', '.ini', '.yaml', '.yml', '.json'}
        if file_result.file_path.suffix in config_extensions and file_result.matches:
            issues.append(ComplianceIssue(
                id=str(uuid.uuid4()),
                severity=ComplianceLevel.CRITICAL,
                article_ref=GDPRArticle.ARTICLE_32,
                category=ComplianceCategory.SECURITY,
                description="PII detected in configuration files",
                location=str(file_result.file_path),
                file_path=str(file_result.file_path),
                remediation_suggestion="Remove PII from configuration files and use secure credential management",
                evidence=f"PII found in {file_result.file_path.name}",
                metadata={'detection_method': 'config_file_analysis', 'file_type': 'configuration'}
            ))
        
        return issues
    
    def _analyze_data_flow_patterns(self, project_path: Path, detection_result: DetectionResult) -> List[ComplianceIssue]:
        """Analyze data flow patterns for compliance violations (enterprise tier)."""
        issues = []
        
        try:
            # Build data flow map
            data_sources = []
            data_processors = []
            data_outputs = []
            
            for file_result in detection_result.file_results:
                file_content_lower = str(file_result.file_path).lower()
                
                # Identify data source files
                if any(keyword in file_content_lower for keyword in ['model', 'schema', 'database', 'migration']):
                    data_sources.append(file_result.file_path)
                
                # Identify data processor files
                if any(keyword in file_content_lower for keyword in ['service', 'controller', 'handler', 'processor']):
                    data_processors.append(file_result.file_path)
                
                # Identify data output files
                if any(keyword in file_content_lower for keyword in ['export', 'report', 'api', 'endpoint']):
                    data_outputs.append(file_result.file_path)
            
            # Check for missing data protection measures in data flow
            if data_sources and data_outputs and not data_processors:
                issues.append(ComplianceIssue(
                    id=str(uuid.uuid4()),
                    severity=ComplianceLevel.MEDIUM,
                    article_ref=GDPRArticle.ARTICLE_25,
                    category=ComplianceCategory.DATA_PROTECTION_BY_DESIGN,
                    description="Data flows directly from source to output without processing layer",
                    location=str(project_path),
                    file_path=str(project_path),
                    remediation_suggestion="Implement data processing layer with privacy controls and validation",
                    evidence=f"Found {len(data_sources)} sources, {len(data_outputs)} outputs, no processors",
                    metadata={'detection_method': 'data_flow_analysis', 'flow_type': 'direct_output'}
                ))
                
        except Exception as e:
            logger.debug(f"Data flow analysis failed: {e}")
        
        return issues
    
    def _perform_security_checks(self, project_path: Path) -> List[ComplianceIssue]:
        """Perform comprehensive Article 32 security checks."""
        issues = []
        
        try:
            # Check for encryption implementation
            encryption_indicators = [
                r'\b(?:encrypt|decrypt|cipher|AES|RSA|elliptic)\b',
                r'\b(?:ssl|tls|https|certificate)\b',
                r'\b(?:bcrypt|scrypt|pbkdf2|argon2)\b'
            ]
            
            encryption_found = False
            for pattern in encryption_indicators:
                matches = self._scan_project_for_pattern(project_path, pattern)
                if matches:
                    encryption_found = True
                    break
            
            if not encryption_found:
                issues.append(self._create_security_issue(
                    "No encryption mechanisms detected",
                    str(project_path),
                    "Implement encryption for data at rest and in transit using industry-standard algorithms",
                    "encryption_absence"
                ))
            
            # Check for secure authentication
            auth_patterns = [
                r'\b(?:authenticate|authorization|login|session)\b',
                r'\b(?:jwt|token|oauth|saml)\b',
                r'\b(?:password_hash|password_verify)\b'
            ]
            
            auth_found = False
            for pattern in auth_patterns:
                matches = self._scan_project_for_pattern(project_path, pattern)
                if matches:
                    auth_found = True
                    break
            
            if not auth_found:
                issues.append(self._create_security_issue(
                    "No authentication mechanisms detected",
                    str(project_path),
                    "Implement robust authentication and authorization for personal data access",
                    "authentication_absence"
                ))
            
            # Check for audit logging
            logging_patterns = [
                r'\b(?:logger|logging|audit|log)\b',
                r'\b(?:access_log|security_log|audit_trail)\b'
            ]
            
            logging_found = False
            for pattern in logging_patterns:
                matches = self._scan_project_for_pattern(project_path, pattern)
                if matches:
                    logging_found = True
                    break
            
            if not logging_found:
                issues.append(self._create_security_issue(
                    "No audit logging mechanisms detected",
                    str(project_path),
                    "Implement comprehensive audit logging for personal data access and processing",
                    "logging_absence"
                ))
                
        except Exception as e:
            logger.warning(f"Security checks failed: {e}")
        
        return issues
    
    def _create_security_issue(self, description: str, location: str, 
                             remediation: str, check_type: str) -> ComplianceIssue:
        """Create a security compliance issue."""
        return ComplianceIssue(
            id=str(uuid.uuid4()),
            severity=ComplianceLevel.HIGH,
            article_ref=GDPRArticle.ARTICLE_32,
            category=ComplianceCategory.SECURITY,
            description=description,
            location=location,
            file_path=location,
            remediation_suggestion=remediation,
            evidence=f"Security check: {check_type}",
            metadata={'check_type': check_type, 'detection_method': 'security_analysis'}
        )
    
    def _perform_dsar_checks(self, project_path: Path) -> List[ComplianceIssue]:
        """Perform comprehensive DSAR implementation checks."""
        issues = []
        
        try:
            dsar_components = {
                'endpoints': False,
                'authentication': False,
                'data_export': False,
                'format_support': False,
                'timeframe_compliance': False
            }
            
            # Check for DSAR endpoints
            endpoint_patterns = [
                r'(?:/api/)?(?:users?/)?(?:data|export|dsar)\b',
                r'\b(?:dsar|data_subject_access|export_user_data)\b'
            ]
            
            for pattern in endpoint_patterns:
                if self._scan_project_for_pattern(project_path, pattern):
                    dsar_components['endpoints'] = True
                    break
            
            # Check for data export functionality
            export_patterns = [
                r'\b(?:export|serialize|json|xml|csv)\b',
                r'\b(?:to_dict|to_json|as_dict)\b'
            ]
            
            for pattern in export_patterns:
                if self._scan_project_for_pattern(project_path, pattern):
                    dsar_components['data_export'] = True
                    break
            
            # Check for authentication in DSAR context
            auth_dsar_patterns = [
                r'(?:dsar|export).*(?:authenticate|authorize|verify)',
                r'(?:authenticate|authorize|verify).*(?:dsar|export)'
            ]
            
            for pattern in auth_dsar_patterns:
                if self._scan_project_for_pattern(project_path, pattern):
                    dsar_components['authentication'] = True
                    break
            
            # Generate issues based on missing components
            missing_components = [k for k, v in dsar_components.items() if not v]
            
            if missing_components:
                severity = ComplianceLevel.CRITICAL if len(missing_components) > 3 else ComplianceLevel.HIGH
                
                issues.append(ComplianceIssue(
                    id=str(uuid.uuid4()),
                    severity=severity,
                    article_ref=GDPRArticle.ARTICLE_15,
                    category=ComplianceCategory.DATA_RIGHTS,
                    description=f"DSAR implementation incomplete - missing: {', '.join(missing_components)}",
                    location=str(project_path),
                    file_path=str(project_path),
                    remediation_suggestion=self._get_dsar_remediation(missing_components),
                    evidence=f"DSAR completeness: {len(dsar_components) - len(missing_components)}/{len(dsar_components)}",
                    metadata={
                        'missing_components': missing_components,
                        'check_type': 'dsar_completeness',
                        'detection_method': 'dsar_analysis'
                    }
                ))
                
        except Exception as e:
            logger.warning(f"DSAR checks failed: {e}")
        
        return issues
    
    def _get_dsar_remediation(self, missing_components: List[str]) -> str:
        """Generate specific remediation suggestions for missing DSAR components."""
        remediation_map = {
            'endpoints': "Create secure API endpoints for data subject access requests",
            'authentication': "Implement strong authentication to verify data subject identity",
            'data_export': "Develop comprehensive data export functionality in machine-readable formats",
            'format_support': "Support multiple export formats (JSON, XML, CSV) as required",
            'timeframe_compliance': "Ensure response within 30 days as mandated by Article 15"
        }
        
        suggestions = [remediation_map.get(comp, f"Implement {comp}") for comp in missing_components]
        return f"DSAR implementation requirements: {'; '.join(suggestions)}."
    
    def _perform_deletion_checks(self, project_path: Path) -> List[ComplianceIssue]:
        """Perform comprehensive right to be forgotten checks."""
        issues = []
        
        try:
            deletion_components = {
                'deletion_endpoints': False,
                'cascade_deletion': False,
                'backup_handling': False,
                'third_party_deletion': False,
                'verification_mechanism': False
            }
            
            # Check for deletion endpoints
            if self._scan_project_for_pattern(project_path, self.DELETION_PATTERNS['endpoint_patterns']):
                deletion_components['deletion_endpoints'] = True
            
            # Check for cascade deletion
            if self._scan_project_for_pattern(project_path, self.DELETION_PATTERNS['cascade_deletion']):
                deletion_components['cascade_deletion'] = True
            
            # Check for backup handling
            backup_patterns = r'\b(?:backup|archive).*(?:delete|remove|purge)\b'
            if self._scan_project_for_pattern(project_path, backup_patterns):
                deletion_components['backup_handling'] = True
            
            # Check for third-party deletion coordination
            third_party_patterns = r'\b(?:api|webhook|notify).*(?:delete|erasure)\b'
            if self._scan_project_for_pattern(project_path, third_party_patterns):
                deletion_components['third_party_deletion'] = True
            
            # Assess deletion completeness
            missing_deletion = [k for k, v in deletion_components.items() if not v]
            
            if missing_deletion:
                severity = (ComplianceLevel.CRITICAL if 'deletion_endpoints' in missing_deletion 
                           else ComplianceLevel.HIGH)
                
                issues.append(ComplianceIssue(
                    id=str(uuid.uuid4()),
                    severity=severity,
                    article_ref=GDPRArticle.ARTICLE_17,
                    category=ComplianceCategory.DATA_RIGHTS,
                    description=f"Incomplete erasure implementation - missing: {', '.join(missing_deletion)}",
                    location=str(project_path),
                    file_path=str(project_path),
                    remediation_suggestion=self._get_deletion_remediation(missing_deletion),
                    evidence=f"Deletion completeness: {len(deletion_components) - len(missing_deletion)}/{len(deletion_components)}",
                    metadata={
                        'missing_components': missing_deletion,
                        'check_type': 'deletion_completeness',
                        'detection_method': 'deletion_analysis'
                    }
                ))
                
        except Exception as e:
            logger.warning(f"Deletion checks failed: {e}")
        
        return issues
    
    def _get_deletion_remediation(self, missing_components: List[str]) -> str:
        """Generate specific remediation for missing deletion components."""
        remediation_map = {
            'deletion_endpoints': "Implement secure user deletion endpoints with proper authentication",
            'cascade_deletion': "Ensure cascade deletion of all related personal data across systems",
            'backup_handling': "Include backup and archive deletion in erasure procedures",
            'third_party_deletion': "Coordinate deletion with third-party services and processors",
            'verification_mechanism': "Implement deletion verification and confirmation processes"
        }
        
        suggestions = [remediation_map.get(comp, f"Implement {comp}") for comp in missing_components]
        return f"Article 17 compliance requirements: {'; '.join(suggestions)}."
    
    def _perform_transfer_checks(self, project_path: Path) -> List[ComplianceIssue]:
        """Perform comprehensive cross-border data transfer checks."""
        issues = []
        
        try:
            # Enhanced third-party service detection
            third_party_services = self._detect_third_party_services(project_path)
            
            for service_info in third_party_services:
                # Check for adequacy decision countries
                if not self._has_adequate_safeguards(service_info):
                    severity = (ComplianceLevel.CRITICAL if service_info['risk_level'] == 'high' 
                               else ComplianceLevel.HIGH)
                    
                    issues.append(ComplianceIssue(
                        id=str(uuid.uuid4()),
                        severity=severity,
                        article_ref=GDPRArticle.ARTICLE_44,
                        category=ComplianceCategory.DATA_TRANSFER,
                        description=f"International data transfer to {service_info['service']} lacks adequate safeguards",
                        location=service_info['location'],
                        file_path=service_info['location'],
                        line_number=service_info.get('line_number'),
                        remediation_suggestion=f"Verify {service_info['service']} has SCCs, BCRs, or adequacy decision for data transfers",
                        evidence=service_info['evidence'],
                        metadata={
                            'service_name': service_info['service'],
                            'transfer_type': service_info['transfer_type'],
                            'detection_method': 'transfer_analysis'
                        }
                    ))
                    
        except Exception as e:
            logger.warning(f"Transfer checks failed: {e}")
        
        return issues
    
    def _detect_third_party_services(self, project_path: Path) -> List[Dict]:
        """Detect third-party services with enhanced accuracy."""
        services = []
        
        known_services = {
            'aws': {'risk': 'medium', 'type': 'cloud'},
            'azure': {'risk': 'medium', 'type': 'cloud'},
            'gcp': {'risk': 'medium', 'type': 'cloud'},
            'stripe': {'risk': 'high', 'type': 'payment'},
            'paypal': {'risk': 'high', 'type': 'payment'},
            'mailchimp': {'risk': 'medium', 'type': 'marketing'},
            'sendgrid': {'risk': 'medium', 'type': 'email'},
            'twilio': {'risk': 'medium', 'type': 'communication'},
            'analytics': {'risk': 'high', 'type': 'tracking'}
        }
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.js', '.java', '.php', '.rb']:
                try:
                    # Use FileHandler for safe file reading
                    content = self.file_handler.read_file(file_path)
                    if content is None:
                        continue
                    
                    for service, info in known_services.items():
                        pattern = rf'\b{service}\.(?:com|net|org|io)\b'
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            services.append({
                                'service': service,
                                'risk_level': info['risk'],
                                'transfer_type': info['type'],
                                'location': str(file_path),
                                'line_number': line_num,
                                'evidence': match.group()
                            })
                            
                except Exception as e:
                    logger.debug(f"Error scanning {file_path}: {e}")
                    continue
        
        return services
    
    def _has_adequate_safeguards(self, service_info: Dict) -> bool:
        """Check if service has adequate data transfer safeguards."""
        # This would integrate with external compliance databases
        # For now, assume high-risk services need validation
        return service_info['risk_level'] != 'high'
    
    def _perform_consent_checks(self, project_path: Path) -> List[ComplianceIssue]:
        """Perform consent management compliance checks."""
        issues = []
        
        try:
            consent_patterns = [
                r'\b(?:consent|agree|accept|opt[-_]?in)\b',
                r'\b(?:cookie.*consent|gdpr.*consent|privacy.*consent)\b',
                r'\b(?:consent.*manager|consent.*banner)\b'
            ]
            
            consent_found = False
            for pattern in consent_patterns:
                if self._scan_project_for_pattern(project_path, pattern):
                    consent_found = True
                    break
            
            # Check for tracking without consent
            tracking_patterns = [
                r'\b(?:ga\(|gtag\(|analytics\.|facebook.*pixel|google.*tag)\b',
                r'\b(?:track|analytics|pixel|beacon)\b'
            ]
            
            tracking_found = False
            for pattern in tracking_patterns:
                if self._scan_project_for_pattern(project_path, pattern):
                    tracking_found = True
                    break
            
            if tracking_found and not consent_found:
                issues.append(ComplianceIssue(
                    id=str(uuid.uuid4()),
                    severity=ComplianceLevel.HIGH,
                    article_ref=GDPRArticle.ARTICLE_6,
                    category=ComplianceCategory.LAWFUL_BASIS,
                    description="Tracking functionality detected without consent management",
                    location=str(project_path),
                    file_path=str(project_path),
                    remediation_suggestion="Implement consent management for tracking, analytics, and marketing activities",
                    evidence="Tracking code found without consent mechanisms",
                    metadata={'check_type': 'consent_tracking', 'detection_method': 'consent_analysis'}
                ))
                
        except Exception as e:
            logger.warning(f"Consent checks failed: {e}")
        
        return issues
    
    def _perform_retention_checks(self, project_path: Path) -> List[ComplianceIssue]:
        """Perform data retention compliance checks."""
        issues = []
        
        try:
            retention_patterns = [
                r'\b(?:retention|expire|ttl|cleanup|purge)\b',
                r'\b(?:delete.*after|remove.*days|expire.*months)\b',
                r'\b(?:created_at|updated_at).*(?:\+|\-|\>|\<)\b'
            ]
            
            retention_found = False
            for pattern in retention_patterns:
                if self._scan_project_for_pattern(project_path, pattern):
                    retention_found = True
                    break
            
            if not retention_found:
                issues.append(ComplianceIssue(
                    id=str(uuid.uuid4()),
                    severity=ComplianceLevel.MEDIUM,
                    article_ref=GDPRArticle.ARTICLE_5,
                    category=ComplianceCategory.RETENTION,
                    description="No data retention mechanisms detected",
                    location=str(project_path),
                    file_path=str(project_path),
                    remediation_suggestion="Implement data retention policies with automated cleanup procedures",
                    evidence="No retention patterns found in codebase",
                    metadata={'check_type': 'retention_absence', 'detection_method': 'retention_analysis'}
                ))
                
        except Exception as e:
            logger.warning(f"Retention checks failed: {e}")
        
        return issues
    
    def _perform_purpose_limitation_checks(self, project_path: Path) -> List[ComplianceIssue]:
        """Perform purpose limitation compliance checks."""
        issues = []
        
        try:
            # Check for purpose specification in data collection
            purpose_patterns = [
                r'\b(?:purpose|reason|use.*for|collect.*for)\b',
                r'\b(?:privacy.*policy|data.*usage|terms.*service)\b'
            ]
            
            purpose_found = False
            for pattern in purpose_patterns:
                if self._scan_project_for_pattern(project_path, pattern):
                    purpose_found = True
                    break
            
            # Check for data sharing without purpose limitation
            sharing_patterns = [
                r'\b(?:share.*data|send.*to|forward.*to|api.*call)\b',
                r'\b(?:third.*party|external.*service|partner.*api)\b'
            ]
            
            sharing_found = False
            for pattern in sharing_patterns:
                if self._scan_project_for_pattern(project_path, pattern):
                    sharing_found = True
                    break
            
            if sharing_found and not purpose_found:
                issues.append(ComplianceIssue(
                    id=str(uuid.uuid4()),
                    severity=ComplianceLevel.MEDIUM,
                    article_ref=GDPRArticle.ARTICLE_5,
                    category=ComplianceCategory.PURPOSE_LIMITATION,
                    description="Data sharing detected without clear purpose limitation",
                    location=str(project_path),
                    file_path=str(project_path),
                    remediation_suggestion="Document and enforce purpose limitation for all data sharing activities",
                    evidence="Data sharing patterns without purpose documentation",
                    metadata={'check_type': 'purpose_limitation', 'detection_method': 'purpose_analysis'}
                ))
                
        except Exception as e:
            logger.warning(f"Purpose limitation checks failed: {e}")
        
        return issues
    
    def _perform_data_minimization_checks(self, project_path: Path) -> List[ComplianceIssue]:
        """Perform data minimization compliance checks."""
        issues = []
        
        try:
            # Check for over-collection patterns
            over_collection_patterns = [
                r'\bSELECT \* FROM\b',
                r'\b(?:fetch|get|retrieve).*all\b',
                r'\b(?:user|person|customer)\..*\*\b'
            ]
            
            over_collection_found = []
            for pattern in over_collection_patterns:
                matches = self._scan_project_for_pattern(project_path, pattern)
                if matches:
                    over_collection_found.extend(matches)
            
            if over_collection_found:
                issues.append(ComplianceIssue(
                    id=str(uuid.uuid4()),
                    severity=ComplianceLevel.MEDIUM,
                    article_ref=GDPRArticle.ARTICLE_5,
                    category=ComplianceCategory.DATA_MINIMIZATION,
                    description="Potential data over-collection patterns detected",
                    location=str(project_path),
                    file_path=str(project_path),
                    remediation_suggestion="Review data collection to ensure only necessary data is processed",
                    evidence=f"Found {len(over_collection_found)} over-collection patterns",
                    metadata={
                        'pattern_count': len(over_collection_found),
                        'check_type': 'data_minimization',
                        'detection_method': 'minimization_analysis'
                    }
                ))
                
        except Exception as e:
            logger.warning(f"Data minimization checks failed: {e}")
        
        return issues
    
    def _apply_ml_filtering(self, issues: List[ComplianceIssue], project_path: Path) -> List[ComplianceIssue]:
        """Apply ML-based false positive reduction to compliance issues."""
        if not self.ml_filter or not issues:
            return issues
        
        filtered_issues = []
        
        try:
            # Convert compliance issues to detection matches for ML filtering
            mock_matches = []
            for issue in issues:
                # Create a mock detection match from the compliance issue
                mock_match = type('MockDetectionMatch', (), {
                    'pattern_name': issue.metadata.get('pattern_name', 'compliance_issue'),
                    'matched_text': issue.evidence[:100] if issue.evidence else issue.description[:100],
                    'line_number': issue.line_number or 1,
                    'column_start': issue.column_start or 0,
                    'column_end': issue.column_end or 100,
                    'confidence': issue.metadata.get('confidence', 0.8),
                    'risk_level': self._map_compliance_level_to_risk(issue.severity),
                    'context_before': '',
                    'context_after': '',
                    'metadata': {
                        'compliance_issue_id': issue.id,
                        'detection_level': 'compliance',
                        'gdpr_article': issue.article_ref.value,
                        'compliance_category': issue.category.value
                    }
                })()
                mock_matches.append(mock_match)
            
            # Apply ML filtering to the mock matches
            if mock_matches:
                # Read file content for context (use first issue's file)
                file_content = ""
                if issues[0].file_path and Path(issues[0].file_path).exists():
                    try:
                        file_content = self.file_handler.read_file(Path(issues[0].file_path))
                        if file_content is None:
                            file_content = ""
                    except Exception:
                        file_content = ""
                
                # Apply ML filtering
                filtered_matches = self.ml_filter.filter_matches(
                    mock_matches, 
                    file_content, 
                    file_path=str(project_path)
                )
                
                # Convert filtered matches back to compliance issues
                filtered_issue_ids = {
                    match.metadata.get('compliance_issue_id') 
                    for match in filtered_matches 
                    if match.metadata.get('compliance_issue_id')
                }
                
                filtered_issues = [
                    issue for issue in issues 
                    if issue.id in filtered_issue_ids
                ]
                
                logger.info(f"ML filtering reduced compliance issues: {len(issues)} → {len(filtered_issues)}")
            
        except Exception as e:
            logger.warning(f"ML filtering failed for compliance issues: {e}")
            return issues
        
        return filtered_issues if filtered_issues else issues
    
    def _map_compliance_level_to_risk(self, compliance_level: ComplianceLevel) -> str:
        """Map compliance level to risk level for ML filtering."""
        mapping = {
            ComplianceLevel.CRITICAL: 'critical',
            ComplianceLevel.HIGH: 'high',
            ComplianceLevel.MEDIUM: 'medium',
            ComplianceLevel.LOW: 'low'
        }
        return mapping.get(compliance_level, 'medium')
    
    def _analyze_with_enhanced_parser(self, parser, file_path: Path, content: str) -> List[ComplianceIssue]:
        """Analyze file using enhanced parser capabilities for GDPR compliance."""
        issues = []
        
        try:
            language = detect_language(file_path)
            
            # Enhanced string analysis for sensitive data
            strings = parser.extract_strings(file_path, content)
            for string_literal in strings:
                if self._contains_sensitive_data(string_literal.value):
                    issue = ComplianceIssue(
                        id=str(uuid.uuid4()),
                        severity=ComplianceLevel.HIGH,
                        article_ref=GDPRArticle.ARTICLE_32,
                        category=ComplianceCategory.SECURITY,
                        description=f"Sensitive data in string literal: {string_literal.context}",
                        location=str(file_path),
                        line_number=string_literal.start_line,
                        column_start=string_literal.start_col,
                        column_end=string_literal.end_col,
                        file_path=str(file_path),
                        remediation_suggestion="Move sensitive data to secure configuration or environment variables",
                        evidence=string_literal.value[:100],
                        metadata={
                            'detection_method': 'enhanced_parser',
                            'parser_language': language,
                            'string_context': string_literal.context,
                            'confidence': 0.9
                        }
                    )
                    issues.append(issue)
            
            # Enhanced analysis features if available
            if hasattr(parser, 'get_enhanced_analysis'):
                try:
                    enhanced_analysis = parser.get_enhanced_analysis(content, file_path)
                    
                    # F-String and Template Literal Analysis
                    if 'f_strings' in enhanced_analysis:
                        for f_string in enhanced_analysis['f_strings']:
                            if f_string.is_sensitive:
                                issue = ComplianceIssue(
                                    id=str(uuid.uuid4()),
                                    severity=ComplianceLevel.HIGH,
                                    article_ref=GDPRArticle.ARTICLE_32,
                                    category=ComplianceCategory.SECURITY,
                                    description=f"Sensitive data in f-string: {f_string.variable_name}",
                                    location=str(file_path),
                                    line_number=f_string.start_line,
                                    column_start=f_string.start_col,
                                    column_end=f_string.end_col,
                                    file_path=str(file_path),
                                    remediation_suggestion="Avoid exposing sensitive variables in f-strings, use secure formatting",
                                    evidence=f_string.expression[:100],
                                    metadata={
                                        'detection_method': 'enhanced_parser_f_string',
                                        'variable_name': f_string.variable_name,
                                        'confidence': 0.95
                                    }
                                )
                                issues.append(issue)
                    
                    # Logging Context Analysis
                    if 'logging_contexts' in enhanced_analysis:
                        for log_context in enhanced_analysis['logging_contexts']:
                            if log_context.contains_pii:
                                issue = ComplianceIssue(
                                    id=str(uuid.uuid4()),
                                    severity=ComplianceLevel.HIGH,
                                    article_ref=GDPRArticle.ARTICLE_32,
                                    category=ComplianceCategory.SECURITY,
                                    description=f"PII detected in logging: {log_context.pii_types}",
                                    location=str(file_path),
                                    line_number=log_context.start_line,
                                    column_start=log_context.start_col,
                                    column_end=log_context.end_col,
                                    file_path=str(file_path),
                                    remediation_suggestion="Remove PII from logging statements or implement data masking",
                                    evidence=f"logging.{log_context.function_name}",
                                    metadata={
                                        'detection_method': 'enhanced_parser_logging',
                                        'pii_types': log_context.pii_types,
                                        'log_level': log_context.level,
                                        'confidence': 0.9
                                    }
                                )
                                issues.append(issue)
                                
                except Exception as e:
                    logger.debug(f"Enhanced parser analysis failed for {file_path}: {e}")
            
            # Variable analysis for sensitive naming patterns
            variables = parser.extract_variables(file_path, content)
            for variable in variables:
                if self._is_sensitive_variable_name(variable.name):
                    issue = ComplianceIssue(
                        id=str(uuid.uuid4()),
                        severity=ComplianceLevel.MEDIUM,
                        article_ref=GDPRArticle.ARTICLE_25,
                        category=ComplianceCategory.DATA_PROTECTION_BY_DESIGN,
                        description=f"Variable name suggests sensitive data: {variable.name}",
                        location=str(file_path),
                        line_number=variable.start_line,
                        column_start=variable.start_col,
                        column_end=variable.end_col,
                        file_path=str(file_path),
                        remediation_suggestion="Use generic variable names or implement proper data classification",
                        evidence=variable.name,
                        metadata={
                            'detection_method': 'enhanced_parser_variable',
                            'variable_type': variable.var_type,
                            'confidence': 0.7
                        }
                    )
                    issues.append(issue)
            
            logger.debug(f"Enhanced parser analysis found {len(issues)} compliance issues for {file_path}")
            
        except Exception as e:
            logger.warning(f"Enhanced parser analysis failed for {file_path}: {e}")
        
        return issues
    
    def _contains_sensitive_data(self, text: str) -> bool:
        """Check if text contains sensitive data patterns."""
        if not text or len(text.strip()) < 5:
            return False
        
        # GDPR-specific sensitive data patterns
        sensitive_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
            r'\b\d{16}\b',             # Credit card
            r'\b(?:password|secret|key|token|api_key)\b.*[:=].*\w+',  # Credentials
            r'\b(?:birth|dob|date.*birth)\b',  # Birth date
            r'\b(?:address|street|zip|postal)\b',  # Address
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_sensitive_variable_name(self, name: str) -> bool:
        """Check if variable name suggests sensitive data."""
        if not name or len(name) < 3:
            return False
        
        name_lower = name.lower()
        sensitive_keywords = [
            'password', 'secret', 'key', 'token', 'credential',
            'email', 'phone', 'ssn', 'social', 'credit', 'card',
            'birth', 'dob', 'address', 'street', 'zip', 'postal',
            'personal', 'private', 'confidential', 'sensitive'
        ]
        
        return any(keyword in name_lower for keyword in sensitive_keywords)