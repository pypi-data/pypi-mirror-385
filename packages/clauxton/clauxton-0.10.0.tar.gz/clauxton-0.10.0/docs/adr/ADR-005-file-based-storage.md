# ADR-005: File-Based Storage Architecture

**Status**: Accepted
**Date**: 2025-02-05
**Deciders**: Clauxton Core Team

## Context

Clauxton needs a storage architecture for:
- Knowledge Base entries (hundreds)
- Task definitions (tens)
- Configuration (project metadata)
- Logs (operation history)
- Backups (disaster recovery)

Requirements:
1. **Simplicity**: No database setup
2. **Version Control**: Git-friendly storage
3. **Human-Readable**: Users can read/edit files
4. **Reliability**: Atomic writes, automatic backups
5. **Security**: Secure file permissions

## Decision

Use **file-based storage** with the following structure:

```
.clauxton/
├── knowledge-base.yml       # All KB entries (single file)
├── tasks.yml                # All tasks (single file)
├── backups/                 # Timestamped backups
│   ├── knowledge-base_20250205_120000_123456.yml
│   └── tasks_20250205_120030_654321.yml
└── logs/                    # Operation logs (JSON Lines)
    └── 2025-02-05.log
```

**Design Principles**:
- **Single File Per Entity Type**: All KB entries in one file, all tasks in one file
- **Atomic Writes**: Temp file + rename pattern
- **Automatic Backups**: Before every destructive operation
- **Secure Permissions**: 700 for directories, 600 for files

## Consequences

### Positive

1. **No Setup Required**:
   - No database installation
   - No migration scripts
   - Works immediately

2. **Git Integration**:
   - `.clauxton/` can be versioned
   - Diffs show exactly what changed
   - History is human-readable

3. **Portability**:
   - Copy `.clauxton/` = copy all data
   - No import/export needed
   - Cross-platform compatible

4. **Disaster Recovery**:
   - Automatic timestamped backups
   - Easy to restore (copy backup file)
   - No special tools required

5. **Debugging**:
   - Open files in text editor
   - Manually edit if needed
   - Clear file structure

### Negative

1. **Scalability Limitations**:
   - Full file read/write for every operation
   - Not suitable for >10,000 entries
   - **Mitigation**: Target use case is <1,000 entries

2. **Concurrency Issues**:
   - No proper locking (file-level only)
   - Race conditions possible
   - **Mitigation**: Atomic writes prevent corruption

3. **Memory Usage**:
   - Load entire file into memory
   - ~1MB per 1,000 entries (acceptable)

4. **No Transactions**:
   - Can't atomic update across multiple files
   - **Mitigation**: Single file per entity type reduces issue

5. **Backup Storage**:
   - Backups accumulate disk space
   - **Mitigation**: Automatic rotation (10 generations default)

## Alternatives Considered

### 1. One File Per Entry

**Structure**:
```
.clauxton/
├── kb/
│   ├── KB-20250205-001.yml
│   ├── KB-20250205-002.yml
│   └── ...
└── tasks/
    ├── TASK-001.yml
    └── ...
```

**Pros**:
- No need to load all entries
- Better for very large collections
- Easier to parallelize

**Cons**:
- More complex directory management
- Many small files (filesystem overhead)
- Git diffs are noisier (many files change)
- ID collision risk without locking

**Why Rejected**: Complexity not justified for <1,000 entries.

### 2. SQLite Database

**Structure**:
```
.clauxton/
└── clauxton.db
```

**Pros**:
- Best performance
- ACID transactions
- SQL query support
- Scales to millions of records

**Cons**:
- Binary format (not human-readable)
- Poor Git integration (binary diffs useless)
- Requires schema migrations
- More complex backup/restore

**Why Rejected**: Binary format conflicts with transparency requirement.

### 3. Append-Only Log (Event Sourcing)

**Structure**:
```
.clauxton/
└── events.log
```

**Pros**:
- Never overwrites data
- Complete history
- Easy to audit

**Cons**:
- Requires replay to get current state
- Slow for large histories
- Complex compaction logic

**Why Rejected**: Overkill for current needs.

### 4. Hybrid (SQLite + YAML Export)

**Pros**:
- Fast SQLite for operations
- YAML export for version control

**Cons**:
- Complexity (two sources of truth)
- Sync issues between SQLite and YAML
- Export/import overhead

**Why Rejected**: Too complex.

### 5. JSON Instead of YAML

**Pros**:
- Faster parsing
- Stricter format

**Cons**:
- Less human-readable
- No comments
- See ADR-001 for full comparison

**Why Rejected**: See ADR-001.

## Implementation Notes

### Atomic Write Pattern

```python
def write_yaml(file_path: Path, data: Dict) -> None:
    # 1. Create backup
    if file_path.exists():
        backup_manager.create_backup(file_path)

    # 2. Write to temp file
    temp_path = file_path.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        yaml.dump(data, f)

    # 3. Atomic rename (POSIX guarantees atomicity)
    temp_path.replace(file_path)

    # 4. Set secure permissions
    file_path.chmod(0o600)
```

### Backup Rotation

```python
class BackupManager:
    def create_backup(self, file_path: Path, max_generations: int = 10):
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_path = backup_dir / f"{file_path.stem}_{timestamp}.yml"
        shutil.copy2(file_path, backup_path)

        # Clean up old backups
        backups = sorted(backup_dir.glob(f"{file_path.stem}_*.yml"))
        for old_backup in backups[max_generations:]:
            old_backup.unlink()
```

### Directory Initialization

```python
def init_clauxton_dir(root: Path) -> Path:
    clauxton_dir = root / ".clauxton"
    clauxton_dir.mkdir(exist_ok=True, mode=0o700)

    # Create subdirectories
    (clauxton_dir / "backups").mkdir(exist_ok=True, mode=0o700)
    (clauxton_dir / "logs").mkdir(exist_ok=True, mode=0o700)

    return clauxton_dir
```

### File Permissions

```python
# Directory: 700 (drwx------)
# Only owner can read, write, execute

# Files: 600 (-rw-------)
# Only owner can read, write
```

## Future Considerations

### Migration Path to Database

If file-based storage becomes insufficient:

1. **Export Script**: `clauxton export --format sqlite`
2. **Import Script**: `clauxton import --from .clauxton.db`
3. **Dual Mode**: Support both file and DB backends

**Triggers for Migration**:
- >1,000 entries (performance degradation)
- Concurrent access requirements
- Complex query needs

### Optimization Without Migration

1. **Lazy Loading**: Load entries on-demand (one file per entry)
2. **Index File**: Maintain index for fast lookups
3. **Compression**: Compress large YAML files (gzip)
4. **Caching**: In-memory cache for frequently accessed data

### Backup Strategies

1. **Remote Backup**: Sync `.clauxton/` to cloud storage
2. **Compression**: Compress old backups automatically
3. **Incremental**: Only backup changed entries (requires per-entry files)

## Performance Characteristics

| Operation       | File I/O | Memory   | Time (100 entries) |
|-----------------|----------|----------|--------------------|
| Load KB         | 1 read   | ~100KB   | ~10ms              |
| Save KB         | 1 write  | ~100KB   | ~20ms              |
| Search KB       | 1 read   | ~100KB   | ~30ms (TF-IDF)     |
| Add Entry       | 1 r+w    | ~100KB   | ~40ms (r+validate+w)|
| Create Backup   | 1 copy   | ~100KB   | ~10ms              |

**Bottleneck**: File I/O for every operation (acceptable for target use case).

## Disaster Recovery

### Backup Recovery

```bash
# List available backups
ls -la .clauxton/backups/

# Restore from backup
cp .clauxton/backups/knowledge-base_20250205_120000_123456.yml \
   .clauxton/knowledge-base.yml
```

### Git Recovery

```bash
# Restore from git history
git checkout HEAD~1 -- .clauxton/knowledge-base.yml
```

### Manual Recovery

```bash
# Edit YAML directly
vim .clauxton/knowledge-base.yml

# Validate YAML
python -c "import yaml; yaml.safe_load(open('.clauxton/knowledge-base.yml'))"
```

## Security Considerations

1. **File Permissions**: 700/600 (owner-only access)
2. **Backup Permissions**: Same as main files
3. **No Encryption**: User responsibility (use encrypted filesystem)
4. **No Remote Access**: Local file access only

## References

- [Atomic File Operations](https://rcrowley.org/2010/01/06/things-unix-can-do-atomically.html)
- [File Permissions Best Practices](https://wiki.archlinux.org/title/File_permissions_and_attributes)
- [Git-Friendly File Formats](https://about.gitlab.com/blog/2020/10/06/git-lfs-in-gitlab/)
- [YAML Performance](https://pyyaml.org/wiki/PyYAMLDocumentation)
