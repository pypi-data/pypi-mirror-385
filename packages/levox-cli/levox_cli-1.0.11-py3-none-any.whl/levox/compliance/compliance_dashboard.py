"""
Compliance Dashboard Generator - Executive-level compliance reporting.

Provides comprehensive compliance dashboards with trend analysis, risk heatmaps,
and executive summaries for audit-ready reporting.
"""

import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import uuid

from ..core.config import Config, LicenseTier
from ..core.exceptions import DetectionError
from ..models.detection_result import DetectionResult
from .models import ComplianceIssue, ComplianceLevel, GDPRArticle
from .compliance_alerter import ComplianceAlert, AlertSeverity


logger = logging.getLogger(__name__)


@dataclass
class ComplianceTrend:
    """Compliance trend data over time."""
    period_start: date
    period_end: date
    compliance_score: float
    total_violations: int
    critical_violations: int
    high_violations: int
    medium_violations: int
    low_violations: int
    improvement_percentage: float = 0.0
    trend_direction: str = "stable"  # improving, stable, declining


@dataclass
class RiskHeatmap:
    """Risk heatmap data for compliance visualization."""
    article: str
    violation_count: int
    severity_distribution: Dict[str, int]
    risk_level: str  # low, medium, high, critical
    trend_direction: str  # improving, stable, declining


@dataclass
class ComplianceMaturity:
    """Compliance maturity assessment."""
    level: int  # 1-5
    title: str
    description: str
    requirements: List[str]
    next_level_requirements: List[str]


@dataclass
class ExecutiveSummary:
    """Executive summary for compliance dashboard."""
    overall_score: float
    grade: str  # A+, A, B, C, D, F
    critical_issues: int
    high_priority_actions: List[str]
    compliance_status: str  # compliant, at-risk, non-compliant
    industry_benchmark: Optional[float] = None
    percentile_ranking: Optional[int] = None


class ComplianceDashboard:
    """
    Executive-level compliance dashboard generator.
    
    Creates comprehensive compliance dashboards with trend analysis, risk heatmaps,
    compliance scoring, and executive summaries for audit-ready reporting.
    """
    
    def __init__(self, config: Config):
        """Initialize the compliance dashboard generator."""
        self.config = config
        self.license_tier = config.license.tier
        
        # Industry benchmark data (simplified for demo)
        self.industry_benchmarks = self._initialize_industry_benchmarks()
        
        # Compliance maturity model
        self.maturity_model = self._initialize_maturity_model()
        
        logger.info("Compliance Dashboard Generator initialized successfully")
    
    def _initialize_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Initialize industry benchmark data."""
        return {
            "SaaS": {
                "average_score": 78.5,
                "top_quartile": 89.2,
                "median": 76.8,
                "bottom_quartile": 65.4
            },
            "FinTech": {
                "average_score": 85.3,
                "top_quartile": 92.7,
                "median": 84.1,
                "bottom_quartile": 72.9
            },
            "HealthTech": {
                "average_score": 88.7,
                "top_quartile": 94.5,
                "median": 87.2,
                "bottom_quartile": 78.3
            },
            "E-commerce": {
                "average_score": 72.1,
                "top_quartile": 84.6,
                "median": 71.8,
                "bottom_quartile": 58.9
            },
            "General": {
                "average_score": 75.0,
                "top_quartile": 87.5,
                "median": 74.2,
                "bottom_quartile": 62.8
            }
        }
    
    def _initialize_maturity_model(self) -> Dict[int, ComplianceMaturity]:
        """Initialize compliance maturity model."""
        return {
            1: ComplianceMaturity(
                level=1,
                title="Initial",
                description="Basic compliance awareness with ad-hoc processes",
                requirements=[
                    "Basic PII detection implemented",
                    "Manual compliance checks",
                    "Limited documentation"
                ],
                next_level_requirements=[
                    "Implement automated compliance scanning",
                    "Create compliance policies",
                    "Establish regular audit cycles"
                ]
            ),
            2: ComplianceMaturity(
                level=2,
                title="Managed",
                description="Structured compliance processes with regular monitoring",
                requirements=[
                    "Automated compliance scanning",
                    "Regular compliance reports",
                    "Basic remediation processes",
                    "Compliance policies documented"
                ],
                next_level_requirements=[
                    "Implement compliance scoring",
                    "Create executive dashboards",
                    "Establish trend monitoring"
                ]
            ),
            3: ComplianceMaturity(
                level=3,
                title="Defined",
                description="Comprehensive compliance program with metrics and trends",
                requirements=[
                    "Compliance scoring implemented",
                    "Executive dashboards available",
                    "Trend analysis and monitoring",
                    "Industry benchmarking"
                ],
                next_level_requirements=[
                    "Implement predictive compliance",
                    "Create compliance automation",
                    "Establish continuous improvement"
                ]
            ),
            4: ComplianceMaturity(
                level=4,
                title="Quantitatively Managed",
                description="Data-driven compliance with predictive capabilities",
                requirements=[
                    "Predictive compliance analytics",
                    "Automated remediation workflows",
                    "Continuous compliance monitoring",
                    "Advanced risk assessment"
                ],
                next_level_requirements=[
                    "Implement AI-powered compliance",
                    "Create real-time compliance monitoring",
                    "Establish compliance excellence"
                ]
            ),
            5: ComplianceMaturity(
                level=5,
                title="Optimizing",
                description="Continuous improvement and innovation in compliance",
                requirements=[
                    "AI-powered compliance insights",
                    "Real-time compliance monitoring",
                    "Continuous improvement processes",
                    "Industry leadership in compliance"
                ],
                next_level_requirements=[
                    "Maintain compliance excellence",
                    "Share best practices",
                    "Drive industry standards"
                ]
            )
        }
    
    def generate_dashboard(self, compliance_data: Dict[str, Any], 
                          industry: str = "General") -> Dict[str, Any]:
        """
        Generate a comprehensive compliance dashboard.
        
        Args:
            compliance_data: Compliance data including alerts, issues, and trends
            industry: Industry type for benchmarking
            
        Returns:
            Complete dashboard data structure
        """
        try:
            # Extract data
            alerts = compliance_data.get('alerts', [])
            issues = compliance_data.get('issues', [])
            trends = compliance_data.get('trends', [])
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(alerts, issues)
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                compliance_score, alerts, issues, industry
            )
            
            # Generate risk heatmap
            risk_heatmap = self._generate_risk_heatmap(alerts, issues)
            
            # Generate trend analysis
            trend_analysis = self._generate_trend_analysis(trends)
            
            # Assess compliance maturity
            maturity_assessment = self._assess_compliance_maturity(compliance_score, alerts)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(alerts, issues, compliance_score)
            
            # Create dashboard
            dashboard = {
                "dashboard_id": str(uuid.uuid4()),
                "generated_at": datetime.now().isoformat(),
                "industry": industry,
                "license_tier": self.license_tier.value,
                "executive_summary": asdict(executive_summary),
                "compliance_score": compliance_score,
                "risk_heatmap": [asdict(risk) for risk in risk_heatmap],
                "trend_analysis": [asdict(trend) for trend in trend_analysis],
                "maturity_assessment": asdict(maturity_assessment),
                "recommendations": recommendations,
                "industry_benchmark": self.industry_benchmarks.get(industry, self.industry_benchmarks["General"]),
                "metadata": {
                    "total_alerts": len(alerts),
                    "total_issues": len(issues),
                    "analysis_period": self._get_analysis_period(trends),
                    "framework_coverage": self._get_framework_coverage(alerts)
                }
            }
            
            logger.info(f"Compliance dashboard generated successfully: {dashboard['dashboard_id']}")
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to generate compliance dashboard: {e}")
            raise DetectionError(f"Dashboard generation failed: {e}")
    
    def _calculate_compliance_score(self, alerts: List[ComplianceAlert], 
                                   issues: List[ComplianceIssue]) -> float:
        """Calculate overall compliance score (0-100)."""
        if not alerts and not issues:
            return 100.0
        
        # Base score
        score = 100.0
        
        # Penalty system
        penalty_weights = {
            AlertSeverity.CRITICAL: 15.0,
            AlertSeverity.HIGH: 10.0,
            AlertSeverity.MEDIUM: 5.0,
            AlertSeverity.LOW: 2.0,
            AlertSeverity.INFO: 0.5
        }
        
        # Apply penalties for alerts
        for alert in alerts:
            penalty = penalty_weights.get(alert.severity, 5.0)
            # Adjust penalty based on confidence
            adjusted_penalty = penalty * alert.confidence
            score -= adjusted_penalty
        
        # Apply penalties for compliance issues
        severity_penalties = {
            ComplianceLevel.CRITICAL: 15.0,
            ComplianceLevel.HIGH: 10.0,
            ComplianceLevel.MEDIUM: 5.0,
            ComplianceLevel.LOW: 2.0
        }
        
        for issue in issues:
            penalty = severity_penalties.get(issue.severity, 5.0)
            # Adjust penalty based on confidence
            adjusted_penalty = penalty * issue.confidence
            score -= adjusted_penalty
        
        # Bonus for proactive controls
        bonus_points = self._calculate_proactive_bonus(alerts, issues)
        score += bonus_points
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, score))
    
    def _calculate_proactive_bonus(self, alerts: List[ComplianceAlert], 
                                   issues: List[ComplianceIssue]) -> float:
        """Calculate bonus points for proactive compliance controls."""
        bonus = 0.0
        
        # Check for encryption controls
        encryption_controls = [
            alert for alert in alerts 
            if 'encryption' in alert.title.lower() or 'tls' in alert.title.lower()
        ]
        if encryption_controls:
            bonus += 2.0
        
        # Check for DSAR implementation
        dsar_controls = [
            alert for alert in alerts 
            if 'dsar' in alert.title.lower() or 'data access' in alert.title.lower()
        ]
        if dsar_controls:
            bonus += 2.0
        
        # Check for deletion mechanisms
        deletion_controls = [
            alert for alert in alerts 
            if 'deletion' in alert.title.lower() or 'erasure' in alert.title.lower()
        ]
        if deletion_controls:
            bonus += 2.0
        
        # Check for consent mechanisms
        consent_controls = [
            alert for alert in alerts 
            if 'consent' in alert.title.lower()
        ]
        if consent_controls:
            bonus += 1.0
        
        return min(bonus, 10.0)  # Cap bonus at 10 points
    
    def _generate_executive_summary(self, compliance_score: float, 
                                   alerts: List[ComplianceAlert], 
                                   issues: List[ComplianceIssue],
                                   industry: str) -> ExecutiveSummary:
        """Generate executive summary."""
        # Calculate grade
        grade = self._calculate_grade(compliance_score)
        
        # Count critical issues
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        critical_issues = [i for i in issues if i.severity == ComplianceLevel.CRITICAL]
        critical_count = len(critical_alerts) + len(critical_issues)
        
        # Determine compliance status
        if compliance_score >= 90:
            status = "compliant"
        elif compliance_score >= 70:
            status = "at-risk"
        else:
            status = "non-compliant"
        
        # Generate high priority actions
        high_priority_actions = self._generate_high_priority_actions(alerts, issues)
        
        # Get industry benchmark
        benchmark_data = self.industry_benchmarks.get(industry, self.industry_benchmarks["General"])
        industry_benchmark = benchmark_data["average_score"]
        
        # Calculate percentile ranking
        percentile_ranking = self._calculate_percentile_ranking(compliance_score, benchmark_data)
        
        return ExecutiveSummary(
            overall_score=compliance_score,
            grade=grade,
            critical_issues=critical_count,
            high_priority_actions=high_priority_actions,
            compliance_status=status,
            industry_benchmark=industry_benchmark,
            percentile_ranking=percentile_ranking
        )
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate compliance grade from score."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_high_priority_actions(self, alerts: List[ComplianceAlert], 
                                       issues: List[ComplianceIssue]) -> List[str]:
        """Generate high priority actions for executives."""
        actions = []
        
        # Critical security issues
        critical_security = [
            a for a in alerts 
            if a.severity == AlertSeverity.CRITICAL and 'security' in a.category.lower()
        ]
        if critical_security:
            actions.append("🔒 Address critical security vulnerabilities immediately")
        
        # Missing DSAR implementation
        missing_dsar = [
            a for a in alerts 
            if 'missing' in a.title.lower() and 'dsar' in a.title.lower()
        ]
        if missing_dsar:
            actions.append("📤 Implement Data Subject Access Request (DSAR) functionality")
        
        # Missing deletion mechanisms
        missing_deletion = [
            a for a in alerts 
            if 'missing' in a.title.lower() and 'deletion' in a.title.lower()
        ]
        if missing_deletion:
            actions.append("🗑️ Implement user data deletion mechanisms")
        
        # Unencrypted data transmission
        unencrypted = [
            a for a in alerts 
            if 'unencrypted' in a.title.lower()
        ]
        if unencrypted:
            actions.append("🛡️ Enable encryption for all data transmission")
        
        # Hardcoded credentials
        hardcoded = [
            a for a in alerts 
            if 'hardcoded' in a.title.lower()
        ]
        if hardcoded:
            actions.append("🔑 Remove hardcoded credentials and implement secret management")
        
        # Cross-border transfers
        transfers = [
            a for a in alerts 
            if 'transfer' in a.title.lower()
        ]
        if transfers:
            actions.append("🌍 Review cross-border data transfers for adequate safeguards")
        
        return actions[:5]  # Limit to top 5 actions
    
    def _calculate_percentile_ranking(self, score: float, benchmark_data: Dict[str, float]) -> int:
        """Calculate percentile ranking against industry benchmark."""
        if score >= benchmark_data["top_quartile"]:
            return 90
        elif score >= benchmark_data["median"]:
            return 75
        elif score >= benchmark_data["bottom_quartile"]:
            return 50
        else:
            return 25
    
    def _generate_risk_heatmap(self, alerts: List[ComplianceAlert], 
                              issues: List[ComplianceIssue]) -> List[RiskHeatmap]:
        """Generate risk heatmap by GDPR article."""
        article_data = {}
        
        # Process alerts
        for alert in alerts:
            article = alert.article_ref
            if article not in article_data:
                article_data[article] = {
                    'violations': 0,
                    'severity_dist': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
                }
            
            article_data[article]['violations'] += 1
            severity = alert.severity.value
            if severity in article_data[article]['severity_dist']:
                article_data[article]['severity_dist'][severity] += 1
        
        # Process compliance issues
        for issue in issues:
            article = issue.article_ref.value
            if article not in article_data:
                article_data[article] = {
                    'violations': 0,
                    'severity_dist': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
                }
            
            article_data[article]['violations'] += 1
            severity = issue.severity.value
            if severity in article_data[article]['severity_dist']:
                article_data[article]['severity_dist'][severity] += 1
        
        # Create risk heatmap entries
        heatmap = []
        for article, data in article_data.items():
            # Determine risk level
            critical_count = data['severity_dist']['critical']
            high_count = data['severity_dist']['high']
            
            if critical_count > 0:
                risk_level = "critical"
            elif high_count > 0:
                risk_level = "high"
            elif data['violations'] > 5:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            heatmap.append(RiskHeatmap(
                article=article,
                violation_count=data['violations'],
                severity_distribution=data['severity_dist'],
                risk_level=risk_level,
                trend_direction="stable"  # Would need historical data for actual trends
            ))
        
        return sorted(heatmap, key=lambda x: x.violation_count, reverse=True)
    
    def _generate_trend_analysis(self, trends: List[ComplianceTrend]) -> List[ComplianceTrend]:
        """Generate trend analysis from historical data."""
        if not trends:
            # Generate mock trend data for demonstration
            today = date.today()
            mock_trends = []
            
            for i in range(6):  # Last 6 months
                trend_date = today - timedelta(days=30 * i)
                mock_trends.append(ComplianceTrend(
                    period_start=trend_date - timedelta(days=30),
                    period_end=trend_date,
                    compliance_score=85.0 - (i * 2),  # Slight improvement over time
                    total_violations=20 - i,
                    critical_violations=max(0, 3 - i),
                    high_violations=max(0, 5 - i),
                    medium_violations=max(0, 7 - i),
                    low_violations=max(0, 5 - i),
                    improvement_percentage=2.0 if i > 0 else 0.0,
                    trend_direction="improving" if i > 0 else "stable"
                ))
            
            return mock_trends
        
        return trends
    
    def _assess_compliance_maturity(self, compliance_score: float, 
                                   alerts: List[ComplianceAlert]) -> ComplianceMaturity:
        """Assess compliance maturity level."""
        # Determine maturity level based on score and capabilities
        if compliance_score >= 95:
            level = 5
        elif compliance_score >= 85:
            level = 4
        elif compliance_score >= 75:
            level = 3
        elif compliance_score >= 60:
            level = 2
        else:
            level = 1
        
        return self.maturity_model[level]
    
    def _generate_recommendations(self, alerts: List[ComplianceAlert], 
                                 issues: List[ComplianceIssue], 
                                 compliance_score: float) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Score-based recommendations
        if compliance_score < 60:
            recommendations.append("🚨 Immediate action required: Compliance score below acceptable threshold")
        elif compliance_score < 80:
            recommendations.append("⚠️ Significant improvements needed to achieve compliance")
        
        # Alert-based recommendations
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        if critical_alerts:
            recommendations.append(f"🔴 Address {len(critical_alerts)} critical compliance violations immediately")
        
        high_alerts = [a for a in alerts if a.severity == AlertSeverity.HIGH]
        if high_alerts:
            recommendations.append(f"🟠 Resolve {len(high_alerts)} high-priority compliance issues")
        
        # Specific recommendations based on violation types
        security_violations = [a for a in alerts if 'security' in a.category.lower()]
        if security_violations:
            recommendations.append("🛡️ Strengthen data security measures and encryption")
        
        dsar_violations = [a for a in alerts if 'dsar' in a.title.lower()]
        if dsar_violations:
            recommendations.append("📤 Implement comprehensive DSAR (Data Subject Access Request) system")
        
        deletion_violations = [a for a in alerts if 'deletion' in a.title.lower()]
        if deletion_violations:
            recommendations.append("🗑️ Establish complete data deletion and erasure mechanisms")
        
        transfer_violations = [a for a in alerts if 'transfer' in a.title.lower()]
        if transfer_violations:
            recommendations.append("🌍 Review and secure all cross-border data transfers")
        
        # General recommendations
        recommendations.extend([
            "📋 Conduct regular compliance audits and assessments",
            "🎓 Provide compliance training for development teams",
            "📊 Implement continuous compliance monitoring",
            "🔄 Establish compliance improvement processes"
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _get_analysis_period(self, trends: List[ComplianceTrend]) -> str:
        """Get analysis period description."""
        if not trends:
            return "Current scan"
        
        if len(trends) == 1:
            return "Single period"
        elif len(trends) <= 3:
            return f"{len(trends)} months"
        elif len(trends) <= 12:
            return f"{len(trends)} months"
        else:
            return f"{len(trends)} periods"
    
    def _get_framework_coverage(self, alerts: List[ComplianceAlert]) -> List[str]:
        """Get framework coverage from alerts."""
        frameworks = set()
        for alert in alerts:
            frameworks.add(alert.framework)
        
        return list(frameworks) if frameworks else ["GDPR"]
    
    def export_dashboard(self, dashboard: Dict[str, Any], format: str = "json", 
                        output_path: Optional[str] = None) -> str:
        """
        Export dashboard to specified format.
        
        Args:
            dashboard: Dashboard data
            format: Export format (json, html, pdf)
            output_path: Output file path
            
        Returns:
            Path to exported file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"compliance_dashboard_{timestamp}.{format}"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(dashboard, f, indent=2, default=str)
        
        elif format.lower() == "html":
            html_content = self._generate_html_dashboard(dashboard)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        elif format.lower() == "pdf":
            # PDF generation would require additional libraries
            # For now, generate HTML and suggest conversion
            html_path = output_path.with_suffix('.html')
            html_content = self._generate_html_dashboard(dashboard)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.warning(f"PDF generation not implemented. HTML version saved to: {html_path}")
            output_path = html_path
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Dashboard exported to: {output_path}")
        return str(output_path)
    
    def _generate_html_dashboard(self, dashboard: Dict[str, Any]) -> str:
        """Generate HTML dashboard with styling."""
        executive_summary = dashboard['executive_summary']
        compliance_score = dashboard['compliance_score']
        risk_heatmap = dashboard['risk_heatmap']
        recommendations = dashboard['recommendations']
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Levox Compliance Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .score-section {{
            padding: 30px;
            text-align: center;
            border-bottom: 1px solid #eee;
        }}
        .score-circle {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2em;
            font-weight: bold;
            color: white;
        }}
        .score-a {{ background: #4CAF50; }}
        .score-b {{ background: #8BC34A; }}
        .score-c {{ background: #FFC107; }}
        .score-d {{ background: #FF9800; }}
        .score-f {{ background: #F44336; }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #667eea;
        }}
        .risk-heatmap {{
            padding: 30px;
            border-top: 1px solid #eee;
        }}
        .risk-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
            background: #f8f9fa;
        }}
        .risk-critical {{ border-left: 4px solid #F44336; }}
        .risk-high {{ border-left: 4px solid #FF9800; }}
        .risk-medium {{ border-left: 4px solid #FFC107; }}
        .risk-low {{ border-left: 4px solid #4CAF50; }}
        .recommendations {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .recommendation {{
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
        }}
        .recommendation:last-child {{
            border-bottom: none;
        }}
        .footer {{
            padding: 20px;
            text-align: center;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Levox Compliance Dashboard</h1>
            <p>Generated on {dashboard['generated_at'][:10]} | Industry: {dashboard['industry']}</p>
        </div>
        
        <div class="score-section">
            <div class="score-circle score-{executive_summary['grade'].lower()}">
                {compliance_score:.1f}
            </div>
            <h2>Compliance Score: {executive_summary['grade']}</h2>
            <p>Status: {executive_summary['compliance_status'].title()}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Critical Issues</h3>
                <p style="font-size: 2em; margin: 0; color: #F44336;">{executive_summary['critical_issues']}</p>
            </div>
            <div class="summary-card">
                <h3>Industry Benchmark</h3>
                <p style="font-size: 2em; margin: 0; color: #667eea;">{executive_summary['industry_benchmark']:.1f}</p>
            </div>
            <div class="summary-card">
                <h3>Percentile Ranking</h3>
                <p style="font-size: 2em; margin: 0; color: #4CAF50;">{executive_summary['percentile_ranking']}th</p>
            </div>
        </div>
        
        <div class="risk-heatmap">
            <h2>Risk Heatmap by GDPR Article</h2>
            {self._generate_risk_html(risk_heatmap)}
        </div>
        
        <div class="recommendations">
            <h2>High Priority Actions</h2>
            {self._generate_recommendations_html(recommendations)}
        </div>
        
        <div class="footer">
            <p>Generated by Levox Compliance Dashboard | License Tier: {dashboard['license_tier']}</p>
        </div>
    </div>
</body>
</html>
"""
        return html_content
    
    def _generate_risk_html(self, risk_heatmap: List[Dict[str, Any]]) -> str:
        """Generate HTML for risk heatmap."""
        html = ""
        for risk in risk_heatmap:
            html += f"""
            <div class="risk-item risk-{risk['risk_level']}">
                <div>
                    <strong>{risk['article']}</strong>
                    <br>
                    <small>{risk['violation_count']} violations</small>
                </div>
                <div>
                    Critical: {risk['severity_distribution']['critical']} | 
                    High: {risk['severity_distribution']['high']} | 
                    Medium: {risk['severity_distribution']['medium']} | 
                    Low: {risk['severity_distribution']['low']}
                </div>
            </div>
            """
        return html
    
    def _generate_recommendations_html(self, recommendations: List[str]) -> str:
        """Generate HTML for recommendations."""
        html = ""
        for rec in recommendations:
            html += f'<div class="recommendation">{rec}</div>'
        return html
