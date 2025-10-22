"""
Task Validator for enhanced YAML validation.

Provides comprehensive validation for task data beyond basic Pydantic validation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class ValidationResult:
    """Result of validation with errors and warnings."""

    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, message: str) -> None:
        """Add validation error."""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add validation warning."""
        self.warnings.append(message)

    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0


class TaskValidator:
    """
    Enhanced validator for task data.

    Validates:
    - Duplicate task IDs
    - Duplicate task names
    - Invalid priority/status values
    - Empty task names
    - Invalid dependencies
    - File existence (warnings only)
    """

    def __init__(self, root: Optional[Path] = None):
        """
        Initialize TaskValidator.

        Args:
            root: Project root directory (for file existence checks)
        """
        self.root = root or Path.cwd()

    def validate_tasks(
        self, tasks_data: List[Dict[str, Any]], existing_task_ids: Optional[Set[str]] = None
    ) -> ValidationResult:
        """
        Validate list of tasks.

        Args:
            tasks_data: List of task dictionaries from YAML
            existing_task_ids: Set of existing task IDs in the system

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()
        existing_task_ids = existing_task_ids or set()

        # Track IDs and names in current batch
        seen_ids: Set[str] = set()
        seen_names: Set[str] = set()

        for i, task_data in enumerate(tasks_data, start=1):
            task_prefix = f"Task {i}"

            # Validate task name
            self._validate_task_name(task_data, task_prefix, result)

            # Validate duplicate IDs
            self._validate_duplicate_id(task_data, task_prefix, seen_ids, existing_task_ids, result)

            # Validate duplicate names
            self._validate_duplicate_name(task_data, task_prefix, seen_names, result)

            # Validate priority
            self._validate_priority(task_data, task_prefix, result)

            # Validate status
            self._validate_status(task_data, task_prefix, result)

            # Validate dependencies
            self._validate_dependencies(task_data, task_prefix, result)

            # Validate estimated hours
            self._validate_estimated_hours(task_data, task_prefix, result)

            # Validate files to edit (warnings only)
            self._validate_files(task_data, task_prefix, result)

        return result

    def _validate_task_name(
        self, task_data: Dict[str, Any], task_prefix: str, result: ValidationResult
    ) -> None:
        """Validate task name."""
        name = task_data.get("name", "").strip()

        if not name:
            result.add_error(f"{task_prefix}: Task name is required and cannot be empty")
        elif len(name) > 255:
            result.add_error(f"{task_prefix}: Task name too long (max 255 characters)")

    def _validate_duplicate_id(
        self,
        task_data: Dict[str, Any],
        task_prefix: str,
        seen_ids: Set[str],
        existing_task_ids: Set[str],
        result: ValidationResult,
    ) -> None:
        """Validate duplicate task IDs."""
        task_id = task_data.get("id")
        if not task_id:
            return  # ID will be auto-generated

        if task_id in seen_ids:
            result.add_error(f"{task_prefix}: Duplicate task ID '{task_id}' in import batch")
        elif task_id in existing_task_ids:
            result.add_error(
                f"{task_prefix}: Task ID '{task_id}' already exists. "
                "Use 'clauxton task update' to modify existing tasks."
            )
        else:
            seen_ids.add(task_id)

    def _validate_duplicate_name(
        self,
        task_data: Dict[str, Any],
        task_prefix: str,
        seen_names: Set[str],
        result: ValidationResult,
    ) -> None:
        """Validate duplicate task names."""
        name = task_data.get("name", "").strip()
        if not name:
            return  # Already handled by _validate_task_name

        if name in seen_names:
            result.add_warning(
                f"{task_prefix}: Duplicate task name '{name}'. "
                "Consider using unique names for clarity."
            )
        else:
            seen_names.add(name)

    def _validate_priority(
        self, task_data: Dict[str, Any], task_prefix: str, result: ValidationResult
    ) -> None:
        """Validate priority value."""
        priority = task_data.get("priority")
        if not priority:
            return  # Priority is optional, defaults to "medium"

        valid_priorities = ["low", "medium", "high", "critical"]
        if priority not in valid_priorities:
            result.add_error(
                f"{task_prefix}: Invalid priority '{priority}'. "
                f"Must be one of: {', '.join(valid_priorities)}"
            )

    def _validate_status(
        self, task_data: Dict[str, Any], task_prefix: str, result: ValidationResult
    ) -> None:
        """Validate status value."""
        status = task_data.get("status")
        if not status:
            return  # Status is optional, defaults to "pending"

        valid_statuses = ["pending", "in_progress", "completed", "blocked"]
        if status not in valid_statuses:
            result.add_error(
                f"{task_prefix}: Invalid status '{status}'. "
                f"Must be one of: {', '.join(valid_statuses)}"
            )

    def _validate_dependencies(
        self, task_data: Dict[str, Any], task_prefix: str, result: ValidationResult
    ) -> None:
        """Validate dependencies format."""
        depends_on = task_data.get("depends_on")
        if not depends_on:
            return

        if not isinstance(depends_on, list):
            result.add_error(f"{task_prefix}: 'depends_on' must be a list of task IDs")
            return

        for dep_id in depends_on:
            if not isinstance(dep_id, str):
                result.add_error(
                    f"{task_prefix}: Dependency ID must be a string, got: {type(dep_id)}"
                )
            elif not dep_id.strip():
                result.add_error(f"{task_prefix}: Dependency ID cannot be empty")

    def _validate_estimated_hours(
        self, task_data: Dict[str, Any], task_prefix: str, result: ValidationResult
    ) -> None:
        """Validate estimated hours."""
        estimated_hours = task_data.get("estimated_hours")
        if estimated_hours is None:
            return  # Optional field

        if not isinstance(estimated_hours, (int, float)):
            result.add_error(
                f"{task_prefix}: 'estimated_hours' must be a number, got: {type(estimated_hours)}"
            )
        elif estimated_hours <= 0:
            result.add_error(
                f"{task_prefix}: 'estimated_hours' must be positive, got: {estimated_hours}"
            )
        elif estimated_hours > 1000:
            result.add_warning(
                f"{task_prefix}: 'estimated_hours' is very large ({estimated_hours}). "
                "Consider breaking down into smaller tasks."
            )

    def _validate_files(
        self, task_data: Dict[str, Any], task_prefix: str, result: ValidationResult
    ) -> None:
        """Validate files to edit (warnings only)."""
        files_to_edit = task_data.get("files_to_edit")
        if not files_to_edit:
            return

        if not isinstance(files_to_edit, list):
            result.add_warning(f"{task_prefix}: 'files_to_edit' should be a list of file paths")
            return

        for file_path in files_to_edit:
            if not isinstance(file_path, str):
                result.add_warning(
                    f"{task_prefix}: File path must be a string, got: {type(file_path)}"
                )
                continue

            # Check if file exists (warning only, file might not exist yet)
            full_path = self.root / file_path
            if not full_path.exists() and not file_path.startswith("/"):
                result.add_warning(
                    f"{task_prefix}: File '{file_path}' does not exist yet. "
                    "This is OK if you plan to create it."
                )
