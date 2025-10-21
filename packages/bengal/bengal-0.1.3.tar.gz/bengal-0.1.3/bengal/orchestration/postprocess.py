"""
Post-processing orchestration for Bengal SSG.

Handles post-build tasks like sitemap generation, RSS feeds, and link validation.
"""


from __future__ import annotations

import concurrent.futures
from collections.abc import Callable
from threading import Lock
from typing import TYPE_CHECKING

from bengal.postprocess.output_formats import OutputFormatsGenerator
from bengal.postprocess.rss import RSSGenerator
from bengal.postprocess.sitemap import SitemapGenerator
from bengal.postprocess.special_pages import SpecialPagesGenerator
from bengal.utils.logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from bengal.core.site import Site

# Thread-safe output lock for parallel processing
_print_lock = Lock()


class PostprocessOrchestrator:
    """
    Handles post-processing tasks.

    Responsibilities:
        - Sitemap generation
        - RSS feed generation
        - Link validation
        - Parallel/sequential execution of tasks
    """

    def __init__(self, site: Site):
        """
        Initialize postprocess orchestrator.

        Args:
            site: Site instance with rendered pages and configuration
        """
        self.site = site

    def run(
        self,
        parallel: bool = True,
        progress_manager=None,
        build_context=None,
        incremental: bool = False,
    ) -> None:
        """
        Perform post-processing tasks (sitemap, RSS, output formats, link validation, etc.).

        Args:
            parallel: Whether to run tasks in parallel
            progress_manager: Live progress manager (optional)
            incremental: Whether this is an incremental build (can skip some tasks)
        """
        # Resolve from context if absent
        if (
            not progress_manager
            and build_context
            and getattr(build_context, "progress_manager", None)
        ):
            progress_manager = build_context.progress_manager
        reporter = None
        if build_context and getattr(build_context, "reporter", None):
            reporter = build_context.reporter

        if not progress_manager:
            if reporter:
                reporter.log("\n🔧 Post-processing:")
            else:
                print("\n🔧 Post-processing:")

        # Collect enabled tasks
        tasks = []

        # Always generate special pages (404, etc.) - important for deployment
        tasks.append(("special pages", self._generate_special_pages))

        # OPTIMIZATION: For incremental builds with small changes, skip some postprocessing
        # This is safe because:
        # - Sitemaps update on full builds (periodic refresh)
        # - RSS regenerated on content rebuild (not layout changes)
        # - Link validation happens in CI/full builds
        if not incremental:
            # Full build: run all tasks
            if self.site.config.get("generate_sitemap", True):
                tasks.append(("sitemap", self._generate_sitemap))

            if self.site.config.get("generate_rss", True):
                tasks.append(("rss", self._generate_rss))

            # Custom output formats (JSON, LLM text, etc.)
            output_formats_config = self.site.config.get("output_formats", {})
            if output_formats_config.get("enabled", True):
                tasks.append(("output formats", self._generate_output_formats))

            if self.site.config.get("validate_links", True):
                tasks.append(("link validation", self._validate_links))
        else:
            # Incremental: only regenerate if explicitly requested
            # (Most users don't need updated sitemaps/RSS for every content change)
            logger.info(
                "postprocessing_incremental",
                reason="skipping_sitemap_rss_validation_for_speed",
            )

        if not tasks:
            return

        # Run in parallel if enabled and multiple tasks
        # Threshold of 2 tasks (always parallel if multiple tasks since they're independent)
        if parallel and len(tasks) > 1:
            self._run_parallel(tasks, progress_manager, reporter)
        else:
            self._run_sequential(tasks, progress_manager, reporter)

    def _run_sequential(
        self, tasks: list[tuple[str, Callable]], progress_manager=None, reporter=None
    ) -> None:
        """
        Run post-processing tasks sequentially.

        Args:
            tasks: List of (task_name, task_function) tuples
            progress_manager: Live progress manager (optional)
        """
        for i, (task_name, task_fn) in enumerate(tasks):
            try:
                if progress_manager:
                    progress_manager.update_phase(
                        "postprocess", current=i + 1, current_item=task_name
                    )
                task_fn()
            except Exception as e:
                if progress_manager:
                    logger.error("postprocess_task_failed", task=task_name, error=str(e))
                else:
                    with _print_lock:
                        if reporter:
                            try:
                                reporter.log(f"  ✗ {task_name}: {e}")
                            except Exception:
                                print(f"  ✗ {task_name}: {e}")
                        else:
                            print(f"  ✗ {task_name}: {e}")

    def _run_parallel(
        self, tasks: list[tuple[str, Callable]], progress_manager=None, reporter=None
    ) -> None:
        """
        Run post-processing tasks in parallel.

        Args:
            tasks: List of (task_name, task_function) tuples
            progress_manager: Live progress manager (optional)
        """
        errors = []
        completed_count = 0
        lock = Lock()

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = {executor.submit(task_fn): name for name, task_fn in tasks}

            for future in concurrent.futures.as_completed(futures):
                task_name = futures[future]
                try:
                    future.result()
                    if progress_manager:
                        with lock:
                            completed_count += 1
                            progress_manager.update_phase(
                                "postprocess", current=completed_count, current_item=task_name
                            )
                except Exception as e:
                    errors.append((task_name, str(e)))
                    if progress_manager:
                        logger.error("postprocess_task_failed", task=task_name, error=str(e))

        # Report errors
        if errors and not progress_manager:
            with _print_lock:
                header = f"  ⚠️  {len(errors)} post-processing task(s) failed:"
                if reporter:
                    try:
                        reporter.log(header)
                        for task_name, error in errors:
                            reporter.log(f"    • {task_name}: {error}")
                    except Exception:
                        print(header)
                        for task_name, error in errors:
                            print(f"    • {task_name}: {error}")
                else:
                    print(header)
                    for task_name, error in errors:
                        print(f"    • {task_name}: {error}")

    def _generate_special_pages(self) -> None:
        """
        Generate special pages like 404 (extracted for parallel execution).

        Raises:
            Exception: If special page generation fails
        """
        generator = SpecialPagesGenerator(self.site)
        generator.generate()

    def _generate_sitemap(self) -> None:
        """
        Generate sitemap.xml (extracted for parallel execution).

        Raises:
            Exception: If sitemap generation fails
        """
        generator = SitemapGenerator(self.site)
        generator.generate()

    def _generate_rss(self) -> None:
        """
        Generate RSS feed (extracted for parallel execution).

        Raises:
            Exception: If RSS generation fails
        """
        generator = RSSGenerator(self.site)
        generator.generate()

    def _generate_output_formats(self) -> None:
        """
        Generate custom output formats like JSON, plain text (extracted for parallel execution).

        Raises:
            Exception: If output format generation fails
        """
        config = self.site.config.get("output_formats", {})
        generator = OutputFormatsGenerator(self.site, config)
        generator.generate()

    def _validate_links(self) -> None:
        """
        Validate internal links across all pages (extracted for parallel execution).

        Checks for broken internal links and logs warnings for any found.

        Raises:
            Exception: If link validation process fails
        """
        from bengal.rendering.link_validator import LinkValidator

        validator = LinkValidator()
        broken_links = validator.validate_site(self.site)
        if broken_links:
            logger.warning("broken_links_found", count=len(broken_links))
