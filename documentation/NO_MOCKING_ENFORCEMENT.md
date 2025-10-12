# NO MOCKING POLICY - Enforcement Guide

## 🚨 ZERO-TOLERANCE POLICY

**Mocking is ILLEGAL in this repository.**

This document explains how the NO MOCKING policy is enforced programmatically.

## Policy Summary

### ❌ BANNED (Illegal)
- `unittest.mock`, `Mock()`, `MagicMock()`
- `pytest-mock`, `mocker` fixture
- `@patch`, `@patch.object` decorators
- Any mocking, stubbing, or test double libraries
- Fake databases or fake HTTP responses
- Simulated external services

### ✅ REQUIRED (Legal)
- Real database operations with actual SQL
- Real HTTP requests through test client
- Real encryption with real libraries
- Real external service calls
- Real integration tests only

## Enforcement Tools

### 1. Validation Script

**File:** `validate_no_mocking.py`

Automated validator that scans Python files for mocking violations.

**Usage:**

```bash
# Check entire codebase
python3 validate_no_mocking.py

# Check specific directory
python3 validate_no_mocking.py --path integration_tests/

# Strict mode (exit with error if violations found)
python3 validate_no_mocking.py --strict

# Verbose output
python3 validate_no_mocking.py --verbose
```

**What it detects:**

✅ **Imports:**
- `from unittest import mock`
- `from unittest.mock import Mock`
- `import unittest.mock`
- `from mock import ...`
- `import pytest_mock`

✅ **Usage:**
- `Mock()`
- `MagicMock()`
- `@patch`
- `mocker.` (pytest-mock fixture)
- `.return_value =`
- `.side_effect =`
- `.assert_called()`
- `.call_count`

⚠️ **Warnings (suspicious patterns):**
- `fake_*` variables/functions
- `stub_*` variables/functions
- `dummy_*` variables/functions

### 2. Pre-commit Hook

**File:** `.pre-commit-config.yaml`

Automatically runs validation before each commit.

**Setup:**

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test it
pre-commit run --all-files
```

**What happens:**
- 🚨 Validation runs on every `git commit`
- ❌ Commit is **blocked** if violations found
- ✅ Commit proceeds if no violations

**Manual run:**
```bash
pre-commit run no-mocking-policy --all-files
```

### 3. Test Runner Integration

**File:** `run_tests.sh`

Tests automatically validate NO MOCKING policy before running.

**What happens:**

```bash
./run_tests.sh

# Output:
# 🔍 Validating NO MOCKING policy...
# ✅ No mocking violations detected
# 
# Running integration tests...
```

If violations found:
```bash
# ❌ MOCKING POLICY VIOLATIONS DETECTED
# Tests cannot run with mocking violations.
# Fix violations and try again.
```

### 4. CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/tests.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Validate NO MOCKING policy
        run: python3 validate_no_mocking.py --strict
      
      - name: Run tests
        run: ./run_tests.sh
```

## Violation Examples

### ❌ VIOLATION 1: Mock Import

```python
# ILLEGAL
from unittest.mock import Mock, patch

def test_something(self):
    mock_db = Mock()  # ❌ BANNED
```

**Fix:**
```python
# LEGAL
from app import db

def test_something(self):
    with db.connection():
        # Real database operations ✅
        user = db.users.insert(email='test@example.com')
```

### ❌ VIOLATION 2: Patch Decorator

```python
# ILLEGAL
@patch('app.send_email')  # ❌ BANNED
def test_email(mock_send):
    mock_send.return_value = True
```

**Fix:**
```python
# LEGAL
def test_email(test_client):
    # Real email sending (or test SMTP server) ✅
    response = test_client.post('/contact', data={'email': 'test@example.com'})
    assert response.status == 200
```

### ❌ VIOLATION 3: pytest-mock

```python
# ILLEGAL
def test_api(mocker):  # ❌ BANNED
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'success': True}
```

**Fix:**
```python
# LEGAL
def test_api(test_client):
    # Real HTTP request ✅
    response = test_client.get('/api/endpoint')
    assert response.json()['success'] is True
```

## Running Validation

### Manual Validation

```bash
# Quick check
python3 validate_no_mocking.py

# Check specific path
python3 validate_no_mocking.py --path integration_tests/

# Strict mode (CI/CD)
python3 validate_no_mocking.py --strict
```

### Automated Validation

```bash
# Pre-commit (runs on git commit)
pre-commit install
git commit -m "Add feature"  # Validation runs automatically

# Test runner (runs before tests)
./run_tests.sh  # Validation runs automatically

# Docker
docker compose -f docker/docker-compose.yaml exec runtime \
  python3 validate_no_mocking.py --strict
```

### CI/CD Validation

```bash
# GitHub Actions, GitLab CI, etc.
python3 validate_no_mocking.py --strict --path integration_tests/
```

## Example Output

### ✅ No Violations

```
================================================================================
🚨 NO MOCKING POLICY VALIDATION
================================================================================

Files checked: 9

✅ NO VIOLATIONS FOUND

All tests follow the NO MOCKING policy.
  ✅ No unittest.mock imports
  ✅ No Mock() or MagicMock() usage
  ✅ No @patch decorators
  ✅ No pytest-mock usage
```

### ❌ Violations Found

```
================================================================================
🚨 NO MOCKING POLICY VALIDATION
================================================================================

Files checked: 9

❌ VIOLATIONS FOUND: 3

The following ILLEGAL mocking patterns were detected:

ERROR: tests/test_bad.py:5 - BANNED IMPORT: from\s+unittest\.mock\s+import
  from unittest.mock import Mock, patch

ERROR: tests/test_bad.py:12 - BANNED MOCK USAGE: \bMock\s*\(
  mock_db = Mock()

ERROR: tests/test_bad.py:15 - BANNED MOCK USAGE: @patch\b
  @patch('app.send_email')

================================================================================
🚨 MOCKING IS ILLEGAL IN THIS REPOSITORY 🚨
================================================================================

⚠️ ZERO-TOLERANCE POLICY:
  ❌ unittest.mock, Mock(), MagicMock(), patch()
  ❌ pytest-mock, mocker fixture
  ❌ Any mocking, stubbing, or test double libraries

✅ ONLY REAL INTEGRATION TESTS ALLOWED:
  ✅ Real database operations with actual SQL
  ✅ Real HTTP requests through test client
  ✅ Real encryption with real libraries
  ✅ Real external service calls

These tests MUST be rewritten without mocking.
```

## Integration Checklist

- [x] Created `validate_no_mocking.py` validation script
- [x] Added `.pre-commit-config.yaml` for pre-commit hooks
- [x] Integrated into `run_tests.sh` test runner
- [ ] Added to CI/CD pipeline (GitHub Actions, GitLab CI, etc.)
- [ ] Documented in project README
- [ ] Team trained on policy

## FAQ

### Q: Can I use test fixtures?

**A: Yes!** Test fixtures that create real data are fine:

```python
# ✅ LEGAL
@pytest.fixture
def test_user():
    with db.connection():
        user_id = db.users.insert(email='test@example.com')
        yield user_id
        db.users[user_id].delete()  # Cleanup
```

### Q: Can I use fake data generators?

**A: Yes!** As long as it goes to a real database:

```python
# ✅ LEGAL
from faker import Faker
fake = Faker()

def test_user_creation():
    with db.connection():
        user = db.users.insert(
            email=fake.email(),  # Fake data ✅
            name=fake.name()     # But real database ✅
        )
```

### Q: What about test doubles for external APIs?

**A: No!** Use real API calls or test instances:

```python
# ❌ ILLEGAL
def test_api(mocker):
    mocker.patch('requests.get', return_value=fake_response)

# ✅ LEGAL
def test_api():
    # Real API call to test/staging environment
    response = requests.get('https://api.example.com/test/endpoint')
    assert response.status_code == 200
```

### Q: Tests are slow with real operations. Can I mock?

**A: No!** Optimize real tests instead:

- Use module-scoped fixtures for expensive setup
- Use transaction rollbacks for faster cleanup
- Parallelize with pytest-xdist
- Use in-memory databases (still real SQLite)

**Speed is NEVER a reason to use mocks.**

### Q: How do I test error conditions?

**A: Trigger real errors:**

```python
# ❌ ILLEGAL
def test_error(mocker):
    mocker.patch('db.insert', side_effect=Exception)

# ✅ LEGAL
def test_error():
    with db.connection():
        # Trigger real constraint violation
        db.users.insert(email='test@example.com')
        with pytest.raises(IntegrityError):
            db.users.insert(email='test@example.com')  # Duplicate email
```

## Related Documentation

- `AGENTS.md` - Repository agent instructions (includes NO MOCKING policy)
- `documentation/README_UI_TESTING.md` - UI testing guide (real browser tests)
- `documentation/CHROME_TESTING_GUIDE.md` - Chrome DevTools integration
- `integration_tests/test_oauth_real_user.py` - Example of real integration tests

## Support

If you're unsure whether something violates the policy:

1. **Run validation:** `python3 validate_no_mocking.py --strict`
2. **Check documentation:** See `AGENTS.md` for detailed policy
3. **Ask yourself:** "Am I testing real code with real operations?"
   - If yes: ✅ Legal
   - If no: ❌ Illegal

**When in doubt: Use real operations!**

