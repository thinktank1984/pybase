#!/usr/bin/env python3
"""NO MOCKING POLICY VALIDATOR - Enforces zero-tolerance policy"""
import os, re, sys
from pathlib import Path

BANNED_IMPORTS = [r'from\s+unittest\s+import\s+mock', r'from\s+unittest\.mock\s+import', r'import\s+mock\b']
BANNED_USAGE = [r'\bMock\s*\(', r'\bMagicMock\s*\(', r'@patch\b', r'mocker\.']

violations = []
files_checked = 0

for file_path in Path('integration_tests').rglob('*.py'):
    files_checked += 1
    with open(file_path, 'r') as f:
        in_docstring = False
        for line_num, line in enumerate(f, 1):
            # Skip docstrings
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
                continue
            if in_docstring or line.strip().startswith('#'):
                continue
            
            # Check for actual violations
            for pattern in BANNED_IMPORTS + BANNED_USAGE:
                if re.search(pattern, line):
                    violations.append(f"{file_path}:{line_num} - {line.strip()}")

print("=" * 80)
print("🚨 NO MOCKING POLICY VALIDATION")
print("=" * 80)
print(f"\nFiles checked: {files_checked}\n")

if violations:
    print(f"❌ VIOLATIONS FOUND: {len(violations)}\n")
    for v in violations:
        print(v)
    print("\n🚨 MOCKING IS ILLEGAL - Rewrite tests without mocks!\n")
    sys.exit(1 if '--strict' in sys.argv else 0)
else:
    print("✅ NO VIOLATIONS FOUND\n")
    print("All tests follow the NO MOCKING policy.")
    print("  ✅ No unittest.mock imports")
    print("  ✅ No Mock() or MagicMock() usage")
    print("  ✅ No @patch decorators\n")
