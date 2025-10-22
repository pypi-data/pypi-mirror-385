# Logging Guide

**Clauxton Structured Logging System** - Complete Guide for Developers and Users

**Status**: ✅ Available in v0.10.0
**Last Updated**: 2025-10-21

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Log Structure](#log-structure)
4. [CLI Usage](#cli-usage)
5. [MCP Tool Usage](#mcp-tool-usage)
6. [Python API Usage](#python-api-usage)
7. [Log Levels](#log-levels)
8. [Operation Types](#operation-types)
9. [Log Rotation](#log-rotation)
10. [Filtering and Querying](#filtering-and-querying)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Overview

Clauxton's logging system provides **structured, persistent logging** for all operations:

### Key Features

- **Daily Log Files**: `.clauxton/logs/YYYY-MM-DD.log` - One file per day
- **JSON Lines Format**: Structured data for easy parsing
- **Automatic Rotation**: Configurable retention (default: 30 days)
- **Rich Filtering**: By operation, level, date range
- **Secure**: 700 permissions for directory, 600 for files
- **Multiple Interfaces**: CLI, MCP tools, Python API

### Use Cases

1. **Debugging**: Review recent operations to troubleshoot issues
2. **Audit Trail**: Track all modifications to KB and tasks
3. **Operation History**: See what Claude Code has done
4. **Error Investigation**: Filter error-level logs
5. **Performance Monitoring**: Track operation timing (metadata)

---

## Quick Start

### Viewing Recent Logs (CLI)

```bash
# Show last 100 entries from past 7 days
clauxton logs

# Show last 20 entries
clauxton logs --limit 20

# Show only errors
clauxton logs --level error

# Show task operations only
clauxton logs --operation task_add

# Show today's logs
clauxton logs --date $(date +%Y-%m-%d)
```

### Viewing Logs (MCP Tool)

```python
# From Claude Code
result = get_recent_logs(limit=10)
print(result["logs"])

# Filter by operation
result = get_recent_logs(operation="task_add", level="error")
```

### Python API

```python
from clauxton.utils.logger import ClauxtonLogger
from pathlib import Path

logger = ClauxtonLogger(Path.cwd())

# Write log
logger.log(
    "task_add",
    "info",
    "Added task TASK-001",
    {"task_id": "TASK-001", "priority": "high"}
)

# Query logs
logs = logger.get_recent_logs(limit=10, operation="task_add")
```

---

## Log Structure

### JSON Lines Format

Each log file contains one JSON object per line:

```json
{
  "timestamp": "2025-10-21T10:30:00.123456",
  "operation": "task_add",
  "level": "info",
  "message": "Added task TASK-001",
  "metadata": {
    "task_id": "TASK-001",
    "priority": "high",
    "estimated_hours": 3.5
  }
}
```

### Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `timestamp` | string | ISO 8601 timestamp | Yes |
| `operation` | string | Operation type (e.g., task_add) | Yes |
| `level` | string | Log level (debug/info/warning/error) | Yes |
| `message` | string | Human-readable message | Yes |
| `metadata` | object | Additional context data | No |

---

## CLI Usage

### Basic Commands

```bash
# View logs
clauxton logs

# With options
clauxton logs --limit 50 --level error --days 30
```

### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--limit` | `-l` | 100 | Max entries to show |
| `--operation` | `-o` | All | Filter by operation type |
| `--level` | | All | Filter by log level |
| `--days` | `-d` | 7 | Days to look back |
| `--date` | | Today | Specific date (YYYY-MM-DD) |
| `--json` | | False | Output in JSON format |

### Examples

#### Show Recent Errors

```bash
clauxton logs --level error --limit 20
```

Output:
```
📋 Showing 3 log entries:

[2025-10-21 10:30:00] ERROR   task_import_yaml    Import failed: Invalid YAML
  └─ error: Duplicate task ID: TASK-001
  └─ file: tasks.yml

[2025-10-21 10:25:00] ERROR   kb_add              Failed to add entry
  └─ error: Title too long (max 50 characters)

[2025-10-21 10:20:00] ERROR   task_add            Validation failed
  └─ error: Invalid priority value
```

#### Show Task Operations

```bash
clauxton logs --operation task_add --days 1
```

#### Export to JSON

```bash
clauxton logs --json > logs-export.json
```

#### View Specific Date

```bash
clauxton logs --date 2025-10-20
```

---

## MCP Tool Usage

### get_recent_logs

**MCP Tool for Claude Code**

```python
def get_recent_logs(
    limit: int = 100,
    operation: Optional[str] = None,
    level: Optional[str] = None,
    days: int = 7
) -> dict
```

#### Parameters

- `limit` - Maximum entries to return (default: 100)
- `operation` - Filter by operation type (optional)
- `level` - Filter by log level (optional)
- `days` - Days to look back (default: 7)

#### Returns

```python
{
    "status": "success",
    "count": 5,
    "logs": [
        {
            "timestamp": "2025-10-21T10:30:00",
            "operation": "task_add",
            "level": "info",
            "message": "Added task TASK-001",
            "metadata": {"task_id": "TASK-001"}
        },
        ...
    ]
}
```

#### Examples

```python
# Get recent errors
logs = get_recent_logs(level="error", limit=10)

# Get today's task operations
logs = get_recent_logs(operation="task_add", days=1)

# Get last 30 days of logs
logs = get_recent_logs(days=30, limit=1000)
```

---

## Python API Usage

### ClauxtonLogger Class

```python
from clauxton.utils.logger import ClauxtonLogger
from pathlib import Path

logger = ClauxtonLogger(Path.cwd())
```

### Methods

#### log()

Write a log entry:

```python
logger.log(
    operation="task_add",
    level="info",
    message="Added task TASK-001",
    metadata={"task_id": "TASK-001", "priority": "high"}
)
```

#### get_recent_logs()

Query recent logs:

```python
logs = logger.get_recent_logs(
    limit=100,
    operation="task_add",
    level="info",
    days=7
)
```

#### get_logs_by_date()

Get logs for specific date:

```python
logs = logger.get_logs_by_date("2025-10-21")
```

#### clear_logs()

Delete all logs:

```python
count = logger.clear_logs()
print(f"Deleted {count} log files")
```

### Example: Custom Logging

```python
from clauxton.utils.logger import ClauxtonLogger
from pathlib import Path

logger = ClauxtonLogger(Path.cwd())

# Log custom operation
logger.log(
    operation="custom_operation",
    level="info",
    message="Custom operation completed",
    metadata={
        "duration_ms": 1234,
        "records_processed": 100
    }
)
```

---

## Log Levels

### Level Hierarchy

| Level | Use Case | CLI Color |
|-------|----------|-----------|
| `debug` | Detailed debugging info | Cyan |
| `info` | General informational messages | Green |
| `warning` | Warning messages (non-blocking) | Yellow |
| `error` | Error messages (failures) | Red |

### Guidelines

- **debug**: Verbose details for troubleshooting
- **info**: Normal operations (default)
- **warning**: Potential issues that don't block execution
- **error**: Failures that prevent operation completion

---

## Operation Types

### Standard Operations

| Operation | Description |
|-----------|-------------|
| `task_add` | Task creation |
| `task_update` | Task modification |
| `task_delete` | Task deletion |
| `task_import_yaml` | Bulk task import |
| `kb_add` | Knowledge Base entry creation |
| `kb_update` | KB entry modification |
| `kb_delete` | KB entry deletion |
| `kb_search` | KB search operation |
| `undo_operation` | Undo/rollback operation |
| `conflict_detect` | Conflict detection |

### Custom Operations

You can log custom operations:

```python
logger.log("custom_sync", "info", "Synced 100 records")
```

---

## Log Rotation

### Automatic Rotation

Logs are automatically rotated before each write operation:

- **Retention**: 30 days (default, configurable)
- **Trigger**: Before each `log()` call
- **Method**: Deletes files older than retention period

### Manual Rotation

```python
# Custom retention (7 days)
logger._rotate_logs(retention_days=7)

# Delete all logs
logger.clear_logs()
```

### Log File Lifecycle

```
Day 0:  Create 2025-10-21.log
Day 1:  Create 2025-10-22.log
Day 30: Create 2025-11-20.log (Day 0 log still exists)
Day 31: Create 2025-11-21.log (Day 0 log deleted automatically)
```

---

## Filtering and Querying

### By Operation

```bash
# CLI
clauxton logs --operation task_add

# MCP
get_recent_logs(operation="task_add")

# Python
logger.get_recent_logs(operation="task_add")
```

### By Level

```bash
# CLI
clauxton logs --level error

# MCP
get_recent_logs(level="error")

# Python
logger.get_recent_logs(level="error")
```

### By Date Range

```bash
# CLI - Last 30 days
clauxton logs --days 30

# CLI - Specific date
clauxton logs --date 2025-10-20

# MCP
get_recent_logs(days=30)

# Python
logger.get_recent_logs(days=30)
```

### Combined Filters

```bash
# CLI
clauxton logs --operation task_add --level error --days 7

# MCP
get_recent_logs(operation="task_add", level="error", days=7)

# Python
logger.get_recent_logs(
    operation="task_add",
    level="error",
    days=7
)
```

---

## Best Practices

### Logging Guidelines

1. **Use Appropriate Levels**
   - `info` for normal operations
   - `error` for failures
   - `warning` for recoverable issues
   - `debug` for detailed troubleshooting

2. **Include Contextual Metadata**
   ```python
   logger.log(
       "task_add",
       "info",
       "Added task",
       {
           "task_id": "TASK-001",
           "priority": "high",
           "estimated_hours": 3.5,
           "user": "admin"
       }
   )
   ```

3. **Write Clear Messages**
   - Good: "Added task TASK-001 with priority high"
   - Bad: "Task added"

4. **Don't Log Sensitive Data**
   - ❌ Passwords, tokens, API keys
   - ❌ Personal information (unless required)
   - ✅ Task IDs, operation types, statuses

5. **Use Consistent Operation Names**
   - Follow naming convention: `noun_verb` (e.g., `task_add`)
   - Use lowercase with underscores

### Performance Considerations

- Logs are written synchronously (minimal overhead)
- Rotation happens before writes (O(n) where n = log files)
- Use appropriate retention periods (30 days default)

---

## Troubleshooting

### No Logs Appearing

**Problem**: `clauxton logs` shows "No logs found"

**Solutions**:
1. Check if `.clauxton/logs/` directory exists
2. Verify logs are being written:
   ```python
   from clauxton.utils.logger import ClauxtonLogger
   logger = ClauxtonLogger(Path.cwd())
   logger.log("test", "info", "Test message")
   ```
3. Check file permissions (should be 600)

### Logs Not Rotating

**Problem**: Old logs not being deleted

**Solutions**:
1. Verify rotation is triggered:
   ```python
   logger._rotate_logs(retention_days=30)
   ```
2. Check for permission errors (logs must be writable)
3. Verify file naming format (YYYY-MM-DD.log)

### Malformed JSON Errors

**Problem**: Logs contain invalid JSON

**Solutions**:
1. Use `ClauxtonLogger.log()` instead of manual writes
2. Validate JSON structure:
   ```bash
   jq . < .clauxton/logs/2025-10-21.log
   ```
3. If corrupted, delete and recreate:
   ```bash
   rm .clauxton/logs/2025-10-21.log
   ```

### Permission Denied

**Problem**: Cannot read/write logs

**Solutions**:
1. Check ownership:
   ```bash
   ls -la .clauxton/logs/
   ```
2. Fix permissions:
   ```bash
   chmod 700 .clauxton/logs
   chmod 600 .clauxton/logs/*.log
   ```

### Large Log Files

**Problem**: Log files consuming too much space

**Solutions**:
1. Reduce retention period:
   ```python
   logger._rotate_logs(retention_days=7)
   ```
2. Clear old logs:
   ```bash
   clauxton logs  # (future: --clear option)
   ```
3. Use `gzip` for archival:
   ```bash
   gzip .clauxton/logs/*.log
   ```

---

## Advanced Usage

### Parsing Logs Programmatically

```python
import json
from pathlib import Path

log_file = Path(".clauxton/logs/2025-10-21.log")

with open(log_file, "r") as f:
    for line in f:
        entry = json.loads(line)
        if entry["level"] == "error":
            print(f"Error: {entry['message']}")
```

### Generating Reports

```bash
# Count operations by type
jq -r '.operation' .clauxton/logs/*.log | sort | uniq -c

# Extract all errors
jq 'select(.level == "error")' .clauxton/logs/*.log

# Calculate operation stats
jq -r '[.operation, .level] | @tsv' .clauxton/logs/*.log | \
  awk '{print $1}' | sort | uniq -c | sort -rn
```

### Integration with External Tools

```bash
# Send to syslog
clauxton logs --json | logger -t clauxton

# Monitor in real-time
tail -f .clauxton/logs/$(date +%Y-%m-%d).log | jq .

# Export to CSV
clauxton logs --json | jq -r \
  '[.timestamp, .operation, .level, .message] | @csv'
```

---

## Summary

Clauxton's logging system provides:

- ✅ **Structured Logging**: JSON Lines format
- ✅ **Multiple Interfaces**: CLI, MCP, Python API
- ✅ **Rich Filtering**: Operation, level, date range
- ✅ **Automatic Rotation**: Configurable retention
- ✅ **Secure**: Owner-only permissions
- ✅ **Production Ready**: 97% test coverage, 47 tests

For more information:
- [Quick Start Guide](quick-start.md)
- [MCP Server Guide](mcp-server.md)
- [CHANGELOG](../CHANGELOG.md)

---

**Need Help?**

- **Issues**: [GitHub Issues](https://github.com/nakishiyaman/clauxton/issues)
- **Documentation**: [docs/](.)
- **Changelog**: [CHANGELOG.md](../CHANGELOG.md)
