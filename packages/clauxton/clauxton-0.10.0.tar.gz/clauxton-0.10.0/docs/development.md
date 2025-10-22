# Development Guide

**Version**: 1.0
**Last Updated**: 2025-10-19

This guide provides detailed instructions for setting up your development environment and contributing to Clauxton.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Development Environment](#development-environment)
- [Running Tests](#running-tests)
- [Code Quality Tools](#code-quality-tools)
- [Debugging](#debugging)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Python** | 3.11+ | Runtime | [python.org](https://www.python.org/downloads/) |
| **Git** | 2.0+ | Version control | [git-scm.com](https://git-scm.com/) |
| **pip** | Latest | Package manager | Included with Python |

### Optional Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| **Claude Code** | Testing plugin integration | [claude.ai/code](https://claude.ai/code) |
| **pyenv** | Python version management | [github.com/pyenv/pyenv](https://github.com/pyenv/pyenv) |
| **pipx** | Install CLI tools globally | `pip install pipx` |
| **direnv** | Auto-activate venv | [direnv.net](https://direnv.net/) |

### System Requirements

- **OS**: Linux, macOS, or Windows (WSL recommended)
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for dependencies + dev tools

---

## Initial Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/clauxton.git
cd clauxton

# Add upstream remote
git remote add upstream https://github.com/nakishiyaman/clauxton.git

# Verify remotes
git remote -v
# origin    https://github.com/YOUR_USERNAME/clauxton.git (fetch)
# origin    https://github.com/YOUR_USERNAME/clauxton.git (push)
# upstream  https://github.com/nakishiyaman/clauxton.git (fetch)
# upstream  https://github.com/nakishiyaman/clauxton.git (push)
```

### 2. Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install Clauxton in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
clauxton --version
# Expected output: clauxton, version 0.1.0

# Verify dev tools
mypy --version
ruff --version
pytest --version
```

**What's installed**:
- **Production dependencies**: `pydantic`, `click`, `pyyaml`, `gitpython`
- **Dev dependencies**: `pytest`, `pytest-cov`, `mypy`, `ruff`, `build`, `twine`

---

## Development Environment

### Project Structure

```
clauxton/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── clauxton/
│   ├── __init__.py          # Package root
│   ├── core/                # Core engine
│   │   ├── knowledge_base.py
│   │   ├── task_manager.py
│   │   ├── dependency_analyzer.py
│   │   └── models.py
│   ├── cli/                 # CLI commands
│   │   └── main.py
│   ├── mcp/                 # MCP servers
│   │   ├── kb_server.py
│   │   └── task_server.py
│   └── utils/               # Utilities
│       ├── yaml_utils.py
│       ├── file_utils.py
│       └── dag_utils.py
├── commands/                # Slash commands
│   ├── kb-search.md
│   └── task-next.md
├── agents/                  # Subagent definitions
│   ├── dependency-analyzer.md
│   └── conflict-detector.md
├── hooks/                   # Lifecycle hooks
│   └── post-edit-update-kb.sh
├── tests/
│   ├── core/
│   ├── cli/
│   ├── mcp/
│   ├── utils/
│   └── integration/
├── docs/
├── pyproject.toml
├── README.md
└── CONTRIBUTING.md
```

### Environment Variables

Create a `.env` file (not committed to git):

```bash
# .env
CLAUXTON_DEBUG=1              # Enable debug logging
CLAUXTON_DATA_DIR=.clauxton   # Override default data directory
PYTHONPATH=./clauxton         # For import resolution
```

Load with:
```bash
export $(cat .env | xargs)
```

### VS Code Setup (Recommended)

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "python.linting.ruffEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

Install recommended extensions:
```bash
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension ms-python.vscode-pylance
```

---

## Running Tests

### Quick Test

```bash
# Run all tests
pytest

# Expected output:
# ==================== test session starts ====================
# collected 42 items
# tests/core/test_knowledge_base.py ........  [ 19%]
# tests/core/test_models.py .........          [ 40%]
# tests/cli/test_main.py .....                 [ 52%]
# tests/utils/test_yaml_utils.py ......        [ 66%]
# tests/integration/test_end_to_end.py ....    [100%]
# ==================== 42 passed in 2.34s ====================
```

### Test with Coverage

```bash
# Run with coverage report
pytest --cov=clauxton --cov-report=term --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Coverage targets**:
- **Minimum**: 70% (Phase 0)
- **Target**: 80% (Phase 1+)
- **Current**: 92% (v0.10.0)
- **Critical paths**: 100% (KB CRUD, Task DAG validation)

### Test Categories

Clauxton has a comprehensive test suite organized by type:

```bash
# Unit tests (core functionality)
pytest tests/core/

# CLI tests (command-line interface)
pytest tests/cli/

# MCP tests (MCP server integration)
pytest tests/mcp/

# Integration tests (end-to-end workflows)
pytest tests/integration/
```

**Note**: Integration tests may require API adjustments. Run with:
```bash
# Run stable tests only (excludes WIP integration tests)
pytest tests/ --ignore=tests/integration/test_full_workflow.py \
              --ignore=tests/integration/test_mcp_integration.py \
              --ignore=tests/integration/test_performance_regression.py
```

### Test Specific Components

```bash
# Run specific test file
pytest tests/core/test_knowledge_base.py

# Run specific test function
pytest tests/core/test_knowledge_base.py::test_add_entry

# Run tests matching pattern
pytest -k "test_search"

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s

# Stop on first failure
pytest -x
```

### Test Categories

```bash
# Unit tests only (fast)
pytest tests/core tests/utils

# Integration tests only (slower)
pytest tests/integration

# Skip slow tests
pytest -m "not slow"
```

---

## Code Quality Tools

### Type Checking (mypy)

```bash
# Run mypy on entire codebase
mypy clauxton

# Run on specific file
mypy clauxton/core/knowledge_base.py

# Strict mode (required for contributions)
mypy --strict clauxton
```

**Fix common mypy errors**:

```python
# ❌ Error: Missing return type
def get_entry(entry_id):
    pass

# ✅ Fixed
def get_entry(entry_id: str) -> KnowledgeBaseEntry:
    pass

# ❌ Error: Incompatible return type
def search(query: str) -> List[KnowledgeBaseEntry]:
    return None  # Error!

# ✅ Fixed
def search(query: str) -> List[KnowledgeBaseEntry]:
    return []
```

### Linting (ruff)

```bash
# Check for issues
ruff check clauxton

# Fix auto-fixable issues
ruff check --fix clauxton

# Format code
ruff format clauxton

# Check specific file
ruff check clauxton/core/knowledge_base.py
```

**Common ruff fixes**:

```python
# ❌ Unused import
from pathlib import Path
from typing import List  # Unused!

# ✅ Fixed (ruff --fix removes it)
from pathlib import Path

# ❌ Line too long (>88 chars)
def very_long_function_name_that_exceeds_the_line_length_limit(parameter1, parameter2, parameter3):
    pass

# ✅ Fixed
def very_long_function_name_that_exceeds_the_line_length_limit(
    parameter1, parameter2, parameter3
):
    pass
```

### Pre-Commit Checks

Run all quality checks before committing:

```bash
# Create a pre-commit script
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Type check
echo "→ mypy"
mypy clauxton

# Lint
echo "→ ruff check"
ruff check clauxton

# Format check
echo "→ ruff format --check"
ruff format --check clauxton

# Tests
echo "→ pytest"
pytest

echo "✅ All checks passed!"
EOF

chmod +x .git/hooks/pre-commit
```

---

## Debugging

### Debug CLI Commands

```bash
# Run CLI with Python debugger
python -m pdb -m clauxton.cli.main kb search "test"

# Add breakpoint in code
def search(query: str):
    import pdb; pdb.set_trace()  # Breakpoint
    # ...
```

### Debug MCP Servers

```bash
# Run MCP server manually
python -m clauxton.mcp.kb_server

# With debug logging
CLAUXTON_DEBUG=1 python -m clauxton.mcp.kb_server
```

### Debug Tests

```bash
# Run test with debugger on failure
pytest --pdb

# Run test with debugger on error
pytest --pdbcls=IPython.terminal.debugger:Pdb

# Print debug output
pytest -s  # Shows print() statements
```

### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Pytest: Current File",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v"],
      "console": "integratedTerminal"
    },
    {
      "name": "CLI: kb search",
      "type": "python",
      "request": "launch",
      "module": "clauxton.cli.main",
      "args": ["kb", "search", "test"],
      "console": "integratedTerminal"
    }
  ]
}
```

---

## Common Tasks

### Add New KB Entry (CLI)

```bash
clauxton kb add \
  --title "New convention" \
  --category convention \
  --tags "coding-style,python"
```

### Run Local Installation

```bash
# Install in editable mode
pip install -e .

# Verify
clauxton --version

# Test commands
clauxton init
clauxton kb search "architecture"
```

### Generate Test Data

```bash
# Create test project
mkdir /tmp/test-project
cd /tmp/test-project

# Initialize Clauxton
clauxton init --project-name "Test Project"

# Add sample KB entries
clauxton kb add --title "Use FastAPI" --category architecture
clauxton kb add --title "Write tests first" --category convention
clauxton kb add --title "Use Pydantic for validation" --category pattern

# Verify YAML
cat .clauxton/knowledge-base.yml
```

### Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build wheel and sdist
python -m build

# Verify contents
unzip -l dist/clauxton-0.1.0-py3-none-any.whl

# Test installation
pip install dist/clauxton-0.1.0-py3-none-any.whl
```

### Update Dependencies

```bash
# Upgrade all dependencies
pip install --upgrade -e ".[dev]"

# Freeze exact versions
pip freeze > requirements-dev.txt

# Update pyproject.toml manually
```

---

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'clauxton'`

**Solution**:
```bash
# Install in editable mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### Permission Errors

**Problem**: `PermissionError: [Errno 13] Permission denied: '.clauxton/knowledge-base.yml'`

**Solution**:
```bash
# Fix permissions
chmod 700 .clauxton
chmod 600 .clauxton/*.yml
```

### YAML Parsing Errors

**Problem**: `yaml.scanner.ScannerError: mapping values are not allowed here`

**Solution**:
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('.clauxton/knowledge-base.yml'))"

# Restore from backup
cp .clauxton/backups/knowledge-base.yml.bak .clauxton/knowledge-base.yml
```

### Test Failures

**Problem**: Tests fail on CI but pass locally

**Solution**:
```bash
# Match CI environment
python3.11 -m venv venv-ci
source venv-ci/bin/activate
pip install -e ".[dev]"
pytest

# Check for timezone issues
TZ=UTC pytest

# Check for file path issues
pytest --basetemp=/tmp/pytest
```

### mypy Errors After Update

**Problem**: New mypy errors after updating dependencies

**Solution**:
```bash
# Regenerate mypy cache
mypy --install-types
rm -rf .mypy_cache
mypy clauxton

# Check for stub packages
pip install types-PyYAML types-setuptools
```

---

## Useful Development Commands

### One-Line Quality Check

```bash
# Run all quality checks
mypy clauxton && ruff check clauxton && ruff format --check clauxton && pytest
```

### Watch Mode (Auto-Run Tests)

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw tests/
```

### Generate Docs

```bash
# Install pdoc
pip install pdoc

# Generate HTML docs
pdoc clauxton -o docs/api/

# Serve docs locally
pdoc clauxton
# Opens http://localhost:8080
```

### Profile Performance

```bash
# Profile CLI command
python -m cProfile -o profile.stats -m clauxton.cli.main kb search "test"

# Analyze results
python -m pstats profile.stats
> sort cumtime
> stats 10
```

---

## Next Steps

After setting up your development environment:

1. **Read the code**: Start with `clauxton/core/models.py` and `clauxton/core/knowledge_base.py`
2. **Run the tests**: `pytest -v` to understand test coverage
3. **Make a small change**: Fix a typo, improve a docstring
4. **Submit a PR**: Follow the [CONTRIBUTING.md](../CONTRIBUTING.md) guide

---

## Getting Help

- **Questions?** Open a [Discussion](https://github.com/nakishiyaman/clauxton/discussions)
- **Bug found?** Open an [Issue](https://github.com/nakishiyaman/clauxton/issues)
- **Want to chat?** Join our Discord (coming soon)

---

**Document Status**: ✅ Complete
**Last Review**: 2025-10-19
**Next Review**: After Phase 0 implementation
