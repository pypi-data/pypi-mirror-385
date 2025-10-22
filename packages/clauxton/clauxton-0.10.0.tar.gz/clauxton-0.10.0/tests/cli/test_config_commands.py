"""
Tests for CLI config commands.

Tests cover:
- config set command (mode and thresholds)
- config get command
- config list command
- Error handling
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
# config set command tests
# ============================================================================


def test_config_set_mode_always(runner: CliRunner, temp_project: Path) -> None:
    """Test 'clauxton config set confirmation_mode always' command."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Set mode to "always"
        result = runner.invoke(cli, ["config", "set", "confirmation_mode", "always"])

        assert result.exit_code == 0
        assert "confirmation_mode" in result.output
        assert "always" in result.output

        # Verify mode is set
        result_get = runner.invoke(cli, ["config", "get", "confirmation_mode"])
        assert result_get.exit_code == 0
        assert "always" in result_get.output


def test_config_set_mode_auto(runner: CliRunner, temp_project: Path) -> None:
    """Test 'clauxton config set confirmation_mode auto' command."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Set mode to "auto"
        result = runner.invoke(cli, ["config", "set", "confirmation_mode", "auto"])

        assert result.exit_code == 0
        assert "confirmation_mode" in result.output
        assert "auto" in result.output


def test_config_set_mode_never(runner: CliRunner, temp_project: Path) -> None:
    """Test 'clauxton config set confirmation_mode never' command."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Set mode to "never"
        result = runner.invoke(cli, ["config", "set", "confirmation_mode", "never"])

        assert result.exit_code == 0
        assert "confirmation_mode" in result.output
        assert "never" in result.output


def test_config_set_invalid_mode(runner: CliRunner, temp_project: Path) -> None:
    """Test setting invalid confirmation mode fails with error."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Try to set invalid mode
        result = runner.invoke(cli, ["config", "set", "confirmation_mode", "invalid"])

        assert result.exit_code != 0
        assert "Error" in result.output or "Invalid" in result.output


def test_config_set_threshold(runner: CliRunner, temp_project: Path) -> None:
    """Test 'clauxton config set task_import_threshold' command."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Set threshold
        result = runner.invoke(
            cli, ["config", "set", "task_import_threshold", "20"]
        )

        assert result.exit_code == 0
        assert "task_import_threshold" in result.output
        assert "20" in result.output

        # Verify threshold is set
        result_get = runner.invoke(cli, ["config", "get", "task_import_threshold"])
        assert result_get.exit_code == 0
        assert "20" in result_get.output


def test_config_set_multiple_thresholds(runner: CliRunner, temp_project: Path) -> None:
    """Test setting multiple thresholds."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Set multiple thresholds
        runner.invoke(cli, ["config", "set", "task_import_threshold", "15"])
        runner.invoke(cli, ["config", "set", "task_delete_threshold", "8"])
        runner.invoke(cli, ["config", "set", "kb_delete_threshold", "5"])

        # Verify all are set
        result_import = runner.invoke(cli, ["config", "get", "task_import_threshold"])
        assert "15" in result_import.output

        result_delete = runner.invoke(cli, ["config", "get", "task_delete_threshold"])
        assert "8" in result_delete.output

        result_kb = runner.invoke(cli, ["config", "get", "kb_delete_threshold"])
        assert "5" in result_kb.output


def test_config_set_invalid_threshold_value(
    runner: CliRunner, temp_project: Path
) -> None:
    """Test setting non-numeric threshold value fails."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Try to set non-numeric value
        result = runner.invoke(
            cli, ["config", "set", "task_import_threshold", "not_a_number"]
        )

        assert result.exit_code != 0
        assert "Error" in result.output or "Invalid" in result.output


def test_config_set_unknown_key(runner: CliRunner, temp_project: Path) -> None:
    """Test setting unknown configuration key fails."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Try to set unknown key
        result = runner.invoke(cli, ["config", "set", "unknown_key", "value"])

        assert result.exit_code != 0
        assert "Error" in result.output or "Unknown" in result.output


def test_config_set_without_init(runner: CliRunner, temp_project: Path) -> None:
    """Test config set without init fails with error."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Try to set config without init
        result = runner.invoke(cli, ["config", "set", "confirmation_mode", "always"])

        assert result.exit_code != 0
        assert "not initialized" in result.output or "init" in result.output


# ============================================================================
# config get command tests
# ============================================================================


def test_config_get_mode(runner: CliRunner, temp_project: Path) -> None:
    """Test 'clauxton config get confirmation_mode' command."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Get default mode (should be "auto")
        result = runner.invoke(cli, ["config", "get", "confirmation_mode"])

        assert result.exit_code == 0
        assert "auto" in result.output


def test_config_get_threshold(runner: CliRunner, temp_project: Path) -> None:
    """Test 'clauxton config get task_import_threshold' command."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Get default threshold
        result = runner.invoke(cli, ["config", "get", "task_import_threshold"])

        assert result.exit_code == 0
        # Should return a numeric value
        assert result.output.strip().isdigit()


def test_config_get_unknown_key(runner: CliRunner, temp_project: Path) -> None:
    """Test getting unknown configuration key fails."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Try to get unknown key
        result = runner.invoke(cli, ["config", "get", "unknown_key"])

        assert result.exit_code != 0
        assert "Error" in result.output or "Unknown" in result.output


def test_config_get_without_init(runner: CliRunner, temp_project: Path) -> None:
    """Test config get without init fails with error."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Try to get config without init
        result = runner.invoke(cli, ["config", "get", "confirmation_mode"])

        assert result.exit_code != 0
        assert "not initialized" in result.output or "init" in result.output


# ============================================================================
# config list command tests
# ============================================================================


def test_config_list_default(runner: CliRunner, temp_project: Path) -> None:
    """Test 'clauxton config list' command shows default values."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # List all config
        result = runner.invoke(cli, ["config", "list"])

        assert result.exit_code == 0
        assert "Clauxton Configuration" in result.output
        assert "confirmation_mode" in result.output
        assert "auto" in result.output  # Default mode
        assert "task_import_threshold" in result.output
        # Default thresholds should be present
        assert "task_delete_threshold" in result.output
        assert "kb_delete_threshold" in result.output


def test_config_list_after_changes(runner: CliRunner, temp_project: Path) -> None:
    """Test 'clauxton config list' command shows updated values."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize Clauxton
        runner.invoke(cli, ["init"])

        # Make changes
        runner.invoke(cli, ["config", "set", "confirmation_mode", "always"])
        runner.invoke(cli, ["config", "set", "task_import_threshold", "25"])

        # List all config
        result = runner.invoke(cli, ["config", "list"])

        assert result.exit_code == 0
        assert "always" in result.output
        assert "25" in result.output


def test_config_list_without_init(runner: CliRunner, temp_project: Path) -> None:
    """Test config list without init fails with error."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Try to list config without init
        result = runner.invoke(cli, ["config", "list"])

        assert result.exit_code != 0
        assert "not initialized" in result.output or "init" in result.output


# ============================================================================
# Integration tests
# ============================================================================


def test_config_roundtrip(runner: CliRunner, temp_project: Path) -> None:
    """Test set -> get -> list workflow."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # Set values
        runner.invoke(cli, ["config", "set", "confirmation_mode", "never"])
        runner.invoke(cli, ["config", "set", "task_import_threshold", "30"])

        # Get values
        result_mode = runner.invoke(cli, ["config", "get", "confirmation_mode"])
        assert "never" in result_mode.output

        result_threshold = runner.invoke(cli, ["config", "get", "task_import_threshold"])
        assert "30" in result_threshold.output

        # List all
        result_list = runner.invoke(cli, ["config", "list"])
        assert "never" in result_list.output
        assert "30" in result_list.output


def test_config_set_negative_threshold_validation_error(
    runner: CliRunner, temp_project: Path
) -> None:
    """Test setting negative threshold triggers ValidationError."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # Try to set negative threshold (should raise ValidationError)
        result = runner.invoke(cli, ["config", "set", "task_import_threshold", "-5"])

        assert result.exit_code != 0
        assert "Error" in result.output


def test_config_set_zero_threshold_validation_error(
    runner: CliRunner, temp_project: Path
) -> None:
    """Test setting zero threshold triggers ValidationError."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize
        runner.invoke(cli, ["init"])

        # Try to set zero threshold (should raise ValidationError)
        result = runner.invoke(cli, ["config", "set", "task_delete_threshold", "0"])

        assert result.exit_code != 0
        assert "Error" in result.output
