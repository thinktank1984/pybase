#!/bin/bash

# Bloggy Setup Script
# This script sets up the Emmett-based Bloggy example application.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up Bloggy (Emmett example app)...${NC}"
echo ""

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

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1
PROJECT_ROOT=$(pwd)
echo -e "${GREEN}✅ Project root: $PROJECT_ROOT${NC}"

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

# Install Emmett and dependencies
echo ""
echo -e "${BLUE}Installing Emmett framework and dependencies...${NC}"
uv pip install --python venv/bin/python emmett>=2.5.0
uv pip install --python venv/bin/python pytest>=7.0.0

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Run database migrations
echo ""
echo -e "${BLUE}Setting up database...${NC}"
cd bloggy || exit 1

# Create databases directory if it doesn't exist
mkdir -p databases

# Check if migrations exist and run them
if [ -d "migrations" ] && [ "$(ls -A migrations/*.py 2>/dev/null)" ]; then
    echo "Applying migrations..."
    if uv run --python ../venv/bin/python emmett migrations up; then
        echo -e "${GREEN}✅ Migrations applied${NC}"
    else
        echo -e "${YELLOW}⚠️  Migration failed - trying to generate initial migration...${NC}"
        uv run --python ../venv/bin/python emmett migrations generate
        uv run --python ../venv/bin/python emmett migrations up || {
            echo -e "${RED}❌ Migrations failed${NC}"
        }
    fi
else
    echo "No migrations found, generating initial migration..."
    uv run --python ../venv/bin/python emmett migrations generate
    uv run --python ../venv/bin/python emmett migrations up || {
        echo -e "${RED}❌ Migrations failed${NC}"
    }
fi

# Setup admin user
echo ""
echo -e "${BLUE}Setting up admin user...${NC}"
if uv run --python ../venv/bin/python emmett setup; then
    echo -e "${GREEN}✅ Admin user created${NC}"
else
    echo -e "${RED}❌ Admin setup failed${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Bloggy Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo ""
echo "1️⃣  Start the Bloggy application:"
echo -e "   ${YELLOW}./run_bloggy.sh${NC}"
echo "   Or manually:"
echo -e "   ${YELLOW}cd bloggy && uv run emmett develop${NC}"
echo ""
echo "2️⃣  Access the application:"
echo "   • Application: http://localhost:8000/"
echo "   • Login with:"
echo "     - Email: doc@emmettbrown.com"
echo "     - Password: fluxcapacitor"
echo ""
echo "3️⃣  Run tests (coverage enabled by default):"
echo -e "   ${YELLOW}./run_tests.sh${NC}"
echo "   Or manually:"
echo -e "   ${YELLOW}cd bloggy && uv run pytest tests.py${NC}"
echo ""
echo -e "${BLUE}📚 About Bloggy:${NC}"
echo "   Bloggy is a micro-blogging application built with Emmett framework."
echo "   It demonstrates:"
echo "   • User authentication and authorization"
echo "   • Database models and ORM"
echo "   • Form handling and validation"
echo "   • Template rendering"
echo "   • Admin-only features"
echo ""
echo -e "${BLUE}📖 Emmett Documentation:${NC}"
echo "   See emmett_documentation/ for comprehensive framework docs"
echo ""
echo -e "${GREEN}Happy blogging! 📝${NC}"
echo ""

