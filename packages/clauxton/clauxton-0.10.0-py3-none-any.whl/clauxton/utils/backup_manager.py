"""
Backup management for Clauxton data files.

This module provides:
- Timestamped backup creation
- Generation limit management (default: 10)
- Automatic cleanup of old backups
- Backup listing and restoration

All backups are stored in .clauxton/backups/ with format:
  filename_YYYYMMDD_HHMMSS_microseconds.yml
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from clauxton.core.models import ValidationError


class BackupManager:
    """
    Manages timestamped backups with generation limit.

    Backups are stored in .clauxton/backups/ directory with format:
      filename_YYYYMMDD_HHMMSS_microseconds.yml

    Example:
        >>> bm = BackupManager(Path(".clauxton/backups"))
        >>> backup = bm.create_backup(Path(".clauxton/tasks.yml"))
        >>> print(backup.name)
        tasks_20251021_143052_123456.yml
    """

    def __init__(self, backup_dir: Path):
        """
        Initialize BackupManager.

        Args:
            backup_dir: Directory to store backups (e.g., .clauxton/backups/)
        """
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    def create_backup(
        self, file_path: Path, max_generations: int = 10
    ) -> Path:
        """
        Create timestamped backup and cleanup old generations.

        Args:
            file_path: File to backup
            max_generations: Max backups to keep (default: 10)

        Returns:
            Path to created backup file

        Raises:
            ValidationError: If backup creation fails

        Example:
            >>> bm = BackupManager(Path(".clauxton/backups"))
            >>> backup = bm.create_backup(Path(".clauxton/tasks.yml"))
            >>> backup.exists()
            True
        """
        if not file_path.exists():
            raise ValidationError(
                f"Cannot backup non-existent file: {file_path}\n\n"
                f"Suggestion: Check if the file path is correct.\n"
                f"  - List files: ls -la {file_path.parent}\n"
                f"  - Check if Clauxton is initialized: clauxton init"
            )

        # Generate timestamped backup filename with microseconds for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name

        try:
            # Copy file to backup location
            shutil.copy2(file_path, backup_path)
            # Set restrictive permissions
            backup_path.chmod(0o600)
        except Exception as e:
            raise ValidationError(
                f"Failed to create backup for '{file_path}': {e}\n\n"
                f"Suggestion: Check permissions and disk space.\n"
                f"  - Check permissions: ls -la {file_path}\n"
                f"  - Check disk space: df -h {file_path.parent}"
            ) from e

        # Cleanup old backups
        try:
            self.cleanup_old_backups(file_path, max_generations)
        except Exception as e:
            # Cleanup failure is not critical, warn but continue
            import sys

            print(
                f"Warning: Failed to cleanup old backups: {e}",
                file=sys.stderr,
            )

        return backup_path

    def cleanup_old_backups(
        self, file_path: Path, max_generations: int = 10
    ) -> List[Path]:
        """
        Remove old backups beyond max_generations.

        Args:
            file_path: Original file path
            max_generations: Max backups to keep

        Returns:
            List of deleted backup paths

        Example:
            >>> bm = BackupManager(Path(".clauxton/backups"))
            >>> deleted = bm.cleanup_old_backups(Path(".clauxton/tasks.yml"), max_generations=5)
            >>> len(deleted)
            3
        """
        # Get all backups for this file
        backups = self.list_backups(file_path)

        # If within limit, nothing to delete
        if len(backups) <= max_generations:
            return []

        # Delete oldest backups (beyond max_generations)
        deleted = []
        for backup in backups[max_generations:]:
            try:
                backup.unlink()
                deleted.append(backup)
            except Exception as e:
                import sys

                print(
                    f"Warning: Failed to delete old backup '{backup}': {e}",
                    file=sys.stderr,
                )

        return deleted

    def list_backups(self, file_path: Path) -> List[Path]:
        """
        List all backups for a file, sorted by timestamp (newest first).

        Args:
            file_path: Original file path

        Returns:
            List of backup paths (sorted newest to oldest)

        Example:
            >>> bm = BackupManager(Path(".clauxton/backups"))
            >>> backups = bm.list_backups(Path(".clauxton/tasks.yml"))
            >>> for backup in backups:
            ...     print(backup.name)
            tasks_20251021_143052_123456.yml
            tasks_20251021_142030_654321.yml
        """
        # Pattern: filename_YYYYMMDD_HHMMSS_microseconds.yml
        pattern = f"{file_path.stem}_*{file_path.suffix}"
        backups = sorted(
            self.backup_dir.glob(pattern),
            key=lambda p: p.name,
            reverse=True,  # Newest first
        )
        return backups

    def restore_backup(self, backup_path: Path, target_path: Path) -> None:
        """
        Restore a backup to target path.

        Args:
            backup_path: Backup file to restore
            target_path: Destination path

        Raises:
            ValidationError: If restoration fails

        Example:
            >>> bm = BackupManager(Path(".clauxton/backups"))
            >>> bm.restore_backup(
            ...     Path(".clauxton/backups/tasks_20251021_143052_123456.yml"),
            ...     Path(".clauxton/tasks.yml")
            ... )
        """
        if not backup_path.exists():
            raise ValidationError(
                f"Backup file not found: {backup_path}\n\n"
                f"Suggestion: List available backups.\n"
                f"  - List backups: ls -la {self.backup_dir}\n"
                f"  - CLI command: clauxton backup list"
            )

        try:
            shutil.copy2(backup_path, target_path)
            # Set restrictive permissions
            target_path.chmod(0o600)
        except Exception as e:
            raise ValidationError(
                f"Failed to restore backup '{backup_path}' to '{target_path}': {e}\n\n"
                f"Suggestion: Check permissions and disk space.\n"
                f"  - Check target directory: ls -la {target_path.parent}\n"
                f"  - Check disk space: df -h {target_path.parent}"
            ) from e

    def get_latest_backup(self, file_path: Path) -> Path | None:
        """
        Get the most recent backup for a file.

        Args:
            file_path: Original file path

        Returns:
            Path to latest backup, or None if no backups exist

        Example:
            >>> bm = BackupManager(Path(".clauxton/backups"))
            >>> latest = bm.get_latest_backup(Path(".clauxton/tasks.yml"))
            >>> latest.name if latest else None
            'tasks_20251021_143052_123456.yml'
        """
        backups = self.list_backups(file_path)
        return backups[0] if backups else None

    def count_backups(self, file_path: Path) -> int:
        """
        Count number of backups for a file.

        Args:
            file_path: Original file path

        Returns:
            Number of backups

        Example:
            >>> bm = BackupManager(Path(".clauxton/backups"))
            >>> bm.count_backups(Path(".clauxton/tasks.yml"))
            5
        """
        return len(self.list_backups(file_path))
