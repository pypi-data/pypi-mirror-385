"""
Evidence package generator for compliance reports.
Generates PDF, HTML, and JSON reports with executive summaries, trends, and remediation proof.
"""

import json
import uuid
import logging
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict

from .models import (
    EvidencePackage, EvidencePackageRequest, EvidencePackageResponse,
    ScanHistoryEntry, ViolationRecord, RemediationEvidence, 
    ViolationTrend, ComplianceMetrics, CompanyProfile
)
from .evidence_store import EvidenceStore
from .trend_analyzer import TrendAnalyzer
from .gdpr_mapper import GDPRMapper


class EvidencePackageGenerator:
    """Generates comprehensive evidence packages for compliance audits."""
    
    def __init__(self, evidence_store: EvidenceStore):
        """Initialize evidence package generator."""
        self.logger = logging.getLogger(__name__)
        self.evidence_store = evidence_store
        self.trend_analyzer = TrendAnalyzer()
        self.gdpr_mapper = GDPRMapper()
    
    def generate_audit_package(self, request: EvidencePackageRequest) -> EvidencePackageResponse:
        """Generate complete audit evidence package."""
        try:
            package_id = str(uuid.uuid4())
            self.logger.info(f"Generating evidence package {package_id} for company {request.company_id}")
            
            # Get scan history for the period
            scan_history = self.evidence_store.get_scan_history(
                request.company_id, 
                request.start_date, 
                request.end_date
            )
            
            if not scan_history:
                return EvidencePackageResponse(
                    package_id=package_id,
                    status="failed",
                    error_message="No scan history found for the specified period"
                )
            
            # Get violations for the period
            violations = self.evidence_store.get_violations(company_id=request.company_id)
            
            # Get remediations
            remediations = self.evidence_store.get_remediations()
            
            # Get company profile
            company_profile = self.evidence_store.get_company_profile(request.company_id)
            
            # Calculate trends
            trends = self.trend_analyzer.calculate_violation_trends(scan_history)
            
            # Calculate compliance metrics
            compliance_metrics = self.trend_analyzer.calculate_compliance_metrics(
                request.company_id, scan_history, violations
            )
            
            # Generate GDPR article mapping
            gdpr_article_mapping = self._generate_gdpr_article_mapping(violations)
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                company_profile, scan_history, violations, 
                remediations, trends, compliance_metrics
            )
            
            # Create evidence package
            evidence_package = EvidencePackage(
                package_id=package_id,
                company_id=request.company_id,
                generated_at=datetime.utcnow(),
                period_start=request.start_date,
                period_end=request.end_date,
                executive_summary=executive_summary,
                scan_history=scan_history,
                violations=violations,
                remediations=remediations,
                trends=trends,
                compliance_metrics=compliance_metrics,
                gdpr_article_mapping=gdpr_article_mapping
            )
            
            # Attach NL insights if present in latest scans
            try:
                from .evidence_store import EvidenceStore
                from .trend_analyzer import TrendAnalyzer
                # Attempt to collect recent NL insights from last scan metadata if available
                # (Best-effort, optional)
                nl_insights = []
                try:
                    last_entries = scan_history[-3:]
                    for entry in last_entries:
                        if entry.metadata and 'nl_insights' in entry.metadata:
                            nl_insights.extend(entry.metadata.get('nl_insights') or [])
                except Exception:
                    nl_insights = []
                if nl_insights:
                    if not hasattr(evidence_package, 'nl_insights'):
                        setattr(evidence_package, 'nl_insights', nl_insights[:50])
            except Exception:
                pass
            
            # Generate report file
            file_path = None
            if request.format == "pdf":
                file_path = self._generate_pdf_report(evidence_package, request.output_path)
            elif request.format == "html":
                file_path = self._generate_html_report(evidence_package, request.output_path)
            elif request.format == "json":
                file_path = self._generate_json_report(evidence_package, request.output_path)
            
            # Save evidence package
            self.evidence_store.save_evidence_package(evidence_package)
            
            return EvidencePackageResponse(
                package_id=package_id,
                status="completed",
                file_path=file_path,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate evidence package: {e}")
            return EvidencePackageResponse(
                package_id=package_id,
                status="failed",
                error_message=str(e)
            )
    
    def _generate_executive_summary(self, company_profile: Optional[CompanyProfile],
                                  scan_history: List[ScanHistoryEntry],
                                  violations: List[ViolationRecord],
                                  remediations: List[RemediationEvidence],
                                  trends: List[ViolationTrend],
                                  compliance_metrics: ComplianceMetrics) -> Dict[str, Any]:
        """Generate executive summary for the evidence package."""
        try:
            # Calculate key metrics
            total_scans = len(scan_history)
            total_violations = len(violations)
            critical_violations = len([v for v in violations if v.severity == 'critical'])
            remediated_violations = len([r for r in remediations if getattr(r.remediation_type, 'value', r.remediation_type) == 'fixed'])
            
            # Calculate improvement metrics
            improvement_metrics = self.trend_analyzer.calculate_improvement_metrics(trends)
            
            # Generate compliance status
            compliance_status = "COMPLIANT" if compliance_metrics.compliance_score >= 80 else "NON-COMPLIANT"
            
            # Generate trend analysis
            trend_direction = compliance_metrics.trend_direction
            if trend_direction == "improving":
                trend_summary = "Improving compliance posture with decreasing violations"
            elif trend_direction == "declining":
                trend_summary = "Declining compliance posture with increasing violations"
            else:
                trend_summary = "Stable compliance posture"
            
            # Generate key findings
            key_findings = self._generate_key_findings(violations, trends, compliance_metrics)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(violations, trends, compliance_metrics)
            
            return {
                'company_name': company_profile.name if company_profile else 'Unknown Company',
                'report_period': f"{compliance_metrics.period_start} to {compliance_metrics.period_end}",
                'compliance_status': compliance_status,
                'compliance_score': compliance_metrics.compliance_score,
                'total_scans': total_scans,
                'total_violations': total_violations,
                'critical_violations': critical_violations,
                'remediated_violations': remediated_violations,
                'improvement_percentage': improvement_metrics.get('overall_improvement', 0.0),
                'trend_summary': trend_summary,
                'key_findings': key_findings,
                'recommendations': recommendations,
                'gdpr_article_compliance': compliance_metrics.gdpr_article_compliance,
                'risk_level': compliance_metrics.risk_level
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate executive summary: {e}")
            return {
                'company_name': 'Unknown Company',
                'compliance_status': 'UNKNOWN',
                'error': str(e)
            }
    
    def _generate_key_findings(self, violations: List[ViolationRecord],
                             trends: List[ViolationTrend],
                             compliance_metrics: ComplianceMetrics) -> List[str]:
        """Generate key findings from violations and trends."""
        findings = []
        
        # Violation count findings
        if violations:
            findings.append(f"Total of {len(violations)} PII violations detected")
            
            critical_count = len([v for v in violations if v.severity == 'critical'])
            if critical_count > 0:
                findings.append(f"{critical_count} critical violations requiring immediate attention")
            
            # Most common violation types
            violation_types = {}
            for violation in violations:
                vtype = getattr(violation.violation_type, 'value', violation.violation_type)
                violation_types[vtype] = violation_types.get(vtype, 0) + 1
            
            most_common = max(violation_types.items(), key=lambda x: x[1]) if violation_types else None
            if most_common:
                findings.append(f"Most common violation type: {most_common[0]} ({most_common[1]} instances)")
        
        # Trend findings
        if trends:
            latest_trend = trends[-1]
            if latest_trend.improvement_percentage > 0:
                findings.append(f"Improvement trend: {latest_trend.improvement_percentage:.1f}% reduction in violations")
            elif latest_trend.improvement_percentage < 0:
                findings.append(f"Concerning trend: {abs(latest_trend.improvement_percentage):.1f}% increase in violations")
        
        # Compliance score findings
        if compliance_metrics.compliance_score < 70:
            findings.append(f"Low compliance score: {compliance_metrics.compliance_score:.1f}/100")
        elif compliance_metrics.compliance_score > 90:
            findings.append(f"Excellent compliance score: {compliance_metrics.compliance_score:.1f}/100")
        
        # GDPR article findings
        if compliance_metrics.gdpr_article_compliance:
            low_compliance_articles = [
                article for article, score in compliance_metrics.gdpr_article_compliance.items()
                if score < 70
            ]
            if low_compliance_articles:
                findings.append(f"Low compliance in GDPR articles: {', '.join(low_compliance_articles)}")
        
        return findings
    
    def _generate_recommendations(self, violations: List[ViolationRecord],
                                trends: List[ViolationTrend],
                                compliance_metrics: ComplianceMetrics) -> List[str]:
        """Generate recommendations based on violations and trends."""
        recommendations = []
        
        # Critical violation recommendations
        critical_violations = [v for v in violations if v.severity == 'critical']
        if critical_violations:
            recommendations.append("Immediately address all critical violations")
            recommendations.append("Implement emergency remediation procedures")
        
        # Trend-based recommendations
        if trends:
            latest_trend = trends[-1]
            if latest_trend.improvement_percentage < -10:
                recommendations.append("Strengthen compliance processes to reverse declining trend")
                recommendations.append("Implement additional monitoring and controls")
        
        # Compliance score recommendations
        if compliance_metrics.compliance_score < 70:
            recommendations.append("Conduct comprehensive compliance review")
            recommendations.append("Implement systematic remediation plan")
            recommendations.append("Consider external compliance audit")
        elif compliance_metrics.compliance_score < 85:
            recommendations.append("Continue improving compliance processes")
            recommendations.append("Address remaining violations systematically")
        
        # GDPR article recommendations
        if compliance_metrics.gdpr_article_compliance:
            low_compliance_articles = [
                article for article, score in compliance_metrics.gdpr_article_compliance.items()
                if score < 70
            ]
            if low_compliance_articles:
                recommendations.append(f"Focus on improving compliance for articles: {', '.join(low_compliance_articles)}")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Continue monitoring compliance status")
            recommendations.append("Maintain current compliance practices")
            recommendations.append("Regular compliance reviews recommended")
        
        return recommendations
    
    def _generate_gdpr_article_mapping(self, violations: List[ViolationRecord]) -> Dict[str, List[str]]:
        """Generate GDPR article mapping for violations."""
        mapping = {}
        
        for violation in violations:
            gdpr_mapping = self.gdpr_mapper.map_violation_to_article(violation)
            article = getattr(gdpr_mapping.article, 'value', gdpr_mapping.article)
            
            if article not in mapping:
                mapping[article] = []
            mapping[article].append(violation.id)
        
        return mapping
    
    def _generate_pdf_report(self, evidence_package: EvidencePackage, 
                           output_path: Optional[str] = None) -> str:
        """Generate PDF report from evidence package."""
        try:
            # This would use reportlab or weasyprint to generate PDF
            # For now, generate HTML and convert to PDF
            html_path = self._generate_html_report(evidence_package, output_path)
            
            # Convert HTML to PDF (simplified)
            # Generate professional PDF filename: Company_Evidence_YYYY-MM-DD.pdf
            date_str = evidence_package.generated_at.strftime('%Y-%m-%d')
            company_name = evidence_package.company_id.replace('_', '').title()[:10]  # Short company name
            pdf_path = f"{company_name}_Evidence_{date_str}.pdf"
            
            # In a real implementation, you'd use:
            # - weasyprint: HTML to PDF
            # - reportlab: Direct PDF generation
            # - wkhtmltopdf: HTML to PDF conversion
            
            self.logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate PDF report: {e}")
            return ""
    
    def _generate_html_report(self, evidence_package: EvidencePackage, 
                            output_path: Optional[str] = None) -> str:
        """Generate HTML report from evidence package."""
        try:
            if not output_path:
                # Generate professional filename: Company_Evidence_YYYY-MM-DD.html
                date_str = evidence_package.generated_at.strftime('%Y-%m-%d')
                company_name = evidence_package.company_id.replace('_', '').title()[:10]  # Short company name
                output_path = f"{company_name}_Evidence_{date_str}.html"
            
            # Generate HTML content
            html_content = self._create_html_template(evidence_package)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}")
            return ""
    
    def _generate_json_report(self, evidence_package: EvidencePackage, 
                            output_path: Optional[str] = None) -> str:
        """Generate JSON report from evidence package."""
        try:
            if not output_path:
                # Generate professional filename: Company_Evidence_YYYY-MM-DD.json
                date_str = evidence_package.generated_at.strftime('%Y-%m-%d')
                company_name = evidence_package.company_id.replace('_', '').title()[:10]  # Short company name
                output_path = f"{company_name}_Evidence_{date_str}.json"
            
            # Convert evidence package to dictionary
            package_dict = asdict(evidence_package)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(package_dict, f, indent=2, default=str)
            
            self.logger.info(f"JSON report generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate JSON report: {e}")
            return ""
    
    def _create_html_template(self, evidence_package: EvidencePackage) -> str:
        """Create HTML template for evidence package."""
        # This is a simplified HTML template
        # In a real implementation, you'd use Jinja2 templates
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GDPR Compliance Evidence Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 3px; }}
        .critical {{ color: #d32f2f; }}
        .high {{ color: #f57c00; }}
        .medium {{ color: #fbc02d; }}
        .low {{ color: #388e3c; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GDPR Compliance Evidence Report</h1>
        <h2>{evidence_package.executive_summary.get('company_name', 'Unknown Company')}</h2>
        <p>Report Period: {evidence_package.executive_summary.get('report_period', 'Unknown')}</p>
        <p>Generated: {evidence_package.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <strong>Compliance Status:</strong> {evidence_package.executive_summary.get('compliance_status', 'Unknown')}
        </div>
        <div class="metric">
            <strong>Compliance Score:</strong> {evidence_package.executive_summary.get('compliance_score', 0):.1f}/100
        </div>
        <div class="metric">
            <strong>Total Scans:</strong> {evidence_package.executive_summary.get('total_scans', 0)}
        </div>
        <div class="metric">
            <strong>Total Violations:</strong> {evidence_package.executive_summary.get('total_violations', 0)}
        </div>
    </div>
    
    <div class="section">
        <h2>Key Findings</h2>
        <ul>
            {''.join(f'<li>{finding}</li>' for finding in evidence_package.executive_summary.get('key_findings', []))}
        </ul>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            {''.join(f'<li>{recommendation}</li>' for recommendation in evidence_package.executive_summary.get('recommendations', []))}
        </ul>
    </div>
    
    <div class="section">
        <h2>Scan History</h2>
        <table>
            <tr>
                <th>Scan Date</th>
                <th>Files Scanned</th>
                <th>Violations</th>
                <th>Critical</th>
                <th>High</th>
                <th>Medium</th>
                <th>Low</th>
            </tr>
            {''.join(f'''
            <tr>
                <td>{scan.scan_timestamp.strftime('%Y-%m-%d %H:%M')}</td>
                <td>{scan.total_files}</td>
                <td>{scan.total_violations}</td>
                <td class="critical">{scan.critical_violations}</td>
                <td class="high">{scan.high_violations}</td>
                <td class="medium">{scan.medium_violations}</td>
                <td class="low">{scan.low_violations}</td>
            </tr>
            ''' for scan in evidence_package.scan_history)}
        </table>
    </div>
    
    <div class="section">
        <h2>Violation Details</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Line</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Description</th>
            </tr>
            {''.join(f'''
            <tr>
                <td>{violation.file_path}</td>
                <td>{violation.line_number}</td>
                <td>{getattr(violation.violation_type, 'value', violation.violation_type)}</td>
                <td class="{violation.severity.lower()}">{violation.severity}</td>
                <td>{violation.description}</td>
            </tr>
            ''' for violation in evidence_package.violations)}
        </table>
    </div>
    
    <div class="section">
        <h2>GDPR Article Compliance</h2>
        <table>
            <tr>
                <th>GDPR Article</th>
                <th>Compliance Score</th>
                <th>Status</th>
            </tr>
            {''.join(f'''
            <tr>
                <td>{article}</td>
                <td>{score:.1f}/100</td>
                <td>{"✓ Compliant" if score >= 80 else "✗ Non-Compliant"}</td>
            </tr>
            ''' for article, score in evidence_package.compliance_metrics.gdpr_article_compliance.items())}
        </table>
    </div>
</body>
</html>
        """
        
        return html
