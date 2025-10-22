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
    """
    Base exception for all Clauxton errors.

    All Clauxton exceptions inherit from this class for easy catching.
    """

    pass


class ValidationError(ClauxtonError):
    """
    Raised when data validation fails.

    This includes:
    - Invalid KB entry or task data
    - Malformed YAML files
    - Schema validation failures
    - Field constraint violations

    Example:
        >>> raise ValidationError(
        ...     "Task name cannot be empty.\\n\\n"
        ...     "Suggestion: Provide a descriptive task name.\\n"
        ...     "  Example: --name 'Setup database schema'"
        ... )
    """

    pass


class NotFoundError(ClauxtonError):
    """
    Raised when an entity (KB entry, task, etc.) is not found.

    Best Practice: Include suggestion with available IDs or how to list them.

    Example:
        >>> available_ids = ["TASK-001", "TASK-002"]
        >>> raise NotFoundError(
        ...     "Task with ID 'TASK-999' not found.\\n\\n"
        ...     "Suggestion: Check if the task ID is correct.\\n"
        ...     f"  Available task IDs: {', '.join(available_ids)}\\n"
        ...     "  List all tasks: clauxton task list"
        ... )
    """

    pass


class DuplicateError(ClauxtonError):
    """
    Raised when attempting to create a duplicate entity.

    Best Practice: Include suggestion to update existing entity or use different ID.

    Example:
        >>> raise DuplicateError(
        ...     "Task with ID 'TASK-001' already exists.\\n\\n"
        ...     "Suggestion: Use a different task ID or update existing task.\\n"
        ...     "  Update existing: clauxton task update TASK-001 --name 'New name'\\n"
        ...     "  View existing: clauxton task get TASK-001"
        ... )
    """

    pass


class CycleDetectedError(ClauxtonError):
    """
    Raised when a circular dependency is detected in task graph.

    Best Practice: Include the cycle path and suggestion to break it.

    Example:
        >>> raise CycleDetectedError(
        ...     "Circular dependency detected: TASK-001 → TASK-002 → TASK-001\\n\\n"
        ...     "Suggestion: Remove one of the dependencies to break the cycle.\\n"
        ...     "  - Remove dependency: clauxton task update TASK-002 --remove-dep TASK-001\\n"
        ...     "  - View dependencies: clauxton task get TASK-001"
        ... )
    """

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
# Conflict Detection Models (Phase 2)
# ============================================================================


class ConflictReport(BaseModel):
    """
    Report of a detected conflict between tasks.

    Conflicts occur when multiple tasks attempt to modify the same files,
    creating potential merge conflicts or coordination issues.

    Attributes:
        task_a_id: ID of first task involved in conflict
        task_b_id: ID of second task involved in conflict
        conflict_type: Type of conflict (file_overlap, dependency_violation)
        risk_level: Risk severity (low, medium, high)
        risk_score: Numerical risk score (0.0-1.0)
        overlapping_files: Files modified by both tasks
        details: Human-readable conflict description
        recommendation: Suggested action to resolve conflict

    Example:
        >>> conflict = ConflictReport(
        ...     task_a_id="TASK-001",
        ...     task_b_id="TASK-003",
        ...     conflict_type="file_overlap",
        ...     risk_level="high",
        ...     risk_score=0.85,
        ...     overlapping_files=["src/api/auth.py"],
        ...     details="Both tasks edit src/api/auth.py",
        ...     recommendation="Complete TASK-001 before starting TASK-003"
        ... )
        >>> conflict.risk_level
        'high'
    """

    task_a_id: str = Field(
        ..., pattern=r"^TASK-\d{3}$", description="First task ID"
    )
    task_b_id: str = Field(
        ..., pattern=r"^TASK-\d{3}$", description="Second task ID"
    )
    conflict_type: Literal["file_overlap", "dependency_violation"] = Field(
        ..., description="Type of conflict"
    )
    risk_level: Literal["low", "medium", "high"] = Field(
        ..., description="Risk severity level"
    )
    risk_score: float = Field(
        ..., ge=0.0, le=1.0, description="Numerical risk score (0.0-1.0)"
    )
    overlapping_files: List[str] = Field(
        default_factory=list, description="Files modified by both tasks"
    )
    details: str = Field(..., min_length=1, description="Conflict description")
    recommendation: str = Field(
        ..., min_length=1, description="Suggested resolution"
    )


# ============================================================================
# Helper Types
# ============================================================================


CategoryType = Literal["architecture", "constraint", "decision", "pattern", "convention"]
TaskStatusType = Literal["pending", "in_progress", "completed", "blocked"]
TaskPriorityType = Literal["low", "medium", "high", "critical"]
ConflictTypeType = Literal["file_overlap", "dependency_violation"]
RiskLevelType = Literal["low", "medium", "high"]
