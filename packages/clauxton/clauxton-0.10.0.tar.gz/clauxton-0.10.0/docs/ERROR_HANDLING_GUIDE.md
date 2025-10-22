# Error Handling Guide

Complete guide to understanding and resolving errors in Clauxton.

## Table of Contents

- [Overview](#overview)
- [Error Categories](#error-categories)
- [Common Errors](#common-errors)
- [Error Recovery Strategies](#error-recovery-strategies)
- [Troubleshooting Workflow](#troubleshooting-workflow)
- [Prevention Best Practices](#prevention-best-practices)

---

## Overview

Clauxton provides **actionable error messages** with:
- **Context**: What went wrong
- **Suggestion**: How to fix it
- **Commands**: Specific commands to run

All errors include the specific location and resolution steps.

---

## Error Categories

### 1. Validation Errors (`ValidationError`)

**Cause**: Invalid input data (empty names, invalid priorities, negative values).

**Example**:
```
ValidationError: Task name cannot be empty.
Suggestion: Provide a descriptive task name.
Example: clauxton task add --name "Setup database"
```

**Resolution**:
1. Check the error message for the specific field
2. Correct the invalid value
3. Retry the operation

---

### 2. Not Found Errors (`NotFoundError`)

**Cause**: Referenced entity doesn't exist (task ID, KB entry ID).

**Example**:
```
NotFoundError: Task 'TASK-999' not found.
Available tasks: TASK-001, TASK-002, TASK-003
Suggestion: Check the task ID and try again.
Command: clauxton task list
```

**Resolution**:
1. List available entities: `clauxton task list` or `clauxton kb list`
2. Verify the correct ID
3. Use the correct ID in your command

---

### 3. Duplicate Errors (`DuplicateError`)

**Cause**: Attempting to create an entity with an existing ID or name.

**Example**:
```
DuplicateError: Task with ID 'TASK-001' already exists.
Suggestion: Update the existing task or use a different ID.
Commands:
  - Update: clauxton task update TASK-001 --name "New Name"
  - View: clauxton task get TASK-001
```

**Resolution**:
- **Update existing**: Use `update` command
- **Create new**: System will auto-generate next available ID
- **Delete old**: Use `delete` command (with undo capability)

---

### 4. Cycle Detected Errors (`CycleDetectedError`)

**Cause**: Circular task dependencies (A depends on B, B depends on A).

**Example**:
```
CycleDetectedError: Circular dependency detected.
Cycle path: TASK-001 -> TASK-002 -> TASK-003 -> TASK-001
Suggestion: Break the cycle by removing one of the dependencies.
Commands:
  - View dependencies: clauxton task get TASK-001
  - Update dependencies: clauxton task update TASK-001 --depends-on ""
```

**Resolution**:
1. Identify the cycle path (shown in error)
2. Choose a dependency to remove
3. Update the task: `clauxton task update TASK-XXX --depends-on ""`

---

### 5. YAML Safety Errors (`YAMLSecurityError`)

**Cause**: YAML content contains dangerous patterns (code injection attempts).

**Example**:
```
YAMLSecurityError: Dangerous YAML pattern detected: !!python/object/apply
Security risk: This pattern can execute arbitrary code.
Suggestion: Remove dangerous patterns and use safe YAML.
See: docs/YAML_FORMAT_GUIDE.md
```

**Resolution**:
1. Remove dangerous tags: `!!python`, `!!exec`, `!!apply`
2. Remove dangerous functions: `__import__`, `eval()`, `exec()`
3. Use safe YAML format (see `docs/YAML_TASK_FORMAT.md`)

---

### 6. Import Errors

#### Partial Import (`status: "partial"`)

**Cause**: Some tasks failed validation during `on_error="skip"` mode.

**Example**:
```json
{
  "status": "partial",
  "imported": 8,
  "skipped": 2,
  "skipped_tasks": [
    {"name": "Invalid Task", "error": "Task name cannot be empty"},
    {"name": "Bad Priority", "error": "Invalid priority: urgent"}
  ]
}
```

**Resolution**:
1. Review `skipped_tasks` list
2. Fix validation errors in YAML
3. Re-import corrected tasks

#### Import Rollback (`status: "error"`)

**Cause**: Error occurred during `on_error="rollback"` mode (default).

**Example**:
```json
{
  "status": "error",
  "error": "Circular dependency detected",
  "message": "Import rolled back - no tasks were created"
}
```

**Resolution**:
1. Check the error message
2. Fix the issue in YAML
3. Retry import (safe - nothing was committed)

---

## Error Recovery Strategies

### Strategy 1: Undo Last Operation

**Best for**: Accidental deletions, bulk operations, incorrect updates.

```bash
# View what will be undone
clauxton undo --history

# Undo last operation
clauxton undo
```

**Supported operations**:
- task_add, task_update, task_delete
- kb_add, kb_update, kb_delete
- task_import_yaml

---

### Strategy 2: Restore from Backup

**Best for**: Corrupted files, manual editing mistakes.

```bash
# List available backups
ls -lh .clauxton/backups/

# Restore from backup (manual)
cp .clauxton/backups/tasks.yml.20251021_060000 .clauxton/tasks.yml

# Verify restoration
clauxton task list
```

**Automatic backups created**:
- Before every write operation
- Retention: Last 10 backups per file
- Location: `.clauxton/backups/`

---

### Strategy 3: Partial Import with Skip Mode

**Best for**: Large imports with some invalid tasks.

```bash
# Skip invalid tasks, import valid ones
clauxton task import tasks.yml --on-error skip

# Review skipped tasks
# (returned in JSON response)
```

**Benefits**:
- Valid tasks are imported
- Invalid tasks are reported
- No need to fix everything upfront

---

### Strategy 4: Dry Run Before Import

**Best for**: Validating large YAML files before committing.

```bash
# Validate without importing
clauxton task import tasks.yml --dry-run

# Check validation results
# If successful → run actual import
clauxton task import tasks.yml
```

**What's checked**:
- YAML syntax
- Task structure
- Dependencies
- Circular references
- Validation rules

---

## Troubleshooting Workflow

### Step 1: Read the Error Message

Clauxton errors include:
1. **Error type**: ValidationError, NotFoundError, etc.
2. **Context**: What went wrong
3. **Suggestion**: How to fix it
4. **Commands**: Specific commands to run

**Example**:
```
NotFoundError: Task 'TASK-999' not found.
Available tasks: TASK-001, TASK-002, TASK-003
Suggestion: Check the task ID and try again.
Command: clauxton task list
```

---

### Step 2: Check Recent Operations

```bash
# View operation history
clauxton undo --history

# View recent logs
clauxton logs --limit 20
```

---

### Step 3: Verify Data Integrity

```bash
# List all tasks
clauxton task list

# List all KB entries
clauxton kb list

# Check for orphaned dependencies
clauxton task list --status blocked
```

---

### Step 4: Attempt Recovery

Try recovery strategies in order:

1. **Undo**: `clauxton undo` (if recent operation)
2. **Fix & Retry**: Correct the error and retry
3. **Restore Backup**: Copy from `.clauxton/backups/`
4. **Manual Edit**: Edit YAML files directly (last resort)

---

### Step 5: Verify Fix

```bash
# Verify tasks
clauxton task list
clauxton task next

# Verify KB
clauxton kb search "test"

# Run validation
clauxton task import tasks.yml --dry-run
```

---

## Common Errors & Solutions

### Error: "Clauxton not initialized"

**Message**:
```
Error: Clauxton not initialized. Run 'clauxton init' first.
```

**Solution**:
```bash
clauxton init
```

---

### Error: "Task name cannot be empty"

**Message**:
```
ValidationError: Task name cannot be empty.
```

**Solution**:
```bash
# Provide a name
clauxton task add --name "Setup database"

# Or fix in YAML
tasks:
  - name: "Setup database"  # ✅ Non-empty name
```

---

### Error: "Invalid priority"

**Message**:
```
ValidationError: Invalid priority 'urgent'. Must be: critical, high, medium, low.
```

**Solution**:
```bash
# Use valid priority
clauxton task add --name "Task" --priority high

# Or fix in YAML
priority: high  # ✅ Valid: critical, high, medium, low
```

---

### Error: "Circular dependency detected"

**Message**:
```
CycleDetectedError: Circular dependency detected.
Cycle path: TASK-001 -> TASK-002 -> TASK-001
```

**Solution**:
```bash
# Remove one dependency to break the cycle
clauxton task update TASK-002 --depends-on ""

# Or update in YAML
# Remove TASK-001 from TASK-002's depends_on
```

---

### Error: "Dangerous YAML pattern detected"

**Message**:
```
YAMLSecurityError: Dangerous YAML pattern detected: !!python/object/apply
```

**Solution**:
```yaml
# ❌ Dangerous
tasks:
  - name: !!python/object/apply:os.system ["rm -rf /"]

# ✅ Safe
tasks:
  - name: "Setup environment"
    description: "Install dependencies"
```

---

### Error: "Confirmation required"

**Message**:
```json
{
  "status": "confirmation_required",
  "count": 15,
  "threshold": 10
}
```

**Solution**:
```bash
# Option 1: Confirm and proceed (if using MCP/API)
# Option 2: Skip confirmation
clauxton task import tasks.yml --skip-confirmation

# Option 3: Change confirmation mode
clauxton config set confirmation_mode never
clauxton task import tasks.yml
```

---

### Error: "File not found"

**Message**:
```
FileNotFoundError: tasks.yml not found
```

**Solution**:
```bash
# Check file path
ls tasks.yml

# Use absolute path
clauxton task import /full/path/to/tasks.yml

# Or navigate to directory
cd /path/to/directory
clauxton task import tasks.yml
```

---

### Error: "Threshold must be >= 1"

**Message**:
```
ValidationError: Invalid threshold value: 0. Must be >= 1.
```

**Solution**:
```bash
# Use positive threshold
clauxton config set task_import_threshold 10
```

---

## Prevention Best Practices

### 1. Use Dry Run Before Import

```bash
# Always validate first
clauxton task import tasks.yml --dry-run

# If successful → import
clauxton task import tasks.yml
```

---

### 2. Use Version Control for YAML Files

```bash
# Commit YAML files to git
git add tasks.yml
git commit -m "Add new tasks"

# Easy rollback if needed
git checkout HEAD~1 tasks.yml
```

---

### 3. Use Skip Mode for Large Imports

```bash
# Import valid tasks, skip invalid
clauxton task import large-tasks.yml --on-error skip

# Review skipped tasks
# Fix issues
# Re-import corrected tasks
```

---

### 4. Enable Logging

```bash
# Logs are enabled by default
# View recent operations
clauxton logs --limit 20

# View errors only
clauxton logs --level error
```

---

### 5. Configure Confirmation Mode

```bash
# For team development (strict)
clauxton config set confirmation_mode always

# For individual development (balanced, default)
clauxton config set confirmation_mode auto

# For rapid prototyping (fast)
clauxton config set confirmation_mode never
```

---

### 6. Regular Backups

```bash
# Backups are automatic
# Verify backups exist
ls -lh .clauxton/backups/

# Keep backups in version control (optional)
git add .clauxton/backups/
git commit -m "Backup snapshot"
```

---

## Advanced Error Handling

### Programmatic Error Handling (Python API)

```python
from clauxton.core.task_manager import TaskManager
from clauxton.core.models import ValidationError, NotFoundError
from pathlib import Path

tm = TaskManager(Path.cwd())

try:
    result = tm.import_yaml(yaml_content, on_error="rollback")
    if result["status"] == "confirmation_required":
        # Handle confirmation prompt
        pass
    elif result["status"] == "success":
        print(f"Imported {result['imported']} tasks")
except ValidationError as e:
    print(f"Validation failed: {e}")
except NotFoundError as e:
    print(f"Not found: {e}")
```

---

### MCP Error Handling

MCP tools return structured errors:

```json
{
  "status": "error",
  "error": "ValidationError",
  "message": "Task name cannot be empty",
  "suggestion": "Provide a descriptive task name",
  "command": "clauxton task add --name 'Task name'"
}
```

---

## Getting Help

### 1. Check Documentation

- **This guide**: `docs/ERROR_HANDLING_GUIDE.md`
- **Troubleshooting**: `docs/troubleshooting.md`
- **YAML format**: `docs/YAML_TASK_FORMAT.md`
- **Configuration**: `docs/configuration-guide.md`

### 2. View Logs

```bash
# Recent operations
clauxton logs --limit 50

# Errors only
clauxton logs --level error

# Specific operation
clauxton logs --operation task_import
```

### 3. Check Operation History

```bash
# View recent operations
clauxton undo --history --limit 20
```

### 4. Report Issues

Found a bug? [Report it on GitHub](https://github.com/nakishiyaman/clauxton/issues)

Include:
- Error message (full output)
- Command that caused error
- Clauxton version: `clauxton --version`
- Log output: `clauxton logs --limit 20`

---

## Related Documentation

- **[Troubleshooting Guide](troubleshooting.md)**: Common issues
- **[Configuration Guide](configuration-guide.md)**: Configuration options
- **[YAML Format Guide](YAML_TASK_FORMAT.md)**: YAML specification
- **[Undo Guide](../CLAUDE.md#undo-commands)**: Undo operations
- **[Logging Guide](logging-guide.md)**: Operation logs

---

**Last Updated**: 2025-10-21 (v0.10.0 Week 2 Day 14)
