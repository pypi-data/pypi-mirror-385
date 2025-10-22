#!/usr/bin/env python3
"""
Levox Benchmarking Framework

This module provides benchmarking capabilities to compare Levox against other
security scanning tools like Semgrep, generating comparative reports.
"""

import os
import sys
import json
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import csv
import yaml

# Add the parent directory to the path to import validation framework
sys.path.insert(0, str(Path(__file__).parent))

from validation_framework import LevoxValidator, ValidationResult, ValidationSummary

@dataclass
class ToolResult:
    """Result from a single tool scan."""
    tool_name: str
    file_path: str
    issues_found: int
    scan_duration: float
    issues: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

@dataclass
class BenchmarkResult:
    """Result from benchmarking multiple tools."""
    test_file: str
    tool_results: Dict[str, ToolResult] = field(default_factory=dict)
    ground_truth: Dict[str, Any] = field(default_factory=dict)
    comparison: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BenchmarkSummary:
    """Summary of all benchmark results."""
    total_files: int
    tools_tested: List[str]
    overall_metrics: Dict[str, Dict[str, float]]
    tool_comparison: Dict[str, Any]
    total_duration: float
    results: List[BenchmarkResult] = field(default_factory=list)

class SecurityToolBenchmarker:
    """Benchmark multiple security scanning tools."""
    
    def __init__(self, test_dir: str = None):
        """Initialize the benchmarker."""
        self.test_dir = Path(test_dir) if test_dir else Path(__file__).parent
        self.ground_truth_path = self.test_dir / "ground_truth.json"
        self.results_dir = self.test_dir / "benchmark_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Load ground truth
        self._load_ground_truth()
        
        # Initialize tools
        self.tools = {
            'levox': self._scan_with_levox,
            'semgrep': self._scan_with_semgrep
        }
        
        # Tool configurations
        self.tool_configs = {
            'semgrep': {
                'python_rules': ['python.security', 'python.security.audit'],
                'javascript_rules': ['javascript.security', 'javascript.security.audit'],
                'java_rules': ['java.security', 'java.security.audit']
            }
        }
    
    def _setup_logging(self):
        """Setup logging configuration."""
        self.logger = logging.getLogger("SecurityToolBenchmarker")
        self.logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
    
    def _load_ground_truth(self):
        """Load ground truth data."""
        try:
            with open(self.ground_truth_path, 'r', encoding='utf-8') as f:
                self.ground_truth = json.load(f)
            self.logger.info(f"Loaded ground truth with {len(self.ground_truth['test_files'])} test files")
        except Exception as e:
            self.logger.error(f"Failed to load ground truth: {e}")
            raise
    
    def _scan_with_levox(self, file_path: str) -> ToolResult:
        """Scan a file with Levox."""
        start_time = time.time()
        
        try:
            # Use the validation framework's Levox integration
            validator = LevoxValidator(use_cli=True)
            
            # Get ground truth for this file
            relative_path = str(Path(file_path).relative_to(self.test_dir))
            if relative_path in self.ground_truth['test_files']:
                ground_truth_data = self.ground_truth['test_files'][relative_path]
                
                # Run validation
                result = validator.validate_file(file_path, ground_truth_data)
                
                scan_duration = time.time() - start_time
                
                return ToolResult(
                    tool_name='levox',
                    file_path=file_path,
                    issues_found=result.actual_issues,
                    scan_duration=scan_duration,
                    issues=result.detected_issues,
                    errors=result.errors
                )
            else:
                # File not in ground truth, run basic scan
                issues, scan_duration = validator._run_levox_cli_scan(file_path)
                
                return ToolResult(
                    tool_name='levox',
                    file_path=file_path,
                    issues_found=len(issues),
                    scan_duration=scan_duration,
                    issues=issues
                )
                
        except Exception as e:
            scan_duration = time.time() - start_time
            return ToolResult(
                tool_name='levox',
                file_path=file_path,
                issues_found=0,
                scan_duration=scan_duration,
                errors=[str(e)]
            )
    
    def _scan_with_semgrep(self, file_path: str) -> ToolResult:
        """Scan a file with Semgrep."""
        start_time = time.time()
        
        try:
            # Determine file type and select appropriate rules
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.py':
                rules = self.tool_configs['semgrep']['python_rules']
            elif file_ext in ['.js', '.jsx']:
                rules = self.tool_configs['semgrep']['javascript_rules']
            elif file_ext == '.java':
                rules = self.tool_configs['semgrep']['java_rules']
            else:
                rules = ['security']
            
            # Run Semgrep
            cmd = [
                'semgrep', 'scan',
                '--config', ','.join(rules),
                '--json',
                # '--quiet',  # Flag not supported in current CLI
                str(file_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            scan_duration = time.time() - start_time
            
            if result.returncode == 0:
                try:
                    # Parse Semgrep JSON output
                    semgrep_results = json.loads(result.stdout)
                    
                    # Extract issues
                    issues = []
                    if 'results' in semgrep_results:
                        for finding in semgrep_results['results']:
                            issue = {
                                'category': finding.get('check_id', 'unknown'),
                                'severity': finding.get('extra', {}).get('severity', 'MEDIUM'),
                                'description': finding.get('extra', {}).get('message', ''),
                                'line': finding.get('start', {}).get('line', 0),
                                'pattern_name': finding.get('check_id', ''),
                                'confidence': 1.0
                            }
                            issues.append(issue)
                    
                    return ToolResult(
                        tool_name='semgrep',
                        file_path=file_path,
                        issues_found=len(issues),
                        scan_duration=scan_duration,
                        issues=issues
                    )
                    
                except json.JSONDecodeError:
                    return ToolResult(
                        tool_name='semgrep',
                        file_path=file_path,
                        issues_found=0,
                        scan_duration=scan_duration,
                        errors=['Failed to parse Semgrep output']
                    )
            else:
                return ToolResult(
                    tool_name='semgrep',
                    file_path=file_path,
                    issues_found=0,
                    scan_duration=scan_duration,
                    errors=[result.stderr or 'Semgrep scan failed']
                )
                
        except subprocess.TimeoutExpired:
            scan_duration = time.time() - start_time
            return ToolResult(
                tool_name='semgrep',
                file_path=file_path,
                issues_found=0,
                scan_duration=scan_duration,
                errors=['Semgrep scan timed out']
            )
        except Exception as e:
            scan_duration = time.time() - start_time
            return ToolResult(
                tool_name='semgrep',
                file_path=file_path,
                issues_found=0,
                scan_duration=scan_duration,
                errors=[str(e)]
            )
    
    def _calculate_comparison_metrics(self, benchmark_result: BenchmarkResult) -> Dict[str, Any]:
        """Calculate comparison metrics between tools."""
        comparison = {}
        
        # Get ground truth for this file
        relative_path = str(Path(benchmark_result.test_file).relative_to(self.test_dir))
        if relative_path in self.ground_truth['test_files']:
            ground_truth_data = self.ground_truth['test_files'][relative_path]
            expected_issues = ground_truth_data.get('expected_issue_count', {})
            expected_min = expected_issues.get('min', 0)
            expected_max = expected_issues.get('max', 0)
            is_positive_test = 'positives' in relative_path
            
            for tool_name, tool_result in benchmark_result.tool_results.items():
                # Calculate precision, recall, F1-score
                if is_positive_test:
                    if expected_min <= tool_result.issues_found <= expected_max:
                        precision = 1.0 if tool_result.issues_found > 0 else 0.0
                        recall = 1.0
                        f1_score = 1.0 if tool_result.issues_found > 0 else 0.0
                    else:
                        precision = 0.0
                        recall = 0.0
                        f1_score = 0.0
                else:
                    if tool_result.issues_found == 0:
                        precision = 1.0
                        recall = 1.0
                        f1_score = 1.0
                    else:
                        precision = 0.0
                        recall = 1.0
                        f1_score = 0.0
                
                comparison[tool_name] = {
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1_score,
                    'issues_found': tool_result.issues_found,
                    'expected_min': expected_min,
                    'expected_max': expected_max,
                    'scan_duration': tool_result.scan_duration
                }
        
        return comparison
    
    def run_benchmark(self, tools: List[str] = None, files: List[str] = None) -> BenchmarkSummary:
        """Run benchmark on specified tools and files."""
        if tools is None:
            tools = list(self.tools.keys())
        
        if files is None:
            # Get all test files from ground truth
            files = []
            for file_path in self.ground_truth['test_files'].keys():
                full_path = self.test_dir / file_path
                if full_path.exists():
                    files.append(str(full_path))
        
        self.logger.info(f"Starting benchmark with tools: {tools}")
        self.logger.info(f"Testing {len(files)} files")
        
        start_time = time.time()
        results = []
        
        for file_path in files:
            self.logger.info(f"Benchmarking file: {file_path}")
            
            benchmark_result = BenchmarkResult(
                test_file=file_path,
                ground_truth=self.ground_truth['test_files'].get(
                    str(Path(file_path).relative_to(self.test_dir)), {}
                )
            )
            
            # Run each tool
            for tool_name in tools:
                if tool_name in self.tools:
                    self.logger.info(f"  Running {tool_name}...")
                    tool_result = self.tools[tool_name](file_path)
                    benchmark_result.tool_results[tool_name] = tool_result
            
            # Calculate comparison metrics
            benchmark_result.comparison = self._calculate_comparison_metrics(benchmark_result)
            results.append(benchmark_result)
        
        total_duration = time.time() - start_time
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(results, tools)
        
        # Create summary
        summary = BenchmarkSummary(
            total_files=len(files),
            tools_tested=tools,
            overall_metrics=overall_metrics,
            tool_comparison=self._create_tool_comparison(results, tools),
            total_duration=total_duration,
            results=results
        )
        
        self.logger.info(f"Benchmark completed in {total_duration:.2f}s")
        return summary
    
    def _calculate_overall_metrics(self, results: List[BenchmarkResult], tools: List[str]) -> Dict[str, Dict[str, float]]:
        """Calculate overall metrics for each tool."""
        overall_metrics = {}
        
        for tool_name in tools:
            tool_results = [r for r in results if tool_name in r.tool_results]
            
            if not tool_results:
                continue
            
            # Calculate averages
            total_precision = sum(r.comparison.get(tool_name, {}).get('precision', 0) for r in tool_results)
            total_recall = sum(r.comparison.get(tool_name, {}).get('recall', 0) for r in tool_results)
            total_f1 = sum(r.comparison.get(tool_name, {}).get('f1_score', 0) for r in tool_results)
            total_duration = sum(r.tool_results[tool_name].scan_duration for r in tool_results)
            
            count = len(tool_results)
            
            overall_metrics[tool_name] = {
                'avg_precision': total_precision / count if count > 0 else 0.0,
                'avg_recall': total_recall / count if count > 0 else 0.0,
                'avg_f1_score': total_f1 / count if count > 0 else 0.0,
                'avg_scan_duration': total_duration / count if count > 0 else 0.0,
                'total_files_scanned': count
            }
        
        return overall_metrics
    
    def _create_tool_comparison(self, results: List[BenchmarkResult], tools: List[str]) -> Dict[str, Any]:
        """Create detailed tool comparison."""
        comparison = {
            'performance': {},
            'accuracy': {},
            'file_breakdown': {}
        }
        
        for tool_name in tools:
            tool_results = [r for r in results if tool_name in r.tool_results]
            
            if not tool_results:
                continue
            
            # Performance comparison
            scan_durations = [r.tool_results[tool_name].scan_duration for r in tool_results]
            comparison['performance'][tool_name] = {
                'total_time': sum(scan_durations),
                'avg_time': sum(scan_durations) / len(scan_durations),
                'min_time': min(scan_durations),
                'max_time': max(scan_durations)
            }
            
            # Accuracy comparison
            f1_scores = [r.comparison.get(tool_name, {}).get('f1_score', 0) for r in tool_results]
            comparison['accuracy'][tool_name] = {
                'avg_f1_score': sum(f1_scores) / len(f1_scores),
                'perfect_scores': sum(1 for score in f1_scores if score == 1.0),
                'failed_scores': sum(1 for score in f1_scores if score == 0.0)
            }
            
            # File breakdown
            file_breakdown = {}
            for r in tool_results:
                file_type = 'positive' if 'positives' in r.test_file else 'negative'
                if file_type not in file_breakdown:
                    file_breakdown[file_type] = {'total': 0, 'passed': 0}
                
                file_breakdown[file_type]['total'] += 1
                if r.comparison.get(tool_name, {}).get('f1_score', 0) == 1.0:
                    file_breakdown[file_type]['passed'] += 1
            
            comparison['file_breakdown'][tool_name] = file_breakdown
        
        return comparison
    
    def save_benchmark_results(self, summary: BenchmarkSummary, output_file: str = None):
        """Save benchmark results to file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.results_dir / f"benchmark_results_{timestamp}.json"
        
        # Convert to serializable format
        results_data = {
            'summary': {
                'total_files': summary.total_files,
                'tools_tested': summary.tools_tested,
                'total_duration': summary.total_duration
            },
            'overall_metrics': summary.overall_metrics,
            'tool_comparison': summary.tool_comparison,
            'results': []
        }
        
        for result in summary.results:
            result_data = {
                'test_file': result.test_file,
                'ground_truth': result.ground_truth,
                'tool_results': {},
                'comparison': result.comparison
            }
            
            for tool_name, tool_result in result.tool_results.items():
                result_data['tool_results'][tool_name] = {
                    'issues_found': tool_result.issues_found,
                    'scan_duration': tool_result.scan_duration,
                    'errors': tool_result.errors
                }
            
            results_data['results'].append(result_data)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Benchmark results saved to: {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save benchmark results: {e}")
    
    def generate_comparative_report(self, summary: BenchmarkSummary, output_format: str = 'markdown') -> str:
        """Generate a comparative report."""
        if output_format == 'markdown':
            return self._generate_markdown_report(summary)
        elif output_format == 'html':
            return self._generate_html_report(summary)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_markdown_report(self, summary: BenchmarkSummary) -> str:
        """Generate Markdown report."""
        report = []
        
        # Header
        report.append("# Security Tool Benchmark Report")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Files:** {summary.total_files}")
        report.append(f"**Tools Tested:** {', '.join(summary.tools_tested)}")
        report.append(f"**Total Duration:** {summary.total_duration:.2f}s")
        report.append("")
        
        # Overall Metrics
        report.append("## Overall Metrics")
        report.append("")
        
        for tool_name, metrics in summary.overall_metrics.items():
            report.append(f"### {tool_name.title()}")
            report.append(f"- **Average Precision:** {metrics['avg_precision']:.3f}")
            report.append(f"- **Average Recall:** {metrics['avg_recall']:.3f}")
            report.append(f"- **Average F1-Score:** {metrics['avg_f1_score']:.3f}")
            report.append(f"- **Average Scan Duration:** {metrics['avg_scan_duration']:.3f}s")
            report.append(f"- **Files Scanned:** {metrics['total_files_scanned']}")
            report.append("")
        
        # Tool Comparison
        report.append("## Tool Comparison")
        report.append("")
        
        # Performance comparison
        report.append("### Performance Comparison")
        report.append("")
        report.append("| Tool | Total Time | Avg Time | Min Time | Max Time |")
        report.append("|------|------------|----------|----------|----------|")
        
        for tool_name in summary.tools_tested:
            if tool_name in summary.tool_comparison['performance']:
                perf = summary.tool_comparison['performance'][tool_name]
                report.append(f"| {tool_name.title()} | {perf['total_time']:.3f}s | {perf['avg_time']:.3f}s | {perf['min_time']:.3f}s | {perf['max_time']:.3f}s |")
        report.append("")
        
        # Accuracy comparison
        report.append("### Accuracy Comparison")
        report.append("")
        report.append("| Tool | Avg F1-Score | Perfect Scores | Failed Scores |")
        report.append("|------|--------------|----------------|---------------|")
        
        for tool_name in summary.tools_tested:
            if tool_name in summary.tool_comparison['accuracy']:
                acc = summary.tool_comparison['accuracy'][tool_name]
                report.append(f"| {tool_name.title()} | {acc['avg_f1_score']:.3f} | {acc['perfect_scores']} | {acc['failed_scores']} |")
        report.append("")
        
        # File breakdown
        report.append("### File Breakdown")
        report.append("")
        
        for tool_name in summary.tools_tested:
            if tool_name in summary.tool_comparison['file_breakdown']:
                breakdown = summary.tool_comparison['file_breakdown'][tool_name]
                report.append(f"#### {tool_name.title()}")
                
                for file_type, stats in breakdown.items():
                    if stats['total'] > 0:
                        success_rate = (stats['passed'] / stats['total']) * 100
                        report.append(f"- **{file_type.title()} Files:** {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
                report.append("")
        
        return "\n".join(report)
    
    def _generate_html_report(self, summary: BenchmarkSummary) -> str:
        """Generate HTML report."""
        # This is a simplified HTML report - you can enhance it further
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Tool Benchmark Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .metric {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Security Tool Benchmark Report</h1>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Total Files:</strong> {summary.total_files}</p>
            <p><strong>Tools Tested:</strong> {', '.join(summary.tools_tested)}</p>
            <p><strong>Total Duration:</strong> {summary.total_duration:.2f}s</p>
            
            <div class="metric">
                <h2>Overall Metrics</h2>
                <table>
                    <tr>
                        <th>Tool</th>
                        <th>Avg Precision</th>
                        <th>Avg Recall</th>
                        <th>Avg F1-Score</th>
                        <th>Avg Scan Duration</th>
                    </tr>
        """
        
        for tool_name, metrics in summary.overall_metrics.items():
            html += f"""
                    <tr>
                        <td>{tool_name.title()}</td>
                        <td>{metrics['avg_precision']:.3f}</td>
                        <td>{metrics['avg_recall']:.3f}</td>
                        <td>{metrics['avg_f1_score']:.3f}</td>
                        <td>{metrics['avg_scan_duration']:.3f}s</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
        </body>
        </html>
        """
        
        return html

def main():
    """Main entry point for benchmarking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Tool Benchmarking Framework")
    parser.add_argument("--tools", nargs="+", choices=['levox', 'semgrep'], 
                       default=['levox', 'semgrep'], help="Tools to benchmark")
    parser.add_argument("--files", nargs="+", help="Specific files to test")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--report-format", choices=['markdown', 'html'], 
                       default='markdown', help="Report format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create benchmarker
        benchmarker = SecurityToolBenchmarker()
        
        # Run benchmark
        summary = benchmarker.run_benchmark(tools=args.tools, files=args.files)
        
        # Save results
        if args.output:
            benchmarker.save_benchmark_results(summary, args.output)
        else:
            benchmarker.save_benchmark_results(summary)
        
        # Generate report
        report = benchmarker.generate_comparative_report(summary, args.report_format)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = benchmarker.results_dir / f"benchmark_report_{timestamp}.{args.report_format}"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Benchmark completed successfully!")
        print(f"Results saved to: {benchmarker.results_dir}")
        print(f"Report saved to: {report_file}")
        
        # Print summary
        print("\n" + "="*50)
        print("BENCHMARK SUMMARY")
        print("="*50)
        
        for tool_name, metrics in summary.overall_metrics.items():
            print(f"\n{tool_name.upper()}:")
            print(f"  F1-Score: {metrics['avg_f1_score']:.3f}")
            print(f"  Precision: {metrics['avg_precision']:.3f}")
            print(f"  Recall: {metrics['avg_recall']:.3f}")
            print(f"  Avg Scan Time: {metrics['avg_scan_duration']:.3f}s")
        
    except Exception as e:
        print(f"Benchmark failed: {e}")
        if args.verbose:
            logging.exception("Error details:")
        sys.exit(1)

if __name__ == "__main__":
    main()
