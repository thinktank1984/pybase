# -*- coding: utf-8 -*-
"""
Automatic Route Generation for BaseModel

Discovers models with `auto_routes` class attribute and automatically
generates CRUD routes without requiring manual setup() functions.

This module integrates with the existing auto_ui system to provide:
- Zero-configuration route generation
- Declarative configuration via auto_routes class attribute
- Full backwards compatibility with manual setup()
- REST API generation
- Permission integration

Usage:
    # In model:
    class Role(BaseModel):
        name = Field.string()
        auto_routes = True  # Routes generated automatically
    
    # In app.py:
    from auto_routes import discover_and_register_auto_routes
    discover_and_register_auto_routes(app, db)
"""

from typing import List, Dict, Any, Optional, Callable
import inspect
import logging
from emmett import App
from emmett.orm import Database, Model
from runtime.auto_ui_generator import auto_ui

logger = logging.getLogger(__name__)


def discover_auto_routes_models(db: Database) -> List[type]:
    """
    Discover all models with auto_routes enabled.
    
    Searches through all registered models in the database and
    finds those with the `auto_routes` class attribute set.
    
    Args:
        db: Emmett Database instance
    
    Returns:
        List of model classes with auto_routes enabled
    """
    auto_routes_models = []
    
    # Get all models registered with the database
    if not hasattr(db, 'Model'):
        logger.warning("Database has no models registered")
        return []
    
    # Iterate through all models
    for table_name, table in db.tables.items():
        # Skip internal tables
        if table_name.startswith('_'):
            continue
        
        # Get the model class associated with this table
        model_class = _find_model_for_table(db, table_name)
        if model_class is None:
            continue
        
        # Check if model has auto_routes attribute
        if hasattr(model_class, 'auto_routes'):
            auto_routes_config = getattr(model_class, 'auto_routes')
            
            # Skip if explicitly disabled
            if auto_routes_config is False:
                continue
            
            # Skip if model has manual setup() in module
            if _has_manual_setup(model_class):
                logger.info(f"Skipping {model_class.__name__} - has manual setup()")
                continue
            
            auto_routes_models.append(model_class)
            logger.info(f"Discovered auto_routes model: {model_class.__name__}")
    
    return auto_routes_models


def _find_model_for_table(db: Database, table_name: str) -> Optional[type]:
    """
    Find the model class associated with a database table.
    
    Args:
        db: Database instance
        table_name: Name of the table
    
    Returns:
        Model class or None if not found
    """
    # Try to find model in db._models (if it exists)
    if hasattr(db, '_models'):
        for model in db._models.values():
            if hasattr(model, 'tablename') and model.tablename == table_name:
                return model
    
    # Fallback: search through Model subclasses
    from runtime.base_model import BaseModel
    for subclass in BaseModel.__subclasses__():
        if hasattr(subclass, 'tablename') and subclass.tablename == table_name:
            return subclass
        # Also check if tablename defaults to class name
        if not hasattr(subclass, 'tablename'):
            if subclass.__name__.lower() == table_name:
                return subclass
    
    return None


def _has_manual_setup(model_class: type) -> bool:
    """
    Check if model has a manual setup() function defined.
    
    Args:
        model_class: Model class to check
    
    Returns:
        True if manual setup exists, False otherwise
    """
    # Check if model's module defines a setup function
    model_module = inspect.getmodule(model_class)
    if model_module and hasattr(model_module, 'setup'):
        return True
    
    return False


def parse_auto_routes_config(model_class: type) -> Dict[str, Any]:
    """
    Parse and normalize auto_routes configuration from model.
    
    Args:
        model_class: Model class with auto_routes attribute
    
    Returns:
        Normalized configuration dictionary
    """
    auto_routes = getattr(model_class, 'auto_routes', None)
    
    # Default configuration
    default_config = {
        'enabled': True,
        'url_prefix': f'/{model_class.tablename}',
        'rest_api': True,
        'rest_prefix': f'/api/{model_class.tablename}',
        'enabled_actions': ['list', 'detail', 'create', 'update', 'delete'],
        'permissions': {},
        'auto_ui_config': {},
        'custom_handlers': {}
    }
    
    # If auto_routes is just True, use all defaults
    if auto_routes is True:
        return default_config
    
    # If auto_routes is a dictionary, merge with defaults
    if isinstance(auto_routes, dict):
        config = default_config.copy()
        
        # Update top-level keys
        for key in ['url_prefix', 'rest_api', 'rest_prefix', 'enabled_actions']:
            if key in auto_routes:
                config[key] = auto_routes[key]
        
        # Merge nested dicts
        if 'permissions' in auto_routes:
            config['permissions'].update(auto_routes['permissions'])
        if 'auto_ui_config' in auto_routes:
            config['auto_ui_config'].update(auto_routes['auto_ui_config'])
        if 'custom_handlers' in auto_routes:
            config['custom_handlers'].update(auto_routes['custom_handlers'])
        
        return config
    
    # If auto_routes is neither True nor dict, use defaults
    return default_config


def validate_auto_routes_config(model_class: type, config: Dict[str, Any]) -> None:
    """
    Validate auto_routes configuration and warn about issues.
    
    Args:
        model_class: Model class
        config: Configuration dictionary
    """
    valid_actions = ['list', 'detail', 'create', 'update', 'delete']
    
    # Check enabled_actions
    enabled_actions = config.get('enabled_actions', [])
    for action in enabled_actions:
        if action not in valid_actions:
            logger.warning(
                f"{model_class.__name__}: Invalid action '{action}' in enabled_actions. "
                f"Valid actions: {valid_actions}"
            )
    
    # Check permissions
    permissions = config.get('permissions', {})
    for action, permission_func in permissions.items():
        if action not in valid_actions:
            logger.warning(
                f"{model_class.__name__}: Permission defined for invalid action '{action}'"
            )
        if not callable(permission_func):
            logger.warning(
                f"{model_class.__name__}: Permission for '{action}' is not callable"
            )


def generate_routes_for_model(app: App, model_class: type, config: Dict[str, Any]) -> None:
    """
    Generate and register routes for a single model.
    
    Uses the existing auto_ui system to generate CRUD routes, then
    optionally adds REST API endpoints.
    
    Args:
        app: Emmett application instance
        model_class: Model class to generate routes for
        config: Auto routes configuration
    """
    url_prefix = config['url_prefix']
    enabled_actions = config['enabled_actions']
    auto_ui_config = config['auto_ui_config']
    
    # Build auto_ui config with permissions and enabled actions
    ui_config = {
        'permissions': config['permissions'],
        **auto_ui_config
    }
    
    # If enabled_actions is limited, we need to customize the generator
    # For now, we'll use auto_ui which generates all routes
    # TODO: Extend auto_ui to support enabled_actions filtering
    
    try:
        # Generate CRUD routes via auto_ui
        logger.info(f"Generating routes for {model_class.__name__} at {url_prefix}")
        generator = auto_ui(app, model_class, url_prefix, ui_config)
        
        # Generate REST API if enabled
        if config['rest_api']:
            rest_prefix = config['rest_prefix']
            logger.info(f"Generating REST API for {model_class.__name__} at {rest_prefix}")
            _generate_rest_api(app, model_class, rest_prefix, enabled_actions)
        
        logger.info(f"Successfully registered routes for {model_class.__name__}")
        
    except Exception as e:
        logger.error(f"Failed to generate routes for {model_class.__name__}: {e}")
        raise


def _generate_rest_api(app: App, model_class: type, rest_prefix: str, enabled_actions: List[str]) -> None:
    """
    Generate REST API endpoints for a model.
    
    Args:
        app: Emmett application instance
        model_class: Model class
        rest_prefix: URL prefix for REST endpoints (e.g., '/api/roles')
        enabled_actions: List of enabled actions
    """
    # Get database instance from model
    db = model_class.db
    
    # LIST endpoint: GET /api/model
    if 'list' in enabled_actions:
        @app.route(f"{rest_prefix}", methods=['get'], name=f'{model_class.tablename}_api_list')
        async def api_list():
            with db.connection():
                records = model_class.all().select()
                return {
                    'status': 'success',
                    'data': [record.to_dict() for record in records]
                }
    
    # DETAIL endpoint: GET /api/model/:id
    if 'detail' in enabled_actions:
        @app.route(f"{rest_prefix}/<int:id>", methods=['get'], name=f'{model_class.tablename}_api_detail')
        async def api_detail(id):
            with db.connection():
                record = model_class.get(id)
                if not record:
                    return {'status': 'error', 'message': 'Not found'}, 404
                return {
                    'status': 'success',
                    'data': record.to_dict()
                }
    
    # CREATE endpoint: POST /api/model
    if 'create' in enabled_actions:
        @app.route(f"{rest_prefix}", methods=['post'], name=f'{model_class.tablename}_api_create')
        async def api_create():
            from emmett import request
            with db.connection():
                data = request.body_params
                record = model_class.create(**data)
                db.commit()
                return {
                    'status': 'success',
                    'data': record.to_dict()
                }, 201
    
    # UPDATE endpoint: PUT /api/model/:id
    if 'update' in enabled_actions:
        @app.route(f"{rest_prefix}/<int:id>", methods=['put'], name=f'{model_class.tablename}_api_update')
        async def api_update(id):
            from emmett import request
            with db.connection():
                record = model_class.get(id)
                if not record:
                    return {'status': 'error', 'message': 'Not found'}, 404
                
                data = request.body_params
                record.update_record(**data)
                db.commit()
                return {
                    'status': 'success',
                    'data': record.to_dict()
                }
    
    # DELETE endpoint: DELETE /api/model/:id
    if 'delete' in enabled_actions:
        @app.route(f"{rest_prefix}/<int:id>", methods=['delete'], name=f'{model_class.tablename}_api_delete')
        async def api_delete(id):
            with db.connection():
                record = model_class.get(id)
                if not record:
                    return {'status': 'error', 'message': 'Not found'}, 404
                
                record.delete_record()
                db.commit()
                return {
                    'status': 'success',
                    'message': 'Deleted successfully'
                }


def discover_and_register_auto_routes(app: App, db: Database) -> None:
    """
    Main entry point: Discover all auto_routes models and register their routes.
    
    Call this in app.py after db.define_models():
    
        from auto_routes import discover_and_register_auto_routes
        discover_and_register_auto_routes(app, db)
    
    Args:
        app: Emmett application instance
        db: Database instance
    """
    logger.info("Starting automatic route discovery...")
    
    # Discover models with auto_routes
    models = discover_auto_routes_models(db)
    
    if not models:
        logger.info("No models with auto_routes found")
        return
    
    logger.info(f"Found {len(models)} models with auto_routes enabled")
    
    # Register routes for each model
    for model_class in models:
        try:
            # Parse configuration
            config = parse_auto_routes_config(model_class)
            
            # Validate configuration
            validate_auto_routes_config(model_class, config)
            
            # Generate and register routes
            generate_routes_for_model(app, model_class, config)
            
        except Exception as e:
            logger.error(f"Failed to register routes for {model_class.__name__}: {e}")
            # Continue with other models
            continue
    
    logger.info("Automatic route registration complete")


__all__ = [
    'discover_auto_routes_models',
    'discover_and_register_auto_routes',
    'parse_auto_routes_config',
    'validate_auto_routes_config',
    'generate_routes_for_model'
]

