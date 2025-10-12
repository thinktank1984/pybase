# Models Directory Structure

This directory contains all model definitions organized by Active Record pattern principles.

## Structure

Each model has its own subdirectory containing a single `model.py` file with everything:

```
models/
├── __init__.py          # Package initialization, exports all models and utilities
├── utils.py             # Shared utility functions (get_or_404, etc.)
│
├── user/                # User model package
│   ├── __init__.py      # Exports User, is_admin, get_current_user, is_authenticated, setup
│   └── model.py         # User model, authentication utilities, and REST API
│
├── post/                # Post model package
│   ├── __init__.py      # Exports Post, setup
│   └── model.py         # Post model, routes, and REST API
│
└── comment/             # Comment model package
    ├── __init__.py      # Exports Comment, setup
    └── model.py         # Comment model and REST API
```

## What's in `model.py`

Each `model.py` contains everything for that model:
- Model class definition (inherits from `emmett.orm.Model`)
- Field definitions with validation and configuration
- Business logic methods and utilities
- Route definitions (using `@app.route`)
- REST API module setup with callbacks
- A `setup(app)` function that registers routes and APIs

## Shared Utilities (`utils.py`)

Contains helper functions used across multiple models:
- `get_or_404(model, record_id)`: Get record or abort with 404

## Usage in `app.py`

```python
# Import models and utilities
from models import User, Post, Comment, is_admin, get_current_user, is_authenticated

# Setup routes and APIs for all models (single call)
from models import setup_all
api_modules = setup_all(app)
```

## Benefits of This Structure

1. **Simplicity**: Each model is one file with everything related
2. **Encapsulation**: Model owns its complete behavior (data + routes + API)
3. **Modularity**: Easy to find and modify all model-specific code
4. **Scalability**: New models follow the same simple pattern
5. **Active Record**: Models contain data + behavior (not presentation)
6. **Less Files**: No separate api.py and views.py files

## What Stays Outside Models

- **HTML Templates**: Remain in `runtime/templates/`
- **Static assets**: CSS, JS, images in `runtime/static/`
- **Application config**: `app.py` for app-level setup
- **Database config**: `app.py` for database connection
- **Middleware/Pipeline**: `app.py` for global concerns

## Adding a New Model

1. Create directory: `models/new_model/`
2. Create `model.py` with:
   - Model class definition
   - Routes (if needed)
   - REST API setup
   - `setup(app)` function
3. Create `__init__.py` to export the model and setup
4. Update `models/__init__.py` to import and export
5. Update `setup_all()` to call your model's setup
6. HTML templates go in `runtime/templates/`

## Testing

Test model imports:
```bash
cd runtime
python -c "from models import User, Post, Comment; print('✓ Models loaded')"
```

Test full app:
```bash
emmett develop
```
