# Knowledge Base YAML Format

This document describes the structure of `.clauxton/knowledge-base.yml` file.

---

## File Location

```
your-project/
└── .clauxton/
    └── knowledge-base.yml
```

**Permissions**: 600 (rw-------)

---

## Schema Structure

```yaml
version: "1.0"               # KB schema version
project_name: "my-project"   # Project name
project_description: null    # Optional project description

entries:
  - id: KB-YYYYMMDD-NNN      # Unique ID (auto-generated)
    title: "Entry title"     # Max 50 chars
    category: architecture   # One of: architecture, constraint, decision, pattern, convention
    content: |               # Detailed content (max 10,000 chars)
      Multiline content here.
      Can span multiple lines.
    tags:                    # List of tags (lowercase)
      - tag1
      - tag2
    created_at: ISO-8601     # Creation timestamp
    updated_at: ISO-8601     # Last update timestamp
    author: null             # Optional author name
    version: 1               # Entry version (increments on update)
```

---

## Complete Example

```yaml
version: '1.0'
project_name: my-ecommerce-api
project_description: E-commerce platform backend API

entries:
  - id: KB-20251019-001
    title: Use FastAPI framework
    category: architecture
    content: |
      All backend APIs use FastAPI framework.

      Reasons:
      - Async/await support out of the box
      - Automatic OpenAPI docs generation
      - Pydantic integration for request/response validation
      - Excellent performance (on par with NodeJS/Go)

      Version: FastAPI 0.100+
      Documentation: https://fastapi.tiangolo.com/
    tags:
      - backend
      - api
      - fastapi
      - python
    created_at: '2025-10-19T10:30:00'
    updated_at: '2025-10-19T10:30:00'
    author: null
    version: 1

  - id: KB-20251019-002
    title: Write tests before implementation
    category: convention
    content: |
      Team follows Test-Driven Development (TDD).

      Process:
      1. Write failing test first
      2. Implement minimum code to pass
      3. Refactor while keeping tests green

      All new features require:
      - Unit tests (pytest)
      - Integration tests where applicable
      - Minimum 80% code coverage
    tags:
      - testing
      - tdd
      - quality
    created_at: '2025-10-19T11:00:00'
    updated_at: '2025-10-19T11:00:00'
    author: null
    version: 1

  - id: KB-20251019-003
    title: Use PostgreSQL for production
    category: decision
    content: |
      Production database is PostgreSQL 15+.

      Reasons for choosing PostgreSQL:
      - Strong ACID compliance
      - JSON support for flexible schemas
      - Excellent performance for OLTP workloads
      - Wide ecosystem and tooling support

      Connection details stored in environment variables:
      - DATABASE_URL (for connection string)
      - DATABASE_POOL_SIZE (default: 10)
    tags:
      - database
      - postgresql
      - production
    created_at: '2025-10-19T12:00:00'
    updated_at: '2025-10-19T15:30:00'
    author: null
    version: 2

  - id: KB-20251019-004
    title: API must support pagination
    category: constraint
    content: |
      All list endpoints must support pagination to handle large datasets.

      Standard pagination parameters:
      - page: Page number (1-indexed)
      - page_size: Items per page (default: 20, max: 100)

      Response format:
      {
        "items": [...],
        "total": 1000,
        "page": 1,
        "page_size": 20,
        "total_pages": 50
      }
    tags:
      - api
      - pagination
      - performance
    created_at: '2025-10-19T13:00:00'
    updated_at: '2025-10-19T13:00:00'
    author: null
    version: 1

  - id: KB-20251019-005
    title: Repository pattern for data access
    category: pattern
    content: |
      Use Repository pattern for all data access layers.

      Structure:
      - repositories/base.py: BaseRepository[T]
      - repositories/user_repository.py: UserRepository(BaseRepository[User])

      Benefits:
      - Decouples business logic from database
      - Makes testing easier (can mock repositories)
      - Centralizes data access logic

      Example:
      class UserRepository(BaseRepository[User]):
          async def find_by_email(self, email: str) -> Optional[User]:
              ...
    tags:
      - pattern
      - repository
      - architecture
    created_at: '2025-10-19T14:00:00'
    updated_at: '2025-10-19T14:00:00'
    author: null
    version: 1
```

---

## Field Descriptions

### Top Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | KB schema version (currently "1.0") |
| `project_name` | string | Yes | Project name (auto-set from directory name) |
| `project_description` | string \| null | No | Optional project description |
| `entries` | list | Yes | List of Knowledge Base entries |

### Entry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique ID (format: KB-YYYYMMDD-NNN) |
| `title` | string | Yes | Entry title (1-50 chars) |
| `category` | string | Yes | One of: `architecture`, `constraint`, `decision`, `pattern`, `convention` |
| `content` | string | Yes | Detailed content (1-10,000 chars) |
| `tags` | list[string] | No | Tags for categorization (lowercase) |
| `created_at` | string (ISO-8601) | Yes | Creation timestamp |
| `updated_at` | string (ISO-8601) | Yes | Last update timestamp |
| `author` | string \| null | No | Author name (optional, defaults to null for privacy) |
| `version` | integer | Yes | Entry version (starts at 1, increments on update) |

---

## Categories

| Category | Description | Example Use Cases |
|----------|-------------|-------------------|
| `architecture` | System design and architectural decisions | "Use microservices architecture", "Separate frontend and backend" |
| `constraint` | Technical or business constraints | "Must support IE11", "API rate limit: 1000 req/min" |
| `decision` | Important project decisions with rationale | "Use PostgreSQL over MySQL", "Deploy on AWS not GCP" |
| `pattern` | Coding patterns and best practices | "Use Repository pattern", "Singleton for config" |
| `convention` | Team conventions and code style | "Use camelCase for JS", "Write tests first (TDD)" |

---

## Manual Editing

You can manually edit `.clauxton/knowledge-base.yml` if needed:

1. **Backup first**: File is backed up automatically to `.clauxton/knowledge-base.yml.bak` on every write
2. **Validate YAML**: Ensure valid YAML syntax
3. **Follow ID format**: Use `KB-YYYYMMDD-NNN` format for IDs
4. **Respect constraints**: Title ≤50 chars, content ≤10,000 chars
5. **Update timestamps**: Use ISO-8601 format (`YYYY-MM-DDTHH:MM:SS`)

**Note**: Clauxton will validate the file on next read. Invalid entries will cause errors.

---

## Version History

An entry's version is incremented each time it's updated via `clauxton kb update`:

```yaml
# Version 1 (original)
- id: KB-20251019-001
  title: "Original title"
  content: "Original content"
  version: 1
  created_at: '2025-10-19T10:00:00'
  updated_at: '2025-10-19T10:00:00'

# After update (version 2)
- id: KB-20251019-001
  title: "Updated title"
  content: "Updated content with more details"
  version: 2
  created_at: '2025-10-19T10:00:00'  # Unchanged
  updated_at: '2025-10-19T15:30:00'  # Updated
```

**Note**: Phase 0 does not maintain version history. Old versions are overwritten. Full version history will be added in Phase 1.

---

## See Also

- [Quick Start Guide](quick-start.md) - Getting started with Clauxton
- [API Reference](api-reference.md) - Python API documentation
- [Architecture](architecture.md) - System architecture
