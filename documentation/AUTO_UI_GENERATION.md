# Auto UI Generation

Automatic CRUD interface generation for Emmett ORM models.

## Overview

The Auto UI Generator automatically creates complete CRUD (Create, Read, Update, Delete) interfaces for your Emmett ORM models with:

- ✅ Automatic route generation for all CRUD operations
- ✅ Responsive, Tailwind CSS-styled templates
- ✅ One UI component mapping for each ORM field type (string, text, int, bool, datetime, date, etc.)
- ✅ Pagination, search, filtering, and sorting
- ✅ Permission integration with Emmett Auth
- ✅ Customizable via model configuration
- ✅ Template override support

## Quick Start

### 1. Basic Usage

```python
from auto_ui_generator import auto_ui

# Enable auto UI for your model
auto_ui(app, Post, '/admin/posts')
```

This single line generates all CRUD routes:
- `GET /admin/posts` - List view with pagination
- `GET /admin/posts/new` - Create form
- `POST /admin/posts` - Create action
- `GET /admin/posts/<id>` - Detail view
- `GET /admin/posts/<id>/edit` - Edit form
- `POST /admin/posts/<id>` - Update action
- `GET /admin/posts/<id>/delete` - Delete confirmation
- `POST /admin/posts/<id>/delete` - Delete action

### 2. Model Configuration

Add an `auto_ui_config` dictionary to your model to customize the interface:

```python
class Post(Model):
    title = Field()
    text = Field.text()
    date = Field.datetime()
    published = Field.bool()
    
    auto_ui_config = {
        'display_name': 'Blog Post',
        'display_name_plural': 'Blog Posts',
        'list_columns': ['id', 'title', 'date', 'published'],
        'search_fields': ['title', 'text'],
        'sort_default': '-date',  # '-' prefix for descending
        'page_size': 25,
        'permissions': {
            'list': lambda: True,  # Public
            'create': lambda: session.auth is not None,  # Logged in users
            'read': lambda: True,  # Public
            'update': lambda: session.auth is not None,  # Logged in users
            'delete': lambda: session.auth and 'admin' in session.auth.user.groups,  # Admins only
        },
        'field_config': {
            'title': {
                'display_name': 'Post Title',
                'help_text': 'Enter a descriptive title',
                'required': True
            },
            'text': {
                'display_name': 'Content',
                'widget': 'textarea'
            },
            'date': {
                'display_name': 'Published Date',
                'readonly': True
            }
        }
    }
```

## UI Component Mappings

Each ORM field type automatically maps to an appropriate UI component:

### Field Type Mappings

| ORM Type | HTML Component | Notes |
|----------|----------------|-------|
| `string` | `<input type="text">` | Standard text input |
| `text` | `<textarea>` | Multi-line text input |
| `bool` | `<input type="checkbox">` | Checkbox for boolean values |
| `int` | `<input type="number">` | Integer input |
| `float` | `<input type="number" step="0.01">` | Decimal number input |
| `datetime` | `<input type="datetime-local">` | Date and time picker |
| `date` | `<input type="date">` | Date picker |
| `time` | `<input type="time">` | Time picker |
| `password` | `<input type="password">` | Password input (hidden) |
| `email` | `<input type="email">` | Email input with validation |
| `url` | `<input type="url">` | URL input with validation |
| `belongs_to` | `<select>` | Dropdown with related records |

### Display Formatters

Field values are automatically formatted for display:

- **Datetime**: `Jan 15, 2025 02:30 PM`
- **Date**: `Jan 15, 2025`
- **Boolean**: `✓ Yes` / `✗ No`
- **Relationships**: `Related Model #ID` or related record name

## Customization

### Custom UI Mappings

Create a `runtime/ui_mapping_custom.json` file to override default mappings:

```json
{
  "mappings": {
    "string": {
      "component": "input",
      "attributes": {
        "type": "text",
        "class": "my-custom-input-class"
      }
    },
    "custom_field_type": {
      "component": "input",
      "attributes": {
        "type": "text",
        "class": "special-field"
      }
    }
  },
  "display_formatters": {
    "custom_field_type": "format_custom"
  }
}
```

### Custom Templates

Override default templates by creating files in `templates/auto_ui_custom/{model_name}/`:

```
templates/
└── auto_ui_custom/
    └── post/
        ├── list.html       # Custom list view
        ├── detail.html     # Custom detail view
        ├── form.html       # Custom create/edit form
        └── delete.html     # Custom delete confirmation
```

Your custom templates receive the same context variables as the default templates.

## Configuration Options

### Model-Level Configuration

| Option | Type | Description |
|--------|------|-------------|
| `display_name` | string | Singular name for the model (e.g., "Blog Post") |
| `display_name_plural` | string | Plural name for the model (e.g., "Blog Posts") |
| `list_columns` | list | Fields to show in list view (default: all fields) |
| `search_fields` | list | Fields to search in (enables search box) |
| `sort_default` | string | Default sort field (prefix with `-` for descending) |
| `page_size` | int | Records per page (default: 25) |
| `permissions` | dict | Permission functions for each operation |
| `field_config` | dict | Per-field customization options |

### Field-Level Configuration

| Option | Type | Description |
|--------|------|-------------|
| `display_name` | string | Label for the field |
| `help_text` | string | Help text shown below the field |
| `widget` | string | Override UI widget type |
| `readonly` | bool | Make field read-only |
| `hidden` | bool | Hide field from forms |
| `required` | bool | Mark field as required |

### Permission Functions

Permission functions should return `True` to allow or `False` to deny:

```python
'permissions': {
    'list': lambda: True,  # Allow all
    'create': lambda: session.auth is not None,  # Require login
    'read': lambda: True,
    'update': lambda: session.auth is not None,
    'delete': lambda: is_admin(),  # Custom function
}
```

## Features

### Pagination

Automatic pagination with configurable page size:
- Navigate between pages
- Shows current page and total pages
- Displays record count

### Search

Search across multiple fields:
- Case-insensitive
- OR logic across search fields
- Preserves search query in pagination

### Sorting

Click column headers to sort:
- Ascending on first click
- Descending on second click
- Visual sort direction indicator

### Responsive Design

Mobile-friendly interface:
- Responsive tables
- Touch-friendly buttons
- Optimized layouts for all screen sizes

### Accessibility

Following WCAG guidelines:
- Semantic HTML
- ARIA labels
- Keyboard navigation support
- Clear focus indicators

## Advanced Usage

### Programmatic Route Generation

For more control, use the `AutoUIGenerator` class directly:

```python
from auto_ui_generator import AutoUIGenerator

generator = AutoUIGenerator(
    app=app,
    model=Post,
    url_prefix='/admin/posts',
    config={
        'display_name': 'Blog Post',
        'page_size': 50
    }
)
generator.register_routes()
```

### Relationship Handling

Belongs-to relationships automatically render as select dropdowns:

```python
class Comment(Model):
    belongs_to('post', 'user')
    text = Field.text()
```

The auto UI will:
- Show dropdown for selecting the related post
- Display related record names in detail view
- Link to related record detail pages

## Files Created

The auto UI generation creates the following files:

- `runtime/ui_mapping.json` - Default field type to UI component mappings
- `runtime/auto_ui_generator.py` - Core generator class
- `runtime/templates/auto_ui/` - Default templates
  - `layout.html` - Base layout
  - `list.html` - List view with pagination
  - `detail.html` - Detail view
  - `form.html` - Create/edit form
  - `delete.html` - Delete confirmation

## Troubleshooting

### Templates Not Found

Ensure the `templates` directory structure is correct:
```
runtime/
└── templates/
    ├── auto_ui/
    │   ├── layout.html
    │   ├── list.html
    │   ├── detail.html
    │   ├── form.html
    │   └── delete.html
    └── layout.html  # Your base app layout
```

### Permissions Not Working

Check that permission functions are callable and return boolean values:
```python
# Good
'create': lambda: session.auth is not None

# Bad (not callable)
'create': True
```

### Custom Mappings Not Loading

Ensure `ui_mapping_custom.json` is:
1. In the `runtime/` directory
2. Valid JSON format
3. Contains correct structure (`mappings` and `display_formatters` keys)

### Fields Not Showing

Check if fields are hidden in model configuration:
```python
fields_rw = {
    'user': False,  # Hidden in forms
}
```

Or in auto_ui_config:
```python
'field_config': {
    'secret_field': {'hidden': True}
}
```

## Examples

See `runtime/app.py` for working examples with the `Post` and `Comment` models.

## Testing

Run the test suite:

```bash
cd runtime
python -m pytest test_auto_ui.py -v
```

## Future Enhancements

Potential features for future versions:
- Bulk operations (bulk delete, bulk update)
- Export functionality (CSV, JSON)
- Breadcrumb navigation
- Inline editing
- Advanced filtering UI
- File upload support
- Rich text editor integration

