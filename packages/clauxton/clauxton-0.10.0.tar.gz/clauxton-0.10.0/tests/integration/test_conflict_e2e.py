"""
End-to-End Integration Tests for Conflict Detection.

Tests cover:
- Real-world workflows with task lifecycle transitions
- Conflict detection during task state changes
- Multi-task scenarios with complex dependencies
- Performance benchmarks with large task sets
"""

import time
from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner

from clauxton.cli.main import cli
from clauxton.core.conflict_detector import ConflictDetector
from clauxton.core.models import Task
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


# ============================================================================
# End-to-End Workflow Tests
# ============================================================================


def test_e2e_task_lifecycle_with_conflicts(initialized_project: Path) -> None:
    """Test complete task lifecycle with conflict detection at each stage."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    detector = ConflictDetector(tm)
    now = datetime.now()

    # Scenario: Two developers working on authentication refactoring

    # Step 1: Developer A creates and starts TASK-001
    task1 = Task(
        id="TASK-001",
        name="Refactor JWT authentication",
        description="Update auth.py to use new JWT library",
        status="pending",
        priority="high",
        files_to_edit=["src/api/auth.py", "src/utils/jwt.py"],
        created_at=now,
    )
    tm.add(task1)

    # No conflicts yet (pending state)
    conflicts = detector.detect_conflicts("TASK-001")
    assert len(conflicts) == 0

    # Start TASK-001
    tm.update("TASK-001", {"status": "in_progress"})

    # Step 2: Developer B creates TASK-002 (overlapping files)
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

    # Check conflicts before starting TASK-002
    conflicts = detect_conflicts("TASK-002")
    assert conflicts["conflict_count"] == 1
    assert conflicts["conflicts"][0]["task_b_id"] == "TASK-001"
    assert "src/api/auth.py" in conflicts["conflicts"][0]["overlapping_files"]
    assert conflicts["conflicts"][0]["risk_level"] in ["medium", "high"]

    # Developer B decides to work on non-conflicting task instead
    # Step 3: Developer B creates TASK-003 (no overlap)
    task3 = Task(
        id="TASK-003",
        name="Update user profile page",
        description="Add new fields to profile UI",
        status="pending",
        priority="low",
        files_to_edit=["src/components/UserProfile.tsx"],
        created_at=now,
    )
    tm.add(task3)

    # No conflicts for TASK-003
    conflicts = detect_conflicts("TASK-003")
    assert conflicts["conflict_count"] == 0

    # Start TASK-003
    tm.update("TASK-003", {"status": "in_progress"})

    # Step 4: Developer A completes TASK-001
    tm.update("TASK-001", {"status": "completed"})

    # Now TASK-002 has no conflicts
    conflicts = detect_conflicts("TASK-002")
    assert conflicts["conflict_count"] == 0

    # Step 5: Developer B can now safely start TASK-002
    tm.update("TASK-002", {"status": "in_progress"})

    # Verify final state
    all_tasks = tm.list_all()
    assert len([t for t in all_tasks if t.status == "completed"]) == 1
    assert len([t for t in all_tasks if t.status == "in_progress"]) == 2


def test_e2e_safe_order_with_complex_dependencies(
    initialized_project: Path,
) -> None:
    """Test safe order recommendation with complex dependency graph."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    now = datetime.now()

    # Scenario: Database migration with dependencies
    # TASK-001: Add new table (no deps)
    # TASK-002: Add columns to existing table (no deps)
    # TASK-003: Create foreign key (depends on TASK-001, TASK-002)
    # TASK-004: Update ORM models (depends on TASK-003)
    # TASK-005: Add API endpoints (depends on TASK-004)

    tasks = [
        Task(
            id="TASK-001",
            name="Add users table",
            status="pending",
            files_to_edit=["migrations/001_add_users.sql"],
            depends_on=[],
            created_at=now,
        ),
        Task(
            id="TASK-002",
            name="Add posts table",
            status="pending",
            files_to_edit=["migrations/002_add_posts.sql"],
            depends_on=[],
            created_at=now,
        ),
        Task(
            id="TASK-003",
            name="Add foreign keys",
            status="pending",
            files_to_edit=["migrations/003_add_foreign_keys.sql"],
            depends_on=["TASK-001", "TASK-002"],
            created_at=now,
        ),
        Task(
            id="TASK-004",
            name="Update ORM models",
            status="pending",
            files_to_edit=["src/models/user.py", "src/models/post.py"],
            depends_on=["TASK-003"],
            created_at=now,
        ),
        Task(
            id="TASK-005",
            name="Add API endpoints",
            status="pending",
            files_to_edit=["src/api/users.py", "src/api/posts.py"],
            depends_on=["TASK-004"],
            created_at=now,
        ),
    ]

    for task in tasks:
        tm.add(task)

    # Get recommended order
    task_ids = ["TASK-001", "TASK-002", "TASK-003", "TASK-004", "TASK-005"]
    result = recommend_safe_order(task_ids)

    order = result["recommended_order"]
    assert len(order) == 5

    # Verify dependency order is respected
    idx_001 = order.index("TASK-001")
    idx_002 = order.index("TASK-002")
    idx_003 = order.index("TASK-003")
    idx_004 = order.index("TASK-004")
    idx_005 = order.index("TASK-005")

    # TASK-003 must come after both TASK-001 and TASK-002
    assert idx_003 > idx_001
    assert idx_003 > idx_002

    # TASK-004 must come after TASK-003
    assert idx_004 > idx_003

    # TASK-005 must come after TASK-004
    assert idx_005 > idx_004


def test_e2e_file_availability_check_workflow(
    initialized_project: Path,
) -> None:
    """Test checking file availability before starting work."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    now = datetime.now()

    # Scenario: Developer wants to edit multiple files

    # Step 1: Create some in-progress tasks
    task1 = Task(
        id="TASK-001",
        name="Refactor auth",
        status="in_progress",
        files_to_edit=["src/api/auth.py", "src/utils/jwt.py"],
        created_at=now,
    )
    task2 = Task(
        id="TASK-002",
        name="Update user model",
        status="in_progress",
        files_to_edit=["src/models/user.py"],
        created_at=now,
    )
    tm.add(task1)
    tm.add(task2)

    # Step 2: Developer wants to work on these files
    files_to_check = [
        "src/api/auth.py",  # Locked by TASK-001
        "src/models/user.py",  # Locked by TASK-002
        "src/api/posts.py",  # Available
    ]

    result = check_file_conflicts(files_to_check)

    # Verify conflict detection
    assert result["file_count"] == 3
    assert set(result["files"]) == set(files_to_check)
    assert set(result["conflicting_tasks"]) == {"TASK-001", "TASK-002"}
    assert "2 in_progress task(s)" in result["message"]

    # Step 3: Check only available files
    available_files = ["src/api/posts.py", "src/utils/logger.py"]
    result2 = check_file_conflicts(available_files)

    assert result2["file_count"] == 2
    assert result2["conflicting_tasks"] == []
    assert result2["all_available"] is True
    assert "available" in result2["message"]


def test_e2e_batch_task_planning(initialized_project: Path) -> None:
    """Test planning optimal order for batch of tasks."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    now = datetime.now()

    # Scenario: Sprint planning with 10 tasks
    tasks = [
        # Backend tasks
        Task(
            id="TASK-001",
            name="Add API endpoint",
            status="pending",
            files_to_edit=["src/api/users.py"],
            created_at=now,
        ),
        Task(
            id="TASK-002",
            name="Add validation",
            status="pending",
            files_to_edit=["src/api/users.py", "src/utils/validators.py"],
            depends_on=["TASK-001"],
            created_at=now,
        ),
        # Frontend tasks
        Task(
            id="TASK-003",
            name="Create user form",
            status="pending",
            files_to_edit=["src/components/UserForm.tsx"],
            created_at=now,
        ),
        Task(
            id="TASK-004",
            name="Add form validation",
            status="pending",
            files_to_edit=["src/components/UserForm.tsx"],
            depends_on=["TASK-003"],
            created_at=now,
        ),
        # Database tasks
        Task(
            id="TASK-005",
            name="Create migration",
            status="pending",
            files_to_edit=["migrations/001_users.sql"],
            created_at=now,
        ),
        Task(
            id="TASK-006",
            name="Update models",
            status="pending",
            files_to_edit=["src/models/user.py"],
            depends_on=["TASK-005"],
            created_at=now,
        ),
        # Testing tasks
        Task(
            id="TASK-007",
            name="Add API tests",
            status="pending",
            files_to_edit=["tests/api/test_users.py"],
            depends_on=["TASK-002"],
            created_at=now,
        ),
        Task(
            id="TASK-008",
            name="Add component tests",
            status="pending",
            files_to_edit=["tests/components/test_UserForm.tsx"],
            depends_on=["TASK-004"],
            created_at=now,
        ),
        # Documentation
        Task(
            id="TASK-009",
            name="Update API docs",
            status="pending",
            files_to_edit=["docs/api.md"],
            depends_on=["TASK-002", "TASK-007"],
            created_at=now,
        ),
        # Integration task
        Task(
            id="TASK-010",
            name="Integration testing",
            status="pending",
            files_to_edit=["tests/integration/test_user_flow.py"],
            depends_on=["TASK-007", "TASK-008"],
            created_at=now,
        ),
    ]

    for task in tasks:
        tm.add(task)

    # Get recommended order
    task_ids = [f"TASK-{i:03d}" for i in range(1, 11)]
    result = recommend_safe_order(task_ids)

    order = result["recommended_order"]
    assert len(order) == 10
    assert set(order) == set(task_ids)

    # Verify key dependencies are respected
    # TASK-002 must come after TASK-001
    assert order.index("TASK-002") > order.index("TASK-001")

    # TASK-004 must come after TASK-003
    assert order.index("TASK-004") > order.index("TASK-003")

    # TASK-006 must come after TASK-005
    assert order.index("TASK-006") > order.index("TASK-005")

    # TASK-007 must come after TASK-002
    assert order.index("TASK-007") > order.index("TASK-002")

    # TASK-009 must come after both TASK-002 and TASK-007
    idx_009 = order.index("TASK-009")
    assert idx_009 > order.index("TASK-002")
    assert idx_009 > order.index("TASK-007")

    # TASK-008 must come after TASK-004
    assert order.index("TASK-008") > order.index("TASK-004")

    # TASK-010 depends on TASK-007 and TASK-008, so must come after both
    idx_010 = order.index("TASK-010")
    assert idx_010 > order.index("TASK-007")
    assert idx_010 > order.index("TASK-008")

    # Either TASK-009 or TASK-010 can be last (both have deep dependency chains)
    assert order[-1] in ["TASK-009", "TASK-010"]


# ============================================================================
# Performance Benchmark Tests
# ============================================================================


def test_performance_detect_conflicts_50_tasks(
    initialized_project: Path,
) -> None:
    """Benchmark conflict detection with 50 tasks."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    detector = ConflictDetector(tm)
    now = datetime.now()

    # Create 50 tasks with realistic file overlap patterns
    # Pattern: 10 tasks per "module", each module has 5 shared files
    modules = ["auth", "users", "posts", "comments", "notifications"]
    tasks = []

    for i in range(50):
        module = modules[i // 10]
        task_num = i % 10

        # Each task edits 2-3 files in its module
        files = [
            f"src/api/{module}.py",
            f"src/models/{module}.py",
        ]
        if task_num % 2 == 0:
            files.append(f"src/utils/{module}_helpers.py")

        task = Task(
            id=f"TASK-{i+1:03d}",
            name=f"Task {i+1} for {module}",
            status="in_progress" if i % 5 == 0 else "pending",
            files_to_edit=files,
            created_at=now,
        )
        tasks.append(task)
        tm.add(task)

    # Benchmark: Detect conflicts for a task in the middle
    target_task_id = "TASK-025"

    start_time = time.perf_counter()
    conflicts = detector.detect_conflicts(target_task_id)
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000

    # Performance assertion: Should complete in < 150ms (allowing for system variability)
    assert elapsed_ms < 150, f"Detection took {elapsed_ms:.2f}ms, expected < 150ms"

    # Functional assertion: Should detect conflicts with tasks in same module
    # TASK-025 is in "posts" module (index 24, module index 2)
    # in_progress tasks: TASK-001, TASK-006, TASK-011, TASK-016, TASK-021,
    #                    TASK-026, TASK-031, TASK-036, TASK-041, TASK-046
    # TASK-021 (index 20, module 2) is in posts and in_progress
    assert len(conflicts) >= 1


def test_performance_recommend_safe_order_50_tasks(
    initialized_project: Path,
) -> None:
    """Benchmark safe order recommendation with 50 tasks."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    detector = ConflictDetector(tm)
    now = datetime.now()

    # Create 50 tasks with chain dependencies
    tasks = []
    for i in range(50):
        depends_on = []
        if i > 0 and i % 10 != 0:
            # Every task depends on previous, except every 10th task
            depends_on = [f"TASK-{i:03d}"]

        task = Task(
            id=f"TASK-{i+1:03d}",
            name=f"Task {i+1}",
            status="pending",
            files_to_edit=[f"src/module_{i // 10}.py"],
            depends_on=depends_on,
            created_at=now,
        )
        tasks.append(task)
        tm.add(task)

    # Benchmark: Get safe order for all 50 tasks
    task_ids = [f"TASK-{i+1:03d}" for i in range(50)]

    start_time = time.perf_counter()
    order = detector.recommend_safe_order(task_ids)
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000

    # Performance assertion: Should complete in < 200ms
    assert elapsed_ms < 200, f"Ordering took {elapsed_ms:.2f}ms, expected < 200ms"

    # Functional assertion: Should return all tasks
    assert len(order) == 50
    assert set(order) == set(task_ids)


def test_performance_check_file_conflicts_100_files(
    initialized_project: Path,
) -> None:
    """Benchmark file conflict check with 100 files."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    detector = ConflictDetector(tm)
    now = datetime.now()

    # Create 20 in_progress tasks, each editing 5 files
    for i in range(20):
        files = [f"src/module_{i}/file_{j}.py" for j in range(5)]
        task = Task(
            id=f"TASK-{i+1:03d}",
            name=f"Task {i+1}",
            status="in_progress",
            files_to_edit=files,
            created_at=now,
        )
        tm.add(task)

    # Benchmark: Check conflicts for 100 files (mix of locked and available)
    files_to_check = []
    # First 100 files from tasks (all locked)
    for i in range(20):
        files_to_check.extend([f"src/module_{i}/file_{j}.py" for j in range(5)])

    start_time = time.perf_counter()
    conflicting_tasks = detector.check_file_conflicts(files_to_check)
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000

    # Performance assertion: Should complete in < 100ms (allowing for system variability)
    assert elapsed_ms < 100, f"File check took {elapsed_ms:.2f}ms, expected < 100ms"

    # Functional assertion: Should find all 20 tasks
    assert len(conflicting_tasks) == 20


# ============================================================================
# Edge Case Tests
# ============================================================================


def test_e2e_concurrent_task_updates(initialized_project: Path) -> None:
    """Test conflict detection during rapid task status changes."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    now = datetime.now()

    # Create 3 tasks editing the same file
    for i in range(1, 4):
        task = Task(
            id=f"TASK-{i:03d}",
            name=f"Task {i}",
            status="pending",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        tm.add(task)

    # Simulate rapid status changes
    # Start TASK-001
    tm.update("TASK-001", {"status": "in_progress"})
    conflicts = detect_conflicts("TASK-002")
    assert conflicts["conflict_count"] == 1

    # Complete TASK-001, start TASK-002 (simulating quick completion)
    tm.update("TASK-001", {"status": "completed"})
    tm.update("TASK-002", {"status": "in_progress"})

    # TASK-003 should now conflict with TASK-002, not TASK-001
    conflicts = detect_conflicts("TASK-003")
    assert conflicts["conflict_count"] == 1
    assert conflicts["conflicts"][0]["task_b_id"] == "TASK-002"

    # Complete TASK-002, start TASK-003
    tm.update("TASK-002", {"status": "completed"})
    tm.update("TASK-003", {"status": "in_progress"})

    # No conflicts now
    conflicts = detect_conflicts("TASK-003")
    assert conflicts["conflict_count"] == 0


def test_e2e_empty_files_to_edit(initialized_project: Path) -> None:
    """Test conflict detection with tasks that have no files_to_edit."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    now = datetime.now()

    # Create tasks with empty files_to_edit (e.g., planning tasks)
    task1 = Task(
        id="TASK-001",
        name="Planning task",
        status="in_progress",
        files_to_edit=[],
        created_at=now,
    )
    task2 = Task(
        id="TASK-002",
        name="Another planning task",
        status="pending",
        files_to_edit=[],
        created_at=now,
    )
    task3 = Task(
        id="TASK-003",
        name="Code task",
        status="pending",
        files_to_edit=["src/api/auth.py"],
        created_at=now,
    )

    tm.add(task1)
    tm.add(task2)
    tm.add(task3)

    # Planning tasks should have no conflicts
    conflicts = detect_conflicts("TASK-002")
    assert conflicts["conflict_count"] == 0

    # Code task should have no conflicts with planning tasks
    conflicts = detect_conflicts("TASK-003")
    assert conflicts["conflict_count"] == 0


def test_e2e_blocked_tasks_excluded_from_conflicts(
    initialized_project: Path,
) -> None:
    """Test that blocked tasks are not considered for conflicts."""
    import os

    os.chdir(initialized_project)

    tm = TaskManager(Path.cwd())
    now = datetime.now()

    # Create tasks with same files but different statuses
    task1 = Task(
        id="TASK-001",
        name="Task 1",
        status="blocked",
        files_to_edit=["src/api/auth.py"],
        created_at=now,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        status="pending",
        files_to_edit=["src/api/auth.py"],
        created_at=now,
    )

    tm.add(task1)
    tm.add(task2)

    # TASK-002 should not conflict with blocked TASK-001
    conflicts = detect_conflicts("TASK-002")
    assert conflicts["conflict_count"] == 0

    # File check should not include blocked tasks
    result = check_file_conflicts(["src/api/auth.py"])
    assert result["conflicting_tasks"] == []
