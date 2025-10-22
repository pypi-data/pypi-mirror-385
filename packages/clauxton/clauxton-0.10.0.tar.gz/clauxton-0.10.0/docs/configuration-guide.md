# Configuration Guide

Complete reference for Clauxton configuration management.

## Table of Contents

- [Overview](#overview)
- [Configuration File](#configuration-file)
- [Confirmation Modes](#confirmation-modes)
- [Confirmation Thresholds](#confirmation-thresholds)
- [CLI Commands](#cli-commands)
- [Use Cases](#use-cases)
- [Troubleshooting](#troubleshooting)

---

## Overview

Clauxton uses a configuration file (`.clauxton/config.yml`) to manage Human-in-the-Loop (HITL) settings. You can customize:

- **Confirmation Mode**: How often to prompt for confirmation (always/auto/never)
- **Confirmation Thresholds**: When to prompt based on operation count

---

## Configuration File

### Location

```
.clauxton/config.yml
```

### Format

```yaml
version: "1.0"
confirmation_mode: auto  # always | auto | never

confirmation_thresholds:
  task_import: 10      # Confirm if importing >= 10 tasks
  task_delete: 5       # Confirm if deleting >= 5 tasks
  kb_delete: 3         # Confirm if deleting >= 3 KB entries
  kb_import: 5         # Confirm if importing >= 5 KB entries
```

### Automatic Creation

The configuration file is created automatically on first use with default values.

---

## Confirmation Modes

### 1. `always` Mode (100% HITL)

**Description**: Confirm **all** write operations, regardless of count.

**Use Case**: Team development, production environments, maximum safety.

**Behavior**:
- Every add/update/delete operation requires confirmation
- No automatic bulk operations
- Strictest workflow

**Set Mode**:
```bash
clauxton config set confirmation_mode always
```

**Example**:
```bash
# Even single task deletion requires confirmation
clauxton task delete TASK-001
# → "Confirm deletion of 1 task? (y/n)"
```

---

### 2. `auto` Mode (75% HITL, **Default**)

**Description**: Confirm operations **only when count exceeds threshold**.

**Use Case**: Individual development, balanced workflow (most common).

**Behavior**:
- Small operations (< threshold): No confirmation
- Large operations (≥ threshold): Confirmation required
- Threshold customizable per operation type

**Set Mode**:
```bash
clauxton config set confirmation_mode auto
```

**Example**:
```bash
# Import 5 tasks: No confirmation (below default threshold of 10)
clauxton task import tasks.yml

# Import 15 tasks: Confirmation required (above threshold)
clauxton task import large-tasks.yml
# → "Confirm import of 15 tasks? (y/n)"
```

---

### 3. `never` Mode (25% HITL)

**Description**: **No confirmation prompts** for any operations.

**Use Case**: Rapid prototyping, personal projects, maximum speed.

**Behavior**:
- All operations execute immediately
- Undo capability available for recovery
- Fastest workflow

**Set Mode**:
```bash
clauxton config set confirmation_mode never
```

**Example**:
```bash
# All operations execute immediately without confirmation
clauxton task import tasks.yml  # ✅ Immediate
clauxton task delete TASK-001   # ✅ Immediate

# Use undo if needed
clauxton undo  # Reverse last operation
```

---

## Confirmation Thresholds

### Default Thresholds

| Operation Type | Default Threshold | Description |
|----------------|-------------------|-------------|
| `task_import` | 10 | Importing ≥10 tasks |
| `task_delete` | 5 | Deleting ≥5 tasks |
| `kb_delete` | 3 | Deleting ≥3 KB entries |
| `kb_import` | 5 | Importing ≥5 KB entries |

### Customizing Thresholds

**Set Threshold**:
```bash
clauxton config set task_import_threshold 20
```

**Get Threshold**:
```bash
clauxton config get task_import_threshold
# Output: 20
```

**Example**:
```bash
# Set stricter threshold for task deletion
clauxton config set task_delete_threshold 3

# Set more lenient threshold for imports
clauxton config set task_import_threshold 50
```

### Custom Operation Types

You can set thresholds for **any operation type** (not limited to defaults):

```bash
clauxton config set my_custom_operation_threshold 15
```

---

## CLI Commands

### `clauxton config set <key> <value>`

Set configuration value.

**Syntax**:
```bash
clauxton config set <key> <value>
```

**Keys**:
- `confirmation_mode` - Set mode (always/auto/never)
- `<operation>_threshold` - Set threshold for operation type

**Examples**:
```bash
# Set confirmation mode
clauxton config set confirmation_mode always

# Set task import threshold
clauxton config set task_import_threshold 20

# Set KB delete threshold
clauxton config set kb_delete_threshold 5
```

**Error Handling**:
```bash
# Invalid mode
clauxton config set confirmation_mode invalid
# → Error: Invalid confirmation mode 'invalid'. Must be 'always', 'auto', or 'never'.

# Invalid threshold (negative)
clauxton config set task_import_threshold -5
# → Error: Invalid threshold value: -5. Must be >= 1.

# Invalid threshold (zero)
clauxton config set task_delete_threshold 0
# → Error: Invalid threshold value: 0. Must be >= 1.

# Non-numeric threshold
clauxton config set task_import_threshold abc
# → Error: Invalid threshold value 'abc'. Must be an integer.
```

---

### `clauxton config get <key>`

Get configuration value.

**Syntax**:
```bash
clauxton config get <key>
```

**Examples**:
```bash
# Get confirmation mode
clauxton config get confirmation_mode
# Output: auto

# Get task import threshold
clauxton config get task_import_threshold
# Output: 10
```

---

### `clauxton config list`

View all configuration values.

**Syntax**:
```bash
clauxton config list
```

**Output**:
```
Clauxton Configuration
========================================
version: 1.0
confirmation_mode: auto

Confirmation Thresholds:
  kb_delete_threshold: 3
  kb_import_threshold: 5
  task_delete_threshold: 5
  task_import_threshold: 10
```

---

## Use Cases

### 1. Team Development (Strict Workflow)

**Scenario**: Shared repository, multiple developers, production data.

**Configuration**:
```bash
clauxton config set confirmation_mode always
```

**Benefits**:
- ✅ Prevents accidental bulk operations
- ✅ Every change is reviewed
- ✅ Maximum safety for production

**Trade-off**:
- ⚠️ More prompts (slower workflow)

---

### 2. Individual Development (Balanced)

**Scenario**: Personal project, frequent iterations, moderate risk.

**Configuration**:
```bash
clauxton config set confirmation_mode auto  # Default
clauxton config set task_import_threshold 15  # Optional: adjust threshold
```

**Benefits**:
- ✅ Small operations are fast (no prompts)
- ✅ Large operations are safe (confirmation)
- ✅ Natural workflow for most developers

**Trade-off**:
- ⚠️ Some operations require confirmation

---

### 3. Rapid Prototyping (Maximum Speed)

**Scenario**: Experimentation, throwaway code, personal learning project.

**Configuration**:
```bash
clauxton config set confirmation_mode never
```

**Benefits**:
- ✅ Zero interruptions
- ✅ Maximum development speed
- ✅ Undo available if mistakes occur

**Trade-off**:
- ⚠️ No safety prompts (must rely on undo)

---

### 4. Mixed Workflow (Custom Thresholds)

**Scenario**: Comfortable with task imports, but cautious about deletions.

**Configuration**:
```bash
clauxton config set confirmation_mode auto
clauxton config set task_import_threshold 50  # Lenient
clauxton config set task_delete_threshold 2   # Strict
```

**Benefits**:
- ✅ Fine-grained control per operation type
- ✅ Customized to your workflow
- ✅ Balanced speed and safety

---

## Troubleshooting

### Config Not Found Error

**Problem**:
```
Error: Clauxton not initialized. Run 'clauxton init' first.
```

**Solution**:
```bash
clauxton init
```

---

### Invalid Config Values

**Problem**: Config file has invalid mode or thresholds.

**Solution**: Clauxton auto-recovers:
- Invalid mode → Resets to `auto` (default)
- Missing thresholds → Merges with defaults

**Manual Fix**:
```bash
# Delete config and recreate
rm .clauxton/config.yml
clauxton config list  # Auto-creates with defaults
```

---

### Config Not Persisting

**Problem**: Changes don't persist across sessions.

**Check File Permissions**:
```bash
ls -la .clauxton/config.yml
# Should be: -rw------- (600)
```

**Fix Permissions**:
```bash
chmod 600 .clauxton/config.yml
```

---

### Unicode Operation Types

**Problem**: Using non-ASCII characters in operation types.

**Solution**: Fully supported! Clauxton handles Unicode correctly:

```bash
clauxton config set task_delete_threshold 10
clauxton config get task_delete_threshold
# Output: 10
```

---

## Configuration Persistence

### Cross-Session Persistence

Configuration is saved to `.clauxton/config.yml` and persists across:
- ✅ Terminal sessions
- ✅ Clauxton CLI invocations
- ✅ MCP server restarts (when MCP integration is added)

### Version Control

**Recommended**: Commit `.clauxton/config.yml` to Git for team consistency.

```bash
git add .clauxton/config.yml
git commit -m "chore: Set confirmation mode to always"
```

**Alternative**: Add to `.gitignore` for per-developer customization.

```bash
echo ".clauxton/config.yml" >> .gitignore
```

---

## Advanced Topics

### Programmatic Access (Python API)

```python
from pathlib import Path
from clauxton.core.confirmation_manager import ConfirmationManager

# Initialize
cm = ConfirmationManager(Path(".clauxton"))

# Get/Set mode
mode = cm.get_mode()  # "auto"
cm.set_mode("always")

# Get/Set thresholds
threshold = cm.get_threshold("task_import")  # 10
cm.set_threshold("task_import", 20)

# Check if confirmation needed
needs_confirm = cm.should_confirm("task_import", 15)  # True
```

---

## Related Documentation

- **[Undo Guide](undo-guide.md)**: Recover from accidental operations
- **[Logging Guide](logging-guide.md)**: Track all operations
- **[CLAUDE.md](../CLAUDE.md)**: Human-in-the-Loop philosophy

---

## Feedback

Found an issue or have a suggestion? [Report it on GitHub](https://github.com/nakishiyaman/clauxton/issues).

---

**Last Updated**: 2025-10-21 (v0.10.0 Week 2 Day 11)
