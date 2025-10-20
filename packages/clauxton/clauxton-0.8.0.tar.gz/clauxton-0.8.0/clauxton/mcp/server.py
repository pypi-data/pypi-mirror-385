"""
MCP Server for Clauxton Knowledge Base.

Provides tools for interacting with the Knowledge Base through
the Model Context Protocol.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from mcp.server.fastmcp import FastMCP

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


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
