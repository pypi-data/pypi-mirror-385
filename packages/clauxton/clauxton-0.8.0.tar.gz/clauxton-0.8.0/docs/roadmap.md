# Clauxton Development Roadmap

**Version**: 1.0
**Last Updated**: 2025-10-19
**Project**: Clauxton - Context that persists for Claude Code

---

## Overview

This roadmap outlines the development plan for Clauxton from Phase 0 (Foundation) through Phase 2 (Conflict Prevention), spanning approximately **16 weeks** (4 months).

---

## Timeline Summary

```
Phase 0: Foundation          [Week 1-2]  ██████████░░░░░░░░░░░░░░░░░░░░░░
Phase 1: Core Engine         [Week 3-8]  ░░░░░░░░░░██████████████████░░░░
Phase 2: Conflict Prevention [Week 9-12] ░░░░░░░░░░░░░░░░░░░░░░░░██████░░
Beta Testing                 [Week 13-14]░░░░░░░░░░░░░░░░░░░░░░░░░░░░████
Public Launch                [Week 15-16]░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
```

---

## Phase 0: Foundation (Week 1-2)

**Goal**: Establish basic project structure and Knowledge Base functionality

### Week 1: Project Setup & Data Models

#### Day 1-2: Core Data Models
- [x] Project structure initialization
- [x] Basic package files (`__init__.py`, `pyproject.toml`, etc.)
- [ ] **Pydantic models** (`clauxton/core/models.py`):
  ```python
  - KnowledgeBaseEntry
  - KnowledgeBaseConfig
  - ValidationError handlers
  ```

#### Day 3-4: Knowledge Base Core
- [ ] **Knowledge Base manager** (`clauxton/core/knowledge_base.py`):
  ```python
  class KnowledgeBase:
      def add(entry: KnowledgeBaseEntry) -> str
      def search(query: str, category: str, tags: list) -> List[KnowledgeBaseEntry]
      def get(entry_id: str) -> KnowledgeBaseEntry
      def _save_to_yaml() -> None
      def _load_from_yaml() -> None
  ```

#### Day 5-7: File I/O & Validation
- [ ] **YAML utilities** (`clauxton/utils/yaml_utils.py`):
  - Safe YAML read/write with atomic operations
  - Schema validation
  - Backup on write
- [ ] **File utilities** (`clauxton/utils/file_utils.py`):
  - `.clauxton/` directory management
  - File permissions (700/600)
- [ ] **Unit tests** (`tests/core/test_knowledge_base.py`):
  - Add entry (valid/invalid)
  - Search functionality
  - YAML persistence

**Deliverables**:
- ✅ Pydantic data models with validation
- ✅ Knowledge Base CRUD operations
- ✅ YAML read/write with validation
- ✅ Unit tests (>70% coverage)

---

### Week 2: CLI & Plugin Integration

#### Day 8-10: CLI Implementation
- [ ] **CLI framework** (`clauxton/cli/main.py`):
  ```bash
  clauxton init              # Initialize .clauxton/ directory
  clauxton kb add            # Add KB entry (interactive)
  clauxton kb search <query> # Search KB
  clauxton kb list           # List all entries
  ```
- [ ] **Interactive prompts** (using Click):
  - Category selection
  - Tag input
  - Content editor (multi-line)

#### Day 11-12: Claude Code Plugin Manifest
- [ ] **Plugin manifest** (`.claude-plugin/plugin.json`):
  ```json
  {
    "commands": [],
    "mcp_servers": [
      {
        "name": "clauxton-kb",
        "command": "python -m clauxton.mcp.kb_server"
      }
    ]
  }
  ```
- [ ] **Basic MCP Server** (`clauxton/mcp/kb_server.py`):
  - Server initialization
  - Health check endpoint
  - Basic tool registration

#### Day 13-14: Testing & Documentation
- [ ] **Integration tests**:
  - CLI → Knowledge Base interaction
  - YAML file creation/modification
- [ ] **Documentation**:
  - `docs/quick-start.md`
  - `docs/installation.md`
  - README examples update
- [ ] **Manual testing**:
  - Install package locally (`pip install -e .`)
  - Run `clauxton init`
  - Add/search KB entries

**Deliverables**:
- ✅ `clauxton init` command functional
- ✅ `clauxton kb add/search` commands functional
- ✅ Basic MCP Server (no tools yet)
- ✅ Integration tests passing
- ✅ User documentation complete

**Success Criteria**:
- [ ] User can install Clauxton locally
- [ ] User can run `clauxton init` to create `.clauxton/`
- [ ] User can add KB entries via CLI
- [ ] User can search KB entries
- [ ] `.clauxton/knowledge-base.yml` is valid YAML
- [ ] Unit + integration tests >70% coverage

---

## Phase 1: Core Engine (Week 3-8)

**Goal**: Implement Task Management, Dependency Analysis, and MCP Server integration

### Week 3-4: Task Management Foundation

#### Task Data Models
- [ ] **Task model** (`clauxton/core/models.py`):
  ```python
  class Task(BaseModel):
      id: str  # TASK-001, TASK-002, ...
      name: str
      status: Literal["pending", "in_progress", "completed", "blocked"]
      priority: Literal["low", "medium", "high", "critical"]
      depends_on: List[str]  # Task IDs
      estimated_hours: Optional[float]
      files_to_edit: List[str]
      related_kb: List[str]
      created_at: datetime
      # ... (see requirements.md)
  ```

#### Task Manager Core
- [ ] **Task Manager** (`clauxton/core/task_manager.py`):
  ```python
  class TaskManager:
      def create_task(task: Task) -> str
      def get_task(task_id: str) -> Task
      def get_next_tasks(priority: str, limit: int) -> List[Task]
      def start_task(task_id: str) -> Task
      def complete_task(task_id: str) -> Task
      def _validate_dag(new_task: Task) -> None  # Cycle detection
  ```

#### DAG Utilities
- [ ] **DAG algorithms** (`clauxton/utils/dag_utils.py`):
  ```python
  def topological_sort(tasks: List[Task]) -> List[str]
  def detect_cycle(tasks: List[Task]) -> Optional[List[str]]
  def find_critical_path(tasks: List[Task]) -> List[str]
  ```

**Deliverables**:
- ✅ Task CRUD operations
- ✅ DAG validation (circular dependency detection)
- ✅ Next task recommendations
- ✅ Unit tests for Task Manager
- ✅ `clauxton task add/list/next` CLI commands

---

### Week 5-6: Dependency Analyzer

#### Static Analysis
- [ ] **Dependency Analyzer** (`clauxton/core/dependency_analyzer.py`):
  ```python
  class DependencyAnalyzer:
      def infer_from_file_edit(file_path: str, current_task_id: str) -> List[DependencyInference]
      def _extract_imports(file_path: str) -> List[str]  # AST
      def _find_tasks_editing_file(file_path: str) -> List[Task]
      def _match_kb_patterns() -> List[DependencyInference]
  ```

#### Pattern Matching
- [ ] **Pattern-based inference**:
  - Same file edit → dependency candidate
  - Import analysis → code dependency
  - KB pattern matching (e.g., "tests after implementation")

**Deliverables**:
- ✅ Dependency inference from code edits
- ✅ AST-based import analysis (Python support)
- ✅ Pattern matching from KB
- ✅ Confidence scoring (0.0-1.0)
- ✅ Unit tests for inference accuracy

---

### Week 7-8: MCP Server & Subagents

#### MCP Server Implementation
- [ ] **KB MCP Server** (`clauxton/mcp/kb_server.py`):
  ```python
  @app.list_tools()
  async def list_tools() -> List[Tool]:
      return [
          Tool(name="kb_search", ...),
          Tool(name="kb_add", ...)
      ]

  @app.call_tool()
  async def call_tool(name: str, arguments: dict):
      # Implement kb_search, kb_add
  ```

- [ ] **Task MCP Server** (`clauxton/mcp/task_server.py`):
  ```python
  Tools: task_create, task_start, task_complete, task_next
  ```

#### Subagent Definitions
- [ ] **Dependency Analyzer Subagent** (`agents/dependency-analyzer.md`):
  ```markdown
  # Dependency Analyzer Subagent

  You are a specialized subagent for analyzing task dependencies.

  ## Input
  - tasks.yml
  - Codebase path
  - KB patterns

  ## Output
  JSON array of inferred dependencies with confidence scores
  ```

#### Slash Commands
- [ ] **Slash commands** (`commands/`):
  - `kb-search.md` → `/kb-search <query>`
  - `kb-add.md` → `/kb-add`
  - `task-next.md` → `/task-next`
  - `task-start.md` → `/task-start <id>`
  - `deps-graph.md` → `/deps-graph`

**Deliverables**:
- ✅ MCP KB Server with kb_search, kb_add tools
- ✅ MCP Task Server with task_* tools
- ✅ Dependency Analyzer Subagent definition
- ✅ All slash commands functional in Claude Code
- ✅ Integration tests for MCP servers

**Success Criteria (Phase 1)**:
- [ ] User can create tasks via `/task-add`
- [ ] User can see next tasks via `/task-next`
- [ ] Dependencies are auto-inferred (>70% accuracy)
- [ ] `/deps-graph` displays task DAG
- [ ] Circular dependencies are detected and rejected
- [ ] Unit + integration tests >80% coverage

---

## Phase 2: Conflict Prevention (Week 9-12)

**Goal**: Implement pre-merge conflict detection and drift detection

### Week 9-10: Conflict Detector

#### Conflict Detection Core
- [ ] **Conflict Detector** (`clauxton/core/conflict_detector.py`):
  ```python
  class ConflictDetector:
      def detect_conflicts(task_ids: List[str]) -> List[ConflictRisk]
      def _analyze_pair(task1: Task, task2: Task) -> ConflictRisk
      def _estimate_line_overlap(file: str, tasks: List[Task]) -> float
      def suggest_execution_order(task_ids: List[str]) -> List[str]
  ```

#### Risk Scoring
- [ ] **Risk calculation**:
  - File overlap detection
  - Line-level overlap estimation (basic heuristic)
  - Historical conflict analysis (from event log)
  - Risk score: 0.0-1.0 (Low/Medium/High)

**Deliverables**:
- ✅ Conflict detection for task pairs
- ✅ Risk scoring algorithm
- ✅ Safe execution order recommendations
- ✅ `/conflicts-check` slash command
- ✅ Unit tests for conflict detection

---

### Week 11-12: Drift Detection & Hooks

#### Drift Detection
- [ ] **Drift tracking**:
  - Expected state vs actual state comparison
  - Detect unexpected file edits
  - Detect scope expansion
  - Suggest task splitting

#### Lifecycle Hooks
- [ ] **Hooks** (`hooks/`):
  - `post-edit-update-kb.sh` → Update KB after Edit tool
  - `pre-task-start.sh` → Conflict check before task start
  - `post-commit.sh` → Auto-update task status on git commit

#### Event Logging
- [ ] **Event Logger** (`clauxton/core/event_logger.py`):
  ```python
  class EventLogger:
      def log(event_type: str, data: dict) -> None
      def get_events(event_type: str, limit: int) -> List[Event]
  ```
- [ ] Event types: `kb_added`, `task_started`, `file_edited`, `conflict_detected`

**Deliverables**:
- ✅ Drift detection functional
- ✅ Lifecycle hooks implemented
- ✅ Event logging (JSON Lines format)
- ✅ Conflict Detector Subagent definition
- ✅ `/conflicts-check` with drift warnings

**Success Criteria (Phase 2)**:
- [ ] Conflict detection accuracy >80%
- [ ] False positive rate <15%
- [ ] Hooks trigger automatically on file edits
- [ ] Drift warnings appear when scope expands
- [ ] Event log captures all major actions
- [ ] Unit + integration tests >80% coverage

---

## Beta Testing (Week 13-14)

### Week 13: Internal Testing
- [ ] **Bug fixes**:
  - Address critical bugs from Phase 0-2
  - Performance optimization
  - Error handling improvements

- [ ] **Documentation**:
  - Complete API reference (`docs/api-reference.md`)
  - Architecture diagram updates
  - Tutorial videos (optional)

### Week 14: External Beta
- [ ] **Beta tester recruitment**:
  - Claude Code Discord announcement
  - Personal network outreach
  - Twitter/X announcement

- [ ] **Feedback collection**:
  - User interviews (3-5 beta testers)
  - Bug reports via GitHub Issues
  - Feature requests

**Success Criteria**:
- [ ] 20-50 beta testers recruited
- [ ] 10+ pieces of actionable feedback
- [ ] Critical bugs fixed
- [ ] Documentation complete

---

## Public Launch (Week 15-16)

### Week 15: Launch Preparation
- [ ] **Final polish**:
  - All documentation reviewed
  - All tests passing (>80% coverage)
  - Performance benchmarks met

- [ ] **Marketing materials**:
  - Demo video (2-3 minutes)
  - Blog post / launch announcement
  - Social media posts

### Week 16: Launch Week
- [ ] **Launch activities**:
  - **Day 1**: Product Hunt launch (9am PST)
  - **Day 1**: HackerNews Show HN post
  - **Day 1**: Reddit r/ClaudeAI, r/programming posts
  - **Day 2-3**: Twitter/X thread with demo
  - **Day 2-3**: Dev.to technical article
  - **Day 4-7**: Community engagement & support

- [ ] **Post-launch**:
  - GitHub release (v0.1.0 → PyPI)
  - Claude Code Plugin Marketplace submission
  - Monitor user feedback & bug reports

**Success Criteria**:
- [ ] PyPI package published
- [ ] 100+ GitHub stars in first week
- [ ] 50+ active users
- [ ] <5 critical bugs reported

---

## Post-Launch (Week 17+)

### Maintenance & Iteration
- [ ] Weekly bug fixes
- [ ] Monthly feature releases
- [ ] User feedback prioritization
- [ ] Community building (Discord, GitHub Discussions)

### Future Phases (Phase 3+)
- **Team Features** (Q2 2025):
  - Shared Knowledge Base (PostgreSQL)
  - Team task assignment
  - Real-time collaboration

- **AI Learning** (Q3 2025):
  - Dependency inference accuracy improvement
  - Project-specific pattern extraction
  - Conflict prediction ML model

- **Integrations** (Q4 2025):
  - Cursor, Windsurf support
  - GitHub Issues/PRs sync
  - Jira/Linear integration

---

## Success Metrics

### Technical Metrics
| Metric | Phase 0 Target | Phase 1 Target | Phase 2 Target |
|--------|----------------|----------------|----------------|
| Test Coverage | >70% | >80% | >80% |
| KB Search Latency | <1s | <1s | <1s |
| Dependency Inference Accuracy | N/A | >70% | >75% |
| Conflict Prediction Accuracy | N/A | N/A | >80% |
| False Positive Rate | N/A | N/A | <15% |

### User Metrics
| Metric | Beta (Week 13-14) | Launch (Week 15-16) | Month 1 |
|--------|-------------------|---------------------|---------|
| Active Users | 20-50 | 100+ | 500+ |
| GitHub Stars | N/A | 200+ | 500+ |
| PyPI Downloads | N/A | 500+ | 2000+ |
| Retention (30-day) | N/A | >50% | >60% |

---

## Risk Management

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| MCP spec changes | Medium | High | Monitor Anthropic Discord, early adoption feedback |
| Dependency inference low accuracy | High | Medium | Provide manual override UI, iterate on algorithm |
| Conflict detection false positives | Medium | Medium | Conservative thresholds, user feedback loop |

### Market Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Competing plugin launches | Medium | Medium | Focus on unique features (conflict detection) |
| Claude Code API instability | Low | High | Fallback to CLI-only mode |
| Low user adoption | Medium | High | Community building, content marketing |

---

## Team & Resources

### Development
- **Primary Developer**: 1 full-time (16 weeks)
- **AI Assistance**: Claude Code (30-40% productivity boost)

### Tools & Infrastructure
- **Development**: VSCode + Claude Code, pytest, mypy
- **CI/CD**: GitHub Actions (free tier)
- **Distribution**: PyPI (free), GitHub (free)
- **Documentation**: Markdown + GitHub Pages (free)

**Total Budget**: $0-12 (domain only, optional)

---

## Next Steps

### Immediate (This Week)
1. [ ] Review and approve this roadmap
2. [ ] Begin Phase 0, Week 1, Day 1-2 (Pydantic models)
3. [ ] Setup development environment (venv, dependencies)

### This Month
- Complete Phase 0 (Week 1-2)
- Begin Phase 1 (Week 3-4)
- First internal dogfooding session

---

## Appendix

### Key Documents
- `docs/project-plan.md` - Market analysis, business strategy
- `docs/requirements.md` - Functional & non-functional requirements
- `docs/technical-design.md` - Architecture & implementation details
- `docs/roadmap.md` - **This document**

### Communication
- **Weekly Progress Updates**: To be documented in `CHANGELOG.md`
- **Blockers**: Flagged immediately in todo list
- **Decisions**: Recorded in `docs/decisions/` (ADR format)

---

**Document Status**: ✅ Ready for Phase 0 implementation
**Last Review**: 2025-10-19
**Next Review**: After Phase 0 completion (Week 2)
