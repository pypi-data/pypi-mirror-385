"""
Tests for MCP Conflict Detection Tools.

Tests cover:
- detect_conflicts MCP tool
- recommend_safe_order MCP tool
- check_file_conflicts MCP tool
- Integration with TaskManager and ConflictDetector
- Error handling
"""

from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner

from clauxton.cli.main import cli
from clauxton.core.models import NotFoundError, Task
from clauxton.core.task_manager import TaskManager
from clauxton.mcp.server import (
    check_file_conflicts,
    detect_conflicts,
    recommend_safe_order,
)


@pytest.fixture
def initialized_project(tmp_path: Path) -> Path:
    """Create initialized Clauxton project."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        yield Path(td)


@pytest.fixture
def sample_tasks(initialized_project: Path) -> list[Task]:
    """Create sample tasks for testing."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    now = datetime.now()

    tasks = [
        Task(
            id="TASK-001",
            name="Refactor API authentication",
            description="Update auth.py to use JWT tokens",
            status="in_progress",
            priority="high",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        ),
        Task(
            id="TASK-002",
            name="Add OAuth support",
            description="Implement OAuth2 flow",
            status="pending",
            priority="medium",
            files_to_edit=["src/api/auth.py", "src/models/user.py"],
            created_at=now,
        ),
        Task(
            id="TASK-003",
            name="Update user model",
            description="Add new fields to User model",
            status="in_progress",
            priority="low",
            files_to_edit=["src/models/user.py"],
            created_at=now,
        ),
        Task(
            id="TASK-004",
            name="Fix database migrations",
            description="Update migration scripts",
            status="pending",
            priority="high",
            files_to_edit=["migrations/001_add_users.sql"],
            created_at=now,
        ),
    ]

    for task in tasks:
        tm.add(task)

    return tasks


# ============================================================================
# detect_conflicts MCP Tool Tests
# ============================================================================


def test_detect_conflicts_tool_basic(
    initialized_project: Path, sample_tasks: list[Task]
) -> None:
    """Test detect_conflicts MCP tool with basic conflict."""
    import os

    os.chdir(initialized_project)

    # Detect conflicts for TASK-002 (pending, edits auth.py + user.py)
    result = detect_conflicts("TASK-002")

    # Should detect conflicts with TASK-001 (auth.py) and TASK-003 (user.py)
    assert result["task_id"] == "TASK-002"
    assert result["conflict_count"] == 2  # Both in_progress tasks
    assert len(result["conflicts"]) == 2

    # Check that both conflicts are present
    conflict_task_ids = {c["task_b_id"] for c in result["conflicts"]}
    assert "TASK-001" in conflict_task_ids  # auth.py overlap
    assert "TASK-003" in conflict_task_ids  # user.py overlap

    # Check conflict details for first conflict
    for conflict in result["conflicts"]:
        assert conflict["task_a_id"] == "TASK-002"
        assert conflict["conflict_type"] == "file_overlap"
        assert conflict["risk_level"] in ["low", "medium", "high"]
        assert 0.0 <= conflict["risk_score"] <= 1.0
        assert len(conflict["overlapping_files"]) > 0
        assert "recommendation" in conflict


def test_detect_conflicts_tool_no_conflicts(
    initialized_project: Path, sample_tasks: list[Task]
) -> None:
    """Test detect_conflicts MCP tool with no conflicts."""
    import os

    os.chdir(initialized_project)

    # Detect conflicts for TASK-004 (no file overlap)
    result = detect_conflicts("TASK-004")

    assert result["task_id"] == "TASK-004"
    assert result["conflict_count"] == 0
    assert result["conflicts"] == []


def test_detect_conflicts_tool_multiple_conflicts(
    initialized_project: Path, sample_tasks: list[Task]
) -> None:
    """Test detect_conflicts MCP tool with multiple conflicts."""
    import os

    os.chdir(initialized_project)

    # Update TASK-002 to in_progress
    tm = TaskManager(Path.cwd())
    tm.update("TASK-002", {"status": "in_progress"})

    # Detect conflicts for TASK-002
    result = detect_conflicts("TASK-002")

    # Should detect conflicts with both TASK-001 and TASK-003
    assert result["task_id"] == "TASK-002"
    assert result["conflict_count"] == 2
    assert len(result["conflicts"]) == 2

    conflict_task_ids = {c["task_b_id"] for c in result["conflicts"]}
    assert "TASK-001" in conflict_task_ids
    assert "TASK-003" in conflict_task_ids


def test_detect_conflicts_tool_task_not_found(
    initialized_project: Path,
) -> None:
    """Test detect_conflicts MCP tool with non-existent task."""
    import os

    os.chdir(initialized_project)

    # Should raise NotFoundError
    with pytest.raises(NotFoundError, match="not found"):
        detect_conflicts("TASK-999")


# ============================================================================
# recommend_safe_order MCP Tool Tests
# ============================================================================


def test_recommend_safe_order_tool_basic(
    initialized_project: Path, sample_tasks: list[Task]
) -> None:
    """Test recommend_safe_order MCP tool."""
    import os

    os.chdir(initialized_project)

    task_ids = ["TASK-001", "TASK-002", "TASK-003"]
    result = recommend_safe_order(task_ids)

    assert result["task_count"] == 3
    assert len(result["recommended_order"]) == 3
    assert set(result["recommended_order"]) == set(task_ids)
    assert "message" in result
    assert "task_details" in result
    assert len(result["task_details"]) == 3
    # Check message contains "minimize" or "minimizes"
    assert "minim" in result["message"].lower()


def test_recommend_safe_order_tool_with_dependencies(
    initialized_project: Path,
) -> None:
    """Test recommend_safe_order MCP tool with task dependencies."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    now = datetime.now()

    # Create tasks with dependencies
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

    # Get recommended order
    result = recommend_safe_order(["TASK-001", "TASK-002", "TASK-003"])

    # Should respect dependency order
    assert result["recommended_order"] == ["TASK-001", "TASK-002", "TASK-003"]


def test_recommend_safe_order_tool_empty_list(
    initialized_project: Path,
) -> None:
    """Test recommend_safe_order MCP tool with empty task list."""
    import os

    os.chdir(initialized_project)

    result = recommend_safe_order([])

    assert result["task_count"] == 0
    assert result["recommended_order"] == []


def test_recommend_safe_order_tool_task_not_found(
    initialized_project: Path,
) -> None:
    """Test recommend_safe_order MCP tool with non-existent task."""
    import os

    os.chdir(initialized_project)

    # Should raise NotFoundError
    with pytest.raises(NotFoundError, match="not found"):
        recommend_safe_order(["TASK-999"])


# ============================================================================
# check_file_conflicts MCP Tool Tests
# ============================================================================


def test_check_file_conflicts_tool_basic(
    initialized_project: Path, sample_tasks: list[Task]
) -> None:
    """Test check_file_conflicts MCP tool."""
    import os

    os.chdir(initialized_project)

    files = ["src/api/auth.py"]
    result = check_file_conflicts(files)

    assert result["file_count"] == 1
    assert result["files"] == ["src/api/auth.py"]
    # TASK-001 is in_progress and edits auth.py
    assert "TASK-001" in result["conflicting_tasks"]
    assert "in_progress" in result["message"]


def test_check_file_conflicts_tool_multiple_files(
    initialized_project: Path, sample_tasks: list[Task]
) -> None:
    """Test check_file_conflicts MCP tool with multiple files."""
    import os

    os.chdir(initialized_project)

    files = ["src/api/auth.py", "src/models/user.py"]
    result = check_file_conflicts(files)

    assert result["file_count"] == 2
    assert result["files"] == files
    # TASK-001 edits auth.py, TASK-003 edits user.py (both in_progress)
    assert set(result["conflicting_tasks"]) == {"TASK-001", "TASK-003"}


def test_check_file_conflicts_tool_no_conflicts(
    initialized_project: Path, sample_tasks: list[Task]
) -> None:
    """Test check_file_conflicts MCP tool with no conflicts."""
    import os

    os.chdir(initialized_project)

    files = ["src/utils/logger.py"]
    result = check_file_conflicts(files)

    assert result["file_count"] == 1
    assert result["conflicting_tasks"] == []
    assert result["all_available"] is True
    assert "available" in result["message"]


def test_check_file_conflicts_tool_empty_files(
    initialized_project: Path,
) -> None:
    """Test check_file_conflicts MCP tool with empty file list."""
    import os

    os.chdir(initialized_project)

    result = check_file_conflicts([])

    assert result["file_count"] == 0
    assert result["files"] == []
    assert result["conflicting_tasks"] == []


# ============================================================================
# Integration Tests
# ============================================================================


def test_conflict_tools_full_workflow(
    initialized_project: Path,
) -> None:
    """Test full workflow using all conflict detection MCP tools."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    now = datetime.now()

    # Step 1: Create tasks
    task1 = Task(
        id="TASK-001",
        name="Refactor authentication",
        status="in_progress",
        files_to_edit=["src/api/auth.py"],
        created_at=now,
    )
    task2 = Task(
        id="TASK-002",
        name="Add OAuth",
        status="pending",
        files_to_edit=["src/api/auth.py", "src/models/user.py"],
        depends_on=[],
        created_at=now,
    )
    task3 = Task(
        id="TASK-003",
        name="Update user model",
        status="pending",
        files_to_edit=["src/models/user.py"],
        depends_on=["TASK-002"],
        created_at=now,
    )

    tm.add(task1)
    tm.add(task2)
    tm.add(task3)

    # Step 2: Check file conflicts before starting TASK-002
    file_check = check_file_conflicts(["src/api/auth.py"])
    assert "TASK-001" in file_check["conflicting_tasks"]

    # Step 3: Detect conflicts for TASK-002
    conflicts = detect_conflicts("TASK-002")
    assert conflicts["conflict_count"] == 1
    assert conflicts["conflicts"][0]["task_b_id"] == "TASK-001"

    # Step 4: Get safe order recommendation
    order = recommend_safe_order(["TASK-001", "TASK-002", "TASK-003"])
    # TASK-003 depends on TASK-002, so order should be:
    # 1. TASK-001 or TASK-002 (both have no unmet deps)
    # 2. The other one
    # 3. TASK-003 (depends on TASK-002)
    # The exact order of TASK-001 and TASK-002 depends on conflict analysis
    assert len(order["recommended_order"]) == 3
    assert order["recommended_order"][-1] == "TASK-003"  # TASK-003 must be last
    assert set(order["recommended_order"]) == {"TASK-001", "TASK-002", "TASK-003"}

    # Step 5: Complete TASK-001
    tm.update("TASK-001", {"status": "completed"})

    # Step 6: Check conflicts again - should be reduced
    conflicts_after = detect_conflicts("TASK-002")
    assert conflicts_after["conflict_count"] == 0

    # Step 7: Start TASK-002
    tm.update("TASK-002", {"status": "in_progress"})

    # Step 8: Check conflicts for TASK-003
    conflicts_task3 = detect_conflicts("TASK-003")
    assert conflicts_task3["conflict_count"] == 1  # Conflicts with TASK-002


def test_conflict_tools_risk_scoring(
    initialized_project: Path,
) -> None:
    """Test that conflict tools return correct risk levels."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    now = datetime.now()

    # High risk: 100% file overlap
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="in_progress",
        files_to_edit=["src/api/auth.py"],
        created_at=now,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        status="in_progress",
        files_to_edit=["src/api/auth.py"],
        created_at=now,
    )

    tm.add(task1)
    tm.add(task2)

    conflicts = detect_conflicts("TASK-001")

    assert conflicts["conflict_count"] == 1
    conflict = conflicts["conflicts"][0]
    assert conflict["risk_score"] == 1.0
    assert conflict["risk_level"] == "high"
