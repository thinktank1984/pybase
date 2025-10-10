#!/bin/bash

# DjangoBase Run Script
# Starts the development server with Docker

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse command line arguments
REBUILD=false
for arg in "$@"; do
    case $arg in
        --rebuild)
            REBUILD=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./run.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --rebuild    Rebuild Docker images before starting containers"
            echo "  --help, -h   Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run.sh              # Start containers with existing images"
            echo "  ./run.sh --rebuild    # Rebuild images and start containers"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if setup has been completed
if [ ! -d "djangobase/.venv" ] && [ ! "$(docker images -q djangobase_local_django 2> /dev/null)" ]; then
    echo -e "${YELLOW}⚠️  Setup not detected. Running setup first...${NC}"
    echo ""
    ./setup/setup.sh
    echo ""
fi

echo -e "${BLUE}🚀 Starting DjangoBase...${NC}"
echo ""

# Kill any processes using the ports
echo "Freeing up ports..."
lsof -ti :3000 | xargs kill -9 2>/dev/null || true
lsof -ti :5678 | xargs kill -9 2>/dev/null || true
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :8025 | xargs kill -9 2>/dev/null || true

echo -e "${GREEN}✅ Ports cleared${NC}"
echo ""

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
            echo -e "${YELLOW}⚠️  Docker is taking longer than expected to start${NC}"
            echo "Please wait for Docker Desktop to fully start, then run this script again."
            exit 1
        fi
        sleep 1
    done
else
    echo -e "${GREEN}✅ Docker is running${NC}"
fi

echo ""

# Rebuild if requested
if [ "$REBUILD" = true ]; then
    echo -e "${BLUE}🔨 Rebuilding Docker images...${NC}"
    just build
    echo -e "${GREEN}✅ Docker images rebuilt${NC}"
    echo ""
fi

echo -e "${BLUE}Starting Docker containers in background...${NC}"
just up

echo ""
echo -e "${GREEN}✅ DjangoBase started successfully!${NC}"
echo ""
echo -e "${BLUE}Services running at:${NC}"
echo "  🌐 Django:     http://localhost:8000"
echo "  📧 Mailpit:    http://localhost:8025"
echo "  🌸 Flower:     http://localhost:5678"
echo "  ⚛️  Node:       http://localhost:3000"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  View logs:     just logs"
echo "  Stop:          just down"
echo "  Restart:       just restart"
echo "  Shell:         just shell"
echo "  Rebuild:       ./run.sh --rebuild"
echo ""
