# Quick Start Guide

Get started with Clauxton in 5 minutes.

---

## What is Clauxton?

Clauxton provides **persistent project context** for Claude Code through a Knowledge Base system. Store architecture decisions, constraints, patterns, and conventions that persist across AI sessions.

---

## Installation

### From Source (Current)

```bash
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton
pip install -e .
```

### From PyPI (Coming Soon)

```bash
pip install clauxton
```

---

## 5-Minute Tutorial

### 1. Initialize Your Project

Navigate to your project directory and initialize Clauxton:

```bash
cd your-project
clauxton init
```

This creates `.clauxton/` directory with:
- `knowledge-base.yml` - Your Knowledge Base storage
- `.gitignore` - Excludes temporary files

**Output:**
```
✓ Initialized Clauxton
  Location: /path/to/your-project/.clauxton
  Knowledge Base: /path/to/your-project/.clauxton/knowledge-base.yml
```

### 2. Add Your First Entry

Add an architecture decision to your Knowledge Base:

```bash
clauxton kb add
```

You'll be prompted for:
- **Title**: "Use FastAPI framework" (max 50 characters)
- **Category**: Choose `architecture`
- **Content**: "All backend APIs use FastAPI for consistency."
- **Tags** (optional): "backend,api,fastapi"

**Output:**
```
✓ Added entry: KB-20251019-001
  Title: Use FastAPI framework
  Category: architecture
  Tags: backend, api, fastapi
```

### 3. List All Entries

View all entries in your Knowledge Base:

```bash
clauxton kb list
```

**Output:**
```
Knowledge Base Entries (1):

  KB-20251019-001
    Title: Use FastAPI framework
    Category: architecture
    Tags: backend, api, fastapi
```

Filter by category:

```bash
clauxton kb list --category architecture
```

### 4. Search Your Knowledge Base

Clauxton uses **TF-IDF algorithm** for relevance-based search. Results are automatically ranked by how relevant they are to your query.

```bash
clauxton kb search "FastAPI"
```

**Output:**
```
Search Results for 'FastAPI' (1):

  KB-20251019-001
    Title: Use FastAPI framework
    Category: architecture
    Tags: backend, api, fastapi
    Preview: All backend APIs use FastAPI for consistency.
```

**How relevance ranking works:**
- More relevant entries appear first
- Entries with multiple matches rank higher
- Considers keyword frequency and rarity
- Automatically filters common words ("the", "a", "is")

**Search with filters:**

```bash
# Search in specific category
clauxton kb search "API" --category architecture

# Limit results (default: 10)
clauxton kb search "API" --limit 5
```

**Fallback behavior:**
If `scikit-learn` is not installed, Clauxton automatically falls back to simple keyword matching. The search will still work, just with less sophisticated ranking.

> 💡 **Tip**: For better search results, use specific technical terms rather than common words. For example, "FastAPI" will give better results than just "API".

Learn more: [Search Algorithm Documentation](search-algorithm.md)

### 5. Get Entry Details

Retrieve full details of a specific entry:

```bash
clauxton kb get KB-20251019-001
```

**Output:**
```
KB-20251019-001
Title: Use FastAPI framework
Category: architecture
Tags: backend, api, fastapi
Version: 1
Created: 2025-10-19 10:30:00
Updated: 2025-10-19 10:30:00

All backend APIs use FastAPI for consistency.
```

### 6. Update Entries

Update existing entries to keep them current:

```bash
# Update title
clauxton kb update KB-20251019-001 --title "Use FastAPI 0.100+"

# Update content and category
clauxton kb update KB-20251019-001 \
  --content "All backend APIs use FastAPI 0.100+ for async support." \
  --category decision

# Update tags
clauxton kb update KB-20251019-001 --tags "backend,api,fastapi,async"
```

**Output:**
```
✓ Updated entry: KB-20251019-001
  Version: 2
  Updated: 2025-10-19 11:00
```

**Note**: Version number increments automatically on each update.

### 7. Delete Entries

Remove outdated entries:

```bash
# Delete with confirmation
clauxton kb delete KB-20251019-001

# Skip confirmation
clauxton kb delete KB-20251019-001 --yes
```

**Output:**
```
✓ Deleted entry: KB-20251019-001
```

---

## Common Workflows

### Adding Multiple Entries

Add entries for different categories:

```bash
# Architecture decision
clauxton kb add
# Title: Microservices architecture
# Category: architecture
# Content: System uses microservices with API gateway.
# Tags: architecture,microservices

# Technical constraint
clauxton kb add
# Title: Support IE11
# Category: constraint
# Content: Must support Internet Explorer 11.
# Tags: browser,compatibility

# Design pattern
clauxton kb add
# Title: Repository pattern
# Category: pattern
# Content: Use Repository pattern for data access layer.
# Tags: pattern,data,repository
```

### Organizing by Category

Clauxton supports 5 categories:

| Category | Description | Example |
|----------|-------------|---------|
| `architecture` | System design decisions | "Use microservices architecture" |
| `constraint` | Technical/business constraints | "Must support IE11" |
| `decision` | Important decisions with rationale | "Choose PostgreSQL over MySQL" |
| `pattern` | Coding patterns & best practices | "Use Repository pattern" |
| `convention` | Team conventions & code style | "Use camelCase for JavaScript" |

### Searching Effectively

```bash
# Search by keyword
clauxton kb search "database"

# Search in specific category
clauxton kb search "database" --category decision

# Search with tag filter
clauxton kb search "API" --tags backend,rest

# Limit results
clauxton kb search "API" --limit 3
```

---

## What Gets Stored?

Your Knowledge Base is stored in `.clauxton/knowledge-base.yml`:

```yaml
version: '1.0'
project_name: your-project

entries:
  - id: KB-20251019-001
    title: Use FastAPI framework
    category: architecture
    content: |
      All backend APIs use FastAPI for consistency.

      Reasons:
      - Async/await support
      - Automatic OpenAPI docs
      - Excellent performance
    tags:
      - backend
      - api
      - fastapi
    created_at: '2025-10-19T10:30:00'
    updated_at: '2025-10-19T10:30:00'
    version: 1
```

**Features:**
- ✅ Human-readable YAML format
- ✅ Git-friendly (commit to version control)
- ✅ Secure permissions (600 for files, 700 for directories)
- ✅ Automatic backups (.yml.bak)
- ✅ Unicode support (日本語, emoji, etc.)

---

## Tips & Best Practices

### 1. Descriptive Titles

Good titles help with search:
- ❌ "API"
- ✅ "Use FastAPI framework"
- ✅ "RESTful API design principles"

### 2. Use Categories Consistently

- **architecture**: High-level system design
- **constraint**: Hard requirements or limitations
- **decision**: Choices with rationale (why we chose X over Y)
- **pattern**: Reusable code patterns
- **convention**: Team agreements on style/process

### 3. Meaningful Tags

Tags improve searchability:
- Use lowercase
- Be specific: "postgresql" not just "database"
- Include technology names: "react", "typescript", "docker"

### 4. Rich Content

Include context in content:
```markdown
# Good content example
All backend APIs use FastAPI framework.

Reasons:
- Async/await support out of the box
- Automatic OpenAPI documentation
- Pydantic integration for validation
- Performance comparable to NodeJS/Go

Version: FastAPI 0.100+
Documentation: https://fastapi.tiangolo.com/

Decision made: 2025-10-15
Reviewed: 2025-10-19
```

### 5. Commit to Git

Your Knowledge Base is version-controlled:

```bash
git add .clauxton/
git commit -m "docs: Add architecture decisions to Knowledge Base"
git push
```

Team members can pull and have the same context!

---

## Next Steps

- [YAML Format Reference](yaml-format.md) - Complete YAML schema
- [Installation Guide](installation.md) - Detailed installation instructions
- [Architecture](architecture.md) - How Clauxton works
- [Technical Design](technical-design.md) - Implementation details

---

## Troubleshooting

### "Error: .clauxton/ not found"

You haven't initialized Clauxton in this directory:

```bash
clauxton init
```

### "Error: .clauxton/ already exists"

Already initialized. Use `--force` to overwrite:

```bash
clauxton init --force
```

### "No results found"

Your search query didn't match any entries:
- Try broader keywords
- Check spelling
- Try searching without category filter

### Want to see all commands?

```bash
clauxton --help
clauxton kb --help
```

---

**Ready to preserve your project context?** Start with `clauxton init`!
