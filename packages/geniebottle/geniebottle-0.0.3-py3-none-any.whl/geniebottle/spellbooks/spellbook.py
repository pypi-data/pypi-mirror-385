import importlib.util
import types
import sys
import os
from rich import print
from typing import Callable
from functools import wraps


class SpellBook:
    '''
    Base class for generating spells.

    Example:
    ```python
        from geniebottle import Magic
        from geniebottle.spellbooks import GenieBottle

        magic = Magic()

        spellbook = GenieBottle()
        spell = spellbook.get('chatgpt')

        magic.add(spell)
    ```
    '''

    def __init__(self):
        self.available_spells = self._list_spells()

    def get(self, name: str, **kwargs) -> Callable:
        '''
        Get a spell from this spellbook.

        Use the `.available_spells` variable to find spells available to this spellbook.

        Args:
            name (str): Name of the spell to get.
            **kwargs (dict): Any additional arguments to pass to the spell function.
            They are overridden if new kwargs are passed to the spell function when
            casting. These kwargs set at this time are available from the
            `spell.defined_kwargs` attribute.

        Returns:
            Spell (Callable): A spell function.
        '''
        if name not in self.available_spells.keys():
            raise Exception("Spell not found...")

        original_func = self.available_spells[name]

        # Check if the spell is bound
        if hasattr(original_func, 'is_bound_spell') and original_func.is_bound_spell:
            # Handle bound spells
            @wraps(original_func)
            def wrapped_function(*args, **new_kwargs):
                all_kwargs = {**kwargs, **new_kwargs}
                return original_func(self, *args, **all_kwargs)
        else:
            # Handle regular spells
            @wraps(original_func)
            def wrapped_function(*args, **new_kwargs):
                all_kwargs = {**kwargs, **new_kwargs}
                return original_func(*args, **all_kwargs)

        setattr(wrapped_function, 'defined_kwargs', kwargs)

        return wrapped_function

    @classmethod
    def _list_spells(cls):
        '''
        List all spells available from the spellbook, considering only functions
        specified in the 'spells' list or tuple in the spells module.
        '''
        current_module_name = cls.__module__
        current_module = sys.modules[current_module_name]
        directory = os.path.dirname(current_module.__file__)

        spells_module_path = os.path.join(directory, 'spells.py')

        if not os.path.exists(spells_module_path):
            raise FileNotFoundError(
                "spells.py doesn't exist in the expected directory. "
                "Please make sure that the spells.py file exists in the same directory "
                "as the spellbook."
            )

        spec = importlib.util.spec_from_file_location("spells", spells_module_path)
        spells_module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = spells_module
        spec.loader.exec_module(spells_module)

        try:
            spell_names_or_funcs = getattr(spells_module, 'spells')
        except AttributeError:
            raise AttributeError(
                "'spells' variable not found in spells.py. Please ensure there's a "
                "list or tuple named 'spells' defining the available spells."
            )

        spells_dict = {}
        for item in spell_names_or_funcs:
            if isinstance(item, str):
                # If the item is a string, get the function by name
                func = getattr(spells_module, item, None)
                if func and isinstance(func, types.FunctionType):
                    spells_dict[item] = func
            elif isinstance(item, types.FunctionType):
                # If the item is a function, add it directly
                spells_dict[item.__name__] = item

            # check if the function is bound to the spellbook
            if hasattr(item, 'is_bound_spell') and item.is_bound_spell:
                # if so, add it to the spells dict
                spells_dict[item.__name__] = item

        return spells_dict

    def check_pricing(self):
        '''
        Provide a link to the pricing page for the spellbook provider

        Example:
        ```python
        from geniebottle.spellbooks import StabilityAI, OpenAI

        spellbook = StabilityAI()
        spellbook.check_pricing()
        # https://platform.stability.ai/pricing

        spellbook = OpenAI()
        spellbook.check_pricing()
        # https://openai.com/pricing
        '''
        raise NotImplementedError

    def __repr__(self):
        return f'<SpellBook>'

    def print(self, text):
        print(text)
