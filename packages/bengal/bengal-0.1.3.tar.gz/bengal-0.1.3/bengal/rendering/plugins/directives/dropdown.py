"""
Dropdown directive for Mistune.

Provides collapsible sections with markdown support including
nested directives and code blocks.
"""


from __future__ import annotations

from mistune.directives import DirectivePlugin

from bengal.utils.logger import get_logger

__all__ = ["DropdownDirective", "render_dropdown"]

logger = get_logger(__name__)


class DropdownDirective(DirectivePlugin):
    """
    Collapsible dropdown directive with markdown support.

    Syntax:
        ````{dropdown} Title
        :open: true

        Content with **markdown**, code blocks, etc.

        !!! note
            Even nested admonitions work!
        ````
    """

    def parse(self, block, m, state):
        """Parse dropdown directive with nested content support."""
        title = self.parse_title(m)
        if not title:
            title = "Details"

        options = dict(self.parse_options(m))
        content = self.parse_content(m)

        # Parse nested markdown content
        children = self.parse_tokens(block, content, state)

        return {"type": "dropdown", "attrs": {"title": title, **options}, "children": children}

    def __call__(self, directive, md):
        """Register the directive and renderer."""
        directive.register("dropdown", self.parse)
        directive.register("details", self.parse)  # Alias

        if md.renderer and md.renderer.NAME == "html":
            md.renderer.register("dropdown", render_dropdown)


def render_dropdown(renderer, text, **attrs):
    """Render dropdown to HTML."""
    title = attrs.get("title", "Details")
    is_open = attrs.get("open", "").lower() in ("true", "1", "yes")
    open_attr = " open" if is_open else ""

    html = (
        f'<details class="dropdown"{open_attr}>\n'
        f"  <summary>{title}</summary>\n"
        f'  <div class="dropdown-content">\n'
        f"{text}"
        f"  </div>\n"
        f"</details>\n"
    )
    return html
