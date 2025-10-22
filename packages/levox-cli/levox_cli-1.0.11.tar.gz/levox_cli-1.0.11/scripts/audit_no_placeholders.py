#!/usr/bin/env python3
"""
Audit script to verify no placeholder code remains in Levox codebase.
Fails CI if any file contains pass, TODO/FIXME, or constant confidence returns.
"""

import re
import sys
import ast
from pathlib import Path
from typing import List, Tuple, Dict, Any
import argparse


class PlaceholderAuditor:
    """Audits codebase for placeholder patterns that should not exist in production."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.violations = []
        
        # Patterns to detect
        self.placeholder_patterns = {
            'pass_in_function': re.compile(r'^\s*def\s+\w+\([^)]*\):\s*\n\s*pass\s*$', re.MULTILINE),
            'todo_fixme': re.compile(r'#\s*(TODO|FIXME|XXX|HACK)', re.IGNORECASE),
            'coming_soon': re.compile(r'(coming\s+soon|placeholder|stub|mock|not\s+implemented)', re.IGNORECASE),
            'constant_confidence': re.compile(r'return\s+0\.7\b|return\s+0\.5\b|confidence\s*=\s*0\.7\b'),
            'dummy_returns': re.compile(r'return\s+(None|\[\]|\{\}|""|\'\')\s*#.*dummy|return\s+.*#.*placeholder', re.IGNORECASE),
            'silent_except': re.compile(r'except[^:]*:\s*\n\s*pass\s*$', re.MULTILINE),
        }
        
        # Files to check (Python files in the levox package)
        self.file_patterns = ['*.py']
        self.exclude_patterns = [
            '*/__pycache__/*',
            '*/.*',
            '*/tests/*',
            '*/test_*.py',
            '*_test.py',
            '*/setup.py',
            '*/scripts/audit_no_placeholders.py',  # Exclude this script itself
            '*/create_ml_model.py',  # ML training data contains legitimate "mock" examples
            '*/scripts/train_ml_filter.py',  # Training script contains legitimate examples
            '*/demo.py'  # Demo file may contain example data
        ]
    
    def audit(self) -> bool:
        """Run the audit and return True if no violations found."""
        print("🔍 Auditing Levox codebase for placeholder patterns...")
        print(f"📁 Scanning: {self.root_path}")
        
        # Find all Python files
        python_files = self._find_python_files()
        print(f"📄 Found {len(python_files)} Python files to audit")
        
        # Check each file
        for file_path in python_files:
            self._audit_file(file_path)
        
        # Report results
        self._report_results()
        
        return len(self.violations) == 0
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files to audit."""
        files = []
        
        for pattern in self.file_patterns:
            found_files = list(self.root_path.rglob(pattern))
            files.extend(found_files)
        
        # Filter out excluded files
        filtered_files = []
        for file_path in files:
            relative_path = file_path.relative_to(self.root_path)
            
            # Check if file should be excluded
            exclude = False
            for exclude_pattern in self.exclude_patterns:
                if file_path.match(exclude_pattern) or str(relative_path).find('__pycache__') != -1:
                    exclude = True
                    break
            
            if not exclude:
                filtered_files.append(file_path)
        
        return sorted(filtered_files)
    
    def _audit_file(self, file_path: Path) -> None:
        """Audit a single Python file for placeholder patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = file_path.relative_to(self.root_path)
            
            # Check for text-based patterns
            self._check_text_patterns(content, relative_path)
            
            # Check for AST-based patterns (more sophisticated)
            self._check_ast_patterns(content, relative_path)
            
        except Exception as e:
            print(f"⚠️  Error auditing {file_path}: {e}")
    
    def _check_text_patterns(self, content: str, file_path: Path) -> None:
        """Check for text-based placeholder patterns."""
        lines = content.split('\n')
        
        for pattern_name, pattern in self.placeholder_patterns.items():
            matches = pattern.finditer(content)
            
            for match in matches:
                # Find line number
                line_start = content.rfind('\n', 0, match.start())
                line_num = content.count('\n', 0, match.start()) + 1
                
                # Get the actual line content
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                # Skip if this looks like legitimate training data or configuration
                if self._is_legitimate_usage(line_content, pattern_name, match.group()):
                    continue
                
                self.violations.append({
                    'file': str(file_path),
                    'line': line_num,
                    'pattern': pattern_name,
                    'content': line_content.strip(),
                    'match': match.group().strip()
                })
    
    def _is_legitimate_usage(self, line_content: str, pattern_name: str, match_text: str) -> bool:
        """Check if this is a legitimate usage rather than a placeholder."""
        line_lower = line_content.lower()
        
        # Training data contexts
        if any(indicator in line_lower for indicator in [
            'training_data', 'test_data', 'example_data', 'sample_data',
            "'mock'", '"mock"', "'placeholder'", '"placeholder"',
            'negative_indicators', 'test_patterns', 'example_patterns'
        ]):
            return True
        
        # Configuration or pattern definitions
        if pattern_name == 'coming_soon' and any(indicator in line_lower for indicator in [
            're.compile', 'pattern', 'regex', 'indicators', 'patterns'
        ]):
            return True
        
        # Legitimate regex pattern definitions
        if 'example|demo|sample|test|mock' in line_content and 're.compile' in line_content:
            return True
            
        return False
    
    def _check_ast_patterns(self, content: str, file_path: Path) -> None:
        """Check for AST-based patterns like pass in function bodies."""
        try:
            tree = ast.parse(content)
            visitor = PlaceholderASTVisitor(str(file_path), content)
            visitor.visit(tree)
            self.violations.extend(visitor.violations)
            
        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"⚠️  AST analysis failed for {file_path}: {e}")
    
    def _report_results(self) -> None:
        """Report audit results."""
        if not self.violations:
            print("✅ No placeholder patterns found! Codebase is production-ready.")
            return
        
        print(f"❌ Found {len(self.violations)} placeholder violations:")
        print()
        
        # Group by file
        violations_by_file = {}
        for violation in self.violations:
            file_path = violation['file']
            if file_path not in violations_by_file:
                violations_by_file[file_path] = []
            violations_by_file[file_path].append(violation)
        
        # Report by file
        for file_path, file_violations in violations_by_file.items():
            print(f"📁 {file_path}:")
            
            for violation in file_violations:
                print(f"  ⚠️  Line {violation['line']:3d}: {violation['pattern']}")
                print(f"      Content: {violation['content']}")
                if violation.get('match') != violation['content']:
                    print(f"      Match: {violation['match']}")
                print()
        
        # Summary by pattern type
        pattern_counts = {}
        for violation in self.violations:
            pattern = violation['pattern']
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        print("📊 Violation Summary:")
        for pattern, count in sorted(pattern_counts.items()):
            print(f"  • {pattern}: {count}")
        
        print()
        print("🚨 AUDIT FAILED: Placeholder patterns detected!")
        print("   Please remove all placeholder code before deploying to production.")


class PlaceholderASTVisitor(ast.NodeVisitor):
    """AST visitor to detect placeholder patterns in Python code."""
    
    def __init__(self, file_path: str, content: str):
        self.file_path = file_path
        self.content = content
        self.lines = content.split('\n')
        self.violations = []
        self.in_function = False
        self.current_function = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to check for placeholder implementations."""
        old_function = self.current_function
        old_in_function = self.in_function
        
        self.current_function = node.name
        self.in_function = True
        
        # Check if function body only contains pass
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            # Skip if this is an abstract method or interface
            if not self._is_abstract_method(node):
                self.violations.append({
                    'file': self.file_path,
                    'line': node.lineno,
                    'pattern': 'pass_in_function_body',
                    'content': f"def {node.name}(...): pass",
                    'match': 'pass'
                })
        
        # Check for constant returns that might be placeholders
        self._check_constant_returns(node)
        
        self.generic_visit(node)
        
        self.current_function = old_function
        self.in_function = old_in_function
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        # Same logic as regular functions
        self.visit_FunctionDef(node)
    
    def visit_Return(self, node: ast.Return) -> None:
        """Check return statements for placeholder values."""
        if self.in_function and node.value:
            # Check for constant confidence values
            if isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, float) and node.value.value in [0.5, 0.7]:
                    # Check if this looks like a placeholder confidence
                    line_content = self.lines[node.lineno - 1] if node.lineno <= len(self.lines) else ""
                    if 'confidence' in line_content.lower() or 'default' in line_content.lower():
                        self.violations.append({
                            'file': self.file_path,
                            'line': node.lineno,
                            'pattern': 'constant_confidence_return',
                            'content': line_content.strip(),
                            'match': f'return {node.value.value}'
                        })
        
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Check assignments for placeholder confidence values."""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            
            # Check for confidence assignments
            if 'confidence' in var_name.lower() and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, float) and node.value.value in [0.5, 0.7]:
                    line_content = self.lines[node.lineno - 1] if node.lineno <= len(self.lines) else ""
                    self.violations.append({
                        'file': self.file_path,
                        'line': node.lineno,
                        'pattern': 'constant_confidence_assignment',
                        'content': line_content.strip(),
                        'match': f'{var_name} = {node.value.value}'
                    })
        
        self.generic_visit(node)
    
    def _is_abstract_method(self, node: ast.FunctionDef) -> bool:
        """Check if this is an abstract method that should have pass."""
        # Check for @abstractmethod decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'abstractmethod':
                return True
        
        # Check if function has docstring indicating it's abstract
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value.lower()
            if 'abstract' in docstring or 'override' in docstring or 'implement' in docstring:
                return True
        
        return False
    
    def _check_constant_returns(self, node: ast.FunctionDef) -> None:
        """Check for suspicious constant returns in function bodies."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Return) and stmt.value:
                if isinstance(stmt.value, ast.Constant):
                    value = stmt.value.value
                    
                    # Check for common placeholder return values
                    if (isinstance(value, str) and value in ['', 'placeholder', 'TODO']) or \
                       (isinstance(value, (list, dict)) and not value) or \
                       (isinstance(value, float) and value in [0.0, 0.5, 0.7, 1.0]):
                        
                        line_content = self.lines[stmt.lineno - 1] if stmt.lineno <= len(self.lines) else ""
                        
                        # Only flag if it looks suspicious (has comments or obvious placeholder indicators)
                        if any(indicator in line_content.lower() for indicator in 
                              ['todo', 'fixme', 'placeholder', 'dummy', 'default', 'temp']):
                            self.violations.append({
                                'file': self.file_path,
                                'line': stmt.lineno,
                                'pattern': 'suspicious_constant_return',
                                'content': line_content.strip(),
                                'match': f'return {value}'
                            })


def main():
    """Main audit function."""
    parser = argparse.ArgumentParser(description='Audit Levox codebase for placeholder patterns')
    parser.add_argument('--root', type=Path, default=Path(__file__).parent.parent,
                       help='Root directory to audit (default: levox package)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    if not args.root.exists():
        print(f"❌ Root directory does not exist: {args.root}")
        sys.exit(1)
    
    # Run audit
    auditor = PlaceholderAuditor(args.root)
    success = auditor.audit()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
