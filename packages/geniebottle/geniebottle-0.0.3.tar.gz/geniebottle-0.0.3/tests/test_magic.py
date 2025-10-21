"""
Tests for the Magic class
"""

import pytest
from geniebottle import Magic


class TestMagicClass:
    """Test the Magic application class"""

    def test_magic_creation(self):
        """Test creating a Magic instance"""
        magic = Magic()
        assert magic is not None
        assert magic.spells == []

    def test_magic_with_max_cost(self):
        """Test creating Magic with max cost per cast"""
        magic = Magic(max_cost_per_cast=0.5)
        assert magic.max_cost_per_cast == 0.5

    def test_add_single_spell(self):
        """Test adding a single spell"""
        magic = Magic()

        def test_spell(input: str):
            return f"Processed: {input}"

        magic.add(test_spell)
        assert len(magic.spells) == 1
        assert magic.spells[0] == test_spell

    def test_add_multiple_spells(self):
        """Test adding multiple spells at once"""
        magic = Magic()

        def spell1(input: str):
            return f"Spell1: {input}"

        def spell2(input: str):
            return f"Spell2: {input}"

        magic.add([spell1, spell2])
        assert len(magic.spells) == 2

    def test_cast_single_spell(self):
        """Test casting a single spell"""
        magic = Magic()

        def echo_spell(input: str):
            return f"Echo: {input}"

        magic.add(echo_spell)
        results = list(magic.cast(input="test"))

        assert len(results) == 1
        assert results[0] == "Echo: test"

    def test_cast_chained_spells(self):
        """Test casting chained spells"""
        magic = Magic()

        def add_prefix(input: str):
            return f"Hello, {input}"

        def add_suffix(input: str):
            return f"{input}!"

        magic.add([add_prefix, add_suffix])
        results = list(magic.cast(chained=True, input="World"))

        assert len(results) == 2
        assert results[0] == "Hello, World"
        assert results[1] == "Hello, World!"

    def test_cast_unchained_spells(self):
        """Test casting unchained spells"""
        magic = Magic()

        def spell1(input: str):
            return f"Spell1: {input}"

        def spell2(input: str):
            return f"Spell2: {input}"

        magic.add([spell1, spell2])
        results = list(magic.cast(chained=False, input="test"))

        assert len(results) == 2
        assert results[0] == "Spell1: test"
        assert results[1] == "Spell2: test"

    def test_magic_repr(self):
        """Test string representation of Magic"""
        magic = Magic()

        def spell1():
            pass

        def spell2():
            pass

        magic.add([spell1, spell2])
        assert repr(magic) == "<Magic: 2 spells>"

    def test_serve_returns_fastapi_app(self):
        """Test that serve method returns a FastAPI app"""
        magic = Magic()

        def test_spell(input: str):
            return f"Result: {input}"

        magic.add(test_spell)
        app = magic.serve()

        # Check that it returns a FastAPI-like object
        assert app is not None
        assert hasattr(app, 'routes') or hasattr(app, 'router')


class TestMagicIntegration:
    """Integration tests for Magic with real spellbooks"""

    def test_magic_with_custom_spell(self):
        """Test using Magic with a custom spell function"""
        magic = Magic()

        def custom_time_spell(input: str):
            """Add timestamp to input"""
            return f"[TIME] {input}"

        magic.add(custom_time_spell)
        results = list(magic.cast(input="Hello"))

        assert len(results) == 1
        assert "[TIME] Hello" in results[0]

    def test_magic_chained_transformation(self):
        """Test a realistic chained transformation"""
        magic = Magic()

        def uppercase(input: str):
            return input.upper()

        def add_exclamation(input: str):
            return f"{input}!!!"

        def add_prefix(input: str):
            return f"ALERT: {input}"

        magic.add([uppercase, add_exclamation, add_prefix])
        results = list(magic.cast(chained=True, input="hello world"))

        assert results[-1] == "ALERT: HELLO WORLD!!!"

    def test_magic_with_generators(self):
        """Test Magic handles generator spells correctly"""
        magic = Magic()

        def streaming_spell(input: str):
            """Yield chunks of output"""
            words = input.split()
            for word in words:
                yield word

        magic.add(streaming_spell)
        results = list(magic.cast(input="hello world test"))

        # Generator should be consumed and concatenated
        assert len(results) > 0
