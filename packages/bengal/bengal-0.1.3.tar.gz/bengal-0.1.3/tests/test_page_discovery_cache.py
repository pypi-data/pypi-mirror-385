"""
Unit tests for PageDiscoveryCache.

Tests cover:
- Loading and saving cache to disk
- Adding, retrieving, and validating metadata
- Cache invalidation and clearing
- Error handling and corruption recovery
"""

import json
from pathlib import Path

import pytest

from bengal.cache.page_discovery_cache import (
    PageDiscoveryCache,
    PageDiscoveryCacheEntry,
    PageMetadata,
)


@pytest.fixture
def cache_dir(tmp_path):
    """Create temporary cache directory."""
    cache_path = tmp_path / ".bengal"
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


@pytest.fixture
def cache(cache_dir):
    """Create PageDiscoveryCache with temporary path."""
    return PageDiscoveryCache(cache_dir / "page_metadata.json")


class TestPageMetadata:
    """Tests for PageMetadata dataclass."""

    def test_create_with_defaults(self):
        """Test creating PageMetadata with minimal arguments."""
        metadata = PageMetadata(source_path="content/index.md", title="Home")
        assert metadata.source_path == "content/index.md"
        assert metadata.title == "Home"
        assert metadata.date is None
        assert metadata.tags == []

    def test_create_with_all_fields(self):
        """Test creating PageMetadata with all fields."""
        metadata = PageMetadata(
            source_path="content/blog.md",
            title="Blog Post",
            date="2025-10-16",
            tags=["python", "testing"],
            section="blog",
            slug="blog-post",
            weight=1,
            lang="en",
            file_hash="abc123",
        )
        assert metadata.tags == ["python", "testing"]
        assert metadata.section == "blog"
        assert metadata.file_hash == "abc123"

    def test_to_dict(self):
        """Test converting PageMetadata to dictionary."""
        metadata = PageMetadata(
            source_path="content/index.md",
            title="Home",
            tags=["nav"],
        )
        data = metadata.to_dict()
        assert data["source_path"] == "content/index.md"
        assert data["title"] == "Home"
        assert data["tags"] == ["nav"]

    def test_from_dict(self):
        """Test creating PageMetadata from dictionary."""
        data = {
            "source_path": "content/index.md",
            "title": "Home",
            "tags": ["nav"],
            "date": None,
            "section": None,
            "slug": None,
            "weight": None,
            "lang": None,
            "file_hash": None,
        }
        metadata = PageMetadata.from_dict(data)
        assert metadata.source_path == "content/index.md"
        assert metadata.title == "Home"


class TestPageDiscoveryCacheEntry:
    """Tests for PageDiscoveryCacheEntry."""

    def test_create_entry(self):
        """Test creating cache entry."""
        metadata = PageMetadata(source_path="content/index.md", title="Home")
        entry = PageDiscoveryCacheEntry(
            metadata=metadata,
            cached_at="2025-10-16T12:00:00",
            is_valid=True,
        )
        assert entry.metadata == metadata
        assert entry.is_valid is True

    def test_entry_to_dict(self):
        """Test converting entry to dictionary."""
        metadata = PageMetadata(source_path="content/index.md", title="Home")
        entry = PageDiscoveryCacheEntry(
            metadata=metadata,
            cached_at="2025-10-16T12:00:00",
        )
        data = entry.to_dict()
        assert data["metadata"]["source_path"] == "content/index.md"
        assert data["cached_at"] == "2025-10-16T12:00:00"
        assert data["is_valid"] is True

    def test_entry_from_dict(self):
        """Test creating entry from dictionary."""
        data = {
            "metadata": {
                "source_path": "content/index.md",
                "title": "Home",
                "date": None,
                "tags": [],
                "section": None,
                "slug": None,
                "weight": None,
                "lang": None,
                "file_hash": None,
            },
            "cached_at": "2025-10-16T12:00:00",
            "is_valid": True,
        }
        entry = PageDiscoveryCacheEntry.from_dict(data)
        assert entry.metadata.source_path == "content/index.md"
        assert entry.is_valid is True


class TestPageDiscoveryCache:
    """Tests for PageDiscoveryCache."""

    def test_create_empty_cache(self, cache_dir):
        """Test creating new empty cache."""
        cache = PageDiscoveryCache(cache_dir / "cache.json")
        assert len(cache.pages) == 0
        assert cache.cache_path == cache_dir / "cache.json"

    def test_add_and_retrieve_metadata(self, cache):
        """Test adding and retrieving metadata."""
        metadata = PageMetadata(source_path="content/index.md", title="Home")
        cache.add_metadata(metadata)

        retrieved = cache.get_metadata(Path("content/index.md"))
        assert retrieved is not None
        assert retrieved.title == "Home"

    def test_has_metadata(self, cache):
        """Test checking if metadata exists."""
        metadata = PageMetadata(source_path="content/index.md", title="Home")
        cache.add_metadata(metadata)

        assert cache.has_metadata(Path("content/index.md")) is True
        assert cache.has_metadata(Path("content/missing.md")) is False

    def test_invalidate_entry(self, cache):
        """Test invalidating a cache entry."""
        metadata = PageMetadata(source_path="content/index.md", title="Home")
        cache.add_metadata(metadata)

        # Entry should be valid initially
        assert cache.has_metadata(Path("content/index.md")) is True

        # Invalidate entry
        cache.invalidate(Path("content/index.md"))

        # Entry should no longer be considered valid
        assert cache.has_metadata(Path("content/index.md")) is False

        # But metadata should still exist
        assert cache.get_metadata(Path("content/index.md")) is None

    def test_invalidate_all(self, cache):
        """Test invalidating all entries."""
        cache.add_metadata(PageMetadata(source_path="content/page1.md", title="P1"))
        cache.add_metadata(PageMetadata(source_path="content/page2.md", title="P2"))

        cache.invalidate_all()

        assert cache.has_metadata(Path("content/page1.md")) is False
        assert cache.has_metadata(Path("content/page2.md")) is False

    def test_clear_cache(self, cache):
        """Test clearing all cache entries."""
        cache.add_metadata(PageMetadata(source_path="content/page1.md", title="P1"))
        cache.add_metadata(PageMetadata(source_path="content/page2.md", title="P2"))

        cache.clear()

        assert len(cache.pages) == 0

    def test_save_and_load(self, cache_dir):
        """Test saving and loading cache from disk."""
        # Create and populate cache
        cache1 = PageDiscoveryCache(cache_dir / "cache.json")
        cache1.add_metadata(
            PageMetadata(
                source_path="content/index.md",
                title="Home",
                tags=["nav"],
            )
        )
        cache1.save_to_disk()

        # Load in new cache instance
        cache2 = PageDiscoveryCache(cache_dir / "cache.json")
        metadata = cache2.get_metadata(Path("content/index.md"))

        assert metadata is not None
        assert metadata.title == "Home"
        assert metadata.tags == ["nav"]

    def test_save_nonexistent_directory(self, tmp_path):
        """Test saving cache creates directories if needed."""
        cache_path = tmp_path / "nested" / "deep" / "cache.json"
        cache = PageDiscoveryCache(cache_path)
        cache.add_metadata(PageMetadata(source_path="test.md", title="Test"))
        cache.save_to_disk()

        assert cache_path.exists()
        assert cache_path.parent == tmp_path / "nested" / "deep"

    def test_load_corrupted_cache(self, cache_dir):
        """Test loading corrupted cache file."""
        cache_file = cache_dir / "cache.json"

        # Write invalid JSON
        with open(cache_file, "w") as f:
            f.write("{ invalid json }")

        # Should handle gracefully
        cache = PageDiscoveryCache(cache_file)
        assert len(cache.pages) == 0

    def test_load_version_mismatch(self, cache_dir):
        """Test loading cache with version mismatch."""
        cache_file = cache_dir / "cache.json"

        # Write cache with wrong version
        data = {
            "version": 999,  # Wrong version
            "pages": {},
        }
        with open(cache_file, "w") as f:
            json.dump(data, f)

        # Should handle gracefully by clearing
        cache = PageDiscoveryCache(cache_file)
        assert len(cache.pages) == 0

    def test_get_valid_entries(self, cache):
        """Test getting all valid entries."""
        cache.add_metadata(PageMetadata(source_path="p1.md", title="P1"))
        cache.add_metadata(PageMetadata(source_path="p2.md", title="P2"))
        cache.add_metadata(PageMetadata(source_path="p3.md", title="P3"))

        # Invalidate one
        cache.invalidate(Path("p2.md"))

        valid = cache.get_valid_entries()
        assert len(valid) == 2
        assert "p1.md" in valid
        assert "p3.md" in valid

    def test_get_invalid_entries(self, cache):
        """Test getting all invalid entries."""
        cache.add_metadata(PageMetadata(source_path="p1.md", title="P1"))
        cache.add_metadata(PageMetadata(source_path="p2.md", title="P2"))

        cache.invalidate(Path("p1.md"))

        invalid = cache.get_invalid_entries()
        assert len(invalid) == 1
        assert "p1.md" in invalid

    def test_validate_entry_with_hash(self, cache):
        """Test validating entry with file hash."""
        metadata = PageMetadata(
            source_path="content.md",
            title="Content",
            file_hash="abc123",
        )
        cache.add_metadata(metadata)

        # Same hash should be valid
        assert cache.validate_entry(Path("content.md"), "abc123") is True

        # Different hash should be invalid
        assert cache.validate_entry(Path("content.md"), "different") is False

    def test_validate_entry_no_hash(self, cache):
        """Test validating entry without stored hash."""
        metadata = PageMetadata(source_path="content.md", title="Content")
        cache.add_metadata(metadata)

        # Without hash, should return True (can't validate)
        assert cache.validate_entry(Path("content.md"), "anything") is True

    def test_stats(self, cache):
        """Test getting cache statistics."""
        cache.add_metadata(PageMetadata(source_path="p1.md", title="P1"))
        cache.add_metadata(PageMetadata(source_path="p2.md", title="P2"))
        cache.add_metadata(PageMetadata(source_path="p3.md", title="P3"))

        cache.invalidate(Path("p1.md"))

        stats = cache.stats()
        assert stats["total_entries"] == 3
        assert stats["valid_entries"] == 2
        assert stats["invalid_entries"] == 1
        assert stats["cache_size_bytes"] > 0

    def test_multiple_metadata_per_page(self, cache):
        """Test that updating metadata overwrites previous entry."""
        metadata1 = PageMetadata(source_path="content.md", title="Title 1")
        cache.add_metadata(metadata1)

        metadata2 = PageMetadata(source_path="content.md", title="Title 2")
        cache.add_metadata(metadata2)

        retrieved = cache.get_metadata(Path("content.md"))
        assert retrieved.title == "Title 2"  # Should be updated

    def test_cache_with_special_characters_in_path(self, cache):
        """Test cache handles paths with special characters."""
        path = "content/blog/my-post-2025.md"
        metadata = PageMetadata(source_path=path, title="Post")
        cache.add_metadata(metadata)

        retrieved = cache.get_metadata(Path(path))
        assert retrieved is not None
        assert retrieved.title == "Post"
