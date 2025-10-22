"""Test version information."""

import token_bowl_chat


def test_version() -> None:
    """Test that version is defined."""
    assert hasattr(token_bowl_chat, "__version__")
    assert isinstance(token_bowl_chat.__version__, str)
    assert token_bowl_chat.__version__ == "0.4.0"
