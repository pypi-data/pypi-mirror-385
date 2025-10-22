# Quick Start Guide

Get started with Clauxton in 5 minutes.

---

## What is Clauxton?

Clauxton provides **persistent project context** for Claude Code through a Knowledge Base system. Store architecture decisions, constraints, patterns, and conventions that persist across AI sessions.

---

## Installation

### From PyPI (Recommended)

```bash
# Install latest stable version
pip install clauxton

# Verify installation
clauxton --version  # Should show: clauxton, version 0.9.0-beta
```

### From Source (Development)

```bash
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton
pip install -e .
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
- ✅ Unicode support (Japanese, emoji, etc.)

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

## Advanced Usage

### Task Management Workflow

Clauxton provides AI-powered task management with automatic dependency inference.

#### Create Tasks with File Association

```bash
# Add task with file tracking
clauxton task add \
  --name "Implement user authentication" \
  --files "src/auth/login.py,src/auth/session.py" \
  --priority high

# Add dependent task
clauxton task add \
  --name "Add user profile API" \
  --files "src/api/users.py,src/auth/session.py" \
  --priority medium
```

**Auto-dependency inference**: Clauxton detects both tasks touch `src/auth/session.py` and automatically creates dependency.

####Get Next Recommended Task

```bash
clauxton task next
```

**Output**:
```
Recommended next task:

  TASK-001 [pending] (high)
    Name: Implement user authentication
    Files: src/auth/login.py, src/auth/session.py

Reason: High priority, no dependencies, blocks 1 other task
```

**AI recommendation considers**:
- Task priorities (critical > high > medium > low)
- Dependencies (won't suggest blocked tasks)
- Tasks that unblock others (maximize parallel work)

#### Track Progress

```bash
# Start working
clauxton task update TASK-001 --status in_progress

# Complete task
clauxton task update TASK-001 --status completed

# List all tasks
clauxton task list

# Filter by status
clauxton task list --status pending
clauxton task list --priority high
```

**Learn more**: [Task Management Guide](task-management-guide.md)

---

### Bulk Task Import (YAML) - NEW v0.10.0

For creating multiple tasks at once, use YAML import (30x faster than manual creation):

#### Create a YAML file (`tasks.yml`)

```yaml
tasks:
  - name: "Setup FastAPI project"
    description: "Initialize FastAPI with basic structure"
    priority: high
    files_to_edit:
      - main.py
      - requirements.txt
    estimated_hours: 2.5

  - name: "Create database models"
    description: "Define SQLAlchemy models"
    priority: high
    depends_on:
      - TASK-001
    files_to_edit:
      - models/user.py
      - models/post.py
    estimated_hours: 3.0

  - name: "Write API tests"
    priority: medium
    depends_on:
      - TASK-002
    files_to_edit:
      - tests/test_api.py
    estimated_hours: 4.0
```

#### Import tasks

```bash
# Validate first (dry-run)
clauxton task import tasks.yml --dry-run

# Import
clauxton task import tasks.yml
```

**Output**:
```
✓ Imported 3 tasks

  • TASK-001
  • TASK-002
  • TASK-003

📋 Next task to work on:
  TASK-001

  Start working:
    clauxton task update TASK-001 --status in_progress
```

**Features**:
- ✅ Auto-ID generation (TASK-001, TASK-002, etc.)
- ✅ Dependency validation (circular dependency detection)
- ✅ Dry-run mode for validation
- ✅ Skip validation with `--skip-validation` flag
- ✅ All-or-nothing import (fails if any task is invalid)

**Use Cases**:
- Project initialization: Define entire task list upfront
- Sprint planning: Import sprint tasks from template
- Team workflows: Share task definitions via Git
- Claude Code integration: Auto-generate and import tasks

**Learn more**: [YAML Task Format Guide](YAML_TASK_FORMAT.md)

---

### Conflict Detection Workflow

Clauxton predicts file conflicts **before** they occur, helping you avoid merge conflicts and coordination issues.

#### Check Task Conflicts

Before starting work on a task, check if it will conflict with other in-progress tasks:

```bash
clauxton conflict detect TASK-002
```

**Output**:
```
Conflict Detection Report
Task: TASK-002 - Add OAuth support
Files: 2 file(s)

⚠ 1 conflict(s) detected

Conflict 1:
  Task: TASK-001 - Refactor JWT authentication
  Risk: MEDIUM (67%)
  Files: 1 overlapping
  → Complete TASK-001 before starting TASK-002, or coordinate changes
```

**Risk Levels**:
- 🔴 **HIGH** (>70%): Many files overlap, high merge conflict risk
- 🟡 **MEDIUM** (40-70%): Some file overlap, coordination recommended
- 🔵 **LOW** (<40%): Minor overlap, safe to proceed with caution

**Verbose mode** for detailed information:

```bash
clauxton conflict detect TASK-002 --verbose
```

Shows:
- Exact overlapping files
- Line-level analysis (if available)
- Detailed recommendations

#### Get Safe Execution Order

Planning to work on multiple tasks? Get AI-recommended order to minimize conflicts:

```bash
clauxton conflict order TASK-001 TASK-002 TASK-003
```

**Output**:
```
Task Execution Order
Tasks: 3 task(s)

Order respects dependencies and minimizes conflicts

Recommended Order:
1. TASK-001 - Refactor authentication
2. TASK-002 - Add OAuth support
3. TASK-003 - Update user model

💡 Execute tasks in this order to minimize conflicts
```

**With task details**:

```bash
clauxton conflict order TASK-001 TASK-002 --details
```

Shows priority, files to edit, and dependencies for each task.

**How it works**:
- Uses topological sort for dependencies
- Analyzes file overlap between tasks
- Considers task priorities
- Suggests optimal order to reduce conflicts

#### Check File Availability

Before editing files, check if other tasks are currently working on them:

```bash
clauxton conflict check src/api/auth.py
```

**Output when available**:
```
File Availability Check
Files: 1 file(s)

✓ All 1 file(s) available for editing
```

**Output when locked**:
```
File Availability Check
Files: 1 file(s)

⚠ 1 task(s) editing these files

Conflicting Tasks:
  TASK-001 - Refactor JWT authentication
  Status: in_progress
  Editing: 1 of your file(s)

💡 Coordinate with task owners or wait until tasks complete
```

**Check multiple files**:

```bash
clauxton conflict check src/api/auth.py src/models/user.py
```

**Verbose mode** shows per-file status:

```bash
clauxton conflict check src/api/*.py --verbose
```

**Output**:
```
File Status:
  ✗ src/api/auth.py (locked by: TASK-001)
  ✓ src/api/users.py (available)
  ✗ src/api/oauth.py (locked by: TASK-002, TASK-003)
```

#### Common Conflict Detection Workflows

**Workflow 1: Pre-Start Check**
```bash
# 1. Check for conflicts before starting
clauxton conflict detect TASK-002

# 2. If conflicts found, check safe order
clauxton conflict order TASK-001 TASK-002

# 3. Start tasks in recommended order
clauxton task update TASK-001 --status in_progress
```

**Workflow 2: Sprint Planning**
```bash
# 1. List all pending tasks
clauxton task list --status pending

# 2. Get optimal execution order
clauxton conflict order TASK-001 TASK-002 TASK-003 TASK-004

# 3. Assign tasks based on order
```

**Workflow 3: File Coordination**
```bash
# 1. Check if file is available
clauxton conflict check src/api/auth.py

# 2. If locked, see who's editing
clauxton conflict check src/api/auth.py --verbose

# 3. Coordinate with team or wait
```

**Learn more**: [Conflict Detection Guide](conflict-detection.md)

---

### MCP Integration with Claude Code

Clauxton provides 12 MCP tools for seamless Claude Code integration.

#### Setup

Create `.claude-plugin/mcp-servers.json`:

```json
{
  "mcpServers": {
    "clauxton": {
      "command": "python",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

Restart Claude Code to activate.

#### Example: Ask Claude about Architecture

```
You: "How do we handle authentication?"

Claude: [Uses kb_search("authentication")]
Based on KB-20251019-002, we use OAuth 2.0 with JWT tokens...
```

#### Example: Get Task Recommendation

```
You: "What should I work on next?"

Claude: [Uses task_next()]
I recommend TASK-001: "Implement user authentication" (high priority)...
```

**Available MCP Tools**:
- **Knowledge Base**: kb_search, kb_add, kb_list, kb_get, kb_update, kb_delete
- **Task Management**: task_add, task_list, task_get, task_update, task_next, task_delete

**Learn more**: [MCP Server Guide](mcp-server.md)

---

### Real-World Example: Feature Development

**Scenario**: Implementing a new user authentication feature

#### Step 1: Document Decision

```bash
clauxton kb add
# Title: Use OAuth 2.0 with JWT for authentication
# Category: decision
# Content: [Detailed reasoning, alternatives, trade-offs]
# Tags: authentication, oauth, jwt, security
```

#### Step 2: Break Down Tasks

```bash
# Task 1: OAuth flow
clauxton task add \
  --name "Implement OAuth 2.0 flow" \
  --files "src/auth/oauth.py" \
  --priority high \
  --kb-refs KB-20251019-002

# Task 2: JWT handling
clauxton task add \
  --name "Implement JWT token generation" \
  --files "src/auth/jwt.py,src/auth/oauth.py" \
  --priority high

# Task 3: API endpoints
clauxton task add \
  --name "Add authentication API endpoints" \
  --files "src/api/auth.py,src/auth/oauth.py" \
  --priority medium
```

**Result**: Clauxton automatically infers:
- TASK-2 depends on TASK-1 (both touch oauth.py)
- TASK-3 depends on TASK-1 (both touch oauth.py)

#### Step 3: Execute in Order

```bash
# Get recommendation
clauxton task next
# → Suggests TASK-001 (no dependencies, high priority)

# Work on Task 1, update status
clauxton task update TASK-001 --status completed

# Get next
clauxton task next
# → Suggests TASK-002 (dependency met, high priority)
```

#### Step 4: Ask Claude for Help

```
You: "Help me implement the OAuth flow according to our architecture"

Claude: [Uses kb_search("OAuth")]
Based on KB-20251019-002, here's the implementation...
[Generates code following your documented decisions]
```

**Benefits**:
- Architecture decisions preserved
- Tasks executed in safe order
- No merge conflicts from file overlap
- Claude has full project context

---

### Performance Tips

#### Large Knowledge Bases (100+ entries)

TF-IDF search remains fast with 200+ entries. For optimal performance:

```bash
# Use specific queries
clauxton kb search "FastAPI OAuth implementation"  # Good
clauxton kb search "authentication"                 # May return many results

# Use category filters
clauxton kb search "database" --category architecture

# Limit results
clauxton kb search "API" --limit 5
```

#### Task Management at Scale (50+ tasks)

```bash
# Filter by status to see active work
clauxton task list --status in_progress

# Filter by priority for focus
clauxton task list --priority critical --status pending

# Use task next for optimal ordering
clauxton task next  # AI considers all factors
```

---

### Integration Patterns

#### Pre-commit Hook: Sync Knowledge Base

```bash
# .git/hooks/pre-commit
#!/bin/bash
# Auto-add KB entries before commit
if [ -d ".clauxton" ]; then
    git add .clauxton/
fi
```

#### CI/CD: Validate Knowledge Base

```yaml
# .github/workflows/validate-kb.yml
name: Validate Knowledge Base
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check KB format
        run: |
          pip install clauxton
          clauxton kb list  # Validates YAML format
```

---

## Complete Tutorial

For a comprehensive step-by-step guide, see:
- [Tutorial: Building Your First Knowledge Base](tutorial-first-kb.md) (30 minutes)

---

**Ready to preserve your project context?** Start with `clauxton init`!
