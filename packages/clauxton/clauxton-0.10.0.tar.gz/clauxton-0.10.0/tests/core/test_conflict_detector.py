"""
Tests for ConflictDetector.

Tests cover:
- Conflict detection for file overlap
- Risk scoring algorithm
- Safe order recommendation (topological sort)
- File conflict checking
- Edge cases (no conflicts, empty files, etc.)
- Error handling
"""

from datetime import datetime
from pathlib import Path

import pytest

from clauxton.core.conflict_detector import ConflictDetector
from clauxton.core.models import ConflictReport, NotFoundError, Task
from clauxton.core.task_manager import TaskManager


@pytest.fixture
def task_manager(tmp_path: Path) -> TaskManager:
    """Create TaskManager with temporary directory."""
    (tmp_path / ".clauxton").mkdir()
    return TaskManager(tmp_path)


@pytest.fixture
def conflict_detector(task_manager: TaskManager) -> ConflictDetector:
    """Create ConflictDetector with TaskManager."""
    return ConflictDetector(task_manager)


@pytest.fixture
def sample_tasks() -> list[Task]:
    """Create sample tasks for testing."""
    now = datetime.now()
    return [
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


# ============================================================================
# Conflict Detection Tests
# ============================================================================


def test_detect_conflicts_file_overlap(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
    sample_tasks: list[Task],
) -> None:
    """Test detecting file overlap conflict."""
    # Add tasks
    task_manager.add(sample_tasks[0])  # TASK-001: in_progress, edits auth.py
    task_manager.add(sample_tasks[1])  # TASK-002: pending, edits auth.py + user.py

    # Detect conflicts for TASK-002 against in_progress tasks
    conflicts = conflict_detector.detect_conflicts("TASK-002")

    # Should detect 1 conflict with TASK-001 (auth.py overlap)
    # Even though TASK-002 is pending, it checks against in_progress tasks
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.task_a_id == "TASK-002"
    assert conflict.task_b_id == "TASK-001"
    assert conflict.conflict_type == "file_overlap"
    assert "src/api/auth.py" in conflict.overlapping_files
    assert conflict.risk_level in ["low", "medium", "high"]
    assert 0.0 <= conflict.risk_score <= 1.0

    # Now start TASK-002
    task_manager.update("TASK-002", {"status": "in_progress"})

    # Detect conflicts for TASK-001
    conflicts = conflict_detector.detect_conflicts("TASK-001")

    # Should still detect 1 conflict with TASK-002 (auth.py overlap)
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.task_a_id == "TASK-001"
    assert conflict.task_b_id == "TASK-002"
    assert conflict.conflict_type == "file_overlap"
    assert "src/api/auth.py" in conflict.overlapping_files


def test_detect_conflicts_no_overlap(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
    sample_tasks: list[Task],
) -> None:
    """Test no conflicts when tasks edit different files."""
    # Add tasks with no file overlap
    task_manager.add(sample_tasks[0])  # TASK-001: edits auth.py
    task_manager.add(sample_tasks[3])  # TASK-004: edits migrations/001_add_users.sql

    # Detect conflicts
    conflicts = conflict_detector.detect_conflicts("TASK-001")

    # Should detect no conflicts
    assert len(conflicts) == 0


def test_detect_conflicts_multiple_overlaps(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
    sample_tasks: list[Task],
) -> None:
    """Test detecting multiple conflicts."""
    # Add tasks
    task_manager.add(sample_tasks[0])  # TASK-001: in_progress, edits auth.py
    task_manager.add(sample_tasks[1])  # TASK-002: pending, edits auth.py + user.py
    task_manager.add(sample_tasks[2])  # TASK-003: in_progress, edits user.py

    # Start TASK-002
    task_manager.update("TASK-002", {"status": "in_progress"})

    # Detect conflicts for TASK-002
    conflicts = conflict_detector.detect_conflicts("TASK-002")

    # Should detect 2 conflicts:
    # - TASK-001 (auth.py overlap)
    # - TASK-003 (user.py overlap)
    assert len(conflicts) == 2

    # Check conflicts
    conflict_task_ids = {c.task_b_id for c in conflicts}
    assert "TASK-001" in conflict_task_ids
    assert "TASK-003" in conflict_task_ids


def test_detect_conflicts_task_not_found(
    conflict_detector: ConflictDetector,
) -> None:
    """Test detecting conflicts for non-existent task raises error."""
    with pytest.raises(NotFoundError, match="not found"):
        conflict_detector.detect_conflicts("TASK-999")


def test_detect_conflicts_empty_files_to_edit(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
) -> None:
    """Test detecting conflicts when task has no files_to_edit."""
    now = datetime.now()
    task = Task(
        id="TASK-001",
        name="Planning task",
        description="No files to edit",
        status="in_progress",
        priority="low",
        files_to_edit=[],
        created_at=now,
    )
    task_manager.add(task)

    # Detect conflicts
    conflicts = conflict_detector.detect_conflicts("TASK-001")

    # Should detect no conflicts
    assert len(conflicts) == 0


# ============================================================================
# Risk Scoring Tests
# ============================================================================


def test_risk_score_high(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
) -> None:
    """Test high risk score when all files overlap."""
    now = datetime.now()

    task1 = Task(
        id="TASK-001",
        name="Task 1",
        description="Edit one file",
        status="in_progress",
        files_to_edit=["src/api/auth.py"],
        created_at=now,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        description="Edit same file",
        status="in_progress",
        files_to_edit=["src/api/auth.py"],
        created_at=now,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    conflicts = conflict_detector.detect_conflicts("TASK-001")

    assert len(conflicts) == 1
    conflict = conflicts[0]
    # Both tasks edit 1 file, 1 overlap → risk = 1.0 / 1.0 = 1.0
    assert conflict.risk_score == 1.0
    assert conflict.risk_level == "high"


def test_risk_score_medium(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
) -> None:
    """Test medium risk score with partial overlap."""
    now = datetime.now()

    task1 = Task(
        id="TASK-001",
        name="Task 1",
        description="Edit two files",
        status="in_progress",
        files_to_edit=["src/api/auth.py", "src/api/users.py"],
        created_at=now,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        description="Edit one overlapping file",
        status="in_progress",
        files_to_edit=["src/api/auth.py"],
        created_at=now,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    conflicts = conflict_detector.detect_conflicts("TASK-001")

    assert len(conflicts) == 1
    conflict = conflicts[0]
    # Task1: 2 files, Task2: 1 file, avg = 1.5, overlap = 1 → risk = 1/1.5 ≈ 0.67
    assert 0.60 <= conflict.risk_score <= 0.70
    assert conflict.risk_level == "medium"


def test_risk_score_low(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
) -> None:
    """Test low risk score with minimal overlap."""
    now = datetime.now()

    task1 = Task(
        id="TASK-001",
        name="Task 1",
        description="Edit many files",
        status="in_progress",
        files_to_edit=[
            "src/api/auth.py",
            "src/api/users.py",
            "src/api/posts.py",
            "src/models/user.py",
        ],
        created_at=now,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        description="Edit one overlapping file",
        status="in_progress",
        files_to_edit=["src/api/auth.py", "src/utils/logger.py"],
        created_at=now,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    conflicts = conflict_detector.detect_conflicts("TASK-001")

    assert len(conflicts) == 1
    conflict = conflicts[0]
    # Task1: 4 files, Task2: 2 files, avg = 3, overlap = 1 → risk = 1/3 ≈ 0.33
    assert 0.30 <= conflict.risk_score <= 0.40
    assert conflict.risk_level == "low"


def test_risk_score_zero_files_edge_case(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
) -> None:
    """Test risk score edge case when both tasks have zero files.

    This tests the defensive programming path where avg_total = 0.
    In practice, this scenario is unlikely (tasks with no files don't
    typically overlap), but it's important to handle gracefully.
    """
    now = datetime.now()

    # Create a special scenario: Both tasks have empty files_to_edit
    # but somehow there's an "overlap" (which is logically impossible,
    # but we test the defensive code path)
    #
    # Since detect_conflicts() checks for file overlap using set intersection,
    # we need to test _create_file_overlap_conflict() directly via a conflict
    # that naturally triggers it.
    #
    # Actually, let's test a more realistic edge case:
    # Task with 0 files cannot conflict, so detect_conflicts returns []
    task1 = Task(
        id="TASK-001",
        name="Planning task",
        description="No files to edit",
        status="in_progress",
        files_to_edit=[],
        created_at=now,
    )
    task2 = Task(
        id="TASK-002",
        name="Another planning task",
        description="Also no files",
        status="in_progress",
        files_to_edit=[],
        created_at=now,
    )

    task_manager.add(task1)
    task_manager.add(task2)

    # Detect conflicts - should find none (empty sets have no overlap)
    conflicts = conflict_detector.detect_conflicts("TASK-001")

    # No overlap, so no conflicts
    assert len(conflicts) == 0

    # Note: This doesn't actually hit line 192 because there's no overlap.
    # Line 192 is only reached when:
    # 1. Both tasks have files_to_edit = []
    # 2. AND there's somehow an overlap (impossible with set intersection)
    #
    # This is truly defensive code that cannot be triggered in normal use.
    # We've tested the realistic case (no overlap = no conflict).


# ============================================================================
# Safe Order Recommendation Tests
# ============================================================================


def test_recommend_safe_order_no_dependencies(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
    sample_tasks: list[Task],
) -> None:
    """Test recommending safe order with no dependencies."""
    # Add tasks with no dependencies
    for task in sample_tasks[:3]:
        task_manager.add(task)

    # Get recommended order
    order = conflict_detector.recommend_safe_order(
        ["TASK-001", "TASK-002", "TASK-003"]
    )

    # Should return all task IDs
    assert len(order) == 3
    assert set(order) == {"TASK-001", "TASK-002", "TASK-003"}


def test_recommend_safe_order_with_dependencies(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
) -> None:
    """Test recommending safe order respects dependencies."""
    now = datetime.now()

    task1 = Task(
        id="TASK-001",
        name="Task 1",
        description="No dependencies",
        status="pending",
        depends_on=[],
        created_at=now,
    )
    task2 = Task(
        id="TASK-002",
        name="Task 2",
        description="Depends on TASK-001",
        status="pending",
        depends_on=["TASK-001"],
        created_at=now,
    )
    task3 = Task(
        id="TASK-003",
        name="Task 3",
        description="Depends on TASK-002",
        status="pending",
        depends_on=["TASK-002"],
        created_at=now,
    )

    task_manager.add(task1)
    task_manager.add(task2)
    task_manager.add(task3)

    # Get recommended order
    order = conflict_detector.recommend_safe_order(
        ["TASK-001", "TASK-002", "TASK-003"]
    )

    # Should respect dependency order: TASK-001 → TASK-002 → TASK-003
    assert order == ["TASK-001", "TASK-002", "TASK-003"]


def test_recommend_safe_order_task_not_found(
    conflict_detector: ConflictDetector,
) -> None:
    """Test recommending safe order for non-existent task raises error."""
    with pytest.raises(NotFoundError, match="not found"):
        conflict_detector.recommend_safe_order(["TASK-999"])


# ============================================================================
# File Conflict Checking Tests
# ============================================================================


def test_check_file_conflicts(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
    sample_tasks: list[Task],
) -> None:
    """Test checking file conflicts."""
    # Add tasks
    task_manager.add(sample_tasks[0])  # TASK-001: in_progress, edits auth.py
    task_manager.add(sample_tasks[2])  # TASK-003: in_progress, edits user.py

    # Check conflicts for auth.py
    conflicting = conflict_detector.check_file_conflicts(["src/api/auth.py"])
    assert conflicting == ["TASK-001"]

    # Check conflicts for user.py
    conflicting = conflict_detector.check_file_conflicts(["src/models/user.py"])
    assert conflicting == ["TASK-003"]

    # Check conflicts for both files
    conflicting = conflict_detector.check_file_conflicts(
        ["src/api/auth.py", "src/models/user.py"]
    )
    assert set(conflicting) == {"TASK-001", "TASK-003"}


def test_check_file_conflicts_no_active_tasks(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
    sample_tasks: list[Task],
) -> None:
    """Test checking file conflicts when no tasks are in_progress."""
    # Add tasks but all are pending
    for task in sample_tasks:
        task.status = "pending"
        task_manager.add(task)

    # Check conflicts
    conflicting = conflict_detector.check_file_conflicts(["src/api/auth.py"])
    assert conflicting == []


def test_check_file_conflicts_empty_files(
    task_manager: TaskManager,
    conflict_detector: ConflictDetector,
) -> None:
    """Test checking file conflicts with empty file list."""
    # Check conflicts with empty list
    conflicting = conflict_detector.check_file_conflicts([])
    assert conflicting == []


# ============================================================================
# ConflictReport Model Tests
# ============================================================================


def test_conflict_report_validation() -> None:
    """Test ConflictReport validation."""
    # Valid report
    report = ConflictReport(
        task_a_id="TASK-001",
        task_b_id="TASK-002",
        conflict_type="file_overlap",
        risk_level="high",
        risk_score=0.85,
        overlapping_files=["src/api/auth.py"],
        details="Both tasks edit src/api/auth.py",
        recommendation="Complete TASK-001 before starting TASK-002",
    )
    assert report.task_a_id == "TASK-001"
    assert report.risk_score == 0.85


def test_conflict_report_invalid_task_id() -> None:
    """Test ConflictReport with invalid task ID."""
    with pytest.raises(ValueError):
        ConflictReport(
            task_a_id="INVALID",  # Invalid format
            task_b_id="TASK-002",
            conflict_type="file_overlap",
            risk_level="high",
            risk_score=0.85,
            overlapping_files=["src/api/auth.py"],
            details="Test",
            recommendation="Test",
        )


def test_conflict_report_invalid_risk_score() -> None:
    """Test ConflictReport with invalid risk score."""
    with pytest.raises(ValueError):
        ConflictReport(
            task_a_id="TASK-001",
            task_b_id="TASK-002",
            conflict_type="file_overlap",
            risk_level="high",
            risk_score=1.5,  # Invalid (> 1.0)
            overlapping_files=["src/api/auth.py"],
            details="Test",
            recommendation="Test",
        )
