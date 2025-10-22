# Contributing to Clauxton

Thank you for your interest in contributing to Clauxton! This document provides guidelines and instructions for contributing.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [CI/CD Workflow](#cicd-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

---

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

---

## Getting Started

### Prerequisites

- **Python 3.11+** (required)
- **Git** (required)
- **Claude Code** (recommended for testing)
- **pip** or **pipx** for package management

### Finding Issues to Work On

1. Check the [Issues](https://github.com/nakishiyaman/clauxton/issues) page
2. Look for issues labeled:
   - `good first issue` - Great for new contributors
   - `help wanted` - We need help on these
   - `bug` - Bug fixes
   - `enhancement` - New features

3. Comment on the issue to let us know you're working on it

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/clauxton.git
cd clauxton

# Add upstream remote
git remote add upstream https://github.com/nakishiyaman/clauxton.git
```

### 2. Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies

```bash
# Install in editable mode with all dependencies
pip install -e .

# Install development dependencies (optional)
pip install pytest pytest-cov mypy ruff

# Verify installation
clauxton --version

# Verify scikit-learn is installed (required for TF-IDF search)
python -c "import sklearn; print(f'scikit-learn {sklearn.__version__} installed')"
```

**Dependencies**:
- **Core**: `click`, `pydantic`, `pyyaml`, `mcp`
- **Search**: `scikit-learn`, `numpy` (optional, but recommended)
- **Development**: `pytest`, `pytest-cov`, `mypy`, `ruff`

### 4. Verify Setup

```bash
# Run tests
pytest

# Run type checker
mypy clauxton

# Run linter
ruff check clauxton
```

For detailed setup instructions, see [docs/development.md](docs/development.md).

---

## Development Workflow

### 1. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming conventions**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

### 2. Make Changes

- Write code following our [Coding Standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed
- Commit frequently with clear messages

### 3. Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short description>

<longer description (optional)>

<footer (optional)>
```

**Types**:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `test:` - Adding/updating tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `chore:` - Maintenance tasks

**Examples**:
```bash
git commit -m "feat(kb): add search by tags functionality"
git commit -m "fix(cli): handle empty knowledge base gracefully"
git commit -m "docs: update quick start guide with examples"
```

### 4. Keep Your Branch Updated

```bash
# Fetch upstream changes
git fetch upstream

# Rebase your branch
git rebase upstream/main

# If conflicts occur, resolve them and continue
git rebase --continue
```

### 5. Push Changes

```bash
git push origin feature/your-feature-name
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with these tools:
- **ruff** - Linter and formatter
- **mypy** - Type checker (strict mode)

### Type Hints

All functions must have type hints:

```python
# ✅ Good
def search_kb(query: str, limit: int = 10) -> List[KnowledgeBaseEntry]:
    """Search Knowledge Base by query."""
    pass

# ❌ Bad
def search_kb(query, limit=10):
    """Search Knowledge Base by query."""
    pass
```

### Docstrings

Use **Google-style docstrings**:

```python
def add_entry(entry: KnowledgeBaseEntry) -> str:
    """
    Add entry to Knowledge Base.

    Args:
        entry: KnowledgeBaseEntry to add

    Returns:
        Entry ID (e.g., "KB-20251019-001")

    Raises:
        ValidationError: If entry is invalid
        DuplicateError: If entry ID already exists

    Example:
        >>> kb = KnowledgeBase(Path("."))
        >>> entry = KnowledgeBaseEntry(...)
        >>> entry_id = kb.add_entry(entry)
        >>> print(entry_id)
        KB-20251019-001
    """
    pass
```

### AI-Friendly Code

Write code that AI (Claude Code) can easily understand and modify:

```python
# ✅ AI-Friendly: Clear, explicit, well-typed
class KnowledgeBase:
    """Knowledge Base manager with YAML persistence."""

    def __init__(self, root_dir: Path) -> None:
        """Initialize Knowledge Base at root_dir."""
        self.root_dir: Path = root_dir
        self.kb_file: Path = root_dir / ".clauxton" / "knowledge-base.yml"

# ❌ Not AI-Friendly: Cryptic, implicit, no types
class KB:
    def __init__(self, d):
        self.d = d
        self.f = d / ".c" / "kb.yml"
```

### Error Handling

Use custom exceptions with clear messages:

```python
# ✅ Good
if not entry.title.strip():
    raise ValidationError(
        "Entry title cannot be empty. "
        "Please provide a descriptive title."
    )

# ❌ Bad
if not entry.title.strip():
    raise Exception("Invalid title")
```

---

## CI/CD Workflow

### Automated Checks

Every push and pull request triggers automated testing via GitHub Actions:

**Jobs Run**:
- **Test Job** (Python 3.11 & 3.12): Runs all 267 tests with coverage (~42-44s)
- **Lint Job**: Runs ruff (code formatting) + mypy (type checking) (~18s)
- **Build Job**: Validates package build with twine (~17s)

**Total CI Time**: ~44 seconds (parallel execution)

All checks must pass before a PR can be merged. View details in the [Actions tab](https://github.com/nakishiyaman/clauxton/actions).

### Running CI Checks Locally

Before pushing, run these checks locally to catch issues early:

```bash
# 1. Run all tests with coverage
pytest --cov=clauxton --cov-report=term-missing

# 2. Check code formatting and style
ruff check clauxton tests

# 3. Run type checking
mypy clauxton

# 4. Build and validate package
python -m build
twine check dist/*
```

**Quick check script**:
```bash
# Run all checks at once
pytest --cov=clauxton && ruff check clauxton tests && mypy clauxton
```

### CI Configuration Files

- **Workflow**: `.github/workflows/ci.yml` - GitHub Actions configuration
- **mypy config**: `mypy.ini` - Type checking rules
- **ruff config**: `pyproject.toml` (under `[tool.ruff]`)

### CI Failure Troubleshooting

#### Lint Failures

**Error**: `ruff check` failed
```bash
# Auto-fix most issues
ruff check --fix clauxton tests

# Common issues:
# - Line too long (>100 chars) - Break into multiple lines
# - Unused imports - Remove them
# - Import order - Will be auto-fixed
```

**Error**: `mypy` type checking failed
```bash
# Run mypy locally to see errors
mypy clauxton

# Common issues:
# - Missing type hints - Add them to functions
# - Incorrect types - Fix type annotations
# - Missing return type - Add -> ReturnType
```

#### Test Failures

**Error**: Tests failed
```bash
# Run tests with verbose output
pytest -v

# Run specific failing test
pytest tests/path/to/test.py::test_name -v

# Common issues:
# - Test works locally but fails in CI - Check Python version
# - Import errors - Check dependencies in pyproject.toml
# - Path issues - Use Path objects, not strings
```

#### Build Failures

**Error**: Package build failed
```bash
# Check pyproject.toml syntax
python -m build

# Common issues:
# - Invalid metadata - Check version, dependencies
# - Missing files - Check MANIFEST.in or pyproject.toml [tool.setuptools]
```

### Coverage Requirements

- **Minimum**: 90% overall coverage (current: 94%)
- **Target**: Maintain or improve current coverage
- New code should have 95%+ coverage where possible

View coverage reports:
- **Local**: `pytest --cov=clauxton --cov-report=html` then open `htmlcov/index.html`
- **CI**: Check Codecov badge in README or visit [Codecov](https://codecov.io/gh/nakishiyaman/clauxton)

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=clauxton --cov-report=html

# Run specific test file
pytest tests/core/test_knowledge_base.py

# Run specific test
pytest tests/core/test_knowledge_base.py::test_add_entry
```

### Writing Tests

- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete user workflows

**Example test**:

```python
import pytest
from clauxton.core.knowledge_base import KnowledgeBase
from clauxton.core.models import KnowledgeBaseEntry

def test_add_entry(tmp_path):
    """Test adding entry to Knowledge Base."""
    # Arrange
    kb = KnowledgeBase(tmp_path)
    entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Test Entry",
        category="architecture",
        content="Test content",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Act
    entry_id = kb.add(entry)

    # Assert
    assert entry_id == "KB-20251019-001"
    retrieved = kb.get(entry_id)
    assert retrieved.title == "Test Entry"
```

### Test Coverage

- **Minimum**: 90% overall coverage (current: 94%)
- **Target**: 95%+ coverage
- **Critical paths**: 95%+ coverage required
  - KB CRUD operations: 96% ✅
  - Task DAG validation: 98% ✅
  - Search functionality: 86-96% ✅

**Coverage Goals by Component**:
- `clauxton/core/`: 95%+ (primary business logic)
- `clauxton/cli/`: 90%+ (user-facing CLI)
- `clauxton/mcp/`: 95%+ (MCP server integration)
- `clauxton/utils/`: 80%+ (utility functions)

**Important Notes**:
- All new features must include comprehensive tests
- Edge cases must be tested (Unicode, special characters, error handling)
- Fallback behaviors must be tested (e.g., search without scikit-learn)
- Integration tests should verify end-to-end workflows

---

## Documentation

### Code Documentation

- All public functions/classes must have docstrings
- Use Google-style docstrings
- Include examples where helpful

### User Documentation

When adding features, update:
- `README.md` - If user-facing feature
- `docs/quick-start.md` - If affects getting started
- `docs/api-reference.md` - If adding public API
- `CHANGELOG.md` - Always update with changes

### Documentation Style

- Use **clear, simple language**
- Include **code examples**
- Provide **context and reasoning**
- Use **bullet points** and **headers** for structure

---

## Submitting Changes

### Before Submitting

Checklist:
- [ ] Code follows style guidelines (ruff, mypy pass)
- [ ] Tests added for new functionality
- [ ] All tests pass (`pytest`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow conventions
- [ ] Branch is up-to-date with `upstream/main`

### Create Pull Request

1. **Push your branch** to your fork
2. **Go to GitHub** and create a Pull Request
3. **Fill out the PR template** completely
4. **Link related issues** (e.g., "Closes #42")
5. **Request review** from maintainers

### PR Review Process

1. **Automated checks** run (tests, linting, type checking)
2. **Maintainer review** (usually within 2-3 days)
3. **Address feedback** by pushing new commits
4. **Approval** from at least one maintainer
5. **Merge** by maintainer (squash and merge)

### After Merge

- Delete your feature branch
- Update your local main branch:
  ```bash
  git checkout main
  git pull upstream main
  git push origin main
  ```

---

## Release Process

(For maintainers)

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features (e.g., 0.1.0 → 0.2.0)
- **PATCH**: Bug fixes (e.g., 0.1.0 → 0.1.1)

### Release Steps

1. Update `__version__.py` and `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Create git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
4. Push tag: `git push origin v0.1.0`
5. Build package: `python -m build`
6. Upload to PyPI: `python -m twine upload dist/*`
7. Create GitHub Release with changelog

---

## Getting Help

- **Questions?** Open a [Discussion](https://github.com/nakishiyaman/clauxton/discussions)
- **Bug found?** Open an [Issue](https://github.com/nakishiyaman/clauxton/issues)
- **Want to chat?** Join our [Discord](#) (coming soon)

---

## Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` (all contributors)
- Release notes (for significant contributions)
- GitHub contributors page

---

## License

By contributing to Clauxton, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

**Thank you for contributing to Clauxton! 🎉**
