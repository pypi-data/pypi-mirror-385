from rich.console import Console
from rich.traceback import Traceback


def safely_cast_spell(spell, kwargs):
    """ Safely run a spell and return any errors, so execution can continue. """
    console = Console()

    try:
        return spell(**kwargs)
    except (AttributeError, Exception) as e:
        message_for_user = f'Error found in spell {spell.__name__}: {e}'

        tb = Traceback()  # this will get the full traceback
        console.print(tb)
        console.print(message_for_user)

        return message_for_user
