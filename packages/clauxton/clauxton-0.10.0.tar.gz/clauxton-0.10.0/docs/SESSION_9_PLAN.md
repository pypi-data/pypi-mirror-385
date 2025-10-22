# Session 9 Action Plan

**Created**: 2025-10-21 (After Session 8 Final Review)
**Target**: Core Module Testing - Eliminate Zero Coverage
**Estimated Duration**: 6-8 hours (Full work day)
**Priority**: **CRITICAL** - Production blocker

---

## 📊 Session 8 Critical Findings

### 🚨 Zero Coverage Modules Identified

| Module | Lines | Impact | Status |
|--------|-------|--------|--------|
| `operation_history.py` | 159 | Undo broken | ❌ CRITICAL |
| `task_validator.py` | 105 | Data corruption risk | ❌ CRITICAL |
| `logger.py` | 79 | Silent failures | ❌ HIGH |
| `confirmation_manager.py` | 68 | Bulk ops unsafe | ❌ HIGH |
| `task_manager.py` | 324/351 | Core logic broken | ❌ CRITICAL |

**Total Untested Lines**: 735 lines (in critical modules)

### 📈 Coverage Status

```
Current:  ████████████████░░░░░░░░░░░░░░░░  70%
Target:   ████████████████████████░░░░░░░░  80%
Goal:     ████████████████████████████░░░░  90% (by Session 10)
```

---

## 🎯 Session 9 Primary Goal

**Eliminate all zero-coverage modules in core business logic**

### Success Criteria

**Must Have**:
- ✅ Zero modules with 0% coverage (5 modules → 0 modules)
- ✅ Overall coverage: 70% → 80%+
- ✅ All critical paths tested
- ✅ operation_history.py: 0% → 80%+
- ✅ task_validator.py: 0% → 90%+
- ✅ logger.py: 0% → 80%+

**Nice to Have**:
- ⭐ task_manager.py: 8% → 60%+
- ⭐ confirmation_manager.py: 0% → 70%+
- ⭐ Overall coverage: 80% → 85%

---

## 📋 Detailed Task Breakdown

### Priority 1: Operation History Testing (CRITICAL)

**File**: `clauxton/core/operation_history.py` (159 lines, 0% coverage)

**Why Critical**: Undo functionality completely untested. Data loss risk.

**Test File**: `tests/core/test_operation_history.py` (NEW)

#### Test Categories

1. **Operation Recording** (8-10 tests)
   ```python
   def test_record_kb_add_operation()
   def test_record_task_add_operation()
   def test_record_kb_update_operation()
   def test_record_kb_delete_operation()
   def test_record_task_delete_operation()
   def test_operation_metadata_stored()
   def test_operation_timestamp_accurate()
   def test_multiple_operations_ordered()
   ```

2. **Undo Execution** (10-12 tests)
   ```python
   def test_undo_kb_add()  # Removes added entry
   def test_undo_kb_delete()  # Restores deleted entry
   def test_undo_kb_update()  # Reverts to previous version
   def test_undo_task_add()
   def test_undo_task_delete()
   def test_undo_task_update()
   def test_undo_with_no_operations()
   def test_undo_updates_history()
   def test_undo_returns_success_status()
   def test_undo_returns_error_on_failure()
   def test_undo_preserves_operation_order()
   def test_undo_handles_corrupted_history()
   ```

3. **History Management** (5-7 tests)
   ```python
   def test_list_operations_returns_all()
   def test_list_operations_with_limit()
   def test_get_last_operation()
   def test_clear_history()
   def test_history_persistence_across_instances()
   def test_history_file_permissions()
   def test_history_atomic_writes()
   ```

4. **Edge Cases** (5-8 tests)
   ```python
   def test_undo_with_missing_files()
   def test_undo_with_permission_errors()
   def test_concurrent_operation_handling()
   def test_large_history_performance()
   def test_corrupted_history_recovery()
   def test_unicode_in_operation_descriptions()
   def test_operation_size_limits()
   def test_history_rotation()
   ```

**Estimated**: 28-37 tests, 4-5 hours

**Target Coverage**: 80%+

---

### Priority 2: Task Validator Testing (CRITICAL)

**File**: `clauxton/core/task_validator.py` (105 lines, 0% coverage)

**Why Critical**: Data validation completely untested. Invalid data can corrupt state.

**Test File**: `tests/core/test_task_validator.py` (NEW)

#### Test Categories

1. **Basic Validation** (8-10 tests)
   ```python
   def test_validate_task_name_not_empty()
   def test_validate_task_name_length()
   def test_validate_priority_valid()
   def test_validate_priority_invalid()
   def test_validate_status_valid()
   def test_validate_status_invalid()
   def test_validate_estimated_hours_positive()
   def test_validate_estimated_hours_reasonable()
   def test_validate_depends_on_list()
   def test_validate_files_to_edit_list()
   ```

2. **Duplicate Detection** (6-8 tests)
   ```python
   def test_detect_duplicate_task_id()
   def test_detect_duplicate_task_name_warning()
   def test_duplicate_id_blocks_creation()
   def test_duplicate_name_shows_warning()
   def test_case_sensitive_duplicate_detection()
   def test_whitespace_normalized_duplicates()
   def test_duplicate_across_statuses()
   def test_duplicate_detection_performance()
   ```

3. **Dependency Validation** (8-10 tests)
   ```python
   def test_validate_dependencies_exist()
   def test_validate_no_circular_dependencies()
   def test_validate_no_self_dependency()
   def test_dependency_chain_validation()
   def test_missing_dependency_error()
   def test_invalid_dependency_format()
   def test_dependency_status_check()
   def test_transitive_dependency_validation()
   def test_dependency_cycle_detection()
   def test_complex_dag_validation()
   ```

4. **File Path Validation** (5-7 tests)
   ```python
   def test_validate_file_paths_format()
   def test_validate_file_paths_exist()
   def test_validate_file_paths_relative()
   def test_validate_no_path_traversal()
   def test_validate_unicode_paths()
   def test_validate_windows_paths()
   def test_nonexistent_file_warning()
   ```

5. **Edge Cases** (5-7 tests)
   ```python
   def test_validate_unicode_task_name()
   def test_validate_emoji_in_name()
   def test_validate_very_long_name()
   def test_validate_special_characters()
   def test_validate_empty_dependencies()
   def test_validate_large_estimated_hours()
   def test_validation_error_messages_clear()
   ```

**Estimated**: 32-42 tests, 3-4 hours

**Target Coverage**: 90%+

---

### Priority 3: Logger Testing (HIGH)

**File**: `clauxton/utils/logger.py` (79 lines, 0% coverage)

**Why High**: Logging untested. Silent failures make debugging impossible.

**Test File**: `tests/utils/test_logger.py` (EXISTS but may need enhancement)

#### Current Status Check

**Action**: Review existing test file first
```bash
cat tests/utils/test_logger.py | head -50
```

#### Test Categories (if tests missing)

1. **Log Writing** (6-8 tests)
   ```python
   def test_log_creates_entry()
   def test_log_with_metadata()
   def test_log_levels_respected()
   def test_log_json_format()
   def test_log_unicode_content()
   def test_log_special_characters()
   def test_log_large_messages()
   def test_log_concurrent_writes()
   ```

2. **Log Rotation** (5-7 tests)
   ```python
   def test_daily_log_files_created()
   def test_old_logs_cleaned_up()
   def test_rotation_threshold_respected()
   def test_rotation_preserves_data()
   def test_rotation_permissions()
   def test_rotation_atomic()
   def test_rotation_error_handling()
   ```

3. **Log Retrieval** (6-8 tests)
   ```python
   def test_get_recent_logs()
   def test_filter_by_operation()
   def test_filter_by_level()
   def test_filter_by_date()
   def test_get_logs_by_date()
   def test_limit_results()
   def test_malformed_json_skipped()
   def test_empty_log_handling()
   ```

4. **Edge Cases** (5-7 tests)
   ```python
   def test_corrupted_log_file()
   def test_permission_denied()
   def test_disk_full()
   def test_concurrent_log_access()
   def test_log_directory_missing()
   def test_unicode_log_paths()
   def test_large_log_files()
   ```

**Estimated**: 22-30 tests, 2-3 hours

**Target Coverage**: 80%+

**Note**: If tests already exist, enhance coverage to 80%+

---

### Priority 4: Task Manager Core Logic (CRITICAL)

**File**: `clauxton/core/task_manager.py` (351 lines, 8% coverage)

**Why Critical**: Core task management severely undertested.

**Test File**: `tests/core/test_task_manager.py` (EXISTS, ~100 tests, but only 8% coverage)

**Strategy**: Identify untested code paths and add targeted tests

#### Analysis Required

1. **Check Existing Coverage**:
   ```bash
   pytest tests/core/test_task_manager.py --cov=clauxton/core/task_manager --cov-report=term-missing
   ```

2. **Identify Missing Lines**: Lines 52-56, 83-109, 150-209, etc.

3. **Add Targeted Tests** for uncovered areas

#### Likely Missing Test Areas

1. **Bulk Operations** (10-12 tests)
   ```python
   def test_add_many_with_progress()
   def test_add_many_validation()
   def test_add_many_atomic()
   def test_add_many_rollback()
   def test_add_many_empty_list()
   def test_add_many_duplicates()
   def test_add_many_invalid_tasks()
   def test_add_many_performance()
   def test_add_many_progress_callback()
   def test_add_many_with_dependencies()
   def test_add_many_dag_validation()
   def test_add_many_error_recovery()
   ```

2. **Complex DAG Operations** (8-10 tests)
   ```python
   def test_complex_dependency_graph()
   def test_transitive_dependencies()
   def test_diamond_dependency_pattern()
   def test_parallel_dependencies()
   def test_deep_dependency_chains()
   def test_dag_with_100_nodes()
   def test_dag_cycle_detection_performance()
   def test_topological_sort_correctness()
   def test_dependency_update_cascades()
   def test_remove_task_updates_dependents()
   ```

3. **Error Handling** (8-10 tests)
   ```python
   def test_corrupted_tasks_file()
   def test_concurrent_modifications()
   def test_permission_errors()
   def test_disk_full_handling()
   def test_invalid_yaml_recovery()
   def test_backup_restoration()
   def test_atomic_write_failure()
   def test_validation_error_rollback()
   def test_partial_operation_cleanup()
   def test_inconsistent_state_recovery()
   ```

4. **Edge Cases** (8-10 tests)
   ```python
   def test_empty_task_manager()
   def test_1000_tasks_performance()
   def test_unicode_task_names()
   def test_emoji_in_descriptions()
   def test_very_long_dependency_chains()
   def test_circular_reference_edge_cases()
   def test_task_status_transitions()
   def test_priority_changes()
   def test_concurrent_task_updates()
   def test_task_file_locking()
   ```

**Estimated**: 34-42 tests, 4-5 hours

**Target Coverage**: 50%+ (minimum), 60%+ (stretch goal)

---

### Priority 5: Confirmation Manager (Optional/Stretch)

**File**: `clauxton/core/confirmation_manager.py` (68 lines, 0% coverage)

**Why Medium**: Used in bulk operations, but less critical than validators.

**Test File**: `tests/core/test_confirmation_manager.py` (NEW)

#### Test Categories (If Time Permits)

1. **Threshold Detection** (5-7 tests)
   ```python
   def test_threshold_not_exceeded()
   def test_threshold_exceeded()
   def test_custom_threshold()
   def test_threshold_calculation()
   def test_zero_threshold()
   def test_very_large_threshold()
   def test_negative_threshold_error()
   ```

2. **Preview Generation** (5-7 tests)
   ```python
   def test_preview_includes_count()
   def test_preview_includes_estimated_hours()
   def test_preview_priority_breakdown()
   def test_preview_status_breakdown()
   def test_preview_format()
   def test_preview_with_empty_list()
   def test_preview_with_large_list()
   ```

3. **Confirmation Modes** (4-6 tests)
   ```python
   def test_auto_mode()
   def test_always_mode()
   def test_never_mode()
   def test_mode_switching()
   def test_invalid_mode()
   def test_mode_persistence()
   ```

**Estimated**: 14-20 tests, 2-3 hours

**Target Coverage**: 70%+

**Note**: Only tackle if time permits after Priority 1-4

---

## 🗓️ Session 9 Timeline

### Phase 1: Setup & Analysis (30 min)

- [ ] Pull latest changes
- [ ] Review Session 8 findings
- [ ] Analyze existing test files
- [ ] Set up test environment
- [ ] Create test file templates

### Phase 2: Operation History (2-2.5 hours)

- [ ] Create `tests/core/test_operation_history.py`
- [ ] Write operation recording tests (8-10 tests)
- [ ] Write undo execution tests (10-12 tests)
- [ ] Write history management tests (5-7 tests)
- [ ] Write edge case tests (5-8 tests)
- [ ] Run tests, verify 80%+ coverage
- [ ] Commit progress

**Checkpoint 1**: operation_history.py: 0% → 80%+

### Phase 3: Task Validator (1.5-2 hours)

- [ ] Create `tests/core/test_task_validator.py`
- [ ] Write basic validation tests (8-10 tests)
- [ ] Write duplicate detection tests (6-8 tests)
- [ ] Write dependency validation tests (8-10 tests)
- [ ] Write file path validation tests (5-7 tests)
- [ ] Write edge case tests (5-7 tests)
- [ ] Run tests, verify 90%+ coverage
- [ ] Commit progress

**Checkpoint 2**: task_validator.py: 0% → 90%+

### Phase 4: Logger Enhancement (1-1.5 hours)

- [ ] Review existing `tests/utils/test_logger.py`
- [ ] Identify coverage gaps
- [ ] Add missing tests (targeting 80%+)
- [ ] Test log writing (if missing)
- [ ] Test log rotation (if missing)
- [ ] Test log retrieval (if missing)
- [ ] Test edge cases (if missing)
- [ ] Run tests, verify 80%+ coverage
- [ ] Commit progress

**Checkpoint 3**: logger.py: 0% → 80%+

### Phase 5: Task Manager Core (2-2.5 hours)

- [ ] Analyze existing test coverage gaps
- [ ] Identify untested code paths
- [ ] Write bulk operation tests (10-12 tests)
- [ ] Write complex DAG tests (8-10 tests)
- [ ] Write error handling tests (8-10 tests)
- [ ] Write edge case tests (8-10 tests)
- [ ] Run tests, verify 50%+ coverage
- [ ] Commit progress

**Checkpoint 4**: task_manager.py: 8% → 50%+

### Phase 6: Wrap-up (30 min)

- [ ] Run full test suite
- [ ] Verify all quality checks pass
- [ ] Update coverage metrics
- [ ] Create SESSION_9_SUMMARY.md
- [ ] Final commit and push

---

## 🎯 Expected Outcomes

### Code Metrics (Before → After)

| Metric | Before | Target | Stretch |
|--------|--------|--------|---------|
| Overall Coverage | 70% | 80% | 85% |
| Zero-coverage modules | 5 | 0 | 0 |
| operation_history.py | 0% | 80% | 85% |
| task_validator.py | 0% | 90% | 95% |
| logger.py | 0% | 80% | 85% |
| task_manager.py | 8% | 50% | 60% |
| Total Tests | 157 | 240+ | 260+ |

### Coverage Visualization

**Before (Session 8)**:
```
Overall:  ████████████████░░░░░░░░░░░░░░░░  70%
CLI:      ████████████████████░░  80%
Core:     ███░░░░░░░░░░░░░░░░░░  15%
Utils:    ████████████░░░░░░░░░  60%
```

**After (Session 9 Target)**:
```
Overall:  ████████████████████████░░░░░░░░  80%
CLI:      ████████████████████░░  80%
Core:     ████████████████░░░░░  60%
Utils:    ████████████████░░░░░  80%
```

---

## 🔧 Technical Guidelines

### Test Writing Standards

#### 1. Test Structure
```python
def test_specific_behavior_with_context():
    """
    Test that X does Y when Z condition.

    Verifies:
    - Expected behavior
    - Edge case handling
    - Error messages
    """
    # Arrange
    setup_data = ...

    # Act
    result = function_under_test(setup_data)

    # Assert
    assert result == expected
    assert error_message_is_clear
```

#### 2. Fixture Usage
```python
@pytest.fixture
def temp_history(tmp_path: Path) -> OperationHistory:
    """Create temporary operation history for testing."""
    return OperationHistory(tmp_path)

def test_with_fixture(temp_history: OperationHistory):
    # Test uses isolated history
    ...
```

#### 3. Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("valid", True),
    ("", False),
    ("   ", False),
    ("🚀 emoji", True),
])
def test_validation_cases(input, expected):
    assert validate(input) == expected
```

#### 4. Exception Testing
```python
def test_raises_validation_error():
    with pytest.raises(ValidationError, match="clear error message"):
        validate_task(invalid_data)
```

#### 5. Mock Usage (When Needed)
```python
from unittest.mock import Mock, patch

def test_with_mock(tmp_path):
    mock_callback = Mock()
    task_manager.add_many(tasks, progress_callback=mock_callback)

    assert mock_callback.call_count == len(tasks)
```

---

### Coverage Verification Commands

```bash
# Test specific module with coverage
pytest tests/core/test_operation_history.py \
  --cov=clauxton/core/operation_history \
  --cov-report=term-missing \
  --cov-report=html

# Check overall coverage
pytest --cov=clauxton --cov-report=term

# Generate HTML coverage report
pytest --cov=clauxton --cov-report=html
open htmlcov/index.html

# Test with verbose output
pytest tests/core/test_operation_history.py -v

# Test specific function
pytest tests/core/test_operation_history.py::test_undo_kb_add -v
```

---

### Quality Checks

Run all quality checks before committing:

```bash
# Type checking
mypy clauxton

# Linting
ruff check clauxton tests

# Security
bandit -r clauxton/ -ll

# Tests
pytest

# All in one
mypy clauxton && ruff check clauxton tests && bandit -r clauxton/ -ll && pytest
```

---

## 🚫 Out of Scope (Session 9)

Explicitly **NOT** included in Session 9:

1. ❌ MCP server testing (deferred to Session 10)
2. ❌ Integration testing framework (deferred to Session 10)
3. ❌ Performance benchmarking (deferred to Session 10)
4. ❌ Edge case testing framework (will start in Session 10)
5. ❌ Documentation updates (only SESSION_9_SUMMARY.md)
6. ❌ Code refactoring (test-only session)
7. ❌ New features (bug fixes OK if found)

---

## 📝 Testing Best Practices

### 1. Test Independence

- Each test should be runnable in isolation
- Use fixtures for setup/teardown
- No shared state between tests

### 2. Test Clarity

- Descriptive test names
- Clear arrange-act-assert structure
- One assertion per concept

### 3. Test Coverage

- Aim for 80%+ line coverage
- Test all branches (if/else, try/except)
- Test edge cases explicitly

### 4. Test Performance

- Tests should run fast (<1s per test)
- Use `tmp_path` for file operations
- Mock slow operations (network, etc.)

### 5. Test Maintainability

- Avoid test duplication
- Use parametrize for similar tests
- Keep tests simple and focused

---

## 🎓 Common Testing Patterns

### Pattern 1: File Operations

```python
def test_creates_file(tmp_path: Path):
    """Test file creation."""
    file_path = tmp_path / "test.yml"

    write_yaml(file_path, {"key": "value"})

    assert file_path.exists()
    assert file_path.read_text() == "key: value\n"
```

### Pattern 2: Exception Handling

```python
def test_handles_error_gracefully():
    """Test error handling."""
    with pytest.raises(ValidationError) as exc_info:
        validate_task({"name": ""})

    assert "name cannot be empty" in str(exc_info.value)
```

### Pattern 3: State Verification

```python
def test_state_updated_correctly():
    """Test state changes."""
    manager = TaskManager(tmp_path)
    initial_count = len(manager.list_all())

    manager.add(task)

    assert len(manager.list_all()) == initial_count + 1
    assert manager.get(task.id) == task
```

### Pattern 4: Callback Testing

```python
def test_callback_invoked():
    """Test callback is called."""
    callback = Mock()

    manager.add_many(tasks, progress_callback=callback)

    assert callback.call_count == len(tasks)
    callback.assert_called_with(len(tasks), len(tasks))
```

---

## 📊 Progress Tracking

### Checklist

**Setup**:
- [ ] Environment ready
- [ ] Test files created
- [ ] Coverage baseline measured

**Priority 1 - Operation History**:
- [ ] Recording tests (8-10)
- [ ] Undo tests (10-12)
- [ ] History management tests (5-7)
- [ ] Edge cases (5-8)
- [ ] Coverage: 0% → 80%+

**Priority 2 - Task Validator**:
- [ ] Basic validation (8-10)
- [ ] Duplicate detection (6-8)
- [ ] Dependency validation (8-10)
- [ ] File path validation (5-7)
- [ ] Edge cases (5-7)
- [ ] Coverage: 0% → 90%+

**Priority 3 - Logger**:
- [ ] Existing tests reviewed
- [ ] Missing tests added
- [ ] Coverage: 0% → 80%+

**Priority 4 - Task Manager**:
- [ ] Coverage gaps identified
- [ ] Bulk operations (10-12)
- [ ] Complex DAG (8-10)
- [ ] Error handling (8-10)
- [ ] Edge cases (8-10)
- [ ] Coverage: 8% → 50%+

**Wrap-up**:
- [ ] All tests passing
- [ ] Quality checks passing
- [ ] SESSION_9_SUMMARY.md created
- [ ] Changes committed

---

## 🔗 Related Documents

- **Session 8 Review**: `docs/SESSION_8_FINAL_REVIEW.md`
- **Coverage Analysis**: `docs/COVERAGE_GAPS_ANALYSIS.md`
- **Original Plan**: `docs/SESSION_8_PLAN.md`
- **Test Performance**: `docs/TEST_PERFORMANCE.md`

---

## 💡 Tips for Success

### 1. Start Simple

Begin with the easiest tests to build momentum:
- Basic validation tests
- Happy path tests
- Simple edge cases

Then move to complex scenarios:
- Error handling
- Edge cases
- Integration

### 2. Use Coverage to Guide

After each test batch:
```bash
pytest tests/core/test_X.py --cov=clauxton/core/X --cov-report=term-missing
```

Look at "Missing" lines and write tests to cover them.

### 3. Commit Frequently

Commit after each module reaches target coverage:
```bash
git add tests/core/test_operation_history.py
git commit -m "test: Add operation history tests (0% → 80%)"
```

### 4. Take Breaks

Testing is mentally intensive. Take 5-10 min breaks between modules.

### 5. Document Assumptions

If a test makes assumptions, document them:
```python
def test_undo_assumes_valid_history():
    """
    Test undo with valid history.

    Assumption: History file is well-formed YAML.
    Edge case of corrupted history tested separately.
    """
```

---

## 🎯 Session 9 Success Definition

**Success** = All of the following:

1. ✅ Zero modules with 0% coverage (5 → 0)
2. ✅ Overall coverage ≥ 80%
3. ✅ operation_history.py ≥ 80%
4. ✅ task_validator.py ≥ 90%
5. ✅ logger.py ≥ 80%
6. ✅ task_manager.py ≥ 50%
7. ✅ All tests passing (240+ total)
8. ✅ All quality checks passing

**Stretch Success** = Above + any of:

- ⭐ Overall coverage ≥ 85%
- ⭐ task_manager.py ≥ 60%
- ⭐ confirmation_manager.py ≥ 70%
- ⭐ Total tests ≥ 260

---

**Ready for Session 9!** 🚀

**Estimated Total Time**: 6-8 hours (full work day)

**Priority Order**: Operation History → Task Validator → Logger → Task Manager

**Goal**: Make Clauxton production-ready by eliminating critical testing gaps.
