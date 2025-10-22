"""
Tests for error recovery functionality.
"""

from clauxton.core.task_manager import TaskManager


class TestErrorRecoveryRollback:
    """Test rollback error recovery strategy (default)."""

    def test_rollback_on_validation_error(self, tmp_path):
        """Test that rollback reverts all changes on validation error."""
        tm = TaskManager(tmp_path)

        # YAML with one valid task and one invalid task (missing name)
        yaml_content = """
        tasks:
          - name: "Valid Task"
            priority: high
          - priority: medium
            # Missing required 'name' field
        """

        result = tm.import_yaml(yaml_content, on_error="rollback")

        # Should return error status, no tasks imported
        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["task_ids"]) == 0
        assert len(result["errors"]) > 0
        assert "name" in result["errors"][0].lower() or "required" in result["errors"][0].lower()

        # Verify no tasks were created
        tasks = tm.list_all()
        assert len(tasks) == 0

    def test_rollback_default_strategy(self, tmp_path):
        """Test that rollback is the default error recovery strategy."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: invalid_priority  # Invalid priority
        """

        # Don't specify on_error, should default to rollback
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(tm.list_all()) == 0

    def test_rollback_multiple_errors(self, tmp_path):
        """Test rollback with multiple validation errors."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Valid Task"
            priority: high
          - priority: medium
            # Missing name
          - name: "Another Task"
            priority: invalid
            # Invalid priority
        """

        result = tm.import_yaml(yaml_content, on_error="rollback")

        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["errors"]) >= 2  # At least 2 errors
        assert len(tm.list_all()) == 0


class TestErrorRecoverySkip:
    """Test skip error recovery strategy."""

    def test_skip_invalid_tasks(self, tmp_path):
        """Test that skip strategy skips invalid tasks and continues."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - priority: medium
            # Missing name - should be skipped
          - name: "Task 3"
            priority: low
        """

        result = tm.import_yaml(yaml_content, on_error="skip", skip_validation=True)

        # Should return partial status
        assert result["status"] == "partial"
        assert result["imported"] == 2  # Only 2 valid tasks
        assert len(result["task_ids"]) == 2
        assert len(result["errors"]) == 1  # 1 error logged
        assert len(result["skipped"]) == 1  # 1 task skipped
        assert "unnamed" in result["skipped"][0]

        # Verify only valid tasks were created
        tasks = tm.list_all()
        assert len(tasks) == 2
        assert tasks[0].name == "Task 1"
        assert tasks[1].name == "Task 3"

    def test_skip_multiple_invalid_tasks(self, tmp_path):
        """Test skip with multiple invalid tasks."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: invalid
            # Invalid priority
          - priority: medium
            # Missing name
          - name: "Task 4"
            priority: low
        """

        result = tm.import_yaml(yaml_content, on_error="skip", skip_validation=True)

        assert result["status"] == "partial"
        assert result["imported"] == 2  # Task 1 and Task 4
        assert len(result["errors"]) == 2
        assert len(result["skipped"]) == 2

        tasks = tm.list_all()
        assert len(tasks) == 2
        assert tasks[0].name == "Task 1"
        assert tasks[1].name == "Task 4"

    def test_skip_all_invalid(self, tmp_path):
        """Test skip when all tasks are invalid."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - priority: high
            # Missing name
          - name: "Task 2"
            priority: invalid
            # Invalid priority
        """

        result = tm.import_yaml(yaml_content, on_error="skip", skip_validation=True)

        # All tasks failed, return error
        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["errors"]) == 2
        assert len(result["skipped"]) == 2
        assert len(tm.list_all()) == 0

    def test_skip_with_success(self, tmp_path):
        """Test skip strategy with all valid tasks (success case)."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: medium
        """

        result = tm.import_yaml(yaml_content, on_error="skip")

        # All tasks valid, should be success
        assert result["status"] == "success"
        assert result["imported"] == 2
        assert len(result["errors"]) == 0
        assert "skipped" not in result or len(result["skipped"]) == 0


class TestErrorRecoveryAbort:
    """Test abort error recovery strategy."""

    def test_abort_on_first_error(self, tmp_path):
        """Test that abort stops immediately on first error."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - priority: medium
            # Missing name - should abort here
          - name: "Task 3"
            priority: low
        """

        result = tm.import_yaml(yaml_content, on_error="abort")

        # Should return error immediately
        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["task_ids"]) == 0
        assert len(result["errors"]) == 1  # Only 1 error (aborted)

        # No tasks created
        tasks = tm.list_all()
        assert len(tasks) == 0

    def test_abort_with_multiple_potential_errors(self, tmp_path):
        """Test abort stops at first error, not processing subsequent errors."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: invalid
            # First error - should abort
          - priority: medium
            # Second error - not processed
        """

        result = tm.import_yaml(yaml_content, on_error="abort", skip_validation=True)

        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["errors"]) == 1  # Only first error
        assert len(tm.list_all()) == 0

    def test_abort_with_valid_tasks_before_error(self, tmp_path):
        """Test abort doesn't commit valid tasks processed before error."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: medium
          - priority: low
            # Error on third task
        """

        result = tm.import_yaml(yaml_content, on_error="abort")

        # Abort strategy: No tasks committed
        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(tm.list_all()) == 0


class TestErrorRecoveryWithUndo:
    """Test error recovery integration with undo functionality."""

    def test_rollback_no_undo_history(self, tmp_path):
        """Test that rollback doesn't create undo history (no changes made)."""
        from clauxton.core.operation_history import OperationHistory

        tm = TaskManager(tmp_path)
        history = OperationHistory(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - priority: invalid
        """

        result = tm.import_yaml(yaml_content, on_error="rollback")

        assert result["status"] == "error"

        # No operation recorded (rollback means no changes)
        operations = history.list_operations()
        assert len(operations) == 0

    def test_skip_creates_undo_history(self, tmp_path):
        """Test that skip strategy creates undo history for successful imports."""
        from clauxton.core.operation_history import OperationHistory

        tm = TaskManager(tmp_path)
        history = OperationHistory(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - priority: invalid
            # Skipped
          - name: "Task 3"
            priority: low
        """

        result = tm.import_yaml(yaml_content, on_error="skip")

        assert result["status"] == "partial"
        assert result["imported"] == 2

        # Operation recorded for 2 successfully imported tasks
        operations = history.list_operations()
        assert len(operations) == 1
        assert operations[0].operation_type == "task_import"
        assert operations[0].operation_data["task_ids"] == result["task_ids"]


class TestErrorRecoveryConfirmationIntegration:
    """Test error recovery with confirmation prompts."""

    def test_skip_with_confirmation_threshold(self, tmp_path):
        """Test skip strategy with confirmation threshold."""
        tm = TaskManager(tmp_path)

        # 10 tasks: some valid, some invalid
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: high
          - priority: medium
            # Missing name - skipped
          - name: "Task 4"
            priority: medium
          - name: "Task 5"
            priority: medium
          - name: "Task 6"
            priority: low
          - name: "Task 7"
            priority: low
          - name: "Task 8"
            priority: low
          - name: "Task 9"
            priority: low
          - name: "Task 10"
            priority: low
        """

        # Skip confirmation AND use skip error recovery
        result = tm.import_yaml(yaml_content, on_error="skip", skip_confirmation=True)

        # Should import 9 valid tasks (1 skipped)
        assert result["status"] == "partial"
        assert result["imported"] == 9
        assert len(result["skipped"]) == 1
        assert len(tm.list_all()) == 9

    def test_rollback_prevents_confirmation(self, tmp_path):
        """Test that rollback errors prevent confirmation check."""
        tm = TaskManager(tmp_path)

        # 10 tasks with one invalid (should trigger confirmation if reached)
        yaml_content = """
        tasks:
          - name: "Task 1"
          - name: "Task 2"
          - priority: invalid
            # Invalid - triggers rollback
          - name: "Task 4"
          - name: "Task 5"
          - name: "Task 6"
          - name: "Task 7"
          - name: "Task 8"
          - name: "Task 9"
          - name: "Task 10"
        """

        result = tm.import_yaml(yaml_content, on_error="rollback")

        # Should return error before confirmation check
        assert result["status"] == "error"
        assert result["imported"] == 0
        assert "confirmation_required" not in result


class TestErrorRecoveryDependencyValidation:
    """Test error recovery with dependency validation errors."""

    def test_skip_with_dependency_errors(self, tmp_path):
        """Test skip strategy with dependency validation errors."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
            depends_on: [TASK-999]
            # Non-existent dependency
          - name: "Task 2"
            priority: medium
        """

        # Skip mode with dependency validation
        # Dependency errors are caught but tasks are already validated as valid
        # So dependency validation fails for the whole batch (rollback-like behavior)
        result = tm.import_yaml(yaml_content, on_error="skip")

        # Actually, both tasks parse fine, but Task 1 has invalid dependency
        # This is a partial success - Task 2 is valid
        assert result["status"] in ["error", "partial"]
        if result["status"] == "partial":
            # Task 2 should be imported, Task 1 fails dependency check
            assert result["imported"] >= 1

    def test_rollback_with_circular_dependency(self, tmp_path):
        """Test rollback with circular dependency error."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            depends_on: [TASK-002]
          - name: "Task 2"
            depends_on: [TASK-001]
            # Circular dependency
        """

        result = tm.import_yaml(yaml_content, on_error="rollback")

        assert result["status"] == "error"
        assert "Circular dependency" in result["errors"][0]
        assert len(tm.list_all()) == 0


class TestErrorRecoveryDryRun:
    """Test error recovery with dry-run mode."""

    def test_dry_run_skip_strategy(self, tmp_path):
        """Test that dry-run with skip strategy validates correctly."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - priority: medium
            # Missing name
          - name: "Task 3"
            priority: low
        """

        result = tm.import_yaml(yaml_content, on_error="skip", dry_run=True)

        # Dry run validates but doesn't import
        # With skip, validation should continue
        assert result["status"] == "partial"
        assert result["imported"] == 0  # Dry run doesn't import
        assert len(result["task_ids"]) == 2  # But shows what would be imported
        assert len(result["skipped"]) == 1
        assert len(tm.list_all()) == 0  # Nothing actually created

    def test_dry_run_rollback_strategy(self, tmp_path):
        """Test that dry-run with rollback strategy returns error."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - priority: invalid
        """

        result = tm.import_yaml(yaml_content, on_error="rollback", dry_run=True)

        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(tm.list_all()) == 0


class TestErrorRecoveryEdgeCases:
    """Test edge cases in error recovery."""

    def test_skip_with_all_validation_errors(self, tmp_path):
        """Test skip when validation errors occur after task parsing."""
        tm = TaskManager(tmp_path)

        # First create a task to establish baseline
        yaml_create = """
        tasks:
          - name: "Existing Task"
            priority: high
        """
        tm.import_yaml(yaml_create)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
            depends_on: [TASK-999]
            # Non-existent dependency
          - name: "Task 2"
            priority: medium
            depends_on: [TASK-888]
            # Non-existent dependency
        """

        result = tm.import_yaml(yaml_content, on_error="skip")

        # With skip mode, dependency validation continues
        # Tasks parse successfully, so they proceed to import
        # Dependency errors are logged but don't block skip mode
        assert result["status"] in ["error", "partial"]
        assert len(result["errors"]) > 0
        # At least some errors should be logged
        assert "TASK-999" in str(result["errors"]) or "TASK-888" in str(result["errors"])

    def test_abort_with_no_errors(self, tmp_path):
        """Test abort strategy with all valid tasks."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: medium
        """

        result = tm.import_yaml(yaml_content, on_error="abort")

        # All valid, should succeed
        assert result["status"] == "success"
        assert result["imported"] == 2
        assert len(result["errors"]) == 0
