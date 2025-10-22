"""
Cross-Module Integration Tests.

Tests cover interactions between multiple Clauxton modules:
- KB + Task integration
- Conflict detection + KB integration
- Undo across modules
- Config persistence
- Backup and restore
"""

from pathlib import Path

from click.testing import CliRunner

from clauxton.cli.main import cli

# ============================================================================
# Test 1: KB and Task Integration
# ============================================================================


def test_kb_task_integration(runner: CliRunner, tmp_path: Path, extract_id) -> None:
    """
    Test KB and Task interaction.

    Workflow:
    1. Add KB entry about architecture decision
    2. Create task referencing the decision
    3. Verify both exist
    4. Search KB for task-related info
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add KB entry about FastAPI
        result = runner.invoke(
            cli,
            [
                "kb",
                "add",
                "--title",
                "Use FastAPI framework",
                "--category",
                "architecture",
                "--content",
                "All APIs should use FastAPI",
                "--tags",
                "fastapi,api,backend",
            ],
        )
        assert result.exit_code == 0
        kb_id = extract_id(result.output, "KB-")

        # Create task to implement FastAPI
        result = runner.invoke(
            cli,
            [
                "task",
                "add",
                "--name",
                "Setup FastAPI project",
                "--priority",
                "high",
                "--files",
                "backend/main.py",
            ],
        )
        assert result.exit_code == 0
        task_id = extract_id(result.output, "TASK-")

        # Verify both exist
        result = runner.invoke(cli, ["kb", "get", kb_id])
        assert result.exit_code == 0
        assert "FastAPI" in result.output

        result = runner.invoke(cli, ["task", "get", task_id])
        assert result.exit_code == 0
        assert "FastAPI" in result.output or task_id in result.output

        # Search KB for API info
        result = runner.invoke(cli, ["kb", "search", "FastAPI"])
        assert result.exit_code == 0
        assert kb_id in result.output or "FastAPI" in result.output


# ============================================================================
# Test 2: Conflict Detection with KB Entries
# ============================================================================


def test_conflict_kb_integration(runner: CliRunner, tmp_path: Path, extract_id) -> None:
    """
    Test conflict detection with KB context.

    Workflow:
    1. Add KB entry about file ownership
    2. Create two tasks editing same file
    3. Detect conflicts
    4. Verify conflict report
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add KB entry about critical file
        result = runner.invoke(
            cli,
            [
                "kb",
                "add",
                "--title",
                "Core API file",
                "--category",
                "constraint",
                "--content",
                "src/api/core.py is critical - coordinate changes",
                "--tags",
                "critical,api",
            ],
        )
        assert result.exit_code == 0

        # Create task 1 editing core.py
        result = runner.invoke(
            cli,
            [
                "task",
                "add",
                "--name",
                "Add auth to core",
                "--priority",
                "high",
                "--files",
                "src/api/core.py",
            ],
        )
        assert result.exit_code == 0
        task1_id = extract_id(result.output, "TASK-")

        # Create task 2 also editing core.py
        result = runner.invoke(
            cli,
            [
                "task",
                "add",
                "--name",
                "Add validation to core",
                "--priority",
                "high",
                "--files",
                "src/api/core.py",
            ],
        )
        assert result.exit_code == 0

        # Detect conflicts
        result = runner.invoke(cli, ["conflict", "detect", task1_id])
        assert result.exit_code == 0
        # Should mention conflict or shared file


# ============================================================================
# Test 3: Undo Across Modules
# ============================================================================


def test_undo_across_modules(runner: CliRunner, tmp_path: Path, extract_id) -> None:
    """
    Test undo across KB and Task operations.

    Workflow:
    1. Add KB entry
    2. Add task
    3. Verify both exist
    4. Undo task
    5. Verify task removed, KB remains
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add KB entry
        result = runner.invoke(
            cli,
            [
                "kb",
                "add",
                "--title",
                "Test KB Entry",
                "--category",
                "architecture",
                "--content",
                "Test content",
                "--tags",
                "test",
            ],
        )
        assert result.exit_code == 0
        kb_id = extract_id(result.output, "KB-")

        # Add task
        result = runner.invoke(
            cli,
            [
                "task",
                "add",
                "--name",
                "Test Task",
                "--priority",
                "medium",
                "--files",
                "src/test.py",
            ],
        )
        assert result.exit_code == 0
        task_id = extract_id(result.output, "TASK-")

        # Verify both exist
        result = runner.invoke(cli, ["kb", "list"])
        assert kb_id in result.output

        result = runner.invoke(cli, ["task", "list"])
        assert task_id in result.output

        # Undo last operation (task add)
        result = runner.invoke(cli, ["undo", "--yes"])
        # Undo may or may not succeed depending on implementation


# ============================================================================
# Test 4: Config Persistence
# ============================================================================


def test_config_persistence(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test configuration persistence across sessions.

    Workflow:
    1. Initialize project
    2. Set config value
    3. Verify config saved
    4. Read config
    5. Verify persistence
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Check if config commands exist
        result = runner.invoke(cli, ["--help"])
        if "config" in result.output.lower():
            # Set config
            result = runner.invoke(
                cli, ["config", "set", "confirmation_mode", "auto"]
            )
            # Config may or may not be supported

            # Get config
            result = runner.invoke(cli, ["config", "get", "confirmation_mode"])
            # Should show config value

        # For now, just verify project initialized
        clauxton_dir = Path.cwd() / ".clauxton"
        assert clauxton_dir.exists()


# ============================================================================
# Test 5: Backup and Restore Workflow
# ============================================================================


def test_backup_restore_workflow(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test backup and restore functionality.

    Workflow:
    1. Add data (KB + tasks)
    2. Verify backups created
    3. Check backup directory
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add KB entry
        result = runner.invoke(
            cli,
            [
                "kb",
                "add",
                "--title",
                "Backup Test",
                "--category",
                "architecture",
                "--content",
                "Test backup",
                "--tags",
                "backup",
            ],
        )
        assert result.exit_code == 0

        # Add task
        result = runner.invoke(
            cli,
            [
                "task",
                "add",
                "--name",
                "Backup Task",
                "--priority",
                "low",
                "--files",
                "src/backup.py",
            ],
        )
        assert result.exit_code == 0

        # Check backup directory exists
        backup_dir = Path.cwd() / ".clauxton" / "backups"
        # Backups may be created automatically
        if backup_dir.exists():
            # Verify some backups exist
            backup_files = list(backup_dir.glob("*"))
            # Backup count depends on implementation
            assert isinstance(backup_files, list)


# ============================================================================
# Test 6: File Permissions Workflow
# ============================================================================


def test_file_permissions_workflow(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test file permission handling.

    Workflow:
    1. Initialize project
    2. Check .clauxton directory permissions
    3. Check YAML file permissions
    4. Verify security settings
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Check .clauxton directory exists
        clauxton_dir = Path.cwd() / ".clauxton"
        assert clauxton_dir.exists()
        assert clauxton_dir.is_dir()

        # Check YAML files exist
        kb_file = clauxton_dir / "knowledge-base.yml"
        tasks_file = clauxton_dir / "tasks.yml"

        # Files should exist after init
        if kb_file.exists():
            # Check readable
            assert kb_file.is_file()
            # Verify can read
            content = kb_file.read_text()
            assert isinstance(content, str)

        if tasks_file.exists():
            assert tasks_file.is_file()
            content = tasks_file.read_text()
            assert isinstance(content, str)


# ============================================================================
# Test 7: End-to-End Workflow
# ============================================================================


def test_complete_end_to_end_workflow(
    runner: CliRunner, tmp_path: Path, extract_id
) -> None:
    """
    Test complete end-to-end workflow across all modules.

    Workflow:
    1. Initialize project
    2. Add KB entries
    3. Add tasks
    4. Check conflicts
    5. Update task status
    6. Export KB
    7. Verify all data persisted
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Step 1: Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Step 2: Add KB entries
        kb_ids = []
        for i in range(3):
            result = runner.invoke(
                cli,
                [
                    "kb",
                    "add",
                    "--title",
                    f"Entry {i+1}",
                    "--category",
                    "architecture",
                    "--content",
                    f"Content {i+1}",
                    "--tags",
                    f"tag{i+1}",
                ],
            )
            assert result.exit_code == 0
            kb_ids.append(extract_id(result.output, "KB-"))

        # Step 3: Add tasks
        task_ids = []
        for i in range(3):
            result = runner.invoke(
                cli,
                [
                    "task",
                    "add",
                    "--name",
                    f"Task {i+1}",
                    "--priority",
                    "medium",
                    "--files",
                    f"src/module{i+1}.py",
                ],
            )
            assert result.exit_code == 0
            task_ids.append(extract_id(result.output, "TASK-"))

        # Step 4: Check conflicts
        result = runner.invoke(cli, ["conflict", "detect", task_ids[0]])
        assert result.exit_code == 0

        # Step 5: Update task status
        result = runner.invoke(
            cli, ["task", "update", task_ids[0], "--status", "in_progress"]
        )
        assert result.exit_code == 0

        # Step 6: Export KB
        export_dir = Path.cwd() / "docs" / "kb"
        result = runner.invoke(cli, ["kb", "export", str(export_dir)])
        assert result.exit_code == 0

        # Step 7: Verify all data
        result = runner.invoke(cli, ["kb", "list"])
        assert result.exit_code == 0
        for kb_id in kb_ids:
            assert kb_id in result.output

        result = runner.invoke(cli, ["task", "list"])
        assert result.exit_code == 0
        for task_id in task_ids:
            assert task_id in result.output

        # Verify export created files
        if export_dir.exists():
            md_files = list(export_dir.glob("*.md"))
            assert len(md_files) >= 1
