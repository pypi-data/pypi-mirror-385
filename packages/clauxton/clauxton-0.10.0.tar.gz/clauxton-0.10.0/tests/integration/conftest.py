"""
Shared fixtures for integration tests.

This module provides common fixtures used across all integration test files:
- CLI runners
- Initialized Clauxton projects
- Sample data generators
- Utility functions
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pytest
from click.testing import CliRunner

from clauxton.cli.main import cli
from clauxton.core.knowledge_base import KnowledgeBase
from clauxton.core.models import KnowledgeBaseEntry, Task
from clauxton.core.task_manager import TaskManager

# ============================================================================
# CLI Fixtures
# ============================================================================


@pytest.fixture
def runner() -> CliRunner:
    """
    Create CLI test runner.

    Returns:
        CliRunner: Click CLI test runner instance
    """
    return CliRunner()


@pytest.fixture
def initialized_project(tmp_path: Path) -> Path:
    """
    Create and initialize Clauxton project.

    This fixture:
    1. Creates a temporary directory
    2. Runs `clauxton init`
    3. Yields the project directory path

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path: Initialized project directory

    Yields:
        Path: Project directory path during test execution
    """
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0, f"Init failed: {result.output}"
        yield Path(td)


@pytest.fixture
def integration_project(tmp_path: Path) -> Path:
    """
    Create a full Clauxton project for integration testing.

    Similar to initialized_project but includes:
    - Pre-populated KB entries
    - Pre-created tasks
    - Sample configuration

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path: Initialized and populated project directory
    """
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        project_path = Path(td)

        # Initialize project
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0, f"Init failed: {result.output}"

        # Add sample KB entries
        kb = KnowledgeBase(project_path)
        sample_entries = [
            KnowledgeBaseEntry(
                id="KB-20251021-001",
                title="FastAPI Architecture",
                category="architecture",
                content="Use FastAPI for REST API implementation",
                tags=["fastapi", "api", "backend"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            KnowledgeBaseEntry(
                id="KB-20251021-002",
                title="JWT Authentication",
                category="decision",
                content="Use JWT tokens for authentication",
                tags=["jwt", "auth", "security"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            KnowledgeBaseEntry(
                id="KB-20251021-003",
                title="Database Constraint",
                category="constraint",
                content="Maximum 1000 users in free tier",
                tags=["database", "limit", "constraint"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]

        for entry in sample_entries:
            kb.add(entry)

        # Add sample tasks
        task_mgr = TaskManager(project_path)
        sample_tasks = [
            Task(
                id="TASK-001",
                name="Setup FastAPI project",
                description="Initialize FastAPI project structure",
                status="pending",
                priority="high",
                files_to_edit=["backend/main.py", "backend/requirements.txt"],
                estimate_hours=2,
                depends_on=[],
            ),
            Task(
                id="TASK-002",
                name="Implement JWT auth",
                description="Add JWT authentication middleware",
                status="pending",
                priority="high",
                files_to_edit=["backend/auth.py", "backend/middleware.py"],
                estimate_hours=3,
                depends_on=["TASK-001"],
            ),
        ]

        for task in sample_tasks:
            task_mgr.add(task)

        yield project_path


# ============================================================================
# Data Generator Fixtures
# ============================================================================


@pytest.fixture
def sample_kb_entries() -> List[KnowledgeBaseEntry]:
    """
    Generate sample KB entries for testing.

    Returns:
        List[KnowledgeBaseEntry]: List of sample KB entries
    """
    return [
        KnowledgeBaseEntry(
            id=f"KB-20251021-{str(i).zfill(3)}",
            title=f"Entry {i}",
            category="architecture",
            content=f"Content for entry {i}",
            tags=[f"tag{i}", "test"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        for i in range(1, 11)
    ]


@pytest.fixture
def sample_tasks() -> List[Task]:
    """
    Generate sample tasks for testing.

    Returns:
        List[Task]: List of sample tasks
    """
    return [
        Task(
            id=f"TASK-{str(i).zfill(3)}",
            name=f"Task {i}",
            description=f"Description for task {i}",
            status="pending",
            priority="medium",
            files_to_edit=[f"src/module{i}.py"],
            estimate_hours=1,
            depends_on=[],
        )
        for i in range(1, 11)
    ]


@pytest.fixture
def large_kb_dataset() -> List[KnowledgeBaseEntry]:
    """
    Generate large KB dataset for performance testing.

    Returns:
        List[KnowledgeBaseEntry]: 100+ KB entries
    """
    entries = []
    categories = ["architecture", "decision", "constraint", "pattern", "convention"]
    for i in range(1, 101):
        entries.append(
            KnowledgeBaseEntry(
                id=f"KB-20251021-{str(i).zfill(3)}",
                title=f"Entry {i}: {categories[i % len(categories)]}",
                category=categories[i % len(categories)],
                content=f"Large content for entry {i}. " * 10,
                tags=[f"tag{i}", f"category_{i % 5}", "performance"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        )
    return entries


@pytest.fixture
def task_yaml_content() -> str:
    """
    Generate sample YAML content for task import testing.

    Returns:
        str: YAML content with multiple tasks
    """
    return """
tasks:
  - name: "Task 1"
    description: "First task"
    priority: high
    files_to_edit:
      - src/module1.py
    estimate: 2

  - name: "Task 2"
    description: "Second task"
    priority: medium
    files_to_edit:
      - src/module2.py
    depends_on:
      - TASK-001
    estimate: 3

  - name: "Task 3"
    description: "Third task"
    priority: low
    files_to_edit:
      - src/module3.py
    depends_on:
      - TASK-002
    estimate: 1
"""


@pytest.fixture
def large_yaml_content() -> str:
    """
    Generate large YAML content for bulk import testing.

    Returns:
        str: YAML content with 20+ tasks
    """
    tasks = []
    for i in range(1, 21):
        tasks.append(
            f"""  - name: "Task {i}"
    description: "Description for task {i}"
    priority: {"high" if i < 5 else "medium" if i < 15 else "low"}
    files_to_edit:
      - src/module{i}.py
    estimate: {(i % 5) + 1}"""
        )

    return "tasks:\n" + "\n\n".join(tasks)


# ============================================================================
# Utility Functions
# ============================================================================


@pytest.fixture
def extract_id():
    """
    Provide ID extraction utility function.

    Returns:
        Callable: Function to extract ID from CLI output
    """

    def _extract(output: str, prefix: str = "KB-") -> str:
        """
        Extract ID from CLI output.

        Args:
            output: CLI command output
            prefix: ID prefix (e.g., "KB-", "TASK-")

        Returns:
            str: Extracted ID
        """
        lines = output.split("\n")
        for line in lines:
            if prefix in line:
                # Extract ID pattern (e.g., KB-YYYYMMDD-NNN or TASK-NNN)
                words = line.split()
                for word in words:
                    if word.startswith(prefix):
                        return word.rstrip(".:,")
        raise ValueError(f"Could not find {prefix} ID in output: {output}")

    return _extract


@pytest.fixture
def count_tests_in_output():
    """
    Provide test counting utility function.

    Returns:
        Callable: Function to count tests in pytest output
    """

    def _count(output: str) -> int:
        """
        Count tests from pytest output.

        Args:
            output: pytest output

        Returns:
            int: Number of tests found
        """
        import re

        match = re.search(r"(\d+) passed", output)
        if match:
            return int(match.group(1))
        return 0

    return _count


# ============================================================================
# MCP Server Fixtures
# ============================================================================


@pytest.fixture
def mcp_context(initialized_project: Path) -> Dict[str, Any]:
    """
    Provide MCP server context for testing.

    This fixture creates a context dictionary that simulates
    the MCP server environment.

    Args:
        initialized_project: Initialized project path

    Returns:
        Dict[str, Any]: MCP context with project_root
    """
    return {"project_root": str(initialized_project)}


# ============================================================================
# File System Fixtures
# ============================================================================


@pytest.fixture
def sample_file_structure(tmp_path: Path) -> Path:
    """
    Create sample file structure for testing.

    Creates:
    - src/
      - module1.py
      - module2.py
      - subdir/
        - module3.py
    - tests/
      - test_module1.py
    - README.md

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path: Root directory with sample structure
    """
    root = tmp_path / "sample_project"
    root.mkdir()

    # Create source files
    src = root / "src"
    src.mkdir()
    (src / "module1.py").write_text("# Module 1\n")
    (src / "module2.py").write_text("# Module 2\n")

    subdir = src / "subdir"
    subdir.mkdir()
    (subdir / "module3.py").write_text("# Module 3\n")

    # Create test files
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_module1.py").write_text("# Test Module 1\n")

    # Create README
    (root / "README.md").write_text("# Sample Project\n")

    return root


# ============================================================================
# Performance Testing Fixtures
# ============================================================================


@pytest.fixture
def benchmark_timer():
    """
    Provide simple benchmark timer utility.

    Returns:
        Callable: Context manager for timing operations
    """
    from contextlib import contextmanager
    from time import time

    @contextmanager
    def _timer():
        """Context manager for timing operations."""
        start = time()
        result = {"duration": 0.0}
        yield result
        result["duration"] = time() - start

    return _timer
