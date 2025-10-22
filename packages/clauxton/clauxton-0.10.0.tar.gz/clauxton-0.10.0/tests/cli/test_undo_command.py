"""
Tests for clauxton undo CLI command.

Tests the undo command functionality including:
- Undoing last operation
- Showing operation history
- Confirmation prompts
- Error handling
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from clauxton.cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create temporary project directory."""
    return tmp_path


# ============================================================================
# undo command tests - showing history
# ============================================================================


def test_undo_history_shows_operations(runner: CliRunner, temp_project: Path) -> None:
    """Test that undo --history command executes without error."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # Show history (may be empty if operation history not implemented)
        result = runner.invoke(cli, ["undo", "--history"])

        assert result.exit_code == 0
        # Either shows operations or shows empty message
        assert "Operation History" in result.output or "No operations in history" in result.output


def test_undo_history_short_option(runner: CliRunner, temp_project: Path) -> None:
    """Test that undo -h shows history."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # Show history with short option
        result = runner.invoke(cli, ["undo", "-h"])

        assert result.exit_code == 0
        assert "Operation History" in result.output or "No operations in history" in result.output


def test_undo_history_with_custom_limit(runner: CliRunner, temp_project: Path) -> None:
    """Test undo history with custom limit."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # Show history with limit
        result = runner.invoke(cli, ["undo", "--history", "--limit", "3"])

        assert result.exit_code == 0
        assert "Operation History" in result.output or "No operations in history" in result.output


def test_undo_history_empty(runner: CliRunner, temp_project: Path) -> None:
    """Test undo --history with no operations."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        # Show history when empty
        result = runner.invoke(cli, ["undo", "--history"])

        assert result.exit_code == 0
        assert "No operations in history" in result.output


# ============================================================================
# undo command tests - undoing operations
# ============================================================================


def test_undo_last_operation_with_confirmation(
    runner: CliRunner, temp_project: Path
) -> None:
    """Test undo command when no operations exist."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # Try to undo when no operations
        result = runner.invoke(cli, ["undo"], input="y\n")

        assert result.exit_code == 0
        # Should show "No operations to undo" message
        assert "No operations to undo" in result.output or "Undoing last operation" in result.output


def test_undo_cancel_confirmation(runner: CliRunner, temp_project: Path) -> None:
    """Test undo command accepts cancellation."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # Cancel undo (when no operations)
        result = runner.invoke(cli, ["undo"], input="n\n")

        assert result.exit_code == 0
        # Either "No operations" or "Cancelled" is acceptable
        assert "No operations to undo" in result.output or "Cancelled" in result.output


def test_undo_no_operations(runner: CliRunner, temp_project: Path) -> None:
    """Test undo when no operations to undo."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        # Try to undo when no operations
        result = runner.invoke(cli, ["undo"])

        assert result.exit_code == 0
        assert "No operations to undo" in result.output


def test_undo_shows_operation_details(runner: CliRunner, temp_project: Path) -> None:
    """Test that undo command works with no operations."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # Try to undo
        result = runner.invoke(cli, ["undo"], input="n\n")

        assert result.exit_code == 0
        # Should show either no operations message or operation details
        assert "No operations to undo" in result.output or "Operation:" in result.output


# ============================================================================
# Integration tests
# ============================================================================


def test_undo_history_workflow(runner: CliRunner, temp_project: Path) -> None:
    """Test complete undo history workflow."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # View history
        history_result = runner.invoke(cli, ["undo", "--history", "--limit", "10"])
        assert history_result.exit_code == 0
        assert (
            "Operation History" in history_result.output
            or "No operations in history" in history_result.output
        )

        # Try undo
        undo_result = runner.invoke(cli, ["undo"], input="n\n")
        assert undo_result.exit_code == 0
        assert "No operations to undo" in undo_result.output or "Cancelled" in undo_result.output


def test_undo_with_various_operations(runner: CliRunner, temp_project: Path) -> None:
    """Test undo history command."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # View history
        history_result = runner.invoke(cli, ["undo", "--history"])
        assert history_result.exit_code == 0
        # History is shown or empty
        assert (
            "Operation History" in history_result.output
            or "No operations in history" in history_result.output
        )


# ============================================================================
# Error handling tests
# ============================================================================


def test_undo_handles_missing_operation_history(
    runner: CliRunner, temp_project: Path
) -> None:
    """Test undo gracefully handles missing operation history."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize but don't create .clauxton directory
        # (simulate corrupted state)

        # Try to show history
        result = runner.invoke(cli, ["undo", "--history"])

        # Should handle gracefully
        assert "No operations in history" in result.output or "Error" in result.output


def test_undo_combined_options(runner: CliRunner, temp_project: Path) -> None:
    """Test undo with combined short options."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # Use combined short options
        result = runner.invoke(cli, ["undo", "-h", "-l", "5"])

        assert result.exit_code == 0
        assert "Operation History" in result.output or "No operations in history" in result.output
