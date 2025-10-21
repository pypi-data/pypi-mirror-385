"""Commands for creating new sites and pages."""


from __future__ import annotations

from datetime import datetime
from pathlib import Path

import click

from bengal.cli.base import BengalGroup
from bengal.cli.site_templates import get_template

# Add these imports
from bengal.utils.build_stats import show_error
from bengal.utils.cli_output import CLIOutput

# Preset definitions for wizard
PRESETS = {
    "blog": {
        "name": "Blog",
        "emoji": "📝",
        "description": "Personal or professional blog",
        "sections": ["blog", "about"],
        "with_content": True,
        "pages_per_section": 3,
        "template_id": "blog",
    },
    "docs": {
        "name": "Documentation",
        "emoji": "📚",
        "description": "Technical docs or guides",
        "sections": ["getting-started", "guides", "reference"],
        "with_content": True,
        "pages_per_section": 3,
        "template_id": "docs",
    },
    "portfolio": {
        "name": "Portfolio",
        "emoji": "💼",
        "description": "Showcase your work",
        "sections": ["about", "projects", "blog", "contact"],
        "with_content": True,
        "pages_per_section": 3,
        "template_id": "portfolio",
    },
    "business": {
        "name": "Business",
        "emoji": "🏢",
        "description": "Company or product site",
        "sections": ["products", "services", "about", "contact"],
        "with_content": True,
        "pages_per_section": 2,
        "template_id": "default",  # Fallback if no business template yet
    },
    "resume": {
        "name": "Resume",
        "emoji": "📄",
        "description": "Professional resume/CV site",
        "sections": ["resume"],
        "with_content": True,
        "pages_per_section": 1,
        "template_id": "resume",
    },
}


def _should_run_init_wizard(template: str, no_init: bool, init_preset: str) -> bool:
    """Determine if we should run the initialization wizard."""
    # Skip if user explicitly said no
    if no_init:
        return False

    # Skip if user provided a preset (they know what they want)
    if init_preset:
        return True

    # Skip if template is non-default (template already has structure)
    # Otherwise, prompt the user
    return template == "default"


def _run_init_wizard(preset: str = None) -> str | None:
    """Run the site initialization wizard and return the selected template ID or None."""

    cli = CLIOutput()

    # If preset was provided via flag, use it directly
    if preset:
        if preset not in PRESETS:
            cli.warning(f"Unknown preset '{preset}'. Available: " + ", ".join(PRESETS.keys()))
            return None

        selected_preset = PRESETS[preset]
        cli.info(f"🏗️  Selected {selected_preset['emoji']} {selected_preset['name']} preset.")
        return selected_preset.get("template_id", "default")

    # Interactive wizard with questionary
    try:
        import questionary
    except ImportError:
        cli.blank()
        cli.warning("Install questionary for better interactive prompts: pip install questionary")
        return None

    # Build choices list
    choices = []
    preset_items = list(PRESETS.items())

    for key, info in preset_items:
        choices.append(
            {
                "name": f"{info['emoji']} {info['name']:<15} - {info['description']}",
                "value": key,
            }
        )

    choices.append(
        {
            "name": "📦 Blank          - Empty site, no initial structure",
            "value": "__blank__",
        }
    )

    choices.append(
        {
            "name": "⚙️  Custom         - Define your own structure",
            "value": "__custom__",
        }
    )

    # Show interactive menu
    cli.blank()
    cli.header("🎯 What kind of site are you building?")
    selection = questionary.select(
        "Select a preset:",
        choices=choices,
        style=questionary.Style(
            [
                ("qmark", "fg:cyan bold"),
                ("question", "fg:cyan bold"),
                ("pointer", "fg:cyan bold"),
                ("highlighted", "fg:cyan bold"),
                ("selected", "fg:green"),
            ]
        ),
    ).ask()

    # Handle cancellation (Ctrl+C)
    if selection is None:
        cli.blank()
        cli.warning("✨ Cancelled. Will create basic default site.")
        return "default"

    # Handle blank
    if selection == "__blank__":
        cli.blank()
        cli.info("✨ Blank site selected. No initial structure added.")
        return None

    # Handle custom
    if selection == "__custom__":
        cli.blank()
        sections_input = cli.prompt(
            "Enter section names (comma-separated, e.g., blog,about)", default="blog,about"
        )
        pages_per = cli.prompt("Pages per section", default=3, type=int)
        cli.blank()
        cli.info(
            f"✨ Custom structure noted (sections={sections_input}, pages={pages_per}). Basic site created; run 'bengal init --sections {sections_input} --pages-per-section {pages_per} --with-content' after to add structure."
        )
        return "default"  # Custom needs post-creation init

    # Regular preset selected
    selected_preset = PRESETS[selection]
    cli.blank()
    cli.info(f"✨ {selected_preset['name']} preset selected.")
    return selected_preset.get("template_id", "default")


@click.group(cls=BengalGroup)
def new() -> None:
    """
    ✨ Create new site, page, layout, partial, or theme.

    Subcommands:
        site      Create a new Bengal site with optional presets
        page      Create a new page in content directory
        layout    Create a new layout template in templates/layouts/
        partial   Create a new partial template in templates/partials/
        theme     Create a new theme scaffold with templates and assets
    """
    pass


@new.command()
@click.argument("name", required=False)
@click.option("--theme", default="default", help="Theme to use")
@click.option(
    "--template",
    default="default",
    help="Site template (default, blog, docs, portfolio, resume, landing)",
)
@click.option(
    "--no-init",
    is_flag=True,
    help="Skip structure initialization wizard",
)
@click.option(
    "--init-preset",
    help="Initialize with preset (blog, docs, portfolio, business, resume) without prompting",
)
def site(name: str, theme: str, template: str, no_init: bool, init_preset: str) -> None:
    """
    🏗️  Create a new Bengal site with optional structure initialization.
    """
    cli = CLIOutput()

    try:
        # Prompt for site name if not provided
        if not name:
            cli.blank()
            cli.header("🏗️  Create a new Bengal site")
            name = cli.prompt("Enter site name")
            if not name:
                cli.warning("✨ Cancelled.")
                raise click.Abort()

        # Store the original name for site title and slugify for directory
        site_title = name.strip()
        site_dir_name = _slugify(site_title)

        # Validate that slugified name is not empty
        if not site_dir_name:
            show_error(
                "Site name must contain at least one alphanumeric character!", show_art=False
            )
            raise click.Abort()

        site_path = Path(site_dir_name)

        if site_path.exists():
            show_error(f"Directory {site_dir_name} already exists!", show_art=False)
            raise click.Abort()

        # Determine effective template
        effective_template = template
        is_custom = False
        wizard_selection = None

        # Check if we should run wizard (only for default + interactive/non-no-init)
        should_run_wizard = _should_run_init_wizard(template, no_init, init_preset)

        if should_run_wizard:
            # Run wizard before creation to get selection
            wizard_selection = _run_init_wizard(init_preset)

            if wizard_selection is not None and wizard_selection != "default":
                effective_template = wizard_selection
            elif wizard_selection == "__custom__":  # Track for advice
                is_custom = True
            # Else: blank/cancel uses default (None -> default)

        # Get the effective template
        site_template = get_template(effective_template)

        # Show what we're creating
        display_text = site_title
        if site_title != site_dir_name:
            display_text += f" → {site_dir_name}"

        cli.blank()
        cli.header(f"🏗️  Creating new Bengal site: {display_text}")
        cli.info(f"   ({site_template.description})")

        # Create directory structure
        site_path.mkdir(parents=True)
        (site_path / "content").mkdir()
        (site_path / "assets" / "css").mkdir(parents=True)
        (site_path / "assets" / "js").mkdir()
        (site_path / "assets" / "images").mkdir()
        (site_path / "templates").mkdir()

        # Create any additional directories from template
        for additional_dir in site_template.additional_dirs:
            (site_path / additional_dir).mkdir(parents=True, exist_ok=True)

        cli.info("   ├─ Created directory structure")

        # Create config file using site_title for the title field
        config_content = f"""[site]
title = "{site_title}"
baseurl = ""
theme = "{theme}"

[build]
output_dir = "public"
parallel = true

[assets]
minify = true
fingerprint = true
"""
        from bengal.utils.atomic_write import atomic_write_text

        atomic_write_text(site_path / "bengal.toml", config_content)
        cli.info("   ├─ Created bengal.toml")

        # Create .gitignore
        gitignore_content = """# Bengal build outputs
public/

# Bengal cache and dev files
.bengal/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
"""
        atomic_write_text(site_path / ".gitignore", gitignore_content)
        cli.info("   ├─ Created .gitignore")

        # Create files from template (pages, data files, etc.)
        files_created = 0
        for template_file in site_template.files:
            base_dir = site_path / template_file.target_dir
            base_dir.mkdir(parents=True, exist_ok=True)

            file_path = base_dir / template_file.relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_text(file_path, template_file.content)
            files_created += 1

        if files_created == 1:
            cli.info(f"   └─ Created {files_created} file")
        else:
            cli.info(f"   └─ Created {files_created} files")

        cli.blank()
        cli.success("✅ Site created successfully!")

        # Handle special cases for wizard
        if wizard_selection is None and init_preset is None:
            cli.blank()
            cli.tip("Run 'bengal init' to add structure later.")
        if is_custom:
            cli.blank()
            cli.tip(
                "For custom sections, run 'bengal init --sections <your-list> --with-content' now."
            )

        # Show next steps
        cli.blank()
        cli.header("📚 Next steps:")
        cli.info(f"   ├─ cd {site_dir_name}")
        cli.info("   └─ bengal site serve")
        cli.blank()

    except Exception as e:
        show_error(f"Failed to create site: {e}", show_art=False)
        raise click.Abort() from e


def _slugify(text: str) -> str:
    """
    Convert text to URL-safe slug with Unicode support.

    This function preserves Unicode word characters (letters, digits, underscore)
    to support international content. Modern browsers and web servers handle
    Unicode URLs correctly.

    Examples:
        "My Awesome Page" → "my-awesome-page"
        "Hello, World!" → "hello-world"
        "Test   Multiple   Spaces" → "test-multiple-spaces"
        "你好世界" → "你好世界" (Chinese characters preserved)
        "مرحبا" → "مرحبا" (Arabic characters preserved)

    Note:
        Uses Python's \\w pattern which includes Unicode word characters.
        Special punctuation is removed, but international letters/digits are kept.
    """
    import re

    # Lowercase
    text = text.lower()

    # Remove special characters (keep alphanumeric, spaces, hyphens)
    # Note: \w matches [a-zA-Z0-9_] plus Unicode letters and digits
    text = re.sub(r"[^\w\s-]", "", text)

    # Replace spaces and multiple hyphens with single hyphen
    text = re.sub(r"[-\s]+", "-", text)

    # Strip leading/trailing hyphens
    return text.strip("-")


@new.command()
@click.argument("name")
@click.option("--section", default="", help="Section to create page in")
def page(name: str, section: str) -> None:
    """
    📄 Create a new page.

    The page name will be automatically slugified for the filename.
    Example: "My Awesome Page" → my-awesome-page.md
    """
    cli = CLIOutput()

    try:
        # Ensure we're in a Bengal site
        content_dir = Path("content")
        if not content_dir.exists():
            show_error("Not in a Bengal site directory!", show_art=False)
            raise click.Abort()

        # Slugify the name for filename
        slug = _slugify(name)

        # Use original name for title (capitalize properly)
        title = name.replace("-", " ").title()

        # Determine page path
        if section:
            page_dir = content_dir / section
            page_dir.mkdir(parents=True, exist_ok=True)
        else:
            page_dir = content_dir

        # Create page file with slugified name
        page_path = page_dir / f"{slug}.md"

        if page_path.exists():
            show_error(f"Page {page_path} already exists!", show_art=False)
            raise click.Abort()

        # Create page content with current timestamp
        page_content = f"""---
title: {title}
date: {datetime.now().isoformat()}
---

# {title}

Your content goes here.
"""
        # Write new page atomically (crash-safe)
        from bengal.utils.atomic_write import atomic_write_text

        atomic_write_text(page_path, page_content)

        cli.blank()
        cli.success(f"✨ Created new page: {page_path}")
        cli.blank()

    except Exception as e:
        show_error(f"Failed to create page: {e}", show_art=False)
        raise click.Abort() from e


@new.command()
@click.argument("name", required=False)
def layout(name: str) -> None:
    """
    📋 Create a new layout template.

    Layouts are reusable HTML templates used by pages.
    Example: "article" → templates/layouts/article.html
    """
    cli = CLIOutput()

    try:
        # Ensure we're in a Bengal site
        templates_dir = Path("templates")
        if not templates_dir.exists():
            show_error("Not in a Bengal site directory!", show_art=False)
            raise click.Abort()

        if not name:
            name = cli.prompt("Enter layout name")
            if not name:
                cli.warning("✨ Cancelled.")
                raise click.Abort()

        # Slugify the name for filename
        slug = _slugify(name)
        layout_dir = templates_dir / "layouts"
        layout_dir.mkdir(parents=True, exist_ok=True)
        layout_path = layout_dir / f"{slug}.html"

        if layout_path.exists():
            show_error(f"Layout {layout_path} already exists!", show_art=False)
            raise click.Abort()

        # Create layout template
        layout_content = """{% extends "base.html" %}

{% block content %}
{# Your layout content here #}
{{ page.content | safe }}
{% endblock %}
"""
        from bengal.utils.atomic_write import atomic_write_text

        atomic_write_text(layout_path, layout_content)

        cli.blank()
        cli.success(f"✨ Created new layout: {layout_path}")
        cli.info(f"   └─ Extend this in pages with: layout: {slug}")
        cli.blank()

    except Exception as e:
        show_error(f"Failed to create layout: {e}", show_art=False)
        raise click.Abort() from e


@new.command()
@click.argument("name", required=False)
def partial(name: str) -> None:
    """
    🧩 Create a new partial template.

    Partials are reusable template fragments included in other templates.
    Example: "sidebar" → templates/partials/sidebar.html
    """
    cli = CLIOutput()

    try:
        # Ensure we're in a Bengal site
        templates_dir = Path("templates")
        if not templates_dir.exists():
            show_error("Not in a Bengal site directory!", show_art=False)
            raise click.Abort()

        if not name:
            name = cli.prompt("Enter partial name")
            if not name:
                cli.warning("✨ Cancelled.")
                raise click.Abort()

        # Slugify the name for filename
        slug = _slugify(name)
        partial_dir = templates_dir / "partials"
        partial_dir.mkdir(parents=True, exist_ok=True)
        partial_path = partial_dir / f"{slug}.html"

        if partial_path.exists():
            show_error(f"Partial {partial_path} already exists!", show_art=False)
            raise click.Abort()

        # Create partial template
        partial_content = (
            """{# Partial: """
            + slug
            + """ #}
{# Include in templates with: {% include "partials/"""
            + slug
            + """.html" %} #}

<div class=\"partial partial-"""
            + slug
            + """\">
  {# Your partial content here #}
</div>
"""
        )
        from bengal.utils.atomic_write import atomic_write_text

        atomic_write_text(partial_path, partial_content)

        cli.blank()
        cli.success(f"✨ Created new partial: {partial_path}")
        cli.info(f'   └─ Include in templates with: {{% include "partials/{slug}.html" %}}')
        cli.blank()

    except Exception as e:
        show_error(f"Failed to create partial: {e}", show_art=False)
        raise click.Abort() from e


@new.command()
@click.argument("name", required=False)
def theme(name: str) -> None:
    """
    🎨 Create a new theme scaffold.

    Themes are self-contained template and asset packages.
    Example: "my-theme" → themes/my-theme/ with templates, partials, and assets
    """
    cli = CLIOutput()

    try:
        if not name:
            name = cli.prompt("Enter theme name")
            if not name:
                cli.warning("✨ Cancelled.")
                raise click.Abort()

        # Slugify the name for directory
        slug = _slugify(name)

        # Determine if we're in a site or creating standalone
        in_site = Path("content").exists() and Path("bengal.toml").exists()

        theme_path = (Path("themes") / slug) if in_site else Path(slug)

        if theme_path.exists():
            show_error(f"Theme directory {theme_path} already exists!", show_art=False)
            raise click.Abort()

        # Create theme directory structure
        theme_path.mkdir(parents=True)
        (theme_path / "templates").mkdir()
        (theme_path / "templates" / "partials").mkdir()
        (theme_path / "assets" / "css").mkdir(parents=True)
        (theme_path / "assets" / "js").mkdir(parents=True)
        (theme_path / "assets" / "images").mkdir(parents=True)

        cli.blank()
        cli.header(f"🎨 Creating new theme: {name}")
        cli.info(f"   → {theme_path}")
        cli.info("   ├─ Created directory structure")

        from bengal.utils.atomic_write import atomic_write_text

        # Create base.html template
        base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ site.config.title }}{% endblock %}</title>
    <meta name="description" content="{% block description %}{{ site.config.description | default('', true) }}{% endblock %}">
    <link rel="stylesheet" href="{{ url_for('assets/css/style.css') }}">
    {% block extra_head %}{% endblock %}
</head>
<body>
    {% include "partials/header.html" %}

    <main>
        {% block content %}{% endblock %}
    </main>

    {% include "partials/footer.html" %}

    <script src="{{ url_for('assets/js/main.js') }}"></script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>
"""
        atomic_write_text(theme_path / "templates" / "base.html", base_template)

        # Create header partial
        header_partial = """<header class="site-header">
    <div class="container">
        <div class="site-title">
            <h1><a href="{{ site.config.baseurl }}">{{ site.config.title }}</a></h1>
        </div>
        <nav class="site-nav">
            {% for menu_item in site.menu.get('main', []) %}
                <a href="{{ menu_item.url }}">{{ menu_item.name }}</a>
            {% endfor %}
        </nav>
    </div>
</header>
"""
        atomic_write_text(theme_path / "templates" / "partials" / "header.html", header_partial)

        # Create footer partial
        footer_partial = """<footer class="site-footer">
    <div class="container">
        <p>&copy; {{ get_current_year() }} {{ site.config.title }}</p>
    </div>
</footer>
"""
        atomic_write_text(theme_path / "templates" / "partials" / "footer.html", footer_partial)
        home_template = """{% extends "base.html" %}

{% block content %}
<div class="home">
    <h1>Welcome to {{ site.config.title }}</h1>
    <p>{{ site.config.description | default('', true) }}</p>
</div>
{% endblock %}
"""
        atomic_write_text(theme_path / "templates" / "home.html", home_template)

        # Create page template
        page_template = """{% extends "base.html" %}

{% block title %}{{ page.title }} - {{ site.config.title }}{% endblock %}

{% block content %}
<article class="page">
    <header class="page-header">
        <h1>{{ page.title }}</h1>
        {% if page.date %}
        <time datetime="{{ page.date | date_iso }}">{{ page.date | strftime('%B %d, %Y') }}</time>
        {% endif %}
    </header>
    <div class="page-content">
        {{ page.content | safe }}
    </div>
</article>
{% endblock %}
"""
        atomic_write_text(theme_path / "templates" / "page.html", page_template)

        cli.info("   ├─ Created 4 templates")
        cli.info("   ├─ Created 2 partials")

        # Create CSS
        css_content = (
            """/* Theme: """
            + name
            + """ */

:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --text-color: #333;
    --bg-color: #fff;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    color: var(--text-color);
    background-color: var(--bg-color);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.site-header {
    background: var(--primary-color);
    color: white;
    padding: 2rem 0;
    margin-bottom: 2rem;
}

.site-footer {
    background: var(--secondary-color);
    color: white;
    padding: 2rem 0;
    margin-top: 4rem;
    text-align: center;
}

article {
    margin: 2rem 0;
}

h1, h2, h3, h4, h5, h6 {
    margin: 1.5rem 0 0.5rem;
    line-height: 1.3;
}
"""
        )
        atomic_write_text(theme_path / "assets" / "css" / "style.css", css_content)
        cli.info("   ├─ Created CSS stylesheet")

        # Create JS
        js_content = (
            """// Theme: """
            + name
            + """

console.log('Theme loaded: """
            + name
            + """');

document.addEventListener('DOMContentLoaded', function() {
    // Your theme scripts here
});
"""
        )
        atomic_write_text(theme_path / "assets" / "js" / "main.js", js_content)
        cli.info("   └─ Created JavaScript")

        cli.blank()
        cli.success("✅ Theme created successfully!")

        # Show next steps
        cli.blank()
        cli.header("📚 Next steps:")
        if in_site:
            cli.tip(f'Update bengal.toml: theme = "{slug}"')
            cli.tip("Run 'bengal serve'")
        else:
            cli.tip(f"Package as: bengal-theme-{slug}")
            cli.tip("Add to pyproject.toml for distribution")
            cli.tip("pip install -e .")
        cli.blank()

    except Exception as e:
        show_error(f"Failed to create theme: {e}", show_art=False)
        raise click.Abort() from e
