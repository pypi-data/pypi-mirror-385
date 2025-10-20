# Best Practices Guide

Guidelines for effective use of Clauxton Knowledge Base and Task Management.

---

## Knowledge Base Best Practices

### 1. Writing Effective Titles

**Goal**: Make entries findable and scannable.

#### ❌ Bad Titles
```
- "API"
- "Database stuff"
- "Important decision"
- "Use X"
```

#### ✅ Good Titles
```
- "Use FastAPI framework for all backend APIs"
- "PostgreSQL 15+ required for production"
- "Authentication via JWT tokens"
- "Repository pattern for data access layer"
```

**Rules**:
- Be specific (include technology names)
- State the decision clearly
- Keep under 50 characters
- Use action verbs ("Use X", "Avoid Y", "Prefer Z")

---

### 2. Choosing the Right Category

Clauxton has 5 categories. Use them consistently:

| Category | When to Use | Examples |
|----------|-------------|----------|
| **architecture** | High-level system design | "Microservices architecture", "Event-driven design" |
| **constraint** | Hard requirements or limitations | "Must support IE11", "Max 200ms response time" |
| **decision** | Important choices with rationale | "Choose PostgreSQL over MySQL", "Use REST not GraphQL" |
| **pattern** | Reusable code patterns | "Repository pattern", "Factory pattern for services" |
| **convention** | Team agreements on style/process | "camelCase for JavaScript", "Feature branch workflow" |

#### Decision Tree

```
Is it about system structure?
  → Yes: architecture

Is it a technical/business limitation?
  → Yes: constraint

Did you choose between alternatives?
  → Yes: decision

Is it a reusable code pattern?
  → Yes: pattern

Is it a team agreement on how to work?
  → Yes: convention
```

#### Examples

```bash
# ✅ Correct categorization
clauxton kb add
# Title: Use microservices architecture
# Category: architecture

clauxton kb add
# Title: Support only PostgreSQL 12+
# Category: constraint

clauxton kb add
# Title: Choose FastAPI over Flask
# Category: decision

clauxton kb add
# Title: Use Repository pattern for DB access
# Category: pattern

clauxton kb add
# Title: Use snake_case for Python
# Category: convention
```

---

### 3. Writing Rich Content

**Goal**: Provide enough context for future reference.

#### ❌ Minimal Content
```yaml
title: Use FastAPI
content: All APIs use FastAPI.
```

#### ✅ Rich Content
```yaml
title: Use FastAPI framework for backend APIs
content: |
  All backend APIs must use FastAPI 0.100+ framework.

  Reasons:
  - Async/await support out of the box
  - Automatic OpenAPI documentation generation
  - Pydantic integration for request/response validation
  - Performance comparable to NodeJS and Go
  - Type hints for better IDE support

  Migration plan:
  - New services: Use FastAPI immediately
  - Existing Flask services: Migrate when refactoring

  Resources:
  - Documentation: https://fastapi.tiangolo.com/
  - Internal guide: docs/backend/fastapi-setup.md

  Decision made: 2025-10-15
  Approved by: Architecture team
  Review date: 2026-10-15
```

**Include**:
- Rationale (why this decision?)
- Context (when does this apply?)
- Exceptions (any edge cases?)
- Resources (links, docs, examples)
- Timeline (when decided, review date)
- Ownership (who decided, who maintains)

---

### 4. Effective Tagging

**Goal**: Improve searchability across categories.

#### Tagging Guidelines

1. **Use lowercase**: `fastapi`, not `FastAPI`
2. **Be specific**: `postgresql` not just `database`
3. **Include technology names**: `react`, `typescript`, `docker`
4. **Include functional areas**: `auth`, `api`, `frontend`, `backend`
5. **Avoid redundancy**: Don't duplicate title words

#### Examples

```bash
# ✅ Good tagging
Title: Use FastAPI framework for backend APIs
Tags: backend, api, fastapi, async, python

Title: JWT authentication for all services
Tags: auth, jwt, security, backend

Title: React 18+ for frontend
Tags: frontend, react, ui, javascript

# ❌ Bad tagging
Title: Use FastAPI
Tags: fastapi  # Too minimal

Title: Use FastAPI framework
Tags: use, fastapi, framework  # Redundant with title

Title: Backend API framework
Tags: stuff, api  # Too generic
```

---

### 5. Keeping Entries Current

**Goal**: Ensure Knowledge Base reflects current reality.

#### Regular Review Process

```bash
# 1. Review old entries (quarterly)
clauxton kb list | grep "2024-"

# 2. Update outdated entries
clauxton kb get KB-20240115-001
clauxton kb update KB-20240115-001 \
  --content "Updated content with new requirements"

# 3. Delete obsolete entries
clauxton kb delete KB-20240115-999 --yes
```

#### When to Update

- Technology version changes (FastAPI 0.95 → 0.100)
- Requirements change (IE11 support dropped)
- Decisions are reversed (GraphQL adopted after all)
- More context discovered (security implications)

#### Version History

Clauxton tracks versions automatically:
```yaml
id: KB-20251019-001
version: 3  # Incremented on each update
created_at: 2025-10-19T10:00:00
updated_at: 2025-10-19T15:30:00
```

---

### 6. Team Collaboration

**Goal**: Share Knowledge Base across the team.

#### Git Workflow

```bash
# 1. Pull latest before adding
git pull origin main

# 2. Add KB entries
clauxton kb add

# 3. Commit with descriptive message
git add .clauxton/
git commit -m "docs(kb): Add authentication architecture decision"

# 4. Push to share with team
git push origin main
```

#### Commit Message Convention

```
docs(kb): Add <brief description>
docs(kb): Update <entry ID> - <reason>
docs(kb): Delete obsolete <topic> entries

Examples:
docs(kb): Add microservices architecture decision
docs(kb): Update KB-20251019-001 - FastAPI version bump
docs(kb): Delete obsolete Flask entries
```

#### Avoiding Conflicts

1. **Coordinate**: Announce major KB updates in team chat
2. **Pull frequently**: Before adding entries
3. **Resolve carefully**: Merge conflicts in YAML are tricky
4. **Use backups**: `.yml.bak` files exist for a reason

---

## Task Management Best Practices

### 1. Granular Task Breakdown

**Goal**: Tasks should be completable in 1-8 hours.

#### ❌ Too Large
```bash
clauxton task add --name "Build authentication system"
# This could take weeks!
```

#### ✅ Right Size
```bash
# Break into smaller tasks
clauxton task add --name "Design authentication schema" --estimate 2.0
clauxton task add --name "Implement JWT token generation" --estimate 3.0 --depends-on TASK-001
clauxton task add --name "Add login endpoint" --estimate 2.0 --depends-on TASK-002
clauxton task add --name "Add logout endpoint" --estimate 1.0 --depends-on TASK-002
clauxton task add --name "Add password reset flow" --estimate 4.0 --depends-on TASK-003
```

**Benefits**:
- Clear progress tracking
- Easier to estimate
- Better dependency management
- Satisfying to complete

---

### 2. Meaningful Task Names

#### ❌ Bad Names
```
- "Fix bug"
- "Update API"
- "Refactor"
- "TODO"
```

#### ✅ Good Names
```
- "Fix login timeout after 5 minutes"
- "Add rate limiting to user API"
- "Refactor auth middleware for testability"
- "Add pagination to search results"
```

**Format**: `<Verb> <What> <Where/Context>`

---

### 3. Using Dependencies Effectively

#### Manual Dependencies

```bash
# Linear dependency chain
clauxton task add --name "Design database schema"
# TASK-001

clauxton task add --name "Create migration script" --depends-on TASK-001
# TASK-002

clauxton task add --name "Run migration on staging" --depends-on TASK-002
# TASK-003
```

#### Auto-Inferred Dependencies

Clauxton infers dependencies from file overlap:

```bash
# Task 1 edits auth.py
clauxton task add \
  --name "Add JWT generation" \
  --files "src/auth.py,src/utils.py"
# TASK-001

# Task 2 also edits auth.py
clauxton task add \
  --name "Add token refresh" \
  --files "src/auth.py"
# TASK-002 automatically depends on TASK-001
```

**Use file-based dependencies when**:
- Multiple tasks modify the same file
- Order matters for code changes
- Avoiding merge conflicts

---

### 4. Priority Levels

Use priorities to guide `clauxton task next`:

| Priority | When to Use | Examples |
|----------|-------------|----------|
| **critical** | Blocking production, security issues | "Fix SQL injection vulnerability" |
| **high** | Core features, tight deadlines | "Implement login for launch" |
| **medium** | Normal feature work | "Add user profile page" |
| **low** | Nice-to-haves, refactoring | "Refactor CSS for consistency" |

```bash
# Critical: Security fix
clauxton task add \
  --name "Patch authentication bypass" \
  --priority critical

# High: Launch blocker
clauxton task add \
  --name "Add payment integration" \
  --priority high

# Medium: Regular work
clauxton task add \
  --name "Add user settings page" \
  --priority medium

# Low: Tech debt
clauxton task add \
  --name "Refactor API client" \
  --priority low
```

---

### 5. Linking Tasks to Knowledge Base

**Goal**: Provide context for task implementation.

```bash
# 1. Add KB entry with architecture decision
clauxton kb add
# Title: Use Repository pattern for data access
# Category: pattern
# Content: All database access goes through Repository classes...
# → KB-20251019-005

# 2. Create task referencing KB entry
clauxton task add \
  --name "Refactor UserService to use Repository pattern" \
  --kb-refs "KB-20251019-005" \
  --files "src/services/user.py,src/repositories/user.py" \
  --estimate 3.0

# 3. When working on task, refer to KB
clauxton task get TASK-001
# Shows: Related KB entries: KB-20251019-005

clauxton kb get KB-20251019-005
# Shows architecture details
```

**When to link**:
- Task implements a KB decision
- Task requires specific constraint knowledge
- Task follows a KB pattern

---

### 6. Task Workflow

#### Recommended Workflow

```bash
# 1. Get next recommended task
clauxton task next
# → TASK-005: Implement JWT token generation

# 2. Start working
clauxton task update TASK-005 --status in_progress

# 3. Work on task...
# (Code, test, commit)

# 4. Complete task
clauxton task update TASK-005 --status completed

# 5. Repeat
clauxton task next
```

#### Task Lifecycle

```
pending → in_progress → completed
                     ↘
                       blocked (if dependencies unmet)
```

**Status meanings**:
- `pending`: Not started, ready to begin
- `in_progress`: Currently being worked on
- `completed`: Finished and merged
- `blocked`: Waiting on dependencies or external factors

---

### 7. Estimates and Tracking

```bash
# Add task with estimate
clauxton task add \
  --name "Add user authentication" \
  --estimate 4.5

# Update actual hours (manual, via API)
# (CLI update coming in Phase 2)
```

**Estimation tips**:
- Use hours (0.5, 1.0, 2.0, 4.0, 8.0)
- Include testing and documentation time
- Add buffer for unknowns (+25%)
- Track actual vs. estimated for learning

---

## Integration Best Practices

### Clauxton + Claude Code

#### 1. **Start conversations with context**

```
User: "Let's implement the authentication system.
       Check KB entry KB-20251019-005 for our architecture."

Claude: [Uses kb_get to retrieve architecture decision]
        [Implements following the KB pattern]
```

#### 2. **Let Claude manage tasks**

```
User: "Create tasks for implementing the user profile feature."

Claude: [Uses task_add to create breakdown]
        TASK-001: Design profile schema
        TASK-002: Add profile endpoints (depends on TASK-001)
        TASK-003: Create profile UI (depends on TASK-002)
```

#### 3. **Reference KB entries in code comments**

```python
# Implements authentication per KB-20251019-005
# See: clauxton kb get KB-20251019-005
class AuthRepository:
    ...
```

---

### Clauxton + Git

#### 1. **Commit .clauxton/ regularly**

```bash
# After significant KB updates
git add .clauxton/
git commit -m "docs(kb): Add Phase 1 architecture decisions"

# After task planning session
git add .clauxton/
git commit -m "tasks: Plan authentication feature tasks"
```

#### 2. **Review KB in PRs**

```markdown
## PR Checklist
- [ ] Code changes
- [ ] Tests added
- [ ] KB updated (if architecture/decision changed)
- [ ] Tasks marked complete
```

---

## Anti-Patterns to Avoid

### ❌ Don't Over-Document

```yaml
# Too detailed - this belongs in code comments
title: Function calculateTotal implementation
content: |
  The calculateTotal function takes items array,
  iterates using forEach, sums prices...
```

**Instead**: Document high-level decisions, not code details.

### ❌ Don't Duplicate Documentation

KB entries should **complement** not **replace** code docs:
- ✅ KB: "Why we use Repository pattern"
- ✅ Code docs: "How this Repository implementation works"

### ❌ Don't Create Orphan Tasks

```bash
# ❌ Task without context
clauxton task add --name "Implement feature X"

# ✅ Task with KB reference
clauxton task add \
  --name "Implement feature X per KB-20251019-007" \
  --kb-refs "KB-20251019-007"
```

### ❌ Don't Forget to Update Status

```bash
# ❌ Task stuck in 'in_progress' forever
# (Forgot to mark complete)

# ✅ Complete tasks promptly
clauxton task update TASK-005 --status completed
```

---

## Performance Tips

### 1. Use Category Filters

```bash
# ❌ Slow: Search everything
clauxton kb search "API"

# ✅ Fast: Filter by category
clauxton kb search "API" --category architecture
```

### 2. Archive Completed Tasks

```bash
# Delete old completed tasks
clauxton task list --status completed

# Delete tasks no longer relevant
clauxton task delete TASK-042 --yes
```

### 3. Keep KB Lean

- Delete obsolete entries
- Merge duplicate entries
- Archive historical decisions (in separate docs)

---

## Checklist for New Projects

```bash
# 1. Initialize Clauxton
cd /path/to/project
clauxton init

# 2. Add core architecture decisions
clauxton kb add  # Framework choice
clauxton kb add  # Database choice
clauxton kb add  # Auth strategy

# 3. Add project constraints
clauxton kb add  # Performance requirements
clauxton kb add  # Browser support
clauxton kb add  # Compliance requirements

# 4. Plan initial tasks
clauxton task add --name "Setup project structure"
clauxton task add --name "Configure CI/CD"
clauxton task add --name "Setup database"

# 5. Commit to git
git add .clauxton/
git commit -m "docs: Initialize Clauxton Knowledge Base"
git push

# 6. Share with team
# Team pulls and has immediate context!
```

---

## Summary

### Knowledge Base Golden Rules

1. ✅ Specific, descriptive titles
2. ✅ Use categories consistently
3. ✅ Rich content with context
4. ✅ Meaningful tags
5. ✅ Keep current through reviews
6. ✅ Commit to git regularly

### Task Management Golden Rules

1. ✅ Break tasks into 1-8 hour chunks
2. ✅ Clear, action-oriented names
3. ✅ Use dependencies wisely
4. ✅ Set appropriate priorities
5. ✅ Link to relevant KB entries
6. ✅ Update status promptly

---

**Next Steps**: See [Quick Start Guide](quick-start.md) for hands-on tutorial.

**Last Updated**: Phase 1 Week 8 (v0.7.0+)
