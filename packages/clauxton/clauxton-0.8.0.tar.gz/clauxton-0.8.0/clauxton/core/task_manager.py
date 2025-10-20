"""
Task Manager for Clauxton.

Provides CRUD operations for task management with YAML persistence.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from clauxton.core.models import (
    CycleDetectedError,
    DuplicateError,
    NotFoundError,
    Task,
    TaskPriorityType,
    TaskStatusType,
)
from clauxton.utils.file_utils import ensure_clauxton_dir
from clauxton.utils.yaml_utils import read_yaml, write_yaml


class TaskManager:
    """
    Manages tasks with YAML persistence.

    Provides CRUD operations for tasks, DAG validation,
    and dependency management.

    Example:
        >>> tm = TaskManager(Path.cwd())
        >>> task = Task(
        ...     id="TASK-001",
        ...     name="Setup database",
        ...     description="Create PostgreSQL schema",
        ...     status="pending",
        ...     created_at=datetime.now()
        ... )
        >>> tm.add(task)
        'TASK-001'
    """

    def __init__(self, root_dir: Path) -> None:
        """
        Initialize TaskManager.

        Args:
            root_dir: Project root directory containing .clauxton/
        """
        self.root_dir: Path = root_dir
        clauxton_dir = ensure_clauxton_dir(root_dir)
        self.tasks_file: Path = clauxton_dir / "tasks.yml"
        self._tasks_cache: Optional[List[Task]] = None
        self._ensure_tasks_exists()

    def add(self, task: Task) -> str:
        """
        Add new task.

        Args:
            task: Task to add

        Returns:
            Task ID

        Raises:
            DuplicateError: If task ID already exists
            CycleDetectedError: If adding task creates circular dependency

        Example:
            >>> task = Task(
            ...     id="TASK-001",
            ...     name="Setup database",
            ...     description="Create PostgreSQL schema",
            ...     status="pending",
            ...     created_at=datetime.now()
            ... )
            >>> tm.add(task)
            'TASK-001'
        """
        tasks = self._load_tasks()

        # Check for duplicate ID
        if any(t.id == task.id for t in tasks):
            raise DuplicateError(
                f"Task with ID '{task.id}' already exists. "
                "Use update() to modify existing tasks."
            )

        # Validate dependencies exist
        for dep_id in task.depends_on:
            if not any(t.id == dep_id for t in tasks):
                raise NotFoundError(
                    f"Dependency task '{dep_id}' not found. "
                    "Add dependencies before dependent tasks."
                )

        # Check for cycles
        if task.depends_on:
            self._validate_no_cycles(task.id, task.depends_on, tasks)

        # Add task
        tasks.append(task)
        self._save_tasks(tasks)
        self._invalidate_cache()

        return task.id

    def get(self, task_id: str) -> Task:
        """
        Get task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task

        Raises:
            NotFoundError: If task not found

        Example:
            >>> task = tm.get("TASK-001")
            >>> print(task.name)
            Setup database
        """
        tasks = self._load_tasks()

        for task in tasks:
            if task.id == task_id:
                return task

        raise NotFoundError(
            f"Task with ID '{task_id}' not found. "
            f"Use list_all() to see available tasks."
        )

    def update(self, task_id: str, updates: Dict[str, Any]) -> Task:
        """
        Update task fields.

        Args:
            task_id: Task ID to update
            updates: Dictionary of fields to update

        Returns:
            Updated Task

        Raises:
            NotFoundError: If task not found
            CycleDetectedError: If update creates circular dependency

        Example:
            >>> updated = tm.update("TASK-001", {
            ...     "status": "in_progress",
            ...     "started_at": datetime.now()
            ... })
            >>> print(updated.status)
            in_progress
        """
        tasks = self._load_tasks()
        task_index = None

        # Find task
        for i, task in enumerate(tasks):
            if task.id == task_id:
                task_index = i
                break

        if task_index is None:
            raise NotFoundError(f"Task with ID '{task_id}' not found.")

        # Get current task
        current_task = tasks[task_index]

        # Check for cycle if updating dependencies
        if "depends_on" in updates:
            new_deps = updates["depends_on"]
            # Validate new dependencies exist
            for dep_id in new_deps:
                if dep_id != task_id and not any(t.id == dep_id for t in tasks):
                    raise NotFoundError(
                        f"Dependency task '{dep_id}' not found. "
                        "Cannot add non-existent dependency."
                    )
            # Check for cycles with new dependencies
            if new_deps:
                self._validate_no_cycles(task_id, new_deps, tasks)

        # Create updated task
        task_dict = current_task.model_dump()
        task_dict.update(updates)
        updated_task = Task(**task_dict)

        # Replace task
        tasks[task_index] = updated_task
        self._save_tasks(tasks)
        self._invalidate_cache()

        return updated_task

    def delete(self, task_id: str) -> None:
        """
        Delete task.

        Args:
            task_id: Task ID to delete

        Raises:
            NotFoundError: If task not found

        Example:
            >>> tm.delete("TASK-001")
        """
        tasks = self._load_tasks()

        # Check if task exists
        task_exists = any(t.id == task_id for t in tasks)
        if not task_exists:
            raise NotFoundError(f"Task with ID '{task_id}' not found.")

        # Check if other tasks depend on this task
        dependents = [t for t in tasks if task_id in t.depends_on]
        if dependents:
            dependent_ids = [t.id for t in dependents]
            raise CycleDetectedError(
                f"Cannot delete task '{task_id}' because it has dependents: "
                f"{', '.join(dependent_ids)}. Delete dependents first."
            )

        # Remove task
        tasks = [t for t in tasks if t.id != task_id]
        self._save_tasks(tasks)
        self._invalidate_cache()

    def list_all(
        self,
        status: Optional[TaskStatusType] = None,
        priority: Optional[TaskPriorityType] = None,
    ) -> List[Task]:
        """
        List all tasks with optional filters.

        Args:
            status: Filter by status (pending, in_progress, completed, blocked)
            priority: Filter by priority (low, medium, high, critical)

        Returns:
            List of Task objects

        Example:
            >>> all_tasks = tm.list_all()
            >>> pending = tm.list_all(status="pending")
            >>> high_priority = tm.list_all(priority="high")
        """
        tasks = self._load_tasks()

        # Apply filters
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]

        return tasks

    def get_next_task(self) -> Optional[Task]:
        """
        Get next task to work on based on dependencies and priority.

        Returns the highest priority task that:
        1. Has status "pending"
        2. All dependencies are completed
        3. Is not blocked

        Returns:
            Next task to work on, or None if no tasks available

        Example:
            >>> next_task = tm.get_next_task()
            >>> if next_task:
            ...     print(f"Work on: {next_task.name}")
        """
        tasks = self._load_tasks()

        # Get pending tasks
        pending = [t for t in tasks if t.status == "pending"]

        # Filter tasks whose dependencies are all completed
        ready_tasks = []
        for task in pending:
            if not task.depends_on:
                # No dependencies, ready to work
                ready_tasks.append(task)
            else:
                # Check if all dependencies are completed
                deps_completed = all(
                    self.get(dep_id).status == "completed" for dep_id in task.depends_on
                )
                if deps_completed:
                    ready_tasks.append(task)

        if not ready_tasks:
            return None

        # Sort by priority: critical > high > medium > low
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        ready_tasks.sort(key=lambda t: priority_order[t.priority])

        return ready_tasks[0]

    def generate_task_id(self) -> str:
        """
        Generate next available task ID.

        Returns:
            Next task ID in format TASK-NNN

        Example:
            >>> task_id = tm.generate_task_id()
            >>> print(task_id)
            TASK-001
        """
        tasks = self._load_tasks()

        if not tasks:
            return "TASK-001"

        # Extract numeric parts and find max
        max_num = 0
        for task in tasks:
            num_str = task.id.split("-")[1]
            num = int(num_str)
            if num > max_num:
                max_num = num

        return f"TASK-{max_num + 1:03d}"

    def _validate_no_cycles(
        self, task_id: str, depends_on: List[str], tasks: List[Task]
    ) -> None:
        """
        Validate that adding dependencies doesn't create cycles.

        Uses DFS to detect cycles in the dependency graph.

        Args:
            task_id: ID of task being added/updated
            depends_on: List of task IDs this task depends on
            tasks: Current list of tasks

        Raises:
            CycleDetectedError: If cycle detected
        """
        # Build adjacency list (task_id -> list of tasks that depend on it)
        graph: Dict[str, List[str]] = {}
        for task in tasks:
            if task.id != task_id:  # Exclude the task being added/updated
                graph[task.id] = task.depends_on

        # Add the new task's dependencies
        graph[task_id] = depends_on

        # DFS to detect cycles
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for task_node_id in graph:
            if task_node_id not in visited:
                if has_cycle(task_node_id):
                    raise CycleDetectedError(
                        f"Adding dependencies {depends_on} to task '{task_id}' "
                        "would create a circular dependency. "
                        "Task dependency graph must be acyclic (DAG)."
                    )

    def _load_tasks(self) -> List[Task]:
        """
        Load tasks from YAML.

        Uses cache if available, otherwise reads from disk.

        Returns:
            List of Task objects
        """
        if self._tasks_cache is not None:
            return self._tasks_cache

        if not self.tasks_file.exists():
            return []

        data = read_yaml(self.tasks_file)

        if not data or "tasks" not in data:
            return []

        tasks = [Task(**task_data) for task_data in data["tasks"]]
        self._tasks_cache = tasks
        return tasks

    def _save_tasks(self, tasks: List[Task]) -> None:
        """
        Save tasks to YAML.

        Args:
            tasks: List of Task objects to save
        """
        data = {
            "version": "1.0",
            "project_name": self.root_dir.name,
            "tasks": [task.model_dump(mode="json") for task in tasks],
        }

        write_yaml(self.tasks_file, data)

    def _invalidate_cache(self) -> None:
        """Invalidate the tasks cache."""
        self._tasks_cache = None

    def _ensure_tasks_exists(self) -> None:
        """Ensure tasks.yml file exists with proper structure."""
        if not self.tasks_file.exists():
            self._save_tasks([])

    def infer_dependencies(self, task_id: str) -> List[str]:
        """
        Infer task dependencies based on file overlap.

        Finds all tasks that edit the same files as the given task
        and have been created earlier (potential dependencies).

        Args:
            task_id: Task ID to infer dependencies for

        Returns:
            List of task IDs that this task likely depends on

        Raises:
            NotFoundError: If task does not exist
        """
        task = self.get(task_id)
        task_files = set(task.files_to_edit)

        if not task_files:
            return []

        tasks = self._load_tasks()
        dependencies: List[str] = []

        for other_task in tasks:
            # Skip self
            if other_task.id == task_id:
                continue

            # Only consider earlier tasks as dependencies
            if other_task.created_at >= task.created_at:
                continue

            # Check for file overlap
            other_files = set(other_task.files_to_edit)
            if task_files & other_files:  # Intersection
                dependencies.append(other_task.id)

        return dependencies

    def apply_inferred_dependencies(
        self,
        task_id: str,
        auto_inferred: Optional[List[str]] = None,
    ) -> Task:
        """
        Apply inferred dependencies to a task.

        Args:
            task_id: Task ID to update
            auto_inferred: Optional list of inferred dependencies
                (if None, will infer automatically)

        Returns:
            Updated Task object

        Raises:
            NotFoundError: If task does not exist
            CycleDetectedError: If applying dependencies would create a cycle
        """
        if auto_inferred is None:
            auto_inferred = self.infer_dependencies(task_id)

        if not auto_inferred:
            return self.get(task_id)

        # Merge with existing dependencies (avoid duplicates)
        task = self.get(task_id)
        combined_deps = list(set(task.depends_on + auto_inferred))

        # Update with combined dependencies
        return self.update(task_id, {"depends_on": combined_deps})
