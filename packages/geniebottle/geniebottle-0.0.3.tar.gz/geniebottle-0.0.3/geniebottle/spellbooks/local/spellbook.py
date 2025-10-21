from geniebottle.spellbooks.spellbook import SpellBook


class Local(SpellBook):
    '''
    `Local` class helps you define a new spell for use with `Magic`.

    Example:
    ```python
        from geniebottle import Magic
        from geniebottle.spellbooks import Local

        magic = Magic()

        magic.add(Local().get('chatgpt'))
    ```
    '''

    def __init__(
        self
    ):
        super().__init__()

    def __repr__(self):
        return '<Local SpellBook>'
