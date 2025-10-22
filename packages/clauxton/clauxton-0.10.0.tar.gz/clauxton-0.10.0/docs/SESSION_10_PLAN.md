# Session 10 Action Plan

**Created**: 2025-10-21 (After Session 9 Verification)
**Target**: Integration Testing & Coverage Refinement
**Estimated Duration**: 4-6 hours
**Priority**: **HIGH** - Integration tests critical for production confidence

---

## 📊 Session 9 Critical Learning

### ⚠️ LESSON: Always Verify Before Planning

Session 9 taught us that coverage reports can be misleading. **Before creating this plan**, we verified actual coverage:

| Module | Previous Report | Actual Coverage | Tests | Status |
|--------|----------------|-----------------|-------|--------|
| conflict_detector.py | 14% | **96%** ✅ | 18 | Nearly perfect |
| knowledge_base.py | 12% | **72%** ✅ | 41 | Good |
| search.py | 19% | **86%** ✅ | 22 | Excellent |

**Conclusion**: These modules are NOT the problem! The issue is **missing integration tests**.

---

## 🎯 Session 10 Revised Goals

### Primary Goal (Priority: CRITICAL)
**Create comprehensive integration test framework**

Integration tests are currently **0%**. This is the real gap, not unit test coverage.

### Secondary Goal (Priority: HIGH)
**Improve knowledge_base.py coverage** (72% → 80%+)

This is the only module that genuinely needs improvement.

---

## 📋 Detailed Task Breakdown

### Phase 1: Integration Test Framework Setup (30-45 min)

#### Create Test Infrastructure

**New Directory Structure**:
```
tests/integration/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_cli_workflows.py    # CLI end-to-end tests
├── test_mcp_workflows.py    # MCP integration tests
└── test_file_operations.py  # File system integration
```

**Fixtures to Create** (`conftest.py`):
```python
@pytest.fixture
def integration_project(tmp_path: Path) -> Path:
    """Create a full Clauxton project for integration testing."""
    project = tmp_path / "test_project"
    project.mkdir()
    # Initialize .clauxton structure
    return project

@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide CLI runner for integration tests."""
    return CliRunner()

@pytest.fixture
def mcp_server(integration_project: Path):
    """Provide MCP server instance for testing."""
    # Setup MCP server
    pass
```

**Deliverable**: Integration test infrastructure ready

---

### Phase 2: CLI Integration Tests (2-2.5 hours)

#### Test Categories

##### 1. Knowledge Base Workflows (8-10 tests)

**Test File**: `tests/integration/test_cli_workflows.py`

```python
def test_kb_full_workflow(cli_runner, tmp_path):
    """Test complete KB workflow: init → add → search → update → delete."""
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = cli_runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add entry
        result = cli_runner.invoke(
            cli,
            ["kb", "add", "--title", "Test Entry", "--category", "architecture"]
        )
        assert result.exit_code == 0
        entry_id = extract_entry_id(result.output)

        # Search
        result = cli_runner.invoke(cli, ["kb", "search", "Test"])
        assert result.exit_code == 0
        assert "Test Entry" in result.output

        # Update
        result = cli_runner.invoke(
            cli,
            ["kb", "update", entry_id, "--title", "Updated Entry"]
        )
        assert result.exit_code == 0

        # Verify update
        result = cli_runner.invoke(cli, ["kb", "get", entry_id])
        assert "Updated Entry" in result.output

        # Delete
        result = cli_runner.invoke(cli, ["kb", "delete", entry_id])
        assert result.exit_code == 0

        # Verify deletion
        result = cli_runner.invoke(cli, ["kb", "list"])
        assert entry_id not in result.output

def test_kb_import_export_workflow(cli_runner, tmp_path):
    """Test KB export and import workflow."""
    # Add entries → export → clear → import → verify

def test_kb_search_workflow(cli_runner, tmp_path):
    """Test search functionality across multiple entries."""
    # Add 10 entries → search with various queries → verify results

def test_kb_category_filtering(cli_runner, tmp_path):
    """Test filtering by category."""
    # Add entries in different categories → filter → verify

def test_kb_tag_search(cli_runner, tmp_path):
    """Test tag-based search."""
    # Add entries with tags → search by tag → verify

def test_kb_empty_state(cli_runner, tmp_path):
    """Test KB commands on empty KB."""
    # Initialize → run commands on empty KB → verify graceful handling

def test_kb_large_dataset(cli_runner, tmp_path):
    """Test KB with 100+ entries."""
    # Add 100 entries → search → list → verify performance

def test_kb_unicode_content(cli_runner, tmp_path):
    """Test KB with Unicode/emoji content."""
    # Add entry with Japanese text + emoji → retrieve → verify

def test_kb_error_recovery(cli_runner, tmp_path):
    """Test KB error handling."""
    # Try invalid operations → verify error messages → verify state consistency
```

**Estimated**: 8-10 tests, 1.5 hours

---

##### 2. Task Management Workflows (10-12 tests)

```python
def test_task_full_workflow(cli_runner, tmp_path):
    """Test complete task workflow: add → list → update → complete → delete."""

def test_task_dependency_workflow(cli_runner, tmp_path):
    """Test task dependencies and DAG validation."""
    # Add tasks with dependencies → verify order → update → verify cascade

def test_task_import_yaml_workflow(cli_runner, tmp_path):
    """Test YAML import workflow."""
    # Create YAML → import → verify → undo → verify rollback

def test_task_import_with_confirmation(cli_runner, tmp_path):
    """Test import with confirmation threshold."""
    # Import 15 tasks → expect confirmation prompt → accept/reject → verify

def test_task_import_error_recovery(cli_runner, tmp_path):
    """Test import error handling modes (rollback/skip/abort)."""

def test_task_conflict_detection(cli_runner, tmp_path):
    """Test conflict detection workflow."""
    # Add conflicting tasks → detect → resolve → verify

def test_task_status_transitions(cli_runner, tmp_path):
    """Test task status lifecycle."""
    # pending → in_progress → completed → verify transitions

def test_task_next_recommendation(cli_runner, tmp_path):
    """Test AI next task recommendation."""
    # Add tasks with dependencies → call next → verify recommendation

def test_task_bulk_operations(cli_runner, tmp_path):
    """Test bulk task operations."""
    # Add many → bulk update → bulk delete → verify

def test_task_export_import_cycle(cli_runner, tmp_path):
    """Test export → import cycle preserves data."""

def test_task_undo_workflow(cli_runner, tmp_path):
    """Test undo functionality."""
    # Import tasks → undo → verify rollback

def test_task_empty_state(cli_runner, tmp_path):
    """Test task commands on empty state."""
```

**Estimated**: 10-12 tests, 2 hours

---

##### 3. Cross-Module Integration (5-7 tests)

```python
def test_kb_task_integration(cli_runner, tmp_path):
    """Test KB and Task interaction."""
    # Add KB entry about task → create task referencing entry → verify

def test_conflict_kb_integration(cli_runner, tmp_path):
    """Test conflict detection with KB entries."""
    # Add KB entries about files → add tasks editing same files → detect conflicts

def test_undo_across_modules(cli_runner, tmp_path):
    """Test undo across KB and Task operations."""
    # KB add → Task add → undo Task → undo KB → verify

def test_config_persistence(cli_runner, tmp_path):
    """Test configuration persistence across sessions."""
    # Set config → exit → reinit → verify config persisted

def test_backup_restore_workflow(cli_runner, tmp_path):
    """Test backup and restore."""
    # Create data → backup → corrupt → restore → verify

def test_file_permissions_workflow(cli_runner, tmp_path):
    """Test file permission handling."""
    # Create files → check permissions → modify → verify security

def test_concurrent_cli_invocations(cli_runner, tmp_path):
    """Test multiple CLI invocations (basic)."""
    # Run multiple commands → verify no corruption
```

**Estimated**: 5-7 tests, 1.5 hours

---

### Phase 3: MCP Server Integration Tests (1.5-2 hours)

#### Test Categories

**Test File**: `tests/integration/test_mcp_workflows.py`

##### MCP Tool Integration (8-10 tests)

```python
def test_mcp_kb_tools_workflow(mcp_server):
    """Test KB tools via MCP."""
    # kb_add → kb_search → kb_update → kb_delete

def test_mcp_task_tools_workflow(mcp_server):
    """Test task tools via MCP."""
    # task_add → task_list → task_update → task_delete

def test_mcp_task_import_workflow(mcp_server):
    """Test task_import_yaml via MCP."""
    # Prepare YAML → task_import_yaml → verify → undo

def test_mcp_conflict_tools_workflow(mcp_server):
    """Test conflict detection tools via MCP."""
    # detect_conflicts → recommend_safe_order → check_file_conflicts

def test_mcp_undo_workflow(mcp_server):
    """Test undo via MCP."""
    # Perform operations → undo_last_operation → verify

def test_mcp_tool_error_handling(mcp_server):
    """Test MCP tool error responses."""
    # Send invalid requests → verify error responses

def test_mcp_tool_composition(mcp_server):
    """Test chaining multiple MCP tools."""
    # kb_add → task_add → detect_conflicts → verify

def test_mcp_concurrent_tools(mcp_server):
    """Test concurrent MCP tool invocations (basic)."""

def test_mcp_large_payload(mcp_server):
    """Test MCP with large data payloads."""
    # Import 100+ tasks via MCP → verify performance

def test_mcp_unicode_handling(mcp_server):
    """Test MCP with Unicode data."""
```

**Estimated**: 8-10 tests, 1.5 hours

---

### Phase 4: Knowledge Base Coverage Refinement (1 hour)

#### Improve knowledge_base.py (72% → 80%+)

**Current Missing Coverage** (60 lines):
- Lines 34-36: Initialization edge cases
- Lines 384: Category validation edge case
- Lines 411: Search edge case
- Lines 493-495: Update validation
- Lines 531-583: Export functionality (53 lines!)
- Lines 606-652: Import functionality (47 lines!)
- Lines 676-712: Advanced operations (37 lines!)

**Priority**: Export/Import functions (100 lines uncovered!)

**New Tests Needed** (8-12 tests):

```python
def test_export_empty_kb(tmp_path):
    """Test exporting empty KB."""

def test_export_large_kb(tmp_path):
    """Test exporting KB with 100+ entries."""

def test_export_unicode_content(tmp_path):
    """Test exporting entries with Unicode."""

def test_export_all_categories(tmp_path):
    """Test exporting entries from all categories."""

def test_import_valid_markdown(tmp_path):
    """Test importing valid Markdown docs."""

def test_import_invalid_format(tmp_path):
    """Test import error handling."""

def test_import_duplicate_handling(tmp_path):
    """Test importing duplicate entries."""

def test_import_large_file(tmp_path):
    """Test importing large documentation."""

def test_export_import_cycle(tmp_path):
    """Test export → import preserves data."""

def test_update_nonexistent_entry(tmp_path):
    """Test updating non-existent entry."""

def test_category_validation_edge_cases(tmp_path):
    """Test category validation with edge cases."""

def test_search_edge_cases(tmp_path):
    """Test search with empty query, special chars, etc."""
```

**Estimated**: 8-12 tests, 1 hour

---

### Phase 5: File System Integration Tests (30-45 min)

**Test File**: `tests/integration/test_file_operations.py`

#### File Operation Tests (5-7 tests)

```python
def test_atomic_file_writes(tmp_path):
    """Test atomic file write operations."""
    # Write → interrupt (mock) → verify no corruption

def test_backup_on_modification(tmp_path):
    """Test automatic backups."""
    # Modify → verify backup created → restore

def test_file_permission_enforcement(tmp_path):
    """Test file permissions are enforced."""
    # Create files → check permissions (600) → verify

def test_concurrent_file_access(tmp_path):
    """Test concurrent access to same file (basic)."""

def test_file_corruption_recovery(tmp_path):
    """Test recovery from corrupted files."""
    # Corrupt YAML → read → verify error handling → restore from backup

def test_large_file_handling(tmp_path):
    """Test handling of large YAML files."""
    # Create large file → read → write → verify performance

def test_unicode_file_paths(tmp_path):
    """Test Unicode in file paths."""
```

**Estimated**: 5-7 tests, 45 minutes

---

## 🎯 Expected Outcomes

### Test Metrics (Before → After)

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Total Tests** | 157 | 195-210 | +38-53 |
| **Integration Tests** | 0 | 30-40 | NEW |
| **knowledge_base.py Coverage** | 72% | 80%+ | +8%+ |
| **Overall Coverage** | ~75% | ~78-80% | +3-5% |

### Coverage Breakdown (After Session 10)

```
Core Modules:
├── operation_history.py: 81% ✅
├── task_validator.py: 100% ✅
├── logger.py: 97% ✅
├── confirmation_manager.py: 96% ✅
├── task_manager.py: 90% ✅
├── conflict_detector.py: 96% ✅
├── search.py: 86% ✅
└── knowledge_base.py: 72% → 80%+ ⭐

Integration:
├── CLI workflows: 30-35 tests ⭐ NEW
├── MCP workflows: 8-10 tests ⭐ NEW
└── File operations: 5-7 tests ⭐ NEW
```

---

## 🗓️ Session 10 Timeline

### Phase 1: Setup (30-45 min)
- [ ] Create `tests/integration/` directory
- [ ] Create fixtures in `conftest.py`
- [ ] Setup test utilities
- [ ] Verify test discovery

**Checkpoint**: Integration test infrastructure ready

---

### Phase 2: CLI Integration (2-2.5 hours)
- [ ] KB workflow tests (8-10 tests)
- [ ] Task workflow tests (10-12 tests)
- [ ] Cross-module tests (5-7 tests)
- [ ] Run tests, verify passing
- [ ] Commit progress

**Checkpoint**: CLI integration tests complete (23-29 tests)

---

### Phase 3: MCP Integration (1.5-2 hours)
- [ ] MCP tool workflow tests (8-10 tests)
- [ ] MCP error handling tests
- [ ] MCP performance tests
- [ ] Run tests, verify passing
- [ ] Commit progress

**Checkpoint**: MCP integration tests complete (8-10 tests)

---

### Phase 4: Knowledge Base Refinement (1 hour)
- [ ] Export/import tests (6-8 tests)
- [ ] Edge case tests (2-4 tests)
- [ ] Run tests, verify 80%+ coverage
- [ ] Commit progress

**Checkpoint**: knowledge_base.py at 80%+ (8-12 tests)

---

### Phase 5: File System Integration (30-45 min)
- [ ] File operation tests (5-7 tests)
- [ ] Run tests, verify passing
- [ ] Commit progress

**Checkpoint**: File system integration complete (5-7 tests)

---

### Phase 6: Verification & Documentation (30 min)
- [ ] Run full test suite
- [ ] Verify all quality checks pass
- [ ] Update SESSION_10_SUMMARY.md
- [ ] Final commit and push

---

## 📊 Success Criteria

### Must Have (All Required)
- ✅ Integration test framework created
- ✅ CLI integration tests (20+ tests)
- ✅ MCP integration tests (8+ tests)
- ✅ knowledge_base.py ≥ 80% coverage
- ✅ All tests passing
- ✅ All quality checks passing

### Nice to Have (Stretch Goals)
- ⭐ File system integration tests (5+ tests)
- ⭐ 40+ integration tests total
- ⭐ Overall coverage ≥ 80%

---

## 🎓 Lessons from Session 9 (Applied Here)

### 1. Verify Before Planning ✅
**Applied**: Verified actual coverage before writing this plan
- conflict_detector: 96% (not 14%)
- knowledge_base: 72% (not 12%)
- search: 86% (not 19%)

### 2. Focus on Real Gaps ✅
**Applied**: Identified that integration tests are the real gap (0%)

### 3. Be Realistic ✅
**Applied**: 4-6 hours for 38-53 tests (not 6-8 hours for 100+ tests)

### 4. Incremental Progress ✅
**Applied**: Phased approach with checkpoints and commits

---

## 🚫 Out of Scope (Session 10)

Explicitly **NOT** included:

1. ❌ CLI module unit tests (0% currently, but CLI works via integration tests)
2. ❌ Performance optimization (deferred to Session 11)
3. ❌ Stress testing with 1000+ entries (deferred to Session 11)
4. ❌ Advanced concurrency tests (low priority for CLI tool)
5. ❌ Unicode/permission edge cases (covered in integration tests)
6. ❌ Utils coverage improvement (48-67% is acceptable for now)

---

## 📝 Testing Best Practices (Session 10)

### Integration Test Patterns

#### Pattern 1: CLI Workflow Test
```python
def test_workflow(cli_runner, tmp_path):
    """Test complete workflow."""
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        # Step 1: Setup
        result = cli_runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Step 2: Operation
        result = cli_runner.invoke(cli, ["command", "args"])
        assert result.exit_code == 0
        assert "expected output" in result.output

        # Step 3: Verification
        result = cli_runner.invoke(cli, ["verify", "command"])
        assert result.exit_code == 0
```

#### Pattern 2: MCP Tool Test
```python
def test_mcp_tool(mcp_server):
    """Test MCP tool."""
    # Invoke tool
    result = mcp_server.call_tool("tool_name", {"arg": "value"})

    # Verify result
    assert result["status"] == "success"
    assert "key" in result["data"]
```

#### Pattern 3: Multi-Step Integration
```python
def test_integration(cli_runner, tmp_path):
    """Test multi-module integration."""
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        # KB operation
        cli_runner.invoke(cli, ["kb", "add", ...])

        # Task operation
        cli_runner.invoke(cli, ["task", "add", ...])

        # Conflict check
        result = cli_runner.invoke(cli, ["conflict", "detect", ...])

        # Verify integration
        assert "expected behavior" in result.output
```

---

## 💡 Tips for Success

### 1. Start with Infrastructure
Build solid fixtures before writing tests. Good fixtures make tests easy.

### 2. Test Real Workflows
Integration tests should mirror actual user workflows.

### 3. Isolate Tests
Each test should be independent and use `tmp_path` for isolation.

### 4. Verify State
Always verify state changes, not just command success.

### 5. Commit Frequently
Commit after each phase to track progress.

---

## 🔗 Related Documents

- **Session 9 Summary**: docs/SESSION_9_SUMMARY.md
- **Project Roadmap**: docs/PROJECT_ROADMAP.md
- **Timeline**: docs/SESSION_TIMELINE.md
- **Quick Status**: docs/QUICK_STATUS.md

---

## 🎯 Session 10 Success Definition

**Success** = All of the following:

1. ✅ Integration test framework created
2. ✅ 30+ integration tests passing
3. ✅ knowledge_base.py ≥ 80% coverage
4. ✅ CLI workflows tested comprehensively
5. ✅ MCP tools tested comprehensively
6. ✅ All quality checks passing
7. ✅ SESSION_10_SUMMARY.md created

**Stretch Success** = Above + any of:

- ⭐ 40+ integration tests
- ⭐ Overall coverage ≥ 80%
- ⭐ File system integration complete

---

**Ready for Session 10!** 🚀

**Estimated Total Time**: 4-6 hours

**Priority Order**:
1. Integration test infrastructure
2. CLI integration tests
3. MCP integration tests
4. Knowledge base refinement
5. File system integration (if time permits)

**Goal**: Achieve confidence in production deployment through comprehensive integration testing.
