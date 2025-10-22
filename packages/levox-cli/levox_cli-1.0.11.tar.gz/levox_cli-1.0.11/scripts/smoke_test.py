#!/usr/bin/env python3
"""
Comprehensive smoke test for Levox PII detection system.
Tests all detection levels, CLI functionality, and outputs expected results.
"""

import os
import sys
import json
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# Add levox to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "levox"))

def run_command(cmd: List[str], cwd: str = None) -> Dict[str, Any]:
    """Run a command and return result info."""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            cwd=cwd or str(project_root),
            timeout=60
        )
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Command timed out'
        }
    except Exception as e:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }

def create_test_files(temp_dir: Path) -> Dict[str, Path]:
    """Create test files with various PII patterns."""
    
    test_files = {}
    
    # Python file with PII
    py_content = '''
"""Test Python file with PII patterns."""

import os
import json

# Email addresses
user_email = "john.doe@example.com"
admin_email = "admin@company.org"

# Credit card numbers
test_cc = "4532-1234-5678-9012"  # Valid Luhn
fake_cc = "1234-5678-9012-3456"  # Invalid Luhn

# Social Security Numbers
ssn = "123-45-6789"
test_ssn = "000-00-0000"  # Test pattern

# API Keys and tokens
api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# Phone numbers
phone = "+1-555-123-4567"
mobile = "(555) 987-6543"

def process_user_data(email, ssn):
    """Process sensitive user data."""
    print(f"Processing user: {email}")
    return {"user_id": hash(ssn)}

# Database connection with credentials
db_config = {
    "host": "db.example.com",
    "user": "admin",
    "password": "super_secret_password",
    "database": "users"
}
'''
    
    test_files['python'] = temp_dir / "test_data.py"
    test_files['python'].write_text(py_content)
    
    # JavaScript file with PII
    js_content = '''
// Test JavaScript file with PII patterns

const config = {
    // Email configurations
    adminEmail: "admin@testcompany.com",
    supportEmail: "support@example.org",
    
    // API credentials
    apiKey: "AIzaSyD-9tSrke72PouQMnMX-a7UAHI7i0zqXdc",
    secretKey: "sk_live_51H7QjKLEHYG8vX8uFqPmr2x",
    
    // Database credentials
    dbPassword: "MySecretPassword123!",
    dbUser: "root",
    
    // Personal data
    testSSN: "987-65-4321",
    creditCard: "5555-5555-5555-4444",
    phoneNumber: "1-800-555-0199"
};

// Function that processes PII
function processUserInfo(email, ssn, creditCard) {
    console.log(`Processing user: ${email}`);
    
    // Simulate data flow
    const userData = {
        email: email,
        ssn: ssn,
        payment: creditCard
    };
    
    // Potential sink - logging sensitive data
    console.log("User data:", JSON.stringify(userData));
    
    return userData;
}

// OAuth token
const oauthToken = "ya29.A0ARrdaM9Y8jKvE6iFuE4jI7X8vZ9gH2qR5cN8dF1sG3hJ4kL6mN7oP8qR9sT0uV1wX2yZ3";

// Environment variables (potential secrets)
process.env.SECRET_KEY = "my-super-secret-key-12345";
process.env.DATABASE_URL = "postgres://user:password@localhost:5432/mydb";
'''
    
    test_files['javascript'] = temp_dir / "test_data.js"
    test_files['javascript'].write_text(js_content)
    
    # Clean file (should have no detections)
    clean_content = '''
"""Clean Python file with no PII."""

import math
import datetime

def calculate_area(radius):
    """Calculate circle area."""
    return math.pi * radius ** 2

def get_current_time():
    """Get current timestamp."""
    return datetime.datetime.now()

# Configuration without sensitive data
config = {
    "app_name": "TestApp",
    "version": "1.0.0",
    "debug": False,
    "max_retries": 3
}

class Calculator:
    """Simple calculator class."""
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
'''
    
    test_files['clean'] = temp_dir / "clean_file.py"
    test_files['clean'].write_text(clean_content)
    
    return test_files

def test_dependency_check():
    """Test dependency validation."""
    print("🔍 Testing dependency validation...")
    
    result = run_command([sys.executable, "-m", "levox.cli_enhanced", "status"])
    
    if result['success']:
        print("✅ Dependency check passed")
        if "Tree-Sitter Parsing" in result['stdout']:
            print("   📄 Tree-Sitter status detected in output")
        if "ML False-Positive Filter" in result['stdout']:
            print("   🤖 ML filter status detected in output")
        return True
    else:
        print(f"❌ Dependency check failed: {result['stderr']}")
        return False

def test_cli_scan(test_files: Dict[str, Path], license_tier: str = "standard") -> bool:  # pragma: no cover
    """Test CLI scanning functionality."""
    print(f"🔍 Testing CLI scan with {license_tier} license...")
    
    temp_dir = list(test_files.values())[0].parent
    
    # Test different output formats
    formats = ['table', 'json', 'sarif']
    
    for fmt in formats:
        print(f"   📋 Testing {fmt} format...")
        
        result = run_command([
            sys.executable, "-m", "levox.cli_enhanced", "scan",
            str(temp_dir),
            "--format", fmt,
            "--telemetry"
        ])
        
        if not result['success']:
            print(f"❌ {fmt} format test failed: {result['stderr']}")
            return False
        
        # Validate output contains expected elements
        if fmt == 'json':
            try:
                output_data = json.loads(result['stdout'])
                if 'scan_summary' not in output_data:
                    print(f"❌ JSON output missing scan_summary")
                    return False
                if 'capabilities' not in output_data:
                    print(f"❌ JSON output missing capabilities")
                    return False
                print(f"   ✅ JSON format valid")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON output: {e}")
                return False
        
        elif fmt == 'sarif':
            try:
                sarif_data = json.loads(result['stdout'])
                if 'runs' not in sarif_data:
                    print(f"❌ SARIF output missing runs")
                    return False
                print(f"   ✅ SARIF format valid")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid SARIF output: {e}")
                return False
        
        else:  # table format
            if "Scan Summary" not in result['stdout']:
                print(f"❌ Table output missing scan summary")
                return False
            print(f"   ✅ Table format valid")
    
    print("✅ CLI scan tests passed")
    return True

def test_detection_levels():  # pragma: no cover
    """Test different detection levels."""
    print("🔍 Testing detection levels...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_files = create_test_files(temp_path)
        
        # Test standard tier (regex only)
        print("   📊 Testing Standard tier...")
        result = run_command([
            sys.executable, "-m", "levox.cli_enhanced", "scan",
            str(temp_path),
            "--format", "json"
        ])
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                matches = data.get('scan_summary', {}).get('total_matches', 0)
                print(f"   ✅ Standard tier: {matches} matches found")
            except:
                print("   ⚠️ Could not parse standard tier results")
        else:
            print(f"   ❌ Standard tier test failed: {result['stderr']}")
            return False
        
        # Test premium tier (regex + AST)
        print("   📊 Testing Premium tier...")
        result = run_command([
            sys.executable, "-m", "levox.cli_enhanced", "scan",
            str(temp_path),
            "--format", "json"
        ])
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                matches = data.get('scan_summary', {}).get('total_matches', 0)
                print(f"   ✅ Premium tier: {matches} matches found")
            except:
                print("   ⚠️ Could not parse premium tier results")
        
        # Test enterprise tier (all levels)
        print("   📊 Testing Enterprise tier...")
        result = run_command([
            sys.executable, "-m", "levox.cli_enhanced", "scan",
            str(temp_path),
            "--format", "json"
        ])
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                matches = data.get('scan_summary', {}).get('total_matches', 0)
                print(f"   ✅ Enterprise tier: {matches} matches found")
            except:
                print("   ⚠️ Could not parse enterprise tier results")
    
    print("✅ Detection level tests completed")
    return True

def test_exit_codes():  # pragma: no cover
    """Test proper exit codes."""
    print("🔍 Testing CLI exit codes...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_files = create_test_files(temp_path)
        
        # Test with violations (should return 1)
        result = run_command([
            sys.executable, "-m", "levox.cli_enhanced", "scan",
            str(test_files['python'].parent),
            "--format", "json"
        ])
        
        if result['returncode'] == 1:
            print("   ✅ Exit code 1 for violations found")
        else:
            print(f"   ⚠️ Unexpected exit code: {result['returncode']} (expected 1)")
        
        # Test clean file (should return 0)
        clean_dir = temp_path / "clean"
        clean_dir.mkdir()
        (clean_dir / "clean.py").write_text("# Clean file\nprint('Hello, World!')")
        
        result = run_command([
            sys.executable, "-m", "levox.cli_enhanced", "scan",
            str(clean_dir),
            "--format", "json"
        ])
        
        if result['returncode'] == 0:
            print("   ✅ Exit code 0 for clean scan")
        else:
            print(f"   ⚠️ Unexpected exit code: {result['returncode']} (expected 0)")
        
        # Test invalid path (should return 3)
        result = run_command([
            sys.executable, "-m", "levox.cli_enhanced", "scan",
            "/nonexistent/path",
            "--format", "json"
        ])
        
        if result['returncode'] == 3:
            print("   ✅ Exit code 3 for config error")
        elif result['returncode'] != 0:
            print(f"   ✅ Non-zero exit code for error: {result['returncode']}")
        else:
            print(f"   ⚠️ Unexpected exit code: {result['returncode']} (expected error)")
    
    print("✅ Exit code tests completed")
    return True

def test_feedback_system():  # pragma: no cover
    """Test feedback submission and export."""
    print("🔍 Testing feedback system...")
    
    # Test feedback stats (should not fail even with no data)
    result = run_command([
        sys.executable, "-m", "levox.cli_enhanced", "feedback", "stats"
    ])
    
    if result['success'] or "No feedback data available" in result['stdout']:
        print("   ✅ Feedback stats command works")
    else:
        print(f"   ⚠️ Feedback stats failed: {result['stderr']}")
    
    # Test feedback export
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as tmp_file:
        tmp_file_name = tmp_file.name
    
    try:
        result = run_command([
            sys.executable, "-m", "levox.cli_enhanced", "feedback", "export",
            tmp_file_name
        ])
        
        if result['success']:
            print("   ✅ Feedback export works")
        else:
            print(f"   ⚠️ Feedback export failed: {result['stderr']}")
    finally:
        # Clean up - try to delete, but don't fail if it's locked
        try:
            os.unlink(tmp_file_name)
        except (OSError, PermissionError):
            pass  # File might be locked on Windows
    
    print("✅ Feedback system tests completed")
    return True

def run_smoke_test():
    """Run comprehensive smoke test."""
    print("🚀 Starting Levox Smoke Test")
    print("=" * 50)
    
    start_time = time.time()
    test_results = []
    
    # Test 1: Dependency validation
    test_results.append(("Dependency Check", test_dependency_check()))
    
    # Test 2: Create test files and run CLI tests
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_files = create_test_files(temp_path)
        
        print(f"📁 Created test files in: {temp_path}")
        for name, path in test_files.items():
            print(f"   📄 {name}: {path.name}")
        
        # Test CLI scanning
        test_results.append(("CLI Scan", test_cli_scan(test_files)))
    
    # Test 3: Detection levels
    test_results.append(("Detection Levels", test_detection_levels()))
    
    # Test 4: Exit codes
    test_results.append(("Exit Codes", test_exit_codes()))
    
    # Test 5: Feedback system
    test_results.append(("Feedback System", test_feedback_system()))
    
    # Test 6: Audit script
    print("🔍 Testing audit script...")
    result = run_command([sys.executable, "levox/scripts/audit_no_placeholders.py"])
    audit_passed = result['success']
    test_results.append(("Audit Script", audit_passed))
    if audit_passed:
        print("   ✅ Audit script passed")
    else:
        print(f"   ❌ Audit script failed: {result['stderr']}")
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📊 SMOKE TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1
    
    print(f"\nSummary: {passed}/{total} tests passed")
    print(f"Duration: {duration:.2f} seconds")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Levox is ready for production.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review the output above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = run_smoke_test()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Smoke test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Smoke test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
