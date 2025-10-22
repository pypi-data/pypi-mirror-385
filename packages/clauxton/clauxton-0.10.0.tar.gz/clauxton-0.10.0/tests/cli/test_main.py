"""
Tests for CLI commands.

Tests cover:
- init command
- kb add/get/list/search/update/delete commands
- Error handling
- Invalid inputs
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from clauxton.cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create temporary project directory."""
    return tmp_path


# ============================================================================
# init command tests
# ============================================================================


def test_init_creates_clauxton_dir(runner: CliRunner, temp_project: Path) -> None:
    """Test that init command creates .clauxton directory."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert ".clauxton" in result.output
        assert Path(".clauxton").exists()
        assert Path(".clauxton/knowledge-base.yml").exists()


def test_init_creates_gitignore(runner: CliRunner, temp_project: Path) -> None:
    """Test that init command creates .gitignore."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        gitignore = Path(".clauxton/.gitignore")
        assert gitignore.exists()
        content = gitignore.read_text()
        assert "*.bak" in content


def test_init_fails_if_already_initialized(runner: CliRunner, temp_project: Path) -> None:
    """Test that init command fails if .clauxton already exists."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # First init should succeed
        result1 = runner.invoke(cli, ["init"])
        assert result1.exit_code == 0

        # Second init should fail
        result2 = runner.invoke(cli, ["init"])
        assert result2.exit_code != 0
        assert "already exists" in result2.output


def test_init_force_overwrites_existing(runner: CliRunner, temp_project: Path) -> None:
    """Test that init --force overwrites existing .clauxton."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # First init
        result1 = runner.invoke(cli, ["init"])
        assert result1.exit_code == 0

        # Force init should succeed
        result2 = runner.invoke(cli, ["init", "--force"])
        assert result2.exit_code == 0
        assert "Initialized" in result2.output


# ============================================================================
# kb add command tests
# ============================================================================


def test_kb_add_creates_entry(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb add command creates entry."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize first
        runner.invoke(cli, ["init"])

        # Add entry
        result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Test Entry\narchitecture\nTest content\ntest,entry\n",
        )

        assert result.exit_code == 0
        assert "Added entry" in result.output
        assert "KB-" in result.output


def test_kb_add_fails_without_init(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb add fails if not initialized."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Test Entry\narchitecture\nTest content\n\n",
        )

        assert result.exit_code != 0
        assert ".clauxton/ not found" in result.output


def test_kb_add_exception_handling(runner: CliRunner, temp_project: Path) -> None:
    """Test kb add exception handling with invalid data."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        # Try to add entry with title that's too long (>50 chars)
        # This should trigger Pydantic validation error
        long_title = (
            "This is a very long title that exceeds the maximum allowed "
            "length of fifty characters"
        )
        result = runner.invoke(
            cli,
            ["kb", "add"],
            input=f"{long_title}\narchitecture\nContent\n\n",
        )

        # Should fail (validation error is raised, caught by Click)
        assert result.exit_code != 0
        # Exception should be raised
        assert result.exception is not None


# ============================================================================
# kb get command tests
# ============================================================================


def test_kb_get_retrieves_entry(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb get retrieves existing entry."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entry
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Test Entry\narchitecture\nTest content\n\n",
        )

        # Extract entry ID from output
        entry_id = None
        for line in add_result.output.split("\n"):
            if "KB-" in line:
                # Extract KB-YYYYMMDD-NNN pattern
                import re

                match = re.search(r"KB-\d{8}-\d{3}", line)
                if match:
                    entry_id = match.group(0)
                    break

        assert entry_id is not None

        # Get entry
        result = runner.invoke(cli, ["kb", "get", entry_id])

        assert result.exit_code == 0
        assert "Test Entry" in result.output
        assert "architecture" in result.output
        assert "Test content" in result.output


def test_kb_get_fails_for_nonexistent(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb get fails for non-existent entry."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        result = runner.invoke(cli, ["kb", "get", "KB-20251019-999"])

        assert result.exit_code != 0
        assert "Error" in result.output


# ============================================================================
# kb list command tests
# ============================================================================


def test_kb_list_shows_all_entries(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb list shows all entries."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entries
        runner.invoke(cli, ["init"])
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Entry 1\narchitecture\nContent 1\n\n",
        )
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Entry 2\ndecision\nContent 2\n\n",
        )

        # List all
        result = runner.invoke(cli, ["kb", "list"])

        assert result.exit_code == 0
        assert "Entry 1" in result.output
        assert "Entry 2" in result.output
        assert "(2)" in result.output  # Should show count


def test_kb_list_filters_by_category(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb list filters by category."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entries
        runner.invoke(cli, ["init"])
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Entry 1\narchitecture\nContent 1\n\n",
        )
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Entry 2\ndecision\nContent 2\n\n",
        )

        # List only architecture
        result = runner.invoke(cli, ["kb", "list", "--category", "architecture"])

        assert result.exit_code == 0
        assert "Entry 1" in result.output
        assert "Entry 2" not in result.output


def test_kb_list_empty_shows_help(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb list shows help message when empty."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        result = runner.invoke(cli, ["kb", "list"])

        assert result.exit_code == 0
        assert "No entries found" in result.output
        assert "clauxton kb add" in result.output


# ============================================================================
# kb search command tests
# ============================================================================


def test_kb_search_finds_entries(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb search finds matching entries."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entry
        runner.invoke(cli, ["init"])
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Use FastAPI\narchitecture\nAll APIs use FastAPI framework.\n\n",
        )

        # Search
        result = runner.invoke(cli, ["kb", "search", "FastAPI"])

        assert result.exit_code == 0
        assert "Use FastAPI" in result.output
        assert "FastAPI" in result.output


def test_kb_search_no_results(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb search handles no results."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        result = runner.invoke(cli, ["kb", "search", "nonexistent"])

        assert result.exit_code == 0
        assert "No results found" in result.output


def test_kb_search_with_category_filter(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb search filters by category."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entries
        runner.invoke(cli, ["init"])
        runner.invoke(
            cli,
            ["kb", "add"],
            input="API Design\narchitecture\nAPI uses REST.\n\n",
        )
        runner.invoke(
            cli,
            ["kb", "add"],
            input="API Decision\ndecision\nChoose REST over GraphQL.\n\n",
        )

        # Search with category filter
        result = runner.invoke(
            cli, ["kb", "search", "API", "--category", "architecture"]
        )

        assert result.exit_code == 0
        assert "API Design" in result.output
        assert "API Decision" not in result.output


# ============================================================================
# Version command tests
# ============================================================================


def test_version_command(runner: CliRunner) -> None:
    """Test that --version shows version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "0.10.0" in result.output


# ============================================================================
# Help command tests
# ============================================================================


def test_help_command(runner: CliRunner) -> None:
    """Test that --help shows help."""
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Clauxton" in result.output
    assert "Knowledge Base" in result.output


def test_kb_help_command(runner: CliRunner) -> None:
    """Test that kb --help shows KB commands."""
    result = runner.invoke(cli, ["kb", "--help"])

    assert result.exit_code == 0
    assert "add" in result.output
    assert "get" in result.output
    assert "list" in result.output
    assert "search" in result.output


# ============================================================================
# kb update command tests
# ============================================================================


def test_kb_update_title(runner: CliRunner, temp_project: Path) -> None:
    """Test updating entry title."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entry
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Original Title\narchitecture\nOriginal content\n\n",
        )

        # Extract entry ID
        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # Update title
        result = runner.invoke(
            cli, ["kb", "update", entry_id, "--title", "Updated Title"]
        )

        assert result.exit_code == 0
        assert "✓ Updated entry" in result.output
        assert entry_id in result.output

        # Verify update
        get_result = runner.invoke(cli, ["kb", "get", entry_id])
        assert "Updated Title" in get_result.output
        assert "Version: 2" in get_result.output


def test_kb_update_content(runner: CliRunner, temp_project: Path) -> None:
    """Test updating entry content."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Title\narchitecture\nOriginal content\n\n",
        )

        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # Update content
        result = runner.invoke(
            cli, ["kb", "update", entry_id, "--content", "Updated content"]
        )

        assert result.exit_code == 0
        assert "✓ Updated entry" in result.output

        # Verify
        get_result = runner.invoke(cli, ["kb", "get", entry_id])
        assert "Updated content" in get_result.output


def test_kb_update_category(runner: CliRunner, temp_project: Path) -> None:
    """Test updating entry category."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Title\narchitecture\nContent\n\n",
        )

        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # Update category
        result = runner.invoke(
            cli, ["kb", "update", entry_id, "--category", "decision"]
        )

        assert result.exit_code == 0

        # Verify
        get_result = runner.invoke(cli, ["kb", "get", entry_id])
        assert "decision" in get_result.output


def test_kb_update_tags(runner: CliRunner, temp_project: Path) -> None:
    """Test updating entry tags."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Title\narchitecture\nContent\nold,tags\n",
        )

        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # Update tags
        result = runner.invoke(
            cli, ["kb", "update", entry_id, "--tags", "new,updated,tags"]
        )

        assert result.exit_code == 0

        # Verify
        get_result = runner.invoke(cli, ["kb", "get", entry_id])
        assert "new" in get_result.output
        assert "updated" in get_result.output


def test_kb_update_multiple_fields(runner: CliRunner, temp_project: Path) -> None:
    """Test updating multiple fields at once."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Title\narchitecture\nContent\n\n",
        )

        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # Update multiple fields
        result = runner.invoke(
            cli,
            [
                "kb",
                "update",
                entry_id,
                "--title",
                "New Title",
                "--content",
                "New Content",
                "--category",
                "decision",
            ],
        )

        assert result.exit_code == 0

        # Verify all updates
        get_result = runner.invoke(cli, ["kb", "get", entry_id])
        assert "New Title" in get_result.output
        assert "New Content" in get_result.output
        assert "decision" in get_result.output


def test_kb_update_no_fields(runner: CliRunner, temp_project: Path) -> None:
    """Test update with no fields shows error."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Title\narchitecture\nContent\n\n",
        )

        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # Update with no fields
        result = runner.invoke(cli, ["kb", "update", entry_id])

        assert result.exit_code == 0
        assert "No fields to update" in result.output


def test_kb_update_nonexistent(runner: CliRunner, temp_project: Path) -> None:
    """Test updating non-existent entry fails."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        result = runner.invoke(
            cli, ["kb", "update", "KB-20251019-999", "--title", "New Title"]
        )

        assert result.exit_code != 0
        assert "Error" in result.output


def test_kb_update_without_init(runner: CliRunner, temp_project: Path) -> None:
    """Test kb update fails without initialization."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        result = runner.invoke(
            cli, ["kb", "update", "KB-20251019-001", "--title", "New Title"]
        )

        assert result.exit_code != 0
        assert ".clauxton/ not found" in result.output


# ============================================================================
# kb delete command tests
# ============================================================================


def test_kb_delete_with_yes_flag(runner: CliRunner, temp_project: Path) -> None:
    """Test deleting entry with --yes flag."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Title\narchitecture\nContent\n\n",
        )

        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # Delete with --yes
        result = runner.invoke(cli, ["kb", "delete", entry_id, "--yes"])

        assert result.exit_code == 0
        assert "✓ Deleted entry" in result.output
        assert entry_id in result.output

        # Verify deletion
        get_result = runner.invoke(cli, ["kb", "get", entry_id])
        assert get_result.exit_code != 0


def test_kb_delete_with_confirmation(runner: CliRunner, temp_project: Path) -> None:
    """Test deleting entry with confirmation prompt."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Title\narchitecture\nContent\n\n",
        )

        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # Delete with confirmation (answer yes)
        result = runner.invoke(cli, ["kb", "delete", entry_id], input="y\n")

        assert result.exit_code == 0
        assert "✓ Deleted entry" in result.output


def test_kb_delete_cancel_confirmation(runner: CliRunner, temp_project: Path) -> None:
    """Test canceling delete confirmation."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Title\narchitecture\nContent\n\n",
        )

        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # Cancel confirmation
        result = runner.invoke(cli, ["kb", "delete", entry_id], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.output

        # Verify entry still exists
        get_result = runner.invoke(cli, ["kb", "get", entry_id])
        assert get_result.exit_code == 0


def test_kb_delete_nonexistent(runner: CliRunner, temp_project: Path) -> None:
    """Test deleting non-existent entry fails."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        result = runner.invoke(cli, ["kb", "delete", "KB-20251019-999", "--yes"])

        assert result.exit_code != 0
        assert "Error" in result.output


# ============================================================================
# Integration Tests for KB Update/Delete
# ============================================================================


def test_kb_update_delete_workflow(runner: CliRunner, temp_project: Path) -> None:
    """Test complete update and delete workflow."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # 1. Initialize
        runner.invoke(cli, ["init"])

        # 2. Add entry
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Original Entry\narchitecture\nOriginal content\noriginal,tags\n",
        )
        assert add_result.exit_code == 0

        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # 3. Get and verify
        get_result = runner.invoke(cli, ["kb", "get", entry_id])
        assert "Original Entry" in get_result.output
        assert "Version: 1" in get_result.output

        # 4. Update title
        update1 = runner.invoke(cli, ["kb", "update", entry_id, "--title", "Updated Entry"])
        assert update1.exit_code == 0
        assert "Version: 2" in update1.output

        # 5. Update content and category
        update2 = runner.invoke(
            cli,
            [
                "kb",
                "update",
                entry_id,
                "--content",
                "New content",
                "--category",
                "decision",
            ],
        )
        assert update2.exit_code == 0
        assert "Version: 3" in update2.output

        # 6. Verify all updates
        get_result2 = runner.invoke(cli, ["kb", "get", entry_id])
        assert "Updated Entry" in get_result2.output
        assert "New content" in get_result2.output
        assert "decision" in get_result2.output
        assert "Version: 3" in get_result2.output

        # 7. Search for updated entry
        search_result = runner.invoke(cli, ["kb", "search", "Updated"])
        assert entry_id in search_result.output

        # 8. Delete entry
        delete_result = runner.invoke(cli, ["kb", "delete", entry_id, "--yes"])
        assert delete_result.exit_code == 0
        assert "Deleted" in delete_result.output

        # 9. Verify deletion
        get_result3 = runner.invoke(cli, ["kb", "get", entry_id])
        assert get_result3.exit_code != 0


def test_kb_version_increments_correctly(runner: CliRunner, temp_project: Path) -> None:
    """Test that version increments correctly with multiple updates."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        # Add entry
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Test\narchitecture\nContent\n\n",
        )

        import re

        match = re.search(r"KB-\d{8}-\d{3}", add_result.output)
        assert match is not None
        entry_id = match.group(0)

        # Multiple updates
        for i in range(1, 6):
            update_result = runner.invoke(
                cli, ["kb", "update", entry_id, "--title", f"Version {i + 1}"]
            )
            assert update_result.exit_code == 0
            assert f"Version: {i + 1}" in update_result.output

        # Final verification
        get_result = runner.invoke(cli, ["kb", "get", entry_id])
        assert "Version: 6" in get_result.output
        assert "Version 6" in get_result.output  # Latest title


# ============================================================================
# kb export command tests
# ============================================================================


def test_kb_export_all_categories(runner: CliRunner, temp_project: Path) -> None:
    """Test exporting all KB categories."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        # Add entries from different categories
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Architecture Decision\narchitecture\nUse microservices\napi\n",
        )
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Technical Constraint\nconstraint\nPython 3.11+\npython\n",
        )
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Use PostgreSQL\ndecision\nPostgreSQL for production\ndb\n",
        )

        # Export
        output_dir = temp_project / "docs" / "kb"
        result = runner.invoke(cli, ["kb", "export", str(output_dir)])

        assert result.exit_code == 0
        assert "✓ Export successful!" in result.output
        assert "Total entries: 3" in result.output
        assert "Files created: 3" in result.output

        # Verify files created
        assert (output_dir / "architecture.md").exists()
        assert (output_dir / "constraint.md").exists()
        assert (output_dir / "decision.md").exists()


def test_kb_export_specific_category(runner: CliRunner, temp_project: Path) -> None:
    """Test exporting specific category only."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        # Add mixed entries
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Arch\narchitecture\nContent\n\n",
        )
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Decision\ndecision\nContent\n\n",
        )

        # Export only decisions
        output_dir = temp_project / "docs" / "adr"
        result = runner.invoke(
            cli, ["kb", "export", str(output_dir), "--category", "decision"]
        )

        assert result.exit_code == 0
        assert "Total entries: 1" in result.output
        assert "Files created: 1" in result.output
        assert "ℹ Decision entries exported in ADR format" in result.output

        # Verify only decision.md exists
        assert (output_dir / "decision.md").exists()
        assert not (output_dir / "architecture.md").exists()


def test_kb_export_short_option(runner: CliRunner, temp_project: Path) -> None:
    """Test export with short category option (-c)."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Pattern\npattern\nRepository pattern\n\n",
        )

        output_dir = temp_project / "docs"
        result = runner.invoke(cli, ["kb", "export", str(output_dir), "-c", "pattern"])

        assert result.exit_code == 0
        assert "Total entries: 1" in result.output
        assert (output_dir / "pattern.md").exists()


def test_kb_export_without_init(runner: CliRunner, temp_project: Path) -> None:
    """Test export fails without initialization."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        output_dir = temp_project / "docs"
        result = runner.invoke(cli, ["kb", "export", str(output_dir)])

        assert result.exit_code == 1
        assert "Error: .clauxton/ not found" in result.output
        assert "Run 'clauxton init' first" in result.output


def test_kb_export_empty_kb(runner: CliRunner, temp_project: Path) -> None:
    """Test export with empty Knowledge Base."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        output_dir = temp_project / "docs"
        result = runner.invoke(cli, ["kb", "export", str(output_dir)])

        # Should succeed but create no files
        assert result.exit_code == 0
        assert "Total entries: 0" in result.output
        assert "Files created: 0" in result.output
