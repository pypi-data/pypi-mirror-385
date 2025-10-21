"""
Section orchestration for Bengal SSG.

Handles section lifecycle: ensuring all sections have index pages,
validation, and structural integrity.
"""


from __future__ import annotations

from typing import TYPE_CHECKING

from bengal.content_types.registry import detect_content_type, get_strategy
from bengal.utils.logger import get_logger
from bengal.utils.page_initializer import PageInitializer
from bengal.utils.url_strategy import URLStrategy

logger = get_logger(__name__)

if TYPE_CHECKING:
    from bengal.core.page import Page
    from bengal.core.section import Section
    from bengal.core.site import Site


class SectionOrchestrator:
    """
    Handles section structure and completeness.

    Responsibilities:
    - Ensure all sections have index pages (explicit or auto-generated)
    - Generate archive pages for sections without _index.md
    - Validate section structure
    - Maintain section hierarchy integrity

    This orchestrator implements the "structural" concerns of sections,
    separate from cross-cutting concerns like taxonomies (tags, categories).
    """

    def __init__(self, site: Site):
        """
        Initialize section orchestrator.

        Args:
            site: Site instance to manage sections for
        """
        self.site = site
        self.url_strategy = URLStrategy()
        self.initializer = PageInitializer(site)

    def finalize_sections(self, affected_sections: set[str] | None = None) -> None:
        """
        Finalize sections by ensuring they have index pages.

        For each section:
        - If it has an explicit _index.md, leave it alone
        - If it doesn't have an index page, generate an archive page
        - Recursively process subsections

        This ensures all section URLs resolve to valid pages.

        Args:
            affected_sections: Set of section paths that were affected by changes.
                             If None, finalize all sections (full build).
                             If provided, only finalize affected sections (incremental).
        """
        logger.info(
            "section_finalization_start",
            section_count=len(self.site.sections),
            incremental=affected_sections is not None,
        )

        archive_count = 0
        for section in self.site.sections:
            # In incremental mode, skip sections not affected by changes
            if affected_sections is not None and str(section.path) not in affected_sections:
                # Still need to recursively check subsections
                archives_created = self._finalize_recursive_filtered(section, affected_sections)
            else:
                archives_created = self._finalize_recursive(section)
            archive_count += archives_created

        # Invalidate page caches once after all sections are finalized
        # (rather than repeatedly during recursive processing)
        if archive_count > 0:
            self.site.invalidate_page_caches()

        logger.info("section_finalization_complete", archives_created=archive_count)

    def _finalize_recursive_filtered(self, section: Section, affected_sections: set[str]) -> int:
        """
        Recursively finalize only affected sections (incremental optimization).

        Args:
            section: Section to finalize
            affected_sections: Set of section paths that were affected

        Returns:
            Number of archive pages created
        """
        archive_count = 0

        # Skip root section (no index needed)
        if section.name == "root":
            # Still process subsections (with filter)
            for subsection in section.subsections:
                if str(subsection.path) in affected_sections:
                    archive_count += self._finalize_recursive(subsection)
                else:
                    archive_count += self._finalize_recursive_filtered(
                        subsection, affected_sections
                    )
            return archive_count

        # Only finalize if this section was affected
        if str(section.path) in affected_sections:
            archive_count += self._finalize_recursive(section)
        else:
            # Not affected - just recursively check subsections
            for subsection in section.subsections:
                if str(subsection.path) in affected_sections:
                    archive_count += self._finalize_recursive(subsection)
                else:
                    archive_count += self._finalize_recursive_filtered(
                        subsection, affected_sections
                    )

        return archive_count

    def _finalize_recursive(self, section: Section) -> int:
        """
        Recursively finalize a section and its subsections.

        Args:
            section: Section to finalize

        Returns:
            Number of archive pages created
        """
        archive_count = 0

        # Skip root section (no index needed)
        if section.name == "root":
            # Still process subsections
            for subsection in section.subsections:
                archive_count += self._finalize_recursive(subsection)
            return archive_count

        # Ensure this section has an index page
        if not section.index_page:
            # Generate archive index
            archive_page = self._create_archive_index(section)
            section.index_page = archive_page
            self.site.pages.append(archive_page)
            archive_count += 1

            logger.debug(
                "section_archive_created",
                section_name=section.name,
                section_path=str(section.path),
                page_count=len(section.pages),
            )
        else:
            # Section has an existing index page - enrich it if it needs section context
            self._enrich_existing_index(section)

        # Recursively finalize subsections
        for subsection in section.subsections:
            archive_count += self._finalize_recursive(subsection)

        return archive_count

    def _detect_content_type(self, section: Section) -> str:
        """
        Detect what kind of content this section contains.

        Delegates to the content type registry's detection logic.

        Args:
            section: Section to analyze

        Returns:
            Content type name (e.g., 'blog', 'doc', 'api-reference')
        """
        return detect_content_type(section)

    def _should_paginate(self, section: Section, content_type: str) -> bool:
        """
        Determine if section should have pagination.

        Delegates to the content type strategy's pagination logic.

        Args:
            section: Section to check
            content_type: Detected content type

        Returns:
            True if section should have pagination
        """
        # Get strategy and ask if pagination is appropriate
        strategy = get_strategy(content_type)

        # Allow explicit override
        if "paginate" in section.metadata:
            return section.metadata["paginate"]

        # Use strategy's logic
        page_count = len(section.pages)
        return strategy.should_paginate(page_count, self.site.config)

    def _get_template_for_content_type(self, content_type: str) -> str:
        """
        Get the appropriate template for a content type.

        Delegates to the content type strategy's template logic.

        Args:
            content_type: Type of content

        Returns:
            Template name
        """
        strategy = get_strategy(content_type)
        return strategy.get_template()

    def _prepare_posts_list(self, section: Section, content_type: str) -> list[Page]:
        """
        Prepare the posts list for a section using content type strategy.

        Args:
            section: Section to prepare posts for
            content_type: Content type of the section

        Returns:
            Filtered and sorted list of pages
        """
        strategy = get_strategy(content_type)

        # Filter out index page (for auto-generated, index_page may not exist yet)
        filtered_pages = strategy.filter_display_pages(
            section.regular_pages, section.index_page if hasattr(section, "index_page") else None
        )

        # Sort according to content type
        return strategy.sort_pages(filtered_pages)

    def _create_archive_index(self, section: Section) -> Page:
        """
        Create an auto-generated index page for a section.

        Detects content type and uses appropriate template:
        - API reference docs: api-reference/list.html (no pagination)
        - CLI reference docs: cli-reference/list.html (no pagination)
        - Tutorial sections: tutorial/list.html (no pagination)
        - Blog/chronological: archive.html (with pagination)
        - Generic sections: index.html (fallback)

        Args:
            section: Section that needs an index page

        Returns:
            Page object representing the section index

        Example:
            >>> section = Section(path=Path('blog'), name='blog')
            >>> archive_page = orchestrator._create_archive_index(section)
            >>> print(archive_page.template)  # 'archive.html'
            >>> print(archive_page.metadata['type'])  # 'archive'
        """
        from bengal.core.page import Page
        from bengal.utils.pagination import Paginator

        # Create virtual path for generated archive (delegate to utility)
        virtual_path = self.url_strategy.make_virtual_path(self.site, "archives", section.name)

        # Detect content type
        content_type = self._detect_content_type(section)

        # Determine template
        template = self._get_template_for_content_type(content_type)

        # Base metadata
        metadata = {
            "title": section.title,
            "template": template,
            "type": content_type,
            "_generated": True,
            "_virtual": True,
            "_section": section,
            # Filter and sort pages using content type strategy
            "_posts": self._prepare_posts_list(section, content_type),
            "_subsections": section.subsections,
            "_content_type": content_type,
        }

        # Add pagination only if appropriate
        if self._should_paginate(section, content_type):
            paginator = Paginator(
                items=section.pages,
                per_page=self.site.config.get("pagination", {}).get("per_page", 10),
            )
            metadata.update(
                {
                    "_paginator": paginator,
                    "_page_num": 1,
                }
            )

        # Create archive page
        archive_page = Page(source_path=virtual_path, content="", metadata=metadata)

        # Compute output path using centralized logic
        archive_page.output_path = self.url_strategy.compute_archive_output_path(
            section=section, page_num=1, site=self.site
        )

        # Ensure page is correctly initialized (sets _site, validates)
        self.initializer.ensure_initialized_for_section(archive_page, section)

        return archive_page

    def _enrich_existing_index(self, section: Section) -> None:
        """
        Enrich an existing user-created index page with section context.

        This adds the same metadata that auto-generated archives get, allowing
        user-created index pages with type: blog or archive to work properly.

        Args:
            section: Section with an existing index page
        """
        index_page = section.index_page
        if not index_page:
            return

        page_type = index_page.metadata.get("type", "")

        # Only enrich pages that need section context (blog, archive, etc.)
        if page_type in ("blog", "archive", "api-reference", "cli-reference", "tutorial"):
            # Add section context metadata if not already present
            if "_section" not in index_page.metadata:
                index_page.metadata["_section"] = section

            if "_posts" not in index_page.metadata:
                # Use content type strategy to filter and sort pages
                from bengal.content_types.registry import get_strategy

                content_type = page_type or "list"
                strategy = get_strategy(content_type)

                # Filter out index page
                filtered_pages = strategy.filter_display_pages(
                    section.regular_pages, section.index_page
                )

                # Sort according to content type
                sorted_pages = strategy.sort_pages(filtered_pages)

                index_page.metadata["_posts"] = sorted_pages

            if "_subsections" not in index_page.metadata:
                index_page.metadata["_subsections"] = section.subsections

            # Add pagination if appropriate and not already present
            if "_paginator" not in index_page.metadata and self._should_paginate(
                section, page_type
            ):
                from bengal.utils.pagination import Paginator

                paginator = Paginator(
                    items=section.pages,
                    per_page=self.site.config.get("pagination", {}).get("per_page", 10),
                )
                index_page.metadata["_paginator"] = paginator
                index_page.metadata["_page_num"] = 1

            logger.debug(
                "section_index_enriched",
                section_name=section.name,
                page_type=page_type,
                post_count=len(section.pages),
            )

    def validate_sections(self) -> list[str]:
        """
        Validate that all sections have valid index pages.

        Returns:
            List of validation error messages (empty if all valid)
        """
        errors = []
        for section in self.site.sections:
            errors.extend(self._validate_recursive(section))
        return errors

    def _validate_recursive(self, section: Section) -> list[str]:
        """
        Recursively validate a section and its subsections.

        Args:
            section: Section to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Skip root section
        if section.name == "root":
            # Still validate subsections
            for subsection in section.subsections:
                errors.extend(self._validate_recursive(subsection))
            return errors

        # Check if section has index page
        if not section.index_page:
            errors.append(
                f"Section '{section.name}' at {section.path} has no index page. "
                "This should not happen after finalization."
            )

        # Note: We don't validate output paths here because they're set later
        # in the render phase. This validation runs in Phase 2 (finalization),
        # while output paths are set in Phase 6 (rendering).

        # Recursively validate subsections
        for subsection in section.subsections:
            errors.extend(self._validate_recursive(subsection))

        return errors
