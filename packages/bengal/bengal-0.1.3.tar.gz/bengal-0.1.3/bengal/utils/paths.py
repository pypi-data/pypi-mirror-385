"""
Path utilities for Bengal SSG.

Provides consistent path management for temporary files, logs, and profiles.
"""


from __future__ import annotations

from pathlib import Path


class BengalPaths:
    """
    Manages Bengal's directory structure for generated files.

    Directory Structure:
    - .bengal-cache.json         → output_dir/.bengal-cache.json (build cache)
    - .bengal-cache/templates/   → output_dir/.bengal-cache/templates/ (Jinja2 bytecode)
    - .bengal-build.log          → source_dir/.bengal-build.log (build logs)
    - .bengal/profiles/          → source_dir/.bengal/profiles/ (performance profiles)

    This provides a clean separation between:
    1. Build outputs (public/) - deployable files
    2. Build metadata (public/.bengal-cache*) - cache files
    3. Development files (source/.bengal*) - logs, profiles
    """

    @staticmethod
    def get_profile_dir(source_dir: Path) -> Path:
        """
        Get the directory for storing performance profiles.

        Args:
            source_dir: Source directory (where content/ and bengal.toml live)

        Returns:
            Path to .bengal/profiles/ directory
        """
        profile_dir = source_dir / ".bengal" / "profiles"
        profile_dir.mkdir(parents=True, exist_ok=True)
        return profile_dir

    @staticmethod
    def get_log_dir(source_dir: Path) -> Path:
        """
        Get the directory for storing build logs.

        Args:
            source_dir: Source directory (where content/ and bengal.toml live)

        Returns:
            Path to .bengal/logs/ directory
        """
        log_dir = source_dir / ".bengal" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    @staticmethod
    def get_build_log_path(source_dir: Path, custom_path: Path | None = None) -> Path:
        """
        Get the path for the build log file.

        Args:
            source_dir: Source directory
            custom_path: Optional custom path specified by user

        Returns:
            Path to build log file
        """
        if custom_path:
            return custom_path

        # For backward compatibility, keep .bengal-build.log at source root
        # In future versions, could migrate to .bengal/logs/build.log
        return source_dir / ".bengal-build.log"

    @staticmethod
    def get_profile_path(
        source_dir: Path, custom_path: Path | None = None, filename: str = "build_profile.stats"
    ) -> Path:
        """
        Get the path for a performance profile file.

        Args:
            source_dir: Source directory
            custom_path: Optional custom path specified by user
            filename: Default filename for the profile

        Returns:
            Path to profile file
        """
        if custom_path:
            return custom_path

        profile_dir = BengalPaths.get_profile_dir(source_dir)
        return profile_dir / filename

    @staticmethod
    def get_cache_path(output_dir: Path) -> Path:
        """
        Get the path for the build cache file.

        Args:
            output_dir: Output directory (public/)

        Returns:
            Path to .bengal-cache.json
        """
        return output_dir / ".bengal-cache.json"

    @staticmethod
    def get_template_cache_dir(output_dir: Path) -> Path:
        """
        Get the directory for Jinja2 bytecode cache.

        Args:
            output_dir: Output directory (public/)

        Returns:
            Path to .bengal-cache/templates/
        """
        cache_dir = output_dir / ".bengal-cache" / "templates"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
