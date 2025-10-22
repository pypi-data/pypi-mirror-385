# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clauxton is a Claude Code plugin providing **persistent project context** through:
- **Knowledge Base**: Store architecture decisions, patterns, constraints, and conventions
- **Task Management**: Auto-inferred task dependencies with DAG validation
- **Conflict Detection**: Pre-merge conflict prediction (Phase 2)

**Status**: v0.9.0-beta - Production ready (94% test coverage, 390 tests)
**v0.10.0 Progress**: Week 2 Day 6 Complete! (528 tests, Enhanced Validation added)

## Build/Test Commands

### Testing
```bash
# Run all tests with coverage
pytest

# Run with HTML coverage report
pytest --cov=clauxton --cov-report=html --cov-report=term

# Run specific test file
pytest tests/core/test_knowledge_base.py

# Run specific test function
pytest tests/core/test_knowledge_base.py::test_add_entry -v

# Run tests by keyword
pytest -k "search" -v
```

### Code Quality
```bash
# Type checking (strict mode enabled)
mypy clauxton

# Linting and formatting
ruff check clauxton tests
ruff check --fix clauxton tests  # Auto-fix issues

# Run all quality checks
mypy clauxton && ruff check clauxton tests && pytest
```

### Building
```bash
# Build package (creates wheel + sdist)
python -m build

# Validate package
twine check dist/*

# Install in editable mode for development
pip install -e .
```

### Running CLI
```bash
# Initialize Clauxton in a project
clauxton init

# Knowledge Base commands
clauxton kb add                    # Interactive add
clauxton kb search "query"         # TF-IDF relevance search
clauxton kb list                   # List all entries
clauxton kb get KB-20251019-001    # Get specific entry
clauxton kb update KB-20251019-001 --title "New title"
clauxton kb delete KB-20251019-001

# Task Management commands
clauxton task add --name "Task name" --priority high
clauxton task list                 # List all tasks
clauxton task get TASK-001         # Get specific task
clauxton task update TASK-001 --status in_progress
clauxton task next                 # Get AI-recommended next task
clauxton task delete TASK-001

# Conflict Detection commands (Phase 2 - v0.9.0-beta)
clauxton conflict detect TASK-001           # Check conflicts for a task
clauxton conflict order TASK-001 TASK-002   # Get safe execution order
clauxton conflict check src/api/users.py    # Check file availability

# Undo commands (v0.10.0 - Week 1 Day 3)
clauxton undo                               # Undo last operation (with confirmation)
clauxton undo --history                     # Show operation history
clauxton undo --history --limit 20          # Show last 20 operations
```

## High-Level Architecture

### Package Structure
```
clauxton/
├── core/                          # Core business logic
│   ├── models.py                  # Pydantic data models (Entry, Task, etc.)
│   ├── knowledge_base.py          # KB CRUD operations (add, search, update, delete)
│   ├── task_manager.py            # Task lifecycle + DAG validation
│   ├── search.py                  # TF-IDF search implementation
│   └── conflict_detector.py       # Conflict detection (Phase 2)
├── cli/                           # Click-based CLI interface
│   ├── main.py                    # Main CLI + KB commands
│   ├── tasks.py                   # Task management commands
│   └── conflicts.py               # Conflict detection commands
├── mcp/                           # MCP Server integration
│   └── server.py                  # 15 MCP tools (kb_*, task_*, conflict detection)
└── utils/                         # Utility modules
    ├── yaml_utils.py              # Safe YAML I/O with atomic writes
    └── file_utils.py              # Secure file operations

Storage: .clauxton/
├── knowledge-base.yml             # All KB entries (YAML)
├── tasks.yml                      # All tasks (YAML)
└── backups/                       # Automatic backups
```

### Key Design Patterns

1. **Pydantic Models**: All data validated with strict typing
   - `KnowledgeBaseEntry`: id, title, category, content, tags, timestamps
   - `Task`: id, name, status, priority, depends_on, files_to_edit
   - Categories: architecture, constraint, decision, pattern, convention
   - Statuses: pending, in_progress, completed, blocked
   - Priorities: critical, high, medium, low

2. **YAML Storage**: Human-readable, Git-friendly
   - All writes are atomic (temp file → rename)
   - Automatic backups before modifications
   - Safe loading with `yaml.safe_load()` (no code execution)

3. **DAG Validation**: Tasks form a Directed Acyclic Graph
   - Cycle detection using DFS
   - Topological sort for execution order
   - Auto-inference of dependencies from file overlap

4. **TF-IDF Search**: Intelligent relevance ranking
   - Powered by scikit-learn
   - Graceful fallback to keyword search if unavailable
   - Multi-field search (title, content, tags)

5. **MCP Integration**: 15 tools exposed to Claude Code
   - Knowledge Base: kb_search, kb_add, kb_list, kb_get, kb_update, kb_delete
   - Task Management: task_add, task_list, task_get, task_update, task_next, task_delete
   - Conflict Detection: detect_conflicts, recommend_safe_order, check_file_conflicts

### Data Flow

**KB Add Flow**:
1. CLI/MCP → `KnowledgeBase.add(entry)`
2. Validate with Pydantic → Generate ID (KB-YYYYMMDD-NNN)
3. Backup existing YAML → Atomic write
4. Store in `.clauxton/knowledge-base.yml`

**Task Creation with Auto-Dependencies**:
1. CLI/MCP → `TaskManager.add(task)`
2. Validate task → Infer dependencies from file overlap
3. DAG validation (cycle detection) → Add to graph
4. Store in `.clauxton/tasks.yml`

**Search Flow**:
1. CLI/MCP → `Search.tfidf_search(query)`
2. Build TF-IDF matrix from all entries
3. Calculate cosine similarity → Rank by relevance
4. Return top N results

## Code Style Guidelines

### Python Type Hints (Required)
```python
# All functions must have type hints
def search_kb(query: str, limit: int = 10) -> List[KnowledgeBaseEntry]:
    """Search Knowledge Base by query."""
    pass
```

### Pydantic Models
```python
# Use Pydantic for data validation
from pydantic import BaseModel, Field

class Task(BaseModel):
    id: str = Field(..., pattern=r"^TASK-\d{3}$")
    name: str = Field(..., min_length=1)
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
```

### Error Handling
```python
# Use custom exceptions with clear messages
class ValidationError(Exception):
    """Validation failed."""
    pass

if not entry.title.strip():
    raise ValidationError(
        "Entry title cannot be empty. "
        "Please provide a descriptive title."
    )
```

### Docstrings (Google Style)
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
    """
    pass
```

### File Permissions
- `.clauxton/` directory: 700 (owner only)
- YAML files: 600 (owner read/write only)

## Testing Guidelines

### Test Structure
```
tests/
├── core/           # Unit tests for core modules (96% coverage target)
├── cli/            # CLI command tests (90% coverage target)
├── mcp/            # MCP server tests (95% coverage target)
├── utils/          # Utility tests (80% coverage target)
└── integration/    # End-to-end tests
```

### Writing Tests
- Use `tmp_path` fixture for file operations
- Test edge cases: Unicode, special characters, empty inputs
- Test error handling: Invalid inputs, missing files
- Test fallback behaviors: Search without scikit-learn

### Coverage Requirements
- Overall: 90% minimum (current: 94%)
- Core modules: 95%+ required
- New features: Must include comprehensive tests

## Configuration Files

### pyproject.toml
- Dependencies: pydantic>=2.0, click>=8.1, pyyaml>=6.0, scikit-learn>=1.3
- Dev dependencies: pytest, pytest-cov, mypy, ruff
- Python version: 3.11+
- Line length: 100 characters
- Entry points: `clauxton` CLI, `clauxton-mcp` server

### mypy.ini
- Strict mode enabled (`disallow_untyped_defs = True`)
- Python version: 3.11
- Ignores missing imports for third-party libs
- Tests directory has relaxed rules

### GitHub Actions (.github/workflows/ci.yml)
- Runs on: Python 3.11 & 3.12
- Jobs: Test (390 tests, ~50s), Lint (ruff + mypy, ~18s), Build (twine check, ~17s)
- All jobs run in parallel (~52s total)

## Important Patterns

### YAML Safety
```python
# ALWAYS use safe_load (never load)
import yaml
with open(path, "r") as f:
    data = yaml.safe_load(f)  # No code execution risk
```

### Atomic File Writes
```python
# Use temp file + rename for atomic writes
from clauxton.utils.yaml_utils import write_yaml

write_yaml(path, data)  # Automatic backup + atomic write
```

### Path Validation
```python
# Validate paths stay within project root
from pathlib import Path

def validate_path(path: Path, root: Path) -> None:
    if not path.resolve().is_relative_to(root.resolve()):
        raise SecurityError("Path traversal detected")
```

### ID Generation
```python
# KB entries: KB-YYYYMMDD-NNN (e.g., KB-20251019-001)
# Tasks: TASK-NNN (e.g., TASK-001)
```

## Common Development Tasks

### Add New CLI Command
1. Add Click command to `clauxton/cli/main.py` or submodule
2. Add corresponding test in `tests/cli/`
3. Update `README.md` usage section
4. Run: `pytest tests/cli/ && mypy clauxton/cli/`

### Add New MCP Tool
1. Add tool function to `clauxton/mcp/server.py` with `@server.call_tool()`
2. Add test in `tests/mcp/test_server.py`
3. Update `docs/mcp-server.md` documentation
4. Run: `pytest tests/mcp/ && mypy clauxton/mcp/`

### Add New Search Feature
1. Update `clauxton/core/search.py`
2. Add tests in `tests/core/test_search.py`
3. Ensure fallback behavior if scikit-learn unavailable
4. Run: `pytest tests/core/test_search.py -v`

### Release Checklist
1. Update version in `clauxton/__version__.py` and `pyproject.toml`
2. Update `CHANGELOG.md` with changes
3. Run full test suite: `pytest --cov=clauxton`
4. Run quality checks: `mypy clauxton && ruff check clauxton`
5. Build package: `python -m build`
6. Create git tag: `git tag -a v0.X.0 -m "Release v0.X.0"`
7. Push tag: `git push origin v0.X.0`
8. Upload to PyPI: `twine upload dist/*`

## Troubleshooting

### Import Errors
```bash
# Install in editable mode
pip install -e .
```

### Test Failures
```bash
# Run with verbose output
pytest -v

# Run specific failing test
pytest tests/path/to/test.py::test_name -v

# Check coverage for missing tests
pytest --cov=clauxton --cov-report=term-missing
```

### mypy Errors
```bash
# Regenerate cache
rm -rf .mypy_cache
mypy --install-types
mypy clauxton
```

### YAML Parsing Errors
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('.clauxton/knowledge-base.yml'))"

# Restore from backup
cp .clauxton/backups/knowledge-base.yml.bak .clauxton/knowledge-base.yml
```

## Clauxton Integration Philosophy

### Core Principle: "Transparent Yet Controllable"

Clauxton follows Claude Code's philosophy:
- **Do the Simple Thing First**: YAML + Markdown (human-readable, Git-friendly)
- **Composable**: MCP integration (seamless with Claude Code)
- **User Control**: CLI override always available
- **Safety-First**: Read-only by default, explicit writes with undo capability
- **Human-in-the-Loop**: Configurable confirmation levels (v0.10.0+)

### When to Use Clauxton (Transparent Integration)

#### 🔍 Phase 1: Requirements Gathering

**Trigger**: User mentions constraints, tech stack, or design decisions

**Action**: Automatically add to Knowledge Base via MCP

**Examples**:

| User Statement | MCP Call | Category |
|----------------|----------|----------|
| "Use FastAPI" | `kb_add(title="FastAPI Adoption", category="architecture", ...)` | architecture |
| "Maximum 1000 items" | `kb_add(title="Data Limit", category="constraint", ...)` | constraint |
| "JWT Authentication" | `kb_add(title="JWT Auth", category="decision", ...)` | decision |
| "Prefer snake_case" | `kb_add(title="Naming Convention", category="convention", ...)` | convention |

**Implementation Pattern**:
```python
# When user mentions technical decisions
if user_mentioned_tech_decision:
    kb_add(
        title=extract_title(user_message),
        category=infer_category(user_message),
        content=user_message,
        tags=extract_tags(user_message)
    )
```

---

#### 📋 Phase 2: Task Planning

**Trigger**: User requests feature implementation or breaks down work

**Action**: Generate tasks and import via YAML (v0.10.0+)

**Example Workflow**:

```
User: "I want to create a Todo app. Build backend with FastAPI and frontend with React."

↓ Claude Code Thought Process ↓

1. Feature breakdown:
   - Backend: FastAPI initialization, API design, DB setup
   - Frontend: React initialization, UI implementation
   - Integration: API integration

2. Generate YAML:
   ```yaml
   tasks:
     - name: "FastAPI Initialization"
       description: "Setup FastAPI project"
       priority: high
       files_to_edit: [backend/main.py, backend/requirements.txt]
       estimate: 1
     - name: "API Design"
       description: "Define Todo CRUD API endpoints"
       priority: high
       files_to_edit: [backend/api/todos.py]
       depends_on: [TASK-001]
       estimate: 2
     ...
   ```

3. Import via MCP:
   ```python
   result = task_import_yaml(yaml_content)
   # → 10 tasks created: TASK-001 to TASK-010
   ```

4. Verify:
   ```python
   tasks = task_list(status="pending")
   # → Confirm all tasks registered
   ```

5. Start implementation:
   ```python
   next_task = task_next()
   # → TASK-001 (FastAPI Initialization)
   ```

↓ User sees ↓

"Created 10 tasks.TASK-001(FastAPI Initialization)Starting from."
```

**Key Points**:
- User doesn't see YAML generation (transparent)
- All tasks created in single operation (efficient)
- Dependencies auto-inferred from file overlap
- Claude Code manages workflow (user just confirms if needed)

---

#### ⚠️ Phase 3: Conflict Detection (Before Implementation)

**Trigger**: Before starting a task

**Action**: Check conflicts via MCP

**Example Workflow**:

```python
# Before implementing TASK-003
conflicts = detect_conflicts("TASK-003")

if conflicts["risk"] == "HIGH":
    # Warn user
    print(f"⚠️ Warning: TASK-003 has HIGH conflict risk with TASK-002")
    print(f"Files: {conflicts['files']}")
    print(f"Recommendation: Complete TASK-002 first")

    # Ask user
    proceed = ask_user("Proceed anyway?")
    if not proceed:
        # Work on another task
        next_task = task_next()
```

**Key Points**:
- Automatic conflict checking (transparent)
- User is warned if HIGH risk
- User decides whether to proceed (control)

---

#### 🛠️ Phase 4: Implementation

**During Implementation**: Update task status

```python
# Start task
task_update("TASK-001", status="in_progress")

# ... implementation ...

# Complete task
task_update("TASK-001", status="completed")

# Move to next
next_task = task_next()
```

---

### Manual Override (User Control)

**Important**: User can always override with CLI

```bash
# View all KB entries
clauxton kb list

# Add entry manually
clauxton kb add --title "..." --category architecture

# Delete incorrect entry
clauxton kb delete KB-20251020-001

# View all tasks
clauxton task list

# Manually update task
clauxton task update TASK-001 --status completed

# Check conflicts manually
clauxton conflict detect TASK-003
```

**Philosophy**: Claude Code uses MCP (transparent), but user has CLI (control)

---

### Transparency & Inspection

**User can inspect at any time**:

```bash
# View internal state
cat .clauxton/knowledge-base.yml
cat .clauxton/tasks.yml

# Git diff
git diff .clauxton/

# Search
clauxton kb search "authentication"
clauxton task list --status pending
```

**Key Points**:
- All data is human-readable (YAML)
- All data is Git-friendly (version control)
- User can manually edit if needed (last resort)

---

### Error Handling

**If Clauxton operations fail**:

```python
try:
    result = kb_add(...)
except Exception as e:
    # Graceful degradation
    print(f"Failed to add to KB: {e}")
    print("Continuing without KB registration...")
    # Implementation continues
```

**Philosophy**: Clauxton is helpful but not blocking

---

### Human-in-the-Loop (v0.10.0+)

**Configurable Confirmation Modes**:

1. **"always" mode** (100% HITL):
   - Every write operation requires confirmation
   - Maximum safety, stricter workflow
   - Use: Team development, production environments

2. **"auto" mode** (75% HITL, default):
   - Threshold-based confirmation (10+ tasks, 5+ KB entries)
   - Balanced approach
   - Use: Most development workflows

3. **"never" mode** (25% HITL):
   - No confirmation prompts
   - Undo capability available
   - Use: Rapid prototyping, personal projects

**Configuration**:
```bash
# Set confirmation mode
clauxton config set confirmation_mode always   # Strict
clauxton config set confirmation_mode auto     # Balanced (default)
clauxton config set confirmation_mode never    # Fast

# View current mode
clauxton config get confirmation_mode
```

**All modes include**:
- ✅ Undo capability (`undo_last_operation()`)
- ✅ Operation logging (`.clauxton/logs/`)
- ✅ Automatic backups (`.clauxton/backups/`)

---

## 🎯 Best Practices

### DO:
✅ Use Clauxton transparently during natural conversation
✅ Register decisions/constraints as they're mentioned
✅ Generate tasks in bulk (YAML import, v0.10.0+)
✅ Check conflicts before implementation
✅ Update task status as you work
✅ Trust user to inspect/override if needed
✅ Respect user's confirmation_mode setting

### DON'T:
❌ Ask user to run CLI commands manually (breaks flow)
❌ Show YAML generation details (too technical)
❌ Skip conflict detection (causes merge issues)
❌ Leave task status outdated (confuses workflow)
❌ Override user's confirmation_mode preference

---

## 🔧 Technical Notes

### MCP Tools Available

**Knowledge Base** (6 tools):
- `kb_search(query, limit)` - Search KB entries
- `kb_add(title, category, content, tags)` - Add entry
- `kb_list(category)` - List entries
- `kb_get(entry_id)` - Get specific entry
- `kb_update(entry_id, ...)` - Update entry
- `kb_delete(entry_id)` - Delete entry

**Task Management** (6 tools + 1 in v0.10.0):
- `task_add(name, priority, files, ...)` - Add single task
- `task_import_yaml(yaml_content, skip_confirmation=False, on_error="rollback")` - ⭐ Bulk import (v0.10.0+)
  - **Confirmation Prompts** (✅ Week 1 Day 4): 14 tests
    - Returns `status: "confirmation_required"` when ≥10 tasks (configurable)
    - Preview includes: task count, estimated hours, priority/status breakdown
    - Use `skip_confirmation=True` for trusted operations
  - **Error Recovery** (✅ Week 1 Day 5): 15 tests
    - `on_error="rollback"` (default): Revert all on error (transactional)
    - `on_error="skip"`: Skip invalid tasks, continue (returns `status: "partial"`)
    - `on_error="abort"`: Stop immediately on first error
  - **YAML Safety** (✅ Week 1 Day 5): 10 tests
    - Blocks dangerous tags: `!!python`, `!!exec`, `!!apply`
    - Blocks dangerous patterns: `__import__`, `eval()`, `exec()`, `compile()`
- `task_list(status, priority)` - List tasks
- `task_get(task_id)` - Get specific task
- `task_update(task_id, status, ...)` - Update task
- `task_next()` - Get AI-recommended next task
- `task_delete(task_id)` - Delete task

**Conflict Detection** (3 tools):
- `detect_conflicts(task_id)` - Check conflicts for task
- `recommend_safe_order(task_ids)` - Get safe execution order
- `check_file_conflicts(file_paths)` - Check file availability

**KB Export** (v0.10.0+):
- `kb_export_docs(output_dir)` - ⭐ Export KB to Markdown docs

**Undo/History** (v0.10.0+ - ✅ Implemented in Week 1 Day 3):
- `undo_last_operation()` - ⭐ Reverse last operation (24 tests, 81% coverage)
- `get_recent_operations(limit)` - View operation history

**Configuration** (v0.10.0+ - Week 2):
- `get_recent_logs()` - View operation logs (planned)

Total: **17 tools** (15 current + 2 implemented in v0.10.0)

---

## 📊 Expected Behavior Changes

### Before Enhancement (Current v0.9.0-beta):

```
User: "I want to create a Todo app"
↓
Claude Code: "First, please run the following commands:
              clauxton task add --name 'FastAPI Initialization' ...
              clauxton task add --name 'API Design' ...
              ..."
↓
User: (manually run commands 10 times)
↓
Claude Code: "tasks registered. Let's begin."
```

**Problem**: Conversation flow is broken, too much manual work

---

### After Enhancement (v0.10.0):

```
User: "I want to create a Todo app"
↓
Claude Code: (internally generates YAML → task_import_yaml())
             "Created 10 tasks:
              - TASK-001: FastAPI Initialization
              - TASK-002: API Design
              - TASK-003: DB Setup
              ...
              TASK-001Starting from."
↓
User: "Yes, please proceed"
↓
Claude Code: (starts Implementation)
```

**Improvement**: Natural conversation, no manual work, efficient

---

## 📈 Success Metrics

**Quantitative Metrics**:
- task registration time: 5minutes → 10seconds(30times faster)
- User operation count: 10times → 0times(Fully automated)
- Claude Philosophy alignment: 70% → 95%(Composable + HITL Achieved)

**Qualitative Metrics**:
- Users can manage tasks through natural conversation only
- Claude CodeClaude Code autonomously utilizes Clauxton
- Manual override always available(User Control)
- Users can choose confirmation level(v0.10.0+)

---

## Development Roadmap

### Phase 0: Foundation (Complete)
- Knowledge Base CRUD operations
- YAML storage with atomic writes
- CLI interface

### Phase 1: Core Engine (Complete - v0.8.0)
- TF-IDF relevance search
- Task Management with DAG validation
- Auto-dependency inference
- MCP Server (12 tools)

### Phase 2: Conflict Detection (Complete - v0.9.0-beta)
- File overlap detection
- Risk scoring (LOW/MEDIUM/HIGH)
- Safe execution order recommendations
- 3 CLI commands: `clauxton conflict detect/order/check`
- 3 MCP tools (15 tools total)

## Links

- **PyPI**: https://pypi.org/project/clauxton/
- **GitHub**: https://github.com/nakishiyaman/clauxton
- **Issues**: https://github.com/nakishiyaman/clauxton/issues
- **Documentation**: See `docs/` directory
