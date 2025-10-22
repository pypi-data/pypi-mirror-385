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

import pytest

from clauxton.mcp.server import (
    check_file_conflicts,
    detect_conflicts,
    kb_add,
    kb_delete,
    kb_get,
    kb_list,
    kb_search,
    kb_update,
    mcp,
    recommend_safe_order,
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


# ============================================================================
# Conflict Detection MCP Tool Tests
# ============================================================================


def test_detect_conflicts_tool_callable() -> None:
    """Test that detect_conflicts tool is callable."""
    assert callable(detect_conflicts)


def test_recommend_safe_order_tool_callable() -> None:
    """Test that recommend_safe_order tool is callable."""
    assert callable(recommend_safe_order)


def test_check_file_conflicts_tool_callable() -> None:
    """Test that check_file_conflicts tool is callable."""
    assert callable(check_file_conflicts)


def test_detect_conflicts_tool_input_validation(tmp_path: Path) -> None:
    """Test detect_conflicts tool with invalid task raises exception."""
    with patch("clauxton.mcp.server.TaskManager") as mock_tm:
        with patch("clauxton.mcp.server.ConflictDetector") as mock_cd:
            # Mock TaskManager to raise exception for invalid task
            mock_tm_instance = MagicMock()
            mock_tm.return_value = mock_tm_instance
            mock_tm_instance.get.side_effect = Exception("Task not found: TASK-999")

            mock_cd_instance = MagicMock()
            mock_cd.return_value = mock_cd_instance

            # Execute tool with invalid task_id - should raise exception
            with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
                with pytest.raises(Exception) as exc_info:
                    detect_conflicts(task_id="TASK-999")

                assert "Task not found" in str(exc_info.value)


def test_detect_conflicts_tool_output_format(tmp_path: Path) -> None:
    """Test detect_conflicts tool output matches expected schema."""
    from datetime import datetime

    from clauxton.core.models import ConflictReport

    with patch("clauxton.mcp.server.TaskManager") as mock_tm:
        with patch("clauxton.mcp.server.ConflictDetector") as mock_cd:
            # Mock TaskManager
            mock_tm_instance = MagicMock()
            mock_tm.return_value = mock_tm_instance
            mock_task = MagicMock()
            mock_task.id = "TASK-001"
            mock_task.name = "Test task"
            mock_tm_instance.get.return_value = mock_task

            # Mock ConflictDetector to return sample conflict
            mock_cd_instance = MagicMock()
            mock_cd.return_value = mock_cd_instance
            sample_conflict = ConflictReport(
                task_a_id="TASK-001",
                task_b_id="TASK-002",
                conflict_type="file_overlap",
                risk_level="medium",
                risk_score=0.5,
                overlapping_files=["file.py"],
                details="Test conflict",
                recommendation="Complete TASK-002 first",
                detected_at=datetime.now(),
            )
            mock_cd_instance.detect_conflicts.return_value = [sample_conflict]

            # Execute tool
            with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
                result = detect_conflicts(task_id="TASK-001")

            # Verify output structure
            assert "task_id" in result
            assert "conflicts" in result
            assert result["task_id"] == "TASK-001"
            assert len(result["conflicts"]) > 0
            # Verify conflict structure
            conflict = result["conflicts"][0]
            assert "task_b_id" in conflict
            assert "risk_level" in conflict
            assert "risk_score" in conflict
            assert "overlapping_files" in conflict


def test_recommend_safe_order_tool_handles_empty_list(tmp_path: Path) -> None:
    """Test recommend_safe_order tool with empty task list."""
    with patch("clauxton.mcp.server.TaskManager") as mock_tm:
        with patch("clauxton.mcp.server.ConflictDetector") as mock_cd:
            # Mock valid empty scenario
            mock_tm_instance = MagicMock()
            mock_tm.return_value = mock_tm_instance

            mock_cd_instance = MagicMock()
            mock_cd.return_value = mock_cd_instance
            mock_cd_instance.recommend_safe_order.return_value = []

            # Execute tool with empty list
            with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
                result = recommend_safe_order(task_ids=[])

            # Verify it handles empty list gracefully
            assert "task_count" in result
            assert result["task_count"] == 0


def test_recommend_safe_order_tool_output_format(tmp_path: Path) -> None:
    """Test recommend_safe_order tool output format."""
    with patch("clauxton.mcp.server.TaskManager") as mock_tm:
        with patch("clauxton.mcp.server.ConflictDetector") as mock_cd:
            # Mock TaskManager
            mock_tm_instance = MagicMock()
            mock_tm.return_value = mock_tm_instance

            # Mock ConflictDetector
            mock_cd_instance = MagicMock()
            mock_cd.return_value = mock_cd_instance
            mock_cd_instance.recommend_safe_order.return_value = [
                "TASK-001",
                "TASK-002",
                "TASK-003",
            ]

            # Execute tool
            with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
                result = recommend_safe_order(
                    task_ids=["TASK-001", "TASK-002", "TASK-003"]
                )

            # Verify output structure
            assert "task_ids" in result or "recommended_order" in result
            # Should contain ordered list
            if "recommended_order" in result:
                assert isinstance(result["recommended_order"], list)
                assert len(result["recommended_order"]) == 3


def test_check_file_conflicts_tool_output_format(tmp_path: Path) -> None:
    """Test check_file_conflicts tool output format."""
    with patch("clauxton.mcp.server.TaskManager") as mock_tm:
        with patch("clauxton.mcp.server.ConflictDetector") as mock_cd:
            # Mock TaskManager
            mock_tm_instance = MagicMock()
            mock_tm.return_value = mock_tm_instance

            # Mock ConflictDetector
            mock_cd_instance = MagicMock()
            mock_cd.return_value = mock_cd_instance
            mock_cd_instance.check_file_conflicts.return_value = ["TASK-001"]

            # Execute tool
            with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
                result = check_file_conflicts(files=["file.py"])

            # Verify output structure
            assert "files" in result or "conflicting_tasks" in result
            # Should contain list of conflicting tasks
            if "conflicting_tasks" in result:
                assert isinstance(result["conflicting_tasks"], list)


# ============================================================================
# task_import_yaml Tool Tests (v0.10.0)
# ============================================================================


def test_task_import_yaml_tool_callable(tmp_path: Path) -> None:
    """Test task_import_yaml tool is callable."""
    from clauxton.mcp.server import task_import_yaml

    assert callable(task_import_yaml)


def test_task_import_yaml_tool_basic(tmp_path: Path) -> None:
    """Test basic YAML import via MCP tool."""
    (tmp_path / ".clauxton").mkdir()

    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        from clauxton.mcp.server import task_import_yaml

        yaml_content = """
tasks:
  - name: "Task A"
    priority: high
  - name: "Task B"
    priority: medium
"""

        result = task_import_yaml(yaml_content=yaml_content)

        assert result["status"] == "success"
        assert result["imported"] == 2
        assert len(result["task_ids"]) == 2


def test_task_import_yaml_tool_dry_run(tmp_path: Path) -> None:
    """Test dry-run mode via MCP tool."""
    (tmp_path / ".clauxton").mkdir()

    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        from clauxton.mcp.server import task_import_yaml

        yaml_content = """
tasks:
  - name: "Task A"
"""

        result = task_import_yaml(yaml_content=yaml_content, dry_run=True)

        assert result["status"] == "success"
        assert result["imported"] == 0  # Nothing imported in dry-run
        assert len(result["task_ids"]) == 1  # But IDs are shown


def test_task_import_yaml_tool_validation_errors(tmp_path: Path) -> None:
    """Test validation errors via MCP tool."""
    (tmp_path / ".clauxton").mkdir()

    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        from clauxton.mcp.server import task_import_yaml

        yaml_content = """
tasks:
  - name: ""
"""

        result = task_import_yaml(yaml_content=yaml_content)

        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["errors"]) > 0


def test_task_import_yaml_tool_circular_dependency(tmp_path: Path) -> None:
    """Test circular dependency detection via MCP tool."""
    (tmp_path / ".clauxton").mkdir()

    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        from clauxton.mcp.server import task_import_yaml

        yaml_content = """
tasks:
  - id: TASK-001
    name: "Task A"
    depends_on:
      - TASK-002
  - id: TASK-002
    name: "Task B"
    depends_on:
      - TASK-001
"""

        result = task_import_yaml(yaml_content=yaml_content)

        assert result["status"] == "error"
        assert result["imported"] == 0
        assert "Circular dependency" in result["errors"][0]


def test_task_import_yaml_tool_skip_validation(tmp_path: Path) -> None:
    """Test skip_validation parameter via MCP tool."""
    (tmp_path / ".clauxton").mkdir()

    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        from clauxton.mcp.server import task_import_yaml

        yaml_content = """
tasks:
  - name: "Task A"
    depends_on:
      - TASK-999
"""

        # Without skip_validation, should fail
        result1 = task_import_yaml(yaml_content=yaml_content, skip_validation=False)
        assert result1["status"] == "error"

        # With skip_validation, should succeed
        result2 = task_import_yaml(yaml_content=yaml_content, skip_validation=True)
        assert result2["status"] == "success"
        assert result2["imported"] == 1


# ============================================================================
# KB Export Tool Tests
# ============================================================================


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_export_docs_success(mock_kb_class: MagicMock, tmp_path: Path) -> None:
    """Test kb_export_docs tool with successful export."""
    from clauxton.mcp.server import kb_export_docs

    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb
    mock_kb.export_to_markdown.return_value = {
        "total_entries": 10,
        "files_created": 3,
        "categories": ["architecture", "decision", "constraint"],
    }

    # Execute tool
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        result = kb_export_docs(output_dir="./docs/kb")

    # Verify
    assert result["status"] == "success"
    assert result["total_entries"] == 10
    assert result["files_created"] == 3
    assert result["categories"] == ["architecture", "decision", "constraint"]
    assert result["output_dir"] == "./docs/kb"
    assert len(result["files"]) == 3
    assert "Exported 10 entries" in result["message"]


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_export_docs_specific_category(
    mock_kb_class: MagicMock, tmp_path: Path
) -> None:
    """Test kb_export_docs tool with category filter."""
    from clauxton.mcp.server import kb_export_docs

    # Setup mock
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb
    mock_kb.export_to_markdown.return_value = {
        "total_entries": 3,
        "files_created": 1,
        "categories": ["decision"],
    }

    # Execute tool
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        result = kb_export_docs(output_dir="./docs/adr", category="decision")

    # Verify
    assert result["status"] == "success"
    assert result["total_entries"] == 3
    assert result["files_created"] == 1
    assert result["categories"] == ["decision"]
    assert "Exported 3 decision entries" in result["message"]


@patch("clauxton.mcp.server.KnowledgeBase")
def test_kb_export_docs_error_handling(mock_kb_class: MagicMock, tmp_path: Path) -> None:
    """Test kb_export_docs tool error handling."""
    from clauxton.mcp.server import kb_export_docs

    # Setup mock to raise exception
    mock_kb = MagicMock()
    mock_kb_class.return_value = mock_kb
    mock_kb.export_to_markdown.side_effect = Exception("Export failed")

    # Execute tool
    with patch("clauxton.mcp.server.Path.cwd", return_value=tmp_path):
        result = kb_export_docs(output_dir="./invalid/path")

    # Verify error response
    assert result["status"] == "error"
    assert "Export failed" in result["error"]
    assert "Failed to export KB" in result["message"]
