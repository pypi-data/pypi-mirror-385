"""
Page Relationships Mixin - Relationship checking and comparisons.
"""


from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . import Page


class PageRelationshipsMixin:
    """
    Mixin providing relationship checking for pages.

    This mixin handles:
    - Page equality checking
    - Section membership
    - Ancestor/descendant relationships
    """

    def eq(self, other: "Page") -> bool:
        """
        Check if two pages are equal.

        Args:
            other: Page to compare with

        Returns:
            True if pages are the same

        Example:
            {% if page.eq(other_page) %}
              <p>Same page!</p>
            {% endif %}
        """
        # Import here to avoid circular dependency
        from . import Page

        if not isinstance(other, Page):
            return False
        return self.source_path == other.source_path

    def in_section(self, section: Any) -> bool:
        """
        Check if this page is in the given section.

        Args:
            section: Section to check

        Returns:
            True if page is in the section

        Example:
            {% if page.in_section(blog_section) %}
              <span class="badge">Blog Post</span>
            {% endif %}
        """
        return self._section == section

    def is_ancestor(self, other: "Page") -> bool:
        """
        Check if this page is an ancestor of another page.

        Args:
            other: Page to check

        Returns:
            True if this page is an ancestor

        Example:
            {% if section.is_ancestor(page) %}
              <p>{{ page.title }} is a descendant</p>
            {% endif %}
        """
        if not self.is_section:
            return False

        # Check if other page is in this section or subsections
        return other._section in self.walk() if hasattr(self, "walk") else False

    def is_descendant(self, other: "Page") -> bool:
        """
        Check if this page is a descendant of another page.

        Args:
            other: Page to check

        Returns:
            True if this page is a descendant

        Example:
            {% if page.is_descendant(section) %}
              <p>Part of {{ section.title }}</p>
            {% endif %}
        """
        return other.is_ancestor(self) if hasattr(other, "is_ancestor") else False
