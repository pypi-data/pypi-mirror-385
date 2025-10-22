"""
Tests for Pydantic data models.

Tests cover:
- Valid model creation
- Validation errors for invalid data
- Field sanitization (whitespace, duplicates)
- JSON serialization/deserialization
"""

from datetime import datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from clauxton.core.models import (
    KnowledgeBaseConfig,
    KnowledgeBaseEntry,
    Task,
)

# ============================================================================
# KnowledgeBaseEntry Tests
# ============================================================================


def test_kb_entry_valid_creation():
    """Test creating a valid KB entry."""
    entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="API uses FastAPI",
        category="architecture",
        content="All backend APIs use FastAPI framework.",
        tags=["backend", "api"],
        created_at=datetime(2025, 10, 19, 10, 30, 0),
        updated_at=datetime(2025, 10, 19, 10, 30, 0),
    )

    assert entry.id == "KB-20251019-001"
    assert entry.title == "API uses FastAPI"
    assert entry.category == "architecture"
    assert entry.content == "All backend APIs use FastAPI framework."
    assert entry.tags == ["backend", "api"]
    assert entry.version == 1
    assert entry.author is None


def test_kb_entry_invalid_id_format():
    """Test that invalid ID format raises validation error."""
    with pytest.raises(PydanticValidationError) as exc_info:
        KnowledgeBaseEntry(
            id="INVALID-ID",  # Invalid format
            title="Test",
            category="architecture",
            content="Test content",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    assert "id" in str(exc_info.value)


def test_kb_entry_title_too_long():
    """Test that title exceeding max length raises validation error."""
    with pytest.raises(PydanticValidationError) as exc_info:
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="A" * 51,  # Max is 50
            category="architecture",
            content="Test content",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    assert "title" in str(exc_info.value)


def test_kb_entry_title_boundary_values():
    """Test title length boundary values (49, 50, 51 characters)."""
    # 49 characters - should pass
    entry_49 = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="A" * 49,
        category="architecture",
        content="Test content",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert len(entry_49.title) == 49

    # 50 characters - should pass (exactly at limit)
    entry_50 = KnowledgeBaseEntry(
        id="KB-20251019-002",
        title="B" * 50,
        category="architecture",
        content="Test content",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert len(entry_50.title) == 50

    # 51 characters - should fail
    with pytest.raises(PydanticValidationError):
        KnowledgeBaseEntry(
            id="KB-20251019-003",
            title="C" * 51,
            category="architecture",
            content="Test content",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


def test_kb_entry_content_boundary_values():
    """Test content length boundary values (9999, 10000, 10001 characters)."""
    # 9999 characters - should pass
    entry_9999 = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Test",
        category="architecture",
        content="A" * 9999,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert len(entry_9999.content) == 9999

    # 10000 characters - should pass (exactly at limit)
    entry_10000 = KnowledgeBaseEntry(
        id="KB-20251019-002",
        title="Test",
        category="architecture",
        content="B" * 10000,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert len(entry_10000.content) == 10000

    # 10001 characters - should fail
    with pytest.raises(PydanticValidationError):
        KnowledgeBaseEntry(
            id="KB-20251019-003",
            title="Test",
            category="architecture",
            content="C" * 10001,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


def test_kb_entry_invalid_category():
    """Test that invalid category raises validation error."""
    with pytest.raises(PydanticValidationError) as exc_info:
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="Test",
            category="invalid_category",  # Not in allowed list
            content="Test content",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    assert "category" in str(exc_info.value)


def test_kb_entry_content_sanitization():
    """Test that content whitespace is trimmed."""
    entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Test",
        category="architecture",
        content="   Test content with whitespace   ",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    assert entry.content == "Test content with whitespace"


def test_kb_entry_empty_content():
    """Test that empty content raises validation error."""
    with pytest.raises(ValueError) as exc_info:
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="Test",
            category="architecture",
            content="   ",  # Only whitespace
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    assert "Content cannot be empty" in str(exc_info.value)


def test_kb_entry_title_sanitization():
    """Test that title whitespace is trimmed."""
    entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="   Test Title   ",
        category="architecture",
        content="Test content",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    assert entry.title == "Test Title"


def test_kb_entry_tags_sanitization():
    """Test that tags are cleaned (lowercased, duplicates removed)."""
    entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Test",
        category="architecture",
        content="Test content",
        tags=["Backend", "API", "backend", "  api  ", ""],  # Duplicates and empty
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Should be lowercased, duplicates removed, empty removed, order preserved
    assert entry.tags == ["backend", "api"]


def test_kb_entry_default_values():
    """Test that default values are set correctly."""
    entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Test",
        category="architecture",
        content="Test content",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    assert entry.tags == []
    assert entry.version == 1
    assert entry.author is None


def test_kb_entry_json_serialization():
    """Test JSON serialization and deserialization."""
    original = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Test",
        category="architecture",
        content="Test content",
        tags=["test"],
        created_at=datetime(2025, 10, 19, 10, 30, 0),
        updated_at=datetime(2025, 10, 19, 10, 30, 0),
    )

    # Serialize to JSON
    json_data = original.model_dump_json()

    # Deserialize from JSON
    restored = KnowledgeBaseEntry.model_validate_json(json_data)

    assert restored.id == original.id
    assert restored.title == original.title
    assert restored.category == original.category
    assert restored.content == original.content
    assert restored.tags == original.tags


def test_kb_entry_id_format_variations():
    """Test various ID format edge cases."""
    # Valid formats
    valid_ids = [
        "KB-20251019-001",
        "KB-20251019-999",
        "KB-19991231-000",
        "KB-20300101-123",
    ]

    for valid_id in valid_ids:
        entry = KnowledgeBaseEntry(
            id=valid_id,
            title="Test",
            category="architecture",
            content="Test content",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert entry.id == valid_id

    # Invalid formats
    invalid_ids = [
        "KB-2025101-001",  # 7 digits instead of 8
        "KB-202510199-001",  # 9 digits instead of 8
        "KB-20251019-01",  # 2 digits instead of 3
        "KB-20251019-1234",  # 4 digits instead of 3
        "kb-20251019-001",  # lowercase
        "KB20251019-001",  # missing hyphen
        "KB-20251019001",  # missing hyphen
    ]

    for invalid_id in invalid_ids:
        with pytest.raises(PydanticValidationError):
            KnowledgeBaseEntry(
                id=invalid_id,
                title="Test",
                category="architecture",
                content="Test content",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )


def test_kb_entry_type_coercion():
    """Test that Pydantic correctly handles type coercion and rejects invalid types."""
    # Version should be coerced to int if passed as string
    entry = KnowledgeBaseEntry(
        id="KB-20251019-001",
        title="Test",
        category="architecture",
        content="Test content",
        version="2",  # String that can be coerced to int
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert entry.version == 2
    assert isinstance(entry.version, int)

    # Tags should reject non-list types
    with pytest.raises(PydanticValidationError):
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="Test",
            category="architecture",
            content="Test content",
            tags="not-a-list",  # Should be a list
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


# ============================================================================
# KnowledgeBaseConfig Tests
# ============================================================================


def test_kb_config_valid_creation():
    """Test creating a valid KB config."""
    config = KnowledgeBaseConfig(
        version="1.0",
        project_name="test-project",
        project_description="A test project",
    )

    assert config.version == "1.0"
    assert config.project_name == "test-project"
    assert config.project_description == "A test project"


def test_kb_config_default_version():
    """Test that version defaults to '1.0'."""
    config = KnowledgeBaseConfig(project_name="test-project")

    assert config.version == "1.0"
    assert config.project_description is None


# ============================================================================
# Task Tests (Phase 1, basic validation only)
# ============================================================================


def test_task_valid_creation():
    """Test creating a valid task."""
    task = Task(
        id="TASK-001",
        name="Setup database",
        description="Create PostgreSQL schema",
        status="pending",
        priority="high",
        created_at=datetime(2025, 10, 19, 9, 0, 0),
    )

    assert task.id == "TASK-001"
    assert task.name == "Setup database"
    assert task.status == "pending"
    assert task.priority == "high"
    assert task.depends_on == []
    assert task.files_to_edit == []
    assert task.related_kb == []


def test_task_invalid_id_format():
    """Test that invalid task ID format raises validation error."""
    with pytest.raises(PydanticValidationError) as exc_info:
        Task(
            id="INVALID",  # Invalid format
            name="Test",
            created_at=datetime.now(),
        )

    assert "id" in str(exc_info.value)


def test_task_invalid_status():
    """Test that invalid status raises validation error."""
    with pytest.raises(PydanticValidationError) as exc_info:
        Task(
            id="TASK-001",
            name="Test",
            status="invalid_status",  # Not in allowed list
            created_at=datetime.now(),
        )

    assert "status" in str(exc_info.value)


def test_task_default_values():
    """Test that default values are set correctly."""
    task = Task(
        id="TASK-001",
        name="Test",
        created_at=datetime.now(),
    )

    assert task.status == "pending"
    assert task.priority == "medium"
    assert task.depends_on == []
    assert task.files_to_edit == []
    assert task.related_kb == []
    assert task.estimated_hours is None
    assert task.actual_hours is None
    assert task.started_at is None
    assert task.completed_at is None
