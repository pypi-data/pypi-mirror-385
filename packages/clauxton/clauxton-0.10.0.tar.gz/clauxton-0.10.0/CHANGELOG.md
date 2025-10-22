# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.10.0] - 2025-10-22

### v0.10.0 - Production Ready
**Release Date**: 2025-10-22
**Status**: 🚀 Released
**Test Coverage**: 91% (758 tests)
**Previous Version**: v0.9.0-beta

### Added

**Bulk Operations**:
- ✅ **YAML Bulk Import** (Week 1 Day 1-2): `task_import_yaml()` - Create multiple tasks in one operation
  - 20 tests, 100% backward compatible
  - Circular dependency detection, dry-run mode
- ✅ **Undo/Rollback** (Week 1 Day 3): `undo_last_operation()` - Reverse accidental operations
  - 24 tests (81% coverage), supports 7 operation types
  - History stored in `.clauxton/history/operations.yml`
  - CLI: `clauxton undo`, `clauxton undo --history`
  - MCP tools: `undo_last_operation()`, `get_recent_operations()`
- ✅ **Confirmation Prompts** (Week 1 Day 4): Threshold-based confirmation for bulk operations
  - 14 tests, prevents accidental bulk operations
  - Default threshold: 10 tasks (configurable)
  - Preview generation: task count, estimated hours, priority/status breakdown
  - Parameters: `skip_confirmation`, `confirmation_threshold`
  - Returns `status: "confirmation_required"` with preview data
  - Works with: YAML import, dry-run mode, validation errors
- ✅ **Error Recovery** (Week 1 Day 5): Transactional import with configurable error handling
  - 15 tests covering rollback/skip/abort strategies
  - `on_error="rollback"` (default): Revert all changes on any error (transactional)
  - `on_error="skip"`: Skip invalid tasks, continue with valid ones (returns `status: "partial"`)
  - `on_error="abort"`: Stop immediately on first error
  - Returns `skipped` list for skip mode
  - Integration with undo functionality
- ✅ **YAML Safety** (Week 1 Day 5): Security checks to prevent code injection
  - 10 tests covering dangerous patterns
  - Detects `!!python`, `!!exec`, `!!apply` tags
  - Detects `__import__`, `eval()`, `exec()`, `compile()` patterns
  - Blocks import before any processing (highest precedence)
  - Clear security error messages

**User Experience Improvements**:
- ✅ **Enhanced Validation** (Week 2 Day 6): Pre-Pydantic validation for better error messages
  - 32 tests (100% coverage of task_validator.py)
  - Validates: task names, duplicate IDs, duplicate names (warning), priorities, statuses, dependencies, estimated hours, file paths
  - Errors (blocking): empty name, duplicate ID, invalid priority/status, negative hours
  - Warnings (non-blocking): duplicate name, large hours (>1000), nonexistent files
  - Integration: Step 1.5 in import_yaml (after YAML parse, before Pydantic)
  - Can be bypassed: `skip_validation=True` parameter
  - Works with error recovery strategies (rollback/skip/abort)
- ✅ **Operation Logging** (Week 2 Day 7): Structured logging with daily log files
  - 47 tests (97% coverage of logger.py - 28 unit + 11 MCP + 11 CLI + 6 error handling tests)
  - Features:
    - Daily log files: `.clauxton/logs/YYYY-MM-DD.log`
    - Automatic log rotation: 30-day retention
    - JSON Lines format: Structured data for easy parsing
    - Filtering: By operation type, log level, date range
    - Secure permissions: 700 for logs directory, 600 for files
  - MCP tool: `get_recent_logs(limit, operation, level, days)`
  - CLI command: `clauxton logs [--limit N] [--operation TYPE] [--level LEVEL] [--days N] [--date YYYY-MM-DD] [--json]`
  - Log levels: debug, info, warning, error
  - Graceful handling: Skips malformed JSON lines, Unicode support
- ✅ **KB Export** (Week 2 Day 8): Generate Markdown documentation from Knowledge Base
  - 24 tests (95% coverage of KB module)
  - Category-based file generation (one .md per category)
  - ADR format for decision entries (Context, Consequences sections)
  - Standard format for other categories
  - Full Unicode support (UTF-8 encoding)
  - MCP tool: `kb_export_docs(output_dir, category)`
  - CLI command: `clauxton kb export OUTPUT_DIR [--category CATEGORY]`
  - Returns statistics: total_entries, files_created, categories
- ✅ **Progress Display + Performance Optimization** (Week 2 Day 9): Batch operations with progress reporting
  - 8 tests (98% coverage of TaskManager)
  - **`add_many(tasks, progress_callback)` method**: Single file write for all tasks
  - Progress callback support: `(current, total) -> None`
  - Comprehensive validation (duplicates, dependencies, cycles)
  - **Performance improvement**: 100 tasks in 0.2s (25x faster than 5s)
  - `import_yaml()` uses batch operation automatically
  - Backward compatible: All existing tests pass (607 total)
- ✅ **Backup Enhancement** (Week 2 Day 10): Timestamped backups with generation management
  - 22 tests (18 BackupManager + 4 yaml_utils integration)
  - **`BackupManager` class**: Centralized backup management
  - **Timestamped backups**: `filename_YYYYMMDD_HHMMSS_microseconds.yml`
  - **Generation limit**: Keep latest 10 backups per file (configurable via `max_generations`)
  - **Automatic cleanup**: Old backups deleted when limit exceeded
  - **Backup directory**: `.clauxton/backups/` (auto-created with 700 permissions)
  - **Legacy compatibility**: `.bak` files still created for backward compatibility
  - **Helper methods**: `get_latest_backup()`, `count_backups()`, `list_backups()`, `restore_backup()`
  - **Performance**: Backup creation < 100ms (tested with 100-entry files)
  - **File permissions**: Backups stored with 600 (owner read/write only)
  - Integrated into `yaml_utils.write_yaml()` - all YAML writes create backups automatically
- ✅ **Error Message Improvement** (Week 2 Day 10): Actionable error messages with suggestions
  - Enhanced all exception classes with detailed docstrings and examples
  - `ValidationError`: Include specific field and fix suggestion
  - `NotFoundError`: List available IDs and how to list them
  - `DuplicateError`: Suggest update or use different ID
  - `CycleDetectedError`: Show cycle path and how to break it
  - All error handlers use new format with context + suggestion + commands
- ✅ **Configurable Confirmation Mode** (Week 2 Day 11): Customizable Human-in-the-Loop level
  - 29 tests (12 core + 17 CLI tests, 94% coverage of confirmation_manager.py)
  - Features:
    - 3 confirmation modes: "always" (100% HITL), "auto" (75% HITL, default), "never" (25% HITL)
    - Configurable thresholds per operation type (task_import, task_delete, kb_delete, kb_import)
    - Configuration stored in `.clauxton/config.yml`
    - Automatic defaults: task_import=10, task_delete=5, kb_delete=3, kb_import=5
  - Core: `ConfirmationManager` class with `get_mode()`, `set_mode()`, `should_confirm()`, `get_threshold()`, `set_threshold()`
  - CLI commands:
    - `clauxton config set confirmation_mode [always|auto|never]`
    - `clauxton config get confirmation_mode`
    - `clauxton config set task_import_threshold N`
    - `clauxton config list` - View all configuration
  - Safety: Invalid mode auto-resets to "auto", malformed config recovery
  - Persistence: Configuration saved across sessions
  - Use cases:
    - Team development: "always" mode for maximum safety
    - Individual development: "auto" mode for balanced workflow (default)
    - Rapid prototyping: "never" mode with undo capability

**📚 Documentation** (13 comprehensive docs):
- **NEW**: `docs/SESSION_8_SUMMARY.md` - KB Export feature (Week 1 Day 4)
- **NEW**: `docs/SESSION_9_SUMMARY.md` - YAML Safety (Week 1 Day 5)
- **NEW**: `docs/SESSION_10_SUMMARY.md` - MCP Undo Tools (Week 2 Day 1)
- **NEW**: `docs/SESSION_11_SUMMARY.md` - Enhanced Validation (Week 2 Day 6)
- **NEW**: `docs/SESSION_11_GAP_ANALYSIS.md` - Gap analysis and v0.10.1 planning
- **NEW**: `docs/ERROR_HANDLING_GUIDE.md` - Complete error resolution guide
- **NEW**: `docs/MIGRATION_v0.10.0.md` - Migration guide from v0.9.0-beta
- **NEW**: `docs/configuration-guide.md` - Configuration reference
- **NEW**: `docs/troubleshooting.md` - Comprehensive troubleshooting (1,300 lines!)
- Existing: `docs/YAML_TASK_FORMAT.md` - YAML format specification
- Existing: `docs/kb-export-guide.md` - KB export guide
- Existing: `docs/logging-guide.md` - Logging system guide
- Existing: `docs/performance-guide.md` - Performance optimization guide
- Existing: `docs/backup-guide.md` - Backup management guide
- Updated: `README.md` - v0.10.0 features, 17 MCP tools, 758 tests
- Updated: `CLAUDE.md` - Integration philosophy, best practices (7,000+ lines!)
- Updated: `CHANGELOG.md` - Complete v0.10.0 changelog

**🧪 Quality** (Session 11 Complete):
- **+368 tests** (390 → **758 tests**)
- **91% overall coverage** (target: 80%, +11% over)
  - **99% MCP server coverage** (target: 60%, +39% over)
  - **84-100% CLI coverage** (target: 40%, +44% over)
  - **87-96% core modules** (KB: 95%, TaskManager: 98%, Search: 86%)
  - **80-85% utils modules** (on target)
- **17 MCP tools** (15 → 17, +2 tools: undo_last_operation, get_recent_operations)
- **CI/CD**: 3 parallel jobs (test, lint, build) ~52s total
- Integration scenarios: Happy path, error recovery, undo flow, confirmation mode, performance testing

**Expected Impact**:
- User operations: 10 commands → 0 (fully automatic)
- Task registration: 5 minutes → 10 seconds (30x faster)
- Error risk: 10-20% → <1%
- Human-in-the-Loop: 50% → 75-100% (configurable)
- Claude philosophy alignment: 70% → 95%

See `docs/design/REVISED_ROADMAP_v0.10.0.md` for complete roadmap.

---

### Phase 3 Features (v0.11.0 and beyond)
- Interactive Mode: Conversational YAML generation
- Project Templates: Pre-built patterns for common projects
- Repository Map: Automatic codebase indexing (like Aider/Devin)
- Web Dashboard: Visual KB/Task/Conflict management

---

## [0.9.0-beta] - 2025-10-20 (Week 12 Complete: Conflict Detection)

### Added - Conflict Detection (Phase 2 - Week 12)

#### Core Features
- **ConflictDetector Engine**: File-based conflict prediction system
  - Detects file overlap between tasks (O(n²) pairwise comparison)
  - Risk scoring: LOW (<40%), MEDIUM (40-70%), HIGH (>70%)
  - Only checks `in_progress` tasks to avoid false positives

- **Safe Execution Order**: Topological sort + conflict-aware scheduling
  - Respects task dependencies (DAG validation)
  - Minimizes file conflicts
  - Considers task priorities (critical > high > medium > low)

- **File Availability Checking**: Pre-edit conflict detection
  - Check which tasks are editing specific files
  - Supports multiple file checking with wildcard patterns

#### CLI Commands (3 new)
- `clauxton conflict detect <TASK_ID> [--verbose]`: Check conflicts for a task
- `clauxton conflict order <TASK_IDS...> [--details]`: Get safe execution order
- `clauxton conflict check <FILES...> [--verbose]`: Check file availability

#### MCP Tools (3 new)
- `detect_conflicts`: Detect conflicts for a task
- `recommend_safe_order`: Get optimal task order
- `check_file_conflicts`: Check file availability

#### Testing & Quality (Week 12 Day 6-8)
- **390 tests total** (+38 error resilience tests): 52 conflict-related tests including:
  - 22 CLI conflict command tests (detect, order, check)
  - 13 integration workflow tests (NEW in Day 7)
  - 9 MCP conflict tool tests (NEW in Day 7)
  - 26 core ConflictDetector tests
  - Edge cases: empty files, nonexistent files, multiple in-progress tasks
  - Risk level validation (LOW/MEDIUM/HIGH)
  - Completed task filtering
  - Priority-based ordering
  - Special characters in file paths (Unicode, spaces)
  - CLI output format regression test (NEW in Day 7)
  - Error handling and boundary conditions

- **38 Error Resilience Tests** (NEW in Day 8):
  - `tests/core/test_error_resilience.py` (24 tests): YAML errors, missing resources, corrupted data, validation errors
  - `tests/cli/test_error_handling.py` (17 tests): CLI error handling, uninitialized project, input validation

- **Code Coverage**: 94% overall, 92-94% for CLI modules (+1-3% improvement)
- **Integration Tests**: 13 end-to-end workflow scenarios
  - Pre-Start Check workflow
  - Sprint Planning with priorities
  - File Coordination lifecycle
  - MCP-CLI consistency validation
  - Error recovery scenarios
  - Performance testing with 20+ tasks
- **Performance**: <500ms for conflict detection (10 tasks), <1s for ordering (20 tasks)

#### Documentation (Week 12 Day 6-8)
- **conflict-detection.md**: Complete 35KB+ guide
  - Python API, MCP tools, CLI commands
  - Algorithm details, performance tuning
  - Comprehensive troubleshooting section (10 detailed issues, NEW in Day 7)
    - No conflicts detected (with debug steps)
    - False positives explanation
    - Risk score calculation with examples
    - Safe order logic
    - Unicode/special characters handling
    - Performance issues with benchmarks
    - MCP tool errors
    - CLI command debugging
    - Vague recommendations analysis

- **quick-start.md**: Added Conflict Detection Workflow section
  - 3 CLI command examples with real output
  - Risk level explanations (🔴 HIGH, 🟡 MEDIUM, 🔵 LOW)
  - 3 common workflows (Pre-Start Check, Sprint Planning, File Coordination)

- **README.md**: Updated with Phase 2 completion
  - ⚠️ Conflict Detection feature highlighted
  - Phase 2 status: Complete (100%)
  - Test count: 390 tests
  - MCP tools: 15 total

- **RELEASE_NOTES_v0.9.0-beta.md**: Migration Guide expanded (NEW in Day 8)
  - Comprehensive upgrade instructions (v0.8.0 → v0.9.0-beta)
  - Workflow updates (Solo/Team/Sprint Planning)
  - Troubleshooting and rollback guide
  - ~5KB of user documentation

### Technical Details
- **Architecture**: ConflictDetector as standalone module in `clauxton/core/`
- **Algorithm**: Pairwise task comparison with early termination
- **Risk Calculation**: File overlap count ÷ total unique files
- **MCP Integration**: 15 tools total (12 existing + 3 new)

### Performance Benchmarks
- Conflict detection: <500ms (10 tasks)
- Safe order recommendation: <1s (20 tasks with dependencies)
- File availability check: <100ms (10 files)

---

## [Week 11] - 2025-10-17 to 2025-10-18

### Added (Week 11: Documentation & Community Setup)

#### Documentation (Days 1-2, 5-6)
- **Tutorial**: `docs/tutorial-first-kb.md` (30-minute complete beginner guide)
- **Use Cases**: `docs/use-cases.md` (10 real-world scenarios with implementation guides)
  - 5 detailed core use cases (Solo Dev, Team, OSS, Enterprise, Student)
  - 5 additional use cases (API, DevOps, Security, Product, Microservices)
  - Before/After comparisons with ROI calculations
  - 50+ code examples
- **Enhanced Guides**:
  - `docs/quick-start.md` - Added Advanced Usage section (+260 lines)
  - `docs/task-management-guide.md` - Added Real-World Workflows section (+290 lines)
  - `docs/troubleshooting.md` - Added platform-specific issues (+609 lines)
    * Windows, macOS, Linux troubleshooting
    * Common error messages explained
    * Advanced debugging techniques
    * Extended FAQ (10 new questions)

#### Community Infrastructure (Day 4)
- **GitHub Templates**:
  - `.github/ISSUE_TEMPLATE/bug_report.yml` - Structured bug reports
  - `.github/ISSUE_TEMPLATE/feature_request.yml` - Use case-focused feature requests
  - `.github/ISSUE_TEMPLATE/question.yml` - Q&A template
  - `.github/pull_request_template.md` - 22-item PR checklist
- **Contributing Guide Enhancement**:
  - `CONTRIBUTING.md` - Added CI/CD Workflow section (+243 lines)
    * Local CI checks guide
    * Troubleshooting for CI failures
    * Coverage requirements (90% minimum, 94% current)

#### CI/CD Automation (Day 3)
- **GitHub Actions Workflow** (`.github/workflows/ci.yml`):
  - Test job (Python 3.11 & 3.12, 267 tests, ~42-44s)
  - Lint job (ruff + mypy, ~18s)
  - Build job (twine validation, ~17s)
  - Total: ~44 seconds (parallel execution)
- **Type Checking Configuration**:
  - `mypy.ini` - Strict type checking with missing import handling
- **README Badges**:
  - CI status badge
  - Codecov coverage badge

### Changed (Week 11)
- **README.md**:
  - Status: Alpha → Production Ready (v0.8.0)
  - Added PyPI installation as primary method
  - Added CI and Codecov badges
  - Updated documentation links (Tutorial, Use Cases)
- **Documentation Structure**:
  - Total docs: 22 → 23 markdown files
  - Total size: ~394 KB → ~520 KB (+32% growth)

### Fixed (Week 11)
- **Tests**:
  - `test_version_command` - Updated expected version (0.1.0 → 0.8.0)
- **CI/CD**:
  - 36 ruff linting errors (unused imports, line length, whitespace)
  - 81 mypy type errors (missing type stubs for third-party libs)
  - Deprecated `upload-artifact@v3` → `v4`

### Notes (Week 11)
- **Test Coverage**: Maintained at 94% (267 tests, all passing)
- **CI/CD**: All checks passing (~44s total runtime)
- **Documentation Quality**: A+ (all recommended docs complete)
- **Community Ready**: Professional contribution infrastructure

### Planned

#### Phase 2: Conflict Prevention (Week 12+)
- Conflict Detector (pre-merge risk analysis)
- Drift Detection
- Lifecycle Hooks
- Event Logging
- Conflict Detector Subagent

---

## [0.8.0] - 2025-10-19 (Week 9-10: TF-IDF Search)

### Added
- **TF-IDF Search Engine** (`clauxton/core/search.py`):
  - Relevance-based search using scikit-learn TfidfVectorizer
  - Cosine similarity scoring for result ranking
  - Automatic stopword filtering (English)
  - N-gram support (unigrams and bigrams)
  - Category filtering with dynamic index rebuilding
  - Graceful degradation to simple search when scikit-learn unavailable
- **Fallback Search** (`knowledge_base.py`):
  - Simple keyword matching with weighted scoring (title: 2.0, tag: 1.5, content: 1.0)
  - Automatic fallback detection when TF-IDF unavailable
  - Consistent API with TF-IDF search
- **Dependencies**:
  - `scikit-learn>=1.3.0` - TF-IDF vectorization (optional)
  - `numpy>=1.24.0` - Required by scikit-learn
- **Test Suite Expansion**:
  - 18 new tests (265 total, up from 247)
  - `_simple_search` fallback method: 0% → ~95% coverage
  - Edge cases: stopwords, Unicode, special characters, error handling
  - scikit-learn unavailable scenario testing
- **Documentation**:
  - `docs/search-algorithm.md` - Complete TF-IDF algorithm explanation (350 lines)
  - README.md - TF-IDF features, dependencies, search examples
  - `docs/quick-start.md` - Search section expansion with TF-IDF usage guide

### Changed
- **Knowledge Base Search**:
  - Search results now ranked by relevance (TF-IDF scores)
  - More relevant entries appear first
  - Empty queries return empty results (consistent behavior)
- **MCP kb_search Tool**:
  - Returns relevance-scored results
  - Backward compatible (same API signature)
- **Test Coverage**:
  - Overall coverage: 92% → 94%
  - `clauxton/core/knowledge_base.py`: 85% → 96%
  - `clauxton/core/search.py`: 83% → 86% (new file)

### Fixed
- Search index rebuild order (now rebuilds before cache invalidation)
- Empty query handling (consistent empty results across both search methods)
- Long content search compatibility with TF-IDF (realistic test data)

### Performance
- Small KB (< 50 entries): Search < 5ms, Indexing < 10ms
- Medium KB (50-200 entries): Search < 10ms, Indexing < 50ms
- Large KB (200+ entries): Search < 20ms, Indexing < 200ms

### Notes
- **Backward Compatible**: Existing search functionality works unchanged
- **Optional Dependency**: scikit-learn is optional; automatic fallback to simple search
- **Production Ready**: 94% test coverage, all edge cases tested

---

## [0.1.0] - TBD (Phase 0 Target)

### Added
- Initial project structure
- Pydantic data models:
  - `KnowledgeBaseEntry` with validation
  - `KnowledgeBaseConfig`
- Knowledge Base manager (`clauxton/core/knowledge_base.py`):
  - `add()` - Add KB entry
  - `search()` - Search with keyword/category/tag filtering
  - `get()` - Retrieve entry by ID
  - `update()` - Update entry with versioning
  - `delete()` - Soft delete
  - `list_all()` - List all entries
- YAML utilities with atomic write and backup
- File utilities with secure permissions (700/600)
- CLI commands:
  - `clauxton init` - Initialize `.clauxton/` directory
  - `clauxton kb add` - Add Knowledge Base entry (interactive)
  - `clauxton kb search <query>` - Search Knowledge Base
  - `clauxton kb list` - List all KB entries
- Basic MCP Server (`clauxton/mcp/kb_server.py`):
  - Health check endpoint
  - Tool registration infrastructure
- Unit tests:
  - `tests/core/test_models.py`
  - `tests/core/test_knowledge_base.py`
  - `tests/utils/test_yaml_utils.py`
  - `tests/cli/test_main.py`
- Integration tests:
  - End-to-end workflow (init → add → search)
- Documentation:
  - `README.md` - Project overview
  - `docs/quick-start.md` - Quick start guide
  - `docs/installation.md` - Installation instructions
  - `docs/project-plan.md` - Market analysis & strategy
  - `docs/requirements.md` - Functional & non-functional requirements
  - `docs/technical-design.md` - Architecture & implementation details
  - `docs/roadmap.md` - 16-week development roadmap
  - `docs/phase-0-plan.md` - Detailed Phase 0 plan
  - `CONTRIBUTING.md` - Contribution guidelines
  - `CODE_OF_CONDUCT.md` - Code of Conduct
- GitHub templates:
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`
- Development setup:
  - `pyproject.toml` with dependencies
  - `.gitignore` for Python projects
  - MIT License

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- File permissions set to 700 (directories) and 600 (files)
- YAML schema validation on read/write
- Input sanitization via Pydantic validators

---

## [0.0.1] - 2025-10-19 (Project Inception)

### Added
- Project structure initialization
- Basic package files
- Planning documentation (Japanese versions)
- Repository setup at `/home/kishiyama-n/workspace/projects/clauxton/`

---

## Format Guide

### Types of Changes
- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes

### Version Format
- **MAJOR** - Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR** - New features (e.g., 0.1.0 → 0.2.0)
- **PATCH** - Bug fixes (e.g., 0.1.0 → 0.1.1)

---

**Note**: This changelog is maintained manually. Contributors should update this file when making significant changes as part of their pull requests.

[Unreleased]: https://github.com/nakishiyaman/clauxton/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/nakishiyaman/clauxton/releases/tag/v0.8.0
[0.1.0]: https://github.com/nakishiyaman/clauxton/releases/tag/v0.1.0
[0.10.0]: https://github.com/nakishiyaman/clauxton/compare/v0.9.0...v0.10.0
[0.9.0-beta]: https://github.com/nakishiyaman/clauxton/compare/v0.8.0...v0.9.0
[0.0.1]: https://github.com/nakishiyaman/clauxton/releases/tag/v0.0.1
