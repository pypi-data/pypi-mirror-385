# Session 11 Plan: MCP Integration & Performance Testing

**Date**: 2025-10-22
**Status**: 📋 Planned
**Estimated Duration**: 3-4 hours
**Target**: Complete v0.10.0 testing requirements

---

## 📍 Current Status (Starting Point)

### What We Have
- ✅ **750 tests** passing (100% success rate)
- ✅ **88 MCP tests** already exist (discovered during planning!)
- ✅ **Core coverage**: 78% overall, 93% KB
- ✅ **Integration tests**: 84 tests, comprehensive workflows
- ✅ **Quality checks**: All passing (ruff, mypy, bandit)

### What We Need
Based on Session 10 Completeness Review:
- ⚠️ **MCP Server Coverage**: 25% (155/206 lines missing)
- ⚠️ **Performance Testing**: Basic only (not production-grade)
- ⚠️ **CLI Coverage**: Various CLI modules need improvement
- ⚠️ **Documentation**: Test writing guide needed

---

## 🎯 Session 11 Goals

### Primary Goals (MUST DO)

#### 1. MCP Server Coverage Improvement (Priority: CRITICAL)
**Current**: 25% coverage (51/206 lines covered)
**Target**: 60%+ coverage (net +35%)
**Why**: MCP server is production interface, must be reliable

**Approach**:
1. Review existing 88 MCP tests to understand current coverage
2. Identify uncovered MCP tool endpoints
3. Add missing integration tests for:
   - KB tools: kb_add, kb_update, kb_delete, kb_export_docs
   - Task tools: task_add, task_import_yaml, task_update, task_delete
   - Conflict tools: detect_conflicts, recommend_safe_order, check_file_conflicts
   - History tools: undo_last_operation, get_recent_operations
   - Config tools: get_config, set_config
4. Add error handling tests for all MCP tools
5. Add MCP server initialization/lifecycle tests

**Estimated Tests**: 15-20 new tests
**Estimated Time**: 2-2.5 hours

#### 2. CLI Coverage Improvement (Priority: HIGH)
**Current**:
- cli/main.py: 20% (265/332 missing)
- cli/tasks.py: 17% (199/240 missing)
- cli/conflicts.py: 15% (111/130 missing)
- cli/config.py: 20% (60/75 missing)

**Target**: 40%+ for each CLI module (net +20-25%)
**Why**: CLI is primary user interface

**Approach**:
1. Focus on most-used commands first:
   - `clauxton init` (if not covered)
   - `clauxton kb add` (basic flow)
   - `clauxton task add` (basic flow)
   - `clauxton task import` (YAML import)
2. Add error handling tests:
   - Invalid arguments
   - Missing files
   - Permission errors
3. Focus on integration tests (not unit tests)

**Estimated Tests**: 10-12 new tests
**Estimated Time**: 1-1.5 hours

### Secondary Goals (SHOULD DO)

#### 3. Performance Benchmarking (Priority: MEDIUM)
**Current**: Basic observation only (50 entries tested)
**Target**: Production-grade performance baseline

**Approach**:
1. Large dataset tests:
   - 1000+ KB entries (add, search, export)
   - 100+ tasks with complex dependencies
   - Memory usage profiling
2. Performance regression tests:
   - Baseline search speed (TF-IDF on 1000 entries)
   - Baseline DAG validation speed (100 tasks)
   - Baseline YAML I/O speed (1000 entries)
3. Document acceptable performance thresholds

**Estimated Tests**: 5-7 new tests
**Estimated Time**: 1 hour

#### 4. Documentation Updates (Priority: LOW)
**Current**: Good documentation, but no test writing guide
**Target**: Help future contributors write good tests

**Approach**:
1. Create `docs/TEST_WRITING_GUIDE.md`:
   - How to write unit tests
   - How to write integration tests
   - How to use fixtures (conftest.py)
   - How to mock external dependencies
   - Coverage best practices
2. Update CLAUDE.md with test patterns

**Estimated Time**: 30 minutes

---

## 📊 Expected Outcomes

### Test Metrics
| Metric | Before (Session 10) | After (Session 11) | Delta |
|--------|---------------------|--------------------| ------|
| **Total Tests** | 750 | ~780-800 | +30-50 |
| **MCP Coverage** | 25% | 60%+ | +35% |
| **CLI Coverage** | ~18% | 40%+ | +22% |
| **Overall Coverage** | 78% | 82%+ | +4% |
| **Integration Tests** | 84 | 95-100 | +11-16 |

### Quality Metrics
- ✅ All MCP tools have integration tests
- ✅ Performance baselines documented
- ✅ CLI commands have basic coverage
- ✅ Test writing guide available

### Production Readiness
**Before**: 98% ready (MCP tests pending)
**After**: **100% ready for v0.10.0 release** 🚀

---

## 📋 Detailed Task Breakdown

### Phase 1: MCP Coverage (2-2.5 hours)

#### Task 1.1: Review Existing MCP Tests (15 min)
```bash
# Review current MCP test files
cat tests/mcp/test_server.py
cat tests/mcp/test_server_integration.py
cat tests/mcp/test_task_tools.py
cat tests/mcp/test_conflict_tools.py
cat tests/mcp/test_logging_tools.py
```

**Output**: List of covered vs uncovered MCP tools

#### Task 1.2: Add Missing KB Tool Tests (30 min)
**Target**: kb_add, kb_update, kb_delete, kb_export_docs

**Test Cases**:
1. `test_mcp_kb_add_success` - Add entry via MCP
2. `test_mcp_kb_add_invalid_category` - Error handling
3. `test_mcp_kb_update_success` - Update entry via MCP
4. `test_mcp_kb_update_nonexistent` - Error handling
5. `test_mcp_kb_delete_success` - Delete entry via MCP
6. `test_mcp_kb_export_docs_success` - Export to Markdown

**Estimated**: 6 tests, 30 minutes

#### Task 1.3: Add Missing Task Tool Tests (45 min)
**Target**: task_add, task_import_yaml, task_update, task_delete

**Test Cases**:
1. `test_mcp_task_add_success` - Add task via MCP
2. `test_mcp_task_add_with_dependencies` - Add task with depends_on
3. `test_mcp_task_import_yaml_success` - Bulk import via MCP
4. `test_mcp_task_import_yaml_with_confirmation` - Confirmation flow
5. `test_mcp_task_import_yaml_error_rollback` - Error handling (rollback)
6. `test_mcp_task_import_yaml_error_skip` - Error handling (skip)
7. `test_mcp_task_update_success` - Update task via MCP
8. `test_mcp_task_delete_success` - Delete task via MCP

**Estimated**: 8 tests, 45 minutes

#### Task 1.4: Add Missing Conflict Tool Tests (15 min)
**Target**: detect_conflicts, recommend_safe_order (if not covered)

**Test Cases**:
1. `test_mcp_detect_conflicts_high_risk` - HIGH risk scenario
2. `test_mcp_recommend_safe_order_complex` - Complex dependencies

**Estimated**: 2 tests, 15 minutes

#### Task 1.5: Add MCP Server Lifecycle Tests (20 min)
**Target**: Server initialization, error handling, cleanup

**Test Cases**:
1. `test_mcp_server_initialization` - Server starts correctly
2. `test_mcp_server_handles_invalid_tool` - Unknown tool error
3. `test_mcp_server_handles_invalid_args` - Invalid arguments error
4. `test_mcp_server_json_serialization` - All tools return valid JSON

**Estimated**: 4 tests, 20 minutes

**Phase 1 Total**: ~20 tests, 2-2.5 hours

---

### Phase 2: CLI Coverage (1-1.5 hours)

#### Task 2.1: Add Core CLI Command Tests (45 min)
**Target**: Most-used commands

**Test Cases**:
1. `test_cli_init_success` - Initialize project (if not covered)
2. `test_cli_init_already_initialized` - Error handling
3. `test_cli_kb_add_interactive` - Interactive add flow
4. `test_cli_kb_add_with_flags` - Add with --title, --category, etc.
5. `test_cli_task_add_interactive` - Interactive add flow
6. `test_cli_task_import_success` - Import from YAML file
7. `test_cli_task_import_invalid_yaml` - Error handling
8. `test_cli_conflict_detect_verbose` - Verbose output

**Estimated**: 8 tests, 45 minutes

#### Task 2.2: Add CLI Error Handling Tests (30 min)
**Target**: Common error scenarios

**Test Cases**:
1. `test_cli_without_init` - Commands fail without .clauxton/
2. `test_cli_permission_denied` - Handle read-only filesystem
3. `test_cli_corrupted_yaml` - Handle corrupted data files
4. `test_cli_invalid_id_format` - Invalid KB/Task ID

**Estimated**: 4 tests, 30 minutes

**Phase 2 Total**: ~12 tests, 1-1.5 hours

---

### Phase 3: Performance Testing (1 hour)

#### Task 3.1: Large Dataset Performance (30 min)
**Test Cases**:
1. `test_performance_kb_add_1000_entries` - Bulk add performance
2. `test_performance_kb_search_1000_entries` - Search speed baseline
3. `test_performance_task_dag_100_tasks` - DAG validation speed

**Estimated**: 3 tests, 30 minutes

#### Task 3.2: Memory Profiling (15 min)
**Test Cases**:
1. `test_memory_kb_large_dataset` - Memory usage with 1000 entries
2. `test_memory_task_complex_dependencies` - Memory usage with 100 tasks

**Estimated**: 2 tests, 15 minutes

#### Task 3.3: Document Performance Baselines (15 min)
- Add performance thresholds to `docs/performance-guide.md`
- Update CLAUDE.md with performance expectations

**Phase 3 Total**: ~5 tests, 1 hour

---

### Phase 4: Documentation (30 min)

#### Task 4.1: Create Test Writing Guide (25 min)
**File**: `docs/TEST_WRITING_GUIDE.md`

**Content**:
1. Introduction to Clauxton testing
2. Unit vs Integration tests
3. Using fixtures (conftest.py)
4. Mocking external dependencies
5. Coverage best practices
6. Running tests locally
7. CI/CD integration

#### Task 4.2: Update CLAUDE.md (5 min)
- Add test patterns section
- Link to TEST_WRITING_GUIDE.md

**Phase 4 Total**: 30 minutes

---

## 🔍 Risk Analysis

### High Risk Items
1. **MCP Server Coverage** - Critical for production
   - Mitigation: Focus on most-used tools first
   - Fallback: Defer advanced features to Session 12

2. **Time Constraints** - 3-4 hour estimate may be tight
   - Mitigation: Prioritize CRITICAL and HIGH items first
   - Fallback: Defer documentation to Session 12

### Medium Risk Items
1. **Performance Tests** - May uncover unexpected issues
   - Mitigation: Document findings, don't block release
   - Fallback: Fix performance issues in v0.10.1

2. **CLI Coverage** - Large surface area
   - Mitigation: Focus on integration tests, not exhaustive
   - Fallback: Incremental improvement in future sessions

### Low Risk Items
1. **Documentation** - Always deferrable
   - Mitigation: Keep scope minimal
   - Fallback: Complete in Session 12

---

## ✅ Success Criteria

### MUST HAVE (Release Blockers)
- ✅ MCP server coverage ≥60%
- ✅ All MCP tools have at least 1 integration test
- ✅ CLI coverage ≥40% for main.py, tasks.py
- ✅ All quality checks passing (ruff, mypy, pytest)

### SHOULD HAVE (Nice to Have)
- ✅ Performance baselines documented
- ✅ CLI error handling tests
- ✅ Memory profiling tests

### COULD HAVE (Deferrable)
- ✅ Test writing guide (can defer to Session 12)
- ✅ Performance optimization (can defer to v0.10.1)

---

## 📚 References

### Related Documents
- **SESSION_10_SUMMARY.md** - Previous session results
- **SESSION_10_COMPLETENESS_REVIEW.md** - Gap analysis
- **QUICK_STATUS.md** - Current project status
- **PROJECT_ROADMAP.md** - Overall plan

### Coverage Reports
- **htmlcov/index.html** - Detailed coverage report
- **htmlcov/status.json** - Coverage data

### Test Files to Review
- `tests/mcp/test_server.py` - Current MCP tests (88 tests)
- `tests/integration/test_cli_*.py` - CLI integration tests
- `tests/integration/conftest.py` - Shared fixtures

---

## 🚀 Expected Impact

### Before Session 11
- MCP server: 25% coverage (risky)
- CLI: ~18% coverage (minimal)
- Performance: Basic only
- Production readiness: 98%

### After Session 11
- MCP server: 60%+ coverage (production-ready)
- CLI: 40%+ coverage (acceptable)
- Performance: Baseline established
- Production readiness: **100%** 🎉

### v0.10.0 Release
With Session 11 complete:
- ✅ All core modules tested (80%+)
- ✅ All integration workflows tested
- ✅ MCP server production-ready
- ✅ Performance baselines documented
- ✅ Ready for PyPI release 🚀

---

## 💡 Notes

### Why 88 MCP Tests Already Exist?
During planning, discovered:
- `tests/mcp/test_server.py` - Core MCP tests
- `tests/mcp/test_server_integration.py` - Integration tests
- `tests/mcp/test_task_tools.py` - Task tool tests
- `tests/mcp/test_conflict_tools.py` - Conflict tool tests
- `tests/mcp/test_logging_tools.py` - Logging tests

**Good News**: Foundation is solid!
**Challenge**: Coverage is still low (25%), need to understand why
**Likely Reason**: Tests exist but don't cover all code paths

### Why Focus on MCP First?
1. **User-facing**: MCP is primary Claude Code interface
2. **Critical**: Must be reliable for production
3. **Gating**: Required for v0.10.0 release
4. **Impact**: +35% coverage gain potential

### Why Not 100% Coverage?
- Diminishing returns beyond 80-85%
- Some code paths are error handling only
- Focus on production-critical paths first
- Can iterate in v0.10.1+

---

**Prepared by**: Claude Code
**Next Session**: Session 11 Execution
**Status**: 📋 Ready to Execute
