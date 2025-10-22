# Batch Task Import Feature Design

**Version**: v0.10.0 (Proposed)
**Status**: Design Phase
**Priority**: HIGH
**Estimated Effort**: 8-12 hours

---

## 1. Overview

### Problem
Currently, adding multiple tasks requires multiple CLI/MCP calls:
- 10 tasks = 10 `task_add()` calls
- No transaction support
- Inefficient for Claude Code automation
- Verbose logging

### Solution
Add batch task import functionality with two approaches:
1. **YAML Import** (Phase 1, HIGH priority) - Human-friendly, Git-manageable
2. **Batch MCP Tool** (Phase 2, MEDIUM priority) - Programmatic bulk operations

---

## 2. Feature Specification

### 2.1 YAML Import (Phase 1)

#### CLI Command
```bash
clauxton task import <yaml-file>

# Options:
#   --dry-run      : Preview import without adding tasks
#   --validate     : Validate YAML only
#   --skip-deps    : Skip dependency resolution
```

#### YAML Format
```yaml
# tasks-template.yml
tasks:
  - name: "FastAPI project initialization"
    priority: high
    description: "Setup FastAPI with basic structure"
    files:
      - backend/main.py
      - backend/requirements.txt
      - backend/pyproject.toml
    estimate: 1
    tags:
      - backend
      - setup

  - name: "PostgreSQL connection setup"
    priority: high
    description: "Configure database connection and SQLAlchemy"
    files:
      - backend/database.py
      - backend/config.py
      - .env.example
    estimate: 2
    depends_on:
      - TASK-001  # Can reference by ID
      # Or by name (auto-resolved):
      # - "FastAPI project initialization"
    kb_refs:
      - KB-20251020-001
    tags:
      - backend
      - database

  - name: "User model creation"
    priority: high
    files:
      - backend/models/user.py
      - backend/alembic/versions/001_create_users.py
    estimate: 2
    depends_on:
      - "PostgreSQL connection setup"  # Name-based reference
```

#### YAML Schema Validation
```yaml
# Schema (using pydantic)
class TaskImportSchema:
    tasks: List[TaskDefinition]

class TaskDefinition:
    name: str                           # Required, max 100 chars
    priority: str = "medium"            # low, medium, high, critical
    description: Optional[str] = None   # Optional, no length limit
    files: List[str] = []               # List of file paths
    estimate: Optional[float] = None    # Estimated hours
    depends_on: List[str] = []          # Task IDs or names
    kb_refs: List[str] = []             # KB entry IDs
    tags: List[str] = []                # Custom tags
```

#### Output
```bash
$ clauxton task import tasks-template.yml

Importing tasks from: tasks-template.yml
✓ Validated 3 tasks
✓ Resolved dependencies:
  - TASK-002 depends on TASK-001
  - TASK-003 depends on TASK-002

✓ Imported 3 tasks:
  - TASK-001: FastAPI project initialization
  - TASK-002: PostgreSQL connection setup
  - TASK-003: User model creation

Next steps:
  clauxton task list
  clauxton task next
```

#### Dry Run
```bash
$ clauxton task import tasks-template.yml --dry-run

Preview import (no changes):
  Would create 3 tasks:
    ✓ TASK-001: FastAPI project initialization (high priority)
    ✓ TASK-002: PostgreSQL connection setup (high priority, depends on TASK-001)
    ✓ TASK-003: User model creation (high priority, depends on TASK-002)

Run without --dry-run to import.
```

---

### 2.2 MCP Tool (Phase 1)

#### Tool Definition
```python
@mcp.tool()
def task_import_yaml(yaml_content: str, dry_run: bool = False) -> dict[str, Any]:
    """
    Import multiple tasks from YAML content.

    Args:
        yaml_content: YAML string containing task definitions
        dry_run: If True, validate only without creating tasks

    Returns:
        Dictionary with:
        - imported_count: Number of tasks imported
        - task_ids: List of created task IDs
        - dependencies: Dependency graph

    Example YAML format:
        tasks:
          - name: "Setup database"
            priority: high
            files: ["db.py"]
            estimate: 2
    """
```

#### Usage from Claude Code
```
User: "Todoアプリのバックエンドタスク10個を追加して"

Claude Code:
1. Generates YAML content with 10 tasks
2. Calls task_import_yaml(yaml_content)
3. Returns: "✓ 10個のタスクを追加しました (TASK-001 ~ TASK-010)"
```

---

### 2.3 Batch MCP Tool (Phase 2)

#### Tool Definition
```python
@mcp.tool()
def task_add_batch(tasks: List[dict[str, Any]]) -> dict[str, Any]:
    """
    Add multiple tasks in a single operation.

    Args:
        tasks: List of task definitions, each with:
            - name (required): Task name
            - priority (optional): low, medium, high, critical (default: medium)
            - description (optional): Detailed description
            - files (optional): List of file paths
            - estimate (optional): Estimated hours
            - depends_on (optional): List of task IDs or names
            - kb_refs (optional): List of KB entry IDs

    Returns:
        Dictionary with:
        - added_count: Number of tasks added
        - task_ids: List of created task IDs
        - errors: List of errors (if any)

    Example:
        task_add_batch([
            {"name": "Task 1", "priority": "high", "files": ["file1.py"]},
            {"name": "Task 2", "priority": "medium", "files": ["file2.py"]}
        ])
    """
```

---

## 3. Implementation Plan

### Phase 1: YAML Import (8 hours)

#### 3.1 Core Implementation (4 hours)
**File**: `clauxton/core/task_importer.py`

```python
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, ValidationError

class TaskDefinition(BaseModel):
    """Task definition for import."""
    name: str
    priority: str = "medium"
    description: Optional[str] = None
    files: List[str] = []
    estimate: Optional[float] = None
    depends_on: List[str] = []
    kb_refs: List[str] = []
    tags: List[str] = []

class TaskImportSchema(BaseModel):
    """Schema for task import YAML."""
    tasks: List[TaskDefinition]

class TaskImporter:
    """Import tasks from YAML files."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.task_manager = TaskManager(project_root)

    def import_from_yaml(
        self,
        yaml_path: Path,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Import tasks from YAML file.

        Args:
            yaml_path: Path to YAML file
            dry_run: If True, validate only without creating tasks

        Returns:
            Dictionary with import results

        Raises:
            ValidationError: If YAML format is invalid
            FileNotFoundError: If YAML file not found
        """
        # 1. Load YAML
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        # 2. Validate schema
        schema = TaskImportSchema(**data)

        # 3. Resolve dependencies (name -> ID)
        resolved_tasks = self._resolve_dependencies(schema.tasks)

        # 4. Dry run: return preview
        if dry_run:
            return self._preview_import(resolved_tasks)

        # 5. Add tasks
        added_tasks = []
        for task_def in resolved_tasks:
            task_id = self.task_manager.generate_task_id()
            task = Task(
                id=task_id,
                name=task_def.name,
                description=task_def.description,
                status="pending",
                priority=task_def.priority,
                depends_on=task_def.depends_on,
                files_to_edit=task_def.files,
                related_kb=task_def.kb_refs,
                estimated_hours=task_def.estimate,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            self.task_manager.add(task)
            added_tasks.append(task_id)

        return {
            "imported_count": len(added_tasks),
            "task_ids": added_tasks,
            "dependencies": self._build_dependency_graph(resolved_tasks),
        }

    def _resolve_dependencies(
        self,
        tasks: List[TaskDefinition]
    ) -> List[TaskDefinition]:
        """
        Resolve dependency names to task IDs.

        Supports:
        - depends_on: ["TASK-001"]  (ID reference)
        - depends_on: ["Task name"]  (Name reference)
        """
        # Name -> ID mapping
        name_to_id: Dict[str, str] = {}

        # Generate IDs for all tasks first
        for i, task in enumerate(tasks):
            task_id = f"TASK-{i+1:03d}"  # Temporary ID
            name_to_id[task.name] = task_id

        # Resolve dependencies
        for task in tasks:
            resolved_deps = []
            for dep in task.depends_on:
                if dep.startswith("TASK-"):
                    # Already an ID
                    resolved_deps.append(dep)
                elif dep in name_to_id:
                    # Name reference -> resolve to ID
                    resolved_deps.append(name_to_id[dep])
                else:
                    raise ValueError(f"Dependency not found: {dep}")
            task.depends_on = resolved_deps

        return tasks

    def _preview_import(self, tasks: List[TaskDefinition]) -> Dict[str, Any]:
        """Generate dry-run preview."""
        return {
            "dry_run": True,
            "task_count": len(tasks),
            "tasks": [
                {
                    "name": task.name,
                    "priority": task.priority,
                    "depends_on": task.depends_on,
                }
                for task in tasks
            ],
        }

    def _build_dependency_graph(
        self,
        tasks: List[TaskDefinition]
    ) -> Dict[str, List[str]]:
        """Build dependency graph for visualization."""
        graph = {}
        for task in tasks:
            graph[task.name] = task.depends_on
        return graph
```

#### 3.2 CLI Command (2 hours)
**File**: `clauxton/cli/task_commands.py`

```python
@task_group.command("import")
@click.argument("yaml_file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Preview import without adding tasks")
@click.option("--validate", is_flag=True, help="Validate YAML only")
def task_import(yaml_file: str, dry_run: bool, validate: bool) -> None:
    """Import tasks from YAML file."""
    try:
        importer = TaskImporter(Path.cwd())
        result = importer.import_from_yaml(
            Path(yaml_file),
            dry_run=dry_run or validate
        )

        if dry_run or validate:
            click.echo(f"Preview import (no changes):")
            click.echo(f"  Would create {result['task_count']} tasks:")
            for task in result['tasks']:
                deps = f" (depends on {', '.join(task['depends_on'])})" if task['depends_on'] else ""
                click.echo(f"    ✓ {task['name']} ({task['priority']} priority){deps}")
        else:
            click.echo(f"✓ Imported {result['imported_count']} tasks:")
            for task_id in result['task_ids']:
                click.echo(f"  - {task_id}")

    except ValidationError as e:
        click.echo(f"❌ Invalid YAML format:", err=True)
        click.echo(str(e), err=True)
        sys.exit(1)
```

#### 3.3 MCP Tool (1 hour)
**File**: `clauxton/mcp/server.py`

```python
@mcp.tool()
def task_import_yaml(yaml_content: str, dry_run: bool = False) -> dict[str, Any]:
    """Import multiple tasks from YAML content."""
    import tempfile

    # Write YAML to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write(yaml_content)
        temp_path = Path(f.name)

    try:
        importer = TaskImporter(Path.cwd())
        result = importer.import_from_yaml(temp_path, dry_run=dry_run)
        return result
    finally:
        temp_path.unlink()
```

#### 3.4 Tests (1 hour)
**File**: `tests/core/test_task_importer.py`

```python
def test_import_tasks_from_yaml(tmp_path: Path) -> None:
    """Test importing tasks from YAML file."""
    yaml_content = """
tasks:
  - name: "Task 1"
    priority: high
    files:
      - file1.py
    estimate: 2
  - name: "Task 2"
    priority: medium
    depends_on:
      - "Task 1"
"""
    yaml_file = tmp_path / "tasks.yml"
    yaml_file.write_text(yaml_content)

    importer = TaskImporter(tmp_path)
    result = importer.import_from_yaml(yaml_file)

    assert result["imported_count"] == 2
    assert len(result["task_ids"]) == 2
```

---

### Phase 2: Batch MCP Tool (4 hours)

#### Implementation
**File**: `clauxton/mcp/server.py`

```python
@mcp.tool()
def task_add_batch(tasks: List[dict[str, Any]]) -> dict[str, Any]:
    """Add multiple tasks in a single operation."""
    tm = TaskManager(Path.cwd())
    added_tasks = []
    errors = []

    for i, task_data in enumerate(tasks):
        try:
            task_id = tm.generate_task_id()
            task = Task(
                id=task_id,
                name=task_data["name"],
                description=task_data.get("description"),
                status="pending",
                priority=task_data.get("priority", "medium"),
                depends_on=task_data.get("depends_on", []),
                files_to_edit=task_data.get("files", []),
                related_kb=task_data.get("kb_refs", []),
                estimated_hours=task_data.get("estimate"),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            tm.add(task)
            added_tasks.append(task_id)
        except Exception as e:
            errors.append({
                "index": i,
                "task_name": task_data.get("name", "Unknown"),
                "error": str(e),
            })

    return {
        "added_count": len(added_tasks),
        "task_ids": added_tasks,
        "errors": errors,
    }
```

---

## 4. Project Templates

### 4.1 Template Repository
```
clauxton/templates/
├── fastapi-backend.yml
├── react-frontend.yml
├── django-backend.yml
├── nextjs-fullstack.yml
└── README.md
```

### 4.2 Example Template: fastapi-backend.yml
```yaml
# FastAPI Backend Project Template
# Usage: clauxton task import fastapi-backend.yml

tasks:
  - name: "FastAPI project initialization"
    priority: high
    description: "Setup FastAPI with basic project structure"
    files:
      - backend/main.py
      - backend/__init__.py
      - backend/requirements.txt
      - backend/pyproject.toml
    estimate: 1
    tags:
      - setup
      - backend

  - name: "Database connection setup"
    priority: high
    description: "Configure PostgreSQL connection with SQLAlchemy"
    files:
      - backend/database.py
      - backend/config.py
      - .env.example
    estimate: 2
    depends_on:
      - "FastAPI project initialization"
    tags:
      - database
      - setup

  - name: "User model and authentication"
    priority: high
    files:
      - backend/models/user.py
      - backend/api/auth.py
      - backend/utils/security.py
      - backend/alembic/versions/001_create_users.py
    estimate: 4
    depends_on:
      - "Database connection setup"
    tags:
      - auth
      - models

  - name: "API endpoint scaffolding"
    priority: medium
    files:
      - backend/api/__init__.py
      - backend/api/routes.py
      - backend/schemas/__init__.py
    estimate: 2
    depends_on:
      - "FastAPI project initialization"
    tags:
      - api

  - name: "Testing setup (pytest)"
    priority: medium
    files:
      - backend/tests/__init__.py
      - backend/tests/conftest.py
      - pytest.ini
    estimate: 2
    tags:
      - testing
```

---

## 5. Documentation Updates

### 5.1 New Documentation
- `docs/BATCH_TASK_IMPORT.md` - Complete guide (this file)
- `docs/templates/README.md` - Template usage guide

### 5.2 Update Existing Docs
- `docs/HOW_TO_USE_v0.10.0.md` - Add batch import section
- `docs/task-management-guide.md` - Add import examples
- `README.md` - Mention template feature

---

## 6. Testing Strategy

### Unit Tests
- ✅ YAML parsing and validation
- ✅ Dependency resolution (name -> ID)
- ✅ Dry-run functionality
- ✅ Error handling (invalid YAML, missing deps)

### Integration Tests
- ✅ CLI: `clauxton task import`
- ✅ MCP: `task_import_yaml()`
- ✅ Batch: `task_add_batch()`

### Edge Cases
- ✅ Circular dependencies
- ✅ Missing dependency references
- ✅ Duplicate task names
- ✅ Invalid priority values
- ✅ Large imports (100+ tasks)

---

## 7. Migration Path

### v0.9.0-beta → v0.10.0

**No breaking changes** - This is an additive feature.

**New features**:
1. `clauxton task import <yaml-file>` CLI command
2. `task_import_yaml()` MCP tool
3. `task_add_batch()` MCP tool (Phase 2)
4. Project templates in `templates/` directory

---

## 8. Future Enhancements

### v0.11.0+
- **Export to YAML**: `clauxton task export tasks.yml`
- **Template sharing**: Public template registry
- **Smart templates**: Templates with placeholder variables
- **Import from URL**: `clauxton task import https://example.com/tasks.yml`

---

## 9. Questions for User

1. **Priority**: Is Phase 1 (YAML import) sufficient for v0.10.0?
2. **Templates**: Should we include standard templates in the package?
3. **Naming**: Any preference for command names?
   - `import` vs `load` vs `batch-add`
4. **Format**: YAML only, or also support JSON/TOML?

---

**Status**: Awaiting user feedback to proceed with implementation.
