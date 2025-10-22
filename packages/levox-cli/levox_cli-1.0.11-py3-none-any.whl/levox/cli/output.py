"""
Levox Output Manager

This module handles all terminal output formatting, including progress bars,
result display, and report generation. It provides a clean interface for
different output formats and verbosity levels.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.columns import Columns
from rich.syntax import Syntax
from rich.tree import Tree
from rich.align import Align
from rich import box

from ..core.config import Config
from ..models.detection_result import DetectionResult, FileResult, DetectionMatch
from ..core.exceptions import LevoxException
from ..compliance.compliance_alerter import ComplianceAlert, AlertSeverity

# Exit codes
EXIT_SUCCESS = 0
EXIT_VIOLATIONS_FOUND = 1
EXIT_RUNTIME_ERROR = 2
EXIT_CONFIG_ERROR = 3

@dataclass
class StructuredIssue:
    """Structured representation of a detection issue for display and reporting."""
    file: str
    line: int
    severity: str
    description: str
    remediation: str
    category: str
    confidence: float
    pattern_name: str
    matched_text: str
    detection_level: str
    risk_level: str
    metadata: Dict[str, Any]
    
    def __lt__(self, other):
        """Sort by severity (CRITICAL > HIGH > MEDIUM > LOW) then by line number."""
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        if self.severity != other.severity:
            return severity_order.get(self.severity, 4) < severity_order.get(other.severity, 4)
        return self.line < other.line

class OutputManager:
    """Manages all terminal output with beautiful formatting and configurable verbosity."""
    
    def __init__(self, config: Config):
        """Initialize the output manager with configuration."""
        self.config = config
        self.console = Console(emoji=(sys.platform != 'win32'))
        self.verbosity = 'summary'
        self.telemetry = False
        
        # Configure Windows console for UTF-8
        if sys.platform == 'win32':
            try:
                if hasattr(sys.stdout, 'reconfigure'):
                    sys.stdout.reconfigure(encoding='utf-8')
                if hasattr(sys.stderr, 'reconfigure'):
                    sys.stderr.reconfigure(encoding='utf-8')
            except Exception:
                pass
    
    def set_verbosity(self, verbosity: str):
        """Set the output verbosity level."""
        self.verbosity = verbosity
    
    def set_telemetry(self, telemetry: bool):
        """Set whether to show telemetry information."""
        self.telemetry = telemetry
    
    # Module-level flag to avoid duplicate banner prints across different components/instances
    # (e.g., interactive shell + scan services in the same process)
    
    
    def print_branding(self):
        """Display the Levox branding once per process."""
        global _BRANDING_PRINTED
        try:
            if _BRANDING_PRINTED:
                return
        except NameError:
            _BRANDING_PRINTED = False
        if _BRANDING_PRINTED:
            return
        logo = """
┌────────────────────────────────────────────────┐
│                                                │
│                                                │
│   ██      ███████ ██    ██  ██████  ██   ██    │
│   ██      ██      ██    ██ ██    ██  ██ ██     │
│   ██      █████   ██    ██ ██    ██   ███      │
│   ██      ██       ██  ██  ██    ██  ██ ██     │ 
│   ███████ ███████   ████    ██████  ██   ██    │
│                                                │
│                  Beta Ready                    │
│                                                │
│                                                │
└────────────────────────────────────────────────┘
"""
        
        self.console.print(logo, style="bold blue")
        
        tagline = Text("🔒 Secure • 🚀 Fast • 🎯 Accurate • 🧪 Beta-Ready", style="bold cyan")
        self.console.print(Align.center(tagline))
        
        version_info = Text("Version 0.9.0 Beta", style="dim")
        self.console.print(Align.center(version_info))
        
        # Show license information
        license_info = self._get_license_display_info()
        if license_info:
            license_text = Text(license_info, style="bold yellow")
            self.console.print(Align.center(license_text))
        
        _BRANDING_PRINTED = True
    
    def show_scan_progress(self, total_files: int, description: str = "🔍 Scanning files..."):
        """Show beautiful scan progress with live updates."""
        progress = Progress(
            SpinnerColumn(style="green"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bright_green"),
            TaskProgressColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
            expand=True
        )
        
        with progress:
            task = progress.add_task(description, total=total_files)
            return task, progress
    
    def update_progress(self, task, progress, current_file: int, total_files: int, filename: str = None):
        """Update the progress bar with current file information."""
        if filename:
            progress.update(task, description=f"🔍 Scanning {filename} ({current_file}/{total_files})")
        else:
            progress.update(task, description=f"🔍 Scanning file {current_file}/{total_files}")
        progress.update(task, advance=1)
    
    def show_scan_summary(self, results: DetectionResult, scan_time: float, 
                          license_tier: str, report_formats: Optional[List[str]] = None):
        """Display a beautiful scan summary with key findings."""
        total_matches = sum(len(file_result.matches) for file_result in results.file_results)
        total_files = len(results.file_results)
        
        # Determine summary style based on findings
        if total_matches > 0:
            summary_text = f"[red]⚠️  Found {total_matches} potential PII violations in {total_files} files[/red]"
            panel_style = "red"
        else:
            summary_text = f"[green]✅ No PII violations found in {total_files} files[/green]"
            panel_style = "green"
        
        # Add report generation info if reports were requested
        if report_formats:
            summary_text += f"\n[dim]📄 Reports generated: {', '.join(report_formats).upper()}[/dim]"
        
        summary_panel = Panel(
            f"{summary_text}\n"
            f"[dim]Scan time: {scan_time:.2f}s | License: {license_tier}[/dim]",
            title="📊 Scan Summary",
            border_style=panel_style,
            padding=(1, 2)
        )
        
        self.console.print(summary_panel)
        self.console.print()
    
    def display_top_10_issues(self, results: DetectionResult):
        """Display the top 10 most critical issues in a beautiful table."""
        # Convert to structured issues and sort by severity
        issues = self._convert_to_structured_issues(results)
        
        if not issues:
            return
        
        # Take top 10 issues
        top_issues = sorted(issues)[:10]
        
        # Create beautiful table
        table = Table(
            title="🚨 Top 10 Critical Issues",
            show_header=True,
            header_style="bold red",
            border_style="red",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        
        table.add_column("Severity", style="bold", width=10)
        table.add_column("File", style="cyan", width=30)
        table.add_column("Line", justify="right", width=6)
        table.add_column("Pattern", style="yellow", width=20)
        table.add_column("Description", style="white", width=50)
        table.add_column("Confidence", justify="right", width=12)
        
        for issue in top_issues:
            # Color-code severity
            severity_style = {
                'CRITICAL': 'bold red',
                'HIGH': 'red',
                'MEDIUM': 'yellow',
                'LOW': 'green'
            }.get(issue.severity, 'white')
            
            # Truncate file path for display
            file_display = Path(issue.file).name
            if len(file_display) > 28:
                file_display = "..." + file_display[-25:]
            
            # Truncate description for display
            desc_display = issue.description
            if len(desc_display) > 47:
                desc_display = desc_display[:44] + "..."
            
            table.add_row(
                f"[{severity_style}]{issue.severity}[/{severity_style}]",
                file_display,
                str(issue.line),
                issue.pattern_name,
                desc_display,
                f"{issue.confidence:.1%}"
            )
        
        self.console.print(table)
        self.console.print()
        
        # Show pagination info if there are more issues
        if len(issues) > 10:
            remaining = len(issues) - 10
            self.console.print(
                f"[dim]📄 Showing top 10 of {len(issues)} total issues. "
                f"Use --full-report for complete details.[/dim]"
            )
            self.console.print()
    
    def display_compliance_alerts(self, compliance_data: Dict[str, Any], alert_threshold: str = 'low'):
        """Display compliance alerts after scan summary."""
        if not compliance_data or 'alerts' not in compliance_data:
            return
        
        alerts = compliance_data['alerts']
        score = compliance_data.get('score')
        
        # Filter by threshold
        threshold_map = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        severity_values = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        min_severity = threshold_map.get(alert_threshold, 0)
        
        filtered_alerts = [a for a in alerts if severity_values.get(a.severity.value, 0) >= min_severity]
        
        if not filtered_alerts:
            return
        
        # Display compliance section
        self.console.print()
        self.console.print(Panel(
            f"[bold red]🔴 COMPLIANCE ALERTS ({len(filtered_alerts)} violations detected)[/bold red]\n"
            f"[dim]Frameworks: {', '.join(compliance_data.get('frameworks', ['GDPR']))}[/dim]",
            border_style="red",
            padding=(1, 2)
        ))
        
        # Show top 5 critical/high alerts
        for alert in filtered_alerts[:5]:
            self.show_compliance_alert(alert)
        
        # Show compliance score
        if score:
            grade_color = {'A+': 'green', 'A': 'green', 'B': 'yellow', 'C': 'yellow', 'D': 'red', 'F': 'red'}
            color = grade_color.get(score.grade, 'white')
            
            self.console.print()
            self.console.print(Panel(
                f"[bold]Compliance Score: {score.score:.1f}/100 (Grade: [{color}]{score.grade}[/{color}])[/bold]\n"
                f"[dim]🏭 Industry Benchmark: {score.percentile}th percentile for {score.industry}[/dim]",
                title="📊 Compliance Assessment",
                border_style=color,
                padding=(1, 2)
            ))
    
    def display_full_results(self, results: DetectionResult, output_format: str = 'table'):
        """Display full scan results in the specified format."""
        if output_format == 'json':
            self._display_json_results(results)
        elif output_format == 'sarif':
            self._display_sarif_results(results)
        elif output_format == 'table':
            self._display_full_table_results(results)
        else:
            self._display_full_table_results(results)
    
    def _display_json_results(self, results: DetectionResult):
        """Display results in JSON format."""
        json_output = self._convert_to_json(results)
        self.console.print(json.dumps(json_output, indent=2))
    
    def _display_sarif_results(self, results: DetectionResult):
        """Display results in SARIF format."""
        sarif_output = self._convert_to_sarif(results)
        self.console.print(json.dumps(sarif_output, indent=2))
    
    def _display_full_table_results(self, results: DetectionResult):
        """Display all results in a comprehensive table format."""
        issues = self._convert_to_structured_issues(results)
        
        if not issues:
            self.console.print("[green]✅ No issues found to display[/green]")
            return
        
        # Group issues by file for better organization
        issues_by_file = {}
        for issue in issues:
            file_path = issue.file
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        # Display each file's issues
        for file_path, file_issues in issues_by_file.items():
            file_name = Path(file_path).name
            
            # Create file header
            file_panel = Panel(
                f"[bold cyan]{file_name}[/bold cyan]\n"
                f"[dim]{file_path}[/dim]",
                title=f"📁 File: {file_name}",
                border_style="blue",
                padding=(0, 1)
            )
            self.console.print(file_panel)
            
            # Create issues table for this file
            table = Table(
                show_header=True,
                header_style="bold blue",
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 1)
            )
            
            table.add_column("Line", justify="right", width=6)
            table.add_column("Severity", style="bold", width=10)
            table.add_column("Pattern", style="yellow", width=20)
            table.add_column("Description", style="white", width=60)
            table.add_column("Confidence", justify="right", width=12)
            
            for issue in sorted(file_issues):
                severity_style = {
                    'CRITICAL': 'bold red',
                    'HIGH': 'red',
                    'MEDIUM': 'yellow',
                    'LOW': 'green'
                }.get(issue.severity, 'white')
                
                table.add_row(
                    str(issue.line),
                    f"[{severity_style}]{issue.severity}[/{severity_style}]",
                    issue.pattern_name,
                    issue.description,
                    f"{issue.confidence:.1%}"
                )
            
            self.console.print(table)
            self.console.print()
    
    def show_telemetry_info(self, results: DetectionResult, scan_time: float):
        """Show detailed telemetry information if enabled."""
        if not self.telemetry:
            return
        
        # Detection level activity
        level_stats = {}
        for file_result in results.file_results:
            for match in file_result.matches:
                level = match.metadata.get('detection_level', 'unknown')
                if level not in level_stats:
                    level_stats[level] = 0
                level_stats[level] += 1
        
        if level_stats:
            self.console.print("[bold cyan]🔧 Detection Level Activity[/bold cyan]")
            self.console.print("─" * 50)
            
            activity_table = Table(
                show_header=True,
                header_style="bold magenta",
                box=box.ROUNDED,
                padding=(0, 1)
            )
            activity_table.add_column("Detection Level", style="cyan")
            activity_table.add_column("Matches Found", justify="right", style="green")
            activity_table.add_column("Status", justify="center", style="bold")
            
            for level, count in level_stats.items():
                activity_table.add_row(level.title(), str(count), "[green]✅ Active[/green]")
            
            self.console.print(activity_table)
            self.console.print()
        
        # Performance metrics
        if hasattr(results, 'metadata') and results.metadata:
            perf_table = Table(
                title="⚡ Performance Metrics",
                show_header=True,
                header_style="bold green",
                box=box.ROUNDED,
                padding=(0, 1)
            )
            perf_table.add_column("Metric", style="cyan")
            perf_table.add_column("Value", justify="right", style="white")
            
            perf_table.add_row("Total Scan Time", f"{scan_time:.3f}s")
            perf_table.add_row("Files Processed", str(len(results.file_results)))
            perf_table.add_row("Average Time per File", f"{scan_time/len(results.file_results):.3f}s")
            
            self.console.print(perf_table)
            self.console.print()
    
    def _convert_to_structured_issues(self, results: DetectionResult) -> List[StructuredIssue]:
        """Convert detection results to structured issues for display and reporting."""
        issues = []
        
        for file_result in results.file_results:
            for match in file_result.matches:
                # Determine severity based on risk level and confidence
                risk_value = getattr(match.risk_level, 'value', str(match.risk_level)).upper()
                confidence = match.confidence
                
                # Enhanced severity scoring using confidence and context
                severity = self._calculate_severity(match, risk_value, confidence)
                
                # Generate clear, actionable description
                description = self._generate_clear_description(match)
                
                # Generate remediation advice
                remediation = self._generate_remediation_advice(match)
                
                # Determine category
                category = self._determine_category(match)
                
                issue = StructuredIssue(
                    file=str(file_result.file_path),
                    line=match.line_number,
                    severity=severity,
                    description=description,
                    remediation=remediation,
                    category=category,
                    confidence=confidence,
                    pattern_name=match.pattern_name,
                    matched_text=match.matched_text,
                    detection_level=match.metadata.get('detection_level', 'unknown'),
                    risk_level=risk_value,
                    metadata=match.metadata
                )
                issues.append(issue)
        
        return sorted(issues)
    
    def _calculate_severity(self, match: DetectionMatch, risk_value: str, confidence: float) -> str:
        """Calculate severity based on risk level, confidence, and context."""
        metadata = match.metadata
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
        
        # Adjust based on context
        if metadata.get('in_log_statement', False):
            base_severity += 1
        if metadata.get('in_config_file', False):
            base_severity += 1
        
        # Clamp to valid range
        base_severity = max(1, min(4, base_severity))
        
        severity_map = {4: 'CRITICAL', 3: 'HIGH', 2: 'MEDIUM', 1: 'LOW'}
        return severity_map[base_severity]
    
    def _generate_clear_description(self, match: DetectionMatch) -> str:
        """Generate a clear, actionable description of the issue."""
        pattern_name = match.pattern_name
        matched_text = match.matched_text
        # Secret validation enrichment badge
        badge = ""
        status = match.metadata.get('secret_validation_status') if isinstance(match.metadata, dict) else None
        if status == 'confirmed_active':
            badge = " [bold green](confirmed)[/bold green]"
        elif status == 'invalid':
            badge = " [yellow](invalid)[/yellow]"
        elif status == 'incomplete':
            badge = " [dim](incomplete)[/dim]"
        
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
        
        return descriptions.get(pattern_name, f"Potential {pattern_name.replace('_', ' ')}: {matched_text}{badge}")
    
    def _generate_remediation_advice(self, match: DetectionMatch) -> str:
        """Generate remediation advice for the detected issue."""
        pattern_name = match.pattern_name
        
        advice = {
            'hardcoded_password': "Move password to environment variables or secure configuration files",
            'api_key': "Store API keys in environment variables or use a secrets management service",
            'email_address': "Consider if this email needs to be in the code or can be externalized",
            'credit_card': "Remove credit card data from code. Use PCI-compliant payment processors",
            'ssn': "Remove SSN from code. Use secure identity verification services",
            'phone_number': "Consider if phone numbers need to be in source code",
            'ip_address': "Use configuration files or environment variables for IP addresses",
            'database_url': "Move database credentials to environment variables or secure config",
            'aws_access_key': "Use IAM roles, environment variables, or AWS Secrets Manager",
            'private_key': "Store private keys in secure key management systems, not in code"
        }
        
        return advice.get(pattern_name, "Review this data and determine if it should be externalized")
    
    def _determine_category(self, match: DetectionMatch) -> str:
        """Determine the category of the detected issue."""
        pattern_name = match.pattern_name.lower()
        
        if any(word in pattern_name for word in ['password', 'secret', 'key', 'token']):
            return 'Credentials & Secrets'
        elif any(word in pattern_name for word in ['email', 'phone', 'ssn', 'credit']):
            return 'Personal Information'
        elif any(word in pattern_name for word in ['ip', 'url', 'hostname']):
            return 'Network Information'
        elif any(word in pattern_name for word in ['database', 'connection']):
            return 'Database & Connections'
        else:
            return 'Other Sensitive Data'
    
    def _convert_to_json(self, results: DetectionResult) -> Dict[str, Any]:
        """Convert results to JSON format for output."""
        total_matches = sum(len(file_result.matches) for file_result in results.file_results)
        total_files = len(results.file_results)
        
        # Safely convert scan_metadata to JSON-serializable format
        safe_scan_metadata = None
        if hasattr(results, 'scan_metadata') and results.scan_metadata:
            safe_scan_metadata = self._make_json_safe(results.scan_metadata)
        
        return {
            'scan_summary': {
                'total_files': total_files,
                'total_matches': total_matches,
                'scan_path': str(results.scan_path) if hasattr(results, 'scan_path') else None,
                'scan_timestamp': datetime.now().isoformat(),
                'filtering_applied': True,  # Indicate that filtering has been applied
                'confidence_threshold': getattr(results, 'confidence_threshold', 0.75)
            },
            'scan_metadata': safe_scan_metadata,
            'results': [
                {
                    'file_path': str(file_result.file_path),
                    'matches': [
                        {
                            'pattern_name': match.pattern_name,
                            'matched_text': match.matched_text,
                            'line_number': match.line_number,
                            'column_start': match.column_start,
                            'column_end': match.column_end,
                            'confidence': match.confidence,
                            'risk_level': match.risk_level.value if hasattr(match.risk_level, 'value') else str(match.risk_level),
                            'detection_level': match.metadata.get('detection_level', 'unknown'),
                            'metadata': self._make_json_safe(match.metadata)
                        }
                        for match in file_result.matches
                    ]
                }
                for file_result in results.file_results
            ]
        }
    
    def _make_json_safe(self, obj: Any) -> Any:
        """Recursively convert objects to JSON-safe format."""
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_safe(item) for item in obj]
        elif isinstance(obj, dict):
            return {str(key): self._make_json_safe(value) for key, value in obj.items()}
        elif hasattr(obj, '__dict__'):
            # Convert objects with __dict__ to string representation
            return str(obj)
        else:
            # For any other type, convert to string
            return str(obj)
    
    def _convert_to_sarif(self, results: DetectionResult) -> Dict[str, Any]:
        """Convert results to SARIF format for output."""
        return {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "Levox",
                        "version": "0.9.0",
                        "informationUri": "https://github.com/levox/levox",
                        "rules": [
                            {
                                "id": match.pattern_name,
                                "name": match.pattern_name,
                                "shortDescription": {"text": f"PII Detection: {match.pattern_name}"},
                                "fullDescription": {"text": f"Detected potential PII of type {match.pattern_name}"}
                            }
                            for file_result in results.file_results
                            for match in file_result.matches
                        ]
                    }
                },
                "results": [
                    {
                        "ruleId": match.pattern_name,
                        "level": "warning" if match.confidence > 0.7 else "note",
                        "message": {"text": f"Potential PII detected: {match.matched_text}"},
                        "locations": [{
                            "physicalLocation": {
                                "artifactLocation": {"uri": str(file_result.file_path)},
                                "region": {
                                    "startLine": match.line_number,
                                    "startColumn": match.column_start,
                                    "endColumn": match.column_end
                                }
                            }
                        }],
                        "properties": {
                            "confidence": match.confidence,
                            "detection_level": match.metadata.get('detection_level', 'unknown')
                        }
                    }
                    for file_result in results.file_results
                    for match in file_result.matches
                ]
            }]
        }
    
    def print_error(self, message: str, details: str = None):
        """Print an error message with optional details."""
        error_panel = Panel(
            f"[red]{message}[/red]",
            title="❌ Error",
            border_style="red",
            padding=(1, 2)
        )
        self.console.print(error_panel)
        
        if details and self.verbosity in ['verbose', 'debug']:
            self.console.print(f"[dim]{details}[/dim]")
    
    def print_warning(self, message: str):
        """Print a warning message."""
        warning_panel = Panel(
            f"[yellow]{message}[/yellow]",
            title="⚠️ Warning",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(warning_panel)
    
    def print_success(self, message: str):
        """Print a success message."""
        success_panel = Panel(
            f"[green]{message}[/green]",
            title="✅ Success",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(success_panel)
    
    def print_info(self, message: str):
        """Print an informational message."""
        info_panel = Panel(
            f"[cyan]{message}[/cyan]",
            title="ℹ️ Info",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(info_panel)
    
    def _get_license_display_info(self) -> Optional[str]:
        """Get license information for display in branding."""
        try:
            from ..core.license_client import get_license_client
            
            client = get_license_client()
            license_info = client.get_license_info()
            
            if license_info and license_info.is_valid:
                tier = license_info.tier.value.title()
                expiry = license_info.expires_at.strftime('%Y-%m-%d')
                return f"🔑 License: {tier} (expires {expiry}) | Type 'license --register' to upgrade"
            else:
                return "🔓 Demo Mode | Type 'license --register' to get a license"
        except Exception:
            return "🔓 Demo Mode | Type 'license --register' to get a license"
    
    def show_compliance_alert(self, alert: ComplianceAlert, show_context: bool = True):
        """
        Display a compliance alert with rich formatting.
        
        Args:
            alert: ComplianceAlert to display
            show_context: Whether to show detailed context
        """
        # Determine alert color and icon based on severity
        severity_config = {
            AlertSeverity.CRITICAL: {"color": "red", "icon": "🔴", "style": "bold red"},
            AlertSeverity.HIGH: {"color": "orange3", "icon": "🟠", "style": "bold orange3"},
            AlertSeverity.MEDIUM: {"color": "yellow", "icon": "🟡", "style": "bold yellow"},
            AlertSeverity.LOW: {"color": "blue", "icon": "🔵", "style": "bold blue"},
            AlertSeverity.INFO: {"color": "cyan", "icon": "ℹ️", "style": "bold cyan"}
        }
        
        config = severity_config.get(alert.severity, severity_config[AlertSeverity.INFO])
        
        # Create alert header
        header_text = Text()
        header_text.append(f"{config['icon']} ", style=config['style'])
        header_text.append(f"{alert.severity.value.upper()}: ", style=config['style'])
        header_text.append(f"{alert.title}", style="bold white")
        
        # Create alert content
        content_lines = []
        
        # Article reference
        if alert.article_ref:
            content_lines.append(f"📋 {alert.article_ref}")
        
        # Description
        if alert.description:
            content_lines.append(f"📝 {alert.description}")
        
        # File and line information
        file_info = f"📁 {Path(alert.file_path).name}"
        if alert.line_number > 0:
            file_info += f":{alert.line_number}"
        content_lines.append(file_info)
        
        # Context (if requested and available)
        if show_context and alert.context:
            content_lines.append(f"🔍 {alert.context}")
        
        # Matched text (if available and not too long)
        if alert.matched_text and len(alert.matched_text) <= 200:
            # Truncate if too long
            text = alert.matched_text
            if len(text) > 100:
                text = text[:97] + "..."
            content_lines.append(f"💻 {text}")
        
        # Remediation
        if alert.remediation:
            content_lines.append(f"🔧 {alert.remediation}")
        
        # Confidence and metadata
        if alert.confidence > 0:
            content_lines.append(f"🎯 Confidence: {alert.confidence:.1%}")
        
        # Create panel content
        panel_content = "\n".join(content_lines)
        
        # Create alert panel
        alert_panel = Panel(
            panel_content,
            title=header_text,
            border_style=config['color'],
            padding=(1, 2),
            expand=False
        )
        
        self.console.print(alert_panel)
    
    def show_compliance_summary(self, alerts: List[ComplianceAlert], scan_duration: float):
        """
        Display a compliance summary at the end of a scan.
        
        Args:
            alerts: List of compliance alerts generated
            scan_duration: Duration of the scan in seconds
        """
        if not alerts:
            # No compliance issues found
            success_panel = Panel(
                "✅ No compliance violations detected\n"
                "Your codebase appears to be compliant with current regulations.",
                title="🎉 Compliance Check Complete",
                border_style="green",
                padding=(1, 2)
            )
            self.console.print()
            self.console.print(success_panel)
            return
        
        # Count alerts by severity
        severity_counts = {}
        for alert in alerts:
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Create summary table
        summary_table = Table(show_header=True, box=box.ROUNDED)
        summary_table.add_column("Severity", style="bold", no_wrap=True)
        summary_table.add_column("Count", justify="center")
        summary_table.add_column("Icon", justify="center")
        
        # Add rows for each severity level
        severity_order = ['critical', 'high', 'medium', 'low', 'info']
        severity_icons = {
            'critical': '🔴',
            'high': '🟠', 
            'medium': '🟡',
            'low': '🔵',
            'info': 'ℹ️'
        }
        
        total_alerts = 0
        for severity in severity_order:
            count = severity_counts.get(severity, 0)
            if count > 0:
                summary_table.add_row(
                    severity.upper(),
                    str(count),
                    severity_icons[severity]
                )
                total_alerts += count
        
        # Create summary content
        summary_content = f"""
📊 Compliance Scan Summary
├─ Total Alerts: {total_alerts}
├─ Scan Duration: {scan_duration:.2f}s
└─ Frameworks Checked: GDPR, CCPA

{summary_table}
"""
        
        # Determine panel style based on highest severity
        highest_severity = None
        for severity in severity_order:
            if severity_counts.get(severity, 0) > 0:
                highest_severity = severity
                break
        
        panel_style = {
            'critical': 'red',
            'high': 'orange3',
            'medium': 'yellow',
            'low': 'blue',
            'info': 'cyan'
        }.get(highest_severity, 'white')
        
        # Create summary panel
        summary_panel = Panel(
            summary_content,
            title="📋 Compliance Summary",
            border_style=panel_style,
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(summary_panel)
        
        # Add recommendations if there are critical/high issues
        critical_high_count = severity_counts.get('critical', 0) + severity_counts.get('high', 0)
        if critical_high_count > 0:
            self.console.print()
            self._show_compliance_recommendations(critical_high_count)
    
    def _show_compliance_recommendations(self, critical_high_count: int):
        """Show compliance recommendations for critical/high issues."""
        recommendations = [
            "🔒 Review and fix all CRITICAL and HIGH severity violations immediately",
            "📋 Ensure all data processing has proper lawful basis (GDPR Article 6)",
            "🛡️ Implement appropriate technical measures for data security (GDPR Article 32)",
            "🗑️ Verify data deletion mechanisms are complete (GDPR Article 17)",
            "📤 Check DSAR (Data Subject Access Request) implementation (GDPR Article 15)",
            "🌍 Review cross-border data transfers for adequate safeguards (GDPR Articles 44-49)"
        ]
        
        if critical_high_count >= 5:
            recommendations.insert(0, "⚠️ Consider conducting a Data Protection Impact Assessment (DPIA)")
        
        recommendations_text = "\n".join(recommendations)
        
        recommendations_panel = Panel(
            recommendations_text,
            title="💡 Compliance Recommendations",
            border_style="yellow",
            padding=(1, 2)
        )
        
        self.console.print(recommendations_panel)
    
    def show_compliance_progress(self, current_file: str, total_files: int, current_file_num: int):
        """
        Show compliance scanning progress.
        
        Args:
            current_file: Currently scanning file
            total_files: Total number of files to scan
            current_file_num: Current file number (1-based)
        """
        if self.verbosity == 'summary':
            return
        
        progress_text = f"🔍 Scanning for compliance violations: {Path(current_file).name} ({current_file_num}/{total_files})"
        
        # Use a simple print for progress to avoid cluttering
        self.console.print(f"[dim]{progress_text}[/dim]", end="\r")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
