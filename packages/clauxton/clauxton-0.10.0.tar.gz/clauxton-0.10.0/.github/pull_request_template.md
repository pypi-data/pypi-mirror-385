## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test addition/improvement
- [ ] CI/CD or build configuration

## Related Issues

<!-- Link related issues using keywords like "Closes #123" or "Fixes #456" -->

Closes #

## Changes Made

<!-- Provide a detailed list of changes -->

-
-
-

## Testing

<!-- Describe the tests you ran and how to reproduce them -->

### Test Environment

- Python version: <!-- e.g., 3.11.5 -->
- OS: <!-- e.g., macOS 14.0 -->
- Clauxton version: <!-- e.g., 0.8.0 -->

### Test Commands Run

```bash
# Add commands you ran to test your changes
pytest
ruff check clauxton tests
mypy clauxton
```

### Test Results

<!-- Paste relevant test output or summarize results -->

## Screenshots (if applicable)

<!-- Add screenshots for UI changes or visual improvements -->

## Checklist

### Code Quality

- [ ] My code follows the project's style guidelines (ruff, mypy)
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have added type hints to all new functions

### Testing

- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested on Python 3.11 and 3.12 (or confirmed CI passed)
- [ ] Test coverage has not decreased (current: 94%)

### Documentation

- [ ] I have updated the documentation (if applicable)
- [ ] I have updated `CHANGELOG.md` with my changes
- [ ] I have updated type definitions and docstrings
- [ ] I have updated examples in docs (if behavior changed)

### CI/CD

- [ ] All CI checks pass (test, lint, build)
- [ ] I have reviewed the CI logs for any warnings
- [ ] No new linting errors were introduced
- [ ] Package builds successfully (`python -m build`)

### Other

- [ ] My changes generate no new warnings
- [ ] I have checked for breaking changes
- [ ] I have updated dependencies if needed (pyproject.toml)
- [ ] This PR is ready for review

## Additional Notes

<!-- Add any additional notes for reviewers -->

## Breaking Changes

<!-- If this PR introduces breaking changes, describe them here and provide migration steps -->

## Reviewer Guidelines

<!-- Optional: Add specific things you'd like reviewers to focus on -->

---

**By submitting this PR, I confirm that my contributions are made under the MIT License.**
