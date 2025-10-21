"""
Module loader for dynamically importing Magic scripts.

This module provides functionality to load Python files as modules
and extract Magic instances from them for serving.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Optional


class ModuleLoadError(Exception):
    """Raised when a module cannot be loaded."""
    pass


class MagicInstanceNotFoundError(Exception):
    """Raised when no Magic instance is found in a module."""
    pass


def load_module_from_file(file_path: str, module_name: Optional[str] = None):
    """
    Dynamically load a Python file as a module.

    Args:
        file_path (str): Path to the Python file to load
        module_name (Optional[str]): Optional name for the module. If not provided,
                                     uses the file stem.

    Returns:
        module: The loaded module

    Raises:
        ModuleLoadError: If the file cannot be loaded or doesn't exist
    """
    path = Path(file_path)

    if not path.exists():
        raise ModuleLoadError(f"File not found: {file_path}")

    if not path.suffix == '.py':
        raise ModuleLoadError(f"File must be a Python file (.py): {file_path}")

    # Use the file stem as module name if not provided
    if module_name is None:
        module_name = path.stem

    try:
        # Create a module spec from the file
        spec = importlib.util.spec_from_file_location(module_name, path)

        if spec is None or spec.loader is None:
            raise ModuleLoadError(f"Could not create module spec for: {file_path}")

        # Create and execute the module
        module = importlib.util.module_from_spec(spec)

        # Add to sys.modules before executing to support imports
        sys.modules[module_name] = module

        # Execute the module
        spec.loader.exec_module(module)

        return module

    except Exception as e:
        # Remove from sys.modules if we added it
        if module_name in sys.modules:
            del sys.modules[module_name]
        raise ModuleLoadError(f"Error loading module from {file_path}: {e}")


def extract_magic_instance(module):
    """
    Extract a Magic instance from a loaded module.

    Args:
        module: The module to search for a Magic instance

    Returns:
        Magic: The Magic instance found in the module

    Raises:
        MagicInstanceNotFoundError: If no Magic instance is found
    """
    from geniebottle.applications import Magic

    # Look for a Magic instance in the module's namespace
    for attr_name in dir(module):
        # Skip private attributes
        if attr_name.startswith('_'):
            continue

        attr = getattr(module, attr_name)

        # Check if it's a Magic instance
        if isinstance(attr, Magic):
            return attr

    raise MagicInstanceNotFoundError(
        f"No Magic instance found in module. "
        f"Make sure your script creates a Magic instance with a name like 'magic' or 'app'."
    )


def load_magic_from_file(file_path: str):
    """
    Load a Python file and extract its Magic instance.

    This is the main convenience function that combines loading and extraction.

    Args:
        file_path (str): Path to the Python file containing a Magic instance

    Returns:
        tuple[module, Magic]: The loaded module and its Magic instance

    Raises:
        ModuleLoadError: If the file cannot be loaded
        MagicInstanceNotFoundError: If no Magic instance is found

    Example:
        >>> module, magic = load_magic_from_file('examples/chat.py')
        >>> print(magic)
        <Magic: 1 spells>
    """
    module = load_module_from_file(file_path)
    magic = extract_magic_instance(module)
    return module, magic
