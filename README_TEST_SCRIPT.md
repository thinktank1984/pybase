# Integration Test Runner Script

## Overview

`run_tests_separate.sh` runs each integration test suite separately and saves the output to individual timestamped files.

## Usage

```bash
./run_tests_separate.sh
```

## What It Does

The script runs 5 test suites in sequence:

1. **tests.py** - Main integration tests (83 tests)
   - Database operations
   - Authentication & authorization
   - API endpoints (posts, comments, users)
   - OpenAPI/Swagger
   - Valkey cache integration
   - Prometheus metrics
   - Web page rendering

2. **test_oauth_real.py** - OAuth integration tests (23 tests)
   - Token encryption/decryption
   - PKCE generation
   - State generation
   - OAuth database operations
   - Security validations

3. **test_roles_integration.py** - Role & permissions tests (19 tests)
   - Role creation and retrieval
   - Permission management
   - User role assignments
   - Ownership-based permissions
   - Seeded data verification

4. **test_auto_ui.py** - Auto UI generation tests (14 tests)
   - UI mapping loader
   - Auto UI generator
   - Component configuration
   - Field type detection
   - Permission checking

5. **test_ui_chrome_real.py** - Chrome UI tests (13 tests)
   - Browser-based UI testing
   - **Note**: Requires Playwright browsers installed

## Output

All test outputs are saved to the `test_results/` directory with timestamps:

```
test_results/
├── 1_tests_20251013_124316.txt
├── 2_oauth_20251013_124316.txt
├── 3_roles_20251013_124316.txt
├── 4_auto_ui_20251013_124316.txt
└── 5_chrome_ui_20251013_124316.txt
```

## Summary Display

After running all tests, the script displays a color-coded summary:

- ✓ **Green** - All tests passed
- ✗ **Red** - Tests failed or errors occurred

Example output:
```
Test Results:

✓ 1_tests_20251013_124316.txt: 83 passed, 333 warnings in 3.00s
✓ 2_oauth_20251013_124316.txt: 23 passed, 17 warnings in 0.09s
✓ 3_roles_20251013_124316.txt: 19 passed, 141 warnings in 0.21s
✓ 4_auto_ui_20251013_124316.txt: 14 passed, 2 warnings in 0.06s
✗ 5_chrome_ui_20251013_124316.txt: No test results found
```

## Viewing Results

To view individual test results:

```bash
cat test_results/1_tests_TIMESTAMP.txt
cat test_results/2_oauth_TIMESTAMP.txt
cat test_results/3_roles_TIMESTAMP.txt
cat test_results/4_auto_ui_TIMESTAMP.txt
cat test_results/5_chrome_ui_TIMESTAMP.txt
```

Or view the most recent results:

```bash
cat test_results/1_tests_*.txt | tail -100
```

## Requirements

- Docker and docker-compose must be running
- The runtime container must be available
- For Chrome UI tests: Playwright browsers must be installed in container

## Test Results Directory

The `test_results/` directory is gitignored and will not be committed to the repository.

## Troubleshooting

### Chrome UI Tests Fail

If Chrome UI tests show "No test results found", install Playwright browsers:

```bash
docker compose -f docker/docker-compose.yaml exec runtime playwright install
```

### Docker Not Running

If you get connection errors, start Docker:

```bash
docker compose -f docker/docker-compose.yaml up runtime -d
```

## Related Scripts

- `run_tests.sh` - Run all tests together (original script)
- `run_type_check.sh` - Run Pyright type checking

