# YAML Task Import Format Guide

**Version**: v0.10.0
**Feature**: Bulk task import via `clauxton task import` or `task_import_yaml()` MCP tool
**Status**: Implemented (Week 1 Day 1-2)

---

## Table of Contents

1. [Overview](#overview)
2. [Basic Format](#basic-format)
3. [Field Reference](#field-reference)
4. [Examples](#examples)
5. [Validation Rules](#validation-rules)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The YAML task import feature enables you to create multiple tasks in a single operation, making it ideal for:

- **Project initialization**: Define all tasks upfront
- **Sprint planning**: Import an entire sprint's worth of tasks
- **Template-based workflows**: Reuse task structures across projects
- **Transparent integration**: Claude Code can auto-generate and import task lists

### Use Cases

| Use Case | Before (Manual) | After (YAML Import) |
|----------|----------------|---------------------|
| Create 10 tasks | 10 separate `clauxton task add` commands | 1 YAML file + 1 import command |
| Time required | ~5 minutes | ~10 seconds |
| Error-prone | High (manual typing) | Low (validated) |

---

## Basic Format

### Minimal Example

```yaml
tasks:
  - name: "Task name"
```

### Complete Example

```yaml
tasks:
  - name: "Setup FastAPI project"
    description: "Initialize FastAPI with basic project structure"
    priority: high
    files_to_edit:
      - main.py
      - requirements.txt
    related_kb:
      - KB-20251019-001
    estimated_hours: 2.5

  - name: "Create database models"
    description: "Define SQLAlchemy models for users and posts"
    priority: high
    depends_on:
      - TASK-001
    files_to_edit:
      - models/user.py
      - models/post.py
    estimated_hours: 3.0
```

---

## Field Reference

### Required Fields

#### `name` (string, required)
- **Description**: Task name
- **Constraints**: Non-empty string
- **Example**: `"Setup database"`

### Optional Fields

#### `description` (string, optional)
- **Description**: Detailed task description
- **Supports**: Multiline text (use YAML `|` or `>` syntax)
- **Example**:
  ```yaml
  description: |
    This task involves:
    1. Setting up PostgreSQL
    2. Creating initial schema
    3. Running migrations
  ```

#### `priority` (string, optional)
- **Description**: Task priority level
- **Values**: `low`, `medium`, `high`, `critical`
- **Default**: `medium`
- **Example**: `priority: high`

#### `depends_on` (list of strings, optional)
- **Description**: List of task IDs this task depends on
- **Format**: `TASK-XXX` format
- **Validation**: All dependencies must exist
- **Circular dependency detection**: Automatic
- **Example**:
  ```yaml
  depends_on:
    - TASK-001
    - TASK-002
  ```

#### `files_to_edit` (list of strings, optional)
- **Description**: Files this task will modify
- **Used for**: Conflict detection, auto-dependency inference
- **Example**:
  ```yaml
  files_to_edit:
    - src/api/users.py
    - tests/test_users.py
  ```

#### `related_kb` (list of strings, optional)
- **Description**: Related Knowledge Base entry IDs
- **Format**: `KB-YYYYMMDD-NNN` format
- **Example**:
  ```yaml
  related_kb:
    - KB-20251019-001
    - KB-20251019-005
  ```

#### `estimated_hours` (number, optional)
- **Description**: Estimated time to complete (in hours)
- **Format**: Float or integer
- **Example**: `estimated_hours: 4.5`

### Auto-Generated Fields

These fields are automatically set and should **not** be included in YAML:

- `id`: Auto-generated (TASK-001, TASK-002, etc.)
- `status`: Always set to `pending`
- `created_at`: Current timestamp
- `started_at`: `null` initially
- `completed_at`: `null` initially
- `actual_hours`: `null` initially

---

## Examples

### Example 1: Simple Task List

```yaml
tasks:
  - name: "Research FastAPI best practices"
    priority: low
    estimated_hours: 2.0

  - name: "Setup project structure"
    priority: high
    estimated_hours: 1.0

  - name: "Implement authentication"
    priority: critical
    estimated_hours: 8.0
```

**Result**: Creates TASK-001, TASK-002, TASK-003

---

### Example 2: Tasks with Dependencies

```yaml
tasks:
  - name: "Design database schema"
    priority: high
    files_to_edit:
      - docs/schema.md

  - name: "Create SQLAlchemy models"
    priority: high
    depends_on:
      - TASK-001
    files_to_edit:
      - models/user.py
      - models/post.py

  - name: "Write database tests"
    priority: medium
    depends_on:
      - TASK-002
    files_to_edit:
      - tests/test_models.py
```

**Dependency Graph**:
```
TASK-001 (Design schema)
   ↓
TASK-002 (Create models)
   ↓
TASK-003 (Write tests)
```

---

### Example 3: Sprint Planning (Full)

```yaml
tasks:
  # Infrastructure
  - name: "Setup Docker environment"
    description: "Configure Docker Compose with PostgreSQL and Redis"
    priority: critical
    files_to_edit:
      - docker-compose.yml
      - Dockerfile
    estimated_hours: 3.0

  # Backend API
  - name: "Implement user registration endpoint"
    description: "POST /api/users - Create new user with email validation"
    priority: high
    depends_on:
      - TASK-001
    files_to_edit:
      - api/routes/users.py
      - api/schemas/user.py
    related_kb:
      - KB-20251019-001  # API design guidelines
    estimated_hours: 4.0

  - name: "Implement login endpoint"
    description: "POST /api/auth/login - JWT token generation"
    priority: high
    depends_on:
      - TASK-002
    files_to_edit:
      - api/routes/auth.py
      - utils/jwt.py
    estimated_hours: 3.0

  # Testing
  - name: "Write integration tests"
    description: "Test registration and login flows end-to-end"
    priority: medium
    depends_on:
      - TASK-002
      - TASK-003
    files_to_edit:
      - tests/integration/test_auth.py
    estimated_hours: 5.0
```

---

### Example 4: Multiline Descriptions

```yaml
tasks:
  - name: "Refactor authentication middleware"
    description: |
      Current Issues:
      - JWT validation is synchronous (blocking)
      - No rate limiting
      - Error messages leak implementation details

      Improvements:
      - Make JWT validation async
      - Add rate limiting (10 req/min)
      - Sanitize error messages

      References:
      - Security audit report (2025-10-15)
      - FastAPI best practices guide
    priority: high
    files_to_edit:
      - middleware/auth.py
      - middleware/rate_limit.py
    estimated_hours: 6.0
```

---

## Validation Rules

### Automatic Validation

The import process validates:

1. **YAML Syntax**: Must be valid YAML
2. **Required Fields**: `name` must be non-empty
3. **Enum Values**: `priority` must be one of: low, medium, high, critical
4. **Dependency Existence**: All `depends_on` IDs must exist (unless `skip_validation=True`)
5. **Circular Dependencies**: Automatically detected using DFS algorithm
6. **Data Types**: All fields must match expected types (string, list, number)

### Validation Error Examples

#### Empty Task Name
```yaml
tasks:
  - name: ""
    priority: high
```
**Error**: `Task 1 (''): Field required: name`

#### Invalid Priority
```yaml
tasks:
  - name: "Task A"
    priority: urgent  # Invalid
```
**Error**: `Task 1 ('Task A'): Input should be 'low', 'medium', 'high', or 'critical'`

#### Circular Dependency
```yaml
tasks:
  - id: TASK-001
    name: "Task A"
    depends_on:
      - TASK-002
  - id: TASK-002
    name: "Task B"
    depends_on:
      - TASK-001
```
**Error**: `Circular dependency detected: TASK-001 → TASK-002 → TASK-001`

#### Nonexistent Dependency
```yaml
tasks:
  - name: "Task A"
    depends_on:
      - TASK-999  # Doesn't exist
```
**Error**: `Task 'Task A' (ID: TASK-001): Depends on non-existent task 'TASK-999'`

---

## Error Handling

### All-or-Nothing Import

If **any** task fails validation, **no tasks are imported**. This ensures consistency.

**Example**:
```yaml
tasks:
  - name: "Valid Task 1"
    priority: high
  - name: ""  # Invalid (empty name)
  - name: "Valid Task 2"
    priority: low
```

**Result**: 0 tasks imported, error message displayed.

### Error Response Format

```json
{
  "status": "error",
  "imported": 0,
  "task_ids": [],
  "errors": [
    "Task 2 (''): Field required: name"
  ],
  "next_task": null
}
```

---

## Best Practices

### 1. Use Descriptive Names

✅ **Good**:
```yaml
- name: "Implement JWT authentication for user login"
```

❌ **Bad**:
```yaml
- name: "Auth"
```

### 2. Break Down Large Tasks

✅ **Good**:
```yaml
- name: "Design database schema"
- name: "Create SQLAlchemy models"
- name: "Write database migration"
- name: "Test database operations"
```

❌ **Bad**:
```yaml
- name: "Setup entire database"
```

### 3. Use Dependencies Wisely

✅ **Good**: Sequential dependencies
```yaml
- name: "Create API endpoint"
  # TASK-001
- name: "Write tests for endpoint"
  depends_on:
    - TASK-001
```

❌ **Bad**: Over-specification
```yaml
- name: "Write README"
  depends_on:
    - TASK-001
    - TASK-002
    - TASK-003
    - TASK-004
    # Too many dependencies for a documentation task
```

### 4. Validate Before Importing

Use `--dry-run` to validate without creating tasks:

```bash
clauxton task import tasks.yml --dry-run
```

### 5. Version Control Your YAML Files

Store task definitions in Git for:
- **Repeatability**: Recreate project structure
- **Templates**: Reuse across similar projects
- **History**: Track changes to project plans

**Example structure**:
```
.clauxton/
  templates/
    fastapi-project.yml
    django-project.yml
    microservice.yml
```

---

## Troubleshooting

### Issue 1: "Invalid YAML format. Expected 'tasks' key"

**Cause**: Missing or incorrect root key

❌ **Wrong**:
```yaml
- name: "Task A"
```

✅ **Correct**:
```yaml
tasks:
  - name: "Task A"
```

---

### Issue 2: "'tasks' must be a list"

**Cause**: `tasks` is not a list

❌ **Wrong**:
```yaml
tasks:
  name: "Single task"
```

✅ **Correct**:
```yaml
tasks:
  - name: "Single task"
```

---

### Issue 3: "YAML parsing error"

**Cause**: Invalid YAML syntax

Common issues:
- Missing quotes around strings with special characters
- Incorrect indentation (use 2 spaces, not tabs)
- Unclosed quotes

❌ **Wrong**:
```yaml
tasks:
  - name: Task with: colon  # Unquoted colon
```

✅ **Correct**:
```yaml
tasks:
  - name: "Task with: colon"
```

---

### Issue 4: Unicode Characters Not Working

**Solution**: Save file as UTF-8

✅ **Supported**:
```yaml
tasks:
  - name: "Task A"
    description: "Description in Japanese"
  - name: "Task with emoji 🚀"
```

---

### Issue 5: Import Succeeds but Tasks Not Visible

**Cause**: Check if you're in the correct directory

```bash
# Verify .clauxton exists
ls -la .clauxton/

# Check tasks were created
clauxton task list
```

---

## CLI Usage

### Basic Import

```bash
clauxton task import tasks.yml
```

**Output**:
```
✓ Imported 5 tasks

  • TASK-001
  • TASK-002
  • TASK-003
  • TASK-004
  • TASK-005

📋 Next task to work on:
  TASK-001

  Start working:
    clauxton task update TASK-001 --status in_progress
```

### Dry-Run (Validation Only)

```bash
clauxton task import tasks.yml --dry-run
```

**Output**:
```
✓ Validation successful (dry-run)
  Would import 5 tasks:
    - TASK-001
    - TASK-002
    - TASK-003
    - TASK-004
    - TASK-005
```

### Skip Dependency Validation

```bash
clauxton task import tasks.yml --skip-validation
```

**Use case**: When importing tasks with forward references (dependencies defined later).

---

## MCP Tool Usage

### From Claude Code

Claude Code can call the MCP tool directly:

```python
result = task_import_yaml(
    yaml_content="""
tasks:
  - name: "Setup FastAPI"
    priority: high
  - name: "Create API endpoints"
    depends_on:
      - TASK-001
""",
    dry_run=False,
    skip_validation=False
)
```

### Response Format

```json
{
  "status": "success",
  "imported": 2,
  "task_ids": ["TASK-001", "TASK-002"],
  "errors": [],
  "next_task": "TASK-001"
}
```

---

## Advanced Features

### Feature 1: ID Continuation

When existing tasks already exist, new IDs continue from the last ID:

**Existing**: TASK-001, TASK-002
**Import**: 3 new tasks
**Result**: TASK-003, TASK-004, TASK-005

---

### Feature 2: Dependency on Existing Tasks

You can create new tasks that depend on existing tasks:

```yaml
tasks:
  - name: "New feature"
    depends_on:
      - TASK-001  # Existing task
```

---

### Feature 3: Next Task Recommendation

After import, Clauxton recommends the highest priority task with no blocking dependencies.

**Priority order**: critical > high > medium > low

---

## Version History

- **v0.10.0 (2025-11-10)**: Initial release
  - YAML bulk import via CLI and MCP
  - Circular dependency detection
  - Dry-run validation mode
  - 24 comprehensive tests (98% coverage)

---

## See Also

- [Task Management Guide](task-management-guide.md)
- [Quick Start Guide](quick-start.md)
- [MCP Integration Guide](MCP_INTEGRATION_GUIDE.md)
- [Conflict Detection Guide](conflict-detection.md)

---

**Questions?** Open an issue at https://github.com/nakishiyaman/clauxton/issues
