"""
Pydantic data models for Clauxton.

This module defines all core data structures using Pydantic v2 for:
- Type safety and validation
- JSON serialization/deserialization
- AI-friendly, declarative code
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# Custom Exceptions
# ============================================================================


class ClauxtonError(Exception):
    """Base exception for all Clauxton errors."""

    pass


class ValidationError(ClauxtonError):
    """Raised when data validation fails."""

    pass


class NotFoundError(ClauxtonError):
    """Raised when an entity (KB entry, task, etc.) is not found."""

    pass


class DuplicateError(ClauxtonError):
    """Raised when attempting to create a duplicate entity."""

    pass


class CycleDetectedError(ClauxtonError):
    """Raised when a circular dependency is detected in task graph."""

    pass


# ============================================================================
# Knowledge Base Models
# ============================================================================


class KnowledgeBaseEntry(BaseModel):
    """
    A single entry in the Knowledge Base.

    Knowledge Base entries capture persistent project context such as:
    - Architecture decisions (e.g., "We use FastAPI for all APIs")
    - Constraints (e.g., "Must support Python 3.11+")
    - Decisions (e.g., "Use PostgreSQL for production")
    - Patterns (e.g., "Repository pattern for data access")
    - Conventions (e.g., "Use Google-style docstrings")

    Attributes:
        id: Unique identifier (format: KB-YYYYMMDD-NNN)
        title: Short, descriptive title (max 50 chars)
        category: Type of knowledge (architecture, constraint, decision, pattern, convention)
        content: Detailed description (max 10,000 chars)
        tags: Optional tags for categorization
        created_at: Timestamp when entry was created
        updated_at: Timestamp when entry was last updated
        author: Optional author name (defaults to None for privacy)
        version: Entry version number (incremented on updates)

    Example:
        >>> entry = KnowledgeBaseEntry(
        ...     id="KB-20251019-001",
        ...     title="API uses FastAPI",
        ...     category="architecture",
        ...     content="All backend APIs use FastAPI framework with async endpoints.",
        ...     tags=["backend", "api"],
        ...     created_at=datetime.now(),
        ...     updated_at=datetime.now()
        ... )
        >>> entry.title
        'API uses FastAPI'
    """

    id: str = Field(
        ...,
        pattern=r"^KB-\d{8}-\d{3}$",
        description="Unique ID (format: KB-YYYYMMDD-NNN)",
    )
    title: str = Field(
        ..., min_length=1, max_length=50, description="Short entry title"
    )
    category: Literal[
        "architecture", "constraint", "decision", "pattern", "convention"
    ] = Field(..., description="Knowledge category")
    content: str = Field(
        ..., min_length=1, max_length=10000, description="Entry content"
    )
    tags: List[str] = Field(
        default_factory=list, description="Tags for categorization"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    author: Optional[str] = Field(None, description="Author name (optional)")
    version: int = Field(default=1, ge=1, description="Entry version number")

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Remove leading/trailing whitespace from content."""
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Content cannot be empty or only whitespace")
        return sanitized

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Remove leading/trailing whitespace from title."""
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Title cannot be empty or only whitespace")
        return sanitized

    @field_validator("tags")
    @classmethod
    def sanitize_tags(cls, v: List[str]) -> List[str]:
        """Remove empty tags and duplicates."""
        cleaned = [tag.strip().lower() for tag in v if tag.strip()]
        return list(dict.fromkeys(cleaned))  # Remove duplicates, preserve order


class KnowledgeBaseConfig(BaseModel):
    """
    Configuration for Knowledge Base.

    Stored at the top of knowledge-base.yml file.

    Attributes:
        version: KB schema version (for future migrations)
        project_name: Name of the project
        project_description: Optional project description

    Example:
        >>> config = KnowledgeBaseConfig(
        ...     version="1.0",
        ...     project_name="my-project",
        ...     project_description="E-commerce platform"
        ... )
        >>> config.project_name
        'my-project'
    """

    version: str = Field(default="1.0", description="KB schema version")
    project_name: str = Field(..., description="Project name")
    project_description: Optional[str] = Field(
        None, description="Project description"
    )


# ============================================================================
# Task Models (for Phase 1, defined here for forward compatibility)
# ============================================================================


class Task(BaseModel):
    """
    A single task in the task management system.

    Tasks represent units of work with dependencies forming a DAG.
    This model is defined in Phase 0 for forward compatibility but
    will be fully implemented in Phase 1.

    Attributes:
        id: Unique identifier (format: TASK-NNN)
        name: Short task name
        description: Detailed description
        status: Current status (pending, in_progress, completed, blocked)
        priority: Task priority level
        depends_on: List of task IDs this task depends on
        files_to_edit: List of files this task will modify
        related_kb: List of related KB entry IDs
        estimated_hours: Estimated time to complete
        actual_hours: Actual time spent
        created_at: Creation timestamp
        started_at: When task was started
        completed_at: When task was completed

    Example:
        >>> task = Task(
        ...     id="TASK-001",
        ...     name="Setup database",
        ...     description="Create PostgreSQL schema",
        ...     status="pending",
        ...     priority="high",
        ...     created_at=datetime.now()
        ... )
        >>> task.status
        'pending'
    """

    id: str = Field(..., pattern=r"^TASK-\d{3}$", description="Unique task ID")
    name: str = Field(..., min_length=1, max_length=100, description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    status: Literal["pending", "in_progress", "completed", "blocked"] = Field(
        default="pending", description="Task status"
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        default="medium", description="Task priority"
    )
    depends_on: List[str] = Field(
        default_factory=list, description="Task IDs this task depends on"
    )
    files_to_edit: List[str] = Field(
        default_factory=list, description="Files this task will modify"
    )
    related_kb: List[str] = Field(
        default_factory=list, description="Related KB entry IDs"
    )
    estimated_hours: Optional[float] = Field(
        None, ge=0, description="Estimated hours to complete"
    )
    actual_hours: Optional[float] = Field(
        None, ge=0, description="Actual hours spent"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


# ============================================================================
# Helper Types
# ============================================================================


CategoryType = Literal["architecture", "constraint", "decision", "pattern", "convention"]
TaskStatusType = Literal["pending", "in_progress", "completed", "blocked"]
TaskPriorityType = Literal["low", "medium", "high", "critical"]
