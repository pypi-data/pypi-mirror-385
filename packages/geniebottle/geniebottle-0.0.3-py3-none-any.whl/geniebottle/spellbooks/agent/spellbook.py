from geniebottle.spellbooks.spellbook import SpellBook


class Agent(SpellBook):
    '''
    `Agent` class helps you define a new spell for use with `Magic`.

    Example:
    ```python
        from geniebottle import Magic
        from geniebottle.spellbooks import Agent

        magic = Magic()

        magic.add(Agent().get('LLMAgent'))
    ```
    '''

    def __init__(
        self
    ):
        super().__init__()

    def __repr__(self):
        return '<Local SpellBook>'
