from functools import wraps
import types


def bind_to_spellbook(cls):
    """ Binds a spell to a spellbook to give the spell access to the spellbook's self.

    Provides a `self` argument for things like accessing the client instantiated in the
    spellbook.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        setattr(func, 'is_bound_spell', True)
        # setattr(cls, func.__name__, wrapper)
        setattr(cls, func.__name__, types.MethodType(wrapper, cls))
        return func
    return decorator
