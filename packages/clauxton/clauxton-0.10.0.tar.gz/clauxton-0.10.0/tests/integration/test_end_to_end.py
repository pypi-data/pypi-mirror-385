"""
Integration tests for end-to-end workflows.

Tests cover complete user workflows:
- Initialize project
- KB: Add, update, delete, search entries
- Tasks: Add, update, dependencies, get next task
- MCP: Knowledge Base and Task Management tools
- Verify YAML persistence
- Complete CLI workflows
"""

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from clauxton.cli.main import cli
from clauxton.core.knowledge_base import KnowledgeBase


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create temporary project directory."""
    return tmp_path


# ============================================================================
# Complete User Workflow Tests
# ============================================================================


def test_complete_workflow(runner: CliRunner, temp_project: Path) -> None:
    """
    Test complete user workflow from init to search.

    Simulates a real user:
    1. Initialize Clauxton
    2. Add 3 KB entries
    3. List all entries
    4. Search for specific entry
    5. Get entry by ID
    6. Verify YAML file structure
    """
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Step 1: Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert Path(".clauxton").exists()
        assert Path(".clauxton/knowledge-base.yml").exists()

        # Step 2: Add 3 entries
        entries_data = [
            {
                "input": (
                    "Use FastAPI\narchitecture\n"
                    "All APIs use FastAPI framework.\nbackend,api\n"
                ),
                "title": "Use FastAPI",
            },
            {
                "input": (
                    "PostgreSQL for production\ndecision\n"
                    "Use PostgreSQL 15+ for production.\ndatabase,postgresql\n"
                ),
                "title": "PostgreSQL for production",
            },
            {
                "input": (
                    "TDD workflow\nconvention\n"
                    "Write tests before implementation.\ntesting,tdd\n"
                ),
                "title": "TDD workflow",
            },
        ]

        for entry in entries_data:
            result = runner.invoke(cli, ["kb", "add"], input=entry["input"])
            assert result.exit_code == 0
            assert "Added entry" in result.output

        # Step 3: List all entries
        result = runner.invoke(cli, ["kb", "list"])
        assert result.exit_code == 0
        assert "(3)" in result.output  # Should show 3 entries
        assert "Use FastAPI" in result.output
        assert "PostgreSQL for production" in result.output
        assert "TDD workflow" in result.output

        # Step 4: Search
        result = runner.invoke(cli, ["kb", "search", "FastAPI"])
        assert result.exit_code == 0
        assert "Use FastAPI" in result.output
        assert "architecture" in result.output

        # Step 5: Get entry by ID (extract from list output)
        list_result = runner.invoke(cli, ["kb", "list"])
        # Extract first entry ID (KB-YYYYMMDD-NNN pattern)
        import re

        match = re.search(r"KB-\d{8}-\d{3}", list_result.output)
        assert match is not None
        entry_id = match.group(0)

        result = runner.invoke(cli, ["kb", "get", entry_id])
        assert result.exit_code == 0
        assert entry_id in result.output

        # Step 6: Verify YAML file structure
        kb_file = Path(".clauxton/knowledge-base.yml")
        with open(kb_file) as f:
            data = yaml.safe_load(f)

        assert data["version"] == "1.0"
        assert "project_name" in data
        assert len(data["entries"]) == 3
        assert all("id" in entry for entry in data["entries"])
        assert all("title" in entry for entry in data["entries"])
        assert all("category" in entry for entry in data["entries"])


def test_persistence_across_sessions(runner: CliRunner, temp_project: Path) -> None:
    """
    Test that data persists across sessions.

    1. Initialize and add entry
    2. Create new KnowledgeBase instance
    3. Verify entry still exists
    """
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Session 1: Init and add
        runner.invoke(cli, ["init"])
        result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Persistent Entry\narchitecture\nThis should persist.\n\n",
        )
        assert result.exit_code == 0

        # Session 2: New KB instance
        kb = KnowledgeBase(Path.cwd())
        entries = kb.list_all()

        assert len(entries) == 1
        assert entries[0].title == "Persistent Entry"
        assert entries[0].category == "architecture"
        assert entries[0].content == "This should persist."


def test_search_workflow(runner: CliRunner, temp_project: Path) -> None:
    """
    Test search workflow with multiple filters.

    1. Add entries across different categories
    2. Search by keyword
    3. Search by category
    4. Search with multiple filters
    """
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        # Add entries
        entries = [
            ("API Design\narchitecture\nRESTful API design.\napi,rest\n", "architecture"),
            ("API Rate Limit\nconstraint\nMax 1000 req/min.\napi,limit\n", "constraint"),
            ("Choose REST\ndecision\nREST over GraphQL.\napi,rest\n", "decision"),
        ]

        for entry_input, _ in entries:
            runner.invoke(cli, ["kb", "add"], input=entry_input)

        # Search by keyword
        result = runner.invoke(cli, ["kb", "search", "API"])
        assert result.exit_code == 0
        assert "(2)" in result.output  # 2 entries have "API" in title/content

        # Search by category
        result = runner.invoke(cli, ["kb", "search", "API", "--category", "architecture"])
        assert result.exit_code == 0
        assert "API Design" in result.output
        assert "API Rate Limit" not in result.output

        # Search with limit
        result = runner.invoke(cli, ["kb", "search", "API", "--limit", "2"])
        assert result.exit_code == 0
        # Should show max 2 results


def test_category_filtering(runner: CliRunner, temp_project: Path) -> None:
    """
    Test category filtering in list command.

    1. Add entries across all 5 categories
    2. List all
    3. List by each category
    """
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        # Add one entry for each category
        categories = [
            ("Arch Entry\narchitecture\nArch content.\n\n", "architecture"),
            ("Const Entry\nconstraint\nConst content.\n\n", "constraint"),
            ("Dec Entry\ndecision\nDec content.\n\n", "decision"),
            ("Pat Entry\npattern\nPat content.\n\n", "pattern"),
            ("Conv Entry\nconvention\nConv content.\n\n", "convention"),
        ]

        for entry_input, _ in categories:
            runner.invoke(cli, ["kb", "add"], input=entry_input)

        # List all
        result = runner.invoke(cli, ["kb", "list"])
        assert result.exit_code == 0
        assert "(5)" in result.output

        # List by each category
        for _, category in categories:
            result = runner.invoke(cli, ["kb", "list", "--category", category])
            assert result.exit_code == 0
            assert "(1)" in result.output


def test_yaml_file_human_readable(runner: CliRunner, temp_project: Path) -> None:
    """
    Test that YAML file is human-readable and properly formatted.

    Verify:
    - Valid YAML syntax
    - Human-readable structure
    - Proper indentation
    - No Python object representations
    """
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Test Entry\narchitecture\nTest content with unicode: 日本語\nemoji,unicode\n",
        )

        kb_file = Path(".clauxton/knowledge-base.yml")
        content = kb_file.read_text()

        # Should be valid YAML
        data = yaml.safe_load(content)
        assert data is not None

        # Should have human-readable fields
        assert "version:" in content
        assert "project_name:" in content
        assert "entries:" in content

        # Should not have Python object representations
        assert "KnowledgeBaseEntry" not in content
        assert "<object" not in content

        # Should support Unicode
        assert "日本語" in content


def test_error_handling_workflow(runner: CliRunner, temp_project: Path) -> None:
    """
    Test error handling in user workflows.

    Test scenarios:
    - Add without init
    - Get non-existent entry
    - Search in empty KB
    - Init twice
    """
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Add without init
        result = runner.invoke(cli, ["kb", "add"], input="Test\narchitecture\nContent\n\n")
        assert result.exit_code != 0
        assert ".clauxton/ not found" in result.output

        # Init
        runner.invoke(cli, ["init"])

        # Get non-existent entry
        result = runner.invoke(cli, ["kb", "get", "KB-20251019-999"])
        assert result.exit_code != 0
        assert "Error" in result.output

        # Search in empty KB
        result = runner.invoke(cli, ["kb", "search", "nonexistent"])
        assert result.exit_code == 0
        assert "No results found" in result.output

        # Init twice (should fail)
        result = runner.invoke(cli, ["init"])
        assert result.exit_code != 0
        assert "already exists" in result.output


def test_backup_creation(runner: CliRunner, temp_project: Path) -> None:
    """
    Test that backup files are created on updates.

    1. Initialize and add entry
    2. Verify no backup initially
    3. Add another entry (triggers write with backup)
    4. Verify backup file exists
    """
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        # First entry
        runner.invoke(cli, ["kb", "add"], input="First\narchitecture\nContent 1\n\n")

        # Check initial state
        kb_file = Path(".clauxton/knowledge-base.yml")
        backup_file = kb_file.with_suffix(".yml.bak")

        # Backup might not exist yet (depends on implementation)
        # But KB file should exist
        assert kb_file.exists()

        # Second entry (should trigger backup)
        runner.invoke(cli, ["kb", "add"], input="Second\narchitecture\nContent 2\n\n")

        # After second write, backup should exist
        assert backup_file.exists()

        # Backup should contain valid YAML
        with open(backup_file) as f:
            backup_data = yaml.safe_load(f)
        assert backup_data is not None
        assert "entries" in backup_data


# ============================================================================
# KB + Task Integration Tests
# ============================================================================


def test_kb_task_integration_workflow(runner: CliRunner, temp_project: Path) -> None:
    """
    Test KB and Task Management integration.

    Workflow:
    1. Create KB entries for architecture decisions
    2. Create tasks referencing KB entries
    3. Complete tasks
    4. Verify KB-Task relationships
    """
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Step 1: Initialize
        runner.invoke(cli, ["init"])

        # Step 2: Add KB entries
        kb_result1 = runner.invoke(
            cli,
            ["kb", "add"],
            input="Use PostgreSQL\narchitecture\nDatabase decision.\ndatabase,postgresql\n",
        )
        assert kb_result1.exit_code == 0

        kb_result2 = runner.invoke(
            cli,
            ["kb", "add"],
            input="FastAPI framework\narchitecture\nAPI framework.\napi,fastapi\n",
        )
        assert kb_result2.exit_code == 0

        # Extract KB IDs
        import re

        kb_id1 = re.search(r"KB-\d{8}-\d{3}", kb_result1.output).group(0)
        _kb_id2 = re.search(r"KB-\d{8}-\d{3}", kb_result2.output).group(0)

        # Step 3: Create tasks with KB references
        task_result = runner.invoke(
            cli,
            [
                "task",
                "add",
                "--name",
                "Setup database schema",
                "--kb-refs",
                kb_id1,
                "--files",
                "schema.sql",
                "--priority",
                "high",
            ],
        )
        assert task_result.exit_code == 0
        assert "TASK-001" in task_result.output

        # Step 4: Verify task shows KB reference
        task_get = runner.invoke(cli, ["task", "get", "TASK-001"])
        assert kb_id1 in task_get.output
        assert "Related KB" in task_get.output

        # Step 5: Complete task workflow
        runner.invoke(cli, ["task", "update", "TASK-001", "--status", "in_progress"])
        runner.invoke(cli, ["task", "update", "TASK-001", "--status", "completed"])

        # Step 6: Verify task completion
        final_get = runner.invoke(cli, ["task", "get", "TASK-001"])
        assert "completed" in final_get.output
        assert "Completed:" in final_get.output


def test_task_dependency_with_kb_references(runner: CliRunner, temp_project: Path) -> None:
    """Test tasks with dependencies and KB references."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        # Add KB entry
        kb_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="API Design\narchitecture\nREST API design.\napi\n",
        )
        import re

        kb_id = re.search(r"KB-\d{8}-\d{3}", kb_result.output).group(0)

        # Create dependent tasks with KB refs
        runner.invoke(
            cli,
            [
                "task",
                "add",
                "--name",
                "Define API spec",
                "--kb-refs",
                kb_id,
                "--priority",
                "high",
            ],
        )

        runner.invoke(
            cli,
            [
                "task",
                "add",
                "--name",
                "Implement API",
                "--depends-on",
                "TASK-001",
                "--kb-refs",
                kb_id,
            ],
        )

        # Verify dependency chain
        task1_get = runner.invoke(cli, ["task", "get", "TASK-001"])
        assert kb_id in task1_get.output

        task2_get = runner.invoke(cli, ["task", "get", "TASK-002"])
        assert "TASK-001" in task2_get.output
        assert kb_id in task2_get.output

        # Get next task (should be TASK-001 due to dependencies)
        next_result = runner.invoke(cli, ["task", "next"])
        assert "TASK-001" in next_result.output
