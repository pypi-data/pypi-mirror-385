"""
Tests for Knowledge Base export to Markdown functionality.

Tests cover:
- All categories export
- Specific category export
- Markdown format validation
- ADR format validation
- Unicode handling
- Error cases (invalid directory, no entries)
"""

from datetime import datetime
from pathlib import Path

import pytest

from clauxton.core.knowledge_base import KnowledgeBase
from clauxton.core.models import KnowledgeBaseEntry, NotFoundError, ValidationError


@pytest.fixture
def kb_with_entries(tmp_path: Path) -> KnowledgeBase:
    """Create Knowledge Base with sample entries across all categories."""
    kb = KnowledgeBase(tmp_path)

    # Architecture entry
    kb.add(
        KnowledgeBaseEntry(
            id="KB-20251020-001",
            title="Use FastAPI Framework",
            category="architecture",
            content="All backend APIs use FastAPI for async support and performance.",
            tags=["backend", "api", "fastapi"],
            created_at=datetime(2025, 10, 20, 10, 0),
            updated_at=datetime(2025, 10, 20, 10, 0),
        )
    )

    # Decision entry
    kb.add(
        KnowledgeBaseEntry(
            id="KB-20251020-002",
            title="PostgreSQL for Production Database",
            category="decision",
            content=(
                "We decided to use PostgreSQL for production due to its "
                "reliability and ACID compliance."
            ),
            tags=["database", "postgresql"],
            created_at=datetime(2025, 10, 20, 11, 0),
            updated_at=datetime(2025, 10, 20, 11, 0),
        )
    )

    # Constraint entry
    kb.add(
        KnowledgeBaseEntry(
            id="KB-20251020-003",
            title="Python 3.11+ Only",
            category="constraint",
            content=(
                "Project requires Python 3.11 or higher for modern type hints "
                "and performance improvements."
            ),
            tags=["python", "version"],
            created_at=datetime(2025, 10, 20, 12, 0),
            updated_at=datetime(2025, 10, 20, 12, 0),
        )
    )

    # Pattern entry
    kb.add(
        KnowledgeBaseEntry(
            id="KB-20251020-004",
            title="Repository Pattern",
            category="pattern",
            content=(
                "Use repository pattern for data access to separate business "
                "logic from data access logic."
            ),
            tags=["design-pattern", "architecture"],
            created_at=datetime(2025, 10, 20, 13, 0),
            updated_at=datetime(2025, 10, 20, 13, 0),
        )
    )

    # Convention entry
    kb.add(
        KnowledgeBaseEntry(
            id="KB-20251020-005",
            title="Google-style Docstrings",
            category="convention",
            content="All Python functions must use Google-style docstrings for consistency.",
            tags=["documentation", "style"],
            created_at=datetime(2025, 10, 20, 14, 0),
            updated_at=datetime(2025, 10, 20, 14, 0),
        )
    )

    return kb


class TestExportAllCategories:
    """Tests for exporting all categories."""

    def test_export_all_categories_success(
        self, kb_with_entries: KnowledgeBase, tmp_path: Path
    ) -> None:
        """Test exporting all categories creates correct files."""
        output_dir = tmp_path / "docs" / "kb"

        stats = kb_with_entries.export_to_markdown(output_dir)

        assert stats["total_entries"] == 5
        assert stats["files_created"] == 5
        assert set(stats["categories"]) == {
            "architecture",
            "decision",
            "constraint",
            "pattern",
            "convention",
        }

        # Verify files exist
        assert (output_dir / "architecture.md").exists()
        assert (output_dir / "decision.md").exists()
        assert (output_dir / "constraint.md").exists()
        assert (output_dir / "pattern.md").exists()
        assert (output_dir / "convention.md").exists()

    def test_export_creates_output_directory(
        self, kb_with_entries: KnowledgeBase, tmp_path: Path
    ) -> None:
        """Test export creates output directory if it doesn't exist."""
        output_dir = tmp_path / "nested" / "deeply" / "nested" / "docs"
        assert not output_dir.exists()

        stats = kb_with_entries.export_to_markdown(output_dir)

        assert output_dir.exists()
        assert output_dir.is_dir()
        assert stats["files_created"] == 5


class TestExportSpecificCategory:
    """Tests for exporting specific category."""

    def test_export_specific_category(
        self, kb_with_entries: KnowledgeBase, tmp_path: Path
    ) -> None:
        """Test exporting only decision category."""
        output_dir = tmp_path / "docs" / "adr"

        stats = kb_with_entries.export_to_markdown(output_dir, category="decision")

        assert stats["total_entries"] == 1
        assert stats["files_created"] == 1
        assert stats["categories"] == ["decision"]

        # Only decision.md should exist
        assert (output_dir / "decision.md").exists()
        assert not (output_dir / "architecture.md").exists()
        assert not (output_dir / "constraint.md").exists()

    def test_export_architecture_category(
        self, kb_with_entries: KnowledgeBase, tmp_path: Path
    ) -> None:
        """Test exporting architecture category."""
        output_dir = tmp_path / "docs"

        stats = kb_with_entries.export_to_markdown(output_dir, category="architecture")

        assert stats["total_entries"] == 1
        assert stats["categories"] == ["architecture"]
        assert (output_dir / "architecture.md").exists()

    def test_export_nonexistent_category(
        self, kb_with_entries: KnowledgeBase, tmp_path: Path
    ) -> None:
        """Test error when category has no entries."""
        output_dir = tmp_path / "docs"

        # Add KB instance but filter to non-existent pattern matching
        # Actually, all categories have entries, so let's test with empty KB
        kb_empty = KnowledgeBase(tmp_path / "empty")

        with pytest.raises(NotFoundError, match="No entries found with category"):
            kb_empty.export_to_markdown(output_dir, category="decision")


class TestMarkdownFormatValidation:
    """Tests for Markdown format correctness."""

    def test_standard_markdown_format(
        self, kb_with_entries: KnowledgeBase, tmp_path: Path
    ) -> None:
        """Test standard markdown format for non-decision categories."""
        output_dir = tmp_path / "docs"
        kb_with_entries.export_to_markdown(output_dir, category="architecture")

        content = (output_dir / "architecture.md").read_text()

        # Verify header
        assert "# Architecture" in content
        assert "This document contains all architecture entries" in content

        # Verify entry structure
        assert "## Use FastAPI Framework" in content
        assert "**ID**: KB-20251020-001" in content
        assert "**Created**: 2025-10-20" in content
        assert "**Tags**: `backend`, `api`, `fastapi`" in content
        assert "All backend APIs use FastAPI" in content

        # Verify separators
        assert content.count("---") >= 2  # Header separator + entry separator

    def test_multiple_entries_in_category(
        self, kb_with_entries: KnowledgeBase, tmp_path: Path
    ) -> None:
        """Test multiple entries are properly separated."""
        kb = kb_with_entries

        # Add another architecture entry
        kb.add(
            KnowledgeBaseEntry(
                id="KB-20251020-006",
                title="Microservices Architecture",
                category="architecture",
                content="System uses microservices for scalability.",
                tags=["microservices"],
                created_at=datetime(2025, 10, 20, 15, 0),
                updated_at=datetime(2025, 10, 20, 15, 0),
            )
        )

        output_dir = tmp_path / "docs"
        kb.export_to_markdown(output_dir, category="architecture")

        content = (output_dir / "architecture.md").read_text()

        # Both entries should be present
        assert "## Use FastAPI Framework" in content
        assert "## Microservices Architecture" in content
        assert content.count("---") >= 3  # Header + 2 entries


class TestADRFormatValidation:
    """Tests for ADR (Architecture Decision Record) format for decisions."""

    def test_adr_format_structure(
        self, kb_with_entries: KnowledgeBase, tmp_path: Path
    ) -> None:
        """Test ADR format has correct structure."""
        output_dir = tmp_path / "docs"
        kb_with_entries.export_to_markdown(output_dir, category="decision")

        content = (output_dir / "decision.md").read_text()

        # Verify ADR-specific header
        assert "# Architecture Decision Records" in content
        assert "This document contains all architectural decisions" in content

        # Verify ADR entry structure
        assert "## PostgreSQL for Production Database" in content
        assert "**ID**: KB-20251020-002" in content
        assert "**Status**: Accepted" in content
        assert "**Date**: 2025-10-20" in content
        assert "**Version**: 1" in content

        # Verify ADR sections
        assert "### Context" in content
        assert "### Consequences" in content
        assert "_This decision has been implemented and accepted._" in content

    def test_adr_with_tags(
        self, kb_with_entries: KnowledgeBase, tmp_path: Path
    ) -> None:
        """Test ADR includes tags properly formatted."""
        output_dir = tmp_path / "docs"
        kb_with_entries.export_to_markdown(output_dir, category="decision")

        content = (output_dir / "decision.md").read_text()

        assert "**Tags**: `database`, `postgresql`" in content

    def test_adr_with_updated_entry(self, tmp_path: Path) -> None:
        """Test ADR shows last updated date for modified entries."""
        kb = KnowledgeBase(tmp_path)

        # Add decision
        kb.add(
            KnowledgeBaseEntry(
                id="KB-20251020-001",
                title="Use GraphQL",
                category="decision",
                content="We will use GraphQL for flexible API queries.",
                tags=["api", "graphql"],
                created_at=datetime(2025, 10, 20, 10, 0),
                updated_at=datetime(2025, 10, 20, 10, 0),
            )
        )

        # Update the entry
        kb.update(
            "KB-20251020-001",
            {
                "content": (
                    "We will use GraphQL for flexible API queries. "
                    "Updated to include subscriptions."
                )
            },
        )

        output_dir = tmp_path / "docs"
        kb.export_to_markdown(output_dir, category="decision")

        content = (output_dir / "decision.md").read_text()

        # Should have "Last Updated" field (value will be today's date)
        assert "**Last Updated**:" in content
        assert "**Version**: 2" in content  # Version should be incremented


class TestUnicodeHandling:
    """Tests for Unicode and special character handling."""

    def test_unicode_content(self, tmp_path: Path) -> None:
        """Test export handles Unicode characters correctly."""
        kb = KnowledgeBase(tmp_path)

        kb.add(
            KnowledgeBaseEntry(
                id="KB-20251020-001",
                title="日本語サポート (Japanese Support)",
                category="architecture",
                content=(
                    "システムは日本語、中文、한글などのUnicode文字をサポートします。\n"
                    "Emoji support: 🚀 ✅ 🎉"
                ),
                tags=["i18n", "unicode", "国際化"],
                created_at=datetime(2025, 10, 20, 10, 0),
                updated_at=datetime(2025, 10, 20, 10, 0),
            )
        )

        output_dir = tmp_path / "docs"
        stats = kb.export_to_markdown(output_dir)

        assert stats["total_entries"] == 1

        # Verify Unicode content
        content = (output_dir / "architecture.md").read_text(encoding="utf-8")

        assert "日本語サポート" in content
        assert "中文" in content
        assert "한글" in content
        assert "🚀 ✅ 🎉" in content
        assert "国際化" in content

    def test_special_markdown_characters(self, tmp_path: Path) -> None:
        """Test export handles special Markdown characters."""
        kb = KnowledgeBase(tmp_path)

        kb.add(
            KnowledgeBaseEntry(
                id="KB-20251020-001",
                title="Use `TypeScript` for **type safety**",
                category="constraint",
                content=(
                    "Code must use TypeScript with strict mode:\n"
                    "- No `any` types\n"
                    "- **Strict** null checks\n"
                    "- _Prefer_ interfaces over types"
                ),
                tags=["typescript", "type-safety"],
                created_at=datetime(2025, 10, 20, 10, 0),
                updated_at=datetime(2025, 10, 20, 10, 0),
            )
        )

        output_dir = tmp_path / "docs"
        kb.export_to_markdown(output_dir)

        content = (output_dir / "constraint.md").read_text()

        # Verify Markdown formatting is preserved
        assert "`TypeScript`" in content
        assert "**type safety**" in content
        assert "- No `any` types" in content


class TestErrorCases:
    """Tests for error handling."""

    def test_invalid_output_path(self, kb_with_entries: KnowledgeBase, tmp_path: Path) -> None:
        """Test error when output path is a file not a directory."""
        # Create a file at output path
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("test")

        with pytest.raises(ValidationError, match="not a directory"):
            kb_with_entries.export_to_markdown(file_path)

    def test_export_empty_kb(self, tmp_path: Path) -> None:
        """Test export with empty Knowledge Base."""
        kb = KnowledgeBase(tmp_path)
        output_dir = tmp_path / "docs"

        stats = kb.export_to_markdown(output_dir)

        # Should succeed but create no files
        assert stats["total_entries"] == 0
        assert stats["files_created"] == 0
        assert stats["categories"] == []
        assert output_dir.exists()  # Directory created

    def test_export_creates_directory_on_permission_error(
        self, kb_with_entries: KnowledgeBase, tmp_path: Path
    ) -> None:
        """Test handling when directory creation fails."""
        # This is hard to test without platform-specific permission handling
        # Just verify that the error is raised with proper message
        import os

        # Create a file where we want the directory
        blocked_path = tmp_path / "blocked.txt"
        blocked_path.write_text("test")

        # Make it read-only (platform-dependent)
        if os.name != "nt":  # Unix-like systems
            os.chmod(blocked_path, 0o444)

        # Try to create directory at file path - should fail
        with pytest.raises(ValidationError):
            kb_with_entries.export_to_markdown(blocked_path)


class TestEntrySorting:
    """Tests for entry sorting in exported files."""

    def test_entries_sorted_by_creation_date(self, tmp_path: Path) -> None:
        """Test entries are sorted by creation date in output."""
        kb = KnowledgeBase(tmp_path)

        # Add entries in non-chronological order
        kb.add(
            KnowledgeBaseEntry(
                id="KB-20251020-003",
                title="Third Entry",
                category="architecture",
                content="Added third",
                tags=[],
                created_at=datetime(2025, 10, 20, 15, 0),
                updated_at=datetime(2025, 10, 20, 15, 0),
            )
        )

        kb.add(
            KnowledgeBaseEntry(
                id="KB-20251020-001",
                title="First Entry",
                category="architecture",
                content="Added first",
                tags=[],
                created_at=datetime(2025, 10, 20, 10, 0),
                updated_at=datetime(2025, 10, 20, 10, 0),
            )
        )

        kb.add(
            KnowledgeBaseEntry(
                id="KB-20251020-002",
                title="Second Entry",
                category="architecture",
                content="Added second",
                tags=[],
                created_at=datetime(2025, 10, 20, 12, 0),
                updated_at=datetime(2025, 10, 20, 12, 0),
            )
        )

        output_dir = tmp_path / "docs"
        kb.export_to_markdown(output_dir)

        content = (output_dir / "architecture.md").read_text()

        # Find positions of entries
        first_pos = content.index("## First Entry")
        second_pos = content.index("## Second Entry")
        third_pos = content.index("## Third Entry")

        # Verify chronological order
        assert first_pos < second_pos < third_pos
