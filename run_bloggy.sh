#!/bin/bash

# Bloggy Run Script
# Quick script to start the Bloggy application

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Navigate to project root, then to bloggy directory
cd "$(dirname "$0")" || exit 1
cd bloggy || exit 1

echo -e "${BLUE}🚀 Starting Bloggy...${NC}"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found!${NC}"
    echo "Please run setup first:"
    echo "  ./setup/setup_bloggy.sh"
    echo ""
    exit 1
fi

# Check if emmett is installed
if ! uv pip list | grep -q "emmett"; then
    echo -e "${YELLOW}⚠️  Emmett not installed!${NC}"
    echo "Installing dependencies..."
    uv pip install emmett>=2.5.0 pytest>=7.0.0
fi

echo -e "${GREEN}✅ Starting development server...${NC}"
echo ""
echo "Access the application at: http://localhost:8000/"
echo "Login with:"
echo "  Email: doc@emmettbrown.com"
echo "  Password: fluxcapacitor"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the server
uv run emmett develop

