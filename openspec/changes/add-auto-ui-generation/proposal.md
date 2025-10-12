# Add Auto UI Generation from Models

## Why

Developers spend significant time writing boilerplate code for CRUD operations: defining routes, creating form templates, handling validation, and rendering data. Emmett already provides `Form.from_model()` for basic form generation, but developers still need to manually create routes, templates, and views for each model.

Auto UI generation from models will dramatically reduce development time by automatically creating complete CRUD interfaces with proper styling, validation, and routing based on model definitions. This allows developers to focus on business logic while getting professional-looking admin interfaces automatically.

## What Changes

- Add `AutoUIGenerator` class that introspects Emmett ORM models and generates complete CRUD interfaces
- Provide decorator-based API: `@app.auto_ui(Post, url_prefix='/admin/posts')` to enable auto UI for a model
- Generate routes automatically: list, create, read, update, delete operations
- Generate templates automatically using Tailwind CSS styling
- Add `ui_mapping.json` configuration file that maps model field types to UI components with attributes
- Support customization through model metadata: field display names, widget types, permissions, list columns
- Allow custom UI mappings via `ui_mapping_custom.json` override file
- Provide hooks for custom validation, permissions, and business logic
- Include pagination, search, and filtering in list views
- Support field-level customization via model decorators
- Generate responsive, accessible UI following modern UX practices

## Impact

### Affected Specs
- **New Capability**: `auto-ui-generation` - Complete specification for auto UI generation system

### Affected Code
- **New File**: `runtime/auto_ui_generator.py` - Core auto UI generation logic
- **New File**: `runtime/ui_mapping.json` - Default field type to UI component mappings
- **New Directory**: `runtime/templates/auto_ui/` - Default templates for generated UIs
- **Modified**: `runtime/app.py` - Add example usage of auto UI generation
- **Modified**: `runtime/tests.py` - Add tests for auto UI generation
- **New File**: `runtime/ui_tests.py` - UI tests for generated interfaces using Chrome DevTools

### Breaking Changes
None - this is a new optional feature that doesn't affect existing code.

### Migration Path
Not applicable - new feature only.

