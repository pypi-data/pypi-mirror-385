"""
Tests for file utilities.

Tests cover:
- Directory creation with proper permissions
- File permission setting
- Path validation (prevent path traversal)
"""

from pathlib import Path

import pytest

from clauxton.utils.file_utils import (
    ensure_clauxton_dir,
    set_secure_directory_permissions,
    set_secure_permissions,
    validate_path_in_project,
)


def test_ensure_clauxton_dir_creates_directory(tmp_path: Path) -> None:
    """Test that ensure_clauxton_dir creates .clauxton/ directory."""
    clauxton_dir = ensure_clauxton_dir(tmp_path)

    assert clauxton_dir.exists()
    assert clauxton_dir.is_dir()
    assert clauxton_dir.name == ".clauxton"


def test_ensure_clauxton_dir_sets_permissions(tmp_path: Path) -> None:
    """Test that ensure_clauxton_dir sets 700 permissions."""
    clauxton_dir = ensure_clauxton_dir(tmp_path)

    # Get permissions (last 3 octal digits)
    perms = oct(clauxton_dir.stat().st_mode)[-3:]
    assert perms == "700"


def test_ensure_clauxton_dir_idempotent(tmp_path: Path) -> None:
    """Test that ensure_clauxton_dir can be called multiple times safely."""
    clauxton_dir1 = ensure_clauxton_dir(tmp_path)
    clauxton_dir2 = ensure_clauxton_dir(tmp_path)

    assert clauxton_dir1 == clauxton_dir2
    assert clauxton_dir1.exists()


def test_set_secure_permissions(tmp_path: Path) -> None:
    """Test that set_secure_permissions sets 600 permissions."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    set_secure_permissions(test_file)

    perms = oct(test_file.stat().st_mode)[-3:]
    assert perms == "600"


def test_set_secure_permissions_nonexistent(tmp_path: Path) -> None:
    """Test that set_secure_permissions does nothing for nonexistent file."""
    test_file = tmp_path / "nonexistent.txt"

    # Should not raise error
    set_secure_permissions(test_file)

    assert not test_file.exists()


def test_set_secure_directory_permissions(tmp_path: Path) -> None:
    """Test that set_secure_directory_permissions sets 700 permissions."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    set_secure_directory_permissions(test_dir)

    perms = oct(test_dir.stat().st_mode)[-3:]
    assert perms == "700"


def test_set_secure_directory_permissions_nonexistent(tmp_path: Path) -> None:
    """Test that set_secure_directory_permissions does nothing for nonexistent directory."""
    test_dir = tmp_path / "nonexistent_dir"

    # Should not raise error
    set_secure_directory_permissions(test_dir)

    assert not test_dir.exists()


def test_validate_path_in_project_valid(tmp_path: Path) -> None:
    """Test that validate_path_in_project returns True for valid path."""
    valid_path = tmp_path / "src" / "main.py"

    result = validate_path_in_project(tmp_path, valid_path)

    assert result is True


def test_validate_path_in_project_nested(tmp_path: Path) -> None:
    """Test that validate_path_in_project works for deeply nested paths."""
    nested_path = tmp_path / "a" / "b" / "c" / "d" / "file.py"

    result = validate_path_in_project(tmp_path, nested_path)

    assert result is True


def test_validate_path_in_project_outside(tmp_path: Path) -> None:
    """Test that validate_path_in_project raises error for path outside project."""
    outside_path = Path("/etc/passwd")

    with pytest.raises(ValueError) as exc_info:
        validate_path_in_project(tmp_path, outside_path)

    assert "Path traversal detected" in str(exc_info.value)
    assert "/etc/passwd" in str(exc_info.value)


def test_validate_path_in_project_parent_traversal(tmp_path: Path) -> None:
    """Test that validate_path_in_project detects .. traversal."""
    # Create a path that tries to escape using ..
    traversal_path = tmp_path / ".." / ".." / "etc" / "passwd"

    with pytest.raises(ValueError) as exc_info:
        validate_path_in_project(tmp_path, traversal_path)

    assert "Path traversal detected" in str(exc_info.value)


def test_validate_path_in_project_same_directory(tmp_path: Path) -> None:
    """Test that validate_path_in_project works for root directory itself."""
    result = validate_path_in_project(tmp_path, tmp_path)

    assert result is True
