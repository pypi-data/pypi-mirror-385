from typing import Callable, Optional, Union, Generator
from PIL import Image
from rich.traceback import install
from .costcalculator import CostCalculator
from .spellcasters import safely_cast_spell
# use nice rich tracebacks
install(show_locals=True)


class Magic:
    """
    `Magic` app class is the main entrypoint to do something with Magic.

    Example:

    ```python
    from geniebottle import Magic
    from geniebottle.spells import GenieBottle

    # declare a new `Magic` instance
    magic = Magic()

    # add a spell to it
    magic.add_spell(GenieBottle('chatgpt'))

    # finally, use it to cast a spell
    magic.cast('Hello, how are you?')

    # or serve it as an api
    magic.serve()
    """

    def __init__(self, max_cost_per_cast=0.01):
        self.spells = []
        self.max_cost_per_cast = max_cost_per_cast

    def add(self, spells: Union[Callable, list[Callable]]) -> None:
        '''
        Add a spell or multiple spells to the magic instance.

        Args:
            spells (Union[Callable, list[Callable]]): The spell function to add. Can be
            auto-generated from a `SpellBook` like `GenieBottle().get('chatgpt')` or
            `OpenAI().get('chatgpt')`. It can also be a custom function.

        Example:
        ```python
        from geniebottle import Magic
        from geniebottle.spellbooks import GenieBottle

        magic = Magic()

        # add a spell
        spell = GenieBottle().get('chatgpt')
        magic.add(spell)

        # or add a custom spell
        def custom_spell(input: str, context: str, system: str):
            """ get the current time and add to the input for context """
            from datetime import datetime
            input = f'The time is {datetime.now().strftime("%H:%M:%S")}. {input}'
            return input, context, system

        magic.add(custom_spell)

        # or add multiple spells at once
        spells = [
            GenieBottle().get('dalle')
            GenieBottle().get('chatgpt'),
        ]
        magic.add(spells)

        # use these spells
        magic.cast('What's the time Mr Wolf?')
        '''
        if isinstance(spells, list):
            self.spells.extend(spells)
            return

        self.spells.append(spells)

    def cast(
        self,
        chained: bool = True,
        chained_input_names: Union[str, list[str], list[list[str]]] = 'input',
        **kwargs
    ):
        '''
        Cast spells added to the magic instance. If multiple spells were provided, this
        will cast all spells in the order they were added. Optionally chain the output
        of one spell to the input of the next spell.

        Args:
            chained (bool, optional): Whether to chain outputs of spells to the input of
            the next spell. Defaults to True.
            chained_input_names (Union[str, list[str], list[list[str]]], optional): The
            name of the input argument/s to chain from the one spell to the next.
            Use a single value if the input name parameter remains the same. Use a list
            of names if using different input argument names for each spell or a list of
            lists of names if there are multiple outputs in a spell being passed to the
            next spell. Defaults to 'input'.
            **kwargs: The input arguments for spell functions. If `chained`
            is True, the output of the previous spell will be passed to the next spell
            overridding the `chained_input_names` kwarg.

        Returns:
            A list of the outputs of the spells cast.
        '''
        cost_calculator = CostCalculator(self.max_cost_per_cast, self.spells)

        cost_calculator.check_cost(**kwargs)

        if not chained:
            for spell in self.spells:
                yield safely_cast_spell(spell, kwargs)
            return

        for i, spell in enumerate(self.spells):
            output = safely_cast_spell(spell, kwargs)

            # if is a generator, yield each item and concatenate 
            # the output to send to the next chained spell
            if isinstance(output, Generator):
                outputs = []
                for item in output:
                    yield item
                    outputs.append(item)

                if isinstance(outputs[0], str):
                    output = ''.join(outputs)
                elif isinstance(outputs, list) and len(outputs) == 1:
                    output = outputs[0]
                else:
                    output = outputs
            else:
                yield output


            if not isinstance(chained_input_names, list):
                kwargs[chained_input_names] = output
                continue

            if not isinstance(chained_input_names[i], list):
                kwargs[chained_input_names[i]] = output
                continue

            for j, chained_input_name in enumerate(chained_input_names[i]):
                kwargs[chained_input_name] = output[j]


    def serve(self, host: str = "0.0.0.0", port: int = 8080):
        '''
        Serve the Magic spells as a REST API using FastAPI.

        This automatically generates REST API endpoints for all spells with
        type validation, error handling, and OpenAPI documentation.

        Args:
            host (str): Host to bind the server to. Defaults to "0.0.0.0"
            port (int): Port to bind the server to. Defaults to 8080

        Returns:
            FastAPI: The FastAPI application instance

        Example:
            ```python
            from geniebottle import Magic
            from geniebottle.spellbooks import OpenAI

            magic = Magic()
            magic.add(OpenAI().get('chatgpt'))

            # Returns a FastAPI app that can be served with uvicorn
            app = magic.serve()
            ```

        Note:
            The returned app can be run with:
            ```bash
            uvicorn module:app --host 0.0.0.0 --port 8080
            ```

            Or use the `beard serve` command:
            ```bash
            beard serve script.py
            ```
        '''
        from geniebottle.fastapi_generator import create_fastapi_app_from_magic
        return create_fastapi_app_from_magic(self)

    def __repr__(self):
        return f'<Magic: {len(self.spells)} spells>'
