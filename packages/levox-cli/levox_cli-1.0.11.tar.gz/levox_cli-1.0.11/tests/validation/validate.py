#!/usr/bin/env python3
"""
Levox Validation Framework CLI

This script provides a command-line interface for running the Levox validation
framework, including benchmarking against other security tools and generating
interactive reports.
"""

import os
import sys
import json
import time
import webbrowser
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import logging
import subprocess
from datetime import datetime

# Add the parent directory to the path to import validation modules
sys.path.insert(0, str(Path(__file__).parent))

from validation_framework import LevoxValidator, ValidationSummary
from benchmark_framework import SecurityToolBenchmarker

def setup_logging(verbose: bool = False, quiet: bool = False):
    """Setup logging configuration."""
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('validation.log')
        ]
    )

def print_banner():
    """Print the validation framework banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    LEVOX VALIDATION FRAMEWORK                ║
║                                                              ║
║  Comprehensive Security Tool Validation & Benchmarking      ║
║  Version 2.0.0                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_config_info(use_cli: bool, benchmark: bool, dashboard: bool):
    """Print configuration information."""
    print("Configuration:")
    print(f"  Mode:           {'CLI' if use_cli else 'Engine'}")
    print(f"  Benchmarking:   {'Enabled' if benchmark else 'Disabled'}")
    print(f"  Dashboard:      {'Enabled' if dashboard else 'Disabled'}")
    print(f"  Timestamp:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def run_validation(use_cli: bool = True, output_file: str = None, 
                   markdown: bool = True) -> ValidationSummary:
    """Run the validation suite."""
    print("🚀 Starting Levox validation suite...")
    
    try:
        # Create validator
        validator = LevoxValidator(use_cli=use_cli)
        
        # Run validation suite
        summary = validator.run_validation_suite()
        
        # Save results
        if output_file:
            validator.save_results(summary, output_file)
        else:
            validator.save_results(summary)
        
        # Generate Markdown summary
        if markdown:
            markdown_file = validator.generate_markdown_summary(summary)
            print(f"📝 Markdown summary generated: {markdown_file}")
        
        print("✅ Validation suite completed successfully!")
        return summary
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        raise

def run_benchmark(tools: List[str] = None, files: List[str] = None,
                  output_file: str = None, report_format: str = 'markdown') -> Dict[str, Any]:
    """Run benchmarking against other security tools."""
    print("🔬 Starting security tool benchmarking...")
    
    try:
        # Create benchmarker
        benchmarker = SecurityToolBenchmarker()
        
        # Run benchmark
        summary = benchmarker.run_benchmark(tools=tools, files=files)
        
        # Save results
        if output_file:
            benchmarker.save_benchmark_results(summary, output_file)
        else:
            benchmarker.save_benchmark_results(summary)
        
        # Generate report
        report = benchmarker.generate_comparative_report(summary, report_format)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = benchmarker.results_dir / f"benchmark_report_{timestamp}.{report_format}"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 Benchmark completed successfully!")
        print(f"📁 Results saved to: {benchmarker.results_dir}")
        print(f"📄 Report saved to: {report_file}")
        
        return {
            'summary': summary,
            'results_dir': str(benchmarker.results_dir),
            'report_file': str(report_file)
        }
        
    except Exception as e:
        print(f"❌ Benchmarking failed: {e}")
        raise

def generate_dashboard_html(validation_summary: ValidationSummary, 
                           benchmark_results: Dict[str, Any] = None) -> str:
    """Generate an interactive HTML dashboard."""
    
    # Create dashboard HTML
    dashboard_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Levox Validation Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
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
            font-size: 1.1em;
        }}
        .content {{
            padding: 30px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .status-passed {{
            color: #4caf50;
        }}
        .status-failed {{
            color: #f44336;
        }}
        .chart-container {{
            margin: 30px 0;
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .chart-title {{
            text-align: center;
            margin-bottom: 20px;
            color: #333;
            font-size: 1.3em;
        }}
        .results-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .results-table th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #e0e0e0;
        }}
        .results-table td {{
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .results-table tr:hover {{
            background-color: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
            text-transform: uppercase;
        }}
        .badge-pass {{
            background: #e8f5e8;
            color: #4caf50;
        }}
        .badge-fail {{
            background: #ffebee;
            color: #f44336;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #e0e0e0;
            margin-top: 30px;
        }}
        .refresh-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 20px 0;
        }}
        .refresh-btn:hover {{
            background: #5a6fd8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Levox Validation Dashboard</h1>
            <p>Security Tool Validation & Benchmarking Results</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Dashboard</button>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Overall Status</div>
                    <div class="metric-value status-{'passed' if validation_summary.validation_passed else 'failed'}">
                        {'✅ PASSED' if validation_summary.validation_passed else '❌ FAILED'}
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Overall Score</div>
                    <div class="metric-value">{validation_summary.overall_score:.3f}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Files Tested</div>
                    <div class="metric-value">{validation_summary.total_files}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Success Rate</div>
                    <div class="metric-value">{((validation_summary.passed_files / validation_summary.total_files) * 100):.1f}%</div>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Detection Metrics</div>
                <canvas id="metricsChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Confusion Matrix</div>
                <canvas id="confusionChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Test Results Breakdown</div>
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Type</th>
                            <th>Expected</th>
                            <th>Detected</th>
                            <th>Score</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Add test results
    for result in validation_summary.results:
        file_type = "Positive" if "positives" in result.file_path else "Negative"
        status_class = "pass" if result.passed else "fail"
        status_text = "PASS" if result.passed else "FAIL"
        
        dashboard_html += f"""
                        <tr>
                            <td>{Path(result.file_path).name}</td>
                            <td>{file_type}</td>
                            <td>{result.expected_issues}</td>
                            <td>{result.actual_issues}</td>
                            <td>{result.score:.3f}</td>
                            <td><span class="badge badge-{status_class}">{status_text}</span></td>
                        </tr>
"""
    
    dashboard_html += """
                    </tbody>
                </table>
            </div>
"""
    
    # Add benchmark results if available
    if benchmark_results:
        dashboard_html += f"""
            <div class="chart-container">
                <div class="chart-title">Benchmark Results</div>
                <p>Benchmark results available in: {benchmark_results.get('report_file', 'N/A')}</p>
                <p>Results directory: {benchmark_results.get('results_dir', 'N/A')}</p>
            </div>
"""
    
    dashboard_html += """
        </div>
        
        <div class="footer">
            <p>Levox Validation Framework v2.0.0 | Generated automatically</p>
        </div>
    </div>
    
    <script>
        // Metrics Chart
        const metricsCtx = document.getElementById('metricsChart').getContext('2d');
        new Chart(metricsCtx, {
            type: 'radar',
            data: {
                labels: ['Precision', 'Recall', 'F1-Score'],
                datasets: [{
                    label: 'Current Score',
                    data: ["""
    
    dashboard_html += f"{validation_summary.precision:.3f}, {validation_summary.recall:.3f}, {validation_summary.f1_score:.3f}"
    
    dashboard_html += """],
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            stepSize: 0.2
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        // Confusion Matrix Chart
        const confusionCtx = document.getElementById('confusionChart').getContext('2d');
        new Chart(confusionCtx, {
            type: 'doughnut',
            data: {
                labels: ['True Positives', 'False Positives', 'False Negatives', 'True Negatives'],
                datasets: [{
                    data: ["""
    
    dashboard_html += f"{validation_summary.true_positives}, {validation_summary.false_positives}, {validation_summary.false_negatives}, {validation_summary.true_negatives}"
    
    dashboard_html += """],
                    backgroundColor: [
                        '#4caf50',
                        '#ff9800',
                        '#f44336',
                        '#2196f3'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
    
    return dashboard_html

def launch_dashboard(validation_summary: ValidationSummary, 
                    benchmark_results: Dict[str, Any] = None,
                    port: int = 8000):
    """Launch a local web server to serve the dashboard."""
    try:
        # Generate dashboard HTML
        dashboard_html = generate_dashboard_html(validation_summary, benchmark_results)
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(dashboard_html)
            temp_file = f.name
        
        # Try to use Python's built-in HTTP server
        try:
            import http.server
            import socketserver
            import threading
            
            # Change to directory containing the temp file
            temp_dir = os.path.dirname(temp_file)
            temp_filename = os.path.basename(temp_file)
            
            class Handler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/':
                        self.path = f'/{temp_filename}'
                    return http.server.SimpleHTTPRequestHandler.do_GET(self)
            
            with socketserver.TCPServer(("", port), Handler) as httpd:
                print(f"🌐 Dashboard server started on http://localhost:{port}")
                print(f"📁 Serving dashboard from: {temp_file}")
                print("🔄 Press Ctrl+C to stop the server")
                
                # Open browser
                webbrowser.open(f'http://localhost:{port}')
                
                # Start server in a separate thread
                server_thread = threading.Thread(target=httpd.serve_forever)
                server_thread.daemon = True
                server_thread.start()
                
                try:
                    # Keep main thread alive
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down dashboard server...")
                    httpd.shutdown()
                    
        except Exception as e:
            print(f"⚠️  Could not start HTTP server: {e}")
            print(f"📄 Dashboard HTML saved to: {temp_file}")
            print("🌐 Open this file in your web browser to view the dashboard")
            
            # Try to open the file directly
            try:
                webbrowser.open(f'file://{temp_file}')
            except:
                pass
    
    except Exception as e:
        print(f"❌ Failed to launch dashboard: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Levox Validation Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run basic validation
  python validate.py
  
  # Run validation with CLI mode
  python validate.py --cli
  
  # Run validation with engine mode
  python validate.py --engine
  
  # Run benchmarking against Semgrep
  python validate.py --benchmark
  
  # Run validation and benchmarking
  python validate.py --benchmark --tools levox semgrep
  
  # Launch interactive dashboard
  python validate.py --dashboard
  
  # Full validation with benchmarking and dashboard
  python validate.py --benchmark --dashboard --verbose
        """
    )
    
    # Validation options
    parser.add_argument("--cli", action="store_true", 
                       help="Use CLI mode for Levox scanning")
    parser.add_argument("--engine", action="store_true", 
                       help="Use engine mode for Levox scanning")
    parser.add_argument("--output", 
                       help="Output file for validation results")
    parser.add_argument("--markdown", action="store_true", default=True,
                       help="Generate Markdown summary (default: True)")
    
    # Benchmarking options
    parser.add_argument("--benchmark", action="store_true",
                       help="Run benchmarking against other security tools")
    parser.add_argument("--tools", nargs="+", 
                       choices=['levox', 'semgrep'],
                       default=['levox', 'semgrep'],
                       help="Tools to benchmark (default: levox, semgrep)")
    parser.add_argument("--files", nargs="+",
                       help="Specific files to test during benchmarking")
    parser.add_argument("--benchmark-output",
                       help="Output file for benchmark results")
    parser.add_argument("--report-format", 
                       choices=['markdown', 'html'],
                       default='markdown',
                       help="Benchmark report format (default: markdown)")
    
    # Dashboard options
    parser.add_argument("--dashboard", action="store_true",
                       help="Launch interactive HTML dashboard")
    parser.add_argument("--port", type=int, default=8000,
                       help="Port for dashboard server (default: 8000)")
    
    # General options
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Suppress output")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose, quiet=args.quiet)
    
    # Print banner
    print_banner()
    
    # Determine scanning mode
    use_cli = args.cli or not args.engine
    
    # Print configuration
    print_config_info(use_cli, args.benchmark, args.dashboard)
    
    try:
        validation_summary = None
        benchmark_results = None
        
        # Run validation
        if not args.benchmark or 'levox' in args.tools:
            validation_summary = run_validation(
                use_cli=use_cli,
                output_file=args.output,
                markdown=args.markdown
            )
            
            # Print summary
            validator = LevoxValidator(use_cli=use_cli)
            validator.print_summary(validation_summary)
        
        # Run benchmarking
        if args.benchmark:
            benchmark_results = run_benchmark(
                tools=args.tools,
                files=args.files,
                output_file=args.benchmark_output,
                report_format=args.report_format
            )
        
        # Launch dashboard
        if args.dashboard:
            if validation_summary is None:
                print("❌ Cannot launch dashboard without validation results")
                print("   Run validation first or use --benchmark with levox tool")
            else:
                print("🚀 Launching interactive dashboard...")
                launch_dashboard(validation_summary, benchmark_results, args.port)
        
        # Exit with appropriate code
        if validation_summary and not validation_summary.validation_passed:
            print("\n❌ Validation failed - some metrics below threshold")
            sys.exit(1)
        else:
            print("\n✅ All operations completed successfully")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n🛑 Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Operation failed: {e}")
        if args.verbose:
            logging.exception("Error details:")
        sys.exit(1)

if __name__ == "__main__":
    main()
