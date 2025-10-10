#!/bin/bash

# DjangoBase Setup Script
# This script sets up the Python environment for the DjangoBase application.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up DjangoBase...${NC}"
echo ""

# Check Python version
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    echo "Please install Python 3.13+ and try again."
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.13"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" 2>/dev/null; then
    echo -e "${RED}❌ Python 3.13+ is required (you have $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"

# Navigate to project root (one level up from setup/)
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

# Check Docker
echo ""
echo -e "${BLUE}Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version 2>/dev/null)
    echo -e "${GREEN}✅ Docker is available: $DOCKER_VERSION${NC}"
    
    # Check docker compose
    if docker compose version &> /dev/null; then
        COMPOSE_VERSION=$(docker compose version)
        echo -e "${GREEN}✅ Docker Compose is available: $COMPOSE_VERSION${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker Compose not found${NC}"
        echo "Install with: brew install docker-compose"
    fi
else
    echo -e "${YELLOW}⚠️  Docker not found${NC}"
    echo "For full development experience, install Docker:"
    echo "  https://docs.docker.com/get-docker/"
fi

# Check just
echo ""
echo -e "${BLUE}Checking just command runner...${NC}"
if command -v just &> /dev/null; then
    JUST_VERSION=$(just --version 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ just is available: $JUST_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  just not found${NC}"
    echo "just is a command runner that simplifies Docker commands."
    echo "Install with: brew install just"
    echo "Or continue without it (use docker compose commands directly)"
fi

# Ask user about setup mode
echo ""
echo -e "${BLUE}Choose setup mode:${NC}"
echo "1) Docker (recommended) - Full environment with PostgreSQL, Redis, etc."
echo "2) Local - Install dependencies locally with uv"
echo "3) Both - Set up both Docker and local environment"
echo ""
read -p "Enter choice [1-3] (default: 1): " -n 1 -r SETUP_MODE
echo ""

if [ -z "$SETUP_MODE" ]; then
    SETUP_MODE="1"
fi

# Docker setup
if [[ "$SETUP_MODE" == "1" ]] || [[ "$SETUP_MODE" == "3" ]]; then
    echo ""
    echo -e "${BLUE}Setting up Docker environment...${NC}"
    
    # Check if Docker is running
    echo "Checking Docker..."
    if ! docker info > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Docker is not running${NC}"
        echo -e "${BLUE}Starting Docker Desktop...${NC}"
        
        # Open Docker Desktop on macOS
        open -a Docker
        
        # Wait for Docker to start (max 60 seconds)
        echo "Waiting for Docker to start..."
        for i in {1..60}; do
            if docker info > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Docker is ready${NC}"
                break
            fi
            if [ $i -eq 60 ]; then
                echo -e "${RED}❌ Docker is taking longer than expected to start${NC}"
                echo "Please wait for Docker Desktop to fully start, then run this script again."
                exit 1
            fi
            sleep 1
        done
    else
        echo -e "${GREEN}✅ Docker is running${NC}"
    fi
    echo ""
    
    # Build Docker containers
    echo "Building Docker containers (this may take a few minutes)..."
    if just build; then
        echo -e "${GREEN}✅ Docker containers built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build Docker containers${NC}"
        exit 1
    fi
    
    # Start containers
    echo ""
    echo "Starting Docker services..."
    if just services; then
        echo -e "${GREEN}✅ Docker services started${NC}"
    else
        echo -e "${RED}❌ Failed to start Docker containers${NC}"
        exit 1
    fi
    
    # Run migrations in Docker
    echo ""
    echo "Running Django migrations in Docker..."
    sleep 3  # Wait for PostgreSQL to be ready
    
    # Create migrations for userapp if needed
    echo "Creating userapp migrations..."
    just manage makemigrations userapp || {
        echo -e "${YELLOW}⚠️  No new userapp migrations needed${NC}"
    }
    
    # Apply all migrations
    just manage migrate || {
        echo -e "${YELLOW}⚠️  Migrations failed, you may need to run them manually${NC}"
    }
    
    echo -e "${GREEN}✅ Database migrations completed${NC}"
fi

# Local setup
if [[ "$SETUP_MODE" == "2" ]] || [[ "$SETUP_MODE" == "3" ]]; then
    echo ""
    echo -e "${BLUE}Setting up local environment...${NC}"
    
    cd djangobase || exit 1
    
    # Sync dependencies with uv
    echo "Installing Python dependencies with uv (from pyproject.toml)..."
    echo "This may take a few minutes..."
    if uv sync; then
        echo -e "${GREEN}✅ All dependencies installed successfully${NC}"
    else
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        echo "Please check the error messages above and try again"
        exit 1
    fi
    
    # Ask about optional extras
    echo ""
    echo -e "${BLUE}Optional: Install additional libraries?${NC}"
    echo "This includes extras for:"
    echo "  • Data processing (pandas, Excel, PDF)"
    echo "  • Cloud integrations (Google Cloud, AWS)"
    echo "  • Web scraping (BeautifulSoup, Scrapy)"
    echo "  • Monitoring (Sentry, enhanced logging)"
    echo "  • GraphQL support"
    echo ""
    read -p "Install optional extras? [y/N] " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}Installing optional dependencies...${NC}"
        if uv pip install -r ../setup/requirements.txt; then
            echo -e "${GREEN}✅ Optional dependencies installed${NC}"
        else
            echo -e "${YELLOW}⚠️  Some optional dependencies failed to install${NC}"
            echo "You can install them later with: cd djangobase && uv pip install -r ../setup/requirements.txt"
        fi
    else
        echo "Skipping optional extras."
        echo "Install later with: cd djangobase && uv pip install -r setup/requirements.txt"
    fi
    
    # Run migrations locally (if not using Docker)
    if [[ "$SETUP_MODE" == "2" ]]; then
        echo ""
        echo -e "${BLUE}Running Django migrations...${NC}"
        
        # Create migrations for userapp if needed
        echo "Creating userapp migrations..."
        uv run python manage.py makemigrations userapp 2>/dev/null || {
            echo -e "${YELLOW}⚠️  No new userapp migrations needed${NC}"
        }
        
        # Apply all migrations
        if uv run python manage.py migrate 2>/dev/null; then
            echo -e "${GREEN}✅ Database migrations completed${NC}"
        else
            echo -e "${YELLOW}⚠️  Database migrations skipped or failed${NC}"
            echo "You may need to configure DATABASE_URL first"
        fi
    fi
    
    cd ..
fi

# Create necessary directories
echo ""
echo -e "${BLUE}Creating project directories...${NC}"
DIRECTORIES=("data" "logs" "uploads" "static" "documentation")

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}✅ Created: $dir/${NC}"
    else
        echo "✓ Already exists: $dir/"
    fi
done

# Create superuser (optional)
if [[ "$SETUP_MODE" == "1" ]] || [[ "$SETUP_MODE" == "3" ]]; then
    echo ""
    read -p "Create Django superuser now? [y/N] " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}Creating Django superuser...${NC}"
        just manage createsuperuser || {
            echo -e "${YELLOW}⚠️  Superuser creation skipped or failed${NC}"
        }
    fi
elif [[ "$SETUP_MODE" == "2" ]]; then
    echo ""
    read -p "Create Django superuser now? [y/N] " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd djangobase || exit 1
        echo ""
        echo -e "${BLUE}Creating Django superuser...${NC}"
        uv run python manage.py createsuperuser || {
            echo -e "${YELLOW}⚠️  Superuser creation skipped or failed${NC}"
        }
        cd ..
    fi
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 DjangoBase Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo ""

if [[ "$SETUP_MODE" == "1" ]] || [[ "$SETUP_MODE" == "3" ]]; then
    echo -e "${YELLOW}📦 Docker Mode${NC}"
    echo ""
    echo "1️⃣  Start the development server:"
    echo -e "   ${YELLOW}./run.sh${NC}"
    echo "   Or manually:"
    echo -e "   ${YELLOW}just up${NC}"
    echo ""
    echo "2️⃣  Access the application:"
    echo "   • Django admin: http://localhost:8000/admin/"
    echo "   • API: http://localhost:8000/api/"
    echo "   • API docs: http://localhost:8000/api/docs/"
    echo "   • Flower (Celery): http://localhost:5555/"
    echo "   • Mailpit: http://localhost:8025/"
    echo ""
    echo "3️⃣  Run commands:"
    echo -e "   ${YELLOW}just manage <command>${NC}    # Django management commands"
    echo -e "   ${YELLOW}just shell${NC}               # Open bash in container"
    echo -e "   ${YELLOW}just logs${NC}                # View logs"
    echo -e "   ${YELLOW}just down${NC}                # Stop containers"
    echo ""
fi

if [[ "$SETUP_MODE" == "2" ]] || [[ "$SETUP_MODE" == "3" ]]; then
    echo -e "${YELLOW}💻 Local Mode${NC}"
    echo ""
    echo "1️⃣  Start the development server:"
    echo -e "   ${YELLOW}cd djangobase${NC}"
    echo -e "   ${YELLOW}uv run python manage.py runserver${NC}"
    echo ""
    echo "2️⃣  Access the application:"
    echo "   • Django admin: http://localhost:8000/admin/"
    echo "   • API: http://localhost:8000/api/"
    echo ""
    echo "3️⃣  Run Django commands:"
    echo -e "   ${YELLOW}uv run python manage.py <command>${NC}"
    echo ""
fi

echo -e "${BLUE}🧪 Run tests:${NC}"
if [[ "$SETUP_MODE" == "1" ]]; then
    echo -e "   ${YELLOW}./run_tests.sh --docker${NC}"
    echo -e "   ${YELLOW}./run_tests.sh --docker --quick${NC}  (fast)"
elif [[ "$SETUP_MODE" == "2" ]]; then
    echo -e "   ${YELLOW}./run_tests.sh${NC}"
    echo -e "   ${YELLOW}./run_tests.sh --quick${NC}  (fast)"
else
    echo -e "   ${YELLOW}./run_tests.sh --docker${NC}  (recommended)"
    echo -e "   ${YELLOW}./run_tests.sh${NC}  (local)"
fi
echo ""
echo -e "${BLUE}📚 Useful commands:${NC}"
echo "   • Format code: cd djangobase && uv run ruff format ."
echo "   • Lint code: cd djangobase && uv run ruff check ."
echo "   • Type check: cd djangobase && uv run mypy djangobase"
echo "   • Create migration: uv run python manage.py makemigrations"
echo "   • Apply migration: uv run python manage.py migrate"
echo "   • Run Celery: uv run celery -A config.celery_app worker -l info"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo "   • Quick start: README.md"
echo "   • Testing: documentation/TESTING.md"
echo "   • Implementation: specifications/implementation_plan.md"
echo ""
echo -e "${BLUE}📦 Optional extras:${NC}"
echo "   Install additional libraries anytime with:"
echo -e "   ${YELLOW}cd djangobase && uv pip install -r ../setup/requirements.txt${NC}"
echo ""
echo "   Includes: pandas, Excel, PDF, cloud integrations, web scraping, etc."
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""