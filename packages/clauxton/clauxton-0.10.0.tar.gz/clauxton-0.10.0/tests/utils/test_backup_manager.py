"""
Tests for BackupManager class.

This module tests:
- Timestamped backup creation
- Generation limit management
- Backup listing and sorting
- Backup restoration
- Error handling
"""

import time
from pathlib import Path

import pytest

from clauxton.core.models import ValidationError
from clauxton.utils.backup_manager import BackupManager


def test_backup_manager_init(tmp_path: Path) -> None:
    """Test BackupManager initialization creates backup directory."""
    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    assert bm.backup_dir == backup_dir
    assert backup_dir.exists()
    assert backup_dir.is_dir()
    # Check restrictive permissions (700)
    assert oct(backup_dir.stat().st_mode)[-3:] == "700"


def test_create_backup_success(tmp_path: Path) -> None:
    """Test successful backup creation."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("version: 1.0\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create backup
    backup_path = bm.create_backup(test_file)

    # Verify
    assert backup_path.exists()
    assert backup_path.parent == backup_dir
    assert backup_path.name.startswith("test_")
    assert backup_path.suffix == ".yml"
    assert backup_path.read_text(encoding="utf-8") == "version: 1.0\n"

    # Check restrictive permissions (600)
    assert oct(backup_path.stat().st_mode)[-3:] == "600"


def test_create_backup_timestamp_format(tmp_path: Path) -> None:
    """Test backup filename has correct timestamp format."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create backup
    backup_path = bm.create_backup(test_file)

    # Verify format: test_YYYYMMDD_HHMMSS_microseconds.yml
    import re

    pattern = r"test_\d{8}_\d{6}_\d{6}\.yml"
    assert re.match(pattern, backup_path.name)


def test_create_backup_nonexistent_file(tmp_path: Path) -> None:
    """Test backup creation fails for non-existent file."""
    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    nonexistent = tmp_path / "nonexistent.yml"

    with pytest.raises(ValidationError) as exc_info:
        bm.create_backup(nonexistent)

    assert "Cannot backup non-existent file" in str(exc_info.value)
    assert "Suggestion" in str(exc_info.value)
    assert "clauxton init" in str(exc_info.value)


def test_list_backups_empty(tmp_path: Path) -> None:
    """Test listing backups when none exist."""
    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    test_file = tmp_path / "test.yml"
    backups = bm.list_backups(test_file)

    assert backups == []


def test_list_backups_sorted(tmp_path: Path) -> None:
    """Test backups are sorted by timestamp (newest first)."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create 3 backups with small delays
    backup1 = bm.create_backup(test_file)
    time.sleep(0.01)  # Ensure different timestamps
    backup2 = bm.create_backup(test_file)
    time.sleep(0.01)
    backup3 = bm.create_backup(test_file)

    # List backups
    backups = bm.list_backups(test_file)

    # Verify sorted newest first
    assert len(backups) == 3
    assert backups[0] == backup3  # Newest
    assert backups[1] == backup2
    assert backups[2] == backup1  # Oldest


def test_cleanup_old_backups_no_deletion(tmp_path: Path) -> None:
    """Test cleanup when backups are within limit."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create 3 backups (within 10 limit)
    for _ in range(3):
        bm.create_backup(test_file)
        time.sleep(0.01)

    # Cleanup with limit of 10
    deleted = bm.cleanup_old_backups(test_file, max_generations=10)

    # Verify nothing deleted
    assert deleted == []
    assert len(bm.list_backups(test_file)) == 3


def test_cleanup_old_backups_deletion(tmp_path: Path) -> None:
    """Test cleanup deletes old backups beyond limit."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create 12 backups
    backups = []
    for _ in range(12):
        backup = bm.create_backup(test_file, max_generations=100)  # Don't cleanup yet
        backups.append(backup)
        time.sleep(0.01)

    # Cleanup with limit of 5
    deleted = bm.cleanup_old_backups(test_file, max_generations=5)

    # Verify 7 deleted (12 - 5 = 7)
    assert len(deleted) == 7
    remaining = bm.list_backups(test_file)
    assert len(remaining) == 5

    # Verify oldest ones were deleted (backups[0] through backups[6])
    for i in range(7):
        assert not backups[i].exists()

    # Verify newest ones remain (backups[7] through backups[11])
    for i in range(7, 12):
        assert backups[i].exists()


def test_create_backup_with_auto_cleanup(tmp_path: Path) -> None:
    """Test create_backup automatically cleans up old backups."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create 12 backups with max_generations=10
    for i in range(12):
        test_file.write_text(f"version: {i}\n", encoding="utf-8")
        bm.create_backup(test_file, max_generations=10)
        time.sleep(0.01)

    # Verify only 10 backups remain
    backups = bm.list_backups(test_file)
    assert len(backups) == 10


def test_restore_backup_success(tmp_path: Path) -> None:
    """Test successful backup restoration."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("original data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create backup
    backup_path = bm.create_backup(test_file)

    # Modify original
    test_file.write_text("modified data\n", encoding="utf-8")
    assert test_file.read_text() == "modified data\n"

    # Restore
    target_path = tmp_path / "restored.yml"
    bm.restore_backup(backup_path, target_path)

    # Verify
    assert target_path.exists()
    assert target_path.read_text(encoding="utf-8") == "original data\n"
    # Check restrictive permissions (600)
    assert oct(target_path.stat().st_mode)[-3:] == "600"


def test_restore_backup_nonexistent(tmp_path: Path) -> None:
    """Test restore fails for non-existent backup."""
    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    nonexistent = backup_dir / "nonexistent_20251021_120000.yml"
    target_path = tmp_path / "target.yml"

    with pytest.raises(ValidationError) as exc_info:
        bm.restore_backup(nonexistent, target_path)

    assert "Backup file not found" in str(exc_info.value)
    assert "Suggestion" in str(exc_info.value)
    assert "List backups" in str(exc_info.value)


def test_get_latest_backup(tmp_path: Path) -> None:
    """Test getting the most recent backup."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create 3 backups
    bm.create_backup(test_file)
    time.sleep(0.01)
    bm.create_backup(test_file)
    time.sleep(0.01)
    latest = bm.create_backup(test_file)

    # Get latest
    result = bm.get_latest_backup(test_file)

    # Verify
    assert result == latest


def test_get_latest_backup_none(tmp_path: Path) -> None:
    """Test get_latest_backup returns None when no backups exist."""
    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    test_file = tmp_path / "test.yml"

    result = bm.get_latest_backup(test_file)

    assert result is None


def test_count_backups(tmp_path: Path) -> None:
    """Test counting backups."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # No backups initially
    assert bm.count_backups(test_file) == 0

    # Create 5 backups
    for _ in range(5):
        bm.create_backup(test_file)
        time.sleep(0.01)

    # Count
    assert bm.count_backups(test_file) == 5


def test_backups_isolated_by_filename(tmp_path: Path) -> None:
    """Test backups are isolated by original filename."""
    # Setup
    file1 = tmp_path / "tasks.yml"
    file2 = tmp_path / "knowledge-base.yml"
    file1.write_text("tasks\n", encoding="utf-8")
    file2.write_text("kb\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create backups for both files
    bm.create_backup(file1)
    bm.create_backup(file1)
    bm.create_backup(file2)

    # Verify isolated
    assert bm.count_backups(file1) == 2
    assert bm.count_backups(file2) == 1


def test_backup_preserves_content(tmp_path: Path) -> None:
    """Test backup preserves exact file content including Unicode."""
    # Setup with Unicode content
    test_file = tmp_path / "test.yml"
    content = "version: 1.0\ntitle: 日本語タイトル\ncontent: 你好世界\n"
    test_file.write_text(content, encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create backup
    backup_path = bm.create_backup(test_file)

    # Verify content preserved
    backup_content = backup_path.read_text(encoding="utf-8")
    assert backup_content == content


def test_create_backup_readonly_directory(tmp_path: Path) -> None:
    """Test backup creation fails gracefully with read-only directory."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir(mode=0o700)
    bm = BackupManager(backup_dir)

    # Make backup directory read-only
    backup_dir.chmod(0o500)

    try:
        # Try to create backup
        with pytest.raises(ValidationError) as exc_info:
            bm.create_backup(test_file)

        assert "Failed to create backup" in str(exc_info.value)
        assert "Suggestion" in str(exc_info.value)
    finally:
        # Restore permissions for cleanup
        backup_dir.chmod(0o700)


def test_restore_backup_readonly_target(tmp_path: Path) -> None:
    """Test restore fails gracefully when target directory is read-only."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create backup
    backup_path = bm.create_backup(test_file)

    # Create read-only target directory
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir(mode=0o700)
    readonly_dir.chmod(0o500)

    try:
        target_path = readonly_dir / "restored.yml"

        # Try to restore
        with pytest.raises(ValidationError) as exc_info:
            bm.restore_backup(backup_path, target_path)

        assert "Failed to restore backup" in str(exc_info.value)
        assert "Suggestion" in str(exc_info.value)
    finally:
        # Restore permissions for cleanup
        readonly_dir.chmod(0o700)


def test_concurrent_backup_operations(tmp_path: Path) -> None:
    """Test concurrent backup creation maintains data integrity."""
    import threading

    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create backups concurrently
    errors = []

    def create_backup_thread() -> None:
        try:
            bm.create_backup(test_file)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=create_backup_thread) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify all backups created successfully
    assert len(errors) == 0
    backups = bm.list_backups(test_file)
    assert len(backups) == 10

    # Verify all backups have unique names (microsecond precision)
    backup_names = [b.name for b in backups]
    assert len(backup_names) == len(set(backup_names))


def test_cleanup_handles_missing_backups(tmp_path: Path) -> None:
    """Test cleanup handles gracefully when backups are deleted externally."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("data\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create 5 backups
    backups = []
    for _ in range(5):
        backup = bm.create_backup(test_file, max_generations=100)
        backups.append(backup)
        time.sleep(0.01)

    # Manually delete one backup (simulating external deletion)
    backups[2].unlink()

    # Cleanup should handle missing file gracefully
    bm.cleanup_old_backups(test_file, max_generations=3)

    # Verify cleanup proceeded despite missing file
    remaining = bm.list_backups(test_file)
    assert len(remaining) <= 3


def test_backup_rotation_maintains_newest(tmp_path: Path) -> None:
    """Test backup rotation keeps newest backups and deletes oldest."""
    # Setup
    test_file = tmp_path / "test.yml"
    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create 15 backups with identifiable content
    backup_contents = []
    for i in range(15):
        content = f"version: {i}\n"
        test_file.write_text(content, encoding="utf-8")
        bm.create_backup(test_file, max_generations=5)
        backup_contents.append(content)
        time.sleep(0.01)

    # Verify only 5 newest remain
    backups = bm.list_backups(test_file)
    assert len(backups) == 5

    # Verify they contain the latest content (versions 10-14)
    contents = [b.read_text(encoding="utf-8") for b in backups]
    for i in range(10, 15):
        assert f"version: {i}\n" in contents


def test_restore_backup_overwrites_existing(tmp_path: Path) -> None:
    """Test restore overwrites existing target file."""
    # Setup
    test_file = tmp_path / "test.yml"
    test_file.write_text("original\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create backup
    backup_path = bm.create_backup(test_file)

    # Create target with different content
    target_path = tmp_path / "target.yml"
    target_path.write_text("existing content\n", encoding="utf-8")

    # Restore (should overwrite)
    bm.restore_backup(backup_path, target_path)

    # Verify overwritten
    assert target_path.read_text(encoding="utf-8") == "original\n"


def test_list_backups_filters_by_filename(tmp_path: Path) -> None:
    """Test list_backups only returns backups for the specified file."""
    # Setup multiple files
    file1 = tmp_path / "tasks.yml"
    file2 = tmp_path / "knowledge-base.yml"
    file3 = tmp_path / "tasks-backup.yml"  # Similar name but different
    file1.write_text("tasks\n", encoding="utf-8")
    file2.write_text("kb\n", encoding="utf-8")
    file3.write_text("tasks-backup\n", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    bm = BackupManager(backup_dir)

    # Create backups
    bm.create_backup(file1)
    bm.create_backup(file1)
    bm.create_backup(file2)
    bm.create_backup(file3)

    # Verify filtering
    tasks_backups = bm.list_backups(file1)
    kb_backups = bm.list_backups(file2)
    tasks_backup_backups = bm.list_backups(file3)

    assert len(tasks_backups) == 2
    assert len(kb_backups) == 1
    assert len(tasks_backup_backups) == 1

    # Verify no cross-contamination
    assert all("tasks_" in b.name for b in tasks_backups)
    assert all("knowledge-base_" in b.name for b in kb_backups)
    assert all("tasks-backup_" in b.name for b in tasks_backup_backups)
