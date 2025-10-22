"""
Trend analysis engine for compliance tracking.
Analyzes violation patterns, improvements, and risk scoring over time.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics

from .models import ScanHistoryEntry, ViolationRecord, ViolationTrend, ComplianceMetrics
from .gdpr_mapper import GDPRMapper


@dataclass
class TrendDataPoint:
    """Single data point in a trend analysis."""
    date: date
    value: float
    metadata: Dict[str, Any] = None


@dataclass
class PatternAnalysis:
    """Analysis of violation patterns."""
    common_violation_types: List[Tuple[str, int]]
    common_file_patterns: List[Tuple[str, int]]
    common_gdpr_articles: List[Tuple[str, int]]
    violation_hotspots: List[Tuple[str, int]]  # file paths with most violations
    time_patterns: Dict[str, int]  # violations by day of week, hour, etc.


@dataclass
class RiskAssessment:
    """Risk assessment based on trends."""
    overall_risk: str  # low, medium, high, critical
    risk_factors: List[str]
    risk_score: float  # 0-100
    trend_direction: str  # improving, stable, declining
    recommendations: List[str]


class TrendAnalyzer:
    """Analyzes violation trends and patterns for compliance insights."""
    
    def __init__(self):
        """Initialize trend analyzer."""
        self.logger = logging.getLogger(__name__)
        self.gdpr_mapper = GDPRMapper()
    
    def calculate_violation_trends(self, scans: List[ScanHistoryEntry], 
                                 period_days: int = 30) -> List[ViolationTrend]:
        """Calculate violation trends over time."""
        try:
            if not scans:
                return []
            
            # Sort scans by date
            sorted_scans = sorted(scans, key=lambda x: x.scan_timestamp)
            
            # Group scans by time periods (weekly)
            trends = []
            current_date = sorted_scans[0].scan_timestamp.date()
            end_date = sorted_scans[-1].scan_timestamp.date()
            
            while current_date <= end_date:
                period_end = current_date + timedelta(days=7)
                
                # Get scans in this period
                period_scans = [
                    scan for scan in sorted_scans
                    if current_date <= scan.scan_timestamp.date() < period_end
                ]
                
                if period_scans:
                    trend = self._calculate_period_trend(period_scans, current_date, period_end)
                    trends.append(trend)
                
                current_date = period_end
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to calculate violation trends: {e}")
            return []
    
    def _calculate_period_trend(self, scans: List[ScanHistoryEntry], 
                               start_date: date, end_date: date) -> ViolationTrend:
        """Calculate trend for a specific time period."""
        total_violations = sum(scan.total_violations for scan in scans)
        new_violations = total_violations  # Simplified - would need more complex logic
        remediated_violations = 0  # Would need remediation tracking
        
        # Calculate violation types distribution
        violation_types = defaultdict(int)
        severity_distribution = defaultdict(int)
        gdpr_articles = defaultdict(int)
        
        for scan in scans:
            severity_distribution['critical'] += scan.critical_violations
            severity_distribution['high'] += scan.high_violations
            severity_distribution['medium'] += scan.medium_violations
            severity_distribution['low'] += scan.low_violations
        
        # Calculate improvement percentage (simplified)
        improvement_percentage = 0.0
        if len(scans) > 1:
            first_scan = scans[0]
            last_scan = scans[-1]
            if first_scan.total_violations > 0:
                improvement_percentage = (
                    (first_scan.total_violations - last_scan.total_violations) / 
                    first_scan.total_violations * 100
                )
        
        return ViolationTrend(
            period_start=start_date,
            period_end=end_date,
            total_violations=total_violations,
            new_violations=new_violations,
            remediated_violations=remediated_violations,
            violation_types=dict(violation_types),
            severity_distribution=dict(severity_distribution),
            gdpr_articles=dict(gdpr_articles),
            improvement_percentage=improvement_percentage
        )
    
    def calculate_improvement_metrics(self, trends: List[ViolationTrend]) -> Dict[str, float]:
        """Calculate improvement metrics from trends."""
        if len(trends) < 2:
            return {
                'overall_improvement': 0.0,
                'violation_reduction_rate': 0.0,
                'consistency_score': 0.0
            }
        
        # Calculate overall improvement
        first_trend = trends[0]
        last_trend = trends[-1]
        
        if first_trend.total_violations > 0:
            overall_improvement = (
                (first_trend.total_violations - last_trend.total_violations) / 
                first_trend.total_violations * 100
            )
        else:
            overall_improvement = 0.0
        
        # Calculate violation reduction rate
        violation_counts = [trend.total_violations for trend in trends]
        reduction_rate = self._calculate_reduction_rate(violation_counts)
        
        # Calculate consistency score
        consistency_score = self._calculate_consistency_score(violation_counts)
        
        return {
            'overall_improvement': overall_improvement,
            'violation_reduction_rate': reduction_rate,
            'consistency_score': consistency_score
        }
    
    def _calculate_reduction_rate(self, violation_counts: List[int]) -> float:
        """Calculate the rate of violation reduction."""
        if len(violation_counts) < 2:
            return 0.0
        
        # Calculate average reduction per period
        reductions = []
        for i in range(1, len(violation_counts)):
            if violation_counts[i-1] > 0:
                reduction = (violation_counts[i-1] - violation_counts[i]) / violation_counts[i-1]
                reductions.append(reduction)
        
        return statistics.mean(reductions) * 100 if reductions else 0.0
    
    def _calculate_consistency_score(self, violation_counts: List[int]) -> float:
        """Calculate consistency score (lower variance = higher consistency)."""
        if len(violation_counts) < 2:
            return 100.0
        
        try:
            variance = statistics.variance(violation_counts)
            # Convert variance to consistency score (0-100)
            # Lower variance = higher consistency
            max_variance = max(violation_counts) if violation_counts else 1
            consistency = max(0, 100 - (variance / max_variance * 100))
            return consistency
        except statistics.StatisticsError:
            return 100.0
    
    def identify_patterns(self, violations: List[ViolationRecord]) -> PatternAnalysis:
        """Identify common patterns in violations."""
        try:
            # Analyze violation types
            violation_type_counts = Counter(violation.violation_type.value for violation in violations)
            common_violation_types = violation_type_counts.most_common(10)
            
            # Analyze file patterns
            file_paths = [violation.file_path for violation in violations]
            file_patterns = self._analyze_file_patterns(file_paths)
            
            # Analyze GDPR articles
            gdpr_article_counts = Counter()
            for violation in violations:
                mapping = self.gdpr_mapper.map_violation_to_article(violation)
                gdpr_article_counts[mapping.article.value] += 1
            common_gdpr_articles = gdpr_article_counts.most_common(10)
            
            # Identify violation hotspots
            file_violation_counts = Counter(file_paths)
            violation_hotspots = file_violation_counts.most_common(10)
            
            # Analyze time patterns
            time_patterns = self._analyze_time_patterns(violations)
            
            return PatternAnalysis(
                common_violation_types=common_violation_types,
                common_file_patterns=file_patterns,
                common_gdpr_articles=common_gdpr_articles,
                violation_hotspots=violation_hotspots,
                time_patterns=time_patterns
            )
            
        except Exception as e:
            self.logger.error(f"Failed to identify patterns: {e}")
            return PatternAnalysis(
                common_violation_types=[],
                common_file_patterns=[],
                common_gdpr_articles=[],
                violation_hotspots=[],
                time_patterns={}
            )
    
    def _analyze_file_patterns(self, file_paths: List[str]) -> List[Tuple[str, int]]:
        """Analyze common file patterns in violations."""
        pattern_counts = Counter()
        
        for file_path in file_paths:
            # Extract directory patterns
            path_parts = file_path.split('/')
            if len(path_parts) > 1:
                directory = '/'.join(path_parts[:-1])
                pattern_counts[f"Directory: {directory}"] += 1
            
            # Extract file extension patterns
            if '.' in file_path:
                extension = file_path.split('.')[-1]
                pattern_counts[f"Extension: .{extension}"] += 1
            
            # Extract common patterns
            if 'test' in file_path.lower():
                pattern_counts["Test files"] += 1
            if 'config' in file_path.lower():
                pattern_counts["Config files"] += 1
            if 'log' in file_path.lower():
                pattern_counts["Log files"] += 1
        
        return pattern_counts.most_common(10)
    
    def _analyze_time_patterns(self, violations: List[ViolationRecord]) -> Dict[str, int]:
        """Analyze time-based patterns in violations."""
        patterns = defaultdict(int)
        
        for violation in violations:
            # Day of week pattern
            day_of_week = violation.created_at.strftime('%A')
            patterns[f"Day: {day_of_week}"] += 1
            
            # Hour of day pattern
            hour = violation.created_at.hour
            if 9 <= hour <= 17:
                patterns["Business hours"] += 1
            else:
                patterns["After hours"] += 1
        
        return dict(patterns)
    
    def predict_compliance_risk(self, trends: List[ViolationTrend], 
                               current_violations: List[ViolationRecord]) -> RiskAssessment:
        """Predict compliance risk based on trends and current state."""
        try:
            risk_factors = []
            risk_score = 0.0
            
            # Analyze trend direction
            if len(trends) >= 2:
                recent_trend = trends[-1]
                older_trend = trends[-2]
                
                if recent_trend.total_violations > older_trend.total_violations:
                    risk_factors.append("Increasing violation trend")
                    risk_score += 20
                elif recent_trend.total_violations < older_trend.total_violations:
                    risk_score -= 10  # Improving trend reduces risk
            
            # Analyze current violation severity
            critical_violations = len([v for v in current_violations if v.severity == 'critical'])
            high_violations = len([v for v in current_violations if v.severity == 'high'])
            
            if critical_violations > 0:
                risk_factors.append(f"{critical_violations} critical violations")
                risk_score += critical_violations * 25
            
            if high_violations > 5:
                risk_factors.append(f"{high_violations} high-severity violations")
                risk_score += high_violations * 5
            
            # Analyze GDPR article coverage
            gdpr_articles = set()
            for violation in current_violations:
                mapping = self.gdpr_mapper.map_violation_to_article(violation)
                gdpr_articles.add(mapping.article)
            
            if len(gdpr_articles) > 3:
                risk_factors.append("Multiple GDPR articles affected")
                risk_score += 15
            
            # Determine overall risk level
            if risk_score >= 70:
                overall_risk = "critical"
            elif risk_score >= 50:
                overall_risk = "high"
            elif risk_score >= 30:
                overall_risk = "medium"
            else:
                overall_risk = "low"
            
            # Determine trend direction
            if len(trends) >= 2:
                if trends[-1].improvement_percentage > 10:
                    trend_direction = "improving"
                elif trends[-1].improvement_percentage < -10:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "unknown"
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(risk_factors, overall_risk)
            
            return RiskAssessment(
                overall_risk=overall_risk,
                risk_factors=risk_factors,
                risk_score=min(100.0, max(0.0, risk_score)),
                trend_direction=trend_direction,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Failed to predict compliance risk: {e}")
            return RiskAssessment(
                overall_risk="unknown",
                risk_factors=["Analysis failed"],
                risk_score=50.0,
                trend_direction="unknown",
                recommendations=["Review compliance status manually"]
            )
    
    def _generate_risk_recommendations(self, risk_factors: List[str], 
                                     overall_risk: str) -> List[str]:
        """Generate recommendations based on risk factors."""
        recommendations = []
        
        if "critical violations" in str(risk_factors):
            recommendations.append("Immediately address all critical violations")
            recommendations.append("Implement emergency remediation procedures")
        
        if "Increasing violation trend" in risk_factors:
            recommendations.append("Review and strengthen compliance processes")
            recommendations.append("Implement additional monitoring and controls")
        
        if "Multiple GDPR articles affected" in risk_factors:
            recommendations.append("Conduct comprehensive GDPR compliance review")
            recommendations.append("Implement article-specific remediation plans")
        
        if overall_risk in ["high", "critical"]:
            recommendations.append("Escalate to compliance officer immediately")
            recommendations.append("Consider external compliance audit")
        
        if not recommendations:
            recommendations.append("Continue monitoring compliance status")
            recommendations.append("Maintain current compliance practices")
        
        return recommendations
    
    def generate_heatmaps(self, violations: List[ViolationRecord]) -> Dict[str, Any]:
        """Generate heatmap data for violation hotspots."""
        try:
            # File-level heatmap
            file_violations = defaultdict(int)
            for violation in violations:
                file_violations[violation.file_path] += 1
            
            # Directory-level heatmap
            directory_violations = defaultdict(int)
            for violation in violations:
                directory = '/'.join(violation.file_path.split('/')[:-1])
                directory_violations[directory] += 1
            
            # Severity heatmap
            severity_violations = defaultdict(int)
            for violation in violations:
                severity_violations[violation.severity] += 1
            
            return {
                'file_heatmap': dict(file_violations),
                'directory_heatmap': dict(directory_violations),
                'severity_heatmap': dict(severity_violations)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate heatmaps: {e}")
            return {
                'file_heatmap': {},
                'directory_heatmap': {},
                'severity_heatmap': {}
            }
    
    def calculate_compliance_metrics(self, company_id: str, 
                                   scans: List[ScanHistoryEntry],
                                   violations: List[ViolationRecord]) -> ComplianceMetrics:
        """Calculate overall compliance metrics for a company."""
        try:
            if not scans:
                return ComplianceMetrics(
                    company_id=company_id,
                    period_start=date.today(),
                    period_end=date.today(),
                    total_scans=0,
                    total_violations=0,
                    critical_violations=0,
                    compliance_score=0.0,
                    trend_direction="unknown",
                    gdpr_article_compliance={},
                    risk_level="unknown"
                )
            
            # Calculate basic metrics
            total_scans = len(scans)
            total_violations = len(violations)
            critical_violations = len([v for v in violations if v.severity == 'critical'])
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(violations)
            
            # Determine trend direction
            trends = self.calculate_violation_trends(scans)
            trend_direction = "stable"
            if trends:
                if trends[-1].improvement_percentage > 10:
                    trend_direction = "improving"
                elif trends[-1].improvement_percentage < -10:
                    trend_direction = "declining"
            
            # Calculate GDPR article compliance
            gdpr_article_compliance = self.gdpr_mapper.calculate_compliance_score(violations)
            
            # Determine risk level
            risk_assessment = self.predict_compliance_risk(trends, violations)
            risk_level = risk_assessment.overall_risk
            
            # Calculate date range
            scan_dates = [scan.scan_timestamp.date() for scan in scans]
            period_start = min(scan_dates) if scan_dates else date.today()
            period_end = max(scan_dates) if scan_dates else date.today()
            
            # Calculate days since last scan
            last_scan_date = max(scan.scan_timestamp for scan in scans) if scans else None
            days_since_last_scan = None
            if last_scan_date:
                days_since_last_scan = (datetime.now().date() - last_scan_date.date()).days
            
            return ComplianceMetrics(
                company_id=company_id,
                period_start=period_start,
                period_end=period_end,
                total_scans=total_scans,
                total_violations=total_violations,
                critical_violations=critical_violations,
                compliance_score=compliance_score,
                trend_direction=trend_direction,
                gdpr_article_compliance=gdpr_article_compliance,
                risk_level=risk_level,
                last_scan_date=last_scan_date,
                days_since_last_scan=days_since_last_scan
            )
            
        except Exception as e:
            self.logger.error(f"Failed to calculate compliance metrics: {e}")
            return ComplianceMetrics(
                company_id=company_id,
                period_start=date.today(),
                period_end=date.today(),
                total_scans=0,
                total_violations=0,
                critical_violations=0,
                compliance_score=0.0,
                trend_direction="unknown",
                gdpr_article_compliance={},
                risk_level="unknown"
            )
    
    def _calculate_compliance_score(self, violations: List[ViolationRecord]) -> float:
        """Calculate overall compliance score (0-100)."""
        if not violations:
            return 100.0
        
        # Start with perfect score
        score = 100.0
        
        # Deduct points for violations
        for violation in violations:
            if violation.severity == 'critical':
                score -= 20
            elif violation.severity == 'high':
                score -= 10
            elif violation.severity == 'medium':
                score -= 5
            else:
                score -= 2
        
        # Ensure score doesn't go below 0
        return max(0.0, score)
