"""
Tests for the scroll system
"""

import pytest
from io import StringIO
from rich.console import Console
from geniebottle.scrolls import Scroll, AgentScroll


class TestAgentScroll:
    """Test the AgentScroll interface"""

    def test_scroll_creation(self):
        """Test that we can create an AgentScroll"""
        scroll = AgentScroll()
        assert scroll is not None
        assert isinstance(scroll, Scroll)

    def test_scroll_with_custom_console(self):
        """Test scroll with custom console for output capture"""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        scroll = AgentScroll(console=console)
        assert scroll.console == console

    def test_unfurl_displays_welcome(self):
        """Test that unfurl displays the welcome message"""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        scroll = AgentScroll(console=console, show_cwd=False)

        scroll.unfurl()

        result = output.getvalue()
        assert "Welcome to the Magic Agent" in result
        assert "/help" in result

    def test_inscribe_message(self):
        """Test inscribing a message"""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        scroll = AgentScroll(console=console)

        scroll.inscribe("💬", "Hello, world!")

        result = output.getvalue()
        assert "💬" in result
        assert "Hello, world!" in result

    def test_cast_spell_creates_animation(self):
        """Test that casting a spell starts properly"""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        scroll = AgentScroll(console=console)

        scroll.cast_spell("test_spell")

        assert scroll._casting is True
        assert scroll._current_spell == "test_spell"

        # Clean up
        scroll.seal()

    def test_reveal_displays_content(self):
        """Test revealing content"""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        scroll = AgentScroll(console=console)

        scroll.cast_spell("test_spell")
        scroll.reveal("Test result")

        result = output.getvalue()
        assert "Test result" in result
        assert scroll._casting is False

    def test_reveal_handles_lists(self):
        """Test revealing list content"""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        scroll = AgentScroll(console=console)

        scroll.cast_spell("test_spell")
        scroll.reveal(["item1", "item2", "item3"])

        result = output.getvalue()
        assert "item1" in result
        assert "item2" in result
        assert "item3" in result

    def test_show_error(self):
        """Test error display"""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        scroll = AgentScroll(console=console)

        scroll.show_error("Test error message")

        result = output.getvalue()
        assert "Test error message" in result
        assert "Error" in result

    def test_show_warning(self):
        """Test warning display"""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        scroll = AgentScroll(console=console)

        scroll.show_warning("Test warning")

        result = output.getvalue()
        assert "Test warning" in result
        assert "Warning" in result

    def test_seal_cleanup(self):
        """Test that seal cleans up properly"""
        scroll = AgentScroll()
        scroll.cast_spell("test_spell")

        scroll.seal()

        assert scroll._animation_active is False

    def test_context_manager(self):
        """Test using scroll as a context manager"""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)

        with AgentScroll(console=console, show_cwd=False) as scroll:
            scroll.inscribe("💬", "Test message")

        result = output.getvalue()
        assert "Welcome to the Magic Agent" in result
        assert "Test message" in result


class TestScrollBase:
    """Test the base Scroll class"""

    def test_scroll_is_abstract(self):
        """Test that Scroll cannot be instantiated directly"""
        with pytest.raises(TypeError):
            Scroll()

    def test_scroll_requires_implementation(self):
        """Test that subclasses must implement abstract methods"""

        class IncompleteScroll(Scroll):
            pass

        with pytest.raises(TypeError):
            IncompleteScroll()
