"""
Unit tests for AssetDependencyMap.

Tests cover:
- Tracking and retrieving asset dependencies
- Bi-directional queries (pages->assets, assets->pages)
- Cache persistence (save/load)
- Invalidation and clearing
- Error handling and recovery
"""

import json
from pathlib import Path

import pytest

from bengal.cache.asset_dependency_map import (
    AssetDependencyEntry,
    AssetDependencyMap,
    AssetReference,
)


@pytest.fixture
def cache_dir(tmp_path):
    """Create temporary cache directory."""
    cache_path = tmp_path / ".bengal"
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


@pytest.fixture
def asset_map(cache_dir):
    """Create AssetDependencyMap with temporary path."""
    return AssetDependencyMap(cache_dir / "asset_deps.json")


class TestAssetReference:
    """Tests for AssetReference dataclass."""

    def test_create_reference(self):
        """Test creating an asset reference."""
        ref = AssetReference(
            url="/images/logo.png",
            type="image",
            source_page="content/index.md",
        )
        assert ref.url == "/images/logo.png"
        assert ref.type == "image"
        assert ref.source_page == "content/index.md"


class TestAssetDependencyEntry:
    """Tests for AssetDependencyEntry."""

    def test_create_entry(self):
        """Test creating a dependency entry."""
        assets = {"/css/style.css", "/images/logo.png"}
        entry = AssetDependencyEntry(
            assets=assets,
            tracked_at="2025-10-16T12:00:00",
            is_valid=True,
        )
        assert entry.assets == assets
        assert entry.is_valid is True

    def test_entry_to_dict(self):
        """Test converting entry to dictionary."""
        assets = {"/images/logo.png", "/css/style.css"}
        entry = AssetDependencyEntry(
            assets=assets,
            tracked_at="2025-10-16T12:00:00",
        )
        data = entry.to_dict()
        assert set(data["assets"]) == assets
        assert data["tracked_at"] == "2025-10-16T12:00:00"
        assert data["is_valid"] is True

    def test_entry_from_dict(self):
        """Test creating entry from dictionary."""
        data = {
            "assets": ["/images/logo.png", "/css/style.css"],
            "tracked_at": "2025-10-16T12:00:00",
            "is_valid": True,
        }
        entry = AssetDependencyEntry.from_dict(data)
        assert entry.assets == {"/images/logo.png", "/css/style.css"}
        assert entry.is_valid is True


class TestAssetDependencyMap:
    """Tests for AssetDependencyMap."""

    def test_create_empty_map(self, cache_dir):
        """Test creating new empty map."""
        asset_map = AssetDependencyMap(cache_dir / "deps.json")
        assert len(asset_map.pages) == 0

    def test_track_and_retrieve(self, asset_map):
        """Test tracking and retrieving assets for a page."""
        assets = {"/css/style.css", "/images/logo.png", "/fonts/inter.woff2"}
        asset_map.track_page_assets(Path("content/index.md"), assets)

        retrieved = asset_map.get_page_assets(Path("content/index.md"))
        assert retrieved == assets

    def test_has_assets(self, asset_map):
        """Test checking if page has tracked assets."""
        assets = {"/css/style.css"}
        asset_map.track_page_assets(Path("content/index.md"), assets)

        assert asset_map.has_assets(Path("content/index.md")) is True
        assert asset_map.has_assets(Path("content/missing.md")) is False

    def test_get_all_assets(self, asset_map):
        """Test getting all unique assets."""
        asset_map.track_page_assets(Path("page1.md"), {"/css/style.css", "/images/logo.png"})
        asset_map.track_page_assets(Path("page2.md"), {"/images/logo.png", "/js/app.js"})

        all_assets = asset_map.get_all_assets()
        assert all_assets == {"/css/style.css", "/images/logo.png", "/js/app.js"}

    def test_get_assets_for_pages(self, asset_map):
        """Test getting assets for multiple pages."""
        asset_map.track_page_assets(Path("p1.md"), {"/css/style.css"})
        asset_map.track_page_assets(Path("p2.md"), {"/images/logo.png"})
        asset_map.track_page_assets(Path("p3.md"), {"/js/app.js"})

        needed = asset_map.get_assets_for_pages([Path("p1.md"), Path("p3.md")])
        assert needed == {"/css/style.css", "/js/app.js"}

    def test_get_asset_pages(self, asset_map):
        """Test reverse lookup - find pages using an asset."""
        asset_map.track_page_assets(Path("p1.md"), {"/css/style.css", "/images/logo.png"})
        asset_map.track_page_assets(Path("p2.md"), {"/images/logo.png"})
        asset_map.track_page_assets(Path("p3.md"), {"/js/app.js"})

        pages = asset_map.get_asset_pages("/images/logo.png")
        assert pages == {"p1.md", "p2.md"}

    def test_invalidate_page(self, asset_map):
        """Test invalidating a page's assets."""
        assets = {"/css/style.css"}
        asset_map.track_page_assets(Path("content.md"), assets)

        assert asset_map.has_assets(Path("content.md")) is True

        asset_map.invalidate(Path("content.md"))

        assert asset_map.has_assets(Path("content.md")) is False

    def test_invalidate_all(self, asset_map):
        """Test invalidating all pages."""
        asset_map.track_page_assets(Path("p1.md"), {"/css/style.css"})
        asset_map.track_page_assets(Path("p2.md"), {"/js/app.js"})

        asset_map.invalidate_all()

        assert asset_map.has_assets(Path("p1.md")) is False
        assert asset_map.has_assets(Path("p2.md")) is False

    def test_clear_map(self, asset_map):
        """Test clearing all dependencies."""
        asset_map.track_page_assets(Path("p1.md"), {"/css/style.css"})
        asset_map.track_page_assets(Path("p2.md"), {"/js/app.js"})

        asset_map.clear()

        assert len(asset_map.pages) == 0

    def test_save_and_load(self, cache_dir):
        """Test saving and loading from disk."""
        # Create and populate
        map1 = AssetDependencyMap(cache_dir / "deps.json")
        map1.track_page_assets(
            Path("content/index.md"),
            {"/css/style.css", "/images/logo.png"},
        )
        map1.save_to_disk()

        # Load in new instance
        map2 = AssetDependencyMap(cache_dir / "deps.json")
        assets = map2.get_page_assets(Path("content/index.md"))

        assert assets == {"/css/style.css", "/images/logo.png"}

    def test_load_nonexistent_file(self, cache_dir):
        """Test loading when file doesn't exist."""
        asset_map = AssetDependencyMap(cache_dir / "nonexistent.json")
        assert len(asset_map.pages) == 0

    def test_load_corrupted_file(self, cache_dir):
        """Test loading corrupted JSON file."""
        cache_file = cache_dir / "deps.json"
        with open(cache_file, "w") as f:
            f.write("{ invalid json }")

        asset_map = AssetDependencyMap(cache_file)
        assert len(asset_map.pages) == 0

    def test_load_version_mismatch(self, cache_dir):
        """Test loading file with wrong version."""
        cache_file = cache_dir / "deps.json"
        data = {"version": 999, "pages": {}}
        with open(cache_file, "w") as f:
            json.dump(data, f)

        asset_map = AssetDependencyMap(cache_file)
        assert len(asset_map.pages) == 0

    def test_get_valid_entries(self, asset_map):
        """Test getting valid entries."""
        asset_map.track_page_assets(Path("p1.md"), {"/css/style.css"})
        asset_map.track_page_assets(Path("p2.md"), {"/js/app.js"})
        asset_map.track_page_assets(Path("p3.md"), {"/images/logo.png"})

        asset_map.invalidate(Path("p2.md"))

        valid = asset_map.get_valid_entries()
        assert len(valid) == 2
        assert "p1.md" in valid
        assert "p3.md" in valid

    def test_get_invalid_entries(self, asset_map):
        """Test getting invalid entries."""
        asset_map.track_page_assets(Path("p1.md"), {"/css/style.css"})
        asset_map.track_page_assets(Path("p2.md"), {"/js/app.js"})

        asset_map.invalidate(Path("p1.md"))

        invalid = asset_map.get_invalid_entries()
        assert len(invalid) == 1
        assert "p1.md" in invalid

    def test_stats(self, asset_map):
        """Test getting statistics."""
        asset_map.track_page_assets(Path("p1.md"), {"/css/style.css", "/images/logo.png"})
        asset_map.track_page_assets(Path("p2.md"), {"/images/logo.png", "/js/app.js"})
        asset_map.track_page_assets(Path("p3.md"), {"/fonts/inter.woff2"})

        asset_map.invalidate(Path("p1.md"))

        stats = asset_map.stats()
        assert stats["total_pages"] == 3
        assert stats["valid_pages"] == 2
        assert stats["invalid_pages"] == 1
        assert stats["unique_assets"] == 3  # logo, app, inter (css from invalidated p1 not counted)
        assert stats["avg_assets_per_page"] > 0
        assert stats["cache_size_bytes"] > 0

    def test_empty_asset_set(self, asset_map):
        """Test tracking page with no assets."""
        asset_map.track_page_assets(Path("blank.md"), set())

        assert asset_map.has_assets(Path("blank.md")) is True
        assets = asset_map.get_page_assets(Path("blank.md"))
        assert len(assets) == 0

    def test_update_existing_page(self, asset_map):
        """Test updating assets for existing page."""
        asset_map.track_page_assets(Path("page.md"), {"/css/old.css"})

        # Update with new assets
        asset_map.track_page_assets(Path("page.md"), {"/css/new.css", "/js/app.js"})

        assets = asset_map.get_page_assets(Path("page.md"))
        assert assets == {"/css/new.css", "/js/app.js"}

    def test_special_characters_in_paths(self, asset_map):
        """Test handling special characters in paths."""
        path = "content/blog/my-post-2025.md"
        assets = {"/images/header-2025.png", "/css/post-style.css"}
        asset_map.track_page_assets(Path(path), assets)

        retrieved = asset_map.get_page_assets(Path(path))
        assert retrieved == assets
