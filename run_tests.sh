#!/bin/bash

# DjangoBase Test Runner
# Runs all tests for both the main application and extensions plugin
# Defaults to Docker environment (use --local for local uv environment)
#
# Usage:
#   ./run_tests.sh              Run all tests in Docker (default)
#   ./run_tests.sh --local      Run all tests locally with uv
#   ./run_tests.sh --quick      Run only root tests (faster)
#   ./run_tests.sh --phase3     Run only Phase 3 (Application) tests
#   ./run_tests.sh --docker     Explicitly use Docker (same as default)
#   USE_DOCKER=false ./run_tests.sh   Override via environment variable

set -e  # Exit on error

# Check if setup has been completed (before parsing args)
if [ ! -d "djangobase/.venv" ] && [ ! "$(docker images -q djangobase_local_django 2> /dev/null)" ]; then
    echo -e "\033[1;33m⚠️  Setup not detected. Running setup first...\033[0m"
    echo ""
    ./setup/setup.sh
    echo ""
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Detect environment and mode
USE_DOCKER=${USE_DOCKER:-true}  # Default to Docker
QUICK_MODE=${QUICK_MODE:-false}
PHASE3_MODE=${PHASE3_MODE:-false}

# Check for flags
for arg in "$@"; do
    if [ "$arg" == "--docker" ]; then
        USE_DOCKER=true
    elif [ "$arg" == "--local" ]; then
        USE_DOCKER=false
    elif [ "$arg" == "--quick" ]; then
        QUICK_MODE=true
    elif [ "$arg" == "--phase3" ]; then
        PHASE3_MODE=true
    fi
done

# Navigate to djangobase directory
cd "$(dirname "$0")/djangobase" || exit 1

print_header "DjangoBase Test Suite"

if [ "$QUICK_MODE" = true ]; then
    print_info "Quick mode: Running only root tests"
fi

if [ "$PHASE3_MODE" = true ]; then
    print_info "Phase 3 mode: Running only application tests"
fi

if [ "$USE_DOCKER" = true ]; then
    print_info "Running tests in Docker environment..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check if containers are running
    if ! docker compose -f docker-compose.local.yml ps | grep -q "Up"; then
        print_info "Starting Docker containers..."
        docker compose -f docker-compose.local.yml up -d
        sleep 5  # Wait for services to start
    fi
    
    if [ "$QUICK_MODE" = true ]; then
        # Quick mode: Just framework tests
        print_header "Quick Tests: Framework Tests Only (Plugin System, Active Record, Auto-CRUD)"
        docker compose -f docker-compose.local.yml run --rm django pytest ../tests/framework/ -v --tb=short || {
            print_error "Quick tests failed"
            exit 1
        }
    elif [ "$PHASE3_MODE" = true ]; then
        # Phase 3 mode: Just application tests
        print_header "Phase 3: Application Tests"
        docker compose -f docker-compose.local.yml run --rm django pytest ../tests/application/ -v --tb=short || {
            print_error "Application tests failed"
            exit 1
        }
    else
        # Full mode: All tests with coverage
        print_header "Phase 1: Framework Tests (Plugin System, Active Record, Auto-CRUD)"
        docker compose -f docker-compose.local.yml run --rm django pytest ../tests/framework/ -v --tb=short || {
            print_error "Framework tests failed"
            exit 1
        }
        
        print_header "Phase 2: Extensions Tests"
        docker compose -f docker-compose.local.yml run --rm django pytest ../tests/extensions/ -v --tb=short || {
            print_error "Extensions tests failed"
            exit 1
        }
        
        print_header "Phase 3: Application Tests"
        docker compose -f docker-compose.local.yml run --rm django pytest ../tests/application/ -v --tb=short || {
            print_error "Application tests failed"
            exit 1
        }
        
        print_header "Phase 4: User Tests"
        docker compose -f docker-compose.local.yml run --rm django pytest ../tests/users/ -v --tb=short || {
            print_error "User tests failed"
            exit 1
        }
        
        print_header "Phase 5: Integration Tests (End-to-End)"
        docker compose -f docker-compose.local.yml run --rm django pytest ../tests/integration/ -v --tb=short || {
            print_error "Integration tests failed"
            exit 1
        }
        
        print_header "Phase 6: All Tests with Coverage"
        docker compose -f docker-compose.local.yml run --rm django pytest \
            ../tests/ \
            --cov=djangobase.extensions \
            --cov=djangobase.core \
            --cov-report=term-missing \
            --cov-report=html \
            -v || {
            print_error "Coverage tests failed"
            exit 1
        }
    fi
    
else
    print_info "Running tests locally with uv..."
    
    # Check if uv is available
    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed or not in PATH"
        print_info "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    if [ "$QUICK_MODE" = true ]; then
        # Quick mode: Just framework tests
        print_header "Quick Tests: Framework Tests Only (Plugin System, Active Record, Auto-CRUD)"
        uv run pytest ../tests/framework/ -v --tb=short || {
            print_error "Quick tests failed"
            exit 1
        }
    elif [ "$PHASE3_MODE" = true ]; then
        # Phase 3 mode: Just application tests
        print_header "Phase 3: Application Tests"
        uv run pytest ../tests/application/ -v --tb=short || {
            print_error "Application tests failed"
            exit 1
        }
    else
        # Full mode: All tests with coverage
        print_header "Phase 1: Framework Tests (Plugin System, Active Record, Auto-CRUD)"
        uv run pytest ../tests/framework/ -v --tb=short || {
            print_error "Framework tests failed"
            exit 1
        }
        
        print_header "Phase 2: Extensions Tests"
        uv run pytest ../tests/extensions/ -v --tb=short || {
            print_error "Extensions tests failed"
            exit 1
        }
        
        print_header "Phase 3: Application Tests"
        uv run pytest ../tests/application/ -v --tb=short || {
            print_error "Application tests failed"
            exit 1
        }
        
        print_header "Phase 4: User Tests"
        uv run pytest ../tests/users/ -v --tb=short || {
            print_error "User tests failed"
            exit 1
        }
        
        print_header "Phase 5: Integration Tests (End-to-End)"
        uv run pytest ../tests/integration/ -v --tb=short || {
            print_error "Integration tests failed"
            exit 1
        }
        
        print_header "Phase 6: All Tests with Coverage"
        uv run pytest \
            ../tests/ \
            --cov=djangobase.extensions \
            --cov=djangobase.core \
            --cov-report=term-missing \
            --cov-report=html \
            -v || {
            print_error "Coverage tests failed"
            exit 1
        }
        
        print_success "Coverage report generated at: htmlcov/index.html"
    fi
fi

print_header "Test Summary"
print_success "All tests passed! ✨"

echo ""

if [ "$QUICK_MODE" = true ]; then
    print_info "Quick mode - ran only root tests"
    echo ""
    print_info "For full test suite with coverage, run:"
    if [ "$USE_DOCKER" = true ]; then
        echo "  ./run_tests.sh"
    else
        echo "  ./run_tests.sh --local"
    fi
elif [ "$PHASE3_MODE" = true ]; then
    print_info "Phase 3 mode - ran only application tests"
    echo ""
    print_info "For full test suite with coverage, run:"
    echo "  ./run_tests.sh"
else
    print_info "Test locations:"
    echo "  - Framework tests:   tests/framework/ (Phase 1: Plugin, Active Record, CRUD)"
    echo "  - Extensions tests:  tests/extensions/ (Phase 2)"
    echo "  - Application tests: tests/application/ (Phase 3: Article model, etc.) ✨"
    echo "  - User tests:        tests/users/ (Phase 4)"
    echo "  - Integration tests: tests/integration/ (Phase 5: End-to-End) 🔗"
    
    echo ""
    print_info "To view coverage report:"
    if [ "$USE_DOCKER" = true ]; then
        echo "  just shell  # then: python -m webbrowser htmlcov/index.html"
        echo "  Or from host: open djangobase/htmlcov/index.html"
    else
        echo "  open htmlcov/index.html"
    fi
fi

echo ""
if [ "$QUICK_MODE" = true ]; then
    print_success "Quick tests complete! 🎉"
elif [ "$PHASE3_MODE" = true ]; then
    print_success "Phase 3 tests complete! 🎉"
else
    print_success "Testing complete! 🎉"
fi

