"""
ChatScroll - A clean interface for chat interactions
"""

from typing import Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from .scroll import Scroll


class ChatScroll(Scroll):
    """
    A scroll designed for simple chat interactions.

    Features:
    - Clean welcome screen
    - User/assistant message display
    - Streaming response support
    - Beautiful formatting

    Example:
    ```python
    scroll = ChatScroll()
    scroll.unfurl()

    scroll.inscribe("💬", "Hello!")
    with scroll.stream_response() as live:
        for chunk in response_chunks:
            live.update(chunk)
    ```
    """

    def __init__(self, console: Optional[Console] = None, title: str = "Magic Chat"):
        """
        Initialize the ChatScroll.

        Args:
            console: Rich console to use
            title: Title for the chat interface
        """
        super().__init__(console)
        self.title = title
        self._live = None

    def unfurl(self):
        """Display the welcome screen."""
        self.console.print("\n")
        self.console.print(Panel(
            f"✨💬 [bold cyan]{self.title}[/bold cyan]\n\n"
            "Ask anything or type [bold]exit[/bold] to quit",
            border_style="cyan",
            padding=(0, 1)
        ))
        self.console.print()

    def inscribe(self, icon: str, message: str):
        """
        Display a message on the scroll.

        Args:
            icon: Icon/emoji to show (e.g., "💬")
            message: The message text
        """
        self.console.print(f"{icon} {message}")

    def cast_spell(self, spell_name: str, show_args: bool = False):
        """
        ChatScroll doesn't display spell casting (simpler interface).

        Args:
            spell_name: Name of the spell (ignored for chat)
            show_args: Whether to show args (ignored for chat)
        """
        pass

    def reveal(self, content: Any):
        """
        Reveal content (for chat, this is the assistant's response).

        Args:
            content: The content to reveal
        """
        if isinstance(content, list):
            for item in content:
                self.console.print(f"  • {item}")
        else:
            self.console.print(str(content))
        self.console.print()

    def stream_response(self):
        """
        Create a Live context for streaming responses.

        Returns:
            Rich Live object for streaming updates

        Example:
        ```python
        with scroll.stream_response() as live:
            for chunk in chunks:
                live.update(chunk)
        ```
        """
        self._live = Live("", console=self.console)
        return self._live

    def seal(self):
        """Clean up when done."""
        if self._live and self._live.is_started:
            self._live.stop()
