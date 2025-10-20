"""
File utilities for secure file and directory management.

This module provides:
- .clauxton/ directory creation with proper permissions
- Secure file permission setting (600/700)
- Path validation and safety checks

All operations prioritize security and prevent unauthorized access.
"""

import os
from pathlib import Path


def ensure_clauxton_dir(root_dir: Path) -> Path:
    """
    Create .clauxton/ directory with proper permissions.

    Sets permissions: 700 (drwx------) for privacy.
    Creates directory if it doesn't exist.

    Args:
        root_dir: Project root directory

    Returns:
        Path to .clauxton/ directory

    Example:
        >>> clauxton_dir = ensure_clauxton_dir(Path("/path/to/project"))
        >>> clauxton_dir.exists()
        True
        >>> oct(clauxton_dir.stat().st_mode)[-3:]
        '700'
    """
    clauxton_dir = root_dir / ".clauxton"

    # Create directory if it doesn't exist
    clauxton_dir.mkdir(parents=True, exist_ok=True)

    # Set secure permissions: 700 (owner read/write/execute only)
    # This prevents other users from reading project context
    set_secure_directory_permissions(clauxton_dir)

    return clauxton_dir


def set_secure_permissions(file_path: Path) -> None:
    """
    Set file permissions to 600 (rw-------).

    Owner can read/write, no access for others.

    Args:
        file_path: Path to file

    Example:
        >>> path = Path(".clauxton/knowledge-base.yml")
        >>> set_secure_permissions(path)
        >>> oct(path.stat().st_mode)[-3:]
        '600'
    """
    if file_path.exists():
        # 0o600 = rw------- (owner read/write only)
        os.chmod(file_path, 0o600)


def set_secure_directory_permissions(dir_path: Path) -> None:
    """
    Set directory permissions to 700 (drwx------).

    Owner can read/write/execute, no access for others.

    Args:
        dir_path: Path to directory

    Example:
        >>> path = Path(".clauxton")
        >>> set_secure_directory_permissions(path)
        >>> oct(path.stat().st_mode)[-3:]
        '700'
    """
    if dir_path.exists() and dir_path.is_dir():
        # 0o700 = drwx------ (owner read/write/execute only)
        os.chmod(dir_path, 0o700)


def validate_path_in_project(root_dir: Path, target_path: Path) -> bool:
    """
    Validate that target_path is within root_dir (prevent path traversal).

    Args:
        root_dir: Project root directory
        target_path: Path to validate

    Returns:
        True if target_path is within root_dir

    Raises:
        ValueError: If target_path is outside root_dir

    Example:
        >>> root = Path("/home/user/project")
        >>> validate_path_in_project(root, root / "src" / "main.py")
        True
        >>> validate_path_in_project(root, Path("/etc/passwd"))
        Traceback (most recent call last):
        ...
        ValueError: Path traversal detected...
    """
    try:
        # Resolve both paths to absolute, canonical paths
        root_resolved = root_dir.resolve()
        target_resolved = target_path.resolve()

        # Check if target is relative to root
        target_resolved.relative_to(root_resolved)
        return True
    except ValueError as e:
        raise ValueError(
            f"Path traversal detected: '{target_path}' is outside project root '{root_dir}'"
        ) from e
