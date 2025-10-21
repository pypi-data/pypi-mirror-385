import inspect
import re
from typing import Callable
import warnings


def get_max_cost(spell):
    if getattr(spell, 'max_cost', None) is None:
        # warnings.warn(f"Spell {spell.__name__} does not have a max_cost attribute.")
        return 0

    if not isinstance(spell.max_cost, Callable):
        return spell.max_cost

    kwargs = get_default_args(spell)
    # override any defaults set when spell was defined
    kwargs.update(spell.defined_kwargs)
    # filter kwargs to only those that are valid for brain
    filtered_kwargs = {
        k: v for k, v in kwargs.items() if k in get_arg_names(spell.max_cost)
    }
    return spell.max_cost(**filtered_kwargs)


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def get_args_without_defaults(func, ignore_args_and_kwargs=True):
    """
    Returns the names of arguments of the given function
    that do not have default values.
    """
    signature = inspect.signature(func)
    kws = [
        name for name, param in signature.parameters.items()
        if param.default is inspect.Parameter.empty
    ]
    if ignore_args_and_kwargs:
        kws = [kw for kw in kws if kw not in ['args', 'kwargs']]

    return kws


def get_arg_names(func):
    signature = inspect.signature(func)
    return [k for k in signature.parameters.keys()]  # change the type to a list of str


def extract_arg_docstrings(docstring, arg_names):
    """
    Extracts and concatenates the docstrings for specific arguments from a function's docstring.

    Args:
        docstring (str): The full docstring of the function.
        arg_names (list of str): A list of names of the arguments whose docstrings are to be extracted.

    Returns:
        str: A concatenated string of the extracted docstrings for the specified arguments.
    """

    combined_doc = ''
    for arg_name in arg_names:
        # Regular expression to match the argument and its multiline description
        pattern = r'\b' + re.escape(arg_name) + r'\s*\(.*?\):\s*(.*?)(?=\n\s*\w+\s*\(.*?\):|\n\s*Returns:|\n\s*\Z)'
        match = re.search(pattern, docstring, re.DOTALL)

        if match:
            # Extract the argument's docstring
            combined_doc += arg_name + ': ' + match.group(1).strip() + '\n\n'
        else:
            # No docstring found for the argument
            combined_doc += arg_name + ': No docstring found.\n\n'

    return combined_doc.strip()


def extract_docstring_description(docstring):
    """
    Extracts the description part of a docstring before the "Args" section.

    Args:
        docstring (str): The docstring from which to extract the description.

    Returns:
        str: The extracted description part of the docstring.
    """
    # Regex pattern to match everything before "Args" section
    pattern = r"^(.*?)(?=\n\s*Args:)"

    # Perform the regex search
    match = re.search(pattern, docstring, re.DOTALL)

    # Return the matched description or an empty string if no match is found
    return match.group(1).strip() if match else ""
