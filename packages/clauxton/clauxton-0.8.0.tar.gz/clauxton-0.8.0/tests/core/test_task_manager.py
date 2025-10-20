"""
Tests for TaskManager.

Tests cover:
- CRUD operations (add, get, update, delete, list)
- Task ID generation
- Dependency management
- Cycle detection
- Priority-based task recommendation
- YAML persistence
- Error handling
"""

from datetime import datetime
from pathlib import Path

import pytest

from clauxton.core.models import CycleDetectedError, DuplicateError, NotFoundError, Task
from clauxton.core.task_manager import TaskManager


@pytest.fixture
def task_manager(tmp_path: Path) -> TaskManager:
    """Create TaskManager with temporary directory."""
    (tmp_path / ".clauxton").mkdir()
    return TaskManager(tmp_path)


@pytest.fixture
def sample_task() -> Task:
    """Create sample task."""
    return Task(
        id="TASK-001",
        name="Setup database",
        description="Create PostgreSQL schema",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )


# ============================================================================
# CRUD Operations Tests
# ============================================================================


def test_add_task(task_manager: TaskManager, sample_task: Task) -> None:
    """Test adding a task."""
    task_id = task_manager.add(sample_task)

    assert task_id == "TASK-001"
    retrieved = task_manager.get("TASK-001")
    assert retrieved.name == "Setup database"
    assert retrieved.status == "pending"


def test_add_duplicate_task(task_manager: TaskManager, sample_task: Task) -> None:
    """Test adding duplicate task ID raises error."""
    task_manager.add(sample_task)

    with pytest.raises(DuplicateError, match="already exists"):
        task_manager.add(sample_task)


def test_get_task(task_manager: TaskManager, sample_task: Task) -> None:
    """Test getting a task by ID."""
    task_manager.add(sample_task)
    task = task_manager.get("TASK-001")

    assert task.id == "TASK-001"
    assert task.name == "Setup database"
    assert task.description == "Create PostgreSQL schema"


def test_get_nonexistent_task(task_manager: TaskManager) -> None:
    """Test getting non-existent task raises error."""
    with pytest.raises(NotFoundError, match="not found"):
        task_manager.get("TASK-999")


def test_update_task(task_manager: TaskManager, sample_task: Task) -> None:
    """Test updating task fields."""
    task_manager.add(sample_task)

    updated = task_manager.update(
        "TASK-001",
        {
            "status": "in_progress",
            "started_at": datetime.now(),
        },
    )

    assert updated.status == "in_progress"
    assert updated.started_at is not None


def test_update_nonexistent_task(task_manager: TaskManager) -> None:
    """Test updating non-existent task raises error."""
    with pytest.raises(NotFoundError, match="not found"):
        task_manager.update("TASK-999", {"status": "completed"})


def test_delete_task(task_manager: TaskManager, sample_task: Task) -> None:
    """Test deleting a task."""
    task_manager.add(sample_task)
    task_manager.delete("TASK-001")

    with pytest.raises(NotFoundError):
        task_manager.get("TASK-001")


def test_delete_nonexistent_task(task_manager: TaskManager) -> None:
    """Test deleting non-existent task raises error."""
    with pytest.raises(NotFoundError, match="not found"):
        task_manager.delete("TASK-999")


def test_list_all_tasks(task_manager: TaskManager) -> None:
    """Test listing all tasks."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        status="in_progress",
        priority="medium",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    tasks = task_manager.list_all()
    assert len(tasks) == 2
    assert any(t.id == "TASK-001" for t in tasks)
    assert any(t.id == "TASK-002" for t in tasks)


def test_list_tasks_by_status(task_manager: TaskManager) -> None:
    """Test filtering tasks by status."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        status="completed",
        priority="medium",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    pending = task_manager.list_all(status="pending")
    assert len(pending) == 1
    assert pending[0].id == "TASK-001"


def test_list_tasks_by_priority(task_manager: TaskManager) -> None:
    """Test filtering tasks by priority."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        status="pending",
        priority="low",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    high_priority = task_manager.list_all(priority="high")
    assert len(high_priority) == 1
    assert high_priority[0].id == "TASK-001"


# ============================================================================
# Dependency Management Tests
# ============================================================================


def test_add_task_with_valid_dependency(task_manager: TaskManager) -> None:
    """Test adding task with valid dependency."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        status="pending",
        priority="high",
        depends_on=["TASK-001"],
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    retrieved = task_manager.get("TASK-002")
    assert "TASK-001" in retrieved.depends_on


def test_add_task_with_invalid_dependency(task_manager: TaskManager) -> None:
    """Test adding task with non-existent dependency fails."""
    task = Task(
        id="TASK-001",
        name="Task 1",
        depends_on=["TASK-999"],  # Non-existent
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    with pytest.raises(NotFoundError, match="Dependency task.*not found"):
        task_manager.add(task)


def test_detect_circular_dependency_direct(task_manager: TaskManager) -> None:
    """Test detecting direct circular dependency (A -> A)."""
    task = Task(
        id="TASK-001",
        name="Task 1",
        depends_on=["TASK-001"],  # Depends on itself
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    # Should fail because TASK-001 doesn't exist yet
    with pytest.raises(NotFoundError):
        task_manager.add(task)


def test_detect_circular_dependency_indirect(task_manager: TaskManager) -> None:
    """Test detecting indirect circular dependency (A -> B -> A)."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        depends_on=["TASK-001"],
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    # Try to make TASK-001 depend on TASK-002 (creates cycle)
    with pytest.raises(CycleDetectedError, match="circular dependency"):
        task_manager.update("TASK-001", {"depends_on": ["TASK-002"]})


def test_delete_task_with_dependents(task_manager: TaskManager) -> None:
    """Test deleting task that has dependents fails."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        depends_on=["TASK-001"],
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    # Cannot delete TASK-001 because TASK-002 depends on it
    with pytest.raises(CycleDetectedError, match="has dependents"):
        task_manager.delete("TASK-001")


# ============================================================================
# Task ID Generation Tests
# ============================================================================


def test_generate_first_task_id(task_manager: TaskManager) -> None:
    """Test generating first task ID."""
    task_id = task_manager.generate_task_id()
    assert task_id == "TASK-001"


def test_generate_sequential_task_ids(task_manager: TaskManager) -> None:
    """Test generating sequential task IDs."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task_manager.add(task1)

    task_id2 = task_manager.generate_task_id()
    assert task_id2 == "TASK-002"

    task2 = Task(
        id=task_id2,
        name="Task 2",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task_manager.add(task2)

    task_id3 = task_manager.generate_task_id()
    assert task_id3 == "TASK-003"


# ============================================================================
# Task Recommendation Tests
# ============================================================================


def test_get_next_task_no_dependencies(task_manager: TaskManager) -> None:
    """Test getting next task when there are no dependencies."""
    task1 = Task(
        id="TASK-001",
        name="High priority task",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Low priority task",
        status="pending",
        priority="low",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    next_task = task_manager.get_next_task()
    assert next_task is not None
    assert next_task.id == "TASK-001"  # High priority first


def test_get_next_task_with_dependencies(task_manager: TaskManager) -> None:
    """Test getting next task respects dependencies."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2 (depends on 1)",
        status="pending",
        priority="critical",  # Higher priority but blocked
        depends_on=["TASK-001"],
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    next_task = task_manager.get_next_task()
    assert next_task is not None
    assert next_task.id == "TASK-001"  # TASK-002 is blocked


def test_get_next_task_when_dependency_completed(task_manager: TaskManager) -> None:
    """Test getting next task after dependency is completed."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="completed",  # Already done
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2 (depends on 1)",
        status="pending",
        priority="high",
        depends_on=["TASK-001"],
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    next_task = task_manager.get_next_task()
    assert next_task is not None
    assert next_task.id == "TASK-002"  # Now unblocked


def test_get_next_task_no_tasks_available(task_manager: TaskManager) -> None:
    """Test getting next task when no tasks are available."""
    task = Task(
        id="TASK-001",
        name="Task 1",
        status="completed",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task_manager.add(task)

    next_task = task_manager.get_next_task()
    assert next_task is None


# ============================================================================
# Dependency Inference Tests
# ============================================================================


def test_infer_dependencies_with_file_overlap(task_manager: TaskManager) -> None:
    """Test inferring dependencies based on file overlap."""
    # Add three tasks with overlapping files
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        files_to_edit=["src/main.py", "src/utils.py"],
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        files_to_edit=["src/main.py"],  # Overlaps with TASK-001
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task3 = Task(
        id="TASK-003",
        name="Task 3",
        files_to_edit=["src/other.py"],  # No overlap
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)
    task_manager.add(task3)

    # TASK-002 should infer dependency on TASK-001 (file overlap)
    inferred = task_manager.infer_dependencies("TASK-002")
    assert "TASK-001" in inferred

    # TASK-003 should not infer any dependencies (no overlap)
    inferred3 = task_manager.infer_dependencies("TASK-003")
    assert len(inferred3) == 0


def test_infer_dependencies_no_files(task_manager: TaskManager) -> None:
    """Test that tasks with no files have no inferred dependencies."""
    task = Task(
        id="TASK-001",
        name="Task without files",
        files_to_edit=[],
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task_manager.add(task)

    inferred = task_manager.infer_dependencies("TASK-001")
    assert len(inferred) == 0


def test_infer_dependencies_only_earlier_tasks(task_manager: TaskManager) -> None:
    """Test that only earlier tasks are considered as dependencies."""
    import time

    # Add task 1
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        files_to_edit=["src/main.py"],
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task_manager.add(task1)

    # Wait a bit to ensure different timestamps
    time.sleep(0.01)

    # Add task 2 (later)
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        files_to_edit=["src/main.py"],
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task_manager.add(task2)

    # TASK-002 should infer dependency on TASK-001
    inferred = task_manager.infer_dependencies("TASK-002")
    assert "TASK-001" in inferred

    # TASK-001 should NOT infer dependency on TASK-002 (later task)
    inferred1 = task_manager.infer_dependencies("TASK-001")
    assert "TASK-002" not in inferred1


def test_apply_inferred_dependencies(task_manager: TaskManager) -> None:
    """Test applying inferred dependencies to a task."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        files_to_edit=["src/main.py"],
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        files_to_edit=["src/main.py"],
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    # Apply inferred dependencies to TASK-002
    updated = task_manager.apply_inferred_dependencies("TASK-002")

    assert "TASK-001" in updated.depends_on


def test_apply_inferred_dependencies_merge_with_existing(
    task_manager: TaskManager,
) -> None:
    """Test that inferred dependencies merge with existing ones."""
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        files_to_edit=["src/main.py"],
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        files_to_edit=["src/utils.py"],
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )
    task3 = Task(
        id="TASK-003",
        name="Task 3",
        files_to_edit=["src/main.py", "src/utils.py"],
        depends_on=["TASK-001"],  # Manually added dependency
        status="pending",
        priority="high",
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
        actual_hours=None,
    )

    task_manager.add(task1)
    task_manager.add(task2)
    task_manager.add(task3)

    # Apply inferred dependencies to TASK-003
    updated = task_manager.apply_inferred_dependencies("TASK-003")

    # Should have both manual and inferred dependencies
    assert "TASK-001" in updated.depends_on  # Manual
    assert "TASK-002" in updated.depends_on  # Inferred (file overlap)


# ============================================================================
# YAML Persistence Tests
# ============================================================================


def test_tasks_persisted_to_yaml(task_manager: TaskManager, sample_task: Task) -> None:
    """Test tasks are persisted to YAML file."""
    task_manager.add(sample_task)

    # Create new TaskManager instance to force reload from disk
    new_tm = TaskManager(task_manager.root_dir)
    retrieved = new_tm.get("TASK-001")

    assert retrieved.name == "Setup database"


def test_yaml_file_structure(task_manager: TaskManager, sample_task: Task, tmp_path: Path) -> None:
    """Test YAML file has correct structure."""
    task_manager.add(sample_task)

    from clauxton.utils.yaml_utils import read_yaml

    data = read_yaml(task_manager.tasks_file)

    assert "version" in data
    assert data["version"] == "1.0"
    assert "project_name" in data
    assert "tasks" in data
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["id"] == "TASK-001"
