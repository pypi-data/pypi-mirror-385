"""
Compliance Framework Engine - Multi-framework compliance orchestrator.

Provides unified compliance analysis across GDPR, CCPA, and future frameworks
with framework registry, unified violation model, and cross-framework scoring.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..core.config import Config, LicenseTier
from ..core.exceptions import DetectionError
from ..models.detection_result import DetectionResult, DetectionMatch
from .models import ComplianceIssue, ComplianceLevel, GDPRArticle
from .compliance_alerter import ComplianceAlert, AlertSeverity
from .gdpr_analyzer import GDPRAnalyzer
from .ccpa_analyzer import CCPAAnalyzer, CCPAArticle


logger = logging.getLogger(__name__)


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    GDPR = "GDPR"
    CCPA = "CCPA"
    ALL = "ALL"


@dataclass
class FrameworkCapability:
    """Framework capability definition."""
    framework: ComplianceFramework
    analyzer_class: str
    article_count: int
    supported_features: List[str]
    license_tier_required: LicenseTier


@dataclass
class UnifiedViolation:
    """Unified violation model across frameworks."""
    id: str
    frameworks: List[ComplianceFramework]
    primary_framework: ComplianceFramework
    article_refs: Dict[ComplianceFramework, str]
    severity: ComplianceLevel
    description: str
    file_path: str
    line_number: int
    evidence: str
    remediation: str
    confidence: float
    category: str
    check_type: str
    created_at: datetime
    cross_framework_mappings: Dict[ComplianceFramework, str] = field(default_factory=dict)


@dataclass
class FrameworkAnalysisResult:
    """Result of framework-specific analysis."""
    framework: ComplianceFramework
    issues: List[ComplianceIssue]
    alerts: List[ComplianceAlert]
    compliance_score: float
    article_coverage: Dict[str, int]
    recommendations: List[str]


@dataclass
class UnifiedComplianceResult:
    """Unified compliance result across all frameworks."""
    frameworks_analyzed: List[ComplianceFramework]
    unified_violations: List[UnifiedViolation]
    framework_results: Dict[ComplianceFramework, FrameworkAnalysisResult]
    overall_compliance_score: float
    cross_framework_insights: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


class ComplianceFrameworkEngine:
    """
    Multi-framework compliance orchestrator.
    
    Provides unified compliance analysis across GDPR, CCPA, and future frameworks
    with framework registry, unified violation model, and cross-framework scoring.
    """
    
    def __init__(self, config: Config):
        """Initialize the compliance framework engine."""
        self.config = config
        self.license_tier = config.license.tier
        
        # Initialize framework registry
        self.framework_registry = self._initialize_framework_registry()
        
        # Initialize analyzers
        self.analyzers = self._initialize_analyzers()
        
        # Framework mapping rules
        self.framework_mappings = self._initialize_framework_mappings()
        
        logger.info("Compliance Framework Engine initialized successfully")
    
    def _initialize_framework_registry(self) -> Dict[ComplianceFramework, FrameworkCapability]:
        """Initialize framework capability registry."""
        return {
            ComplianceFramework.GDPR: FrameworkCapability(
                framework=ComplianceFramework.GDPR,
                analyzer_class="GDPRAnalyzer",
                article_count=15,
                supported_features=[
                    "Data Subject Rights",
                    "Security Requirements",
                    "Data Minimization",
                    "Cross-border Transfers",
                    "Breach Notification",
                    "Audit Logging"
                ],
                license_tier_required=LicenseTier.PRO
            ),
            ComplianceFramework.CCPA: FrameworkCapability(
                framework=ComplianceFramework.CCPA,
                analyzer_class="CCPAAnalyzer",
                article_count=12,
                supported_features=[
                    "Consumer Rights",
                    "Data Security",
                    "Opt-out Mechanisms",
                    "Non-discrimination",
                    "Notice Requirements",
                    "Breach Notification"
                ],
                license_tier_required=LicenseTier.BUSINESS
            )
        }
    
    def _initialize_analyzers(self) -> Dict[ComplianceFramework, Any]:
        """Initialize framework analyzers."""
        analyzers = {}
        
        # Initialize GDPR analyzer
        if self.license_tier in [LicenseTier.PRO, LicenseTier.BUSINESS, LicenseTier.ENTERPRISE]:
            analyzers[ComplianceFramework.GDPR] = GDPRAnalyzer(self.config)
        
        # Initialize CCPA analyzer
        if self.license_tier in [LicenseTier.BUSINESS, LicenseTier.ENTERPRISE]:
            analyzers[ComplianceFramework.CCPA] = CCPAAnalyzer(self.config)
        
        return analyzers
    
    def _initialize_framework_mappings(self) -> Dict[str, Dict[ComplianceFramework, str]]:
        """Initialize cross-framework mapping rules."""
        return {
            "data_access_right": {
                ComplianceFramework.GDPR: "Article 15",
                ComplianceFramework.CCPA: "§1798.100"
            },
            "data_deletion_right": {
                ComplianceFramework.GDPR: "Article 17",
                ComplianceFramework.CCPA: "§1798.105"
            },
            "opt_out_right": {
                ComplianceFramework.GDPR: "Article 21",
                ComplianceFramework.CCPA: "§1798.120"
            },
            "data_security": {
                ComplianceFramework.GDPR: "Article 32",
                ComplianceFramework.CCPA: "§1798.150"
            },
            "breach_notification": {
                ComplianceFramework.GDPR: "Article 33",
                ComplianceFramework.CCPA: "§1798.150"
            },
            "non_discrimination": {
                ComplianceFramework.GDPR: "Article 22",
                ComplianceFramework.CCPA: "§1798.125"
            }
        }
    
    def analyze_compliance(self, results: DetectionResult, 
                          frameworks: List[ComplianceFramework] = None) -> UnifiedComplianceResult:
        """
        Analyze compliance across multiple frameworks.
        
        Args:
            results: Detection results from scan
            frameworks: Frameworks to analyze (default: all available)
            
        Returns:
            Unified compliance result across frameworks
        """
        try:
            # Determine frameworks to analyze
            if frameworks is None:
                frameworks = self._get_available_frameworks()
            
            # Validate framework availability
            available_frameworks = self._get_available_frameworks()
            frameworks = [f for f in frameworks if f in available_frameworks]
            
            if not frameworks:
                # Quiet path: no frameworks available for this tier
                logger.info("No compliance frameworks available for current license tier; returning empty result")
                return UnifiedComplianceResult(
                    frameworks_analyzed=[],
                    unified_violations=[],
                    framework_results={},
                    overall_compliance_score=0.0,
                    cross_framework_insights={},
                    recommendations=[]
                )
            
            # Analyze each framework
            framework_results = {}
            unified_violations = []
            
            for framework in frameworks:
                if framework in self.analyzers:
                    framework_result = self._analyze_framework(framework, results)
                    framework_results[framework] = framework_result
                    
                    # Convert to unified violations
                    unified_violations.extend(
                        self._convert_to_unified_violations(framework_result.issues, framework)
                    )
            
            # Calculate overall compliance score
            overall_score = self._calculate_overall_score(framework_results)
            
            # Generate cross-framework insights
            cross_framework_insights = self._generate_cross_framework_insights(framework_results)
            
            # Generate unified recommendations
            recommendations = self._generate_unified_recommendations(framework_results, unified_violations)
            
            return UnifiedComplianceResult(
                frameworks_analyzed=frameworks,
                unified_violations=unified_violations,
                framework_results=framework_results,
                overall_compliance_score=overall_score,
                cross_framework_insights=cross_framework_insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze multi-framework compliance: {e}")
            raise DetectionError(f"Multi-framework compliance analysis failed: {e}")
    
    def _get_available_frameworks(self) -> List[ComplianceFramework]:
        """Get available frameworks for current license tier."""
        available = []
        
        def tier_rank(tier: LicenseTier) -> int:
            order = {
                LicenseTier.STARTER: 0,
                LicenseTier.PRO: 1,
                LicenseTier.BUSINESS: 2,
                LicenseTier.ENTERPRISE: 3,
            }
            return order.get(tier, -1)
        
        current_rank = tier_rank(self.license_tier)
        for framework, capability in self.framework_registry.items():
            if current_rank >= tier_rank(capability.license_tier_required):
                available.append(framework)
        
        return available
    
    def _analyze_framework(self, framework: ComplianceFramework, 
                          results: DetectionResult) -> FrameworkAnalysisResult:
        """Analyze compliance for a specific framework."""
        analyzer = self.analyzers[framework]
        
        # Filter detections for compliance analysis
        filtered_results = self._filter_detections_for_compliance(results)
        
        # Run framework-specific analysis with filtered results
        issues = analyzer.analyze_compliance(filtered_results)
        
        # Generate alerts from issues
        alerts = self._generate_alerts_from_issues(issues, framework)
        
        # Calculate compliance score
        compliance_score = self._calculate_framework_score(issues)
        
        # Calculate article coverage
        article_coverage = self._calculate_article_coverage(issues)
        
        # Generate recommendations
        recommendations = self._generate_framework_recommendations(issues, framework)
        
        return FrameworkAnalysisResult(
            framework=framework,
            issues=issues,
            alerts=alerts,
            compliance_score=compliance_score,
            article_coverage=article_coverage,
            recommendations=recommendations
        )
    
    def _filter_detections_for_compliance(self, results: DetectionResult) -> DetectionResult:
        """
        Filter detections to only include those relevant for compliance analysis.
        
        Args:
            results: Original detection results
            
        Returns:
            Filtered detection results with only compliance-relevant detections
        """
        
        # Compliance-relevant pattern types
        compliance_relevant_patterns = {
            'email', 'ssn', 'credit_card', 'phone', 'address', 'name',
            'password', 'api_key', 'secret', 'token', 'private_key',
            'social_security', 'drivers_license', 'passport', 'bank_account'
        }
        
        # Filter matches based on severity and pattern type
        filtered_matches = []
        for match in results.matches:
            # Only process HIGH/CRITICAL severity detections
            if match.severity not in ['HIGH', 'CRITICAL']:
                continue
            
            # Only process detections with sufficient confidence
            if match.confidence < 0.7:
                continue
            
            # Skip test context detections
            if match.metadata.get('in_test_context', False):
                continue
            
            # Skip framework-safe patterns
            if match.metadata.get('framework_safe', False):
                continue
            
            # Check if pattern is compliance-relevant
            pattern_name = match.pattern_name.lower()
            if any(compliance_pattern in pattern_name for compliance_pattern in compliance_relevant_patterns):
                filtered_matches.append(match)
        
        # Create filtered results
        filtered_results = DetectionResult(
            matches=filtered_matches,
            total_files_scanned=results.total_files_scanned,
            total_matches_found=len(filtered_matches),
            scan_duration=results.scan_duration,
            scan_timestamp=results.scan_timestamp,
            config=results.config,
            metadata={
                **results.metadata,
                'compliance_filtered': True,
                'original_match_count': len(results.matches),
                'filtered_match_count': len(filtered_matches)
            }
        )
        
        logger.info(f"Compliance filtering: {len(results.matches)} -> {len(filtered_matches)} detections")
        
        return filtered_results
    
    def _should_trigger_compliance_check(self, detection: DetectionMatch) -> bool:
        """
        Determine if a detection should trigger compliance analysis.
        
        Args:
            detection: Detection match to evaluate
            
        Returns:
            True if the detection should trigger compliance analysis
        """
        # Only HIGH/CRITICAL severity
        if detection.severity not in ['HIGH', 'CRITICAL']:
            return False
        
        # Only high confidence detections
        if detection.confidence < 0.7:
            return False
        
        # Skip test context
        if detection.metadata.get('in_test_context', False):
            return False
        
        # Skip framework-safe patterns
        if detection.metadata.get('framework_safe', False):
            return False
        
        # Check pattern relevance
        compliance_relevant_patterns = {
            'email', 'ssn', 'credit_card', 'phone', 'address', 'name',
            'password', 'api_key', 'secret', 'token', 'private_key',
            'social_security', 'drivers_license', 'passport', 'bank_account'
        }
        
        pattern_name = detection.pattern_name.lower()
        return any(compliance_pattern in pattern_name for compliance_pattern in compliance_relevant_patterns)
    
    def _create_compliance_issue(self, detection: DetectionMatch, framework: ComplianceFramework) -> Optional[ComplianceIssue]:
        """
        Create a compliance issue from a detection match with intelligent filtering.
        
        Args:
            detection: Detection match to convert
            framework: Compliance framework (GDPR, CCPA)
            
        Returns:
            ComplianceIssue if the detection should create an issue, None otherwise
        """
        # Skip if in test context
        if detection.metadata.get('in_test_context', False):
            return None
        
        # Skip if framework-safe pattern
        if detection.metadata.get('framework_safe', False):
            return None
        
        # Only HIGH/CRITICAL severity
        if detection.severity not in ['HIGH', 'CRITICAL']:
            return None
        
        # Only high confidence detections
        if detection.confidence < 0.7:
            return None
        
        # Map detection to compliance article
        article_ref = self._map_detection_to_article(detection, framework)
        if not article_ref:
            return None
        
        # Determine compliance level from severity
        compliance_level_mapping = {
            'CRITICAL': ComplianceLevel.CRITICAL,
            'HIGH': ComplianceLevel.HIGH,
            'MEDIUM': ComplianceLevel.MEDIUM,
            'LOW': ComplianceLevel.LOW
        }
        
        compliance_level = compliance_level_mapping.get(detection.severity, ComplianceLevel.MEDIUM)
        
        # Generate remediation suggestion
        remediation = self._generate_remediation_suggestion(detection, framework, article_ref)
        
        # Create compliance issue
        issue = ComplianceIssue(
            id=f"{framework.value}_{detection.pattern_name}_{detection.line}",
            framework=framework,
            article_ref=article_ref,
            severity=compliance_level,
            description=f"{framework.value} {article_ref.value} violation detected",
            file_path=detection.file,
            line_number=detection.line,
            evidence=detection.matched_text,
            remediation=remediation,
            confidence=detection.confidence,
            category=self._categorize_detection(detection),
            check_type="automated_detection",
            created_at=datetime.now(),
            metadata={
                'detection_id': detection.rule_id,
                'pattern_name': detection.pattern_name,
                'engine': detection.engine,
                'original_severity': detection.severity,
                'context_before': detection.context_before,
                'context_after': detection.context_after
            }
        )
        
        return issue
    
    def _map_detection_to_article(self, detection: DetectionMatch, framework: ComplianceFramework) -> Optional[Union[GDPRArticle, CCPAArticle]]:
        """Map detection pattern to compliance article."""
        pattern_name = detection.pattern_name.lower()
        
        if framework == ComplianceFramework.GDPR:
            # GDPR article mapping
            if 'email' in pattern_name or 'personal' in pattern_name:
                return GDPRArticle.ARTICLE_32  # Security of processing
            elif 'password' in pattern_name or 'secret' in pattern_name or 'api_key' in pattern_name:
                return GDPRArticle.ARTICLE_32  # Security of processing
            elif 'ssn' in pattern_name or 'social_security' in pattern_name:
                return GDPRArticle.ARTICLE_9  # Special categories of personal data
            elif 'credit_card' in pattern_name or 'bank_account' in pattern_name:
                return GDPRArticle.ARTICLE_9  # Special categories of personal data
            elif 'phone' in pattern_name or 'address' in pattern_name:
                return GDPRArticle.ARTICLE_32  # Security of processing
            else:
                return GDPRArticle.ARTICLE_32  # Default to security
        
        elif framework == ComplianceFramework.CCPA:
            # CCPA article mapping
            if 'email' in pattern_name or 'personal' in pattern_name:
                return CCPAArticle.SECTION_1798_150  # Security measures
            elif 'password' in pattern_name or 'secret' in pattern_name or 'api_key' in pattern_name:
                return CCPAArticle.SECTION_1798_150  # Security measures
            elif 'ssn' in pattern_name or 'social_security' in pattern_name:
                return CCPAArticle.SECTION_1798_150  # Security measures
            elif 'credit_card' in pattern_name or 'bank_account' in pattern_name:
                return CCPAArticle.SECTION_1798_150  # Security measures
            elif 'phone' in pattern_name or 'address' in pattern_name:
                return CCPAArticle.SECTION_1798_150  # Security measures
            else:
                return CCPAArticle.SECTION_1798_150  # Default to security
        
        return None
    
    def _generate_remediation_suggestion(self, detection: DetectionMatch, framework: ComplianceFramework, article_ref) -> str:
        """Generate context-aware remediation suggestion."""
        pattern_name = detection.pattern_name.lower()
        
        if 'password' in pattern_name or 'secret' in pattern_name or 'api_key' in pattern_name:
            return "Implement encryption at rest and in transit. Use secure key management systems and environment variables for sensitive data."
        elif 'email' in pattern_name or 'personal' in pattern_name:
            return "Implement data encryption and access controls. Ensure proper data handling procedures are in place."
        elif 'ssn' in pattern_name or 'social_security' in pattern_name:
            return "Implement additional security measures for sensitive personal data. Consider data minimization and purpose limitation."
        elif 'credit_card' in pattern_name or 'bank_account' in pattern_name:
            return "Implement PCI DSS compliance measures. Use tokenization and secure payment processing systems."
        elif 'phone' in pattern_name or 'address' in pattern_name:
            return "Implement data protection measures and access controls for personal contact information."
        else:
            return f"Review and implement appropriate security measures for {detection.pattern_name} data handling."
    
    def _categorize_detection(self, detection: DetectionMatch) -> str:
        """Categorize detection for compliance analysis."""
        pattern_name = detection.pattern_name.lower()
        
        if 'password' in pattern_name or 'secret' in pattern_name or 'api_key' in pattern_name:
            return "authentication_security"
        elif 'email' in pattern_name or 'personal' in pattern_name:
            return "personal_data_exposure"
        elif 'ssn' in pattern_name or 'social_security' in pattern_name:
            return "sensitive_personal_data"
        elif 'credit_card' in pattern_name or 'bank_account' in pattern_name:
            return "financial_data_exposure"
        elif 'phone' in pattern_name or 'address' in pattern_name:
            return "contact_information_exposure"
        else:
            return "general_data_exposure"
    
    def _generate_alerts_from_issues(self, issues: List[ComplianceIssue], 
                                    framework: ComplianceFramework) -> List[ComplianceAlert]:
        """Generate alerts from compliance issues."""
        alerts = []
        
        for issue in issues:
            # Map compliance level to alert severity
            severity_mapping = {
                ComplianceLevel.CRITICAL: AlertSeverity.CRITICAL,
                ComplianceLevel.HIGH: AlertSeverity.HIGH,
                ComplianceLevel.MEDIUM: AlertSeverity.MEDIUM,
                ComplianceLevel.LOW: AlertSeverity.LOW
            }
            
            alert = ComplianceAlert(
                severity=severity_mapping.get(issue.severity, AlertSeverity.MEDIUM),
                framework=framework.value,
                article_ref=issue.article_ref.value,
                title=f"{framework.value} {issue.article_ref.value} Violation",
                description=issue.description,
                file_path=issue.file_path,
                line_number=issue.line_number,
                context=issue.evidence,
                remediation=issue.remediation,
                confidence=issue.confidence,
                category=issue.category,
                matched_text=issue.evidence,
                metadata={
                    "check_type": issue.check_type,
                    "created_at": issue.created_at.isoformat(),
                    "framework": framework.value
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def _calculate_framework_score(self, issues: List[ComplianceIssue]) -> float:
        """Calculate compliance score for a framework."""
        if not issues:
            return 100.0
        
        base_score = 100.0
        penalty_weights = {
            ComplianceLevel.CRITICAL: 15.0,
            ComplianceLevel.HIGH: 10.0,
            ComplianceLevel.MEDIUM: 5.0,
            ComplianceLevel.LOW: 2.0
        }
        
        total_penalty = 0.0
        for issue in issues:
            penalty = penalty_weights.get(issue.severity, 5.0)
            adjusted_penalty = penalty * issue.confidence
            total_penalty += adjusted_penalty
        
        final_score = max(0.0, base_score - total_penalty)
        return min(100.0, final_score)
    
    def _calculate_article_coverage(self, issues: List[ComplianceIssue]) -> Dict[str, int]:
        """Calculate article coverage for issues."""
        coverage = {}
        for issue in issues:
            article = issue.article_ref.value
            coverage[article] = coverage.get(article, 0) + 1
        return coverage
    
    def _generate_framework_recommendations(self, issues: List[ComplianceIssue], 
                                          framework: ComplianceFramework) -> List[str]:
        """Generate recommendations for a framework."""
        recommendations = []
        
        # Count issues by severity
        critical_count = len([i for i in issues if i.severity == ComplianceLevel.CRITICAL])
        high_count = len([i for i in issues if i.severity == ComplianceLevel.HIGH])
        
        if critical_count > 0:
            recommendations.append(f"🔴 Address {critical_count} critical {framework.value} violations immediately")
        
        if high_count > 0:
            recommendations.append(f"🟠 Resolve {high_count} high-priority {framework.value} issues")
        
        # Framework-specific recommendations
        if framework == ComplianceFramework.GDPR:
            recommendations.extend([
                "📋 Ensure all data processing has lawful basis",
                "🛡️ Implement appropriate technical measures",
                "🗑️ Verify data deletion mechanisms",
                "📤 Check DSAR implementation"
            ])
        elif framework == ComplianceFramework.CCPA:
            recommendations.extend([
                "📋 Implement consumer data access requests",
                "🗑️ Provide data deletion mechanisms",
                "🚫 Create opt-out of sale functionality",
                "⚖️ Ensure non-discrimination policies"
            ])
        
        return recommendations[:5]  # Limit to top 5
    
    def _convert_to_unified_violations(self, issues: List[ComplianceIssue], 
                                     framework: ComplianceFramework) -> List[UnifiedViolation]:
        """Convert framework issues to unified violations."""
        unified_violations = []
        
        for issue in issues:
            # Find cross-framework mappings
            cross_framework_mappings = self._find_cross_framework_mappings(issue, framework)
            
            unified_violation = UnifiedViolation(
                id=f"{framework.value}_{issue.article_ref.value}_{issue.file_path}_{issue.line_number}",
                frameworks=[framework] + list(cross_framework_mappings.keys()),
                primary_framework=framework,
                article_refs={framework: issue.article_ref.value},
                severity=issue.severity,
                description=issue.description,
                file_path=issue.file_path,
                line_number=issue.line_number,
                evidence=issue.evidence,
                remediation=issue.remediation,
                confidence=issue.confidence,
                category=issue.category,
                check_type=issue.check_type,
                created_at=issue.created_at,
                cross_framework_mappings=cross_framework_mappings
            )
            
            # Add cross-framework article references
            for mapped_framework, mapped_article in cross_framework_mappings.items():
                unified_violation.article_refs[mapped_framework] = mapped_article
            
            unified_violations.append(unified_violation)
        
        return unified_violations
    
    def _find_cross_framework_mappings(self, issue: ComplianceIssue, 
                                      framework: ComplianceFramework) -> Dict[ComplianceFramework, str]:
        """Find cross-framework mappings for an issue."""
        mappings = {}
        
        # Map based on violation type
        violation_type = self._classify_violation_type(issue)
        
        if violation_type in self.framework_mappings:
            framework_mapping = self.framework_mappings[violation_type]
            
            # Find other frameworks that have this mapping
            for other_framework, article_ref in framework_mapping.items():
                if other_framework != framework and other_framework in self.analyzers:
                    mappings[other_framework] = article_ref
        
        return mappings
    
    def _classify_violation_type(self, issue: ComplianceIssue) -> str:
        """Classify violation type for cross-framework mapping."""
        article = issue.article_ref.value.lower()
        
        # GDPR to violation type mapping
        if "article 15" in article or "right of access" in article.lower():
            return "data_access_right"
        elif "article 17" in article or "right to erasure" in article.lower():
            return "data_deletion_right"
        elif "article 21" in article or "right to object" in article.lower():
            return "opt_out_right"
        elif "article 32" in article or "security" in article.lower():
            return "data_security"
        elif "article 33" in article or "breach" in article.lower():
            return "breach_notification"
        elif "article 22" in article or "discrimination" in article.lower():
            return "non_discrimination"
        
        # CCPA to violation type mapping
        elif "§1798.100" in article or "right to know" in article.lower():
            return "data_access_right"
        elif "§1798.105" in article or "right to delete" in article.lower():
            return "data_deletion_right"
        elif "§1798.120" in article or "opt-out" in article.lower():
            return "opt_out_right"
        elif "§1798.150" in article or "security" in article.lower():
            return "data_security"
        elif "§1798.125" in article or "discrimination" in article.lower():
            return "non_discrimination"
        
        return "unknown"
    
    def _calculate_overall_score(self, framework_results: Dict[ComplianceFramework, FrameworkAnalysisResult]) -> float:
        """Calculate overall compliance score across frameworks."""
        if not framework_results:
            return 0.0
        
        # Weight frameworks equally for now
        total_score = sum(result.compliance_score for result in framework_results.values())
        return total_score / len(framework_results)
    
    def _generate_cross_framework_insights(self, framework_results: Dict[ComplianceFramework, FrameworkAnalysisResult]) -> Dict[str, Any]:
        """Generate cross-framework insights."""
        insights = {
            "framework_count": len(framework_results),
            "score_comparison": {},
            "common_violations": [],
            "framework_specific_issues": {},
            "compliance_gaps": []
        }
        
        # Score comparison
        for framework, result in framework_results.items():
            insights["score_comparison"][framework.value] = result.compliance_score
        
        # Common violations (simplified)
        all_issues = []
        for result in framework_results.values():
            all_issues.extend(result.issues)
        
        # Group by violation type
        violation_types = {}
        for issue in all_issues:
            violation_type = self._classify_violation_type(issue)
            if violation_type not in violation_types:
                violation_types[violation_type] = []
            violation_types[violation_type].append(issue)
        
        # Find common violations
        for violation_type, issues in violation_types.items():
            if len(issues) > 1:  # Appears in multiple frameworks
                insights["common_violations"].append({
                    "type": violation_type,
                    "count": len(issues),
                    "frameworks": list(set(issue.article_ref.value.split()[0] for issue in issues))
                })
        
        return insights
    
    def _generate_unified_recommendations(self, framework_results: Dict[ComplianceFramework, FrameworkAnalysisResult], 
                                         unified_violations: List[UnifiedViolation]) -> List[str]:
        """Generate unified recommendations across frameworks."""
        recommendations = []
        
        # Cross-framework recommendations
        cross_framework_violations = [v for v in unified_violations if len(v.frameworks) > 1]
        if cross_framework_violations:
            recommendations.append(f"🌍 Address {len(cross_framework_violations)} cross-framework violations")
        
        # Framework-specific recommendations
        for framework, result in framework_results.items():
            if result.compliance_score < 70:
                recommendations.append(f"📋 Improve {framework.value} compliance score ({result.compliance_score:.1f})")
        
        # General recommendations
        recommendations.extend([
            "🔄 Implement continuous compliance monitoring",
            "📊 Track compliance metrics across frameworks",
            "🎓 Provide compliance training for development teams",
            "🛡️ Establish unified compliance policies"
        ])
        
        return recommendations[:8]  # Limit to top 8
    
    def get_framework_capabilities(self) -> Dict[str, Any]:
        """Get framework capabilities for current license tier."""
        capabilities = {}
        
        for framework, capability in self.framework_registry.items():
            if self.license_tier >= capability.license_tier_required:
                capabilities[framework.value] = {
                    "available": True,
                    "analyzer_class": capability.analyzer_class,
                    "article_count": capability.article_count,
                    "supported_features": capability.supported_features,
                    "license_tier_required": capability.license_tier_required.value
                }
            else:
                capabilities[framework.value] = {
                    "available": False,
                    "license_tier_required": capability.license_tier_required.value,
                    "upgrade_required": True
                }
        
        return capabilities
    
    def validate_framework_selection(self, frameworks: List[ComplianceFramework]) -> Dict[str, Any]:
        """Validate framework selection for current license tier."""
        validation_result = {
            "valid": True,
            "available_frameworks": [],
            "unavailable_frameworks": [],
            "recommendations": []
        }
        
        available_frameworks = self._get_available_frameworks()
        
        for framework in frameworks:
            if framework in available_frameworks:
                validation_result["available_frameworks"].append(framework.value)
            else:
                validation_result["unavailable_frameworks"].append(framework.value)
                validation_result["valid"] = False
        
        if not validation_result["valid"]:
            validation_result["recommendations"].append(
                f"Upgrade to {self.framework_registry[ComplianceFramework.CCPA].license_tier_required.value} tier for CCPA support"
            )
        
        return validation_result
