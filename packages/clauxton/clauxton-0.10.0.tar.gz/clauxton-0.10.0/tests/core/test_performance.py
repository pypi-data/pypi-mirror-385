"""
Performance tests for TaskManager batch operations.

Tests performance and memory efficiency of bulk task operations.
"""

import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from clauxton.core.models import Task
from clauxton.core.task_manager import TaskManager


def test_add_many_performance_100_tasks(tmp_path: Path) -> None:
    """
    Test add_many() performance with 100 tasks.

    Target: < 1 second for 100 tasks (25x faster than individual adds)
    """
    tm = TaskManager(tmp_path)

    # Generate 100 tasks
    tasks = []
    for i in range(1, 101):
        task = Task(
            id=f"TASK-{i:03d}",
            name=f"Task {i}",
            description=f"Description for task {i}",
            status="pending",
            priority="medium",
            depends_on=[],
            files_to_edit=[f"file{i}.py"],
            created_at=datetime.now(timezone.utc),
        )
        tasks.append(task)

    # Measure performance
    start_time = time.time()
    task_ids = tm.add_many(tasks)
    elapsed = time.time() - start_time

    # Verify results
    assert len(task_ids) == 100
    assert task_ids[0] == "TASK-001"
    assert task_ids[99] == "TASK-100"

    # Performance assertion: Should complete in < 1 second
    # Target: 0.2 seconds (25x faster than 5 seconds for individual adds)
    assert elapsed < 1.0, f"add_many took {elapsed:.2f}s, expected < 1.0s"

    # Verify all tasks were saved
    all_tasks = tm.list_all()
    assert len(all_tasks) == 100


def test_add_many_progress_callback(tmp_path: Path) -> None:
    """
    Test progress callback is called correctly during batch add.

    Progress callback should be called:
    - At completion (final count)
    - Every 5 tasks (if using incremental reporting in future)
    """
    tm = TaskManager(tmp_path)

    # Generate 12 tasks
    tasks = []
    for i in range(1, 13):
        task = Task(
            id=f"TASK-{i:03d}",
            name=f"Task {i}",
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        tasks.append(task)

    # Track progress calls
    progress_calls = []

    def progress_callback(current: int, total: int) -> None:
        progress_calls.append((current, total))

    # Add tasks with progress callback
    task_ids = tm.add_many(tasks, progress_callback=progress_callback)

    # Verify results
    assert len(task_ids) == 12
    assert len(progress_calls) >= 1  # At least final call

    # Verify final call shows completion
    final_call = progress_calls[-1]
    assert final_call == (12, 12), "Final progress should be (12, 12)"


def test_add_many_empty_list(tmp_path: Path) -> None:
    """
    Test add_many() with empty list.

    Should return empty list without error.
    """
    tm = TaskManager(tmp_path)

    task_ids = tm.add_many([])

    assert task_ids == []
    assert len(tm.list_all()) == 0


def test_add_many_with_dependencies(tmp_path: Path) -> None:
    """
    Test add_many() with tasks that have dependencies.

    Should validate dependencies across the batch.
    """
    tm = TaskManager(tmp_path)

    # Create tasks with dependencies
    tasks = [
        Task(
            id="TASK-001",
            name="Task 1",
            status="pending",
            depends_on=[],
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            id="TASK-002",
            name="Task 2",
            status="pending",
            depends_on=["TASK-001"],  # Depends on first task in batch
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            id="TASK-003",
            name="Task 3",
            status="pending",
            depends_on=["TASK-001", "TASK-002"],  # Depends on multiple
            created_at=datetime.now(timezone.utc),
        ),
    ]

    # Should succeed
    task_ids = tm.add_many(tasks)

    assert len(task_ids) == 3
    assert tm.get("TASK-002").depends_on == ["TASK-001"]
    assert tm.get("TASK-003").depends_on == ["TASK-001", "TASK-002"]


def test_add_many_duplicate_in_batch(tmp_path: Path) -> None:
    """
    Test add_many() detects duplicate IDs within batch.

    Should raise DuplicateError if same ID appears twice in batch.
    """
    from clauxton.core.models import DuplicateError

    tm = TaskManager(tmp_path)

    # Create tasks with duplicate ID
    tasks = [
        Task(
            id="TASK-001",
            name="Task 1",
            status="pending",
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            id="TASK-001",  # Duplicate!
            name="Task 1 Duplicate",
            status="pending",
            created_at=datetime.now(timezone.utc),
        ),
    ]

    # Should raise DuplicateError
    with pytest.raises(DuplicateError) as exc_info:
        tm.add_many(tasks)

    assert "Duplicate task ID 'TASK-001' found in batch" in str(exc_info.value)
    assert "positions 1 and 2" in str(exc_info.value)


def test_add_many_missing_dependency(tmp_path: Path) -> None:
    """
    Test add_many() detects missing dependencies.

    Should raise NotFoundError if dependency doesn't exist.
    """
    from clauxton.core.models import NotFoundError

    tm = TaskManager(tmp_path)

    # Create task with non-existent dependency
    tasks = [
        Task(
            id="TASK-001",
            name="Task 1",
            status="pending",
            depends_on=["TASK-999"],  # Doesn't exist!
            created_at=datetime.now(timezone.utc),
        ),
    ]

    # Should raise NotFoundError
    with pytest.raises(NotFoundError) as exc_info:
        tm.add_many(tasks)

    assert "Dependency task 'TASK-999' not found" in str(exc_info.value)


def test_add_many_circular_dependency(tmp_path: Path) -> None:
    """
    Test add_many() detects circular dependencies.

    Should raise CycleDetectedError if cycle exists in batch.
    """
    from clauxton.core.models import CycleDetectedError

    tm = TaskManager(tmp_path)

    # Create circular dependency: 1 -> 2 -> 3 -> 1
    tasks = [
        Task(
            id="TASK-001",
            name="Task 1",
            status="pending",
            depends_on=["TASK-003"],  # Circular!
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            id="TASK-002",
            name="Task 2",
            status="pending",
            depends_on=["TASK-001"],
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            id="TASK-003",
            name="Task 3",
            status="pending",
            depends_on=["TASK-002"],
            created_at=datetime.now(timezone.utc),
        ),
    ]

    # Should raise CycleDetectedError
    with pytest.raises(CycleDetectedError) as exc_info:
        tm.add_many(tasks)

    assert "circular dependencies" in str(exc_info.value).lower()


def test_import_yaml_uses_batch_operation(tmp_path: Path) -> None:
    """
    Test import_yaml() uses add_many() for batch operation.

    Should be fast for large imports.
    """
    tm = TaskManager(tmp_path)

    # Generate YAML for 50 tasks
    yaml_content = "tasks:\n"
    for i in range(1, 51):
        yaml_content += f"  - name: 'Task {i}'\n"
        yaml_content += f"    description: 'Description {i}'\n"
        yaml_content += "    priority: medium\n"

    # Measure performance
    start_time = time.time()
    result = tm.import_yaml(yaml_content, skip_confirmation=True)
    elapsed = time.time() - start_time

    # Verify results
    assert result["status"] == "success"
    assert result["imported"] == 50

    # Performance assertion: Should complete in < 1 second
    assert elapsed < 1.0, f"import_yaml took {elapsed:.2f}s, expected < 1.0s"

    # Verify all tasks were created
    all_tasks = tm.list_all()
    assert len(all_tasks) == 50
