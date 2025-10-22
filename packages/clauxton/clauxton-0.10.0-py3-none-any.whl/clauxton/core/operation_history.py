"""
Operation History Management for Undo/Rollback functionality.

This module provides the ability to track, undo, and rollback operations
performed by Clauxton, ensuring users can recover from mistakes.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from clauxton.utils.yaml_utils import read_yaml, write_yaml


class OperationType:
    """Operation types that can be undone."""

    KB_ADD = "kb_add"
    KB_DELETE = "kb_delete"
    KB_UPDATE = "kb_update"
    TASK_ADD = "task_add"
    TASK_DELETE = "task_delete"
    TASK_UPDATE = "task_update"
    TASK_IMPORT = "task_import"


class Operation:
    """
    Represents a single operation that can be undone.

    Attributes:
        operation_type: Type of operation (e.g., "kb_add", "task_import")
        timestamp: When the operation was performed
        operation_data: Data needed to undo the operation
        description: Human-readable description
    """

    def __init__(
        self,
        operation_type: str,
        operation_data: Dict[str, Any],
        description: str,
    ):
        self.operation_type = operation_type
        self.timestamp = datetime.now().isoformat()
        self.operation_data = operation_data
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary for storage."""
        return {
            "operation_type": self.operation_type,
            "timestamp": self.timestamp,
            "operation_data": self.operation_data,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Operation":
        """Create operation from dictionary."""
        op = cls(
            operation_type=data["operation_type"],
            operation_data=data["operation_data"],
            description=data["description"],
        )
        op.timestamp = data["timestamp"]
        return op


class OperationHistory:
    """
    Manages operation history for undo/rollback functionality.

    Features:
    - Record all operations (KB, Tasks)
    - Undo last operation
    - List recent operations
    - Configurable history size (default: 100)
    """

    def __init__(self, root: Path, max_history: int = 100):
        """
        Initialize operation history manager.

        Args:
            root: Project root directory
            max_history: Maximum number of operations to keep (default: 100)
        """
        self.root = root
        self.max_history = max_history
        self.history_dir = root / ".clauxton" / "history"
        self.history_file = self.history_dir / "operations.yml"

        # Ensure history directory exists
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # Initialize empty history if file doesn't exist
        if not self.history_file.exists():
            write_yaml(self.history_file, {"operations": []})

    def record(self, operation: Operation) -> None:
        """
        Record an operation to history.

        Args:
            operation: Operation to record

        Example:
            >>> history = OperationHistory(Path("."))
            >>> op = Operation(
            ...     operation_type=OperationType.TASK_ADD,
            ...     operation_data={"task_id": "TASK-001", "backup": {...}},
            ...     description="Added task: Setup FastAPI"
            ... )
            >>> history.record(op)
        """
        # Load existing history
        data = read_yaml(self.history_file)
        operations = data.get("operations", [])

        # Add new operation
        operations.append(operation.to_dict())

        # Trim history if exceeds max_history
        if len(operations) > self.max_history:
            operations = operations[-self.max_history :]

        # Save history
        write_yaml(self.history_file, {"operations": operations})

    def get_last_operation(self) -> Optional[Operation]:
        """
        Get the last recorded operation.

        Returns:
            Last operation or None if history is empty

        Example:
            >>> history = OperationHistory(Path("."))
            >>> last_op = history.get_last_operation()
            >>> if last_op:
            ...     print(f"Last: {last_op.description}")
        """
        data = read_yaml(self.history_file)
        operations = data.get("operations", [])

        if not operations:
            return None

        return Operation.from_dict(operations[-1])

    def remove_last_operation(self) -> Optional[Operation]:
        """
        Remove and return the last operation from history.

        Returns:
            Removed operation or None if history is empty

        Example:
            >>> history = OperationHistory(Path("."))
            >>> op = history.remove_last_operation()
            >>> # Now op can be processed for undo
        """
        data = read_yaml(self.history_file)
        operations = data.get("operations", [])

        if not operations:
            return None

        # Remove last operation
        last_op_data = operations.pop()
        last_op = Operation.from_dict(last_op_data)

        # Save updated history
        write_yaml(self.history_file, {"operations": operations})

        return last_op

    def list_operations(self, limit: int = 10) -> List[Operation]:
        """
        List recent operations.

        Args:
            limit: Maximum number of operations to return (default: 10)

        Returns:
            List of operations (most recent first)

        Example:
            >>> history = OperationHistory(Path("."))
            >>> recent = history.list_operations(limit=5)
            >>> for op in recent:
            ...     print(f"{op.timestamp}: {op.description}")
        """
        data = read_yaml(self.history_file)
        operations = data.get("operations", [])

        # Get last N operations (most recent first)
        recent_ops = operations[-limit:][::-1]

        return [Operation.from_dict(op_data) for op_data in recent_ops]

    def clear_history(self) -> int:
        """
        Clear all operation history.

        Returns:
            Number of operations cleared

        Example:
            >>> history = OperationHistory(Path("."))
            >>> count = history.clear_history()
            >>> print(f"Cleared {count} operations")
        """
        data = read_yaml(self.history_file)
        operations = data.get("operations", [])
        count = len(operations)

        # Clear history
        write_yaml(self.history_file, {"operations": []})

        return count

    def undo_last_operation(self) -> Dict[str, Any]:
        """
        Undo the last operation.

        Returns:
            Result dictionary with status and details

        Raises:
            ValueError: If no operations to undo
            RuntimeError: If undo fails

        Example:
            >>> history = OperationHistory(Path("."))
            >>> result = history.undo_last_operation()
            >>> if result["status"] == "success":
            ...     print(f"Undone: {result['description']}")
        """
        # Get last operation
        last_op = self.remove_last_operation()
        if not last_op:
            return {
                "status": "error",
                "error": "No operations to undo",
                "message": "Operation history is empty",
            }

        try:
            # Perform undo based on operation type
            if last_op.operation_type == OperationType.TASK_IMPORT:
                return self._undo_task_import(last_op)
            elif last_op.operation_type == OperationType.TASK_ADD:
                return self._undo_task_add(last_op)
            elif last_op.operation_type == OperationType.TASK_DELETE:
                return self._undo_task_delete(last_op)
            elif last_op.operation_type == OperationType.TASK_UPDATE:
                return self._undo_task_update(last_op)
            elif last_op.operation_type == OperationType.KB_ADD:
                return self._undo_kb_add(last_op)
            elif last_op.operation_type == OperationType.KB_DELETE:
                return self._undo_kb_delete(last_op)
            elif last_op.operation_type == OperationType.KB_UPDATE:
                return self._undo_kb_update(last_op)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown operation type: {last_op.operation_type}",
                    "message": "Cannot undo this type of operation",
                }

        except Exception as e:
            # Re-add operation to history if undo fails
            self.record(last_op)
            return {
                "status": "error",
                "error": str(e),
                "message": f"Failed to undo operation: {e}",
            }

    def _undo_task_import(self, operation: Operation) -> Dict[str, Any]:
        """Undo a task import operation (delete imported tasks)."""
        from clauxton.core.task_manager import TaskManager

        task_ids = operation.operation_data.get("task_ids", [])

        # Delete all imported tasks
        tm = TaskManager(root_dir=self.root)
        deleted_count = 0

        # Delete tasks from the tasks list
        all_tasks = tm.list_all()
        remaining_tasks = [t for t in all_tasks if t.id not in task_ids]
        deleted_count = len(all_tasks) - len(remaining_tasks)

        # Save the updated task list
        tm._save_tasks(remaining_tasks)
        tm._invalidate_cache()

        return {
            "status": "success",
            "operation_type": operation.operation_type,
            "description": operation.description,
            "details": {
                "deleted_tasks": deleted_count,
                "task_ids": task_ids,
            },
            "message": f"Undone: {operation.description} (deleted {deleted_count} tasks)",
        }

    def _undo_task_add(self, operation: Operation) -> Dict[str, Any]:
        """Undo a task add operation (delete the task)."""
        from clauxton.core.task_manager import TaskManager

        task_id = operation.operation_data.get("task_id", "")
        if not task_id:
            return {
                "status": "error",
                "error": "Missing task_id in operation data",
                "message": "Cannot undo: task_id not found",
            }

        tm = TaskManager(root_dir=self.root)
        tm.delete(task_id)

        return {
            "status": "success",
            "operation_type": operation.operation_type,
            "description": operation.description,
            "details": {"task_id": task_id},
            "message": f"Undone: {operation.description} (deleted task {task_id})",
        }

    def _undo_task_delete(self, operation: Operation) -> Dict[str, Any]:
        """Undo a task delete operation (restore the task)."""
        task_data = operation.operation_data.get("task_backup")
        if not task_data:
            return {
                "status": "error",
                "error": "Missing task_backup in operation data",
                "message": "Cannot undo: task backup not found",
            }

        # Restore task from backup
        # Note: We need to directly write to tasks.yml since the task was deleted
        tasks_file = self.root / ".clauxton" / "tasks.yml"
        data = read_yaml(tasks_file)
        tasks = data.get("tasks", [])
        tasks.append(task_data)
        write_yaml(tasks_file, {"tasks": tasks})

        return {
            "status": "success",
            "operation_type": operation.operation_type,
            "description": operation.description,
            "details": {"task_id": task_data.get("id")},
            "message": f"Undone: {operation.description} (restored task {task_data.get('id')})",
        }

    def _undo_task_update(self, operation: Operation) -> Dict[str, Any]:
        """Undo a task update operation (restore previous state)."""
        from clauxton.core.task_manager import TaskManager

        task_id = operation.operation_data.get("task_id", "")
        old_state = operation.operation_data.get("old_state")

        if not task_id or not old_state:
            return {
                "status": "error",
                "error": "Missing task_id or old_state in operation data",
                "message": "Cannot undo: required data not found",
            }

        tm = TaskManager(root_dir=self.root)

        # Restore old state by updating all fields
        for key, value in old_state.items():
            if key != "id":  # Don't update ID
                tm.update(task_id, **{key: value})

        return {
            "status": "success",
            "operation_type": operation.operation_type,
            "description": operation.description,
            "details": {"task_id": task_id},
            "message": f"Undone: {operation.description} (restored task {task_id})",
        }

    def _undo_kb_add(self, operation: Operation) -> Dict[str, Any]:
        """Undo a KB add operation (delete the entry)."""
        from clauxton.core.knowledge_base import KnowledgeBase

        entry_id = operation.operation_data.get("entry_id", "")
        if not entry_id:
            return {
                "status": "error",
                "error": "Missing entry_id in operation data",
                "message": "Cannot undo: entry_id not found",
            }

        kb = KnowledgeBase(root_dir=self.root)
        kb.delete(entry_id)

        return {
            "status": "success",
            "operation_type": operation.operation_type,
            "description": operation.description,
            "details": {"entry_id": entry_id},
            "message": f"Undone: {operation.description} (deleted entry {entry_id})",
        }

    def _undo_kb_delete(self, operation: Operation) -> Dict[str, Any]:
        """Undo a KB delete operation (restore the entry)."""
        entry_data = operation.operation_data.get("entry_backup")
        if not entry_data:
            return {
                "status": "error",
                "error": "Missing entry_backup in operation data",
                "message": "Cannot undo: entry backup not found",
            }

        # Restore entry from backup
        kb_file = self.root / ".clauxton" / "knowledge-base.yml"
        data = read_yaml(kb_file)
        entries = data.get("entries", [])
        entries.append(entry_data)
        write_yaml(kb_file, {"entries": entries})

        entry_id = entry_data.get("id", "unknown")
        return {
            "status": "success",
            "operation_type": operation.operation_type,
            "description": operation.description,
            "details": {"entry_id": entry_id},
            "message": f"Undone: {operation.description} (restored entry {entry_id})",
        }

    def _undo_kb_update(self, operation: Operation) -> Dict[str, Any]:
        """Undo a KB update operation (restore previous state)."""
        from clauxton.core.knowledge_base import KnowledgeBase

        entry_id = operation.operation_data.get("entry_id", "")
        old_state = operation.operation_data.get("old_state")

        if not entry_id or not old_state:
            return {
                "status": "error",
                "error": "Missing entry_id or old_state in operation data",
                "message": "Cannot undo: required data not found",
            }

        kb = KnowledgeBase(root_dir=self.root)

        # Restore old state
        updates = {
            "title": old_state.get("title"),
            "category": old_state.get("category"),
            "content": old_state.get("content"),
            "tags": old_state.get("tags"),
        }
        kb.update(entry_id, updates)

        return {
            "status": "success",
            "operation_type": operation.operation_type,
            "description": operation.description,
            "details": {"entry_id": entry_id},
            "message": f"Undone: {operation.description} (restored entry {entry_id})",
        }
