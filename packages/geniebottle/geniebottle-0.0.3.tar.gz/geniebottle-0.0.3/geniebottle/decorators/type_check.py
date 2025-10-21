from functools import wraps
from pydantic import create_model, ValidationError
from typing import get_type_hints, Union, _GenericAlias
import inspect


def type_name(type_hint):
    """ Returns a readable name for a type hint. """
    if isinstance(type_hint, _GenericAlias):
        if type_hint.__origin__ is Union:
            return "Union[" + ", ".join(type_name(arg) for arg in type_hint.__args__) + "]"
        return type_hint._name  # For other generic types like List, Dict, etc.
    return type_hint.__name__


def type_check(func: callable) -> callable:
    hints = get_type_hints(func)
    DynamicModel = create_model('DynamicModel', **{k: (v, ...) for k, v in hints.items()})

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs)
        func_args.apply_defaults()
        args_dict = dict(func_args.arguments)

        # handle self seperately
        self_arg = args_dict.pop('self', None)

        try:
            validated_args = DynamicModel(**args_dict).model_dump()
        except ValidationError as e:
            error_messages = {}
            for error in e.errors():
                param = error['loc'][0]

                if param in error_messages:
                    continue

                expected_type = type_name(hints[param]) if param in hints else 'Unknown'
                received_value = args_dict.get(param, 'None')
                received_type = type(received_value).__name__
                error_message = (
                    f"ValidationError for '{param}': Expected {expected_type}, "
                    f"received {received_type} (value: {received_value})."
                )
                error_messages[param] = error_message

            error_msg = '\n'.join(error_messages.values())
            raise TypeError(error_msg) from None

        # add back self when calling function
        if self_arg is not None:
            return func(self_arg, **validated_args)

        return func(**validated_args)

    return wrapper
