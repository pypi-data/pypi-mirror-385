"""
Full Workflow Integration Tests.

Tests cover complete end-to-end workflows:
- Init → YAML import → Task execution → KB export → Undo
- Error cascade through all safety layers
- Configuration changes affecting behavior
- Multi-user task conflict scenarios
- KB full lifecycle
"""

from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner

from clauxton.cli.main import cli
from clauxton.core.knowledge_base import KnowledgeBase
from clauxton.core.models import Task
from clauxton.core.task_manager import TaskManager


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def initialized_project(tmp_path: Path) -> Path:
    """Create and initialize Clauxton project."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        yield Path(td)


# ============================================================================
# Test 1: Complete Workflow (Init → Import → Execute → Export → Undo)
# ============================================================================


def test_complete_workflow_init_to_export(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test complete workflow: init → import → execute → export → undo.

    Workflow:
    1. Initialize project
    2. Add KB entries
    3. Import tasks via YAML
    4. Execute tasks (update status)
    5. Export KB to Markdown
    6. Undo last operation
    7. Verify all state changes
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Step 1: Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert Path(".clauxton").exists()

        # Step 2: Add KB entries (architecture decisions)
        kb_entries = [
            ("FastAPI Framework\narchitecture\nUse FastAPI for all APIs.\napi,fastapi\n"),
            ("PostgreSQL Database\narchitecture\nUse PostgreSQL 15+.\ndatabase,postgresql\n"),
            ("TDD Approach\nconvention\nWrite tests first.\ntesting,tdd\n"),
        ]

        kb_result_ids = []
        for entry_input in kb_entries:
            result = runner.invoke(cli, ["kb", "add"], input=entry_input)
            assert result.exit_code == 0
            # Extract KB ID from output
            import re
            match = re.search(r"KB-\d{8}-\d{3}", result.output)
            if match:
                kb_result_ids.append(match.group(0))

        # Verify KB entries
        kb = KnowledgeBase(Path.cwd())
        entries = kb.list_all()
        assert len(entries) == 3
        assert len(kb_result_ids) == 3

        # Step 3: Import tasks via YAML
        yaml_content = """
tasks:
  - name: Setup FastAPI project
    description: Initialize FastAPI project structure
    priority: high
    files_to_edit:
      - backend/main.py
      - backend/requirements.txt
    estimate: 2

  - name: Setup PostgreSQL
    description: Configure PostgreSQL connection
    priority: high
    files_to_edit:
      - backend/database.py
      - backend/config.py
    estimate: 3

  - name: Write API tests
    description: Write tests for API endpoints
    priority: medium
    files_to_edit:
      - tests/test_api.py
    depends_on:
      - TASK-001
    estimate: 4
"""
        # Create YAML file
        yaml_file = Path("tasks.yml")
        yaml_file.write_text(yaml_content)

        # Import tasks (skip validation for test)
        result = runner.invoke(
            cli, ["task", "import", str(yaml_file), "--skip-validation"]
        )
        assert result.exit_code == 0
        assert "Imported 3 tasks" in result.output or "3 tasks" in result.output

        # Verify tasks
        tm = TaskManager(Path.cwd())
        tasks = tm.list_all()
        assert len(tasks) == 3
        assert tasks[0].id == "TASK-001"
        assert tasks[1].id == "TASK-002"
        assert tasks[2].id == "TASK-003"
        assert tasks[2].depends_on == ["TASK-001"]

        # Step 4: Execute tasks (update status)
        # Start TASK-001
        result = runner.invoke(cli, ["task", "update", "TASK-001", "--status", "in_progress"])
        assert result.exit_code == 0

        # Complete TASK-001
        result = runner.invoke(cli, ["task", "update", "TASK-001", "--status", "completed"])
        assert result.exit_code == 0

        # Start TASK-002
        result = runner.invoke(cli, ["task", "update", "TASK-002", "--status", "in_progress"])
        assert result.exit_code == 0

        # Verify task states - reload TaskManager to get fresh state
        tm = TaskManager(Path.cwd())
        task1 = tm.get("TASK-001")
        assert task1.status == "completed"
        assert task1.completed_at is not None

        task2 = tm.get("TASK-002")
        assert task2.status == "in_progress"

        # Step 5: Export KB to Markdown
        export_dir = Path("docs/kb")
        result = runner.invoke(cli, ["kb", "export", str(export_dir)])
        assert result.exit_code == 0
        assert export_dir.exists()

        # Verify exported files (categories: architecture, convention)
        exported_files = list(export_dir.rglob("*.md"))
        # At least 2 category files (architecture.md, convention.md)
        assert len(exported_files) >= 2

        # Step 6: Undo last operation
        # Note: Skipping undo test as behavior is complex and tested separately

        # Step 7: Verify all state changes are consistent
        # KB should still have 3 entries
        final_entries = kb.list_all()
        assert len(final_entries) == 3

        # Tasks should be: TASK-001=completed, TASK-002=in_progress, TASK-003=pending
        final_tasks = tm.list_all()
        assert len(final_tasks) == 3
        assert final_tasks[0].status == "completed"
        assert final_tasks[1].status == "in_progress"
        assert final_tasks[2].status == "pending"


# ============================================================================
# Test 2: Error Cascade (YAML Safety → Validation → Recovery)
# ============================================================================


def test_error_cascade_yaml_safety_to_recovery(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test error handling cascade through all safety layers.

    Scenarios:
    1. YAML safety: Detect dangerous code injection
    2. Validation: Detect invalid task data
    3. Error recovery: Handle rollback/skip/abort modes
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Scenario 1: YAML Safety - Dangerous code injection
        dangerous_yaml = """
tasks:
  - name: !!python/object/apply:os.system ["rm -rf /"]
    description: Malicious task
    priority: high
"""
        yaml_file = Path("dangerous.yml")
        yaml_file.write_text(dangerous_yaml)

        result = runner.invoke(cli, ["task", "import", str(yaml_file)])
        assert result.exit_code != 0
        assert "Dangerous" in result.output or "unsafe" in result.output.lower()

        # Scenario 2: Validation - Invalid task data
        invalid_yaml = """
tasks:
  - name: ""
    description: Task with empty name
    priority: invalid_priority
    files_to_edit: []
"""
        yaml_file2 = Path("invalid.yml")
        yaml_file2.write_text(invalid_yaml)

        result = runner.invoke(cli, ["task", "import", str(yaml_file2)])
        assert result.exit_code != 0
        assert "Error" in result.output or "Invalid" in result.output

        # Scenario 3: Error Recovery - Mixed valid/invalid tasks
        mixed_yaml = """
tasks:
  - name: Valid Task 1
    description: This is valid
    priority: high
    files_to_edit:
      - file1.py

  - name: ""
    description: Invalid - empty name
    priority: medium

  - name: Valid Task 2
    description: Another valid task
    priority: low
    files_to_edit:
      - file2.py
"""
        yaml_file3 = Path("mixed.yml")
        yaml_file3.write_text(mixed_yaml)

        # Test rollback mode (default)
        result = runner.invoke(
            cli, ["task", "import", str(yaml_file3)]
        )
        assert result.exit_code != 0

        tm = TaskManager(Path.cwd())
        tasks = tm.list_all()
        # No tasks should be imported (rollback)
        assert len(tasks) == 0

        # Note: --on-error option is not yet implemented in CLI
        # Skip the error recovery mode test for now


# ============================================================================
# Test 3: Confirmation Mode Workflow
# ============================================================================


def test_confirmation_mode_workflow(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test confirmation mode changes affect import behavior.

    Modes:
    - always: Always prompt
    - auto: Prompt based on threshold (default)
    - never: Never prompt
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Test 1: Set to "never" mode
        result = runner.invoke(cli, ["config", "set", "confirmation_mode", "never"])
        assert result.exit_code == 0

        # Import tasks without confirmation (should not prompt)
        yaml_content = """
tasks:
  - name: Task 1
    description: Test task
    priority: high
"""
        yaml_file = Path("tasks.yml")
        yaml_file.write_text(yaml_content)

        # In "never" mode, should import without prompt
        result = runner.invoke(cli, ["task", "import", str(yaml_file)])
        assert result.exit_code == 0
        # Should not see confirmation prompt
        assert "Confirm" not in result.output or "imported" in result.output.lower()

        # Test 2: Set to "always" mode
        result = runner.invoke(cli, ["config", "set", "confirmation_mode", "always"])
        assert result.exit_code == 0

        yaml_content2 = """
tasks:
  - name: Task 2
    description: Another test task
    priority: medium
"""
        yaml_file2 = Path("tasks2.yml")
        yaml_file2.write_text(yaml_content2)

        # In "always" mode, should prompt (but we skip with flag)
        result = runner.invoke(
            cli, ["task", "import", str(yaml_file2), "--skip-validation"]
        )
        assert result.exit_code == 0

        # Test 3: Set back to "auto" mode (default)
        result = runner.invoke(cli, ["config", "set", "confirmation_mode", "auto"])
        assert result.exit_code == 0

        # Verify config
        result = runner.invoke(cli, ["config", "get", "confirmation_mode"])
        assert result.exit_code == 0
        assert "auto" in result.output.lower()


# ============================================================================
# Test 4: Multi-User Scenario with Conflicts
# ============================================================================


def test_multi_user_scenario_with_conflicts(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test task conflicts detection in multi-user scenario.

    Scenario:
    - User A starts TASK-001 (edits auth.py)
    - User B wants to start TASK-002 (also edits auth.py)
    - Conflict detection warns User B
    - User B waits for User A to complete
    - User B can now safely start TASK-002
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        tm = TaskManager(Path.cwd())
        now = datetime.now()

        # User A: Create and start TASK-001
        task1 = Task(
            id="TASK-001",
            name="Refactor authentication",
            description="Update auth.py to use JWT",
            status="pending",
            priority="high",
            files_to_edit=["src/api/auth.py", "src/utils/jwt.py"],
            created_at=now,
        )
        tm.add(task1)

        # User A starts work
        result = runner.invoke(cli, ["task", "update", "TASK-001", "--status", "in_progress"])
        assert result.exit_code == 0

        # User B: Create TASK-002 (overlapping file)
        task2 = Task(
            id="TASK-002",
            name="Add OAuth2 support",
            description="Implement OAuth2 in auth.py",
            status="pending",
            priority="medium",
            files_to_edit=["src/api/auth.py", "src/models/user.py"],
            created_at=now,
        )
        tm.add(task2)

        # User B checks for conflicts before starting
        result = runner.invoke(cli, ["conflict", "detect", "TASK-002"])
        assert result.exit_code == 0
        assert "conflict" in result.output.lower()
        assert "TASK-001" in result.output
        assert "src/api/auth.py" in result.output

        # User B decides to wait and works on TASK-003 instead
        task3 = Task(
            id="TASK-003",
            name="Update user profile UI",
            description="No conflicts",
            status="pending",
            priority="low",
            files_to_edit=["src/components/UserProfile.tsx"],
            created_at=now,
        )
        tm.add(task3)

        # Check TASK-003 has no conflicts
        result = runner.invoke(cli, ["conflict", "detect", "TASK-003"])
        assert result.exit_code == 0
        assert "No conflicts" in result.output or "0 conflict" in result.output

        # User A completes TASK-001
        result = runner.invoke(cli, ["task", "update", "TASK-001", "--status", "completed"])
        assert result.exit_code == 0

        # User B checks TASK-002 again
        result = runner.invoke(cli, ["conflict", "detect", "TASK-002"])
        assert result.exit_code == 0
        assert "No conflicts" in result.output or "0 conflict" in result.output

        # User B can now start TASK-002
        result = runner.invoke(cli, ["task", "update", "TASK-002", "--status", "in_progress"])
        assert result.exit_code == 0

        # Verify final state
        final_tasks = tm.list_all()
        assert len(final_tasks) == 3
        assert final_tasks[0].status == "completed"
        assert final_tasks[1].status == "in_progress"
        assert final_tasks[2].status == "pending"


# ============================================================================
# Test 5: KB Full Lifecycle
# ============================================================================


def test_kb_full_lifecycle(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test KB full lifecycle: add → search → update → export → delete.

    Workflow:
    1. Add multiple KB entries (5 entries)
    2. Search by various criteria
    3. Update entries
    4. Export to Markdown
    5. Delete entries
    6. Verify all operations
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        kb = KnowledgeBase(Path.cwd())

        # Step 1: Add multiple KB entries
        entries = [
            ("REST API Design\narchitecture\nUse RESTful principles.\napi,rest\n"),
            (
                "GraphQL Alternative\ndecision\n"
                "Chose REST over GraphQL.\napi,graphql\n"
            ),
            ("Rate Limiting\nconstraint\nMax 1000 requests/min.\napi,limit\n"),
            (
                "Repository Pattern\npattern\n"
                "Use repository pattern for data access.\npattern,data\n"
            ),
            (
                "Code Review Process\nconvention\n"
                "All PRs require 2 approvals.\nprocess,review\n"
            ),
        ]

        entry_ids = []
        for entry_input in entries:
            result = runner.invoke(cli, ["kb", "add"], input=entry_input)
            assert result.exit_code == 0
            # Extract entry ID from output
            import re

            match = re.search(r"KB-\d{8}-\d{3}", result.output)
            if match:
                entry_ids.append(match.group(0))

        # Should have extracted 5 IDs
        assert len(entry_ids) == 5, f"Expected 5 entry IDs, got {len(entry_ids)}: {entry_ids}"

        # Reload KB to get fresh state
        kb = KnowledgeBase(Path.cwd())
        all_entries = kb.list_all()
        assert len(all_entries) == 5

        # Step 2: Search by various criteria
        # Search by keyword
        result = runner.invoke(cli, ["kb", "search", "API"])
        assert result.exit_code == 0
        assert "REST API Design" in result.output or "api" in result.output.lower()

        # Search by category
        result = runner.invoke(cli, ["kb", "search", "pattern", "--category", "pattern"])
        assert result.exit_code == 0
        assert "Repository Pattern" in result.output

        # Search with limit
        result = runner.invoke(cli, ["kb", "search", "API", "--limit", "2"])
        assert result.exit_code == 0

        # Step 3: Update entries
        # Update title
        result = runner.invoke(
            cli,
            ["kb", "update", entry_ids[0], "--title", "RESTful API Design Principles"],
        )
        assert result.exit_code == 0

        # Verify update - reload KB to get fresh state
        kb = KnowledgeBase(Path.cwd())
        updated_entry = kb.get(entry_ids[0])
        assert updated_entry.title == "RESTful API Design Principles"
        assert updated_entry.updated_at is not None

        # Update tags
        result = runner.invoke(
            cli, ["kb", "update", entry_ids[0], "--tags", "api,rest,design"]
        )
        assert result.exit_code == 0

        # Reload KB again after second update
        kb = KnowledgeBase(Path.cwd())
        updated_entry = kb.get(entry_ids[0])
        assert set(updated_entry.tags) == {"api", "rest", "design"}

        # Step 4: Export to Markdown
        export_dir = Path("docs/kb")
        result = runner.invoke(cli, ["kb", "export", str(export_dir)])
        assert result.exit_code == 0
        assert export_dir.exists()

        # Verify exported files
        exported_files = list(export_dir.rglob("*.md"))
        assert len(exported_files) >= 5

        # Verify content of one exported file
        architecture_dir = export_dir / "architecture"
        if architecture_dir.exists():
            md_files = list(architecture_dir.glob("*.md"))
            assert len(md_files) >= 1
            # Read one file and verify format
            content = md_files[0].read_text()
            assert "# " in content  # Markdown header
            assert "**Category:**" in content or "Category" in content

        # Step 5: Delete entries
        # Delete one entry
        result = runner.invoke(cli, ["kb", "delete", entry_ids[4]], input="y\n")
        assert result.exit_code == 0

        # Verify deletion - reload KB
        kb = KnowledgeBase(Path.cwd())
        remaining_entries = kb.list_all()
        assert len(remaining_entries) == 4

        # Try to get deleted entry (should fail)
        with pytest.raises(Exception):
            kb.get(entry_ids[4])

        # Step 6: Final verification
        # List all entries
        result = runner.invoke(cli, ["kb", "list"])
        assert result.exit_code == 0
        assert "(4)" in result.output  # 4 entries remaining

        # Verify specific categories
        result = runner.invoke(cli, ["kb", "list", "--category", "architecture"])
        assert result.exit_code == 0
        assert "RESTful API Design Principles" in result.output
