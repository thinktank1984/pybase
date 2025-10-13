# Model Validation System

This document describes the model validation system that helps maintain code quality by detecting anti-patterns in Emmett models.

## Overview

The model validation system ensures that Emmett models follow best practices and don't contain anti-patterns like HTTP handling, template rendering, or external API calls in model classes.

## Components

### 1. Model Validator (`runtime/validate_models.py`)

A comprehensive validation script that checks models for anti-patterns.

**Usage:**
```bash
cd runtime

# Validate all models
python validate_models.py --all

# Validate specific models
python validate_models.py User Post

# Output as JSON
python validate_models.py --all --json

# Show only errors (hide warnings)
python validate_models.py --all --severity error

# Verbose output
python validate_models.py --all --verbose
```

**Anti-patterns detected:**
- ✗ HTTP request/response handling in models
- ✗ Template rendering in models
- ✗ HTML generation in models
- ✗ External API calls in models
- ✗ Direct session access in models
- ✗ Email sending in models
- ✗ Overly complex methods (>50 lines)
- ℹ Missing validation rules
- ℹ Missing docstrings

### 2. Wrapper Script (`runtime/validate.sh`)

Simple wrapper that runs validation with proper environment setup.

**Usage:**
```bash
./runtime/validate.sh --all
```

### 3. Application Startup Integration (`run_bloggy.sh`)

Model validation runs automatically when starting the application:

```bash
./run_bloggy.sh

# Output:
🚀 Starting Runtime Application in Docker...

Running setup checks...
✅ Setup complete!

Validating Emmett models...
✓ User: PASS (no violations)
✓ Post: PASS (no violations)
✓ Comment: PASS (no violations)
✅ Model validation passed
```

**Behavior:**
- Runs after setup checks, before app starts
- Shows warnings but doesn't block startup
- Works in both Docker and local modes

### 4. Git Pre-Commit Hook (`hooks/pre-commit`)

Prevents committing code with model anti-patterns.

**Installation:**
```bash
# One-time setup
./hooks/install.sh

# Manual installation
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Behavior:**
- Runs automatically on `git commit`
- Only checks when model files are modified
- **Blocks commits** if models contain errors
- Allows commits if models only have warnings
- Can be bypassed with `git commit --no-verify` (not recommended)

**Example workflow:**
```bash
# Modify a model with anti-patterns
vim runtime/models/post.py

# Try to commit
git add runtime/models/post.py
git commit -m "Update Post model"

# Hook runs and blocks commit:
🔍 Model files changed, running validation...

❌ Model validation failed

Models contain anti-patterns that must be fixed before committing.

To fix:
  1. Review the validation errors above
  2. Fix the issues in your model files
  3. Re-run: python runtime/validate_models.py --all

To commit anyway (NOT RECOMMENDED): git commit --no-verify
```

## Validation Rules

### Error-Level (Block Commits)

These violations will prevent commits and must be fixed:

1. **HTTP Handling**
   - `request.` usage
   - `response.` usage
   - `redirect()` calls
   - `abort()` calls
   - **Fix:** Move HTTP handling to controllers/route handlers

2. **Template Rendering**
   - `render_template()` calls
   - Template engine usage
   - **Fix:** Move presentation logic to views

3. **HTML Generation**
   - HTML tags in strings (`<div>`, `<p>`, etc.)
   - **Fix:** Use templates for HTML generation

### Warning-Level (Allow Commits)

These violations are reported but don't block commits:

1. **External API Calls**
   - `requests.` usage
   - `urllib.` usage
   - `httpx.` or `aiohttp.` usage
   - **Fix:** Move API calls to service layer

2. **Session Access**
   - Direct `session.` or `session[]` access
   - **Fix:** Pass user/data as method parameters

3. **Email Sending**
   - `mailer.` usage
   - `send_email()` calls
   - **Fix:** Move email sending to service layer

### Info-Level (Informational)

These are suggestions for improvement:

1. **Complexity**
   - Methods longer than 50 lines
   - Methods with multiple responsibilities
   - **Fix:** Break into smaller methods or move to services

2. **Documentation**
   - Missing model docstrings
   - Missing method docstrings
   - **Fix:** Add descriptive docstrings

3. **Validation**
   - Models with fields but no validation rules
   - **Fix:** Add validation attribute to ensure data integrity

## Integration Points

### 1. Development Workflow
```bash
./run_bloggy.sh  # Validates before starting app
```

### 2. Git Workflow
```bash
git commit       # Validates before allowing commit
```

### 3. CI/CD (Recommended)
```yaml
# GitHub Actions example
- name: Validate Models
  run: |
    cd runtime
    python validate_models.py --all --severity error

# Exit code 1 if errors found, blocks deployment
```

### 4. Manual Validation
```bash
cd runtime
python validate_models.py --all --verbose
```

## Benefits

**For Developers:**
- ✅ Catches anti-patterns early (before code review)
- ✅ Clear error messages with fix suggestions
- ✅ Fast feedback loop
- ✅ Learn best practices through validation messages

**For Code Quality:**
- ✅ Enforces architectural boundaries
- ✅ Prevents mixing concerns (models vs controllers)
- ✅ Maintains separation of concerns
- ✅ Consistent patterns across codebase

**For Team:**
- ✅ Reduces "please fix this" comments in PR reviews
- ✅ Self-documenting best practices
- ✅ Automated enforcement of standards
- ✅ Easier onboarding (validation teaches patterns)

## Repository Policies

This validation system supports our repository policies:

### NO MOCKING POLICY
Models should contain domain logic only, not HTTP/template/external concerns. This makes them easier to test with real integration tests.

### SEPARATION OF CONCERNS
- **Models:** Domain logic, data validation, relationships
- **Controllers:** HTTP handling, request/response
- **Views:** Template rendering, HTML generation
- **Services:** External APIs, email, complex workflows

## Troubleshooting

### Hook not running

```bash
# Check installation
ls -la .git/hooks/pre-commit

# Make executable
chmod +x .git/hooks/pre-commit

# Test manually
./hooks/pre-commit
```

### Python not found

The system tries multiple Python interpreters:
1. Project venv: `../venv/bin/python`
2. uv wrapper: `uv run python`
3. System: `python3` or `python`

### Validation errors unclear

```bash
# Run with verbose output
cd runtime
python validate_models.py --all --verbose

# Run with specific severity
python validate_models.py --all --severity info
```

### Need to bypass validation

```bash
# For WIP commits only (not recommended for main branch)
git commit --no-verify -m "WIP: refactoring models"
```

## Examples

### Good Model (Passes Validation)

```python
from emmett.orm import Model, Field

class Post(Model):
    """Blog post with title and content."""
    
    title = Field.string()
    text = Field.text()
    author = Field.belongs_to('user')
    created_at = Field.datetime()
    
    validation = {
        'title': {'presence': True, 'len': {'range': (3, 250)}},
        'text': {'presence': True}
    }
    
    def summary(self, length: int = 100) -> str:
        """Return truncated summary of post text.
        
        Args:
            length: Maximum length of summary
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if len(self.text) <= length:
            return self.text
        return self.text[:length] + '...'
```

### Bad Model (Fails Validation)

```python
from emmett.orm import Model, Field
from emmett import request, redirect  # ✗ HTTP imports

class Post(Model):
    title = Field.string()
    text = Field.text()
    
    def create_from_request(self):  # ✗ HTTP handling in model
        """Create post from HTTP request."""
        self.title = request.post_vars.title  # ✗ Direct request access
        self.text = request.post_vars.text
        self.save()
        redirect('/posts')  # ✗ HTTP redirect in model
        
    def render_html(self):  # ✗ HTML generation in model
        """Render post as HTML."""
        return f"<div class='post'><h1>{self.title}</h1><p>{self.text}</p></div>"
```

**Validation output:**
```
✗ Post: FAIL
   Found 3 violation(s): 3 errors

   [HTTP_HANDLING]
     ✗ Post.create_from_request
        Methods should not accept request objects
        → Move HTTP handling to controllers. Models should only contain domain logic.
     
     ✗ Post (line 12)
        Found HTTP request access in model
        → Move HTTP handling to controllers
     
     ✗ Post (line 15)
        Found HTTP redirect in model
        → Move HTTP handling to controllers
   
   [HTML_GENERATION]
     ✗ Post (line 19)
        Models should not generate HTML
        → Use templates for HTML generation

✗ Validation failed with 3 error(s)
```

## See Also

- `/runtime/validate_models.py` - Validation script source
- `/runtime/validate.sh` - Wrapper script
- `/hooks/README.md` - Git hooks documentation
- `/run_bloggy.sh` - Application startup script
- `/AGENTS.md` - Complete repository guidelines
- `/documentation/NO_MOCKING_ENFORCEMENT.md` - Testing policies

