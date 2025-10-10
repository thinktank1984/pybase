#!/bin/bash

# Bloggy Run Script
# Quick script to start the Bloggy application

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

echo -e "${BLUE}🚀 Starting Bloggy...${NC}"
echo ""

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
if [ ! -f "$PROJECT_ROOT/bloggy/databases/bloggy.db" ]; then
    echo -e "${YELLOW}⚠️  Database not found. Setting up...${NC}"
    cd bloggy
    mkdir -p databases
    uv run --python ../venv/bin/python emmett migrations up 2>/dev/null || true
    uv run --python ../venv/bin/python emmett setup 2>/dev/null || true
    cd ..
    echo -e "${GREEN}✅ Database setup complete${NC}"
fi

echo ""
echo -e "${GREEN}✅ All checks passed! Starting development server...${NC}"
echo ""
echo "Access the application at: http://localhost:8000/"
echo "Login with:"
echo "  Email: doc@emmettbrown.com"
echo "  Password: fluxcapacitor"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the server
cd bloggy
uv run --python ../venv/bin/python emmett develop

