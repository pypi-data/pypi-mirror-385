# Tutorial: Building Your First Knowledge Base

**Time**: 30 minutes
**Level**: Beginner
**Prerequisites**: Python 3.11+, basic command line knowledge

---

## What You'll Learn

By the end of this tutorial, you'll be able to:
- ✅ Install and set up Clauxton in your project
- ✅ Create and manage Knowledge Base entries
- ✅ Search with TF-IDF relevance ranking
- ✅ Create and track tasks with dependencies
- ✅ Integrate Clauxton with Claude Code via MCP

---

## Introduction (2 minutes)

### What is Clauxton?

Clauxton provides **persistent project context** for AI-assisted development. It solves three key problems:

1. **Session Context Loss**: AI forgets your architecture decisions between sessions
2. **Manual Dependency Tracking**: You manually manage task dependencies
3. **Post-hoc Conflict Detection**: You discover conflicts after they happen

### How Clauxton Helps

**Knowledge Base**: Store architecture decisions, constraints, patterns, and conventions that persist across AI sessions.

**Task Management**: Automatic dependency inference from file overlap, AI-powered task recommendations.

**TF-IDF Search**: Find relevant context quickly, even with 200+ entries.

---

## Step 1: Installation & Setup (2 minutes)

### Install from PyPI

```bash
# Install latest stable version
pip install clauxton

# Verify installation
clauxton --version
```

**Expected output**:
```
clauxton, version 0.8.0
```

### Initialize Your Project

Navigate to your project directory:

```bash
cd your-project
clauxton init
```

**Output**:
```
✓ Initialized Clauxton
  Location: /path/to/your-project/.clauxton
  Knowledge Base: /path/to/your-project/.clauxton/knowledge-base.yml
```

**What happened**:
- Created `.clauxton/` directory
- Created `knowledge-base.yml` (empty, ready for entries)
- Added `.gitignore` for temporary files

---

## Step 2: Understanding Categories (2 minutes)

Clauxton organizes knowledge into 5 categories:

| Category | Purpose | Example |
|----------|---------|---------|
| `architecture` | System design decisions | "Use microservices architecture" |
| `constraint` | Technical/business limits | "Must support offline mode" |
| `decision` | Important choices with rationale | "Chose PostgreSQL over MongoDB" |
| `pattern` | Coding patterns and practices | "Use Repository pattern for data access" |
| `convention` | Team conventions and style | "Use camelCase for variables" |

**Why categories matter**:
- Filter searches by category
- Organize knowledge logically
- Help AI understand context type

---

## Step 3: Add Your First Entry (3 minutes)

### Interactive Entry Creation

```bash
clauxton kb add
```

You'll be prompted for:

**1. Title** (max 50 characters):
```
Use FastAPI framework for backend APIs
```

**2. Category** (choose from 5):
```
architecture
```

**3. Content** (detailed description):
```
All backend APIs will use FastAPI framework.

Reasoning:
- Async/await support for high performance
- Automatic OpenAPI documentation generation
- Excellent type hints integration with Pydantic
- Strong ecosystem and community

Alternatives considered:
- Flask: Lacks async support, less modern
- Django: Too heavyweight for our use case

Trade-offs:
- Smaller ecosystem than Flask/Django
- Team learning curve (mitigated by good docs)

Decision date: 2025-10-19
```

**4. Tags** (optional, comma-separated):
```
backend, api, fastapi, framework
```

**Output**:
```
✓ Added entry: KB-20251019-001
  Title: Use FastAPI framework for backend APIs
  Category: architecture
  Tags: backend, api, fastapi, framework
```

### Understanding Entry IDs

Format: `KB-YYYYMMDD-NNN`
- `KB`: Knowledge Base prefix
- `20251019`: Creation date (2025-10-19)
- `001`: Sequential number (1st entry of the day)

---

## Step 4: Add More Entries (5 minutes)

Let's add a few more entries to demonstrate search:

### Entry 2: Authentication Decision

```bash
clauxton kb add
```

**Details**:
- Title: `Use OAuth 2.0 with JWT tokens`
- Category: `decision`
- Content:
```
Authentication will use OAuth 2.0 flow with JWT (JSON Web Tokens).

Reasons:
- Industry standard for API authentication
- Stateless (no server-side sessions)
- JWT payload can include user metadata
- Works across microservices

Implementation:
- Access tokens: 15 min expiry
- Refresh tokens: 7 day expiry
- RS256 signing algorithm

Security considerations:
- Store refresh tokens securely (httpOnly cookies)
- Rotate signing keys quarterly
- Implement token revocation list

Related: KB-20251019-001 (FastAPI has excellent OAuth support)
```
- Tags: `authentication, oauth, jwt, security`

---

### Entry 3: Database Constraint

```bash
clauxton kb add
```

**Details**:
- Title: `PostgreSQL 15+ required for production`
- Category: `constraint`
- Content:
```
Production environment MUST use PostgreSQL 15 or higher.

Requirements:
- Strong ACID guarantees needed for financial transactions
- JSON/JSONB support for flexible schemas
- Row-level security (RLS) for multi-tenancy

Constraints:
- Cannot use SQLite in production (dev/test only)
- Must maintain backward compatibility to PostgreSQL 15
- Migration scripts must be tested on PostgreSQL 15

Deployment:
- Use managed service (AWS RDS, GCP Cloud SQL)
- Minimum instance: db.t3.medium (2 vCPU, 4 GB RAM)
```
- Tags: `database, postgresql, constraint, production`

---

### Entry 4: Code Convention

```bash
clauxton kb add
```

**Details**:
- Title: `Use Google-style docstrings`
- Category: `convention`
- Content:
```
All Python functions/classes MUST use Google-style docstrings.

Format:
\"\"\"
Brief description.

Detailed description (optional).

Args:
    param1: Description
    param2: Description

Returns:
    Description

Raises:
    ExceptionType: When this happens
\"\"\"

Tools:
- VSCode extension: autoDocstring
- Linter: pydocstyle with Google convention

Examples: See docs/code-style-examples.md
```
- Tags: `python, docstring, convention, code-style`

---

## Step 5: List All Entries (1 minute)

### View All Knowledge

```bash
clauxton kb list
```

**Output**:
```
Knowledge Base Entries (4):

  KB-20251019-001
    Title: Use FastAPI framework for backend APIs
    Category: architecture
    Tags: backend, api, fastapi, framework

  KB-20251019-002
    Title: Use OAuth 2.0 with JWT tokens
    Category: decision
    Tags: authentication, oauth, jwt, security

  KB-20251019-003
    Title: PostgreSQL 15+ required for production
    Category: constraint
    Tags: database, postgresql, constraint, production

  KB-20251019-004
    Title: Use Google-style docstrings
    Category: convention
    Tags: python, docstring, convention, code-style
```

### Filter by Category

```bash
# Only architecture decisions
clauxton kb list --category architecture

# Only constraints
clauxton kb list --category constraint
```

---

## Step 6: Search with TF-IDF (3 minutes)

### Simple Search

```bash
clauxton kb search "FastAPI"
```

**Output** (ranked by relevance):
```
Search Results for 'FastAPI' (2):

  1. KB-20251019-001 (score: 0.95)
    Title: Use FastAPI framework for backend APIs
    Category: architecture
    Tags: backend, api, fastapi, framework
    Preview: All backend APIs will use FastAPI framework...

  2. KB-20251019-002 (score: 0.32)
    Title: Use OAuth 2.0 with JWT tokens
    Category: decision
    Tags: authentication, oauth, jwt, security
    Preview: ...Related: KB-20251019-001 (FastAPI has excellent OAuth support)
```

**Why this ranking?**
- Entry 1: "FastAPI" appears in title and multiple times in content → high score (0.95)
- Entry 2: "FastAPI" appears once in "Related" note → low score (0.32)

---

### Multi-word Search

```bash
clauxton kb search "authentication security"
```

**Output**:
```
Search Results for 'authentication security' (2):

  1. KB-20251019-002 (score: 0.88)
    Title: Use OAuth 2.0 with JWT tokens
    Category: decision
    Tags: authentication, oauth, jwt, security

  2. KB-20251019-003 (score: 0.15)
    Title: PostgreSQL 15+ required for production
    Category: constraint
    Tags: database, postgresql, constraint, production
```

**Why this ranking?**
- Entry 2: Both "authentication" and "security" appear frequently → high score
- Entry 3: "security" mentioned once (RLS feature) → low score

---

### Search with Filters

```bash
# Only search in architecture category
clauxton kb search "API" --category architecture

# Limit to top 3 results
clauxton kb search "python" --limit 3
```

---

### How TF-IDF Works (Understanding Relevance)

**TF-IDF** = Term Frequency × Inverse Document Frequency

**Term Frequency (TF)**:
- How often the search term appears in this entry
- More appearances = more relevant

**Inverse Document Frequency (IDF)**:
- How rare the term is across all entries
- Rare terms (like "FastAPI") are more valuable than common terms (like "use")

**Result**:
- Entries with multiple rare search terms rank highest
- Common words ("the", "a", "is") are automatically filtered out

**Learn more**: [Search Algorithm Documentation](search-algorithm.md)

---

## Step 7: Get Entry Details (1 minute)

```bash
clauxton kb get KB-20251019-001
```

**Output**:
```
Entry: KB-20251019-001

Title: Use FastAPI framework for backend APIs
Category: architecture
Tags: backend, api, fastapi, framework

Content:
All backend APIs will use FastAPI framework.

Reasoning:
- Async/await support for high performance
- Automatic OpenAPI documentation generation
...

Metadata:
  Created: 2025-10-19 10:30:00
  Updated: 2025-10-19 10:30:00
  Version: 1
```

---

## Step 8: Update an Entry (2 minutes)

### Update Title

```bash
clauxton kb update KB-20251019-001 \
  --title "Use FastAPI 0.100+ for all backend APIs"
```

### Update Content

```bash
clauxton kb update KB-20251019-001 \
  --content "All backend APIs will use FastAPI 0.100 or higher.

Updated reasoning:
- Version 0.100 includes critical performance improvements
- Backward compatible with 0.9x
- Migration guide: docs/fastapi-upgrade.md"
```

### Update Multiple Fields

```bash
clauxton kb update KB-20251019-001 \
  --category decision \
  --tags "backend,api,fastapi,framework,v0.100"
```

**Version Management**:
- Each update increments version number
- Created/Updated timestamps automatically managed
- Version history preserved in YAML

---

## Step 9: Task Management (5 minutes)

### Add Your First Task

```bash
clauxton task add \
  --name "Implement FastAPI authentication" \
  --priority high \
  --files "src/auth/oauth.py,src/auth/jwt.py"
```

**Output**:
```
✓ Added task: TASK-001
  Name: Implement FastAPI authentication
  Priority: high
  Status: pending
  Files: src/auth/oauth.py, src/auth/jwt.py
```

---

### Add Task with Manual Dependency

```bash
clauxton task add \
  --name "Add API endpoints for user management" \
  --depends-on TASK-001 \
  --files "src/api/users.py" \
  --priority medium
```

**Why dependency?**
- User management API needs authentication system first
- Manual dependency ensures correct execution order

---

### Add Task with Auto-inferred Dependency

```bash
# Add another task touching same file
clauxton task add \
  --name "Add JWT token refresh endpoint" \
  --files "src/auth/jwt.py,src/api/auth.py" \
  --priority medium
```

**Auto-inference**:
- TASK-001 touches `src/auth/jwt.py`
- TASK-003 also touches `src/auth/jwt.py`
- Clauxton automatically infers: TASK-003 depends on TASK-001
- Prevents merge conflicts!

---

### List Tasks

```bash
clauxton task list
```

**Output**:
```
Tasks (3):

  TASK-001 [pending] (high)
    Name: Implement FastAPI authentication
    Files: src/auth/oauth.py, src/auth/jwt.py
    Dependencies: None

  TASK-002 [pending] (medium)
    Name: Add API endpoints for user management
    Files: src/api/users.py
    Dependencies: TASK-001

  TASK-003 [pending] (medium)
    Name: Add JWT token refresh endpoint
    Files: src/auth/jwt.py, src/api/auth.py
    Dependencies: TASK-001 (auto-inferred)
```

---

### Get Next Recommended Task

```bash
clauxton task next
```

**Output**:
```
Recommended next task:

  TASK-001 [pending] (high)
    Name: Implement FastAPI authentication
    Files: src/auth/oauth.py, src/auth/jwt.py

Reason: High priority, no dependencies, blocks 2 other tasks
```

**AI Recommendation Logic**:
1. Tasks with no unmet dependencies
2. Higher priority first
3. Tasks that unblock other tasks
4. Optimal execution order for parallel work

---

### Update Task Status

```bash
# Start working on TASK-001
clauxton task update TASK-001 --status in_progress

# Complete TASK-001
clauxton task update TASK-001 --status completed

# Get next task again
clauxton task next
```

**Output**:
```
Recommended next task:

  TASK-002 [pending] (medium)
    Name: Add API endpoints for user management
    Files: src/api/users.py

Reason: Dependency TASK-001 completed, high priority among remaining
```

---

## Step 10: Claude Code Integration (5 minutes)

### Setup MCP Server

Create `.claude-plugin/mcp-servers.json` in your project root:

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

### Restart Claude Code

After creating the config file, restart Claude Code to load the MCP server.

---

### Use KB Search from Claude

**Example conversation**:

```
You: "How do we handle authentication in this project?"

Claude: [Uses kb_search("authentication")]

Based on KB-20251019-002, we use OAuth 2.0 with JWT tokens for authentication.

Here's the approach:
- OAuth 2.0 flow for industry-standard auth
- JWT tokens (access: 15min, refresh: 7day)
- RS256 signing algorithm
- Stateless authentication (no server sessions)

The decision was made because:
- Industry standard for API authentication
- Works across microservices
- JWT can include user metadata

Implementation details:
- Access tokens expire in 15 minutes
- Refresh tokens expire in 7 days
- Store refresh tokens in httpOnly cookies
- Implement token revocation list

This integrates with our FastAPI backend (KB-20251019-001).
```

---

### Use Task Recommendations from Claude

```
You: "What should I work on next?"

Claude: [Uses task_next()]

I recommend working on TASK-001: "Implement FastAPI authentication"

Reasoning:
- High priority task
- No dependencies blocking it
- Two other tasks depend on it (TASK-002, TASK-003)
- Affects files: src/auth/oauth.py, src/auth/jwt.py

This will unblock the user management API and JWT refresh endpoint tasks.

Would you like me to help you implement the OAuth flow?
```

---

### MCP Tools Available

**Knowledge Base** (6 tools):
- `kb_search(query, category?, limit?)` - Search with TF-IDF
- `kb_add(title, category, content, tags?)` - Add entry
- `kb_list(category?)` - List all entries
- `kb_get(entry_id)` - Get entry details
- `kb_update(entry_id, ...)` - Update entry
- `kb_delete(entry_id)` - Delete entry

**Task Management** (6 tools):
- `task_add(name, description?, priority?, depends_on?, files?, ...)` - Add task
- `task_list(status?, priority?)` - List tasks
- `task_get(task_id)` - Get task details
- `task_update(task_id, status?, ...)` - Update task
- `task_next()` - Get AI-recommended next task
- `task_delete(task_id)` - Delete task

**Full documentation**: [MCP Server Guide](mcp-server.md)

---

## Best Practices (3 minutes)

### Knowledge Base

**When to add entries**:
- ✅ When making architecture decisions
- ✅ When establishing constraints
- ✅ When choosing between alternatives
- ✅ When documenting patterns
- ❌ Not for code documentation (use code comments)
- ❌ Not for temporary notes (use TODO comments)

**Writing good titles**:
- ✅ "Use PostgreSQL 15+ for production database"
- ❌ "Database decision"
- ✅ "REST API uses semantic versioning (v1, v2)"
- ❌ "API versioning"

**Effective tagging**:
- Use specific technical terms: `fastapi`, `postgresql`, `oauth`
- Include technology stack: `python`, `typescript`, `react`
- Add domain terms: `authentication`, `payment`, `notification`
- 3-6 tags per entry is optimal

---

### Task Management

**Breaking down tasks**:
- One task per file/module when possible
- Estimate time if helpful (use `--estimate 2.5` for 2.5 hours)
- Link to KB entries (use `--kb-refs KB-20251019-001`)
- Associate files for auto-dependency inference

**Using priorities**:
- `critical`: System down, data loss, security breach
- `high`: Blocking other work, user-facing bugs
- `medium`: Regular features, improvements
- `low`: Nice-to-haves, technical debt

**Auto-dependency vs Manual**:
- Let Clauxton infer from file overlap (it's smart!)
- Add manual dependencies for logical requirements (auth before user API)
- Review dependencies with `clauxton task list`

---

## What's Next?

### Advanced Features

**Learn more about**:
- [Search Algorithm](search-algorithm.md) - How TF-IDF works under the hood
- [Task Management Guide](task-management-guide.md) - Advanced task workflows
- [MCP Server Guide](mcp-server.md) - Full Claude Code integration
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

### Real-World Use Cases

See [Use Cases](use-cases.md) for examples:
- Tracking Architecture Decisions (ADR)
- Managing Refactoring Tasks
- Finding Relevant Context with TF-IDF
- Auto-inferring Task Dependencies
- MCP Integration Workflows

### Join the Community

- **Questions**: [GitHub Discussions](https://github.com/nakishiyaman/clauxton/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/nakishiyaman/clauxton/issues)
- **Contribute**: [Contributing Guide](../CONTRIBUTING.md)

---

## Summary

**What you learned**:
- ✅ Install Clauxton (`pip install clauxton`)
- ✅ Initialize project (`clauxton init`)
- ✅ Create Knowledge Base entries (5 categories)
- ✅ Search with TF-IDF relevance ranking
- ✅ Manage tasks with dependencies
- ✅ Use AI-powered task recommendations
- ✅ Integrate with Claude Code via MCP

**Key concepts**:
- **Knowledge Base**: Persistent project context (architecture, decisions, constraints, patterns, conventions)
- **TF-IDF Search**: Relevance-based ranking (rare terms = more valuable)
- **Task Management**: Auto-dependency inference from file overlap
- **MCP Integration**: 12 tools for Claude Code

**Time to proficiency**: 30 minutes 🎉

---

**Congratulations!** You've completed the Clauxton tutorial.

You now have persistent project context that works across AI sessions. Try using `kb_search` and `task_next` from Claude Code to experience the full power of Clauxton!

---

**Tutorial created**: 2025-10-19
**Clauxton version**: 0.8.0
**Estimated completion time**: 30 minutes
