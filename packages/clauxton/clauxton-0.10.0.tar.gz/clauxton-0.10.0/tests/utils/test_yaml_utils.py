"""
Tests for YAML utilities.

Tests cover:
- Reading valid/invalid/missing YAML files
- Atomic writes with backups
- Schema validation
- Error handling
"""

from pathlib import Path

import pytest

from clauxton.core.models import ValidationError
from clauxton.utils.yaml_utils import (
    read_yaml,
    validate_kb_yaml,
    validate_tasks_yaml,
    write_yaml,
)


def test_read_yaml_valid(tmp_path: Path) -> None:
    """Test reading a valid YAML file."""
    yaml_file = tmp_path / "test.yml"
    yaml_file.write_text("version: '1.0'\nname: test\nvalues: [1, 2, 3]")

    data = read_yaml(yaml_file)

    assert data["version"] == "1.0"
    assert data["name"] == "test"
    assert data["values"] == [1, 2, 3]


def test_read_yaml_missing_file(tmp_path: Path) -> None:
    """Test reading a non-existent file returns empty dict."""
    yaml_file = tmp_path / "nonexistent.yml"

    data = read_yaml(yaml_file)

    assert data == {}


def test_read_yaml_invalid(tmp_path: Path) -> None:
    """Test reading malformed YAML raises ValidationError."""
    yaml_file = tmp_path / "invalid.yml"
    yaml_file.write_text("invalid: yaml: content: [unclosed")

    with pytest.raises(ValidationError) as exc_info:
        read_yaml(yaml_file)

    assert "Failed to parse YAML" in str(exc_info.value)
    assert "invalid.yml" in str(exc_info.value)


def test_read_yaml_empty_file(tmp_path: Path) -> None:
    """Test reading empty file returns empty dict."""
    yaml_file = tmp_path / "empty.yml"
    yaml_file.write_text("")

    data = read_yaml(yaml_file)

    assert data == {}


def test_write_yaml_creates_file(tmp_path: Path) -> None:
    """Test writing YAML creates file with correct content."""
    yaml_file = tmp_path / "output.yml"
    data = {"version": "1.0", "name": "test", "values": [1, 2, 3]}

    write_yaml(yaml_file, data, backup=False)

    assert yaml_file.exists()
    content = yaml_file.read_text()
    assert "version: '1.0'" in content
    assert "name: test" in content


def test_write_yaml_atomic(tmp_path: Path) -> None:
    """Test that write_yaml is atomic (uses temp file + rename)."""
    yaml_file = tmp_path / "atomic.yml"
    data = {"test": "data"}

    write_yaml(yaml_file, data, backup=False)

    # Verify temp file is not left behind
    temp_file = tmp_path / "atomic.yml.tmp"
    assert not temp_file.exists()

    # Verify final file exists
    assert yaml_file.exists()


def test_write_yaml_with_backup(tmp_path: Path) -> None:
    """Test that write_yaml creates backup when overwriting."""
    yaml_file = tmp_path / "backup-test.yml"
    backup_file = tmp_path / "backup-test.yml.bak"

    # Write initial data
    initial_data = {"version": "1.0"}
    write_yaml(yaml_file, initial_data, backup=False)

    # Overwrite with backup enabled
    new_data = {"version": "2.0"}
    write_yaml(yaml_file, new_data, backup=True)

    # Verify backup was created with old content
    assert backup_file.exists()
    backup_content = backup_file.read_text()
    assert "version: '1.0'" in backup_content

    # Verify main file has new content
    main_content = yaml_file.read_text()
    assert "version: '2.0'" in main_content


def test_write_yaml_creates_parent_dirs(tmp_path: Path) -> None:
    """Test that write_yaml creates parent directories if needed."""
    yaml_file = tmp_path / "nested" / "dir" / "file.yml"
    data = {"test": "data"}

    write_yaml(yaml_file, data, backup=False)

    assert yaml_file.exists()
    assert yaml_file.parent.exists()


def test_validate_kb_yaml_valid() -> None:
    """Test validating a valid Knowledge Base YAML structure."""
    data = {"version": "1.0", "project_name": "test-project", "entries": []}

    result = validate_kb_yaml(data)

    assert result is True


def test_validate_kb_yaml_missing_version() -> None:
    """Test validation fails when version is missing."""
    data = {"project_name": "test", "entries": []}

    with pytest.raises(ValidationError) as exc_info:
        validate_kb_yaml(data)

    assert "missing 'version'" in str(exc_info.value)


def test_validate_kb_yaml_missing_project_name() -> None:
    """Test validation fails when project_name is missing."""
    data = {"version": "1.0", "entries": []}

    with pytest.raises(ValidationError) as exc_info:
        validate_kb_yaml(data)

    assert "missing 'project_name'" in str(exc_info.value)


def test_validate_kb_yaml_missing_entries() -> None:
    """Test validation fails when entries is missing."""
    data = {"version": "1.0", "project_name": "test"}

    with pytest.raises(ValidationError) as exc_info:
        validate_kb_yaml(data)

    assert "missing 'entries'" in str(exc_info.value)


def test_validate_kb_yaml_entries_not_list() -> None:
    """Test validation fails when entries is not a list."""
    data = {"version": "1.0", "project_name": "test", "entries": "not-a-list"}

    with pytest.raises(ValidationError) as exc_info:
        validate_kb_yaml(data)

    assert "'entries' must be a list" in str(exc_info.value)


def test_validate_tasks_yaml_valid() -> None:
    """Test validating a valid Tasks YAML structure."""
    data = {"version": "1.0", "tasks": []}

    result = validate_tasks_yaml(data)

    assert result is True


def test_validate_tasks_yaml_missing_version() -> None:
    """Test validation fails when version is missing."""
    data = {"tasks": []}

    with pytest.raises(ValidationError) as exc_info:
        validate_tasks_yaml(data)

    assert "missing 'version'" in str(exc_info.value)


def test_validate_tasks_yaml_missing_tasks() -> None:
    """Test validation fails when tasks is missing."""
    data = {"version": "1.0"}

    with pytest.raises(ValidationError) as exc_info:
        validate_tasks_yaml(data)

    assert "missing 'tasks'" in str(exc_info.value)


def test_validate_tasks_yaml_tasks_not_list() -> None:
    """Test validation fails when tasks is not a list."""
    data = {"version": "1.0", "tasks": "not-a-list"}

    with pytest.raises(ValidationError) as exc_info:
        validate_tasks_yaml(data)

    assert "'tasks' must be a list" in str(exc_info.value)


def test_write_yaml_unicode_support(tmp_path: Path) -> None:
    """Test that write_yaml correctly handles Unicode characters."""
    yaml_file = tmp_path / "unicode.yml"
    data = {
        "japanese": "日本語",
        "emoji": "🎉",
        "chinese": "中文",
    }

    write_yaml(yaml_file, data, backup=False)

    # Read back and verify
    read_data = read_yaml(yaml_file)
    assert read_data["japanese"] == "日本語"
    assert read_data["emoji"] == "🎉"
    assert read_data["chinese"] == "中文"


def test_write_yaml_preserves_order(tmp_path: Path) -> None:
    """Test that write_yaml preserves dictionary order (Python 3.7+)."""
    yaml_file = tmp_path / "order.yml"
    data = {
        "first": "1",
        "second": "2",
        "third": "3",
        "fourth": "4",
    }

    write_yaml(yaml_file, data, backup=False)

    # Read back and verify order is preserved
    content = yaml_file.read_text()
    lines = content.strip().split("\n")
    assert lines[0].startswith("first:")
    assert lines[1].startswith("second:")
    assert lines[2].startswith("third:")
    assert lines[3].startswith("fourth:")


def test_write_yaml_creates_timestamped_backup(tmp_path: Path) -> None:
    """Test that write_yaml creates timestamped backup via BackupManager."""
    yaml_file = tmp_path / "test.yml"
    backup_dir = tmp_path / "backups"

    # Write initial data
    data1 = {"version": "1.0", "count": 1}
    write_yaml(yaml_file, data1, backup=False)

    # Write again with backup enabled (default)
    data2 = {"version": "1.0", "count": 2}
    write_yaml(yaml_file, data2, backup=True)

    # Verify timestamped backup exists
    assert backup_dir.exists()
    backups = list(backup_dir.glob("test_*.yml"))
    assert len(backups) == 1
    assert backups[0].name.startswith("test_")

    # Verify backup contains old data
    from clauxton.utils.yaml_utils import read_yaml
    backup_data = read_yaml(backups[0])
    assert backup_data["count"] == 1

    # Verify current file has new data
    current_data = read_yaml(yaml_file)
    assert current_data["count"] == 2


def test_write_yaml_generation_limit(tmp_path: Path) -> None:
    """Test that write_yaml respects max_generations parameter."""
    yaml_file = tmp_path / "test.yml"
    backup_dir = tmp_path / "backups"

    # Write initial data
    data = {"version": "1.0", "count": 0}
    write_yaml(yaml_file, data, backup=False)

    # Write 12 times with max_generations=5
    for i in range(1, 13):
        data = {"version": "1.0", "count": i}
        write_yaml(yaml_file, data, backup=True, max_generations=5)

    # Verify only 5 backups exist
    backups = list(backup_dir.glob("test_*.yml"))
    assert len(backups) == 5

    # Verify backups contain most recent data (7-11, since 12 is current)
    from clauxton.utils.yaml_utils import read_yaml
    backup_counts = sorted([read_yaml(b)["count"] for b in backups])
    assert backup_counts == [7, 8, 9, 10, 11]


def test_write_yaml_legacy_bak_compatibility(tmp_path: Path) -> None:
    """Test that write_yaml still creates legacy .bak file."""
    yaml_file = tmp_path / "test.yml"
    bak_file = tmp_path / "test.yml.bak"

    # Write initial data
    data1 = {"version": "1.0", "data": "original"}
    write_yaml(yaml_file, data1, backup=False)

    # Write again with backup
    data2 = {"version": "1.0", "data": "updated"}
    write_yaml(yaml_file, data2, backup=True)

    # Verify legacy .bak exists
    assert bak_file.exists()

    # Verify .bak contains old data
    from clauxton.utils.yaml_utils import read_yaml
    bak_data = read_yaml(bak_file)
    assert bak_data["data"] == "original"


def test_write_yaml_performance(tmp_path: Path) -> None:
    """Test that backup creation is fast (< 100ms requirement)."""
    import time

    yaml_file = tmp_path / "test.yml"

    # Write initial data
    data = {"version": "1.0", "entries": [f"entry_{i}" for i in range(100)]}
    write_yaml(yaml_file, data, backup=False)

    # Measure backup creation time
    start = time.time()
    write_yaml(yaml_file, data, backup=True)
    elapsed = (time.time() - start) * 1000  # Convert to ms

    # Should be under 100ms
    assert elapsed < 100, f"Backup took {elapsed:.2f}ms (expected < 100ms)"


def test_read_yaml_large_file(tmp_path: Path) -> None:
    """Test reading a large YAML file with many entries."""
    yaml_file = tmp_path / "large.yml"

    # Create YAML with 1000 entries
    large_data = {
        "version": "1.0",
        "entries": [{"id": f"KB-20251019-{i:03d}", "title": f"Entry {i}"} for i in range(1000)],
    }

    write_yaml(yaml_file, large_data, backup=False)

    # Read back and verify
    read_data = read_yaml(yaml_file)
    assert len(read_data["entries"]) == 1000
    assert read_data["entries"][0]["id"] == "KB-20251019-000"
    assert read_data["entries"][999]["id"] == "KB-20251019-999"


def test_write_yaml_empty_dict(tmp_path: Path) -> None:
    """Test writing an empty dictionary."""
    yaml_file = tmp_path / "empty.yml"
    data = {}

    write_yaml(yaml_file, data, backup=False)

    # Read back
    read_data = read_yaml(yaml_file)
    assert read_data == {}


def test_write_yaml_nested_structures(tmp_path: Path) -> None:
    """Test writing deeply nested data structures."""
    yaml_file = tmp_path / "nested.yml"
    data = {
        "level1": {
            "level2": {
                "level3": {
                    "level4": {
                        "value": "deep",
                        "list": [1, 2, 3],
                    }
                }
            }
        }
    }

    write_yaml(yaml_file, data, backup=False)

    # Read back and verify
    read_data = read_yaml(yaml_file)
    assert read_data["level1"]["level2"]["level3"]["level4"]["value"] == "deep"
    assert read_data["level1"]["level2"]["level3"]["level4"]["list"] == [1, 2, 3]


def test_read_yaml_dangerous_tags_blocked(tmp_path: Path) -> None:
    """Test that yaml.safe_load blocks dangerous YAML tags."""
    yaml_file = tmp_path / "dangerous.yml"

    # YAML with Python object tag (should be blocked by safe_load)
    dangerous_yaml = """
version: 1.0
entries:
  - !!python/object/apply:os.system
    args: ['echo hacked']
"""
    yaml_file.write_text(dangerous_yaml, encoding="utf-8")

    # safe_load should raise an error for dangerous tags
    with pytest.raises(ValidationError) as exc_info:
        read_yaml(yaml_file)

    assert "Failed to parse YAML" in str(exc_info.value)


def test_read_yaml_with_special_characters(tmp_path: Path) -> None:
    """Test reading YAML with special characters and escape sequences."""
    yaml_file = tmp_path / "special.yml"
    data = {
        "quotes": 'He said "Hello"',
        "apostrophes": "It's working",
        "newlines": "Line 1\nLine 2",
        "tabs": "Col1\tCol2",
        "backslash": "C:\\Users\\test",
    }

    write_yaml(yaml_file, data, backup=False)

    # Read back and verify
    read_data = read_yaml(yaml_file)
    assert read_data["quotes"] == 'He said "Hello"'
    assert read_data["apostrophes"] == "It's working"
    assert read_data["newlines"] == "Line 1\nLine 2"
    assert read_data["tabs"] == "Col1\tCol2"
    assert read_data["backslash"] == "C:\\Users\\test"


def test_write_yaml_atomic_failure_cleanup(tmp_path: Path) -> None:
    """Test that temporary file is cleaned up if write fails."""
    yaml_file = tmp_path / "test.yml"
    temp_file = tmp_path / "test.yml.tmp"

    # Create a directory with the target file's name (will cause write to fail)
    yaml_file.mkdir()

    # Try to write (should fail)
    with pytest.raises(ValidationError):
        write_yaml(yaml_file, {"test": "data"}, backup=False)

    # Verify temp file was cleaned up
    assert not temp_file.exists()


def test_write_yaml_backup_failure_continues(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that write continues even if backup creation fails."""
    yaml_file = tmp_path / "test.yml"
    backup_dir = tmp_path / "backups"

    # Write initial data
    write_yaml(yaml_file, {"version": "1.0"}, backup=False)

    # Make backup directory read-only (backup will fail)
    backup_dir.mkdir(mode=0o700)
    backup_dir.chmod(0o500)

    try:
        # Write should succeed despite backup failure
        write_yaml(yaml_file, {"version": "2.0"}, backup=True)

        # Verify warning was printed
        captured = capsys.readouterr()
        assert "Warning" in captured.err
        assert "backup" in captured.err.lower()

        # Verify file was written with new data
        read_data = read_yaml(yaml_file)
        assert read_data["version"] == "2.0"
    finally:
        # Restore permissions
        backup_dir.chmod(0o700)


def test_write_yaml_readonly_parent_dir(tmp_path: Path) -> None:
    """Test write fails gracefully when parent directory is read-only."""
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir(mode=0o700)
    readonly_dir.chmod(0o500)

    yaml_file = readonly_dir / "test.yml"

    try:
        with pytest.raises(ValidationError) as exc_info:
            write_yaml(yaml_file, {"test": "data"}, backup=False)

        assert "Failed to write YAML" in str(exc_info.value)
    finally:
        # Restore permissions for cleanup
        readonly_dir.chmod(0o700)


def test_read_yaml_permission_denied(tmp_path: Path) -> None:
    """Test read fails gracefully when file is not readable."""
    yaml_file = tmp_path / "unreadable.yml"
    yaml_file.write_text("version: '1.0'", encoding="utf-8")

    # Make file unreadable
    yaml_file.chmod(0o000)

    try:
        with pytest.raises(ValidationError) as exc_info:
            read_yaml(yaml_file)

        assert "Failed to read YAML" in str(exc_info.value)
    finally:
        # Restore permissions for cleanup
        yaml_file.chmod(0o600)


def test_write_yaml_sequential_updates(tmp_path: Path) -> None:
    """Test multiple sequential writes maintain data integrity."""
    yaml_file = tmp_path / "sequential.yml"

    # Write multiple times sequentially
    for i in range(10):
        data = {"version": "1.0", "count": i, "data": f"update_{i}"}
        write_yaml(yaml_file, data, backup=False)

    # Verify final state
    final_data = read_yaml(yaml_file)
    assert final_data["count"] == 9
    assert final_data["data"] == "update_9"


def test_write_yaml_very_large_file(tmp_path: Path) -> None:
    """Test writing a very large YAML file (>1MB)."""
    yaml_file = tmp_path / "large.yml"

    # Create 10,000 entries (should be >1MB)
    large_data = {
        "version": "1.0",
        "entries": [
            {
                "id": f"KB-20251019-{i:05d}",
                "title": f"Entry {i}" * 10,  # Make each entry larger
                "content": f"Content for entry {i}" * 50,
                "tags": [f"tag{j}" for j in range(10)],
            }
            for i in range(10000)
        ],
    }

    # Write large file
    write_yaml(yaml_file, large_data, backup=False)

    # Verify file size
    file_size = yaml_file.stat().st_size
    assert file_size > 1_000_000, f"File size {file_size} is not >1MB"

    # Verify can read back
    read_data = read_yaml(yaml_file)
    assert len(read_data["entries"]) == 10000


def test_validate_kb_yaml_entries_with_invalid_items() -> None:
    """Test KB validation with entries containing invalid items."""
    data = {
        "version": "1.0",
        "project_name": "test",
        "entries": [
            {"id": "KB-001", "title": "Valid entry"},
            None,  # Invalid entry
            {"id": "KB-002", "title": "Another valid entry"},
        ],
    }

    # validate_kb_yaml only checks top-level structure, not individual entries
    # Individual entry validation is done by KnowledgeBase class
    result = validate_kb_yaml(data)
    assert result is True


def test_write_yaml_preserves_booleans_and_nulls(tmp_path: Path) -> None:
    """Test that write_yaml correctly preserves booleans and null values."""
    yaml_file = tmp_path / "types.yml"
    data = {
        "boolean_true": True,
        "boolean_false": False,
        "null_value": None,
        "zero": 0,
        "empty_string": "",
    }

    write_yaml(yaml_file, data, backup=False)

    # Read back and verify types are preserved
    read_data = read_yaml(yaml_file)
    assert read_data["boolean_true"] is True
    assert read_data["boolean_false"] is False
    assert read_data["null_value"] is None
    assert read_data["zero"] == 0
    assert read_data["empty_string"] == ""
