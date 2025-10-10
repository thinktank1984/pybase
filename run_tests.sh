#!/bin/bash

# Bloggy Test Runner
# Runs tests for the Bloggy application (bloggy/tests.py)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
VERBOSE=false
COVERAGE=true  # Coverage is ON by default

# Show help
show_help() {
    echo "Usage: ./run_tests.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -v, --verbose      Verbose output"
    echo "  --no-coverage      Skip coverage report (coverage enabled by default)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh                # Run tests with coverage (default)"
    echo "  ./run_tests.sh -v             # Run with verbose output and coverage"
    echo "  ./run_tests.sh --no-coverage  # Run without coverage report"
    echo ""
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-coverage)
            COVERAGE=false
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
echo -e "${BLUE}🧪 Bloggy Test Runner${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if bloggy directory exists
if [ ! -d "bloggy" ]; then
    echo -e "${RED}❌ Bloggy directory not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

cd bloggy

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Setting up...${NC}"
    if command -v uv &> /dev/null; then
        uv venv
        uv pip install emmett>=2.5.0 pytest>=7.0.0
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    else
        echo -e "${RED}❌ uv not found. Please run: ./setup/setup_bloggy.sh${NC}"
        exit 1
    fi
fi

# Check if emmett is installed
if ! uv pip list 2>/dev/null | grep -q "emmett"; then
    echo -e "${YELLOW}Installing Emmett and pytest...${NC}"
    uv pip install emmett>=2.5.0 pytest>=7.0.0
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Build test command
TEST_CMD="pytest tests.py"

if [ "$VERBOSE" = true ]; then
    TEST_CMD="$TEST_CMD -v"
fi

if [ "$COVERAGE" = true ]; then
    # Install pytest-cov if needed
    if ! uv pip list 2>/dev/null | grep -q "pytest-cov"; then
        echo -e "${YELLOW}Installing pytest-cov...${NC}"
        uv pip install pytest-cov
    fi
    TEST_CMD="$TEST_CMD --cov=app --cov-report=html --cov-report=term"
fi

# Run tests
echo -e "${YELLOW}Running Bloggy tests...${NC}"
echo ""

if uv run $TEST_CMD; then
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${BLUE}Coverage report generated at: bloggy/htmlcov/index.html${NC}"
        echo "Open with: open bloggy/htmlcov/index.html"
    fi
    
    cd ..
    exit 0
else
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Tests failed${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    cd ..
    exit 1
fi
