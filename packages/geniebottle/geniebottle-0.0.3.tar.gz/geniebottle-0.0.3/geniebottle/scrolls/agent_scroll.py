"""
AgentScroll - A beautiful terminal interface for agent interactions
"""

import sys
import time
import threading
from typing import Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .scroll import Scroll


class AgentScroll(Scroll):
    """
    A scroll designed for agent interactions in the terminal.

    Features:
    - Clean spell casting display (no duplicate "Casting..." text)
    - Smooth animations
    - Beautiful formatting
    - Automatic cleanup of temporary displays

    Example:
    ```python
    scroll = AgentScroll()
    scroll.unfurl()

    scroll.inscribe("💬", "Hello!")
    scroll.cast_spell("text_response")
    scroll.reveal("Hi there!")
    ```
    """

    def __init__(self, console: Optional[Console] = None, show_cwd: bool = True):
        """
        Initialize the AgentScroll.

        Args:
            console: Rich console to use
            show_cwd: Whether to show current working directory in welcome
        """
        super().__init__(console)
        self.show_cwd = show_cwd
        self._casting = False
        self._animation_thread = None
        self._animation_active = False
        self._current_spell = ""
        self._spell_started = False

    def unfurl(self):
        """Display the welcome screen."""
        import os

        self.console.print("\n")
        welcome_text = "✨🤖 [bold cyan]Welcome to the Magic Agent![/bold cyan]\n\n"
        welcome_text += "/help for help, /system to change how I behave"

        if self.show_cwd:
            welcome_text += f"\n\ncwd: [dim]{os.getcwd()}[/dim]"

        self.console.print(Panel(
            welcome_text,
            border_style="cyan",
            padding=(0, 1)
        ))

        self.console.print("\n[dim]Some tips for getting started:[/dim]\n")
        self.console.print("[dim]  Ask me what I can do[/dim]")
        self.console.print("[dim]  Use me to generate images, text, files, edit, run terminal commands and even edit myself![/dim]")
        self.console.print("[dim]  Be as specific as you would when talking with someone for the best results[/dim]\n")

    def inscribe(self, icon: str, message: str):
        """
        Display a message on the scroll.

        Args:
            icon: Icon/emoji to show (e.g., "💬")
            message: The message text
        """
        self.console.print(f"\n{icon} {message}")

    def cast_spell(self, spell_name: str, show_args: bool = False):
        """
        Show that a spell is being cast.

        This displays a clean, animated header while the spell executes.
        The animation automatically stops when args start streaming or when
        the spell completes.

        Args:
            spell_name: Name of the spell
            show_args: Whether to show streaming arguments
        """
        self._current_spell = spell_name
        self._casting = True
        self._spell_started = False

        # Start animation
        self._animation_active = True
        self.console.print()  # Blank line before spell
        self._animation_thread = threading.Thread(target=self._animate_casting, daemon=True)
        self._animation_thread.start()

    def stream_args(self, chunk: str):
        """
        Stream spell arguments as they're being prepared.

        This stops the animation and shows the static spell header,
        then streams the args in dim text.

        Args:
            chunk: A chunk of the arguments to display
        """
        # Stop animation on first chunk
        if self._animation_active:
            self._stop_animation()
            self._show_static_header()

        # Stream the chunk
        self.console.print(f"[dim]{chunk}[/dim]", end='')
        sys.stdout.flush()

    def reveal(self, content: Any):
        """
        Reveal the spell result.

        This stops any animation, ensures the header is shown, and displays
        the result cleanly.

        Args:
            content: The result to display
        """
        # Stop animation if still running
        if self._animation_active:
            self._stop_animation()

        # If we haven't shown the header yet (spell with no args), show it now
        if not self._spell_started:
            self._show_static_header()

        # Add spacing if we were streaming args
        if self._spell_started:
            self.console.print("\n")

        # Display result
        if isinstance(content, list):
            # Format lists nicely
            for item in content[:5]:
                self.console.print(f"  • {item}")
            if len(content) > 5:
                self.console.print(f"  [dim]... and {len(content) - 5} more[/dim]")
        else:
            self.console.print(str(content))

        self.console.print()

        # Reset state
        self._casting = False
        self._spell_started = False
        self._current_spell = ""

    def show_error(self, error_message: str):
        """
        Display an error message.

        Args:
            error_message: The error to display
        """
        if self._animation_active:
            self._stop_animation()

        self.console.print()
        self.console.print(Panel(
            f"[red]{error_message}[/red]",
            title="[bold red]⚠️  Error[/bold red]",
            border_style="red",
            padding=(0, 1)
        ))
        self.console.print()

    def show_warning(self, warning_message: str):
        """
        Display a warning message.

        Args:
            warning_message: The warning to display
        """
        self.console.print()
        self.console.print(Panel(
            warning_message,
            title="[bold yellow]Warning[/bold yellow]",
            border_style="yellow",
            padding=(0, 1)
        ))

    def seal(self):
        """Clean up when done."""
        if self._animation_active:
            self._stop_animation()

    def _animate_casting(self):
        """Animate the spell casting header with rainbow colors."""
        colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']
        color_offset = 0

        while self._animation_active and self._casting:
            # Build animated text
            text = Text()
            text.append("🪄 Casting ", style="bold")

            for i, char in enumerate(self._current_spell):
                color_idx = (i + color_offset) % len(colors)
                text.append(char, style=f"bold {colors[color_idx]}")

            text.append(" (esc to interrupt)", style="dim")

            # Clear line and print
            sys.stdout.write("\r\033[K")
            self.console.print(text, end='')
            sys.stdout.flush()

            time.sleep(0.4)
            color_offset += 1

    def _stop_animation(self):
        """Stop the casting animation."""
        self._animation_active = False
        if self._animation_thread:
            self._animation_thread.join(timeout=0.5)
            self._animation_thread = None

        # Clear the animation line
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def _show_static_header(self):
        """Show the static spell header (called after animation stops)."""
        if not self._spell_started:
            self.console.print(f"🪄 [bold]Cast[/bold] [cyan]{self._current_spell}[/cyan]")
            self.console.print()
            self._spell_started = True
