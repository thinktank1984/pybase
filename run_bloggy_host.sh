#!/bin/bash

# Runtime Application Run Script - Host Mode Only
# Runs locally on the host machine without Docker

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

echo -e "${BLUE}🚀 Starting Runtime Application (host mode)...${NC}"
echo ""

# Set environment variable for SQLite database for local development
export DATABASE_URL="sqlite://runtime/databases/main.db"

# Run setup script first to ensure environment is ready
echo -e "${BLUE}Running setup checks...${NC}"
"$PROJECT_ROOT/setup/setup.sh" --local
echo ""

# Validate models for anti-patterns
echo -e "${BLUE}Validating Emmett models...${NC}"
cd runtime
if python validate_models.py --all --severity warning; then
    echo -e "${GREEN}✅ Model validation passed${NC}"
else
    echo -e "${YELLOW}⚠ Model validation found issues (see output above)${NC}"
fi
cd "$PROJECT_ROOT"
echo ""

# Run database migrations before starting server
echo -e "${BLUE}Running database migrations...${NC}"
cd runtime
if DATABASE_URL="sqlite:///workspaces/pybase/runtime/databases/main.db" ../venv/bin/emmett migrations up 2>/dev/null; then
    echo -e "${GREEN}✅ Database migrations completed${NC}"
else
    # Migrations might fail if tables already exist - that's OK
    echo -e "${YELLOW}⚠️  Migration note: Database might already be migrated${NC}"
fi
cd "$PROJECT_ROOT"
echo ""

# Build Tailwind CSS before starting server
echo -e "${BLUE}Building Tailwind CSS...${NC}"
cd runtime
if command -v npm &> /dev/null; then
    npm install --silent 2>&1 | grep -v "npm WARN" || true
    npm run build:css
    echo -e "${GREEN}✅ Tailwind CSS built successfully${NC}"
else
    echo -e "${RED}❌ npm not found! Please install Node.js and npm${NC}"
    echo "   Visit: https://nodejs.org/"
    exit 1
fi
echo ""

echo -e "${GREEN}✅ Setup complete! Starting development server...${NC}"
echo ""
echo "Access the application at: ${GREEN}http://localhost:8000${NC}"
echo "In GitHub Codespaces: Use port forwarding to access the app"
echo ""
echo "Login with:"
echo "  Email: ${YELLOW}doc@emmettbrown.com${NC}"
echo "  Password: ${YELLOW}fluxcapacitor${NC}"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the server - bind to all interfaces for GitHub Codespaces compatibility
uv run --python ../venv/bin/python emmett develop --host 0.0.0.0