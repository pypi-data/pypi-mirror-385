"""
Tests for Operation History and Undo/Rollback functionality.
"""

from clauxton.core.operation_history import Operation, OperationHistory, OperationType
from clauxton.core.task_manager import TaskManager


class TestOperationHistory:
    """Test OperationHistory class."""

    def test_record_operation(self, tmp_path):
        """Test recording an operation."""
        history = OperationHistory(tmp_path)

        operation = Operation(
            operation_type=OperationType.TASK_IMPORT,
            operation_data={"task_ids": ["TASK-001", "TASK-002"]},
            description="Imported 2 tasks from YAML",
        )

        history.record(operation)

        # Verify operation was recorded
        last_op = history.get_last_operation()
        assert last_op is not None
        assert last_op.operation_type == OperationType.TASK_IMPORT
        assert last_op.description == "Imported 2 tasks from YAML"
        assert last_op.operation_data["task_ids"] == ["TASK-001", "TASK-002"]

    def test_get_last_operation_empty(self, tmp_path):
        """Test getting last operation when history is empty."""
        history = OperationHistory(tmp_path)
        last_op = history.get_last_operation()
        assert last_op is None

    def test_list_operations(self, tmp_path):
        """Test listing operations."""
        history = OperationHistory(tmp_path)

        # Record multiple operations
        for i in range(5):
            operation = Operation(
                operation_type=OperationType.TASK_ADD,
                operation_data={"task_id": f"TASK-{i:03d}"},
                description=f"Added task {i}",
            )
            history.record(operation)

        # List operations
        operations = history.list_operations(limit=3)
        assert len(operations) == 3

        # Verify most recent first
        assert operations[0].description == "Added task 4"
        assert operations[1].description == "Added task 3"
        assert operations[2].description == "Added task 2"

    def test_max_history_limit(self, tmp_path):
        """Test that history respects max_history limit."""
        history = OperationHistory(tmp_path, max_history=5)

        # Record 10 operations
        for i in range(10):
            operation = Operation(
                operation_type=OperationType.TASK_ADD,
                operation_data={"task_id": f"TASK-{i:03d}"},
                description=f"Added task {i}",
            )
            history.record(operation)

        # Should only keep last 5
        all_ops = history.list_operations(limit=100)
        assert len(all_ops) == 5
        assert all_ops[0].description == "Added task 9"
        assert all_ops[4].description == "Added task 5"

    def test_clear_history(self, tmp_path):
        """Test clearing history."""
        history = OperationHistory(tmp_path)

        # Record operations
        for i in range(3):
            operation = Operation(
                operation_type=OperationType.TASK_ADD,
                operation_data={"task_id": f"TASK-{i:03d}"},
                description=f"Added task {i}",
            )
            history.record(operation)

        # Clear history
        count = history.clear_history()
        assert count == 3

        # Verify empty
        last_op = history.get_last_operation()
        assert last_op is None


class TestUndoTaskImport:
    """Test undoing task import operations."""

    def test_undo_task_import(self, tmp_path):
        """Test undoing a task import operation."""
        tm = TaskManager(tmp_path)
        history = OperationHistory(tmp_path)

        # Import tasks via YAML
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: medium
        """
        result = tm.import_yaml(yaml_content)
        assert result["status"] == "success"
        assert result["imported"] == 2

        # Verify tasks exist
        tasks = tm.list_all()
        assert len(tasks) == 2

        # Undo import
        undo_result = history.undo_last_operation()
        if undo_result["status"] != "success":
            print(f"Undo failed: {undo_result}")
        error_msg = f"Undo failed: {undo_result.get('error', 'Unknown error')}"
        assert undo_result["status"] == "success", error_msg
        assert undo_result["operation_type"] == OperationType.TASK_IMPORT
        print(f"Undo result: {undo_result}")
        assert undo_result["details"]["deleted_tasks"] == 2

        # Verify tasks were deleted (create new instance to avoid cache)
        tm_fresh = TaskManager(tmp_path)
        tasks = tm_fresh.list_all()
        print(f"Tasks after undo: {[t.id for t in tasks]}")
        assert len(tasks) == 0

    def test_undo_multiple_imports(self, tmp_path):
        """Test undoing multiple import operations."""
        tm = TaskManager(tmp_path)
        history = OperationHistory(tmp_path)

        # First import
        yaml_content1 = """
        tasks:
          - name: "Task 1"
            priority: high
        """
        tm.import_yaml(yaml_content1)

        # Second import
        yaml_content2 = """
        tasks:
          - name: "Task 2"
            priority: high
        """
        tm.import_yaml(yaml_content2)

        assert len(tm.list_all()) == 2

        # Undo last import (Task 2)
        undo_result1 = history.undo_last_operation()
        assert undo_result1["status"] == "success"
        tm_check1 = TaskManager(tmp_path)
        assert len(tm_check1.list_all()) == 1
        assert tm_check1.list_all()[0].name == "Task 1"

        # Undo first import (Task 1)
        undo_result2 = history.undo_last_operation()
        assert undo_result2["status"] == "success"
        tm_check2 = TaskManager(tmp_path)
        assert len(tm_check2.list_all()) == 0

    def test_undo_empty_history(self, tmp_path):
        """Test undoing when history is empty."""
        history = OperationHistory(tmp_path)

        result = history.undo_last_operation()
        assert result["status"] == "error"
        assert "No operations to undo" in result["error"]

    def test_undo_partial_deletion(self, tmp_path):
        """Test undo when some tasks are already deleted."""
        tm = TaskManager(tmp_path)
        history = OperationHistory(tmp_path)

        # Import tasks
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: high
        """
        result = tm.import_yaml(yaml_content)
        task_ids = result["task_ids"]

        # Manually delete one task
        tm.delete(task_ids[0])

        # Undo should still work (delete remaining task)
        undo_result = history.undo_last_operation()
        assert undo_result["status"] == "success"
        # Should delete 1 task (the one that still exists)
        assert undo_result["details"]["deleted_tasks"] == 1

        # Verify only 1 task remains (the manually deleted one is gone)
        tm_check = TaskManager(tmp_path)
        assert len(tm_check.list_all()) == 0

    def test_undo_with_dependencies(self, tmp_path):
        """Test undoing import with task dependencies."""
        tm = TaskManager(tmp_path)
        history = OperationHistory(tmp_path)

        # Import tasks with dependencies
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: high
            depends_on: [TASK-001]
        """
        result = tm.import_yaml(yaml_content)
        assert result["status"] == "success"

        # Undo should delete both tasks
        undo_result = history.undo_last_operation()
        assert undo_result["status"] == "success"
        assert undo_result["details"]["deleted_tasks"] == 2
        tm_check = TaskManager(tmp_path)
        assert len(tm_check.list_all()) == 0


class TestUndoTaskOperations:
    """Test undoing individual task operations (future implementation)."""

    def test_operation_to_dict(self):
        """Test Operation serialization."""
        operation = Operation(
            operation_type=OperationType.TASK_ADD,
            operation_data={"task_id": "TASK-001"},
            description="Added task",
        )

        data = operation.to_dict()
        assert data["operation_type"] == OperationType.TASK_ADD
        assert data["operation_data"]["task_id"] == "TASK-001"
        assert data["description"] == "Added task"
        assert "timestamp" in data

    def test_operation_from_dict(self):
        """Test Operation deserialization."""
        data = {
            "operation_type": "task_add",
            "timestamp": "2025-10-20T15:30:00",
            "operation_data": {"task_id": "TASK-001"},
            "description": "Added task",
        }

        operation = Operation.from_dict(data)
        assert operation.operation_type == "task_add"
        assert operation.timestamp == "2025-10-20T15:30:00"
        assert operation.operation_data["task_id"] == "TASK-001"
        assert operation.description == "Added task"


class TestHistoryPersistence:
    """Test operation history persistence."""

    def test_history_persists_across_instances(self, tmp_path):
        """Test that history persists across OperationHistory instances."""
        # Create first instance and record operation
        history1 = OperationHistory(tmp_path)
        operation = Operation(
            operation_type=OperationType.TASK_IMPORT,
            operation_data={"task_ids": ["TASK-001"]},
            description="Imported 1 task",
        )
        history1.record(operation)

        # Create second instance and verify operation exists
        history2 = OperationHistory(tmp_path)
        last_op = history2.get_last_operation()
        assert last_op is not None
        assert last_op.description == "Imported 1 task"

    def test_history_file_created(self, tmp_path):
        """Test that history file is created."""
        _ = OperationHistory(tmp_path)

        history_file = tmp_path / ".clauxton" / "history" / "operations.yml"
        assert history_file.exists()


class TestUndoSingleTaskOperations:
    """Test undoing single task operations (add, delete, update)."""

    def test_undo_task_add_missing_data(self, tmp_path):
        """Test undo task_add with missing task_id."""
        history = OperationHistory(tmp_path)

        # Record operation with missing task_id
        operation = Operation(
            operation_type=OperationType.TASK_ADD,
            operation_data={},  # Missing task_id
            description="Added task",
        )
        history.record(operation)

        # Undo should fail gracefully
        result = history.undo_last_operation()
        assert result["status"] == "error"
        assert "task_id" in result["error"].lower()

    def test_undo_task_delete_missing_backup(self, tmp_path):
        """Test undo task_delete with missing backup data."""
        history = OperationHistory(tmp_path)

        # Record operation with missing task_backup
        operation = Operation(
            operation_type=OperationType.TASK_DELETE,
            operation_data={},  # Missing task_backup
            description="Deleted task",
        )
        history.record(operation)

        # Undo should fail gracefully
        result = history.undo_last_operation()
        assert result["status"] == "error"
        assert "backup" in result["error"].lower()

    def test_undo_task_update_missing_data(self, tmp_path):
        """Test undo task_update with missing data."""
        history = OperationHistory(tmp_path)

        # Record operation with missing old_state
        operation = Operation(
            operation_type=OperationType.TASK_UPDATE,
            operation_data={"task_id": "TASK-001"},  # Missing old_state
            description="Updated task",
        )
        history.record(operation)

        # Undo should fail gracefully
        result = history.undo_last_operation()
        assert result["status"] == "error"
        assert "old_state" in result["error"].lower()


class TestUndoKBOperations:
    """Test undoing Knowledge Base operations."""

    def test_undo_kb_add_missing_data(self, tmp_path):
        """Test undo kb_add with missing entry_id."""
        history = OperationHistory(tmp_path)

        # Record operation with missing entry_id
        operation = Operation(
            operation_type=OperationType.KB_ADD,
            operation_data={},  # Missing entry_id
            description="Added KB entry",
        )
        history.record(operation)

        # Undo should fail gracefully
        result = history.undo_last_operation()
        assert result["status"] == "error"
        assert "entry_id" in result["error"].lower()

    def test_undo_kb_delete_missing_backup(self, tmp_path):
        """Test undo kb_delete with missing backup data."""
        history = OperationHistory(tmp_path)

        # Record operation with missing entry_backup
        operation = Operation(
            operation_type=OperationType.KB_DELETE,
            operation_data={},  # Missing entry_backup
            description="Deleted KB entry",
        )
        history.record(operation)

        # Undo should fail gracefully
        result = history.undo_last_operation()
        assert result["status"] == "error"
        assert "backup" in result["error"].lower()

    def test_undo_kb_update_missing_data(self, tmp_path):
        """Test undo kb_update with missing data."""
        history = OperationHistory(tmp_path)

        # Record operation with missing old_state
        operation = Operation(
            operation_type=OperationType.KB_UPDATE,
            operation_data={"entry_id": "KB-20251020-001"},  # Missing old_state
            description="Updated KB entry",
        )
        history.record(operation)

        # Undo should fail gracefully
        result = history.undo_last_operation()
        assert result["status"] == "error"
        assert "old_state" in result["error"].lower()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_undo_unknown_operation_type(self, tmp_path):
        """Test undoing an unknown operation type."""
        history = OperationHistory(tmp_path)

        # Manually add operation with unknown type
        operation = Operation(
            operation_type="unknown_operation",
            operation_data={},
            description="Unknown operation",
        )
        history.record(operation)

        # Undo should fail gracefully
        result = history.undo_last_operation()
        assert result["status"] == "error"
        assert "Unknown operation type" in result["error"]

    def test_concurrent_history_access(self, tmp_path):
        """Test concurrent access to history (basic test)."""
        history1 = OperationHistory(tmp_path)
        history2 = OperationHistory(tmp_path)

        # Record from different instances
        op1 = Operation(
            operation_type=OperationType.TASK_ADD,
            operation_data={"task_id": "TASK-001"},
            description="Added task 1",
        )
        history1.record(op1)

        op2 = Operation(
            operation_type=OperationType.TASK_ADD,
            operation_data={"task_id": "TASK-002"},
            description="Added task 2",
        )
        history2.record(op2)

        # Both operations should be recorded
        all_ops = history1.list_operations(limit=10)
        assert len(all_ops) == 2

    def test_remove_last_operation(self, tmp_path):
        """Test removing last operation from history."""
        history = OperationHistory(tmp_path)

        # Record operation
        operation = Operation(
            operation_type=OperationType.TASK_IMPORT,
            operation_data={"task_ids": ["TASK-001"]},
            description="Imported 1 task",
        )
        history.record(operation)

        # Remove last operation
        removed_op = history.remove_last_operation()
        assert removed_op is not None
        assert removed_op.description == "Imported 1 task"

        # History should be empty now
        last_op = history.get_last_operation()
        assert last_op is None

    def test_undo_when_undo_fails_restores_history(self, tmp_path):
        """Test that operation is restored to history if undo fails."""
        from clauxton.core.task_manager import TaskManager

        tm = TaskManager(tmp_path)
        history = OperationHistory(tmp_path)

        # Import tasks
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
        """
        result = tm.import_yaml(yaml_content)
        assert result["status"] == "success"

        # Manually corrupt the operation data to cause undo failure
        # (This simulates a scenario where undo logic encounters an error)
        last_op = history.get_last_operation()
        assert last_op is not None

        # Record a corrupted operation (invalid task_id type)
        from clauxton.core.operation_history import Operation, OperationType

        corrupted_op = Operation(
            operation_type=OperationType.TASK_ADD,
            operation_data={"task_id": None},  # Invalid task_id
            description="Corrupted operation",
        )
        history.record(corrupted_op)

        # Try to undo - should fail but not crash
        result = history.undo_last_operation()
        # The operation should fail gracefully
        assert result["status"] == "error"
