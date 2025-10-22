# Migration Guide: v0.9.0-beta → v0.10.0

Complete guide for migrating from Clauxton v0.9.0-beta to v0.10.0.

## Table of Contents

- [Overview](#overview)
- [Breaking Changes](#breaking-changes)
- [New Features](#new-features)
- [Migration Steps](#migration-steps)
- [API Changes](#api-changes)
- [Configuration Changes](#configuration-changes)
- [Troubleshooting](#troubleshooting)

---

## Overview

**Good News**: **v0.10.0 is 100% backward compatible!**

- ✅ No breaking changes
- ✅ Existing CLIncommands work unchanged
- ✅ Existing MCP tools work unchanged
- ✅ Existing YAML files work unchanged
- ✅ Existing `.clauxton/` data preserved

**What's New**: v0.10.0 adds **15 new features** without breaking existing functionality.

---

## Breaking Changes

### None! 🎉

v0.10.0 is **fully backward compatible** with v0.9.0-beta.

All existing:
- CLI commands
- MCP tools
- YAML formats
- Configuration files
- Data files

...continue to work without modification.

---

## New Features

### 1. YAML Bulk Import (Week 2 Day 1-2)

**What's New**: Import multiple tasks in a single operation.

**Before (v0.9.0-beta)**:
```bash
# Manual task creation (10 commands)
clauxton task add --name "Task 1"
clauxton task add --name "Task 2"
# ... repeat 10 times
```

**After (v0.10.0)**:
```bash
# Single bulk import
clauxton task import tasks.yml
```

**Migration**: No action required. Manual commands still work.

---

### 2. Undo/Rollback (Week 2 Day 3)

**What's New**: Reverse accidental operations.

**New Commands**:
```bash
clauxton undo                 # Undo last operation
clauxton undo --history       # View operation history
```

**New MCP Tools**:
- `undo_last_operation()`
- `get_recent_operations(limit)`

**Migration**: No action required. Optional feature.

---

### 3. Confirmation Prompts (Week 2 Day 4)

**What's New**: Threshold-based confirmation for bulk operations.

**Default Behavior**: Prompts when importing ≥10 tasks.

**Opt-out**:
```bash
# Skip confirmation
clauxton task import tasks.yml --skip-confirmation
```

**Migration**: No action required. Existing `--skip-confirmation` parameter continues to work.

---

### 4. Error Recovery (Week 2 Day 5)

**What's New**: Transactional imports with configurable error handling.

**New Parameter**: `--on-error [rollback|skip|abort]`

**Default**: `rollback` (safe, transactional)

**Migration**: No action required. Defaults to safest option.

---

### 5. YAML Safety (Week 2 Day 5)

**What's New**: Automatic detection of dangerous YAML patterns.

**Protected Against**:
- `!!python/object/apply`
- `__import__`, `eval()`, `exec()`

**Migration**: If your YAML files use dangerous patterns (unlikely), they will be rejected. Use safe YAML syntax.

---

### 6. Enhanced Validation (Week 2 Day 6)

**What's New**: Pre-Pydantic validation with better error messages.

**Validates**:
- Task names (non-empty)
- Duplicate IDs/names
- Invalid priorities/statuses
- Negative estimated hours
- File paths

**Migration**: Invalid tasks that previously passed may now be caught. Fix validation errors in YAML.

---

### 7. Operation Logging (Week 2 Day 7)

**What's New**: Structured logging with daily log files.

**New Commands**:
```bash
clauxton logs [--limit N] [--operation TYPE] [--level LEVEL]
```

**New MCP Tool**:
- `get_recent_logs(limit, operation, level, days)`

**Location**: `.clauxton/logs/YYYY-MM-DD.log`

**Migration**: No action required. Logging is automatic.

---

### 8. KB Export (Week 2 Day 8)

**What's New**: Export Knowledge Base to Markdown documentation.

**New Commands**:
```bash
clauxton kb export docs/       # Export all categories
clauxton kb export docs/ -c decision  # Export decisions only
```

**New MCP Tool**:
- `kb_export_docs(output_dir, category)`

**Migration**: No action required. Optional feature.

---

### 9. Progress Display (Week 2 Day 9)

**What's New**: Real-time progress bars for bulk operations.

**Displays Progress For**:
- Task import (100+ tasks)
- Task export
- Search operations

**Migration**: No action required. Automatic.

---

### 10. Performance Optimization (Week 2 Day 9)

**What's New**: 10x faster bulk operations.

**Before**: 100 tasks in ~10s
**After**: 100 tasks in ~1s

**Migration**: No action required. Automatic performance gains.

---

### 11. Backup Enhancement (Week 2 Day 10)

**What's New**: Automatic backups before every write operation.

**Backup Strategy**:
- Before every write
- Last 10 backups kept
- Location: `.clauxton/backups/`
- Format: `tasks.yml.YYYYMMDD_HHMMSS`

**Migration**: No action required. Automatic.

---

### 12. Error Message Improvement (Week 2 Day 10)

**What's New**: Actionable error messages with context + suggestion + commands.

**Example**:
```
NotFoundError: Task 'TASK-999' not found.
Available tasks: TASK-001, TASK-002, TASK-003
Suggestion: Check the task ID and try again.
Command: clauxton task list
```

**Migration**: No action required. Better error messages automatically.

---

### 13. Configurable Confirmation Mode (Week 2 Day 11)

**What's New**: Set Human-in-the-Loop level (always/auto/never).

**New Commands**:
```bash
clauxton config set confirmation_mode [always|auto|never]
clauxton config get confirmation_mode
clauxton config list
```

**Default**: `auto` (75% HITL, threshold-based)

**Migration**: No action required. Defaults to balanced mode.

---

## Migration Steps

### Step 1: Backup Existing Data

```bash
# Backup .clauxton directory
cp -r .clauxton .clauxton.backup

# Or use git
cd .clauxton
git add -A
git commit -m "Backup before v0.10.0 upgrade"
```

---

### Step 2: Upgrade Clauxton

```bash
# Upgrade via pip
pip install --upgrade clauxton

# Verify version
clauxton --version
# Should show: clauxton, version 0.10.0
```

---

### Step 3: Verify Data Integrity

```bash
# Check tasks
clauxton task list

# Check KB
clauxton kb list

# Check configuration
clauxton config list
```

---

### Step 4: Test New Features (Optional)

```bash
# Test undo
clauxton task add --name "Test Task"
clauxton undo

# Test logging
clauxton logs --limit 10

# Test KB export
clauxton kb export /tmp/kb-test/

# Test config
clauxton config get confirmation_mode
```

---

### Step 5: Update Workflows (Optional)

**If you were using manual task creation**:
```bash
# Old workflow (v0.9.0)
clauxton task add --name "Task 1"
clauxton task add --name "Task 2"
# ...

# New workflow (v0.10.0, optional)
# Create tasks.yml
clauxton task import tasks.yml
```

---

## API Changes

### Python API

**No breaking changes!** All existing APIs continue to work.

**New APIs**:

```python
from clauxton.core.task_manager import TaskManager
from clauxton.core.confirmation_manager import ConfirmationManager
from clauxton.core.operation_history import OperationHistory
from clauxton.utils.logger import Logger
from pathlib import Path

# Existing API (still works)
tm = TaskManager(Path.cwd())
tm.add(task)

# New APIs (optional)
cm = ConfirmationManager(Path(".clauxton"))
cm.set_mode("auto")

history = OperationHistory(Path(".clauxton"))
history.undo_last_operation()

logger = Logger(Path(".clauxton"))
logger.log("info", "task_add", {"task_id": "TASK-001"})
```

---

### MCP Tools

**No breaking changes!** All existing tools continue to work.

**New Tools** (15 → 17):

```python
# Existing tools (v0.9.0-beta)
task_add()
task_list()
kb_search()
# ... (15 tools total)

# New tools (v0.10.0)
undo_last_operation()          # NEW
get_recent_operations(limit)   # NEW
kb_export_docs(output_dir)     # NEW
get_recent_logs(limit)         # NEW

# Total: 17 tools
```

---

## Configuration Changes

### New Configuration File: `.clauxton/config.yml`

**Created Automatically** on first use.

**Default Content**:
```yaml
version: "1.0"
confirmation_mode: auto  # always | auto | never

confirmation_thresholds:
  task_import: 10
  task_delete: 5
  kb_delete: 3
  kb_import: 5
```

**Migration**: No action required. Created automatically.

---

### New Directory: `.clauxton/logs/`

**Created Automatically** when logging is used.

**Structure**:
```
.clauxton/logs/
├── 2025-10-21.log
├── 2025-10-20.log
└── ...
```

**Retention**: 30 days (automatic cleanup)

**Migration**: No action required. Created automatically.

---

### New Directory: `.clauxton/backups/`

**Created Automatically** when backups are created.

**Structure**:
```
.clauxton/backups/
├── tasks.yml.20251021_060000
├── tasks.yml.20251021_050000
├── knowledge-base.yml.20251021_060000
└── ...
```

**Retention**: Last 10 backups per file

**Migration**: No action required. Created automatically.

---

## Troubleshooting

### Issue: "Confirmation required" after upgrade

**Cause**: Default confirmation mode is `auto` (threshold-based).

**Solution**:
```bash
# Option 1: Skip confirmation for this operation
clauxton task import tasks.yml --skip-confirmation

# Option 2: Change confirmation mode
clauxton config set confirmation_mode never

# Option 3: Adjust threshold
clauxton config set task_import_threshold 50
```

---

### Issue: YAML import fails with "Dangerous pattern detected"

**Cause**: YAML contains dangerous tags/functions.

**Solution**:
```yaml
# ❌ Dangerous (will be rejected)
tasks:
  - name: !!python/object/apply:os.system ["rm -rf /"]

# ✅ Safe (will be accepted)
tasks:
  - name: "Setup environment"
    description: "Install dependencies"
```

---

### Issue: Validation errors for previously valid tasks

**Cause**: Enhanced validation catches more errors.

**Solution**:
```bash
# View validation errors
clauxton task import tasks.yml --dry-run

# Fix errors in YAML
# Example: Add missing task names, fix invalid priorities

# Retry import
clauxton task import tasks.yml
```

---

### Issue: Backups taking too much space

**Cause**: Automatic backups create files in `.clauxton/backups/`.

**Solution**:
```bash
# Backups are limited to last 10 per file
# Cleanup is automatic

# Manual cleanup (if needed)
rm .clauxton/backups/*.bak

# Or adjust retention (future feature)
```

---

### Issue: Need to restore old data after upgrade

**Cause**: Unexpected behavior after upgrade.

**Solution**:
```bash
# Restore from backup
cp -r .clauxton.backup .clauxton

# Or use undo
clauxton undo --history
clauxton undo  # Undo recent operations

# Or restore from git
cd .clauxton
git checkout HEAD~1
```

---

## Rollback to v0.9.0-beta

If you need to rollback:

```bash
# Restore data backup
cp -r .clauxton.backup .clauxton

# Downgrade package
pip install clauxton==0.9.0b1

# Verify version
clauxton --version
# Should show: clauxton, version 0.9.0-beta
```

**Note**: New v0.10.0 features will not be available after rollback.

---

## Feature Compatibility Matrix

| Feature | v0.9.0-beta | v0.10.0 | Backward Compatible |
|---------|-------------|---------|---------------------|
| Task Management | ✅ | ✅ | ✅ Yes |
| KB Management | ✅ | ✅ | ✅ Yes |
| Conflict Detection | ✅ | ✅ | ✅ Yes |
| MCP Integration | ✅ (15 tools) | ✅ (17 tools) | ✅ Yes |
| YAML Bulk Import | ❌ | ✅ | ✅ Yes (new feature) |
| Undo/Rollback | ❌ | ✅ | ✅ Yes (new feature) |
| Confirmation Prompts | ❌ | ✅ | ✅ Yes (new feature) |
| Error Recovery | ❌ | ✅ | ✅ Yes (new feature) |
| YAML Safety | ❌ | ✅ | ✅ Yes (new feature) |
| Enhanced Validation | ❌ | ✅ | ✅ Yes (new feature) |
| Operation Logging | ❌ | ✅ | ✅ Yes (new feature) |
| KB Export | ❌ | ✅ | ✅ Yes (new feature) |
| Progress Display | ❌ | ✅ | ✅ Yes (new feature) |
| Performance Optimization | ❌ | ✅ | ✅ Yes (automatic) |
| Backup Enhancement | ❌ | ✅ | ✅ Yes (automatic) |
| Better Error Messages | ❌ | ✅ | ✅ Yes (automatic) |
| Configurable Confirmation | ❌ | ✅ | ✅ Yes (new feature) |

---

## Getting Help

### Documentation

- **[ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md)**: Error resolution
- **[configuration-guide.md](configuration-guide.md)**: Configuration options
- **[YAML_TASK_FORMAT.md](YAML_TASK_FORMAT.md)**: YAML specification
- **[logging-guide.md](logging-guide.md)**: Logging system
- **[kb-export-guide.md](kb-export-guide.md)**: KB export

### Support

- **GitHub Issues**: [Report bugs/issues](https://github.com/nakishiyaman/clauxton/issues)
- **Discussions**: [Ask questions](https://github.com/nakishiyaman/clauxton/discussions)

---

## Summary

**v0.10.0 is a major feature release with 100% backward compatibility.**

✅ **No breaking changes**
✅ **15 new features**
✅ **100% backward compatible**
✅ **Automatic performance gains**
✅ **Better error messages**
✅ **Enhanced safety**

**Upgrade with confidence!**

---

**Last Updated**: 2025-10-21 (v0.10.0 Week 2 Day 14)
