"""
Tests for CLI Conflict Detection Commands.

Tests cover:
- conflict detect command
- conflict order command
- conflict check command
- Error handling
- Output formatting
"""

from datetime import datetime
from pathlib import Path

from click.testing import CliRunner

from clauxton.cli.main import cli
from clauxton.core.models import Task
from clauxton.core.task_manager import TaskManager


def test_conflict_detect_no_conflicts(tmp_path: Path) -> None:
    """Test conflict detect command with no conflicts."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create task
        tm = TaskManager(Path.cwd())
        task = Task(
            id="TASK-001",
            name="Test task",
            status="pending",
            files_to_edit=["src/api/auth.py"],
            created_at=datetime.now(),
        )
        tm.add(task)

        # Run conflict detect
        result = runner.invoke(cli, ["conflict", "detect", "TASK-001"])
        assert result.exit_code == 0
        assert "No conflicts detected" in result.output
        assert "safe to start" in result.output


def test_conflict_detect_with_conflicts(tmp_path: Path) -> None:
    """Test conflict detect command with conflicts."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        task1 = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        task2 = Task(
            id="TASK-002",
            name="Add OAuth",
            status="pending",
            files_to_edit=["src/api/auth.py", "src/models/user.py"],
            created_at=now,
        )
        tm.add(task1)
        tm.add(task2)

        # Run conflict detect
        result = runner.invoke(cli, ["conflict", "detect", "TASK-002"])
        assert result.exit_code == 0
        assert "conflict(s) detected" in result.output
        assert "TASK-001" in result.output
        assert "Refactor auth" in result.output


def test_conflict_detect_verbose(tmp_path: Path) -> None:
    """Test conflict detect command with verbose output."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        task1 = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        task2 = Task(
            id="TASK-002",
            name="Add OAuth",
            status="pending",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        tm.add(task1)
        tm.add(task2)

        # Run conflict detect with verbose
        result = runner.invoke(cli, ["conflict", "detect", "TASK-002", "--verbose"])
        assert result.exit_code == 0
        assert "Overlapping files:" in result.output
        assert "src/api/auth.py" in result.output
        assert "Details:" in result.output


def test_conflict_detect_task_not_found(tmp_path: Path) -> None:
    """Test conflict detect command with non-existent task."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Run conflict detect with non-existent task
        result = runner.invoke(cli, ["conflict", "detect", "TASK-999"])
        assert result.exit_code == 1
        assert "Error:" in result.output


def test_conflict_order_basic(tmp_path: Path) -> None:
    """Test conflict order command."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        for i in range(1, 4):
            task = Task(
                id=f"TASK-{i:03d}",
                name=f"Task {i}",
                status="pending",
                files_to_edit=[f"src/file{i}.py"],
                created_at=now,
            )
            tm.add(task)

        # Run conflict order
        result = runner.invoke(
            cli, ["conflict", "order", "TASK-001", "TASK-002", "TASK-003"]
        )
        assert result.exit_code == 0
        assert "Task Execution Order" in result.output
        assert "Recommended Order:" in result.output
        assert "TASK-001" in result.output
        assert "TASK-002" in result.output
        assert "TASK-003" in result.output


def test_conflict_order_with_dependencies(tmp_path: Path) -> None:
    """Test conflict order command with dependencies."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks with dependencies
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        task1 = Task(
            id="TASK-001",
            name="Task 1",
            status="pending",
            depends_on=[],
            created_at=now,
        )
        task2 = Task(
            id="TASK-002",
            name="Task 2",
            status="pending",
            depends_on=["TASK-001"],
            created_at=now,
        )
        task3 = Task(
            id="TASK-003",
            name="Task 3",
            status="pending",
            depends_on=["TASK-002"],
            created_at=now,
        )
        tm.add(task1)
        tm.add(task2)
        tm.add(task3)

        # Run conflict order
        result = runner.invoke(
            cli, ["conflict", "order", "TASK-001", "TASK-002", "TASK-003"]
        )
        assert result.exit_code == 0
        assert "respects dependencies" in result.output


def test_conflict_order_with_details(tmp_path: Path) -> None:
    """Test conflict order command with details flag."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        task = Task(
            id="TASK-001",
            name="High priority task",
            status="pending",
            priority="high",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        tm.add(task)

        # Run conflict order with details
        result = runner.invoke(cli, ["conflict", "order", "TASK-001", "--details"])
        assert result.exit_code == 0
        assert "Priority:" in result.output
        assert "Files:" in result.output


def test_conflict_order_task_not_found(tmp_path: Path) -> None:
    """Test conflict order command with non-existent task."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Run conflict order with non-existent task
        result = runner.invoke(cli, ["conflict", "order", "TASK-999"])
        assert result.exit_code == 1
        assert "Error:" in result.output


def test_conflict_check_no_conflicts(tmp_path: Path) -> None:
    """Test conflict check command with no conflicts."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create task (not in_progress)
        tm = TaskManager(Path.cwd())
        task = Task(
            id="TASK-001",
            name="Test task",
            status="pending",
            files_to_edit=["src/api/auth.py"],
            created_at=datetime.now(),
        )
        tm.add(task)

        # Run conflict check
        result = runner.invoke(cli, ["conflict", "check", "src/api/auth.py"])
        assert result.exit_code == 0
        assert "available for editing" in result.output


def test_conflict_check_with_conflicts(tmp_path: Path) -> None:
    """Test conflict check command with conflicts."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create in_progress task
        tm = TaskManager(Path.cwd())
        task = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=datetime.now(),
        )
        tm.add(task)

        # Run conflict check
        result = runner.invoke(cli, ["conflict", "check", "src/api/auth.py"])
        assert result.exit_code == 0
        assert "task(s) editing these files" in result.output
        assert "TASK-001" in result.output
        assert "Refactor auth" in result.output


def test_conflict_check_multiple_files(tmp_path: Path) -> None:
    """Test conflict check command with multiple files."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        task1 = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        task2 = Task(
            id="TASK-002",
            name="Update model",
            status="in_progress",
            files_to_edit=["src/models/user.py"],
            created_at=now,
        )
        tm.add(task1)
        tm.add(task2)

        # Run conflict check with multiple files
        result = runner.invoke(
            cli, ["conflict", "check", "src/api/auth.py", "src/models/user.py"]
        )
        assert result.exit_code == 0
        assert "TASK-001" in result.output
        assert "TASK-002" in result.output


def test_conflict_check_verbose(tmp_path: Path) -> None:
    """Test conflict check command with verbose output."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create in_progress task
        tm = TaskManager(Path.cwd())
        task = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=datetime.now(),
        )
        tm.add(task)

        # Run conflict check with verbose
        result = runner.invoke(
            cli, ["conflict", "check", "src/api/auth.py", "--verbose"]
        )
        assert result.exit_code == 0
        assert "File Status:" in result.output
        assert "locked by:" in result.output


def test_conflict_help_commands(tmp_path: Path) -> None:
    """Test help output for conflict commands."""
    runner = CliRunner()

    # Test conflict group help
    result = runner.invoke(cli, ["conflict", "--help"])
    assert result.exit_code == 0
    assert "Conflict detection commands" in result.output
    assert "detect" in result.output
    assert "order" in result.output
    assert "check" in result.output

    # Test detect help
    result = runner.invoke(cli, ["conflict", "detect", "--help"])
    assert result.exit_code == 0
    assert "Detect conflicts for a specific task" in result.output

    # Test order help
    result = runner.invoke(cli, ["conflict", "order", "--help"])
    assert result.exit_code == 0
    assert "Recommend safe execution order" in result.output

    # Test check help
    result = runner.invoke(cli, ["conflict", "check", "--help"])
    assert result.exit_code == 0
    assert "Check which tasks are currently editing" in result.output


# ============================================================================
# CRITICAL TESTS - Edge Cases
# ============================================================================


def test_conflict_detect_empty_task_files(tmp_path: Path) -> None:
    """Test conflict detect with task that has no files_to_edit."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create task with empty files_to_edit
        tm = TaskManager(Path.cwd())
        task = Task(
            id="TASK-001",
            name="Design architecture",
            status="pending",
            files_to_edit=[],  # No files
            created_at=datetime.now(),
        )
        tm.add(task)

        # Run conflict detect
        result = runner.invoke(cli, ["conflict", "detect", "TASK-001"])
        assert result.exit_code == 0
        assert "No conflicts detected" in result.output
        assert "safe to start" in result.output


def test_conflict_check_nonexistent_files(tmp_path: Path) -> None:
    """Test conflict check with files that don't exist in any task."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create task with different files
        tm = TaskManager(Path.cwd())
        task = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=datetime.now(),
        )
        tm.add(task)

        # Check files that no task is editing
        result = runner.invoke(
            cli, ["conflict", "check", "src/models/user.py", "src/utils/helpers.py"]
        )
        assert result.exit_code == 0
        assert "available for editing" in result.output


def test_conflict_detect_multiple_in_progress(tmp_path: Path) -> None:
    """Test conflict detect with multiple in_progress tasks."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create 5 in_progress tasks, some with overlapping files
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        tasks_data = [
            ("TASK-001", "Refactor auth", ["src/api/auth.py"], "in_progress"),
            ("TASK-002", "Add OAuth", ["src/api/auth.py"], "in_progress"),
            (
                "TASK-003",
                "Update user model",
                ["src/models/user.py", "src/api/auth.py"],
                "in_progress",
            ),
            ("TASK-004", "Add tests", ["tests/test_auth.py"], "in_progress"),
            (
                "TASK-005",
                "Update docs",
                ["docs/auth.md", "src/api/auth.py"],
                "in_progress",
            ),
        ]

        for task_id, name, files, status in tasks_data:
            task = Task(
                id=task_id,
                name=name,
                status=status,
                files_to_edit=files,
                created_at=now,
            )
            tm.add(task)

        # Create new task that overlaps with auth.py
        new_task = Task(
            id="TASK-006",
            name="Security improvements",
            status="pending",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        tm.add(new_task)

        # Run conflict detect - should find 4 conflicts (TASK-001, 002, 003, 005)
        result = runner.invoke(cli, ["conflict", "detect", "TASK-006"])
        assert result.exit_code == 0
        assert "conflict(s) detected" in result.output
        # Should detect conflicts with tasks editing auth.py
        assert "TASK-001" in result.output or "TASK-002" in result.output


def test_conflict_detect_risk_levels(tmp_path: Path) -> None:
    """Test that different risk levels are displayed correctly."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        tm = TaskManager(Path.cwd())
        now = datetime.now()

        # Create tasks with different file overlap levels
        # Low risk: 1 file overlap
        task_low = Task(
            id="TASK-001",
            name="Low risk task",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )

        # Medium risk: 2-3 files overlap
        task_medium_base = Task(
            id="TASK-002",
            name="Medium risk task base",
            status="in_progress",
            files_to_edit=["src/api/auth.py", "src/api/users.py"],
            created_at=now,
        )

        # High risk: 4+ files overlap
        task_high_base = Task(
            id="TASK-003",
            name="High risk task base",
            status="in_progress",
            files_to_edit=[
                "src/api/auth.py",
                "src/api/users.py",
                "src/models/user.py",
                "src/utils/security.py",
            ],
            created_at=now,
        )

        tm.add(task_low)
        tm.add(task_medium_base)
        tm.add(task_high_base)

        # Test low risk
        task_check_low = Task(
            id="TASK-101",
            name="Check low",
            status="pending",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        tm.add(task_check_low)

        result = runner.invoke(cli, ["conflict", "detect", "TASK-101", "--verbose"])
        assert result.exit_code == 0
        # Should show risk level (LOW, MEDIUM, or HIGH)
        assert "Risk:" in result.output


def test_conflict_detect_ignores_completed_tasks(tmp_path: Path) -> None:
    """Test that completed tasks are not checked for conflicts."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        tm = TaskManager(Path.cwd())
        now = datetime.now()

        # Create completed task
        completed_task = Task(
            id="TASK-001",
            name="Refactor auth (completed)",
            status="completed",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )

        # Create in_progress task
        in_progress_task = Task(
            id="TASK-002",
            name="Add OAuth (in progress)",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )

        # Create pending task to check
        pending_task = Task(
            id="TASK-003",
            name="Security improvements",
            status="pending",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )

        tm.add(completed_task)
        tm.add(in_progress_task)
        tm.add(pending_task)

        # Run conflict detect - should only find TASK-002, not TASK-001
        result = runner.invoke(cli, ["conflict", "detect", "TASK-003"])
        assert result.exit_code == 0

        # Should detect in_progress task
        assert "TASK-002" in result.output

        # Should NOT detect completed task
        assert "TASK-001" not in result.output or "completed" not in result.output


# ============================================================================
# CLI OUTPUT REGRESSION TESTS
# ============================================================================


def test_conflict_detect_output_format_stable(tmp_path: Path) -> None:
    """Test that output format remains stable for parsing."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        tm = TaskManager(Path.cwd())
        now = datetime.now()

        # Create conflicting tasks
        task1 = Task(
            id="TASK-001",
            name="Task 1",
            status="in_progress",
            files_to_edit=["file.py"],
            created_at=now,
        )
        task2 = Task(
            id="TASK-002",
            name="Task 2",
            status="pending",
            files_to_edit=["file.py"],
            created_at=now,
        )
        tm.add(task1)
        tm.add(task2)

        # Run conflict detect
        result = runner.invoke(cli, ["conflict", "detect", "TASK-002"])
        assert result.exit_code == 0

        # Verify stable output format (for parsing scripts)
        output = result.output

        # Required sections
        assert "Conflict Detection Report" in output
        assert "Task:" in output
        assert "TASK-002" in output
        assert "Files:" in output

        # Conflict information
        assert "conflict(s) detected" in output
        assert "TASK-001" in output

        # Risk level format
        assert "Risk:" in output
        # Should be one of: HIGH, MEDIUM, LOW
        assert (
            "HIGH" in output.upper()
            or "MEDIUM" in output.upper()
            or "LOW" in output.upper()
        )

        # Recommendation indicator
        assert "→" in output


# ============================================================================
# MEDIUM TESTS - Additional Coverage
# ============================================================================


def test_conflict_order_respects_priority(tmp_path: Path) -> None:
    """Test that task order respects priority levels."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        tm = TaskManager(Path.cwd())
        now = datetime.now()

        # Create tasks with different priorities (no dependencies, no file conflicts)
        tasks_data = [
            ("TASK-001", "Low priority", [], "low", ["src/file1.py"]),
            ("TASK-002", "High priority", [], "high", ["src/file2.py"]),
            ("TASK-003", "Critical priority", [], "critical", ["src/file3.py"]),
            ("TASK-004", "Medium priority", [], "medium", ["src/file4.py"]),
        ]

        for task_id, name, deps, priority, files in tasks_data:
            task = Task(
                id=task_id,
                name=name,
                status="pending",
                priority=priority,
                depends_on=deps,
                files_to_edit=files,
                created_at=now,
            )
            tm.add(task)

        # Run conflict order
        result = runner.invoke(
            cli, ["conflict", "order", "TASK-001", "TASK-002", "TASK-003", "TASK-004"]
        )
        assert result.exit_code == 0

        # Output should contain ordered tasks
        assert "TASK-003" in result.output  # Critical should appear
        assert "TASK-002" in result.output  # High should appear
        assert "TASK-001" in result.output  # Low should appear


def test_conflict_check_special_characters_in_paths(tmp_path: Path) -> None:
    """Test conflict check with special characters in file paths."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        tm = TaskManager(Path.cwd())
        now = datetime.now()

        # Create task with special character file paths
        special_files = [
            "src/api/user (v2).py",
            "src/models/ユーザー.py",
            "src/utils/file-with-dashes.py",
        ]

        task = Task(
            id="TASK-001",
            name="Handle special chars",
            status="in_progress",
            files_to_edit=special_files,
            created_at=now,
        )
        tm.add(task)

        # Check one of these special files
        result = runner.invoke(cli, ["conflict", "check", "src/models/ユーザー.py"])
        assert result.exit_code == 0
        assert "TASK-001" in result.output or "task(s) editing" in result.output


def test_conflict_order_empty_task_list(tmp_path: Path) -> None:
    """Test conflict order with empty task list."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Run conflict order with non-existent tasks
        result = runner.invoke(cli, ["conflict", "order", "TASK-999"])
        # Should show error
        assert result.exit_code == 1
        assert "Error:" in result.output
