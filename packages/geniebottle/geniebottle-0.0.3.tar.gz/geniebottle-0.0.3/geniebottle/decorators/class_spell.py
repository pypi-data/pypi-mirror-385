import inspect
from functools import wraps, update_wrapper


def merge_signatures(sig1, sig2):
    """
    Merge two signatures while ensuring that non-default arguments come before default arguments.
    Variadic keyword parameters (**kwargs) are placed at the end.
    """
    params1 = sig1.parameters
    params2 = sig2.parameters

    # Separate parameters into with and without defaults
    params_with_defaults = []
    params_without_defaults = []

    # Add parameters from sig1, respecting order and defaults
    for name, param in params1.items():
        if param.default is param.empty:
            params_without_defaults.append(param)
        else:
            params_with_defaults.append(param)

    # Add parameters from sig2 that are not in sig1
    for name, param in params2.items():
        if name not in params1:
            if param.default is param.empty:
                params_without_defaults.append(param)
            else:
                params_with_defaults.append(param)

    # Ensure correct order of parameters, ignoring 'self'
    merged_params = params_without_defaults + params_with_defaults
    variadic_keyword_params = [param for param in merged_params if param.kind == param.VAR_KEYWORD]
    positional_keyword_params = [param for param in merged_params if param.kind == param.VAR_POSITIONAL]
    merged_params = [
        param for param in merged_params 
        if param.kind != param.VAR_KEYWORD 
        and param.kind != param.VAR_POSITIONAL
        and param.name != 'self'
    ] + positional_keyword_params + variadic_keyword_params

    return sig1.replace(parameters=merged_params)


def class_spell(cls):
    """
    Initializes a class spell and calls its 'run' method, effectively treating it like
    a spell function.

    Also merges the signatures of the __init__ and run methods, so that the spell
    can have arguments checked and used for calculating cost.
    """
    def wrapped_function(**kwargs):
        instance = cls(**kwargs)
        kwargs.pop('input', None)
        return instance.run(**kwargs)

    init_signature = inspect.signature(cls)
    run_signature = inspect.signature(cls.run)
    merged_signature = merge_signatures(init_signature, run_signature)

    update_wrapper(wrapped_function, cls, assigned=('__name__', '__qualname__'))
    wrapped_function.__signature__ = merged_signature

    return wrapped_function
