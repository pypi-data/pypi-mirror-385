### Task Management Guide

**Clauxton Task Management - Plan, Track, and Execute with AI**

This guide explains how to use Clauxton's task management system to organize work with dependency tracking and AI-powered recommendations.

---

## Overview

Clauxton Task Management provides:
- **Task CRUD**: Create, read, update, delete tasks
- **Dependency Tracking**: Define task dependencies (DAG structure)
- **Priority Management**: Critical > High > Medium > Low
- **Status Tracking**: Pending → In Progress → Completed
- **AI Recommendations**: Get next task based on dependencies and priority
- **YAML Persistence**: Human-readable tasks.yml format

**Status**: ✅ Available (Phase 1, Week 4)

---

## Quick Start

### 1. Initialize Your Project

```bash
cd your-project
clauxton init
```

### 2. Add Your First Task

```bash
clauxton task add
# Prompt: Task name? Setup database
# Default priority: medium
# ...

✓ Added task: TASK-001
  Name: Setup database
  Priority: medium
```

### 3. List All Tasks

```bash
clauxton task list

Tasks (1):

  TASK-001
    Name: Setup database
    Status: pending
    Priority: medium
```

### 4. Get Next Task to Work On

```bash
clauxton task next

📋 Next Task to Work On:

  TASK-001
  Name: Setup database
  Priority: medium

  Start working on this task:
    clauxton task update TASK-001 --status in_progress
```

---

## Task Structure

### Task Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique ID (TASK-NNN) | TASK-001 |
| `name` | string | Short task name (max 100 chars) | "Setup database" |
| `description` | string? | Detailed description | "Create PostgreSQL schema..." |
| `status` | enum | Current status | pending, in_progress, completed, blocked |
| `priority` | enum | Task priority | low, medium, high, critical |
| `depends_on` | list | Task IDs this depends on | ["TASK-001", "TASK-002"] |
| `files_to_edit` | list | Files to modify | ["src/db/schema.sql"] |
| `related_kb` | list | Related KB entries | ["KB-20251019-001"] |
| `estimated_hours` | float? | Estimated time | 4.5 |
| `actual_hours` | float? | Actual time spent | 5.2 |
| `created_at` | datetime | Creation timestamp | 2025-10-19T10:30:00 |
| `started_at` | datetime? | When started | 2025-10-19T11:00:00 |
| `completed_at` | datetime? | When completed | 2025-10-19T15:30:00 |

### Status Lifecycle

```
pending → in_progress → completed
   ↓
blocked (when dependencies incomplete)
```

### Priority Levels

- **Critical**: Blocking issues, urgent fixes
- **High**: Important features, high-value work
- **Medium**: Normal tasks (default)
- **Low**: Nice-to-have, cleanup tasks

---

## CLI Commands

### `clauxton task add`

Add a new task with dependencies.

**Basic Usage:**
```bash
clauxton task add --name "Setup database"
```

**With Options:**
```bash
clauxton task add \
  --name "Add API endpoint" \
  --description "Create /api/v1/users endpoint" \
  --priority high \
  --depends-on TASK-001 \
  --files "src/api/users.py,tests/test_users.py" \
  --kb-refs KB-20251019-001 \
  --estimate 3.5
```

**Parameters:**
- `--name` (required): Task name
- `--description`: Detailed description
- `--priority`: low | medium | high | critical (default: medium)
- `--depends-on`: Comma-separated task IDs
- `--files`: Comma-separated file paths
- `--kb-refs`: Comma-separated KB entry IDs
- `--estimate`: Estimated hours (float)

---

### `clauxton task list`

List all tasks with optional filters.

**Basic Usage:**
```bash
clauxton task list
```

**Filter by Status:**
```bash
clauxton task list --status pending
clauxton task list --status in_progress
clauxton task list --status completed
```

**Filter by Priority:**
```bash
clauxton task list --priority high
clauxton task list --priority critical
```

---

### `clauxton task get <id>`

Get detailed information about a task.

**Usage:**
```bash
clauxton task get TASK-001
```

**Output:**
```
TASK-001
Name: Setup database
Status: pending
Priority: high

Description:
Create PostgreSQL schema for production database

Depends on: (none)

Files to edit:
  - src/db/schema.sql
  - migrations/001_init.sql

Related KB entries: KB-20251019-001

Estimated: 4.0 hours

Created: 2025-10-19 10:30
```

---

### `clauxton task update <id>`

Update task fields.

**Update Status:**
```bash
clauxton task update TASK-001 --status in_progress
# Auto-sets started_at timestamp

clauxton task update TASK-001 --status completed
# Auto-sets completed_at timestamp
```

**Update Priority:**
```bash
clauxton task update TASK-001 --priority high
```

**Update Multiple Fields:**
```bash
clauxton task update TASK-001 \
  --status completed \
  --priority high \
  --description "Updated description"
```

**Parameters:**
- `--status`: pending | in_progress | completed | blocked
- `--priority`: low | medium | high | critical
- `--name`: Update task name
- `--description`: Update description

**Note**: Timestamps (`started_at`, `completed_at`) are set automatically when status changes.

---

### `clauxton task delete <id>`

Delete a task.

**Usage:**
```bash
clauxton task delete TASK-001
# Prompts for confirmation

clauxton task delete TASK-001 --yes
# Skip confirmation
```

**Important**: Cannot delete tasks that have dependents. Delete dependent tasks first.

---

### `clauxton task next`

Get AI-recommended next task to work on.

**Usage:**
```bash
clauxton task next
```

**Algorithm:**
1. Filter tasks with status = "pending"
2. Exclude tasks whose dependencies are incomplete
3. Sort by priority (critical > high > medium > low)
4. Return highest priority task

**Output:**
```
📋 Next Task to Work On:

  TASK-003
  Name: Add API endpoint
  Priority: high

  Description:
    Create /api/v1/users endpoint with CRUD operations

  Files to edit:
    - src/api/users.py
    - tests/test_users.py

  Estimated: 3.5 hours

  Start working on this task:
    clauxton task update TASK-003 --status in_progress
```

---

## Common Workflows

### Workflow 1: Feature Development with Dependencies

**Scenario**: Implement user authentication

```bash
# Step 1: Add database migration task
clauxton task add \
  --name "Create users table" \
  --priority high \
  --files "migrations/002_users.sql"

# Output: TASK-001

# Step 2: Add authentication task (depends on database)
clauxton task add \
  --name "Implement JWT authentication" \
  --priority high \
  --depends-on TASK-001 \
  --files "src/auth.py,tests/test_auth.py"

# Output: TASK-002

# Step 3: Add API endpoint (depends on auth)
clauxton task add \
  --name "Add /login endpoint" \
  --priority medium \
  --depends-on TASK-002 \
  --files "src/api/auth.py"

# Output: TASK-003

# Step 4: Get next task (returns TASK-001, others are blocked)
clauxton task next
# → TASK-001 (no dependencies)

# Step 5: Start working
clauxton task update TASK-001 --status in_progress

# Step 6: Complete task
clauxton task update TASK-001 --status completed

# Step 7: Get next task (now TASK-002 is unblocked)
clauxton task next
# → TASK-002
```

---

### Workflow 2: Bug Fix Triage

**Scenario**: Multiple bugs need prioritization

```bash
# Add critical bug
clauxton task add \
  --name "Fix login crash" \
  --priority critical \
  --description "App crashes when user logs in"

# Add high priority bug
clauxton task add \
  --name "Fix memory leak" \
  --priority high \
  --description "Memory usage grows over time"

# Add medium priority bug
clauxton task add \
  --name "Fix typo in UI" \
  --priority medium

# Get next task (returns critical priority first)
clauxton task next
# → "Fix login crash" (critical)
```

---

### Workflow 3: Sprint Planning

**Scenario**: Plan 2-week sprint

```bash
# Add all sprint tasks
clauxton task add --name "Feature A" --priority high --estimate 8
clauxton task add --name "Feature B" --priority high --estimate 5
clauxton task add --name "Feature C" --priority medium --estimate 13
clauxton task add --name "Bug fixes" --priority medium --estimate 3

# List all pending tasks to review
clauxton task list --status pending

# Start working on highest priority
clauxton task next
clauxton task update TASK-001 --status in_progress

# Track progress
clauxton task list --status completed
clauxton task list --status in_progress
clauxton task list --status pending
```

---

## Dependency Management

### Valid Dependency Graph (DAG)

```
TASK-001 (Setup DB)
   ↓
TASK-002 (Add tables) ← depends on TASK-001
   ↓
TASK-003 (Add API) ← depends on TASK-002
```

**CLI:**
```bash
clauxton task add --name "Setup DB"
# → TASK-001

clauxton task add --name "Add tables" --depends-on TASK-001
# → TASK-002

clauxton task add --name "Add API" --depends-on TASK-002
# → TASK-003
```

### Invalid: Circular Dependency

```
TASK-001 → TASK-002
    ↑          ↓
    └──────────┘
```

**CLI:**
```bash
clauxton task add --name "Task 1"
# → TASK-001

clauxton task add --name "Task 2" --depends-on TASK-001
# → TASK-002

clauxton task update TASK-001 --depends-on TASK-002
# ❌ Error: Adding dependencies ["TASK-002"] to task 'TASK-001' would create
#    a circular dependency. Task dependency graph must be acyclic (DAG).
```

### Deleting Tasks with Dependents

```bash
clauxton task delete TASK-001
# ❌ Error: Cannot delete task 'TASK-001' because it has dependents: TASK-002.
#    Delete dependents first.

# Solution: Delete in reverse dependency order
clauxton task delete TASK-002  # ✓ OK
clauxton task delete TASK-001  # ✓ OK
```

---

## YAML Storage

Tasks are stored in `.clauxton/tasks.yml`:

```yaml
version: '1.0'
project_name: my-project

tasks:
  - id: TASK-001
    name: Setup database
    description: Create PostgreSQL schema
    status: pending
    priority: high
    depends_on: []
    files_to_edit:
      - migrations/001_init.sql
    related_kb:
      - KB-20251019-001
    estimated_hours: 4.0
    actual_hours: null
    created_at: '2025-10-19T10:30:00'
    started_at: null
    completed_at: null
```

**Features:**
- Human-readable YAML format
- Git-friendly (commit `.clauxton/` for team sharing)
- Automatic backups (`.yml.bak`)
- Secure permissions (700/600)

---

## Tips & Best Practices

### 1. Use Descriptive Names

❌ Bad: "Fix bug"
✅ Good: "Fix login crash on iOS"

### 2. Break Down Large Tasks

❌ Bad: "Implement user system" (too broad)
✅ Good:
- "Create users table migration"
- "Implement JWT authentication"
- "Add user registration endpoint"
- "Add user profile page"

### 3. Set Dependencies Correctly

```bash
# Database migration must come first
TASK-001: Create tables

# Then add business logic
TASK-002: Implement auth (depends on TASK-001)

# Finally add UI
TASK-003: Add login page (depends on TASK-002)
```

### 4. Use Priorities Wisely

- **Critical**: Production is down, users can't work
- **High**: Important feature for sprint, blocking other work
- **Medium**: Normal tasks, planned work
- **Low**: Nice-to-have, cleanup, technical debt

### 5. Track Files to Edit

```bash
clauxton task add \
  --name "Add user API" \
  --files "src/api/users.py,tests/test_users.py,docs/api.md"
```

Benefits:
- See what files you'll need to modify
- Detect potential conflicts (Phase 2 feature)
- Better task estimation

### 6. Link to Knowledge Base

```bash
clauxton task add \
  --name "Implement caching" \
  --kb-refs KB-20251019-005
```

Benefits:
- Quick access to related architecture decisions
- Maintain consistency with project conventions
- Onboard new team members faster

---

## Troubleshooting

### "Error: .clauxton/ not found"

**Solution**: Initialize Clauxton first
```bash
clauxton init
```

### "Error: Dependency task 'TASK-XXX' not found"

**Solution**: Add dependencies before dependent tasks
```bash
# Wrong order
clauxton task add --name "Task 2" --depends-on TASK-001  # ❌ TASK-001 doesn't exist

# Correct order
clauxton task add --name "Task 1"  # ✓ TASK-001
clauxton task add --name "Task 2" --depends-on TASK-001  # ✓ OK
```

### "No tasks ready to work on"

**Causes**:
1. All tasks are completed
2. All pending tasks are blocked by dependencies
3. All tasks are in_progress

**Solution**: Check status
```bash
clauxton task list
clauxton task list --status completed
clauxton task list --status in_progress
```

---

## Next Steps

- [MCP Server Guide](mcp-server.md) - Use tasks with Claude Code
- [Phase 1 Plan](phase-1-plan.md) - Upcoming features (Week 5-8)
- [YAML Format Reference](yaml-format.md) - Understanding the data structure

---

## Coming Soon (Phase 1, Week 5-6)

**Auto-Dependency Inference**:
Claude Code will automatically detect dependencies based on file overlap:
```
TASK-001: Edit src/api/users.py
TASK-002: Edit src/api/users.py  ← Auto-detected dependency on TASK-001
```

**Status**: ✅ Week 4 Complete | Task Management with CLI | 157 tests passing
