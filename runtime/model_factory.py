# -*- coding: utf-8 -*-
"""
Model Factory for Testing

Provides factories to easily create test data for Emmett models.

Usage:
    from model_factory import Factory, register_factory
    
    # Define factory
    class PostFactory(Factory):
        model = Post
        
        title = "Test Post {n}"
        content = "Test content for post {n}"
        published = False
        user_id = 1
    
    # Create test data
    post = PostFactory.create()
    post = PostFactory.create(published=True, title="Custom")
    posts = PostFactory.create_batch(10)
"""

import random
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Type
from emmett.orm import Model


class Factory:
    """
    Base factory class for creating test model instances.
    
    Subclass and define:
    - model: The Emmett Model class
    - field defaults: Default values or generators
    
    Example:
        class UserFactory(Factory):
            model = User
            email = lambda n: f"user{n}@example.com"
            username = lambda n: f"user{n}"
            password = "testpass123"
    """
    
    model: Optional[Type[Model]] = None
    _sequence = 0
    _instances: List[Model] = []
    
    @classmethod
    def _get_next_sequence(cls) -> int:
        """Get next sequence number."""
        cls._sequence += 1
        return cls._sequence
    
    @classmethod
    def _resolve_value(cls, value: Any, sequence: int) -> Any:
        """Resolve a value (can be callable or static)."""
        if callable(value):
            try:
                return value(sequence)
            except TypeError:
                return value()
        return value
    
    @classmethod
    def _format_string(cls, value: str, sequence: int) -> str:
        """Format string with {n} placeholder."""
        if '{n}' in value:  # type: ignore[reportUnnecessaryIsInstance]
            return value.format(n=sequence)
        return value
    
    @classmethod
    def build(cls, **kwargs) -> Model:
        """
        Build model instance (without saving to database).
        
        Args:
            **kwargs: Override default attributes
            
        Returns:
            Model instance (not saved)
        """
        if cls.model is None:  # type: ignore[reportUnnecessaryComparison]
            raise ValueError("Factory must define 'model' class attribute")
        
        sequence = cls._get_next_sequence()
        
        # Get default attributes from factory
        attrs = {}
        for key, value in cls.__dict__.items():
            if key.startswith('_') or key == 'model':
                continue
            if callable(value) and key in ['build', 'create', 'create_batch', 'reset']:
                continue
            
            resolved_value = cls._resolve_value(value, sequence)
            resolved_value = cls._format_string(resolved_value, sequence)
            attrs[key] = resolved_value
        
        # Override with provided kwargs
        attrs.update(kwargs)
        
        # Create instance (use model's __init__ if available)
        instance = cls.model(**attrs)
        return instance
    
    @classmethod
    def create(cls, **kwargs) -> Model:
        """
        Create and save model instance to database.
        
        Args:
            **kwargs: Override default attributes
            
        Returns:
            Saved model instance
        """
        instance = cls.model.create(**cls._get_attributes(**kwargs))
        cls._instances.append(instance)
        return instance
    
    @classmethod
    def _get_attributes(cls, **kwargs) -> Dict[str, Any]:
        """Get attributes dict for creation."""
        sequence = cls._get_next_sequence()
        
        attrs = {}
        for key, value in cls.__dict__.items():
            if key.startswith('_') or key == 'model':
                continue
            if callable(value) and key in ['build', 'create', 'create_batch', 'reset', '_get_attributes', '_resolve_value', '_format_string', '_get_next_sequence']:
                continue
            
            resolved_value = cls._resolve_value(value, sequence)
            resolved_value = cls._format_string(resolved_value, sequence)
            attrs[key] = resolved_value
        
        attrs.update(kwargs)
        return attrs
    
    @classmethod
    def create_batch(cls, count: int, **kwargs) -> List[Model]:
        """
        Create multiple instances.
        
        Args:
            count: Number of instances to create
            **kwargs: Override default attributes for all instances
            
        Returns:
            List of saved model instances
        """
        return [cls.create(**kwargs) for _ in range(count)]
    
    @classmethod
    def reset(cls):
        """Reset factory state."""
        cls._sequence = 0
        cls._instances = []


# Common attribute generators
class Generators:
    """Common generators for factory attributes."""
    
    @staticmethod
    def email(n: int) -> str:
        """Generate test email."""
        return f"user{n}@example.com"
    
    @staticmethod
    def username(n: int) -> str:
        """Generate test username."""
        return f"user{n}"
    
    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate random string."""
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    @staticmethod
    def random_int(min_val: int = 0, max_val: int = 100) -> int:
        """Generate random integer."""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def random_bool() -> bool:
        """Generate random boolean."""
        return random.choice([True, False])
    
    @staticmethod
    def random_choice(choices: List[Any]) -> Any:
        """Pick random choice from list."""
        return random.choice(choices)
    
    @staticmethod
    def datetime_now() -> datetime:
        """Get current datetime."""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def datetime_past(days: int = 30) -> datetime:
        """Get datetime in the past."""
        return datetime.now(timezone.utc) - timedelta(days=random.randint(1, days))
    
    @staticmethod
    def datetime_future(days: int = 30) -> datetime:
        """Get datetime in the future."""
        return datetime.now(timezone.utc) + timedelta(days=random.randint(1, days))


# Factory registry
_factories: Dict[str, Type[Factory]] = {}


def register_factory(name: str, factory_class: Type[Factory]):
    """Register a factory by name."""
    _factories[name] = factory_class


def get_factory(name: str) -> Optional[Type[Factory]]:
    """Get factory by name."""
    return _factories.get(name)


# Example factories for common models
"""
from app import User, Post, Comment
from model_factory import Factory, Generators, register_factory

class UserFactory(Factory):
    model = User
    email = Generators.email
    username = Generators.username
    first_name = "John"
    last_name = lambda n: f"Doe{n}"
    password = "testpass123"

register_factory('user', UserFactory)


class PostFactory(Factory):
    model = Post
    title = "Test Post {n}"
    text = "This is test content for post {n}."
    date = Generators.datetime_past
    user = 1  # Or use: lambda: UserFactory.create().id
    
register_factory('post', PostFactory)


class CommentFactory(Factory):
    model = Comment
    text = "Test comment {n}"
    date = Generators.datetime_now
    user = 1
    post = 1  # Or use: lambda: PostFactory.create().id

register_factory('comment', CommentFactory)


# Usage in tests:
def test_post_creation():
    post = PostFactory.create()
    assert post.id is not None
    assert post.title.startswith("Test Post")

def test_post_with_comments():
    post = PostFactory.create()
    comments = CommentFactory.create_batch(5, post=post.id)
    assert len(comments) == 5

def test_custom_post():
    post = PostFactory.create(
        title="Custom Title",
        published=True
    )
    assert post.title == "Custom Title"
    assert post.published == True
"""


# Faker integration (optional)
try:
    from faker import Faker  # type: ignore[reportMissingImports]
    fake = Faker()
    
    class FakerGenerators:
        """Generators using Faker library."""
        
        @staticmethod
        def name() -> str:
            return fake.name()
        
        @staticmethod
        def email() -> str:
            return fake.email()
        
        @staticmethod
        def username() -> str:
            return fake.user_name()
        
        @staticmethod
        def text(sentences: int = 3) -> str:
            return fake.text(max_nb_chars=200)
        
        @staticmethod
        def paragraph() -> str:
            return fake.paragraph()
        
        @staticmethod
        def url() -> str:
            return fake.url()
        
        @staticmethod
        def phone() -> str:
            return fake.phone_number()
        
        @staticmethod
        def address() -> str:
            return fake.address()
        
        @staticmethod
        def company() -> str:
            return fake.company()
    
    FAKER_AVAILABLE = True
except ImportError:
    FakerGenerators = None  # type: ignore[assignment, misc]
    FAKER_AVAILABLE = False  # type: ignore[reportConstantRedefinition]

