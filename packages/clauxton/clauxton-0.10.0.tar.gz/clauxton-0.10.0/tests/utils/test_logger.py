"""
Tests for logging utilities.

Tests the ClauxtonLogger class including:
- Log writing and reading
- Log rotation
- Filtering by operation, level, and date
- JSON Lines format
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from clauxton.utils.logger import ClauxtonLogger


def test_log_write_creates_log_file(tmp_path: Path) -> None:
    """Test that logging creates log file in correct directory."""
    logger = ClauxtonLogger(tmp_path)

    # Write log
    logger.log("task_add", "info", "Added task TASK-001", {"task_id": "TASK-001"})

    # Verify log file exists
    logs_dir = tmp_path / ".clauxton" / "logs"
    assert logs_dir.exists()
    assert logs_dir.stat().st_mode & 0o777 == 0o700  # Directory permissions

    # Verify today's log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"{today}.log"
    assert log_file.exists()
    assert log_file.stat().st_mode & 0o777 == 0o600  # File permissions


def test_log_json_lines_format(tmp_path: Path) -> None:
    """Test that logs are written in JSON Lines format."""
    logger = ClauxtonLogger(tmp_path)

    # Write multiple logs
    logger.log("task_add", "info", "Added task TASK-001", {"task_id": "TASK-001"})
    logger.log("kb_search", "debug", "Searched for 'API'", {"query": "API"})

    # Read log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / ".clauxton" / "logs" / f"{today}.log"

    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Verify JSON Lines format
    assert len(lines) == 2

    # Parse first line
    entry1 = json.loads(lines[0])
    assert entry1["operation"] == "task_add"
    assert entry1["level"] == "info"
    assert entry1["message"] == "Added task TASK-001"
    assert entry1["metadata"]["task_id"] == "TASK-001"
    assert "timestamp" in entry1

    # Parse second line
    entry2 = json.loads(lines[1])
    assert entry2["operation"] == "kb_search"
    assert entry2["level"] == "debug"


def test_get_recent_logs_returns_newest_first(tmp_path: Path) -> None:
    """Test that get_recent_logs returns newest entries first."""
    logger = ClauxtonLogger(tmp_path)

    # Write logs in sequence
    logger.log("task_add", "info", "Message 1")
    logger.log("task_add", "info", "Message 2")
    logger.log("task_add", "info", "Message 3")

    # Get recent logs
    logs = logger.get_recent_logs(limit=10)

    # Verify order (newest first)
    assert len(logs) == 3
    assert logs[0]["message"] == "Message 3"
    assert logs[1]["message"] == "Message 2"
    assert logs[2]["message"] == "Message 1"


def test_get_recent_logs_filters_by_operation(tmp_path: Path) -> None:
    """Test filtering logs by operation type."""
    logger = ClauxtonLogger(tmp_path)

    # Write mixed operations
    logger.log("task_add", "info", "Added task")
    logger.log("kb_search", "info", "Searched KB")
    logger.log("task_add", "info", "Added another task")
    logger.log("task_delete", "warning", "Deleted task")

    # Filter by operation
    logs = logger.get_recent_logs(operation="task_add")

    # Verify filtering
    assert len(logs) == 2
    assert all(log["operation"] == "task_add" for log in logs)


def test_get_recent_logs_filters_by_level(tmp_path: Path) -> None:
    """Test filtering logs by log level."""
    logger = ClauxtonLogger(tmp_path)

    # Write mixed levels
    logger.log("task_add", "info", "Info message")
    logger.log("task_add", "error", "Error message")
    logger.log("kb_search", "warning", "Warning message")
    logger.log("task_add", "debug", "Debug message")

    # Filter by level
    logs = logger.get_recent_logs(level="error")

    # Verify filtering
    assert len(logs) == 1
    assert logs[0]["level"] == "error"
    assert logs[0]["message"] == "Error message"


def test_get_recent_logs_respects_limit(tmp_path: Path) -> None:
    """Test that limit parameter works correctly."""
    logger = ClauxtonLogger(tmp_path)

    # Write 10 logs
    for i in range(10):
        logger.log("task_add", "info", f"Message {i}")

    # Get with limit
    logs = logger.get_recent_logs(limit=5)

    # Verify limit
    assert len(logs) == 5
    # Should get newest 5 (messages 5-9)
    assert logs[0]["message"] == "Message 9"
    assert logs[4]["message"] == "Message 5"


def test_get_logs_by_date(tmp_path: Path) -> None:
    """Test getting logs for specific date."""
    logger = ClauxtonLogger(tmp_path)

    # Write logs
    today = datetime.now().strftime("%Y-%m-%d")
    logger.log("task_add", "info", "Today's log")

    # Get logs by date
    logs = logger.get_logs_by_date(today)

    # Verify
    assert len(logs) == 1
    assert logs[0]["message"] == "Today's log"


def test_get_logs_by_date_nonexistent_date(tmp_path: Path) -> None:
    """Test getting logs for date with no logs."""
    logger = ClauxtonLogger(tmp_path)

    # Try to get logs from nonexistent date
    logs = logger.get_logs_by_date("2020-01-01")

    # Verify empty
    assert logs == []


def test_log_rotation_deletes_old_logs(tmp_path: Path) -> None:
    """Test that old logs are automatically deleted."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create old log file (40 days ago)
    old_date = datetime.now() - timedelta(days=40)
    old_log_file = logs_dir / f"{old_date.strftime('%Y-%m-%d')}.log"
    old_log_file.write_text('{"test": "old"}\n')

    # Create recent log file (5 days ago)
    recent_date = datetime.now() - timedelta(days=5)
    recent_log_file = logs_dir / f"{recent_date.strftime('%Y-%m-%d')}.log"
    recent_log_file.write_text('{"test": "recent"}\n')

    # Write new log (triggers rotation)
    logger.log("task_add", "info", "New log")

    # Verify old log deleted, recent log kept
    assert not old_log_file.exists()
    assert recent_log_file.exists()

    # Verify today's log exists
    today = datetime.now().strftime("%Y-%m-%d")
    today_log = logs_dir / f"{today}.log"
    assert today_log.exists()


def test_log_rotation_custom_retention(tmp_path: Path) -> None:
    """Test log rotation with custom retention period."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create log file (10 days ago)
    old_date = datetime.now() - timedelta(days=10)
    old_log_file = logs_dir / f"{old_date.strftime('%Y-%m-%d')}.log"
    old_log_file.write_text('{"test": "old"}\n')

    # Rotate with 7-day retention
    logger._rotate_logs(retention_days=7)

    # Verify old log deleted
    assert not old_log_file.exists()


def test_clear_logs_deletes_all(tmp_path: Path) -> None:
    """Test clearing all log files."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create multiple log files
    for i in range(5):
        date = datetime.now() - timedelta(days=i)
        log_file = logs_dir / f"{date.strftime('%Y-%m-%d')}.log"
        log_file.write_text('{"test": "data"}\n')

    # Clear logs
    count = logger.clear_logs()

    # Verify all deleted
    assert count == 5
    assert not list(logs_dir.glob("*.log"))


def test_log_with_empty_metadata(tmp_path: Path) -> None:
    """Test logging with no metadata."""
    logger = ClauxtonLogger(tmp_path)

    # Write log without metadata
    logger.log("task_add", "info", "Simple message")

    # Get log
    logs = logger.get_recent_logs(limit=1)

    # Verify metadata is empty dict
    assert logs[0]["metadata"] == {}


def test_log_handles_unicode(tmp_path: Path) -> None:
    """Test that logs handle Unicode characters correctly."""
    logger = ClauxtonLogger(tmp_path)

    # Write log with Unicode
    logger.log(
        "task_add",
        "info",
        "タスクを追加しました",
        {"name": "日本語のタスク"},
    )

    # Get log
    logs = logger.get_recent_logs(limit=1)

    # Verify Unicode preserved
    assert logs[0]["message"] == "タスクを追加しました"
    assert logs[0]["metadata"]["name"] == "日本語のタスク"


def test_log_malformed_json_lines_skipped(tmp_path: Path) -> None:
    """Test that malformed JSON lines are skipped gracefully."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create log file with malformed JSON
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"{today}.log"

    # Add timestamps for proper sorting
    time1 = datetime.now()
    time2 = time1 + timedelta(seconds=1)

    log_file.write_text(
        f'{{"valid": "json", "timestamp": "{time1.isoformat()}"}}\n'
        'invalid json line\n'
        f'{{"another": "valid", "timestamp": "{time2.isoformat()}"}}\n'
    )

    # Get logs (should skip malformed line)
    logs = logger.get_recent_logs(limit=10)

    # Verify only valid entries returned
    assert len(logs) == 2
    # Logs are returned newest first (by timestamp)
    assert logs[0].get("another") == "valid"
    assert logs[1].get("valid") == "json"


def test_get_recent_logs_across_multiple_days(tmp_path: Path) -> None:
    """Test getting logs from multiple days."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create logs for multiple days
    for i in range(3):
        date = datetime.now() - timedelta(days=i)
        log_file = logs_dir / f"{date.strftime('%Y-%m-%d')}.log"
        entry = {
            "timestamp": date.isoformat(),
            "operation": "task_add",
            "level": "info",
            "message": f"Day {i} message",
            "metadata": {},
        }
        log_file.write_text(json.dumps(entry) + "\n")

    # Get logs from last 3 days
    logs = logger.get_recent_logs(days=3)

    # Verify all days included
    assert len(logs) == 3


def test_log_level_case_insensitive(tmp_path: Path) -> None:
    """Test that log level filtering is case insensitive."""
    logger = ClauxtonLogger(tmp_path)

    # Write logs with different case levels
    logger.log("task_add", "INFO", "Message 1")
    logger.log("task_add", "Error", "Message 2")

    # Filter with lowercase
    logs = logger.get_recent_logs(level="info")

    # Verify filtering works (log() lowercases level)
    assert len(logs) == 1
    assert logs[0]["level"] == "info"


def test_get_recent_logs_combined_filters(tmp_path: Path) -> None:
    """Test using multiple filters together."""
    logger = ClauxtonLogger(tmp_path)

    # Write various logs
    logger.log("task_add", "info", "Task info")
    logger.log("task_add", "error", "Task error")
    logger.log("kb_search", "info", "KB info")
    logger.log("task_add", "info", "Another task info")

    # Filter by operation AND level
    logs = logger.get_recent_logs(operation="task_add", level="info")

    # Verify both filters applied
    assert len(logs) == 2
    assert all(log["operation"] == "task_add" for log in logs)
    assert all(log["level"] == "info" for log in logs)


def test_logs_directory_created_with_correct_permissions(tmp_path: Path) -> None:
    """Test that logs directory is created with secure permissions."""
    _ = ClauxtonLogger(tmp_path)

    logs_dir = tmp_path / ".clauxton" / "logs"

    # Verify directory exists with correct permissions
    assert logs_dir.exists()
    assert logs_dir.is_dir()
    assert logs_dir.stat().st_mode & 0o777 == 0o700


def test_log_file_permissions_set_correctly(tmp_path: Path) -> None:
    """Test that log files have secure permissions."""
    logger = ClauxtonLogger(tmp_path)

    # Write log
    logger.log("task_add", "info", "Test message")

    # Check file permissions
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / ".clauxton" / "logs" / f"{today}.log"

    assert log_file.stat().st_mode & 0o777 == 0o600


def test_get_logs_by_date_handles_empty_lines(tmp_path: Path) -> None:
    """Test that get_logs_by_date skips empty lines."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create log file with empty lines
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"{today}.log"
    log_file.write_text(
        '{"message": "first"}\n'
        '\n'
        '   \n'
        '{"message": "second"}\n'
        '\n'
    )

    # Get logs
    logs = logger.get_logs_by_date(today)

    # Verify empty lines skipped
    assert len(logs) == 2
    assert logs[0]["message"] == "first"
    assert logs[1]["message"] == "second"


def test_get_logs_by_date_handles_malformed_json(tmp_path: Path) -> None:
    """Test that get_logs_by_date gracefully handles malformed JSON."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create log file with malformed JSON
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"{today}.log"
    log_file.write_text(
        '{"valid": "entry"}\n'
        '{invalid json\n'
        '{"another": "valid"}\n'
    )

    # Get logs (should skip malformed line)
    logs = logger.get_logs_by_date(today)

    # Verify only valid entries returned
    assert len(logs) == 2
    assert logs[0]["valid"] == "entry"
    assert logs[1]["another"] == "valid"


def test_rotate_logs_handles_invalid_filename(tmp_path: Path) -> None:
    """Test that log rotation skips files with invalid date format."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create files with invalid names
    invalid_file = logs_dir / "invalid-name.log"
    invalid_file.write_text("test")

    # Create an old valid file
    old_date = datetime.now() - timedelta(days=40)
    old_file = logs_dir / f"{old_date.strftime('%Y-%m-%d')}.log"
    old_file.write_text("test")

    # Rotate logs (30-day retention)
    logger._rotate_logs(retention_days=30)

    # Verify invalid file not deleted (couldn't parse date, so skipped)
    assert invalid_file.exists()
    # Old valid file should be deleted
    assert not old_file.exists()


def test_rotate_logs_handles_file_deletion_errors(tmp_path: Path) -> None:
    """Test that log rotation continues when file deletion fails."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create old log files
    old_date1 = datetime.now() - timedelta(days=40)
    old_file1 = logs_dir / f"{old_date1.strftime('%Y-%m-%d')}.log"
    old_file1.write_text("test")

    old_date2 = datetime.now() - timedelta(days=50)
    old_file2 = logs_dir / f"{old_date2.strftime('%Y-%m-%d')}.log"
    old_file2.write_text("test")

    # Make one file read-only (deletion will fail)
    old_file1.chmod(0o444)

    # Rotate logs
    try:
        logger._rotate_logs(retention_days=30)

        # Should continue despite error
        # old_file1 might still exist (permission denied)
        # old_file2 should be deleted
        assert not old_file2.exists()
    finally:
        # Cleanup: restore permissions
        if old_file1.exists():
            old_file1.chmod(0o644)


def test_clear_logs_handles_deletion_errors(tmp_path: Path) -> None:
    """Test that clear_logs continues when some files can't be deleted."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create multiple log files
    log1 = logs_dir / "2025-01-01.log"
    log1.write_text("test")

    log2 = logs_dir / "2025-01-02.log"
    log2.write_text("test")

    # Make one file read-only
    log1.chmod(0o444)

    # Clear logs
    try:
        count = logger.clear_logs()

        # Should have deleted at least one file
        assert count >= 1
        # log2 should be deleted
        assert not log2.exists()
    finally:
        # Cleanup
        if log1.exists():
            log1.chmod(0o644)
            log1.unlink()


def test_get_recent_logs_handles_empty_lines(tmp_path: Path) -> None:
    """Test that get_recent_logs skips empty lines in log files."""
    logger = ClauxtonLogger(tmp_path)
    logs_dir = tmp_path / ".clauxton" / "logs"

    # Create log file with empty lines and whitespace
    today = datetime.now()
    log_file = logs_dir / f"{today.strftime('%Y-%m-%d')}.log"

    entry1 = {
        "timestamp": today.isoformat(),
        "operation": "task_add",
        "level": "info",
        "message": "Message 1",
        "metadata": {},
    }
    entry2 = {
        "timestamp": (today + timedelta(seconds=1)).isoformat(),
        "operation": "task_add",
        "level": "info",
        "message": "Message 2",
        "metadata": {},
    }

    log_file.write_text(
        json.dumps(entry1) + "\n" +
        "\n" +
        "   \n" +
        json.dumps(entry2) + "\n" +
        "\n"
    )

    # Get recent logs
    logs = logger.get_recent_logs(limit=10)

    # Should skip empty lines and return valid entries
    assert len(logs) == 2
    assert logs[0]["message"] == "Message 2"  # Newest first
    assert logs[1]["message"] == "Message 1"
