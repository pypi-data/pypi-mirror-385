"""
Levox Report Generator

This module handles report generation in various formats (JSON, HTML, PDF, SARIF).
Reports are only generated when explicitly requested, preventing unintended file creation.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid

from ..core.config import Config
from ..models.detection_result import DetectionResult
from .output import OutputManager

class ReportGenerator:
    """Generates professional reports in various formats."""
    
    def __init__(self, config: Config, output_manager: OutputManager):
        """Initialize the report generator."""
        self.config = config
        self.output_manager = output_manager
        self.report_dir = self._get_report_directory()
    
    def generate_report(self, results: DetectionResult, format_type: str, 
                       scan_time: float, license_tier: str) -> Optional[str]:
        """Generate a report in the specified format."""
        try:
            if format_type == 'json':
                return self._generate_json_report(results, scan_time, license_tier)
            elif format_type == 'html':
                return self._generate_html_report(results, scan_time, license_tier)
            elif format_type == 'pdf':
                return self._generate_pdf_report(results, scan_time, license_tier)
            elif format_type == 'sarif':
                return self._generate_sarif_report(results, scan_time, license_tier)
            else:
                self.output_manager.print_warning(f"Unsupported report format: {format_type}")
                return None
                
        except Exception as e:
            self.output_manager.print_error(f"Failed to generate {format_type} report: {e}")
            return None
    
    def generate_report_from_file(self, results: Union[DetectionResult, Dict[str, Any]], format_type: str,
                                 output_file: Optional[str], template: Optional[str],
                                 include_metadata: bool) -> Optional[str]:
        """Generate a report from file results."""
        try:
            # Handle new scan results format
            if isinstance(results, dict):
                # New format: {'scan_metadata': {...}, 'scan_results': {...}}
                scan_results = results.get('scan_results', {})
                scan_metadata = results.get('scan_metadata', {})
                
                # Convert scan_results back to DetectionResult-like structure for compatibility
                if 'file_results' in scan_results:
                    # Already in the right format
                    processed_results = scan_results
                else:
                    # Need to restructure the data
                    processed_results = self._restructure_scan_results(scan_results)
            else:
                # Old format: direct DetectionResult
                processed_results = results
                scan_metadata = {}
            
            if format_type == 'json':
                return self._generate_json_report_from_file(processed_results, output_file, include_metadata)
            elif format_type == 'html':
                return self._generate_html_report_from_file(processed_results, output_file, template, include_metadata)
            elif format_type == 'pdf':
                return self._generate_pdf_report_from_file(processed_results, output_file, template, include_metadata)
            elif format_type == 'sarif':
                return self._generate_sarif_report_from_file(processed_results, output_file, include_metadata)
            else:
                self.output_manager.print_warning(f"Unsupported report format: {format_type}")
                return None
                
        except Exception as e:
            self.output_manager.print_error(f"Failed to generate {format_type} report: {e}")
            return None
    
    def _get_report_directory(self) -> Path:
        """Get the directory for storing reports."""
        # Try to use configured report directory
        if hasattr(self.config, 'report_directory') and self.config.report_directory:
            report_dir = Path(self.config.report_directory)
        else:
            # Default to user's home directory
            report_dir = Path.home() / ".levox" / "reports"
        
        # Create directory if it doesn't exist
        report_dir.mkdir(parents=True, exist_ok=True)
        return report_dir
    
    def _generate_json_report(self, results: DetectionResult, scan_time: float, 
                             license_tier: str) -> str:
        """Generate a JSON report with compliance data."""
        report_data = self._prepare_report_data(results, scan_time, license_tier)
        
        # Add compliance data if available
        if hasattr(results, 'compliance_data') and results.compliance_data:
            report_data['compliance_analysis'] = {
                'alerts': [self._alert_to_dict(a) for a in results.compliance_data['alerts']],
                'score': self._score_to_dict(results.compliance_data['score']),
                'frameworks': results.compliance_data['frameworks'],
                'cross_framework_insights': results.compliance_data.get('cross_framework_insights', {})
            }
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"levox_report_{timestamp}.json"
        report_path = self.report_dir / filename
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return str(report_path)
    
    def _generate_html_report(self, results: DetectionResult, scan_time: float, 
                             license_tier: str) -> str:
        """Generate an HTML report with compliance dashboard."""
        html_content = self._generate_html_content(results, scan_time, license_tier)
        
        # Add compliance dashboard if available
        if hasattr(results, 'compliance_data') and results.compliance_data:
            try:
                from ..compliance.compliance_dashboard import ComplianceDashboard
                
                dashboard_gen = ComplianceDashboard(self.config)
                compliance_html = dashboard_gen.generate_html_dashboard(
                    results.compliance_data['alerts'],
                    results.compliance_data['score']
                )
                
                # Insert compliance section before closing body tag
                html_content = html_content.replace('</body>', f'{compliance_html}</body>')
            except Exception as e:
                self.output_manager.print_warning(f"Failed to add compliance dashboard: {e}")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"levox_report_{timestamp}.html"
        report_path = self.report_dir / filename
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _generate_pdf_report(self, results: DetectionResult, scan_time: float, 
                            license_tier: str) -> str:
        """Generate a PDF report with executive compliance dashboard."""
        try:
            # Generate HTML first (which includes compliance dashboard)
            html_path = self._generate_html_report(results, scan_time, license_tier)
            
            # Convert to PDF (if weasyprint available)
            try:
                from weasyprint import HTML
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_filename = f"levox_report_{timestamp}.pdf"
                pdf_path = self.report_dir / pdf_filename
                HTML(html_path).write_pdf(pdf_path)
                return str(pdf_path)
            except ImportError:
                self.output_manager.print_warning("PDF generation requires weasyprint: pip install weasyprint")
                return html_path  # Fallback to HTML
                
        except Exception as e:
            self.output_manager.print_error(f"Failed to generate PDF report: {e}")
            return None
    
    def _generate_sarif_report(self, results: DetectionResult, scan_time: float, 
                              license_tier: str) -> str:
        """Generate a SARIF report."""
        sarif_data = self._prepare_sarif_data(results, scan_time, license_tier)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"levox_report_{timestamp}.sarif"
        report_path = self.report_dir / filename
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(sarif_data, f, indent=2, ensure_ascii=False)
        
        return str(report_path)
    
    def _generate_json_report_from_file(self, results: Union[DetectionResult, Dict[str, Any]], 
                                       output_file: Optional[str], 
                                       include_metadata: bool) -> Optional[str]:
        """Generate JSON report from file results."""
        # Handle both DetectionResult objects and dictionaries
        if isinstance(results, dict):
            # Check if this is already restructured data
            if 'file_results' in results and 'total_issues_found' in results:
                # Data is already in the right format
                report_data = results.copy()
            else:
                # Extract scan results from the new format
                scan_results = results.get('scan_results', {})
                scan_metadata = results.get('scan_metadata', {})
                
                # Convert to JSON format
                if 'results' in scan_results:
                    report_data = {
                        'total_issues_found': scan_results.get('scan_summary', {}).get('total_matches', 0),
                        'total_files_scanned': scan_results.get('scan_summary', {}).get('total_files', 0),
                        'scan_path': scan_results.get('scan_summary', {}).get('scan_path', 'Unknown'),
                        'file_results': scan_results['results']
                    }
                else:
                    report_data = scan_results
        else:
            # Handle DetectionResult object
            report_data = self.output_manager._convert_to_json(results)
            scan_metadata = {}
        
        if include_metadata:
            report_data['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'levox_version': '0.9.0',
                'report_type': 'json',
                'scan_metadata': scan_metadata
            }
        
        # Always save to file for clean terminal output
        if not output_file:
            # Generate a default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scan_name = "scan_report"
            if hasattr(results, 'scan_path') and results.scan_path:
                scan_name = Path(results['scan_path']).name
            elif isinstance(results, dict) and 'scan_path' in results:
                scan_name = Path(results['scan_path']).name
            
            output_file = f"levox_report_{scan_name}_{timestamp}.json"
        
        # Write to output file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def _generate_html_report_from_file(self, results: DetectionResult, 
                                       output_file: Optional[str], 
                                       template: Optional[str],
                                       include_metadata: bool) -> Optional[str]:
        """Generate HTML report from file results."""
        html_content = self._generate_html_content(results, 0.0, 'enterprise', include_metadata)
        
        # Always save to file for clean terminal output
        if not output_file:
            # Generate a default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scan_name = "scan_report"
            if hasattr(results, 'scan_path') and results.scan_path:
                scan_name = Path(results.scan_path).name
            elif isinstance(results, dict) and 'scan_path' in results:
                scan_name = Path(results['scan_path']).name
            
            output_file = f"levox_report_{scan_name}_{timestamp}.html"
        
        # Write to output file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def _generate_pdf_report_from_file(self, results: DetectionResult, 
                                      output_file: Optional[str], 
                                      template: Optional[str],
                                      include_metadata: bool) -> Optional[str]:
        """Generate PDF report from file results."""
        return self._generate_pdf_report(results, 0.0, 'enterprise')
    
    def _generate_sarif_report_from_file(self, results: DetectionResult, 
                                        output_file: Optional[str], 
                                        include_metadata: bool) -> Optional[str]:
        """Generate SARIF report from file results."""
        sarif_data = self.output_manager._convert_to_sarif(results)
        
        if include_metadata:
            sarif_data['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'levox_version': '0.9.0',
                'report_type': 'sarif'
            }
        
        # Always save to file for clean terminal output
        if not output_file:
            # Generate a default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scan_name = "scan_report"
            if hasattr(results, 'scan_path') and results.scan_path:
                scan_name = Path(results.scan_path).name
            elif isinstance(results, dict) and 'scan_path' in results:
                scan_name = Path(results['scan_path']).name
            
            output_file = f"levox_report_{scan_name}_{timestamp}.sarif"
        
        # Write to output file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sarif_data, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def _prepare_report_data(self, results: DetectionResult, scan_time: float, 
                            license_tier: str) -> Dict[str, Any]:
        """Prepare comprehensive report data."""
        total_matches = sum(len(file_result.matches) for file_result in results.file_results)
        total_files = len(results.file_results)
        
        # Group issues by severity
        issues_by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        for file_result in results.file_results:
            for match in file_result.matches:
                severity = self._calculate_severity(match)
                if severity in issues_by_severity:
                    issues_by_severity[severity].append({
                        'file': str(file_result.file_path),
                        'line': match.line_number,
                        'pattern': match.pattern_name,
                        'description': self._generate_description(match),
                        'confidence': match.confidence,
                        'matched_text': match.matched_text[:100] + "..." if len(match.matched_text) > 100 else match.matched_text
                    })
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'levox_version': '0.9.0',
                'license_tier': license_tier,
                'scan_time_seconds': scan_time
            },
            'scan_summary': {
                'total_files_scanned': total_files,
                'total_issues_found': total_matches,
                'scan_path': str(results.scan_path) if hasattr(results, 'scan_path') else None,
                'severity_distribution': {
                    severity: len(issues) for severity, issues in issues_by_severity.items()
                }
            },
            'issues_by_severity': issues_by_severity,
            'detailed_results': [
                {
                    'file_path': str(file_result.file_path),
                    'file_size_bytes': getattr(file_result, 'file_size', 0),
                    'language': getattr(file_result, 'language', 'unknown'),
                    'matches': [
                        {
                            'pattern_name': match.pattern_name,
                            'line_number': match.line_number,
                            'column_start': match.column_start,
                            'column_end': match.column_end,
                            'matched_text': match.matched_text,
                            'confidence': match.confidence,
                            'risk_level': str(match.risk_level),
                            'detection_level': match.metadata.get('detection_level', 'unknown'),
                            'metadata': match.metadata
                        }
                        for match in file_result.matches
                    ]
                }
                for file_result in results.file_results
            ]
        }
        # Attach NL insights if present
        try:
            nl = getattr(results, 'scan_metadata', {}) or {}
            if isinstance(nl, dict) and 'nl_insights' in nl:
                report['nl_insights'] = nl['nl_insights']
        except Exception:
            pass
        return report
    
    def _prepare_sarif_data(self, results: DetectionResult, scan_time: float, 
                            license_tier: str) -> Dict[str, Any]:
        """Prepare SARIF format data with enhanced CI/CD metadata."""
        # Get CI/CD environment information
        ci_info = self._get_ci_environment_info()
        
        # Collect unique rules
        unique_rules = {}
        for file_result in results.file_results:
            for match in file_result.matches:
                if match.pattern_name not in unique_rules:
                    unique_rules[match.pattern_name] = {
                        "id": match.pattern_name,
                        "name": match.pattern_name,
                        "shortDescription": {"text": f"PII Detection: {match.pattern_name}"},
                        "fullDescription": {"text": self._get_pattern_description(match.pattern_name)},
                        "helpUri": f"https://github.com/levox/levox/docs/patterns#{match.pattern_name}",
                        "properties": {
                            "category": self._get_pattern_category(match.pattern_name),
                            "severity": self._calculate_severity(match),
                            "confidence": match.confidence
                        }
                    }
        
        return {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "Levox",
                        "version": "0.9.0",
                        "informationUri": "https://levoxserver.vercel.app",
                        "fullName": "Levox Enterprise PII/GDPR Detection Tool",
                        "rules": list(unique_rules.values())
                    }
                },
                "invocations": [{
                    "executionSuccessful": True,
                    "startTimeUtc": datetime.now().isoformat(),
                    "endTimeUtc": datetime.now().isoformat(),
                    "toolExecutionNotifications": [],
                    "environmentVariables": ci_info.get("environment_variables", {}),
                    "workingDirectory": {
                        "uri": ci_info.get("working_directory", ".")
                    }
                }],
                "artifacts": [
                    {
                        "location": {"uri": str(file_result.file_path)},
                        "length": getattr(file_result, 'file_size', 0),
                        "mimeType": self._get_mime_type(file_result.file_path),
                        "sourceLanguage": self._get_source_language(file_result.file_path)
                    }
                    for file_result in results.file_results
                ],
                "results": [
                    {
                        "ruleId": match.pattern_name,
                        "level": self._get_sarif_level(match),
                        "message": {
                            "text": self._get_sarif_message(match),
                            "richText": self._get_rich_text_message(match)
                        },
                        "locations": [{
                            "physicalLocation": {
                                "artifactLocation": {"uri": str(file_result.file_path)},
                                "region": {
                                    "startLine": match.line_number,
                                    "startColumn": match.column_start,
                                    "endColumn": match.column_end,
                                    "snippet": {
                                        "text": match.matched_text[:200] + "..." if len(match.matched_text) > 200 else match.matched_text
                                    }
                                }
                            }
                        }],
                        "properties": {
                            "confidence": match.confidence,
                            "detection_level": match.metadata.get('detection_level', 'unknown'),
                            "license_tier": license_tier,
                            "severity": self._calculate_severity(match),
                            "category": self._get_pattern_category(match.pattern_name),
                            "remediation": self._get_remediation_guidance(match.pattern_name),
                            "ci_metadata": {
                                "scan_time": scan_time,
                                "environment": ci_info.get("environment", "unknown"),
                                "build_id": ci_info.get("build_id"),
                                "commit_hash": ci_info.get("commit_hash"),
                                "branch": ci_info.get("branch"),
                                "pull_request": ci_info.get("pull_request")
                            }
                        },
                        "fixes": self._get_sarif_fixes(match),
                        "relatedLocations": self._get_related_locations(match)
                    }
                    for file_result in results.file_results
                    for match in file_result.matches
                ],
                "properties": {
                    "scan_summary": {
                        "total_files_scanned": len(results.file_results),
                        "total_issues_found": sum(len(file_result.matches) for file_result in results.file_results),
                        "scan_time_seconds": scan_time,
                        "license_tier": license_tier,
                        "ci_environment": ci_info.get("environment", "unknown")
                    }
                }
            }]
        }
    
    def _generate_html_content(self, results: Union[DetectionResult, Dict[str, Any]], scan_time: float, 
                              license_tier: str, include_metadata: bool = False) -> str:
        """Generate HTML report content."""
        # Handle both DetectionResult objects and dictionaries
        if isinstance(results, dict):
            # Extract data from dictionary format
            file_results = results.get('file_results', [])
            total_matches = results.get('total_issues_found', 0)
            total_files = len(file_results)
            
            # If scan_time is 0, try to get it from the results
            if scan_time == 0.0 and 'scan_metadata' in results:
                scan_time = results['scan_metadata'].get('scan_time', 0.0)
        else:
            # Handle DetectionResult object
            file_results = results.file_results
            total_matches = sum(len(file_result.matches) for file_result in results.file_results)
            total_files = len(results.file_results)
        
        # Generate severity distribution
        severity_dist = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for file_result in file_results:
            # Handle both object and dict formats
            if isinstance(file_result, dict):
                matches = file_result.get('matches', [])
                file_path = file_result.get('file_path', 'Unknown')
            else:
                matches = file_result.matches
                file_path = file_result.file_path
            
            for match in matches:
                # Handle both object and dict formats
                if isinstance(match, dict):
                    severity = self._calculate_severity_from_dict(match)
                else:
                    severity = self._calculate_severity(match)
                
                if severity in severity_dist:
                    severity_dist[severity] += 1
        
        # NL insights for narrative section
        nl_list: List[Dict[str, Any]] = []
        try:
            if not isinstance(results, dict) and hasattr(results, 'scan_metadata') and results.scan_metadata:
                nl_list = results.scan_metadata.get('nl_insights', []) or []
            elif isinstance(results, dict):
                nl_list = (results.get('scan_metadata', {}) or {}).get('nl_insights', []) or []
        except Exception:
            nl_list = []

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Levox Security Scan Report</title>
    <style>
        :root {{
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --info-color: #17a2b8;
            --light-bg: #f8f9fa;
            --dark-bg: #343a40;
            --border-color: #e9ecef;
            --text-muted: #6c757d;
            --shadow: 0 2px 10px rgba(0,0,0,0.1);
            --shadow-lg: 0 4px 20px rgba(0,0,0,0.15);
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 20px auto;
            background: white;
            border-radius: 16px;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
            position: relative;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.3;
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 3em;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            letter-spacing: -0.02em;
        }}
        
        .header .subtitle {{
            font-size: 1.3em;
            opacity: 0.95;
            margin-top: 15px;
            font-weight: 300;
        }}
        
        .header .badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 20px;
            backdrop-filter: blur(10px);
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .tabs {{
            display: flex;
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 30px;
            background: var(--light-bg);
            border-radius: 8px 8px 0 0;
            overflow: hidden;
        }}
        
        .tab {{
            flex: 1;
            padding: 15px 20px;
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            color: var(--text-muted);
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .tab.active {{
            background: white;
            color: var(--primary-color);
            box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
        }}
        
        .tab:hover:not(.active) {{
            background: rgba(255,255,255,0.5);
            color: var(--primary-color);
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .summary {{
            background: var(--light-bg);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid var(--border-color);
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 25px;
            margin-top: 25px;
        }}
        
        .summary-item {{
            text-align: center;
            padding: 25px 20px;
            background: white;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .summary-item::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }}
        
        .summary-item:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }}
        
        .summary-number {{
            font-size: 2.5em;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 8px;
        }}
        
        .summary-label {{
            color: var(--text-muted);
            font-size: 0.95em;
            font-weight: 500;
        }}
        
        .compliance-dashboard {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 25px 0;
        }}
        
        .compliance-score {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            text-align: center;
        }}
        
        .score-gauge {{
            margin: 20px 0;
        }}
        
        .score-circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: conic-gradient(var(--success-color) 0deg, var(--success-color) calc(var(--score, 0) * 3.6deg), var(--border-color) calc(var(--score, 0) * 3.6deg));
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            position: relative;
        }}
        
        .score-circle::before {{
            content: '';
            position: absolute;
            width: 80px;
            height: 80px;
            background: white;
            border-radius: 50%;
        }}
        
        .score-number {{
            font-size: 2em;
            font-weight: 700;
            color: var(--primary-color);
            z-index: 1;
        }}
        
        .score-label {{
            font-size: 0.8em;
            color: var(--text-muted);
            margin-left: 2px;
        }}
        
        .framework-badges {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 15px;
        }}
        
        .framework-badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            color: white;
        }}
        
        .framework-gdpr {{
            background: linear-gradient(135deg, #667eea, #764ba2);
        }}
        
        .framework-ccpa {{
            background: linear-gradient(135deg, #f093fb, #f5576c);
        }}
        
        .compliance-alerts {{
            margin: 25px 0;
        }}
        
        .alert {{
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid;
        }}
        
        .alert-critical {{
            background: #f8d7da;
            border-left-color: var(--danger-color);
            color: #721c24;
        }}
        
        .alert-high {{
            background: #fff3cd;
            border-left-color: var(--warning-color);
            color: #856404;
        }}
        
        .alert-medium {{
            background: #d1ecf1;
            border-left-color: var(--info-color);
            color: #0c5460;
        }}
        
        .alert-low {{
            background: #d4edda;
            border-left-color: var(--success-color);
            color: #155724;
        }}
        
        .insight-card {{
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: box-shadow 0.2s ease;
        }}
        
        .insight-card:hover {{
            box-shadow: var(--shadow);
        }}
        
        .insight-card h4 {{
            margin: 0 0 10px 0;
            color: var(--primary-color);
            font-size: 1.1em;
        }}
        
        .insight-actions {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--border-color);
        }}
        
        .action-item {{
            display: inline-block;
            background: var(--light-bg);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.9em;
            color: var(--text-muted);
            margin-right: 10px;
        }}
        
        .severity-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.8em;
            font-weight: 600;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .severity-critical {{ background: var(--danger-color); }}
        .severity-high {{ background: #fd7e14; }}
        .severity-medium {{ background: var(--warning-color); color: #212529; }}
        .severity-low {{ background: var(--success-color); }}
        
        .issues-section {{
            margin-top: 30px;
        }}
        
        .file-section {{
            margin-bottom: 30px;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            background: white;
        }}
        
        .file-header {{
            background: var(--light-bg);
            padding: 20px 25px;
            border-bottom: 1px solid var(--border-color);
            font-weight: 600;
            color: var(--dark-bg);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .file-header .file-icon {{
            font-size: 1.2em;
        }}
        
        .file-path {{
            font-size: 0.9em;
            color: var(--text-muted);
            margin-top: 5px;
            font-weight: normal;
        }}
        
        .issues-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .issues-table th {{
            background: var(--light-bg);
            padding: 15px 20px;
            text-align: left;
            font-weight: 600;
            color: var(--dark-bg);
            border-bottom: 2px solid var(--border-color);
        }}
        
        .issues-table td {{
            padding: 15px 20px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: top;
        }}
        
        .issues-table tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .issues-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .footer {{
            background: var(--dark-bg);
            color: white;
            padding: 30px;
            text-align: center;
            margin-top: 40px;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .footer .brand {{
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        
        .footer .tagline {{
            opacity: 0.8;
            font-size: 0.95em;
        }}
        
        .timeline-entry, .timeline-list {{
            margin: 20px 0;
        }}

        .timeline-item {{
            padding: 15px;
            margin: 10px 0;
            background: white;
            border-left: 4px solid var(--primary-color);
            border-radius: 8px;
            display: grid;
            grid-template-columns: 150px 1fr 200px;
            gap: 15px;
            align-items: center;
        }}

        .timeline-date {{
            font-weight: 600;
            color: var(--primary-color);
        }}

        .timeline-path {{
            color: var(--text-muted);
            font-size: 0.9em;
        }}

        .timeline-stats {{
            text-align: right;
            font-size: 0.9em;
            color: var(--text-muted);
        }}
        
        .compliance-summary {{
            display: flex;
            align-items: center;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .compliance-stats {{
            display: flex;
            gap: 20px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: var(--primary-color);
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: var(--text-muted);
        }}
        
        .frameworks-section {{
            margin-top: 30px;
        }}
        
        .frameworks-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .framework-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: var(--shadow);
            border-left: 4px solid var(--primary-color);
        }}
        
        .framework-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .framework-header h4 {{
            margin: 0;
            color: var(--primary-color);
        }}
        
        .framework-score {{
            font-size: 1.5em;
            font-weight: bold;
            color: var(--success-color);
        }}
        
        .framework-stats {{
            display: flex;
            gap: 15px;
        }}
        
        .framework-stat {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .violations-section {{
            margin-top: 30px;
        }}
        
        .violations-list {{
            margin-top: 20px;
        }}
        
        .violation-item {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: var(--shadow);
            border-left: 4px solid var(--warning-color);
        }}
        
        .violation-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .violation-frameworks {{
            font-weight: bold;
            color: var(--primary-color);
        }}
        
        .violation-severity {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .violation-severity.critical {{
            background: var(--danger-color);
            color: white;
        }}
        
        .violation-severity.high {{
            background: #ff6b35;
            color: white;
        }}
        
        .violation-severity.medium {{
            background: var(--warning-color);
            color: black;
        }}
        
        .violation-severity.low {{
            background: var(--info-color);
            color: white;
        }}
        
        .violation-details {{
            display: grid;
            gap: 10px;
        }}
        
        .violation-description {{
            font-weight: 500;
            color: var(--dark-bg);
        }}
        
        .violation-articles {{
            font-size: 0.9em;
            color: var(--text-muted);
        }}
        
        .violation-file {{
            font-size: 0.9em;
            color: var(--text-muted);
            font-family: monospace;
        }}
        
        .violation-remediation {{
            background: var(--light-bg);
            padding: 10px;
            border-radius: 4px;
            font-size: 0.9em;
            color: var(--dark-bg);
        }}
        
        .compliance-status {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 15px;
            background: var(--light-bg);
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .compliance-status.success {{
            border-left: 4px solid var(--success-color);
        }}
        
        .status-icon {{
            font-size: 1.5em;
        }}
        
        .status-text {{
            font-weight: bold;
            color: var(--success-color);
        }}
        
        .compliance-info {{
            background: var(--light-bg);
            padding: 20px;
            border-radius: 8px;
        }}
        
        .compliance-info p {{
            margin: 10px 0;
            color: var(--dark-bg);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 12px;
            }}
            
            .header {{
                padding: 30px 20px;
            }}
            
            .header h1 {{
                font-size: 2.2em;
            }}
            
            .content {{
                padding: 25px 20px;
            }}
            
            .summary-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .compliance-dashboard {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .tabs {{
                flex-direction: column;
            }}
            
            .tab {{
                border-bottom: 1px solid var(--border-color);
            }}
            
            .tab:last-child {{
                border-bottom: none;
            }}
            
            .issues-table {{
                font-size: 0.9em;
            }}
            
            .issues-table th,
            .issues-table td {{
                padding: 12px 15px;
            }}
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            
            .container {{
                box-shadow: none;
                margin: 0;
                border-radius: 0;
            }}
            
            .tabs {{
                display: none;
            }}
            
            .tab-content {{
                display: block !important;
            }}
        }}
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Tab functionality
            const tabs = document.querySelectorAll('.tab');
            const tabContents = document.querySelectorAll('.tab-content');
            
            tabs.forEach(tab => {{
                tab.addEventListener('click', function() {{
                    const targetTab = this.getAttribute('data-tab');
                    
                    // Remove active class from all tabs and contents
                    tabs.forEach(t => t.classList.remove('active'));
                    tabContents.forEach(tc => tc.classList.remove('active'));
                    
                    // Add active class to clicked tab and corresponding content
                    this.classList.add('active');
                    document.getElementById(targetTab).classList.add('active');
                }});
            }});
            
            // Set score circle CSS variable
            const scoreCircles = document.querySelectorAll('.score-circle');
            scoreCircles.forEach(circle => {{
                const score = circle.getAttribute('data-score') || 0;
                circle.style.setProperty('--score', score);
            }});
        }});
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>🔒 Levox Security Scan Report</h1>
                <div class="subtitle">PII Detection & GDPR Compliance Analysis</div>
                <div class="badge">Enterprise Edition • {license_tier.title()}</div>
            </div>
        </div>
        
        <div class="content">
            <div class="tabs">
                <button class="tab active" data-tab="summary">📊 Summary</button>
                <button class="tab" data-tab="compliance">🧭 Compliance</button>
                <button class="tab" data-tab="issues">🔍 Issues</button>
                <button class="tab" data-tab="timeline">📈 Timeline</button>
            </div>
            
            <div id="summary" class="tab-content active">
                <div class="summary">
                    <h2>📊 Scan Summary</h2>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <div class="summary-number">{total_files}</div>
                            <div class="summary-label">Files Scanned</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-number">{total_matches}</div>
                            <div class="summary-label">Issues Found</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-number">{scan_time:.2f}s</div>
                            <div class="summary-label">Scan Time</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-number">{license_tier.title()}</div>
                            <div class="summary-label">License Tier</div>
                        </div>
                    </div>
                    
                    <h3>🚨 Severity Distribution</h3>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <div class="summary-number">{severity_dist['CRITICAL']}</div>
                            <div class="summary-label">Critical</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-number">{severity_dist['HIGH']}</div>
                            <div class="summary-label">High</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-number">{severity_dist['MEDIUM']}</div>
                            <div class="summary-label">Medium</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-number">{severity_dist['LOW']}</div>
                            <div class="summary-label">Low</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="compliance" class="tab-content">
                {self._generate_compliance_section(results)}
            </div>
            
            <div id="issues" class="tab-content">
                <div class="issues-section">
                    <h2>🔍 Detailed Issues</h2>
        """
        
        # Generate timeline content and insert it
        timeline_html = self._generate_timeline_tab(results, scan_time)
        html = html.replace(
            '<div id="issues" class="tab-content">',
            f'<div id="timeline" class="tab-content">\n{timeline_html}\n            </div>\n            \n            <div id="issues" class="tab-content">'
        )
        
        # Add file sections
        for file_result in file_results:
            # Handle both object and dict formats
            if isinstance(file_result, dict):
                matches = file_result.get('matches', [])
                file_path = file_result.get('file_path', 'Unknown')
            else:
                matches = file_result.matches
                file_path = file_result.file_path
            
            if not matches:
                continue
                
            file_name = Path(file_path).name
            file_path_str = str(file_path)
            
            html += f"""
                <div class="file-section">
                    <div class="file-header">
                        📁 {file_name}
                        <div style="font-size: 0.8em; font-weight: normal; margin-top: 5px; color: #6c757d;">
                            {file_path_str}
                        </div>
                    </div>
                    <table class="issues-table">
                        <thead>
                            <tr>
                                <th>Line</th>
                                <th>Severity</th>
                                <th>Pattern</th>
                                <th>Description</th>
                                <th>Confidence</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for match in matches:
                # Handle both object and dict formats
                if isinstance(match, dict):
                    severity = self._calculate_severity_from_dict(match)
                    description = self._generate_description_from_dict(match)
                    confidence_pct = f"{match.get('confidence', 0):.1%}"
                    line_number = match.get('line_number', 0)
                    pattern_name = match.get('pattern_name', 'Unknown')
                else:
                    severity = self._calculate_severity(match)
                    description = self._generate_description(match)
                    confidence_pct = f"{match.confidence:.1%}"
                    line_number = match.line_number
                    pattern_name = match.pattern_name
                
                html += f"""
                            <tr>
                                <td>{line_number}</td>
                                <td><span class="severity-badge severity-{severity.lower()}">{severity}</span></td>
                                <td>{pattern_name}</td>
                                <td>{description}</td>
                                <td>{confidence_pct}</td>
                            </tr>
                """
            
            html += """
                        </tbody>
                    </table>
                </div>
            """
        
        # Natural Language compliance prompts section
        if nl_list:
            html += """
                <div class="issues-section">
                    <h2>🗣️ Natural Language Compliance Prompts</h2>
                    <p>The following questions highlight potentially unnecessary data usage:</p>
                    <ul>
            """
            for ins in nl_list[:50]:
                desc = ins.get('description', '')
                html += f"<li>{desc}</li>"
            html += """
                    </ul>
                </div>
            """

        # Add metadata if requested
        if include_metadata:
            html += f"""
                <div class="summary">
                    <h2>📋 Metadata</h2>
                    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Levox Version:</strong> 0.9.0</p>
                    <p><strong>Report Type:</strong> HTML</p>
                </div>
            """
        
        # Compliance dashboard section
        try:
            has_compliance_data = False
            compliance_data = None
            compliance_note = None
            
            if not isinstance(results, dict) and hasattr(results, 'compliance_data'):
                has_compliance_data = bool(results.compliance_data)
                compliance_data = results.compliance_data
                if hasattr(results, 'scan_metadata') and results.scan_metadata:
                    compliance_note = results.scan_metadata.get('compliance_error') or results.scan_metadata.get('compliance_note')
            elif isinstance(results, dict):
                compliance_data = results.get('compliance_data')
                has_compliance_data = bool(compliance_data)
                compliance_note = (results.get('scan_metadata', {}) or {}).get('compliance_error') or (results.get('scan_metadata', {}) or {}).get('compliance_note')
            
            if has_compliance_data and compliance_data:
                # Generate compliance dashboard
                compliance_dashboard_html = self._generate_compliance_dashboard(compliance_data)
                # Insert into compliance tab by replacing the placeholder comment
                html = html.replace(
                    '<div id="compliance" class="tab-content">\n                <!-- Compliance content will be inserted here -->\n            </div>',
                    f'<div id="compliance" class="tab-content">\n{compliance_dashboard_html}\n            </div>'
                )
            else:
                # Show compliance unavailable message
                compliance_unavailable_html = f"""
                <div class="summary" style="border-left: 4px solid #ffc107;">
                    <h2>⚠️ Compliance Section Not Available</h2>
                    <p>{(compliance_note or 'Compliance frameworks were not available for this scan or license tier. Enable GDPR/CCPA frameworks or upgrade your license to view the compliance dashboard and article mappings.')}</p>
                </div>
                """
                html = html.replace(
                    '<div id="compliance" class="tab-content">\n                <!-- Compliance content will be inserted here -->\n            </div>',
                    f'<div id="compliance" class="tab-content">\n{compliance_unavailable_html}\n            </div>'
                )
        except Exception:
            pass
        
        html += """
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by Levox - Enterprise PII/GDPR Detection Tool</p>
            <p>🔒 Secure • 🚀 Fast • 🎯 Accurate</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def _calculate_severity(self, match) -> str:
        """Calculate severity for a detection match."""
        # Use the same logic as the output manager
        risk_value = getattr(match.risk_level, 'value', str(match.risk_level)).upper()
        confidence = match.confidence
        pattern_name = match.pattern_name.lower()
        
        # Base severity from risk level
        base_severity = {
            'CRITICAL': 4,
            'HIGH': 3,
            'MEDIUM': 2,
            'LOW': 1
        }.get(risk_value, 2)
        
        # Adjust based on confidence
        if confidence > 0.9:
            base_severity += 1
        elif confidence < 0.5:
            base_severity -= 1
        
        # Adjust based on pattern type
        if 'password' in pattern_name or 'secret' in pattern_name:
            base_severity += 1
        elif 'email' in pattern_name and confidence < 0.7:
            base_severity -= 1
        
        # Clamp to valid range
        base_severity = max(1, min(4, base_severity))
        
        severity_map = {4: 'CRITICAL', 3: 'HIGH', 2: 'MEDIUM', 1: 'LOW'}
        return severity_map[base_severity]
    
    def _generate_description(self, match) -> str:
        """Generate a description for a detection match."""
        pattern_name = match.pattern_name
        matched_text = match.matched_text
        
        descriptions = {
            'hardcoded_password': f"Hardcoded password found: '{matched_text[:20]}{'...' if len(matched_text) > 20 else ''}'",
            'api_key': f"API key exposed in code: '{matched_text[:20]}{'...' if len(matched_text) > 20 else ''}'",
            'email_address': f"Email address found: {matched_text}",
            'credit_card': f"Credit card number detected: {matched_text[:4]}****{matched_text[-4:]}",
            'ssn': f"Social Security Number detected: {matched_text[:3]}-**-{matched_text[-4:]}",
            'phone_number': f"Phone number found: {matched_text}",
            'ip_address': f"IP address found: {matched_text}",
            'database_url': f"Database connection string found: {matched_text.split('@')[0]}@***",
            'aws_access_key': f"AWS access key found: {matched_text[:20]}...",
            'private_key': f"Private key or certificate found in code"
        }
        
        return descriptions.get(pattern_name, f"Potential {pattern_name.replace('_', ' ')}: {matched_text}")
    
    def _generate_compliance_dashboard(self, compliance_data: Dict[str, Any]) -> str:
        """Generate compliance dashboard HTML section."""
        try:
            # Extract compliance data
            alerts = compliance_data.get('alerts', [])
            score = compliance_data.get('score', {})
            frameworks = compliance_data.get('frameworks', [])
            violations = compliance_data.get('unified_violations', [])
            insights = compliance_data.get('cross_framework_insights', [])
            
            # Get NL insights from scan metadata if available
            nl_insights = []
            try:
                if hasattr(self, '_current_results') and self._current_results:
                    if hasattr(self._current_results, 'scan_metadata') and self._current_results.scan_metadata:
                        nl_insights = self._current_results.scan_metadata.get('nl_insights', [])
            except:
                pass
            
            html = f"""
            <div class="summary">
                <h2>🧭 Executive Compliance Summary</h2>
                <div class="compliance-dashboard">
                    <div class="compliance-score">
                        <h3>Compliance Score</h3>
                        <div class="score-gauge">
                            <div class="score-circle" data-score="{score.get('overall_score', 0)}">
                                <span class="score-number">{score.get('overall_score', 0)}</span>
                                <span class="score-label">/ 100</span>
                            </div>
                        </div>
                        <p class="score-description">{score.get('description', 'Overall compliance assessment')}</p>
                    </div>
                    
                    <div class="frameworks-analyzed">
                        <h3>Frameworks Analyzed</h3>
                        <div class="framework-badges">
            """
            
            for framework in frameworks:
                framework_name = framework.upper() if isinstance(framework, str) else str(framework).upper()
                html += f'<span class="framework-badge framework-{framework_name.lower()}">{framework_name}</span>'
            
            html += """
                        </div>
                    </div>
                </div>
                
                <div class="compliance-alerts">
                    <h3>🚨 Compliance Alerts</h3>
            """
            
            if alerts:
                for alert in alerts[:5]:  # Show top 5 alerts
                    severity = alert.get('severity', 'medium').upper()
                    html += f"""
                    <div class="alert alert-{severity.lower()}">
                        <strong>{alert.get('title', 'Compliance Alert')}</strong>
                        <p>{alert.get('description', 'No description available')}</p>
                        <small>Framework: {alert.get('framework', 'Unknown')} | Article: {alert.get('article', 'N/A')}</small>
                    </div>
                    """
            else:
                html += '<p class="no-alerts">✅ No compliance alerts found</p>'
            
            html += """
                </div>
                
                <div class="nl-insights">
                    <h3>🔍 Natural Language Compliance Insights</h3>
            """
            
            if nl_insights:
                for insight in nl_insights[:3]:  # Show top 3 insights
                    html += f"""
                    <div class="insight-card">
                        <h4>{insight.get('title', 'Compliance Insight')}</h4>
                        <p>{insight.get('description', 'No description available')}</p>
                        <div class="insight-actions">
                            <span class="action-item">📋 {insight.get('action', 'Review findings')}</span>
                        </div>
                    </div>
                    """
            else:
                html += '<p class="no-insights">No natural language insights available for this scan.</p>'
            
            html += """
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            return f"""
            <div class="summary" style="border-left: 4px solid #dc3545;">
                <h2>❌ Compliance Dashboard Error</h2>
                <p>Failed to render compliance dashboard: {str(e)}</p>
            </div>
            """
    
    def _generate_compliance_section(self, results: Union[DetectionResult, Dict[str, Any]]) -> str:
        """Generate compliance dashboard section."""
        # Extract compliance data
        compliance_data = None
        if isinstance(results, dict):
            compliance_data = results.get('compliance_data', {})
        elif hasattr(results, 'compliance_data'):
            compliance_data = results.compliance_data
        
        if not compliance_data:
            return """
                <div class="compliance-dashboard">
                    <h2>🧭 Compliance Dashboard</h2>
                    <div class="compliance-summary">
                        <div class="compliance-item">
                            <div class="compliance-status success">
                                <span class="status-icon">✅</span>
                                <span class="status-text">No compliance violations detected</span>
                            </div>
                        </div>
                        <div class="compliance-info">
                            <p>✅ No GDPR/CCPA violations found in the scanned codebase.</p>
                            <p>🔒 All detected PII patterns appear to be in safe contexts (test data, framework patterns, etc.).</p>
                        </div>
                    </div>
                </div>
            """
        
        # Extract compliance information
        frameworks_analyzed = compliance_data.get('frameworks_analyzed', [])
        unified_violations = compliance_data.get('unified_violations', [])
        overall_score = compliance_data.get('overall_compliance_score', 100.0)
        framework_results = compliance_data.get('framework_results', {})
        
        # Generate compliance HTML
        compliance_html = f"""
            <div class="compliance-dashboard">
                <h2>🧭 Compliance Dashboard</h2>
                
                <div class="compliance-summary">
                    <div class="compliance-score">
                        <div class="score-circle" data-score="{overall_score}">
                            <span class="score-number">{overall_score:.0f}</span>
                            <span class="score-label">Compliance Score</span>
                        </div>
                    </div>
                    
                    <div class="compliance-stats">
                        <div class="stat-item">
                            <div class="stat-number">{len(frameworks_analyzed)}</div>
                            <div class="stat-label">Frameworks Analyzed</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{len(unified_violations)}</div>
                            <div class="stat-label">Violations Found</div>
                        </div>
                    </div>
                </div>
                
                <div class="frameworks-section">
                    <h3>📋 Framework Analysis</h3>
                    <div class="frameworks-grid">
        """
        
        # Add framework results
        for framework, result in framework_results.items():
            framework_name = framework.value if hasattr(framework, 'value') else str(framework)
            issues_count = len(result.get('issues', []))
            compliance_score = result.get('compliance_score', 100.0)
            
            compliance_html += f"""
                        <div class="framework-card">
                            <div class="framework-header">
                                <h4>{framework_name}</h4>
                                <div class="framework-score">{compliance_score:.0f}</div>
                            </div>
                            <div class="framework-stats">
                                <div class="framework-stat">
                                    <span class="stat-label">Issues:</span>
                                    <span class="stat-value">{issues_count}</span>
                                </div>
                            </div>
                        </div>
            """
        
        compliance_html += """
                    </div>
                </div>
        """
        
        # Add violations section if any exist
        if unified_violations:
            compliance_html += """
                <div class="violations-section">
                    <h3>⚠️ Compliance Violations</h3>
                    <div class="violations-list">
            """
            
            for violation in unified_violations[:10]:  # Limit to first 10
                frameworks = violation.get('frameworks', [])
                frameworks_str = ', '.join([f.value if hasattr(f, 'value') else str(f) for f in frameworks])
                article_refs = violation.get('article_refs', {})
                article_str = ', '.join([f"{k.value if hasattr(k, 'value') else k}: {v}" for k, v in article_refs.items()])
                
                compliance_html += f"""
                        <div class="violation-item">
                            <div class="violation-header">
                                <span class="violation-frameworks">{frameworks_str}</span>
                                <span class="violation-severity {violation.get('severity', 'MEDIUM').lower()}">{violation.get('severity', 'MEDIUM')}</span>
                            </div>
                            <div class="violation-details">
                                <div class="violation-description">{violation.get('description', 'No description')}</div>
                                <div class="violation-articles">{article_str}</div>
                                <div class="violation-file">{violation.get('file_path', 'Unknown')}:{violation.get('line_number', 0)}</div>
                                <div class="violation-remediation">{violation.get('remediation', 'No remediation provided')}</div>
                            </div>
                        </div>
                """
            
            compliance_html += """
                    </div>
                </div>
            """
        
        compliance_html += """
            </div>
        """
        
        return compliance_html
    
    def _generate_timeline_tab(self, results, scan_time: float) -> str:
        """Generate timeline tab content showing scan history and trends."""
        try:
            timeline_html = '<div class="summary"><h2>📈 Scan Timeline & History</h2>'
            
            # Current scan info
            timeline_html += f'''
            <div class="timeline-entry">
                <h3>Current Scan</h3>
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Duration:</strong> {scan_time:.2f}s</p>
                <p><strong>Files Scanned:</strong> {len(results.file_results) if hasattr(results, 'file_results') else 0}</p>
                <p><strong>Issues Found:</strong> {results.total_matches if hasattr(results, 'total_matches') else 0}</p>
            </div>
            '''
            
            # Load scan history if available
            try:
                from ..core.user_config import get_user_config
                user_config = get_user_config()
                history = user_config.history[-10:]  # Last 10 scans
                
                if history:
                    timeline_html += '<h3>Recent Scan History</h3><div class="timeline-list">'
                    for scan in reversed(history):
                        timeline_html += f'''
                        <div class="timeline-item">
                            <span class="timeline-date">{scan.timestamp.strftime('%Y-%m-%d %H:%M')}</span>
                            <span class="timeline-path">{scan.scan_path}</span>
                            <span class="timeline-stats">{scan.matches_found} issues in {scan.files_scanned} files</span>
                        </div>
                        '''
                    timeline_html += '</div>'
            except Exception:
                timeline_html += '<p class="no-data">No historical scan data available.</p>'
            
            timeline_html += '</div>'
            return timeline_html
        except Exception as e:
            return f'<div class="summary"><h2>📈 Timeline</h2><p>Error generating timeline: {str(e)}</p></div>'

    def _generate_description_from_dict(self, match_dict: Dict[str, Any]) -> str:
        """Generate a description for a detection match from a dictionary."""
        pattern_name = match_dict.get('pattern_name', 'Unknown')
        matched_text = match_dict.get('matched_text', '')

        descriptions = {
            'hardcoded_password': f"Hardcoded password found: '{matched_text[:20]}{'...' if len(matched_text) > 20 else ''}'",
            'api_key': f"API key exposed in code: '{matched_text[:20]}{'...' if len(matched_text) > 20 else ''}'",
            'email_address': f"Email address found: {matched_text}",
            'credit_card': f"Credit card number detected: {matched_text[:4]}****{matched_text[-4:]}",
            'ssn': f"Social Security Number detected: {matched_text[:3]}-**-{matched_text[-4:]}",
            'phone_number': f"Phone number found: {matched_text}",
            'ip_address': f"IP address found: {matched_text}",
            'database_url': f"Database connection string found: {matched_text.split('@')[0]}@***",
            'aws_access_key': f"AWS access key found: {matched_text[:20]}...",
            'private_key': f"Private key or certificate found in code"
        }

        return descriptions.get(pattern_name, f"Potential {pattern_name.replace('_', ' ')}: {matched_text}")

    def _calculate_severity_from_dict(self, match_dict: Dict[str, Any]) -> str:
        """Calculate severity for a detection match from a dictionary."""
        risk_value = match_dict.get('risk_level', 'MEDIUM').upper()
        confidence = match_dict.get('confidence', 0.5)
        pattern_name = match_dict.get('pattern_name', 'Unknown').lower()

        # Base severity from risk level
        base_severity = {
            'CRITICAL': 4,
            'HIGH': 3,
            'MEDIUM': 2,
            'LOW': 1
        }.get(risk_value, 2)

        # Adjust based on confidence
        if confidence > 0.9:
            base_severity += 1
        elif confidence < 0.5:
            base_severity -= 1

        # Adjust based on pattern type
        if 'password' in pattern_name or 'secret' in pattern_name:
            base_severity += 1
        elif 'email' in pattern_name and confidence < 0.7:
            base_severity -= 1

        # Clamp to valid range
        base_severity = max(1, min(4, base_severity))

        severity_map = {4: 'CRITICAL', 3: 'HIGH', 2: 'MEDIUM', 1: 'LOW'}
        return severity_map[base_severity]

    def _restructure_scan_results(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Restructure scan results to match expected format."""
        # Handle the actual scan results structure
        if 'results' in scan_results:
            # Convert 'results' to 'file_results' for compatibility
            restructured = {
                'file_results': scan_results['results'],
                'total_issues_found': scan_results.get('scan_summary', {}).get('total_matches', 0),
                'scan_path': scan_results.get('scan_summary', {}).get('scan_path', 'Unknown')
            }
            return restructured
        elif 'total_issues_found' in scan_results and 'file_results' not in scan_results:
            # Convert from summary format to detailed format
            restructured = {
                'file_results': [],
                'total_issues_found': scan_results.get('total_issues_found', 0),
                'scan_path': scan_results.get('scan_path', 'Unknown')
            }
            return restructured
        
        return scan_results
    
    def _get_ci_environment_info(self) -> Dict[str, Any]:
        """Get CI/CD environment information."""
        ci_info = {
            "environment": "unknown",
            "environment_variables": {},
            "working_directory": os.getcwd(),
            "build_id": None,
            "commit_hash": None,
            "branch": None,
            "pull_request": None
        }
        
        # Detect CI environment
        if os.getenv("GITHUB_ACTIONS"):
            ci_info.update({
                "environment": "github_actions",
                "build_id": os.getenv("GITHUB_RUN_ID"),
                "commit_hash": os.getenv("GITHUB_SHA"),
                "branch": os.getenv("GITHUB_REF_NAME"),
                "pull_request": os.getenv("GITHUB_PR_NUMBER"),
                "environment_variables": {
                    "GITHUB_REPOSITORY": os.getenv("GITHUB_REPOSITORY"),
                    "GITHUB_WORKFLOW": os.getenv("GITHUB_WORKFLOW"),
                    "GITHUB_ACTOR": os.getenv("GITHUB_ACTOR")
                }
            })
        elif os.getenv("GITLAB_CI"):
            ci_info.update({
                "environment": "gitlab_ci",
                "build_id": os.getenv("CI_PIPELINE_ID"),
                "commit_hash": os.getenv("CI_COMMIT_SHA"),
                "branch": os.getenv("CI_COMMIT_REF_NAME"),
                "pull_request": os.getenv("CI_MERGE_REQUEST_IID"),
                "environment_variables": {
                    "CI_PROJECT_NAME": os.getenv("CI_PROJECT_NAME"),
                    "CI_PIPELINE_URL": os.getenv("CI_PIPELINE_URL"),
                    "CI_COMMIT_AUTHOR": os.getenv("CI_COMMIT_AUTHOR")
                }
            })
        elif os.getenv("JENKINS_URL"):
            ci_info.update({
                "environment": "jenkins",
                "build_id": os.getenv("BUILD_NUMBER"),
                "commit_hash": os.getenv("GIT_COMMIT"),
                "branch": os.getenv("GIT_BRANCH"),
                "environment_variables": {
                    "JOB_NAME": os.getenv("JOB_NAME"),
                    "BUILD_URL": os.getenv("BUILD_URL"),
                    "GIT_COMMITTER_NAME": os.getenv("GIT_COMMITTER_NAME")
                }
            })
        elif os.getenv("AZURE_DEVOPS"):
            ci_info.update({
                "environment": "azure_devops",
                "build_id": os.getenv("BUILD_BUILDID"),
                "commit_hash": os.getenv("BUILD_SOURCEVERSION"),
                "branch": os.getenv("BUILD_SOURCEBRANCHNAME"),
                "pull_request": os.getenv("SYSTEM_PULLREQUEST_PULLREQUESTNUMBER"),
                "environment_variables": {
                    "BUILD_REPOSITORY_NAME": os.getenv("BUILD_REPOSITORY_NAME"),
                    "BUILD_DEFINITIONNAME": os.getenv("BUILD_DEFINITIONNAME"),
                    "BUILD_REQUESTEDFOR": os.getenv("BUILD_REQUESTEDFOR")
                }
            })
        elif os.getenv("CIRCLECI"):
            ci_info.update({
                "environment": "circleci",
                "build_id": os.getenv("CIRCLE_BUILD_NUM"),
                "commit_hash": os.getenv("CIRCLE_SHA1"),
                "branch": os.getenv("CIRCLE_BRANCH"),
                "pull_request": os.getenv("CIRCLE_PULL_REQUEST"),
                "environment_variables": {
                    "CIRCLE_PROJECT_REPONAME": os.getenv("CIRCLE_PROJECT_REPONAME"),
                    "CIRCLE_USERNAME": os.getenv("CIRCLE_USERNAME"),
                    "CIRCLE_WORKFLOW_ID": os.getenv("CIRCLE_WORKFLOW_ID")
                }
            })
        elif os.getenv("BITBUCKET_BUILD_NUMBER"):
            ci_info.update({
                "environment": "bitbucket_pipelines",
                "build_id": os.getenv("BITBUCKET_BUILD_NUMBER"),
                "commit_hash": os.getenv("BITBUCKET_COMMIT"),
                "branch": os.getenv("BITBUCKET_BRANCH"),
                "pull_request": os.getenv("BITBUCKET_PR_ID"),
                "environment_variables": {
                    "BITBUCKET_REPO_FULL_NAME": os.getenv("BITBUCKET_REPO_FULL_NAME"),
                    "BITBUCKET_STEP_UUID": os.getenv("BITBUCKET_STEP_UUID"),
                    "BITBUCKET_BUILD_NUMBER": os.getenv("BITBUCKET_BUILD_NUMBER")
                }
            })
        
        return ci_info
    
    def _get_pattern_description(self, pattern_name: str) -> str:
        """Get detailed description for a pattern."""
        descriptions = {
            "hardcoded_password": "Hardcoded passwords pose a significant security risk as they can be easily discovered in source code. Use environment variables or secure credential management systems instead.",
            "api_key": "API keys exposed in source code can be misused by unauthorized parties. Store API keys in secure environment variables or key management services.",
            "email_address": "Email addresses found in code may indicate PII exposure. Consider if this data should be externalized or anonymized.",
            "credit_card": "Credit card numbers in source code violate PCI DSS compliance requirements. Never store credit card data in code repositories.",
            "ssn": "Social Security Numbers are highly sensitive PII that should never be stored in source code. Use secure data storage solutions.",
            "phone_number": "Phone numbers may contain PII and should be handled according to privacy regulations like GDPR.",
            "ip_address": "IP addresses may be considered PII in certain jurisdictions and should be handled appropriately.",
            "database_url": "Database connection strings often contain sensitive credentials and should be externalized to environment variables.",
            "aws_access_key": "AWS access keys provide access to cloud resources and should never be stored in source code. Use IAM roles or secure key management.",
            "private_key": "Private keys and certificates should never be stored in source code repositories. Use secure key management systems."
        }
        return descriptions.get(pattern_name, f"Potential {pattern_name.replace('_', ' ')} detected in source code.")
    
    def _get_pattern_category(self, pattern_name: str) -> str:
        """Get category for a pattern."""
        categories = {
            "hardcoded_password": "Authentication",
            "api_key": "API Security",
            "email_address": "PII",
            "credit_card": "Financial Data",
            "ssn": "PII",
            "phone_number": "PII",
            "ip_address": "Network",
            "database_url": "Database",
            "aws_access_key": "Cloud Credentials",
            "private_key": "Cryptography"
        }
        return categories.get(pattern_name, "Security")
    
    def _get_sarif_level(self, match) -> str:
        """Get SARIF level for a match."""
        severity = self._calculate_severity(match)
        confidence = match.confidence
        
        if severity == "CRITICAL" and confidence > 0.9:
            return "error"
        elif severity in ["HIGH", "CRITICAL"] and confidence > 0.7:
            return "error"
        elif severity == "MEDIUM" and confidence > 0.8:
            return "warning"
        elif severity in ["MEDIUM", "LOW"] and confidence > 0.5:
            return "warning"
        else:
            return "note"
    
    def _get_sarif_message(self, match) -> str:
        """Get SARIF message for a match."""
        pattern_name = match.pattern_name
        matched_text = match.matched_text
        
        messages = {
            "hardcoded_password": f"Hardcoded password detected: '{matched_text[:20]}{'...' if len(matched_text) > 20 else ''}'",
            "api_key": f"API key exposed in code: '{matched_text[:20]}{'...' if len(matched_text) > 20 else ''}'",
            "email_address": f"Email address found: {matched_text}",
            "credit_card": f"Credit card number detected: {matched_text[:4]}****{matched_text[-4:]}",
            "ssn": f"Social Security Number detected: {matched_text[:3]}-**-{matched_text[-4:]}",
            "phone_number": f"Phone number found: {matched_text}",
            "ip_address": f"IP address found: {matched_text}",
            "database_url": f"Database connection string found: {matched_text.split('@')[0]}@***",
            "aws_access_key": f"AWS access key found: {matched_text[:20]}...",
            "private_key": "Private key or certificate found in code"
        }
        
        return messages.get(pattern_name, f"Potential {pattern_name.replace('_', ' ')}: {matched_text}")
    
    def _get_rich_text_message(self, match) -> str:
        """Get rich text message for SARIF."""
        base_message = self._get_sarif_message(match)
        remediation = self._get_remediation_guidance(match.pattern_name)
        
        return f"{base_message}\n\n**Remediation:** {remediation}"
    
    def _get_remediation_guidance(self, pattern_name: str) -> str:
        """Get remediation guidance for a pattern."""
        guidance = {
            "hardcoded_password": "Store passwords in environment variables or use a secure credential management system like HashiCorp Vault or AWS Secrets Manager.",
            "api_key": "Move API keys to environment variables or use a secure key management service. Never commit API keys to version control.",
            "email_address": "Consider if email addresses need to be in source code. If required, use configuration files or environment variables.",
            "credit_card": "Never store credit card data in source code. Use PCI-compliant payment processors and tokenization services.",
            "ssn": "Social Security Numbers should never be stored in source code. Use secure databases with proper encryption and access controls.",
            "phone_number": "Store phone numbers in secure databases with proper access controls. Consider data anonymization techniques.",
            "ip_address": "IP addresses may be considered PII. Store in secure databases and implement proper access controls.",
            "database_url": "Move database connection strings to environment variables or configuration files outside of version control.",
            "aws_access_key": "Use IAM roles instead of access keys when possible. Store access keys in AWS Secrets Manager or similar services.",
            "private_key": "Store private keys in secure key management systems. Never commit private keys to version control."
        }
        return guidance.get(pattern_name, "Review the detected pattern and implement appropriate security measures.")
    
    def _get_sarif_fixes(self, match) -> List[Dict[str, Any]]:
        """Get SARIF fixes for a match."""
        fixes = []
        
        if match.pattern_name in ["hardcoded_password", "api_key", "database_url", "aws_access_key"]:
            fixes.append({
                "description": {
                    "text": "Replace hardcoded value with environment variable"
                },
                "artifactChanges": [{
                    "artifactLocation": {"uri": str(match.file_path)},
                    "replacements": [{
                        "deletedRegion": {
                            "startLine": match.line_number,
                            "startColumn": match.column_start,
                            "endColumn": match.column_end
                        },
                        "insertedContent": {
                            "text": f"os.getenv('{match.pattern_name.upper()}_KEY')"
                        }
                    }]
                }]
            })
        
        return fixes
    
    def _get_related_locations(self, match) -> List[Dict[str, Any]]:
        """Get related locations for a match."""
        related = []
        
        # Add related locations based on pattern type
        if match.pattern_name == "hardcoded_password":
            related.append({
                "id": 1,
                "physicalLocation": {
                    "artifactLocation": {"uri": "https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_credentials"},
                    "region": {"startLine": 1}
                },
                "message": {"text": "OWASP guidance on hardcoded credentials"}
            })
        
        return related
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for a file."""
        mime_types = {
            ".py": "text/x-python",
            ".js": "text/javascript",
            ".ts": "text/typescript",
            ".java": "text/x-java-source",
            ".go": "text/x-go",
            ".rs": "text/x-rust",
            ".cpp": "text/x-c++",
            ".c": "text/x-c",
            ".h": "text/x-c",
            ".php": "text/x-php",
            ".rb": "text/x-ruby",
            ".swift": "text/x-swift",
            ".kt": "text/x-kotlin",
            ".scala": "text/x-scala",
            ".clj": "text/x-clojure",
            ".hs": "text/x-haskell",
            ".ml": "text/x-ocaml",
            ".fs": "text/x-fsharp",
            ".vb": "text/x-vb",
            ".cs": "text/x-csharp",
            ".dart": "text/x-dart",
            ".r": "text/x-r",
            ".m": "text/x-objective-c",
            ".pl": "text/x-perl",
            ".sh": "text/x-shellscript",
            ".bash": "text/x-shellscript",
            ".zsh": "text/x-shellscript",
            ".fish": "text/x-fish",
            ".ps1": "text/x-powershell",
            ".bat": "text/x-msdos-batch",
            ".cmd": "text/x-msdos-batch"
        }
        
        return mime_types.get(file_path.suffix.lower(), "text/plain")
    
    def _get_source_language(self, file_path: Path) -> str:
        """Get source language for a file."""
        languages = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".clj": "clojure",
            ".hs": "haskell",
            ".ml": "ocaml",
            ".fs": "fsharp",
            ".vb": "vb",
            ".cs": "csharp",
            ".dart": "dart",
            ".r": "r",
            ".m": "objective-c",
            ".pl": "perl",
            ".sh": "shell",
            ".bash": "shell",
            ".zsh": "shell",
            ".fish": "fish",
            ".ps1": "powershell",
            ".bat": "batch",
            ".cmd": "batch"
        }
        
        return languages.get(file_path.suffix.lower(), "unknown")
    
    def _alert_to_dict(self, alert) -> Dict[str, Any]:
        """Convert ComplianceAlert to dictionary."""
        try:
            return {
                'id': alert.id,
                'timestamp': alert.timestamp.isoformat(),
                'severity': alert.severity.value if hasattr(alert.severity, 'value') else str(alert.severity),
                'framework': alert.framework,
                'article_ref': alert.article_ref,
                'title': alert.title,
                'description': alert.description,
                'file_path': alert.file_path,
                'line_number': alert.line_number,
                'context': alert.context,
                'remediation': alert.remediation,
                'confidence': alert.confidence,
                'category': alert.category,
                'matched_text': alert.matched_text,
                'metadata': alert.metadata
            }
        except Exception as e:
            self.output_manager.print_warning(f"Failed to convert alert to dict: {e}")
            return {}
    
    def _score_to_dict(self, score) -> Dict[str, Any]:
        """Convert ComplianceScore to dictionary."""
        try:
            return {
                'score': score.score,
                'grade': score.grade,
                'risk_level': score.risk_level.value if hasattr(score.risk_level, 'value') else str(score.risk_level),
                'industry': score.industry,
                'percentile': score.percentile,
                'scoring_breakdown': score.scoring_breakdown,
                'recommendations': score.recommendations,
                'generated_at': score.generated_at.isoformat() if hasattr(score.generated_at, 'isoformat') else str(score.generated_at)
            }
        except Exception as e:
            self.output_manager.print_warning(f"Failed to convert score to dict: {e}")
            return {}
