"""CLI commands for task management."""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import click

from clauxton.core.task_manager import TaskManager


@click.group()
def task() -> None:
    """Task management commands."""
    pass


@task.command("add")
@click.option("--name", prompt="Task name", help="Task name")
@click.option("--description", help="Task description")
@click.option(
    "--priority",
    type=click.Choice(["low", "medium", "high", "critical"], case_sensitive=False),
    default="medium",
    help="Task priority",
)
@click.option("--depends-on", help="Comma-separated list of task IDs this depends on")
@click.option("--files", help="Comma-separated list of files to edit")
@click.option("--kb-refs", help="Comma-separated list of related KB entry IDs")
@click.option("--estimate", type=float, help="Estimated hours to complete")
def add_task(
    name: str,
    description: Optional[str],
    priority: str,
    depends_on: Optional[str],
    files: Optional[str],
    kb_refs: Optional[str],
    estimate: Optional[float],
) -> None:
    """
    Add a new task.

    Example:
        $ clauxton task add --name "Setup database" --priority high
        $ clauxton task add --name "Add API endpoint" --depends-on TASK-001
    """
    from clauxton.core.models import Task

    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    tm = TaskManager(root_dir)

    # Generate task ID
    task_id = tm.generate_task_id()

    # Parse dependencies
    dependencies = []
    if depends_on:
        dependencies = [d.strip() for d in depends_on.split(",") if d.strip()]

    # Parse files
    files_list = []
    if files:
        files_list = [f.strip() for f in files.split(",") if f.strip()]

    # Parse KB refs
    kb_list = []
    if kb_refs:
        kb_list = [k.strip() for k in kb_refs.split(",") if k.strip()]

    # Create task
    task_obj = Task(
        id=task_id,
        name=name,
        description=description,
        status="pending",
        priority=priority.lower(),  # type: ignore[arg-type]
        depends_on=dependencies,
        files_to_edit=files_list,
        related_kb=kb_list,
        estimated_hours=estimate,
        actual_hours=None,
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
    )

    try:
        tm.add(task_obj)
        click.echo(click.style(f"✓ Added task: {task_id}", fg="green"))
        click.echo(f"  Name: {name}")
        click.echo(f"  Priority: {priority}")
        if dependencies:
            click.echo(f"  Depends on: {', '.join(dependencies)}")
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@task.command("import")
@click.argument("yaml_file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Validate without creating tasks")
@click.option("--skip-validation", is_flag=True, help="Skip dependency validation")
def import_tasks(yaml_file: str, dry_run: bool, skip_validation: bool) -> None:
    """
    Import multiple tasks from YAML file.

    This command enables bulk task creation from YAML format,
    with automatic validation and circular dependency detection.

    Example:
        $ clauxton task import tasks.yml
        $ clauxton task import tasks.yml --dry-run
        $ clauxton task import tasks.yml --skip-validation

    YAML Format:
        tasks:
          - name: "Setup FastAPI"
            priority: high
            files_to_edit:
              - main.py
              - config.py
          - name: "Create API endpoints"
            priority: high
            depends_on:
              - TASK-001
            files_to_edit:
              - api/users.py
    """
    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    tm = TaskManager(root_dir)

    # Read YAML file
    try:
        yaml_path = Path(yaml_file)
        yaml_content = yaml_path.read_text(encoding="utf-8")
    except Exception as e:
        click.echo(click.style(f"Error reading file: {e}", fg="red"))
        raise click.Abort()

    # Import tasks
    try:
        result = tm.import_yaml(
            yaml_content=yaml_content,
            dry_run=dry_run,
            skip_validation=skip_validation,
        )

        if result["status"] == "error":
            click.echo(click.style("✗ Import failed", fg="red"))
            click.echo()
            for error in result["errors"]:
                click.echo(click.style(f"  • {error}", fg="red"))
            raise click.Abort()

        # Success
        if dry_run:
            click.echo(click.style("✓ Validation successful (dry-run)", fg="green"))
            click.echo(f"  Would import {len(result['task_ids'])} tasks:")
            for task_id in result["task_ids"]:
                click.echo(f"    - {task_id}")
        else:
            click.echo(click.style(f"✓ Imported {result['imported']} tasks", fg="green"))
            click.echo()
            for task_id in result["task_ids"]:
                click.echo(f"  • {task_id}")

            if result.get("next_task"):
                click.echo()
                click.echo(click.style("📋 Next task to work on:", bold=True))
                click.echo(f"  {result['next_task']}")
                click.echo()
                click.echo("  Start working:")
                click.echo(f"    clauxton task update {result['next_task']} --status in_progress")

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@task.command("list")
@click.option(
    "--status",
    type=click.Choice(["pending", "in_progress", "completed", "blocked"]),
    help="Filter by status",
)
@click.option(
    "--priority",
    type=click.Choice(["low", "medium", "high", "critical"]),
    help="Filter by priority",
)
def list_tasks(status: Optional[str], priority: Optional[str]) -> None:
    """
    List all tasks.

    Example:
        $ clauxton task list
        $ clauxton task list --status pending
        $ clauxton task list --priority high
    """
    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    tm = TaskManager(root_dir)

    tasks = tm.list_all(
        status=status,  # type: ignore[arg-type]
        priority=priority,  # type: ignore[arg-type]
    )

    if not tasks:
        click.echo("No tasks found")
        return

    click.echo(click.style(f"\nTasks ({len(tasks)}):\n", bold=True))

    for task_obj in tasks:
        click.echo(click.style(f"  {task_obj.id}", fg="cyan"))
        click.echo(f"    Name: {task_obj.name}")
        click.echo(f"    Status: {task_obj.status}")
        click.echo(f"    Priority: {task_obj.priority}")
        if task_obj.depends_on:
            click.echo(f"    Depends on: {', '.join(task_obj.depends_on)}")
        if task_obj.files_to_edit:
            click.echo(f"    Files: {len(task_obj.files_to_edit)} files")
        click.echo()


@task.command("get")
@click.argument("task_id")
def get_task(task_id: str) -> None:
    """
    Get task details by ID.

    Example:
        $ clauxton task get TASK-001
    """
    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    tm = TaskManager(root_dir)

    try:
        task_obj = tm.get(task_id)

        click.echo(click.style(f"\n{task_obj.id}", fg="cyan", bold=True))
        click.echo(f"Name: {task_obj.name}")
        click.echo(f"Status: {task_obj.status}")
        click.echo(f"Priority: {task_obj.priority}")

        if task_obj.description:
            click.echo(f"\nDescription:\n{task_obj.description}")

        if task_obj.depends_on:
            click.echo(f"\nDepends on: {', '.join(task_obj.depends_on)}")

        if task_obj.files_to_edit:
            click.echo("\nFiles to edit:")
            for file in task_obj.files_to_edit:
                click.echo(f"  - {file}")

        if task_obj.related_kb:
            click.echo(f"\nRelated KB entries: {', '.join(task_obj.related_kb)}")

        if task_obj.estimated_hours:
            click.echo(f"\nEstimated: {task_obj.estimated_hours} hours")
        if task_obj.actual_hours:
            click.echo(f"Actual: {task_obj.actual_hours} hours")

        click.echo(f"\nCreated: {task_obj.created_at.strftime('%Y-%m-%d %H:%M')}")
        if task_obj.started_at:
            click.echo(f"Started: {task_obj.started_at.strftime('%Y-%m-%d %H:%M')}")
        if task_obj.completed_at:
            click.echo(f"Completed: {task_obj.completed_at.strftime('%Y-%m-%d %H:%M')}")
        click.echo()

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@task.command("update")
@click.argument("task_id")
@click.option("--status", type=click.Choice(["pending", "in_progress", "completed", "blocked"]))
@click.option("--priority", type=click.Choice(["low", "medium", "high", "critical"]))
@click.option("--name", help="Update task name")
@click.option("--description", help="Update task description")
def update_task(
    task_id: str,
    status: Optional[str],
    priority: Optional[str],
    name: Optional[str],
    description: Optional[str],
) -> None:
    """
    Update task fields.

    Example:
        $ clauxton task update TASK-001 --status in_progress
        $ clauxton task update TASK-001 --priority high
    """
    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    tm = TaskManager(root_dir)

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

    if not updates:
        click.echo(click.style("Error: No fields to update", fg="yellow"))
        return

    try:
        tm.update(task_id, updates)
        click.echo(click.style(f"✓ Updated task: {task_id}", fg="green"))
        for key, value in updates.items():
            click.echo(f"  {key}: {value}")
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@task.command("delete")
@click.argument("task_id")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete_task(task_id: str, yes: bool) -> None:
    """
    Delete a task.

    Example:
        $ clauxton task delete TASK-001
        $ clauxton task delete TASK-001 --yes
    """
    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    tm = TaskManager(root_dir)

    try:
        task_obj = tm.get(task_id)

        if not yes:
            click.echo(f"Delete task: {task_obj.name} ({task_id})?")
            if not click.confirm("Are you sure?"):
                click.echo("Cancelled")
                return

        tm.delete(task_id)
        click.echo(click.style(f"✓ Deleted task: {task_id}", fg="green"))

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@task.command("next")
def next_task() -> None:
    """
    Get next task to work on.

    Suggests the highest priority task whose dependencies are completed.

    Example:
        $ clauxton task next
    """
    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    tm = TaskManager(root_dir)

    next_task_obj = tm.get_next_task()

    if not next_task_obj:
        click.echo("No tasks ready to work on")
        click.echo("All tasks are either completed, in progress, or blocked by dependencies")
        return

    click.echo(click.style("\n📋 Next Task to Work On:\n", bold=True))
    click.echo(click.style(f"  {next_task_obj.id}", fg="cyan", bold=True))
    click.echo(f"  Name: {next_task_obj.name}")
    click.echo(f"  Priority: {next_task_obj.priority}")

    if next_task_obj.description:
        click.echo("\n  Description:")
        click.echo(f"    {next_task_obj.description}")

    if next_task_obj.files_to_edit:
        click.echo("\n  Files to edit:")
        for file in next_task_obj.files_to_edit:
            click.echo(f"    - {file}")

    if next_task_obj.estimated_hours:
        click.echo(f"\n  Estimated: {next_task_obj.estimated_hours} hours")

    click.echo("\n  Start working on this task:")
    click.echo(f"    clauxton task update {next_task_obj.id} --status in_progress")
    click.echo()
