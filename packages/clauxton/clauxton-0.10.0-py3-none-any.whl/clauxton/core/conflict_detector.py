"""
Conflict Detection for Clauxton.

Detects potential conflicts between tasks based on file overlap,
dependency violations, and other risk factors.
"""

from typing import List, Literal

from clauxton.core.models import ConflictReport, Task
from clauxton.core.task_manager import TaskManager


class ConflictDetector:
    """
    Detect potential conflicts between tasks.

    Analyzes tasks to identify file overlap conflicts, dependency violations,
    and other coordination issues that could lead to merge conflicts or
    workflow problems.

    Example:
        >>> from pathlib import Path
        >>> tm = TaskManager(Path.cwd())
        >>> detector = ConflictDetector(tm)
        >>> conflicts = detector.detect_conflicts("TASK-001")
        >>> if conflicts:
        ...     print(f"Found {len(conflicts)} conflict(s)")
    """

    def __init__(self, task_manager: TaskManager) -> None:
        """
        Initialize ConflictDetector.

        Args:
            task_manager: TaskManager instance for task data access
        """
        self.task_manager = task_manager

    def detect_conflicts(self, task_id: str) -> List[ConflictReport]:
        """
        Detect conflicts for a specific task.

        Analyzes the given task against all in_progress tasks to identify
        potential conflicts based on file overlap.

        Args:
            task_id: Task ID to check for conflicts

        Returns:
            List of ConflictReport objects (empty if no conflicts)

        Raises:
            NotFoundError: If task_id not found

        Example:
            >>> conflicts = detector.detect_conflicts("TASK-001")
            >>> for conflict in conflicts:
            ...     print(f"{conflict.risk_level}: {conflict.details}")
        """
        task = self.task_manager.get(task_id)
        conflicts: List[ConflictReport] = []

        # Get all in_progress tasks
        all_tasks = self.task_manager.list_all()
        active_tasks = [t for t in all_tasks if t.status == "in_progress"]

        for other_task in active_tasks:
            # Skip self
            if other_task.id == task_id:
                continue

            # Check file overlap
            overlap = set(task.files_to_edit) & set(other_task.files_to_edit)
            if overlap:
                conflict = self._create_file_overlap_conflict(
                    task, other_task, list(overlap)
                )
                conflicts.append(conflict)

        return conflicts

    def recommend_safe_order(self, task_ids: List[str]) -> List[str]:
        """
        Recommend safe execution order for tasks to minimize conflicts.

        Uses topological sort based on dependencies and conflict analysis
        to suggest an order that minimizes merge conflicts.

        Args:
            task_ids: List of task IDs to order

        Returns:
            List of task IDs in recommended execution order

        Raises:
            NotFoundError: If any task_id not found

        Example:
            >>> task_ids = ["TASK-001", "TASK-002", "TASK-003"]
            >>> order = detector.recommend_safe_order(task_ids)
            >>> print(" → ".join(order))
        """
        # Get all tasks
        tasks = [self.task_manager.get(tid) for tid in task_ids]

        # Topological sort based on dependencies
        ordered: List[str] = []
        remaining = set(task_ids)

        while remaining:
            # Find tasks with no dependencies in remaining set
            ready = [
                tid
                for tid in remaining
                if all(
                    dep not in remaining or dep in ordered
                    for dep in next(t for t in tasks if t.id == tid).depends_on
                )
            ]

            if not ready:
                # Circular dependency or all remaining have unmet deps
                # Just add them in original order
                ordered.extend(sorted(remaining))
                break

            # Add tasks with fewest file conflicts first
            ready_sorted = self._sort_by_conflict_potential(
                ready, [t for t in tasks if t.id in ready]
            )
            for tid in ready_sorted:
                ordered.append(tid)
                remaining.remove(tid)

        return ordered

    def check_file_conflicts(self, files: List[str]) -> List[str]:
        """
        Check which tasks are currently editing the given files.

        Args:
            files: List of file paths to check

        Returns:
            List of task IDs that have in_progress status and
            overlap with the given files

        Example:
            >>> files = ["src/api/auth.py"]
            >>> conflicting_tasks = detector.check_file_conflicts(files)
            >>> if conflicting_tasks:
            ...     print(f"Files in use by: {conflicting_tasks}")
        """
        all_tasks = self.task_manager.list_all()
        active_tasks = [t for t in all_tasks if t.status == "in_progress"]

        conflicting_task_ids: List[str] = []
        file_set = set(files)

        for task in active_tasks:
            task_files = set(task.files_to_edit)
            if file_set & task_files:
                conflicting_task_ids.append(task.id)

        return conflicting_task_ids

    def _create_file_overlap_conflict(
        self, task_a: Task, task_b: Task, overlapping_files: List[str]
    ) -> ConflictReport:
        """
        Create ConflictReport for file overlap conflict.

        Args:
            task_a: First task
            task_b: Second task
            overlapping_files: Files modified by both tasks

        Returns:
            ConflictReport with calculated risk score
        """
        # Calculate risk score based on number of overlapping files
        # and total files being edited
        num_overlap = len(overlapping_files)
        total_files_a = len(task_a.files_to_edit)
        total_files_b = len(task_b.files_to_edit)

        # Risk score: higher overlap = higher risk
        # Formula: (overlap_count) / (avg_total_files)
        avg_total = (total_files_a + total_files_b) / 2
        if avg_total == 0:
            risk_score = 0.0
        else:
            risk_score = min(1.0, num_overlap / avg_total)

        # Determine risk level based on score
        risk_level: Literal["low", "medium", "high"]
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Generate details and recommendation
        file_list = ", ".join(overlapping_files)
        details = (
            f"Both tasks edit: {file_list}. "
            f"Task {task_a.id} has {total_files_a} file(s), "
            f"Task {task_b.id} has {total_files_b} file(s)."
        )

        recommendation = (
            f"Complete {task_a.id} before starting {task_b.id}, "
            f"or coordinate changes in {file_list}."
        )

        return ConflictReport(
            task_a_id=task_a.id,
            task_b_id=task_b.id,
            conflict_type="file_overlap",
            risk_level=risk_level,
            risk_score=round(risk_score, 2),
            overlapping_files=overlapping_files,
            details=details,
            recommendation=recommendation,
        )

    def _sort_by_conflict_potential(
        self, task_ids: List[str], tasks: List[Task]
    ) -> List[str]:
        """
        Sort tasks by conflict potential (fewest conflicts first).

        Args:
            task_ids: Task IDs to sort
            tasks: Task objects

        Returns:
            Sorted list of task IDs
        """
        # Calculate conflict score for each task
        # (number of files that overlap with other tasks)
        scores = {}
        for tid in task_ids:
            task = next(t for t in tasks if t.id == tid)
            conflict_score = 0

            for other_tid in task_ids:
                if tid == other_tid:
                    continue
                other = next(t for t in tasks if t.id == other_tid)
                overlap = set(task.files_to_edit) & set(other.files_to_edit)
                conflict_score += len(overlap)

            scores[tid] = conflict_score

        # Sort by score (ascending - fewer conflicts first)
        return sorted(task_ids, key=lambda tid: scores[tid])
