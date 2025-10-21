from geniebottle.spellbooks.spellbook import SpellBook

class File(SpellBook):
    '''
    `File` class helps you define a new spell for use with `Magic`.

    Example:
    ```python
        from geniebottle import Magic
        from geniebottle.spellbooks import File

        magic = Magic()

        magic.add(File().get('read_file'))
    ```
    '''

    def __init__(
        self
    ):
        super().__init__()

    def __repr__(self):
        return '<File SpellBook>'
