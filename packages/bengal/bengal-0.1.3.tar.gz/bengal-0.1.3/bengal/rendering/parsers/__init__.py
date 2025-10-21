"""
Content parser for Markdown and other formats.

Supports multiple parser engines:
- python-markdown: Full-featured, slower (default)
- mistune: Fast, subset of features
"""


from __future__ import annotations

from bengal.rendering.parsers.base import BaseMarkdownParser
from bengal.rendering.parsers.mistune import MistuneParser
from bengal.rendering.parsers.python_markdown import PythonMarkdownParser

try:
    # Auto-apply Pygments performance patch for tests and default behavior
    from bengal.rendering.parsers.pygments_patch import PygmentsPatch

    PygmentsPatch.apply()
except Exception:
    pass

# Legacy alias for backwards compatibility
MarkdownParser = PythonMarkdownParser

__all__ = [
    "BaseMarkdownParser",
    "PythonMarkdownParser",
    "MistuneParser",
    "MarkdownParser",
    "create_markdown_parser",
]


def create_markdown_parser(engine: str | None = None) -> BaseMarkdownParser:
    """
    Factory function to create a markdown parser instance.

    Args:
        engine: Parser engine to use ('python-markdown', 'mistune', or None for default)

    Returns:
        Markdown parser instance

    Raises:
        ValueError: If engine is not supported
    """
    engine = (engine or "mistune").lower()

    if engine == "mistune":
        return MistuneParser()
    elif engine in ("python-markdown", "python_markdown", "markdown"):
        return PythonMarkdownParser()
    else:
        raise ValueError(
            f"Unsupported markdown engine: {engine}. Choose from: 'python-markdown', 'mistune'"
        )
