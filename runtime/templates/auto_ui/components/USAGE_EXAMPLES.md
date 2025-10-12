# Component Usage Examples

## Form Components

### String Input
```html
{{include 'auto_ui/components/form/string.html' 
  field_name='title' 
  label='Post Title' 
  value=record.title
  required=True
  placeholder='Enter title here'
  help_text='A descriptive title for your post'
  error=form.errors.title}}
```

### Text Area
```html
{{include 'auto_ui/components/form/text.html' 
  field_name='content' 
  label='Content' 
  value=record.content
  rows=10
  required=True
  help_text='Write your post content'}}
```

### Checkbox
```html
{{include 'auto_ui/components/form/bool.html' 
  field_name='published' 
  label='Published' 
  value=record.published
  help_text='Check to make this post public'}}
```

### Select Dropdown (Relationship)
```html
{{include 'auto_ui/components/form/select.html' 
  field_name='category' 
  label='Category' 
  value=record.category
  required=True
  options=[
    {'value': 1, 'label': 'Technology'},
    {'value': 2, 'label': 'Science'}
  ]}}
```

## Display Components

### String Display
```html
{{include 'auto_ui/components/display/string.html' 
  label='Title' 
  value=record.title}}
```

### Boolean Display with Badge
```html
{{include 'auto_ui/components/display/bool.html' 
  label='Published' 
  value=record.published}}
```

### DateTime Display
```html
{{include 'auto_ui/components/display/datetime.html' 
  label='Created At' 
  value=record.created_at
  formatted_value='Jan 15, 2025 2:30 PM'}}
```

### Relationship Display with Link
```html
{{include 'auto_ui/components/display/relationship.html' 
  label='Author' 
  value=record.user
  formatted_value='John Doe'
  related_url='/admin/users/123'}}
```

## Table Components

### Complete Table Row
```html
<tr>
  {{include 'auto_ui/components/table/int.html' value=record.id}}
  {{include 'auto_ui/components/table/string.html' value=record.title}}
  {{include 'auto_ui/components/table/bool.html' value=record.published}}
  {{include 'auto_ui/components/table/datetime.html' 
    value=record.created_at
    formatted_value='Jan 15, 2025'}}
  <td class="actions">
    <a href="/edit/{{=record.id}}">Edit</a>
  </td>
</tr>
```

## Complete Form Example

```html
<form method="post" action="/posts/create">
  {{include 'auto_ui/components/form/string.html' 
    field_name='title' 
    label='Title' 
    required=True}}
  
  {{include 'auto_ui/components/form/text.html' 
    field_name='content' 
    label='Content' 
    rows=10
    required=True}}
  
  {{include 'auto_ui/components/form/bool.html' 
    field_name='published' 
    label='Publish immediately'}}
  
  {{include 'auto_ui/components/form/select.html' 
    field_name='category' 
    label='Category' 
    options=categories
    required=True}}
  
  <button type="submit" class="btn btn-primary">Create Post</button>
</form>
```

## Complete Detail View Example

```html
<div class="detail-view">
  <dl class="space-y-4">
    {{include 'auto_ui/components/display/string.html' 
      label='Title' 
      value=post.title}}
    
    {{include 'auto_ui/components/display/text.html' 
      label='Content' 
      value=post.content}}
    
    {{include 'auto_ui/components/display/bool.html' 
      label='Published' 
      value=post.published}}
    
    {{include 'auto_ui/components/display/relationship.html' 
      label='Author' 
      formatted_value=post.user.name
      related_url=url('user_detail', post.user.id)}}
    
    {{include 'auto_ui/components/display/datetime.html' 
      label='Created' 
      value=post.created_at
      formatted_value=format_datetime(post.created_at)}}
  </dl>
</div>
```

## Customization Example

Override a component by creating your own version:

```
templates/
└── auto_ui_custom/
    └── components/
        └── form/
            └── string.html  ← Your custom version
```

Your custom component:
```html
{{# Custom string input with icon #}}
<div class="form-field">
  <label for="{{=field_name}}" class="label-with-icon">
    <svg class="icon">...</svg>
    {{=label}}
  </label>
  <input type="text" 
         id="{{=field_name}}"
         name="{{=field_name}}"
         value="{{=value or ''}}"
         class="custom-input-class">
</div>
```
