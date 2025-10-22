"""
CLI Error Handling Tests.

Tests CLI command error handling paths including:
- Generic exceptions
- Invalid inputs
- File system errors
- Edge cases
"""

from pathlib import Path

from click.testing import CliRunner

from clauxton.cli.main import cli


class TestConflictCommandErrorHandling:
    """Test conflict command error handling."""

    def test_conflict_detect_nonexistent_task(self, tmp_path: Path) -> None:
        """Test detect command with nonexistent task ID."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Try to detect conflicts for non-existent task
            result = runner.invoke(cli, ["conflict", "detect", "TASK-999"])

            assert result.exit_code == 1
            assert "error" in result.output.lower()

    def test_conflict_order_nonexistent_tasks(self, tmp_path: Path) -> None:
        """Test order command with nonexistent task IDs."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Try to order non-existent tasks
            result = runner.invoke(
                cli, ["conflict", "order", "TASK-998", "TASK-999"]
            )

            assert result.exit_code == 1
            assert "error" in result.output.lower()

    def test_conflict_check_empty_file_list(self, tmp_path: Path) -> None:
        """Test check command with no files provided."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Try to check with no files - should show usage error
            result = runner.invoke(cli, ["conflict", "check"])

            assert result.exit_code == 2  # Usage error
            assert "usage" in result.output.lower() or "required" in result.output.lower()


class TestTaskCommandErrorHandling:
    """Test task command error handling."""

    def test_task_get_nonexistent(self, tmp_path: Path) -> None:
        """Test getting nonexistent task."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            result = runner.invoke(cli, ["task", "get", "TASK-999"])

            assert result.exit_code == 1
            assert "error" in result.output.lower()

    def test_task_update_nonexistent(self, tmp_path: Path) -> None:
        """Test updating nonexistent task."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            result = runner.invoke(
                cli, ["task", "update", "TASK-999", "--status", "completed"]
            )

            assert result.exit_code == 1
            assert "error" in result.output.lower()

    def test_task_delete_nonexistent(self, tmp_path: Path) -> None:
        """Test deleting nonexistent task."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            result = runner.invoke(cli, ["task", "delete", "TASK-999"])

            assert result.exit_code == 1
            assert "error" in result.output.lower()

    def test_task_add_with_invalid_priority(self, tmp_path: Path) -> None:
        """Test adding task with invalid priority."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            result = runner.invoke(
                cli, ["task", "add", "--name", "Test", "--priority", "invalid"]
            )

            # Should fail with validation error
            assert result.exit_code != 0
            assert "error" in result.output.lower() or "invalid" in result.output.lower()


class TestKBCommandErrorHandling:
    """Test KB command error handling."""

    def test_kb_get_nonexistent(self, tmp_path: Path) -> None:
        """Test getting nonexistent KB entry."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            result = runner.invoke(cli, ["kb", "get", "KB-999"])

            assert result.exit_code == 1
            assert "error" in result.output.lower()

    def test_kb_update_nonexistent(self, tmp_path: Path) -> None:
        """Test updating nonexistent KB entry."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            result = runner.invoke(
                cli, ["kb", "update", "KB-999", "--title", "New Title"]
            )

            assert result.exit_code == 1
            assert "error" in result.output.lower()

    def test_kb_delete_nonexistent(self, tmp_path: Path) -> None:
        """Test deleting nonexistent KB entry."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            result = runner.invoke(cli, ["kb", "delete", "KB-999"])

            assert result.exit_code == 1
            assert "error" in result.output.lower()


class TestInitCommandErrorHandling:
    """Test init command error handling."""

    def test_init_twice_shows_warning(self, tmp_path: Path) -> None:
        """Test initializing twice shows appropriate message."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # First init
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Second init
            result = runner.invoke(cli, ["init"])

            # Should succeed but show it's already initialized
            assert "already" in result.output.lower() or "exists" in result.output.lower()


class TestCommandInputValidation:
    """Test command input validation."""

    def test_conflict_detect_requires_task_id(self, tmp_path: Path) -> None:
        """Test detect command requires task ID argument."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Try detect without task ID
            result = runner.invoke(cli, ["conflict", "detect"])

            assert result.exit_code == 2  # Usage error
            assert "usage" in result.output.lower() or "required" in result.output.lower()

    def test_conflict_order_requires_task_ids(self, tmp_path: Path) -> None:
        """Test order command requires at least one task ID."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Try order without task IDs
            result = runner.invoke(cli, ["conflict", "order"])

            assert result.exit_code == 2  # Usage error
            assert "usage" in result.output.lower() or "required" in result.output.lower()

    def test_task_add_requires_name(self, tmp_path: Path) -> None:
        """Test task add requires name."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Try add without name - should prompt or fail
            result = runner.invoke(cli, ["task", "add"], input="\n")

            # Either prompts for name or shows error
            assert result.exit_code != 0 or "name" in result.output.lower()


class TestUninitializedProjectErrors:
    """Test error handling when project not initialized."""

    def test_task_command_before_init_fails_gracefully(self, tmp_path: Path) -> None:
        """Test task commands fail gracefully before init."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Try task list without init
            result = runner.invoke(cli, ["task", "list"])

            # Should show error about initialization
            assert result.exit_code == 1
            assert "init" in result.output.lower() or "not found" in result.output.lower()

    def test_kb_command_before_init_fails_gracefully(self, tmp_path: Path) -> None:
        """Test KB commands fail gracefully before init."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Try KB list without init
            result = runner.invoke(cli, ["kb", "list"])

            # Should show error about initialization
            assert result.exit_code == 1
            assert "init" in result.output.lower() or "not found" in result.output.lower()

    def test_conflict_command_before_init_fails_gracefully(
        self, tmp_path: Path
    ) -> None:
        """Test conflict commands fail gracefully before init."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Try conflict detect without init
            result = runner.invoke(cli, ["conflict", "detect", "TASK-001"])

            # Should show error about initialization
            assert result.exit_code == 1
            assert "init" in result.output.lower() or "not found" in result.output.lower()
