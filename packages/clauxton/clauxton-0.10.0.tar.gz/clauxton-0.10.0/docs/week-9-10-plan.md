# Week 9-10 実装計画: Phase 1完了 + v0.8.0リリース準備

**期間**: Week 9-10 (2週間)
**アプローチ**: ハイブリッド (Phase 1完了 + リリース準備 + Phase 2準備)
**目標**: TF-IDF検索実装, ドキュメント整備, v0.8.0リリース

---

## 概要

Phase 1 (Week 1-8) は機能的には完了しましたが, 以下が未実装:
- ❌ Enhanced Search (TF-IDF) - 検索精度向上
- ❌ Slash Commands - ユーザー体験向上
- ❌ リリースドキュメント (CHANGELOG, CONTRIBUTING)

このWeek 9-10で, これらを完成させ, v0.8.0としてリリース準備を整えます.

---

## Week 9: Enhanced Search + Documentation

### Day 1-2: TF-IDF Search 実装

#### 目標
現在の線形検索を, TF-IDF (Term Frequency-Inverse Document Frequency) アルゴリズムで置き換え, 検索精度と関連性を向上させる.

#### 実装内容

**新規ファイル**: `clauxton/core/search.py`

```python
"""
Enhanced search engine with TF-IDF.

Provides relevance-based search for Knowledge Base entries.
"""
from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from clauxton.core.models import KnowledgeBaseEntry


class SearchEngine:
    """TF-IDF based search engine for Knowledge Base entries."""

    def __init__(self, entries: List[KnowledgeBaseEntry]):
        """
        Initialize search engine with entries.

        Args:
            entries: List of Knowledge Base entries to index
        """
        self.entries = entries
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)  # Unigrams and bigrams
        )
        self._build_index()

    def _build_index(self) -> None:
        """Build TF-IDF index from entries."""
        if not self.entries:
            self.tfidf_matrix = None
            return

        # Create corpus: combine title, content, tags
        corpus = [
            f"{entry.title} {entry.content} {' '.join(entry.tags or [])}"
            for entry in self.entries
        ]

        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[KnowledgeBaseEntry, float]]:
        """
        Search for entries matching query.

        Args:
            query: Search query string
            category: Optional category filter
            limit: Maximum number of results

        Returns:
            List of (entry, relevance_score) tuples, sorted by relevance (highest first)
        """
        if not self.entries or self.tfidf_matrix is None:
            return []

        # Filter by category first
        filtered_entries = self.entries
        if category:
            filtered_entries = [e for e in self.entries if e.category == category]
            if not filtered_entries:
                return []

        # Transform query to TF-IDF vector
        query_vec = self.vectorizer.transform([query])

        # Calculate cosine similarity
        if category:
            # Need to rebuild index for filtered entries
            temp_engine = SearchEngine(filtered_entries)
            scores = cosine_similarity(query_vec, temp_engine.tfidf_matrix)[0]
            indices = scores.argsort()[-limit:][::-1]
            return [(filtered_entries[i], scores[i]) for i in indices if scores[i] > 0]
        else:
            scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]
            indices = scores.argsort()[-limit:][::-1]
            return [(self.entries[i], scores[i]) for i in indices if scores[i] > 0]

    def rebuild_index(self, entries: List[KnowledgeBaseEntry]) -> None:
        """
        Rebuild index with new entries.

        Args:
            entries: Updated list of entries
        """
        self.entries = entries
        self._build_index()
```

#### 既存コード修正: `clauxton/core/knowledge_base.py`

```python
# 追加: SearchEngineのインポート
from clauxton.core.search import SearchEngine

class KnowledgeBase:
    def __init__(self, root_dir: Path):
        # ... 既存コード ...
        self.search_engine: Optional[SearchEngine] = None
        self._rebuild_search_index()

    def _rebuild_search_index(self) -> None:
        """Rebuild search index after data changes."""
        entries = self.list_all()
        if entries:
            self.search_engine = SearchEngine(entries)

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[KnowledgeBaseEntry]:
        """
        Search entries using TF-IDF algorithm.

        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum results

        Returns:
            List of matching entries, sorted by relevance
        """
        if not self.search_engine:
            self._rebuild_search_index()

        if not self.search_engine:
            return []  # No entries

        results = self.search_engine.search(query, category, limit)
        return [entry for entry, score in results]

    def add(self, entry: KnowledgeBaseEntry) -> str:
        # ... 既存のadd実装 ...
        # 最後に追加:
        self._rebuild_search_index()
        return entry.id

    def update(self, entry_id: str, updates: dict) -> KnowledgeBaseEntry:
        # ... 既存のupdate実装 ...
        # 最後に追加:
        self._rebuild_search_index()
        return updated_entry

    def delete(self, entry_id: str) -> None:
        # ... 既存のdelete実装 ...
        # 最後に追加:
        self._rebuild_search_index()
```

#### 依存関係追加

**pyproject.toml**:
```toml
dependencies = [
    "click>=8.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
    "mcp>=0.1.0",
    "scikit-learn>=1.3.0",  # NEW
    "numpy>=1.24.0",        # NEW (scikit-learnの依存)
]
```

#### テスト追加: `tests/core/test_search.py` (新規)

```python
"""Tests for TF-IDF search engine."""
import pytest
from clauxton.core.search import SearchEngine
from clauxton.core.models import KnowledgeBaseEntry
from datetime import datetime


@pytest.fixture
def sample_entries():
    """Create sample KB entries for testing."""
    return [
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="Use FastAPI framework",
            category="architecture",
            content="All backend APIs use FastAPI for async support and automatic docs.",
            tags=["backend", "api", "fastapi"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
        KnowledgeBaseEntry(
            id="KB-20251019-002",
            title="PostgreSQL for production",
            category="decision",
            content="Use PostgreSQL 15+ for production databases.",
            tags=["database", "postgresql"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
        KnowledgeBaseEntry(
            id="KB-20251019-003",
            title="Repository pattern",
            category="pattern",
            content="Use Repository pattern for all database access layers.",
            tags=["pattern", "database"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
    ]


def test_search_basic(sample_entries):
    """Test basic TF-IDF search."""
    engine = SearchEngine(sample_entries)
    results = engine.search("FastAPI", limit=10)

    assert len(results) > 0
    assert results[0][0].id == "KB-20251019-001"  # FastAPI entry should be first
    assert results[0][1] > 0  # Score should be positive


def test_search_relevance_ranking(sample_entries):
    """Test that more relevant results rank higher."""
    engine = SearchEngine(sample_entries)
    results = engine.search("database", limit=10)

    # Both PostgreSQL and Repository entries mention "database"
    # Should return both
    assert len(results) >= 2
    entry_ids = [r[0].id for r in results]
    assert "KB-20251019-002" in entry_ids
    assert "KB-20251019-003" in entry_ids


def test_search_with_category_filter(sample_entries):
    """Test search with category filter."""
    engine = SearchEngine(sample_entries)
    results = engine.search("database", category="decision", limit=10)

    assert len(results) == 1
    assert results[0][0].id == "KB-20251019-002"
    assert results[0][0].category == "decision"


def test_search_empty_query(sample_entries):
    """Test search with empty query."""
    engine = SearchEngine(sample_entries)
    results = engine.search("", limit=10)

    # Empty query should return all entries (or none, depending on implementation)
    assert isinstance(results, list)


def test_search_no_matches(sample_entries):
    """Test search with no matches."""
    engine = SearchEngine(sample_entries)
    results = engine.search("nonexistent_term_xyz", limit=10)

    assert len(results) == 0


def test_search_empty_entries():
    """Test search with no entries."""
    engine = SearchEngine([])
    results = engine.search("test", limit=10)

    assert len(results) == 0


def test_rebuild_index(sample_entries):
    """Test rebuilding search index."""
    engine = SearchEngine([])
    assert engine.tfidf_matrix is None

    engine.rebuild_index(sample_entries)
    results = engine.search("FastAPI", limit=10)

    assert len(results) > 0
```

#### 実行コマンド

```bash
# 依存関係インストール
pip install scikit-learn numpy

# テスト実行
pytest tests/core/test_search.py -v

# 既存テストの互換性確認
pytest tests/core/test_knowledge_base.py -v

# 全テスト実行
pytest tests/ -v
```

**期間**: 2日 (Day 1-2)

---

### Day 3: CHANGELOG.md + CONTRIBUTING.md

#### CHANGELOG.md 作成

**ファイル**: `CHANGELOG.md`

```markdown
# Changelog

All notable changes to Clauxton will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.0] - 2025-10-XX

### Added
- **Enhanced Search**: TF-IDF algorithm for relevance-based search (Phase 1 Week 9)
- **Task Management**: Complete CRUD operations with auto-dependency inference (Phase 1 Week 4-5)
- **MCP Server**: 12 tools for Knowledge Base and Task Management (Phase 1 Week 3-5)
- **Slash Commands**: 5 commands for quick access to common operations (Phase 1 Week 9)
- **Documentation**: Troubleshooting guide and best practices guide (Phase 1 Week 8)
- **Testing**: 237 comprehensive tests with 94% code coverage (Phase 1 Week 8)
- Auto-dependency inference from file overlap
- Task priority and status management
- KB entry versioning on updates
- Automatic backup (.yml.bak) on file updates
- Unicode support in Knowledge Base (日本語, emoji, etc.)

### Changed
- Improved search relevance with TF-IDF algorithm (was linear scan)
- CLI error messages are more helpful and actionable
- Task "next" command now respects dependencies and priority

### Fixed
- Task update with no fields now shows clear error message
- Task delete confirmation properly handles cancellation
- Optional fields (actual_hours, description, estimated_hours) display correctly
- Exception handling in all CLI commands

### Documentation
- Added troubleshooting guide with FAQ
- Added best practices guide for KB and Task usage
- Added Phase 1 completion summary
- Improved MCP Server documentation with examples
- Updated README with installation and quick start

## [0.7.0] - 2025-10-19

### Added
- Knowledge Base update command (Phase 1 Week 6-7)
- Knowledge Base delete command (Phase 1 Week 6-7)
- Task Management CLI (Phase 1 Week 4-5)
- MCP Server with Task Management tools (Phase 1 Week 5)

### Changed
- Improved error handling across all commands
- Enhanced CLI output formatting

## [0.1.0] - 2025-10-15

### Added
- Initial release (Phase 0)
- Knowledge Base CRUD (add, get, list, search)
- YAML persistence
- Basic CLI
- 111 tests with 93% coverage

---

[Unreleased]: https://github.com/nakishiyaman/clauxton/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/nakishiyaman/clauxton/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/nakishiyaman/clauxton/compare/v0.1.0...v0.7.0
[0.1.0]: https://github.com/nakishiyaman/clauxton/releases/tag/v0.1.0
```

#### CONTRIBUTING.md 作成

**ファイル**: `CONTRIBUTING.md`

```markdown
# Contributing to Clauxton

Thank you for your interest in contributing to Clauxton! We welcome contributions from the community.

## Getting Started

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nakishiyaman/clauxton.git
   cd clauxton
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guide
- **Type hints**: Required for all functions and methods
- **Docstrings**: Use Google-style docstrings for all public APIs
- **Formatting**: Code is formatted with `black` (line length: 100)
- **Imports**: Sorted with `isort`

Example:
```python
from typing import List, Optional

def search_entries(
    query: str,
    category: Optional[str] = None,
    limit: int = 10
) -> List[KnowledgeBaseEntry]:
    """
    Search Knowledge Base entries by query.

    Args:
        query: Search query string
        category: Optional category filter
        limit: Maximum number of results

    Returns:
        List of matching entries, sorted by relevance

    Raises:
        ValueError: If limit is negative
    """
    ...
```

### Testing Requirements

- **Coverage**: All new code must have tests with 90%+ coverage
- **Test framework**: pytest
- **Test location**: Mirror source structure in `tests/` directory
- **Test naming**: `test_<functionality>.py`, functions: `test_<scenario>()`

Run tests:
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=clauxton --cov-report=term-missing

# Specific file
pytest tests/core/test_search.py -v
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding or updating tests
- `refactor`: Code refactoring (no functional change)
- `perf`: Performance improvement
- `chore`: Build process, dependencies, etc.

**Examples**:
```
feat(search): Add TF-IDF search engine

Implement TF-IDF algorithm using scikit-learn for relevance-based
search. Improves search accuracy for large Knowledge Bases (200+ entries).

Closes #42

---

fix(cli): Handle empty task update gracefully

Show clear error message when task update is called without any fields.

---

docs: Add troubleshooting guide

Created comprehensive troubleshooting guide covering installation issues,
KB errors, task management problems, and MCP server debugging.
```

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**:
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Run tests locally**:
   ```bash
   pytest tests/ -v --cov=clauxton
   ```

4. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat(scope): Your feature description"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feat/your-feature-name
   ```

6. **Create Pull Request**:
   - Use the PR template
   - Link related issues
   - Wait for CI checks to pass
   - Address review feedback

### PR Checklist

- [ ] Tests added/updated (90%+ coverage maintained)
- [ ] Documentation updated (if public API changed)
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow Conventional Commits
- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] No breaking changes (or clearly documented)

## Project Structure

```
clauxton/
├── clauxton/
│   ├── cli/           # CLI commands
│   ├── core/          # Core business logic
│   ├── mcp/           # MCP Server
│   └── utils/         # Utilities
├── tests/
│   ├── cli/           # CLI tests
│   ├── core/          # Core tests
│   ├── mcp/           # MCP tests
│   └── integration/   # Integration tests
├── docs/              # Documentation
└── pyproject.toml     # Project config
```

## Areas for Contribution

### High Priority
- Enhanced search algorithms (fuzzy matching, semantic search)
- Performance optimization (large Knowledge Bases)
- Additional MCP tools
- Integration with other tools (Jira, GitHub Issues)

### Medium Priority
- Web UI (optional)
- Export/import functionality
- Task templates
- Analytics and insights

### Documentation
- Tutorial videos
- More examples
- API reference
- Translation (Japanese, etc.)

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **Email**: your.email@example.com

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Clauxton!**
```

**期間**: 1日 (Day 3)

---

### Day 4-5: Slash Commands 実装

#### 概要
Claude Codeでクイックアクセスできる Slash Commands を実装します.

#### ディレクトリ構造
```
.claude/
└── commands/
    ├── kb-search.md
    ├── kb-add.md
    ├── task-next.md
    ├── task-start.md
    └── task-list.md
```

#### 1. `kb-search.md`

```markdown
---
name: kb-search
description: Search the Knowledge Base for relevant entries
arguments:
  - name: query
    description: Search query (keyword or phrase)
    required: true
  - name: category
    description: Filter by category (architecture, constraint, decision, pattern, convention)
    required: false
  - name: limit
    description: Maximum number of results (default: 10)
    required: false
---

# Knowledge Base Search

Search the Knowledge Base for entries matching "{{query}}".

## Instructions

1. Use the `kb_search` MCP tool with the following parameters:
   - query: "{{query}}"
   {{#if category}}- category: "{{category}}"{{/if}}
   {{#if limit}}- limit: {{limit}}{{/if}}

2. Display results in a clear, readable format showing:
   - Entry ID
   - Title
   - Category
   - Content preview (first 100 chars)
   - Tags

3. If no results found, suggest:
   - Trying broader keywords
   - Removing category filter
   - Checking spelling

## Example

```
User: /kb-search "FastAPI"

Results:
1. KB-20251019-001 - Use FastAPI framework
   Category: architecture
   Preview: All backend APIs use FastAPI for async support...
   Tags: backend, api, fastapi
```
```

#### 2. `kb-add.md`

```markdown
---
name: kb-add
description: Add a new entry to the Knowledge Base
---

# Add Knowledge Base Entry

Guide the user through adding a new Knowledge Base entry.

## Instructions

1. Ask the user for the following information:
   - **Title**: Short, descriptive title (max 50 chars)
   - **Category**: One of: architecture, constraint, decision, pattern, convention
   - **Content**: Detailed description
   - **Tags** (optional): Comma-separated tags

2. Use the `kb_add` MCP tool with the collected information.

3. Display the created entry ID and confirm success.

## Best Practices to Suggest

- **Title**: Be specific (e.g., "Use FastAPI framework" not "API")
- **Category**:
  - architecture: System design
  - constraint: Hard requirements
  - decision: Choices with rationale
  - pattern: Reusable code patterns
  - convention: Team agreements
- **Content**: Include context, rationale, and examples
- **Tags**: Use lowercase, be specific (e.g., "postgresql" not "database")

## Example

```
You: Let's add a Knowledge Base entry. What's the title?
User: Use PostgreSQL for production
You: Great! What category? (architecture, constraint, decision, pattern, convention)
User: decision
You: What's the content?
User: Use PostgreSQL 15+ for all production databases.
You: Any tags? (optional, comma-separated)
User: database,postgresql

[Calls kb_add MCP tool]

✓ Added entry: KB-20251019-005
  Title: Use PostgreSQL for production
  Category: decision
  Tags: database, postgresql
```
```

#### 3. `task-next.md`

```markdown
---
name: task-next
description: Get the next recommended task to work on
---

# Get Next Task

Retrieve the AI-recommended next task to work on.

## Instructions

1. Use the `task_next` MCP tool (no parameters needed).

2. If a task is returned:
   - Display task details:
     - Task ID
     - Name
     - Priority
     - Description (if present)
     - Files to edit (if present)
     - Related KB entries (if present)
     - Estimated hours (if present)
   - Show command to start the task:
     ```
     /task-start <TASK-ID>
     ```

3. If no tasks available:
   - Explain that all tasks are either:
     - Completed
     - In progress
     - Blocked by dependencies
   - Suggest:
     - Listing all tasks: `/task-list`
     - Adding new tasks

## Example

```
User: /task-next

📋 Next Task to Work On:

TASK-003 - Implement user authentication
Priority: high
Files: src/auth.py, tests/test_auth.py
Related KB: KB-20251019-005
Estimated: 4.0 hours

Description:
Implement JWT-based authentication following our architecture decision.

To start this task:
/task-start TASK-003
```
```

#### 4. `task-start.md`

```markdown
---
name: task-start
description: Start working on a task
arguments:
  - name: task_id
    description: Task ID (e.g., TASK-001)
    required: true
---

# Start Task

Mark task {{task_id}} as in progress.

## Instructions

1. First, use `task_get` MCP tool to retrieve task details for {{task_id}}.

2. Display task information:
   - Name
   - Description
   - Files to edit
   - Related KB entries (fetch and display these)
   - Dependencies (check if all are completed)

3. Check dependencies:
   - If any dependencies are not completed, warn the user
   - Show which tasks must be completed first

4. If dependencies are satisfied, use `task_update` MCP tool:
   - task_id: "{{task_id}}"
   - status: "in_progress"

5. Display confirmation and next steps:
   - Show files to edit
   - Display related KB entries for context
   - Suggest starting with reading the KB entries

## Example

```
User: /task-start TASK-003

Loading task TASK-003...

TASK-003 - Implement user authentication
Description: Implement JWT-based authentication
Files to edit:
  - src/auth.py
  - tests/test_auth.py
Related KB:
  - KB-20251019-005: Use JWT for authentication

Checking dependencies... ✓ All dependencies completed

✓ Started task TASK-003

Next steps:
1. Review related KB entry:
   clauxton kb get KB-20251019-005

2. Edit files:
   - src/auth.py
   - tests/test_auth.py

3. When done, mark as completed:
   clauxton task update TASK-003 --status completed
```
```

#### 5. `task-list.md`

```markdown
---
name: task-list
description: List all tasks with optional filters
arguments:
  - name: status
    description: Filter by status (pending, in_progress, completed, blocked)
    required: false
  - name: priority
    description: Filter by priority (low, medium, high, critical)
    required: false
---

# List Tasks

List all tasks{{#if status}} with status "{{status}}"{{/if}}{{#if priority}} and priority "{{priority}}"{{/if}}.

## Instructions

1. Use the `task_list` MCP tool with parameters:
   {{#if status}}- status: "{{status}}"{{/if}}
   {{#if priority}}- priority: "{{priority}}"{{/if}}

2. Display tasks in a clear table or list format:
   - Task ID
   - Name
   - Status
   - Priority
   - Dependencies (if any)

3. Group tasks by status for better readability:
   - 🔴 Critical priority
   - 🟠 High priority
   - 🟡 Medium priority
   - 🟢 Low priority

4. Show summary statistics:
   - Total tasks
   - By status: X pending, Y in progress, Z completed

## Example

```
User: /task-list --status pending

Tasks (5 pending):

🔴 CRITICAL
  TASK-001 - Fix security vulnerability
    Status: pending
    Depends on: none

🟠 HIGH
  TASK-003 - Implement user authentication
    Status: pending
    Depends on: TASK-002

  TASK-005 - Add API rate limiting
    Status: pending
    Depends on: TASK-003

🟡 MEDIUM
  TASK-006 - Add user profile page
    Status: pending
    Depends on: TASK-003

🟢 LOW
  TASK-008 - Refactor CSS
    Status: pending
    Depends on: none

Summary: 5 pending, 2 in progress, 3 completed
```
```

#### 実装手順

```bash
# 1. ディレクトリ作成
mkdir -p .claude/commands

# 2. ファイル作成
touch .claude/commands/kb-search.md
touch .claude/commands/kb-add.md
touch .claude/commands/task-next.md
touch .claude/commands/task-start.md
touch .claude/commands/task-list.md

# 3. 各ファイルに上記内容をコピー

# 4. Claude Codeで動作確認
# Claude Codeを再起動して, /kb-search などのコマンドが認識されることを確認
```

**期間**: 2日 (Day 4-5)

---

## Week 10: Release Preparation + Phase 2 Setup

### Day 6-7: PyPI リリース準備

#### pyproject.toml 更新

```toml
[project]
name = "clauxton"
version = "0.8.0"
description = "Persistent project context for Claude Code - Knowledge Base and Task Management"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
keywords = ["claude-code", "knowledge-base", "task-management", "mcp", "ai", "context"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: Version Control",
]

dependencies = [
    "click>=8.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
    "mcp>=0.1.0",
    "scikit-learn>=1.3.0",
    "numpy>=1.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
]

[project.scripts]
clauxton = "clauxton.cli.main:cli"
clauxton-mcp = "clauxton.mcp.server:main"

[project.urls]
Homepage = "https://github.com/nakishiyaman/clauxton"
Documentation = "https://github.com/nakishiyaman/clauxton/tree/main/docs"
Repository = "https://github.com/nakishiyaman/clauxton"
Issues = "https://github.com/nakishiyaman/clauxton/issues"
Changelog = "https://github.com/nakishiyaman/clauxton/blob/main/CHANGELOG.md"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["clauxton"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --strict-markers --cov=clauxton --cov-report=term-missing"

[tool.coverage.run]
source = ["clauxton"]
omit = ["tests/*", "*/test_*.py"]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false

[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

#### LICENSE ファイル作成 (MIT)

```text
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

#### ビルドとテスト

```bash
# 1. 依存関係インストール
pip install build twine

# 2. ビルド
python -m build

# 3. 生成物確認
ls -lh dist/
# clauxton-0.8.0-py3-none-any.whl
# clauxton-0.8.0.tar.gz

# 4. TestPyPIでテスト (オプション)
twine upload --repository testpypi dist/*

# 5. TestPyPIからインストールテスト
pip install --index-url https://test.pypi.org/simple/ clauxton

# 6. 動作確認
clauxton --help
```

**期間**: 2日 (Day 6-7)

---

### Day 8-9: GitHub Release + Phase 2 設計

#### GitHub Release v0.8.0 作成

```bash
# 1. タグ作成
git tag -a v0.8.0 -m "Release v0.8.0: Enhanced Search + Documentation"

# 2. タグをプッシュ
git push origin v0.8.0

# 3. GitHub UIでReleaseを作成
# https://github.com/nakishiyaman/clauxton/releases/new

# Title: v0.8.0 - Enhanced Search + Documentation
# Body: (CHANGELOG.mdの[0.8.0]セクションをコピー)
# Attach files:
#   - dist/clauxton-0.8.0-py3-none-any.whl
#   - dist/clauxton-0.8.0.tar.gz
```

#### Phase 2 計画書作成

**ファイル**: `docs/phase-2-plan.md`

```markdown
# Phase 2 Implementation Plan: Conflict Prevention

**Duration**: Week 11-14 (4 weeks)
**Goal**: Pre-merge conflict detection and drift detection
**Status**: Planning

---

## Overview

Phase 2 adds intelligent conflict prevention capabilities:
1. **Conflict Detector**: Analyze tasks for potential file conflicts
2. **Risk Scoring**: Estimate conflict probability
3. **Safe Execution Order**: Recommend optimal task sequence
4. **Drift Detection**: Detect unexpected scope changes

---

## Week 11-12: Conflict Detector Core

### Features

#### ConflictDetector Class
```python
class ConflictDetector:
    def detect_conflicts(task_ids: List[str]) -> List[ConflictRisk]
    def analyze_pair(task1: Task, task2: Task) -> ConflictRisk
    def estimate_line_overlap(file: str, tasks: List[Task]) -> float
    def suggest_order(task_ids: List[str]) -> List[str]
```

#### Risk Scoring
- File overlap detection
- Line-level overlap estimation
- Historical conflict analysis
- Risk score: 0.0-1.0 (Low/Medium/High)

#### CLI Commands
```bash
clauxton conflicts check [task-ids]
clauxton conflicts suggest-order [task-ids]
```

#### MCP Tool
- `conflicts_check`: Check conflicts between tasks

---

## Week 13-14: Drift Detection + Polish

### Features

#### Drift Detection
- Expected vs actual state comparison
- Detect unexpected file edits
- Detect scope expansion
- Suggest task splitting

#### Event Logging
- Log all major actions
- JSON Lines format
- Event types: kb_added, task_started, file_edited, conflict_detected

---

## Success Criteria

- Conflict detection accuracy >80%
- False positive rate <15%
- Event log captures all actions
- All tests passing (90%+ coverage)

---

**Next Steps**: Begin Week 11 implementation after v0.8.0 release
```

**期間**: 2日 (Day 8-9)

---

### Day 10: バッファ + 最終確認

#### チェックリスト

**コード**:
- [ ] TF-IDF検索動作確認
- [ ] 全テスト合格 (237+)
- [ ] カバレッジ 94%+ 維持
- [ ] 依存関係正しくインストール

**ドキュメント**:
- [ ] CHANGELOG.md 完成
- [ ] CONTRIBUTING.md 完成
- [ ] README.md 更新 (v0.8.0インストール手順)
- [ ] Slash Commands 5個動作確認

**リリース**:
- [ ] pyproject.toml バージョン 0.8.0
- [ ] LICENSE ファイル作成
- [ ] PyPI ビルド成功
- [ ] GitHub Release v0.8.0 作成

**Phase 2**:
- [ ] Phase 2 計画書作成
- [ ] Conflict Detector 設計完了

**期間**: 1日 (Day 10)

---

## 成功基準 (Week 9-10全体)

### 技術メトリクス
- ✅ TF-IDF検索実装完了
- ✅ 検索速度 <1s (200+ エントリ)
- ✅ テストカバレッジ 94%+ 維持
- ✅ 全テスト合格 (237+)

### ドキュメント
- ✅ CHANGELOG.md 完成
- ✅ CONTRIBUTING.md 完成
- ✅ Slash Commands 5個実装
- ✅ Phase 2 計画書作成

### リリース
- ✅ PyPI パッケージ準備完了
- ✅ GitHub Release v0.8.0 作成
- ✅ README.md インストール手順更新

---

## リスク管理

### リスク1: TF-IDF実装の複雑性
**確率**: 中
**影響**: 高
**対策**: scikit-learn使用で実装簡素化, プロトタイプで動作確認

### リスク2: PyPIリリースの初回トラブル
**確率**: 高
**影響**: 中
**対策**: TestPyPIで事前テスト, ドキュメント熟読

### リスク3: スケジュール遅延
**確率**: 中
**影響**: 低
**対策**: Day 10をバッファとして確保, 優先度明確化

---

## 次のアクション

### 今すぐ (Day 1開始)
1. scikit-learn インストール
   ```bash
   pip install scikit-learn numpy
   ```

2. `clauxton/core/search.py` 作成開始

### 今週中 (Day 1-5)
- TF-IDF検索実装 (Day 1-2)
- ドキュメント作成 (Day 3)
- Slash Commands実装 (Day 4-5)

### 来週 (Day 6-10)
- PyPIリリース準備 (Day 6-7)
- GitHub Release作成 (Day 8-9)
- バッファ + 確認 (Day 10)

---

**ステータス**: 計画完成, 実装準備完了
**作成日**: 2025-10-19
**次のマイルストーン**: TF-IDF検索実装完了 (Day 2終了時)
