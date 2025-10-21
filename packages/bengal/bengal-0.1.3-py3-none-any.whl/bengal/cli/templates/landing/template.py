"""Landing template definition."""


from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ..base import SiteTemplate, TemplateFile


def _load_template_file(relative_path: str) -> str:
    """Load a template file from the pages directory."""
    template_dir = Path(__file__).parent
    file_path = template_dir / "pages" / relative_path

    with open(file_path) as f:
        content = f.read()

    # Replace template variables
    current_date = datetime.now().strftime("%Y-%m-%d")
    content = content.replace("{{date}}", current_date)

    return content


def _create_landing_template() -> SiteTemplate:
    """Create the landing page site template."""

    files = [
        TemplateFile(
            relative_path="index.md",
            content=_load_template_file("index.md"),
            target_dir="content",
        ),
        TemplateFile(
            relative_path="privacy.md",
            content=_load_template_file("privacy.md"),
            target_dir="content",
        ),
        TemplateFile(
            relative_path="terms.md",
            content=_load_template_file("terms.md"),
            target_dir="content",
        ),
    ]

    return SiteTemplate(
        id="landing",
        name="Landing",
        description="Landing page for products or services",
        files=files,
        additional_dirs=[],
        menu_sections=[],  # Landing pages typically use custom CTAs, not standard nav
    )


# Export the template
TEMPLATE = _create_landing_template()
