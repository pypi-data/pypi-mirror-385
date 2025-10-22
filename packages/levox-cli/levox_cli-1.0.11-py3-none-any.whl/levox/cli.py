"""
Enhanced CLI interface for Levox with beautiful, professional UI/UX design.
"""

import os
import sys
import json
import yaml
import time
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, NamedTuple
from datetime import datetime
import uuid
from dataclasses import dataclass

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.traceback import install
from rich import box
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner

from .core.config import Config, load_default_config, LicenseTier
from .core.engine import DetectionEngine
from .core.exceptions import LevoxException, DetectionError, ConfigurationError
from .core.feedback import FeedbackCollector
from .models.detection_result import DetectionResult, DetectionMatch
from .utils.performance import PerformanceMonitor
from .parsers import get_supported_languages, TREE_SITTER_AVAILABLE

# Configure logging
import logging

def setup_logging(verbose: bool = False):
    """Setup logging configuration with reduced noise."""
    # Create logs directory
    log_dir = Path.home() / ".levox" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(log_dir / "latest.log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler for user-facing messages only
    if verbose:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    else:
        # Only show warnings and errors in console by default
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('tree_sitter').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    # Suppress verbose Levox internal loggers in non-verbose mode
    if not verbose:
        logging.getLogger('levox.engine').setLevel(logging.WARNING)
        logging.getLogger('levox.detection').setLevel(logging.WARNING)
        logging.getLogger('levox.parsers').setLevel(logging.WARNING)
        logging.getLogger('levox.compliance').setLevel(logging.WARNING)

# Configure Windows console for UTF-8 to avoid UnicodeEncodeError
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Initialize rich console (disable emoji rendering on Windows for safety)
console = Console(emoji=(sys.platform != 'win32'))

# Exit codes
EXIT_SUCCESS = 0
EXIT_VIOLATIONS_FOUND = 1
EXIT_RUNTIME_ERROR = 2
EXIT_CONFIG_ERROR = 3
EXIT_DEPENDENCY_MISSING = 4

# Beautiful ASCII Art Logo
LEVOX_LOGO = """
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

# Structured Issue Model for CLI Output
@dataclass
class StructuredIssue:
    """Structured representation of a detection issue for CLI display and reporting."""
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

class LevoxCLI:
    """Enhanced Levox CLI with beautiful UI/UX and professional design."""
    
    def __init__(self):
        self.config = None
        self.engine = None
        self.feedback_collector = None
        self.last_scan_results = None  # Store last scan results for reporting
        self.last_scan_path = None
        self.last_scan_time = None
        self.last_license_tier = None
        
    def print_branding(self):
        """Display the beautiful Levox branding."""
        console.print(LEVOX_LOGO, style="bold blue")
        
        # Tagline with gradient effect
        tagline = Text("🔒 Secure • 🚀 Fast • 🎯 Accurate • 🧪 Beta-Ready", style="bold cyan")
        console.print(Align.center(tagline))
        
        # Version info
        version_info = Text("Version 0.9.0 Beta", style="dim")
        console.print(Align.center(version_info))
    
    def show_scan_progress(self, total_files: int):
        """Show beautiful scan progress with live updates."""
        progress = Progress(
            SpinnerColumn(style="green"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bright_green"),
            TaskProgressColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            expand=True
        )
        
        with progress:
            task = progress.add_task("🔍 Scanning files...", total=total_files)
            
            # Simulate progress (this would be updated by the actual scan)
            for i in range(total_files):
                time.sleep(0.1)  # Simulate work
                progress.update(task, advance=1)
                
                # Update description with current file
                progress.update(task, description=f"🔍 Scanning file {i+1}/{total_files}")
        
        console.print("✅ Scan completed successfully!", style="bold green")
    
    def validate_dependencies(self) -> Dict[str, Any]:
        """Validate required dependencies and return capability status."""
        capabilities = {
            'tree_sitter_available': TREE_SITTER_AVAILABLE,
            'languages': get_supported_languages(),
            'ml_libraries': self._check_ml_libraries(),
            'optional_libraries': self._check_optional_libraries()
        }
        
        return capabilities
    
    def _check_ml_libraries(self) -> Dict[str, bool]:
        """Check ML library availability."""
        ml_status = {}
        
        try:
            import xgboost
            ml_status['xgboost'] = True
        except ImportError:
            ml_status['xgboost'] = False
        
        try:
            import sklearn
            ml_status['scikit_learn'] = True
        except ImportError:
            ml_status['scikit_learn'] = False
        
        return ml_status
    
    def _check_optional_libraries(self) -> Dict[str, bool]:
        """Check optional library availability."""
        optional_status = {}
        
        try:
            import watchdog
            optional_status['watchdog'] = True
        except ImportError:
            optional_status['watchdog'] = False
        
        try:
            import sqlite3
            optional_status['sqlite3'] = True
        except ImportError:
            optional_status['sqlite3'] = False
        
        return optional_status
    
    def _convert_to_structured_issues(self, results: DetectionResult) -> List[StructuredIssue]:
        """Convert detection results to structured issues for CLI display and reporting."""
        issues = []
        
        for file_result in results.file_results:
            for match in file_result.matches:
                # Determine severity based on risk level and confidence
                risk_value = getattr(match.risk_level, 'value', str(match.risk_level)).upper()
                confidence = match.confidence
                
                # Enhanced severity scoring using confidence and context
                severity = self._calculate_severity(match, risk_value, confidence)
                
                # Generate clear, actionable description based on pattern type and context
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
        
        return sorted(issues)  # Sort by severity and line number
    
    def _calculate_severity(self, match: DetectionMatch, risk_value: str, confidence: float) -> str:
        """Calculate severity based on risk level, confidence, and context."""
        metadata = match.metadata
        pattern_name = match.pattern_name.lower()
        
        # Base severity from risk level
        base_severity = {
            'CRITICAL': 'CRITICAL',
            'HIGH': 'HIGH',
            'MEDIUM': 'MEDIUM',
            'LOW': 'LOW'
        }.get(risk_value, 'MEDIUM')
        
        # Adjust severity based on confidence
        if confidence < 0.3:
            # Low confidence findings get reduced severity
            if base_severity == 'HIGH':
                base_severity = 'MEDIUM'
            elif base_severity == 'MEDIUM':
                base_severity = 'LOW'
        
        # Context-based adjustments
        if metadata.get('test_context'):
            # Test files get reduced severity
            if base_severity == 'HIGH':
                base_severity = 'MEDIUM'
            elif base_severity == 'MEDIUM':
                base_severity = 'LOW'
        
        if metadata.get('is_fixture') or metadata.get('is_mock'):
            # Test fixtures and mocks get reduced severity
            if base_severity in ['HIGH', 'MEDIUM']:
                base_severity = 'LOW'
        
        # Enhanced AST analysis patterns get context-based severity
        if 'enhanced_f_string_analysis' in pattern_name or 'enhanced_template_literal_analysis' in pattern_name:
            # These are often false positives, so reduce severity
            if base_severity == 'HIGH':
                base_severity = 'MEDIUM'
            elif base_severity == 'MEDIUM':
                base_severity = 'LOW'
        
        if 'parser_string_analysis' in pattern_name or 'parser_variable_analysis' in pattern_name:
            # Parser-level findings are often less critical
            if base_severity == 'HIGH':
                base_severity = 'MEDIUM'
        
        # Dataflow findings get higher severity if they involve sensitive sinks
        if 'dataflow' in pattern_name:
            sink_type = metadata.get('sink_type', '')
            if sink_type in ['logging', 'console', 'file', 'network']:
                # Sensitive sinks get higher severity
                if base_severity == 'MEDIUM':
                    base_severity = 'HIGH'
            else:
                # Less sensitive sinks get lower severity
                if base_severity == 'HIGH':
                    base_severity = 'MEDIUM'
        
        return base_severity
    
    def _generate_clear_description(self, match: DetectionMatch) -> str:
        """Generate clear, actionable descriptions instead of vague technical names."""
        pattern_name = match.pattern_name.lower()
        metadata = match.metadata
        
        # Handle enhanced AST analysis patterns with clear descriptions
        if 'enhanced_f_string_analysis' in pattern_name:
            var_name = metadata.get('variable_name', 'variable')
            return f"F-string contains potentially sensitive variable '{var_name}' - review for PII exposure"
        
        elif 'enhanced_template_literal_analysis' in pattern_name:
            var_name = metadata.get('variable_name', 'variable')
            return f"Template literal contains potentially sensitive variable '{var_name}' - review for PII exposure"
        
        elif 'enhanced_logging_analysis' in pattern_name:
            pii_types = metadata.get('pii_types', ['data'])
            return f"Logging statement may expose {', '.join(pii_types)} - review for PII in logs"
        
        elif 'parser_string_analysis' in pattern_name:
            return "String literal may contain sensitive data - review for hardcoded PII"
        
        elif 'parser_variable_analysis' in pattern_name:
            return "Variable assignment may contain sensitive data - review for hardcoded PII"
        
        elif 'parser_comment_analysis' in pattern_name:
            return "Comment may contain sensitive information - review for PII in comments"
        
        elif 'dataflow' in pattern_name:
            source_type = metadata.get('source_type', 'input')
            sink_type = metadata.get('sink_type', 'output')
            return f"Data flow detected from {source_type} to {sink_type} - review for PII exposure"
        
        # Handle standard PII patterns
        elif 'email' in pattern_name:
            return "Email address detected - review if hardcoded email is necessary"
        
        elif 'ssn' in pattern_name or 'social_security' in pattern_name:
            return "Social Security Number detected - remove from code immediately"
        
        elif 'credit_card' in pattern_name:
            return "Credit card number detected - remove from code immediately"
        
        elif 'password' in pattern_name:
            return "Password detected - use environment variables or secure vaults"
        
        elif 'api_key' in pattern_name:
            return "API key detected - use environment variables or secure storage"
        
        elif 'phone' in pattern_name:
            return "Phone number detected - review if hardcoded number is necessary"
        
        elif 'ip_address' in pattern_name:
            return "IP address detected - review if hardcoded address is necessary"
        
        # Default case for unknown patterns
        else:
            # Convert technical names to readable descriptions
            readable_name = pattern_name.replace('_', ' ').title()
            return f"Potential {readable_name} detected - review for sensitive data"
    
    def _generate_remediation_advice(self, match: DetectionMatch) -> str:
        """Generate specific remediation advice based on pattern type and context."""
        pattern_name = match.pattern_name.lower()
        metadata = match.metadata
        
        # Enhanced AST analysis remediation
        if 'enhanced_f_string_analysis' in pattern_name:
            return "Review f-string usage and ensure sensitive variables are not exposed. Consider using placeholders or sanitization."
        
        elif 'enhanced_template_literal_analysis' in pattern_name:
            return "Review template literal usage and ensure sensitive variables are not exposed. Consider using placeholders or sanitization."
        
        elif 'enhanced_logging_analysis' in pattern_name:
            return "Review logging statements and remove or sanitize PII before logging. Use structured logging with sensitive data filtering."
        
        elif 'parser_string_analysis' in pattern_name:
            return "Review string literals and replace hardcoded sensitive data with environment variables or configuration files."
        
        elif 'parser_variable_analysis' in pattern_name:
            return "Review variable assignments and replace hardcoded sensitive data with environment variables or secure storage."
        
        elif 'parser_comment_analysis' in pattern_name:
            return "Review comments and remove any sensitive information. Use generic descriptions instead of actual data."
        
        elif 'dataflow' in pattern_name:
            return "Review data flow paths and implement proper input validation and output sanitization to prevent PII exposure."
        
        # Standard PII pattern remediation
        elif 'email' in pattern_name:
            return "Replace hardcoded email with environment variables, configuration files, or user input validation."
        
        elif 'ssn' in pattern_name or 'social_security' in pattern_name:
            return "Remove SSN from code immediately. Use secure storage or external identity verification services."
        
        elif 'credit_card' in pattern_name:
            return "Remove credit card numbers from code immediately. Use secure payment processing services with proper PCI compliance."
        
        elif 'password' in pattern_name:
            return "Replace hardcoded passwords with environment variables, secure vaults, or dynamic credential generation."
        
        elif 'api_key' in pattern_name:
            return "Replace hardcoded API keys with environment variables, secure storage, or dynamic credential management."
        
        elif 'phone' in pattern_name:
            return "Replace hardcoded phone numbers with user input, configuration files, or external data sources."
        
        elif 'ip_address' in pattern_name:
            return "Replace hardcoded IP addresses with configuration files, environment variables, or dynamic discovery."
        
        # Default remediation
        else:
            return "Review this data and ensure it's not sensitive information. Consider using placeholders, environment variables, or secure storage."
    
    def _determine_category(self, match: DetectionMatch) -> str:
        """Determine issue category based on pattern type and context."""
        pattern_name = match.pattern_name.lower()
        
        # Enhanced AST analysis categories
        if 'enhanced_f_string_analysis' in pattern_name or 'enhanced_template_literal_analysis' in pattern_name:
            return "Code Structure"
        
        elif 'enhanced_logging_analysis' in pattern_name:
            return "Logging & Monitoring"
        
        elif 'parser_string_analysis' in pattern_name or 'parser_variable_analysis' in pattern_name:
            return "Code Content"
        
        elif 'parser_comment_analysis' in pattern_name:
            return "Documentation"
        
        elif 'dataflow' in pattern_name:
            return "Data Flow"
        
        # Standard PII categories
        elif 'email' in pattern_name or 'phone' in pattern_name:
            return "Personal Information"
        
        elif 'ssn' in pattern_name or 'social_security' in pattern_name:
            return "Government ID"
        
        elif 'credit_card' in pattern_name:
            return "Financial Data"
        
        elif 'password' in pattern_name or 'api_key' in pattern_name:
            return "Credentials"
        
        elif 'ip_address' in pattern_name:
            return "Network Configuration"
        
        else:
            return "Other"
    
    def _save_reports(self, issues: List[StructuredIssue], scan_path: str, scan_time: float, 
                      license_tier: str, output_dir: Optional[str] = None, 
                      report_formats: Optional[List[str]] = None) -> Dict[str, str]:
        """Save comprehensive reports in multiple formats."""
        if not report_formats:
            return {}
        
        console.print(f"[dim]🔧 Starting report generation for {len(issues)} issues...[/dim]")
        
        if output_dir is None:
            output_dir = Path.cwd()
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"levox_report_{timestamp}"
        
        report_paths = {}
        
        # Generate requested report formats
        if 'json' in report_formats:
            console.print(f"[dim]🔧 Generating JSON report...[/dim]")
            json_path = output_dir / f"{base_name}.json"
            json_report = {
                'scan_info': {
                    'timestamp': datetime.now().isoformat(),
                    'scan_path': scan_path,
                    'scan_time_seconds': scan_time,
                    'license_tier': license_tier,
                    'total_issues': len(issues)
                },
                'issues': [
                    {
                        'file': issue.file,
                        'line': issue.line,
                        'severity': issue.severity,
                        'description': issue.description,
                        'remediation': issue.remediation,
                        'category': issue.category,
                        'confidence': issue.confidence,
                        'pattern_name': issue.pattern_name,
                        'matched_text': issue.matched_text[:200],  # Truncate for JSON
                        'detection_level': issue.detection_level,
                        'risk_level': issue.risk_level,
                        'metadata': issue.metadata
                    }
                    for issue in issues
                ]
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_report, f, indent=2, ensure_ascii=False)
            report_paths['json'] = str(json_path)
            console.print(f"[dim]✅ JSON report saved: {json_path}[/dim]")
        
        if 'html' in report_formats:
            console.print(f"[dim]🔧 Generating HTML report...[/dim]")
            html_path = output_dir / f"{base_name}.html"
            html_report = self._generate_enhanced_html(issues, scan_path, scan_time, license_tier)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
            report_paths['html'] = str(html_path)
            console.print(f"[dim]✅ HTML report saved: {html_path}[/dim]")
        
        if 'pdf' in report_formats:
            try:
                console.print(f"[dim]🔧 Generating PDF report...[/dim]")
                pdf_path = output_dir / f"{base_name}.pdf"
                self._generate_pdf_report(issues, scan_path, scan_time, license_tier, pdf_path)
                report_paths['pdf'] = str(pdf_path)
                console.print(f"[dim]✅ PDF report saved: {pdf_path}[/dim]")
            except Exception as e:
                console.print(f"[yellow]⚠️ PDF generation failed: {e}[/yellow]")
                report_paths['pdf'] = None
        
        if report_paths:
            console.print(f"[dim]✅ Reports generated successfully[/dim]")
        
        return report_paths
    
    def _generate_enhanced_html(self, issues: List[StructuredIssue], scan_path: str, 
                               scan_time: float, license_tier: str) -> str:
        """Generate enhanced HTML report with structured issue display."""
        
        # Count issues by severity
        severity_counts = {}
        category_counts = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Levox PII Detection Report</title>
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
            <h1>🔍 Levox PII Detection Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>License: {license_tier} | Scan time: {scan_time:.2f}s</p>
        </div>
        
        <div class="summary">
            <h2>📊 Executive Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(issues)}</div>
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
            <p><strong>Categories Found:</strong> {', '.join(category_counts.keys())}</p>
        </div>
        
        <div class="issues">
            <h2>🔍 Detailed Issues</h2>"""
        
        for issue in issues:
            severity_class = issue.severity.lower()
            severity_color_class = f"severity-{severity_class}"
            
            html += f"""
            <div class="issue-card {severity_class}">
                <div class="issue-header">
                    <h3>{issue.description}</h3>
                    <span class="severity-badge {severity_color_class}">{issue.severity}</span>
                </div>
                
                <div class="file-info">
                    <strong>File:</strong> {issue.file}:{issue.line}
                </div>
                
                <p><strong>Category:</strong> <span class="category-tag">{issue.category}</span></p>
                <p><strong>Pattern:</strong> {issue.pattern_name}</p>
                <p><strong>Confidence:</strong> {issue.confidence:.2f}</p>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {issue.confidence * 100}%"></div>
                </div>
                
                <div class="remediation">
                    <strong>💡 Remediation:</strong> {issue.remediation}
                </div>
            </div>"""
        
        html += """
        </div>
        
        <div class="footer">
            <p>Generated by Levox - Advanced PII Detection Tool</p>
            <p>For more information, visit: https://github.com/levox/levox</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_pdf_report(self, issues: List[StructuredIssue], scan_path: str, 
                            scan_time: float, license_tier: str, pdf_path: Path) -> None:
        """Generate PDF report with visualization."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.graphics.shapes import Drawing
            from reportlab.graphics.charts.piecharts import Pie
            from reportlab.graphics.charts.barcharts import VerticalBarChart
        except ImportError:
            raise ImportError("PDF generation requires reportlab: pip install reportlab")
        
        # Create PDF document
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph("🔍 Levox PII Detection Report", title_style))
        story.append(Spacer(1, 20))
        
        # Scan info
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20
        )
        story.append(Paragraph(f"<b>Scan Path:</b> {scan_path}", info_style))
        story.append(Paragraph(f"<b>Scan Time:</b> {scan_time:.2f} seconds", info_style))
        story.append(Paragraph(f"<b>License Tier:</b> {license_tier}", info_style))
        story.append(Paragraph(f"<b>Total Issues:</b> {len(issues)}", info_style))
        story.append(Spacer(1, 20))
        
        # Severity distribution chart
        severity_counts = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        if severity_counts:
            # Create pie chart
            drawing = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 100
            pie.height = 100
            pie.data = list(severity_counts.values())
            pie.labels = list(severity_counts.keys())
            pie.slices.strokeWidth = 0.5
            
            # Color scheme
            colors_list = [colors.red, colors.orange, colors.yellow, colors.green]
            for i, slice in enumerate(pie.slices):
                slice.fillColor = colors_list[i % len(colors_list)]
            
            drawing.add(pie)
            story.append(drawing)
            story.append(Spacer(1, 20))
        
        # Issues table
        if issues:
            story.append(Paragraph("<b>Top Issues by Severity:</b>", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # Table data
            table_data = [['File:Line', 'Severity', 'Description', 'Category']]
            for issue in issues[:20]:  # Top 20 issues
                table_data.append([
                    f"{Path(issue.file).name}:{issue.line}",
                    issue.severity,
                    issue.description[:50] + "..." if len(issue.description) > 50 else issue.description,
                    issue.category
                ])
            
            # Create table
            table = Table(table_data, colWidths=[1.5*inch, 0.8*inch, 2.5*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        
    def _display_top_10_issues(self, issues: List[StructuredIssue]) -> None:
        """Display top issues in beautiful, professional CLI format."""
        if not issues:
            return
        
        # Count issues by severity for summary
        severity_counts = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        # Show severity breakdown with beautiful styling
        console.print("\n[bold cyan]🚨 Issue Summary[/bold cyan]")
        console.print("─" * 50)
        
        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        for severity in severity_order:
            if severity in severity_counts:
                icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(severity, '⚪')
                count = severity_counts[severity]
                console.print(f"   {icon} {severity}: {count}")
        
        # Show top 5 issues by severity in a beautiful table
        console.print(f"\n[bold cyan]🔍 Top Issues by Severity[/bold cyan]")
        console.print("─" * 80)
        
        # Sort by severity and line number
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_issues = sorted(issues, key=lambda x: (severity_order.get(x.severity, 4), x.line))
        
        # Create beautiful issue table
        issue_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        issue_table.add_column("Severity", style="bold", width=10)
        issue_table.add_column("File:Line", style="cyan", width=20)
        issue_table.add_column("Description", style="white", width=50)
        
        # Display top 5 issues
        for i, issue in enumerate(sorted_issues[:5]):
            severity_icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(issue.severity, '⚪')
            file_display = f"{Path(issue.file).name}:{issue.line}"
            desc = issue.description[:70] + "..." if len(issue.description) > 70 else issue.description
            
            issue_table.add_row(f"{severity_icon} {issue.severity}", file_display, desc)
        
        console.print(issue_table)
        
        if len(issues) > 5:
            console.print(f"\n[dim]... and {len(issues) - 5} more issues[/dim]")
        
        console.print()  # Add spacing
        
        # Show "More Details in Report" message
        console.print(Panel(
            "[bold]📄 More Details Available[/bold]\n"
            "[dim]Run with --report json html pdf to generate comprehensive reports[/dim]",
            title="💡 Tip",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def print_capability_status(self, capabilities: Dict[str, Any], license_tier: str = 'enterprise'):
        """Print detailed capability status with beautiful styling."""
        console.print("\n[bold cyan]🔍 Levox Capability Status[/bold cyan]")
        console.print("─" * 60)
        
        # Create capability table with improved styling
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED, padding=(0, 1))
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center", style="bold")
        table.add_column("Details", style="dim", max_width=50)
        
        # Core parsing
        if capabilities['tree_sitter_available']:
            table.add_row("Tree-Sitter Parsing", "[green]✅ Active[/green]", "Multi-language AST parsing")
        else:
            table.add_row("Tree-Sitter Parsing", "[red]❌ Missing[/red]", "Install: pip install tree-sitter tree-sitter-languages")
        
        # Language support
        lang_info = capabilities['languages']
        supported_langs = [lang for lang, info in lang_info['languages'].items() if info['available']]
        if supported_langs:
            table.add_row("Language Support", "[green]✅ Active[/green]", f"Supported: {', '.join(supported_langs)}")
        else:
            table.add_row("Language Support", "[yellow]⚠️ Limited[/yellow]", "Only basic regex detection available")
        
        # Detection levels based on license
        table.add_row("Regex Detection", "[green]✅ Active[/green]", "Pattern-based PII detection")
        
        if license_tier in ['premium', 'enterprise']:
            if capabilities['tree_sitter_available']:
                table.add_row("AST Analysis", "[green]✅ Active[/green]", "Context-aware detection")
            else:
                table.add_row("AST Analysis", "[red]❌ Disabled[/red]", "Requires Tree-Sitter")
        else:
            table.add_row("AST Analysis", "[blue]🔒 Premium[/blue]", "Upgrade license for AST analysis")
        
        if license_tier == 'enterprise':
            if capabilities['tree_sitter_available']:
                table.add_row("Dataflow Analysis", "[green]✅ Active[/green]", "Taint tracking analysis")
            else:
                table.add_row("Dataflow Analysis", "[red]❌ Disabled[/red]", "Requires Tree-Sitter")
        else:
            table.add_row("Dataflow Analysis", "[blue]🔒 Enterprise[/blue]", "Upgrade license for dataflow analysis")
        
        # ML Filter (Enterprise only)
        ml_available = capabilities['ml_libraries']['xgboost'] and capabilities['ml_libraries']['scikit_learn']
        if license_tier == 'enterprise':
            if ml_available:
                table.add_row("ML False-Positive Filter", "[green]✅ Active[/green]", "XGBoost-based filtering")
            else:
                missing = []
                if not capabilities['ml_libraries']['xgboost']:
                    missing.append('xgboost')
                if not capabilities['ml_libraries']['scikit_learn']:
                    missing.append('scikit-learn')
                table.add_row("ML False-Positive Filter", "[red]❌ Disabled[/red]", f"Install: pip install {' '.join(missing)}")
        else:
            table.add_row("ML False-Positive Filter", "[blue]🔒 Enterprise[/blue]", "Upgrade license for ML filtering")
        
        # Feedback system
        if capabilities['optional_libraries']['sqlite3']:
            table.add_row("Feedback System", "[green]✅ Active[/green]", "SQLite-based feedback collection")
        else:
            table.add_row("Feedback System", "[red]❌ Disabled[/red]", "SQLite3 required")
        
        # Hot-reload
        if capabilities['optional_libraries']['watchdog']:
            table.add_row("Config Hot-Reload", "[green]✅ Active[/green]", "Automatic config updates")
        else:
            table.add_row("Config Hot-Reload", "[red]❌ Disabled[/red]", "Install: pip install watchdog")
        
        console.print(table)
        console.print()  # Add spacing
        
        # License info with improved styling
        license_panel = Panel(
            f"[bold]Current License:[/bold] {license_tier.title()}\n"
            f"[dim]Detection levels available: {self._get_available_levels(license_tier)}[/dim]",
            title="📄 License Information",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(license_panel)
        console.print()  # Add spacing
    
    def _get_available_levels(self, license_tier: str) -> str:
        """Get available detection levels for license tier."""
        if license_tier == 'enterprise':
            return "Regex, AST, Dataflow, ML Filter"
        elif license_tier == 'premium':
            return "Regex, AST"
        else:
            return "Regex"
    
    def run_scan(self, path: str, output_format: str = 'table',
                 output_file: Optional[str] = None, verbose: bool = False, telemetry: bool = False,
                 max_file_size_mb: Optional[int] = None, exclude_patterns: Optional[List[str]] = None,
                 scan_optional: bool = False, allow_fallback_parsing: bool = True, require_full_ast: bool = False,
                 report_formats: Optional[List[str]] = None, dev_mode: bool = False, verbosity: str = 'summary') -> bool:
        """Run a scan with beautiful progress indicators and professional output."""
        
        start_time = time.time()
        
        try:
            # Setup logging based on verbosity
            setup_logging(verbose)
            
            # Show beautiful branding (only in non-interactive mode)
            if not hasattr(self, '_interactive_mode') or not self._interactive_mode:
                self.print_branding()
            
            # Inform user about log file location (only in non-verbose mode)
            if not verbose:
                log_dir = Path.home() / ".levox" / "logs"
                console.print(f"[dim]📝 Detailed logs: {log_dir}/latest.log[/dim]")
                console.print()  # Add spacing
            
            # Validate dependencies first
            capabilities = self.validate_dependencies()
            
            # Get license information from license client
            try:
                from .core.license_client import get_license_client
                license_client = get_license_client()
                license_info = license_client.get_license_info()
                license_tier = license_info.tier.value
                
                console.print(f"[dim]🔑 Using license tier: {license_tier.title()}[/dim]")
                
            except Exception as e:
                console.print(f"[yellow]⚠️  Warning: Could not retrieve license information: {e}[/yellow]")
                console.print(f"[dim]🔒 Using standard tier (limited features)[/dim]")
                license_tier = 'standard'
            
            # Check for missing critical dependencies
            missing_deps = []
            if not capabilities['tree_sitter_available'] and license_tier in ['premium', 'enterprise']:
                missing_deps.append('tree-sitter tree-sitter-languages')
            
            if missing_deps:
                console.print(f"[red]❌ Missing required dependencies:[/red]")
                for dep in missing_deps:
                    console.print(f"  • pip install {dep}")
                return EXIT_DEPENDENCY_MISSING
            
            # Initialize engine with license tier
            config = self.config or load_default_config()
            config.license.tier = LicenseTier(license_tier.lower())
            
            # Configure parser settings
            config.allow_fallback_parsing = allow_fallback_parsing
            config.require_full_ast = require_full_ast
            
            # Configure file discovery settings
            config.scan_optional = scan_optional
            
            self.engine = DetectionEngine(config)
            
            # Show capability status if telemetry requested
            if telemetry:
                self.print_capability_status(capabilities, license_tier)
                console.print()
            
            # Run scan with beautiful progress tracking
            scan_path = Path(path)
            if not scan_path.exists():
                console.print(f"[red]❌ Path does not exist: {path}[/red]")
                return EXIT_CONFIG_ERROR
            
            # Beautiful scan header
            scan_header = Panel(
                f"[bold cyan]🔍 Scanning:[/bold cyan] {scan_path.absolute()}\n"
                f"[dim]License: {license_tier.title()} | Format: {output_format}[/dim]",
                title="🚀 Scan Configuration",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(scan_header)
            
            if report_formats:
                console.print(f"[dim]📄 Reports: {', '.join(report_formats).upper()}[/dim]")
            console.print()  # Add spacing
            
            # Show scan progress with spinner
            with console.status("[bold green]🔍 Scanning files...", spinner="dots"):
                results = self.engine.scan_directory(str(scan_path))
            
            # Store scan results for reporting
            self.last_scan_results = results
            self.last_scan_path = str(scan_path)
            self.last_scan_time = time.time() - start_time
            self.last_license_tier = license_tier
            
            # Process results
            total_matches = sum(len(file_result.matches) for file_result in results.file_results)
            scan_time = time.time() - start_time
            
            # Show beautiful scan completion message
            if total_matches > 0:
                completion_panel = Panel(
                    f"[bold yellow]⚠️  Scan complete: {total_matches} issues found in {len(results.file_results)} files[/bold yellow]\n"
                    f"[dim]Scan time: {scan_time:.2f}s[/dim]",
                    title="📊 Scan Results",
                    border_style="yellow",
                    padding=(1, 2)
                )
                console.print(completion_panel)
            else:
                completion_panel = Panel(
                    f"[bold green]✅ Scan complete: No issues found in {len(results.file_results)} files[/bold green]\n"
                    f"[dim]Scan time: {scan_time:.2f}s[/dim]",
                    title="🎉 Clean Scan",
                    border_style="green",
                    padding=(1, 2)
                )
                console.print(completion_panel)
            
            console.print()  # Add spacing
            
            # Display results
            self._display_results(results, output_format, capabilities, license_tier, telemetry, scan_time, report_formats)
            
            # Save to file if requested
            if output_file:
                self._save_results(results, output_file, output_format)
                console.print(f"[green]💾 Results saved to {output_file}[/green]")
            
            # Return appropriate exit code
            if total_matches > 0:
                return EXIT_VIOLATIONS_FOUND
            else:
                return EXIT_SUCCESS
                
        except ConfigurationError as e:
            console.print(f"[red]❌ Configuration Error: {e}[/red]")
            return EXIT_CONFIG_ERROR
        except DetectionError as e:
            console.print(f"[red]❌ Detection Error: {e}[/red]")
            return EXIT_RUNTIME_ERROR
        except Exception as e:
            console.print(f"[red]❌ Unexpected Error: {e}[/red]")
            if telemetry:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return EXIT_RUNTIME_ERROR

    def _display_results(self, results: DetectionResult, output_format: str, 
                        capabilities: Dict[str, Any], license_tier: str, 
                        telemetry: bool, scan_time: float, report_formats: Optional[List[str]] = None):
        """Display scan results in the specified format with beautiful styling."""
        
        total_matches = sum(len(file_result.matches) for file_result in results.file_results)
        total_files = len(results.file_results)
        
        if output_format == 'json':
            # JSON output
            json_output = {
                'scan_summary': {
                    'total_files': total_files,
                    'total_matches': total_matches,
                    'scan_time_seconds': scan_time,
                    'license_tier': license_tier
                },
                'capabilities': capabilities,
                'results': [
                    {
                        'file_path': str(file_result.file_path),
                        'matches': [
                            {
                                'pattern_name': match.pattern_name,
                                'matched_text': match.matched_text,
                                'line_number': match.line_number,
                                'confidence': match.confidence,
                                'risk_level': match.risk_level.value if hasattr(match.risk_level, 'value') else str(match.risk_level),
                                'detection_level': match.metadata.get('detection_level', 'unknown')
                            }
                            for match in file_result.matches
                        ]
                    }
                    for file_result in results.file_results
                ]
            }
            console.print(json.dumps(json_output, indent=2))
            
        elif output_format == 'sarif':
            # SARIF output
            sarif_output = self._generate_sarif(results, capabilities, license_tier)
            console.print(json.dumps(sarif_output, indent=2))
            
        elif output_format == 'html':
            # HTML output
            html_output = self._generate_html(results, capabilities, license_tier, scan_time)
            console.print(html_output)
            
        else:
            # Table output (default) - most beautiful
            self._display_table_results(results, capabilities, license_tier, telemetry, scan_time, report_formats)
    
    def _display_table_results(self, results: DetectionResult, capabilities: Dict[str, Any],
                              license_tier: str, telemetry: bool, scan_time: float,
                              report_formats: Optional[List[str]] = None):
        """Display results in beautiful table format using structured issues."""
        
        total_matches = sum(len(file_result.matches) for file_result in results.file_results)
        total_files = len(results.file_results)
        
        # Convert to structured issues
        issues = self._convert_to_structured_issues(results)
        
        # Beautiful summary panel with color coding
        if total_matches > 0:
            summary_text = f"[red]⚠️  Found {total_matches} potential PII violations in {total_files} files[/red]"
            panel_style = "red"
        else:
            summary_text = f"[green]✅ No PII violations found in {total_files} files[/green]"
            panel_style = "green"
        
        summary_panel = Panel(
            f"{summary_text}\n"
            f"[dim]Scan time: {scan_time:.2f}s | License: {license_tier}[/dim]",
            title="📊 Scan Summary",
            border_style=panel_style,
            padding=(1, 2)
        )
        console.print(summary_panel)
        console.print()  # Add spacing
        
        if total_matches > 0:
            # Save comprehensive reports only if requested
            if report_formats:
                try:
                    report_paths = self._save_reports(issues, str(results.scan_path), scan_time, license_tier, report_formats=report_formats)
                    if report_paths:
                        console.print(f"[dim]📄 Reports saved: {', '.join(report_formats).upper()}[/dim]")
                        console.print()  # Add spacing
                except Exception as e:
                    console.print(f"[yellow]⚠️ Report generation failed: {e}[/yellow]")
                    console.print()  # Add spacing
            
            # Display top 10 issues in beautiful format
            self._display_top_10_issues(issues)

            # Optional: show per-file stage timings when telemetry enabled
            if telemetry:
                console.print()  # Add spacing
                for file_result in results.file_results:
                    stage_times = file_result.metadata.get('stage_times') if hasattr(file_result, 'metadata') else None
                    if not stage_times:
                        continue
                    timings = Table(title=f"Stage timings for {file_result.file_path}", show_header=True, header_style="bold blue", box=box.ROUNDED)
                    timings.add_column("Stage", style="white")
                    timings.add_column("Time (s)", justify="right")
                    for stage_name, secs in stage_times.items():
                        timings.add_row(stage_name.title(), f"{secs:.3f}")
                    console.print(timings)
                    console.print()  # Add spacing
        
        # Show detection level activity if telemetry enabled
        if telemetry:
            self._show_detection_activity(results)
    
    def _show_detection_activity(self, results: DetectionResult):
        """Show which detection levels were active and their results with beautiful styling."""
        
        level_stats = {}
        for file_result in results.file_results:
            for match in file_result.matches:
                level = match.metadata.get('detection_level', 'unknown')
                if level not in level_stats:
                    level_stats[level] = 0
                level_stats[level] += 1
        
        if level_stats:
            console.print("\n[bold cyan]🔧 Detection Level Activity[/bold cyan]")
            console.print("─" * 50)
            
            activity_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED, padding=(0, 1))
            activity_table.add_column("Detection Level", style="cyan")
            activity_table.add_column("Matches Found", justify="right", style="green")
            activity_table.add_column("Status", justify="center", style="bold")
            
            for level, count in level_stats.items():
                activity_table.add_row(level.title(), str(count), "[green]✅ Active[/green]")
            
            console.print(activity_table)
            console.print()  # Add spacing
    
    def _generate_sarif(self, results: DetectionResult, capabilities: Dict[str, Any], license_tier: str) -> Dict[str, Any]:
        """Generate SARIF format output."""
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
                            "detection_level": match.metadata.get('detection_level', 'unknown'),
                            "license_tier": license_tier
                        }
                    }
                    for file_result in results.file_results
                    for match in file_result.matches
                ]
            }]
        }
    
    def _generate_html(self, results: DetectionResult, capabilities: Dict[str, Any], 
                      license_tier: str, scan_time: float) -> str:
        """Generate HTML format output."""
        total_matches = sum(len(file_result.matches) for file_result in results.file_results)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Levox PII Detection Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }}
        .results {{ margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .high-confidence {{ color: #d73027; }}
        .medium-confidence {{ color: #fc8d59; }}
        .low-confidence {{ color: #fee08b; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Levox PII Detection Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>License: {license_tier} | Scan time: {scan_time:.2f}s</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <p>Total matches: {total_matches}</p>
        <p>Files scanned: {len(results.file_results)}</p>
    </div>
    
    <div class="results">
        <h2>🔍 Detection Results</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Line</th>
                <th>Pattern</th>
                <th>Match</th>
                <th>Confidence</th>
                <th>Level</th>
            </tr>"""
        
        for file_result in results.file_results:
            for match in file_result.matches:
                confidence_class = "high-confidence" if match.confidence > 0.8 else "medium-confidence" if match.confidence > 0.5 else "low-confidence"
                html += f"""
            <tr>
                <td>{file_result.file_path}</td>
                <td>{match.line_number}</td>
                <td>{match.pattern_name}</td>
                <td>{match.matched_text[:100]}</td>
                <td class="{confidence_class}">{match.confidence:.2f}</td>
                <td>{match.metadata.get('detection_level', 'unknown')}</td>
            </tr>"""
        
        html += """
        </table>
    </div>
</body>
</html>"""
        return html
    
    def _save_results(self, results: DetectionResult, output_file: str, output_format: str):
        """Save results to file."""
        with open(output_file, 'w') as f:
            if output_format == 'json':
                json.dump(self._results_to_dict(results), f, indent=2)
            elif output_format == 'yaml':
                yaml.dump(self._results_to_dict(results), f)
            else:
                # Plain text format
                for file_result in results.file_results:
                    for match in file_result.matches:
                        f.write(f"{file_result.file_path}:{match.line_number}: {match.pattern_name} - {match.matched_text}\n")
    
    def _results_to_dict(self, results: DetectionResult) -> Dict[str, Any]:
        """Convert results to dictionary."""
        return {
            'file_results': [
                {
                    'file_path': str(file_result.file_path),
                    'matches': [
                        {
                            'pattern_name': match.pattern_name,
                            'matched_text': match.matched_text,
                            'line_number': match.line_number,
                            'confidence': match.confidence,
                            'risk_level': str(match.risk_level),
                            'metadata': match.metadata
                        }
                        for match in file_result.matches
                    ]
                }
                for file_result in results.file_results
            ]
        }

    def generate_reports(self, report_formats: List[str], output_dir: Optional[str] = None) -> Dict[str, str]:
        """Generate reports from the last scan results."""
        if not self.last_scan_results:
            console.print("[yellow]⚠️ No scan results available. Run a scan first.[/yellow]")
            return {}
        
        try:
            from .compliance.reporting import ComplianceReporter
            
            # Initialize compliance reporter
            config = self.config or load_default_config()
            reporter = ComplianceReporter(config)
            
            # Generate reports using the compliance reporter
            reports = reporter.generate_scan_report(
                detection_result=self.last_scan_results,
                scan_path=self.last_scan_path,
                scan_time=self.last_scan_time,
                license_tier=self.last_license_tier,
                output_formats=report_formats
            )
            
            # Save reports to files if output directory specified
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                saved_reports = {}
                for format_type, content in reports.items():
                    if content:
                        filename = f"levox_report_{timestamp}.{format_type}"
                        file_path = output_path / filename
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        saved_reports[format_type] = str(file_path)
                
                return saved_reports
            
            return reports
            
        except Exception as e:
            console.print(f"[red]❌ Failed to generate reports: {e}[/red]")
            return {}


# CLI instance
levox_cli = LevoxCLI()


def print_banner():
    """Print the beautiful Levox banner."""
    console.print(LEVOX_LOGO, style="bold blue")
    console.print()
    
    # Tagline with gradient effect
    tagline = Text("🔒 Secure • 🚀 Fast • 🎯 Accurate • 🧪 Beta-Ready", style="bold cyan")
    console.print(Align.center(tagline))
    console.print()
    
    # Version info
    version_info = Text("Version 0.9.0 Beta", style="dim")
    console.print(Align.center(version_info))
    console.print()


def print_version(ctx, param, value):
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
        console.print("Levox v1.0.9 - AI-powered PII/GDPR Detection Tool")
    ctx.exit()

@click.group()
@click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help='Show version and exit.')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output and detailed logging.')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output.')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file.')
@click.pass_context
def cli(ctx, verbose, quiet, config):
    """
    Levox - AI-powered PII/GDPR Detection CLI
    
    Detect Personally Identifiable Information (PII) and ensure GDPR compliance
    in your codebase with our advanced detection technology.
    
    Quick Start:
    • Scan current directory: levox scan
    • Scan specific path: levox scan /path/to/code
    • Generate reports: levox scan --report json html
    • Show system status: levox status
    • Get help: levox <command> --help
    
    Pricing: Currently FREE - paid plans coming soon
    Website: levoxserver.vercel.app
    
    For feedback please email us at aifenrix@gmail.com
    """
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set up configuration
    try:
        if config:
            levox_cli.config = Config.from_file(config)
        else:
            levox_cli.config = load_default_config()
    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        ctx.exit(EXIT_CONFIG_ERROR)
    
    # Set up logging level
    if verbose:
        levox_cli.config.log_level = "DEBUG"
    if quiet:
        levox_cli.config.log_level = "ERROR"
    
    # Print banner (unless quiet)
    if not quiet:
        # Don't print banner here to avoid duplication - it's already shown in run_scan
        pass
    
    # Suppress tree-sitter deprecation warnings
    import warnings
    warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")
    
    return ctx


@cli.command()
@click.argument('path', type=str, default='.')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'sarif', 'html']),
              default='table', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--verbose', is_flag=True, help='Enable verbose output and detailed logging')
@click.option('--debug', is_flag=True, help='Enable debug output (alias for --verbose)')
@click.option('--telemetry', is_flag=True, help='Show detailed capability and performance info')
@click.option('--max-file-size-mb', type=int, help='Maximum file size to scan in MB')
@click.option('--exclude-patterns', multiple=True, help='File patterns to exclude')
@click.option('--scan-optional/--no-scan-optional', is_flag=True, default=False, 
              help='Toggle scanning of optional file types (.txt, .md) in addition to source code and config files')
@click.option('--allow-fallback-parsing', is_flag=True, default=True, help='Allow fallback parsing when Tree-Sitter unavailable')
@click.option('--require-full-ast', is_flag=True, help='Require full AST parsing (fail if Tree-Sitter unavailable)')
@click.option('--report', 'report_formats', type=click.Choice(['json', 'html', 'pdf']), multiple=True, 
              help='Generate reports in specific formats (can specify multiple: --report json --report html)')
@click.option('--no-report', is_flag=True, default=False, help='Skip report generation entirely')
@click.option('--dev', is_flag=True, help='Developer mode: show internal traces, confidence scores, timings, and engine details')
@click.option('--verbosity', type=click.Choice(['summary', 'verbose', 'debug']), default='summary',
              help='Output verbosity level: summary (default), verbose, or debug')
@click.pass_context
def scan(ctx, path, output_format, output, verbose, debug, telemetry, max_file_size_mb, exclude_patterns, scan_optional, allow_fallback_parsing, require_full_ast, report_formats, no_report, dev, verbosity):
    """Scan files/directories for PII violations with beautiful progress indicators."""
    
    # Handle debug flag as verbose
    if debug:
        verbose = True
        verbosity = 'debug'
    
    # Handle report generation logic
    if no_report:
        report_formats = []
    elif not report_formats:
        # Default: no reports unless specifically requested
        report_formats = []
    
    # Robust path handling for Windows and quoted paths
    from pathlib import Path
    try:
        # Handle quoted paths and Windows path issues
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        elif path.startswith("'") and path.endswith("'"):
            path = path[1:-1]
        
        # Handle Windows path normalization
        if sys.platform == 'win32':
            # Convert forward slashes to backslashes for Windows
            path = path.replace('/', '\\')
            # Handle UNC paths and drive letters
            if path.startswith('\\\\'):
                # UNC path - leave as is
                pass
            elif len(path) >= 2 and path[1] == ':':
                # Drive letter path - ensure proper format
                path = path[0].upper() + path[1:]
            elif not path.startswith('\\\\') and not path.startswith('.') and not path.startswith('\\'):
                # Relative path - ensure it's properly formatted
                path = Path.cwd() / path
        
        scan_path = Path(path).resolve()
        if not scan_path.exists():
            console.print(f"[red]❌ Path does not exist: {scan_path}[/red]")
            ctx.exit(EXIT_CONFIG_ERROR)
    except Exception as e:
        console.print(f"[red]❌ Invalid path: {path} - {e}[/red]")
        console.print(f"[yellow]💡 Tip: Use quotes around paths with spaces: \"{path}\"[/yellow]")
        ctx.exit(EXIT_CONFIG_ERROR)
    
    exit_code = levox_cli.run_scan(
        path=str(scan_path),
        output_format=output_format,
        output_file=output,
        verbose=verbose,
        telemetry=telemetry,
        max_file_size_mb=max_file_size_mb,
        exclude_patterns=list(exclude_patterns) if exclude_patterns else None,
        scan_optional=scan_optional,
        allow_fallback_parsing=allow_fallback_parsing,
        require_full_ast=require_full_ast,
        report_formats=list(report_formats) if report_formats else None,
        dev_mode=dev,
        verbosity=verbosity
    )
    
    ctx.exit(exit_code)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--format', 'output_format', type=click.Choice(['json', 'html', 'sarif']),
              default='json', help='Report format')
@click.option('--output', '-o', type=click.Path(), help='Output file for report')
def report(file_path, output_format, output):
    """Generate detailed scan reports from previous scan results."""
    try:
        from pathlib import Path
        from levox.models.detection_result import DetectionResult
        
        # Load results from file
        results = DetectionResult.from_file(file_path)
        
        # Generate report in requested format
        if output_format == 'json':
            report_content = results.to_json(indent=2)
        elif output_format == 'html':
            report_content = levox_cli._generate_html(results, {}, 'enterprise', 0.0)
        elif output_format == 'sarif':
            report_content = json.dumps(levox_cli._generate_sarif(results, {}, 'enterprise'), indent=2)
        
        # Output report
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(report_content)
            console.print(f"[green]✅ Report saved to {output}[/green]")
        else:
            console.print(report_content)
            
    except FileNotFoundError:
        console.print(f"[red]❌ Results file not found: {file_path}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Failed to generate report: {e}[/red]")


@cli.command()
def status():
    """Show system status and capabilities with beautiful styling."""
    # Show beautiful branding (only in non-interactive mode)
    if not hasattr(levox_cli, '_interactive_mode') or not levox_cli._interactive_mode:
        levox_cli.print_branding()
    
    # Get license information from license client
    try:
        from .core.license_client import get_license_client
        license_client = get_license_client()
        license_info = license_client.get_license_info()
        license_tier = license_info.tier.value
        
        console.print(f"[dim]🔑 Current license tier: {license_tier.title()}[/dim]")
        
    except Exception as e:
        console.print(f"[yellow]⚠️  Warning: Could not retrieve license information: {e}[/yellow]")
        console.print(f"[dim]🔒 Using standard tier (limited features)[/dim]")
        license_tier = 'standard'
    
    capabilities = levox_cli.validate_dependencies()
    levox_cli.print_capability_status(capabilities, license_tier)


@cli.group()
def feedback():
    """Feedback management commands."""
    pass


@feedback.command('submit')
@click.argument('match_id')
@click.argument('verdict', type=click.Choice(['true_positive', 'false_positive', 'uncertain']))
@click.option('--notes', help='Optional notes about the feedback')
def submit_feedback(match_id, verdict, notes):
    """Submit feedback for a detection match."""
    try:
        if not levox_cli.feedback_collector:
            levox_cli.feedback_collector = FeedbackCollector(levox_cli.config)
        
        feedback_id = levox_cli.feedback_collector.submit_feedback(
            match_id=match_id,
            verdict=verdict,
            notes=notes
        )
        
        console.print(f"[green]✅ Feedback submitted: {feedback_id}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to submit feedback: {e}[/red]")


@feedback.command('stats')
@click.option('--days', default=30, help='Number of days to include in stats')
def feedback_stats(days):
    """Show feedback statistics."""
    try:
        if not levox_cli.feedback_collector:
            levox_cli.feedback_collector = FeedbackCollector(levox_cli.config)
        
        stats = levox_cli.feedback_collector.get_feedback_stats(days)
        
        if stats:
            console.print(f"[bold cyan]📊 Feedback Statistics (Last {days} days)[/bold cyan]")
            
            table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", justify="right", style="green")
            
            table.add_row("Total Feedback", str(stats.get('total_feedback', 0)))
            
            verdict_counts = stats.get('verdict_counts', {})
            for verdict, count in verdict_counts.items():
                table.add_row(f"  {verdict.replace('_', ' ').title()}", str(count))
            
            console.print(table)
        else:
            console.print("[yellow]No feedback data available[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Failed to get feedback stats: {e}[/red]")


@feedback.command('export')
@click.argument('output_path', type=click.Path())
@click.option('--limit', type=int, help='Maximum number of records to export')
def export_feedback(output_path, limit):
    """Export feedback data to JSONL format."""
    try:
        if not levox_cli.feedback_collector:
            levox_cli.feedback_collector = FeedbackCollector(levox_cli.config)
        
        count = levox_cli.feedback_collector.export_feedback_jsonl(output_path, limit)
        console.print(f"[green]✅ Exported {count} feedback records to {output_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to export feedback: {e}[/red]")


@cli.command()
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def models(format, output, verbose):
    """Manage and evaluate ML models."""
    try:
        from levox.detection.ml_filter import MLFilter
        from levox.core.config import load_default_config
        import pickle
        
        config = load_default_config()
        ml_filter = MLFilter(config)
        
        # Get model information
        if ml_filter.model_info:
            current_model = {
                'id': ml_filter.model_info.model_id,
                'type': ml_filter.model_info.model_type,
                'version': ml_filter.model_info.version,
                'training_date': ml_filter.model_info.training_date,
                'accuracy': ml_filter.model_info.metrics.accuracy,
                'f1_score': ml_filter.model_info.metrics.f1_score,
                'precision': ml_filter.model_info.metrics.precision,
                'recall': ml_filter.model_info.metrics.recall,
                'training_samples': ml_filter.model_info.training_samples,
                'validation_samples': ml_filter.model_info.validation_samples
            }
        else:
            current_model = None
        
        # Find all available models
        models_dir = Path("configs/ml_models")
        available_models = []
        
        if models_dir.exists():
            for model_file in models_dir.glob("*.pkl"):
                try:
                    # Load model data to get info
                    with open(model_file, 'rb') as f:
                        # SECURITY: Use safe pickle loading with restrictions
                        import pickle
                        import io
                        
                        # Create a restricted unpickler that only allows safe classes
                        class RestrictedUnpickler(pickle.Unpickler):
                            def find_class(self, module, name):
                                # Only allow safe built-in types and numpy/sklearn classes
                                safe_modules = {
                                    'numpy', 'sklearn', 'scipy', 'pandas',
                                    'builtins', '__builtin__'
                                }
                                safe_classes = {
                                    'list', 'dict', 'tuple', 'set', 'str', 'int', 'float', 'bool',
                                    'ndarray', 'DataFrame', 'Series'
                                }
                                
                                if module in safe_modules and name in safe_classes:
                                    return super().find_class(module, name)
                                else:
                                    raise pickle.UnpicklingError(f"Unsafe class: {module}.{name}")
                        
                        # Use restricted unpickler
                        model_data = RestrictedUnpickler(f).load()
                    
                    if 'model_info' in model_data:
                        model_info = model_data['model_info']
                        
                        # Handle both old and new model structures
                        if 'metrics' in model_info and isinstance(model_info['metrics'], dict):
                            # New structure with nested metrics
                            metrics = model_info['metrics']
                            accuracy = metrics.get('accuracy', 0.0)
                            f1_score = metrics.get('f1_score', 0.0)
                            precision = metrics.get('precision', 0.0)
                            recall = metrics.get('recall', 0.0)
                        else:
                            # Old structure with metrics directly in model_info
                            accuracy = model_info.get('accuracy', 0.0)
                            f1_score = model_info.get('f1_score', 0.0)
                            precision = model_info.get('precision', 0.0)
                            recall = model_info.get('recall', 0.0)
                        
                        # Simple scoring formula
                        score = (accuracy * 0.4) + (f1_score * 0.4) + (precision * 0.1) + (recall * 0.1)
                        
                        available_models.append({
                            'path': model_file.name,
                            'id': model_info.get('model_id', 'unknown'),
                            'type': model_info.get('model_type', 'unknown'),
                            'version': model_info.get('version', 'unknown'),
                            'training_date': model_info.get('training_date', 'unknown'),
                            'accuracy': accuracy,
                            'f1_score': f1_score,
                            'precision': precision,
                            'recall': recall,
                            'training_samples': model_info.get('training_samples', 0),
                            'validation_samples': model_info.get('validation_samples', 0),
                            'score': score,
                            'is_current': current_model and current_model['id'] == model_info.get('model_id', '')
                        })
                        
                except Exception as e:
                    if verbose:
                        print(f"Failed to load model {model_file.name}: {e}")
                    continue
        
        # Sort by score (best first)
        available_models.sort(key=lambda x: x['score'], reverse=True)
        
        if format == 'json':
            result = {
                'current_model': current_model,
                'available_models': available_models,
                'best_model': available_models[0] if available_models else None
            }
            
            if output:
                with open(output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                click.echo(f"Model information saved to {output}")
            else:
                click.echo(json.dumps(result, indent=2, default=str))
        else:
            # Table format
            click.echo("🤖 Levox ML Model Management")
            click.echo("=" * 50)
            
            if current_model:
                click.echo(f"📊 Current Model: {current_model['id']}")
                click.echo(f"   Type: {current_model['type']} v{current_model['version']}")
                click.echo(f"   Training Date: {current_model['training_date']}")
                click.echo(f"   Accuracy: {current_model['accuracy']:.3f}")
                click.echo(f"   F1-Score: {current_model['f1_score']:.3f}")
                click.echo(f"   Training Samples: {current_model['training_samples']}")
                click.echo()
            
            if available_models:
                click.echo("📋 Available Models (sorted by performance):")
                click.echo("-" * 50)
                
                # Table header
                click.echo(f"{'Model':<25} {'Score':<8} {'Accuracy':<10} {'F1':<8} {'Samples':<12} {'Status':<10}")
                click.echo("-" * 75)
                
                for model in available_models:
                    status = "🟢 ACTIVE" if model['is_current'] else "⚪ AVAILABLE"
                    click.echo(f"{model['path']:<25} {model['score']:<8.3f} {model['accuracy']:<10.3f} "
                             f"{model['f1_score']:<8.3f} {model['training_samples']:<12} {status:<10}")
                
                click.echo()
                click.echo(f"🏆 Best Model: {available_models[0]['path']} (Score: {available_models[0]['score']:.3f})")
                
                if current_model and available_models[0]['id'] != current_model['id']:
                    current_score = next(m['score'] for m in available_models if m['is_current'])
                    improvement = available_models[0]['score'] - current_score
                    if improvement > 0:
                        click.echo(f"💡 Better model available! Improvement: +{improvement:.3f}")
                        click.echo("   Run 'levox switch-model --auto' to switch to the best model")
            else:
                click.echo("❌ No models found in models directory")
    
    except Exception as e:
        click.echo(f"❌ Error managing models: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()

@cli.command()
@click.option('--model-id', type=str, help='Specific model ID to switch to')
@click.option('--auto', is_flag=True, help='Automatically switch to the best available model')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def switch_model(model_id, auto, verbose):
    """Switch to a different ML model."""
    try:
        from levox.detection.ml_filter import MLFilter
        from levox.core.config import load_default_config
        
        config = load_default_config()
        ml_filter = MLFilter(config)
        
        if auto:
            # Automatically switch to the best model
            click.echo("🔄 Automatically switching to best available model...")
            
            # Trigger model check
            ml_filter._check_for_better_models()
            
            if ml_filter.model_info:
                click.echo(f"✅ Switched to model: {ml_filter.model_info.model_id}")
                click.echo(f"   Type: {ml_filter.model_info.model_type} v{ml_filter.model_info.version}")
                click.echo(f"   Accuracy: {ml_filter.model_info.metrics.accuracy:.3f}")
                click.echo(f"   F1-Score: {ml_filter.model_info.metrics.f1_score:.3f}")
            else:
                click.echo("❌ Failed to switch models")
        
        elif model_id:
            # Switch to specific model
            models_dir = Path(__file__).parent.parent.parent / "configs" / "ml_models"
            target_model = None
            
            if models_dir.exists():
                for model_file in models_dir.glob("*.pkl"):
                    try:
                        model_info = ml_filter._peek_model_info(str(model_file))
                        if model_info and model_info.model_id == model_id:
                            target_model = model_file
                            break
                    except Exception:
                        continue
            
            if target_model:
                click.echo(f"🔄 Switching to model: {model_id}")
                if ml_filter._load_model(str(target_model)):
                    click.echo(f"✅ Successfully switched to: {target_model.name}")
                    click.echo(f"   Type: {ml_filter.model_info.model_type} v{ml_filter.model_info.version}")
                    click.echo(f"   Accuracy: {ml_filter.model_info.metrics.accuracy:.3f}")
                    click.echo(f"   F1-Score: {ml_filter.model_info.metrics.f1_score:.3f}")
                else:
                    click.echo(f"❌ Failed to switch to model: {model_id}")
            else:
                click.echo(f"❌ Model not found: {model_id}")
        
        else:
            click.echo("❌ Please specify --auto or --model-id")
    
    except Exception as e:
        click.echo(f"❌ Error switching models: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()

@cli.command()
@click.option('--format', type=click.Choice(['table', 'json', 'markdown']), default='table', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def help(format, output, verbose):
    """
    Show comprehensive help with all available commands and options.
    
    This command provides a complete overview of all Levox CLI commands,
    their usage, and available options for different verbosity levels.
    """
    try:
        help_data = {
            "cli_overview": {
                "description": "Levox - Enterprise PII/GDPR Detection CLI",
                "version": "0.9.0 Beta",
                "main_commands": ["scan", "status", "report", "feedback", "models", "help", "history", "ml_health", "generate_report", "switch_model", "set-report-directory"]
            },
            "verbose_output_options": {
                "summary": {
                    "description": "Default output mode - shows essential information only",
                    "usage": "levox scan /path --verbosity summary",
                    "includes": ["File path", "Line number", "Severity", "Description"],
                    "excludes": ["Engine details", "Confidence scores", "Code snippets", "Timing data"]
                },
                "verbose": {
                    "description": "Enhanced output mode - shows detailed detection information",
                    "usage": "levox scan /path --verbosity verbose",
                    "includes": ["File path", "Line number", "Severity", "Description", "Engine", "Rule ID", "Confidence", "Code snippet"],
                    "excludes": ["Raw JSON data", "Internal traces", "Performance metrics"]
                },
                "debug": {
                    "description": "Developer mode - shows all available information",
                    "usage": "levox scan /path --verbosity debug",
                    "includes": ["All verbose information", "Raw DetectionResult objects", "Internal traces", "Performance metrics", "Engine timing"],
                    "excludes": ["Nothing - shows everything"]
                }
            },
            "toggle_options": {
                "cli_toggle_flags": {
                    "--scan-optional/--no-scan-optional": "Toggle scanning of optional file types (.txt, .md)",
                    "--allow-fallback-parsing": "Allow fallback parsing when Tree-Sitter unavailable",
                    "--require-full-ast": "Require full AST parsing (fail if Tree-Sitter unavailable)",
                    "--cfg, --deep-scan": "Enable Control Flow Graph analysis for complex PII detection",
                    "--telemetry": "Show detailed capability and performance information",
                    "--no-report": "Skip report generation entirely",
                    "--dev": "Enable developer mode with internal traces",
                    "--include-metadata": "Include detailed metadata in reports",
                    "--latest": "Generate report from latest scan results",
                    "--list": "List available scan results for reporting",
                    "--detailed": "Show detailed capability information",
                    "--check-dependencies": "Verify all dependencies are available",
                    "--auto": "Automatically switch to best available ML model",
                    "--from-last-scan": "Generate reports from last scan results"
                },
                "verbosity_flags": {
                    "--verbosity": "Choose output detail level (summary/verbose/debug)",
                    "--dev": "Enable developer mode with internal traces",
                    "--verbose, -v": "Enable verbose logging and output",
                    "--quiet, -q": "Suppress all output except errors"
                },
                "output_formats": {
                    "--format": "Choose output format (table/json/sarif/html)",
                    "--report": "Generate reports in specific formats (json/html/pdf)",
                    "--output, -o": "Save results to specified file"
                },
                "scan_options": {
                    "--license-tier": "License tier is automatically detected from verified license",
                    "--max-workers": "Set number of concurrent file scanners",
                    "--max-file-size-mb": "Limit file size for scanning",
                    "--exclude-patterns": "Exclude files matching patterns"
                },
                "configuration_toggles": {
                    "enable_ast": "Enable AST analysis (Premium+)",
                    "enable_dataflow": "Enable dataflow analysis (Enterprise)",
                    "enable_ml": "Enable ML-based false positive reduction",
                    "enable_context_analysis": "Enable context-aware detection",
                    "enable_compliance_audit": "Enable GDPR compliance checking",
                    "enable_context_aware_filtering": "Enable context-aware filtering",
                    "enable_safe_literal_detection": "Enable safe literal detection",
                    "enable_variable_heuristics": "Enable variable heuristics",
                    "enable_placeholder_detection": "Enable placeholder detection",
                    "enable_ml_monitoring": "Enable ML system monitoring",
                    "enable_async": "Enable asynchronous processing",
                    "cache_ast_parses": "Cache AST parsing for performance",
                    "enable_compression": "Enable log compression",
                    "include_security_checks": "Include security compliance checks",
                    "include_dsar_checks": "Include Data Subject Access Request checks",
                    "include_deletion_checks": "Include data deletion checks",
                    "include_transfer_checks": "Include data transfer checks",
                    "include_consent_checks": "Include consent management checks",
                    "include_retention_checks": "Include data retention checks",
                    "enable_crypto_verification": "Enable cryptographic verification (Enterprise)",
                    "enable_dashboards": "Enable compliance dashboards (Premium+)",
                    "enable_trends": "Enable trend analysis (Enterprise)",
                    "enable_export": "Enable data export functionality"
                }
            },
            "all_commands": {
                "scan": {
                    "description": "Scan files/directories for PII violations and GDPR compliance issues",
                    "usage": "levox scan <path> [options]",
                    "key_options": ["--cfg", "--verbosity", "--report", "--output"]
                },
                "status": {
                    "description": "Show system status, capabilities, and dependency information",
                    "usage": "levox status [options]",
                    "key_options": ["--detailed", "--check-dependencies"]
                },
                "report": {
                    "description": "Generate detailed reports from previous scan results",
                    "usage": "levox report [file] [options]",
                    "key_options": ["--format", "--output", "--latest", "--list"]
                },
                "feedback": {
                    "description": "Submit feedback for detection matches to improve accuracy",
                    "usage": "levox feedback <match_id> <verdict> [options]",
                    "key_options": ["--notes", "--confidence"]
                },
                "models": {
                    "description": "Manage and evaluate ML models used for detection",
                    "usage": "levox models [options]",
                    "key_options": ["--list", "--evaluate", "--train", "--export"]
                },
                "history": {
                    "description": "Show scan history and available results for reporting",
                    "usage": "levox history [options]",
                    "key_options": ["--detailed", "--limit"]
                },
                "set-report-directory": {
                    "description": "Choose where reports are saved using Windows Explorer",
                    "usage": "levox set-report-directory",
                    "key_options": ["Opens folder picker dialog"]
                },
                "ml_health": {
                    "description": "Check ML system health and performance",
                    "usage": "levox ml_health [options]",
                    "key_options": ["--format", "--output", "--verbose"]
                },
                "switch_model": {
                    "description": "Switch to a different ML model",
                    "usage": "levox switch_model [options]",
                    "key_options": ["--model-id", "--auto", "--verbose"]
                },
                "generate_report": {
                    "description": "Generate reports from the last scan results",
                    "usage": "levox generate_report [options]",
                    "key_options": ["--format", "--output-dir", "--from-last-scan"]
                },
                "help": {
                    "description": "Show comprehensive help with all available commands and options",
                    "usage": "levox help [options]",
                    "key_options": ["--format", "--output", "--verbose"]
                }
            },
            "quick_examples": {
                "basic_scan": "levox scan /path/to/code",
                "verbose_scan": "levox scan /path/to/code --verbosity verbose",
                "debug_scan": "levox scan /path/to/code --verbosity debug",
                "generate_reports": "levox scan /path/to/code --report json --report html",
                "developer_mode": "levox scan /path/to/code --dev",
                "save_results": "levox scan /path/to/code --output results.json",
                "check_status": "levox status --detailed",
                "view_history": "levox history --detailed --limit 20",
                "ml_health_check": "levox ml_health --verbose",
                "switch_best_model": "levox switch_model --auto",
                "set_report_directory": "levox set-report-directory"
            },
            "configuration_tips": {
                "verbosity_workflow": [
                    "Start with 'summary' mode for quick overview",
                    "Use 'verbose' mode for detailed analysis",
                    "Switch to 'debug' mode for troubleshooting",
                    "Use '--dev' flag for development insights"
                ],
                "performance_tuning": [
                    "Adjust '--max-workers' based on CPU cores",
                    "Use '--max-file-size-mb' for large codebases",
                    "Exclude test files with '--exclude-patterns'",
                    "Enable caching with enterprise license"
                ]
            }
        }
        
        if format == 'json':
            output_content = json.dumps(help_data, indent=2, default=str)
        elif format == 'markdown':
            output_content = _generate_markdown_help(help_data)
        else:
            # Default table format
            _display_help_table(help_data, verbose)
            return
        
        # Handle output
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            click.echo(f"Help documentation saved to {output}")
        else:
            click.echo(output_content)
            
    except Exception as e:
        click.echo(f"❌ Error generating help: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()


def _display_help_table(help_data, verbose):
    """Display help information in a formatted table."""
    console = Console()
    
    # CLI Overview
    overview = help_data["cli_overview"]
    console.print(Panel(
        f"[bold blue]{overview['description']}[/bold blue]\n"
        f"[dim]Version: {overview['version']}[/dim]\n"
        f"[cyan]Available Commands: {len(overview['main_commands'])}[/cyan]",
        title="🚀 Levox CLI Overview",
        border_style="blue"
    ))
    
    # All Available Commands
    console.print("\n[bold green]📋 All Available Commands[/bold green]")
    commands_table = Table(show_header=True, header_style="bold magenta")
    commands_table.add_column("Command", style="cyan", width=15)
    commands_table.add_column("Description", style="white", width=50)
    commands_table.add_column("Usage", style="yellow", width=30)
    commands_table.add_column("Key Options", style="green", width=25)
    
    for cmd_name, cmd_info in help_data["all_commands"].items():
        commands_table.add_row(
            cmd_name,
            cmd_info["description"][:47] + "..." if len(cmd_info["description"]) > 50 else cmd_info["description"],
            cmd_info["usage"],
            ", ".join(cmd_info["key_options"][:2]) + "..." if len(cmd_info["key_options"]) > 2 else ", ".join(cmd_info["key_options"])
        )
    
    console.print(commands_table)
    
    # Verbose Output Options
    console.print("\n[bold green]📊 Verbose Output Options[/bold green]")
    verbosity_table = Table(show_header=True, header_style="bold magenta")
    verbosity_table.add_column("Mode", style="cyan")
    verbosity_table.add_column("Description", style="white")
    verbosity_table.add_column("Usage", style="yellow")
    verbosity_table.add_column("Includes", style="green")
    
    for mode, details in help_data["verbose_output_options"].items():
        verbosity_table.add_row(
            mode.upper(),
            details["description"],
            details["usage"],
            ", ".join(details["includes"][:3]) + "..." if len(details["includes"]) > 3 else ", ".join(details["includes"])
        )
    
    console.print(verbosity_table)
    
    # Toggle Options
    console.print("\n[bold green]⚙️  Toggle Options[/bold green]")
    
    # CLI Toggle Flags
    if "cli_toggle_flags" in help_data["toggle_options"]:
        console.print("\n[bold cyan]🎛️  CLI Toggle Flags[/bold cyan]")
        cli_flags_table = Table(show_header=True, header_style="bold magenta")
        cli_flags_table.add_column("Flag", style="cyan", width=30)
        cli_flags_table.add_column("Description", style="white", width=60)
        
        for flag, desc in help_data["toggle_options"]["cli_toggle_flags"].items():
            cli_flags_table.add_row(flag, desc)
        
        console.print(cli_flags_table)
    
    # Verbosity flags
    verbosity_flags = help_data["toggle_options"]["verbosity_flags"]
    flags_table = Table(show_header=True, header_style="bold magenta")
    flags_table.add_column("Flag", style="cyan")
    flags_table.add_column("Description", style="white")
    
    for flag, desc in verbosity_flags.items():
        flags_table.add_row(flag, desc)
    
    console.print(Panel(flags_table, title="🎛️  Verbosity & Output Flags", border_style="green"))
    
    # Configuration Toggles
    if "configuration_toggles" in help_data["toggle_options"]:
        console.print("\n[bold cyan]⚙️  Configuration Toggles[/bold cyan]")
        console.print("[dim]These toggles are set in configuration files, not CLI flags[/dim]")
        
        config_table = Table(show_header=True, header_style="bold magenta")
        config_table.add_column("Toggle", style="cyan", width=35)
        config_table.add_column("Description", style="white", width=55)
        
        for toggle, desc in help_data["toggle_options"]["configuration_toggles"].items():
            config_table.add_row(toggle, desc)
        
        console.print(config_table)
    
    # Quick Examples
    console.print("\n[bold green]💡 Quick Examples[/bold green]")
    examples_table = Table(show_header=True, header_style="bold magenta")
    examples_table.add_column("Use Case", style="cyan")
    examples_table.add_column("Command", style="yellow")
    
    for use_case, command in help_data["quick_examples"].items():
        examples_table.add_row(use_case.replace("_", " ").title(), command)
    
    console.print(examples_table)
    
    # Configuration Tips
    if verbose:
        console.print("\n[bold green]🔧 Configuration Tips[/bold green]")
        
        # Verbosity workflow
        workflow_panel = Panel(
            "\n".join([f"• {tip}" for tip in help_data["configuration_tips"]["verbosity_workflow"]]),
            title="📈 Verbosity Workflow",
            border_style="blue"
        )
        console.print(workflow_panel)
        
        # Performance tuning
        performance_panel = Panel(
            "\n".join([f"• {tip}" for tip in help_data["configuration_tips"]["performance_tuning"]]),
            title="⚡ Performance Tuning",
            border_style="yellow"
        )
        console.print(performance_panel)
    
    # Footer
    console.print("\n[dim]💡 Tip: Use 'levox <command> --help' for detailed help on specific commands[/dim]")
    console.print("[dim]📚 For more information, visit the project documentation[/dim]")


def _generate_markdown_help(help_data):
    """Generate markdown format help documentation."""
    md_content = []
    
    # Header
    md_content.append(f"# {help_data['cli_overview']['description']}")
    md_content.append(f"**Version:** {help_data['cli_overview']['version']}")
    md_content.append("")
    
    # All Available Commands
    md_content.append("## All Available Commands")
    md_content.append("")
    
    for cmd_name, cmd_info in help_data["all_commands"].items():
        md_content.append(f"### {cmd_name}")
        md_content.append(f"**Description:** {cmd_info['description']}")
        md_content.append(f"**Usage:** `{cmd_info['usage']}`")
        md_content.append("**Key Options:**")
        for option in cmd_info["key_options"]:
            md_content.append(f"- `{option}`")
        md_content.append("")
    
    # Verbose Output Options
    md_content.append("## Verbose Output Options")
    md_content.append("")
    
    for mode, details in help_data["verbose_output_options"].items():
        md_content.append(f"### {mode.title()} Mode")
        md_content.append(f"**Description:** {details['description']}")
        md_content.append(f"**Usage:** `{details['usage']}`")
        md_content.append("**Includes:**")
        for item in details["includes"]:
            md_content.append(f"- {item}")
        md_content.append("")
    
    # Toggle Options
    md_content.append("## Toggle Options")
    md_content.append("")
    
    # CLI Toggle Flags
    if "cli_toggle_flags" in help_data["toggle_options"]:
        md_content.append("### CLI Toggle Flags")
        md_content.append("")
        for flag, desc in help_data["toggle_options"]["cli_toggle_flags"].items():
            md_content.append(f"- **{flag}:** {desc}")
        md_content.append("")
    
    # Verbosity Flags
    if "verbosity_flags" in help_data["toggle_options"]:
        md_content.append("### Verbosity Flags")
        md_content.append("")
        for flag, desc in help_data["toggle_options"]["verbosity_flags"].items():
            md_content.append(f"- **{flag}:** {desc}")
        md_content.append("")
    
    # Configuration Toggles
    if "configuration_toggles" in help_data["toggle_options"]:
        md_content.append("### Configuration Toggles")
        md_content.append("")
        md_content.append("These toggles are set in configuration files, not CLI flags:")
        md_content.append("")
        for toggle, desc in help_data["toggle_options"]["configuration_toggles"].items():
            md_content.append(f"- **{toggle}:** {desc}")
        md_content.append("")
    
    # Quick Examples
    md_content.append("## Quick Examples")
    md_content.append("")
    
    for use_case, command in help_data["quick_examples"].items():
        md_content.append(f"**{use_case.replace('_', ' ').title()}:**")
        md_content.append(f"```bash")
        md_content.append(command)
        md_content.append("```")
        md_content.append("")
    
    return "\n".join(md_content)


@cli.command()
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def ml_health(format, output, verbose):
    """Check ML system health and performance."""
    try:
        from levox.detection.ml_filter import MLFilter
        from levox.core.config import load_default_config
        
        config = load_default_config()
        ml_filter = MLFilter(config)
        
        # Get comprehensive health status
        health_status = ml_filter.get_health_status()
        
        if format == 'json':
            if output:
                with open(output, 'w') as f:
                    json.dump(health_status, f, indent=2, default=str)
                click.echo(f"Health status saved to {output}")
            else:
                click.echo(json.dumps(health_status, indent=2, default=str))
        else:
            # Table format
            click.echo("🏥 ML System Health Check")
            click.echo("=" * 50)
            
            # Overall status
            status_emoji = {
                'healthy': '🟢',
                'degraded': '🟡',
                'unhealthy': '🔴'
            }
            status = health_status.get('status', 'unknown')
            click.echo(f"Status: {status_emoji.get(status, '⚪')} {status.upper()}")
            
            # Uptime
            uptime = health_status.get('uptime_seconds', 0)
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            click.echo(f"Uptime: {hours}h {minutes}m")
            
            # Model information
            model_info = health_status.get('model_info', {})
            if model_info and model_info.get('loaded'):
                click.echo(f"Model: {model_info.get('model_id', 'unknown')}")
                click.echo(f"Version: {model_info.get('version', 'unknown')}")
                click.echo(f"Switches: {model_info.get('last_switch', 0)}")
            else:
                click.echo("Model: ❌ Not loaded")
            
            # Performance metrics
            performance = health_status.get('performance', {})
            if performance:
                click.echo(f"\n📊 Performance Metrics:")
                click.echo(f"  Total Processed: {performance.get('total_processed', 0)}")
                click.echo(f"  Total Filtered: {performance.get('total_filtered', 0)}")
                click.echo(f"  ML Predictions: {performance.get('ml_predictions', 0)}")
                click.echo(f"  Rule Fallbacks: {performance.get('rule_fallbacks', 0)}")
                click.echo(f"  Avg Inference: {performance.get('avg_inference_time', 0):.2f}ms")
            
            # Error metrics
            errors = health_status.get('errors', {})
            if errors:
                click.echo(f"\n⚠️  Error Metrics:")
                click.echo(f"  Total Errors: {errors.get('total', 0)}")
                error_rate = errors.get('error_rate', 0)
                click.echo(f"  Error Rate: {error_rate:.2%}")
                if errors.get('last_error_time'):
                    last_error = datetime.fromtimestamp(errors['last_error_time'])
                    click.echo(f"  Last Error: {last_error.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Circuit breaker status
            circuit_breaker = health_status.get('circuit_breaker', {})
            if circuit_breaker:
                click.echo(f"\n🔌 Circuit Breaker:")
                click.echo(f"  State: {circuit_breaker.get('state', 'unknown')}")
                click.echo(f"  Failures: {circuit_breaker.get('failure_count', 0)}")
                click.echo(f"  Successes: {circuit_breaker.get('success_count', 0)}")
            
            # Issues
            issues = health_status.get('issues', [])
            if issues:
                click.echo(f"\n🚨 Issues Detected:")
                for issue in issues:
                    click.echo(f"  • {issue}")
            
            # Recommendations
            if status == 'degraded':
                click.echo(f"\n💡 Recommendations:")
                if 'ML model not loaded' in issues:
                    click.echo("  • Check model files in configs/ml_models/")
                if 'Circuit breaker is open' in issues:
                    click.echo("  • Wait for circuit breaker to reset or check logs")
                if 'High inference latency' in issues:
                    click.echo("  • Consider reducing batch size or optimizing features")
                if 'High error rate' in issues:
                    click.echo("  • Check logs for specific error patterns")
            
            click.echo(f"\nHealth check completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    except Exception as e:
        click.echo(f"❌ Error checking ML health: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()


@cli.command()
@click.option('--format', 'output_format', type=click.Choice(['json', 'html', 'pdf']), 
              multiple=True, help='Report formats to generate (can specify multiple)')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory for reports')
@click.option('--from-last-scan', is_flag=True, default=True, help='Generate reports from last scan results')
def generate_report(output_format, output_dir, from_last_scan):
    """Generate reports from the last scan results."""
    if not from_last_scan:
        console.print("[yellow]⚠️ Only --from-last-scan is currently supported[/yellow]")
        return
    
    if not levox_cli.last_scan_results:
        console.print("[red]❌ No scan results available. Run a scan first with: levox scan <path>[/red]")
        return
    
    console.print(f"[bold cyan]📄 Generating reports from last scan...[/bold cyan]")
    console.print(f"[dim]Scan path: {levox_cli.last_scan_path}[/dim]")
    console.print(f"[dim]Scan time: {levox_cli.last_scan_time:.2f}s[/dim]")
    console.print(f"[dim]License tier: {levox_cli.last_license_tier}[/dim]")
    console.print()
    
    # Generate reports
    report_formats = list(output_format) if output_format else ['json']
    console.print(f"[dim]Generating reports in formats: {', '.join(report_formats)}[/dim]")
    
    reports = levox_cli.generate_reports(report_formats, output_dir)
    
    if reports:
        if output_dir:
            console.print(f"[green]✅ Reports saved to: {output_dir}[/green]")
            for format_type, file_path in reports.items():
                console.print(f"   📄 {format_type.upper()}: {file_path}")
        else:
            console.print("[green]✅ Reports generated successfully[/green]")
            for format_type, content in reports.items():
                if content:
                    console.print(f"   📄 {format_type.upper()}: {len(content)} characters")
    else:
        console.print("[red]❌ Failed to generate reports[/red]")


@cli.command()
def set_report_directory():
    """Choose where reports are saved using Windows Explorer."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        import os
        
        # Hide the main tkinter window
        root = tk.Tk()
        root.withdraw()
        
        # Open folder picker dialog
        folder_path = filedialog.askdirectory(
            title="Choose Directory for Levox Reports",
            initialdir=os.path.expanduser("~")
        )
        
        if folder_path:
            # Save the selected directory to configuration
            config_path = os.path.expanduser("~/.levox/config.yaml")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Load existing config or create new
            config = {}
            if os.path.exists(config_path):
                try:
                    import yaml
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f) or {}
                except:
                    pass
            
            # Update report directory
            config['report_directory'] = folder_path
            
            # Save updated config
            try:
                import yaml
                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                
                click.echo(f"✅ Report directory set to: {folder_path}")
                click.echo(f"📁 Reports will now be saved to: {folder_path}")
                click.echo(f"💾 Configuration saved to: {config_path}")
                
            except Exception as e:
                click.echo(f"❌ Failed to save configuration: {e}")
                click.echo(f"📁 Selected directory: {folder_path}")
                click.echo("💡 You can manually set this in your config file")
        else:
            click.echo("❌ No directory selected. Report directory unchanged.")
            
    except ImportError:
        click.echo("❌ tkinter not available. Please install tkinter or manually set report directory in config.")
    except Exception as e:
        click.echo(f"❌ Error setting report directory: {e}")


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Show detailed usage information')
def usage(verbose):
    """Show freemium feature usage status and remaining limits."""
    try:
        from levox.core.rate_limiter import get_rate_limiter
        
        limiter = get_rate_limiter()
        usage_summary = limiter.get_usage_summary()
        
        # Create beautiful usage table
        table = Table(
            title="🎯 Freemium Feature Usage Status",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        
        table.add_column("Feature", style="cyan", no_wrap=True)
        table.add_column("Used", style="yellow", justify="center")
        table.add_column("Limit", style="green", justify="center")
        table.add_column("Remaining", style="blue", justify="center")
        table.add_column("Reset Date", style="dim", justify="center")
        table.add_column("Status", style="bold", justify="center")
        
        if verbose:
            table.add_column("Last Used", style="dim", justify="center")
        
        # Add feature rows
        for feature_name, feature_data in usage_summary['features'].items():
            # Determine status and color
            if feature_data['can_use']:
                status = "✅ Available"
                status_style = "green"
            else:
                status = "❌ Limit Reached"
                status_style = "red"
            
            # Format reset date
            reset_date = feature_data['reset_date'].strftime('%Y-%m-%d') if feature_data['reset_date'] else 'N/A'
            
            # Format last used
            last_used = feature_data['last_used'].strftime('%Y-%m-%d %H:%M') if feature_data['last_used'] else 'Never'
            
            # Add row
            row_data = [
                feature_name.replace('_', ' ').title(),
                str(feature_data['usage_count']),
                str(feature_data['monthly_limit']),
                str(feature_data['remaining_uses']),
                reset_date,
                status
            ]
            
            if verbose:
                row_data.append(last_used)
            
            table.add_row(*row_data)
        
        # Display summary
        console.print()
        console.print(Panel(
            f"[bold cyan]📊 Usage Summary[/bold cyan]\n"
            f"Total Features: {usage_summary['total_features']}\n"
            f"Available: {usage_summary['features_available']} ✅\n"
            f"At Limit: {usage_summary['features_at_limit']} ❌",
            title="🎯 Freemium Status",
            border_style="cyan"
        ))
        
        console.print()
        console.print(table)
        
        # Show helpful information
        if usage_summary['features_at_limit'] > 0:
            console.print()
            console.print(Panel(
                "[bold yellow]💡 Feature Limit Reached[/bold yellow]\n"
                "Some features have reached their monthly usage limit.\n"
                "They will be automatically reset on the 1st of next month.\n"
                "Upgrade to Premium/Enterprise for unlimited usage!",
                border_style="yellow"
            ))
        
        console.print()
        console.print(Panel(
            "[bold blue]🔧 Usage Tracking[/bold blue]\n"
            "Usage is tracked per feature and resets monthly.\n"
            "Data is stored locally in ~/.levox/feature_usage.json\n"
            "Run 'levox usage --verbose' for detailed information.",
            border_style="blue"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Failed to get usage status: {e}[/red]")
        return EXIT_RUNTIME_ERROR
    
    return EXIT_SUCCESS


@cli.command()
@click.argument('feature_name', required=False)
@click.option('--all', is_flag=True, help='Reset all feature usage')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def reset_usage(feature_name, all, confirm):
    """Reset feature usage for a specific feature or all features."""
    try:
        from levox.core.rate_limiter import get_rate_limiter
        
        limiter = get_rate_limiter()
        
        if all:
            if confirm:
                limiter.reset_all_usage()
                console.print("[green]✅ All feature usage has been reset.[/green]")
            else:
                console.print("[yellow]⚠️ Are you sure you want to reset all feature usage?[/yellow]")
                console.print("[bold]Enter 'yes' to confirm:[/bold]")
                if click.prompt().lower() == 'yes':
                    limiter.reset_all_usage()
                    console.print("[green]✅ All feature usage has been reset.[/green]")
                else:
                    console.print("[red]❌ Reset cancelled.[/red]")
        else:
            if feature_name:
                if confirm:
                    limiter.reset_feature_usage(feature_name)
                    console.print(f"[green]✅ Usage for '{feature_name}' has been reset.[/green]")
                else:
                    console.print(f"[yellow]⚠️ Are you sure you want to reset usage for '{feature_name}'?[/yellow]")
                    console.print("[bold]Enter 'yes' to confirm:[/bold]")
                    if click.prompt().lower() == 'yes':
                        limiter.reset_feature_usage(feature_name)
                        console.print(f"[green]✅ Usage for '{feature_name}' has been reset.[/green]")
                    else:
                        console.print("[red]❌ Reset cancelled.[/red]")
            else:
                console.print("[red]❌ No feature name provided.[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error resetting usage: {e}[/red]")


if __name__ == '__main__':
    cli()
