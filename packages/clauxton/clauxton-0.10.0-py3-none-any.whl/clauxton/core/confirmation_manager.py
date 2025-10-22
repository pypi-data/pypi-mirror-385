"""
Confirmation Manager for Clauxton.

Manages confirmation levels for operations with configurable modes.
"""

from pathlib import Path
from typing import Any, Dict, Literal

from clauxton.core.models import ValidationError
from clauxton.utils.file_utils import ensure_clauxton_dir
from clauxton.utils.yaml_utils import read_yaml, write_yaml

ConfirmationMode = Literal["always", "auto", "never"]

def _get_default_config() -> Dict[str, Any]:
    """
    Get default configuration.

    Returns a fresh copy to avoid mutation.
    """
    return {
        "version": "1.0",
        "confirmation_mode": "auto",  # Default to balanced mode
        "confirmation_thresholds": {
            "task_import": 10,
            "task_delete": 5,
            "kb_delete": 3,
            "kb_import": 5,
        },
    }


class ConfirmationManager:
    """
    Manage confirmation levels for operations.

    Supports 3 modes:
    - "always": Confirm all write operations (100% HITL)
    - "auto": Confirm based on thresholds (75% HITL, default)
    - "never": No confirmation prompts (25% HITL)

    Example:
        >>> cm = ConfirmationManager(Path(".clauxton"))
        >>> cm.set_mode("always")
        >>> cm.should_confirm("task_import", 5)
        True
    """

    def __init__(self, clauxton_dir: Path) -> None:
        """
        Initialize ConfirmationManager.

        Args:
            clauxton_dir: Path to .clauxton directory
        """
        self.clauxton_dir = clauxton_dir
        self.config_path = clauxton_dir / "config.yml"
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file or create default."""
        if not self.config_path.exists():
            # Create default config
            ensure_clauxton_dir(self.clauxton_dir)
            default_config = _get_default_config()
            write_yaml(self.config_path, default_config)
            self._config = default_config.copy()
        else:
            # Load existing config
            self._config = read_yaml(self.config_path)
            # Merge with defaults for missing keys
            default_config = _get_default_config()
            if "version" not in self._config:
                self._config["version"] = default_config["version"]
            if "confirmation_mode" not in self._config:
                self._config["confirmation_mode"] = default_config["confirmation_mode"]
            if "confirmation_thresholds" not in self._config:
                default_thresholds: Dict[str, int] = default_config["confirmation_thresholds"]  # type: ignore[assignment]
                self._config["confirmation_thresholds"] = default_thresholds.copy()
            else:
                # Merge threshold defaults
                default_thresholds_dict: Dict[str, int] = default_config["confirmation_thresholds"]  # type: ignore[assignment]
                for key, value in default_thresholds_dict.items():
                    if key not in self._config["confirmation_thresholds"]:
                        self._config["confirmation_thresholds"][key] = value

    def _save_config(self) -> None:
        """Save configuration to file."""
        write_yaml(self.config_path, self._config)

    def get_mode(self) -> ConfirmationMode:
        """
        Get current confirmation mode.

        Returns:
            Current mode: "always", "auto", or "never"

        Example:
            >>> cm.get_mode()
            'auto'
        """
        mode: str = self._config.get("confirmation_mode", "auto")
        if mode not in ["always", "auto", "never"]:
            # Invalid mode, reset to default
            mode = "auto"
            self._config["confirmation_mode"] = mode
            self._save_config()
        return mode  # type: ignore[return-value]

    def set_mode(self, mode: ConfirmationMode) -> None:
        """
        Set confirmation mode.

        Args:
            mode: New mode ("always", "auto", or "never")

        Raises:
            ValidationError: If mode is invalid

        Example:
            >>> cm.set_mode("always")
        """
        if mode not in ["always", "auto", "never"]:
            raise ValidationError(
                f"Invalid confirmation mode: {mode}. "
                "Must be 'always', 'auto', or 'never'."
            )
        self._config["confirmation_mode"] = mode
        self._save_config()

    def should_confirm(
        self, operation_type: str, operation_count: int = 1
    ) -> bool:
        """
        Check if confirmation is needed for an operation.

        Args:
            operation_type: Type of operation (e.g., "task_import", "task_delete")
            operation_count: Number of items affected (default: 1)

        Returns:
            True if confirmation is needed, False otherwise

        Logic:
            - "always" mode: Always return True
            - "never" mode: Always return False
            - "auto" mode: Return True if operation_count >= threshold

        Example:
            >>> cm.set_mode("auto")
            >>> cm.should_confirm("task_import", 5)
            False  # Below default threshold (10)
            >>> cm.should_confirm("task_import", 15)
            True   # Above threshold
        """
        mode = self.get_mode()

        if mode == "always":
            return True
        elif mode == "never":
            return False
        else:  # auto mode
            threshold = self.get_threshold(operation_type)
            return operation_count >= threshold

    def get_threshold(self, operation_type: str) -> int:
        """
        Get threshold for an operation type.

        Args:
            operation_type: Type of operation

        Returns:
            Threshold value (default: 10 if not configured)

        Example:
            >>> cm.get_threshold("task_import")
            10
        """
        thresholds: Dict[str, Any] = self._config.get("confirmation_thresholds", {})
        threshold: int = thresholds.get(operation_type, 10)
        return threshold

    def set_threshold(self, operation_type: str, value: int) -> None:
        """
        Set threshold for an operation type.

        Args:
            operation_type: Type of operation
            value: New threshold value (must be >= 1)

        Raises:
            ValidationError: If value < 1

        Example:
            >>> cm.set_threshold("task_import", 5)
        """
        if value < 1:
            raise ValidationError(
                f"Invalid threshold value: {value}. Must be >= 1."
            )

        if "confirmation_thresholds" not in self._config:
            self._config["confirmation_thresholds"] = {}

        self._config["confirmation_thresholds"][operation_type] = value
        self._save_config()

    def get_all_config(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dictionary with all configuration values

        Example:
            >>> cm.get_all_config()
            {'version': '1.0', 'confirmation_mode': 'auto', ...}
        """
        return self._config.copy()
