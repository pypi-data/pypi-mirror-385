"""
Compliance Scoring Engine - Industry-grade compliance scoring with benchmarks.

Provides weighted scoring by GDPR/CCPA article, industry benchmarks, and compliance
grading (A+ to F) for enterprise compliance assessment.
"""

import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import statistics

from ..core.config import Config, LicenseTier
from ..core.exceptions import DetectionError
from .models import ComplianceIssue, ComplianceLevel, GDPRArticle
from .compliance_alerter import ComplianceAlert, AlertSeverity


logger = logging.getLogger(__name__)


class ComplianceGrade(str, Enum):
    """Compliance grade levels."""
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class IndustryType(str, Enum):
    """Industry types for benchmarking."""
    SAAS = "SaaS"
    FINTECH = "FinTech"
    HEALTHTECH = "HealthTech"
    ECOMMERCE = "E-commerce"
    GENERAL = "General"


@dataclass
class ArticleWeight:
    """Weight configuration for GDPR/CCPA articles."""
    article: str
    weight: float
    critical_penalty: float
    high_penalty: float
    medium_penalty: float
    low_penalty: float
    description: str


@dataclass
class ComplianceScore:
    """Comprehensive compliance score result."""
    overall_score: float
    grade: ComplianceGrade
    article_scores: Dict[str, float]
    weighted_score: float
    industry_benchmark: float
    percentile_ranking: int
    trend_direction: str  # improving, stable, declining
    risk_level: str  # low, medium, high, critical
    scoring_breakdown: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class IndustryBenchmark:
    """Industry benchmark data."""
    industry: IndustryType
    average_score: float
    top_quartile: float
    median: float
    bottom_quartile: float
    sample_size: int
    last_updated: date


class ComplianceScorer:
    """
    Industry-grade compliance scoring engine.
    
    Provides weighted scoring by GDPR/CCPA article, industry benchmarks,
    and compliance grading for enterprise compliance assessment.
    """
    
    def __init__(self, config: Config):
        """Initialize the compliance scorer."""
        self.config = config
        self.license_tier = config.license.tier
        
        # Initialize article weights
        self.article_weights = self._initialize_article_weights()
        
        # Initialize industry benchmarks
        self.industry_benchmarks = self._initialize_industry_benchmarks()
        
        # Scoring configuration
        self.base_score = 100.0
        self.max_bonus = 15.0
        self.min_score = 0.0
        
        logger.info("Compliance Scorer initialized successfully")
    
    def _initialize_article_weights(self) -> Dict[str, ArticleWeight]:
        """Initialize article weights for scoring."""
        return {
            # Article 32 - Security (highest weight)
            "GDPR Article 32": ArticleWeight(
                article="GDPR Article 32",
                weight=1.5,
                critical_penalty=20.0,
                high_penalty=15.0,
                medium_penalty=8.0,
                low_penalty=3.0,
                description="Security of processing - Critical for data protection"
            ),
            
            # Article 6 - Lawful basis (high weight)
            "GDPR Article 6": ArticleWeight(
                article="GDPR Article 6",
                weight=1.3,
                critical_penalty=18.0,
                high_penalty=12.0,
                medium_penalty=6.0,
                low_penalty=2.0,
                description="Lawful basis for processing - Fundamental requirement"
            ),
            
            # Article 17 - Right to erasure (high weight)
            "GDPR Article 17": ArticleWeight(
                article="GDPR Article 17",
                weight=1.3,
                critical_penalty=18.0,
                high_penalty=12.0,
                medium_penalty=6.0,
                low_penalty=2.0,
                description="Right to erasure - Critical data subject right"
            ),
            
            # Article 15 - Right of access (medium-high weight)
            "GDPR Article 15": ArticleWeight(
                article="GDPR Article 15",
                weight=1.2,
                critical_penalty=15.0,
                high_penalty=10.0,
                medium_penalty=5.0,
                low_penalty=2.0,
                description="Right of access - Important data subject right"
            ),
            
            # Article 25 - Data protection by design (medium weight)
            "GDPR Article 25": ArticleWeight(
                article="GDPR Article 25",
                weight=1.1,
                critical_penalty=12.0,
                high_penalty=8.0,
                medium_penalty=4.0,
                low_penalty=1.5,
                description="Data protection by design and default"
            ),
            
            # Article 5(1)(c) - Data minimization (medium weight)
            "GDPR Article 5(1)(c)": ArticleWeight(
                article="GDPR Article 5(1)(c)",
                weight=1.1,
                critical_penalty=12.0,
                high_penalty=8.0,
                medium_penalty=4.0,
                low_penalty=1.5,
                description="Data minimization principle"
            ),
            
            # Article 44-49 - Cross-border transfers (medium weight)
            "GDPR Articles 44-49": ArticleWeight(
                article="GDPR Articles 44-49",
                weight=1.0,
                critical_penalty=10.0,
                high_penalty=7.0,
                medium_penalty=3.5,
                low_penalty=1.0,
                description="Cross-border data transfers"
            ),
            
            # Article 7 - Conditions for consent (medium weight)
            "GDPR Article 7": ArticleWeight(
                article="GDPR Article 7",
                weight=1.0,
                critical_penalty=10.0,
                high_penalty=7.0,
                medium_penalty=3.5,
                low_penalty=1.0,
                description="Conditions for consent"
            ),
            
            # Article 30 - Records of processing (lower weight)
            "GDPR Article 30": ArticleWeight(
                article="GDPR Article 30",
                weight=0.8,
                critical_penalty=8.0,
                high_penalty=5.0,
                medium_penalty=2.5,
                low_penalty=0.8,
                description="Records of processing activities"
            ),
            
            # Article 33-34 - Breach notification (lower weight)
            "GDPR Article 33": ArticleWeight(
                article="GDPR Article 33",
                weight=0.8,
                critical_penalty=8.0,
                high_penalty=5.0,
                medium_penalty=2.5,
                low_penalty=0.8,
                description="Breach notification to supervisory authority"
            ),
            "GDPR Article 34": ArticleWeight(
                article="GDPR Article 34",
                weight=0.8,
                critical_penalty=8.0,
                high_penalty=5.0,
                medium_penalty=2.5,
                low_penalty=0.8,
                description="Breach notification to data subject"
            ),
            
            # CCPA articles (similar weights to GDPR)
            "CCPA §1798.100": ArticleWeight(
                article="CCPA §1798.100",
                weight=1.2,
                critical_penalty=15.0,
                high_penalty=10.0,
                medium_penalty=5.0,
                low_penalty=2.0,
                description="Right to Know - CCPA data access right"
            ),
            "CCPA §1798.105": ArticleWeight(
                article="CCPA §1798.105",
                weight=1.3,
                critical_penalty=18.0,
                high_penalty=12.0,
                medium_penalty=6.0,
                low_penalty=2.0,
                description="Right to Delete - CCPA data deletion right"
            ),
            "CCPA §1798.120": ArticleWeight(
                article="CCPA §1798.120",
                weight=1.1,
                critical_penalty=12.0,
                high_penalty=8.0,
                medium_penalty=4.0,
                low_penalty=1.5,
                description="Right to Opt-Out - CCPA sale opt-out right"
            ),
            "CCPA §1798.150": ArticleWeight(
                article="CCPA §1798.150",
                weight=1.5,
                critical_penalty=20.0,
                high_penalty=15.0,
                medium_penalty=8.0,
                low_penalty=3.0,
                description="Data Security - CCPA security requirements"
            )
        }
    
    def _initialize_industry_benchmarks(self) -> Dict[IndustryType, IndustryBenchmark]:
        """Initialize industry benchmark data."""
        return {
            IndustryType.SAAS: IndustryBenchmark(
                industry=IndustryType.SAAS,
                average_score=78.5,
                top_quartile=89.2,
                median=76.8,
                bottom_quartile=65.4,
                sample_size=1250,
                last_updated=date.today()
            ),
            IndustryType.FINTECH: IndustryBenchmark(
                industry=IndustryType.FINTECH,
                average_score=85.3,
                top_quartile=92.7,
                median=84.1,
                bottom_quartile=72.9,
                sample_size=890,
                last_updated=date.today()
            ),
            IndustryType.HEALTHTECH: IndustryBenchmark(
                industry=IndustryType.HEALTHTECH,
                average_score=88.7,
                top_quartile=94.5,
                median=87.2,
                bottom_quartile=78.3,
                sample_size=650,
                last_updated=date.today()
            ),
            IndustryType.ECOMMERCE: IndustryBenchmark(
                industry=IndustryType.ECOMMERCE,
                average_score=72.1,
                top_quartile=84.6,
                median=71.8,
                bottom_quartile=58.9,
                sample_size=2100,
                last_updated=date.today()
            ),
            IndustryType.GENERAL: IndustryBenchmark(
                industry=IndustryType.GENERAL,
                average_score=75.0,
                top_quartile=87.5,
                median=74.2,
                bottom_quartile=62.8,
                sample_size=5000,
                last_updated=date.today()
            )
        }
    
    def calculate_compliance_score(self, alerts: List[ComplianceAlert], 
                                  issues: List[ComplianceIssue],
                                  industry: IndustryType = IndustryType.GENERAL,
                                  historical_scores: Optional[List[float]] = None) -> ComplianceScore:
        """
        Calculate comprehensive compliance score.
        
        Args:
            alerts: List of compliance alerts
            issues: List of compliance issues
            industry: Industry type for benchmarking
            historical_scores: Historical scores for trend analysis
            
        Returns:
            Comprehensive compliance score result
        """
        try:
            # Calculate article-specific scores
            article_scores = self._calculate_article_scores(alerts, issues)
            
            # Calculate weighted overall score
            weighted_score = self._calculate_weighted_score(article_scores)
            
            # Apply bonuses for proactive controls
            bonus_points = self._calculate_proactive_bonus(alerts, issues)
            
            # Calculate final score
            overall_score = min(self.base_score, weighted_score + bonus_points)
            overall_score = max(self.min_score, overall_score)
            
            # Determine grade
            grade = self._calculate_grade(overall_score)
            
            # Get industry benchmark
            benchmark = self.industry_benchmarks[industry]
            
            # Calculate percentile ranking
            percentile_ranking = self._calculate_percentile_ranking(overall_score, benchmark)
            
            # Determine trend direction
            trend_direction = self._calculate_trend_direction(overall_score, historical_scores)
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_score, alerts, issues)
            
            # Generate scoring breakdown
            scoring_breakdown = self._generate_scoring_breakdown(
                article_scores, weighted_score, bonus_points, overall_score
            )
            
            # Generate recommendations
            recommendations = self._generate_score_recommendations(
                overall_score, grade, article_scores, alerts, issues
            )
            
            return ComplianceScore(
                overall_score=overall_score,
                grade=grade,
                article_scores=article_scores,
                weighted_score=weighted_score,
                industry_benchmark=benchmark.average_score,
                percentile_ranking=percentile_ranking,
                trend_direction=trend_direction,
                risk_level=risk_level,
                scoring_breakdown=scoring_breakdown,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate compliance score: {e}")
            raise DetectionError(f"Score calculation failed: {e}")
    
    def _calculate_article_scores(self, alerts: List[ComplianceAlert], 
                                 issues: List[ComplianceIssue]) -> Dict[str, float]:
        """Calculate scores for each GDPR/CCPA article."""
        article_data = {}
        
        # Process alerts
        for alert in alerts:
            article = alert.article_ref
            if article not in article_data:
                article_data[article] = {
                    'violations': [],
                    'weight': self.article_weights.get(article, self.article_weights["GDPR Article 32"]).weight
                }
            article_data[article]['violations'].append(alert)
        
        # Process compliance issues
        for issue in issues:
            article = issue.article_ref.value
            if article not in article_data:
                article_data[article] = {
                    'violations': [],
                    'weight': self.article_weights.get(article, self.article_weights["GDPR Article 32"]).weight
                }
            article_data[article]['violations'].append(issue)
        
        # Calculate scores for each article
        article_scores = {}
        for article, data in article_data.items():
            score = self.base_score
            weight_config = self.article_weights.get(article, self.article_weights["GDPR Article 32"])
            
            # Apply penalties based on violation severity
            for violation in data['violations']:
                if isinstance(violation, ComplianceAlert):
                    severity = violation.severity
                    confidence = violation.confidence
                else:  # ComplianceIssue
                    severity_mapping = {
                        ComplianceLevel.CRITICAL: AlertSeverity.CRITICAL,
                        ComplianceLevel.HIGH: AlertSeverity.HIGH,
                        ComplianceLevel.MEDIUM: AlertSeverity.MEDIUM,
                        ComplianceLevel.LOW: AlertSeverity.LOW
                    }
                    severity = severity_mapping.get(violation.severity, AlertSeverity.MEDIUM)
                    confidence = violation.confidence
                
                # Get penalty based on severity
                if severity == AlertSeverity.CRITICAL:
                    penalty = weight_config.critical_penalty
                elif severity == AlertSeverity.HIGH:
                    penalty = weight_config.high_penalty
                elif severity == AlertSeverity.MEDIUM:
                    penalty = weight_config.medium_penalty
                else:
                    penalty = weight_config.low_penalty
                
                # Apply penalty with confidence adjustment
                adjusted_penalty = penalty * confidence
                score -= adjusted_penalty
            
            # Apply article weight
            weighted_score = score * data['weight']
            article_scores[article] = max(self.min_score, min(self.base_score, weighted_score))
        
        return article_scores
    
    def _calculate_weighted_score(self, article_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score from article scores."""
        if not article_scores:
            return self.base_score
        
        # Calculate weighted average
        total_weight = 0.0
        weighted_sum = 0.0
        
        for article, score in article_scores.items():
            weight = self.article_weights.get(article, self.article_weights["GDPR Article 32"]).weight
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return self.base_score
        
        return weighted_sum / total_weight
    
    def _calculate_proactive_bonus(self, alerts: List[ComplianceAlert], 
                                   issues: List[ComplianceIssue]) -> float:
        """Calculate bonus points for proactive compliance controls."""
        bonus = 0.0
        
        # Check for encryption controls
        encryption_indicators = [
            'encryption', 'tls', 'ssl', 'https', 'aes', 'rsa'
        ]
        encryption_found = any(
            any(indicator in alert.title.lower() for indicator in encryption_indicators)
            for alert in alerts
        )
        if encryption_found:
            bonus += 3.0
        
        # Check for DSAR implementation
        dsar_indicators = ['dsar', 'data access', 'export user', 'personal data']
        dsar_found = any(
            any(indicator in alert.title.lower() for indicator in dsar_indicators)
            for alert in alerts
        )
        if dsar_found:
            bonus += 3.0
        
        # Check for deletion mechanisms
        deletion_indicators = ['deletion', 'erasure', 'delete user', 'purge']
        deletion_found = any(
            any(indicator in alert.title.lower() for indicator in deletion_indicators)
            for alert in alerts
        )
        if deletion_found:
            bonus += 3.0
        
        # Check for consent mechanisms
        consent_indicators = ['consent', 'opt-in', 'permission', 'agreement']
        consent_found = any(
            any(indicator in alert.title.lower() for indicator in consent_indicators)
            for alert in alerts
        )
        if consent_found:
            bonus += 2.0
        
        # Check for audit logging
        audit_indicators = ['audit', 'logging', 'tracking', 'monitoring']
        audit_found = any(
            any(indicator in alert.title.lower() for indicator in audit_indicators)
            for alert in alerts
        )
        if audit_found:
            bonus += 2.0
        
        # Check for data minimization
        minimization_indicators = ['minimization', 'minimal', 'necessary', 'limited']
        minimization_found = any(
            any(indicator in alert.title.lower() for indicator in minimization_indicators)
            for alert in alerts
        )
        if minimization_found:
            bonus += 2.0
        
        return min(bonus, self.max_bonus)
    
    def _calculate_grade(self, score: float) -> ComplianceGrade:
        """Calculate compliance grade from score."""
        if score >= 95:
            return ComplianceGrade.A_PLUS
        elif score >= 90:
            return ComplianceGrade.A
        elif score >= 80:
            return ComplianceGrade.B
        elif score >= 70:
            return ComplianceGrade.C
        elif score >= 60:
            return ComplianceGrade.D
        else:
            return ComplianceGrade.F
    
    def _calculate_percentile_ranking(self, score: float, 
                                      benchmark: IndustryBenchmark) -> int:
        """Calculate percentile ranking against industry benchmark."""
        if score >= benchmark.top_quartile:
            return 90
        elif score >= benchmark.median:
            return 75
        elif score >= benchmark.bottom_quartile:
            return 50
        else:
            return 25
    
    def _calculate_trend_direction(self, current_score: float, 
                                  historical_scores: Optional[List[float]]) -> str:
        """Calculate trend direction from historical scores."""
        if not historical_scores or len(historical_scores) < 2:
            return "stable"
        
        # Calculate trend over last 3 scores
        recent_scores = historical_scores[-3:]
        if len(recent_scores) < 2:
            return "stable"
        
        # Calculate average change
        changes = []
        for i in range(1, len(recent_scores)):
            changes.append(recent_scores[i] - recent_scores[i-1])
        
        avg_change = statistics.mean(changes)
        
        if avg_change > 2.0:
            return "improving"
        elif avg_change < -2.0:
            return "declining"
        else:
            return "stable"
    
    def _determine_risk_level(self, score: float, alerts: List[ComplianceAlert], 
                              issues: List[ComplianceIssue]) -> str:
        """Determine overall risk level."""
        critical_count = len([a for a in alerts if a.severity == AlertSeverity.CRITICAL])
        critical_count += len([i for i in issues if i.severity == ComplianceLevel.CRITICAL])
        
        if score < 50 or critical_count > 5:
            return "critical"
        elif score < 70 or critical_count > 2:
            return "high"
        elif score < 85:
            return "medium"
        else:
            return "low"
    
    def _generate_scoring_breakdown(self, article_scores: Dict[str, float], 
                                   weighted_score: float, bonus_points: float, 
                                   overall_score: float) -> Dict[str, Any]:
        """Generate detailed scoring breakdown."""
        return {
            "base_score": self.base_score,
            "article_penalties": {
                article: self.base_score - score 
                for article, score in article_scores.items()
            },
            "weighted_score": weighted_score,
            "proactive_bonus": bonus_points,
            "final_score": overall_score,
            "score_distribution": {
                "excellent": len([s for s in article_scores.values() if s >= 90]),
                "good": len([s for s in article_scores.values() if 80 <= s < 90]),
                "fair": len([s for s in article_scores.values() if 70 <= s < 80]),
                "poor": len([s for s in article_scores.values() if s < 70])
            }
        }
    
    def _generate_score_recommendations(self, score: float, grade: ComplianceGrade,
                                       article_scores: Dict[str, float],
                                       alerts: List[ComplianceAlert],
                                       issues: List[ComplianceIssue]) -> List[str]:
        """Generate recommendations based on score."""
        recommendations = []
        
        # Score-based recommendations
        if grade == ComplianceGrade.F:
            recommendations.append("🚨 URGENT: Immediate compliance intervention required")
        elif grade == ComplianceGrade.D:
            recommendations.append("⚠️ CRITICAL: Significant compliance improvements needed")
        elif grade == ComplianceGrade.C:
            recommendations.append("📋 IMPORTANT: Address compliance gaps to improve score")
        
        # Article-specific recommendations
        poor_articles = [article for article, score in article_scores.items() if score < 70]
        if poor_articles:
            recommendations.append(f"🎯 Focus on improving {len(poor_articles)} poorly performing articles")
        
        # Critical issues
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        if critical_alerts:
            recommendations.append(f"🔴 Address {len(critical_alerts)} critical violations immediately")
        
        # Security recommendations
        security_articles = [a for a in alerts if 'security' in a.category.lower()]
        if security_articles:
            recommendations.append("🛡️ Strengthen data security measures and encryption")
        
        # DSAR recommendations
        dsar_articles = [a for a in alerts if 'dsar' in a.title.lower()]
        if dsar_articles:
            recommendations.append("📤 Implement comprehensive DSAR system")
        
        # General recommendations
        recommendations.extend([
            "📊 Implement continuous compliance monitoring",
            "🎓 Provide compliance training for development teams",
            "🔄 Establish regular compliance review cycles",
            "📈 Track compliance metrics and trends over time"
        ])
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def get_industry_benchmark(self, industry: IndustryType) -> IndustryBenchmark:
        """Get industry benchmark data."""
        return self.industry_benchmarks[industry]
    
    def compare_to_industry(self, score: float, industry: IndustryType) -> Dict[str, Any]:
        """Compare score to industry benchmark."""
        benchmark = self.industry_benchmarks[industry]
        
        return {
            "score": score,
            "industry_average": benchmark.average_score,
            "industry_median": benchmark.median,
            "industry_top_quartile": benchmark.top_quartile,
            "industry_bottom_quartile": benchmark.bottom_quartile,
            "vs_average": score - benchmark.average_score,
            "vs_median": score - benchmark.median,
            "percentile_ranking": self._calculate_percentile_ranking(score, benchmark),
            "performance_level": self._get_performance_level(score, benchmark)
        }
    
    def _get_performance_level(self, score: float, benchmark: IndustryBenchmark) -> str:
        """Get performance level relative to industry."""
        if score >= benchmark.top_quartile:
            return "Top Performer"
        elif score >= benchmark.median:
            return "Above Average"
        elif score >= benchmark.bottom_quartile:
            return "Average"
        else:
            return "Below Average"
    
    def export_score_report(self, score_result: ComplianceScore, 
                           format: str = "json") -> str:
        """Export compliance score report."""
        if format.lower() == "json":
            return json.dumps(asdict(score_result), indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
