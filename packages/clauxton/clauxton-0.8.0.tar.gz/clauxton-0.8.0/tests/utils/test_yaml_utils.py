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
