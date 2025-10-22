#!/usr/bin/env python3
"""
Levox Validation Framework

This module provides comprehensive validation capabilities for the Levox security
scanning tool, including issue detection, scoring, and reporting.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import csv
import yaml

@dataclass
class ValidationResult:
    """Result of validating a single test file."""
    file_path: str
    expected_issues: int
    actual_issues: int
    detected_issues: List[Dict[str, Any]] = field(default_factory=list)
    expected_categories: List[str] = field(default_factory=list)
    detected_categories: List[str] = field(default_factory=list)
    score: float = 0.0
    passed: bool = False
    errors: List[str] = field(default_factory=list)
    scan_duration: float = 0.0
    ground_truth: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationSummary:
    """Summary of all validation results."""
    total_files: int
    passed_files: int
    failed_files: int
    total_issues_detected: int
    total_issues_expected: int
    precision: float
    recall: float
    f1_score: float
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    overall_score: float
    validation_passed: bool
    results: List[ValidationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class LevoxValidator:
    """Main validator class for Levox security scanning."""
    
    def __init__(self, use_cli: bool = True, levox_path: str = None):
        """Initialize the validator."""
        self.use_cli = use_cli
        self.levox_path = levox_path or "levox"
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Load ground truth
        self._load_ground_truth()
        
        # Initialize issue categorization
        self._init_issue_categorization()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        self.logger = logging.getLogger("LevoxValidator")
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
        ground_truth_path = Path(__file__).parent / "ground_truth.json"
        try:
            with open(ground_truth_path, 'r', encoding='utf-8') as f:
                self.ground_truth = json.load(f)
            self.logger.info(f"Loaded ground truth with {len(self.ground_truth['test_files'])} test files")
        except Exception as e:
            self.logger.error(f"Failed to load ground truth: {e}")
            raise
    
    def _init_issue_categorization(self):
        """Initialize issue categorization patterns."""
        self.category_patterns = {
            'hardcoded_credentials': [
                'password', 'secret', 'api_key', 'token', 'credential', 'auth'
            ],
            'sql_injection': [
                'sql', 'query', 'database', 'injection', 'execute', 'cursor'
            ],
            'xss': [
                'xss', 'cross_site', 'script', 'html', 'dom', 'innerHTML'
            ],
            'weak_cryptography': [
                'md5', 'sha1', 'des', 'rc4', 'weak', 'crypto', 'hash'
            ],
            'pii_logging': [
                'email', 'phone', 'ssn', 'credit_card', 'personal', 'log'
            ],
            'path_traversal': [
                'path', 'file', 'directory', 'traversal', 'upload', 'download'
            ],
            'command_injection': [
                'command', 'shell', 'execute', 'system', 'subprocess', 'os'
            ],
            'xml_external_entity': [
                'xml', 'xxe', 'external', 'entity', 'parse', 'dom'
            ],
            'server_side_request_forgery': [
                'url', 'request', 'fetch', 'download', 'network', 'http'
            ],
            'unsafe_deserialization': [
                'pickle', 'deserialize', 'loads', 'marshal', 'yaml', 'json'
            ],
            'race_condition': [
                'thread', 'concurrent', 'race', 'lock', 'synchronize'
            ],
            'prototype_pollution': [
                'prototype', 'pollution', 'object', 'merge', 'assign'
            ]
        }
    
    def _run_levox_cli_scan(self, file_path: str) -> Tuple[List[Dict[str, Any]], float]:
        """Run Levox CLI scan and capture output."""
        start_time = time.time()
        
        try:
            # Run Levox CLI scan
            cmd = [
                self.levox_path, "scan",
                "--format", "json",
                # "--quiet",  # Flag not supported in current CLI
                str(file_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            
            scan_duration = time.time() - start_time
            
            if result.returncode == 0:
                try:
                    # Parse JSON output
                    scan_results = json.loads(result.stdout)
                    
                    # Extract issues
                    issues = []
                    if 'files' in scan_results:
                        for file_result in scan_results['files']:
                            if 'issues' in file_result:
                                issues.extend(file_result['issues'])
                    
                    return issues, scan_duration
                    
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse Levox output: {e}")
                    return [], scan_duration
            else:
                self.logger.warning(f"Levox CLI scan failed: {result.stderr}")
                return [], scan_duration
                
        except subprocess.TimeoutExpired:
            scan_duration = time.time() - start_time
            self.logger.warning("Levox CLI scan timed out")
            return [], scan_duration
        except Exception as e:
            scan_duration = time.time() - start_time
            self.logger.error(f"Levox CLI scan error: {e}")
            return [], scan_duration
    
    def _run_levox_engine_scan(self, file_path: str) -> Tuple[List[Dict[str, Any]], float]:
        """Run Levox engine scan directly."""
        start_time = time.time()
        
        try:
            # Import Levox engine
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from levox.core.engine import DetectionEngine
            
            # Initialize engine
            engine = DetectionEngine()
            
            # Scan file
            result = engine.scan_file(file_path)
            
            scan_duration = time.time() - start_time
            
            # Convert result to standard format
            issues = []
            if hasattr(result, 'matches'):
                for match in result.matches:
                    issues.append({
                        'category': getattr(match, 'pattern_name', 'unknown'),
                        'severity': getattr(match, 'risk_level', 'MEDIUM'),
                        'description': getattr(match, 'matched_text', ''),
                        'line': getattr(match, 'line_number', 0),
                        'pattern_name': getattr(match, 'pattern_name', ''),
                        'confidence': getattr(match, 'confidence', 1.0)
                    })
            
            return issues, scan_duration
            
        except Exception as e:
            scan_duration = time.time() - start_time
            self.logger.error(f"Levox engine scan error: {e}")
            return [], scan_duration
    
    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Categorize detected issues based on patterns."""
        categories = set()
        
        for issue in issues:
            description = issue.get('description', '').lower()
            pattern_name = issue.get('pattern_name', '').lower()
            
            for category, patterns in self.category_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in description or pattern.lower() in pattern_name:
                        categories.add(category)
                        break
        
        return list(categories)
    
    def _calculate_score(self, result: ValidationResult) -> float:
        """Calculate score for validation result."""
        if result.expected_issues == 0:
            # Negative test case
            if result.actual_issues == 0:
                return 1.0  # Perfect score
            else:
                return 0.0  # False positive
        else:
            # Positive test case
            if result.actual_issues == 0:
                return 0.0  # False negative
            else:
                # Calculate score based on issue count accuracy
                expected_range = result.ground_truth.get('expected_issue_count', {})
                expected_min = expected_range.get('min', result.expected_issues)
                expected_max = expected_range.get('max', result.expected_issues)
                
                if expected_min <= result.actual_issues <= expected_max:
                    return 1.0  # Perfect score
                else:
                    # Partial score based on how close we are
                    if result.actual_issues < expected_min:
                        return result.actual_issues / expected_min
                    else:
                        return expected_max / result.actual_issues
    
    def validate_file(self, file_path: str, ground_truth_data: Dict[str, Any]) -> ValidationResult:
        """Validate a single test file."""
        start_time = time.time()
        
        try:
            # Run scan
            if self.use_cli:
                issues, scan_duration = self._run_levox_cli_scan(file_path)
            else:
                issues, scan_duration = self._run_levox_engine_scan(file_path)
            
            # Get expected values
            expected_issues = ground_truth_data.get('expected_issue_count', {})
            expected_min = expected_issues.get('min', 0)
            expected_max = expected_issues.get('max', 0)
            expected_categories = []
            
            for issue_info in ground_truth_data.get('expected_issues', []):
                expected_categories.extend(issue_info.get('patterns', []))
            
            # Categorize detected issues
            detected_categories = self._categorize_issues(issues)
            
            # Create result
            result = ValidationResult(
                file_path=file_path,
                expected_issues=expected_max,
                actual_issues=len(issues),
                detected_issues=issues,
                expected_categories=expected_categories,
                detected_categories=detected_categories,
                scan_duration=scan_duration,
                ground_truth=ground_truth_data
            )
            
            # Calculate score
            result.score = self._calculate_score(result)
            result.passed = result.score >= 0.8  # 80% threshold
            
            return result
            
        except Exception as e:
            scan_duration = time.time() - start_time
            self.logger.error(f"Validation failed for {file_path}: {e}")
            
            return ValidationResult(
                file_path=file_path,
                expected_issues=0,
                actual_issues=0,
                score=0.0,
                passed=False,
                errors=[str(e)],
                scan_duration=scan_duration,
                ground_truth=ground_truth_data
            )
    
    def run_validation_suite(self) -> ValidationSummary:
        """Run validation suite on all test files."""
        self.logger.info("Starting validation suite...")
        
        start_time = time.time()
        results = []
        
        # Process each test file
        for file_path, ground_truth_data in self.ground_truth['test_files'].items():
            full_path = Path(__file__).parent / file_path
            
            if full_path.exists():
                self.logger.info(f"Validating: {file_path}")
                result = self.validate_file(str(full_path), ground_truth_data)
                results.append(result)
            else:
                self.logger.warning(f"Test file not found: {file_path}")
        
        # Calculate summary metrics
        summary = self._calculate_summary_metrics(results)
        summary.results = results
        summary.metadata = self.ground_truth.get('metadata', {})
        
        # Check if validation passed thresholds
        config = self.ground_truth.get('validation_config', {})
        scoring = config.get('scoring', {})
        
        precision_threshold = scoring.get('precision_threshold', 0.8)
        recall_threshold = scoring.get('recall_threshold', 0.8)
        f1_threshold = scoring.get('f1_threshold', 0.8)
        
        summary.validation_passed = (
            summary.precision >= precision_threshold and
            summary.recall >= recall_threshold and
            summary.f1_score >= f1_threshold
        )
        
        total_duration = time.time() - start_time
        self.logger.info(f"Validation suite completed in {total_duration:.2f}s")
        
        return summary
    
    def _calculate_summary_metrics(self, results: List[ValidationResult]) -> ValidationSummary:
        """Calculate summary metrics from validation results."""
        total_files = len(results)
        passed_files = sum(1 for r in results if r.passed)
        failed_files = total_files - passed_files
        
        # Calculate confusion matrix
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        true_negatives = 0
        
        total_issues_detected = 0
        total_issues_expected = 0
        
        for result in results:
            total_issues_detected += result.actual_issues
            total_issues_expected += result.expected_issues
            
            if result.expected_issues > 0:  # Positive test
                if result.actual_issues > 0:
                    true_positives += 1
                else:
                    false_negatives += 1
            else:  # Negative test
                if result.actual_issues > 0:
                    false_positives += 1
                else:
                    true_negatives += 1
        
        # Calculate metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Calculate overall score
        overall_score = sum(r.score for r in results) / len(results) if results else 0.0
        
        return ValidationSummary(
            total_files=total_files,
            passed_files=passed_files,
            failed_files=failed_files,
            total_issues_detected=total_issues_detected,
            total_issues_expected=total_issues_expected,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            true_negatives=true_negatives,
            overall_score=overall_score,
            validation_passed=False  # Will be set later
        )
    
    def save_results(self, summary: ValidationSummary, output_file: str = None):
        """Save validation results to file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.results_dir / f"validation_results_{timestamp}.json"
        
        # Convert to serializable format
        results_data = {
            'summary': {
                'total_files': summary.total_files,
                'passed_files': summary.passed_files,
                'failed_files': summary.failed_files,
                'total_issues_detected': summary.total_issues_detected,
                'total_issues_expected': summary.total_issues_expected,
                'precision': summary.precision,
                'recall': summary.recall,
                'f1_score': summary.f1_score,
                'true_positives': summary.true_positives,
                'false_positives': summary.false_positives,
                'false_negatives': summary.false_negatives,
                'true_negatives': summary.true_negatives,
                'overall_score': summary.overall_score,
                'validation_passed': summary.validation_passed,
                'timestamp': summary.timestamp
            },
            'metadata': summary.metadata,
            'results': []
        }
        
        for result in summary.results:
            result_data = {
                'file_path': result.file_path,
                'expected_issues': result.expected_issues,
                'actual_issues': result.actual_issues,
                'detected_categories': result.detected_categories,
                'expected_categories': result.expected_categories,
                'score': result.score,
                'passed': result.passed,
                'errors': result.errors,
                'scan_duration': result.scan_duration
            }
            results_data['results'].append(result_data)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Results saved to: {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
    
    def generate_markdown_summary(self, summary: ValidationSummary, output_file: str = None) -> str:
        """Generate Markdown summary report."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.results_dir / f"summary_{timestamp}.md"
        
        # Generate report content
        report = []
        
        # Header
        report.append("# Levox Validation Framework Report")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Version:** {summary.metadata.get('version', 'Unknown')}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        
        status_icon = "✅" if summary.validation_passed else "❌"
        report.append(f"{status_icon} **Overall Status:** {'PASSED' if summary.validation_passed else 'FAILED'}")
        report.append(f"📊 **Overall Score:** {summary.overall_score:.3f}")
        report.append(f"📁 **Files Tested:** {summary.total_files}")
        report.append(f"✅ **Passed:** {summary.passed_files}")
        report.append(f"❌ **Failed:** {summary.failed_files}")
        report.append("")
        
        # Key Metrics
        report.append("## Key Metrics")
        report.append("")
        
        report.append("| Metric | Value | Threshold | Status |")
        report.append("|--------|-------|-----------|--------|")
        
        config = self.ground_truth.get('validation_config', {})
        scoring = config.get('scoring', {})
        
        precision_threshold = scoring.get('precision_threshold', 0.8)
        recall_threshold = scoring.get('recall_threshold', 0.8)
        f1_threshold = scoring.get('f1_threshold', 0.8)
        
        precision_status = "✅" if summary.precision >= precision_threshold else "❌"
        recall_status = "✅" if summary.recall >= recall_threshold else "❌"
        f1_status = "✅" if summary.f1_score >= f1_threshold else "❌"
        
        report.append(f"| Precision | {summary.precision:.3f} | {precision_threshold} | {precision_status} |")
        report.append(f"| Recall | {summary.recall:.3f} | {recall_threshold} | {recall_status} |")
        report.append(f"| F1-Score | {summary.f1_score:.3f} | {f1_threshold} | {f1_status} |")
        report.append("")
        
        # Confusion Matrix
        report.append("## Confusion Matrix")
        report.append("")
        
        report.append("| | Predicted Positive | Predicted Negative |")
        report.append("|-------------------|---------------------|---------------------|")
        report.append(f"| **Actual Positive** | {summary.true_positives} (TP) | {summary.false_negatives} (FN) |")
        report.append(f"| **Actual Negative** | {summary.false_positives} (FP) | {summary.true_negatives} (TN) |")
        report.append("")
        
        # Issue Summary
        report.append("## Issue Summary")
        report.append("")
        report.append(f"- **Total Issues Expected:** {summary.total_issues_expected}")
        report.append(f"- **Total Issues Detected:** {summary.total_issues_detected}")
        report.append(f"- **Detection Rate:** {(summary.total_issues_detected / summary.total_issues_expected * 100):.1f}%" if summary.total_issues_expected > 0 else "- **Detection Rate:** N/A")
        report.append("")
        
        # Test Results Breakdown
        report.append("## Test Results Breakdown")
        report.append("")
        
        # Group results by type
        positive_results = [r for r in summary.results if 'positives' in r.file_path]
        negative_results = [r for r in summary.results if 'negatives' in r.file_path]
        
        if positive_results:
            report.append("### Positive Tests (Vulnerable Code)")
            report.append("")
            report.append("| File | Expected | Detected | Score | Status |")
            report.append("|------|----------|----------|-------|--------|")
            
            for result in positive_results:
                status = "✅" if result.passed else "❌"
                report.append(f"| {Path(result.file_path).name} | {result.expected_issues} | {result.actual_issues} | {result.score:.3f} | {status} |")
            report.append("")
        
        if negative_results:
            report.append("### Negative Tests (Clean Code)")
            report.append("")
            report.append("| File | Expected | Detected | Score | Status |")
            report.append("|------|----------|----------|-------|--------|")
            
            for result in negative_results:
                status = "✅" if result.passed else "❌"
                report.append(f"| {Path(result.file_path).name} | {result.expected_issues} | {result.actual_issues} | {result.score:.3f} | {status} |")
            report.append("")
        
        # Performance Metrics
        report.append("## Performance Metrics")
        report.append("")
        
        total_scan_time = sum(r.scan_duration for r in summary.results)
        avg_scan_time = total_scan_time / len(summary.results) if summary.results else 0
        
        report.append(f"- **Total Scan Time:** {total_scan_time:.3f}s")
        report.append(f"- **Average Scan Time:** {avg_scan_time:.3f}s")
        report.append(f"- **Files per Second:** {len(summary.results) / total_scan_time:.2f}" if total_scan_time > 0 else "- **Files per Second:** N/A")
        report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        
        if not summary.validation_passed:
            if summary.precision < precision_threshold:
                report.append("- **Improve Precision:** Reduce false positives by refining detection rules")
            if summary.recall < recall_threshold:
                report.append("- **Improve Recall:** Reduce false negatives by expanding detection coverage")
            if summary.f1_score < f1_threshold:
                report.append("- **Balance Precision/Recall:** Optimize detection thresholds for better F1-score")
        else:
            report.append("- **Maintain Performance:** Current detection capabilities meet quality thresholds")
            report.append("- **Monitor Trends:** Continue tracking metrics to prevent regression")
        
        report.append("")
        
        # Footer
        report.append("---")
        report.append(f"*Report generated by Levox Validation Framework v{summary.metadata.get('version', 'Unknown')}*")
        report.append(f"*Total test files: {summary.total_files} | Positive tests: {len(positive_results)} | Negative tests: {len(negative_results)}*")
        
        report_content = "\n".join(report)
        
        # Save to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            self.logger.info(f"Markdown summary saved to: {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save Markdown summary: {e}")
        
        return report_content
    
    def print_summary(self, summary: ValidationSummary):
        """Print validation summary to console."""
        print("\n" + "="*60)
        print("LEVOX VALIDATION FRAMEWORK - RESULTS SUMMARY")
        print("="*60)
        
        # Overall status
        status = "✅ PASSED" if summary.validation_passed else "❌ FAILED"
        print(f"Overall Status: {status}")
        print(f"Overall Score: {summary.overall_score:.3f}")
        print()
        
        # Key metrics
        print("Key Metrics:")
        print(f"  Precision: {summary.precision:.3f}")
        print(f"  Recall:    {summary.recall:.3f}")
        print(f"  F1-Score:  {summary.f1_score:.3f}")
        print()
        
        # File summary
        print("File Summary:")
        print(f"  Total Files: {summary.total_files}")
        print(f"  Passed:     {summary.passed_files}")
        print(f"  Failed:     {summary.failed_files}")
        print()
        
        # Issue summary
        print("Issue Summary:")
        print(f"  Expected Issues: {summary.total_issues_expected}")
        print(f"  Detected Issues: {summary.total_issues_detected}")
        if summary.total_issues_expected > 0:
            detection_rate = (summary.total_issues_detected / summary.total_issues_expected) * 100
            print(f"  Detection Rate:  {detection_rate:.1f}%")
        print()
        
        # Confusion matrix
        print("Confusion Matrix:")
        print(f"  True Positives:  {summary.true_positives}")
        print(f"  False Positives: {summary.false_positives}")
        print(f"  False Negatives: {summary.false_negatives}")
        print(f"  True Negatives:  {summary.true_negatives}")
        print()
        
        # Threshold evaluation
        config = self.ground_truth.get('validation_config', {})
        scoring = config.get('scoring', {})
        
        precision_threshold = scoring.get('precision_threshold', 0.8)
        recall_threshold = scoring.get('recall_threshold', 0.8)
        f1_threshold = scoring.get('f1_threshold', 0.8)
        
        print("Threshold Evaluation:")
        print(f"  Precision: {summary.precision:.3f} {'✅' if summary.precision >= precision_threshold else '❌'} (threshold: {precision_threshold})")
        print(f"  Recall:    {summary.recall:.3f} {'✅' if summary.recall >= recall_threshold else '❌'} (threshold: {recall_threshold})")
        print(f"  F1-Score:  {summary.f1_score:.3f} {'✅' if summary.f1_score >= f1_threshold else '❌'} (threshold: {f1_threshold})")
        print()
        
        if not summary.validation_passed:
            print("❌ VALIDATION FAILED: One or more metrics below threshold")
            print("   This indicates potential issues with detection accuracy")
        else:
            print("✅ VALIDATION PASSED: All metrics above threshold")
            print("   Detection accuracy meets quality standards")
        
        print("="*60)

def main():
    """Main entry point for validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Levox Validation Framework")
    parser.add_argument("--cli", action="store_true", help="Use CLI mode for scanning")
    parser.add_argument("--engine", action="store_true", help="Use engine mode for scanning")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--markdown", help="Generate Markdown summary")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    try:
        # Create validator
        use_cli = not args.engine
        validator = LevoxValidator(use_cli=use_cli)
        
        # Run validation suite
        summary = validator.run_validation_suite()
        
        # Save results
        if args.output:
            validator.save_results(summary, args.output)
        else:
            validator.save_results(summary)
        
        # Generate Markdown summary
        if args.markdown:
            validator.generate_markdown_summary(summary, args.markdown)
        else:
            validator.generate_markdown_summary(summary)
        
        # Print summary
        validator.print_summary(summary)
        
        # Exit with appropriate code
        sys.exit(0 if summary.validation_passed else 1)
        
    except Exception as e:
        print(f"Validation failed: {e}")
        if not args.quiet:
            logging.exception("Error details:")
        sys.exit(1)

if __name__ == "__main__":
    main()
