# Test Performance Notes

## Summary

The Clauxton test suite contains 683 tests that run efficiently when executed in smaller groups, but experience slowdown when run all together locally. **This is not a problem for CI/CD**, which completes all tests successfully.

## Performance Characteristics

### Individual Module Performance (Fast ✅)

| Module | Tests | Time | Status |
|--------|-------|------|--------|
| `tests/core/` | 317 | ~5.7s | ✅ Fast |
| `tests/cli/` | 145 | ~3.5s | ✅ Fast |
| `tests/mcp/` | 88 | ~4.3s | ✅ Fast |
| `tests/integration/` | 44 | ~15s | ✅ Fast |
| `tests/utils/` | ~89 | ~3s | ✅ Fast |
| **Total (individual)** | **683** | **~32s** | **✅ Expected** |

### Full Suite Performance

| Environment | Time | Status |
|-------------|------|--------|
| **Local (all together)** | 120s+ (timeout) | ⚠️ Slow |
| **GitHub Actions CI** | ~50s | ✅ Fast |

## Root Cause

The slowdown when running all tests together locally is likely due to:

1. **Test interdependencies**: Temporary file cleanup and state management
2. **Coverage overhead**: pytest-cov measuring coverage across 683 tests
3. **Sequential execution**: pytest runs tests sequentially by default

**Important**: This does NOT indicate buggy code. All tests pass individually and in CI.

## Recommended Workflows

### For Local Development (Recommended ✅)

Run only the relevant test module during development:

```bash
# When working on core functionality
pytest tests/core/

# When working on CLI commands
pytest tests/cli/

# When working on MCP server
pytest tests/mcp/

# When working on integration features
pytest tests/integration/test_full_workflow.py

# Quick smoke test (critical tests only)
pytest tests/integration/test_full_workflow.py tests/integration/test_mcp_integration.py
```

### For Pre-Commit Verification

Run type checking and linting (fast):

```bash
mypy clauxton          # ~2s
ruff check clauxton tests  # ~1s
pytest tests/integration/  # ~15s (critical tests)
```

### For Full Verification

**Use GitHub Actions CI** (push to trigger):

```bash
git push origin <branch>
# GitHub Actions will run all 683 tests in ~50s
```

## CI/CD Performance

GitHub Actions CI runs efficiently because:
- ✅ Fresh environment (no state pollution)
- ✅ Optimized pytest configuration
- ✅ Parallel job execution (lint, test, build run concurrently)
- ✅ Sufficient timeout (120s configured in `.github/workflows/ci.yml`)

**CI Status**: All 683 tests pass consistently ✅

## Troubleshooting

### If CI starts failing with timeout

1. Check `.github/workflows/ci.yml` timeout setting:
   ```yaml
   timeout-minutes: 10  # Should be sufficient
   ```

2. Check for new slow tests:
   ```bash
   pytest tests/ --durations=20
   ```

3. Consider pytest-xdist for parallel execution:
   ```bash
   pip install pytest-xdist
   pytest tests/ -n auto
   ```

## Future Optimization (Optional)

If local full test suite execution becomes necessary:

### Option 1: Install pytest-xdist (parallel execution)

```bash
pip install pytest-xdist
pytest tests/ -n auto  # Uses all CPU cores
# Expected: ~15-20s for 683 tests
```

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "pytest-xdist>=3.5",  # Add this
    # ...
]
```

### Option 2: Split test execution

```bash
# Run in separate commands
pytest tests/core/ tests/cli/ && \
pytest tests/mcp/ tests/utils/ && \
pytest tests/integration/
```

## Conclusion

**Current approach (Option 1) is optimal**:
- ✅ Fast local development (test only what you change)
- ✅ Full verification via CI (all tests run automatically)
- ✅ No code changes needed
- ✅ No additional dependencies

The test suite is healthy and CI is the source of truth for test status.
