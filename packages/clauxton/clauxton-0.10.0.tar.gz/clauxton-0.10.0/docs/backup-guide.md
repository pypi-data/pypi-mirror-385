# Backup Management Guide

This guide explains Clauxton's backup system, including automatic backup creation, generation management, and restoration.

## Overview

Clauxton automatically creates timestamped backups of all YAML files (tasks, knowledge base) before any modifications. This ensures data safety and allows you to recover from accidental changes.

**Key Features**:
- **Automatic backups**: Created on every YAML write
- **Timestamped filenames**: `filename_YYYYMMDD_HHMMSS_microseconds.yml`
- **Generation limit**: Keeps latest 10 backups per file (configurable)
- **Automatic cleanup**: Deletes old backups beyond limit
- **Legacy compatibility**: `.bak` files still created

---

## Backup Directory Structure

```
.clauxton/
├── knowledge-base.yml              # Current file
├── knowledge-base.yml.bak          # Legacy backup (most recent)
├── tasks.yml
├── tasks.yml.bak
└── backups/                        # Timestamped backups
    ├── knowledge-base_20251021_143052_123456.yml  (newest)
    ├── knowledge-base_20251021_142030_654321.yml
    ├── knowledge-base_20251021_141015_789012.yml
    ├── ...
    ├── knowledge-base_20251020_153000_345678.yml  (10th generation)
    ├── tasks_20251021_143100_111111.yml
    └── tasks_20251021_143000_222222.yml
```

**Permissions**:
- Backup directory: `700` (owner only)
- Backup files: `600` (owner read/write only)

---

## Automatic Backups

Backups are created automatically whenever you:
- Add/update/delete KB entries
- Add/update/delete tasks
- Import tasks from YAML
- Perform any operation that modifies YAML files

**Example**:
```bash
# Add a KB entry (backup created automatically)
clauxton kb add --title "Use FastAPI" --category architecture

# Result:
# ✓ KB entry added: KB-20251021-001
# ✓ Backup created: .clauxton/backups/knowledge-base_20251021_143052_123456.yml
```

---

## Manual Backup Management

### Using Python API

```python
from pathlib import Path
from clauxton.utils.backup_manager import BackupManager

# Initialize BackupManager
bm = BackupManager(Path(".clauxton/backups"))

# Create a backup
backup = bm.create_backup(Path(".clauxton/tasks.yml"))
print(f"Backup created: {backup}")
# → Backup created: .clauxton/backups/tasks_20251021_143052_123456.yml

# List all backups (newest first)
backups = bm.list_backups(Path(".clauxton/tasks.yml"))
for backup in backups:
    print(f"  - {backup.name}")
# → tasks_20251021_143052_123456.yml
# → tasks_20251021_142030_654321.yml
# → ...

# Get latest backup
latest = bm.get_latest_backup(Path(".clauxton/tasks.yml"))
print(f"Latest: {latest.name if latest else 'None'}")

# Count backups
count = bm.count_backups(Path(".clauxton/tasks.yml"))
print(f"Total backups: {count}")

# Restore a backup
bm.restore_backup(latest, Path(".clauxton/tasks.yml"))
print("Backup restored!")
```

### Using yaml_utils (Integrated)

```python
from pathlib import Path
from clauxton.utils.yaml_utils import write_yaml

data = {"version": "1.0", "tasks": [...]}

# Write with automatic backup (default: 10 generations)
write_yaml(Path(".clauxton/tasks.yml"), data)

# Write with custom generation limit
write_yaml(Path(".clauxton/tasks.yml"), data, max_generations=5)

# Write without backup
write_yaml(Path(".clauxton/tasks.yml"), data, backup=False)
```

---

## Generation Management

### Default Behavior

- **Default limit**: 10 backups per file
- **Automatic cleanup**: Triggered on every backup creation
- **Deletion policy**: Oldest backups deleted first

**Example**:
```python
# Create 12 backups (limit: 10)
for i in range(12):
    data = {"version": "1.0", "count": i}
    write_yaml(Path(".clauxton/tasks.yml"), data)

# Result: Only 10 most recent backups remain
# Deleted: tasks_20251021_140000_*.yml (oldest 2)
```

### Custom Generation Limit

```python
# Keep only 5 backups
write_yaml(Path(".clauxton/tasks.yml"), data, max_generations=5)

# Keep 20 backups
write_yaml(Path(".clauxton/tasks.yml"), data, max_generations=20)

# Manual cleanup
bm.cleanup_old_backups(Path(".clauxton/tasks.yml"), max_generations=3)
```

---

## Restoration

### Restore Latest Backup

```python
from clauxton.utils.backup_manager import BackupManager

bm = BackupManager(Path(".clauxton/backups"))

# Get latest backup
latest = bm.get_latest_backup(Path(".clauxton/tasks.yml"))

if latest:
    # Restore to original file
    bm.restore_backup(latest, Path(".clauxton/tasks.yml"))
    print(f"Restored from {latest.name}")
else:
    print("No backups found")
```

### Restore Specific Backup

```python
# List all backups
backups = bm.list_backups(Path(".clauxton/tasks.yml"))

# Choose a specific backup (e.g., 3rd most recent)
if len(backups) >= 3:
    target_backup = backups[2]
    bm.restore_backup(target_backup, Path(".clauxton/tasks.yml"))
    print(f"Restored from {target_backup.name}")
```

### Restore to Different Location

```python
# Restore to a new file (for inspection)
bm.restore_backup(
    Path(".clauxton/backups/tasks_20251021_143052_123456.yml"),
    Path(".clauxton/tasks_restored.yml")
)
```

---

## Best Practices

### 1. Regular Inspection

Check your backups periodically:

```bash
# List backups
ls -lh .clauxton/backups/

# Count backups by file
ls .clauxton/backups/tasks_* | wc -l
ls .clauxton/backups/knowledge-base_* | wc -l
```

### 2. Version Control Integration

Backup directory can be committed to Git for team collaboration:

```bash
# Add backups to Git (optional)
git add .clauxton/backups/
git commit -m "Add backups for recovery"
```

**Note**: Backups are excluded by default in `.gitignore` to avoid bloat. Only commit if needed.

### 3. Disaster Recovery

Before major operations (e.g., bulk delete):

```python
# Create explicit backup before risky operation
bm = BackupManager(Path(".clauxton/backups"))
bm.create_backup(Path(".clauxton/tasks.yml"))

# Perform risky operation
# ...

# If something went wrong, restore immediately
latest = bm.get_latest_backup(Path(".clauxton/tasks.yml"))
bm.restore_backup(latest, Path(".clauxton/tasks.yml"))
```

### 4. Backup Verification

Verify backups contain expected data:

```python
from clauxton.utils.yaml_utils import read_yaml

# Read backup
backup_data = read_yaml(Path(".clauxton/backups/tasks_20251021_143052_123456.yml"))

# Verify critical data
assert "version" in backup_data
assert "tasks" in backup_data
print(f"Backup contains {len(backup_data['tasks'])} tasks")
```

---

## Troubleshooting

### Issue: Backup Directory Missing

**Symptom**: `FileNotFoundError: .clauxton/backups/`

**Solution**:
```python
# BackupManager creates directory automatically
bm = BackupManager(Path(".clauxton/backups"))  # Creates if missing
```

### Issue: Too Many Backups

**Symptom**: `.clauxton/backups/` has 100+ files

**Solution**:
```python
# Cleanup old backups manually
bm.cleanup_old_backups(Path(".clauxton/tasks.yml"), max_generations=5)
bm.cleanup_old_backups(Path(".clauxton/knowledge-base.yml"), max_generations=5)
```

### Issue: Permission Denied

**Symptom**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
```bash
# Fix permissions
chmod 700 .clauxton/backups
chmod 600 .clauxton/backups/*.yml
```

### Issue: Backup Restoration Failed

**Symptom**: `ValidationError: Failed to restore backup`

**Solution**:
1. Check backup file exists:
   ```bash
   ls -l .clauxton/backups/tasks_*.yml
   ```
2. Verify backup is not corrupted:
   ```python
   data = read_yaml(backup_path)
   print(data)  # Should show valid YAML
   ```
3. Check target directory permissions:
   ```bash
   ls -ld .clauxton/
   ```

---

## Performance

**Backup Creation**: < 100ms (tested with 100-entry files)

**Factors affecting performance**:
- File size (larger files take longer)
- Disk I/O speed
- Number of existing backups (cleanup time)

**Benchmarks**:
- 10 KB file: ~5ms
- 100 KB file: ~20ms
- 1 MB file: ~80ms

---

## Technical Details

### Timestamp Format

- Format: `YYYYMMDD_HHMMSS_microseconds`
- Example: `20251021_143052_123456`
- Ensures unique filenames even with rapid operations

### File Naming Pattern

```
{original_filename}_{timestamp}{original_extension}

Examples:
  tasks.yml → tasks_20251021_143052_123456.yml
  knowledge-base.yml → knowledge-base_20251021_143052_123456.yml
```

### Backup Isolation

Backups are isolated by original filename:
- `tasks.yml` backups: `tasks_*.yml`
- `knowledge-base.yml` backups: `knowledge-base_*.yml`

This allows independent generation management per file.

---

## API Reference

### BackupManager Class

```python
class BackupManager:
    """Manages timestamped backups with generation limit."""

    def __init__(self, backup_dir: Path):
        """Initialize with backup directory."""

    def create_backup(
        self, file_path: Path, max_generations: int = 10
    ) -> Path:
        """Create backup and cleanup old generations."""

    def list_backups(self, file_path: Path) -> List[Path]:
        """List backups (newest first)."""

    def get_latest_backup(self, file_path: Path) -> Path | None:
        """Get most recent backup."""

    def count_backups(self, file_path: Path) -> int:
        """Count backups for a file."""

    def cleanup_old_backups(
        self, file_path: Path, max_generations: int = 10
    ) -> List[Path]:
        """Delete old backups beyond limit."""

    def restore_backup(
        self, backup_path: Path, target_path: Path
    ) -> None:
        """Restore backup to target path."""
```

### yaml_utils Integration

```python
def write_yaml(
    file_path: Path,
    data: Dict[str, Any],
    backup: bool = True,
    max_generations: int = 10,
) -> None:
    """
    Write YAML with automatic backup.

    Args:
        file_path: Path to YAML file
        data: Data to write
        backup: Create backup before writing (default: True)
        max_generations: Max backups to keep (default: 10)
    """
```

---

## See Also

- [Operation History Guide](./operation-history-guide.md) - Undo/rollback functionality
- [Error Handling Guide](./error-handling-guide.md) - Error recovery strategies
- [YAML Format Guide](./yaml-format-guide.md) - YAML file structure

---

**Version**: v0.10.0 (Week 2 Day 10)
**Last Updated**: 2025-10-21
