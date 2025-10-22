# Clauxton Developer Workflow Guide

**Version**: v0.10.0
**Last Updated**: 2025-10-21
**Status**: Complete

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Workflow Phases](#workflow-phases)
3. [Phase 0: Project Initialization](#phase-0-project-initialization)
4. [Phase 1: Requirements Gathering](#phase-1-requirements-gathering)
5. [Phase 2: Task Planning](#phase-2-task-planning)
6. [Phase 3: Conflict Detection](#phase-3-conflict-detection)
7. [Phase 4: Implementation](#phase-4-implementation)
8. [Phase 5: Monitoring & Logging](#phase-5-monitoring--logging)
9. [Phase 6: Error Recovery](#phase-6-error-recovery)
10. [Requirement Changes](#requirement-changes)
11. [Manual Control](#manual-control)
12. [Best Practices](#best-practices)
13. [Metrics & Performance](#metrics--performance)

---

## Overview

Clauxton provides a **transparent yet controllable** workflow for software development with Claude Code. This guide explains how developers interact with Clauxton throughout the entire development lifecycle.

### Core Philosophy

```
┌─────────────────────────────────────────────────────────────┐
│  Natural Conversation → Automatic Management → User Control │
└─────────────────────────────────────────────────────────────┘
```

**Key Principles:**

- **Transparent Integration**: Claude Code uses Clauxton automatically during natural conversation
- **Human-in-the-Loop**: Configurable confirmation levels (always/auto/never)
- **Safety First**: Undo capability, automatic backups, operation logging
- **User Control**: CLI override always available for manual adjustments

### What Clauxton Manages

```
┌─────────────────────────────────────────────────────────────┐
│                    Clauxton Components                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📚 Knowledge Base           📋 Task Management             │
│  • Architecture decisions    • Task creation & tracking     │
│  • Constraints              • Dependency inference          │
│  • Design decisions         • DAG validation                │
│  • Conventions              • Progress monitoring           │
│  • Patterns                 • Priority management           │
│                                                              │
│  ⚠️  Conflict Detection      🔄 Change Management           │
│  • File overlap detection   • Requirement changes           │
│  • Risk scoring             • Task updates                  │
│  • Safe order suggestions   • KB updates                    │
│                                                              │
│  📝 Operation Logging        ⏪ Undo Capability             │
│  • Daily log files          • 7 operation types             │
│  • JSON Lines format        • 50 operations history         │
│  • 30-day retention         • Instant recovery              │
└─────────────────────────────────────────────────────────────┘
```

---

## Workflow Phases

The complete development workflow consists of 7 phases:

```
┌──────────────────────────────────────────────────────────────────────┐
│                      Development Workflow                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Phase 0: Project Initialization                                     │
│     ↓                                                                 │
│  Phase 1: Requirements Gathering (Natural Conversation)              │
│     ↓                                                                 │
│  Phase 2: Task Planning (YAML Bulk Import)                           │
│     ↓                                                                 │
│  Phase 3: Conflict Detection (Before Implementation)                 │
│     ↓                                                                 │
│  Phase 4: Implementation (Code + Test)                               │
│     ↓                                                                 │
│  Phase 5: Monitoring & Logging (Operation Logs)                      │
│     ↓                                                                 │
│  Phase 6: Error Recovery (Undo if needed)                            │
│     ↓                                                                 │
│  ← → Requirement Changes (Insert at any phase)                       │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Project Initialization

### Developer Actions

```bash
# Create project directory
mkdir todo-app && cd todo-app

# Initialize Clauxton
clauxton init

# Start Claude Code
code .
```

### Generated Structure

```
todo-app/
├── .clauxton/
│   ├── knowledge-base.yml      # Empty initially
│   ├── tasks.yml               # Empty initially
│   ├── config.yml              # Default configuration
│   ├── backups/                # Automatic backups
│   │   └── (timestamped backups)
│   └── logs/                   # Operation logs
│       └── YYYY-MM-DD.log      # Daily log files
├── .gitignore                  # Includes .clauxton/logs/
└── (project files)
```

### Configuration Options

```bash
# View current configuration
clauxton config list

# Set confirmation mode (always/auto/never)
clauxton config set confirmation_mode auto  # Default

# Set thresholds
clauxton config set task_import_threshold 10
clauxton config set kb_bulk_add_threshold 5
```

**Confirmation Modes:**

| Mode | HITL % | Confirmation Triggers | Use Case |
|------|--------|----------------------|----------|
| `always` | 100% | Every write operation | Team development, production |
| `auto` | 75% | 10+ tasks, 5+ KB entries | Individual development (default) |
| `never` | 25% | None (undo available) | Rapid prototyping |

---

## Phase 1: Requirements Gathering

### Natural Conversation Flow

**Developer → Claude Code:**

```
"I want to build a Todo app with FastAPI + React.
- Backend: FastAPI, PostgreSQL, JWT authentication
- Frontend: React 18, Vite, TailwindCSS
- Max 1000 todos, pagination required
- Naming: snake_case (Python), camelCase (JS)"
```

### Transparent KB Registration

Claude Code automatically registers requirements to Knowledge Base:

```python
# 1. Architecture decision
kb_add(
    title="FastAPI + React Architecture",
    category="architecture",
    content="FastAPI backend + React frontend with PostgreSQL and JWT auth",
    tags=["fastapi", "react", "postgresql", "jwt"]
)
# → KB-20251021-001

# 2. Constraint
kb_add(
    title="Todo Data Limit",
    category="constraint",
    content="Max 1000 todos. Pagination required (20 items/page).",
    tags=["constraint", "performance"]
)
# → KB-20251021-002

# 3. Convention
kb_add(
    title="Naming Convention",
    category="convention",
    content="Python: snake_case, JavaScript: camelCase",
    tags=["style", "convention"]
)
# → KB-20251021-003
```

### Developer Sees

```
Got it! I'll build a Todo app with FastAPI + React.
Here's the configuration:
- Backend: FastAPI + PostgreSQL + JWT authentication
- Frontend: React 18 + Vite + TailwindCSS
- Constraints: Max 1000 items, pagination (20 items/page)
- Naming: Python=snake_case, JS=camelCase

Registered 3 entries to Knowledge Base. Should I create tasks?
```

### KB Categories

```
┌─────────────────────────────────────────────────────────────┐
│                  Knowledge Base Categories                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📐 architecture  → Tech stack, system design               │
│  ⚠️  constraint    → Data limits, performance requirements   │
│  ✅ decision      → Design choices, trade-offs              │
│  🔧 pattern       → Code patterns, best practices            │
│  📝 convention    → Naming rules, code style                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Points:**

- ✅ Developer speaks naturally, no CLI commands
- ✅ Claude Code extracts and categorizes requirements automatically
- ✅ KB entries are human-readable YAML
- ✅ Git-friendly for version control

---

## Phase 2: Task Planning

### Bulk Task Generation (v0.10.0)

**Developer → Claude Code:**

```
"Yes, please proceed"
```

### Transparent YAML Generation

Claude Code analyzes the project and generates tasks internally:

```yaml
# Generated YAML (not shown to user)
tasks:
  - name: "FastAPI Initialization"
    description: "Set up FastAPI project structure"
    priority: high
    files_to_edit:
      - backend/main.py
      - backend/requirements.txt
      - backend/config.py
    estimate: 1

  - name: "PostgreSQL Database Design"
    description: "Design Todo and User tables with migrations"
    priority: high
    files_to_edit:
      - backend/models.py
      - backend/database.py
      - alembic/versions/001_create_tables.py
    depends_on:
      - TASK-001
    estimate: 2

  # ... 8 more tasks ...
```

### Automatic Dependency Inference

Clauxton infers dependencies from file overlap:

```
File Overlap Detection:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TASK-001 edits: backend/main.py, backend/requirements.txt
TASK-002 edits: backend/models.py, backend/database.py
TASK-003 edits: backend/api/todos.py, backend/schemas/todo.py

→ TASK-002 depends on TASK-001 (no file overlap, but logical order)
→ TASK-003 depends on TASK-002 (requires models.py)

DAG Validation: ✅ No cycles detected
```

### Confirmation Prompt (auto mode)

If 10+ tasks are being created, user confirmation is required:

```
⚠️  Confirmation Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Attempting to import 10 tasks.

📊 Summary:
─────────────────────────────────────────────────
  Total Tasks:     10
  Estimated Hours: 19 hours

  Priority Breakdown:
    Critical:      2 tasks (10%)
    High:          4 tasks (40%)
    Medium:        4 tasks (40%)
    Low:           0 tasks (0%)

  Status Breakdown:
    Pending:       10 tasks (100%)

📋 Tasks Preview:
─────────────────────────────────────────────────
  TASK-001: FastAPI Initialization (high, 1h)
  TASK-002: PostgreSQL Database Design (high, 2h)
  TASK-003: Todo CRUD API Implementation (high, 3h)
  TASK-004: JWT Authentication Implementation (critical, 2h)
  TASK-005: Pagination Implementation (medium, 1h)
  TASK-006: React + Vite Initialization (high, 1h)
  TASK-007: Todo List Component Implementation (high, 2h)
  TASK-008: Todo Add/Edit Form Implementation (medium, 2h)
  TASK-009: API Integration  Auth Flow Implementation (critical, 3h)
  TASK-010: E2E Test Implementation (medium, 2h)

Continue? [y/N]
```

**Developer Response:** `y`

### Task Import Result

```
✅ Created 10 tasks:

📋 Backend Tasks (TASK-001 ~ TASK-005):
─────────────────────────────────────────────────
  TASK-001: FastAPI Initialization (1h)
  TASK-002: PostgreSQL Database Design (2h)
  TASK-003: Todo CRUD API Implementation (3h)
  TASK-004: JWT Authentication Implementation (2h)
  TASK-005: Pagination Implementation (1h)

📋 Frontend Tasks (TASK-006 ~ TASK-009):
─────────────────────────────────────────────────
  TASK-006: React + Vite Initialization (1h)
  TASK-007: Todo List Component Implementation (2h)
  TASK-008: Todo Add/Edit Form Implementation (2h)
  TASK-009: API Integration  Auth Flow Implementation (3h)

📋 Integration Tasks (TASK-010):
─────────────────────────────────────────────────
  TASK-010: E2E Test Implementation (2h)

📊 Dependency Graph:
─────────────────────────────────────────────────
  TASK-001 → TASK-002 → TASK-003 → TASK-005
                      → TASK-004
  TASK-006 → TASK-007 → TASK-009 → TASK-010
           → TASK-008

🚀 Ready to start with TASK-001!
```

### Performance

```
┌─────────────────────────────────────────────────────────────┐
│              Task Import Performance (v0.10.0)               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Before (v0.9.0):  10 tasks = 10 commands × 30s = 5 minutes │
│  After (v0.10.0):  10 tasks = 1 command × 0.2s = instant    │
│                                                              │
│  Performance Gain: 30x faster ⚡                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Points:**

- ✅ User says "yes" only once
- ✅ 10 tasks created in 0.2 seconds (30x faster)
- ✅ Dependencies automatically inferred
- ✅ DAG validation ensures no circular dependencies
- ✅ Confirmation prompt for HITL control

---

## Phase 3: Conflict Detection

### Automatic Pre-Implementation Check

Before starting any task, Claude Code automatically checks for conflicts:

```python
# Before implementing TASK-001
conflicts = detect_conflicts("TASK-001")

# Result:
{
    "task_id": "TASK-001",
    "risk": "LOW",
    "conflicts": [],
    "message": "No conflicts detected. Safe to proceed."
}
```

### Conflict Risk Levels

```
┌─────────────────────────────────────────────────────────────┐
│                    Conflict Risk Levels                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🟢 LOW:     No overlapping files                           │
│             → Safe to proceed                               │
│                                                              │
│  🟡 MEDIUM:  1-2 tasks editing same files                   │
│             → Warning shown, user decides                   │
│                                                              │
│  🔴 HIGH:    3+ tasks or circular dependencies              │
│             → Strong recommendation to wait                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Medium Risk Example

```python
# TASK-003 depends on backend/models.py
# TASK-002 is currently modifying backend/models.py

conflicts = detect_conflicts("TASK-003")

# Result:
{
    "task_id": "TASK-003",
    "risk": "MEDIUM",
    "conflicts": [
        {
            "task_id": "TASK-002",
            "status": "in_progress",
            "overlapping_files": ["backend/models.py"],
            "reason": "TASK-002 is modifying backend/models.py"
        }
    ],
    "message": "Medium risk: 1 task is editing overlapping files.",
    "recommendation": "Wait for TASK-002 to complete, or coordinate changes."
}
```

### User Warning

```
⚠️  Conflict Detection: TASK-003
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Risk Level: 🟡 MEDIUM

Conflicting Tasks:
  • TASK-002 (in_progress)
    Overlapping Files: backend/models.py
    Reason: Database models are being modified

📋 Recommendation:
  Complete TASK-002 first, or coordinate changes carefully.

Options:
  A) Wait for TASK-002 to complete
  B) Work on a different task (TASK-006 available)
  C) Proceed anyway (requires coordination)

Choose [A/B/C]:
```

**Developer Choice:** `B` → Move to TASK-006 (no conflicts)

### Safe Order Recommendation

```python
# Get safe execution order for multiple tasks
safe_order = recommend_safe_order(["TASK-001", "TASK-002", "TASK-003"])

# Result:
{
    "order": ["TASK-001", "TASK-002", "TASK-003"],
    "parallel_safe": [
        ["TASK-001"],
        ["TASK-002"],
        ["TASK-003"]
    ],
    "conflicts": []
}
```

**Key Points:**

- ✅ Automatic conflict checking before every task
- ✅ Risk level visualization (LOW/MEDIUM/HIGH)
- ✅ User decides whether to proceed
- ✅ Alternative task suggestions provided
- ✅ Safe execution order recommendations

---

## Phase 4: Implementation

### Task Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   Task Execution Flow                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Update Status: pending → in_progress                    │
│     ↓                                                        │
│  2. Search KB: Get relevant context                         │
│     ↓                                                        │
│  3. Implement: Write code based on KB info                  │
│     ↓                                                        │
│  4. Test: Run unit tests                                    │
│     ↓                                                        │
│  5. Update Status: in_progress → completed                  │
│     ↓                                                        │
│  6. Next Task: Get next recommended task                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Claude Code's Internal Process

```python
# 1. Mark task as in_progress
task_update("TASK-001", status="in_progress")

# 2. Search KB for relevant information
kb_results = kb_search("FastAPI Initialization")
# → Returns KB-20251021-001 (FastAPI + React Architecture)

# 3. Implementation
print("TASK-001 (FastAPI Initialization) Implementation.")
print()
print("From KB-20251021-001:")
print("- FastAPI + PostgreSQL + JWT authentication using")
print("- Naming convention: snake_case")
print()

# Create files...
# backend/main.py
# backend/requirements.txt
# backend/config.py

# 4. Run tests
pytest("backend/tests/")

# 5. Mark as completed
task_update("TASK-001", status="completed")

# 6. Get next task
next_task = task_next()
# → TASK-002 (PostgreSQL Database Design)
```

### Developer Sees

```
🚀 TASK-001 (FastAPI Initialization) Implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Knowledge Base Reference:
  KB-20251021-001: FastAPI + React Architecture
    • FastAPI + PostgreSQL + JWT authentication using
    • Naming convention: snake_case

📝 Creating Files:
  ✅ backend/main.py (FastAPI application)
  ✅ backend/requirements.txt (dependencies)
  ✅ backend/config.py (configuration)

🧪 Running Tests:
  ✅ test_main.py::test_app_creation ... PASSED
  ✅ test_main.py::test_health_endpoint ... PASSED

  All tests passed!

✅ TASK-001 Complete! (1h actual)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Progress: 1/10 tasks completed (10%)
⏱️  Time Spent: 1h / 19h estimated

🚀 Next Task: TASK-002 (PostgreSQL Database Design)
```

### KB-Driven Implementation

Claude Code automatically references KB entries during implementation:

```
Implementation Decision Points:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Variable naming:
   KB-20251021-003 → Use snake_case
   ✅ Applied: user_id, todo_items, created_at

2. Authentication:
   KB-20251021-001 → JWT authentication
   ✅ Applied: JWT middleware, token validation

3. Data limits:
   KB-20251021-002 → Max 1000 todos
   ✅ Applied: Pagination with limit=20, max_items=1000
```

**Key Points:**

- ✅ Task status automatically updated
- ✅ KB information used during implementation
- ✅ Tests run automatically
- ✅ Progress tracking shown
- ✅ Next task automatically suggested

---

## Phase 5: Monitoring & Logging

### Operation Logs (v0.10.0)

All operations are logged to `.clauxton/logs/YYYY-MM-DD.log`:

```jsonl
{"timestamp": "2025-10-21T10:00:00", "operation": "task_import_yaml", "level": "info", "details": {"count": 10, "duration": "0.2s"}}
{"timestamp": "2025-10-21T10:15:00", "operation": "task_update", "level": "info", "details": {"task_id": "TASK-001", "changes": {"status": "pending → in_progress"}}}
{"timestamp": "2025-10-21T10:45:00", "operation": "task_update", "level": "info", "details": {"task_id": "TASK-001", "changes": {"status": "in_progress → completed"}}}
{"timestamp": "2025-10-21T11:00:00", "operation": "kb_search", "level": "debug", "details": {"query": "FastAPI Initialization", "results": 1}}
```

### View Logs

**CLI:**

```bash
# View recent logs
clauxton logs --limit 10

# Filter by operation
clauxton logs --operation task_update

# Filter by level
clauxton logs --level info

# Filter by date
clauxton logs --date 2025-10-21
```

**Claude Code (via MCP):**

```python
# Get recent logs
logs = get_recent_logs(limit=10)

# Get specific operation logs
logs = get_recent_logs(operation="task_update", limit=5)
```

### Log Retention

```
┌─────────────────────────────────────────────────────────────┐
│                     Log Retention Policy                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  • Daily log files: .clauxton/logs/YYYY-MM-DD.log           │
│  • Retention: 30 days (automatic cleanup)                   │
│  • Format: JSON Lines (one JSON object per line)            │
│  • Levels: debug, info, warning, error                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Points:**

- ✅ All operations logged automatically
- ✅ JSON Lines format for structured data
- ✅ 30-day automatic retention
- ✅ Filterable by operation, level, date
- ✅ CLI and MCP access

---

## Phase 6: Error Recovery

### Undo Capability (v0.10.0)

Clauxton supports undo for 7 operation types:

```
┌─────────────────────────────────────────────────────────────┐
│                   Undoable Operations                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. task_add          → Delete created task                 │
│  2. task_delete       → Restore deleted task                │
│  3. task_update       → Revert changes                      │
│  4. kb_add            → Delete created entry                │
│  5. kb_delete         → Restore deleted entry               │
│  6. kb_update         → Revert changes                      │
│  7. task_import_yaml  → Delete all imported tasks           │
│                                                              │
│  History: Last 50 operations stored                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Undo Workflow

**Scenario:** Accidentally deleted TASK-001

```bash
# Mistake
clauxton task delete TASK-001
# → TASK-001 deleted

# Realize mistake
clauxton undo
# → Confirmation prompt

# Or via Claude Code
"Undo the last operation"
```

### Undo Confirmation

```
⏪ Undo Last Operation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Operation: task_delete
Task: TASK-001 (FastAPI Initialization)
Timestamp: 2025-10-21 11:30:00

⚠️  This will restore TASK-001 with all its data:
  • Name: FastAPI Initialization
  • Status: completed
  • Priority: high
  • Files: backend/main.py, backend/requirements.txt, backend/config.py
  • Dependencies: None
  • Dependents: TASK-002

Proceed with undo? [Y/n]
```

**Developer:** `Y`

### Undo Result

```
✅ Undo Successful!

Restored Content:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TASK-001: FastAPI Initialization
  Status: completed
  Files: 3 files restored
  Dependencies: TASK-002 dependency link restored

Current task status:
  ✅ TASK-001: completed
  ⏳ TASK-002: pending
  ... (other tasks)
```

### View Undo History

```bash
# Show operation history
clauxton undo --history --limit 10
```

```
📜 Operation History (Last 10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. task_delete (TASK-001)      2025-10-21 11:30:00  [UNDONE]
2. task_update (TASK-003)      2025-10-21 11:15:00
3. task_update (TASK-003)      2025-10-21 11:00:00
4. kb_add (KB-20251021-004)    2025-10-21 10:50:00
5. task_update (TASK-001)      2025-10-21 10:45:00
6. task_update (TASK-001)      2025-10-21 10:15:00
7. task_import_yaml (10 tasks) 2025-10-21 10:00:00
8. kb_add (KB-20251021-003)    2025-10-21 09:58:00
9. kb_add (KB-20251021-002)    2025-10-21 09:57:00
10. kb_add (KB-20251021-001)   2025-10-21 09:56:00

Note: Operations marked [UNDONE] have been reversed.
```

**Key Points:**

- ✅ Undo for 7 operation types
- ✅ Last 50 operations stored
- ✅ Confirmation before undo
- ✅ Full data restoration
- ✅ History view available

---

## Requirement Changes

### Overview

Requirements often change during development. Clauxton handles three types of changes:

```
┌─────────────────────────────────────────────────────────────┐
│                   Requirement Change Types                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Addition:   New features, new constraints               │
│  2. Modification: Spec changes, threshold adjustments        │
│  3. Deletion:   Removed features, scope reduction           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Change Management Workflow

```
┌─────────────────────────────────────────────────────────────┐
│            Requirement Change Management Flow                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Developer states change in natural language             │
│     ↓                                                        │
│  2. Claude Code analyzes impact                             │
│     • Affected KB entries                                   │
│     • Affected tasks                                        │
│     • Dependency changes                                    │
│     ↓                                                        │
│  3. Present summary to developer                            │
│     • KB updates                                            │
│     • Task updates                                          │
│     • Estimate changes                                      │
│     ↓                                                        │
│  4. Developer chooses action                                │
│     A) Automatic update (recommended)                       │
│     B) Manual adjustment                                    │
│     C) Review before deciding                               │
│     ↓                                                        │
│  5. Execute changes + update dependency graph               │
│     ↓                                                        │
│  6. Verify + continue development                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Change Type 1: Addition

**Scenario:** Add tag feature to todos mid-development

**Current State:**
- ✅ TASK-001, TASK-002: completed
- 🔄 TASK-003: in_progress
- ⏳ TASK-004~010: pending

**Developer → Claude Code:**

```
"Actually, I want to add tag functionality to todos.
- Enable multi-tags for each todo
- Enable filtering by tags
- Max 10 tags per todo"
```

**Impact Analysis:**

```
📋 Requirement Change: Feature Addition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

New Feature: Todo Tag Feature

📚 KB Changes:
  ✅ KB-20251021-004 (New): Todo Tag Feature Specification

⚠️  Affected Tasks: 4 tasks

  ✅ TASK-002 (completed) → Reopen required
     • Add tags table to database schema
     • Create migration script
     Files: +alembic/versions/002_add_tags.py

  🔄 TASK-003 (in_progress) → Modification required
     • Add tag API endpoints
     Files: +backend/api/tags.py, +backend/schemas/tag.py
     Estimate: 3h → 4h

  ⏳ TASK-005 (pending) → Modification required
     • Add tag filtering to pagination
     Files: +backend/services/search.py
     Estimate: 1h → 2h

  ⏳ TASK-007 (pending) → Modification required
     • Add tag display UI
     Files: +frontend/src/components/TagBadge.jsx
     Estimate: 2h → 3h

📋 New Tasks:
  • TASK-011: Tag Filtering Search API Implementation (2h)
    Priority: medium
    Depends on: TASK-003

📊 Impact Summary:
  Tasks Modified:    4
  Tasks Added:       1
  Estimate Change:   19h → 22h (+3h)

┌─────────────────────────────────────────────────────────────┐
│  Choose Action:                                              │
│    A) Auto-update tasks (recommended)                       │
│    B) Manual adjustment via CLI                             │
│    C) Review changes first                                  │
└─────────────────────────────────────────────────────────────┘

Your choice [A/B/C]:
```

**Developer:** `A` (auto-update)

**Auto-Update Process:**

```python
# 1. Add new KB entry
kb_add(
    title="Todo Tag Feature",
    category="decision",
    content="Add multi-tags (max 10) to each todo...",
    tags=["feature", "todo", "tags"]
)
# → KB-20251021-004

# 2. Reopen completed task
task_update("TASK-002",
    status="pending",
    description="PostgreSQL DB Design + Add Tags Table",
    files_to_edit=[..., "alembic/versions/002_add_tags.py"]
)

# 3. Update in_progress task
task_update("TASK-003",
    description="Todo CRUD API + Tag API Implementation",
    files_to_edit=[..., "backend/api/tags.py", "backend/schemas/tag.py"],
    estimate=4
)

# 4. Update pending tasks
task_update("TASK-005", ...)
task_update("TASK-007", ...)

# 5. Add new task
task_import_yaml("""
tasks:
  - name: "Tag Filtering Search API Implementation"
    priority: medium
    depends_on: [TASK-003]
    estimate: 2
""")
# → TASK-011

# 6. Recalculate dependency graph
recalculate_dependencies()
```

**Result:**

```
✅ Auto-Update Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 KB: 1 entry added
📋 Tasks: 4 updated, 1 added

Updated Dependency Graph:
  TASK-001 → TASK-002 → TASK-003 → TASK-011 → TASK-005
                      → TASK-004
  TASK-006 → TASK-007 → TASK-009 → TASK-010

📊 New Estimate: 22h (was 19h, +3h)

⚠️  Current Status:
  • TASK-003 remains in_progress
  • Please add tag API implementation
  • After TASK-003, work on TASK-002 (add tags table)

Continue? [Y/n]
```

---

### Change Type 2: Modification

**Scenario:** Change data limit from 1000 to 5000 todos

**Developer → Claude Code:**

```
"Actually, I want to change the todo limit from 1000 to 5000.
Change pagination to 50 items/page."
```

**Impact Analysis:**

```
📋 Requirement Change: Specification Update
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Changed Spec: Todo Data Limit

📚 KB Changes:
  ✏️  KB-20251021-002 (Updated):
     Old: Max 1000 items, 20 items/page
     New: Max 5000 items, 50 items/page

⚠️  Affected Tasks: 3 tasks

  ⏳ TASK-002 (pending) → Database optimization needed
     • Add indexes for 5000-item performance
     • Update constraints
     Files: backend/models.py, backend/database.py

  ⏳ TASK-005 (pending) → Pagination logic change
     • Update page size: 20 → 50
     Files: backend/api/todos.py

  ⏳ TASK-007 (pending) → UI display count change
     • Update frontend pagination: 20 → 50
     Files: frontend/src/components/TodoList.jsx

📊 Impact Summary:
  Tasks Modified:    3
  Tasks Added:       0
  Estimate Change:   19h → 19h (no change)

Auto-update? [Y/n]
```

**Developer:** `Y`

**Result:**

```
✅ Specification Updated!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 KB-20251021-002: Updated
  Max todos: 1000 → 5000
  Page size: 20 → 50

📋 Tasks: 3 updated
  • TASK-002: Add DB optimization notes
  • TASK-005: Update to 50 items/page
  • TASK-007: Update UI to 50 items/page

Development continues with updated specs.
```

---

### Change Type 3: Deletion

**Scenario:** Replace JWT with OAuth2 Google authentication

**Developer → Claude Code:**

```
"Actually, I want to switch from JWT to OAuth2 (Google auth).
Delete all JWT-related tasks and replace with OAuth2 tasks."
```

**Impact Analysis:**

```
📋 Requirement Change: Feature Replacement
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Change: JWT Authentication → OAuth2 Google Authentication

📚 KB Changes:
  ❌ KB-20251021-001 (Deleted): JWT authentication description
  ✅ KB-20251021-005 (New): OAuth2 Google Authentication

⚠️  Affected Tasks: 2 tasks

  ❌ TASK-004 (pending) → To be deleted
     • JWT Authentication Implementation task is no longer needed
     ⚠️  Warning: TASK-010 depends on TASK-004

  ✏️  TASK-009 (pending) → To be modified
     • Change to OAuth2 authentication flow
     Files: +frontend/src/components/GoogleLoginButton.jsx

📋 New Tasks:
  • TASK-012: OAuth2 Google Authentication Implementation (3h)
    Priority: critical
    Depends on: TASK-002
    Files: backend/core/oauth.py, backend/api/auth.py

📋 Dependency Updates:
  • TASK-010: Change dependency TASK-004 → TASK-012

📊 Impact Summary:
  Tasks Deleted:     1 (TASK-004)
  Tasks Modified:    2 (TASK-009, TASK-010)
  Tasks Added:       1 (TASK-012)
  Estimate Change:   19h → 20h (+1h)

┌─────────────────────────────────────────────────────────────┐
│  ⚠️  Warning: Deleting TASK-004 affects dependencies!       │
│     TASK-010 will be updated to depend on TASK-012 instead. │
└─────────────────────────────────────────────────────────────┘

Proceed with deletion and replacement? [Y/n]
```

**Developer:** `Y`

**Auto-Update Process:**

```python
# 1. Delete old KB entry
kb_delete("KB-20251021-001")

# 2. Add new KB entry
kb_add(
    title="Adopt OAuth2 Google Authentication",
    category="decision",
    content="Change from JWT to OAuth2. Reason: Better UX, no password management",
    tags=["oauth2", "google", "authentication"]
)
# → KB-20251021-005

# 3. Delete old task
task_delete("TASK-004")

# 4. Create new task
task_import_yaml("""
tasks:
  - name: "OAuth2 Google Authentication Implementation"
    priority: critical
    depends_on: [TASK-002]
    files_to_edit:
      - backend/api/auth.py
      - backend/core/oauth.py
      - backend/config.py
    estimate: 3
""")
# → TASK-012

# 5. Update dependent tasks
task_update("TASK-009",
    description="OAuth2 Authentication Flow Implementation (Google Auth)",
    files_to_edit=[..., "frontend/src/components/GoogleLoginButton.jsx"]
)

task_update("TASK-010",
    depends_on=["TASK-005", "TASK-009", "TASK-012"]  # TASK-004 → TASK-012
)

# 6. Recalculate dependencies
recalculate_dependencies()
```

**Result:**

```
✅ Feature Replacement Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 KB Changes:
  ❌ KB-20251021-001 (Deleted): JWT Authentication
  ✅ KB-20251021-005 (Added): OAuth2 Google Authentication

📋 Task Changes:
  ❌ TASK-004 (Deleted): JWT Authentication Implementation
  ✅ TASK-012 (Added): OAuth2 Google Authentication Implementation
  ✏️  TASK-009 (Updated): OAuth2 Authentication Flow Implementation
  ✏️  TASK-010 (Updated): Dependency changed

Updated Dependency Graph:
  TASK-001 → TASK-002 → TASK-003 → TASK-011 → TASK-005
                      → TASK-012 (new)
  TASK-006 → TASK-007 → TASK-009 → TASK-010
                       ↑
                   TASK-012

📊 New Estimate: 20h (was 19h, +1h)

Current Tasks:
  ✅ TASK-001, TASK-002: completed
  🔄 TASK-003: in_progress
  ⏳ TASK-005~012: pending (TASK-004 deleted)

Next: Complete TASK-003, then work on TASK-012.
```

---

### Undo Requirement Change

**Scenario:** Developer regrets the OAuth2 change

**Developer → Claude Code:**

```
"Actually, JWT auth was fine. Cancel the OAuth2 change."
```

**Undo Process:**

```
📋 Undo: JWT → OAuth2 Change (6 operations)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recent Operations (in reverse order):
  1. task_update (TASK-010, dependency change)
  2. task_update (TASK-009, OAuth2 implementation)
  3. task_import_yaml (TASK-012 created)
  4. task_delete (TASK-004 deleted)
  5. kb_add (KB-20251021-005 created)
  6. kb_delete (KB-20251021-001 deleted)

⚠️  Undo all 6 operations? [Y/n]
```

**Developer:** `Y`

```
⏪ Undoing operations...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ Undo #1: TASK-010 dependency restored
  ✅ Undo #2: TASK-009 description restored
  ✅ Undo #3: TASK-012 deleted
  ✅ Undo #4: TASK-004 restored
  ✅ Undo #5: KB-20251021-005 deleted
  ✅ Undo #6: KB-20251021-001 restored

✅ Undo Complete! Reverted to JWT configuration.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 KB:
  ✅ KB-20251021-001 (Restored): FastAPI + React + JWT
  ❌ KB-20251021-005 (Deleted): OAuth2 Google

📋 Tasks:
  ✅ TASK-004 (Restored): JWT Authentication Implementation
  ❌ TASK-012 (Deleted): OAuth2 Implementation
  ✅ TASK-009 (Restored): Original API Integration
  ✅ TASK-010 (Restored): Original dependencies

Dependency Graph:
  TASK-001 → TASK-002 → TASK-003 → TASK-011 → TASK-005
                      → TASK-004 (restored)
  TASK-006 → TASK-007 → TASK-009 → TASK-010

Back to original configuration.
```

---

### Change Management Summary

```
┌─────────────────────────────────────────────────────────────┐
│            Requirement Change Capabilities                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ Natural Language: State changes in conversation         │
│  ✅ Impact Analysis: Automatic affected task detection      │
│  ✅ Auto-Update: One-click updates with confirmation        │
│  ✅ Manual Control: CLI override always available           │
│  ✅ Undo Support: Reverse up to 50 operations               │
│  ✅ Dependency Tracking: Automatic graph recalculation      │
│  ✅ Estimate Updates: Automatic time re-estimation          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Points:**

- ✅ Changes expressed in natural language
- ✅ Automatic impact analysis
- ✅ Three action options (auto/manual/review)
- ✅ Dependency graph automatically updated
- ✅ Full undo capability for all changes
- ✅ KB and tasks stay synchronized

---

## Manual Control

### CLI Override

Developers can manually override any Clauxton operation using CLI:

```bash
# ── Knowledge Base ──────────────────────────────────────────

# List all KB entries
clauxton kb list

# Search KB
clauxton kb search "authentication"

# Get specific entry
clauxton kb get KB-20251021-001

# Add entry manually
clauxton kb add \
  --title "Manual Entry" \
  --category architecture \
  --content "Manual content" \
  --tags tag1,tag2

# Update entry
clauxton kb update KB-20251021-001 \
  --title "New Title" \
  --content "New content"

# Delete entry
clauxton kb delete KB-20251021-001


# ── Task Management ─────────────────────────────────────────

# List tasks
clauxton task list                    # All tasks
clauxton task list --status pending   # Filter by status
clauxton task list --priority high    # Filter by priority

# Get task details
clauxton task get TASK-001

# Add task manually
clauxton task add \
  --name "Manual Task" \
  --priority high \
  --files backend/main.py,backend/config.py \
  --depends-on TASK-001 \
  --estimate 2

# Update task
clauxton task update TASK-001 \
  --status completed \
  --description "New description" \
  --estimate 3

# Delete task
clauxton task delete TASK-001

# Get next recommended task
clauxton task next


# ── Conflict Detection ──────────────────────────────────────

# Detect conflicts for a task
clauxton conflict detect TASK-003

# Get safe execution order
clauxton conflict order TASK-001 TASK-002 TASK-003

# Check file conflicts
clauxton conflict check backend/models.py backend/api/todos.py


# ── Import/Export ───────────────────────────────────────────

# Import tasks from YAML
clauxton task import tasks.yml

# Export KB to Markdown
clauxton kb export docs/kb/


# ── Undo/History ────────────────────────────────────────────

# Undo last operation
clauxton undo

# View operation history
clauxton undo --history --limit 20


# ── Logs ────────────────────────────────────────────────────

# View recent logs
clauxton logs --limit 10

# Filter logs
clauxton logs --operation task_update --level info


# ── Configuration ───────────────────────────────────────────

# List configuration
clauxton config list

# Get specific config
clauxton config get confirmation_mode

# Set configuration
clauxton config set confirmation_mode always
clauxton config set task_import_threshold 10
```

### Direct YAML Editing

Advanced users can edit YAML files directly:

```bash
# Edit knowledge base
vim .clauxton/knowledge-base.yml

# Edit tasks
vim .clauxton/tasks.yml

# Edit configuration
vim .clauxton/config.yml
```

**⚠️ Warning:** Direct YAML editing bypasses validation. Use with caution.

### Git Integration

All Clauxton data is Git-friendly:

```bash
# View changes
git diff .clauxton/

# Commit changes
git add .clauxton/
git commit -m "Update tasks and KB"

# View history
git log -p .clauxton/

# Revert changes
git checkout HEAD -- .clauxton/
```

**Key Points:**

- ✅ Full CLI access for all operations
- ✅ Direct YAML editing for advanced users
- ✅ Git integration for version control
- ✅ Claude Code uses MCP (transparent)
- ✅ User has CLI override (control)

---

## Best Practices

### DO ✅

1. **Use Natural Language**
   - Express requirements in conversation
   - Let Claude Code handle the registration
   - Trust automatic task generation

2. **Leverage Automatic Features**
   - Use bulk import for task creation (30x faster)
   - Trust conflict detection before implementation
   - Rely on KB search during coding

3. **Configure Confirmation Mode**
   - `always`: Team development, production
   - `auto`: Individual development (recommended)
   - `never`: Rapid prototyping

4. **Review Before Committing**
   - Check `.clauxton/` changes before git commit
   - Use `git diff .clauxton/` to see modifications
   - Verify task dependencies make sense

5. **Use Undo When Needed**
   - Don't hesitate to undo mistakes
   - Check `clauxton undo --history` to see what happened
   - Undo is instant and safe

6. **Monitor Progress**
   - Check logs periodically: `clauxton logs`
   - Review task status: `clauxton task list`
   - Track estimates vs. actuals

### DON'T ❌

1. **Don't Break the Flow**
   - ❌ Don't manually run CLI commands during conversation
   - ✅ Let Claude Code handle operations transparently
   - Exception: Manual override for corrections

2. **Don't Skip Conflict Checks**
   - ❌ Don't ignore conflict warnings
   - ✅ Wait for conflicting tasks to complete
   - ✅ Or coordinate changes carefully

3. **Don't Edit YAML During Development**
   - ❌ Don't manually edit `.clauxton/*.yml` while Claude Code is running
   - ✅ Use CLI commands instead
   - ✅ Direct editing only for bulk changes or fixes

4. **Don't Ignore KB Information**
   - ❌ Don't implement without checking KB
   - ✅ Reference KB entries for constraints and conventions
   - ✅ Update KB when requirements change

5. **Don't Forget to Update Task Status**
   - ❌ Don't leave tasks stuck in `in_progress`
   - ✅ Claude Code usually handles this automatically
   - ✅ Manually update if needed: `clauxton task update TASK-001 --status completed`

---

## Metrics & Performance

### Performance Benchmarks (v0.10.0)

```
┌─────────────────────────────────────────────────────────────┐
│                  Performance Benchmarks                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Operation           Target        Achieved      Status     │
│  ─────────────────────────────────────────────────────────  │
│  Bulk Import         < 1s (100)   0.2s          ✅ 5x better│
│  KB Export           < 5s (1000)  ~4s           ✅ Met      │
│  KB Search           < 200ms      ~150ms        ✅ Met      │
│  Conflict Detection  < 150ms      ~120ms        ✅ Met      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Improvements

```
┌─────────────────────────────────────────────────────────────┐
│              Before vs After Comparison                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Metric              Before        After        Improvement │
│  ─────────────────────────────────────────────────────────  │
│  Task Creation       5 min         10 sec       30x faster  │
│  User Commands       10 commands   0 commands   100% auto   │
│  Conversation Flow   Broken        Seamless     Natural     │
│  Conflict Detection  Manual        Automatic    Proactive   │
│  Error Recovery      Manual undo   1-click      Instant     │
│  HITL Control        Fixed         3 modes      Flexible    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### User Experience Metrics

```
┌─────────────────────────────────────────────────────────────┐
│                User Experience Improvements                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Aspect              Before        After        Impact      │
│  ─────────────────────────────────────────────────────────  │
│  Manual Operations   10+ per task  0 per task   Eliminated  │
│  Context Loss        Frequent      None         Seamless    │
│  Error Risk          10-20%        < 1%         Safety      │
│  Claude Alignment    70%           95%          Philosophy  │
│  Developer Focus     Tool usage    Code writing Productive  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Test Coverage (v0.10.0)

```
┌─────────────────────────────────────────────────────────────┐
│                    Quality Metrics                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Metric              v0.9.0        v0.10.0      Change      │
│  ─────────────────────────────────────────────────────────  │
│  Tests               390           666          +286 (+73%) │
│  Coverage            94%           92%          -2% (more)  │
│  MCP Tools           15            20           +5 tools    │
│  CLI Commands        ~20           ~27          +7 commands │
│  Documentation       7 guides      10 guides    +3 major    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

### Workflow Overview

Clauxton v0.10.0 provides a **complete, transparent, and safe** development workflow:

1. **Phase 0**: Initialize project with `clauxton init`
2. **Phase 1**: Speak naturally about requirements → Auto KB registration
3. **Phase 2**: Approve task plan → Bulk import (30x faster)
4. **Phase 3**: Automatic conflict detection → Safe execution order
5. **Phase 4**: Implement with KB context → Auto status updates
6. **Phase 5**: Monitor progress via logs → 30-day retention
7. **Phase 6**: Undo mistakes instantly → Up to 50 operations

### Key Advantages

```
┌─────────────────────────────────────────────────────────────┐
│                    Clauxton Advantages                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🚀 Performance:   30x faster task creation                 │
│  🤖 Automation:    Zero manual commands during flow         │
│  🛡️  Safety:        Undo, backups, conflict detection       │
│  🔧 Control:       CLI override always available            │
│  📊 Visibility:    Logs, history, Git integration           │
│  🎯 Flexibility:   3 confirmation modes (always/auto/never) │
│  🔄 Adaptability:  Handle requirement changes seamlessly    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Developer Experience

**Before Clauxton:**
- Manual task tracking
- Frequent context loss
- High error risk
- Repetitive CLI commands

**After Clauxton v0.10.0:**
- Natural conversation
- Seamless workflow
- Automatic safety
- Focus on coding

---

## Next Steps

### For New Users

1. Read [Quick Start Guide](quick-start.md)
2. Follow [MCP Integration Guide](MCP_INTEGRATION_GUIDE.md)
3. Review [YAML Task Format](YAML_TASK_FORMAT.md)
4. Practice with a small project

### For Existing Users

1. Read [Migration Guide](MIGRATION_v0.10.0.md)
2. Configure confirmation mode
3. Try bulk task import
4. Explore undo capability

### For Advanced Users

1. Read [Error Handling Guide](ERROR_HANDLING_GUIDE.md)
2. Review [Configuration Guide](configuration-guide.md)
3. Study [Performance Guide](performance-guide.md)
4. Contribute to [Development](development.md)

---

## Related Documentation

- [Quick Start Guide](quick-start.md) - Get started in 5 minutes
- [MCP Integration Guide](MCP_INTEGRATION_GUIDE.md) - Claude Code setup
- [YAML Task Format](YAML_TASK_FORMAT.md) - Task YAML specification
- [Error Handling Guide](ERROR_HANDLING_GUIDE.md) - Troubleshooting
- [Configuration Guide](configuration-guide.md) - Configuration options
- [Migration Guide](MIGRATION_v0.10.0.md) - Upgrade from v0.9.0

---

**Version**: v0.10.0
**Last Updated**: 2025-10-21
**Feedback**: https://github.com/nakishiyaman/clauxton/issues
