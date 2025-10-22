"""
Tests for MCP logging tools.

Tests the get_recent_logs MCP tool integration.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from clauxton.mcp.server import get_recent_logs
from clauxton.utils.logger import ClauxtonLogger


def test_get_recent_logs_mcp_tool_returns_success(tmp_path: Path, monkeypatch) -> None:
    """Test that get_recent_logs MCP tool returns success status."""
    # Setup: Change working directory
    monkeypatch.chdir(tmp_path)

    # Create logger and write logs
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Test message 1", {"task_id": "TASK-001"})
    logger.log("kb_search", "info", "Test message 2", {"query": "test"})

    # Call MCP tool
    result = get_recent_logs(limit=10)

    # Verify response structure
    assert result["status"] == "success"
    assert "count" in result
    assert "logs" in result
    assert isinstance(result["logs"], list)


def test_get_recent_logs_mcp_tool_returns_correct_count(tmp_path: Path, monkeypatch) -> None:
    """Test that MCP tool returns correct log count."""
    monkeypatch.chdir(tmp_path)

    # Create logger and write logs
    logger = ClauxtonLogger(tmp_path)
    for i in range(5):
        logger.log("task_add", "info", f"Message {i}")

    # Call MCP tool
    result = get_recent_logs(limit=10)

    # Verify count
    assert result["count"] == 5
    assert len(result["logs"]) == 5


def test_get_recent_logs_mcp_tool_filters_by_operation(tmp_path: Path, monkeypatch) -> None:
    """Test MCP tool filtering by operation type."""
    monkeypatch.chdir(tmp_path)

    # Create logger and write mixed operations
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Task added")
    logger.log("kb_search", "info", "KB searched")
    logger.log("task_add", "info", "Another task added")

    # Call MCP tool with filter
    result = get_recent_logs(operation="task_add")

    # Verify filtering
    assert result["count"] == 2
    assert all(log["operation"] == "task_add" for log in result["logs"])


def test_get_recent_logs_mcp_tool_filters_by_level(tmp_path: Path, monkeypatch) -> None:
    """Test MCP tool filtering by log level."""
    monkeypatch.chdir(tmp_path)

    # Create logger and write mixed levels
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Info message")
    logger.log("task_add", "error", "Error message")
    logger.log("task_add", "warning", "Warning message")

    # Call MCP tool with filter
    result = get_recent_logs(level="error")

    # Verify filtering
    assert result["count"] == 1
    assert result["logs"][0]["level"] == "error"


def test_get_recent_logs_mcp_tool_respects_limit(tmp_path: Path, monkeypatch) -> None:
    """Test that MCP tool respects limit parameter."""
    monkeypatch.chdir(tmp_path)

    # Create logger and write many logs
    logger = ClauxtonLogger(tmp_path)
    for i in range(20):
        logger.log("task_add", "info", f"Message {i}")

    # Call MCP tool with limit
    result = get_recent_logs(limit=5)

    # Verify limit
    assert result["count"] == 5
    assert len(result["logs"]) == 5


def test_get_recent_logs_mcp_tool_respects_days(tmp_path: Path, monkeypatch) -> None:
    """Test that MCP tool respects days parameter."""
    monkeypatch.chdir(tmp_path)

    _ = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create logs for today
    today = datetime.now()
    log_file_today = logs_dir / f"{today.strftime('%Y-%m-%d')}.log"
    entry_today = {
        "timestamp": today.isoformat(),
        "operation": "task_add",
        "level": "info",
        "message": "Today's log",
        "metadata": {},
    }
    log_file_today.write_text(json.dumps(entry_today) + "\n")

    # Create logs for 10 days ago
    old_date = today - timedelta(days=10)
    log_file_old = logs_dir / f"{old_date.strftime('%Y-%m-%d')}.log"
    entry_old = {
        "timestamp": old_date.isoformat(),
        "operation": "task_add",
        "level": "info",
        "message": "Old log",
        "metadata": {},
    }
    log_file_old.write_text(json.dumps(entry_old) + "\n")

    # Call MCP tool with days=7 (should only get today's log)
    result = get_recent_logs(days=7)

    # Verify only recent logs returned
    assert result["count"] == 1
    assert result["logs"][0]["message"] == "Today's log"


def test_get_recent_logs_mcp_tool_returns_newest_first(tmp_path: Path, monkeypatch) -> None:
    """Test that MCP tool returns logs in newest-first order."""
    monkeypatch.chdir(tmp_path)

    # Create logger and write logs
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "First")
    logger.log("task_add", "info", "Second")
    logger.log("task_add", "info", "Third")

    # Call MCP tool
    result = get_recent_logs(limit=10)

    # Verify order (newest first)
    assert result["logs"][0]["message"] == "Third"
    assert result["logs"][1]["message"] == "Second"
    assert result["logs"][2]["message"] == "First"


def test_get_recent_logs_mcp_tool_includes_metadata(tmp_path: Path, monkeypatch) -> None:
    """Test that MCP tool includes metadata in response."""
    monkeypatch.chdir(tmp_path)

    # Create logger and write log with metadata
    logger = ClauxtonLogger(tmp_path)
    logger.log(
        "task_add",
        "info",
        "Task added",
        {"task_id": "TASK-001", "priority": "high", "estimated_hours": 3.5},
    )

    # Call MCP tool
    result = get_recent_logs(limit=1)

    # Verify metadata included
    log_entry = result["logs"][0]
    assert "metadata" in log_entry
    assert log_entry["metadata"]["task_id"] == "TASK-001"
    assert log_entry["metadata"]["priority"] == "high"
    assert log_entry["metadata"]["estimated_hours"] == 3.5


def test_get_recent_logs_mcp_tool_handles_no_logs(tmp_path: Path, monkeypatch) -> None:
    """Test MCP tool when no logs exist."""
    monkeypatch.chdir(tmp_path)

    # Initialize logger (but don't write any logs)
    _ = ClauxtonLogger(tmp_path)

    # Call MCP tool
    result = get_recent_logs()

    # Verify empty response
    assert result["status"] == "success"
    assert result["count"] == 0
    assert result["logs"] == []


def test_get_recent_logs_mcp_tool_combined_filters(tmp_path: Path, monkeypatch) -> None:
    """Test MCP tool with multiple filters combined."""
    monkeypatch.chdir(tmp_path)

    # Create logger and write various logs
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Task info")
    logger.log("task_add", "error", "Task error")
    logger.log("kb_search", "info", "KB info")
    logger.log("task_add", "info", "Another task info")

    # Call MCP tool with multiple filters
    result = get_recent_logs(operation="task_add", level="info", limit=5)

    # Verify both filters applied
    assert result["count"] == 2
    assert all(log["operation"] == "task_add" for log in result["logs"])
    assert all(log["level"] == "info" for log in result["logs"])
