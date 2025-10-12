# -*- coding: utf-8 -*-
"""
Auto UI Generator for Emmett Framework

Automatically generates CRUD interfaces from Emmett ORM models with:
- Automatic route generation (list, create, read, update, delete)
- Automatic form generation with appropriate widgets
- Pagination, search, filtering, and sorting
- Permission integration with Emmett Auth
- Responsive design with Tailwind CSS
- Customization via model configuration
"""

import json
import os
from datetime import datetime, date, time
from typing import Dict, Any, List, Optional, Callable
from functools import wraps

from emmett import request, response, redirect, url, abort, session
from emmett.orm import Model, Field
from emmett.forms import Form
from emmett.html import tag


class UIMappingLoader:
    """
    Loads and manages UI mappings from JSON configuration files.
    
    Supports default mappings with custom overrides for field types to UI components.
    """
    
    def __init__(self, default_path='ui_mapping.json', custom_path='ui_mapping_custom.json'):
        self.default_path = default_path
        self.custom_path = custom_path
        self.mappings = {}
        self.formatters = {}
    
    def load(self):
        """Load and merge UI mappings from JSON files."""
        self._load_defaults()
        self._load_custom()
        return self
    
    def _load_defaults(self):
        """Load default ui_mapping.json."""
        try:
            if os.path.exists(self.default_path):
                with open(self.default_path, 'r') as f:
                    data = json.load(f)
                    self.mappings = data.get('mappings', {})
                    self.formatters = data.get('display_formatters', {})
            else:
                # Fallback to hardcoded defaults
                self._use_hardcoded_defaults()
        except Exception as e:
            print(f"Warning: Failed to load ui_mapping.json: {e}. Using hardcoded defaults.")
            self._use_hardcoded_defaults()
    
    def _load_custom(self):
        """Load and merge ui_mapping_custom.json."""
        try:
            if os.path.exists(self.custom_path):
                with open(self.custom_path, 'r') as f:
                    custom_data = json.load(f)
                    # Merge custom mappings (override defaults)
                    custom_mappings = custom_data.get('mappings', {})
                    self.mappings.update(custom_mappings)
                    # Merge custom formatters
                    custom_formatters = custom_data.get('display_formatters', {})
                    self.formatters.update(custom_formatters)
        except Exception as e:
            # Custom mappings are optional, so we don't warn if file doesn't exist
            if os.path.exists(self.custom_path):
                print(f"Warning: Failed to load ui_mapping_custom.json: {e}")
    
    def _use_hardcoded_defaults(self):
        """Fallback hardcoded default mappings."""
        self.mappings = {
            'string': {
                'component': 'input',
                'attributes': {'type': 'text', 'class': 'form-input rounded-md border-gray-300'}
            },
            'text': {
                'component': 'textarea',
                'attributes': {'rows': 5, 'class': 'form-textarea rounded-md border-gray-300'}
            },
            'bool': {
                'component': 'input',
                'attributes': {'type': 'checkbox', 'class': 'form-checkbox rounded'}
            },
            'int': {
                'component': 'input',
                'attributes': {'type': 'number', 'class': 'form-input rounded-md border-gray-300'}
            },
            'datetime': {
                'component': 'input',
                'attributes': {'type': 'datetime-local', 'class': 'form-input rounded-md border-gray-300'}
            },
            'date': {
                'component': 'input',
                'attributes': {'type': 'date', 'class': 'form-input rounded-md border-gray-300'}
            },
            'belongs_to': {
                'component': 'select',
                'attributes': {'class': 'form-select rounded-md border-gray-300'},
                'populate': 'related_records'
            }
        }
        self.formatters = {
            'datetime': 'format_datetime',
            'date': 'format_date',
            'bool': 'format_boolean',
            'belongs_to': 'format_relationship'
        }
    
    def get_component_for_type(self, field_type):
        """Get UI component configuration for field type."""
        return self.mappings.get(field_type, self._default_mapping())
    
    def _default_mapping(self):
        """Default mapping for unknown field types."""
        return {
            'component': 'input',
            'attributes': {'type': 'text', 'class': 'form-input rounded-md border-gray-300'}
        }
    
    def get_formatter_for_type(self, field_type):
        """Get display formatter function name for field type."""
        return self.formatters.get(field_type)


class AutoUIGenerator:
    """
    Automatically generates CRUD interfaces for Emmett ORM models.
    
    Features:
    - Automatic route generation (list, create, read, update, delete)
    - Form generation with appropriate widgets based on field types
    - Pagination, search, filtering, and sorting
    - Permission integration with Emmett Auth
    - Responsive Tailwind CSS templates
    - Customization via model configuration
    
    Usage:
        generator = AutoUIGenerator(app, Post, '/admin/posts')
        generator.register_routes()
    
    Or use the decorator API:
        @app.auto_ui(Post, url_prefix='/admin/posts')
    """
    
    def __init__(self, app, model, url_prefix, config=None):
        self.app = app
        self.model = model
        self.url_prefix = url_prefix.rstrip('/')
        self.model_name = model.__name__.lower()
        self.config = self._merge_config(model, config)
        self.ui_mapping = UIMappingLoader(
            default_path=os.path.join(os.path.dirname(__file__), 'ui_mapping.json'),
            custom_path=os.path.join(os.path.dirname(__file__), 'ui_mapping_custom.json')
        ).load()
        # Get database instance from model's table
        self.db = model.db
    
    def _merge_config(self, model, config):
        """Merge model auto_ui_config with provided config."""
        default_config = {
            'display_name': model.__name__,
            'display_name_plural': model.__name__ + 's',
            'list_columns': None,  # None means all fields
            'search_fields': [],
            'sort_default': 'id',
            'page_size': 25,
            'permissions': {
                'list': lambda: True,
                'create': lambda: True,
                'read': lambda: True,
                'update': lambda: True,
                'delete': lambda: True,
            },
            'field_config': {}
        }
        
        # Merge with model's auto_ui_config if it exists
        if hasattr(model, 'auto_ui_config'):
            model_config = model.auto_ui_config
            default_config.update(model_config)
            # Merge nested dicts
            if 'permissions' in model_config:
                default_config['permissions'].update(model_config['permissions'])
            if 'field_config' in model_config:
                default_config['field_config'].update(model_config['field_config'])
        
        # Merge with provided config
        if config:
            default_config.update(config)
            if 'permissions' in config:
                default_config['permissions'].update(config['permissions'])
            if 'field_config' in config:
                default_config['field_config'].update(config['field_config'])
        
        return default_config
    
    def register_routes(self):
        """Register all CRUD routes with the app."""
        self._register_list_route()
        self._register_create_routes()
        self._register_detail_route()
        self._register_update_routes()
        self._register_delete_routes()
    
    def _check_permission(self, operation):
        """Check if current user has permission for operation."""
        perm_func = self.config['permissions'].get(operation)
        if perm_func and callable(perm_func):
            return perm_func()
        return True  # Default allow if no permission configured
    
    def _require_permission(self, operation):
        """Decorator to require permission for a route."""
        def decorator(f):
            @wraps(f)
            async def wrapper(*args, **kwargs):
                if not self._check_permission(operation):
                    if session.auth:
                        abort(403, f"You don't have permission to {operation} {self.config['display_name_plural']}")
                    else:
                        redirect(url('auth/login'))
                return await f(*args, **kwargs)
            return wrapper
        return decorator
    
    def _register_list_route(self):
        """Create and register list view route."""
        @self.app.route(f"{self.url_prefix}/", name=f"{self.model_name}_list")
        async def list_view():
            if not self._check_permission('list'):
                if session.auth:
                    abort(403)
                redirect(url('auth/login'))
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            per_page = self.config['page_size']
            
            # Build query
            query = self.db(self.model)
            
            # Search
            search_query = request.query_params.get('q', '').strip()
            if search_query and self.config['search_fields']:
                search_conditions = []
                for field_name in self.config['search_fields']:
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        search_conditions.append(field.contains(search_query))
                if search_conditions:
                    # Combine with OR
                    combined = search_conditions[0]
                    for condition in search_conditions[1:]:
                        combined = combined | condition
                    query = query.where(combined)
            
            # Sorting
            sort_field = request.query_params.get('sort', self.config['sort_default'])
            if sort_field.startswith('-'):
                # Descending
                sort_field_name = sort_field[1:]
                if hasattr(self.model, sort_field_name):
                    query = query.select(orderby=~getattr(self.model, sort_field_name))
            else:
                # Ascending
                if hasattr(self.model, sort_field):
                    query = query.select(orderby=getattr(self.model, sort_field))
            
            # Count total
            total_count = query.count()
            
            # Paginate
            offset = (page - 1) * per_page
            records = query.select(limitby=(offset, per_page))
            
            # Calculate pagination metadata
            total_pages = (total_count + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            
            # Determine which columns to show
            list_columns = self.config['list_columns']
            if not list_columns:
                # Show all fields except hidden ones
                list_columns = [f for f in self._get_model_fields() 
                               if not self._is_field_hidden(f)]
            
            return self.app.template(
                self._get_template('list.html'),
                records=records,
                model_name=self.config['display_name'],
                model_name_plural=self.config['display_name_plural'],
                columns=list_columns,
                page=page,
                total_pages=total_pages,
                total_count=total_count,
                per_page=per_page,
                has_prev=has_prev,
                has_next=has_next,
                search_query=search_query,
                sort_field=sort_field,
                url_prefix=self.url_prefix,
                model_name_lower=self.model_name,
                format_field=self._format_field_value,
                can_create=self._check_permission('create'),
                can_read=self._check_permission('read'),
                can_update=self._check_permission('update'),
                can_delete=self._check_permission('delete')
            )
        
        return list_view
    
    def _register_create_routes(self):
        """Create and register create form and action routes."""
        @self.app.route(f"{self.url_prefix}/new", name=f"{self.model_name}_new")
        async def create_form():
            if not self._check_permission('create'):
                if session.auth:
                    abort(403)
                redirect(url('auth/login'))
            
            form = Form(self.model)
            
            return self.app.template(
                self._get_template('form.html'),
                form=form,
                model_name=self.config['display_name'],
                action_url=url(f"{self.model_name}_create"),
                cancel_url=url(f"{self.model_name}_list"),
                is_edit=False
            )
        
        @self.app.route(f"{self.url_prefix}/", methods=['post'], name=f"{self.model_name}_create")
        async def create_action():
            if not self._check_permission('create'):
                if session.auth:
                    abort(403)
                redirect(url('auth/login'))
            
            form = Form(self.model)
            
            if form.accepted:
                record = form.vars
                redirect(url(f"{self.model_name}_detail", record.id))
            
            return self.app.template(
                self._get_template('form.html'),
                form=form,
                model_name=self.config['display_name'],
                action_url=url(f"{self.model_name}_create"),
                cancel_url=url(f"{self.model_name}_list"),
                is_edit=False
            )
        
        return create_form, create_action
    
    def _register_detail_route(self):
        """Create and register detail view route."""
        @self.app.route(f"{self.url_prefix}/<int:record_id>", name=f"{self.model_name}_detail")
        async def detail_view(record_id):
            if not self._check_permission('read'):
                if session.auth:
                    abort(403)
                redirect(url('auth/login'))
            
            record = self.db(self.model.id == record_id).select().first()
            if not record:
                abort(404, f"{self.config['display_name']} not found")
            
            # Get all readable fields
            fields = self._get_model_fields()
            field_data = []
            for field_name in fields:
                if not self._is_field_hidden(field_name):
                    field_config = self.config['field_config'].get(field_name, {})
                    display_name = field_config.get('display_name', field_name.replace('_', ' ').title())
                    value = getattr(record, field_name)
                    formatted_value = self._format_field_value(field_name, value)
                    field_data.append({
                        'name': field_name,
                        'display_name': display_name,
                        'value': value,
                        'formatted_value': formatted_value
                    })
            
            return self.app.template(
                self._get_template('detail.html'),
                record=record,
                model_name=self.config['display_name'],
                field_data=field_data,
                edit_url=url(f"{self.model_name}_edit", record_id),
                delete_url=url(f"{self.model_name}_delete_confirm", record_id),
                list_url=url(f"{self.model_name}_list"),
                can_update=self._check_permission('update'),
                can_delete=self._check_permission('delete')
            )
        
        return detail_view
    
    def _register_update_routes(self):
        """Create and register update form and action routes."""
        @self.app.route(f"{self.url_prefix}/<int:record_id>/edit", name=f"{self.model_name}_edit")
        async def update_form(record_id):
            if not self._check_permission('update'):
                if session.auth:
                    abort(403)
                redirect(url('auth/login'))
            
            record = self.db(self.model.id == record_id).select().first()
            if not record:
                abort(404, f"{self.config['display_name']} not found")
            
            form = Form(self.model, record=record)
            
            return self.app.template(
                self._get_template('form.html'),
                form=form,
                model_name=self.config['display_name'],
                action_url=url(f"{self.model_name}_update", record_id),
                cancel_url=url(f"{self.model_name}_detail", record_id),
                is_edit=True
            )
        
        @self.app.route(f"{self.url_prefix}/<int:record_id>", methods=['post'], name=f"{self.model_name}_update")
        async def update_action(record_id):
            if not self._check_permission('update'):
                if session.auth:
                    abort(403)
                redirect(url('auth/login'))
            
            record = self.db(self.model.id == record_id).select().first()
            if not record:
                abort(404, f"{self.config['display_name']} not found")
            
            form = Form(self.model, record=record)
            
            if form.accepted:
                redirect(url(f"{self.model_name}_detail", record_id))
            
            return self.app.template(
                self._get_template('form.html'),
                form=form,
                model_name=self.config['display_name'],
                action_url=url(f"{self.model_name}_update", record_id),
                cancel_url=url(f"{self.model_name}_detail", record_id),
                is_edit=True
            )
        
        return update_form, update_action
    
    def _register_delete_routes(self):
        """Create and register delete confirmation and action routes."""
        @self.app.route(f"{self.url_prefix}/<int:record_id>/delete", name=f"{self.model_name}_delete_confirm")
        async def delete_confirm(record_id):
            if not self._check_permission('delete'):
                if session.auth:
                    abort(403)
                redirect(url('auth/login'))
            
            record = self.db(self.model.id == record_id).select().first()
            if not record:
                abort(404, f"{self.config['display_name']} not found")
            
            return self.app.template(
                self._get_template('delete.html'),
                record=record,
                model_name=self.config['display_name'],
                delete_url=url(f"{self.model_name}_delete_action", record_id),
                cancel_url=url(f"{self.model_name}_detail", record_id)
            )
        
        @self.app.route(f"{self.url_prefix}/<int:record_id>/delete", methods=['post'], name=f"{self.model_name}_delete_action")
        async def delete_action(record_id):
            if not self._check_permission('delete'):
                if session.auth:
                    abort(403)
                redirect(url('auth/login'))
            
            record = self.db(self.model.id == record_id).select().first()
            if not record:
                abort(404, f"{self.config['display_name']} not found")
            
            record.delete_record()
            
            # Store success message in session if available
            if hasattr(session, 'flash'):
                session.flash = f"{self.config['display_name']} deleted successfully"
            
            redirect(url(f"{self.model_name}_list"))
        
        return delete_confirm, delete_action
    
    def _get_model_fields(self):
        """Extract field names from model."""
        fields = []
        for key, value in self.model.__dict__.items():
            if isinstance(value, Field):
                fields.append(key)
        return fields
    
    def _get_field_type(self, field_name):
        """Determine field type for UI mapping."""
        if not hasattr(self.model, field_name):
            return 'string'
        
        field = getattr(self.model, field_name)
        if not isinstance(field, Field):
            return 'string'
        
        # Check field type
        field_type = field._type
        
        # Map pyDAL types to UI mapping types
        # Note: Emmett/pyDAL already uses short names (bool, int, etc.)
        # but we include both long and short forms for compatibility
        type_mapping = {
            'string': 'string',
            'text': 'text',
            'blob': 'text',
            'bool': 'bool',
            'boolean': 'bool',
            'int': 'int',
            'integer': 'int',
            'bigint': 'int',
            'float': 'float',
            'double': 'float',
            'decimal': 'float',
            'date': 'date',
            'time': 'time',
            'datetime': 'datetime',
            'password': 'password',
            'upload': 'file',
            'reference': 'belongs_to',
        }
        
        return type_mapping.get(field_type, 'string')
    
    def _is_field_hidden(self, field_name):
        """Check if field should be hidden."""
        field_config = self.config['field_config'].get(field_name, {})
        if field_config.get('hidden', False):
            return True
        
        # Check model's fields_rw configuration
        if hasattr(self.model, 'fields_rw'):
            rw_config = self.model.fields_rw.get(field_name)
            if rw_config is False:
                return True
        
        return False
    
    def _format_field_value(self, field_name, value):
        """Format field value for display using formatters."""
        if value is None:
            return '-'
        
        field_type = self._get_field_type(field_name)
        formatter_name = self.ui_mapping.get_formatter_for_type(field_type)
        
        if formatter_name and hasattr(self, formatter_name):
            return getattr(self, formatter_name)(value, field_name)
        
        return str(value)
    
    def format_datetime(self, value, field_name=None):
        """Format datetime objects."""
        if isinstance(value, datetime):
            return value.strftime('%b %d, %Y %I:%M %p')
        return str(value)
    
    def format_date(self, value, field_name=None):
        """Format date objects."""
        if isinstance(value, date):
            return value.strftime('%b %d, %Y')
        return str(value)
    
    def format_time(self, value, field_name=None):
        """Format time objects."""
        if isinstance(value, time):
            return value.strftime('%I:%M %p')
        return str(value)
    
    def format_boolean(self, value, field_name=None):
        """Format boolean values."""
        if value is True:
            return '✓ Yes'
        elif value is False:
            return '✗ No'
        return str(value)
    
    def format_relationship(self, value, field_name=None):
        """Format relationship fields."""
        # For belongs_to relationships, pyDAL stores the ID
        # We need to fetch the related record to display it properly
        if isinstance(value, int) and field_name:
            # Try to find the related model
            for attr_name in dir(self.model):
                if attr_name.startswith('_'):
                    continue
                attr = getattr(self.model, attr_name)
                if hasattr(attr, 'reference') and attr.reference:
                    # This is a reference field
                    ref_model = attr.reference
                    try:
                        related_record = self.db(ref_model.id == value).select().first()
                        if related_record:
                            # Try common display fields
                            for display_field in ['name', 'title', 'email', 'username']:
                                if hasattr(related_record, display_field):
                                    return getattr(related_record, display_field)
                            return f"{ref_model.__name__} #{value}"
                    except:
                        pass
        
        return str(value)
    
    def _get_template(self, template_name):
        """Get template path with override support."""
        # Check for custom template first
        custom_template = f'auto_ui_custom/{self.model_name}/{template_name}'
        custom_path = os.path.join(self.app.template_folder, custom_template)
        if os.path.exists(custom_path):
            return custom_template
        
        # Use default template
        return f'auto_ui/{template_name}'


def auto_ui(app, model, url_prefix, config=None):
    """
    Decorator/function to enable auto UI generation for a model.
    
    Usage:
        auto_ui(app, Post, '/admin/posts')
    
    Args:
        app: Emmett application instance
        model: ORM Model class
        url_prefix: URL prefix for routes (e.g., '/admin/posts')
        config: Optional configuration dictionary
    
    Returns:
        AutoUIGenerator instance
    """
    generator = AutoUIGenerator(app, model, url_prefix, config)
    generator.register_routes()
    return generator

