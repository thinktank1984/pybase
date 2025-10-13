#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emmett Model Pattern Validation CLI
Should run before running the user app
Validates that Emmett models follow best practices and don't contain anti-patterns.

Usage:
    python validate_models.py --all              # Validate all models
    python validate_models.py Post Comment       # Validate specific models
    python validate_models.py --json             # Output as JSON
    python validate_models.py --verbose          # Verbose output
    python validate_models.py --fix              # Suggest fixes

Anti-patterns detected:
    - HTTP request handling in models
    - Template rendering in models
    - External API calls in models
    - HTML generation in models
    - Direct session access in models
    - Complex business logic that should be in services
"""

import sys
import json
import inspect
import argparse
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# Import models
try:
    from app import User, Post, Comment, db
    from emmett.orm import Model
except ImportError as e:
    print(f"Error importing models: {e}", file=sys.stderr)
    print("Make sure you're running this from the runtime directory", file=sys.stderr)
    sys.exit(1)


@dataclass
class Violation:
    """Represents a pattern violation."""
    model: str
    type: str
    location: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    suggestion: str = ""
    line_number: Optional[int] = None


class ModelValidator:
    """Validates Emmett models for anti-patterns."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.violations: List[Violation] = []
    
    def validate_model(self, model_class: type) -> List[Violation]:
        """Validate a single model class."""
        self.violations = []
        
        if not issubclass(model_class, Model):
            return self.violations
        
        # Get model source code
        try:
            source = inspect.getsource(model_class)
            source_lines = source.split('\n')
        except (OSError, TypeError):
            return self.violations
        
        # Run validation checks
        self._check_http_handling(model_class, source, source_lines)
        self._check_template_rendering(model_class, source, source_lines)
        self._check_html_generation(model_class, source, source_lines)
        self._check_external_api_calls(model_class, source, source_lines)
        self._check_session_access(model_class, source, source_lines)
        self._check_email_sending(model_class, source, source_lines)
        self._check_complex_methods(model_class, source_lines)
        self._check_validation_defined(model_class)
        self._check_missing_docstrings(model_class)
        
        return self.violations
    
    def _add_violation(self, model: str, type: str, location: str, severity: str,
                      message: str, suggestion: str = "", line_number: Optional[int] = None):
        """Add a violation to the list."""
        self.violations.append(Violation(
            model=model,
            type=type,
            location=location,
            severity=severity,
            message=message,
            suggestion=suggestion,
            line_number=line_number
        ))
    
    def _check_http_handling(self, model_class, source, source_lines):
        """Check for HTTP request/response handling."""
        model_name = model_class.__name__
        
        # Check for request parameter in methods
        for name, method in inspect.getmembers(model_class, predicate=inspect.isfunction):
            if name.startswith('_'):
                continue
            
            try:
                sig = inspect.signature(method)
                if 'request' in sig.parameters:
                    self._add_violation(
                        model=model_name,
                        type='http_handling',
                        location=f'{model_name}.{name}',
                        severity='error',
                        message='Methods should not accept request objects',
                        suggestion='Move HTTP handling to controllers. Models should only contain domain logic.'
                    )
            except (ValueError, TypeError):
                pass
        
        # Check source for HTTP-related imports/usage
        http_patterns = [
            ('request.', 'HTTP request access'),
            ('response.', 'HTTP response access'),
            ('redirect(', 'HTTP redirect'),
            ('abort(', 'HTTP abort (use exceptions instead)'),
        ]
        
        for pattern, description in http_patterns:
            if pattern in source:
                # Find line numbers
                for i, line in enumerate(source_lines, 1):
                    if pattern in line and not line.strip().startswith('#'):
                        self._add_violation(
                            model=model_name,
                            type='http_handling',
                            location=f'{model_name} (line {i})',
                            severity='error',
                            message=f'Found {description} in model',
                            suggestion='Move HTTP handling to controllers',
                            line_number=i
                        )
    
    def _check_template_rendering(self, model_class, source, source_lines):
        """Check for template rendering."""
        model_name = model_class.__name__
        
        template_patterns = [
            'render_template',
            'render(',
            '.template(',
            'Template(',
        ]
        
        for pattern in template_patterns:
            if pattern in source:
                for i, line in enumerate(source_lines, 1):
                    if pattern in line and not line.strip().startswith('#'):
                        self._add_violation(
                            model=model_name,
                            type='template_rendering',
                            location=f'{model_name} (line {i})',
                            severity='error',
                            message='Models should not render templates',
                            suggestion='Move presentation logic to views/controllers',
                            line_number=i
                        )
    
    def _check_html_generation(self, model_class, source, source_lines):
        """Check for HTML generation."""
        model_name = model_class.__name__
        
        html_patterns = [
            '<html',
            '<div',
            '<span',
            '<p>',
            '<table',
            '<form',
        ]
        
        for pattern in html_patterns:
            if pattern.lower() in source.lower():
                for i, line in enumerate(source_lines, 1):
                    if pattern.lower() in line.lower() and not line.strip().startswith('#'):
                        self._add_violation(
                            model=model_name,
                            type='html_generation',
                            location=f'{model_name} (line {i})',
                            severity='error',
                            message='Models should not generate HTML',
                            suggestion='Use templates for HTML generation',
                            line_number=i
                        )
    
    def _check_external_api_calls(self, model_class, source, source_lines):
        """Check for external API calls."""
        model_name = model_class.__name__
        
        api_patterns = [
            'requests.',
            'urllib.',
            'httpx.',
            'aiohttp.',
        ]
        
        for pattern in api_patterns:
            if pattern in source:
                for i, line in enumerate(source_lines, 1):
                    if pattern in line and not line.strip().startswith('#'):
                        self._add_violation(
                            model=model_name,
                            type='external_api',
                            location=f'{model_name} (line {i})',
                            severity='warning',
                            message='Models should not make external API calls',
                            suggestion='Move external API calls to service layer',
                            line_number=i
                        )
    
    def _check_session_access(self, model_class, source, source_lines):
        """Check for direct session access."""
        model_name = model_class.__name__
        
        if 'session.' in source or 'session[' in source:
            for i, line in enumerate(source_lines, 1):
                if ('session.' in line or 'session[' in line) and not line.strip().startswith('#'):
                    # Allow session.auth pattern (common in Emmett)
                    if 'session.auth' not in line:
                        self._add_violation(
                            model=model_name,
                            type='session_access',
                            location=f'{model_name} (line {i})',
                            severity='warning',
                            message='Models should not directly access session',
                            suggestion='Pass user/data as method parameters instead',
                            line_number=i
                        )
    
    def _check_email_sending(self, model_class, source, source_lines):
        """Check for email sending."""
        model_name = model_class.__name__
        
        email_patterns = [
            'mailer.',
            'send_mail',
            'send_email',
            'smtp.',
        ]
        
        for pattern in email_patterns:
            if pattern in source:
                for i, line in enumerate(source_lines, 1):
                    if pattern in line and not line.strip().startswith('#'):
                        self._add_violation(
                            model=model_name,
                            type='email_sending',
                            location=f'{model_name} (line {i})',
                            severity='warning',
                            message='Models should not send emails directly',
                            suggestion='Move email sending to service layer',
                            line_number=i
                        )
    
    def _check_complex_methods(self, model_class, source_lines):
        """Check for overly complex methods."""
        model_name = model_class.__name__
        
        for name, method in inspect.getmembers(model_class, predicate=inspect.isfunction):
            if name.startswith('_'):
                continue
            
            try:
                method_source = inspect.getsource(method)
                lines = method_source.split('\n')
                
                # Check method length
                if len(lines) > 50:
                    self._add_violation(
                        model=model_name,
                        type='complexity',
                        location=f'{model_name}.{name}',
                        severity='info',
                        message=f'Method is very long ({len(lines)} lines)',
                        suggestion='Consider breaking into smaller methods or moving to service layer'
                    )
                
                # Check for multiple responsibilities (heuristic)
                responsibility_keywords = ['and', 'then', 'process', 'handle', 'manage']
                method_name_lower = name.lower()
                responsibility_count = sum(1 for keyword in responsibility_keywords if keyword in method_name_lower)
                
                if responsibility_count >= 2:
                    self._add_violation(
                        model=model_name,
                        type='complexity',
                        location=f'{model_name}.{name}',
                        severity='info',
                        message='Method name suggests multiple responsibilities',
                        suggestion='Consider single-responsibility principle: one method, one purpose'
                    )
            except (OSError, TypeError):
                pass
    
    def _check_validation_defined(self, model_class):
        """Check if validation is defined for required fields."""
        model_name = model_class.__name__
        
        # Check if model has validation attribute
        if not hasattr(model_class, 'validation'):
            # Get fields
            fields = []
            for key, value in model_class.__dict__.items():
                if not key.startswith('_') and hasattr(value, '__class__'):
                    if 'Field' in value.__class__.__name__:
                        fields.append(key)
            
            if fields:
                self._add_violation(
                    model=model_name,
                    type='missing_validation',
                    location=model_name,
                    severity='info',
                    message='Model has fields but no validation rules defined',
                    suggestion='Consider adding validation attribute to ensure data integrity'
                )
    
    def _check_missing_docstrings(self, model_class):
        """Check for missing docstrings."""
        model_name = model_class.__name__
        
        # Check model docstring
        if not model_class.__doc__ or not model_class.__doc__.strip():
            self._add_violation(
                model=model_name,
                type='documentation',
                location=model_name,
                severity='info',
                message='Model is missing docstring',
                suggestion='Add docstring describing model purpose and relationships'
            )
        
        # Check method docstrings
        for name, method in inspect.getmembers(model_class, predicate=inspect.isfunction):
            if name.startswith('_'):
                continue
            
            if not method.__doc__ or not method.__doc__.strip():
                self._add_violation(
                    model=model_name,
                    type='documentation',
                    location=f'{model_name}.{name}',
                    severity='info',
                    message=f'Method {name} is missing docstring',
                    suggestion='Add docstring describing method purpose and parameters'
                )


def get_all_models() -> List[type]:
    """Get all Emmett models from app."""
    models = []
    for model in [User, Post, Comment]:
        if issubclass(model, Model):
            models.append(model)
    return models


def print_results(results: Dict[str, List[Violation]], verbose: bool = False):
    """Print validation results in human-readable format."""
    total_models = len(results)
    total_violations = sum(len(v) for v in results.values())
    
    errors = sum(1 for violations in results.values() for v in violations if v.severity == 'error')
    warnings = sum(1 for violations in results.values() for v in violations if v.severity == 'warning')
    infos = sum(1 for violations in results.values() for v in violations if v.severity == 'info')
    
    print("=" * 80)
    print("Emmett Model Pattern Validation Results")
    print("=" * 80)
    print(f"\nModels checked: {total_models}")
    print(f"Total violations: {total_violations}")
    print(f"  ✗ Errors: {errors}")
    print(f"  ⚠ Warnings: {warnings}")
    print(f"  ℹ Info: {infos}")
    print()
    
    for model_name, violations in results.items():
        if not violations:
            print(f"✓ {model_name}: PASS (no violations)")
            continue
        
        model_errors = [v for v in violations if v.severity == 'error']
        model_warnings = [v for v in violations if v.severity == 'warning']
        model_infos = [v for v in violations if v.severity == 'info']
        
        status = "FAIL" if model_errors else "PASS WITH WARNINGS"
        print(f"{'✗' if model_errors else '⚠'} {model_name}: {status}")
        print(f"   Found {len(violations)} violation(s): {len(model_errors)} errors, {len(model_warnings)} warnings, {len(model_infos)} info")
        print()
        
        # Group violations by type
        violations_by_type = {}
        for v in violations:
            if v.type not in violations_by_type:
                violations_by_type[v.type] = []
            violations_by_type[v.type].append(v)
        
        for vtype, vlist in violations_by_type.items():
            print(f"   [{vtype.upper()}]")
            for v in vlist:
                severity_symbol = {'error': '✗', 'warning': '⚠', 'info': 'ℹ'}[v.severity]
                print(f"     {severity_symbol} {v.location}")
                print(f"        {v.message}")
                if v.suggestion:
                    print(f"        → {v.suggestion}")
            print()
    
    if total_violations == 0:
        print("\n✓ All models pass validation!")
    elif errors > 0:
        print(f"\n✗ Validation failed with {errors} error(s)")
    else:
        print(f"\n⚠ Validation passed with {warnings} warning(s)")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Validate Emmett models for anti-patterns and best practices'
    )
    parser.add_argument(
        'models',
        nargs='*',
        help='Specific models to validate (default: all)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all models'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Include detailed information'
    )
    parser.add_argument(
        '--severity',
        choices=['error', 'warning', 'info'],
        default='error',
        help='Minimum severity level to report (default: error)'
    )
    
    args = parser.parse_args()
    
    # Determine which models to validate
    if args.all or not args.models:
        models_to_validate = get_all_models()
    else:
        models_to_validate = []
        available_models = {
            'User': User,
            'Post': Post,
            'Comment': Comment
        }
        for model_name in args.models:
            if model_name in available_models:
                models_to_validate.append(available_models[model_name])
            else:
                print(f"Error: Unknown model '{model_name}'", file=sys.stderr)
                print(f"Available models: {', '.join(available_models.keys())}", file=sys.stderr)
                sys.exit(1)
    
    if not models_to_validate:
        print("Error: No models found to validate", file=sys.stderr)
        sys.exit(1)
    
    # Validate models
    validator = ModelValidator(verbose=args.verbose)
    results = {}
    
    for model in models_to_validate:
        violations = validator.validate_model(model)
        
        # Filter by severity
        severity_order = {'error': 0, 'warning': 1, 'info': 2}
        min_severity = severity_order[args.severity]
        filtered_violations = [
            v for v in violations
            if severity_order[v.severity] <= min_severity
        ]
        
        results[model.__name__] = filtered_violations
    
    # Output results
    if args.json:
        json_results = {
            model_name: [asdict(v) for v in violations]
            for model_name, violations in results.items()
        }
        print(json.dumps(json_results, indent=2))
    else:
        print_results(results, verbose=args.verbose)
    
    # Exit with error code if any errors found
    has_errors = any(
        v.severity == 'error'
        for violations in results.values()
        for v in violations
    )
    
    sys.exit(1 if has_errors else 0)


if __name__ == '__main__':
    main()

