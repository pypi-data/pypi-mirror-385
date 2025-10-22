"""
Tests for MCP Task Management Tools.

Tests cover:
- task_add: Add new task
- task_list: List tasks with filters
- task_get: Get task by ID
- task_update: Update task fields
- task_next: Get recommended next task
- task_delete: Delete task
- Error handling
"""

from pathlib import Path

import pytest

from clauxton.core.task_manager import TaskManager
from clauxton.mcp.server import (
    task_add,
    task_delete,
    task_get,
    task_list,
    task_next,
    task_update,
)


@pytest.fixture
def task_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TaskManager:
    """Create TaskManager with temporary directory."""
    (tmp_path / ".clauxton").mkdir()
    monkeypatch.chdir(tmp_path)
    return TaskManager(tmp_path)


# ============================================================================
# task_add Tests
# ============================================================================


def test_task_add_basic(task_manager: TaskManager) -> None:
    """Test adding a basic task."""
    result = task_add(name="Test task")

    assert "task_id" in result
    assert result["task_id"] == "TASK-001"
    assert result["name"] == "Test task"
    assert result["priority"] == "medium"

    # Verify task was created
    task = task_manager.get("TASK-001")
    assert task.name == "Test task"
    assert task.status == "pending"


def test_task_add_with_all_fields(task_manager: TaskManager) -> None:
    """Test adding task with all optional fields."""
    result = task_add(
        name="Complex task",
        description="Detailed description",
        priority="high",
        depends_on=None,
        files=["src/main.py", "tests/test_main.py"],
        kb_refs=["KB-20251019-001"],
        estimate=4.5,
    )

    assert result["task_id"] == "TASK-001"
    assert result["priority"] == "high"

    task = task_manager.get("TASK-001")
    assert task.description == "Detailed description"
    assert task.priority == "high"
    assert task.files_to_edit == ["src/main.py", "tests/test_main.py"]
    assert task.related_kb == ["KB-20251019-001"]
    assert task.estimated_hours == 4.5


def test_task_add_with_dependencies(task_manager: TaskManager) -> None:
    """Test adding task with dependencies."""
    # Add first task
    result1 = task_add(name="Task 1")
    assert result1["task_id"] == "TASK-001"

    # Add second task depending on first
    result2 = task_add(name="Task 2", depends_on=["TASK-001"])
    assert result2["task_id"] == "TASK-002"

    task2 = task_manager.get("TASK-002")
    assert "TASK-001" in task2.depends_on


# ============================================================================
# task_list Tests
# ============================================================================


def test_task_list_all(task_manager: TaskManager) -> None:
    """Test listing all tasks."""
    # Add some tasks
    task_add(name="Task 1", priority="high")
    task_add(name="Task 2", priority="low")
    task_add(name="Task 3", priority="medium")

    results = task_list()
    assert len(results) == 3
    assert all("id" in task for task in results)
    assert all("name" in task for task in results)


def test_task_list_filter_by_status(task_manager: TaskManager) -> None:
    """Test filtering tasks by status."""
    task_add(name="Task 1")
    task_add(name="Task 2")

    # Update one task to in_progress
    task_update("TASK-001", status="in_progress")

    pending = task_list(status="pending")
    assert len(pending) == 1
    assert pending[0]["id"] == "TASK-002"

    in_progress = task_list(status="in_progress")
    assert len(in_progress) == 1
    assert in_progress[0]["id"] == "TASK-001"


def test_task_list_filter_by_priority(task_manager: TaskManager) -> None:
    """Test filtering tasks by priority."""
    task_add(name="Task 1", priority="high")
    task_add(name="Task 2", priority="low")
    task_add(name="Task 3", priority="high")

    high_priority = task_list(priority="high")
    assert len(high_priority) == 2
    assert all(task["priority"] == "high" for task in high_priority)


def test_task_list_empty(task_manager: TaskManager) -> None:
    """Test listing tasks when none exist."""
    results = task_list()
    assert len(results) == 0


# ============================================================================
# task_get Tests
# ============================================================================


def test_task_get_existing(task_manager: TaskManager) -> None:
    """Test getting an existing task."""
    task_add(
        name="Test task",
        description="Description",
        priority="high",
        files=["src/main.py"],
    )

    result = task_get("TASK-001")
    assert result["id"] == "TASK-001"
    assert result["name"] == "Test task"
    assert result["description"] == "Description"
    assert result["priority"] == "high"
    assert result["files_to_edit"] == ["src/main.py"]


def test_task_get_nonexistent(task_manager: TaskManager) -> None:
    """Test getting non-existent task raises error."""
    from clauxton.core.models import NotFoundError

    with pytest.raises(NotFoundError):
        task_get("TASK-999")


# ============================================================================
# task_update Tests
# ============================================================================


def test_task_update_status(task_manager: TaskManager) -> None:
    """Test updating task status."""
    task_add(name="Test task")

    result = task_update("TASK-001", status="in_progress")
    assert "Successfully updated" in result["message"]

    task = task_manager.get("TASK-001")
    assert task.status == "in_progress"
    assert task.started_at is not None


def test_task_update_status_to_completed(task_manager: TaskManager) -> None:
    """Test updating status to completed sets completed_at."""
    task_add(name="Test task")

    task_update("TASK-001", status="completed")

    task = task_manager.get("TASK-001")
    assert task.status == "completed"
    assert task.completed_at is not None


def test_task_update_priority(task_manager: TaskManager) -> None:
    """Test updating task priority."""
    task_add(name="Test task", priority="low")

    task_update("TASK-001", priority="high")

    task = task_manager.get("TASK-001")
    assert task.priority == "high"


def test_task_update_multiple_fields(task_manager: TaskManager) -> None:
    """Test updating multiple fields at once."""
    task_add(name="Test task", description="Old description")

    task_update(
        "TASK-001",
        status="in_progress",
        priority="high",
        name="Updated name",
        description="New description",
    )

    task = task_manager.get("TASK-001")
    assert task.status == "in_progress"
    assert task.priority == "high"
    assert task.name == "Updated name"
    assert task.description == "New description"


# ============================================================================
# task_next Tests
# ============================================================================


def test_task_next_no_dependencies(task_manager: TaskManager) -> None:
    """Test getting next task when no dependencies."""
    task_add(name="Low priority", priority="low")
    task_add(name="High priority", priority="high")

    result = task_next()
    assert result is not None
    assert result["id"] == "TASK-002"  # High priority first
    assert result["priority"] == "high"


def test_task_next_with_dependencies(task_manager: TaskManager) -> None:
    """Test getting next task respects dependencies."""
    task_add(name="Task 1", priority="low")
    task_add(name="Task 2", priority="high", depends_on=["TASK-001"])

    # TASK-002 has higher priority but depends on TASK-001
    result = task_next()
    assert result is not None
    assert result["id"] == "TASK-001"  # Must do TASK-001 first


def test_task_next_after_dependency_completed(task_manager: TaskManager) -> None:
    """Test getting next task after dependency is completed."""
    task_add(name="Task 1")
    task_add(name="Task 2", depends_on=["TASK-001"])

    # Complete TASK-001
    task_update("TASK-001", status="completed")

    # Now TASK-002 should be recommended
    result = task_next()
    assert result is not None
    assert result["id"] == "TASK-002"


def test_task_next_no_tasks_available(task_manager: TaskManager) -> None:
    """Test getting next task when none are available."""
    task_add(name="Task 1")
    task_update("TASK-001", status="completed")

    result = task_next()
    assert result is None


# ============================================================================
# task_delete Tests
# ============================================================================


def test_task_delete_existing(task_manager: TaskManager) -> None:
    """Test deleting an existing task."""
    task_add(name="Test task")

    result = task_delete("TASK-001")
    assert "Successfully deleted" in result["message"]

    # Verify task was deleted
    from clauxton.core.models import NotFoundError

    with pytest.raises(NotFoundError):
        task_manager.get("TASK-001")


def test_task_delete_nonexistent(task_manager: TaskManager) -> None:
    """Test deleting non-existent task raises error."""
    from clauxton.core.models import NotFoundError

    with pytest.raises(NotFoundError):
        task_delete("TASK-999")


def test_task_delete_with_dependents(task_manager: TaskManager) -> None:
    """Test deleting task with dependents fails."""
    task_add(name="Task 1")
    task_add(name="Task 2", depends_on=["TASK-001"])

    from clauxton.core.models import CycleDetectedError

    with pytest.raises(CycleDetectedError):
        task_delete("TASK-001")


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_task_workflow(task_manager: TaskManager) -> None:
    """Test complete task management workflow."""
    # 1. Add tasks
    task_add(name="Setup database", priority="high")
    task_add(
        name="Add API endpoint",
        depends_on=["TASK-001"],
        files=["src/api.py"],
    )

    # 2. List tasks
    tasks = task_list()
    assert len(tasks) == 2

    # 3. Get next task (should be TASK-001)
    next_task_result = task_next()
    assert next_task_result is not None
    assert next_task_result["id"] == "TASK-001"

    # 4. Start working on TASK-001
    task_update("TASK-001", status="in_progress")

    # 5. Complete TASK-001
    task_update("TASK-001", status="completed")

    # 6. Get next task (now TASK-002 is unblocked)
    next_task_result = task_next()
    assert next_task_result is not None
    assert next_task_result["id"] == "TASK-002"

    # 7. Get task details
    task_details = task_get("TASK-002")
    assert task_details["files_to_edit"] == ["src/api.py"]

    # 8. Complete TASK-002
    task_update("TASK-002", status="completed")

    # 9. No more tasks
    next_task_result = task_next()
    assert next_task_result is None

    # 10. Filter completed tasks
    completed = task_list(status="completed")
    assert len(completed) == 2
