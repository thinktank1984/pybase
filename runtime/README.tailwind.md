# Tailwind CSS Integration Guide

This document explains how to use Tailwind CSS in the Emmett Framework runtime application.

## Overview

Tailwind CSS is integrated using the standalone CLI (no Node.js required). The setup includes:
- **Tailwind CLI binary** installed in Docker container
- **Configuration file** at `runtime/tailwind.config.js`
- **Input CSS** at `runtime/static/input.css` with Tailwind directives
- **Output CSS** generated to `runtime/static/tailwind.css`

## Quick Start

### Building Tailwind CSS

#### Using Docker (Recommended)

```bash
# One-time build
docker compose -f docker/docker-compose.yaml run --rm runtime bash -c "cd runtime && /usr/local/bin/tailwind -i static/input.css -o static/tailwind.css"

# Watch mode (automatically rebuilds on changes)
docker compose -f docker/docker-compose.yaml run --rm runtime bash -c "cd runtime && /usr/local/bin/tailwind -i static/input.css -o static/tailwind.css --watch"

# Production build (minified)
docker compose -f docker/docker-compose.yaml run --rm runtime bash -c "cd runtime && /usr/local/bin/tailwind -i static/input.css -o static/tailwind.css --minify"
```

#### Using Local Development

If you've installed Tailwind CLI locally:

```bash
cd runtime
tailwind -i static/input.css -o static/tailwind.css

# Watch mode
tailwind -i static/input.css -o static/tailwind.css --watch

# Production build
tailwind -i static/input.css -o static/tailwind.css --minify
```

## Using Tailwind in Templates

Tailwind CSS is already included in the base layout template. Just use utility classes in your HTML:

### Example: Basic Styling

```html
<!-- runtime/templates/example.html -->
{{extend 'layout.html'}}

<div class="max-w-2xl mx-auto p-6">
    <h1 class="text-3xl font-bold text-gray-800 mb-4">
        Hello Tailwind!
    </h1>
    
    <p class="text-gray-600 leading-relaxed">
        This paragraph uses Tailwind utility classes.
    </p>
    
    <button class="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded">
        Click Me
    </button>
</div>
```

### Example: Responsive Design

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="bg-white p-4 rounded-lg shadow">Card 1</div>
    <div class="bg-white p-4 rounded-lg shadow">Card 2</div>
    <div class="bg-white p-4 rounded-lg shadow">Card 3</div>
</div>
```

### Example: Forms with Tailwind

```html
<form class="space-y-4">
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
            Email
        </label>
        <input type="email" 
               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
               placeholder="you@example.com">
    </div>
    
    <button type="submit" 
            class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors">
        Submit
    </button>
</form>
```

## Configuration

### Customizing Theme

Edit `runtime/tailwind.config.js` to customize colors, spacing, fonts, etc.:

```javascript
module.exports = {
  content: [
    "./templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        'brand-blue': '#377ba8',
        'brand-gray': '#eee',
      },
      fontFamily: {
        'serif': ['Georgia', 'serif'],
        'sans': ['sans-serif'],
      },
    },
  },
  plugins: [],
}
```

### Adding Content Paths

If you have additional templates or components in other directories:

```javascript
module.exports = {
  content: [
    "./templates/**/*.html",
    "./components/**/*.html",  // Add custom paths
    "./admin/**/*.html",
  ],
  // ...
}
```

### Safelisting Dynamic Classes

If you generate class names dynamically (e.g., `text-${color}-500`), add them to the safelist:

```javascript
module.exports = {
  content: [
    "./templates/**/*.html",
  ],
  safelist: [
    'text-red-500',
    'text-green-500',
    'text-blue-500',
    'bg-red-100',
    'bg-green-100',
    'bg-blue-100',
  ],
  // ...
}
```

## Coexisting with Custom CSS

Tailwind CSS and custom CSS work together. The load order in `layout.html` is:

1. **Tailwind CSS** (`tailwind.css`) - Loads first
2. **Custom CSS** (`style.css`) - Loads second, can override Tailwind

This means you can:
- Use Tailwind utilities for most styling
- Override with custom CSS when needed
- Gradually migrate from custom CSS to Tailwind

### Example Migration

**Before (custom CSS only):**
```css
/* style.css */
.page { margin: 2em auto; width: 35em; padding: 0.8em; }
```

**After (Tailwind utilities):**
```html
<div class="max-w-2xl mx-auto px-6 py-4">
  <!-- Content -->
</div>
```

**Hybrid Approach:**
```html
<!-- Use Tailwind for layout, custom classes for specific styling -->
<div class="max-w-2xl mx-auto px-6 py-4 page-custom">
  <!-- Content -->
</div>
```

## Development Workflow

### Typical Workflow

1. **Start the application** in Docker:
   ```bash
   docker compose -f docker/docker-compose.yaml up runtime
   ```

2. **In another terminal, start Tailwind watch mode:**
   ```bash
   docker compose -f docker/docker-compose.yaml run --rm runtime bash -c "cd runtime && /usr/local/bin/tailwind -i static/input.css -o static/tailwind.css --watch"
   ```

3. **Edit templates** - Add Tailwind classes to HTML
4. **Tailwind automatically rebuilds** when it detects changes
5. **Refresh browser** to see changes

### Tips for Development

- **Fast rebuilds**: Tailwind watch mode rebuilds in ~100ms
- **No restart needed**: Just refresh the browser after Tailwind rebuilds
- **Check file size**: Development build is ~1-2KB, production should be <20KB with purging

## Production Deployment

For production, always build with `--minify` flag:

```bash
cd runtime
tailwind -i static/input.css -o static/tailwind.css --minify
```

This will:
- Remove unused CSS classes
- Minify the output
- Typically reduce file size from 3MB → 10-20KB

## Common Tailwind Patterns

### Centering Content

```html
<div class="flex items-center justify-center min-h-screen">
  <div class="text-center">
    <h1 class="text-4xl font-bold">Centered Content</h1>
  </div>
</div>
```

### Card Component

```html
<div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
  <h3 class="text-xl font-semibold mb-2">Card Title</h3>
  <p class="text-gray-600">Card content goes here...</p>
</div>
```

### Navigation Bar

```html
<nav class="bg-gray-800 text-white">
  <div class="container mx-auto px-4 py-3 flex items-center justify-between">
    <a href="/" class="text-xl font-bold">Bloggy</a>
    <div class="space-x-4">
      <a href="/login" class="hover:text-gray-300">Login</a>
      <a href="/logout" class="hover:text-gray-300">Logout</a>
    </div>
  </div>
</nav>
```

### Alert Messages

```html
<!-- Success -->
<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
  Success message!
</div>

<!-- Error -->
<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
  Error message!
</div>

<!-- Info -->
<div class="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded">
  Info message!
</div>
```

### Grid Layouts

```html
<!-- 3-column grid on desktop, 1 column on mobile -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>
```

## Troubleshooting

### CSS Not Updating

**Problem**: Changes to templates don't reflect in CSS  
**Solution**:
- Rebuild Tailwind CSS
- Check that `tailwind.config.js` content paths include your template
- Verify Tailwind watch mode is running
- Clear browser cache

### Classes Not Working

**Problem**: Tailwind classes have no effect  
**Solution**:
- Check that `tailwind.css` is included in `layout.html`
- Verify CSS file was generated (check `static/tailwind.css` exists)
- Inspect element in browser to see if styles are applied
- Check for typos in class names

### Large File Size

**Problem**: `tailwind.css` is very large (>1MB)  
**Solution**:
- Use `--minify` flag for production builds
- Verify `content` paths in `tailwind.config.js` are correct
- Production builds with proper purging should be <20KB

### Dynamic Classes Not Working

**Problem**: Dynamically generated classes (e.g., `text-${color}-500`) don't work  
**Solution**:
- Add classes to `safelist` in `tailwind.config.js`
- Or use complete class names: `text-red-500`, `text-blue-500`, etc.
- Tailwind can't detect classes generated at runtime

## Resources

- **Tailwind CSS Docs**: https://tailwindcss.com/docs
- **Tailwind Play (Testing)**: https://play.tailwindcss.com/
- **Emmett Templates Docs**: `/emmett_documentation/docs/templates.md`
- **This Project**: `/runtime/templates/` for examples

## File Reference

```
runtime/
├── tailwind.config.js        # Tailwind configuration
├── static/
│   ├── input.css             # Tailwind directives (source)
│   ├── tailwind.css          # Generated CSS (gitignored)
│   └── style.css             # Custom CSS (preserved)
└── templates/
    ├── layout.html           # Base template (includes Tailwind CSS)
    └── *.html                # Your templates (use Tailwind classes)
```

## Next Steps

1. **Learn Tailwind**: Visit https://tailwindcss.com/docs to learn utility classes
2. **Migrate existing styles**: Gradually replace custom CSS with Tailwind utilities
3. **Create components**: Build reusable HTML snippets with Tailwind
4. **Optimize for production**: Always use `--minify` flag before deployment
5. **Customize theme**: Edit `tailwind.config.js` to match your brand

Happy styling! 🎨

