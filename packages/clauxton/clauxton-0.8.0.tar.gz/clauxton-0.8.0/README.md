# Clauxton

**Context that persists for Claude Code**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/nakishiyaman/clauxton)

> ⚠️ **Alpha Status**: Clauxton is currently in Phase 0 development. Core features are being implemented. Not yet ready for production use.

Clauxton is a Claude Code plugin that provides **persistent project context** to solve AI-assisted development pain points.

**Vision** (Roadmap):
1. ✅ **Session Context Loss** → Persistent Knowledge Base (Phase 0 - In Progress)
2. 🔄 **Manual Dependency Tracking** → Auto-inferred task dependencies (Phase 1 - Planned)
3. 🔄 **Post-hoc Conflict Detection** → Pre-merge conflict prediction (Phase 2 - Planned)

---

## 🎯 Quick Start

> **Note**: CLI installation only. Full Claude Code plugin integration coming in Phase 1.

```bash
# Install from source (PyPI release coming soon)
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton
pip install -e .

# Initialize in your project
cd your-project
clauxton init

# Add knowledge to your Knowledge Base
clauxton kb add

# Search your Knowledge Base
clauxton kb search "architecture"
```

---

## ✨ Features

### ✅ Phase 0: Foundation (Complete)

#### Knowledge Base Management
- ✅ **Persistent Context**: Store architecture decisions, patterns, constraints, conventions
- ✅ **Category System**: Organize entries by type (architecture, constraint, decision, pattern, convention)
- ✅ **YAML Storage**: Human-readable, Git-friendly YAML format
- ✅ **TF-IDF Search**: Relevance-based search with automatic ranking (see [Search Algorithm](docs/search-algorithm.md))
- ✅ **CRUD Operations**: Add, get, update, delete, list entries
- ✅ **Atomic Writes**: Safe file operations with automatic backups
- ✅ **Secure Permissions**: 700/600 permissions for privacy

### 🚧 Phase 1: Core Engine (In Progress - Week 6/8)

#### Knowledge Base CRUD (✅ Week 3 + Week 7 - Complete)
- ✅ **MCP Tools**: kb_search, kb_add, kb_list, kb_get, kb_update, kb_delete
- ✅ **CLI Commands**: kb add, kb get, kb list, kb search, kb update, kb delete
- ✅ **Claude Code Integration**: .claude-plugin/mcp-servers.json
- ✅ **Type-Safe**: Full Pydantic validation
- ✅ **Version Management**: Automatic versioning on updates

#### Task Management (✅ Week 4 - Complete)
- ✅ **CRUD Operations**: Add, get, update, delete, list tasks
- ✅ **Dependency Tracking**: Define task dependencies (DAG structure)
- ✅ **Cycle Detection**: Prevent circular dependencies with DFS algorithm
- ✅ **Priority Management**: Critical > High > Medium > Low
- ✅ **AI Recommendations**: get_next_task() based on priority and dependencies
- ✅ **CLI Commands**: task add, task list, task get, task update, task delete, task next
- ✅ **YAML Persistence**: tasks.yml with automatic backups

#### Task Management MCP Tools (✅ Week 5 - Complete)
- ✅ **MCP Tools**: task_add, task_list, task_get, task_update, task_next, task_delete
- ✅ **Auto Dependency Inference**: Infer dependencies from file overlap
- ✅ **Claude Code Integration**: Full task management via MCP
- ✅ **AI-Powered Recommendations**: get_next_task() via MCP

#### Dependency Analysis (⏳ Week 6 - Planned)
- 🔄 **Task Graph Visualization**: ASCII/Mermaid dependency graphs
- 🔄 **Enhanced Inference**: Multi-file pattern analysis

### 🔄 Phase 2: Conflict Prevention (Planned)

#### Pre-merge Conflict Detection
- 🔄 **File Overlap Detection**: Detect potential merge conflicts
- 🔄 **Risk Scoring**: Calculate conflict risk (0.0-1.0)
- 🔄 **Safe Execution Order**: Recommend optimal task order
- 🔄 **Drift Detection**: Detect scope expansion

---

## 📦 Installation

### Requirements

- **Python**: 3.11 or higher
- **Dependencies**:
  - `click>=8.0.0` - CLI framework
  - `pydantic>=2.0.0` - Data validation
  - `pyyaml>=6.0.0` - YAML parsing
  - `mcp>=0.1.0` - MCP server integration
  - `scikit-learn>=1.3.0` - TF-IDF search (optional, falls back to simple search if not installed)
  - `numpy>=1.24.0` - Required by scikit-learn

### Development Installation (Current)

```bash
# Clone repository
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install in editable mode (includes all dependencies)
pip install -e .

# Verify installation
clauxton --version
```

### PyPI Installation (Coming Soon)

```bash
# Full installation (with TF-IDF search)
pip install clauxton

# Minimal installation (simple keyword search only)
pip install clauxton --no-deps
pip install click pydantic pyyaml mcp
```

**Note on Search**: Clauxton uses **TF-IDF algorithm** for relevance-based search when `scikit-learn` is installed. If not available, it automatically falls back to simple keyword matching. See [Search Algorithm](docs/search-algorithm.md) for details.

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
```

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

**Task Management Tools** (✅ Week 5):
- `task_add(name, description?, priority?, depends_on?, files?, kb_refs?, estimate?)` - Add task
- `task_list(status?, priority?)` - List tasks with filters
- `task_get(task_id)` - Get task details
- `task_update(task_id, status?, priority?, name?, description?)` - Update task
- `task_next()` - Get AI-recommended next task
- `task_delete(task_id)` - Delete task

See [MCP Server Guide](docs/mcp-server.md) for complete documentation.

### Coming in Phase 2

```bash
# Conflict detection
/conflicts-check
```

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
- [MCP Server Quick Start](docs/mcp-server-quickstart.md) - Get started with Claude Code ✨ NEW
- [Task Management Guide](docs/task-management-guide.md) - Complete task management documentation ✨ NEW
- [Search Algorithm](docs/search-algorithm.md) - TF-IDF search explanation ✨ NEW
- [Installation Guide](docs/installation.md) - Complete installation instructions
- [YAML Format Reference](docs/yaml-format.md) - Complete Knowledge Base YAML specification
- [MCP Server Guide](docs/mcp-server.md) - Complete MCP Server documentation

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

| Phase | Status | Completion | Target Date |
|-------|--------|------------|-------------|
| **Phase 0: Foundation** | ✅ Complete | 100% | Week 2 (2025-11-02) |
| **Phase 1: Core Engine** | 🚧 In Progress | 88% | Week 3-8 |
| Phase 2: Conflict Prevention | 📋 Planned | 0% | Week 9-12 |
| Beta Testing | 📋 Planned | 0% | Week 13-14 |
| Public Launch | 📋 Planned | 0% | Week 15-16 |

**Phase 0 Progress** (Complete ✅):
- ✅ Pydantic data models (100%)
- ✅ YAML utilities (100%)
- ✅ Knowledge Base core (100%)
- ✅ CLI implementation (100%)
- ⏳ Basic MCP Server (0% - deferred to Phase 1)
- ✅ Tests & Documentation (100% - 111 tests, 93% coverage)

**Phase 1 Progress** (Week 9/10 - 95%):
- ✅ Knowledge Base CRUD (100% - complete with update/delete)
- ✅ MCP KB Tools (100% - kb_search, kb_add, kb_list, kb_get, kb_update, kb_delete)
- ✅ Task Management (100% - CRUD, dependencies, DAG validation, CLI)
- ✅ Task Management MCP Tools (100% - task_add, task_list, task_get, task_update, task_next, task_delete)
- ✅ Auto Dependency Inference (100% - file overlap detection)
- ✅ TF-IDF Search (100% - relevance-based search with fallback)
- 🚧 Documentation (80% - Week 9-10)
- ✅ Tests: 265 total, 94% coverage

See [Phase 0 Completion Summary](docs/PHASE_0_COMPLETE.md) for detailed results.
See [docs/roadmap.md](docs/roadmap.md) for overall timeline.
See [docs/phase-1-plan.md](docs/phase-1-plan.md) for next steps.

---

## 🔗 Links

- **GitHub**: [https://github.com/nakishiyaman/clauxton](https://github.com/nakishiyaman/clauxton)
- **Issues**: [https://github.com/nakishiyaman/clauxton/issues](https://github.com/nakishiyaman/clauxton/issues)
- **Discussions**: [https://github.com/nakishiyaman/clauxton/discussions](https://github.com/nakishiyaman/clauxton/discussions)
- **PyPI**: Coming after Phase 0 completion

---

## 🙏 Acknowledgments

This project was inspired by the need for persistent context in AI-assisted development. Special thanks to the Claude Code team for building an extensible platform.

**Note**: Clauxton is an independent project and is not officially affiliated with Anthropic or Claude Code.

---

**Built with ❤️ for Claude Code users**
