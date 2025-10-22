# ADR-001: YAML for Data Storage

**Status**: Accepted
**Date**: 2025-01-15
**Deciders**: Clauxton Core Team

## Context

Clauxton needs a data format for storing:
- Knowledge Base entries (architecture decisions, constraints, patterns)
- Task definitions (name, status, dependencies, files)
- Project metadata (version, configuration)

Requirements:
1. **Human-readable**: Users should be able to read and edit files directly
2. **Git-friendly**: Diffs should be meaningful for version control
3. **Structured**: Support for nested data, lists, and dictionaries
4. **Simple**: No database setup required
5. **Portable**: Cross-platform compatibility

## Decision

Use **YAML** as the primary data storage format for all Clauxton data files.

All data is stored in `.clauxton/` directory:
- `.clauxton/knowledge-base.yml` - KB entries
- `.clauxton/tasks.yml` - Task definitions
- `.clauxton/backups/` - Timestamped YAML backups
- `.clauxton/logs/` - JSON Lines logs (not YAML)

## Consequences

### Positive

1. **Human-Readable**:
   - Users can read and understand files without tools
   - Easy to edit manually in emergencies
   - Clean diffs in version control

2. **Git-Friendly**:
   - Line-based format works well with git
   - Merge conflicts are manageable
   - History is human-readable

3. **No Setup Required**:
   - No database installation
   - No migration scripts
   - Works on any system with Python

4. **Flexibility**:
   - Easy to add new fields
   - Supports complex nested structures
   - Backward compatibility via optional fields

5. **Debugging**:
   - Easy to inspect data
   - Can manually fix corrupted files
   - Clear error messages from PyYAML

### Negative

1. **Performance**:
   - Slower than binary formats for large datasets
   - Full file read/write for every operation
   - Not suitable for >10,000 entries (not a target use case)

2. **Concurrency**:
   - File-level locking only (via atomic writes)
   - No transaction support
   - Race conditions possible (mitigated by atomic writes)

3. **Security**:
   - YAML bombs (alias expansion attacks)
   - Dangerous tags (`!!python`, `!!exec`)
   - **Mitigation**: Use `yaml.safe_load()` only

4. **Schema Enforcement**:
   - YAML itself has no schema validation
   - **Mitigation**: Pydantic models for validation

5. **File Size**:
   - YAML is verbose compared to JSON
   - Larger file sizes (acceptable for target use case)

## Alternatives Considered

### 1. JSON

**Pros**:
- Faster parsing than YAML
- Stricter format (fewer edge cases)
- Native JavaScript support

**Cons**:
- Less human-readable (no comments, strict quotes)
- No native support for dates
- Not as Git-friendly (single-line arrays)

**Why Rejected**: Readability is more important than speed for Clauxton's use case.

### 2. TOML

**Pros**:
- Very human-readable
- Stricter than YAML (fewer gotchas)
- Good for configuration files

**Cons**:
- Limited nested structure support
- Less popular in Python ecosystem
- Not ideal for complex data (tasks with dependencies)

**Why Rejected**: Limited nesting support makes task dependencies awkward.

### 3. SQLite

**Pros**:
- Best performance
- ACID transactions
- SQL query support

**Cons**:
- Binary format (not human-readable)
- Poor Git integration (binary diffs)
- Requires schema migrations
- Overhead for simple use case

**Why Rejected**: Binary format conflicts with Git-friendly requirement.

### 4. Plain Text (Markdown)

**Pros**:
- Most human-readable
- Excellent Git integration
- No parsing required

**Cons**:
- No structure (hard to parse programmatically)
- No validation
- Manual parsing required

**Why Rejected**: Lack of structure makes programmatic access difficult.

## Implementation Notes

### Safety Measures

```python
# ALWAYS use safe_load
import yaml

with open(file_path, "r") as f:
    data = yaml.safe_load(f)  # ✅ Safe
    # data = yaml.load(f)  # ❌ NEVER - allows code execution
```

### Atomic Writes

```python
# Write to temp file, then rename (atomic on POSIX)
temp_path = file_path.with_suffix(".tmp")
with open(temp_path, "w") as f:
    yaml.dump(data, f)
temp_path.replace(file_path)  # Atomic
```

### Backup Strategy

```python
# Automatic backups before overwrites
backup_manager.create_backup(file_path, max_generations=10)
write_yaml(file_path, data)
```

## Future Considerations

1. **Scalability**: If users exceed 1,000 entries, consider:
   - Split files (one file per entry)
   - Index file for fast lookups
   - SQLite migration path

2. **Performance**: If performance becomes an issue:
   - Add in-memory caching
   - Lazy loading
   - Incremental writes

3. **Schema Validation**: Consider adding YAML schema validation (JSON Schema for YAML).

## References

- [YAML Specification](https://yaml.org/spec/1.2.2/)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [YAML Security Best Practices](https://github.com/yaml/yaml-spec/wiki/Security)
- [Architecture Decision Records](https://adr.github.io/)
