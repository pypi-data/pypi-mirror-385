"""
Tests for MCP Server.

Tests cover:
- Server instantiation
- Tool registration
- Tool execution (KB: search, add, list, get, update, delete)
- Tool execution (Tasks: add, list, get, update, next, delete)
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from clauxton.mcp.server import (
    kb_add,
    kb_delete,
    kb_get,
    kb_list,
    kb_search,
    kb_update,
    mcp,
    task_add,
    task_delete,
    task_get,
    task_list,
    task_next,
    task_update,
)

# ============================================================================
# Server Instantiation Tests
# ============================================================================


def test_mcp_server_created() -> None:
    """Test that MCP server instance is created."""
    assert mcp is not None
    assert mcp.name == "Clauxton"


def test_mcp_server_has_tools() -> None:
    """Test that MCP server has tools registered."""
    # FastMCP should have registered our tools
    # We can verify by checking that our functions are decorated
    # Knowledge Base tools
    assert callable(kb_search)
    assert callable(kb_add)
    assert callable(kb_list)
    assert callable(kb_get)
    assert callable(kb_update)
    assert callable(kb_delete)
    # Task Management tools
    assert callable(task_add)
    assert callable(task_list)
    assert callable(task_get)
    assert callable(task_update)
    assert callable(task_next)
    assert callable(task_delete)


# ============================================================================
# Tool Execution Tests (with mocked KB)
# ============================================================================


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_search_tool(mock_kb_class: MagicMock, tmp_path: Path) -> None:
    """Test kb_search tool execution."""
    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb

    # Mock search results
    from datetime import datetime

    from clauxton.core.models import KnowledgeBaseEntry

    mock_entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Test Entry",
        category="architecture",
        content="Test content",
        tags=["test"],
        created_at=datetime(2025, 10, 19, 10, 0, 0),
        updated_at=datetime(2025, 10, 19, 10, 0, 0),
        author=None,
    )
    mock_kb.search.return_value = [mock_entry]

    # Execute tool
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        results = kb_search("test query")

    # Verify
    assert len(results) == 1
    assert results[0]["id"] == "KB-20251019-001"
    assert results[0]["title"] == "Test Entry"
    assert results[0]["category"] == "architecture"
    mock_kb.search.assert_called_once_with("test query", category=None, limit=10)


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_add_tool(mock_kb_class: MagicMock, tmp_path: Path) -> None:
    """Test kb_add tool execution."""
    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb
    mock_kb.list_all.return_value = []  # No existing entries
    mock_kb.add.return_value = "KB-20251019-001"

    # Execute tool
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        result = kb_add(
            title="Test Entry",
            category="architecture",
            content="Test content",
            tags=["test"],
        )

    # Verify
    assert result["id"].startswith("KB-")
    assert "Successfully added" in result["message"]
    mock_kb.add.assert_called_once()


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_list_tool(mock_kb_class: MagicMock, tmp_path: Path) -> None:
    """Test kb_list tool execution."""
    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb

    from datetime import datetime

    from clauxton.core.models import KnowledgeBaseEntry

    mock_entries = [
        KnowledgeBaseEntry(
            id=f"KB-20251019-{i:03d}",
            title=f"Entry {i}",
            category="architecture",
            content=f"Content {i}",
            tags=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            author=None,
        )
        for i in range(1, 4)
    ]
    mock_kb.list_all.return_value = mock_entries

    # Execute tool
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        results = kb_list()

    # Verify
    assert len(results) == 3
    assert all("id" in r for r in results)
    assert all("title" in r for r in results)


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_list_with_category_filter(
    mock_kb_class: MagicMock, tmp_path: Path
) -> None:
    """Test kb_list tool with category filter."""
    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb

    from datetime import datetime

    from clauxton.core.models import KnowledgeBaseEntry

    mock_entries = [
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="Arch Entry",
            category="architecture",
            content="Content",
            tags=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            author=None,
        ),
        KnowledgeBaseEntry(
            id="KB-20251019-002",
            title="Dec Entry",
            category="decision",
            content="Content",
            tags=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            author=None,
        ),
    ]
    mock_kb.list_all.return_value = mock_entries

    # Execute tool with filter
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        results = kb_list(category="architecture")

    # Verify - should only return architecture entries
    assert len(results) == 1
    assert results[0]["category"] == "architecture"


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_get_tool(mock_kb_class: MagicMock, tmp_path: Path) -> None:
    """Test kb_get tool execution."""
    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb

    from datetime import datetime

    from clauxton.core.models import KnowledgeBaseEntry

    mock_entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Test Entry",
        category="architecture",
        content="Test content",
        tags=["test"],
        created_at=datetime(2025, 10, 19, 10, 0, 0),
        updated_at=datetime(2025, 10, 19, 10, 0, 0),
        author=None,
        version=1,
    )
    mock_kb.get.return_value = mock_entry

    # Execute tool
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        result = kb_get("KB-20251019-001")

    # Verify
    assert result["id"] == "KB-20251019-001"
    assert result["title"] == "Test Entry"
    assert result["version"] == 1
    mock_kb.get.assert_called_once_with("KB-20251019-001")


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_update_tool(mock_kb_class: MagicMock, tmp_path: Path) -> None:
    """Test kb_update tool execution."""
    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb

    from datetime import datetime

    from clauxton.core.models import KnowledgeBaseEntry

    # Mock updated entry (version 2)
    updated_entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Updated Title",
        category="architecture",
        content="Updated content",
        tags=["updated"],
        created_at=datetime(2025, 10, 19, 10, 0, 0),
        updated_at=datetime(2025, 10, 19, 11, 0, 0),
        author=None,
        version=2,
    )
    mock_kb.update.return_value = updated_entry

    # Execute tool
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        result = kb_update(
            entry_id="KB-20251019-001",
            title="Updated Title",
            content="Updated content",
        )

    # Verify
    assert result["id"] == "KB-20251019-001"
    assert result["title"] == "Updated Title"
    assert result["content"] == "Updated content"
    assert result["version"] == 2
    assert "Successfully updated" in result["message"]
    mock_kb.update.assert_called_once()
    # Check that update was called with correct dict
    call_args = mock_kb.update.call_args
    assert call_args[0][0] == "KB-20251019-001"
    assert "title" in call_args[0][1]
    assert "content" in call_args[0][1]


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_update_no_fields(mock_kb_class: MagicMock, tmp_path: Path) -> None:
    """Test kb_update with no fields returns error."""
    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb

    # Execute tool with no update fields
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        result = kb_update(entry_id="KB-20251019-001")

    # Verify error response
    assert "error" in result
    assert "No fields to update" in result["error"]
    # Update should not have been called
    mock_kb.update.assert_not_called()


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_update_all_fields(mock_kb_class: MagicMock, tmp_path: Path) -> None:
    """Test kb_update with all fields."""
    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb

    from datetime import datetime

    from clauxton.core.models import KnowledgeBaseEntry

    updated_entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="New Title",
        category="decision",
        content="New content",
        tags=["new", "tags"],
        created_at=datetime(2025, 10, 19, 10, 0, 0),
        updated_at=datetime(2025, 10, 19, 11, 0, 0),
        author=None,
        version=2,
    )
    mock_kb.update.return_value = updated_entry

    # Execute tool with all fields
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        result = kb_update(
            entry_id="KB-20251019-001",
            title="New Title",
            content="New content",
            category="decision",
            tags=["new", "tags"],
        )

    # Verify
    assert result["title"] == "New Title"
    assert result["category"] == "decision"
    assert result["content"] == "New content"
    assert result["tags"] == ["new", "tags"]
    assert result["version"] == 2


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_delete_tool(mock_kb_class: MagicMock, tmp_path: Path) -> None:
    """Test kb_delete tool execution."""
    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb

    from datetime import datetime

    from clauxton.core.models import KnowledgeBaseEntry

    # Mock entry to be deleted
    entry_to_delete = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Entry to Delete",
        category="architecture",
        content="Content",
        tags=[],
        created_at=datetime(2025, 10, 19, 10, 0, 0),
        updated_at=datetime(2025, 10, 19, 10, 0, 0),
        author=None,
    )
    mock_kb.get.return_value = entry_to_delete
    mock_kb.delete.return_value = None

    # Execute tool
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        result = kb_delete(entry_id="KB-20251019-001")

    # Verify
    assert result["id"] == "KB-20251019-001"
    assert "Successfully deleted" in result["message"]
    assert "Entry to Delete" in result["message"]
    mock_kb.get.assert_called_once_with("KB-20251019-001")
    mock_kb.delete.assert_called_once_with("KB-20251019-001")
