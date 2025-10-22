"""
Task Manager for Clauxton.

Provides CRUD operations for task management with YAML persistence.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

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

# Type alias for progress callback
ProgressCallback = Callable[[int, int], None]


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

    def add_many(
        self,
        tasks_to_add: List[Task],
        progress_callback: Optional[ProgressCallback] = None,
    ) -> List[str]:
        """
        Add multiple tasks efficiently with optional progress reporting.

        This method optimizes bulk task creation by:
        1. Validating all tasks first
        2. Writing to disk only once (batch operation)
        3. Reporting progress every 5 tasks

        Args:
            tasks_to_add: List of Task objects to add
            progress_callback: Optional callback function(current, total)
                              Called every 5 tasks. Example:
                              lambda current, total: print(f"{current}/{total}")

        Returns:
            List of task IDs created

        Raises:
            DuplicateError: If any task ID already exists
            NotFoundError: If any dependency task not found
            CycleDetectedError: If adding tasks creates circular dependency

        Example:
            >>> tasks = [
            ...     Task(id="TASK-001", name="Setup", status="pending", created_at=datetime.now()),
            ...     Task(id="TASK-002", name="Build", status="pending", created_at=datetime.now())
            ... ]
            >>> def report(curr, total):
            ...     print(f"Progress: {curr}/{total}")
            >>> task_ids = tm.add_many(tasks, progress_callback=report)
            Progress: 2/2
            >>> task_ids
            ['TASK-001', 'TASK-002']
        """
        if not tasks_to_add:
            return []

        existing_tasks = self._load_tasks()
        existing_ids = {t.id for t in existing_tasks}

        # Validate all tasks first (fail fast)
        for i, task in enumerate(tasks_to_add, 1):
            # Check for duplicate ID
            if task.id in existing_ids:
                raise DuplicateError(
                    f"Task with ID '{task.id}' already exists. "
                    "Use update() to modify existing tasks."
                )

            # Check for duplicates within the batch
            for j, other_task in enumerate(tasks_to_add[:i - 1], 1):
                if task.id == other_task.id:
                    raise DuplicateError(
                        f"Duplicate task ID '{task.id}' found in batch "
                        f"(positions {j} and {i}). Each task must have unique ID."
                    )

            # Validate dependencies exist (in existing or in batch)
            batch_ids = {t.id for t in tasks_to_add}
            all_available_ids = existing_ids | batch_ids

            for dep_id in task.depends_on:
                if dep_id not in all_available_ids:
                    raise NotFoundError(
                        f"Task '{task.name}' (ID: {task.id}): "
                        f"Dependency task '{dep_id}' not found. "
                        "Add dependencies before dependent tasks."
                    )

        # Check for cycles with all tasks (existing + new)
        temp_graph = {t.id: t.depends_on for t in existing_tasks}
        for task in tasks_to_add:
            temp_graph[task.id] = task.depends_on

        cycle_errors = self._detect_cycles_in_graph(temp_graph)
        if cycle_errors:
            raise CycleDetectedError(
                f"Adding tasks would create circular dependencies: "
                f"{', '.join(cycle_errors)}"
            )

        # All validations passed - perform batch write
        all_tasks = existing_tasks + tasks_to_add
        self._save_tasks(all_tasks)
        self._invalidate_cache()

        # Collect task IDs
        task_ids = [t.id for t in tasks_to_add]

        # Report progress (call callback for final progress)
        if progress_callback:
            progress_callback(len(tasks_to_add), len(tasks_to_add))

        return task_ids

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

    def import_yaml(
        self,
        yaml_content: str,
        dry_run: bool = False,
        skip_validation: bool = False,
        skip_confirmation: bool = False,
        confirmation_threshold: int = 10,
        on_error: str = "rollback",
    ) -> Dict[str, Any]:
        """
        Import multiple tasks from YAML content.

        This method enables bulk task creation from YAML format,
        with validation and circular dependency detection.

        Args:
            yaml_content: YAML string containing tasks
            dry_run: If True, validate only without creating tasks
            skip_validation: If True, skip dependency validation
            skip_confirmation: If True, skip confirmation prompt (default: False)
            confirmation_threshold: Number of tasks to trigger confirmation (default: 10)
            on_error: Error recovery strategy (default: "rollback")
                - "rollback": Revert all changes on error (transactional)
                - "skip": Skip failed tasks, continue with others
                - "abort": Stop immediately on first error

        Returns:
            Dictionary with:
                - status: "success" | "error" | "confirmation_required" | "partial"
                - imported: Number of tasks imported (0 if dry_run)
                - task_ids: List of created task IDs
                - errors: List of error messages (if any)
                - skipped: List of skipped task names (if on_error="skip")
                - next_task: Recommended next task ID
                - confirmation_required: True if confirmation needed (optional)
                - preview: Preview of tasks to import (optional)

        Raises:
            No exceptions raised; errors returned in result dict

        Example:
            >>> yaml_content = '''
            ... tasks:
            ...   - name: "Setup FastAPI"
            ...     priority: high
            ...     files_to_edit: [main.py]
            ...   - name: "Create API"
            ...     priority: high
            ...     depends_on: [TASK-001]
            ... '''
            >>> result = tm.import_yaml(yaml_content)
            >>> result
            {
                "status": "success",
                "imported": 2,
                "task_ids": ["TASK-001", "TASK-002"],
                "next_task": "TASK-001"
            }

            >>> # Error recovery with skip
            >>> result = tm.import_yaml(yaml_content, on_error="skip")
            >>> result
            {
                "status": "partial",
                "imported": 1,
                "skipped": ["Failed task"],
                "errors": ["Task validation error..."]
            }
        """
        from datetime import datetime, timezone

        import yaml

        errors: List[str] = []
        task_ids: List[str] = []
        skipped: List[str] = []

        try:
            # Step 0: YAML Safety Check
            safety_errors = self._validate_yaml_safety(yaml_content)
            if safety_errors:
                return {
                    "status": "error",
                    "imported": 0,
                    "task_ids": [],
                    "errors": safety_errors,
                    "next_task": None,
                }

            # Step 1: Parse YAML
            data = yaml.safe_load(yaml_content)
            if not isinstance(data, dict) or "tasks" not in data:
                return {
                    "status": "error",
                    "imported": 0,
                    "task_ids": [],
                    "errors": [
                        "Invalid YAML format. Expected 'tasks' key at root. "
                        "Example: tasks:\n  - name: 'Task name'"
                    ],
                    "next_task": None,
                }

            tasks_data = data["tasks"]
            if not isinstance(tasks_data, list):
                return {
                    "status": "error",
                    "imported": 0,
                    "task_ids": [],
                    "errors": ["'tasks' must be a list of task objects"],
                    "next_task": None,
                }

            if len(tasks_data) == 0:
                return {
                    "status": "success",
                    "imported": 0,
                    "task_ids": [],
                    "errors": [],
                    "next_task": None,
                }

            # Step 1.5: Enhanced validation (unless skipped)
            if not skip_validation:
                from clauxton.core.task_validator import TaskValidator

                existing_tasks_temp = self._load_tasks()
                existing_task_ids = {task.id for task in existing_tasks_temp}

                validator = TaskValidator(self.root_dir)
                validation_result = validator.validate_tasks(tasks_data, existing_task_ids)

                # Add validation errors
                if not validation_result.is_valid():
                    errors.extend(validation_result.errors)

                    if on_error == "rollback" or on_error == "abort":
                        # Return immediately with validation errors
                        return {
                            "status": "error",
                            "imported": 0,
                            "task_ids": [],
                            "errors": errors,
                            "next_task": None,
                        }
                    # For skip mode, continue with warnings only

                # Log warnings (these don't block import)
                if validation_result.has_warnings():
                    # Warnings are informational, not blocking
                    pass

            # Step 2: Generate task IDs and validate
            existing_tasks = self._load_tasks()
            next_id_num = len(existing_tasks) + 1
            tasks_to_create: List[Task] = []

            for i, task_data in enumerate(tasks_data, start=1):
                try:
                    # Add required fields if missing
                    if "id" not in task_data:
                        task_data["id"] = f"TASK-{next_id_num:03d}"
                        next_id_num += 1

                    if "status" not in task_data:
                        task_data["status"] = "pending"

                    if "created_at" not in task_data:
                        task_data["created_at"] = datetime.now(timezone.utc)

                    if "depends_on" not in task_data:
                        task_data["depends_on"] = []

                    if "files_to_edit" not in task_data:
                        task_data["files_to_edit"] = []

                    if "priority" not in task_data:
                        task_data["priority"] = "medium"

                    # Validate with Pydantic
                    task = Task(**task_data)
                    tasks_to_create.append(task)

                except Exception as e:
                    error_msg = f"Task {i} ('{task_data.get('name', 'unnamed')}'): {str(e)}"

                    if on_error == "abort":
                        # Abort: Return error immediately
                        return {
                            "status": "error",
                            "imported": 0,
                            "task_ids": [],
                            "errors": [error_msg],
                            "next_task": None,
                        }
                    elif on_error == "skip":
                        # Skip: Record error and skipped task, continue
                        errors.append(error_msg)
                        skipped.append(task_data.get("name", "unnamed"))
                        continue
                    else:  # rollback (default)
                        # Rollback: Collect error and will return at end
                        errors.append(error_msg)

            # Check errors based on strategy
            if errors and on_error == "rollback":
                # Rollback: No tasks created, return error
                return {
                    "status": "error",
                    "imported": 0,
                    "task_ids": [],
                    "errors": errors,
                    "next_task": None,
                }

            # After skip mode processing, check if any tasks remain
            if not tasks_to_create:
                # Skip mode: All tasks failed
                return {
                    "status": "error",
                    "imported": 0,
                    "task_ids": [],
                    "errors": errors if errors else ["No valid tasks to import"],
                    "skipped": skipped,
                    "next_task": None,
                }

            # Step 3: Check dependencies (if not skipped)
            if not skip_validation:
                existing_ids = {t.id for t in existing_tasks}
                new_ids = {t.id for t in tasks_to_create}
                all_ids = existing_ids | new_ids

                for task in tasks_to_create:
                    for dep_id in task.depends_on:
                        if dep_id not in all_ids:
                            errors.append(
                                f"Task '{task.name}' (ID: {task.id}): "
                                f"Depends on non-existent task '{dep_id}'"
                            )

                # Handle dependency errors based on strategy
                if errors and on_error == "rollback":
                    return {
                        "status": "error",
                        "imported": 0,
                        "task_ids": [],
                        "errors": errors,
                        "next_task": None,
                    }
                # For skip/abort, errors are already recorded, continue

            # Step 4: Detect circular dependencies
            temp_graph = {t.id: t.depends_on for t in existing_tasks}
            for task in tasks_to_create:
                temp_graph[task.id] = task.depends_on

            cycle_errors = self._detect_cycles_in_graph(temp_graph)
            if cycle_errors:
                # Circular dependency errors always block import
                return {
                    "status": "error",
                    "imported": 0,
                    "task_ids": [],
                    "errors": cycle_errors,
                    "next_task": None,
                }

            # Step 4.5: Check if confirmation is required
            needs_confirmation = (
                not skip_confirmation
                and not dry_run
                and len(tasks_to_create) >= confirmation_threshold
            )
            if needs_confirmation:
                # Generate preview
                preview = self._generate_import_preview(tasks_to_create)

                return {
                    "status": "confirmation_required",
                    "imported": 0,
                    "task_ids": [],
                    "errors": [],
                    "next_task": None,
                    "confirmation_required": True,
                    "preview": preview,
                    "tasks_to_create": len(tasks_to_create),
                }

            # Step 5: Create tasks (if not dry_run)
            if not dry_run:
                if skip_validation:
                    # When skipping validation, write directly to avoid validation in add_many()
                    all_tasks = existing_tasks + tasks_to_create
                    self._save_tasks(all_tasks)
                    self._invalidate_cache()
                    task_ids = [t.id for t in tasks_to_create]
                else:
                    # Use batch operation for performance with validation
                    # Progress callback reports every 5 tasks or at completion
                    progress_data = {"last_reported": 0}

                    def progress_callback(current: int, total: int) -> None:
                        # Report every 5 tasks or at completion
                        if current == total or current - progress_data["last_reported"] >= 5:
                            progress_data["last_reported"] = current
                            # Progress reporting is internal, no need to print

                    # Use add_many() for efficient batch operation
                    task_ids = self.add_many(tasks_to_create, progress_callback=progress_callback)

                # Record operation for undo
                from clauxton.core.operation_history import (
                    Operation,
                    OperationHistory,
                    OperationType,
                )

                history = OperationHistory(self.root_dir)
                operation = Operation(
                    operation_type=OperationType.TASK_IMPORT,
                    operation_data={"task_ids": task_ids},
                    description=f"Imported {len(task_ids)} tasks from YAML",
                )
                history.record(operation)

            # Step 6: Get next task
            next_task_id = None
            if task_ids and not dry_run:
                try:
                    next_task = self.get_next_task()
                    next_task_id = next_task.id if next_task else None
                except Exception:
                    # If get_next_task fails, just use first task
                    next_task_id = task_ids[0] if task_ids else None

            # Determine final status
            final_status = "success"
            if errors and on_error == "skip":
                # Some tasks were skipped
                final_status = "partial"

            result = {
                "status": final_status,
                "imported": len(tasks_to_create) if not dry_run else 0,
                "task_ids": task_ids if not dry_run else [t.id for t in tasks_to_create],
                "errors": errors if errors else [],
                "next_task": next_task_id,
            }

            # Add skipped info if any tasks were skipped
            if skipped:
                result["skipped"] = skipped

            return result

        except yaml.YAMLError as e:
            return {
                "status": "error",
                "imported": 0,
                "task_ids": [],
                "errors": [f"YAML parsing error: {str(e)}"],
                "next_task": None,
            }
        except Exception as e:
            return {
                "status": "error",
                "imported": 0,
                "task_ids": [],
                "errors": [f"Unexpected error: {str(e)}"],
                "next_task": None,
            }

    def _generate_import_preview(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Generate a preview of tasks to be imported.

        Args:
            tasks: List of Task objects to preview

        Returns:
            Dictionary with preview information

        Example:
            >>> preview = tm._generate_import_preview(tasks)
            >>> print(preview)
            {
                "task_count": 10,
                "total_estimated_hours": 25.5,
                "by_priority": {"critical": 2, "high": 5, "medium": 3},
                "by_status": {"pending": 10},
                "tasks_summary": [
                    {"id": "TASK-001", "name": "Setup FastAPI", "priority": "high"},
                    ...
                ]
            }
        """
        from collections import Counter

        # Count by priority
        by_priority = Counter(t.priority for t in tasks)

        # Count by status
        by_status = Counter(t.status for t in tasks)

        # Calculate total estimated hours
        total_hours = sum(t.estimated_hours or 0 for t in tasks)

        # Create task summaries (first 5 tasks)
        tasks_summary = [
            {
                "id": t.id,
                "name": t.name,
                "priority": t.priority,
                "estimated_hours": t.estimated_hours,
            }
            for t in tasks[:5]
        ]

        return {
            "task_count": len(tasks),
            "total_estimated_hours": total_hours,
            "by_priority": dict(by_priority),
            "by_status": dict(by_status),
            "tasks_summary": tasks_summary,
        }

    def _validate_yaml_safety(self, yaml_content: str) -> List[str]:
        """
        Validate YAML content for dangerous patterns.

        Detects potential code injection risks like:
        - !!python/object tag (arbitrary code execution)
        - !!python/name tag (module imports)
        - __import__ function calls
        - eval(), exec() function calls

        Args:
            yaml_content: Raw YAML string to validate

        Returns:
            List of security error messages (empty if safe)

        Example:
            >>> errors = tm._validate_yaml_safety("tasks:\\n  - name: Test")
            >>> errors
            []

            >>> errors = tm._validate_yaml_safety("!!python/object/apply:os.system")
            >>> errors
            ['Dangerous YAML tag detected: !!python']
        """
        errors: List[str] = []

        # Dangerous YAML tags
        dangerous_tags = ["!!python", "!!exec", "!!apply"]
        for tag in dangerous_tags:
            if tag in yaml_content:
                errors.append(
                    f"Dangerous YAML tag detected: {tag}. "
                    "This could allow code injection. "
                    "Please use plain YAML without special tags."
                )

        # Dangerous function calls
        dangerous_patterns = [
            ("__import__", "Import statements"),
            ("eval(", "eval() function"),
            ("exec(", "exec() function"),
            ("compile(", "compile() function"),
        ]
        for pattern, description in dangerous_patterns:
            if pattern in yaml_content:
                errors.append(
                    f"Potentially dangerous pattern detected: {description}. "
                    "Please remove this before importing."
                )

        return errors

    def _detect_cycles_in_graph(self, graph: Dict[str, List[str]]) -> List[str]:
        """
        Detect circular dependencies in a dependency graph using DFS.

        Args:
            graph: Dictionary mapping task IDs to lists of dependency IDs

        Returns:
            List of error messages describing cycles (empty if no cycles)
        """
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: List[str] = []

        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Cycle detected
                cycle_start = path.index(node)
                cycle_path = " → ".join(path[cycle_start:] + [node])
                cycles.append(f"Circular dependency detected: {cycle_path}")
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor, path + [node])

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles
