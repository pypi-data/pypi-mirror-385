"""
Base Scroll class for creating beautiful, themed interfaces
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from rich.console import Console


class Scroll(ABC):
    """
    Base class for creating magical scroll interfaces.

    A scroll is a themed UI component that provides a consistent experience
    for users interacting with magic. Different scrolls can be created for
    different contexts (terminal, web, etc.) while maintaining the same
    magical feel.

    Example:
    ```python
    from geniebottle.scrolls import AgentScroll

    scroll = AgentScroll()
    scroll.unfurl()  # Display welcome
    scroll.inscribe("💬", "User message")
    scroll.cast_spell("text_response", show_args=True)
    scroll.reveal("This is the result")
    ```
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize a scroll.

        Args:
            console: Rich console to use for output. If None, creates a new one.
        """
        self.console = console or Console()

    @abstractmethod
    def unfurl(self):
        """
        Unfurl the scroll - show the welcome/intro screen.
        Called once at the start of the scroll's use.
        """
        pass

    @abstractmethod
    def inscribe(self, icon: str, message: str):
        """
        Inscribe a message on the scroll.

        Args:
            icon: An emoji or symbol to show before the message
            message: The message to display
        """
        pass

    @abstractmethod
    def cast_spell(self, spell_name: str, show_args: bool = False):
        """
        Show that a spell is being cast.

        Args:
            spell_name: Name of the spell being cast
            show_args: Whether to show a streaming args display
        """
        pass

    @abstractmethod
    def reveal(self, content: Any):
        """
        Reveal the result of a spell or operation.

        Args:
            content: The content to reveal (can be str, list, etc.)
        """
        pass

    @abstractmethod
    def seal(self):
        """
        Seal the scroll - perform any cleanup when done.
        """
        pass

    def __enter__(self):
        """Context manager entry"""
        self.unfurl()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.seal()
        return False
