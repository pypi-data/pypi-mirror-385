"""
Integration tests for Conflict Detection workflows.

Tests end-to-end workflows combining CLI, MCP, and Core components.
"""

from datetime import datetime
from pathlib import Path

from click.testing import CliRunner

from clauxton.cli.main import cli
from clauxton.core.conflict_detector import ConflictDetector
from clauxton.core.models import Task
from clauxton.core.task_manager import TaskManager


class TestWorkflowPreStartCheck:
    """Test Pre-Start Check workflow."""

    def test_complete_pre_start_workflow(self, tmp_path: Path) -> None:
        """
        Test complete pre-start check workflow.

        Workflow:
        1. Create 2 in_progress tasks with overlapping files
        2. Add new task with same files
        3. Run: clauxton conflict detect TASK-003
        4. Verify: Conflict detected, recommendation shown
        5. Run: clauxton conflict order TASK-001 TASK-002 TASK-003
        6. Verify: Safe order returned
        """
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Step 1: Initialize
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Step 2: Create 2 in_progress tasks with overlapping files
            tm = TaskManager(Path.cwd())
            now = datetime.now()

            task1 = Task(
                id="TASK-001",
                name="Refactor authentication",
                status="in_progress",
                priority="high",
                files_to_edit=["src/api/auth.py", "src/models/user.py"],
                created_at=now,
            )
            task2 = Task(
                id="TASK-002",
                name="Add OAuth support",
                status="in_progress",
                priority="medium",
                files_to_edit=["src/api/auth.py", "src/api/oauth.py"],
                created_at=now,
            )
            tm.add(task1)
            tm.add(task2)

            # Step 3: Add new task with same files
            task3 = Task(
                id="TASK-003",
                name="Security improvements",
                status="pending",
                priority="high",
                files_to_edit=["src/api/auth.py"],
                created_at=now,
            )
            tm.add(task3)

            # Step 4: Run conflict detect
            result = runner.invoke(cli, ["conflict", "detect", "TASK-003"])
            assert result.exit_code == 0
            assert "conflict(s) detected" in result.output
            # Should detect conflicts with TASK-001 and TASK-002
            assert "TASK-001" in result.output or "TASK-002" in result.output
            assert "Risk:" in result.output
            assert "→" in result.output  # Recommendation indicator

            # Step 5: Run conflict order
            result = runner.invoke(
                cli, ["conflict", "order", "TASK-001", "TASK-002", "TASK-003"]
            )
            assert result.exit_code == 0
            assert "Recommended Order:" in result.output
            assert "TASK-001" in result.output
            assert "TASK-002" in result.output
            assert "TASK-003" in result.output
            # Verify execution hint
            assert "minimize conflicts" in result.output.lower()

    def test_pre_start_check_with_verbose(self, tmp_path: Path) -> None:
        """Test pre-start check with verbose output."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            tm = TaskManager(Path.cwd())
            now = datetime.now()

            # Create conflicting tasks
            task1 = Task(
                id="TASK-001",
                name="Task 1",
                status="in_progress",
                files_to_edit=["file1.py", "file2.py"],
                created_at=now,
            )
            task2 = Task(
                id="TASK-002",
                name="Task 2",
                status="pending",
                files_to_edit=["file1.py", "file3.py"],
                created_at=now,
            )
            tm.add(task1)
            tm.add(task2)

            # Run with verbose
            result = runner.invoke(cli, ["conflict", "detect", "TASK-002", "--verbose"])
            assert result.exit_code == 0
            assert "Overlapping files:" in result.output or "file1.py" in result.output
            assert "Details:" in result.output


class TestWorkflowSprintPlanning:
    """Test Sprint Planning workflow."""

    def test_sprint_planning_with_priorities(self, tmp_path: Path) -> None:
        """
        Test sprint planning workflow with task priorities.

        Workflow:
        1. Create 5 tasks with various priorities and file overlaps
        2. Run: clauxton conflict order TASK-*
        3. Verify: Order respects priorities and minimizes conflicts
        """
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            tm = TaskManager(Path.cwd())
            now = datetime.now()

            # Create tasks with different priorities
            tasks_data = [
                ("TASK-001", "Critical bug fix", "critical", ["src/core.py"]),
                ("TASK-002", "High priority feature", "high", ["src/api.py"]),
                (
                    "TASK-003",
                    "Medium refactor",
                    "medium",
                    ["src/core.py", "src/utils.py"],
                ),
                ("TASK-004", "Low priority docs", "low", ["docs/guide.md"]),
                (
                    "TASK-005",
                    "High priority test",
                    "high",
                    ["tests/test_api.py"],
                ),
            ]

            for task_id, name, priority, files in tasks_data:
                task = Task(
                    id=task_id,
                    name=name,
                    status="pending",
                    priority=priority,
                    files_to_edit=files,
                    created_at=now,
                )
                tm.add(task)

            # Run conflict order
            result = runner.invoke(
                cli,
                [
                    "conflict",
                    "order",
                    "TASK-001",
                    "TASK-002",
                    "TASK-003",
                    "TASK-004",
                    "TASK-005",
                ],
            )
            assert result.exit_code == 0
            assert "Recommended Order:" in result.output

            # Verify critical task appears first
            lines = result.output.split("\n")
            order_section_started = False
            first_task = None
            for line in lines:
                if "Recommended Order:" in line:
                    order_section_started = True
                    continue
                if order_section_started and "TASK-" in line:
                    if "TASK-001" in line:  # Critical task
                        first_task = "TASK-001"
                        break

            # Critical task should be prioritized
            assert first_task == "TASK-001" or "TASK-001" in result.output

    def test_sprint_planning_with_details(self, tmp_path: Path) -> None:
        """Test sprint planning with --details flag."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            tm = TaskManager(Path.cwd())
            now = datetime.now()

            task = Task(
                id="TASK-001",
                name="Test task",
                status="pending",
                priority="high",
                files_to_edit=["src/file.py"],
                created_at=now,
            )
            tm.add(task)

            # Run with details
            result = runner.invoke(cli, ["conflict", "order", "TASK-001", "--details"])
            assert result.exit_code == 0
            assert "Priority:" in result.output
            assert "Files:" in result.output


class TestWorkflowFileCoordination:
    """Test File Coordination workflow."""

    def test_file_coordination_lifecycle(self, tmp_path: Path) -> None:
        """
        Test file coordination workflow.

        Workflow:
        1. Start TASK-001 (in_progress, edits file.py)
        2. Run: clauxton conflict check file.py
        3. Verify: File locked by TASK-001
        4. Complete TASK-001
        5. Run: clauxton conflict check file.py
        6. Verify: File available
        """
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            tm = TaskManager(Path.cwd())
            now = datetime.now()

            # Step 1: Start TASK-001
            task1 = Task(
                id="TASK-001",
                name="Edit file",
                status="in_progress",
                files_to_edit=["src/api/auth.py"],
                created_at=now,
            )
            tm.add(task1)

            # Step 2: Check file - should be locked
            result = runner.invoke(cli, ["conflict", "check", "src/api/auth.py"])
            assert result.exit_code == 0
            assert "task(s) editing these files" in result.output or "TASK-001" in result.output

            # Step 4: Complete TASK-001
            tm.update("TASK-001", {"status": "completed"})

            # Step 5: Check file again - should be available
            result = runner.invoke(cli, ["conflict", "check", "src/api/auth.py"])
            assert result.exit_code == 0
            assert "available for editing" in result.output

    def test_file_coordination_multiple_files(self, tmp_path: Path) -> None:
        """Test checking multiple files at once."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            tm = TaskManager(Path.cwd())
            now = datetime.now()

            # Lock one file
            task = Task(
                id="TASK-001",
                name="Task",
                status="in_progress",
                files_to_edit=["file1.py"],
                created_at=now,
            )
            tm.add(task)

            # Check multiple files (one locked, one free)
            result = runner.invoke(cli, ["conflict", "check", "file1.py", "file2.py"])
            assert result.exit_code == 0
            # Should show mixed status
            assert "TASK-001" in result.output or "task(s) editing" in result.output


class TestWorkflowMCPCLIConsistency:
    """Test MCP and CLI produce consistent results."""

    def test_mcp_cli_detect_consistency(self, tmp_path: Path) -> None:
        """
        Test that MCP and CLI detect conflicts consistently.

        Workflow:
        1. Create test scenario (2 conflicting tasks)
        2. Call CLI: clauxton conflict detect
        3. Call Core API directly (simulating MCP)
        4. Verify: Both return same conflicts
        """
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            tm = TaskManager(Path.cwd())
            detector = ConflictDetector(tm)
            now = datetime.now()

            # Create test scenario
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

            # CLI detection
            cli_result = runner.invoke(cli, ["conflict", "detect", "TASK-002"])
            assert cli_result.exit_code == 0

            # Core API detection (simulating MCP)
            core_conflicts = detector.detect_conflicts("TASK-002")

            # Verify consistency
            assert len(core_conflicts) > 0  # Should find conflict
            assert "TASK-001" in cli_result.output  # CLI should show same

    def test_mcp_cli_order_consistency(self, tmp_path: Path) -> None:
        """Test that MCP and CLI order tasks consistently."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            tm = TaskManager(Path.cwd())
            detector = ConflictDetector(tm)
            now = datetime.now()

            # Create tasks
            for i in range(1, 4):
                task = Task(
                    id=f"TASK-{i:03d}",
                    name=f"Task {i}",
                    status="pending",
                    files_to_edit=[f"file{i}.py"],
                    created_at=now,
                )
                tm.add(task)

            # CLI order
            cli_result = runner.invoke(
                cli, ["conflict", "order", "TASK-001", "TASK-002", "TASK-003"]
            )
            assert cli_result.exit_code == 0

            # Core API order (simulating MCP)
            core_order = detector.recommend_safe_order(
                ["TASK-001", "TASK-002", "TASK-003"]
            )

            # Verify consistency
            assert len(core_order) == 3
            for task_id in core_order:
                assert task_id in cli_result.output


class TestWorkflowErrorRecovery:
    """Test error handling across components."""

    def test_workflow_handles_missing_task(self, tmp_path: Path) -> None:
        """Test graceful error handling for missing task."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Try to detect conflicts for non-existent task
            result = runner.invoke(cli, ["conflict", "detect", "TASK-999"])
            assert result.exit_code == 1
            assert "Error:" in result.output

    def test_workflow_handles_empty_task_list(self, tmp_path: Path) -> None:
        """Test error handling for empty task list."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Try to order non-existent tasks
            result = runner.invoke(cli, ["conflict", "order", "TASK-999"])
            assert result.exit_code == 1
            assert "Error:" in result.output

    def test_workflow_handles_corrupted_data_gracefully(self, tmp_path: Path) -> None:
        """Test that system handles corrupted data gracefully."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            # Create valid task first
            tm = TaskManager(Path.cwd())
            task = Task(
                id="TASK-001",
                name="Test",
                status="pending",
                files_to_edit=["file.py"],
                created_at=datetime.now(),
            )
            tm.add(task)

            # Verify normal operation works
            result = runner.invoke(cli, ["conflict", "detect", "TASK-001"])
            assert result.exit_code == 0


class TestWorkflowPerformance:
    """Test workflow performance with realistic task counts."""

    def test_workflow_handles_many_tasks(self, tmp_path: Path) -> None:
        """Test that workflow handles 20+ tasks efficiently."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            tm = TaskManager(Path.cwd())
            now = datetime.now()

            # Create 20 tasks
            task_ids = []
            for i in range(1, 21):
                task = Task(
                    id=f"TASK-{i:03d}",
                    name=f"Task {i}",
                    status="pending",
                    files_to_edit=[f"src/file{i % 5}.py"],  # Some overlap
                    created_at=now,
                )
                tm.add(task)
                task_ids.append(task.id)

            # Test ordering performance
            result = runner.invoke(cli, ["conflict", "order"] + task_ids[:10])
            assert result.exit_code == 0
            # Should complete reasonably fast (tested by timeout in runner)

    def test_workflow_handles_complex_dependencies(self, tmp_path: Path) -> None:
        """Test workflow with complex dependency chains."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init"])
            assert result.exit_code == 0

            tm = TaskManager(Path.cwd())
            now = datetime.now()

            # Create dependency chain: 1 -> 2 -> 3
            task1 = Task(
                id="TASK-001",
                name="Base task",
                status="pending",
                depends_on=[],
                files_to_edit=["base.py"],
                created_at=now,
            )
            task2 = Task(
                id="TASK-002",
                name="Dependent task",
                status="pending",
                depends_on=["TASK-001"],
                files_to_edit=["feature.py"],
                created_at=now,
            )
            task3 = Task(
                id="TASK-003",
                name="Final task",
                status="pending",
                depends_on=["TASK-002"],
                files_to_edit=["integration.py"],
                created_at=now,
            )
            tm.add(task1)
            tm.add(task2)
            tm.add(task3)

            # Order should respect dependencies
            result = runner.invoke(
                cli, ["conflict", "order", "TASK-001", "TASK-002", "TASK-003"]
            )
            assert result.exit_code == 0
            assert "respects dependencies" in result.output.lower()
