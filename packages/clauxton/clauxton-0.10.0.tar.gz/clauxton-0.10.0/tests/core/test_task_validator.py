"""
Tests for TaskValidator - Enhanced validation.
"""

from clauxton.core.task_validator import TaskValidator, ValidationResult


class TestValidationResult:
    """Test ValidationResult class."""

    def test_validation_result_initially_valid(self):
        """Test validation result is initially valid."""
        result = ValidationResult()
        assert result.is_valid()
        assert not result.has_warnings()
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_add_error_makes_invalid(self):
        """Test adding error makes result invalid."""
        result = ValidationResult()
        result.add_error("Test error")
        assert not result.is_valid()
        assert len(result.errors) == 1
        assert result.errors[0] == "Test error"

    def test_add_warning_keeps_valid(self):
        """Test adding warning keeps result valid."""
        result = ValidationResult()
        result.add_warning("Test warning")
        assert result.is_valid()
        assert result.has_warnings()
        assert len(result.warnings) == 1


class TestTaskNameValidation:
    """Test task name validation."""

    def test_empty_task_name(self, tmp_path):
        """Test empty task name is rejected."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "", "priority": "high"}]
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("name is required" in e.lower() for e in result.errors)

    def test_missing_task_name(self, tmp_path):
        """Test missing task name is rejected."""
        validator = TaskValidator(tmp_path)
        tasks = [{"priority": "high"}]
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("name is required" in e.lower() for e in result.errors)

    def test_task_name_too_long(self, tmp_path):
        """Test task name over 255 characters is rejected."""
        validator = TaskValidator(tmp_path)
        long_name = "a" * 256
        tasks = [{"name": long_name, "priority": "high"}]
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("too long" in e.lower() for e in result.errors)

    def test_valid_task_name(self, tmp_path):
        """Test valid task name passes."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Valid Task Name", "priority": "high"}]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()


class TestDuplicateIDValidation:
    """Test duplicate task ID validation."""

    def test_duplicate_id_in_batch(self, tmp_path):
        """Test duplicate IDs in same batch are rejected."""
        validator = TaskValidator(tmp_path)
        tasks = [
            {"id": "TASK-001", "name": "Task 1"},
            {"id": "TASK-001", "name": "Task 2"},  # Duplicate
        ]
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("duplicate task id" in e.lower() for e in result.errors)

    def test_duplicate_id_with_existing(self, tmp_path):
        """Test duplicate ID with existing task is rejected."""
        validator = TaskValidator(tmp_path)
        existing_ids = {"TASK-001", "TASK-002"}
        tasks = [{"id": "TASK-001", "name": "New Task"}]
        result = validator.validate_tasks(tasks, existing_ids)

        assert not result.is_valid()
        assert any("already exists" in e.lower() for e in result.errors)

    def test_unique_ids_pass(self, tmp_path):
        """Test unique IDs pass validation."""
        validator = TaskValidator(tmp_path)
        tasks = [
            {"id": "TASK-001", "name": "Task 1"},
            {"id": "TASK-002", "name": "Task 2"},
        ]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()


class TestDuplicateNameValidation:
    """Test duplicate task name validation (warnings only)."""

    def test_duplicate_name_warning(self, tmp_path):
        """Test duplicate names generate warnings."""
        validator = TaskValidator(tmp_path)
        tasks = [
            {"name": "Same Name", "priority": "high"},
            {"name": "Same Name", "priority": "medium"},
        ]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()  # Still valid (warning only)
        assert result.has_warnings()
        assert any("duplicate task name" in w.lower() for w in result.warnings)

    def test_unique_names_no_warning(self, tmp_path):
        """Test unique names don't generate warnings."""
        validator = TaskValidator(tmp_path)
        tasks = [
            {"name": "Task 1", "priority": "high"},
            {"name": "Task 2", "priority": "medium"},
        ]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()
        assert not result.has_warnings()


class TestPriorityValidation:
    """Test priority validation."""

    def test_invalid_priority(self, tmp_path):
        """Test invalid priority value is rejected."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "priority": "urgent"}]  # Invalid
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("invalid priority" in e.lower() for e in result.errors)

    def test_valid_priorities(self, tmp_path):
        """Test all valid priorities pass."""
        validator = TaskValidator(tmp_path)
        tasks = [
            {"name": "Task 1", "priority": "critical"},
            {"name": "Task 2", "priority": "high"},
            {"name": "Task 3", "priority": "medium"},
            {"name": "Task 4", "priority": "low"},
        ]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()

    def test_missing_priority_is_ok(self, tmp_path):
        """Test missing priority is OK (defaults to medium)."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task"}]  # No priority
        result = validator.validate_tasks(tasks)

        assert result.is_valid()


class TestStatusValidation:
    """Test status validation."""

    def test_invalid_status(self, tmp_path):
        """Test invalid status value is rejected."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "status": "working"}]  # Invalid
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("invalid status" in e.lower() for e in result.errors)

    def test_valid_statuses(self, tmp_path):
        """Test all valid statuses pass."""
        validator = TaskValidator(tmp_path)
        tasks = [
            {"name": "Task 1", "status": "pending"},
            {"name": "Task 2", "status": "in_progress"},
            {"name": "Task 3", "status": "completed"},
            {"name": "Task 4", "status": "blocked"},
        ]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()


class TestDependencyValidation:
    """Test dependency validation."""

    def test_depends_on_not_list(self, tmp_path):
        """Test depends_on must be a list."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "depends_on": "TASK-001"}]  # String, not list
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("must be a list" in e.lower() for e in result.errors)

    def test_depends_on_empty_string(self, tmp_path):
        """Test empty string in depends_on is rejected."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "depends_on": [""]}]  # Empty string
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("cannot be empty" in e.lower() for e in result.errors)

    def test_depends_on_non_string(self, tmp_path):
        """Test non-string dependency ID is rejected."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "depends_on": [123]}]  # Integer
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("must be a string" in e.lower() for e in result.errors)

    def test_valid_depends_on(self, tmp_path):
        """Test valid depends_on passes."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "depends_on": ["TASK-001", "TASK-002"]}]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()


class TestEstimatedHoursValidation:
    """Test estimated hours validation."""

    def test_estimated_hours_negative(self, tmp_path):
        """Test negative estimated hours is rejected."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "estimated_hours": -1}]
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("must be positive" in e.lower() for e in result.errors)

    def test_estimated_hours_zero(self, tmp_path):
        """Test zero estimated hours is rejected."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "estimated_hours": 0}]
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("must be positive" in e.lower() for e in result.errors)

    def test_estimated_hours_too_large(self, tmp_path):
        """Test very large estimated hours generates warning."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "estimated_hours": 2000}]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()  # Valid but has warning
        assert result.has_warnings()
        assert any("very large" in w.lower() for w in result.warnings)

    def test_estimated_hours_non_numeric(self, tmp_path):
        """Test non-numeric estimated hours is rejected."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "estimated_hours": "many"}]
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert any("must be a number" in e.lower() for e in result.errors)

    def test_valid_estimated_hours(self, tmp_path):
        """Test valid estimated hours pass."""
        validator = TaskValidator(tmp_path)
        tasks = [
            {"name": "Task 1", "estimated_hours": 1},
            {"name": "Task 2", "estimated_hours": 2.5},
            {"name": "Task 3", "estimated_hours": 100},
        ]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()


class TestFileValidation:
    """Test files_to_edit validation (warnings only)."""

    def test_files_to_edit_not_list(self, tmp_path):
        """Test files_to_edit not a list generates warning."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "files_to_edit": "main.py"}]  # String, not list
        result = validator.validate_tasks(tasks)

        assert result.is_valid()  # Valid but has warning
        assert result.has_warnings()
        assert any("should be a list" in w.lower() for w in result.warnings)

    def test_file_path_non_string(self, tmp_path):
        """Test non-string file path generates warning."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "files_to_edit": [123]}]  # Integer
        result = validator.validate_tasks(tasks)

        assert result.is_valid()
        assert result.has_warnings()

    def test_nonexistent_file_warning(self, tmp_path):
        """Test nonexistent file generates warning."""
        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "files_to_edit": ["nonexistent.py"]}]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()
        assert result.has_warnings()
        assert any("does not exist" in w.lower() for w in result.warnings)

    def test_existing_file_no_warning(self, tmp_path):
        """Test existing file doesn't generate warning."""
        # Create a test file
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file")

        validator = TaskValidator(tmp_path)
        tasks = [{"name": "Task", "files_to_edit": ["test.py"]}]
        result = validator.validate_tasks(tasks)

        assert result.is_valid()
        # Should not have warning about this file
        assert not any("test.py" in w and "does not exist" in w.lower() for w in result.warnings)


class TestMultipleErrors:
    """Test handling of multiple validation errors."""

    def test_multiple_errors_in_single_task(self, tmp_path):
        """Test task with multiple errors reports all."""
        validator = TaskValidator(tmp_path)
        tasks = [
            {
                "name": "",  # Empty name
                "priority": "urgent",  # Invalid priority
                "estimated_hours": -1,  # Negative hours
            }
        ]
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert len(result.errors) >= 3  # At least 3 errors

    def test_errors_across_multiple_tasks(self, tmp_path):
        """Test errors across multiple tasks are collected."""
        validator = TaskValidator(tmp_path)
        tasks = [
            {"name": "", "priority": "high"},  # Error: empty name
            {"name": "Task 2", "priority": "invalid"},  # Error: invalid priority
            {"name": "Task 3", "estimated_hours": -5},  # Error: negative hours
        ]
        result = validator.validate_tasks(tasks)

        assert not result.is_valid()
        assert len(result.errors) >= 3
