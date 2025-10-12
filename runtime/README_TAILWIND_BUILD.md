# Tailwind CSS Build Guide

## Overview

This application uses Tailwind CSS for styling. Tailwind must be compiled from `static/input.css` into `static/tailwind.css` before running the application.

**✅ AUTOMATIC BUILD**: The `run_bloggy.sh` script automatically builds Tailwind CSS when you start the application, so you usually don't need to do anything manually!

## Why Compilation is Needed

- **Source**: `static/input.css` contains Tailwind directives (`@tailwind base`, `@tailwind components`, `@tailwind utilities`)
- **Output**: `static/tailwind.css` contains the actual CSS classes used in your templates
- **The app loads**: `tailwind.css` (not `input.css`)

Tailwind scans your templates (configured in `tailwind.config.js`) and only includes CSS for classes you actually use, keeping the file size small.

## When to Rebuild

You need to rebuild Tailwind CSS when:
- ✅ You add new Tailwind classes to your templates
- ✅ You modify templates and use different utility classes
- ✅ You update `tailwind.config.js`
- ✅ First time setting up the project
- ❌ You only change Python code (no rebuild needed)
- ❌ You only change custom CSS in `style.css` (no rebuild needed)

## Build Commands

### Option 1: Using npm scripts (Recommended)

```bash
# One-time build (production)
npm run build:css

# Watch mode (auto-rebuild on template changes)
npm run watch:css
```

### Option 2: Direct Tailwind CLI

```bash
# One-time build
npx tailwindcss -i ./static/input.css -o ./static/tailwind.css --minify

# Watch mode
npx tailwindcss -i ./static/input.css -o ./static/tailwind.css --watch
```

### Option 3: Inside Docker Container

```bash
# One-time build in Docker
docker compose -f docker/docker-compose.yaml exec -w /app/runtime runtime npm run build:css

# Watch mode in Docker
docker compose -f docker/docker-compose.yaml exec -w /app/runtime runtime npm run watch:css
```

## Development Workflow

### Recommended: Use run_bloggy.sh (Automatic Build)

```bash
# The script automatically builds Tailwind CSS before starting!
./run_bloggy.sh

# Or for local mode:
./run_bloggy.sh --local

# Or for foreground mode:
./run_bloggy.sh --foreground
```

### Manual Build (Advanced)

If you need to rebuild Tailwind CSS manually without restarting the app:

#### Local Development

```bash
# Terminal 1: Watch and rebuild CSS automatically
cd runtime
npm run watch:css

# Terminal 2: Run the application
cd runtime
uv run emmett develop
```

#### Docker Development

```bash
# Build CSS inside running container
docker compose -f docker/docker-compose.yaml exec -w /app/runtime runtime npm run build:css
```

## Checking If Rebuild is Needed

If you see styling issues (e.g., large icons, missing colors, no spacing), check if Tailwind needs rebuilding:

```bash
# Check the size of tailwind.css (should be several KB if properly compiled)
ls -lh static/tailwind.css

# Check if specific classes exist
grep "h-12" static/tailwind.css
grep "w-8" static/tailwind.css
```

If classes are missing, rebuild with:
```bash
npm run build:css
```

## Tailwind Configuration

The `tailwind.config.js` file tells Tailwind where to look for classes:

```javascript
module.exports = {
  content: [
    "./templates/**/*.html",  // Scans all template files
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

If you add templates in new locations, update the `content` array.

## Troubleshooting

### Problem: CSS classes not working

**Solution**: Rebuild Tailwind CSS
```bash
npm run build:css
```

### Problem: `npx: command not found`

**Solution**: Install Node.js and npm first
```bash
# macOS
brew install node

# Or use Docker which has Node.js pre-installed
docker compose -f docker/docker-compose.yaml exec runtime npm run build:css
```

### Problem: Icons showing too large

**Solution**: This usually means Tailwind classes like `w-8`, `h-12` aren't compiled yet
```bash
npm run build:css
# Then restart the application
```

### Problem: Styles look like basic HTML

**Solution**: Tailwind CSS wasn't built or isn't loading
```bash
# Rebuild
npm run build:css

# Check the file exists and has content
ls -lh static/tailwind.css

# Verify app is serving static files
curl http://localhost:8081/static/tailwind.css
```

## Production Deployment

For production, always build CSS before deploying:

```bash
cd runtime
npm run build:css  # Creates minified tailwind.css
```

Add this to your deployment process or Dockerfile:

```dockerfile
# In Dockerfile
WORKDIR /app/runtime
RUN npm install
RUN npm run build:css
```

## Summary

**Quick Start:**
1. `cd runtime`
2. `npm install` (first time only)
3. `npm run build:css` (every time you change templates)
4. Run your app

**During Development:**
- Use `npm run watch:css` in one terminal
- Run the app in another terminal
- CSS rebuilds automatically when you save template files

