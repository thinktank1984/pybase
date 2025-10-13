# Git Hooks for Emmett Project

This directory contains git hooks that help maintain code quality and prevent anti-patterns from entering the codebase.

## Available Hooks

### pre-commit

Runs **Emmett model validation** before allowing commits.

**What it does:**
- Checks if any model files have been modified (`runtime/app.py`, `runtime/models/*.py`)
- Runs `validate_models.py` to check for anti-patterns
- **Blocks commits** if models contain errors (anti-patterns)
- **Allows commits** if models only have warnings (can be fixed later)

**Anti-patterns detected:**
- HTTP request/response handling in models
- Template rendering in models
- HTML generation in models
- External API calls in models
- Direct session access in models
- Email sending in models
- Overly complex methods

## Installation

### Automatic Installation (Recommended)

```bash
# From project root
./hooks/install.sh
```

### Manual Installation

```bash
# From project root
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Usage

Once installed, the hooks run automatically:

```bash
# Make changes to models
vim runtime/models/post.py

# Try to commit (hook runs automatically)
git add runtime/models/post.py
git commit -m "Update Post model"

# If validation fails:
❌ Model validation failed

Models contain anti-patterns that must be fixed before committing.

To fix:
  1. Review the validation errors above
  2. Fix the issues in your model files
  3. Re-run: python runtime/validate_models.py --all
```

### Bypassing Hooks (Not Recommended)

If you need to commit despite validation failures:

```bash
git commit --no-verify -m "WIP: fixing models"
```

**⚠️ Warning:** Bypassing hooks should only be done for:
- Work-in-progress commits on feature branches
- Emergency hotfixes (fix the issues ASAP after)

**Never bypass hooks for:**
- Commits to main/master branch
- Pull request commits
- Production deployments

## Testing Hooks Locally

Test the pre-commit hook without committing:

```bash
# From project root
./hooks/pre-commit
```

Or test validation directly:

```bash
cd runtime
python validate_models.py --all
```

## Uninstalling Hooks

```bash
# Remove pre-commit hook
rm .git/hooks/pre-commit
```

## CI/CD Integration

These hooks should also be enforced in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Validate Models
  run: |
    cd runtime
    python validate_models.py --all --severity error
```

## Troubleshooting

### Hook not running

1. Check hook is installed: `ls -la .git/hooks/pre-commit`
2. Check hook is executable: `chmod +x .git/hooks/pre-commit`
3. Run hook manually to see errors: `./hooks/pre-commit`

### Python not found

The hook tries multiple Python interpreters:
1. `../venv/bin/python` (project virtual environment)
2. `uv run python` (if uv is installed)
3. `python3`
4. `python`

Make sure you have Python installed and the project dependencies set up.

### Hook too slow

The hook only validates models when model files are actually changed. If it's still slow:

1. Run validation separately: `python runtime/validate_models.py --all`
2. Fix all issues once
3. Future commits will be fast (no issues to report)

## Why Use Git Hooks?

**Benefits:**
- ✅ Catches anti-patterns before they enter the codebase
- ✅ Enforces best practices automatically
- ✅ Prevents broken code from reaching code review
- ✅ Saves time in code review (fewer "please fix this" comments)
- ✅ Maintains consistent code quality across the team

**Repository Policy:**
This project follows strict **NO MOCKING** and **INTEGRATION TESTING ONLY** policies. Git hooks help enforce architectural best practices to maintain code quality.

## See Also

- `/runtime/validate_models.py` - Model validation script
- `/runtime/validate.sh` - Wrapper script for validation
- `/run_bloggy.sh` - Application startup (includes validation)
- `/documentation/NO_MOCKING_ENFORCEMENT.md` - Testing policies
- `/AGENTS.md` - Complete repository guidelines

