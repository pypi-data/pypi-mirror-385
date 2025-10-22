"""
Clauxton CLI - Conflict Detection Commands.

Provides CLI commands for conflict detection:
- conflict detect: Detect conflicts for a task
- conflict order: Get safe execution order for tasks
- conflict check: Check file availability
"""

from pathlib import Path

import click

from clauxton.core.conflict_detector import ConflictDetector
from clauxton.core.models import NotFoundError
from clauxton.core.task_manager import TaskManager


@click.group()
def conflict() -> None:
    """
    Conflict detection commands.

    Detect potential conflicts between tasks before they occur.
    Helps avoid merge conflicts and coordination issues.

    Examples:
        clauxton conflict detect TASK-001
        clauxton conflict order TASK-001 TASK-002 TASK-003
        clauxton conflict check src/api/auth.py src/models/user.py
    """
    pass


@conflict.command()
@click.argument("task_id")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed conflict information",
)
def detect(task_id: str, verbose: bool) -> None:
    """
    Detect conflicts for a specific task.

    Analyzes the given task against all in_progress tasks to identify
    file overlap conflicts.

    TASK_ID: Task ID to check (e.g., TASK-001)

    Examples:
        clauxton conflict detect TASK-002
        clauxton conflict detect TASK-005 --verbose
    """
    try:
        tm = TaskManager(Path.cwd())
        detector = ConflictDetector(tm)

        # Get task info
        task = tm.get(task_id)
        conflicts = detector.detect_conflicts(task_id)

        # Display header
        click.echo(f"\n{click.style('Conflict Detection Report', bold=True)}")
        click.echo(f"Task: {click.style(task_id, fg='cyan')} - {task.name}")
        click.echo(f"Files: {len(task.files_to_edit)} file(s)")
        click.echo()

        if not conflicts:
            click.echo(
                click.style("✓ No conflicts detected", fg="green", bold=True)
            )
            click.echo("This task is safe to start working on.")
            return

        # Display conflicts
        click.echo(
            click.style(
                f"⚠ {len(conflicts)} conflict(s) detected",
                fg="yellow",
                bold=True,
            )
        )
        click.echo()

        for i, c in enumerate(conflicts, 1):
            # Get conflicting task name
            conflicting_task = tm.get(c.task_b_id)

            # Risk level color
            risk_color = {
                "high": "red",
                "medium": "yellow",
                "low": "blue",
            }[c.risk_level]

            click.echo(f"Conflict {i}:")
            click.echo(
                f"  Task: {click.style(c.task_b_id, fg='cyan')} - "
                f"{conflicting_task.name}"
            )
            click.echo(
                f"  Risk: {click.style(c.risk_level.upper(), fg=risk_color, bold=True)} "
                f"({c.risk_score:.0%})"
            )
            click.echo(
                f"  Files: {click.style(str(len(c.overlapping_files)), fg='yellow')} "
                f"overlapping"
            )

            if verbose:
                click.echo("  Overlapping files:")
                for file in c.overlapping_files:
                    click.echo(f"    - {file}")
                click.echo(f"  Details: {c.details}")

            click.echo(
                f"  {click.style('→', fg='green')} {c.recommendation}"
            )
            click.echo()

    except NotFoundError as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()
    except Exception as e:
        click.echo(click.style(f"Unexpected error: {e}", fg="red"))
        raise click.Abort()


@conflict.command()
@click.argument("task_ids", nargs=-1, required=True)
@click.option(
    "--details",
    "-d",
    is_flag=True,
    help="Show task details (priority, files)",
)
def order(task_ids: tuple[str, ...], details: bool) -> None:
    """
    Recommend safe execution order for tasks.

    Uses topological sort based on dependencies and conflict analysis
    to suggest an order that minimizes merge conflicts.

    TASK_IDS: Space-separated list of task IDs

    Examples:
        clauxton conflict order TASK-001 TASK-002 TASK-003
        clauxton conflict order TASK-* --details
    """
    try:
        tm = TaskManager(Path.cwd())
        detector = ConflictDetector(tm)

        task_list = list(task_ids)
        recommended = detector.recommend_safe_order(task_list)

        # Display header
        click.echo(f"\n{click.style('Task Execution Order', bold=True)}")
        click.echo(f"Tasks: {len(task_list)} task(s)")
        click.echo()

        # Check if any tasks have dependencies
        tasks = [tm.get(tid) for tid in task_list]
        has_deps = any(t.depends_on for t in tasks)

        if has_deps:
            click.echo(
                click.style(
                    "Order respects dependencies and minimizes conflicts",
                    fg="blue",
                )
            )
        else:
            click.echo(
                click.style(
                    "Order minimizes file conflicts (no dependencies)",
                    fg="blue",
                )
            )
        click.echo()

        # Display recommended order
        click.echo(click.style("Recommended Order:", bold=True))
        for i, task_id in enumerate(recommended, 1):
            task = tm.get(task_id)

            # Priority color
            priority_color = {
                "critical": "red",
                "high": "yellow",
                "medium": "blue",
                "low": "white",
            }.get(task.priority, "white")

            click.echo(
                f"{i}. {click.style(task_id, fg='cyan')} - {task.name}"
            )

            if details:
                click.echo(
                    f"   Priority: {click.style(task.priority.upper(), fg=priority_color)}"
                )
                click.echo(f"   Files: {len(task.files_to_edit)} file(s)")
                if task.depends_on:
                    deps_str = ", ".join(task.depends_on)
                    click.echo(
                        f"   Depends on: {click.style(deps_str, fg='yellow')}"
                    )

        click.echo()
        click.echo(
            click.style(
                "💡 Execute tasks in this order to minimize conflicts",
                fg="green",
            )
        )

    except NotFoundError as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()
    except Exception as e:
        click.echo(click.style(f"Unexpected error: {e}", fg="red"))
        raise click.Abort()


@conflict.command()
@click.argument("files", nargs=-1, required=True)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed task information",
)
def check(files: tuple[str, ...], verbose: bool) -> None:
    """
    Check which tasks are currently editing specific files.

    Useful for determining if files are available for editing or
    if coordination with other tasks is needed.

    FILES: Space-separated list of file paths

    Examples:
        clauxton conflict check src/api/auth.py
        clauxton conflict check src/api/*.py --verbose
    """
    try:
        tm = TaskManager(Path.cwd())
        detector = ConflictDetector(tm)

        file_list = list(files)
        conflicting = detector.check_file_conflicts(file_list)

        # Display header
        click.echo(f"\n{click.style('File Availability Check', bold=True)}")
        click.echo(f"Files: {len(file_list)} file(s)")
        click.echo()

        if not conflicting:
            click.echo(
                click.style(
                    f"✓ All {len(file_list)} file(s) available for editing",
                    fg="green",
                    bold=True,
                )
            )
            return

        # Display conflicts
        click.echo(
            click.style(
                f"⚠ {len(conflicting)} task(s) editing these files",
                fg="yellow",
                bold=True,
            )
        )
        click.echo()

        # Build file map
        file_map: dict[str, list[str]] = {f: [] for f in file_list}
        for task_id in conflicting:
            task = tm.get(task_id)
            for file in file_list:
                if file in task.files_to_edit:
                    file_map[file].append(task_id)

        # Display by task
        click.echo(click.style("Conflicting Tasks:", bold=True))
        for task_id in conflicting:
            task = tm.get(task_id)
            task_files = [f for f in file_list if f in task.files_to_edit]

            click.echo(
                f"  {click.style(task_id, fg='cyan')} - {task.name}"
            )
            click.echo(
                f"  Status: {click.style(task.status, fg='yellow')}"
            )
            click.echo(f"  Editing: {len(task_files)} of your file(s)")

            if verbose:
                for file in task_files:
                    click.echo(f"    - {file}")

        click.echo()

        # Display by file
        if verbose:
            click.echo(click.style("File Status:", bold=True))
            for file in file_list:
                if file_map[file]:
                    tasks_str = ", ".join(file_map[file])
                    click.echo(
                        f"  {click.style('✗', fg='red')} {file} "
                        f"(locked by: {click.style(tasks_str, fg='yellow')})"
                    )
                else:
                    click.echo(
                        f"  {click.style('✓', fg='green')} {file} "
                        f"(available)"
                    )
            click.echo()

        click.echo(
            click.style(
                "💡 Coordinate with task owners or wait until tasks complete",
                fg="blue",
            )
        )

    except Exception as e:
        click.echo(click.style(f"Unexpected error: {e}", fg="red"))
        raise click.Abort()
