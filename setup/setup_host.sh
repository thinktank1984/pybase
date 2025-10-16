#!/bin/bash

# Host Setup Script for Turso Database
# This script sets up the environment for local development without Docker.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up Host Environment for Turso Database...${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1
PROJECT_ROOT=$(pwd)

echo -e "${GREEN}✅ Project root: $PROJECT_ROOT${NC}"

# Check Python version
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    echo "Please install Python 3.9+ and try again."
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo -e "${RED}❌ Python 3.9+ is required (you have $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"

# Check and install uv
echo ""
echo -e "${BLUE}Checking uv package manager...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  uv not found. Installing uv (fast Python package installer)...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add uv to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"

    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ uv installation failed or not in PATH${NC}"
        echo "Please run one of:"
        echo "  source ~/.bashrc    # for bash"
        echo "  source ~/.zshrc     # for zsh"
        echo "Then run this script again."
        exit 1
    fi
fi

UV_VERSION=$(uv --version 2>/dev/null || echo "unknown")
echo -e "${GREEN}✅ uv is available: $UV_VERSION${NC}"

# Create virtual environment in project root
echo ""
echo -e "${BLUE}Setting up virtual environment...${NC}"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment in project root..."
    uv venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Install dependencies including turso
echo ""
echo -e "${BLUE}Installing dependencies including Turso...${NC}"
uv pip install --python venv/bin/python emmett>=2.5.0
uv pip install --python venv/bin/python pytest>=7.0.0
uv pip install --python venv/bin/python pyturso

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create Turso database directory
echo ""
echo -e "${BLUE}Setting up Turso database...${NC}"
cd runtime || exit 1

# Create databases directory if it doesn't exist
mkdir -p databases

# Create the Turso database file if it doesn't exist
if [ ! -f "databases/bloggy.turso.db" ]; then
    echo -e "${YELLOW}⚠️  Turso database file not found. Creating...${NC}"
    touch databases/bloggy.turso.db
    echo -e "${GREEN}✅ Turso database file created${NC}"
else
    echo -e "${GREEN}✅ Turso database file exists${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Host Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo ""
echo "1️⃣  Activate virtual environment:"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo "2️⃣  Start the application:"
echo -e "   ${YELLOW}cd runtime && python app.py${NC}"
echo ""
echo "3️⃣  Access the application:"
echo "   • Application: http://localhost:8000/"
echo ""
echo -e "${BLUE}📚 About Turso Database:${NC}"
echo "   Local Turso database file: runtime/databases/bloggy.turso.db"
echo "   Uses import turso and turso.connect() API pattern"
echo ""
echo -e "${GREEN}Happy coding with Turso! 🗄️${NC}"
echo ""