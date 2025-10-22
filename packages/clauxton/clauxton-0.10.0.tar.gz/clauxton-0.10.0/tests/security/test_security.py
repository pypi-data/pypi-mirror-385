"""
Security tests for Clauxton.

Tests core security features:
- YAML injection protection (dangerous tags)
- File permissions
- YAML bomb protection
"""

from pathlib import Path

import pytest

from clauxton.core.models import ValidationError
from clauxton.utils.logger import ClauxtonLogger
from clauxton.utils.yaml_utils import read_yaml


def test_yaml_safe_load_blocks_python_execution(tmp_path: Path) -> None:
    """Test that yaml.safe_load blocks Python code execution."""
    yaml_file = tmp_path / "malicious.yml"

    # YAML with Python object instantiation
    malicious_yaml = """
!!python/object/apply:os.system
args: ['touch /tmp/hacked']
"""
    yaml_file.write_text(malicious_yaml, encoding="utf-8")

    # safe_load should reject this
    with pytest.raises(ValidationError):
        read_yaml(yaml_file)

    # Verify no file was created (command not executed)
    assert not Path("/tmp/hacked").exists()


def test_yaml_dangerous_tags_blocked(tmp_path: Path) -> None:
    """Test that dangerous YAML tags are blocked."""
    yaml_file = tmp_path / "dangerous.yml"

    dangerous_patterns = [
        # Python object instantiation
        "!!python/object:os.system",
        # Arbitrary code execution
        "!!python/object/apply:eval",
        # Module import
        "!!python/module:subprocess",
    ]

    for pattern in dangerous_patterns:
        yaml_file.write_text(f"data: {pattern}\n", encoding="utf-8")

        # Should reject dangerous tags
        with pytest.raises(ValidationError):
            read_yaml(yaml_file)


def test_log_files_have_secure_permissions(tmp_path: Path) -> None:
    """Test that log files have secure permissions."""
    logger = ClauxtonLogger(tmp_path)

    # Write log
    logger.log("test_operation", "info", "Test message")

    # Verify log file permissions
    logs_dir = tmp_path / ".clauxton" / "logs"
    for log_file in logs_dir.glob("*.log"):
        assert log_file.stat().st_mode & 0o777 == 0o600


def test_yaml_bomb_protection(tmp_path: Path) -> None:
    """Test that YAML bomb (billion laughs attack) is handled."""
    yaml_file = tmp_path / "bomb.yml"

    # YAML bomb (alias expansion)
    yaml_bomb = """
a: &a ["lol", "lol", "lol", "lol", "lol", "lol", "lol", "lol", "lol"]
b: &b [*a, *a, *a, *a, *a, *a, *a, *a, *a]
c: &c [*b, *b, *b, *b, *b, *b, *b, *b, *b]
"""
    yaml_file.write_text(yaml_bomb, encoding="utf-8")

    # PyYAML safe_load should handle this (may be slow but won't crash)
    try:
        data = read_yaml(yaml_file)
        # If it loads, verify it's just nested lists
        assert isinstance(data, dict)
    except (MemoryError, ValidationError):
        # Acceptable to reject if too large
        pass
