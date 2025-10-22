"""
Tests for clauxton logs CLI command.

Tests the logs command with various options and filters.
"""

from datetime import datetime
from pathlib import Path

from click.testing import CliRunner

from clauxton.cli.main import cli
from clauxton.utils.logger import ClauxtonLogger


def test_logs_command_shows_recent_logs(tmp_path: Path, monkeypatch) -> None:
    """Test that logs command displays recent logs."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create logs
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Added task TASK-001")
    logger.log("kb_search", "info", "Searched for 'API'")

    # Run command
    result = runner.invoke(cli, ["logs"])

    # Verify output
    assert result.exit_code == 0
    assert "Showing 2 log entries" in result.output
    assert "task_add" in result.output
    assert "kb_search" in result.output
    assert "Added task TASK-001" in result.output
    assert "Searched for 'API'" in result.output


def test_logs_command_with_limit(tmp_path: Path, monkeypatch) -> None:
    """Test logs command with --limit option."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create multiple logs
    logger = ClauxtonLogger(tmp_path)
    for i in range(10):
        logger.log("task_add", "info", f"Message {i}")

    # Run command with limit
    result = runner.invoke(cli, ["logs", "--limit", "3"])

    # Verify output
    assert result.exit_code == 0
    assert "Showing 3 log entries" in result.output


def test_logs_command_filters_by_operation(tmp_path: Path, monkeypatch) -> None:
    """Test logs command with --operation filter."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create mixed operations
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Task added")
    logger.log("kb_search", "info", "KB searched")
    logger.log("task_add", "info", "Another task")

    # Run command with operation filter
    result = runner.invoke(cli, ["logs", "--operation", "task_add"])

    # Verify output
    assert result.exit_code == 0
    assert "Showing 2 log entries" in result.output
    assert "task_add" in result.output
    assert "kb_search" not in result.output


def test_logs_command_filters_by_level(tmp_path: Path, monkeypatch) -> None:
    """Test logs command with --level filter."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create mixed levels
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Info message")
    logger.log("task_add", "error", "Error message")
    logger.log("task_add", "warning", "Warning message")

    # Run command with level filter
    result = runner.invoke(cli, ["logs", "--level", "error"])

    # Verify output
    assert result.exit_code == 0
    assert "Showing 1 log entries" in result.output
    assert "ERROR" in result.output
    assert "Error message" in result.output


def test_logs_command_with_days_option(tmp_path: Path, monkeypatch) -> None:
    """Test logs command with --days option."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create log
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Recent log")

    # Run command with days option
    result = runner.invoke(cli, ["logs", "--days", "1"])

    # Verify output
    assert result.exit_code == 0
    assert "Recent log" in result.output


def test_logs_command_with_date_option(tmp_path: Path, monkeypatch) -> None:
    """Test logs command with --date option."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create log
    logger = ClauxtonLogger(tmp_path)
    today = datetime.now().strftime("%Y-%m-%d")
    logger.log("task_add", "info", "Today's log")

    # Run command with specific date
    result = runner.invoke(cli, ["logs", "--date", today])

    # Verify output
    assert result.exit_code == 0
    assert "Today's log" in result.output


def test_logs_command_json_output(tmp_path: Path, monkeypatch) -> None:
    """Test logs command with --json option."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create log
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Test message", {"task_id": "TASK-001"})

    # Run command with JSON output
    result = runner.invoke(cli, ["logs", "--json"])

    # Verify JSON output
    assert result.exit_code == 0
    assert '"operation": "task_add"' in result.output
    assert '"message": "Test message"' in result.output
    assert '"task_id": "TASK-001"' in result.output


def test_logs_command_with_no_logs(tmp_path: Path, monkeypatch) -> None:
    """Test logs command when no logs exist."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Initialize but don't create logs
    _ = ClauxtonLogger(tmp_path)

    # Run command
    result = runner.invoke(cli, ["logs"])

    # Verify output
    assert result.exit_code == 0
    assert "No logs found" in result.output


def test_logs_command_shows_metadata(tmp_path: Path, monkeypatch) -> None:
    """Test that logs command displays metadata."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create log with metadata
    logger = ClauxtonLogger(tmp_path)
    logger.log(
        "task_add",
        "info",
        "Task added",
        {"task_id": "TASK-001", "priority": "high"},
    )

    # Run command
    result = runner.invoke(cli, ["logs"])

    # Verify metadata in output
    assert result.exit_code == 0
    assert "task_id: TASK-001" in result.output
    assert "priority: high" in result.output


def test_logs_command_color_codes_by_level(tmp_path: Path, monkeypatch) -> None:
    """Test that logs command uses color coding for log levels."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create logs with different levels
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Info message")
    logger.log("task_add", "error", "Error message")

    # Run command (color output depends on terminal)
    result = runner.invoke(cli, ["logs"])

    # Verify level indicators present
    assert result.exit_code == 0
    assert "INFO" in result.output
    assert "ERROR" in result.output


def test_logs_command_short_options(tmp_path: Path, monkeypatch) -> None:
    """Test logs command with short option flags."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create logs
    logger = ClauxtonLogger(tmp_path)
    for i in range(10):
        logger.log("task_add", "info", f"Message {i}")

    # Run command with short options
    result = runner.invoke(cli, ["logs", "-l", "5", "-d", "7"])

    # Verify output
    assert result.exit_code == 0
    assert "Showing 5 log entries" in result.output


def test_logs_command_combined_filters(tmp_path: Path, monkeypatch) -> None:
    """Test logs command with multiple filters."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create mixed logs
    logger = ClauxtonLogger(tmp_path)
    logger.log("task_add", "info", "Task info")
    logger.log("task_add", "error", "Task error")
    logger.log("kb_search", "info", "KB info")

    # Run command with multiple filters
    result = runner.invoke(
        cli, ["logs", "--operation", "task_add", "--level", "info"]
    )

    # Verify filtering
    assert result.exit_code == 0
    assert "Task info" in result.output
    assert "Task error" not in result.output
    assert "KB info" not in result.output
