# Auto UI Components

Separate, reusable components for each ORM field type organized by usage pattern.

## Component Organization

### Form Components (`form/`)
Used in create and edit forms for data input.

- `string.html` - Text input
- `text.html` - Textarea
- `bool.html` - Checkbox
- `int.html` - Number input (integer)
- `float.html` - Number input with decimal
- `datetime.html` - Datetime picker
- `date.html` - Date picker
- `time.html` - Time picker
- `password.html` - Password input
- `email.html` - Email input with validation
- `url.html` - URL input with validation
- `select.html` - Select dropdown (for belongs_to relationships)

### Display Components (`display/`)
Used in detail views to show field values.

- `string.html` - Plain text display
- `text.html` - Multi-line text display
- `bool.html` - Badge display (Yes/No)
- `datetime.html` - Formatted date/time with <time> tag
- `relationship.html` - Link to related record

### Table Components (`table/`)
Used in list views to display data in tables.

- `string.html` - Table cell with text
- `text.html` - Table cell with truncated text
- `bool.html` - Table cell with badge
- `datetime.html` - Table cell with formatted date
- `int.html` - Table cell with number (right-aligned)
- `relationship.html` - Table cell with link to related record

## Usage

Each component expects specific context variables:

### Form Components
```python
{
    'field_name': 'title',
    'label': 'Post Title',
    'value': 'Current value',
    'required': True,
    'readonly': False,
    'help_text': 'Enter a title',
    'error': 'Validation error message',
    'placeholder': 'Placeholder text'
}
```

### Display Components
```python
{
    'label': 'Post Title',
    'value': 'The actual value',
    'formatted_value': 'Formatted version'
}
```

### Table Components
```python
{
    'value': 'The actual value',
    'formatted_value': 'Formatted version',
    'related_url': '/admin/posts/123'  # For relationships
}
```

## Component Loading

Components are loaded by the `AutoUIGenerator` based on field type:

```python
# Map field type to component
field_type = generator._get_field_type('title')  # 'string'
component = f'auto_ui/components/form/{field_type}.html'
```

## Customization

Override components by creating custom versions:

```
templates/
└── auto_ui_custom/
    └── components/
        └── form/
            └── string.html  # Your custom string input
```

## Benefits of This Architecture

1. **Separation of Concerns**: Form, display, and table rendering are separate
2. **Reusability**: Each component is self-contained and reusable
3. **Maintainability**: Easy to update a specific component without affecting others
4. **Customization**: Easy to override individual components
5. **Consistency**: All fields of the same type render consistently
6. **Scalability**: Easy to add new field types by adding new component files

