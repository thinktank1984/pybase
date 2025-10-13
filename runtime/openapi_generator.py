# -*- coding: utf-8 -*-
"""
OpenAPI 3.0 Specification Generator for Emmett REST APIs

This module automatically generates OpenAPI 3.0 specifications from
Emmett REST modules, providing interactive Swagger UI documentation.
"""

from typing import Dict, Any, List, Optional
from emmett.orm import Model
from emmett import App


class OpenAPIGenerator:
    """Generates OpenAPI 3.0 specification from Emmett REST modules"""
    
    def __init__(self, app: App, title: str = "API Documentation", 
                 version: str = "1.0.0", description: str = ""):
        self.app = app
        self.title = title
        self.version = version
        self.description = description
        self.rest_modules = []
        
    def register_rest_module(self, module_name: str, model: Model, 
                            url_prefix: str, disabled_methods: Optional[List[str]] = None):
        """Register a REST module for documentation generation"""
        self.rest_modules.append({
            'name': module_name,
            'model': model,
            'url_prefix': url_prefix,
            'disabled_methods': disabled_methods or []
        })
        
    def _get_field_type(self, field) -> Dict[str, Any]:
        """Convert Emmett field type to OpenAPI type"""
        field_type = field.type
        
        type_mapping = {
            'string': {'type': 'string'},
            'text': {'type': 'string'},
            'integer': {'type': 'integer'},
            'bigint': {'type': 'integer', 'format': 'int64'},
            'float': {'type': 'number', 'format': 'float'},
            'double': {'type': 'number', 'format': 'double'},
            'decimal': {'type': 'number'},
            'boolean': {'type': 'boolean'},
            'date': {'type': 'string', 'format': 'date'},
            'datetime': {'type': 'string', 'format': 'date-time'},
            'time': {'type': 'string', 'format': 'time'},
            'json': {'type': 'object'},
            'list:string': {'type': 'array', 'items': {'type': 'string'}},
            'list:integer': {'type': 'array', 'items': {'type': 'integer'}},
        }
        
        return type_mapping.get(field_type, {'type': 'string'})
    
    def _generate_model_schema(self, model: Model, for_input: bool = False) -> Dict[str, Any]:
        """Generate OpenAPI schema for a model"""
        properties = {}
        required = []
        
        # Get model fields from the table
        if not hasattr(model, 'table') or model.table is None:
            # Return a basic schema if table not available
            return {'type': 'object', 'properties': {}}
        
        # Get model fields
        for field_name in model.table.fields:  # type: ignore[union-attr]
            if field_name == 'id':
                continue  # Skip ID for input schemas
                
            field = getattr(model, field_name)
            
            # Skip foreign key fields (they appear as <model>_id in forms)
            if hasattr(field, 'reference'):
                # Add the reference field (e.g., user -> user_id)
                ref_field_name = f"{field_name}"
                properties[ref_field_name] = {'type': 'integer', 'description': f'ID of related {field_name}'}
                continue
            
            field_schema = self._get_field_type(field)
            
            # Add description if available
            if hasattr(field, 'comment') and field.comment:
                field_schema['description'] = field.comment
            
            properties[field_name] = field_schema
            
            # Check if field is required (from validation)
            if hasattr(model, 'validation') and field_name in model.validation:  # type: ignore[attr-defined]
                validation = model.validation[field_name]  # type: ignore[attr-defined]
                if isinstance(validation, dict) and validation.get('presence'):
                    required.append(field_name)
        
        # Always include id in output schemas
        if not for_input:
            properties['id'] = {'type': 'integer', 'description': 'Unique identifier'}
        
        schema = {
            'type': 'object',
            'properties': properties
        }
        
        if required:
            schema['required'] = required
            
        return schema
    
    def _generate_paths(self) -> Dict[str, Any]:
        """Generate OpenAPI paths for all REST modules"""
        paths = {}
        
        for module in self.rest_modules:
            model = module['model']
            url_prefix = module['url_prefix']
            disabled = module['disabled_methods']
            model_name = model.__name__
            
            # List endpoint: GET /api/posts
            list_path = f"/{url_prefix}"
            if 'list' not in disabled:
                paths[list_path] = {
                    'get': {
                        'tags': [model_name],
                        'summary': f'List all {model_name.lower()}s',
                        'description': f'Retrieve a list of all {model_name.lower()} records',
                        'responses': {
                            '200': {
                                'description': 'Successful response',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'data': {
                                                    'type': 'array',
                                                    'items': {'$ref': f'#/components/schemas/{model_name}'}
                                                },
                                                'meta': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'object': {'type': 'string'},
                                                        'has_more': {'type': 'boolean'},
                                                        'total_objects': {'type': 'integer'}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            
            # Create endpoint: POST /api/posts
            if 'create' not in disabled:
                if list_path not in paths:
                    paths[list_path] = {}
                paths[list_path]['post'] = {
                    'tags': [model_name],
                    'summary': f'Create a new {model_name.lower()}',
                    'description': f'Create a new {model_name.lower()} record',
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': {'$ref': f'#/components/schemas/{model_name}Input'}
                            }
                        }
                    },
                    'responses': {
                        '201': {
                            'description': 'Created successfully',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': f'#/components/schemas/{model_name}'}
                                }
                            }
                        },
                        '422': {
                            'description': 'Validation error',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/ValidationError'}
                                }
                            }
                        }
                    }
                }
            
            # Detail endpoint: GET /api/posts/:id
            detail_path = f"/{url_prefix}/{{id}}"
            paths[detail_path] = {}
            
            if 'read' not in disabled:
                paths[detail_path]['get'] = {
                    'tags': [model_name],
                    'summary': f'Get a single {model_name.lower()}',
                    'description': f'Retrieve a {model_name.lower()} by ID',
                    'parameters': [
                        {
                            'name': 'id',
                            'in': 'path',
                            'required': True,
                            'schema': {'type': 'integer'},
                            'description': f'{model_name} ID'
                        }
                    ],
                    'responses': {
                        '200': {
                            'description': 'Successful response',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': f'#/components/schemas/{model_name}'}
                                }
                            }
                        },
                        '404': {
                            'description': 'Not found'
                        }
                    }
                }
            
            # Update endpoint: PUT /api/posts/:id
            if 'update' not in disabled:
                paths[detail_path]['put'] = {
                    'tags': [model_name],
                    'summary': f'Update a {model_name.lower()} (full)',
                    'description': f'Replace all fields of a {model_name.lower()}',
                    'parameters': [
                        {
                            'name': 'id',
                            'in': 'path',
                            'required': True,
                            'schema': {'type': 'integer'},
                            'description': f'{model_name} ID'
                        }
                    ],
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': {'$ref': f'#/components/schemas/{model_name}Input'}
                            }
                        }
                    },
                    'responses': {
                        '200': {
                            'description': 'Updated successfully',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': f'#/components/schemas/{model_name}'}
                                }
                            }
                        },
                        '404': {'description': 'Not found'},
                        '422': {
                            'description': 'Validation error',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/ValidationError'}
                                }
                            }
                        }
                    }
                }
                
                # Partial update: PATCH /api/posts/:id
                paths[detail_path]['patch'] = {
                    'tags': [model_name],
                    'summary': f'Update a {model_name.lower()} (partial)',
                    'description': f'Update specific fields of a {model_name.lower()}',
                    'parameters': [
                        {
                            'name': 'id',
                            'in': 'path',
                            'required': True,
                            'schema': {'type': 'integer'},
                            'description': f'{model_name} ID'
                        }
                    ],
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': {'$ref': f'#/components/schemas/{model_name}Input'}
                            }
                        }
                    },
                    'responses': {
                        '200': {
                            'description': 'Updated successfully',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': f'#/components/schemas/{model_name}'}
                                }
                            }
                        },
                        '404': {'description': 'Not found'},
                        '422': {
                            'description': 'Validation error',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/ValidationError'}
                                }
                            }
                        }
                    }
                }
            
            # Delete endpoint: DELETE /api/posts/:id
            if 'delete' not in disabled:
                paths[detail_path]['delete'] = {
                    'tags': [model_name],
                    'summary': f'Delete a {model_name.lower()}',
                    'description': f'Remove a {model_name.lower()} from the database',
                    'parameters': [
                        {
                            'name': 'id',
                            'in': 'path',
                            'required': True,
                            'schema': {'type': 'integer'},
                            'description': f'{model_name} ID'
                        }
                    ],
                    'responses': {
                        '204': {'description': 'Deleted successfully'},
                        '404': {'description': 'Not found'}
                    }
                }
        
        return paths
    
    def _generate_schemas(self) -> Dict[str, Any]:
        """Generate OpenAPI schemas for all models"""
        schemas = {}
        
        for module in self.rest_modules:
            model = module['model']
            model_name = model.__name__
            
            # Output schema (includes all fields + id)
            schemas[model_name] = self._generate_model_schema(model, for_input=False)
            
            # Input schema (for create/update, excludes id and auto-generated fields)
            schemas[f"{model_name}Input"] = self._generate_model_schema(model, for_input=True)
        
        # Add common error schema
        schemas['ValidationError'] = {
            'type': 'object',
            'properties': {
                'errors': {
                    'type': 'object',
                    'additionalProperties': {'type': 'string'}
                }
            }
        }
        
        return schemas
    
    def generate(self) -> Dict[str, Any]:
        """Generate complete OpenAPI 3.0 specification"""
        spec = {
            'openapi': '3.0.3',
            'info': {
                'title': self.title,
                'description': self.description,
                'version': self.version
            },
            'servers': [
                {
                    'url': 'http://localhost:8081',
                    'description': 'Development server'
                }
            ],
            'paths': self._generate_paths(),
            'components': {
                'schemas': self._generate_schemas()
            },
            'tags': []
        }
        
        # Generate tags for each model
        for module in self.rest_modules:
            model_name = module['model'].__name__
            spec['tags'].append({
                'name': model_name,
                'description': f'Operations for {model_name} resources'
            })
        
        return spec

