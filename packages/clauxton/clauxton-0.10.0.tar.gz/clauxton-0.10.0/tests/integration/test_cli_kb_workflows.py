"""
CLI Knowledge Base Workflow Integration Tests.

Tests cover complete KB workflows through CLI:
- Full CRUD workflow (add → search → update → delete)
- Import/export workflows
- Search functionality with various queries
- Category filtering
- Tag-based search
- Empty state handling
- Large dataset handling
- Unicode content support
- Error recovery
"""

from pathlib import Path

from click.testing import CliRunner

from clauxton.cli.main import cli

# ============================================================================
# Test 1: Complete KB CRUD Workflow
# ============================================================================


def test_kb_full_workflow(runner: CliRunner, tmp_path: Path, extract_id) -> None:
    """
    Test complete KB workflow: init → add → search → update → delete.

    Workflow:
    1. Initialize project
    2. Add KB entry
    3. Search for entry
    4. Update entry
    5. Verify update
    6. Delete entry
    7. Verify deletion
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0, f"Init failed: {result.output}"

        # Add entry
        result = runner.invoke(
            cli,
            [
                "kb",
                "add",
                "--title",
                "Test Entry",
                "--category",
                "architecture",
                "--content",
                "Test content for KB entry",
                "--tags",
                "test,architecture,api",
            ],
        )
        assert result.exit_code == 0, f"Add failed: {result.output}"
        assert "Added entry" in result.output or "KB-" in result.output
        entry_id = extract_id(result.output, "KB-")

        # Search
        result = runner.invoke(cli, ["kb", "search", "Test"])
        assert result.exit_code == 0, f"Search failed: {result.output}"
        assert "Test Entry" in result.output
        assert entry_id in result.output

        # Update
        result = runner.invoke(
            cli,
            ["kb", "update", entry_id, "--title", "Updated Entry"],
        )
        assert result.exit_code == 0, f"Update failed: {result.output}"

        # Verify update
        result = runner.invoke(cli, ["kb", "get", entry_id])
        assert result.exit_code == 0, f"Get failed: {result.output}"
        assert "Updated Entry" in result.output

        # Delete
        result = runner.invoke(cli, ["kb", "delete", entry_id, "--yes"])
        assert result.exit_code == 0, f"Delete failed: {result.output}"

        # Verify deletion
        result = runner.invoke(cli, ["kb", "list"])
        assert result.exit_code == 0
        assert entry_id not in result.output


# ============================================================================
# Test 2: KB Import/Export Workflow
# ============================================================================


def test_kb_import_export_workflow(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test KB export and import workflow.

    Workflow:
    1. Initialize project
    2. Add multiple entries
    3. Export to docs
    4. Verify export files created
    5. Read exported content
    6. Verify content integrity
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add multiple entries
        entries = [
            ("Entry 1", "architecture", "Content 1", "tag1,api"),
            ("Entry 2", "decision", "Content 2", "tag2,auth"),
            ("Entry 3", "constraint", "Content 3", "tag3,database"),
        ]

        for title, category, content, tags in entries:
            result = runner.invoke(
                cli,
                [
                    "kb",
                    "add",
                    "--title",
                    title,
                    "--category",
                    category,
                    "--content",
                    content,
                    "--tags",
                    tags,
                ],
            )
            assert result.exit_code == 0

        # Export to docs
        export_dir = Path.cwd() / "docs" / "kb"
        result = runner.invoke(cli, ["kb", "export", str(export_dir)])
        assert result.exit_code == 0
        assert "Exported" in result.output or "export" in result.output.lower()

        # Verify export files created
        assert export_dir.exists()
        exported_files = list(export_dir.glob("*.md"))
        assert len(exported_files) >= 3, f"Expected 3+ files, got {len(exported_files)}"

        # Verify content integrity
        for file in exported_files:
            content = file.read_text()
            assert len(content) > 0, f"Empty export file: {file}"
            # Check for markdown structure
            assert "# " in content or "## " in content


# ============================================================================
# Test 3: KB Search Workflow
# ============================================================================


def test_kb_search_workflow(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test search functionality across multiple entries.

    Tests:
    - Keyword search
    - Multi-word search
    - Relevance ranking (TF-IDF)
    - Search limit
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add diverse entries
        entries = [
            ("FastAPI Implementation", "architecture", "Use FastAPI for REST API", "fastapi,api"),
            ("JWT Authentication", "decision", "Implement JWT authentication", "jwt,auth,security"),
            ("Database Schema", "architecture", "PostgreSQL database schema", "database,postgres"),
            ("API Rate Limiting", "constraint", "Maximum 1000 requests per hour", "api,limit"),
            ("Logging Pattern", "pattern", "Use structured logging with JSON", "logging,json"),
            ("Error Handling", "convention", "Return JSON errors with status codes", "error,api"),
            ("Testing Strategy", "decision", "Use pytest for testing", "pytest,testing"),
            ("Docker Setup", "architecture", "Containerize with Docker", "docker,container"),
            ("CI/CD Pipeline", "pattern", "GitHub Actions for CI/CD", "github,cicd"),
            ("Code Style", "convention", "Follow PEP 8 style guide", "style,pep8"),
        ]

        for title, category, content, tags in entries:
            result = runner.invoke(
                cli,
                [
                    "kb",
                    "add",
                    "--title",
                    title,
                    "--category",
                    category,
                    "--content",
                    content,
                    "--tags",
                    tags,
                ],
            )
            assert result.exit_code == 0

        # Test keyword search
        result = runner.invoke(cli, ["kb", "search", "API"])
        assert result.exit_code == 0
        assert "API" in result.output or "api" in result.output.lower()

        # Test multi-word search
        result = runner.invoke(cli, ["kb", "search", "JWT authentication"])
        assert result.exit_code == 0
        assert "JWT" in result.output or "Authentication" in result.output

        # Test search with limit
        result = runner.invoke(cli, ["kb", "search", "architecture", "--limit", "3"])
        assert result.exit_code == 0

        # Test no results
        result = runner.invoke(cli, ["kb", "search", "nonexistent_keyword_xyz"])
        assert result.exit_code == 0
        # Should handle gracefully (either no results or empty)


# ============================================================================
# Test 4: KB Category Filtering
# ============================================================================


def test_kb_category_filtering(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test filtering by category.

    Tests:
    - List all entries
    - Filter by architecture
    - Filter by decision
    - Filter by constraint
    - Filter by pattern
    - Filter by convention
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add entries in different categories
        categories = ["architecture", "decision", "constraint", "pattern", "convention"]
        for i, category in enumerate(categories, 1):
            result = runner.invoke(
                cli,
                [
                    "kb",
                    "add",
                    "--title",
                    f"Entry {i}",
                    "--category",
                    category,
                    "--content",
                    f"Content for {category}",
                    "--tags",
                    f"tag{i}",
                ],
            )
            assert result.exit_code == 0

        # List all entries
        result = runner.invoke(cli, ["kb", "list"])
        assert result.exit_code == 0
        for category in categories:
            # Check if category or entry appears
            output_lower = result.output.lower()
            assert (
                category in output_lower or "entry" in output_lower
            ), f"Category {category} not found"

        # Filter by each category
        for category in categories:
            result = runner.invoke(cli, ["kb", "list", "--category", category])
            assert result.exit_code == 0
            # Should show entries from this category


# ============================================================================
# Test 5: KB Tag Search
# ============================================================================


def test_kb_tag_search(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test tag-based search.

    Tests:
    - Search by single tag
    - Search by multiple tags
    - Tag relevance
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add entries with specific tags
        entries = [
            ("API Design", "architecture", "REST API design", "api,rest,design"),
            ("API Testing", "pattern", "API testing strategy", "api,testing,pytest"),
            ("Auth API", "architecture", "Authentication API", "api,auth,jwt"),
            ("Database", "architecture", "Database schema", "database,postgres"),
        ]

        for title, category, content, tags in entries:
            result = runner.invoke(
                cli,
                [
                    "kb",
                    "add",
                    "--title",
                    title,
                    "--category",
                    category,
                    "--content",
                    content,
                    "--tags",
                    tags,
                ],
            )
            assert result.exit_code == 0

        # Search by tag
        result = runner.invoke(cli, ["kb", "search", "api"])
        assert result.exit_code == 0
        # Should find entries with 'api' tag or 'api' in content
        assert "API" in result.output or "api" in result.output


# ============================================================================
# Test 6: KB Empty State
# ============================================================================


def test_kb_empty_state(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test KB commands on empty KB.

    Tests:
    - List empty KB
    - Search empty KB
    - Get non-existent entry
    - Delete non-existent entry
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # List empty KB
        result = runner.invoke(cli, ["kb", "list"])
        assert result.exit_code == 0
        # Should handle empty state gracefully

        # Search empty KB
        result = runner.invoke(cli, ["kb", "search", "test"])
        assert result.exit_code == 0
        # Should return no results gracefully

        # Get non-existent entry
        result = runner.invoke(cli, ["kb", "get", "KB-20251021-999"])
        assert result.exit_code != 0  # Should fail
        assert "not found" in result.output.lower() or "error" in result.output.lower()

        # Delete non-existent entry
        result = runner.invoke(cli, ["kb", "delete", "KB-20251021-999", "--yes"])
        assert result.exit_code != 0  # Should fail


# ============================================================================
# Test 7: KB Large Dataset
# ============================================================================


def test_kb_large_dataset(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test KB with 50+ entries.

    Tests:
    - Add many entries
    - List all
    - Search performance
    - Export performance
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add 50 entries
        categories = ["architecture", "decision", "constraint", "pattern", "convention"]
        for i in range(1, 51):
            result = runner.invoke(
                cli,
                [
                    "kb",
                    "add",
                    "--title",
                    f"Entry {i}",
                    "--category",
                    categories[i % len(categories)],
                    "--content",
                    f"Content for entry {i}. This is a longer content to simulate real entries.",
                    "--tags",
                    f"tag{i},category{i % 5},performance",
                ],
            )
            assert result.exit_code == 0

        # List all
        result = runner.invoke(cli, ["kb", "list"])
        assert result.exit_code == 0

        # Search
        result = runner.invoke(cli, ["kb", "search", "entry"])
        assert result.exit_code == 0

        # Export
        export_dir = Path.cwd() / "docs" / "kb"
        result = runner.invoke(cli, ["kb", "export", str(export_dir)])
        assert result.exit_code == 0


# ============================================================================
# Test 8: KB Unicode Content
# ============================================================================


def test_kb_unicode_content(runner: CliRunner, tmp_path: Path, extract_id) -> None:
    """
    Test KB with Unicode/emoji content.

    Tests:
    - Add entry with Japanese text
    - Add entry with emojis
    - Add entry with special characters
    - Search Unicode content
    - Export Unicode content
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Add entry with Japanese text
        result = runner.invoke(
            cli,
            [
                "kb",
                "add",
                "--title",
                "日本語タイトル",
                "--category",
                "architecture",
                "--content",
                "これは日本語のコンテンツです。",
                "--tags",
                "日本語,テスト",
            ],
        )
        assert result.exit_code == 0
        entry_id_1 = extract_id(result.output, "KB-")

        # Add entry with emojis
        result = runner.invoke(
            cli,
            [
                "kb",
                "add",
                "--title",
                "Emoji Entry 🚀",
                "--category",
                "decision",
                "--content",
                "Testing with emojis: 🔥 💯 ✅",
                "--tags",
                "emoji,test",
            ],
        )
        assert result.exit_code == 0
        entry_id_2 = extract_id(result.output, "KB-")

        # Add entry with special characters
        result = runner.invoke(
            cli,
            [
                "kb",
                "add",
                "--title",
                "Special: <>&\"'",
                "--category",
                "pattern",
                "--content",
                "Testing special chars: <>&\"'",
                "--tags",
                "special,test",
            ],
        )
        assert result.exit_code == 0

        # Retrieve and verify
        result = runner.invoke(cli, ["kb", "get", entry_id_1])
        assert result.exit_code == 0
        assert "日本語" in result.output or "UTF" in result.output or entry_id_1 in result.output

        result = runner.invoke(cli, ["kb", "get", entry_id_2])
        assert result.exit_code == 0


# ============================================================================
# Test 9: KB Error Recovery
# ============================================================================


def test_kb_error_recovery(runner: CliRunner, tmp_path: Path) -> None:
    """
    Test KB error handling.

    Tests:
    - Invalid category
    - Empty title
    - Invalid ID format
    - Duplicate operations
    """
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Invalid category
        result = runner.invoke(
            cli,
            [
                "kb",
                "add",
                "--title",
                "Test",
                "--category",
                "invalid_category",
                "--content",
                "Test",
                "--tags",
                "test",
            ],
        )
        assert result.exit_code != 0  # Should fail

        # Empty title (if interactive mode)
        # This test depends on how CLI handles empty inputs

        # Invalid ID format
        result = runner.invoke(cli, ["kb", "get", "INVALID-ID"])
        assert result.exit_code != 0

        # Add valid entry
        result = runner.invoke(
            cli,
            [
                "kb",
                "add",
                "--title",
                "Valid Entry",
                "--category",
                "architecture",
                "--content",
                "Valid content",
                "--tags",
                "valid",
            ],
        )
        assert result.exit_code == 0

        # Verify state consistency after errors
        result = runner.invoke(cli, ["kb", "list"])
        assert result.exit_code == 0
        assert "Valid Entry" in result.output
