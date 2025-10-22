"""
MCP Server for Clauxton Knowledge Base.

Provides tools for interacting with the Knowledge Base through
the Model Context Protocol.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from mcp.server.fastmcp import FastMCP

from clauxton.core.conflict_detector import ConflictDetector
from clauxton.core.knowledge_base import KnowledgeBase
from clauxton.core.models import KnowledgeBaseEntry, Task
from clauxton.core.task_manager import TaskManager

# Create MCP server instance
mcp = FastMCP("Clauxton")


@mcp.tool()
def kb_search(
    query: str,
    category: Optional[str] = None,
    limit: int = 10,
) -> List[dict[str, Any]]:
    """
    Search the Knowledge Base for entries matching the query.

    Args:
        query: Search query string
        category: Optional category filter (architecture, constraint, decision, pattern, convention)
        limit: Maximum number of results to return (default: 10)

    Returns:
        List of matching Knowledge Base entries with id, title, category, content, tags
    """
    kb = KnowledgeBase(Path.cwd())
    results = kb.search(query, category=category, limit=limit)
    return [
        {
            "id": entry.id,
            "title": entry.title,
            "category": entry.category,
            "content": entry.content,
            "tags": entry.tags,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
        }
        for entry in results
    ]


@mcp.tool()
def kb_add(
    title: str,
    category: str,
    content: str,
    tags: Optional[List[str]] = None,
) -> dict[str, str]:
    """
    Add a new entry to the Knowledge Base.

    Args:
        title: Entry title (max 50 characters)
        category: Entry category (architecture, constraint, decision, pattern, convention)
        content: Entry content (detailed description)
        tags: Optional list of tags for categorization

    Returns:
        Dictionary with id and success message
    """
    kb = KnowledgeBase(Path.cwd())

    # Generate entry ID
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    entries = kb.list_all()
    same_day_entries = [e for e in entries if e.id.startswith(f"KB-{date_str}")]
    sequence = len(same_day_entries) + 1
    entry_id = f"KB-{date_str}-{sequence:03d}"

    # Create entry
    entry = KnowledgeBaseEntry(
        id=entry_id,
        title=title,
        category=category,  # type: ignore[arg-type]
        content=content,
        tags=tags or [],
        created_at=now,
        updated_at=now,
        author=None,
    )

    kb.add(entry)
    return {
        "id": entry_id,
        "message": f"Successfully added entry: {entry_id}",
    }


@mcp.tool()
def kb_list(category: Optional[str] = None) -> List[dict[str, Any]]:
    """
    List all Knowledge Base entries.

    Args:
        category: Optional category filter (architecture, constraint, decision, pattern, convention)

    Returns:
        List of all Knowledge Base entries
    """
    kb = KnowledgeBase(Path.cwd())
    entries = kb.list_all()

    # Filter by category if specified
    if category:
        entries = [e for e in entries if e.category == category]

    return [
        {
            "id": entry.id,
            "title": entry.title,
            "category": entry.category,
            "content": entry.content,
            "tags": entry.tags,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
        }
        for entry in entries
    ]


@mcp.tool()
def kb_get(entry_id: str) -> dict[str, Any]:
    """
    Get a specific Knowledge Base entry by ID.

    Args:
        entry_id: Entry ID (e.g., KB-20251019-001)

    Returns:
        Knowledge Base entry details
    """
    kb = KnowledgeBase(Path.cwd())
    entry = kb.get(entry_id)
    return {
        "id": entry.id,
        "title": entry.title,
        "category": entry.category,
        "content": entry.content,
        "tags": entry.tags,
        "created_at": entry.created_at.isoformat(),
        "updated_at": entry.updated_at.isoformat(),
        "version": entry.version,
    }


@mcp.tool()
def kb_update(
    entry_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> dict[str, Any]:
    """
    Update an existing Knowledge Base entry.

    Args:
        entry_id: Entry ID to update (e.g., KB-20251019-001)
        title: New title (optional)
        content: New content (optional)
        category: New category (optional)
        tags: New tags list (optional)

    Returns:
        Updated entry details including new version number
    """
    kb = KnowledgeBase(Path.cwd())

    # Prepare updates dictionary
    updates: dict[str, Any] = {}
    if title is not None:
        updates["title"] = title
    if content is not None:
        updates["content"] = content
    if category is not None:
        updates["category"] = category
    if tags is not None:
        updates["tags"] = tags

    if not updates:
        return {
            "error": "No fields to update",
            "message": "Provide at least one field to update",
        }

    # Update entry
    updated_entry = kb.update(entry_id, updates)

    return {
        "id": updated_entry.id,
        "title": updated_entry.title,
        "category": updated_entry.category,
        "content": updated_entry.content,
        "tags": updated_entry.tags,
        "version": updated_entry.version,
        "updated_at": updated_entry.updated_at.isoformat(),
        "message": f"Successfully updated entry: {entry_id}",
    }


@mcp.tool()
def kb_delete(entry_id: str) -> dict[str, str]:
    """
    Delete a Knowledge Base entry.

    Args:
        entry_id: Entry ID to delete (e.g., KB-20251019-001)

    Returns:
        Success message
    """
    kb = KnowledgeBase(Path.cwd())

    # Get entry title for confirmation message
    entry = kb.get(entry_id)
    entry_title = entry.title

    # Delete entry
    kb.delete(entry_id)

    return {
        "id": entry_id,
        "message": f"Successfully deleted entry: {entry_id} ({entry_title})",
    }


@mcp.tool()
def task_add(
    name: str,
    description: Optional[str] = None,
    priority: str = "medium",
    depends_on: Optional[List[str]] = None,
    files: Optional[List[str]] = None,
    kb_refs: Optional[List[str]] = None,
    estimate: Optional[float] = None,
) -> dict[str, Any]:
    """
    Add a new task to the task list.

    Args:
        name: Task name (required)
        description: Detailed task description
        priority: Task priority (low, medium, high, critical) - default: medium
        depends_on: List of task IDs this task depends on
        files: List of files this task will modify
        kb_refs: List of related Knowledge Base entry IDs
        estimate: Estimated hours to complete

    Returns:
        Dictionary with task_id and success message
    """
    tm = TaskManager(Path.cwd())

    # Generate task ID
    task_id = tm.generate_task_id()

    # Create task object
    task = Task(
        id=task_id,
        name=name,
        description=description,
        status="pending",
        priority=priority,  # type: ignore[arg-type]
        depends_on=depends_on or [],
        files_to_edit=files or [],
        related_kb=kb_refs or [],
        estimated_hours=estimate,
        actual_hours=None,
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
    )

    tm.add(task)
    return {
        "task_id": task_id,
        "message": f"Successfully added task: {task_id}",
        "name": name,
        "priority": priority,
    }


@mcp.tool()
def task_list(
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> List[dict[str, Any]]:
    """
    List all tasks with optional filters.

    Args:
        status: Filter by status (pending, in_progress, completed, blocked)
        priority: Filter by priority (low, medium, high, critical)

    Returns:
        List of tasks with details
    """
    tm = TaskManager(Path.cwd())
    tasks = tm.list_all(
        status=status,  # type: ignore[arg-type]
        priority=priority,  # type: ignore[arg-type]
    )

    return [
        {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "depends_on": task.depends_on,
            "files_to_edit": task.files_to_edit,
            "related_kb": task.related_kb,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
        for task in tasks
    ]


@mcp.tool()
def task_get(task_id: str) -> dict[str, Any]:
    """
    Get detailed information about a specific task.

    Args:
        task_id: Task ID (e.g., TASK-001)

    Returns:
        Task details
    """
    tm = TaskManager(Path.cwd())
    task = tm.get(task_id)

    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "depends_on": task.depends_on,
        "files_to_edit": task.files_to_edit,
        "related_kb": task.related_kb,
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


@mcp.tool()
def task_update(
    task_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> dict[str, str]:
    """
    Update a task's fields.

    Args:
        task_id: Task ID to update
        status: New status (pending, in_progress, completed, blocked)
        priority: New priority (low, medium, high, critical)
        name: New task name
        description: New task description

    Returns:
        Dictionary with success message and updated fields
    """
    tm = TaskManager(Path.cwd())

    updates: dict[str, Any] = {}
    if status:
        updates["status"] = status
        # Auto-set timestamps
        if status == "in_progress":
            updates["started_at"] = datetime.now()
        elif status == "completed":
            updates["completed_at"] = datetime.now()
    if priority:
        updates["priority"] = priority
    if name:
        updates["name"] = name
    if description:
        updates["description"] = description

    tm.update(task_id, updates)
    return {
        "task_id": task_id,
        "message": f"Successfully updated task: {task_id}",
        "updates": str(updates),
    }


@mcp.tool()
def task_next() -> Optional[dict[str, Any]]:
    """
    Get the next recommended task to work on.

    Returns highest priority task whose dependencies are completed.

    Returns:
        Next task details, or None if no tasks are available
    """
    tm = TaskManager(Path.cwd())
    next_task = tm.get_next_task()

    if not next_task:
        return None

    return {
        "id": next_task.id,
        "name": next_task.name,
        "description": next_task.description,
        "priority": next_task.priority,
        "files_to_edit": next_task.files_to_edit,
        "estimated_hours": next_task.estimated_hours,
        "related_kb": next_task.related_kb,
    }


@mcp.tool()
def task_delete(task_id: str) -> dict[str, str]:
    """
    Delete a task.

    Args:
        task_id: Task ID to delete

    Returns:
        Dictionary with success message
    """
    tm = TaskManager(Path.cwd())
    tm.delete(task_id)
    return {
        "task_id": task_id,
        "message": f"Successfully deleted task: {task_id}",
    }


@mcp.tool()
def task_import_yaml(
    yaml_content: str,
    dry_run: bool = False,
    skip_validation: bool = False,
    skip_confirmation: bool = False,
    on_error: str = "rollback",
) -> dict[str, Any]:
    """
    Import multiple tasks from YAML content.

    This tool enables bulk task creation from YAML format, with automatic
    validation, dependency checking, and circular dependency detection.

    Args:
        yaml_content: YAML string containing tasks
        dry_run: If True, validate only without creating tasks (default: False)
        skip_validation: If True, skip dependency validation (default: False)
        skip_confirmation: If True, skip confirmation prompt (default: False)
        on_error: Error recovery strategy (default: "rollback")
            - "rollback": Revert all changes on error (transactional)
            - "skip": Skip failed tasks, continue with others
            - "abort": Stop immediately on first error

    Returns:
        Dictionary with:
            - status: "success" | "error" | "confirmation_required" | "partial"
            - imported: Number of tasks imported (0 if dry_run)
            - task_ids: List of created task IDs
            - errors: List of error messages (if any)
            - next_task: Recommended next task ID
            - confirmation_required: True if confirmation needed (optional)
            - preview: Preview of tasks to import (optional)

    Example:
        >>> yaml_content = '''
        ... tasks:
        ...   - name: "Setup FastAPI"
        ...     priority: high
        ...     files_to_edit:
        ...       - main.py
        ...   - name: "Create API"
        ...     priority: high
        ...     depends_on:
        ...       - TASK-001
        ... '''
        >>> task_import_yaml(yaml_content)
        {
            "status": "success",
            "imported": 2,
            "task_ids": ["TASK-001", "TASK-002"],
            "errors": [],
            "next_task": "TASK-001"
        }

    YAML Format:
        tasks:
          - name: "Task name" (required)
            description: "Detailed description" (optional)
            priority: high | medium | low | critical (optional, default: medium)
            depends_on:  (optional)
              - TASK-001
            files_to_edit:  (optional)
              - src/file1.py
              - src/file2.py
            related_kb:  (optional)
              - KB-20251019-001
            estimated_hours: 4.5 (optional)

    Notes:
        - Task IDs are auto-generated (TASK-001, TASK-002, etc.)
        - Circular dependencies are automatically detected
        - Dependencies are validated to exist
        - Use dry_run=True to validate before creating tasks
    """
    tm = TaskManager(Path.cwd())
    result = tm.import_yaml(
        yaml_content=yaml_content,
        dry_run=dry_run,
        skip_validation=skip_validation,
        skip_confirmation=skip_confirmation,
        on_error=on_error,
    )
    return result


# ============================================================================
# Conflict Detection Tools (Phase 2)
# ============================================================================


@mcp.tool()
def detect_conflicts(task_id: str) -> dict[str, Any]:
    """
    Detect potential conflicts for a task.

    Analyzes the given task against all in_progress tasks to identify
    file overlap conflicts that could lead to merge issues.

    Args:
        task_id: Task ID to check for conflicts (e.g., TASK-001)

    Returns:
        Dictionary with conflict count and list of conflict details

    Example:
        >>> detect_conflicts("TASK-002")
        {
            "task_id": "TASK-002",
            "task_name": "Add OAuth support",
            "conflict_count": 1,
            "status": "conflicts_detected",
            "summary": "Found 1 conflict with in_progress tasks",
            "max_risk_level": "medium",
            "conflicts": [
                {
                    "task_a_id": "TASK-002",
                    "task_b_id": "TASK-001",
                    "task_b_name": "Refactor JWT authentication",
                    "conflict_type": "file_overlap",
                    "risk_level": "medium",
                    "risk_score": 0.67,
                    "overlapping_files": ["src/api/auth.py"],
                    "details": "Both tasks edit: src/api/auth.py. ...",
                    "recommendation": "Complete TASK-002 before starting TASK-001, ..."
                }
            ]
        }
    """
    tm = TaskManager(Path.cwd())
    detector = ConflictDetector(tm)

    # Get task to include its name in response
    task = tm.get(task_id)
    conflicts = detector.detect_conflicts(task_id)

    # Calculate max risk level
    max_risk = "low"
    if conflicts:
        risk_levels = [c.risk_level for c in conflicts]
        if "high" in risk_levels:
            max_risk = "high"
        elif "medium" in risk_levels:
            max_risk = "medium"

    # Determine status and summary message
    if not conflicts:
        status = "no_conflicts"
        summary = "No conflicts detected. Safe to start working on this task."
    else:
        status = "conflicts_detected"
        summary = (
            f"Found {len(conflicts)} conflict(s) with in_progress tasks. "
            f"Max risk: {max_risk}."
        )

    return {
        "task_id": task_id,
        "task_name": task.name,
        "conflict_count": len(conflicts),
        "status": status,
        "summary": summary,
        "max_risk_level": max_risk,
        "conflicts": [
            {
                "task_a_id": c.task_a_id,
                "task_b_id": c.task_b_id,
                "task_b_name": tm.get(c.task_b_id).name,  # Include conflicting task name
                "conflict_type": c.conflict_type,
                "risk_level": c.risk_level,
                "risk_score": c.risk_score,
                "overlapping_files": c.overlapping_files,
                "details": c.details,
                "recommendation": c.recommendation,
            }
            for c in conflicts
        ],
    }


@mcp.tool()
def recommend_safe_order(task_ids: List[str]) -> dict[str, Any]:
    """
    Recommend safe execution order for tasks.

    Uses topological sort based on dependencies and conflict analysis
    to suggest an order that minimizes merge conflicts.

    Args:
        task_ids: List of task IDs to order (e.g., ["TASK-001", "TASK-002"])

    Returns:
        Dictionary with recommended execution order

    Example:
        >>> recommend_safe_order(["TASK-001", "TASK-002", "TASK-003"])
        {
            "task_count": 3,
            "recommended_order": ["TASK-001", "TASK-002", "TASK-003"],
            "task_details": [
                {"id": "TASK-001", "name": "Task 1", "priority": "high"},
                {"id": "TASK-002", "name": "Task 2", "priority": "medium"},
                {"id": "TASK-003", "name": "Task 3", "priority": "low"}
            ],
            "has_dependencies": true,
            "message": "Execute tasks in the order shown to minimize conflicts"
        }
    """
    tm = TaskManager(Path.cwd())
    detector = ConflictDetector(tm)

    order = detector.recommend_safe_order(task_ids)

    # Get task details for better context
    task_details = []
    has_dependencies = False
    for task_id in order:
        task = tm.get(task_id)
        task_details.append({
            "id": task.id,
            "name": task.name,
            "priority": task.priority,
            "files_count": len(task.files_to_edit),
        })
        if task.depends_on:
            has_dependencies = True

    # Create descriptive message
    if not order:
        message = "No tasks to order"
    elif has_dependencies:
        message = "Execution order respects dependencies and minimizes conflicts"
    else:
        message = "Execution order minimizes file conflicts (no dependencies found)"

    return {
        "task_count": len(order),
        "recommended_order": order,
        "task_details": task_details,
        "has_dependencies": has_dependencies,
        "message": message,
    }


@mcp.tool()
def check_file_conflicts(files: List[str]) -> dict[str, Any]:
    """
    Check which tasks are currently editing specific files.

    Useful for determining if files are available for editing or
    if coordination with other tasks is needed.

    Args:
        files: List of file paths to check (e.g., ["src/api/auth.py"])

    Returns:
        Dictionary with conflicting task IDs and details

    Example:
        >>> check_file_conflicts(["src/api/auth.py", "src/models/user.py"])
        {
            "file_count": 2,
            "files": ["src/api/auth.py", "src/models/user.py"],
            "conflicting_tasks": ["TASK-001", "TASK-003"],
            "task_details": [
                {"id": "TASK-001", "name": "Refactor auth", "files": ["src/api/auth.py"]},
                {"id": "TASK-003", "name": "Update model", "files": ["src/models/user.py"]}
            ],
            "file_map": {
                "src/api/auth.py": ["TASK-001"],
                "src/models/user.py": ["TASK-003"]
            },
            "all_available": false,
            "message": "2 in_progress task(s) are editing these files"
        }
    """
    tm = TaskManager(Path.cwd())
    detector = ConflictDetector(tm)

    conflicting_tasks = detector.check_file_conflicts(files)

    # Get task details for conflicting tasks
    task_details = []
    file_map: dict[str, list[str]] = {file: [] for file in files}

    for task_id in conflicting_tasks:
        task = tm.get(task_id)
        # Find which files this task is editing from the checked files
        task_files = [f for f in files if f in task.files_to_edit]
        task_details.append({
            "id": task.id,
            "name": task.name,
            "files": task_files,
            "priority": task.priority,
        })
        # Update file map
        for file in task_files:
            file_map[file].append(task.id)

    # Determine status
    all_available = len(conflicting_tasks) == 0

    # Create descriptive message
    if not files:
        message = "No files specified"
    elif all_available:
        message = f"All {len(files)} file(s) are available for editing"
    else:
        locked_count = len([f for f in files if file_map[f]])
        message = (
            f"{len(conflicting_tasks)} in_progress task(s) "
            f"editing {locked_count}/{len(files)} file(s)"
        )

    return {
        "file_count": len(files),
        "files": files,
        "conflicting_tasks": conflicting_tasks,
        "task_details": task_details,
        "file_map": file_map,
        "all_available": all_available,
        "message": message,
    }


@mcp.tool()
def undo_last_operation() -> dict[str, Any]:
    """
    Undo the last operation performed by Clauxton.

    This tool allows users to revert the most recent operation such as:
    - task_import (deletes imported tasks)
    - task_add (deletes the task)
    - task_delete (restores the task)
    - task_update (restores previous state)
    - kb_add (deletes the entry)
    - kb_delete (restores the entry)
    - kb_update (restores previous state)

    Returns:
        Dictionary with undo result status and details

    Example:
        >>> # After importing 10 tasks
        >>> undo_last_operation()
        {
            "status": "success",
            "operation_type": "task_import",
            "description": "Imported 10 tasks from YAML",
            "details": {
                "deleted_tasks": 10,
                "task_ids": ["TASK-001", "TASK-002", ...]
            },
            "message": "Undone: Imported 10 tasks from YAML (deleted 10 tasks)"
        }
    """
    from clauxton.core.operation_history import OperationHistory

    history = OperationHistory(Path.cwd())
    result = history.undo_last_operation()

    return result


@mcp.tool()
def get_recent_operations(limit: int = 10) -> dict[str, Any]:
    """
    Get recent operations that can be undone.

    This tool shows the operation history, allowing users to see
    what operations have been performed recently.

    Args:
        limit: Maximum number of operations to return (default: 10)

    Returns:
        Dictionary with list of recent operations

    Example:
        >>> get_recent_operations(limit=5)
        {
            "status": "success",
            "count": 5,
            "operations": [
                {
                    "operation_type": "task_import",
                    "timestamp": "2025-10-20T15:30:00",
                    "description": "Imported 10 tasks from YAML"
                },
                ...
            ]
        }
    """
    from clauxton.core.operation_history import OperationHistory

    history = OperationHistory(Path.cwd())
    operations = history.list_operations(limit=limit)

    return {
        "status": "success",
        "count": len(operations),
        "operations": [
            {
                "operation_type": op.operation_type,
                "timestamp": op.timestamp,
                "description": op.description,
            }
            for op in operations
        ],
    }


@mcp.tool()
def kb_export_docs(
    output_dir: str,
    category: Optional[str] = None,
) -> dict[str, Any]:
    """
    Export Knowledge Base entries to Markdown documentation files.

    Creates one Markdown file per category (or a single file if category specified).
    Decision entries use ADR (Architecture Decision Record) format.
    Other categories use standard documentation format.

    Args:
        output_dir: Directory path to write Markdown files to (will be created if doesn't exist)
        category: Optional category filter to export only specific category
            Values: "architecture", "constraint", "decision", "pattern", "convention"

    Returns:
        Dictionary with export statistics and file list

    Example:
        >>> kb_export_docs(output_dir="./docs/kb")
        {
            "status": "success",
            "total_entries": 15,
            "files_created": 5,
            "categories": ["architecture", "decision", "constraint"],
            "output_dir": "./docs/kb",
            "files": [
                "architecture.md",
                "decision.md",
                "constraint.md"
            ],
            "message": "Exported 15 entries to 5 file(s) in ./docs/kb"
        }

        >>> kb_export_docs(output_dir="./docs/adr", category="decision")
        {
            "status": "success",
            "total_entries": 3,
            "files_created": 1,
            "categories": ["decision"],
            "output_dir": "./docs/adr",
            "files": ["decision.md"],
            "message": "Exported 3 decision entries to ./docs/adr/decision.md"
        }

    Use Cases:
        1. **Documentation Generation**: Export KB to readable Markdown docs for team
        2. **ADR Archive**: Export decision entries as Architecture Decision Records
        3. **Knowledge Sharing**: Share project context with new team members
        4. **Version Control**: Commit exported docs to Git for versioning
        5. **Static Site**: Use exported Markdown in documentation sites (MkDocs, etc.)

    Notes:
        - Decision entries use ADR format (Context, Decision, Consequences)
        - Other categories use standard format (Title, Content, Metadata)
        - Files are named by category (e.g., architecture.md, decision.md)
        - Output directory will be created if it doesn't exist
        - Existing files will be overwritten
        - Entries are sorted by creation date within each file
    """
    kb = KnowledgeBase(Path.cwd())
    output_path = Path(output_dir)

    try:
        stats = kb.export_to_markdown(output_path, category=category)

        # Generate list of created files
        files = [f"{cat}.md" for cat in stats["categories"]]

        # Create descriptive message
        if category:
            message = (
                f"Exported {stats['total_entries']} {category} entries "
                f"to {output_dir}/{category}.md"
            )
        else:
            message = (
                f"Exported {stats['total_entries']} entries "
                f"to {stats['files_created']} file(s) in {output_dir}"
            )

        return {
            "status": "success",
            "total_entries": stats["total_entries"],
            "files_created": stats["files_created"],
            "categories": stats["categories"],
            "output_dir": output_dir,
            "files": files,
            "message": message,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to export KB: {e}",
        }


# ============================================================================
# Logging Tools (v0.10.0 Week 2 Day 7)
# ============================================================================


@mcp.tool()
def get_recent_logs(
    limit: int = 100,
    operation: Optional[str] = None,
    level: Optional[str] = None,
    days: int = 7,
) -> dict[str, Any]:
    """
    Get recent log entries from Clauxton logs.

    Returns structured log entries from the last N days, with optional
    filtering by operation type and log level.

    Args:
        limit: Maximum number of entries to return (default: 100)
        operation: Filter by operation type (optional)
            Examples: "task_add", "kb_search", "task_import_yaml"
        level: Filter by log level (optional)
            Values: "debug", "info", "warning", "error"
        days: Number of days to look back (default: 7)

    Returns:
        Dictionary with status, count, and list of log entries

    Example:
        >>> get_recent_logs(limit=10, operation="task_add", level="info")
        {
            "status": "success",
            "count": 5,
            "logs": [
                {
                    "timestamp": "2025-10-21T10:30:00",
                    "operation": "task_add",
                    "level": "info",
                    "message": "Added task TASK-001",
                    "metadata": {"task_id": "TASK-001", "priority": "high"}
                },
                ...
            ]
        }

    Use Cases:
        1. **Debugging**: Review recent operations to troubleshoot issues
        2. **Audit Trail**: Track all modifications to KB and tasks
        3. **Operation History**: See what Claude Code has done recently
        4. **Error Investigation**: Filter error-level logs to diagnose problems

    Notes:
        - Log files are stored in .clauxton/logs/ directory
        - Logs are automatically rotated after 30 days
        - Logs use JSON Lines format for structured data
        - Timestamps are in ISO 8601 format
    """
    from clauxton.utils.logger import ClauxtonLogger

    logger = ClauxtonLogger(Path.cwd())
    logs = logger.get_recent_logs(
        limit=limit,
        operation=operation,
        level=level,
        days=days,
    )

    return {
        "status": "success",
        "count": len(logs),
        "logs": logs,
    }


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
