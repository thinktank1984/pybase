#!/bin/bash

# Bloggy Test Runner
# Runs tests for the Bloggy application (runtime/tests.py + UI tests)

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

# Show help
show_help() {
    echo "Usage: ./run_tests.sh [OPTIONS]"
    echo ""
    echo "Test Selection:"
    echo "  --all              Run all tests (app + Chrome) [DEFAULT]"
    echo "  --app              Run only application tests"
    echo "  --chrome           Run only Chrome DevTools tests"
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
    echo "Other Options:"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh                          # Run all tests (app + Chrome)"
    echo "  ./run_tests.sh --app                    # Run only app tests"
    echo "  ./run_tests.sh -v --app                 # Run app tests with verbose output"
    echo "  ./run_tests.sh -k test_api              # Run only tests matching 'test_api'"
    echo "  ./run_tests.sh -k prometheus --app      # Run Prometheus tests only"
    echo "  ./run_tests.sh -x --app                 # Stop on first failure"
    echo "  ./run_tests.sh --durations=5 --app      # Show 5 slowest tests"
    echo "  ./run_tests.sh --no-coverage --app      # Run without coverage"
    echo "  ./run_tests.sh -vv -x -k test_login     # Very verbose, stop on fail, specific test"
    echo "  HAS_CHROME_MCP=true ./run_tests.sh --chrome  # Run real Chrome UI tests"
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

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧪 Bloggy Test Runner (Docker)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if runtime directory exists
if [ ! -d "runtime" ]; then
    echo -e "${RED}❌ Runtime directory not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is required but not installed.${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

PROJECT_ROOT=$(pwd)
DOCKER_COMPOSE="docker compose -f docker/docker-compose.yaml"
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

echo ""

# Function to run app tests
run_app_tests() {
    echo -e "${YELLOW}🔬 Running Application Tests...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    TEST_CMD="cd /app/runtime && pytest tests.py"
    
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
        TEST_CMD="$TEST_CMD --cov=. --cov-report=html --cov-report=term"
    fi
    
    # Add extra pytest args
    if [ -n "$PYTEST_EXTRA_ARGS" ]; then
        TEST_CMD="$TEST_CMD $PYTEST_EXTRA_ARGS"
    fi
    
    echo -e "${CYAN}📝 Command: $TEST_CMD${NC}"
    echo ""
    
    if $DOCKER_COMPOSE exec runtime bash -c "$TEST_CMD"; then
        echo -e "${GREEN}✅ Application tests passed!${NC}"
        return 0
    else
        echo -e "${RED}❌ Application tests failed${NC}"
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
    
    # Check if Chrome is available
    if [ -z "$HAS_CHROME_MCP" ]; then
        echo -e "${CYAN}ℹ️  Chrome MCP integration not enabled${NC}"
        echo -e "${YELLOW}⚠️  Skipping Chrome tests (NO MOCKING ALLOWED per repository policy)${NC}"
        echo ""
        echo -e "${CYAN}   To enable REAL Chrome testing:${NC}"
        echo -e "${CYAN}   1. Export environment variable: export HAS_CHROME_MCP=true${NC}"
        echo -e "${CYAN}   2. Ensure Chrome browser is running on host${NC}"
        echo -e "${CYAN}   3. Ensure app is running at http://localhost:8081${NC}"
        echo -e "${CYAN}   4. Ensure MCP Chrome DevTools is available${NC}"
        echo ""
        echo -e "${CYAN}   Then run: HAS_CHROME_MCP=true ./run_tests.sh --chrome${NC}"
        echo ""
        echo -e "${GREEN}✅ Chrome tests skipped (prerequisites not met)${NC}"
        return 0
    fi
    
    # Real Chrome tests (run on HOST, not in Docker)
    echo -e "${CYAN}🌐 Running REAL Chrome integration tests...${NC}"
    echo -e "${CYAN}   This will actually open Chrome and test the UI${NC}"
    echo ""
    
    # Check if app is running
    echo -e "${CYAN}📡 Checking if app is accessible...${NC}"
    if ! curl -s http://localhost:8081 > /dev/null 2>&1; then
        echo -e "${RED}❌ App not accessible at http://localhost:8081${NC}"
        echo -e "${YELLOW}   Start the app first:${NC}"
        echo -e "${YELLOW}   cd runtime && emmett develop${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ App is running${NC}"
    echo ""
    
    # Run Chrome tests on HOST (not in Docker)
    cd "$PROJECT_ROOT/runtime"
    
    TEST_CMD="pytest test_ui_chrome_real.py"
    
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
    
    echo -e "${CYAN}📝 Command: $TEST_CMD${NC}"
    echo -e "${CYAN}📁 Working directory: runtime/${NC}"
    echo ""
    
    if eval "$TEST_CMD"; then
        echo ""
        echo -e "${GREEN}✅ Chrome tests passed!${NC}"
        echo -e "${GREEN}📸 Screenshots saved to: runtime/screenshots/${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ Chrome tests failed${NC}"
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
