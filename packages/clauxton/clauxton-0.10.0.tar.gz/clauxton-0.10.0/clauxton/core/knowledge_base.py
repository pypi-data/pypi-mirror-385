"""
Knowledge Base manager for persistent project context.

This module provides:
- CRUD operations for Knowledge Base entries
- Keyword-based search with category/tag filtering
- YAML persistence with atomic writes
- Automatic ID generation
- Caching for performance

Example:
    >>> from pathlib import Path
    >>> kb = KnowledgeBase(Path("."))
    >>> entry_id = kb.add(KnowledgeBaseEntry(...))
    >>> results = kb.search("architecture", category="decision")
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from clauxton.core.models import (
    DuplicateError,
    KnowledgeBaseEntry,
    NotFoundError,
)
from clauxton.utils.file_utils import ensure_clauxton_dir, set_secure_permissions
from clauxton.utils.yaml_utils import read_yaml, validate_kb_yaml, write_yaml

# Optional TF-IDF search (falls back to simple search if scikit-learn not available)
try:
    from clauxton.core.search import SearchEngine
    SEARCH_ENGINE_AVAILABLE = True
except ImportError:
    SEARCH_ENGINE_AVAILABLE = False
    SearchEngine = None  # type: ignore


class KnowledgeBase:
    """
    Knowledge Base manager.

    Handles CRUD operations for project-specific context.
    Uses YAML for human-readable storage with atomic writes.

    Attributes:
        root_dir: Project root directory
        kb_file: Path to knowledge-base.yml file
        _entries_cache: Optional cache of loaded entries

    Example:
        >>> kb = KnowledgeBase(Path("/path/to/project"))
        >>> entry = KnowledgeBaseEntry(...)
        >>> entry_id = kb.add(entry)
        >>> print(entry_id)
        KB-20251019-001
    """

    def __init__(self, root_dir: Path) -> None:
        """
        Initialize Knowledge Base at root_dir.

        Args:
            root_dir: Project root directory

        Example:
            >>> kb = KnowledgeBase(Path("."))
        """
        self.root_dir: Path = root_dir
        clauxton_dir = ensure_clauxton_dir(root_dir)
        self.kb_file: Path = clauxton_dir / "knowledge-base.yml"
        self._entries_cache: Optional[List[KnowledgeBaseEntry]] = None
        self._search_engine: Optional[Any] = None  # SearchEngine instance
        self._ensure_kb_exists()
        self._rebuild_search_index()

    def add(self, entry: KnowledgeBaseEntry) -> str:
        """
        Add new entry to Knowledge Base.

        Args:
            entry: KnowledgeBaseEntry to add

        Returns:
            Entry ID

        Raises:
            DuplicateError: If entry ID already exists

        Example:
            >>> entry = KnowledgeBaseEntry(
            ...     id="KB-20251019-001",
            ...     title="Use FastAPI",
            ...     category="architecture",
            ...     content="All APIs use FastAPI framework",
            ...     created_at=datetime.now(),
            ...     updated_at=datetime.now()
            ... )
            >>> kb.add(entry)
            'KB-20251019-001'
        """
        entries = self._load_entries()

        # Check for duplicate ID
        if any(e.id == entry.id for e in entries):
            raise DuplicateError(
                f"Entry with ID '{entry.id}' already exists. "
                "Use update() to modify existing entries."
            )

        # Add entry
        entries.append(entry)
        self._save_entries(entries)
        self._rebuild_search_index()  # Rebuild before invalidating cache
        self._invalidate_cache()

        return entry.id

    def get(self, entry_id: str) -> KnowledgeBaseEntry:
        """
        Get entry by ID.

        Args:
            entry_id: Entry ID to retrieve

        Returns:
            KnowledgeBaseEntry

        Raises:
            NotFoundError: If entry not found

        Example:
            >>> entry = kb.get("KB-20251019-001")
            >>> print(entry.title)
            Use FastAPI
        """
        entries = self._load_entries()

        for entry in entries:
            if entry.id == entry_id:
                return entry

        raise NotFoundError(
            f"Entry with ID '{entry_id}' not found in Knowledge Base. "
            f"Use list_all() to see available entries."
        )

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[KnowledgeBaseEntry]:
        """
        Search Knowledge Base with TF-IDF relevance ranking.

        Uses TF-IDF algorithm for relevance-based search if scikit-learn is available.
        Falls back to simple keyword matching if not.

        Args:
            query: Search query (keywords)
            category: Optional category filter
            tags: Optional tag filter (matches any tag)
            limit: Maximum results to return

        Returns:
            List of matching entries, sorted by relevance

        Example:
            >>> results = kb.search("api", category="architecture")
            >>> for entry in results:
            ...     print(entry.title)
            Use FastAPI
            API versioning strategy
        """
        # Use TF-IDF search if available
        if SEARCH_ENGINE_AVAILABLE and self._search_engine is not None:
            results = self._search_engine.search(query, category=category, limit=limit)
            entries_with_scores = results

            # Apply tag filter if specified
            if tags:
                filtered = []
                for entry, score in entries_with_scores:
                    if any(tag in entry.tags for tag in tags):
                        filtered.append((entry, score))
                entries_with_scores = filtered

            return [entry for entry, _ in entries_with_scores[:limit]]

        # Fallback to simple keyword search
        return self._simple_search(query, category, tags, limit)

    def _simple_search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[KnowledgeBaseEntry]:
        """
        Simple keyword-based search (fallback when TF-IDF unavailable).

        Args:
            query: Search query
            category: Optional category filter
            tags: Optional tag filter
            limit: Maximum results

        Returns:
            List of matching entries
        """
        entries = self._load_entries()
        query_lower = query.lower().strip()

        # If query is empty after stripping, return empty results
        if not query_lower:
            return []

        matches: List[tuple[KnowledgeBaseEntry, float]] = []

        for entry in entries:
            # Skip if category filter doesn't match
            if category and entry.category != category:
                continue

            # Skip if tag filter doesn't match
            if tags and not any(tag in entry.tags for tag in tags):
                continue

            # Calculate relevance score
            score = 0.0

            # Title matches (weight: 2.0)
            if query_lower in entry.title.lower():
                score += 2.0

            # Content matches (weight: 1.0)
            if query_lower in entry.content.lower():
                score += 1.0

            # Tag matches (weight: 1.5)
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 1.5
                    break

            # Only include if there's a match
            if score > 0:
                matches.append((entry, score))

        # Sort by relevance (descending) and limit results
        matches.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in matches[:limit]]

    def update(self, entry_id: str, updates: Dict[str, Any]) -> KnowledgeBaseEntry:
        """
        Update entry. Creates new version.

        Args:
            entry_id: Entry ID to update
            updates: Dictionary of fields to update

        Returns:
            Updated KnowledgeBaseEntry

        Raises:
            NotFoundError: If entry not found

        Example:
            >>> updated = kb.update("KB-20251019-001", {
            ...     "content": "Updated content",
            ...     "tags": ["api", "fastapi", "updated"]
            ... })
            >>> print(updated.version)
            2
        """
        entries = self._load_entries()
        entry_index = None

        # Find entry
        for i, entry in enumerate(entries):
            if entry.id == entry_id:
                entry_index = i
                break

        if entry_index is None:
            raise NotFoundError(f"Entry with ID '{entry_id}' not found.")

        # Get current entry and create updated version
        current_entry = entries[entry_index]
        entry_dict = current_entry.model_dump()

        # Apply updates
        for key, value in updates.items():
            if key in entry_dict and key not in ["id", "created_at", "version"]:
                entry_dict[key] = value

        # Increment version and update timestamp
        entry_dict["version"] = current_entry.version + 1
        entry_dict["updated_at"] = datetime.now()

        # Create updated entry
        updated_entry = KnowledgeBaseEntry(**entry_dict)

        # Replace in list
        entries[entry_index] = updated_entry
        self._save_entries(entries)
        self._rebuild_search_index()  # Rebuild before invalidating cache
        self._invalidate_cache()

        return updated_entry

    def delete(self, entry_id: str, reason: Optional[str] = None) -> None:
        """
        Delete entry (hard delete).

        Note: This is a hard delete. Consider implementing soft delete
        with a 'deleted' flag in Phase 1 for better data preservation.

        Args:
            entry_id: Entry ID to delete
            reason: Optional reason for deletion (for audit log in Phase 2)

        Raises:
            NotFoundError: If entry not found

        Example:
            >>> kb.delete("KB-20251019-001", reason="Outdated decision")
        """
        entries = self._load_entries()
        entry_index = None

        # Find entry
        for i, entry in enumerate(entries):
            if entry.id == entry_id:
                entry_index = i
                break

        if entry_index is None:
            raise NotFoundError(f"Entry with ID '{entry_id}' not found.")

        # Remove entry
        entries.pop(entry_index)
        self._save_entries(entries)
        self._rebuild_search_index()  # Rebuild before invalidating cache
        self._invalidate_cache()

    def list_all(self, include_deleted: bool = False) -> List[KnowledgeBaseEntry]:
        """
        List all entries.

        Args:
            include_deleted: Include deleted entries (for Phase 1 soft delete)

        Returns:
            List of all KnowledgeBaseEntry objects

        Example:
            >>> all_entries = kb.list_all()
            >>> print(f"Total entries: {len(all_entries)}")
            Total entries: 5
        """
        # Note: include_deleted parameter is for future soft delete implementation
        return self._load_entries()

    def _load_entries(self) -> List[KnowledgeBaseEntry]:
        """
        Load entries from YAML.

        Uses cache if available, otherwise reads from disk.

        Returns:
            List of KnowledgeBaseEntry objects
        """
        if self._entries_cache is not None:
            return self._entries_cache

        data = read_yaml(self.kb_file)

        # If file is empty or doesn't have entries, return empty list
        if not data or "entries" not in data:
            return []

        # Parse entries
        entries = []
        for entry_data in data["entries"]:
            # Parse datetime fields
            if "created_at" in entry_data and isinstance(entry_data["created_at"], str):
                entry_data["created_at"] = datetime.fromisoformat(entry_data["created_at"])
            if "updated_at" in entry_data and isinstance(entry_data["updated_at"], str):
                entry_data["updated_at"] = datetime.fromisoformat(entry_data["updated_at"])

            entries.append(KnowledgeBaseEntry(**entry_data))

        # Update cache
        self._entries_cache = entries
        return entries

    def _save_entries(self, entries: List[KnowledgeBaseEntry]) -> None:
        """
        Save entries to YAML.

        Args:
            entries: List of KnowledgeBaseEntry objects to save
        """
        # Load current config or create default
        data = read_yaml(self.kb_file)
        if not data:
            data = {
                "version": "1.0",
                "project_name": self.root_dir.name,
                "project_description": None,
            }

        # Convert entries to dict format
        entries_data = []
        for entry in entries:
            entry_dict = entry.model_dump()
            # Convert datetime to ISO format string
            entry_dict["created_at"] = entry.created_at.isoformat()
            entry_dict["updated_at"] = entry.updated_at.isoformat()
            entries_data.append(entry_dict)

        data["entries"] = entries_data

        # Validate before writing
        validate_kb_yaml(data)

        # Write with backup
        write_yaml(self.kb_file, data, backup=True)

        # Set secure permissions
        set_secure_permissions(self.kb_file)

    def _ensure_kb_exists(self) -> None:
        """
        Create KB file if it doesn't exist.

        Creates minimal YAML structure with project config.
        """
        if not self.kb_file.exists():
            initial_data: Dict[str, Any] = {
                "version": "1.0",
                "project_name": self.root_dir.name,
                "project_description": None,
                "entries": [],
            }
            write_yaml(self.kb_file, initial_data, backup=False)
            set_secure_permissions(self.kb_file)

    def _generate_id(self) -> str:
        """
        Generate unique KB ID (KB-YYYYMMDD-NNN).

        Returns:
            Unique ID string

        Example:
            >>> kb._generate_id()
            'KB-20251019-001'
        """
        entries = self._load_entries()
        today = datetime.now().strftime("%Y%m%d")

        # Find all IDs for today
        today_ids = [
            int(e.id.split("-")[-1])
            for e in entries
            if e.id.startswith(f"KB-{today}")
        ]

        # Get next sequence number
        next_num = max(today_ids, default=0) + 1

        return f"KB-{today}-{next_num:03d}"

    def _invalidate_cache(self) -> None:
        """Invalidate entries cache."""
        self._entries_cache = None

    def _rebuild_search_index(self) -> None:
        """Rebuild TF-IDF search index after data changes."""
        if not SEARCH_ENGINE_AVAILABLE or SearchEngine is None:
            return

        # Use _load_entries directly to avoid cache issues
        entries = self._load_entries()
        if entries:
            try:
                self._search_engine = SearchEngine(entries)
            except Exception:
                # If search engine fails to initialize, fall back to simple search
                self._search_engine = None
        else:
            self._search_engine = None

    def export_to_markdown(
        self,
        output_dir: Path,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Export Knowledge Base entries to Markdown documentation files.

        Creates one Markdown file per category (or a single file if category specified).
        Decision entries use ADR (Architecture Decision Record) format.
        Other categories use standard documentation format.

        Args:
            output_dir: Directory to write Markdown files to
            category: Optional category filter (export only this category)

        Returns:
            Dictionary with export statistics:
                - "total_entries": Total entries exported
                - "files_created": Number of files created
                - "categories": List of categories exported

        Raises:
            ValidationError: If output_dir is invalid or not writable
            NotFoundError: If no entries match the category filter

        Example:
            >>> stats = kb.export_to_markdown(Path("./docs/kb"))
            >>> print(stats)
            {"total_entries": 15, "files_created": 5, "categories": [...]}
        """
        # Validate output directory
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                from clauxton.core.models import ValidationError
                raise ValidationError(
                    f"Cannot create output directory '{output_dir}': {e}"
                )

        if not output_dir.is_dir():
            from clauxton.core.models import ValidationError
            raise ValidationError(
                f"Output path '{output_dir}' is not a directory"
            )

        # Load entries
        entries = self._load_entries()

        # Filter by category if specified
        if category:
            entries = [e for e in entries if e.category == category]
            if not entries:
                raise NotFoundError(
                    f"No entries found with category '{category}'"
                )

        # Group entries by category
        entries_by_category: Dict[str, List[KnowledgeBaseEntry]] = {}
        for entry in entries:
            if entry.category not in entries_by_category:
                entries_by_category[entry.category] = []
            entries_by_category[entry.category].append(entry)

        # Export each category
        files_created = 0
        total_entries = 0

        for cat, cat_entries in entries_by_category.items():
            filename = f"{cat}.md"
            file_path = output_dir / filename

            # Generate content based on category
            if cat == "decision":
                content = self._generate_adr_markdown(cat_entries)
            else:
                content = self._generate_standard_markdown(cat, cat_entries)

            # Write file
            file_path.write_text(content, encoding="utf-8")
            files_created += 1
            total_entries += len(cat_entries)

        return {
            "total_entries": total_entries,
            "files_created": files_created,
            "categories": list(entries_by_category.keys()),
        }

    def _generate_adr_markdown(self, entries: List[KnowledgeBaseEntry]) -> str:
        """
        Generate ADR-format Markdown for decision entries.

        ADR Format:
        - Title
        - Status: Accepted/Rejected/Superseded
        - Context: What is the issue we're addressing?
        - Decision: What is the change we're proposing?
        - Consequences: What are the positive/negative outcomes?

        Args:
            entries: List of decision entries to export

        Returns:
            Markdown content string
        """
        lines = [
            "# Architecture Decision Records",
            "",
            "This document contains all architectural decisions made for this project.",
            "",
            "---",
            "",
        ]

        for entry in sorted(entries, key=lambda e: e.created_at):
            lines.extend([
                f"## {entry.title}",
                "",
                f"**ID**: {entry.id}  ",
                "**Status**: Accepted  ",
                f"**Date**: {entry.created_at.strftime('%Y-%m-%d')}  ",
                f"**Version**: {entry.version}  ",
            ])

            if entry.tags:
                tags_str = ", ".join(f"`{tag}`" for tag in entry.tags)
                lines.append(f"**Tags**: {tags_str}  ")

            lines.extend([
                "",
                "### Context",
                "",
                entry.content,
                "",
                "### Consequences",
                "",
                "_This decision has been implemented and accepted._",
                "",
            ])

            if entry.updated_at != entry.created_at:
                lines.extend([
                    f"**Last Updated**: {entry.updated_at.strftime('%Y-%m-%d')}",
                    "",
                ])

            lines.extend([
                "---",
                "",
            ])

        return "\n".join(lines)

    def _generate_standard_markdown(
        self,
        category: str,
        entries: List[KnowledgeBaseEntry]
    ) -> str:
        """
        Generate standard Markdown for non-decision categories.

        Standard Format:
        - Title with category header
        - Entry title as section
        - Content
        - Metadata (ID, tags, dates)

        Args:
            category: Category name
            entries: List of entries to export

        Returns:
            Markdown content string
        """
        # Capitalize category for title
        category_title = category.capitalize()

        lines = [
            f"# {category_title}",
            "",
            f"This document contains all {category} entries for this project.",
            "",
            "---",
            "",
        ]

        for entry in sorted(entries, key=lambda e: e.created_at):
            lines.extend([
                f"## {entry.title}",
                "",
                f"**ID**: {entry.id}  ",
                f"**Created**: {entry.created_at.strftime('%Y-%m-%d')}  ",
            ])

            if entry.updated_at != entry.created_at:
                lines.append(
                    f"**Updated**: {entry.updated_at.strftime('%Y-%m-%d')}  "
                )

            if entry.tags:
                tags_str = ", ".join(f"`{tag}`" for tag in entry.tags)
                lines.append(f"**Tags**: {tags_str}  ")

            lines.extend([
                "",
                entry.content,
                "",
                "---",
                "",
            ])

        return "\n".join(lines)
