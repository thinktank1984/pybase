# -*- coding: utf-8 -*-
"""
Base Model with Full-Stack Capabilities

A "fat model" base class that includes:
- HTTP request handling
- Response formatting
- Template rendering
- External API calls
- Email sending
- Session management
- Routing logic

All features have sensible defaults that can be overridden with decorators.
"""

from functools import wraps
from typing import Any, Dict, Optional, Callable
from emmett.orm import Model
from emmett import request, response, redirect, url, abort, current, session
from emmett.tools import Mailer
import json


class BaseModel(Model):
    """
    Full-stack base model with HTTP, templates, APIs, email, sessions, and routing.
    
    Usage:
        class Post(BaseModel):
            title = Field()
            content = Field.text()
            
            @http_handler('create')
            def handle_create(self, req):
                # Custom create logic
                pass
            
            @response_formatter('json')
            def format_json(self, data):
                # Custom JSON formatting
                return {'custom': data}
    """
    
    # Class-level registries for overrides
    _http_handlers: Dict[str, Callable] = {}
    _response_formatters: Dict[str, Callable] = {}
    _template_renderers: Dict[str, Callable] = {}
    _api_clients: Dict[str, Callable] = {}
    _email_handlers: Dict[str, Callable] = {}
    _session_handlers: Dict[str, Callable] = {}
    _route_handlers: Dict[str, Callable] = {}
    
    # ========================================================================
    # HTTP REQUEST HANDLING (Base Implementation + Override Decorator)
    # ========================================================================
    
    def handle_request(self, operation: str = 'read', req: Any = None):
        """
        Base HTTP request handler.
        
        Args:
            operation: Operation type ('create', 'read', 'update', 'delete')
            req: Request object (defaults to current request)
            
        Returns:
            Response data
        """
        if req is None:
            req = request
        
        # Check for override
        handler_key = f"{self.__class__.__name__}:{operation}"
        if handler_key in self._http_handlers:
            return self._http_handlers[handler_key](self, req)
        
        # Default implementation
        if operation == 'create':
            return self._default_create_handler(req)
        elif operation == 'read':
            return self._default_read_handler(req)
        elif operation == 'update':
            return self._default_update_handler(req)
        elif operation == 'delete':
            return self._default_delete_handler(req)
        else:
            abort(400, f"Unknown operation: {operation}")
    
    def _default_create_handler(self, req):
        """Default handler for create operations."""
        data = req.body_params
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        return {'id': self.id, 'message': 'Created successfully'}
    
    def _default_read_handler(self, req):
        """Default handler for read operations."""
        return self.to_dict()
    
    def _default_update_handler(self, req):
        """Default handler for update operations."""
        data = req.body_params
        self.update_record(**data)
        return {'id': self.id, 'message': 'Updated successfully'}
    
    def _default_delete_handler(self, req):
        """Default handler for delete operations."""
        self.delete_record()
        return {'message': 'Deleted successfully'}
    
    # ========================================================================
    # RESPONSE FORMATTING (Base Implementation + Override Decorator)
    # ========================================================================
    
    def format_response(self, data: Any, format_type: str = 'json') -> Any:
        """
        Base response formatter.
        
        Args:
            data: Data to format
            format_type: Format type ('json', 'xml', 'html')
            
        Returns:
            Formatted response
        """
        # Check for override
        formatter_key = f"{self.__class__.__name__}:{format_type}"
        if formatter_key in self._response_formatters:
            return self._response_formatters[formatter_key](self, data)
        
        # Default implementation
        if format_type == 'json':
            return self._default_json_formatter(data)
        elif format_type == 'xml':
            return self._default_xml_formatter(data)
        elif format_type == 'html':
            return self._default_html_formatter(data)
        else:
            return data
    
    def _default_json_formatter(self, data):
        """Default JSON formatter."""
        if isinstance(data, dict):
            return data
        return self.to_dict()
    
    def _default_xml_formatter(self, data):
        """Default XML formatter."""
        # Simple XML conversion
        xml = ['<?xml version="1.0"?>']
        xml.append(f'<{self.__class__.__name__.lower()}>')
        for key, value in self.to_dict().items():
            xml.append(f'  <{key}>{value}</{key}>')
        xml.append(f'</{self.__class__.__name__.lower()}>')
        return '\n'.join(xml)
    
    def _default_html_formatter(self, data):
        """Default HTML formatter."""
        return f"<div class='model'>{self.to_dict()}</div>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for key in dir(self):
            if key.startswith('_') or callable(getattr(self, key)):
                continue
            try:
                value = getattr(self, key)
                if not callable(value):
                    result[key] = value
            except:
                pass
        return result
    
    # ========================================================================
    # TEMPLATE RENDERING (Base Implementation + Override Decorator)
    # ========================================================================
    
    def render_template(self, template_name: Optional[str] = None, **context):
        """
        Base template renderer.
        
        Args:
            template_name: Template name (defaults to model_name.html)
            **context: Template context
            
        Returns:
            Rendered template
        """
        if template_name is None:
            template_name = f"{self.__class__.__name__.lower()}.html"
        
        # Check for override
        renderer_key = f"{self.__class__.__name__}:{template_name}"
        if renderer_key in self._template_renderers:
            return self._template_renderers[renderer_key](self, **context)
        
        # Default implementation
        return self._default_template_renderer(template_name, **context)
    
    def _default_template_renderer(self, template_name, **context):
        """Default template renderer."""
        from emmett import current
        context['record'] = self
        context['model_name'] = self.__class__.__name__
        try:
            return current.app.template(template_name, **context)
        except:
            # Fallback if no app context
            return f"<div>Model: {self.__class__.__name__}, Template: {template_name}</div>"
    
    # ========================================================================
    # EXTERNAL API CALLS (Base Implementation + Override Decorator)
    # ========================================================================
    
    def call_api(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None):
        """
        Base external API caller.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            
        Returns:
            API response
        """
        # Check for override
        api_key = f"{self.__class__.__name__}:{endpoint}"
        if api_key in self._api_clients:
            return self._api_clients[api_key](self, method, data)
        
        # Default implementation
        return self._default_api_caller(endpoint, method, data)
    
    def _default_api_caller(self, endpoint, method, data):
        """Default API caller."""
        try:
            import requests
            
            if method == 'GET':
                resp = requests.get(endpoint, params=data)
            elif method == 'POST':
                resp = requests.post(endpoint, json=data)
            elif method == 'PUT':
                resp = requests.put(endpoint, json=data)
            elif method == 'DELETE':
                resp = requests.delete(endpoint)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return resp.json() if resp.headers.get('content-type') == 'application/json' else resp.text
        except ImportError:
            return {'error': 'requests library not installed'}
        except Exception as e:
            return {'error': str(e)}
    
    # ========================================================================
    # EMAIL SENDING (Base Implementation + Override Decorator)
    # ========================================================================
    
    def send_email(self, to: str, subject: str, body: str, email_type: str = 'default'):
        """
        Base email sender.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            email_type: Type of email (for overrides)
            
        Returns:
            Success status
        """
        # Check for override
        email_key = f"{self.__class__.__name__}:{email_type}"
        if email_key in self._email_handlers:
            return self._email_handlers[email_key](self, to, subject, body)
        
        # Default implementation
        return self._default_email_sender(to, subject, body)
    
    def _default_email_sender(self, to, subject, body):
        """Default email sender."""
        try:
            from emmett import current
            mailer = current.app.ext.Mailer
            
            message = mailer.send(
                to=to,
                subject=subject,
                body=body
            )
            return {'success': True, 'message': 'Email sent'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # SESSION MANAGEMENT (Base Implementation + Override Decorator)
    # ========================================================================
    
    def get_session_data(self, key: str, default: Any = None):
        """
        Get data from session.
        
        Args:
            key: Session key
            default: Default value
            
        Returns:
            Session value
        """
        # Check for override
        session_key = f"{self.__class__.__name__}:get:{key}"
        if session_key in self._session_handlers:
            return self._session_handlers[session_key](self, key, default)
        
        # Default implementation
        return self._default_get_session(key, default)
    
    def set_session_data(self, key: str, value: Any):
        """
        Set data in session.
        
        Args:
            key: Session key
            value: Value to set
        """
        # Check for override
        session_key = f"{self.__class__.__name__}:set:{key}"
        if session_key in self._session_handlers:
            return self._session_handlers[session_key](self, key, value)
        
        # Default implementation
        return self._default_set_session(key, value)
    
    def _default_get_session(self, key, default):
        """Default session getter."""
        try:
            return session.get(key, default)
        except:
            return default
    
    def _default_set_session(self, key, value):
        """Default session setter."""
        try:
            session[key] = value
            return True
        except:
            return False
    
    # ========================================================================
    # ROUTING LOGIC (Base Implementation + Override Decorator)
    # ========================================================================
    
    def generate_route(self, action: str = 'show', **params):
        """
        Generate route URL for this model.
        
        Args:
            action: Action name ('show', 'edit', 'delete', etc.)
            **params: Additional route parameters
            
        Returns:
            Generated URL
        """
        # Check for override
        route_key = f"{self.__class__.__name__}:{action}"
        if route_key in self._route_handlers:
            return self._route_handlers[route_key](self, **params)
        
        # Default implementation
        return self._default_route_generator(action, **params)
    
    def _default_route_generator(self, action, **params):
        """Default route generator."""
        model_name = self.__class__.__name__.lower()
        
        if action == 'show':
            return url(f'{model_name}_detail', self.id)
        elif action == 'edit':
            return url(f'{model_name}_edit', self.id)
        elif action == 'delete':
            return url(f'{model_name}_delete', self.id)
        elif action == 'list':
            return url(f'{model_name}_list')
        else:
            return url(f'{model_name}_{action}', self.id, **params)
    
    def redirect_to(self, action: str = 'show', **params):
        """
        Redirect to a route for this model.
        
        Args:
            action: Action name
            **params: Additional parameters
        """
        route_url = self.generate_route(action, **params)
        return redirect(route_url)


# ============================================================================
# DECORATORS FOR OVERRIDING DEFAULTS
# ============================================================================

def http_handler(operation: str):
    """
    Decorator to override default HTTP handler.
    
    Usage:
        class Post(BaseModel):
            @http_handler('create')
            def custom_create(self, req):
                # Custom logic
                pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, req):
            return func(self, req)
        
        # Register override
        def register_on_class(cls):
            handler_key = f"{cls.__name__}:{operation}"
            cls._http_handlers[handler_key] = func
            return wrapper
        
        # Store registration function on the wrapper
        wrapper._register_handler = register_on_class
        return wrapper
    return decorator


def response_formatter(format_type: str):
    """
    Decorator to override default response formatter.
    
    Usage:
        class Post(BaseModel):
            @response_formatter('json')
            def custom_json(self, data):
                return {'custom': data}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, data):
            return func(self, data)
        
        def register_on_class(cls):
            formatter_key = f"{cls.__name__}:{format_type}"
            cls._response_formatters[formatter_key] = func
            return wrapper
        
        wrapper._register_formatter = register_on_class
        return wrapper
    return decorator


def template_renderer(template_name: str):
    """
    Decorator to override default template renderer.
    
    Usage:
        class Post(BaseModel):
            @template_renderer('post.html')
            def custom_render(self, **context):
                # Custom rendering
                pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, **context):
            return func(self, **context)
        
        def register_on_class(cls):
            renderer_key = f"{cls.__name__}:{template_name}"
            cls._template_renderers[renderer_key] = func
            return wrapper
        
        wrapper._register_renderer = register_on_class
        return wrapper
    return decorator


def api_client(endpoint: str):
    """
    Decorator to override default API client.
    
    Usage:
        class Post(BaseModel):
            @api_client('/external/posts')
            def custom_api_call(self, method, data):
                # Custom API logic
                pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, method, data):
            return func(self, method, data)
        
        def register_on_class(cls):
            api_key = f"{cls.__name__}:{endpoint}"
            cls._api_clients[api_key] = func
            return wrapper
        
        wrapper._register_api = register_on_class
        return wrapper
    return decorator


def email_handler(email_type: str):
    """
    Decorator to override default email handler.
    
    Usage:
        class Post(BaseModel):
            @email_handler('welcome')
            def custom_welcome_email(self, to, subject, body):
                # Custom email logic
                pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, to, subject, body):
            return func(self, to, subject, body)
        
        def register_on_class(cls):
            email_key = f"{cls.__name__}:{email_type}"
            cls._email_handlers[email_key] = func
            return wrapper
        
        wrapper._register_email = register_on_class
        return wrapper
    return decorator


def session_handler(operation: str, key: str):
    """
    Decorator to override default session handler.
    
    Usage:
        class Post(BaseModel):
            @session_handler('get', 'user_posts')
            def custom_get_session(self, key, default):
                # Custom session logic
                pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        
        def register_on_class(cls):
            session_key = f"{cls.__name__}:{operation}:{key}"
            cls._session_handlers[session_key] = func
            return wrapper
        
        wrapper._register_session = register_on_class
        return wrapper
    return decorator


def route_handler(action: str):
    """
    Decorator to override default route generator.
    
    Usage:
        class Post(BaseModel):
            @route_handler('show')
            def custom_show_route(self, **params):
                return f"/custom/posts/{self.id}"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, **params):
            return func(self, **params)
        
        def register_on_class(cls):
            route_key = f"{cls.__name__}:{action}"
            cls._route_handlers[route_key] = func
            return wrapper
        
        wrapper._register_route = register_on_class
        return wrapper
    return decorator

