# KB Export Guide

## Overview

The KB Export feature allows you to export Knowledge Base entries to Markdown documentation files. Decision entries are exported in ADR (Architecture Decision Record) format, while other categories use standard documentation format.

## Features

- **Category-based export**: One Markdown file per category
- **ADR format for decisions**: Architecture Decision Records with Context and Consequences sections
- **Standard format for other categories**: Clean, readable documentation
- **Unicode support**: Full support for international characters and emoji
- **Automatic directory creation**: Output directory created if it doesn't exist

## Usage

### CLI Command

Export all categories:
```bash
clauxton kb export ./docs/kb
```

Export specific category:
```bash
clauxton kb export ./docs/adr --category decision
```

Short option:
```bash
clauxton kb export ~/project-docs/kb -c architecture
```

### MCP Tool

```python
# Export all categories
result = kb_export_docs(output_dir="./docs/kb")

# Export only decisions
result = kb_export_docs(output_dir="./docs/adr", category="decision")
```

### Python API

```python
from pathlib import Path
from clauxton.core.knowledge_base import KnowledgeBase

kb = KnowledgeBase(Path("."))
stats = kb.export_to_markdown(Path("./docs/kb"))

print(f"Exported {stats['total_entries']} entries to {stats['files_created']} files")
```

## Output Format

### Standard Format (architecture, constraint, pattern, convention)

```markdown
# Architecture

This document contains all architecture entries for this project.

---

## Use FastAPI Framework

**ID**: KB-20251020-001
**Created**: 2025-10-20
**Tags**: `backend`, `api`, `fastapi`

All backend APIs use FastAPI for async support and performance.

---
```

### ADR Format (decision)

```markdown
# Architecture Decision Records

This document contains all architectural decisions made for this project.

---

## PostgreSQL for Production Database

**ID**: KB-20251020-002
**Status**: Accepted
**Date**: 2025-10-20
**Version**: 1
**Tags**: `database`, `postgresql`

### Context

We decided to use PostgreSQL for production due to its reliability and ACID compliance.

### Consequences

_This decision has been implemented and accepted._

---
```

## Use Cases

1. **Documentation Generation**: Export KB to readable Markdown docs for team
2. **ADR Archive**: Export decision entries as Architecture Decision Records
3. **Knowledge Sharing**: Share project context with new team members
4. **Version Control**: Commit exported docs to Git for versioning
5. **Static Site**: Use exported Markdown in documentation sites (MkDocs, etc.)

## File Naming

Files are named by category:
- `architecture.md`
- `decision.md`
- `constraint.md`
- `pattern.md`
- `convention.md`

## Notes

- Entries are sorted by creation date within each file
- Existing files will be overwritten
- Unicode characters are fully supported (UTF-8 encoding)
- Output directory permissions: 755 (readable by all, writable by owner)

## Examples

### Export for Documentation Site

```bash
# Export to MkDocs docs directory
clauxton kb export ./docs/knowledge-base

# Add to mkdocs.yml
nav:
  - Knowledge Base:
    - Architecture: knowledge-base/architecture.md
    - Decisions: knowledge-base/decision.md
```

### Export for Git Repository

```bash
# Export to docs
clauxton kb export ./docs/kb

# Commit to Git
git add docs/kb/
git commit -m "docs: Update knowledge base documentation"
```

### Export ADRs Only

```bash
# Export only architectural decisions
clauxton kb export ./docs/adr --category decision

# Commit ADRs
git add docs/adr/
git commit -m "docs: Add architecture decision records"
```
