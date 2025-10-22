# Session 8 Action Plan

**Created**: 2025-10-21 (After Session 7)
**Target**: Performance Optimization + Community Readiness
**Estimated Duration**: 5-6 hours

---

## 📊 Session 7 Results Summary

### ✅ Completed
- Utils test coverage: 80%+ achieved (backup: 89%, yaml: 95%, logger: 97%)
- Security test suite: 4 critical tests
- SECURITY.md: Complete (283 lines)
- ADRs: 5 comprehensive documents (1,548 lines)
- Lint & Type Check: 100% pass

### ⚠️ Critical Gaps Identified
1. **CLI Coverage**: 0% (integration tests exist, unit tests missing)
2. **Core Business Logic**: 8-19% (knowledge_base: 12%, task_manager: 8%)
3. **Security Tooling**: Bandit not integrated
4. **Documentation**: CONTRIBUTING.md missing

---

## 🎯 Session 8 Priorities

### Priority 1: Critical Coverage Improvements (3-4 hours)

#### A. CLI Unit Tests (HIGH PRIORITY) ⚠️
**Goal**: Increase CLI coverage from 0% to 60%+

**Files to focus on**:
1. **`cli/main.py`** (332 lines, 0% coverage)
   - [ ] Test `init` command
   - [ ] Test KB commands (add, search, list, get, update, delete)
   - [ ] Test error handling (invalid inputs)
   - [ ] Test help messages
   - **Estimated**: 1.5 hours

2. **`cli/tasks.py`** (240 lines, 0% coverage)
   - [ ] Test task commands (add, list, get, update, next, delete)
   - [ ] Test task import from YAML
   - [ ] Test error messages
   - **Estimated**: 1 hour

3. **`cli/conflicts.py`** (130 lines, 0% coverage) - OPTIONAL
   - [ ] Test conflict detection commands
   - **Estimated**: 30 min

**Rationale**: CLI is the primary user interface. Zero coverage is a critical gap despite integration tests.

#### B. Core Business Logic (DEFERRED to Session 9)
- `core/knowledge_base.py`: 12% → 80%
- `core/task_manager.py`: 8% → 80%
- **Rationale**: More complex, requires dedicated session

---

### Priority 2: Security Linting Integration (30 min)

**Goal**: Add Bandit security linter to CI/CD

**Steps**:
1. [ ] Install Bandit: `pip install bandit`
2. [ ] Add to `pyproject.toml`:
   ```toml
   [project.optional-dependencies]
   dev = [
       # ... existing ...
       "bandit>=1.7",
   ]
   ```
3. [ ] Configure `.bandit` config file (exclude tests, set severity)
4. [ ] Add to CI workflow (`.github/workflows/ci.yml`):
   ```yaml
   - name: Security Lint (Bandit)
     run: bandit -r clauxton/ -ll
   ```
5. [ ] Run locally and fix any issues
6. [ ] Update README.md with security badge

**Expected Findings**: 0-2 issues (codebase is already secure)

---

### Priority 3: KB Export Optimization (1.5-2 hours)

**Goal**: Improve KB export performance for large datasets

**Current State**:
- Export works but may be slow for >100 entries
- No progress indicators
- No batch optimization

**Tasks**:
1. [ ] Profile current performance
   - Test with 100, 500, 1000 entries
   - Identify bottlenecks

2. [ ] Implement optimizations
   - [ ] Batch write operations
   - [ ] Progress indicators (click.progressbar)
   - [ ] Memory-efficient streaming

3. [ ] Add tests
   - [ ] Test with large datasets (500+ entries)
   - [ ] Test progress indicator
   - [ ] Test error handling (disk full, etc.)

4. [ ] Benchmark improvements
   - Document before/after performance

**Estimated Time**: 1.5-2 hours

---

### Priority 4: CONTRIBUTING.md (1 hour)

**Goal**: Create comprehensive contributor guide

**Structure**:
```markdown
# Contributing to Clauxton

## Development Setup
- Prerequisites
- Installation
- Virtual environment

## Development Workflow
- Branch naming
- Commit messages
- Running tests

## Pull Request Guidelines
- PR template
- Code review checklist
- CI requirements

## Testing Requirements
- Coverage thresholds
- Test categories
- Running specific tests

## Code Style
- Type hints required
- Ruff configuration
- Mypy strict mode

## Security
- Security testing
- Vulnerability reporting
- Safe coding practices

## Release Process
- Version bumping
- Changelog updates
- PyPI deployment
```

**Estimated Time**: 1 hour

---

### Priority 5: Documentation Updates (30 min)

**Tasks**:
1. [ ] Update README.md
   - Add security badge (Bandit)
   - Link to SECURITY.md
   - Link to CONTRIBUTING.md

2. [ ] Update CHANGELOG.md (if not exists, create)
   - Document Session 7 changes
   - Prepare for v0.10.0 release

3. [ ] Review and update quickstart guides
   - Ensure security best practices mentioned

**Estimated Time**: 30 min

---

## 📋 Session 8 Execution Plan

### Phase 1: Setup (15 min)
1. [ ] Pull latest changes: `git pull origin main`
2. [ ] Verify CI is green
3. [ ] Activate venv: `source .venv/bin/activate`
4. [ ] Review SESSION_7_REVIEW.md

### Phase 2: CLI Tests (1.5 hours)
1. [ ] Create `tests/cli/test_main_commands.py`
2. [ ] Test init, KB commands
3. [ ] Run tests, verify coverage improvement
4. [ ] Commit progress

### Phase 3: Task CLI Tests (1 hour)
1. [ ] Create `tests/cli/test_task_commands.py`
2. [ ] Test all task commands
3. [ ] Run tests, verify coverage
4. [ ] Commit progress

### Phase 4: Security Linting (30 min)
1. [ ] Install and configure Bandit
2. [ ] Run locally, fix issues
3. [ ] Add to CI
4. [ ] Commit changes

### Phase 5: KB Export Optimization (1.5 hours)
1. [ ] Profile current performance
2. [ ] Implement optimizations
3. [ ] Test and benchmark
4. [ ] Commit changes

### Phase 6: CONTRIBUTING.md (1 hour)
1. [ ] Draft document
2. [ ] Review against best practices
3. [ ] Commit

### Phase 7: Documentation (30 min)
1. [ ] Update README.md
2. [ ] Update/create CHANGELOG.md
3. [ ] Final commit

### Phase 8: Wrap-up (15 min)
1. [ ] Run full test suite
2. [ ] Verify all CI checks pass
3. [ ] Create SESSION_8_SUMMARY.md
4. [ ] Push to GitHub

---

## 🎯 Success Criteria

### Must Have (Session 8)
- ✅ CLI coverage: 60%+ (currently 0%)
- ✅ Bandit integrated in CI
- ✅ CONTRIBUTING.md created
- ✅ KB export optimized (with benchmarks)
- ✅ All tests passing
- ✅ All lint checks passing

### Nice to Have
- ⭐ CLI coverage: 80%+
- ⭐ Conflict CLI tests
- ⭐ Performance regression tests
- ⭐ CHANGELOG.md comprehensive

### Deferred to Session 9
- Core business logic coverage (knowledge_base, task_manager)
- API reference documentation (mkdocs)
- Advanced security tests (fuzzing, etc.)

---

## 🔧 Technical Notes

### CLI Testing Strategy

**Approach**: Use Click's testing utilities
```python
from click.testing import CliRunner
from clauxton.cli.main import cli

def test_kb_add():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Test init
        result = runner.invoke(cli, ['init'])
        assert result.exit_code == 0

        # Test kb add
        result = runner.invoke(cli, ['kb', 'add', '--title', 'Test'])
        assert result.exit_code == 0
        assert 'KB-' in result.output
```

**Challenges**:
- Interactive prompts (use `--title`, `--category` flags)
- File system isolation (use `runner.isolated_filesystem()`)
- Mocking user input (use `input` parameter)

### Bandit Configuration

**`.bandit` file**:
```yaml
exclude_dirs:
  - /tests/
  - /docs/

skips:
  - B101  # assert_used (OK in tests)
  - B601  # paramiko_calls (not used)

tests:
  - B201  # flask_debug_true
  - B301  # pickle usage
  - B302  # marshal usage
  - B303  # MD5 usage
  - B304  # insecure ciphers
  - B305  # insecure cipher modes
  - B306  # mktemp usage
  - B307  # eval usage
  - B308  # mark_safe usage
  - B309  # HTTPSConnection without verification
  - B310  # urllib usage
  - B311  # random usage
  - B312  # telnetlib usage
  - B313  # XML parsing
  - B314  # XML parsing with lxml
  - B315  # XML parsing with expatreader
  - B316  # XML parsing with sax
  - B317  # XML parsing with expatbuilder
  - B318  # XML parsing with minidom
  - B319  # XML parsing with pulldom
  - B320  # XML parsing with etree
  - B321  # ftplib usage
  - B322  # input usage
  - B323  # unverified context
  - B324  # hashlib weak hash
  - B325  # tempnam usage
  - B401  # import subprocess
  - B402  # import ftplib
  - B403  # import pickle
  - B404  # import subprocess
  - B405  # import xml etree
  - B406  # import xml sax
  - B407  # import xml expat
  - B408  # import xml minidom
  - B409  # import xml pulldom
  - B410  # import lxml
  - B411  # import xmlrpclib
  - B412  # import httpoxy
  - B413  # import pycrypto
  - B501  # request without cert validation
  - B502  # ssl with bad version
  - B503  # ssl with bad defaults
  - B504  # ssl with no version
  - B505  # weak crypto key
  - B506  # unsafe yaml load
  - B507  # ssh no host key verification
  - B601  # paramiko calls
  - B602  # shell with shell=True
  - B603  # subprocess without shell
  - B604  # any other function with shell
  - B605  # start process with shell
  - B606  # start process without shell
  - B607  # start process with partial path
  - B608  # hardcoded SQL
  - B609  # wildcard injection
  - B610  # django extra
  - B611  # django rawsql
  - B701  # jinja2 autoescape
  - B702  # mako templates
  - B703  # django mark safe
```

---

## 📊 Expected Outcomes

### Code Metrics (Before → After)

| Metric | Before | Target | Stretch Goal |
|--------|--------|--------|--------------|
| CLI Coverage | 0% | 60% | 80% |
| Overall Coverage | ~75% | ~80% | ~85% |
| Bandit Issues | Unknown | 0 | 0 |
| CI Pipeline Time | ~1m | ~1.5m | ~2m |

### Documentation

| Document | Status | Target |
|----------|--------|--------|
| CONTRIBUTING.md | ❌ Missing | ✅ Complete |
| CHANGELOG.md | ❌ Missing | ✅ Created |
| README.md | ⚠️ Needs update | ✅ Updated |

### Performance

| Operation | Before | Target | Measurement |
|-----------|--------|--------|-------------|
| KB Export (100 entries) | Unknown | <500ms | Benchmark |
| KB Export (1000 entries) | Unknown | <5s | Benchmark |

---

## 🚫 Out of Scope (Session 8)

The following are explicitly **NOT** included in Session 8:

1. ❌ Core business logic coverage (deferred to Session 9)
2. ❌ MCP server tests (deferred)
3. ❌ API reference documentation (deferred)
4. ❌ Performance benchmark suite (partial only)
5. ❌ Advanced security tests (fuzzing, TOCTOU)
6. ❌ Complexity metrics (Radon)
7. ❌ Dead code detection (Vulture)

---

## 📝 Notes for Executor

### CLI Testing Tips

1. **Use Click's CliRunner**: Isolated filesystem and output capture
2. **Test both success and failure**: Invalid inputs, missing files
3. **Mock external dependencies**: File I/O, network calls (if any)
4. **Test help text**: Ensure documentation is accurate

### Bandit Tips

1. **Start with defaults**: Don't over-configure initially
2. **Fix real issues**: Don't just skip warnings
3. **Document skips**: Explain why certain checks are skipped
4. **Integrate early**: Catch issues before they accumulate

### Performance Optimization Tips

1. **Profile first**: Don't optimize blindly
2. **Measure twice**: Before and after benchmarks
3. **Document assumptions**: Expected dataset sizes
4. **Consider trade-offs**: Memory vs speed, complexity vs performance

---

## 🔗 Related Documents

- **Session 7 Review**: `docs/SESSION_7_REVIEW.md`
- **Quality Analysis**: `docs/QUALITY_ANALYSIS.md`
- **Test Performance Guide**: `docs/TEST_PERFORMANCE.md`
- **Original Plan**: `docs/NEXT_SESSION_PLAN.md`

---

**Ready for Session 8!** 🚀
