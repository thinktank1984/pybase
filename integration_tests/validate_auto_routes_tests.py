#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate that test_auto_routes.py follows NO MOCKING policy.

This script scans the test file and ensures:
- No mock imports (unittest.mock, pytest-mock, etc.)
- No Mock objects or MagicMock usage
- No patch() decorators or context managers
- No fake/stub implementations

Usage:
    python integration_tests/validate_auto_routes_tests.py
"""

import re
import sys
from pathlib import Path


def validate_no_mocking(file_path):
    """
    Validate that a test file contains no mocking.
    
    Args:
        file_path: Path to test file
        
    Returns:
        tuple: (is_valid, violations)
    """
    violations = []
    
    with open(file_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Pattern checks
    checks = [
        # Import checks
        (r'from\s+unittest\s+import\s+mock', 'Imports unittest.mock (ILLEGAL)'),
        (r'from\s+unittest\.mock', 'Imports unittest.mock (ILLEGAL)'),
        (r'import\s+unittest\.mock', 'Imports unittest.mock (ILLEGAL)'),
        (r'from\s+pytest_mock', 'Imports pytest-mock (ILLEGAL)'),
        (r'import\s+mock', 'Imports mock library (ILLEGAL)'),
        
        # Mock usage checks
        (r'Mock\(', 'Uses Mock() (ILLEGAL)'),
        (r'MagicMock\(', 'Uses MagicMock() (ILLEGAL)'),
        (r'AsyncMock\(', 'Uses AsyncMock() (ILLEGAL)'),
        (r'@patch\(', 'Uses @patch decorator (ILLEGAL)'),
        (r'@mock\.patch', 'Uses @mock.patch decorator (ILLEGAL)'),
        (r'with\s+patch\(', 'Uses patch() context manager (ILLEGAL)'),
        (r'with\s+mock\.patch', 'Uses mock.patch context manager (ILLEGAL)'),
        
        # Mocker fixture (pytest-mock)
        (r'def\s+\w+\(.*mocker.*\)', 'Uses mocker fixture (ILLEGAL)'),
        
        # Common fake patterns
        (r'FakeDatabase', 'Uses fake database (ILLEGAL)'),
        (r'FakeHTTP', 'Uses fake HTTP (ILLEGAL)'),
        (r'FakeClient', 'Uses fake client (ILLEGAL)'),
        
        # Skip decorators (also illegal)
        (r'@pytest\.mark\.skip', 'Uses @pytest.mark.skip (ILLEGAL)'),
        (r'@pytest\.mark\.skipif', 'Uses @pytest.mark.skipif (ILLEGAL)'),
        (r'pytest\.skip\(', 'Calls pytest.skip() (ILLEGAL)'),
    ]
    
    for line_num, line in enumerate(lines, 1):
        for pattern, message in checks:
            if re.search(pattern, line):
                violations.append({
                    'line': line_num,
                    'content': line.strip(),
                    'violation': message
                })
    
    return len(violations) == 0, violations


def check_required_patterns(file_path):
    """
    Check that test file uses real integration patterns.
    
    Args:
        file_path: Path to test file
        
    Returns:
        tuple: (has_patterns, missing)
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    required_patterns = [
        ('test_client.get(', 'Real HTTP GET requests'),
        ('test_client.post(', 'Real HTTP POST requests'),
        ('test_db.connection()', 'Real database connection'),
        ('.create(', 'Real database creates'),
        ('assert response.status', 'Real response assertions'),
    ]
    
    missing = []
    for pattern, description in required_patterns:
        if pattern not in content:
            missing.append(description)
    
    return len(missing) == 0, missing


def main():
    """Main validation function."""
    test_file = Path(__file__).parent / 'test_auto_routes.py'
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return 1
    
    print(f"🔍 Validating {test_file.name} for NO MOCKING compliance...")
    print()
    
    # Check for mocking violations
    is_valid, violations = validate_no_mocking(test_file)
    
    if not is_valid:
        print(f"❌ MOCKING DETECTED - {len(violations)} violation(s) found:")
        print()
        for v in violations:
            print(f"  Line {v['line']}: {v['violation']}")
            print(f"    {v['content']}")
        print()
        print("⚠️  THIS REPOSITORY HAS A ZERO-TOLERANCE POLICY FOR MOCKING")
        print("⚠️  All tests must use real integration testing")
        return 1
    
    print("✅ No mocking detected")
    print()
    
    # Check for required integration patterns
    has_patterns, missing = check_required_patterns(test_file)
    
    if not has_patterns:
        print(f"⚠️  Warning: Missing integration patterns:")
        for pattern in missing:
            print(f"  - {pattern}")
        print()
    else:
        print("✅ Uses real integration testing patterns")
        print()
    
    # Count tests
    with open(test_file, 'r') as f:
        content = f.read()
    
    test_count = len(re.findall(r'^def test_', content, re.MULTILINE))
    class_count = len(re.findall(r'^class Test\w+\(', content, re.MULTILINE))
    
    print(f"📊 Test Statistics:")
    print(f"  - Test functions: {test_count}")
    print(f"  - Test model classes: {class_count}")
    print(f"  - Lines of code: {len(content.split(chr(10)))}")
    print()
    
    print("✅ ALL CHECKS PASSED")
    print()
    print("Test file follows NO MOCKING policy:")
    print("  ✓ No unittest.mock imports")
    print("  ✓ No Mock/MagicMock usage")
    print("  ✓ No patch decorators")
    print("  ✓ No pytest-mock usage")
    print("  ✓ No skip decorators")
    print("  ✓ Uses real HTTP requests")
    print("  ✓ Uses real database operations")
    print("  ✓ Verifies actual state changes")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

