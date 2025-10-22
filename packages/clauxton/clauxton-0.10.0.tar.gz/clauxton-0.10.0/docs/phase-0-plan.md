# Phase 0 Implementation Plan: Foundation

**Duration**: Week 1-2 (14 days)
**Goal**: Establish basic project structure and Knowledge Base functionality
**Status**: Ready to Start

---

## Overview

Phase 0 establishes the foundation for Clauxton by implementing:
1. **Core data models** (Pydantic)
2. **Knowledge Base CRUD** operations
3. **CLI interface** (`clauxton init`, `clauxton kb`)
4. **Basic MCP Server** (no tools yet, just infrastructure)
5. **Unit & integration tests**

---

## Week 1: Core Implementation

### Day 1-2: Pydantic Data Models ✅

**File**: `clauxton/core/models.py`

**Tasks**:
1. [ ] Create `KnowledgeBaseEntry` model:
   ```python
   class KnowledgeBaseEntry(BaseModel):
       id: str = Field(..., pattern=r"KB-\d{8}-\d{3}")
       title: str = Field(..., max_length=50)
       category: Literal["architecture", "constraint", "decision", "pattern", "convention"]
       content: str = Field(..., max_length=10000)
       tags: List[str] = Field(default_factory=list)
       created_at: datetime
       updated_at: datetime
       author: Optional[str] = None
       version: int = 1

       @validator("content")
       def sanitize_content(cls, v):
           return v.strip()
   ```

2. [ ] Create `KnowledgeBaseConfig` model:
   ```python
   class KnowledgeBaseConfig(BaseModel):
       version: str = "1.0"
       project_name: str
       project_description: Optional[str] = None
   ```

3. [ ] Create custom exceptions:
   ```python
   class ClauxtonError(Exception):
       """Base exception for Clauxton."""

   class ValidationError(ClauxtonError):
       """Raised when data validation fails."""

   class NotFoundError(ClauxtonError):
       """Raised when entity is not found."""
   ```

**Tests** (`tests/core/test_models.py`):
- [ ] Valid entry creation
- [ ] Invalid entry (title too long, invalid category, etc.)
- [ ] Content sanitization
- [ ] JSON serialization/deserialization

**Time**: 2 days
**Dependencies**: None
**Acceptance Criteria**:
- All model tests pass
- Type checking with mypy passes
- Models can serialize to/from JSON

---

### Day 3-4: YAML Utilities ✅

**File**: `clauxton/utils/yaml_utils.py`

**Tasks**:
1. [ ] Implement safe YAML read:
   ```python
   def read_yaml(file_path: Path) -> dict:
       """
       Read YAML file safely.

       Returns empty dict if file doesn't exist.
       Raises ValidationError if YAML is malformed.
       """
   ```

2. [ ] Implement atomic YAML write:
   ```python
   def write_yaml(file_path: Path, data: dict, backup: bool = True) -> None:
       """
       Write YAML file atomically (write to temp, then rename).

       If backup=True, creates .bak file before overwriting.
       """
   ```

3. [ ] Implement schema validation:
   ```python
   def validate_kb_yaml(data: dict) -> bool:
       """Validate Knowledge Base YAML structure."""
   ```

**File**: `clauxton/utils/file_utils.py`

**Tasks**:
1. [ ] Implement `.clauxton/` directory management:
   ```python
   def ensure_clauxton_dir(root_dir: Path) -> Path:
       """
       Create .clauxton/ directory with proper permissions.

       Sets permissions: 700 (drwx------)
       Returns path to .clauxton/
       """
   ```

2. [ ] Implement file permission setting:
   ```python
   def set_secure_permissions(file_path: Path) -> None:
       """Set file permissions to 600 (rw-------)."""
   ```

**Tests**:
- [ ] YAML read (valid, invalid, missing file)
- [ ] YAML write (atomic, backup creation)
- [ ] Directory creation with permissions
- [ ] File permission setting

**Time**: 2 days
**Dependencies**: Day 1-2 (models)
**Acceptance Criteria**:
- YAML read/write is atomic (no data loss on crash)
- Backup files are created
- Permissions are correctly set (700/600)

---

### Day 5-7: Knowledge Base Core ✅

**File**: `clauxton/core/knowledge_base.py`

**Tasks**:
1. [ ] Implement `KnowledgeBase` class:
   ```python
   class KnowledgeBase:
       """
       Knowledge Base manager.

       Handles CRUD operations for project-specific context.
       Uses YAML for human-readable storage.
       """

       def __init__(self, root_dir: Path):
           self.root_dir = root_dir
           self.kb_file = root_dir / ".clauxton" / "knowledge-base.yml"
           self._ensure_kb_exists()
           self._entries_cache: Optional[List[KnowledgeBaseEntry]] = None

       def add(self, entry: KnowledgeBaseEntry) -> str:
           """Add new entry. Returns entry ID."""

       def get(self, entry_id: str) -> KnowledgeBaseEntry:
           """Get entry by ID. Raises NotFoundError if not found."""

       def search(
           self,
           query: str,
           category: Optional[str] = None,
           tags: Optional[List[str]] = None,
           limit: int = 10
       ) -> List[KnowledgeBaseEntry]:
           """
           Search Knowledge Base.

           Uses simple keyword matching (case-insensitive).
           Future: TF-IDF or vector search.
           """

       def update(self, entry_id: str, updates: dict) -> KnowledgeBaseEntry:
           """Update entry. Creates new version."""

       def delete(self, entry_id: str, reason: Optional[str] = None) -> None:
           """Soft delete entry (sets deleted flag)."""

       def list_all(self, include_deleted: bool = False) -> List[KnowledgeBaseEntry]:
           """List all entries."""

       def _load_entries(self) -> List[KnowledgeBaseEntry]:
           """Load entries from YAML."""

       def _save_entries(self, entries: List[KnowledgeBaseEntry]) -> None:
           """Save entries to YAML."""

       def _ensure_kb_exists(self) -> None:
           """Create KB file if it doesn't exist."""

       def _generate_id(self) -> str:
           """Generate unique KB ID (KB-YYYYMMDD-NNN)."""

       def _invalidate_cache(self) -> None:
           """Invalidate entries cache."""
   ```

2. [ ] Implement search algorithm:
   - Keyword matching in title/content/tags
   - Category filtering
   - Tag filtering
   - Relevance scoring (simple: count of keyword matches)
   - Sort by relevance

**Tests** (`tests/core/test_knowledge_base.py`):
- [ ] Add entry (valid)
- [ ] Add entry (duplicate ID handling)
- [ ] Get entry (exists, not exists)
- [ ] Search (by keyword, by category, by tags)
- [ ] Update entry (versioning)
- [ ] Delete entry (soft delete)
- [ ] List all entries
- [ ] YAML persistence (add → restart → verify)

**Time**: 3 days
**Dependencies**: Day 1-4 (models, utils)
**Acceptance Criteria**:
- All CRUD operations functional
- Search returns relevant results
- YAML file is valid and human-readable
- Test coverage >80%

---

## Week 2: CLI & Integration

### Day 8-10: CLI Implementation ✅

**File**: `clauxton/cli/main.py`

**Tasks**:
1. [ ] Setup Click CLI framework:
   ```python
   import click

   @click.group()
   @click.version_option(version="0.1.0")
   def cli():
       """Clauxton - Context that persists for Claude Code."""
       pass

   if __name__ == "__main__":
       cli()
   ```

2. [ ] Implement `clauxton init`:
   ```python
   @cli.command()
   @click.option("--project-name", prompt=True, help="Project name")
   @click.option("--description", default="", help="Project description")
   def init(project_name: str, description: str):
       """Initialize Clauxton in current directory."""
       # 1. Check if .clauxton/ already exists
       # 2. Create .clauxton/ directory
       # 3. Create knowledge-base.yml with config
       # 4. Create config.yml
       # 5. Print success message with next steps
   ```

3. [ ] Implement `clauxton kb add`:
   ```python
   @cli.group()
   def kb():
       """Knowledge Base commands."""
       pass

   @kb.command()
   @click.option("--title", prompt=True, help="Entry title")
   @click.option("--category", type=click.Choice(...), prompt=True)
   @click.option("--tags", help="Comma-separated tags")
   def add(title: str, category: str, tags: str):
       """Add entry to Knowledge Base."""
       # 1. Prompt for content (multi-line editor)
       # 2. Create KnowledgeBaseEntry
       # 3. Validate
       # 4. Add to KB
       # 5. Print success with entry ID
   ```

4. [ ] Implement `clauxton kb search`:
   ```python
   @kb.command()
   @click.argument("query")
   @click.option("--category", help="Filter by category")
   @click.option("--tags", help="Filter by tags")
   @click.option("--limit", default=10, help="Max results")
   def search(query: str, category: str, tags: str, limit: int):
       """Search Knowledge Base."""
       # 1. Load KB
       # 2. Search with filters
       # 3. Format results (rich table or markdown)
       # 4. Print results
   ```

5. [ ] Implement `clauxton kb list`:
   ```python
   @kb.command()
   @click.option("--category", help="Filter by category")
   def list(category: str):
       """List all KB entries."""
   ```

**File**: `clauxton/cli/kb_commands.py` (optional, for organization)

**Tests** (`tests/cli/test_main.py`):
- [ ] `clauxton --version`
- [ ] `clauxton --help`
- [ ] `clauxton init` (creates .clauxton/)
- [ ] `clauxton kb add` (interactive)
- [ ] `clauxton kb search <query>`
- [ ] `clauxton kb list`

**Time**: 3 days
**Dependencies**: Day 1-7 (models, KB core)
**Acceptance Criteria**:
- All CLI commands functional
- Interactive prompts work correctly
- Output is user-friendly (formatted, colored)
- Error messages are clear

---

### Day 11-12: Basic MCP Server ✅

**File**: `clauxton/mcp/kb_server.py`

**Tasks**:
1. [ ] Research MCP SDK:
   - Check if MCP SDK is available for Python
   - If not, implement minimal MCP protocol manually

2. [ ] Implement basic MCP Server:
   ```python
   from mcp.server import Server

   app = Server("clauxton-kb")

   @app.list_tools()
   async def list_tools():
       """List available tools (empty for Phase 0)."""
       return []

   @app.health_check()
   async def health():
       """Health check endpoint."""
       return {"status": "ok", "version": "0.1.0"}

   if __name__ == "__main__":
       app.run()
   ```

3. [ ] Update plugin manifest:
   ```json
   {
     "mcp_servers": [
       {
         "name": "clauxton-kb",
         "command": "python -m clauxton.mcp.kb_server",
         "description": "Knowledge Base MCP Server"
       }
     ]
   }
   ```

**Tests** (`tests/mcp/test_kb_server.py`):
- [ ] Server starts successfully
- [ ] Health check returns OK
- [ ] list_tools returns empty array

**Time**: 2 days
**Dependencies**: Day 1-10
**Acceptance Criteria**:
- MCP Server can be started
- Health check responds
- No tools implemented yet (Phase 1 task)

---

### Day 13-14: Testing & Documentation ✅

**Tasks**:
1. [ ] **Integration tests** (`tests/integration/test_end_to_end.py`):
   ```python
   def test_complete_workflow(tmp_project):
       """Test complete user workflow."""
       # 1. clauxton init
       # 2. clauxton kb add (3 entries)
       # 3. clauxton kb search
       # 4. Verify .clauxton/knowledge-base.yml
   ```

2. [ ] **Code quality**:
   - [ ] Run mypy (strict mode)
   - [ ] Run ruff (linter)
   - [ ] Check test coverage (>70%)
   - [ ] Fix any issues

3. [ ] **Documentation**:
   - [ ] `docs/quick-start.md`:
     ```markdown
     # Quick Start

     ## Installation
     pip install clauxton

     ## Initialize Project
     cd your-project
     clauxton init

     ## Add Knowledge
     clauxton kb add

     ## Search Knowledge
     clauxton kb search "architecture"
     ```

   - [ ] `docs/installation.md`:
     ```markdown
     # Installation Guide

     ## Requirements
     - Python 3.11+
     - Git (recommended)

     ## Install from PyPI
     pip install clauxton

     ## Install from Source
     git clone https://github.com/nakishiyaman/clauxton.git
     cd clauxton
     pip install -e .
     ```

   - [ ] Update `README.md` with Phase 0 features

4. [ ] **Manual testing**:
   - [ ] Install locally: `pip install -e .`
   - [ ] Run `clauxton init` in test project
   - [ ] Add 5 KB entries
   - [ ] Search KB with various queries
   - [ ] Verify YAML file is human-readable
   - [ ] Check file permissions (700/600)

**Time**: 2 days
**Dependencies**: Day 1-12
**Acceptance Criteria**:
- All tests pass (unit + integration)
- Test coverage >70%
- mypy passes (strict mode)
- ruff passes
- Documentation is complete and accurate
- Manual testing successful

---

## Deliverables Checklist

### Code
- [ ] `clauxton/core/models.py` (Pydantic models)
- [ ] `clauxton/core/knowledge_base.py` (KB manager)
- [ ] `clauxton/utils/yaml_utils.py` (YAML I/O)
- [ ] `clauxton/utils/file_utils.py` (File management)
- [ ] `clauxton/cli/main.py` (CLI framework)
- [ ] `clauxton/mcp/kb_server.py` (Basic MCP Server)

### Tests
- [ ] `tests/core/test_models.py`
- [ ] `tests/core/test_knowledge_base.py`
- [ ] `tests/utils/test_yaml_utils.py`
- [ ] `tests/utils/test_file_utils.py`
- [ ] `tests/cli/test_main.py`
- [ ] `tests/mcp/test_kb_server.py`
- [ ] `tests/integration/test_end_to_end.py`
- [ ] Test coverage >70%

### Documentation
- [ ] `docs/quick-start.md`
- [ ] `docs/installation.md`
- [ ] `README.md` updated with Phase 0 features
- [ ] Code docstrings (Google style)

### Configuration
- [ ] `.claude-plugin/plugin.json` (MCP Server registered)
- [ ] `pyproject.toml` (dependencies updated)

---

## Success Criteria

### Functional
- [ ] User can run `clauxton init` to create `.clauxton/`
- [ ] User can add KB entries via `clauxton kb add`
- [ ] User can search KB via `clauxton kb search <query>`
- [ ] User can list KB entries via `clauxton kb list`
- [ ] `.clauxton/knowledge-base.yml` is valid YAML
- [ ] `.clauxton/knowledge-base.yml` is human-readable

### Technical
- [ ] All tests pass
- [ ] Test coverage >70%
- [ ] mypy passes (strict mode)
- [ ] ruff passes (no warnings)
- [ ] No critical bugs

### User Experience
- [ ] CLI is intuitive and user-friendly
- [ ] Error messages are clear and actionable
- [ ] Interactive prompts work smoothly
- [ ] Output is well-formatted (tables, colors)

---

## Risk Mitigation

### Technical Risks
| Risk | Mitigation |
|------|------------|
| MCP SDK not available for Python | Implement minimal MCP protocol manually; defer full implementation to Phase 1 |
| YAML file corruption | Implement atomic writes with backups; test extensively |
| Slow search on large KB | Optimize search algorithm; add caching (not critical for Phase 0) |

### Schedule Risks
| Risk | Mitigation |
|------|------------|
| Day 1-7 takes longer than expected | Simplify search algorithm (exact match only); defer advanced features to Phase 1 |
| MCP Server implementation blocked | Skip MCP Server for Phase 0; focus on CLI |

---

## Next Steps After Phase 0

1. **Review & Demo**: Internal demo of Phase 0 functionality
2. **Feedback**: Collect feedback from self-testing
3. **Planning**: Review Phase 1 plan, adjust timeline if needed
4. **Start Phase 1**: Begin Week 3 (Task Management Foundation)

---

## Daily Checklist Template

```markdown
### Day X: [Task Name]

**Goal**: [One-sentence goal]

**Tasks**:
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

**Tests**:
- [ ] Unit tests written
- [ ] Tests passing

**Blockers**: None / [Description]

**Notes**: [Any notes or decisions made]

**Time Spent**: X hours

**Status**: ✅ Complete / 🔄 In Progress / ❌ Blocked
```

---

**Phase 0 Status**: 📋 Ready to Begin
**Estimated Completion**: 2025-11-02 (14 days from 2025-10-20)
**Next Action**: Begin Day 1-2 (Pydantic Data Models)
