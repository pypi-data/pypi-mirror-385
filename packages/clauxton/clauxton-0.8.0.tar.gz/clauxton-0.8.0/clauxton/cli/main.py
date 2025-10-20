"""
Clauxton CLI - Command Line Interface for Knowledge Base and Task Management.

This module provides CLI commands for:
- Knowledge Base management (kb add, kb get, kb list, kb search, kb update, kb delete)
- Project initialization (init)
- Future: Task management (Phase 1)
- Future: Conflict detection (Phase 2)

Example:
    >>> clauxton init
    >>> clauxton kb add
    >>> clauxton kb search "architecture"
"""

from pathlib import Path
from typing import Any, Optional

import click

from clauxton.__version__ import __version__


@click.group()
@click.version_option(version=__version__, prog_name="clauxton")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Clauxton - Persistent context for Claude Code.

    Provides Knowledge Base, Task Management, and Conflict Detection
    to solve AI-assisted development pain points.

    Phase 0: Knowledge Base (Current)
    Phase 1: Task Management (Planned)
    Phase 2: Conflict Detection (Planned)
    """
    # Ensure context object exists
    ctx.ensure_object(dict)


@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing .clauxton directory if it exists",
)
@click.pass_context
def init(ctx: click.Context, force: bool) -> None:
    """
    Initialize Clauxton in the current directory.

    Creates .clauxton/ directory with:
    - knowledge-base.yml (empty Knowledge Base)
    - tasks.yml (for Phase 1)
    - .gitignore (excludes sensitive files)

    Example:
        $ clauxton init
        $ clauxton init --force  # Overwrite existing
    """
    from clauxton.utils.file_utils import ensure_clauxton_dir, set_secure_directory_permissions
    from clauxton.utils.yaml_utils import write_yaml

    root_dir = Path.cwd()

    # Check if .clauxton already exists
    clauxton_dir = root_dir / ".clauxton"
    if clauxton_dir.exists() and not force:
        click.echo(
            click.style(
                f"Error: .clauxton/ already exists at {root_dir}", fg="red"
            )
        )
        click.echo("Use --force to overwrite")
        ctx.exit(1)

    # Create .clauxton directory
    clauxton_dir = ensure_clauxton_dir(root_dir)
    set_secure_directory_permissions(clauxton_dir)

    # Create knowledge-base.yml
    from typing import Any, Dict

    kb_file = clauxton_dir / "knowledge-base.yml"
    kb_data: Dict[str, Any] = {
        "version": "1.0",
        "project_name": root_dir.name,
        "project_description": None,
        "entries": [],
    }
    write_yaml(kb_file, kb_data, backup=False)

    # Create .gitignore
    gitignore_file = clauxton_dir / ".gitignore"
    gitignore_content = """# Clauxton internal files
*.bak
*.tmp
.DS_Store
"""
    gitignore_file.write_text(gitignore_content)

    click.echo(click.style("✓ Initialized Clauxton", fg="green"))
    click.echo(f"  Location: {clauxton_dir}")
    click.echo(f"  Knowledge Base: {kb_file}")


@cli.group()
def kb() -> None:
    """
    Knowledge Base commands.

    Manage project context with:
    - add: Add new entry
    - get: Get entry by ID
    - list: List all entries
    - search: Search entries
    - update: Update entry (Phase 1)
    - delete: Delete entry (Phase 1)
    """
    pass


@kb.command()
@click.option("--title", prompt="Title", help="Entry title (max 50 chars)")
@click.option(
    "--category",
    prompt="Category",
    type=click.Choice(
        ["architecture", "constraint", "decision", "pattern", "convention"]
    ),
    help="Entry category",
)
@click.option("--content", prompt="Content", help="Entry content (max 10000 chars)")
@click.option(
    "--tags",
    help="Comma-separated tags (e.g., 'api,backend,fastapi')",
    default="",
)
def add(title: str, category: str, content: str, tags: str) -> None:
    """
    Add new entry to Knowledge Base.

    Example:
        $ clauxton kb add
        Title: Use FastAPI framework
        Category: architecture
        Content: All backend APIs use FastAPI...
        Tags (optional): backend,api,fastapi
    """
    from datetime import datetime

    from clauxton.core.knowledge_base import KnowledgeBase
    from clauxton.core.models import KnowledgeBaseEntry

    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    # Create Knowledge Base instance
    kb_instance = KnowledgeBase(root_dir)

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    # Generate ID
    entry_id = kb_instance._generate_id()

    # Create entry
    from typing import Literal, cast

    now = datetime.now()
    entry = KnowledgeBaseEntry(
        id=entry_id,
        title=title,
        category=cast(
            Literal["architecture", "constraint", "decision", "pattern", "convention"],
            category,
        ),
        content=content,
        tags=tag_list,
        created_at=now,
        updated_at=now,
        author=None,
    )

    # Add to Knowledge Base
    try:
        kb_instance.add(entry)
        click.echo(click.style(f"✓ Added entry: {entry_id}", fg="green"))
        click.echo(f"  Title: {title}")
        click.echo(f"  Category: {category}")
        click.echo(f"  Tags: {', '.join(tag_list) if tag_list else '(none)'}")
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@kb.command()
@click.argument("entry_id")
def get(entry_id: str) -> None:
    """
    Get entry by ID.

    Example:
        $ clauxton kb get KB-20251019-001
    """
    from clauxton.core.knowledge_base import KnowledgeBase
    from clauxton.core.models import NotFoundError

    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    kb_instance = KnowledgeBase(root_dir)

    try:
        entry = kb_instance.get(entry_id)

        # Display entry
        click.echo(click.style(f"\n{entry.id}", fg="cyan", bold=True))
        click.echo(click.style(f"Title: {entry.title}", bold=True))
        click.echo(f"Category: {entry.category}")
        click.echo(f"Tags: {', '.join(entry.tags) if entry.tags else '(none)'}")
        click.echo(f"Version: {entry.version}")
        click.echo(f"Created: {entry.created_at}")
        click.echo(f"Updated: {entry.updated_at}")
        click.echo(f"\n{entry.content}\n")
    except NotFoundError as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@kb.command("list")
@click.option(
    "--category",
    type=click.Choice(
        ["architecture", "constraint", "decision", "pattern", "convention"]
    ),
    help="Filter by category",
)
def list_entries(category: Optional[str]) -> None:
    """
    List all Knowledge Base entries.

    Example:
        $ clauxton kb list
        $ clauxton kb list --category architecture
    """
    from clauxton.core.knowledge_base import KnowledgeBase

    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    kb_instance = KnowledgeBase(root_dir)
    entries = kb_instance.list_all()

    # Filter by category if specified
    if category:
        entries = [e for e in entries if e.category == category]

    if not entries:
        if category:
            click.echo(f"No entries found with category '{category}'")
        else:
            click.echo("No entries found")
        click.echo("Use 'clauxton kb add' to add an entry")
        return

    # Display entries
    click.echo(click.style(f"\nKnowledge Base Entries ({len(entries)}):\n", bold=True))

    for entry in entries:
        click.echo(click.style(f"  {entry.id}", fg="cyan"))
        click.echo(f"    Title: {entry.title}")
        click.echo(f"    Category: {entry.category}")
        if entry.tags:
            click.echo(f"    Tags: {', '.join(entry.tags)}")
        click.echo()


@kb.command()
@click.argument("query")
@click.option(
    "--category",
    type=click.Choice(
        ["architecture", "constraint", "decision", "pattern", "convention"]
    ),
    help="Filter by category",
)
@click.option("--tags", help="Filter by tags (comma-separated)")
@click.option("--limit", default=10, help="Maximum number of results (default: 10)")
def search(query: str, category: Optional[str], tags: Optional[str], limit: int) -> None:
    """
    Search Knowledge Base entries.

    Searches in title, content, and tags.

    Example:
        $ clauxton kb search "API"
        $ clauxton kb search "FastAPI" --category architecture
        $ clauxton kb search "database" --tags backend,postgresql
    """
    from clauxton.core.knowledge_base import KnowledgeBase

    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    kb_instance = KnowledgeBase(root_dir)

    # Parse tags
    tag_list = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    # Search
    results = kb_instance.search(query, category=category, tags=tag_list, limit=limit)

    if not results:
        click.echo(f"No results found for '{query}'")
        return

    # Display results
    click.echo(
        click.style(f"\nSearch Results for '{query}' ({len(results)}):\n", bold=True)
    )

    for entry in results:
        click.echo(click.style(f"  {entry.id}", fg="cyan"))
        click.echo(f"    Title: {entry.title}")
        click.echo(f"    Category: {entry.category}")
        if entry.tags:
            click.echo(f"    Tags: {', '.join(entry.tags)}")
        # Show first 100 chars of content
        content_preview = (
            entry.content[:100] + "..." if len(entry.content) > 100 else entry.content
        )
        click.echo(f"    Preview: {content_preview}")
        click.echo()


@kb.command()
@click.argument("entry_id")
@click.option("--title", help="New title")
@click.option("--content", help="New content")
@click.option(
    "--category",
    type=click.Choice(["architecture", "constraint", "decision", "pattern", "convention"]),
    help="New category",
)
@click.option("--tags", help="New tags (comma-separated)")
def update(
    entry_id: str,
    title: Optional[str],
    content: Optional[str],
    category: Optional[str],
    tags: Optional[str],
) -> None:
    """
    Update an existing Knowledge Base entry.

    Example:
        $ clauxton kb update KB-20251019-001 --title "New title"
        $ clauxton kb update KB-20251019-001 --content "New content"
        $ clauxton kb update KB-20251019-001 --tags "api,backend,updated"
    """
    from clauxton.core.knowledge_base import KnowledgeBase

    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    kb_instance = KnowledgeBase(root_dir)

    # Prepare updates
    updates: dict[str, Any] = {}
    if title:
        updates["title"] = title
    if content:
        updates["content"] = content
    if category:
        updates["category"] = category
    if tags:
        updates["tags"] = [t.strip() for t in tags.split(",") if t.strip()]

    if not updates:
        click.echo(click.style("Error: No fields to update", fg="yellow"))
        click.echo("Use --title, --content, --category, or --tags")
        return

    try:
        updated_entry = kb_instance.update(entry_id, updates)
        click.echo(click.style(f"✓ Updated entry: {entry_id}", fg="green"))
        click.echo(f"  Title: {updated_entry.title}")
        click.echo(f"  Version: {updated_entry.version}")
        click.echo(f"  Updated: {updated_entry.updated_at.strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@kb.command()
@click.argument("entry_id")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete(entry_id: str, yes: bool) -> None:
    """
    Delete a Knowledge Base entry.

    Example:
        $ clauxton kb delete KB-20251019-001
        $ clauxton kb delete KB-20251019-001 --yes
    """
    from clauxton.core.knowledge_base import KnowledgeBase

    root_dir = Path.cwd()

    # Check if .clauxton exists
    if not (root_dir / ".clauxton").exists():
        click.echo(click.style("Error: .clauxton/ not found", fg="red"))
        click.echo("Run 'clauxton init' first")
        raise click.Abort()

    kb_instance = KnowledgeBase(root_dir)

    try:
        entry = kb_instance.get(entry_id)

        if not yes:
            click.echo(f"Delete entry: {entry.title} ({entry_id})?")
            if not click.confirm("Are you sure?"):
                click.echo("Cancelled")
                return

        kb_instance.delete(entry_id)
        click.echo(click.style(f"✓ Deleted entry: {entry_id}", fg="green"))

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


# ============================================================================
# Task Management Commands (Phase 1)
# ============================================================================

from clauxton.cli.tasks import task  # noqa: E402

cli.add_command(task)


if __name__ == "__main__":
    cli()
