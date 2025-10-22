# Levox Validation Framework

A comprehensive validation framework for testing and measuring the accuracy of Levox's GDPR and security vulnerability detection capabilities.

## Overview

The validation framework provides:
- **Test Cases**: Known positive and negative examples of security issues
- **Ground Truth**: Expected detection results for each test case
- **Automated Testing**: Pytest-based validation suite
- **Metrics**: Precision, Recall, F1-score, and confusion matrix
- **Regression Protection**: Ensures detection quality doesn't degrade
- **Multiple Output Formats**: JSON, CSV, and HTML reports

## Directory Structure

```
tests/validation/
├── positives/                    # Test files with known security issues
│   ├── hardcoded_password.py    # Hardcoded credentials
│   ├── pii_in_logs.py          # PII logging violations
│   ├── sql_injection.py        # SQL injection vulnerabilities
│   ├── weak_crypto.py          # Weak cryptography practices
│   ├── xss_vulnerability.js    # XSS vulnerabilities
│   └── java_security_issues.java # Java security issues
├── negatives/                    # Clean code examples (no issues)
│   ├── clean_python.py         # Secure Python code
│   └── clean_javascript.js     # Secure JavaScript code
├── results/                      # Validation results storage
├── ground_truth.json            # Expected results for each test
├── validation_framework.py      # Core validation engine
├── test_validation_framework.py # Pytest test suite
├── validate.py                  # Standalone validation script
└── README.md                    # This file
```

## Test Categories

### Positive Tests (Should Detect Issues)

1. **Hardcoded Credentials** (`hardcoded_password.py`)
   - Passwords, API keys, secrets in code
   - Expected: 8-12 issues detected

2. **PII Logging** (`pii_in_logs.py`)
   - Emails, phone numbers, SSNs in logs
   - Expected: 6-10 issues detected

3. **SQL Injection** (`sql_injection.py`)
   - String concatenation, format strings, dynamic queries
   - Expected: 8-15 issues detected

4. **Weak Cryptography** (`weak_crypto.py`)
   - MD5, SHA1, weak iterations, hardcoded keys
   - Expected: 6-12 issues detected

5. **XSS Vulnerabilities** (`xss_vulnerability.js`)
   - innerHTML, eval, unsafe DOM manipulation
   - Expected: 8-15 issues detected

6. **Java Security Issues** (`java_security_issues.java`)
   - Multiple vulnerability types in Java
   - Expected: 13-20 issues detected

### Negative Tests (Should NOT Detect Issues)

1. **Clean Python Code** (`clean_python.py`)
   - Secure practices, proper validation
   - Expected: 0 issues detected

2. **Clean JavaScript Code** (`clean_javascript.js`)
   - Safe DOM manipulation, input validation
   - Expected: 0 issues detected

## Quick Start

### 1. Run Basic Validation

```bash
# From the validation directory
python validate.py
```

### 2. Run with Verbose Output

```bash
python validate.py --verbose
```

### 3. Force CLI Mode (if engine unavailable)

```bash
python validate.py --cli
```

### 4. Save Results to File

```bash
python validate.py --output my_results.json
```

### 5. Export Additional Formats

```bash
# Export as CSV
python validate.py --export csv

# Export as HTML report
python validate.py --export html

# Export with custom filename
python validate.py --export csv --export-file results.csv
```

## Using the Framework Programmatically

### Basic Usage

```python
from validation_framework import LevoxValidator

# Create validator
validator = LevoxValidator(use_cli=True)

# Run validation suite
summary = validator.run_validation_suite()

# Print results
success = validator.print_summary(summary)

# Save results
validator.save_results(summary, "results.json")
```

### Custom Configuration

```python
# Use custom Levox config
validator = LevoxValidator(
    config_path="path/to/config.yaml",
    use_cli=False  # Use engine mode if available
)
```

### Individual File Validation

```python
# Validate specific file
ground_truth = validator.ground_truth["test_files"]["positives/hardcoded_password.py"]
result = validator.validate_file("path/to/file.py", ground_truth)

print(f"Detected {result.actual_issues} issues")
print(f"Expected {result.expected_issues} issues")
print(f"Passed: {result.passed}")
```

## Pytest Integration

### Run Validation Tests

```bash
# Run all tests
pytest test_validation_framework.py -v

# Run specific test class
pytest test_validation_framework.py::TestValidationFramework -v

# Run with coverage
pytest test_validation_framework.py --cov=validation_framework --cov-report=html
```

### Integration Tests

```bash
# Run integration tests (requires real test files)
pytest test_validation_framework.py::TestIntegration -v -m integration
```

## Metrics and Scoring

### Detection Metrics

- **Precision**: True Positives / (True Positives + False Positives)
- **Recall**: True Positives / (True Positives + False Negatives)
- **F1-Score**: 2 × (Precision × Recall) / (Precision + Recall)

### Thresholds

Default thresholds (configurable in `ground_truth.json`):
- Precision: ≥ 0.8 (80%)
- Recall: ≥ 0.8 (80%)
- F1-Score: ≥ 0.8 (80%)

### Scoring System

- **Perfect Score (1.0)**: All expected issues detected
- **Partial Score (0.5-0.99)**: Some issues detected, within acceptable range
- **Failed Score (0.0)**: No issues detected when expected, or false positives

## Configuration

### Ground Truth Configuration

Edit `ground_truth.json` to:
- Add new test files
- Modify expected issue counts
- Adjust severity weights
- Change scoring thresholds

### Levox Configuration

The framework can use Levox's configuration files:
- `--config path/to/config.yaml`: Custom Levox config
- Default config used if none specified

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Levox Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run validation suite
        run: |
          cd tests/validation
          python validate.py --output results.json
      
      - name: Run pytest suite
        run: |
          cd tests/validation
          pytest test_validation_framework.py -v --cov=validation_framework
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: validation-results
          path: tests/validation/results.json
```

### Exit Codes

- **0**: Validation passed (all thresholds met)
- **1**: Validation failed (some thresholds not met)
- **130**: Interrupted by user
- **Other**: Unexpected errors

## Extending the Framework

### Adding New Test Cases

1. **Create Test File**
   ```python
   # positives/new_vulnerability.py
   def vulnerable_function():
       # Add code with known security issues
       password = "hardcoded123"
       return password
   ```

2. **Update Ground Truth**
   ```json
   {
     "positives/new_vulnerability.py": {
       "expected_issues": [
         {
           "category": "hardcoded_credentials",
           "severity": "HIGH",
           "patterns": ["hardcoded_password"],
           "min_count": 1,
           "description": "Should detect hardcoded password"
         }
       ],
       "expected_issue_count": {
         "min": 1,
         "max": 3
       },
       "languages": ["python"],
       "tags": ["credentials", "passwords"]
     }
   }
   ```

### Adding New Detection Categories

1. **Update Categorization Logic**
   ```python
   def _categorize_issues(self, issues):
       # Add new category detection
       if any(word in description for word in ['new_pattern']):
           categories.add('new_category')
   ```

2. **Update Ground Truth Patterns**
   ```json
   "patterns": ["new_pattern", "another_pattern"]
   ```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from the validation directory
   - Check Python path includes parent directories

2. **CLI Mode Required**
   - Use `--cli` flag if Levox engine unavailable
   - Check Levox installation and dependencies

3. **Test Files Not Found**
   - Verify test file paths in `ground_truth.json`
   - Check file permissions and existence

4. **Low Detection Rates**
   - Review Levox configuration
   - Check if detection rules are enabled
   - Verify test file content matches expected patterns

### Debug Mode

```bash
# Enable verbose logging
python validate.py --verbose

# Check individual file validation
python validate.py --verbose 2>&1 | grep "Validating file"
```

## Performance Considerations

- **Scan Timeout**: 60 seconds per file (configurable)
- **Memory Usage**: Results stored in memory during validation
- **Parallel Processing**: Future enhancement for large test suites
- **Caching**: Consider caching scan results for repeated runs

## Contributing

1. **Add Test Cases**: Create realistic security vulnerability examples
2. **Improve Ground Truth**: Refine expected results based on actual detection
3. **Enhance Metrics**: Add new scoring algorithms or thresholds
4. **Documentation**: Update this README with new features

## License

This validation framework is part of the Levox project and follows the same license terms.

## Support

For issues and questions:
1. Check this README and code comments
2. Review Levox documentation
3. Open an issue in the project repository
4. Check validation results for specific failure details
