"""
CLI integration tests for task commands.

Tests the full CLI workflow for task management:
- clauxton task add
- clauxton task list
- clauxton task get
- clauxton task update
- clauxton task next
- clauxton task delete
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
def initialized_project(tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create and initialize a test project."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    monkeypatch.chdir(project_dir)

    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 0
    return project_dir


# ============================================================================
# task add Tests
# ============================================================================


def test_task_add_basic(runner: CliRunner, initialized_project: Path) -> None:
    """Test basic task creation via CLI."""
    result = runner.invoke(
        cli,
        ["task", "add", "--name", "Test task"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "✓ Added task: TASK-001" in result.output
    assert "Test task" in result.output


def test_task_add_with_priority(runner: CliRunner, initialized_project: Path) -> None:
    """Test task creation with priority."""
    result = runner.invoke(
        cli,
        ["task", "add", "--name", "High priority task", "--priority", "high"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "TASK-001" in result.output
    assert "high" in result.output


def test_task_add_with_dependencies(runner: CliRunner, initialized_project: Path) -> None:
    """Test task creation with dependencies."""
    # Add first task
    result1 = runner.invoke(
        cli,
        ["task", "add", "--name", "Task 1"],
        catch_exceptions=False,
    )
    assert result1.exit_code == 0

    # Add second task with dependency
    result2 = runner.invoke(
        cli,
        ["task", "add", "--name", "Task 2", "--depends-on", "TASK-001"],
        catch_exceptions=False,
    )
    assert result2.exit_code == 0
    assert "TASK-002" in result2.output
    assert "Depends on: TASK-001" in result2.output


def test_task_add_with_all_options(runner: CliRunner, initialized_project: Path) -> None:
    """Test task creation with all options."""
    result = runner.invoke(
        cli,
        [
            "task",
            "add",
            "--name",
            "Complex task",
            "--description",
            "Detailed description",
            "--priority",
            "critical",
            "--files",
            "src/main.py,tests/test_main.py",
            "--kb-refs",
            "KB-20251019-001",
            "--estimate",
            "4.5",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "TASK-001" in result.output


def test_task_add_without_init(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test task add fails without initialization."""
    project_dir = tmp_path / "uninit"
    project_dir.mkdir()
    monkeypatch.chdir(project_dir)

    result = runner.invoke(
        cli,
        ["task", "add", "--name", "Test"],
        catch_exceptions=False,
    )

    assert result.exit_code != 0
    assert ".clauxton/ not found" in result.output


# ============================================================================
# task list Tests
# ============================================================================


def test_task_list_empty(runner: CliRunner, initialized_project: Path) -> None:
    """Test listing tasks when none exist."""
    result = runner.invoke(cli, ["task", "list"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "No tasks found" in result.output


def test_task_list_all(runner: CliRunner, initialized_project: Path) -> None:
    """Test listing all tasks."""
    # Add some tasks
    runner.invoke(cli, ["task", "add", "--name", "Task 1"])
    runner.invoke(cli, ["task", "add", "--name", "Task 2"])
    runner.invoke(cli, ["task", "add", "--name", "Task 3"])

    result = runner.invoke(cli, ["task", "list"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Tasks (3)" in result.output
    assert "TASK-001" in result.output
    assert "TASK-002" in result.output
    assert "TASK-003" in result.output


def test_task_list_filter_by_status(runner: CliRunner, initialized_project: Path) -> None:
    """Test filtering tasks by status."""
    # Add tasks
    runner.invoke(cli, ["task", "add", "--name", "Task 1"])
    runner.invoke(cli, ["task", "add", "--name", "Task 2"])

    # Update one task status
    runner.invoke(cli, ["task", "update", "TASK-001", "--status", "in_progress"])

    # List pending tasks
    result = runner.invoke(
        cli, ["task", "list", "--status", "pending"], catch_exceptions=False
    )

    assert result.exit_code == 0
    assert "TASK-002" in result.output
    assert "TASK-001" not in result.output or "pending" not in result.output


def test_task_list_filter_by_priority(runner: CliRunner, initialized_project: Path) -> None:
    """Test filtering tasks by priority."""
    runner.invoke(cli, ["task", "add", "--name", "Task 1", "--priority", "high"])
    runner.invoke(cli, ["task", "add", "--name", "Task 2", "--priority", "low"])

    result = runner.invoke(
        cli, ["task", "list", "--priority", "high"], catch_exceptions=False
    )

    assert result.exit_code == 0
    assert "TASK-001" in result.output


# ============================================================================
# task get Tests
# ============================================================================


def test_task_get_existing(runner: CliRunner, initialized_project: Path) -> None:
    """Test getting an existing task."""
    runner.invoke(
        cli,
        [
            "task",
            "add",
            "--name",
            "Test task",
            "--description",
            "Description",
            "--priority",
            "high",
        ],
    )

    result = runner.invoke(cli, ["task", "get", "TASK-001"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "TASK-001" in result.output
    assert "Test task" in result.output
    assert "Description" in result.output
    assert "high" in result.output


def test_task_get_nonexistent(runner: CliRunner, initialized_project: Path) -> None:
    """Test getting non-existent task."""
    result = runner.invoke(cli, ["task", "get", "TASK-999"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "Error" in result.output


# ============================================================================
# task update Tests
# ============================================================================


def test_task_update_status(runner: CliRunner, initialized_project: Path) -> None:
    """Test updating task status."""
    runner.invoke(cli, ["task", "add", "--name", "Test task"])

    result = runner.invoke(
        cli,
        ["task", "update", "TASK-001", "--status", "in_progress"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "✓ Updated task: TASK-001" in result.output

    # Verify update
    get_result = runner.invoke(cli, ["task", "get", "TASK-001"])
    assert "in_progress" in get_result.output


def test_task_update_priority(runner: CliRunner, initialized_project: Path) -> None:
    """Test updating task priority."""
    runner.invoke(cli, ["task", "add", "--name", "Test task", "--priority", "low"])

    result = runner.invoke(
        cli,
        ["task", "update", "TASK-001", "--priority", "critical"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "✓ Updated task" in result.output


def test_task_update_multiple_fields(runner: CliRunner, initialized_project: Path) -> None:
    """Test updating multiple fields at once."""
    runner.invoke(cli, ["task", "add", "--name", "Test task"])

    result = runner.invoke(
        cli,
        [
            "task",
            "update",
            "TASK-001",
            "--status",
            "in_progress",
            "--priority",
            "high",
            "--name",
            "Updated name",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0


# ============================================================================
# task next Tests
# ============================================================================


def test_task_next_no_tasks(runner: CliRunner, initialized_project: Path) -> None:
    """Test task next when no tasks available."""
    result = runner.invoke(cli, ["task", "next"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "No tasks ready to work on" in result.output


def test_task_next_single_task(runner: CliRunner, initialized_project: Path) -> None:
    """Test task next with single task."""
    runner.invoke(cli, ["task", "add", "--name", "Test task"])

    result = runner.invoke(cli, ["task", "next"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Next Task to Work On" in result.output
    assert "TASK-001" in result.output


def test_task_next_respects_priority(runner: CliRunner, initialized_project: Path) -> None:
    """Test that task next returns highest priority task."""
    runner.invoke(cli, ["task", "add", "--name", "Low priority", "--priority", "low"])
    runner.invoke(cli, ["task", "add", "--name", "High priority", "--priority", "high"])

    result = runner.invoke(cli, ["task", "next"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "TASK-002" in result.output  # High priority task
    assert "high" in result.output


def test_task_next_respects_dependencies(runner: CliRunner, initialized_project: Path) -> None:
    """Test that task next respects dependencies."""
    runner.invoke(cli, ["task", "add", "--name", "Task 1", "--priority", "low"])
    runner.invoke(
        cli,
        ["task", "add", "--name", "Task 2", "--priority", "high", "--depends-on", "TASK-001"],
    )

    result = runner.invoke(cli, ["task", "next"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "TASK-001" in result.output  # Must do TASK-001 first


# ============================================================================
# task delete Tests
# ============================================================================


def test_task_delete_with_yes_flag(runner: CliRunner, initialized_project: Path) -> None:
    """Test deleting task with --yes flag."""
    runner.invoke(cli, ["task", "add", "--name", "Test task"])

    result = runner.invoke(
        cli, ["task", "delete", "TASK-001", "--yes"], catch_exceptions=False
    )

    assert result.exit_code == 0
    assert "✓ Deleted task: TASK-001" in result.output


def test_task_delete_nonexistent(runner: CliRunner, initialized_project: Path) -> None:
    """Test deleting non-existent task."""
    result = runner.invoke(
        cli, ["task", "delete", "TASK-999", "--yes"], catch_exceptions=False
    )

    assert result.exit_code != 0
    assert "Error" in result.output


# ============================================================================
# Optional Fields Tests
# ============================================================================


def test_task_with_kb_refs(runner: CliRunner, initialized_project: Path) -> None:
    """Test task with KB references."""
    result = runner.invoke(
        cli,
        [
            "task",
            "add",
            "--name",
            "Test with KB refs",
            "--kb-refs",
            "KB-20251019-001,KB-20251019-002",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "TASK-001" in result.output

    # Verify KB refs are stored
    get_result = runner.invoke(cli, ["task", "get", "TASK-001"])
    assert "KB-20251019-001" in get_result.output
    assert "KB-20251019-002" in get_result.output


def test_task_with_estimate(runner: CliRunner, initialized_project: Path) -> None:
    """Test task with estimated hours."""
    result = runner.invoke(
        cli,
        ["task", "add", "--name", "Task with estimate", "--estimate", "5.5"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    # Verify estimate is stored
    get_result = runner.invoke(cli, ["task", "get", "TASK-001"])
    assert "5.5" in get_result.output or "Estimated" in get_result.output


def test_task_timestamps(runner: CliRunner, initialized_project: Path) -> None:
    """Test task timestamps (started_at, completed_at)."""
    # Add task
    runner.invoke(cli, ["task", "add", "--name", "Test timestamps"])

    # Start task
    runner.invoke(cli, ["task", "update", "TASK-001", "--status", "in_progress"])
    get_result1 = runner.invoke(cli, ["task", "get", "TASK-001"])
    assert "Started:" in get_result1.output

    # Complete task
    runner.invoke(cli, ["task", "update", "TASK-001", "--status", "completed"])
    get_result2 = runner.invoke(cli, ["task", "get", "TASK-001"])
    assert "Completed:" in get_result2.output


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_task_workflow(runner: CliRunner, initialized_project: Path) -> None:
    """Test complete task management workflow."""
    # 1. Add tasks
    runner.invoke(cli, ["task", "add", "--name", "Setup database", "--priority", "high"])
    runner.invoke(
        cli,
        [
            "task",
            "add",
            "--name",
            "Add API endpoint",
            "--depends-on",
            "TASK-001",
            "--files",
            "src/api.py",
        ],
    )

    # 2. List tasks
    list_result = runner.invoke(cli, ["task", "list"])
    assert "Tasks (2)" in list_result.output

    # 3. Get next task (should be TASK-001)
    next_result = runner.invoke(cli, ["task", "next"])
    assert "TASK-001" in next_result.output

    # 4. Start working on TASK-001
    update_result = runner.invoke(
        cli, ["task", "update", "TASK-001", "--status", "in_progress"]
    )
    assert update_result.exit_code == 0

    # 5. Complete TASK-001
    complete_result = runner.invoke(
        cli, ["task", "update", "TASK-001", "--status", "completed"]
    )
    assert complete_result.exit_code == 0

    # 6. Get next task (now TASK-002 is unblocked)
    next_result2 = runner.invoke(cli, ["task", "next"])
    assert "TASK-002" in next_result2.output

    # 7. Get task details
    get_result = runner.invoke(cli, ["task", "get", "TASK-002"])
    assert "src/api.py" in get_result.output

    # 8. Complete TASK-002
    runner.invoke(cli, ["task", "update", "TASK-002", "--status", "completed"])

    # 9. No more tasks
    next_result3 = runner.invoke(cli, ["task", "next"])
    assert "No tasks ready to work on" in next_result3.output

    # 10. List completed tasks
    completed_result = runner.invoke(cli, ["task", "list", "--status", "completed"])
    assert "Tasks (2)" in completed_result.output


# ============================================================================
# Error Handling Tests
# ============================================================================


def test_task_add_exception_handling(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test exception handling in task add command."""
    from unittest.mock import patch

    from clauxton.core.task_manager import TaskManager

    project_dir = tmp_path / "project"
    project_dir.mkdir()
    monkeypatch.chdir(project_dir)

    # Initialize project
    runner.invoke(cli, ["init"])

    # Mock TaskManager.add to raise exception
    with patch.object(TaskManager, "add", side_effect=Exception("Simulated error")):
        result = runner.invoke(
            cli,
            ["task", "add", "--name", "Test task"],
            catch_exceptions=False,
        )

        assert result.exit_code != 0
        assert "Error: Simulated error" in result.output


def test_task_get_exception_handling(
    runner: CliRunner, initialized_project: Path
) -> None:
    """Test exception handling in task get command."""
    from unittest.mock import patch

    from clauxton.core.task_manager import TaskManager

    # Mock TaskManager.get to raise exception
    with patch.object(TaskManager, "get", side_effect=Exception("Task data corrupted")):
        result = runner.invoke(cli, ["task", "get", "TASK-001"], catch_exceptions=False)

        assert result.exit_code != 0
        assert "Error: Task data corrupted" in result.output


def test_task_update_exception_handling(
    runner: CliRunner, initialized_project: Path
) -> None:
    """Test exception handling in task update command."""
    from unittest.mock import patch

    from clauxton.core.task_manager import TaskManager

    # Add a task first
    runner.invoke(cli, ["task", "add", "--name", "Test task"])

    # Mock TaskManager.update to raise exception
    with patch.object(
        TaskManager, "update", side_effect=Exception("Update failed")
    ):
        result = runner.invoke(
            cli,
            ["task", "update", "TASK-001", "--status", "in_progress"],
            catch_exceptions=False,
        )

        assert result.exit_code != 0
        assert "Error: Update failed" in result.output


def test_task_update_no_fields(runner: CliRunner, initialized_project: Path) -> None:
    """Test task update with no fields specified."""
    # Add a task first
    runner.invoke(cli, ["task", "add", "--name", "Test task"])

    # Try to update without any fields
    result = runner.invoke(
        cli, ["task", "update", "TASK-001"], catch_exceptions=False
    )

    assert result.exit_code == 0
    assert "No fields to update" in result.output


def test_task_delete_exception_handling(
    runner: CliRunner, initialized_project: Path
) -> None:
    """Test exception handling in task delete command."""
    from unittest.mock import patch

    from clauxton.core.task_manager import TaskManager

    # Add a task first
    runner.invoke(cli, ["task", "add", "--name", "Test task"])

    # Mock TaskManager.delete to raise exception
    with patch.object(
        TaskManager, "delete", side_effect=Exception("Cannot delete task")
    ):
        result = runner.invoke(
            cli, ["task", "delete", "TASK-001", "--yes"], catch_exceptions=False
        )

        assert result.exit_code != 0
        assert "Error: Cannot delete task" in result.output


def test_task_delete_with_confirmation(runner: CliRunner, initialized_project: Path) -> None:
    """Test task delete with interactive confirmation."""
    # Add a task first
    runner.invoke(cli, ["task", "add", "--name", "Test task"])

    # Test cancellation
    result = runner.invoke(
        cli, ["task", "delete", "TASK-001"], input="n\n", catch_exceptions=False
    )

    assert result.exit_code == 0
    assert "Cancelled" in result.output

    # Verify task still exists
    get_result = runner.invoke(cli, ["task", "get", "TASK-001"])
    assert "TASK-001" in get_result.output


def test_task_with_actual_hours(runner: CliRunner, initialized_project: Path) -> None:
    """Test task display with actual_hours field."""
    from clauxton.core.task_manager import TaskManager

    # Add a task
    runner.invoke(cli, ["task", "add", "--name", "Test task"])

    # Manually set actual_hours in the task
    tm = TaskManager(Path.cwd())
    tm.get("TASK-001")  # Verify task exists
    tm.update("TASK-001", {"actual_hours": 3.5})

    # Get task and verify actual_hours is displayed
    result = runner.invoke(cli, ["task", "get", "TASK-001"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "3.5" in result.output or "Actual" in result.output


def test_task_update_description(runner: CliRunner, initialized_project: Path) -> None:
    """Test updating task description."""
    # Add a task
    runner.invoke(cli, ["task", "add", "--name", "Test task"])

    # Update description
    result = runner.invoke(
        cli,
        ["task", "update", "TASK-001", "--description", "Updated description"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Updated task" in result.output

    # Verify description was updated
    get_result = runner.invoke(cli, ["task", "get", "TASK-001"])
    assert "Updated description" in get_result.output


def test_task_next_with_description_and_estimate(
    runner: CliRunner, initialized_project: Path
) -> None:
    """Test task next displays description and estimated hours."""
    # Add task with description and estimate
    runner.invoke(
        cli,
        [
            "task",
            "add",
            "--name",
            "Complex task",
            "--description",
            "This is a detailed description",
            "--estimate",
            "8.0",
        ],
    )

    # Get next task
    result = runner.invoke(cli, ["task", "next"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Next Task to Work On" in result.output
    assert "This is a detailed description" in result.output
    assert "8.0" in result.output or "Estimated" in result.output


# ============================================================================
# task import Tests (v0.10.0)
# ============================================================================


def test_task_import_basic(runner: CliRunner, initialized_project: Path) -> None:
    """Test basic YAML task import via CLI."""
    # Create YAML file
    yaml_file = initialized_project / "tasks.yml"
    yaml_file.write_text(
        """
tasks:
  - name: "Task A"
    priority: high
  - name: "Task B"
    priority: medium
"""
    )

    result = runner.invoke(
        cli,
        ["task", "import", str(yaml_file)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "✓ Imported 2 tasks" in result.output
    assert "TASK-001" in result.output
    assert "TASK-002" in result.output


def test_task_import_dry_run(runner: CliRunner, initialized_project: Path) -> None:
    """Test dry-run mode for import."""
    yaml_file = initialized_project / "tasks.yml"
    yaml_file.write_text(
        """
tasks:
  - name: "Task A"
"""
    )

    result = runner.invoke(
        cli,
        ["task", "import", str(yaml_file), "--dry-run"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "✓ Validation successful (dry-run)" in result.output
    assert "Would import 1 tasks" in result.output

    # Verify no tasks were created
    list_result = runner.invoke(cli, ["task", "list"])
    assert "No tasks found" in list_result.output


def test_task_import_with_errors(runner: CliRunner, initialized_project: Path) -> None:
    """Test import with validation errors."""
    yaml_file = initialized_project / "tasks.yml"
    yaml_file.write_text(
        """
tasks:
  - name: "Valid Task"
  - name: ""
"""
    )

    result = runner.invoke(
        cli,
        ["task", "import", str(yaml_file)],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "✗ Import failed" in result.output


def test_task_import_nonexistent_file(runner: CliRunner, initialized_project: Path) -> None:
    """Test import with nonexistent file."""
    result = runner.invoke(
        cli,
        ["task", "import", "nonexistent.yml"],
        catch_exceptions=False,
    )

    assert result.exit_code != 0


def test_task_import_with_next_task_recommendation(
    runner: CliRunner, initialized_project: Path
) -> None:
    """Test import shows next task recommendation."""
    yaml_file = initialized_project / "tasks.yml"
    yaml_file.write_text(
        """
tasks:
  - name: "Low priority"
    priority: low
  - name: "High priority"
    priority: high
"""
    )

    result = runner.invoke(
        cli,
        ["task", "import", str(yaml_file)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Next task to work on:" in result.output
    assert "TASK-002" in result.output  # Should recommend high priority task
