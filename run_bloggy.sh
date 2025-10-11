#!/bin/bash

# Runtime Application Run Script
# Supports both Docker and local development modes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Navigate to project root
cd "$(dirname "$0")" || exit 1
PROJECT_ROOT=$(pwd)

# Parse command line arguments
USE_DOCKER=false
if [[ "$1" == "--docker" ]] || [[ "$1" == "-d" ]]; then
    USE_DOCKER=true
fi

# Show usage if help requested
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --docker, -d    Run in Docker (recommended)"
    echo "  --local, -l     Run locally with uv (default)"
    echo "  --help, -h      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Run locally"
    echo "  $0 --docker     # Run in Docker"
    exit 0
fi

if [ "$USE_DOCKER" = true ]; then
    echo -e "${BLUE}🚀 Starting Runtime Application in Docker...${NC}"
else
    echo -e "${BLUE}🚀 Starting Runtime Application (local mode)...${NC}"
fi
echo ""

if [ "$USE_DOCKER" = true ]; then
    # ============================================================================
    # DOCKER MODE
    # ============================================================================
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is required but not installed.${NC}"
        echo "Install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check if docker compose is available
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is required but not available.${NC}"
        echo "Update Docker to get Compose V2"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker detected${NC}"
    echo ""
    echo "Access the application at: ${GREEN}http://localhost:8081${NC}"
    echo ""
    echo "Login with:"
    echo "  Email: ${YELLOW}doc@emmettbrown.com${NC}"
    echo "  Password: ${YELLOW}fluxcapacitor${NC}"
    echo ""
    echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    # Run docker compose
    cd docker
    docker compose up runtime --build
    
else
    # ============================================================================
    # LOCAL MODE
    # ============================================================================
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
        exit 1
    fi
    
    # Check and install uv if needed
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}⚠️  uv not found. Installing...${NC}"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    # Check if venv exists in project root
    if [ ! -d "$PROJECT_ROOT/venv" ]; then
        echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
        uv venv venv
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    fi
    
    # Check if emmett is installed
    if ! uv pip list --python venv/bin/python 2>/dev/null | grep -q "emmett"; then
        echo -e "${YELLOW}⚠️  Emmett not installed. Installing dependencies...${NC}"
        uv pip install --python venv/bin/python emmett>=2.5.0 pytest>=7.0.0
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    fi
    
    # Check if database exists
    if [ ! -f "$PROJECT_ROOT/runtime/databases/bloggy.db" ]; then
        echo -e "${YELLOW}⚠️  Database not found. Setting up...${NC}"
        cd runtime
        mkdir -p databases
        uv run --python ../venv/bin/python emmett migrations up 2>/dev/null || true
        uv run --python ../venv/bin/python emmett setup 2>/dev/null || true
        cd ..
        echo -e "${GREEN}✅ Database setup complete${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ All checks passed! Starting development server...${NC}"
    echo ""
    echo "Access the application at: ${GREEN}http://localhost:8000${NC}"
    echo ""
    echo "Login with:"
    echo "  Email: ${YELLOW}doc@emmettbrown.com${NC}"
    echo "  Password: ${YELLOW}fluxcapacitor${NC}"
    echo ""
    echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    # Start the server
    cd runtime
    uv run --python ../venv/bin/python emmett develop
fi

