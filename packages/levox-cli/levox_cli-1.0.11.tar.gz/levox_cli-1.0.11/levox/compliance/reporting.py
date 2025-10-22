"""
Compliance Reporter - Comprehensive GDPR compliance reporting system.

Generates detailed compliance reports with Rich console formatting, multiple output formats,
GDPR compliance scoring, and premium/enterprise dashboards.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import asdict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
# Progress bars removed to avoid typewriter effect
from rich.layout import Layout
from rich.columns import Columns
from rich.bar import Bar
from rich.align import Align
from rich import box

from ..core.config import Config, LicenseTier
from ..core.exceptions import DetectionError
from .models import (
    ComplianceResult, ComplianceIssue, ComplianceLevel, ComplianceCategory,
    GDPRArticle, ComplianceReport
)


logger = logging.getLogger(__name__)


class ComplianceReporter:
    """
    Production-grade compliance reporter with Rich console formatting and multiple output formats.
    
    Generates comprehensive GDPR compliance reports including executive summary,
    per-article findings, severity distribution, and remediation checklist.
    """
    
    def __init__(self, config: Config):
        """Initialize the compliance reporter."""
        self.config = config
        self.license_tier = config.license.tier
        self.console = Console()
        
        # Report configuration
        self.enable_dashboards = self.license_tier in [LicenseTier.PREMIUM, LicenseTier.ENTERPRISE]
        self.enable_trends = self.license_tier == LicenseTier.ENTERPRISE
        self.enable_export = True
        
        logger.info("Compliance Reporter initialized successfully")
    
    def generate_compliance_report(self, compliance_result: ComplianceResult) -> str:
        """
        Generate a comprehensive compliance report.
        
        Args:
            compliance_result: The compliance audit result to report on
            
        Returns:
            Formatted report string
        """
        try:
            logger.info("Generating compliance report...")
            
            # Generate different report sections
            executive_summary = self._generate_executive_summary(compliance_result)
            findings_table = self._generate_findings_table(compliance_result)
            severity_distribution = self._generate_severity_distribution(compliance_result)
            article_breakdown = self._generate_article_breakdown(compliance_result)
            remediation_checklist = self._generate_remediation_checklist(compliance_result)
            
            # Premium/Enterprise features
            dashboard = ""
            if self.enable_dashboards:
                dashboard = self._generate_compliance_dashboard(compliance_result)
            
            trends = ""
            if self.enable_trends:
                trends = self._generate_trend_analysis(compliance_result)
            
            # Combine all sections
            report = f"""
{executive_summary}

{findings_table}

{severity_distribution}

{article_breakdown}

{remediation_checklist}

{dashboard}

{trends}
"""
            
            logger.info("Compliance report generated successfully")
            return report.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise DetectionError(f"Report generation failed: {e}")
    
    def _generate_executive_summary(self, result: ComplianceResult) -> str:
        """Generate executive summary section."""
        status_color = "green" if result.is_compliant else "red" if result.needs_attention else "yellow"
        status_text = "✅ COMPLIANT" if result.is_compliant else "🚨 NEEDS ATTENTION" if result.needs_attention else "⚠️  WARNING"
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    GDPR COMPLIANCE REPORT                    ║
║                                                              ║
║  Project: {result.project_path:<45} ║
║  Audit Date: {result.audit_timestamp.strftime('%Y-%m-%d %H:%M:%S'):<40} ║
║  Duration: {result.audit_duration:.1f}s{' ' * 35} ║
╚══════════════════════════════════════════════════════════════╝

{status_text} - Overall Compliance Score: {result.compliance_score:.1f}/100

📊 SUMMARY STATISTICS:
• Total Issues Found: {result.total_issues}
• Critical Issues: {result.critical_issues_count}
• High Priority Issues: {result.high_issues_count}
• Articles Checked: {len(result.issues_by_article)}
• Compliance Status: {'Compliant' if result.is_compliant else 'Needs Attention' if result.needs_attention else 'Warning'}

🎯 KEY FINDINGS:
"""
        
        if result.critical_issues_count > 0:
            summary += f"• 🚨 {result.critical_issues_count} critical issues require immediate attention\n"
        if result.high_issues_count > 0:
            summary += f"• ⚠️  {result.high_issues_count} high priority issues need prompt resolution\n"
        
        if result.is_compliant:
            summary += "• ✅ Project meets GDPR compliance requirements\n"
        elif result.needs_attention:
            summary += "• 🚨 Project requires immediate attention to achieve compliance\n"
        else:
            summary += "• ⚠️  Project has compliance gaps that need addressing\n"
        
        return summary
    
    def _generate_findings_table(self, result: ComplianceResult) -> str:
        """Generate detailed findings table."""
        if not result.compliance_issues:
            return "\n📋 DETAILED FINDINGS:\nNo compliance issues found. ✅\n"
        
        # Group issues by severity for better organization
        issues_by_severity = {}
        for issue in result.compliance_issues:
            severity = issue.severity
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)
        
        findings = "\n📋 DETAILED FINDINGS:\n"
        
        # Process issues by severity (critical first)
        severity_order = [ComplianceLevel.CRITICAL, ComplianceLevel.HIGH, ComplianceLevel.MEDIUM, ComplianceLevel.LOW]
        
        for severity in severity_order:
            if severity not in issues_by_severity:
                continue
            
            severity_icon = {
                ComplianceLevel.CRITICAL: "🚨",
                ComplianceLevel.HIGH: "⚠️",
                ComplianceLevel.MEDIUM: "🔶",
                ComplianceLevel.LOW: "ℹ️"
            }.get(severity, "•")
            
            findings += f"\n{severity_icon} {severity.upper()} PRIORITY ISSUES ({len(issues_by_severity[severity])}):\n"
            findings += "─" * 80 + "\n"
            
            for i, issue in enumerate(issues_by_severity[severity], 1):
                findings += f"{i:2d}. {issue.description}\n"
                findings += f"    📍 Location: {issue.location}"
                if issue.line_number:
                    findings += f":{issue.line_number}"
                findings += "\n"
                findings += f"    📚 Article: {issue.article_ref}\n"
                findings += f"    🏷️  Category: {issue.category.value.replace('_', ' ').title()}\n"
                if issue.remediation_suggestion:
                    findings += f"    💡 Remediation: {issue.remediation_suggestion}\n"
                if issue.evidence:
                    findings += f"    🔍 Evidence: {issue.evidence[:100]}{'...' if len(issue.evidence) > 100 else ''}\n"
                findings += "\n"
        
        return findings
    
    def _generate_severity_distribution(self, result: ComplianceResult) -> str:
        """Generate severity distribution visualization."""
        if not result.issues_by_severity:
            return ""
        
        distribution = "\n📊 SEVERITY DISTRIBUTION:\n"
        distribution += "─" * 50 + "\n"
        
        total_issues = result.total_issues
        if total_issues == 0:
            distribution += "✅ No issues found\n"
            return distribution
        
        # Create visual bars
        for severity in [ComplianceLevel.CRITICAL, ComplianceLevel.HIGH, ComplianceLevel.MEDIUM, ComplianceLevel.LOW]:
            count = result.issues_by_severity.get(severity, 0)
            if count == 0:
                continue
            
            percentage = (count / total_issues) * 100
            bar_length = int((percentage / 100) * 40)  # 40 character bar
            
            severity_icon = {
                ComplianceLevel.CRITICAL: "🚨",
                ComplianceLevel.HIGH: "⚠️",
                ComplianceLevel.MEDIUM: "🔶",
                ComplianceLevel.LOW: "ℹ️"
            }.get(severity, "•")
            
            bar = "█" * bar_length + "░" * (40 - bar_length)
            distribution += f"{severity_icon} {severity.value.upper():<10} {count:3d} ({percentage:5.1f}%) {bar}\n"
        
        return distribution
    
    def _generate_article_breakdown(self, result: ComplianceResult) -> str:
        """Generate GDPR article breakdown."""
        if not result.issues_by_article:
            return ""
        
        breakdown = "\n📚 GDPR ARTICLE BREAKDOWN:\n"
        breakdown += "─" * 60 + "\n"
        
        # Sort articles by issue count (descending)
        sorted_articles = sorted(
            result.issues_by_article.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for article, count in sorted_articles:
            breakdown += f"• {article.value:<25} : {count:3d} issue{'s' if count != 1 else ''}\n"
        
        return breakdown
    
    def _generate_remediation_checklist(self, result: ComplianceResult) -> str:
        """Generate actionable remediation checklist."""
        if not result.compliance_issues:
            return "\n✅ REMEDIATION CHECKLIST:\nNo issues to remediate. Project is compliant!\n"
        
        checklist = "\n🔧 REMEDIATION CHECKLIST:\n"
        checklist += "─" * 60 + "\n"
        
        # Group by priority
        priority_issues = {
            ComplianceLevel.CRITICAL: [],
            ComplianceLevel.HIGH: [],
            ComplianceLevel.MEDIUM: [],
            ComplianceLevel.LOW: []
        }
        
        for issue in result.compliance_issues:
            priority_issues[issue.severity].append(issue)
        
        for priority in [ComplianceLevel.CRITICAL, ComplianceLevel.HIGH, ComplianceLevel.MEDIUM, ComplianceLevel.LOW]:
            issues = priority_issues[priority]
            if not issues:
                continue
            
            priority_icon = {
                ComplianceLevel.CRITICAL: "🚨",
                ComplianceLevel.HIGH: "⚠️",
                ComplianceLevel.MEDIUM: "🔶",
                ComplianceLevel.LOW: "ℹ️"
            }.get(priority, "•")
            
            checklist += f"\n{priority_icon} {priority.value.upper()} PRIORITY ACTIONS:\n"
            
            for i, issue in enumerate(issues, 1):
                checklist += f"  {i}. {issue.description}\n"
                if issue.remediation_suggestion:
                    checklist += f"     → {issue.remediation_suggestion}\n"
                checklist += f"     📍 {issue.location}"
                if issue.line_number:
                    checklist += f":{issue.line_number}"
                checklist += "\n\n"
        
        return checklist
    
    def _generate_compliance_dashboard(self, result: ComplianceResult) -> str:
        """Generate premium/enterprise compliance dashboard."""
        if not self.enable_dashboards:
            return ""
        
        dashboard = "\n🎛️  COMPLIANCE DASHBOARD (Premium/Enterprise):\n"
        dashboard += "─" * 60 + "\n"
        
        # Compliance score breakdown
        score_breakdown = self._calculate_score_breakdown(result)
        dashboard += f"📈 Score Breakdown:\n"
        dashboard += f"   • Base Score: {score_breakdown['base_score']:.1f}\n"
        dashboard += f"   • Coverage Bonus: {score_breakdown['coverage_bonus']:.1f}\n"
        dashboard += f"   • Final Score: {result.compliance_score:.1f}\n\n"
        
        # Risk assessment
        risk_level = "LOW" if result.compliance_score >= 80 else "MEDIUM" if result.compliance_score >= 60 else "HIGH"
        dashboard += f"⚠️  Risk Assessment: {risk_level}\n"
        
        # Compliance maturity
        maturity = self._assess_compliance_maturity(result)
        dashboard += f"🏗️  Compliance Maturity: {maturity}\n"
        
        # Next audit recommendation
        next_audit = self._recommend_next_audit(result)
        dashboard += f"📅 Next Audit Recommendation: {next_audit}\n"
        
        return dashboard
    
    def _generate_trend_analysis(self, result: ComplianceResult) -> str:
        """Generate enterprise trend analysis."""
        if not self.enable_trends:
            return ""
        
        trends = "\n📊 TREND ANALYSIS (Enterprise):\n"
        trends += "─" * 50 + "\n"
        
        # This would typically pull from historical data
        # For now, provide placeholder analysis
        trends += "• Historical trend analysis requires multiple audit data points\n"
        trends += "• Enable continuous monitoring for trend insights\n"
        trends += "• Consider scheduling regular compliance assessments\n"
        
        return trends
    
    def _calculate_score_breakdown(self, result: ComplianceResult) -> Dict[str, float]:
        """Calculate detailed compliance score breakdown."""
        if not result.compliance_issues:
            return {
                'base_score': 100.0,
                'coverage_bonus': 0.0,
                'final_score': 100.0
            }
        
        # Calculate penalties based on severity
        severity_weights = {
            ComplianceLevel.CRITICAL: 10.0,
            ComplianceLevel.HIGH: 7.0,
            ComplianceLevel.MEDIUM: 4.0,
            ComplianceLevel.LOW: 1.0
        }
        
        total_penalty = 0.0
        total_weight = 0.0
        
        for issue in result.compliance_issues:
            weight = severity_weights.get(issue.severity, 1.0)
            total_weight += weight
            total_penalty += weight * 2.0  # Each issue reduces score by 2 points per weight
        
        base_score = max(0.0, 100.0 - total_penalty)
        coverage_bonus = min(10.0, total_weight * 0.5)
        final_score = min(100.0, base_score + coverage_bonus)
        
        return {
            'base_score': base_score,
            'coverage_bonus': coverage_bonus,
            'final_score': final_score
        }
    
    def _assess_compliance_maturity(self, result: ComplianceResult) -> str:
        """Assess overall compliance maturity level."""
        if result.compliance_score >= 90:
            return "EXCELLENT - Industry leading compliance practices"
        elif result.compliance_score >= 80:
            return "GOOD - Strong compliance foundation with minor gaps"
        elif result.compliance_score >= 70:
            return "FAIR - Basic compliance in place, significant improvements needed"
        elif result.compliance_score >= 60:
            return "POOR - Major compliance gaps, immediate action required"
        else:
            return "CRITICAL - Severe compliance failures, urgent intervention needed"
    
    def _recommend_next_audit(self, result: ComplianceResult) -> str:
        """Recommend timing for next compliance audit."""
        if result.compliance_score >= 90:
            return "6 months - Maintain excellent compliance"
        elif result.compliance_score >= 80:
            return "3 months - Address minor gaps"
        elif result.compliance_score >= 70:
            return "1 month - Focus on high-priority issues"
        elif result.compliance_score >= 60:
            return "2 weeks - Immediate attention required"
        else:
            return "1 week - Critical compliance failures detected"
    
    def export_report(self, compliance_result: ComplianceResult, output_path: str, 
                     format: str = "markdown") -> bool:
        """
        Export compliance report to specified format and location.
        
        Args:
            compliance_result: The compliance audit result
            output_path: Path to export the report
            format: Export format (markdown, json, html)
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "markdown":
                return self._export_markdown(compliance_result, output_path)
            elif format.lower() == "json":
                return self._export_json(compliance_result, output_path)
            elif format.lower() == "html":
                return self._export_html(compliance_result, output_path)
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            return False
    
    def _export_markdown(self, result: ComplianceResult, output_path: Path) -> bool:
        """Export report as Markdown."""
        try:
            markdown_content = f"""# GDPR Compliance Report

## Executive Summary

**Project:** {result.project_path}  
**Audit Date:** {result.audit_timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Compliance Score:** {result.compliance_score:.1f}/100  
**Status:** {'✅ COMPLIANT' if result.is_compliant else '🚨 NEEDS ATTENTION' if result.needs_attention else '⚠️ WARNING'}

## Summary Statistics

- **Total Issues:** {result.total_issues}
- **Critical Issues:** {result.critical_issues_count}
- **High Priority Issues:** {result.high_issues_count}
- **Articles Checked:** {len(result.issues_by_article)}

## Detailed Findings

"""
            
            if result.compliance_issues:
                for issue in result.compliance_issues:
                    markdown_content += f"""### {issue.severity.value.upper()}: {issue.description}

- **Location:** {issue.location}{f':{issue.line_number}' if issue.line_number else ''}
- **Article:** {issue.article_ref.value}
- **Category:** {issue.category.value.replace('_', ' ').title()}
- **Remediation:** {issue.remediation_suggestion or 'No remediation suggestion provided'}
- **Evidence:** {issue.evidence or 'No evidence provided'}

"""
            else:
                markdown_content += "No compliance issues found. ✅\n"
            
            # Add remediation checklist
            markdown_content += "\n## Remediation Checklist\n\n"
            
            if result.compliance_issues:
                for issue in result.compliance_issues:
                    markdown_content += f"- [ ] {issue.description}\n"
            else:
                markdown_content += "- [x] No issues to remediate\n"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdown report exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export Markdown report: {e}")
            return False
    
    def _export_json(self, result: ComplianceResult, output_path: Path) -> bool:
        """Export report as JSON."""
        try:
            # Create structured report data
            report_data = {
                "metadata": {
                    "report_type": "GDPR Compliance Report",
                    "generated_at": datetime.now().isoformat(),
                    "license_tier": self.license_tier.value,
                    "version": "1.0.0"
                },
                "project_info": {
                    "path": result.project_path,
                    "audit_timestamp": result.audit_timestamp.isoformat(),
                    "completion_timestamp": result.completion_timestamp.isoformat(),
                    "audit_duration": result.audit_duration
                },
                "compliance_summary": {
                    "score": result.compliance_score,
                    "is_compliant": result.is_compliant,
                    "needs_attention": result.needs_attention,
                    "total_issues": result.total_issues,
                    "issues_by_severity": {k.value: v for k, v in result.issues_by_severity.items()},
                    "issues_by_article": {k.value: v for k, v in result.issues_by_article.items()}
                },
                "detailed_findings": [
                    {
                        "id": issue.id,
                        "severity": issue.severity.value,
                        "article": issue.article_ref.value,
                        "category": issue.category.value,
                        "description": issue.description,
                        "location": issue.location,
                        "line_number": issue.line_number,
                        "remediation": issue.remediation_suggestion,
                        "evidence": issue.evidence
                    }
                    for issue in result.compliance_issues
                ]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"JSON report exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export JSON report: {e}")
            return False
    
    def _export_html(self, result: ComplianceResult, output_path: Path) -> bool:
        """Export report as HTML."""
        try:
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GDPR Compliance Report - {result.project_path}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .score {{ font-size: 24px; font-weight: bold; }}
        .compliant {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .critical {{ color: #dc3545; }}
        .issue {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007bff; background: #f8f9fa; }}
        .critical-issue {{ border-left-color: #dc3545; background: #f8d7da; }}
        .high-issue {{ border-left-color: #ffc107; background: #fff3cd; }}
        .medium-issue {{ border-left-color: #17a2b8; background: #d1ecf1; }}
        .low-issue {{ border-left-color: #28a745; background: #d4edda; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GDPR Compliance Report</h1>
        <p><strong>Project:</strong> {result.project_path}</p>
        <p><strong>Audit Date:</strong> {result.audit_timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p class="score {'compliant' if result.is_compliant else 'warning' if not result.needs_attention else 'critical'}">
            Compliance Score: {result.compliance_score:.1f}/100
        </p>
    </div>
    
    <h2>Summary</h2>
    <p>Total Issues: {result.total_issues} | Critical: {result.critical_issues_count} | High: {result.high_issues_count}</p>
    
    <h2>Detailed Findings</h2>
"""
            
            if result.compliance_issues:
                for issue in result.compliance_issues:
                    severity_class = f"{issue.severity.value}-issue"
                    html_content += f"""
    <div class="issue {severity_class}">
        <h3>{issue.severity.value.upper()}: {issue.description}</h3>
        <p><strong>Location:</strong> {issue.location}{f':{issue.line_number}' if issue.line_number else ''}</p>
        <p><strong>Article:</strong> {issue.article_ref.value}</p>
        <p><strong>Category:</strong> {issue.category.value.replace('_', ' ').title()}</p>
        <p><strong>Remediation:</strong> {issue.remediation_suggestion or 'No remediation suggestion provided'}</p>
        <p><strong>Evidence:</strong> {issue.evidence or 'No evidence provided'}</p>
    </div>
"""
            else:
                html_content += "<p>✅ No compliance issues found.</p>"
            
            html_content += """
</body>
</html>
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export HTML report: {e}")
            return False
    
    def display_interactive_report(self, compliance_result: ComplianceResult) -> None:
        """Display interactive compliance report in the console."""
        try:
            # Generate and display the report
            report = self.generate_compliance_report(compliance_result)
            self.console.print(Panel(report, title="GDPR Compliance Report", border_style="blue"))
            
        except Exception as e:
            logger.error(f"Failed to display interactive report: {e}")
            self.console.print(f"[red]Error displaying report: {e}[/red]")
    
    def generate_detection_report(self, detection_result: 'DetectionResult', 
                                 output_formats: List[str] = None) -> Dict[str, str]:
        """
        Generate detection report from DetectionResult objects.
        
        Args:
            detection_result: The detection result to report on
            output_formats: List of output formats to generate
            
        Returns:
            Dictionary mapping format to report content
        """
        if output_formats is None:
            output_formats = ['json']
        
        reports = {}
        
        try:
            for format_type in output_formats:
                if format_type == 'json':
                    reports['json'] = self._generate_json_report(detection_result)
                elif format_type == 'html':
                    reports['html'] = self._generate_html_report(detection_result)
                elif format_type == 'pdf':
                    reports['pdf'] = self._generate_pdf_report(detection_result)
                else:
                    self.logger.warning(f"Unsupported output format: {format_type}")
            
            return reports
            
        except Exception as e:
            self.logger.error(f"Failed to generate detection report: {e}")
            return {}
    
    def generate_scan_report(self, detection_result: 'DetectionResult', 
                           scan_path: str, scan_time: float, license_tier: str,
                           output_formats: List[str] = None) -> Dict[str, str]:
        """
        Generate comprehensive scan report from DetectionResult.
        
        Args:
            detection_result: The detection result to report on
            scan_path: Path that was scanned
            scan_time: Time taken for the scan
            license_tier: License tier used
            output_formats: List of output formats to generate
            
        Returns:
            Dictionary mapping format to report content
        """
        if output_formats is None:
            output_formats = ['json']
        
        reports = {}
        
        try:
            for format_type in output_formats:
                if format_type == 'json':
                    reports['json'] = self._generate_scan_json_report(detection_result, scan_path, scan_time, license_tier)
                elif format_type == 'html':
                    reports['html'] = self._generate_scan_html_report(detection_result, scan_path, scan_time, license_tier)
                elif format_type == 'pdf':
                    reports['pdf'] = self._generate_scan_pdf_report(detection_result, scan_path, scan_time, license_tier)
                else:
                    self.logger.warning(f"Unsupported output format: {format_type}")
            
            return reports
            
        except Exception as e:
            self.logger.error(f"Failed to generate scan report: {e}")
            return {}
    
    def _generate_json_report(self, detection_result: 'DetectionResult') -> str:
        """Generate JSON report from DetectionResult."""
        try:
            report_data = {
                'report_type': 'detection_summary',
                'generated_at': datetime.utcnow().isoformat(),
                'scan_summary': detection_result.get_summary(),
                'file_results': [
                    {
                        'file_path': str(fr.file_path),
                        'language': fr.language,
                        'total_lines': fr.total_lines,
                        'scan_time': fr.scan_time,
                        'match_count': fr.match_count,
                        'high_risk_matches': len(fr.high_risk_matches),
                        'matches': [
                            {
                                'line': match.line,
                                'engine': match.engine,
                                'rule_id': match.rule_id,
                                'severity': match.severity,
                                'confidence': match.confidence,
                                'snippet': match.snippet,
                                'description': match.description,
                                'pattern_name': match.pattern_name,
                                'matched_text': match.matched_text
                            } for match in fr.matches
                        ]
                    } for fr in detection_result.file_results
                ],
                'performance_metrics': {
                    'total_scan_time': detection_result.total_scan_time,
                    'average_file_time': detection_result.average_file_time,
                    'memory_peak_mb': detection_result.memory_peak_mb,
                    'engine_timing': detection_result.get_engine_timing_summary()
                }
            }
            
            return json.dumps(report_data, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Failed to generate JSON report: {e}")
            return json.dumps({'error': str(e)})
    
    def _generate_html_report(self, detection_result: 'DetectionResult') -> str:
        """Generate HTML report from DetectionResult."""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Levox Detection Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .severity-critical {{ color: #dc3545; font-weight: bold; }}
        .severity-high {{ color: #fd7e14; font-weight: bold; }}
        .severity-medium {{ color: #ffc107; font-weight: bold; }}
        .severity-low {{ color: #28a745; font-weight: bold; }}
        .file-result {{ border: 1px solid #dee2e6; border-radius: 8px; margin-bottom: 15px; padding: 15px; }}
        .match {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 4px; }}
        .snippet {{ font-family: monospace; background: #e9ecef; padding: 10px; border-radius: 4px; margin: 5px 0; }}
        .engine-badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
        .engine-regex {{ background: #007bff; color: white; }}
        .engine-ast {{ background: #28a745; color: white; }}
        .engine-dataflow {{ background: #fd7e14; color: white; }}
        .engine-ml_filter {{ background: #6f42c1; color: white; }}
        .engine-context {{ background: #20c997; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Levox Detection Report</h1>
        <p>Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Scan Summary</h2>
        <p><strong>Scan ID:</strong> {detection_result.scan_id}</p>
        <p><strong>Path Scanned:</strong> {detection_result.scan_path}</p>
        <p><strong>Files Scanned:</strong> {detection_result.files_scanned}</p>
        <p><strong>Files with Matches:</strong> {detection_result.files_with_matches}</p>
        <p><strong>Total Matches:</strong> {detection_result.total_matches}</p>
        <p><strong>Scan Duration:</strong> {detection_result.scan_duration:.2f}s</p>
        <p><strong>License Tier:</strong> {detection_result.license_tier}</p>
    </div>
    
    <div class="summary">
        <h2>⚠️ Severity Distribution</h2>
        <p><span class="severity-critical">Critical:</span> {detection_result.risk_summary.get('CRITICAL', 0)}</p>
        <p><span class="severity-high">High:</span> {detection_result.risk_summary.get('HIGH', 0)}</p>
        <p><span class="severity-medium">Medium:</span> {detection_result.risk_summary.get('MEDIUM', 0)}</p>
        <p><span class="severity-low">Low:</span> {detection_result.risk_summary.get('LOW', 0)}</p>
    </div>
    
    <div class="summary">
        <h2>🔍 Engine Distribution</h2>
        {''.join([f'<p><strong>{engine}:</strong> {count}</p>' for engine, count in detection_result.engine_summary.items()])}
    </div>
    
    <h2>📁 File Results</h2>
"""
            
            for fr in detection_result.file_results:
                if fr.match_count > 0:
                    html_content += f"""
    <div class="file-result">
        <h3>📄 {fr.file_path.name}</h3>
        <p><strong>Path:</strong> {fr.file_path}</p>
        <p><strong>Language:</strong> {fr.language}</p>
        <p><strong>Total Lines:</strong> {fr.total_lines}</p>
        <p><strong>Scan Time:</strong> {fr.scan_time:.3f}s</p>
        <p><strong>Matches Found:</strong> {fr.match_count}</p>
        
        <h4>🔍 Detections:</h4>
"""
                    
                    for match in fr.matches:
                        severity_class = f"severity-{match.severity.lower()}"
                        engine_class = f"engine-{match.engine}"
                        
                        html_content += f"""
        <div class="match">
            <p><strong>Line {match.line}:</strong> <span class="{severity_class}">{match.severity}</span></p>
            <p><strong>Engine:</strong> <span class="engine-badge {engine_class}">{match.engine.upper()}</span></p>
            <p><strong>Rule:</strong> {match.rule_id}</p>
            <p><strong>Confidence:</strong> {match.confidence:.2f}</p>
            <p><strong>Description:</strong> {match.description}</p>
            <div class="snippet">{match.snippet}</div>
        </div>
"""
                    
                    html_content += """
    </div>
"""
            
            html_content += """
</body>
</html>
"""
            
            return html_content
            
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}")
            return f"<html><body><h1>Error generating report: {e}</h1></body></html>"
    
    def _generate_pdf_report(self, detection_result: 'DetectionResult') -> str:
        """Generate PDF report from DetectionResult."""
        try:
            # For now, return a message indicating PDF generation
            # In a production environment, you would use a library like reportlab or weasyprint
            return f"PDF report generation not yet implemented. Use --report json or --report html instead."
            
        except Exception as e:
            self.logger.error(f"Failed to generate PDF report: {e}")
            return f"Error generating PDF report: {e}"
    
    def _generate_scan_json_report(self, detection_result: 'DetectionResult', 
                                  scan_path: str, scan_time: float, license_tier: str) -> str:
        """Generate JSON report for scan results."""
        try:
            report_data = {
                'report_type': 'scan_summary',
                'generated_at': datetime.now().isoformat(),
                'scan_info': {
                    'scan_path': scan_path,
                    'scan_time_seconds': scan_time,
                    'license_tier': license_tier,
                    'scan_id': detection_result.scan_id,
                    'scan_timestamp': detection_result.scan_timestamp.isoformat() if hasattr(detection_result, 'scan_timestamp') else None
                },
                'scan_summary': detection_result.get_summary(),
                'file_results': [
                    {
                        'file_path': str(fr.file_path),
                        'language': fr.language,
                        'total_lines': fr.total_lines,
                        'scan_time': fr.scan_time,
                        'match_count': fr.match_count,
                        'high_risk_matches': len(fr.high_risk_matches),
                        'matches': [
                            {
                                'line': match.line,
                                'engine': match.engine,
                                'rule_id': match.rule_id,
                                'severity': match.severity,
                                'confidence': match.confidence,
                                'snippet': match.snippet,
                                'description': match.description,
                                'pattern_name': match.pattern_name,
                                'matched_text': match.matched_text,
                                'risk_level': str(match.risk_level),
                                'metadata': match.metadata
                            } for match in fr.matches
                        ]
                    } for fr in detection_result.file_results
                ],
                'performance_metrics': {
                    'total_scan_time': getattr(detection_result, 'total_scan_time', scan_time),
                    'average_file_time': getattr(detection_result, 'average_file_time', 0.0),
                    'memory_peak_mb': getattr(detection_result, 'memory_peak_mb', 0.0),
                    'engine_timing': detection_result.get_engine_timing_summary()
                }
            }
            
            return json.dumps(report_data, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Failed to generate scan JSON report: {e}")
            return json.dumps({'error': str(e)})
    
    def _generate_scan_html_report(self, detection_result: 'DetectionResult', 
                                  scan_path: str, scan_time: float, license_tier: str) -> str:
        """Generate HTML report for scan results."""
        try:
            # Count issues by severity
            severity_counts = {}
            for fr in detection_result.file_results:
                for match in fr.matches:
                    severity = match.severity
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Levox Scan Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
        .summary {{ margin: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .issues {{ margin: 20px; }}
        .issue-card {{ background: white; margin: 10px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-left: 4px solid #ddd; }}
        .issue-card.critical {{ border-left-color: #dc3545; }}
        .issue-card.high {{ border-left-color: #fd7e14; }}
        .issue-card.medium {{ border-left-color: #ffc107; }}
        .issue-card.low {{ border-left-color: #28a745; }}
        .issue-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .severity-badge {{ padding: 5px 12px; border-radius: 15px; color: white; font-weight: bold; font-size: 0.9em; }}
        .severity-critical {{ background: #dc3545; }}
        .severity-high {{ background: #fd7e14; }}
        .severity-medium {{ background: #ffc107; color: #333; }}
        .severity-low {{ background: #28a745; }}
        .file-info {{ font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 3px; margin: 10px 0; }}
        .remediation {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #007bff; }}
        .category-tag {{ background: #e9ecef; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; color: #495057; }}
        .confidence-bar {{ background: #e9ecef; height: 8px; border-radius: 4px; margin: 10px 0; }}
        .confidence-fill {{ height: 100%; border-radius: 4px; background: linear-gradient(90deg, #28a745, #ffc107, #fd7e14, #dc3545); }}
        .footer {{ text-align: center; padding: 20px; color: #666; border-top: 1px solid #eee; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Levox Scan Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>License: {license_tier} | Scan time: {scan_time:.2f}s</p>
        </div>
        
        <div class="summary">
            <h2>📊 Executive Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{detection_result.total_matches}</div>
                    <div class="stat-label">Total Issues</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{severity_counts.get('CRITICAL', 0)}</div>
                    <div class="stat-label">Critical</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{severity_counts.get('HIGH', 0)}</div>
                    <div class="stat-label">High</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{severity_counts.get('MEDIUM', 0)}</div>
                    <div class="stat-label">Medium</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{severity_counts.get('LOW', 0)}</div>
                    <div class="stat-label">Low</div>
                </div>
            </div>
            
            <h3>📁 Scan Details</h3>
            <p><strong>Path:</strong> {scan_path}</p>
            <p><strong>Files Scanned:</strong> {detection_result.files_scanned}</p>
            <p><strong>Files with Issues:</strong> {detection_result.files_with_matches}</p>
        </div>
        
        <div class="issues">
            <h2>🔍 Detailed Issues</h2>"""
            
            # Group issues by file for better organization
            issues_by_file = {}
            for fr in detection_result.file_results:
                if fr.matches:
                    issues_by_file[str(fr.file_path)] = fr.matches
            
            for file_path, matches in issues_by_file.items():
                html_content += f"""
            <h3>📄 {Path(file_path).name}</h3>
            <p><strong>Path:</strong> {file_path}</p>"""
                
                for match in matches:
                    severity_class = match.severity.lower()
                    severity_color_class = f"severity-{severity_class}"
                    
                    html_content += f"""
            <div class="issue-card {severity_class}">
                <div class="issue-header">
                    <h4>{match.description or match.pattern_name}</h4>
                    <span class="severity-badge {severity_color_class}">{match.severity}</span>
                </div>
                
                <div class="file-info">
                    <strong>File:</strong> {file_path}:{match.line}
                </div>
                
                <p><strong>Pattern:</strong> {match.pattern_name}</p>
                <p><strong>Engine:</strong> {match.engine}</p>
                <p><strong>Confidence:</strong> {match.confidence:.2f}</p>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {match.confidence * 100}%"></div>
                </div>
                
                <p><strong>Matched Text:</strong> {match.matched_text[:200]}{'...' if len(match.matched_text) > 200 else ''}</p>
                
                {f'<div class="remediation"><strong>💡 Description:</strong> {match.description}</div>' if match.description else ''}
            </div>"""
            
            html_content += """
        </div>
        
        <div class="footer">
            <p>Generated by Levox - Advanced PII Detection Tool</p>
            <p>For more information, visit: https://github.com/levox/levox</p>
        </div>
    </div>
</body>
</html>"""
            
            return html_content
            
        except Exception as e:
            self.logger.error(f"Failed to generate scan HTML report: {e}")
            return f"<html><body><h1>Error generating report: {e}</h1></body></html>"
    
    def _generate_scan_pdf_report(self, detection_result: 'DetectionResult', 
                                 scan_path: str, scan_time: float, license_tier: str) -> str:
        """Generate PDF report for scan results."""
        try:
            # For now, return a message indicating PDF generation
            # In a production environment, you would use a library like reportlab or weasyprint
            return f"PDF report generation not yet implemented. Use --report json or --report html instead."
            
        except Exception as e:
            self.logger.error(f"Failed to generate scan PDF report: {e}")
            return f"Error generating PDF report: {e}"
