from functools import wraps


def limit_cost(max_cost=None, **limit_args) -> callable:
    """
    A decorator to apply to spells to specify how they should be limited in terms of
    cost per usage. Accepts any number of named limit arguments.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            out = func(*args, **kwargs)
            return out

        # Assign each limit argument as an attribute of the wrapper
        for key, value in limit_args.items():
            if not str(key).startswith('cost'):
                raise ValueError(
                    f"limit_cost decorator only accepts limit arguments that start "
                    f"with 'cost'. Received {key}={value}."
                )
            setattr(wrapper, key, value)

        # Assign max_cost
        setattr(wrapper, 'max_cost', max_cost)

        return wrapper

    return decorator
