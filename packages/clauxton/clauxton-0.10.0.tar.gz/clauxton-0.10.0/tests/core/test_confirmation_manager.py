"""
Tests for ConfirmationManager.

Tests confirmation mode management and threshold configuration.
"""

from pathlib import Path

import pytest

from clauxton.core.confirmation_manager import ConfirmationManager
from clauxton.core.models import ValidationError


def test_confirmation_manager_init(tmp_path: Path) -> None:
    """Test ConfirmationManager initialization creates config if missing."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)

    # Config file should be created
    assert (clauxton_dir / "config.yml").exists()

    # Default mode should be "auto"
    assert cm.get_mode() == "auto"

    # Default thresholds should be loaded
    assert cm.get_threshold("task_import") == 10
    assert cm.get_threshold("task_delete") == 5
    assert cm.get_threshold("kb_delete") == 3
    assert cm.get_threshold("kb_import") == 5


def test_get_set_mode(tmp_path: Path) -> None:
    """Test getting and setting confirmation mode."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)

    # Default mode is "auto"
    assert cm.get_mode() == "auto"

    # Set to "always"
    cm.set_mode("always")
    assert cm.get_mode() == "always"

    # Set to "never"
    cm.set_mode("never")
    assert cm.get_mode() == "never"

    # Set back to "auto"
    cm.set_mode("auto")
    assert cm.get_mode() == "auto"


def test_should_confirm_always_mode(tmp_path: Path) -> None:
    """Test should_confirm returns True for all operations in 'always' mode."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)
    cm.set_mode("always")

    # Should always confirm regardless of count
    assert cm.should_confirm("task_import", 1) is True
    assert cm.should_confirm("task_import", 5) is True
    assert cm.should_confirm("task_import", 100) is True
    assert cm.should_confirm("task_delete", 1) is True
    assert cm.should_confirm("kb_delete", 1) is True


def test_should_confirm_auto_mode(tmp_path: Path) -> None:
    """Test should_confirm respects thresholds in 'auto' mode."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)
    cm.set_mode("auto")

    # Below threshold (task_import default: 10)
    assert cm.should_confirm("task_import", 1) is False
    assert cm.should_confirm("task_import", 5) is False
    assert cm.should_confirm("task_import", 9) is False

    # At or above threshold
    assert cm.should_confirm("task_import", 10) is True
    assert cm.should_confirm("task_import", 15) is True
    assert cm.should_confirm("task_import", 100) is True

    # Test task_delete (default: 5)
    assert cm.should_confirm("task_delete", 4) is False
    assert cm.should_confirm("task_delete", 5) is True
    assert cm.should_confirm("task_delete", 10) is True

    # Test kb_delete (default: 3)
    assert cm.should_confirm("kb_delete", 2) is False
    assert cm.should_confirm("kb_delete", 3) is True
    assert cm.should_confirm("kb_delete", 5) is True


def test_should_confirm_never_mode(tmp_path: Path) -> None:
    """Test should_confirm returns False for all operations in 'never' mode."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)
    cm.set_mode("never")

    # Should never confirm regardless of count
    assert cm.should_confirm("task_import", 1) is False
    assert cm.should_confirm("task_import", 100) is False
    assert cm.should_confirm("task_delete", 50) is False
    assert cm.should_confirm("kb_delete", 20) is False


def test_get_set_threshold(tmp_path: Path) -> None:
    """Test getting and setting thresholds."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)

    # Default threshold
    assert cm.get_threshold("task_import") == 10

    # Set custom threshold
    cm.set_threshold("task_import", 20)
    assert cm.get_threshold("task_import") == 20

    # Set threshold for new operation type
    cm.set_threshold("custom_operation", 15)
    assert cm.get_threshold("custom_operation") == 15

    # Unknown operation type returns default (10)
    assert cm.get_threshold("unknown_operation") == 10


def test_invalid_mode(tmp_path: Path) -> None:
    """Test setting invalid mode raises ValidationError."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)

    with pytest.raises(ValidationError, match="Invalid confirmation mode"):
        cm.set_mode("invalid")  # type: ignore

    with pytest.raises(ValidationError, match="Invalid confirmation mode"):
        cm.set_mode("enabled")  # type: ignore


def test_invalid_threshold(tmp_path: Path) -> None:
    """Test setting invalid threshold raises ValidationError."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)

    # Threshold must be >= 1
    with pytest.raises(ValidationError, match="Invalid threshold value"):
        cm.set_threshold("task_import", 0)

    with pytest.raises(ValidationError, match="Invalid threshold value"):
        cm.set_threshold("task_import", -5)


def test_config_persistence(tmp_path: Path) -> None:
    """Test configuration persists across instances."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    # First instance - set values
    cm1 = ConfirmationManager(clauxton_dir)
    cm1.set_mode("always")
    cm1.set_threshold("task_import", 25)

    # Second instance - should load saved values
    cm2 = ConfirmationManager(clauxton_dir)
    assert cm2.get_mode() == "always"
    assert cm2.get_threshold("task_import") == 25


def test_get_all_config(tmp_path: Path) -> None:
    """Test get_all_config returns complete configuration."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)
    cm.set_mode("always")
    cm.set_threshold("task_import", 30)

    config = cm.get_all_config()

    assert config["version"] == "1.0"
    assert config["confirmation_mode"] == "always"
    assert config["confirmation_thresholds"]["task_import"] == 30
    assert "task_delete" in config["confirmation_thresholds"]


def test_malformed_config_recovery(tmp_path: Path) -> None:
    """Test recovery from malformed configuration file."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    # Create valid config first
    cm1 = ConfirmationManager(clauxton_dir)
    cm1.set_mode("always")

    # Manually corrupt the config with invalid mode
    config_path = clauxton_dir / "config.yml"
    with open(config_path, "w") as f:
        f.write("version: '1.0'\nconfirmation_mode: invalid_mode\n")

    # Load with corrupted config - should reset to default "auto"
    cm2 = ConfirmationManager(clauxton_dir)
    assert cm2.get_mode() == "auto"  # Should reset invalid mode to default


def test_custom_threshold_in_auto_mode(tmp_path: Path) -> None:
    """Test custom thresholds work correctly in auto mode."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)
    cm.set_mode("auto")

    # Set custom threshold
    cm.set_threshold("task_import", 5)

    # Test with custom threshold
    assert cm.should_confirm("task_import", 4) is False
    assert cm.should_confirm("task_import", 5) is True
    assert cm.should_confirm("task_import", 10) is True


def test_partial_config_merge(tmp_path: Path) -> None:
    """Test merging when config has partial thresholds."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    # Create config with only some thresholds
    from clauxton.utils.yaml_utils import write_yaml
    config_path = clauxton_dir / "config.yml"
    partial_config = {
        "version": "1.0",
        "confirmation_mode": "auto",
        "confirmation_thresholds": {
            "task_import": 20,  # Only one threshold
        }
    }
    write_yaml(config_path, partial_config)

    # Load should merge missing defaults
    cm = ConfirmationManager(clauxton_dir)

    assert cm.get_threshold("task_import") == 20  # Preserved
    assert cm.get_threshold("task_delete") == 5   # Default merged
    assert cm.get_threshold("kb_delete") == 3     # Default merged
    assert cm.get_threshold("kb_import") == 5     # Default merged


def test_unicode_operation_type(tmp_path: Path) -> None:
    """Test operation types with Unicode characters."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    cm = ConfirmationManager(clauxton_dir)

    # Set threshold with Unicode operation type
    cm.set_threshold("タスク削除", 8)
    assert cm.get_threshold("タスク削除") == 8

    # Test should_confirm with Unicode
    cm.set_mode("auto")
    assert cm.should_confirm("タスク削除", 7) is False
    assert cm.should_confirm("タスク削除", 8) is True


def test_empty_thresholds_in_config(tmp_path: Path) -> None:
    """Test loading config with empty confirmation_thresholds."""
    clauxton_dir = tmp_path / ".clauxton"
    clauxton_dir.mkdir()

    from clauxton.utils.yaml_utils import write_yaml
    config_path = clauxton_dir / "config.yml"
    empty_config = {
        "version": "1.0",
        "confirmation_mode": "never",
        "confirmation_thresholds": {}  # Empty
    }
    write_yaml(config_path, empty_config)

    # Load should populate defaults
    cm = ConfirmationManager(clauxton_dir)

    assert cm.get_mode() == "never"
    assert cm.get_threshold("task_import") == 10  # Default
    assert cm.get_threshold("task_delete") == 5   # Default
