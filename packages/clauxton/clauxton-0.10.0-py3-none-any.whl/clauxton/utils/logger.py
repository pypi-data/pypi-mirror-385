"""
Logging utilities for Clauxton.

Provides structured logging with daily log files and automatic rotation.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from clauxton.utils.file_utils import ensure_clauxton_dir


class ClauxtonLogger:
    """
    Clauxton structured logger.

    Features:
    - Daily log files (.clauxton/logs/YYYY-MM-DD.log)
    - Automatic log rotation (30-day retention)
    - JSON-formatted log entries
    - Operation tracking with metadata

    Example:
        >>> logger = ClauxtonLogger(Path.cwd())
        >>> logger.log("task_add", "info", "Added task TASK-001", {"task_id": "TASK-001"})
        >>> logs = logger.get_recent_logs(limit=10)
    """

    def __init__(self, root_dir: Path) -> None:
        """
        Initialize ClauxtonLogger.

        Args:
            root_dir: Project root directory containing .clauxton/
        """
        self.root_dir: Path = root_dir
        clauxton_dir = ensure_clauxton_dir(root_dir)
        self.logs_dir: Path = clauxton_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True, mode=0o700)

    def log(
        self,
        operation: str,
        level: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Write log entry.

        Args:
            operation: Operation type (e.g., "task_add", "kb_search")
            level: Log level (debug, info, warning, error)
            message: Human-readable message
            metadata: Optional metadata dictionary

        Example:
            >>> logger.log(
            ...     "task_add",
            ...     "info",
            ...     "Added task TASK-001",
            ...     {"task_id": "TASK-001", "priority": "high"}
            ... )
        """
        # Rotate old logs before writing
        self._rotate_logs()

        # Get today's log file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"{today}.log"

        # Create log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "level": level.lower(),
            "message": message,
            "metadata": metadata or {},
        }

        # Append to log file (JSON Lines format)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Set file permissions (owner read/write only)
        log_file.chmod(0o600)

    def get_recent_logs(
        self,
        limit: int = 100,
        operation: Optional[str] = None,
        level: Optional[str] = None,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Get recent log entries.

        Args:
            limit: Maximum number of entries to return
            operation: Filter by operation type (optional)
            level: Filter by log level (optional)
            days: Number of days to look back (default: 7)

        Returns:
            List of log entries (newest first)

        Example:
            >>> logs = logger.get_recent_logs(limit=10, operation="task_add")
            >>> print(logs[0]["message"])
            Added task TASK-001
        """
        entries: List[Dict[str, Any]] = []

        # Get log files for the last N days
        end_date = datetime.now()

        for day_offset in range(days):
            date = end_date - timedelta(days=day_offset)
            date_str = date.strftime("%Y-%m-%d")
            log_file = self.logs_dir / f"{date_str}.log"

            if not log_file.exists():
                continue

            # Read log file (JSON Lines format)
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)

                        # Apply filters
                        if operation and entry.get("operation") != operation:
                            continue
                        if level and entry.get("level") != level.lower():
                            continue

                        entries.append(entry)

                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue

        # Sort by timestamp (newest first)
        entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

        # Apply limit
        return entries[:limit]

    def get_logs_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        Get all log entries for a specific date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            List of log entries for that date

        Example:
            >>> logs = logger.get_logs_by_date("2025-10-21")
            >>> len(logs)
            42
        """
        log_file = self.logs_dir / f"{date}.log"

        if not log_file.exists():
            return []

        entries: List[Dict[str, Any]] = []

        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue

        return entries

    def _rotate_logs(self, retention_days: int = 30) -> None:
        """
        Rotate old log files.

        Deletes log files older than retention_days.

        Args:
            retention_days: Number of days to keep logs (default: 30)
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        # Scan logs directory
        for log_file in self.logs_dir.glob("*.log"):
            # Parse date from filename (YYYY-MM-DD.log)
            try:
                date_str = log_file.stem  # Remove .log extension
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                # Delete if older than cutoff
                if file_date < cutoff_date:
                    log_file.unlink()

            except (ValueError, OSError):
                # Skip files with invalid names or errors
                continue

    def clear_logs(self) -> int:
        """
        Clear all log files.

        Returns:
            Number of files deleted

        Example:
            >>> count = logger.clear_logs()
            >>> print(f"Deleted {count} log files")
        """
        count = 0

        for log_file in self.logs_dir.glob("*.log"):
            try:
                log_file.unlink()
                count += 1
            except OSError:
                continue

        return count
