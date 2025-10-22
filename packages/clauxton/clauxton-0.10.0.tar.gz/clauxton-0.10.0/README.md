# Clauxton

**Context that persists for Claude Code**

[![CI](https://github.com/nakishiyaman/clauxton/workflows/CI/badge.svg)](https://github.com/nakishiyaman/clauxton/actions)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![PyPI Version](https://img.shields.io/pypi/v/clauxton)](https://pypi.org/project/clauxton/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/clauxton)](https://pypi.org/project/clauxton/)
[![Development Status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/nakishiyaman/clauxton)
[![Test Coverage](https://img.shields.io/badge/coverage-70%25-yellow.svg)](https://github.com/nakishiyaman/clauxton)
[![codecov](https://codecov.io/gh/nakishiyaman/clauxton/branch/main/graph/badge.svg)](https://codecov.io/gh/nakishiyaman/clauxton)

> ✅ **Production Ready**: Clauxton v0.9.0-beta is stable and ready for production use. Phase 1-2 complete with TF-IDF search, task management, conflict detection, and MCP integration.
> 🚀 **v0.10.0 Coming Soon** (2025-11-10): Transparent integration with Claude Code - natural conversation only, no manual commands!

Clauxton is a Claude Code plugin that provides **persistent project context** to solve AI-assisted development pain points.

**Vision** (Roadmap):
1. ✅ **Session Context Loss** → Persistent Knowledge Base with TF-IDF Search (Phase 0-1 - **Complete**)
2. ✅ **Manual Dependency Tracking** → Auto-inferred task dependencies (Phase 1 - **Complete**)
3. ✅ **Post-hoc Conflict Detection** → Pre-merge conflict prediction (Phase 2 - **Complete in v0.9.0-beta**)
4. 🚀 **Manual CLI Operations** → Transparent Integration (Phase 3 - **In Progress, v0.10.0**)

---

## 🎯 Quick Start

### Install from PyPI (Recommended)

```bash
# Install Clauxton with all features (TF-IDF search)
pip install clauxton

# Verify installation
clauxton --version  # Should show: clauxton, version 0.9.0-beta
```

### Basic Usage

```bash
# Initialize in your project
cd your-project
clauxton init

# Add knowledge to your Knowledge Base
clauxton kb add
# Enter: Title, Category, Content, Tags

# Search with TF-IDF relevance ranking
clauxton kb search "FastAPI authentication"
# Results are ranked by relevance - most relevant first!

# Get next recommended task (AI-powered)
clauxton task next

# Undo last operation (v0.10.0 feature)
clauxton undo                   # Undo with confirmation
clauxton undo --history         # View operation history

# Configure confirmation mode (v0.10.0 feature)
clauxton config set confirmation_mode auto    # Balanced (default)
clauxton config set confirmation_mode always  # Maximum safety
clauxton config set confirmation_mode never   # Maximum speed
clauxton config list            # View all configuration
```

### Install from Source (Development)

```bash
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton
pip install -e .
```

### MCP Integration with Claude Code

Set up Clauxton as MCP tools in Claude Code (15 tools available):

```bash
# Automatic setup (Linux/macOS)
./setup-mcp.sh

# Or see detailed guide
docs/MCP_INTEGRATION_GUIDE.md
```

**With v0.10.0 (Coming 2025-11-10)**, Claude Code will use Clauxton **transparently**:

```
You: "Build a Todo app with FastAPI"

Claude Code: (Automatically creates 10 tasks via MCP, no manual commands needed)
             "Created 10 tasks. Starting with TASK-001: FastAPI setup"

You: "Sounds good!"

Claude Code: (Begins implementation)
```

**No more manual CLI commands** - just natural conversation! See `CLAUDE.md` for details.

---

## ✨ Features

- 🧠 **Persistent Knowledge Base** - Store architecture decisions, patterns, constraints across sessions
- 📋 **Task Management** - AI-powered task tracking with automatic dependency inference
- ⚠️ **Conflict Detection** - Predict file conflicts before they occur, get safe execution order (v0.9.0-beta)
- 🔍 **TF-IDF Search** - Relevance-based search with intelligent ranking (powered by scikit-learn)
- 🔒 **Privacy First** - Local-only by default, no cloud dependencies
- 🤖 **MCP Integration** - Seamless integration with Claude Code via Model Context Protocol

### ✅ Phase 1: Complete (v0.9.0-beta)

#### 🔍 TF-IDF Relevance Search
- ✅ **Intelligent Ranking**: TF-IDF algorithm ranks results by relevance (powered by scikit-learn)
- ✅ **Automatic Fallback**: Gracefully falls back to keyword search if scikit-learn unavailable
- ✅ **Fast Performance**: Validated with 200+ knowledge base entries
- ✅ **Query Understanding**: Understands multi-word queries and technical terms
- ✅ **See**: [Search Algorithm Documentation](docs/search-algorithm.md)

#### 📚 Knowledge Base Management
- ✅ **Persistent Context**: Store architecture decisions, patterns, constraints, conventions
- ✅ **Category System**: 5 categories (architecture, constraint, decision, pattern, convention)
- ✅ **YAML Storage**: Human-readable, Git-friendly format
- ✅ **CRUD Operations**: Add, get, update, delete, list entries
- ✅ **Version Management**: Automatic versioning on updates
- ✅ **Atomic Writes**: Safe file operations with automatic backups
- ✅ **Secure Permissions**: 700/600 permissions for privacy

#### ✅ Task Management System
- ✅ **Full CRUD**: Add, get, update, delete, list tasks
- ✅ **Smart Dependencies**: Auto-inferred from file overlap + manual dependencies
- ✅ **DAG Validation**: Cycle detection prevents circular dependencies
- ✅ **Priority Management**: 4 levels (Critical > High > Medium > Low)
- ✅ **AI Recommendations**: `task next` suggests optimal next task
- ✅ **Progress Tracking**: Track status (pending, in_progress, completed, blocked)
- ✅ **Time Estimates**: Optional hour estimates for planning

#### 🚀 v0.10.0 Features (Transparent Integration)
**Bulk Operations**:
- ✅ **YAML Bulk Import**: Create multiple tasks from YAML file - 30x faster than manual
- ✅ **KB Export**: Export Knowledge Base to Markdown documentation
- ✅ **Progress Display**: Real-time progress bars for bulk operations (100+ items)

**Safety & Recovery**:
- ✅ **Undo/Rollback**: Reverse accidental operations with full history tracking
- ✅ **Error Recovery**: Transactional import with `rollback`/`skip`/`abort` strategies
- ✅ **YAML Safety**: Security checks to prevent code injection attacks
- ✅ **Backup Enhancement**: Automatic backups before every write operation (last 10 kept)
- ✅ **Enhanced Validation**: Pre-Pydantic validation with clear error messages

**User Experience**:
- ✅ **Confirmation Prompts**: Threshold-based warnings for bulk operations
- ✅ **Configurable Confirmation Mode**: Set HITL level (always/auto/never)
- ✅ **Operation Logging**: Structured logging with daily log files (30-day retention)
- ✅ **Better Error Messages**: Actionable errors with context + suggestion + commands
- ✅ **Performance Optimization**: 10x faster bulk operations

**Total**: 13 new features in v0.10.0

#### 🔌 MCP Server Integration (20 Tools)
**Knowledge Base Tools** (7):
- ✅ `kb_search` - TF-IDF relevance-ranked search
- ✅ `kb_add` - Add new knowledge entry
- ✅ `kb_list` - List all entries (filterable by category)
- ✅ `kb_get` - Get entry by ID
- ✅ `kb_update` - Update existing entry
- ✅ `kb_delete` - Delete entry
- ✅ `kb_export_docs` - **NEW v0.10.0**: Export KB to Markdown docs

**Task Management Tools** (7):
- ✅ `task_add` - Create task with auto-dependency inference
- ✅ `task_import_yaml` - **NEW v0.10.0**: Bulk import tasks from YAML
- ✅ `task_list` - List tasks (filterable by status/priority)
- ✅ `task_get` - Get task details
- ✅ `task_update` - Update task fields
- ✅ `task_next` - Get AI-recommended next task
- ✅ `task_delete` - Delete task

**Conflict Detection Tools** (3):
- ✅ `detect_conflicts` - Detect file conflicts for a task
- ✅ `recommend_safe_order` - Get optimal task execution order
- ✅ `check_file_conflicts` - Check if files are being edited

**Operation Management Tools** (2) - **NEW v0.10.0**:
- ✅ `undo_last_operation` - Reverse accidental operations
- ✅ `get_recent_operations` - View operation history

**Logging Tools** (1) - **NEW v0.10.0**:
- ✅ `get_recent_logs` - View recent operation logs

#### 📊 Quality Metrics
- ✅ **666 Tests** - Comprehensive test coverage (+276 for v0.10.0 features):
  - Week 1 Day 1-2: YAML Import (24 core + 6 MCP + 6 CLI tests)
  - Week 1 Day 3: Undo/Rollback (24 tests, 81% coverage)
  - Week 1 Day 4: Confirmation Prompts (14 tests)
  - Week 1 Day 5: Error Recovery + YAML Safety (33 tests)
  - Week 2 Day 6: Enhanced Validation (32 tests, 100% coverage)
  - Week 2 Day 7: Logging Functionality (47 tests, 97% coverage)
  - Week 2 Day 8: KB Export (24 tests, 95% coverage)
  - Week 2 Day 9: Progress Display + Performance (11 tests)
  - Week 2 Day 10: Backup Enhancement (18 tests, 89% coverage)
  - Week 2 Day 11: Configurable Confirmation Mode (34 tests, 96% coverage)
- ✅ **92% Coverage** - High code quality maintained (98% task_manager, 100% task_validator, 97% logger, 96% confirmation_manager, 95% KB/MCP)
- ✅ **13 Integration Tests** - End-to-end workflow validation
- ✅ **Type Safe** - Full Pydantic validation with strict mode
- ✅ **Production Ready** - Stable v0.9.0-beta release, **v0.10.0 Week 2 Day 11 complete**

### ✅ Phase 2: Conflict Detection (Complete in v0.9.0-beta)

#### ⚠️ Pre-merge Conflict Detection
- ✅ **File Overlap Detection**: Detects file conflicts between tasks
- ✅ **Risk Scoring**: Calculates risk (LOW <40%, MEDIUM 40-70%, HIGH >70%)
- ✅ **Safe Execution Order**: Recommends optimal task execution order
- ✅ **File Availability Check**: Check if files are currently being edited
- ✅ **CLI Commands**: `conflict detect`, `conflict order`, `conflict check`
- ✅ **MCP Tools**: Full integration for Claude Code

### 🔄 Phase 3: Advanced Conflict Prevention (Planned)
- 🔄 **Line-Level Conflict Detection**: Detect conflicts at code line level
- 🔄 **Drift Detection**: Track scope expansion in tasks
- 🔄 **Event Logging**: Complete audit trail with events.jsonl
- 🔄 **Lifecycle Hooks**: Pre-commit and post-edit hooks

---

## 📦 Installation

### PyPI Installation (Recommended)

```bash
# Install latest stable version (includes all features)
pip install clauxton

# Verify installation
clauxton --version  # Should show: clauxton, version 0.9.0-beta

# Install specific version
pip install clauxton==0.8.0
```

**What's Included**:
- ✅ Knowledge Base management (CRUD + TF-IDF search)
- ✅ Task Management system with auto-dependencies
- ✅ Conflict Detection (pre-merge conflict prediction)
- ✅ MCP Server (15 tools for Claude Code)
- ✅ All dependencies (scikit-learn, numpy, pydantic, click, pyyaml, mcp)

### Development Installation

```bash
# Clone repository
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install in editable mode
pip install -e .

# Run tests
pytest
```

### Requirements

- **Python**: 3.11 or higher
- **Dependencies** (auto-installed with pip):
  - `pydantic>=2.0` - Data validation
  - `click>=8.1` - CLI framework
  - `pyyaml>=6.0` - YAML parsing
  - `gitpython>=3.1` - Git integration
  - `mcp>=1.0` - MCP server
  - `scikit-learn>=1.3` - TF-IDF search
  - `numpy>=1.24` - Required by scikit-learn

**Note on Search**: Clauxton uses **TF-IDF algorithm** for intelligent relevance ranking. If scikit-learn is unavailable, it automatically falls back to keyword matching. See [Search Algorithm](docs/search-algorithm.md) for details.

---

## 🚀 Usage

### Knowledge Base Commands (Phase 0 ✅)

```bash
# Initialize Clauxton in your project
clauxton init

# Add knowledge entry (interactive)
clauxton kb add

# Search Knowledge Base (TF-IDF relevance ranking)
clauxton kb search "architecture"          # Results ranked by relevance
clauxton kb search "API" --category architecture
clauxton kb search "FastAPI" --limit 5     # Limit to top 5 results

# List all entries
clauxton kb list
clauxton kb list --category decision

# Get entry by ID
clauxton kb get KB-20251019-001

# Update entry
clauxton kb update KB-20251019-001 --title "New Title"
clauxton kb update KB-20251019-001 --content "New content" --category decision

# Delete entry
clauxton kb delete KB-20251019-001
clauxton kb delete KB-20251019-001 --yes  # Skip confirmation
```

### Task Management Commands (Phase 1 Week 4 ✅)

```bash
# Add a new task
clauxton task add --name "Setup database" --priority high

# Add task with dependencies
clauxton task add \
  --name "Add API endpoint" \
  --depends-on TASK-001 \
  --files "src/api/users.py" \
  --estimate 3.5

# List all tasks
clauxton task list
clauxton task list --status pending
clauxton task list --priority high

# Get task details
clauxton task get TASK-001

# Update task
clauxton task update TASK-001 --status in_progress
clauxton task update TASK-001 --priority critical

# Get next recommended task (AI-powered)
clauxton task next

# Delete task
clauxton task delete TASK-001

# Bulk import tasks from YAML (NEW v0.10.0)
clauxton task import tasks.yml
clauxton task import tasks.yml --dry-run  # Validate without creating
```

**YAML Bulk Import Example** (`tasks.yml`):
```yaml
tasks:
  - name: "Setup FastAPI project"
    priority: high
    files_to_edit:
      - main.py
      - requirements.txt
    estimated_hours: 2.5

  - name: "Create database models"
    priority: high
    depends_on:
      - TASK-001
    files_to_edit:
      - models/user.py
      - models/post.py
    estimated_hours: 3.0

  - name: "Write API tests"
    priority: medium
    depends_on:
      - TASK-002
    estimated_hours: 4.0
```

See [YAML Task Format Guide](docs/YAML_TASK_FORMAT.md) for complete specification.

### MCP Server (Phase 1 - Available Now!)

The Clauxton MCP Server provides full Knowledge Base and Task Management for Claude Code:

```json
// .claude-plugin/mcp-servers.json
{
  "mcpServers": {
    "clauxton": {
      "command": "python",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**Knowledge Base Tools**:
- `kb_search(query, category?, limit?)` - Search with TF-IDF relevance ranking
- `kb_add(title, category, content, tags?)` - Add new entry
- `kb_list(category?)` - List all entries
- `kb_get(entry_id)` - Get entry by ID
- `kb_update(entry_id, title?, content?, category?, tags?)` - Update entry
- `kb_delete(entry_id)` - Delete entry

> **Note**: Search results are automatically ranked by relevance using TF-IDF algorithm. Most relevant entries appear first.

**Task Management Tools**:
- `task_add(name, description?, priority?, depends_on?, files?, kb_refs?, estimate?)` - Add task
- `task_import_yaml(yaml_content, dry_run?, skip_validation?)` - **NEW v0.10.0**: Bulk import tasks from YAML
- `task_list(status?, priority?)` - List tasks with filters
- `task_get(task_id)` - Get task details
- `task_update(task_id, status?, priority?, name?, description?)` - Update task
- `task_next()` - Get AI-recommended next task
- `task_delete(task_id)` - Delete task

See [MCP Server Guide](docs/mcp-server.md) for complete documentation.

### Conflict Detection Commands (Phase 2 ✅)

```bash
# Check conflicts before starting a task
clauxton conflict detect TASK-001

# Get safe execution order for multiple tasks
clauxton conflict order TASK-001 TASK-002 TASK-003

# Check if specific files are being edited
clauxton conflict check src/api/users.py src/models/user.py
```

See [Conflict Detection Guide](docs/conflict-detection.md) for complete documentation.

### Knowledge Base YAML Structure

After running `clauxton kb add`, your entries are stored in `.clauxton/knowledge-base.yml`:

```yaml
version: '1.0'
project_name: my-project

entries:
  - id: KB-20251019-001
    title: Use FastAPI framework
    category: architecture
    content: |
      All backend APIs use FastAPI framework.

      Reasons:
      - Async/await support
      - Automatic OpenAPI docs
      - Excellent performance
    tags:
      - backend
      - api
      - fastapi
    created_at: '2025-10-19T10:30:00'
    updated_at: '2025-10-19T10:30:00'
    version: 1
```

**Categories**:
- `architecture`: System design decisions
- `constraint`: Technical/business constraints
- `decision`: Important project decisions with rationale
- `pattern`: Coding patterns and best practices
- `convention`: Team conventions and code style

See [YAML Format Reference](docs/yaml-format.md) for complete schema documentation.

---

## 🏗️ Architecture

### Current (Phase 0-1)

```
clauxton/
├── core/
│   ├── models.py          # Pydantic data models ✅
│   └── knowledge_base.py  # KB CRUD operations ✅
├── utils/
│   ├── yaml_utils.py      # Safe YAML I/O ✅
│   └── file_utils.py      # Secure file operations ✅
├── cli/
│   └── main.py            # CLI commands ✅
└── mcp/
    └── server.py          # MCP Server ✅ (Phase 1, Week 3)
```

**Storage**: `.clauxton/knowledge-base.yml` (YAML format)

### Planned (Phase 1-2)

- **Task Management MCP Tools**: task_add, task_list, task_next (Week 4)
- **Dependency Analysis**: Auto-inference, DAG validation (Week 5-6)
- **Enhanced Search**: TF-IDF relevance (Week 7)
- **Conflict Detection**: Pre-merge conflict analysis (Phase 2)

See [docs/architecture.md](docs/architecture.md) for complete design.

---

## 📚 Documentation

### User Guides
- [Quick Start Guide](docs/quick-start.md) - Get started in 5 minutes (CLI)
- **[Developer Workflow Guide](docs/DEVELOPER_WORKFLOW_GUIDE.md)** - Complete development workflow with examples and diagrams ✨ NEW v0.10.0
- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** - Shell alias setup, virtual environment isolation explained ✨ NEW
- **[How to Use v0.9.0-beta](docs/HOW_TO_USE_v0.9.0-beta.md)** - Complete usage guide for current version ✨ NEW
- **[MCP Integration Guide](docs/MCP_INTEGRATION_GUIDE.md)** - Step-by-step Claude Code integration (20 tools) ✨ NEW
- [Tutorial: Your First Knowledge Base](docs/tutorial-first-kb.md) - 30-minute beginner guide
- [Use Cases & Examples](docs/use-cases.md) - Real-world scenarios and implementations
- [MCP Server Quick Start](docs/mcp-server-quickstart.md) - Get started with Claude Code
- [Task Management Guide](docs/task-management-guide.md) - Complete task management documentation
- [Search Algorithm](docs/search-algorithm.md) - TF-IDF search explanation
- [YAML Format Reference](docs/yaml-format.md) - Complete Knowledge Base YAML specification
- [MCP Server Guide](docs/mcp-server.md) - Complete MCP Server documentation
- [Conflict Detection Guide](docs/conflict-detection.md) - Complete conflict detection documentation (40KB)

### Developer Guides
- [Architecture Overview](docs/architecture.md) - System design and data flow
- [Development Guide](docs/development.md) - Setup and contribution guide
- [Technical Design](docs/technical-design.md) - Implementation details
- [Roadmap](docs/roadmap.md) - 16-week development plan
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

### Coming Soon
- API Reference (Phase 1)
- Configuration Guide (Phase 1)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 📊 Project Status

| Phase | Status | Completion | Release |
|-------|--------|------------|---------|
| **Phase 0: Foundation** | ✅ Complete | 100% | v0.1.0 |
| **Phase 1: Core Engine** | ✅ Complete | 100% | v0.8.0 |
| **Phase 2: Conflict Detection** | ✅ Complete | 100% | **v0.9.0-beta** |
| Phase 3: Advanced Features | 📋 Planned | 0% | v0.10.0 (target) |
| Beta Testing | 🔄 In Progress | 0% | - |
| v1.0 Public Launch | 📋 Planned | 0% | v1.0.0 (target) |

**Phase 1 Complete** (v0.8.0 - Released 2025-10-19) ✅:
- ✅ Knowledge Base CRUD (6 MCP tools + CLI)
- ✅ TF-IDF Relevance Search (scikit-learn powered)
- ✅ Task Management (6 MCP tools + CLI)
- ✅ Auto Dependency Inference (file overlap detection)
- ✅ DAG Validation (cycle detection)
- ✅ Full Documentation (20 guides)
- ✅ **267 tests, 94% coverage**

**Phase 2 Complete** (v0.9.0-beta - Released 2025-10-20) ✅:
- 🆕 Conflict Detection (file-based conflict prediction)
- 🆕 Risk Scoring (LOW/MEDIUM/HIGH)
- 🆕 Safe Execution Order (topological sort + conflict-aware)
- 🆕 3 CLI Commands (detect, order, check)
- 🆕 3 MCP Tools (15 tools total)
- 🆕 **390 tests (+123), 94% coverage maintained**
- 🆕 Comprehensive migration guide
- 🆕 **Production ready, beta release**

See [docs/PHASE_1_COMPLETE.md](docs/PHASE_1_COMPLETE.md) for full Phase 1 summary.
See [CHANGELOG.md](CHANGELOG.md) for detailed version history.
See [docs/roadmap.md](docs/roadmap.md) for Phase 2 plans.

---

## 🔒 Security

Clauxton takes security seriously and follows industry best practices:

### Security Measures

- **Static Analysis**: Automated security scanning with [Bandit](https://github.com/PyCQA/bandit) in CI/CD
- **Safe YAML Loading**: Uses `yaml.safe_load()` to prevent code execution
- **Secure File Permissions**:
  - `.clauxton/` directory: 700 (owner only)
  - Data files: 600 (owner read/write only)
- **Input Validation**: All inputs validated with Pydantic models
- **No Command Injection**: No `shell=True` without sanitization
- **Path Traversal Protection**: All file operations validated against project root

### Security Scanning Results

Latest scan (Session 8, 2025-10-21):
- **Lines Scanned**: 5,609
- **Issues Found**: 0
- **Severity**: MEDIUM or higher checked
- **Status**: ✅ **PASSED**

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead, please:
1. Email security concerns to the maintainers
2. Include: description, reproduction steps, potential impact, suggested fix
3. We will respond within 48 hours

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

---

## 🔗 Links

- **PyPI**: [https://pypi.org/project/clauxton/](https://pypi.org/project/clauxton/)
- **GitHub**: [https://github.com/nakishiyaman/clauxton](https://github.com/nakishiyaman/clauxton)
- **GitHub Releases**: [https://github.com/nakishiyaman/clauxton/releases](https://github.com/nakishiyaman/clauxton/releases)
- **Issues**: [https://github.com/nakishiyaman/clauxton/issues](https://github.com/nakishiyaman/clauxton/issues)
- **Discussions**: [https://github.com/nakishiyaman/clauxton/discussions](https://github.com/nakishiyaman/clauxton/discussions)

---

## 🙏 Acknowledgments

This project was inspired by the need for persistent context in AI-assisted development. Special thanks to the Claude Code team for building an extensible platform.

**Note**: Clauxton is an independent project and is not officially affiliated with Anthropic or Claude Code.

---

**Built with ❤️ for Claude Code users**
