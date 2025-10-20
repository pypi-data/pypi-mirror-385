# Phase 1 Implementation Plan: Core Engine

**Duration**: Week 3-8 (6 weeks)
**Goal**: Implement MCP Server, Task Management, and Knowledge Base enhancements
**Status**: Ready to Start

---

## Overview

Phase 1 builds upon Phase 0's solid foundation to add:
1. **MCP Server** with Knowledge Base tools
2. **Task Management** (CRUD operations)
3. **Auto-dependency Inference** (analyzing file changes)
4. **Enhanced Search** (TF-IDF, better relevance)
5. **Knowledge Base Updates** (update/delete commands)

**Key Principle**: Deliver incremental value. Each week should produce working, testable features.

---

## Phase 1 Prerequisites (✅ Complete)

From Phase 0:
- ✅ Knowledge Base CRUD (add, get, list, search)
- ✅ CLI framework (Click-based)
- ✅ YAML persistence
- ✅ Pydantic models (KnowledgeBaseEntry, Task)
- ✅ 111 tests, 93% coverage
- ✅ User documentation

---

## Week 3: MCP Server Foundation

**Goal**: Create working MCP Server with Knowledge Base tools

### Day 15-16: MCP Server Setup & Research

**Tasks**:
1. **Research MCP SDK**:
   - Check latest MCP Python SDK documentation
   - Understand Server/Tool protocol
   - Review example servers (if available)

2. **Install MCP Dependencies**:
   ```bash
   pip install mcp  # or equivalent SDK
   ```

3. **Create Basic Server** (`clauxton/mcp/kb_server.py`):
   ```python
   from mcp.server import Server

   app = Server("clauxton-kb")

   @app.tool()
   async def health_check():
       """Health check endpoint."""
       return {"status": "ok", "version": "0.2.0"}

   if __name__ == "__main__":
       app.run()
   ```

**Tests** (`tests/mcp/test_kb_server.py`):
- [ ] Server starts successfully
- [ ] Health check responds

**Time**: 2 days
**Deliverable**: Basic MCP Server that starts and responds to health check

---

### Day 17-18: Knowledge Base Tools

**Tasks**:
1. **Implement `kb-search` tool**:
   ```python
   @app.tool()
   async def kb_search(query: str, category: Optional[str] = None, limit: int = 10):
       """Search Knowledge Base.

       Args:
           query: Search keywords
           category: Filter by category (optional)
           limit: Max results (default 10)

       Returns:
           List of matching KB entries
       """
       kb = KnowledgeBase(Path.cwd())
       results = kb.search(query, category=category, limit=limit)
       return [entry.model_dump() for entry in results]
   ```

2. **Implement `kb-add` tool**:
   ```python
   @app.tool()
   async def kb_add(title: str, category: str, content: str, tags: List[str] = []):
       """Add entry to Knowledge Base.

       Args:
           title: Entry title (max 50 chars)
           category: One of: architecture, constraint, decision, pattern, convention
           content: Entry content (max 10000 chars)
           tags: Optional tags

       Returns:
           Entry ID (e.g., KB-20251019-001)
       """
       kb = KnowledgeBase(Path.cwd())
       entry_id = kb._generate_id()
       entry = KnowledgeBaseEntry(
           id=entry_id,
           title=title,
           category=category,
           content=content,
           tags=tags,
           created_at=datetime.now(),
           updated_at=datetime.now(),
       )
       kb.add(entry)
       return entry_id
   ```

3. **Implement `kb-list` tool**:
   ```python
   @app.tool()
   async def kb_list(category: Optional[str] = None):
       """List all Knowledge Base entries."""
       kb = KnowledgeBase(Path.cwd())
       entries = kb.list_all()
       if category:
           entries = [e for e in entries if e.category == category]
       return [{"id": e.id, "title": e.title, "category": e.category} for e in entries]
   ```

**Tests** (`tests/mcp/test_kb_tools.py`):
- [ ] `kb-search` returns correct results
- [ ] `kb-add` creates entry
- [ ] `kb-list` lists entries
- [ ] Tools handle errors gracefully

**Time**: 2 days
**Deliverable**: 3 working MCP tools for Knowledge Base

---

### Day 19-21: Plugin Manifest & Integration

**Tasks**:
1. **Create plugin manifest** (`.claude-plugin/plugin.json`):
   ```json
   {
     "name": "clauxton",
     "version": "0.2.0",
     "description": "Persistent project context for Claude Code",
     "mcp_servers": [
       {
         "name": "clauxton-kb",
         "command": "python -m clauxton.mcp.kb_server",
         "description": "Knowledge Base MCP Server",
         "env": {}
       }
     ],
     "commands": [],
     "hooks": []
   }
   ```

2. **Test MCP Server with Claude Code**:
   - Install Clauxton in a test project
   - Start MCP Server
   - Test tools via Claude Code UI
   - Document any issues

3. **Add server logging**:
   ```python
   import logging

   logger = logging.getLogger("clauxton.mcp")
   logger.setLevel(logging.INFO)

   @app.tool()
   async def kb_search(...):
       logger.info(f"Searching KB: query={query}, category={category}")
       # ... implementation
   ```

**Tests**:
- [ ] Plugin manifest is valid JSON
- [ ] MCP Server can be started via manifest
- [ ] Tools are discoverable
- [ ] Logging works

**Time**: 3 days
**Deliverable**: Working plugin manifest, MCP Server integrated with Claude Code

**Week 3 Success Criteria**:
- [ ] MCP Server starts and responds
- [ ] `kb-search`, `kb-add`, `kb-list` tools work
- [ ] Claude Code can discover and use tools
- [ ] Tests pass (>80% coverage for MCP code)

---

## Week 4: Task Management Foundation

**Goal**: Implement Task CRUD operations

### Day 22-24: Task Manager Core

**File**: `clauxton/core/task_manager.py`

**Tasks**:
1. **Implement TaskManager class**:
   ```python
   class TaskManager:
       def __init__(self, root_dir: Path):
           self.root_dir = root_dir
           self.tasks_file = root_dir / ".clauxton" / "tasks.yml"
           self._tasks_cache: Optional[List[Task]] = None
           self._ensure_tasks_file_exists()

       def add(self, task: Task) -> str:
           """Add task and return ID."""

       def get(self, task_id: str) -> Task:
           """Get task by ID."""

       def update(self, task_id: str, updates: Dict[str, Any]) -> Task:
           """Update task fields."""

       def delete(self, task_id: str) -> None:
           """Delete task."""

       def list_all(self, status: Optional[str] = None) -> List[Task]:
           """List all tasks, optionally filtered by status."""

       def _generate_id(self) -> str:
           """Generate unique task ID (TASK-001, TASK-002, ...)."""

       def _save_tasks(self, tasks: List[Task]) -> None:
           """Save tasks to YAML."""

       def _load_tasks(self) -> List[Task]:
           """Load tasks from YAML."""
   ```

2. **Implement Task model enhancements** (if needed):
   ```python
   class Task(BaseModel):
       id: str = Field(..., pattern=r"^TASK-\d{3}$")
       name: str = Field(..., min_length=1, max_length=100)
       description: Optional[str] = Field(default=None, max_length=1000)
       status: Literal["pending", "in_progress", "completed", "blocked"] = "pending"
       priority: Literal["low", "medium", "high"] = "medium"
       depends_on: List[str] = Field(default_factory=list)  # List of task IDs
       files_to_edit: List[str] = Field(default_factory=list)  # File paths
       related_kb: List[str] = Field(default_factory=list)  # KB entry IDs
       created_at: datetime
       started_at: Optional[datetime] = None
       completed_at: Optional[datetime] = None
       estimated_hours: Optional[float] = None
       actual_hours: Optional[float] = None
   ```

**Tests** (`tests/core/test_task_manager.py`):
- [ ] Add task (valid/invalid)
- [ ] Get task (exists/not exists)
- [ ] Update task (all fields, validation)
- [ ] Delete task
- [ ] List tasks (all, filtered by status)
- [ ] ID generation (sequential)
- [ ] YAML persistence

**Time**: 3 days
**Deliverable**: TaskManager with full CRUD operations

---

### Day 25-28: Task CLI Commands

**File**: `clauxton/cli/main.py` (add task commands)

**Tasks**:
1. **Implement `clauxton task add`**:
   ```python
   @cli.group()
   def task():
       """Task management commands."""
       pass

   @task.command()
   @click.option("--name", prompt=True, help="Task name")
   @click.option("--description", help="Task description")
   @click.option("--priority", type=click.Choice(["low", "medium", "high"]), default="medium")
   def add(name: str, description: Optional[str], priority: str):
       """Add new task."""
       # Implementation
   ```

2. **Implement `clauxton task list`**:
   ```python
   @task.command("list")
   @click.option("--status", type=click.Choice(["pending", "in_progress", "completed", "blocked"]))
   def list_tasks(status: Optional[str]):
       """List all tasks."""
       # Implementation
   ```

3. **Implement `clauxton task get`**:
   ```python
   @task.command()
   @click.argument("task_id")
   def get(task_id: str):
       """Get task details."""
       # Implementation
   ```

4. **Implement `clauxton task update`**:
   ```python
   @task.command()
   @click.argument("task_id")
   @click.option("--status", type=click.Choice([...]))
   @click.option("--name", help="Update task name")
   @click.option("--description", help="Update description")
   def update(task_id: str, **kwargs):
       """Update task."""
       # Implementation
   ```

5. **Implement `clauxton task delete`**:
   ```python
   @task.command()
   @click.argument("task_id")
   @click.confirmation_option(prompt="Are you sure?")
   def delete(task_id: str):
       """Delete task."""
       # Implementation
   ```

**Tests** (`tests/cli/test_task_commands.py`):
- [ ] `clauxton task add` creates task
- [ ] `clauxton task list` shows tasks
- [ ] `clauxton task get` retrieves task
- [ ] `clauxton task update` modifies task
- [ ] `clauxton task delete` removes task
- [ ] Error handling (task not found, etc.)

**Time**: 4 days
**Deliverable**: Complete task CLI commands

**Week 4 Success Criteria**:
- [ ] TaskManager CRUD operations work
- [ ] All task CLI commands functional
- [ ] Tasks persist to `tasks.yml`
- [ ] Tests pass (>80% coverage)

---

## Week 5-6: Dependency Analysis & Auto-inference

**Goal**: Infer task dependencies from file changes

### Day 29-31: File Change Detection

**File**: `clauxton/core/dependency_analyzer.py`

**Tasks**:
1. **Implement GitDiffAnalyzer**:
   ```python
   class GitDiffAnalyzer:
       def __init__(self, repo_path: Path):
           self.repo = git.Repo(repo_path)

       def get_changed_files(self, task_id: str) -> List[str]:
           """Get files changed for a task (from git diff)."""

       def detect_file_overlap(self, task1_files: List[str], task2_files: List[str]) -> bool:
           """Check if two tasks touch the same files."""
   ```

2. **Implement DependencyInferrer**:
   ```python
   class DependencyInferrer:
       def __init__(self, task_manager: TaskManager, git_analyzer: GitDiffAnalyzer):
           self.task_manager = task_manager
           self.git_analyzer = git_analyzer

       def infer_dependencies(self, task_id: str) -> List[str]:
           """Infer task dependencies based on file overlap."""
           task = self.task_manager.get(task_id)
           task_files = set(task.files_to_edit)

           dependencies = []
           for other_task in self.task_manager.list_all():
               if other_task.id == task_id:
                   continue
               other_files = set(other_task.files_to_edit)
               if task_files & other_files:  # Intersection
                   dependencies.append(other_task.id)

           return dependencies

       def validate_dag(self, tasks: List[Task]) -> bool:
           """Validate that task dependencies form a DAG (no cycles)."""
           # Topological sort algorithm
   ```

**Tests** (`tests/core/test_dependency_analyzer.py`):
- [ ] Detects file changes from git
- [ ] Identifies file overlap between tasks
- [ ] Infers dependencies correctly
- [ ] Detects circular dependencies
- [ ] Validates DAG structure

**Time**: 3 days
**Deliverable**: Dependency inference from file analysis

---

### Day 32-35: Task Dependency CLI & MCP Tools

**Tasks**:
1. **Add dependency commands**:
   ```bash
   clauxton task deps <task_id>          # Show dependencies
   clauxton task deps <task_id> --infer  # Auto-infer and update
   clauxton task graph                   # Show task dependency graph
   ```

2. **Add MCP tools for tasks**:
   ```python
   @app.tool()
   async def task_add(name: str, description: str, files_to_edit: List[str]):
       """Add task with auto-dependency inference."""

   @app.tool()
   async def task_next():
       """Get next task to work on (topologically sorted)."""

   @app.tool()
   async def task_graph():
       """Get task dependency graph."""
   ```

3. **Implement task visualization**:
   ```python
   def render_task_graph(tasks: List[Task]) -> str:
       """Render task graph as ASCII or Mermaid diagram."""
       # Example output:
       # TASK-001 (pending)
       #   └── TASK-002 (pending)
       #         └── TASK-003 (completed)
   ```

**Tests**:
- [ ] `clauxton task deps` shows dependencies
- [ ] `clauxton task deps --infer` infers correctly
- [ ] `clauxton task graph` renders correctly
- [ ] MCP tools work with Claude Code
- [ ] Circular dependency detection works

**Time**: 4 days
**Deliverable**: Task dependency management with auto-inference

**Week 5-6 Success Criteria**:
- [ ] Auto-infers dependencies from file changes
- [ ] Detects circular dependencies
- [ ] Suggests next task to work on
- [ ] Visualizes task graph
- [ ] MCP tools for task management work

---

## Week 7: Knowledge Base Enhancements

**Goal**: Add update/delete, improve search

### Day 36-38: Update & Delete Commands

**Tasks**:
1. **Implement `clauxton kb update`**:
   ```python
   @kb.command()
   @click.argument("entry_id")
   @click.option("--title", help="New title")
   @click.option("--content", help="New content")
   @click.option("--tags", help="New tags (comma-separated)")
   def update(entry_id: str, **kwargs):
       """Update KB entry."""
       kb = KnowledgeBase(Path.cwd())
       updates = {k: v for k, v in kwargs.items() if v is not None}
       kb.update(entry_id, updates)
       click.echo(f"✓ Updated entry: {entry_id}")
   ```

2. **Implement `clauxton kb delete`**:
   ```python
   @kb.command()
   @click.argument("entry_id")
   @click.confirmation_option(prompt="Are you sure?")
   def delete(entry_id: str):
       """Delete KB entry."""
       kb = KnowledgeBase(Path.cwd())
       kb.delete(entry_id)
       click.echo(f"✓ Deleted entry: {entry_id}")
   ```

3. **Add MCP tools**:
   ```python
   @app.tool()
   async def kb_update(entry_id: str, title: Optional[str] = None, content: Optional[str] = None):
       """Update KB entry."""

   @app.tool()
   async def kb_delete(entry_id: str):
       """Delete KB entry."""
   ```

**Tests**:
- [ ] Update command works
- [ ] Delete command works
- [ ] Version increments on update
- [ ] MCP tools work

**Time**: 3 days
**Deliverable**: Update/delete functionality for KB

---

### Day 39-42: Enhanced Search (TF-IDF)

**File**: `clauxton/core/search_engine.py`

**Tasks**:
1. **Implement TF-IDF search**:
   ```python
   from sklearn.feature_extraction.text import TfidfVectorizer
   from sklearn.metrics.pairwise import cosine_similarity

   class SearchEngine:
       def __init__(self, entries: List[KnowledgeBaseEntry]):
           self.entries = entries
           self.vectorizer = TfidfVectorizer()
           self.tfidf_matrix = None
           self._build_index()

       def _build_index(self):
           """Build TF-IDF index from all entries."""
           corpus = [f"{e.title} {e.content} {' '.join(e.tags)}" for e in self.entries]
           self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

       def search(self, query: str, limit: int = 10) -> List[Tuple[KnowledgeBaseEntry, float]]:
           """Search with TF-IDF scoring."""
           query_vec = self.vectorizer.transform([query])
           scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

           # Get top results
           top_indices = scores.argsort()[-limit:][::-1]
           return [(self.entries[i], scores[i]) for i in top_indices if scores[i] > 0]
   ```

2. **Integrate with KnowledgeBase**:
   ```python
   class KnowledgeBase:
       def search_tfidf(self, query: str, limit: int = 10) -> List[KnowledgeBaseEntry]:
           """Search using TF-IDF (better relevance than keyword matching)."""
           entries = self._load_entries()
           search_engine = SearchEngine(entries)
           results = search_engine.search(query, limit)
           return [entry for entry, score in results]
   ```

3. **Update CLI to use TF-IDF**:
   ```python
   @kb.command()
   @click.argument("query")
   @click.option("--method", type=click.Choice(["keyword", "tfidf"]), default="tfidf")
   def search(query: str, method: str, ...):
       """Search with improved algorithm."""
       if method == "tfidf":
           results = kb.search_tfidf(query, ...)
       else:
           results = kb.search(query, ...)
   ```

**Tests**:
- [ ] TF-IDF search returns relevant results
- [ ] Better than keyword search for complex queries
- [ ] Performance is acceptable (<1s for 100 entries)

**Optional**: If scikit-learn is too heavy, implement simpler ranking:
- BM25 algorithm
- Custom relevance scoring with term frequency

**Time**: 4 days
**Deliverable**: Improved search with TF-IDF or BM25

**Week 7 Success Criteria**:
- [ ] KB update/delete commands work
- [ ] Search relevance improved
- [ ] MCP tools updated
- [ ] Tests pass

---

## Week 8: Integration, Testing & Documentation

**Goal**: Polish, test, document

### Day 43-45: Integration Testing

**Tasks**:
1. **End-to-end workflow tests**:
   ```python
   def test_task_workflow():
       # Add task
       # Infer dependencies
       # Update task status
       # Get next task
       # Verify DAG
   ```

2. **MCP Server integration tests**:
   - Test all tools work together
   - Test error handling
   - Test concurrent access

3. **Performance testing**:
   - 100 KB entries search performance
   - 50 tasks dependency inference
   - MCP tool response time

**Tests**:
- [ ] Complete user workflows (20+ scenarios)
- [ ] MCP Server stress testing
- [ ] Performance benchmarks

**Time**: 3 days
**Deliverable**: Comprehensive integration test suite

---

### Day 46-49: Documentation & Polish

**Tasks**:
1. **Update user documentation**:
   - Update `docs/quick-start.md` with task commands
   - Create `docs/task-management.md`
   - Create `docs/mcp-server.md`
   - Update README with Phase 1 features

2. **Create video/GIF demos** (optional):
   - Using MCP tools in Claude Code
   - Task dependency visualization

3. **Code cleanup**:
   - Remove dead code
   - Improve error messages
   - Add docstrings
   - Format with ruff

4. **Final testing**:
   - Manual testing with real projects
   - Bug fixes
   - Performance optimization

**Deliverables**:
- [ ] Complete user documentation
- [ ] API reference documentation
- [ ] Changelog for v0.2.0
- [ ] Migration guide (if needed)

**Time**: 4 days
**Deliverable**: Polished Phase 1 release

---

## Phase 1 Success Criteria

### Functional Requirements
- [ ] MCP Server with 6+ working tools (kb-*, task-*)
- [ ] Task CRUD operations (add, get, update, delete, list)
- [ ] Auto-dependency inference from file analysis
- [ ] DAG validation (no circular dependencies)
- [ ] Enhanced search (TF-IDF or BM25)
- [ ] KB update/delete functionality

### Quality Requirements
- [ ] 150+ tests passing (111 existing + 40+ new)
- [ ] >85% code coverage
- [ ] Type checking passes (mypy --strict)
- [ ] Linting passes (ruff)
- [ ] Performance benchmarks met:
  - Search 100 entries: <1s
  - Infer dependencies (50 tasks): <2s
  - MCP tool response: <500ms

### Documentation Requirements
- [ ] Quick Start updated
- [ ] Task Management guide
- [ ] MCP Server guide
- [ ] API reference
- [ ] Changelog

### User Acceptance Criteria
- [ ] User can manage tasks via CLI
- [ ] User can use MCP tools in Claude Code
- [ ] Dependencies are auto-inferred correctly
- [ ] Search returns relevant results
- [ ] No data loss (atomic writes, backups)

---

## Phase 1 Deliverables Summary

**Code**:
- `clauxton/mcp/kb_server.py` - MCP Server with tools
- `clauxton/core/task_manager.py` - Task CRUD
- `clauxton/core/dependency_analyzer.py` - Dependency inference
- `clauxton/core/search_engine.py` - Enhanced search
- `clauxton/cli/main.py` - Updated CLI with task commands

**Tests**:
- `tests/mcp/` - MCP Server tests
- `tests/core/test_task_manager.py` - Task tests
- `tests/core/test_dependency_analyzer.py` - Dependency tests
- `tests/cli/test_task_commands.py` - Task CLI tests
- `tests/integration/test_phase1.py` - Phase 1 integration tests

**Documentation**:
- `docs/task-management.md` - Task management guide
- `docs/mcp-server.md` - MCP Server setup & usage
- `docs/quick-start.md` - Updated with Phase 1 features
- `CHANGELOG.md` - Version 0.2.0 release notes

---

## Risk Mitigation

### Technical Risks

**Risk 1**: MCP SDK not available or unstable
- **Mitigation**: Research SDK early (Day 15), have fallback plan to implement MCP protocol manually
- **Contingency**: Use simpler RPC mechanism if MCP is too complex

**Risk 2**: Dependency inference too slow or inaccurate
- **Mitigation**: Start with simple file overlap detection, add complexity gradually
- **Contingency**: Make auto-inference optional, allow manual dependency specification

**Risk 3**: TF-IDF adds too much complexity/dependencies
- **Mitigation**: Make it optional (scikit-learn as optional dependency)
- **Contingency**: Use simpler BM25 or weighted keyword matching

### Schedule Risks

**Risk**: 6 weeks is tight for all features
- **Mitigation**: Prioritize MCP Server (Week 3) and Task CRUD (Week 4) - these are must-haves
- **Contingency**: Move enhanced search to Phase 1.5 if needed
- **Buffer**: Week 8 has 7 days for polish/overflow

---

## Next Steps After Phase 1

Phase 1 completion enables Phase 2: Conflict Prevention
- Pre-merge conflict detection
- Risk scoring
- Safe execution order
- Drift detection

Estimated Phase 2 timeline: 4 weeks (Week 9-12)

---

## Questions to Resolve Before Starting

1. **MCP SDK**: Which MCP Python SDK should we use? (Research needed)
2. **Task Persistence**: YAML vs SQLite for tasks? (YAML for consistency with KB)
3. **Dependency Algorithm**: File overlap only, or also analyze import statements?
4. **Search Enhancement**: TF-IDF (needs scikit-learn) vs BM25 (pure Python)?
5. **Testing Strategy**: Mock git operations or use real test repositories?

---

**Last Updated**: 2025-10-19
**Next Review**: After Week 3 (MCP Server completion)
