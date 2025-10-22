"""
Tests for MCP Undo and Operation History Tools.

Tests cover:
- undo_last_operation tool
- get_recent_operations tool
- Operation history integration
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from clauxton.mcp.server import get_recent_operations, undo_last_operation

# ============================================================================
# Undo Tool Tests
# ============================================================================


@patch("clauxton.core.operation_history.OperationHistory")
def test_undo_last_operation_success(mock_history_class: MagicMock, tmp_path: Path) -> None:
    """Test undo_last_operation tool with successful undo."""
    # Setup mock
    mock_history = MagicMock()
    mock_history_class.return_value = mock_history

    # Mock undo result
    mock_history.undo_last_operation.return_value = {
        "status": "success",
        "operation_type": "task_import_yaml",
        "data": {
            "deleted_tasks": 5,
            "task_ids": ["TASK-001", "TASK-002", "TASK-003", "TASK-004", "TASK-005"],
        },
        "message": "Undone: Imported 5 tasks from YAML (deleted 5 tasks)",
    }

    # Execute
    result = undo_last_operation()

    # Verify
    assert result["status"] == "success"
    assert result["operation_type"] == "task_import_yaml"
    assert result["data"]["deleted_tasks"] == 5
    assert len(result["data"]["task_ids"]) == 5
    assert "Undone" in result["message"]

    # Verify mock calls
    mock_history.undo_last_operation.assert_called_once()


@patch("clauxton.core.operation_history.OperationHistory")
def test_undo_last_operation_no_history(mock_history_class: MagicMock, tmp_path: Path) -> None:
    """Test undo_last_operation tool when no operations to undo."""
    # Setup mock
    mock_history = MagicMock()
    mock_history_class.return_value = mock_history

    # Mock empty result
    mock_history.undo_last_operation.return_value = {
        "status": "error",
        "message": "No operations to undo",
    }

    # Execute
    result = undo_last_operation()

    # Verify
    assert result["status"] == "error"
    assert "No operations" in result["message"]


@patch("clauxton.core.operation_history.OperationHistory")
def test_undo_last_operation_kb_add(mock_history_class: MagicMock, tmp_path: Path) -> None:
    """Test undo_last_operation tool for KB add operation."""
    # Setup mock
    mock_history = MagicMock()
    mock_history_class.return_value = mock_history

    # Mock undo result for KB add
    mock_history.undo_last_operation.return_value = {
        "status": "success",
        "operation_type": "kb_add",
        "data": {
            "entry_id": "KB-20251022-001",
            "title": "Test Entry",
        },
        "message": "Undone: Added KB entry KB-20251022-001",
    }

    # Execute
    result = undo_last_operation()

    # Verify
    assert result["status"] == "success"
    assert result["operation_type"] == "kb_add"
    assert "KB-20251022-001" in result["data"]["entry_id"]


# ============================================================================
# Operation History Tool Tests
# ============================================================================


@patch("clauxton.core.operation_history.OperationHistory")
def test_get_recent_operations_success(mock_history_class: MagicMock, tmp_path: Path) -> None:
    """Test get_recent_operations tool with operations."""
    # Setup mock
    mock_history = MagicMock()
    mock_history_class.return_value = mock_history

    # Mock operations
    from datetime import datetime

    mock_op1 = MagicMock()
    mock_op1.operation_type = "kb_add"
    mock_op1.timestamp = datetime(2025, 10, 22, 10, 0, 0)
    mock_op1.description = "Added KB entry KB-20251022-001"

    mock_op2 = MagicMock()
    mock_op2.operation_type = "task_import_yaml"
    mock_op2.timestamp = datetime(2025, 10, 22, 9, 0, 0)
    mock_op2.description = "Imported 10 tasks from YAML"

    mock_history.list_operations.return_value = [mock_op1, mock_op2]

    # Execute
    result = get_recent_operations(limit=10)

    # Verify
    assert result["status"] == "success"
    assert result["count"] == 2
    assert len(result["operations"]) == 2

    # Check first operation
    assert result["operations"][0]["operation_type"] == "kb_add"
    assert result["operations"][0]["description"] == "Added KB entry KB-20251022-001"

    # Check second operation
    assert result["operations"][1]["operation_type"] == "task_import_yaml"
    assert result["operations"][1]["description"] == "Imported 10 tasks from YAML"

    # Verify mock calls
    mock_history.list_operations.assert_called_once_with(limit=10)


@patch("clauxton.core.operation_history.OperationHistory")
def test_get_recent_operations_empty(mock_history_class: MagicMock, tmp_path: Path) -> None:
    """Test get_recent_operations tool with no operations."""
    # Setup mock
    mock_history = MagicMock()
    mock_history_class.return_value = mock_history

    # Mock empty operations
    mock_history.list_operations.return_value = []

    # Execute
    result = get_recent_operations(limit=10)

    # Verify
    assert result["status"] == "success"
    assert result["count"] == 0
    assert result["operations"] == []


@patch("clauxton.core.operation_history.OperationHistory")
def test_get_recent_operations_custom_limit(mock_history_class: MagicMock, tmp_path: Path) -> None:
    """Test get_recent_operations tool with custom limit."""
    # Setup mock
    mock_history = MagicMock()
    mock_history_class.return_value = mock_history

    # Mock operations (5 operations)
    from datetime import datetime

    mock_ops = []
    for i in range(5):
        mock_op = MagicMock()
        mock_op.operation_type = "kb_add"
        mock_op.timestamp = datetime(2025, 10, 22, 10, i, 0)
        mock_op.description = f"Operation {i+1}"
        mock_ops.append(mock_op)

    mock_history.list_operations.return_value = mock_ops

    # Execute with limit=3
    result = get_recent_operations(limit=3)

    # Verify
    assert result["status"] == "success"
    assert result["count"] == 5  # All operations returned (limit applied by history manager)

    # Verify mock calls with correct limit
    mock_history.list_operations.assert_called_once_with(limit=3)


@patch("clauxton.core.operation_history.OperationHistory")
def test_get_recent_operations_various_types(mock_history_class: MagicMock, tmp_path: Path) -> None:
    """Test get_recent_operations tool with various operation types."""
    # Setup mock
    mock_history = MagicMock()
    mock_history_class.return_value = mock_history

    # Mock various operations
    from datetime import datetime

    operations = [
        ("kb_add", "Added KB entry"),
        ("kb_update", "Updated KB entry"),
        ("kb_delete", "Deleted KB entry"),
        ("task_add", "Added task"),
        ("task_import_yaml", "Imported tasks"),
        ("task_update", "Updated task"),
    ]

    mock_ops = []
    for i, (op_type, desc) in enumerate(operations):
        mock_op = MagicMock()
        mock_op.operation_type = op_type
        mock_op.timestamp = datetime(2025, 10, 22, 10, i, 0)
        mock_op.description = desc
        mock_ops.append(mock_op)

    mock_history.list_operations.return_value = mock_ops

    # Execute
    result = get_recent_operations(limit=20)

    # Verify
    assert result["status"] == "success"
    assert result["count"] == 6
    assert len(result["operations"]) == 6

    # Check that all operation types are present
    op_types = [op["operation_type"] for op in result["operations"]]
    assert "kb_add" in op_types
    assert "kb_update" in op_types
    assert "task_import_yaml" in op_types


# ============================================================================
# Integration Tests
# ============================================================================


@patch("clauxton.core.operation_history.OperationHistory")
def test_undo_and_history_integration(mock_history_class: MagicMock, tmp_path: Path) -> None:
    """Test undo and get_recent_operations integration."""
    # Setup mock
    mock_history = MagicMock()
    mock_history_class.return_value = mock_history

    from datetime import datetime

    # Mock initial operations (before undo)
    mock_op = MagicMock()
    mock_op.operation_type = "task_import_yaml"
    mock_op.timestamp = datetime(2025, 10, 22, 10, 0, 0)
    mock_op.description = "Imported 5 tasks from YAML"

    mock_history.list_operations.return_value = [mock_op]

    # Get operations before undo
    result_before = get_recent_operations(limit=10)
    assert result_before["count"] == 1
    assert result_before["operations"][0]["operation_type"] == "task_import_yaml"

    # Mock undo result
    mock_history.undo_last_operation.return_value = {
        "status": "success",
        "operation_type": "task_import_yaml",
        "data": {"deleted_tasks": 5},
        "message": "Undone: Imported 5 tasks from YAML",
    }

    # Perform undo
    undo_result = undo_last_operation()
    assert undo_result["status"] == "success"

    # Mock operations after undo (empty)
    mock_history.list_operations.return_value = []

    # Get operations after undo
    result_after = get_recent_operations(limit=10)
    assert result_after["count"] == 0
