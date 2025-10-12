#!/bin/bash

# Docker Entrypoint Script for Runtime Application
# This script runs inside the Docker container before starting the application

set -e

echo "🔵 Docker Entrypoint: Starting initialization..."

# Navigate to runtime directory
cd /app/runtime

# Build Tailwind CSS
echo "🎨 Building Tailwind CSS..."
if [ -f "package.json" ]; then
    # Remove host's node_modules to avoid binary compatibility issues
    # (host might be macOS, container is Linux)
    if [ -d "node_modules" ]; then
        echo "   Removing host node_modules (incompatible binaries)..."
        rm -rf node_modules
    fi
    
    # Install fresh Linux-compatible packages
    echo "   Installing npm packages for Linux..."
    npm install --silent 2>&1 | grep -v "npm WARN" || true
    
    # Build Tailwind CSS
    echo "   Compiling Tailwind CSS..."
    npm run build:css 2>&1 | tail -2
    echo "✅ Tailwind CSS built successfully"
else
    echo "⚠️  package.json not found, skipping Tailwind build"
fi

# Run database migrations
echo "🗄️  Running database migrations..."
emmett migrations up || echo "⚠️  No migrations to run or migrations failed"

echo "✅ Initialization complete!"
echo ""

# Execute the main command (passed as arguments to this script)
exec "$@"

