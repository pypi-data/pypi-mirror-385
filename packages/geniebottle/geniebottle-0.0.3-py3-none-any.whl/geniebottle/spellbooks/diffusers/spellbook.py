from geniebottle.spellbooks.spellbook import SpellBook


class Diffusers(SpellBook):
    '''
    `Diffusers` class helps you define a new spell for use with `Magic`.

    Example:
    ```python
        from geniebottle import Magic
        from geniebottle.spellbooks import Diffusers

        magic = Magic()

        magic.add(Diffusers().get('image_generation'))
    ```
    '''

    def __init__(
        self
    ):
        super().__init__()

    def __repr__(self):
        return '<Local SpellBook>'
