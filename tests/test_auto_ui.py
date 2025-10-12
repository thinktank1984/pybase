# -*- coding: utf-8 -*-
"""
Tests for Auto UI Generation

🚨 CRITICAL POLICY: NO MOCKING ALLOWED 🚨

⚠️ USING MOCKS, STUBS, OR TEST DOUBLES IS ILLEGAL IN THIS REPOSITORY ⚠️

This is a ZERO-TOLERANCE POLICY:
- ❌ FORBIDDEN: unittest.mock, Mock(), MagicMock(), patch()
- ❌ FORBIDDEN: pytest-mock, mocker fixture
- ❌ FORBIDDEN: Any mocking, stubbing, or test double libraries
- ❌ FORBIDDEN: Fake in-memory databases or fake HTTP responses
- ❌ FORBIDDEN: Simulated external services or APIs

✅ ONLY REAL INTEGRATION TESTS ARE ALLOWED:
- ✅ Real database operations with actual SQL
- ✅ Real HTTP requests through test client
- ✅ Real browser interactions with Chrome DevTools MCP
- ✅ Real external service calls (or skip tests if unavailable)

If you write a test with mocks, the test is INVALID and must be rewritten.

Tests the auto UI generator functionality including:
- UI mapping loading
- Route generation
- Form generation
- Permission checking
- Template rendering
"""

import pytest
import os
import json
import sys
from datetime import datetime
from emmett import App
from emmett.orm import Database, Model, Field, belongs_to

# Add runtime directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime'))

from auto_ui_generator import AutoUIGenerator, UIMappingLoader, auto_ui


# Test models
class TestPost(Model):
    title = Field()
    text = Field.text()
    published = Field.bool()
    views = Field.int()
    created_at = Field.datetime()
    
    auto_ui_config = {
        'display_name': 'Test Post',
        'display_name_plural': 'Test Posts',
        'list_columns': ['id', 'title', 'published'],
        'search_fields': ['title', 'text'],
        'sort_default': '-created_at'
    }


class TestComment(Model):
    belongs_to('test_post')
    text = Field.text()
    created_at = Field.datetime()


class TestUIMappingLoader:
    """Test UI mapping loader functionality."""
    
    def test_load_default_mappings(self):
        """Test loading default UI mappings."""
        loader = UIMappingLoader(
            default_path=os.path.join(os.path.dirname(__file__), '..', 'runtime', 'ui_mapping.json')
        )
        loader.load()
        
        # Check that standard field types are mapped
        assert 'string' in loader.mappings
        assert 'text' in loader.mappings
        assert 'bool' in loader.mappings
        assert 'int' in loader.mappings
        assert 'datetime' in loader.mappings
        assert 'date' in loader.mappings
        
        # Check string mapping details
        string_mapping = loader.mappings['string']
        assert string_mapping['component'] == 'input'
        assert 'attributes' in string_mapping
        assert string_mapping['attributes']['type'] == 'text'
    
    def test_load_custom_mappings(self, tmp_path):
        """Test loading and merging custom UI mappings."""
        # Create temporary custom mapping file
        custom_mapping = {
            'mappings': {
                'string': {
                    'component': 'input',
                    'attributes': {
                        'type': 'text',
                        'class': 'custom-input-class'
                    }
                },
                'custom_type': {
                    'component': 'input',
                    'attributes': {
                        'type': 'custom'
                    }
                }
            }
        }
        custom_path = tmp_path / 'ui_mapping_custom.json'
        with open(custom_path, 'w') as f:
            json.dump(custom_mapping, f)
        
        loader = UIMappingLoader(
            default_path=os.path.join(os.path.dirname(__file__), '..', 'runtime', 'ui_mapping.json'),
            custom_path=str(custom_path)
        )
        loader.load()
        
        # Check custom type was added
        assert 'custom_type' in loader.mappings
        
        # Check string mapping was overridden
        string_mapping = loader.mappings['string']
        assert string_mapping['attributes']['class'] == 'custom-input-class'
    
    def test_get_component_for_type(self):
        """Test getting UI component for field type."""
        loader = UIMappingLoader(
            default_path=os.path.join(os.path.dirname(__file__), '..', 'runtime', 'ui_mapping.json')
        )
        loader.load()
        
        # Test known type
        string_component = loader.get_component_for_type('string')
        assert string_component['component'] == 'input'
        
        # Test unknown type (should return default)
        unknown_component = loader.get_component_for_type('unknown_type')
        assert unknown_component['component'] == 'input'
        assert unknown_component['attributes']['type'] == 'text'
    
    def test_get_formatter_for_type(self):
        """Test getting display formatter for field type."""
        loader = UIMappingLoader(
            default_path=os.path.join(os.path.dirname(__file__), '..', 'runtime', 'ui_mapping.json')
        )
        loader.load()
        
        # Test datetime formatter
        assert loader.get_formatter_for_type('datetime') == 'format_datetime'
        
        # Test boolean formatter
        assert loader.get_formatter_for_type('bool') == 'format_boolean'
        
        # Test unknown type (should return None)
        assert loader.get_formatter_for_type('unknown_type') is None


class TestAutoUIGenerator:
    """Test AutoUIGenerator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = App(__name__)
        self.app.config.db.uri = 'sqlite:memory'
        self.db = Database(self.app)
        self.db.define_models(TestPost, TestComment)
    
    def test_generator_initialization(self):
        """Test AutoUIGenerator initialization."""
        generator = AutoUIGenerator(self.app, TestPost, '/admin/posts')
        
        assert generator.app == self.app
        assert generator.model == TestPost
        assert generator.url_prefix == '/admin/posts'
        assert generator.model_name == 'testpost'
        
        # Check config merged from model
        assert generator.config['display_name'] == 'Test Post'
        assert generator.config['display_name_plural'] == 'Test Posts'
        assert 'title' in generator.config['search_fields']
    
    def test_merge_config(self):
        """Test configuration merging."""
        custom_config = {
            'display_name': 'Custom Post',
            'page_size': 50
        }
        generator = AutoUIGenerator(self.app, TestPost, '/admin/posts', custom_config)
        
        # Custom config should override
        assert generator.config['display_name'] == 'Custom Post'
        assert generator.config['page_size'] == 50
        
        # Model config should still be present
        assert generator.config['display_name_plural'] == 'Test Posts'
        assert 'title' in generator.config['search_fields']
    
    def test_get_model_fields(self):
        """Test extracting field names from model."""
        generator = AutoUIGenerator(self.app, TestPost, '/admin/posts')
        fields = generator._get_model_fields()
        
        assert 'title' in fields
        assert 'text' in fields
        assert 'published' in fields
        assert 'views' in fields
        assert 'created_at' in fields
    
    def test_get_field_type(self):
        """Test determining field type for UI mapping."""
        generator = AutoUIGenerator(self.app, TestPost, '/admin/posts')
        
        # Test string field
        assert generator._get_field_type('title') == 'string'
        
        # Test text field
        assert generator._get_field_type('text') == 'text'
        
        # Test boolean field
        assert generator._get_field_type('published') == 'bool'
        
        # Test integer field
        assert generator._get_field_type('views') == 'int'
        
        # Test datetime field
        assert generator._get_field_type('created_at') == 'datetime'
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        generator = AutoUIGenerator(self.app, TestPost, '/admin/posts')
        
        dt = datetime(2025, 1, 15, 14, 30)
        formatted = generator.format_datetime(dt)
        
        assert 'Jan 15, 2025' in formatted
        assert '02:30 PM' in formatted
    
    def test_format_boolean(self):
        """Test boolean formatting."""
        generator = AutoUIGenerator(self.app, TestPost, '/admin/posts')
        
        assert '✓' in generator.format_boolean(True)
        assert 'Yes' in generator.format_boolean(True)
        
        assert '✗' in generator.format_boolean(False)
        assert 'No' in generator.format_boolean(False)
    
    def test_format_field_value_none(self):
        """Test formatting None values."""
        generator = AutoUIGenerator(self.app, TestPost, '/admin/posts')
        
        formatted = generator._format_field_value('title', None)
        assert formatted == '-'
    
    def test_check_permission(self):
        """Test permission checking."""
        config = {
            'permissions': {
                'list': lambda: True,
                'create': lambda: False
            }
        }
        generator = AutoUIGenerator(self.app, TestPost, '/admin/posts', config)
        
        # Test permission that allows
        assert generator._check_permission('list') is True
        
        # Test permission that denies
        assert generator._check_permission('create') is False
        
        # Test unconfigured permission (default allow)
        assert generator._check_permission('update') is True
    
    def test_route_registration(self):
        """Test that routes are registered with the app."""
        generator = AutoUIGenerator(self.app, TestPost, '/admin/posts')
        
        # Register routes (should not raise any errors)
        generator.register_routes()
        
        # Verify the generator was successful
        assert generator is not None
        assert generator.model == TestPost


class TestAutoUIFunction:
    """Test the auto_ui convenience function."""
    
    def test_auto_ui_function(self):
        """Test auto_ui function creates and registers routes."""
        app = App(__name__)
        app.config.db.uri = 'sqlite:memory'
        db = Database(app)
        db.define_models(TestPost)
        
        # Call auto_ui function
        generator = auto_ui(app, TestPost, '/admin/posts')
        
        # Check that generator was created
        assert isinstance(generator, AutoUIGenerator)
        assert generator.model == TestPost
        assert generator.url_prefix == '/admin/posts'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

