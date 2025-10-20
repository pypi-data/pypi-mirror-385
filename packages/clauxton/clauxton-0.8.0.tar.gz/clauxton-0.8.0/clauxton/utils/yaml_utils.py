"""
YAML utilities for safe, atomic file operations.

This module provides:
- Safe YAML reading with schema validation
- Atomic YAML writing (write to temp, then rename)
- Automatic backup creation before overwrites
- Error handling for malformed YAML

All operations prioritize data integrity and prevent corruption.
"""

import shutil
from pathlib import Path
from typing import Any, Dict

import yaml

from clauxton.core.models import ValidationError


def read_yaml(file_path: Path) -> Dict[str, Any]:
    """
    Read YAML file safely.

    Returns empty dict if file doesn't exist.
    Raises ValidationError if YAML is malformed.

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML data as dictionary

    Raises:
        ValidationError: If YAML is malformed or cannot be parsed

    Example:
        >>> data = read_yaml(Path(".clauxton/knowledge-base.yml"))
        >>> print(data.get("version"))
        1.0
    """
    if not file_path.exists():
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data is not None else {}
    except yaml.YAMLError as e:
        raise ValidationError(
            f"Failed to parse YAML file '{file_path}': {e}. "
            "The file may be corrupted. Check backups or fix manually."
        ) from e
    except Exception as e:
        raise ValidationError(
            f"Failed to read YAML file '{file_path}': {e}"
        ) from e


def write_yaml(file_path: Path, data: Dict[str, Any], backup: bool = True) -> None:
    """
    Write YAML file atomically (write to temp, then rename).

    If backup=True, creates .bak file before overwriting.
    Uses atomic rename to prevent data loss on crash.

    Args:
        file_path: Path to YAML file
        data: Data to write (must be dict)
        backup: Create backup before overwriting (default: True)

    Raises:
        ValidationError: If write operation fails

    Example:
        >>> data = {"version": "1.0", "entries": []}
        >>> write_yaml(Path(".clauxton/knowledge-base.yml"), data)
        # File written atomically with backup created
    """
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create backup if file exists and backup=True
    if backup and file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        try:
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            # Backup failure is not critical, warn but continue
            import sys

            print(
                f"Warning: Failed to create backup '{backup_path}': {e}",
                file=sys.stderr,
            )

    # Write to temporary file first (atomic write pattern)
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        # Atomic rename (POSIX guarantees atomicity)
        temp_path.replace(file_path)
    except Exception as e:
        # Clean up temp file on error
        if temp_path.exists():
            temp_path.unlink()
        raise ValidationError(
            f"Failed to write YAML file '{file_path}': {e}"
        ) from e


def validate_kb_yaml(data: Dict[str, Any]) -> bool:
    """
    Validate Knowledge Base YAML structure.

    Checks for required fields and basic schema compliance.

    Args:
        data: Parsed YAML data

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails

    Example:
        >>> data = {"version": "1.0", "project_name": "test", "entries": []}
        >>> validate_kb_yaml(data)
        True
    """
    # Check for required top-level fields
    if "version" not in data:
        raise ValidationError(
            "Invalid Knowledge Base YAML: missing 'version' field. "
            "Expected format: {version: '1.0', project_name: 'name', entries: []}"
        )

    if "project_name" not in data:
        raise ValidationError(
            "Invalid Knowledge Base YAML: missing 'project_name' field."
        )

    if "entries" not in data:
        raise ValidationError(
            "Invalid Knowledge Base YAML: missing 'entries' field. "
            "This should be a list of knowledge base entries."
        )

    # Check entries is a list
    if not isinstance(data["entries"], list):
        entries_type = type(data["entries"]).__name__
        raise ValidationError(
            f"Invalid Knowledge Base YAML: 'entries' must be a list, "
            f"got {entries_type}"
        )

    return True


def validate_tasks_yaml(data: Dict[str, Any]) -> bool:
    """
    Validate Tasks YAML structure.

    Checks for required fields and basic schema compliance.
    (Full implementation in Phase 1)

    Args:
        data: Parsed YAML data

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails

    Example:
        >>> data = {"version": "1.0", "tasks": []}
        >>> validate_tasks_yaml(data)
        True
    """
    if "version" not in data:
        raise ValidationError("Invalid Tasks YAML: missing 'version' field.")

    if "tasks" not in data:
        raise ValidationError("Invalid Tasks YAML: missing 'tasks' field.")

    if not isinstance(data["tasks"], list):
        raise ValidationError(
            f"Invalid Tasks YAML: 'tasks' must be a list, got {type(data['tasks']).__name__}"
        )

    return True
