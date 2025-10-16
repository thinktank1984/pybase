#!/bin/bash

# Bloggy Test Runner (Host Mode)
# Runs tests for the Bloggy application on the host machine

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Default values
VERBOSE=false
COVERAGE=true  # Coverage is ON by default
TEST_MODE="all"  # Default to running all tests
STOP_ON_FAILURE=false
TEST_PATTERN=""
SHOW_DURATIONS=false
PYTEST_EXTRA_ARGS=""
CLEAN_SCREENSHOTS=true  # Clean screenshots by default
HEADED_MODE=false  # All tests run on host now
SEPARATE_MODE=true  # Run tests separately with output files (DEFAULT)

# Show help
show_help() {
    echo "Usage: ./run_tests_host.sh [OPTIONS]"
    echo ""
    echo "Test Selection:"
    echo "  --all              Run all tests (app + Chrome) [DEFAULT]"
    echo "  --app              Run only application tests"
    echo "  --chrome           Run only Chrome DevTools tests"
    echo "  --separate         Run tests separately with output files [DEFAULT]"
    echo "  --together         Run tests together (disable separate mode)"
    echo "  -k PATTERN         Run tests matching PATTERN (e.g., -k test_api)"
    echo ""
    echo "Output Options:"
    echo "  -v, --verbose      Verbose output (show individual test names)"
    echo "  -vv                Very verbose output (show test details)"
    echo "  -x, --stop         Stop on first failure"
    echo "  --durations=N      Show N slowest tests (default: 10)"
    echo "  --tb=short         Short traceback format"
    echo "  --tb=long          Long traceback format"
    echo ""
    echo "Coverage Options:"
    echo "  --no-coverage      Skip coverage report (coverage enabled by default)"
    echo "  --cov-min=N        Fail if coverage below N% (default: no minimum)"
    echo ""
    echo "Cleanup Options:"
    echo "  --keep-screenshots   Keep existing screenshots (cleanup enabled by default)"
    echo ""
    echo "Chrome Options:"
    echo "  --headed             Run Chrome tests in visible/foreground mode (on host)"
    echo ""
    echo "Other Options:"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests_host.sh                          # Run all 8 tests separately (DEFAULT)"
    echo "  ./run_tests_host.sh --together --app         # Run app tests together (combined output)"
    echo "  ./run_tests_host.sh --app                    # Run app tests separately with output files"
    echo "  ./run_tests_host.sh -v --app                 # Run app tests separately with verbose output"
    echo "  ./run_tests_host.sh -k test_api --together   # Run matching tests together"
    echo "  ./run_tests_host.sh -k prometheus --app      # Run Prometheus tests separately"
    echo "  ./run_tests_host.sh -x --app                 # Run separately, stop on first failure"
    echo "  ./run_tests_host.sh --durations=5 --app      # Run separately, show 5 slowest tests"
    echo "  ./run_tests_host.sh --no-coverage --app      # Run separately without coverage"
    echo "  ./run_tests_host.sh -vv -x -k test_login     # Separate mode, very verbose, stop on fail"
    echo "  ./run_tests_host.sh --keep-screenshots --chrome  # Keep screenshots and run Chrome tests"
    echo "  ./run_tests_host.sh --chrome                     # Run real Chrome UI tests (auto-cleans)"
    echo "  ./run_tests_host.sh --chrome --headed            # Run Chrome tests in visible browser"
    echo ""
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            if [ "$VERBOSE" = "false" ]; then
                VERBOSE=true
            else
                VERBOSE="vv"  # Very verbose if -v used twice
            fi
            shift
            ;;
        -vv)
            VERBOSE="vv"
            shift
            ;;
        -x|--stop)
            STOP_ON_FAILURE=true
            shift
            ;;
        -k)
            TEST_PATTERN="$2"
            shift 2
            ;;
        --durations*)
            if [[ "$1" == *"="* ]]; then
                SHOW_DURATIONS="${1#*=}"
            else
                SHOW_DURATIONS="10"
            fi
            shift
            ;;
        --tb=*)
            PYTEST_EXTRA_ARGS="$PYTEST_EXTRA_ARGS --tb=${1#*=}"
            shift
            ;;
        --cov-min=*)
            PYTEST_EXTRA_ARGS="$PYTEST_EXTRA_ARGS --cov-fail-under=${1#*=}"
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --all)
            TEST_MODE="all"
            shift
            ;;
        --app)
            TEST_MODE="app"
            shift
            ;;
        --chrome)
            TEST_MODE="chrome"
            shift
            ;;
        --separate)
            SEPARATE_MODE=true
            shift
            ;;
        --together)
            SEPARATE_MODE=false
            shift
            ;;
        --keep-screenshots)
            CLEAN_SCREENSHOTS=false
            shift
            ;;
        --headed)
            HEADED_MODE=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Detect GitHub Spaces environment
IS_GITHUB_SPACES=false
if [ "${GITHUB_ACTIONS}" = "true" ] || [ "${CODESPACES}" = "true" ]; then
    IS_GITHUB_SPACES=true
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🧪 Bloggy Test Runner (GitHub Spaces - 8 Test Suites)${NC}"
    echo -e "${BLUE}🚀 RUNNING IN GITHUB SPACES ENVIRONMENT${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🧪 Bloggy Test Runner (Host Mode - 8 Test Suites)${NC}"
    echo -e "${BLUE}💻 ALL TESTS RUN ON HOST MACHINE${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi
echo ""

# Check if runtime directory exists
if [ ! -d "runtime" ]; then
    echo -e "${RED}❌ Runtime directory not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Set environment variables for SQLite database for local development
# Use same database as run_bloggy_host.sh
export DATABASE_URL="sqlite://bloggy.db"
export TEST_DATABASE_URL="sqlite://bloggy.db"

# Run database migrations before tests
echo -e "${CYAN}🔄 Running database migrations...${NC}"
if ! (cd runtime && DATABASE_URL="sqlite://bloggy.db" ../venv/bin/emmett migrations up); then
    echo -e "${RED}❌ Database migration failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Database migrations completed${NC}"
echo ""

# Check if pytest is available in virtual environment
if [ ! -f "./venv/bin/pytest" ]; then
    echo -e "${RED}❌ pytest is required but not installed in virtual environment.${NC}"
    echo "Please install pytest: ./venv/bin/pip install pytest"
    exit 1
fi
if [ "$SEPARATE_MODE" = true ]; then
    echo -e "${YELLOW}🔬 Running All 8 Test Suites Separately on Host...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Each test suite will be saved to a separate output file${NC}"
    echo ""

    # Create output directory if it doesn't exist
    OUTPUT_DIR="test_results"
    mkdir -p "$OUTPUT_DIR"

    # Timestamp for this run
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

    # Track overall test failures
    OVERALL_SUCCESS=0

    echo -e "${YELLOW}[1/8]${NC} Running tests.py (main integration tests)..."
    if ./venv/bin/pytest integration_tests/tests.py -v --tb=short \
        > "${OUTPUT_DIR}/01_tests_${TIMESTAMP}.txt" 2>&1; then
        echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/01_tests_${TIMESTAMP}.txt"
    else
        echo -e "${RED}✗${NC} Tests failed - Output saved to ${OUTPUT_DIR}/01_tests_${TIMESTAMP}.txt"
        OVERALL_SUCCESS=1
    fi
    echo ""

    echo -e "${YELLOW}[2/8]${NC} Running test_oauth_real.py (OAuth integration tests)..."
    if ./venv/bin/pytest integration_tests/test_oauth_real.py -v --tb=short \
        > "${OUTPUT_DIR}/02_oauth_${TIMESTAMP}.txt" 2>&1; then
        echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/02_oauth_${TIMESTAMP}.txt"
    else
        echo -e "${RED}✗${NC} Tests failed - Output saved to ${OUTPUT_DIR}/02_oauth_${TIMESTAMP}.txt"
        OVERALL_SUCCESS=1
    fi
    echo ""

    echo -e "${YELLOW}[3/8]${NC} Running test_roles_integration.py (roles & permissions tests)..."
    if ./venv/bin/pytest integration_tests/test_roles_integration.py -v --tb=short \
        > "${OUTPUT_DIR}/03_roles_integration_${TIMESTAMP}.txt" 2>&1; then
        echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/03_roles_integration_${TIMESTAMP}.txt"
    else
        echo -e "${RED}✗${NC} Tests failed - Output saved to ${OUTPUT_DIR}/03_roles_integration_${TIMESTAMP}.txt"
        OVERALL_SUCCESS=1
    fi
    echo ""

    echo -e "${YELLOW}[4/8]${NC} Running test_auto_ui.py (auto UI generation tests)..."
    if ./venv/bin/pytest integration_tests/test_auto_ui.py -v --tb=short \
        > "${OUTPUT_DIR}/04_auto_ui_${TIMESTAMP}.txt" 2>&1; then
        echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/04_auto_ui_${TIMESTAMP}.txt"
    else
        echo -e "${RED}✗${NC} Tests failed - Output saved to ${OUTPUT_DIR}/04_auto_ui_${TIMESTAMP}.txt"
        OVERALL_SUCCESS=1
    fi
    echo ""

    echo -e "${YELLOW}[5/8]${NC} Running test_ui_chrome_real.py (Chrome UI tests)..."
    if ./venv/bin/pytest integration_tests/test_ui_chrome_real.py -v --tb=short \
        > "${OUTPUT_DIR}/05_chrome_ui_${TIMESTAMP}.txt" 2>&1; then
        echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/05_chrome_ui_${TIMESTAMP}.txt"
    else
        echo -e "${RED}✗${NC} Tests failed - Output saved to ${OUTPUT_DIR}/05_chrome_ui_${TIMESTAMP}.txt"
        OVERALL_SUCCESS=1
    fi
    echo ""

    echo -e "${YELLOW}[6/8]${NC} Running test_roles_rest_api.py (roles REST API tests)..."
    if ./venv/bin/pytest integration_tests/test_roles_rest_api.py -v --tb=short \
        > "${OUTPUT_DIR}/06_roles_rest_api_${TIMESTAMP}.txt" 2>&1; then
        echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/06_roles_rest_api_${TIMESTAMP}.txt"
    else
        echo -e "${RED}✗${NC} Tests failed - Output saved to ${OUTPUT_DIR}/06_roles_rest_api_${TIMESTAMP}.txt"
        OVERALL_SUCCESS=1
    fi
    echo ""

    echo -e "${YELLOW}[7/8]${NC} Running test_roles.py (basic role tests)..."
    if ./venv/bin/pytest integration_tests/test_roles.py -v --tb=short \
        > "${OUTPUT_DIR}/07_roles_${TIMESTAMP}.txt" 2>&1; then
        echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/07_roles_${TIMESTAMP}.txt"
    else
        echo -e "${RED}✗${NC} Tests failed - Output saved to ${OUTPUT_DIR}/07_roles_${TIMESTAMP}.txt"
        OVERALL_SUCCESS=1
    fi
    echo ""

    echo -e "${YELLOW}[8/8]${NC} Running test_oauth_real_user.py (OAuth real user tests)..."
    if ./venv/bin/pytest integration_tests/test_oauth_real_user.py -v --tb=short \
        > "${OUTPUT_DIR}/08_oauth_real_user_${TIMESTAMP}.txt" 2>&1; then
        echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/08_oauth_real_user_${TIMESTAMP}.txt"
    else
        echo -e "${RED}✗${NC} Tests failed - Output saved to ${OUTPUT_DIR}/08_oauth_real_user_${TIMESTAMP}.txt"
        OVERALL_SUCCESS=1
    fi
    echo ""

    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo ""

    # Generate summary by checking each output file
    echo "Test Results:"
    echo ""

    for file in "${OUTPUT_DIR}"/*_${TIMESTAMP}.txt; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")

            # Check if pytest ran at all
            if grep -q "test session starts" "$file"; then
                # Get the final summary line from pytest output
                summary=$(grep -E "=+ [0-9]+ .* in [0-9.]+s =+" "$file" | tail -1)

                if [ -n "$summary" ]; then
                    # Extract key information from summary
                    if echo "$summary" | grep -q "failed"; then
                        echo -e "${RED}✗${NC} $filename: $summary"
                    elif echo "$summary" | grep -q "error"; then
                        echo -e "${RED}✗${NC} $filename: $summary"
                    elif echo "$summary" | grep -q "passed"; then
                        echo -e "${GREEN}✓${NC} $filename: $summary"
                    else
                        echo -e "${YELLOW}⚠${NC} $filename: $summary"
                    fi
                else
                    # Look for alternative summary formats
                    alt_summary=$(grep -E "[0-9]+ (passed|failed|error)" "$file" | tail -1)
                    if [ -n "$alt_summary" ]; then
                        if echo "$alt_summary" | grep -E "(failed|error)"; then
                            echo -e "${RED}✗${NC} $filename: $alt_summary"
                        else
                            echo -e "${GREEN}✓${NC} $filename: $alt_summary"
                        fi
                    else
                        echo -e "${YELLOW}⚠${NC} $filename: Tests ran but no summary found"
                    fi
                fi
            elif grep -q "No module named" "$file"; then
                # Import error
                error_line=$(grep "No module named" "$file" | head -1)
                echo -e "${RED}✗${NC} $filename: Import error - $error_line"
            elif grep -q "collected 0 items" "$file"; then
                # No tests found
                echo -e "${YELLOW}⚠${NC} $filename: No tests collected"
            elif grep -q "ERROR" "$file"; then
                # General error during test collection/setup
                error_line=$(grep "ERROR:" "$file" | head -1)
                echo -e "${RED}✗${NC} $filename: Error - $error_line"
            else
                echo -e "${RED}✗${NC} $filename: No test results found"
            fi
        fi
    done

    echo ""
    echo "=========================================="
    echo -e "${GREEN}All test outputs saved to: ${OUTPUT_DIR}/${NC}"
    echo "=========================================="
    echo ""
    echo "To view individual results:"
    echo "  cat ${OUTPUT_DIR}/01_tests_${TIMESTAMP}.txt"
    echo "  cat ${OUTPUT_DIR}/02_oauth_${TIMESTAMP}.txt"
    echo "  cat ${OUTPUT_DIR}/03_roles_integration_${TIMESTAMP}.txt"
    echo "  cat ${OUTPUT_DIR}/04_auto_ui_${TIMESTAMP}.txt"
    echo "  cat ${OUTPUT_DIR}/05_chrome_ui_${TIMESTAMP}.txt"
    echo "  cat ${OUTPUT_DIR}/06_roles_rest_api_${TIMESTAMP}.txt"
    echo "  cat ${OUTPUT_DIR}/07_roles_${TIMESTAMP}.txt"
    echo "  cat ${OUTPUT_DIR}/08_oauth_real_user_${TIMESTAMP}.txt"
    echo ""

    # Exit with failure code if any tests failed
    if [ "$OVERALL_SUCCESS" -eq 0 ]; then
        echo -e "${GREEN}✅ All test suites passed successfully!${NC}"
        exit 0
    else
        echo -e "${RED}❌ One or more test suites failed!${NC}"
        exit 1
    fi
fi

PROJECT_ROOT=$(pwd)
PYTEST_CMD="pytest"
TEST_FAILED=0

# Display test mode
case $TEST_MODE in
    all)
        echo -e "${CYAN}📋 Test Mode: ALL (App + Chrome)${NC}"
        ;;
    app)
        echo -e "${CYAN}📋 Test Mode: Application Tests Only${NC}"
        ;;
    chrome)
        echo -e "${CYAN}📋 Test Mode: Chrome DevTools Tests Only${NC}"
        ;;
esac

# Display options
if [ -n "$TEST_PATTERN" ]; then
    echo -e "${CYAN}🔍 Test Pattern: $TEST_PATTERN${NC}"
fi
if [ "$VERBOSE" = "vv" ]; then
    echo -e "${CYAN}📢 Verbosity: Very Verbose (-vv)${NC}"
elif [ "$VERBOSE" = true ]; then
    echo -e "${CYAN}📢 Verbosity: Verbose (-v)${NC}"
fi
if [ "$STOP_ON_FAILURE" = true ]; then
    echo -e "${CYAN}⛔ Stop on first failure: Enabled${NC}"
fi
if [ "$COVERAGE" = false ]; then
    echo -e "${CYAN}📊 Coverage: Disabled${NC}"
fi
if [ "$SHOW_DURATIONS" != "false" ]; then
    echo -e "${CYAN}⏱️  Show slowest: ${SHOW_DURATIONS} tests${NC}"
fi
if [ "$CLEAN_SCREENSHOTS" = false ]; then
    echo -e "${CYAN}📸 Screenshots: Will be kept (cleanup disabled)${NC}"
fi
if [ "$HEADED_MODE" = true ]; then
    echo -e "${CYAN}👁️  Chrome Mode: Visible/Foreground (--headed)${NC}"
fi

echo ""

# Function to clean screenshots
clean_screenshots() {
    local SCREENSHOT_DIR="$PROJECT_ROOT/runtime/screenshots"

    if [ ! -d "$SCREENSHOT_DIR" ]; then
        echo -e "${CYAN}ℹ️  Screenshot directory does not exist, skipping cleanup${NC}"
        return 0
    fi

    echo -e "${YELLOW}🧹 Cleaning screenshots directory...${NC}"

    # Count files before cleanup
    local FILE_COUNT=$(find "$SCREENSHOT_DIR" -type f -name "*.png" 2>/dev/null | wc -l | tr -d ' ')

    if [ "$FILE_COUNT" -eq 0 ]; then
        echo -e "${CYAN}ℹ️  No screenshots to clean${NC}"
        return 0
    fi

    # Remove all PNG files
    find "$SCREENSHOT_DIR" -type f -name "*.png" -delete

    echo -e "${GREEN}✅ Removed $FILE_COUNT screenshot(s)${NC}"
    echo ""
}

# Function to run app tests (all 8 test suites)
run_app_tests() {
    echo -e "${YELLOW}🔬 Running Application Tests on Host (8 Test Suites)...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}💻 Running on HOST MACHINE${NC}"
    echo -e "${CYAN}📋 Test Suites: tests.py, oauth, roles, auto_ui, chrome,${NC}"
    echo -e "${CYAN}                roles_rest_api, roles (basic), oauth_real_user${NC}"
    echo ""

    # Clean screenshots if requested (some app tests generate screenshots too)
    if [ "$CLEAN_SCREENSHOTS" = true ]; then
        clean_screenshots
    fi

    # Run all 8 test files explicitly
    TEST_FILES=(
        "integration_tests/tests.py"
        "integration_tests/test_oauth_real.py"
        "integration_tests/test_roles_integration.py"
        "integration_tests/test_auto_ui.py"
        "integration_tests/test_ui_chrome_real.py"
        "integration_tests/test_roles_rest_api.py"
        "integration_tests/test_roles.py"
        "integration_tests/test_oauth_real_user.py"
    )

    TEST_CMD="./venv/bin/pytest ${TEST_FILES[*]}"

    # Add verbosity
    if [ "$VERBOSE" = "vv" ]; then
        TEST_CMD="$TEST_CMD -vv"
    elif [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -v"
    fi

    # Add stop on failure
    if [ "$STOP_ON_FAILURE" = true ]; then
        TEST_CMD="$TEST_CMD -x"
    fi

    # Add test pattern
    if [ -n "$TEST_PATTERN" ]; then
        TEST_CMD="$TEST_CMD -k \"$TEST_PATTERN\""
        echo -e "${CYAN}🔍 Running tests matching: $TEST_PATTERN${NC}"
    fi

    # Add duration reporting
    if [ "$SHOW_DURATIONS" != "false" ]; then
        TEST_CMD="$TEST_CMD --durations=$SHOW_DURATIONS"
    fi

    # Add coverage
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD --cov=runtime --cov-report=html --cov-report=term"
    fi

    # Add extra pytest args
    if [ -n "$PYTEST_EXTRA_ARGS" ]; then
        TEST_CMD="$TEST_CMD $PYTEST_EXTRA_ARGS"
    fi

    echo -e "${CYAN}📝 Host Command: $TEST_CMD${NC}"
    echo ""

    if eval "$TEST_CMD"; then
        echo -e "${GREEN}✅ Application tests passed! (ran on host machine)${NC}"
        return 0
    else
        echo -e "${RED}❌ Application tests failed (ran on host machine)${NC}"
        return 1
    fi
}

# UI tests removed - they were mock tests that violated the no-mocking policy
# Use --chrome option to run real Chrome DevTools integration tests instead

# Function to run Chrome tests
run_chrome_tests() {
    echo ""
    echo -e "${YELLOW}🌐 Running Chrome DevTools Tests...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    if [ "$IS_GITHUB_SPACES" = true ]; then
        echo -e "${CYAN}🚀 Running in GITHUB SPACES (headless mode)${NC}"
    else
        if [ "$HEADED_MODE" = true ]; then
            echo -e "${CYAN}💻 Running on HOST MACHINE (--headed mode for visible browser)${NC}"
        else
            echo -e "${CYAN}💻 Running on HOST MACHINE (headless mode)${NC}"
        fi
    fi
    echo ""

    # Clean screenshots if requested
    if [ "$CLEAN_SCREENSHOTS" = true ]; then
        clean_screenshots
    fi

    # Install Playwright browsers for GitHub Spaces
    if [ "$IS_GITHUB_SPACES" = true ]; then
        echo -e "${CYAN}🔧 Ensuring Playwright browsers are available...${NC}"

        # Install playwright first if needed
        if ! python3 -c "import playwright" 2>/dev/null; then
            echo -e "${CYAN}   Installing playwright...${NC}"
            pip install playwright > /dev/null 2>&1
        fi

        # Install chromium browser
        if ! python3 -m playwright install chromium --force > /dev/null 2>&1; then
            echo -e "${RED}❌ Failed to install Playwright browsers${NC}"
            echo -e "${YELLOW}   Chrome tests will be skipped${NC}"
            # Don't return error, just continue without Chrome tests
            SKIP_CHROME_TESTS=true
        else
            echo -e "${GREEN}✅ Playwright browsers ready${NC}"
        fi
        echo ""
    fi

    # Check if we should skip Chrome tests
    if [ "${SKIP_CHROME_TESTS}" = true ]; then
        echo -e "${YELLOW}⚠️  Skipping Chrome tests due to Playwright installation issues${NC}"
        echo -e "${YELLOW}   This is expected in some GitHub Spaces environments${NC}"
        return 0
    fi

    # Real Chrome integration tests
    echo -e "${CYAN}🌐 Running REAL Chrome integration tests...${NC}"
    echo ""

    # Check if app is running
    echo -e "${CYAN}📡 Checking if app is accessible...${NC}"
    if ! curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo -e "${RED}❌ App not accessible at http://localhost:8000${NC}"
        echo -e "${YELLOW}   Start the app first${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ App is running${NC}"
    echo ""

    if [ "$IS_GITHUB_SPACES" = true ]; then
        echo -e "${CYAN}🚀 Running in GITHUB SPACES environment${NC}"
    else
        echo -e "${CYAN}💻 Running on HOST MACHINE${NC}"
    fi
    echo ""

    # Use pytest with timeout to prevent hanging
    TEST_CMD="timeout 120 python3 -m pytest integration_tests/test_ui_chrome_real.py"

    # Add verbosity
    if [ "$VERBOSE" = "vv" ]; then
        TEST_CMD="$TEST_CMD -vv"
    elif [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -v"
    fi

    # Add stop on failure
    if [ "$STOP_ON_FAILURE" = true ]; then
        TEST_CMD="$TEST_CMD -x"
    fi

    # Add test pattern
    if [ -n "$TEST_PATTERN" ]; then
        TEST_CMD="$TEST_CMD -k \"$TEST_PATTERN\""
        echo -e "${CYAN}🔍 Running tests matching: $TEST_PATTERN${NC}"
    fi

    # Always add -s for Chrome tests (to see output)
    TEST_CMD="$TEST_CMD -s"

    # Add extra pytest args
    if [ -n "$PYTEST_EXTRA_ARGS" ]; then
        TEST_CMD="$TEST_CMD $PYTEST_EXTRA_ARGS"
    fi

    echo -e "${CYAN}📝 Host Command: $TEST_CMD${NC}"
    echo ""

    cd "$PROJECT_ROOT"
    if eval "$TEST_CMD"; then
        echo ""
        echo -e "${GREEN}✅ Chrome tests passed! (ran on HOST MACHINE)${NC}"
        echo -e "${GREEN}📸 Screenshots saved to: runtime/screenshots/${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ Chrome tests failed (ran on HOST MACHINE)${NC}"
        return 1
    fi
}

# Run tests based on mode
case $TEST_MODE in
    all)
        run_app_tests || TEST_FAILED=1
        run_chrome_tests || TEST_FAILED=1
        ;;
    app)
        run_app_tests || TEST_FAILED=1
        ;;
    chrome)
        run_chrome_tests || TEST_FAILED=1
        ;;
    *)
        echo -e "${RED}Invalid test mode: $TEST_MODE${NC}"
        exit 1
        ;;
esac

# Final summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $TEST_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"

    if [ "$COVERAGE" = true ] && [ "$TEST_MODE" != "chrome" ]; then
        echo ""
        echo -e "${BLUE}📊 Coverage report generated at: runtime/htmlcov/index.html${NC}"
        echo "   Open with: open runtime/htmlcov/index.html"
    fi

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi