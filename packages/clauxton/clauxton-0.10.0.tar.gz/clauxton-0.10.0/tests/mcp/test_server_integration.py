"""
Integration tests for MCP Server with real Knowledge Base.

Tests cover:
- Real KB operations (no mocking)
- End-to-end tool workflows
- Error handling
- Edge cases
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from clauxton.cli.main import cli
from clauxton.core.models import NotFoundError
from clauxton.mcp.server import kb_add, kb_get, kb_list, kb_search


@pytest.fixture
def initialized_project(tmp_path: Path) -> Path:
    """Create initialized Clauxton project."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        yield Path(td)


# ============================================================================
# Integration Tests (Real KB)
# ============================================================================


def test_kb_search_integration(initialized_project: Path) -> None:
    """Test kb_search with real Knowledge Base."""
    import os

    os.chdir(initialized_project)

    # Add entries first
    kb_add(
        title="FastAPI Framework",
        category="architecture",
        content="Use FastAPI for all backend APIs",
        tags=["backend", "api"],
    )
    kb_add(
        title="PostgreSQL Database",
        category="architecture",
        content="Use PostgreSQL 15+ for production",
        tags=["database", "postgresql"],
    )

    # Search
    results = kb_search(query="FastAPI")

    # Verify
    assert len(results) == 1
    assert results[0]["title"] == "FastAPI Framework"
    assert "backend" in results[0]["tags"]


def test_kb_add_integration(initialized_project: Path) -> None:
    """Test kb_add with real Knowledge Base."""
    import os

    os.chdir(initialized_project)

    # Add entry
    result = kb_add(
        title="Test Entry",
        category="decision",
        content="This is a test decision",
        tags=["test"],
    )

    # Verify
    assert "id" in result
    assert result["id"].startswith("KB-")
    assert "Successfully added" in result["message"]

    # Verify entry exists
    entry = kb_get(result["id"])
    assert entry["title"] == "Test Entry"
    assert entry["category"] == "decision"


def test_kb_list_integration(initialized_project: Path) -> None:
    """Test kb_list with real Knowledge Base."""
    import os

    os.chdir(initialized_project)

    # Add multiple entries
    kb_add("Entry 1", "architecture", "Content 1", ["tag1"])
    kb_add("Entry 2", "decision", "Content 2", ["tag2"])
    kb_add("Entry 3", "architecture", "Content 3", ["tag3"])

    # List all
    all_entries = kb_list()
    assert len(all_entries) == 3

    # List by category
    arch_entries = kb_list(category="architecture")
    assert len(arch_entries) == 2
    assert all(e["category"] == "architecture" for e in arch_entries)


def test_kb_get_integration(initialized_project: Path) -> None:
    """Test kb_get with real Knowledge Base."""
    import os

    os.chdir(initialized_project)

    # Add entry
    add_result = kb_add(
        title="Get Test",
        category="pattern",
        content="Test content",
        tags=["test"],
    )
    entry_id = add_result["id"]

    # Get entry
    entry = kb_get(entry_id)

    # Verify
    assert entry["id"] == entry_id
    assert entry["title"] == "Get Test"
    assert entry["category"] == "pattern"
    assert entry["version"] == 1


# ============================================================================
# Error Handling Tests
# ============================================================================


def test_kb_get_not_found(initialized_project: Path) -> None:
    """Test kb_get with non-existent entry ID."""
    import os

    os.chdir(initialized_project)

    # Attempt to get non-existent entry
    with pytest.raises(NotFoundError):
        kb_get("KB-20251019-999")


def test_kb_search_no_results(initialized_project: Path) -> None:
    """Test kb_search with no matches."""
    import os

    os.chdir(initialized_project)

    # Add entry
    kb_add("Test Entry", "architecture", "Content", [])

    # Search for non-existent term
    results = kb_search(query="NonExistentTerm")

    # Verify empty results
    assert len(results) == 0


def test_kb_list_empty(initialized_project: Path) -> None:
    """Test kb_list with empty Knowledge Base."""
    import os

    os.chdir(initialized_project)

    # List without adding anything
    results = kb_list()

    # Verify empty
    assert len(results) == 0


# ============================================================================
# Edge Case Tests
# ============================================================================


def test_kb_add_multiple_same_day(initialized_project: Path) -> None:
    """Test kb_add creates sequential IDs for same-day entries."""
    import os

    os.chdir(initialized_project)

    # Add multiple entries on same day
    result1 = kb_add("Entry 1", "architecture", "Content 1", [])
    result2 = kb_add("Entry 2", "architecture", "Content 2", [])
    result3 = kb_add("Entry 3", "architecture", "Content 3", [])

    # Extract sequence numbers
    id1 = result1["id"]
    id2 = result2["id"]
    id3 = result3["id"]

    # Verify same date prefix
    assert id1.split("-")[1] == id2.split("-")[1] == id3.split("-")[1]

    # Verify sequential numbers
    seq1 = int(id1.split("-")[2])
    seq2 = int(id2.split("-")[2])
    seq3 = int(id3.split("-")[2])

    assert seq2 == seq1 + 1
    assert seq3 == seq2 + 1


def test_kb_add_with_unicode(initialized_project: Path) -> None:
    """Test kb_add with Unicode content."""
    import os

    os.chdir(initialized_project)

    # Add entry with Japanese text
    result = kb_add(
        title="Unicode Test 日本語",
        category="convention",
        content="Content with emoji 🚀 and Japanese: これはテストです",
        tags=["unicode", "日本語"],
    )

    # Verify
    entry = kb_get(result["id"])
    assert "日本語" in entry["title"]
    assert "🚀" in entry["content"]
    assert "日本語" in entry["tags"]


def test_kb_search_with_special_characters(initialized_project: Path) -> None:
    """Test kb_search with special characters."""
    import os

    os.chdir(initialized_project)

    # Add entry with special characters
    kb_add(
        title="API Endpoint /api/v1/users",
        category="architecture",
        content="RESTful API endpoint for user management: /api/v1/users",
        tags=["api", "rest"],
    )

    # Search with special characters
    results = kb_search(query="/api/v1/users")

    # Verify
    assert len(results) == 1
    assert "/api/v1/users" in results[0]["content"]


def test_kb_list_category_filter_case_sensitive(initialized_project: Path) -> None:
    """Test kb_list category filter is case-sensitive."""
    import os

    os.chdir(initialized_project)

    # Add entry
    kb_add("Test", "architecture", "Content", [])

    # Filter with wrong case (should not match)
    results = kb_list(category="Architecture")

    # Verify no results (case-sensitive)
    assert len(results) == 0

    # Filter with correct case
    results = kb_list(category="architecture")
    assert len(results) == 1


def test_kb_add_max_length_title(initialized_project: Path) -> None:
    """Test kb_add with maximum length title (50 chars)."""
    import os

    os.chdir(initialized_project)

    # 50 characters exactly
    long_title = "A" * 50

    # Should succeed
    result = kb_add(
        title=long_title,
        category="pattern",
        content="Content",
        tags=[],
    )

    # Verify
    entry = kb_get(result["id"])
    assert len(entry["title"]) == 50
    assert entry["title"] == long_title


def test_kb_search_with_limit(initialized_project: Path) -> None:
    """Test kb_search respects limit parameter."""
    import os

    os.chdir(initialized_project)

    # Add 5 entries with same keyword
    for i in range(5):
        kb_add(f"API Entry {i}", "architecture", f"API content {i}", ["api"])

    # Search with limit
    results = kb_search(query="API", limit=3)

    # Verify limit is respected
    assert len(results) == 3


def test_kb_search_with_category_filter(initialized_project: Path) -> None:
    """Test kb_search with category filter."""
    import os

    os.chdir(initialized_project)

    # Add entries in different categories
    kb_add("API Design", "architecture", "API architecture", ["api"])
    kb_add("API Limit", "constraint", "API rate limit", ["api"])
    kb_add("Choose API", "decision", "API decision", ["api"])

    # Search with category filter
    results = kb_search(query="API", category="architecture")

    # Verify only architecture entries
    assert len(results) == 1
    assert results[0]["category"] == "architecture"
    assert results[0]["title"] == "API Design"


# ============================================================================
# Workflow Tests
# ============================================================================


def test_complete_workflow(initialized_project: Path) -> None:
    """Test complete MCP tool workflow."""
    import os

    os.chdir(initialized_project)

    # 1. Add entries
    kb_add("Entry 1", "architecture", "Content 1", ["tag1"])
    id2 = kb_add("Entry 2", "decision", "Content 2", ["tag2"])["id"]
    kb_add("Entry 3", "architecture", "Content 3", ["tag3"])

    # 2. List all
    all_entries = kb_list()
    assert len(all_entries) == 3

    # 3. List by category
    arch_entries = kb_list(category="architecture")
    assert len(arch_entries) == 2

    # 4. Search
    results = kb_search(query="Entry")
    assert len(results) == 3

    # 5. Get specific entry
    entry = kb_get(id2)
    assert entry["title"] == "Entry 2"
    assert entry["category"] == "decision"
