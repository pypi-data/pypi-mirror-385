from geniebottle.spellbooks.spellbook import SpellBook

class Editor(SpellBook):
    '''
    `Editor` class helps you define a new spell for use with `Magic`.

    Example:
    ```python
        from geniebottle import Magic
        from geniebottle.spellbooks import Editor

        magic = Magic()

        magic.add(Editor().get('create_file'))
    ```
    '''

    def __init__(
        self
    ):
        super().__init__()

    def __repr__(self):
        return '<Editor SpellBook>'
