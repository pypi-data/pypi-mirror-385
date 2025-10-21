"""
Utilities for creating Pydantic models from function signatures.

This module provides shared functionality for both the @type_check decorator
and the FastAPI generator to create Pydantic models from function signatures.
"""

import inspect
from typing import get_type_hints, get_origin, get_args, Any, Dict, Tuple, Optional, Callable
from pydantic import BaseModel, Field, create_model


def is_callable_type(type_hint) -> bool:
    """
    Check if a type hint is Callable or contains Callable.

    Examples:
        Callable -> True
        Callable[[int], str] -> True
        list[Callable] -> True
        str -> False
    """
    if type_hint is Callable:
        return True

    # Check if it's a generic type with Callable origin (e.g., Callable[[int], str])
    origin = get_origin(type_hint)
    if origin is Callable or (hasattr(origin, '__name__') and origin.__name__ == 'Callable'):
        return True

    # Check if it's a list/tuple/etc containing Callable (e.g., list[Callable])
    if origin in (list, tuple, set):
        args = get_args(type_hint)
        if args:
            return any(is_callable_type(arg) for arg in args)

    return False


def create_pydantic_fields_from_signature(
    func: callable,
    preserve_defaults: bool = True,
    extract_descriptions: bool = False,
    exclude_params: Optional[list[str]] = None
) -> Dict[str, Tuple]:
    """
    Extract Pydantic field definitions from a function signature.

    This is the core logic shared between @type_check validation and FastAPI
    model generation, with options to control behavior.

    Args:
        func: The function to introspect
        preserve_defaults: If True, preserve default values from function signature.
                          If False, all fields become required (useful for validation)
        extract_descriptions: If True, extract field descriptions from docstrings
                             (useful for OpenAPI documentation)
        exclude_params: List of parameter names to exclude from the model

    Returns:
        Dict mapping field names to (type, default/Field) tuples suitable for
        create_model()

    Example:
        >>> def my_func(name: str, age: int = 0):
        ...     pass
        >>> fields = create_pydantic_fields_from_signature(my_func)
        >>> Model = create_model('MyModel', **fields)
    """
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)

    exclude_params = exclude_params or []

    # Extract docstrings if requested
    arg_descriptions = {}
    if extract_descriptions:
        from geniebottle.utils import extract_arg_docstrings
        docstring = inspect.getdoc(func) or ""
        for param_name in sig.parameters.keys():
            if param_name in ['self', 'args', 'kwargs']:
                continue
            arg_doc_text = extract_arg_docstrings(docstring, [param_name])
            if arg_doc_text and not arg_doc_text.startswith(f"{param_name}: No docstring"):
                arg_descriptions[param_name] = arg_doc_text.replace(f"{param_name}: ", "").strip()

    # Build field definitions
    fields = {}
    for name, param in sig.parameters.items():
        # Skip special parameters and excluded params
        if name in ['self', 'args', 'kwargs'] or name in exclude_params:
            continue

        # Get type annotation (default to Any if not specified)
        field_type = type_hints.get(name, Any)

        # Handle default values
        if preserve_defaults:
            default_value = param.default if param.default != inspect.Parameter.empty else ...
        else:
            default_value = ...  # All fields required

        # Add description if available
        if extract_descriptions and name in arg_descriptions:
            fields[name] = (field_type, Field(default=default_value, description=arg_descriptions[name]))
        else:
            fields[name] = (field_type, default_value)

    return fields


def create_request_model_from_spell(spell, model_name: Optional[str] = None) -> type[BaseModel]:
    """
    Create a Pydantic model for FastAPI request validation from a spell.

    This is a convenience wrapper around create_pydantic_fields_from_signature
    specifically for FastAPI/OpenAPI usage. Automatically excludes Callable
    parameters since they cannot be serialized to JSON.

    Args:
        spell: The spell function to introspect
        model_name: Optional custom model name (defaults to "{SpellName}Request")

    Returns:
        A Pydantic BaseModel class for request validation
    """
    import warnings

    # Get all type hints to check for Callable parameters
    sig = inspect.signature(spell)
    type_hints = get_type_hints(spell)

    # Find parameters with Callable types
    callable_params = []
    for param_name, param in sig.parameters.items():
        if param_name in ['self', 'args', 'kwargs']:
            continue

        param_type = type_hints.get(param_name, Any)
        if is_callable_type(param_type):
            callable_params.append(param_name)

    # Check if callable params are predefined in defined_kwargs
    undefined_callable_params = []
    if callable_params:
        defined_kwargs = getattr(spell, 'defined_kwargs', {})
        for param in callable_params:
            if param not in defined_kwargs:
                undefined_callable_params.append(param)

    # Warn if there are callable params without default values
    if undefined_callable_params:
        warnings.warn(
            f"Spell '{spell.__name__}' has Callable parameters {undefined_callable_params} "
            f"that are not predefined. These parameters will be excluded from the REST API endpoint. "
            f"To use this spell via REST API, define these parameters when getting the spell from the spellbook:\n"
            f"  spell = SpellBook().get('{spell.__name__}', {', '.join(f'{p}=...' for p in undefined_callable_params)})",
            UserWarning
        )

    # Exclude all callable parameters from the API model
    fields = create_pydantic_fields_from_signature(
        spell,
        preserve_defaults=True,      # FastAPI needs optional params
        extract_descriptions=True,   # For OpenAPI docs
        exclude_params=callable_params  # Exclude Callable params
    )

    # Generate model name if not provided
    if model_name is None:
        spell_name = spell.__name__
        model_name = f"{spell_name.capitalize()}Request"

    return create_model(model_name, **fields)


def create_validation_model_from_func(func, model_name: str = 'DynamicModel') -> type[BaseModel]:
    """
    Create a Pydantic model for runtime type validation.

    This is used by the @type_check decorator to validate function arguments.

    Args:
        func: The function to introspect
        model_name: Name for the model (default: 'DynamicModel')

    Returns:
        A Pydantic BaseModel class for validation
    """
    fields = create_pydantic_fields_from_signature(
        func,
        preserve_defaults=False,     # All fields required for validation
        extract_descriptions=False   # Not needed for validation
    )

    return create_model(model_name, **fields)
