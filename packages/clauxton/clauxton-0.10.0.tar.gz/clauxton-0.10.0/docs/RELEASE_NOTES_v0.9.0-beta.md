# Clauxton v0.9.0-beta Release Notes

**Release Date**: October 20, 2025
**Codename**: "Conflict Prevention"
**Status**: Beta Release

---

## 🎉 Overview

Clauxton v0.9.0-beta introduces **Conflict Detection**, a powerful new feature that predicts file conflicts between tasks **before** they occur. This release completes Week 12 of Phase 2 development, bringing intelligent conflict prevention to your development workflow.

---

## ✨ What's New

### 🎯 Conflict Detection Engine

Predict and prevent merge conflicts before starting work on tasks.

#### Key Features

**1. File Overlap Detection**
- Automatically detects when multiple tasks plan to edit the same files
- Considers only `in_progress` tasks to avoid false positives
- Fast pairwise comparison algorithm (O(n²) with early termination)

**2. Risk Scoring System**
```
🔴 HIGH   (>70%):  Many files overlap - high merge conflict risk
🟡 MEDIUM (40-70%): Some overlap - coordination recommended
🔵 LOW    (<40%):  Minor overlap - proceed with caution
```

**3. Smart Recommendations**
- Suggests which task to complete first
- Provides conflict-aware execution order
- Identifies safe vs. risky task combinations

---

## 🔧 New CLI Commands

### 1. `clauxton conflict detect`

Check for conflicts before starting a task:

```bash
clauxton conflict detect TASK-002
```

**Output**:
```
Conflict Detection Report
Task: TASK-002 - Add OAuth support
Files: 2 file(s)

⚠ 1 conflict(s) detected

Conflict 1:
  Task: TASK-001 - Refactor authentication
  Risk: MEDIUM (67%)
  Files: 1 overlapping
  → Complete TASK-001 before starting TASK-002, or coordinate changes
```

**Options**:
- `--verbose`: Show detailed file lists and analysis

### 2. `clauxton conflict order`

Get AI-recommended execution order for multiple tasks:

```bash
clauxton conflict order TASK-001 TASK-002 TASK-003
```

**Output**:
```
Recommended Order:
1. TASK-001 - Refactor authentication
2. TASK-002 - Add OAuth support
3. TASK-003 - Update user model

💡 Execute tasks in this order to minimize conflicts
```

**How it works**:
- Uses topological sort for dependencies
- Analyzes file overlap between tasks
- Considers task priorities
- Suggests optimal order

**Options**:
- `--details`: Show priority, files, and dependencies for each task

### 3. `clauxton conflict check`

Check file availability before editing:

```bash
clauxton conflict check src/api/auth.py
```

**Output (available)**:
```
✓ All 1 file(s) available for editing
```

**Output (locked)**:
```
⚠ 1 task(s) editing these files

Conflicting Tasks:
  TASK-001 - Refactor authentication
  Status: in_progress
  Editing: 1 of your file(s)

💡 Coordinate with task owners or wait until tasks complete
```

**Options**:
- `--verbose`: Show per-file lock status

---

## 🤖 New MCP Tools

Three new MCP tools for seamless Claude Code integration:

### 1. `detect_conflicts`

**Description**: Detect conflicts for a specific task
**Input**: `task_id` (string)
**Output**: List of conflicts with risk scores

**Example**:
```python
result = mcp.call_tool("detect_conflicts", {"task_id": "TASK-002"})
# Returns: [{"task_b_id": "TASK-001", "risk_level": "medium", ...}]
```

### 2. `recommend_safe_order`

**Description**: Get optimal task execution order
**Input**: `task_ids` (array of strings)
**Output**: Ordered list of task IDs

**Example**:
```python
result = mcp.call_tool("recommend_safe_order", {
    "task_ids": ["TASK-001", "TASK-002", "TASK-003"]
})
# Returns: ["TASK-001", "TASK-002", "TASK-003"]
```

### 3. `check_file_conflicts`

**Description**: Check which tasks are editing specific files
**Input**: `files` (array of file paths)
**Output**: List of conflicting task IDs

**Example**:
```python
result = mcp.call_tool("check_file_conflicts", {
    "files": ["src/api/auth.py"]
})
# Returns: ["TASK-001", "TASK-003"]
```

---

## 📊 Performance

All performance targets met or exceeded:

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| Conflict detection (5 tasks) | <2s | <500ms | ✅ 4x faster |
| Safe order (20 tasks) | <2s | <1s | ✅ 2x faster |
| File check (10 files) | <500ms | <100ms | ✅ 5x faster |

**Scalability**:
- Handles 50+ concurrent tasks efficiently
- No performance degradation with large file lists
- Optimized pairwise comparison with early exit

---

## 🧪 Testing

Comprehensive test coverage ensures reliability:

| Category | Tests | Coverage |
|----------|-------|----------|
| **Core ConflictDetector** | 26 | 96% |
| **MCP Conflict Tools** | 9 | 99% |
| **CLI Commands** | 22 | 91% |
| **Integration Workflows** | 13 | 100% |
| **Total (All Modules)** | **352** | **94%** |

**Test Highlights (Week 12 Day 6-7)**:
- ✅ **52 Conflict Tests**: Comprehensive coverage of all conflict features
- ✅ **13 Integration Tests** (NEW Day 7): End-to-end workflow validation
  - Pre-Start Check workflow
  - Sprint Planning with priorities
  - File Coordination lifecycle
  - MCP-CLI consistency
  - Error recovery
  - Performance (20+ tasks)
- ✅ **9 MCP Tool Tests** (NEW Day 7): Full tool validation
- ✅ **CLI Output Regression Test** (NEW Day 7): Stable output format
- ✅ Edge cases: Empty files, nonexistent paths, special characters, Unicode
- ✅ Risk levels: LOW, MEDIUM, HIGH validation
- ✅ Status filtering: Completed tasks properly ignored
- ✅ Priority ordering: Critical > High > Medium > Low
- ✅ Error handling: Graceful failures with clear messages

---

## 📚 Documentation

Complete documentation added:

### New Guides

**1. Conflict Detection Guide** (`docs/conflict-detection.md`)
- 35KB+ comprehensive guide
- Python API reference
- MCP tools documentation
- CLI command examples
- Algorithm details
- Performance tuning
- **Comprehensive Troubleshooting** (NEW Day 7): 10 detailed issues
  - No conflicts detected (with debug steps)
  - False positives explanation
  - Risk score calculation examples
  - Safe order logic
  - Unicode/special characters handling
  - Performance issues with benchmarks
  - MCP tool errors
  - CLI command debugging

**2. Quick Start Updates** (`docs/quick-start.md`)
- Conflict Detection Workflow section (+170 lines)
- 3 command examples with real output
- Risk level explanations
- Common workflows:
  - Pre-Start Check
  - Sprint Planning
  - File Coordination

### Updated Documentation

**3. README.md**
- Features section updated
- Conflict Detection highlighted
- v0.9.0-beta references

**4. CHANGELOG.md**
- Complete v0.9.0-beta entry
- Week 12 development history
- Technical details
- Performance benchmarks

---

## 🔄 Upgrade Guide

### From v0.8.0 to v0.9.0-beta

**No breaking changes** - Direct upgrade supported. All existing workflows continue to work.

#### Step 1: Installation

```bash
# Upgrade via pip
pip install --upgrade clauxton

# Verify installation
clauxton --version
# Expected output: clauxton, version 0.9.0-beta
```

#### Step 2: Test Existing Workflow

All v0.8.0 commands work unchanged:

```bash
# Your existing workflows remain intact
clauxton task list
clauxton kb search "your query"
clauxton task next
```

#### Step 3: Adopt New Features (Optional)

Three new conflict detection commands are now available:

**1. Pre-Start Conflict Check**
```bash
# Before (v0.8.0):
clauxton task next
# Start working immediately

# After (v0.9.0-beta) - Recommended:
clauxton task next
# Output: Next: TASK-003 - Security improvements

clauxton conflict detect TASK-003
# ✅ No conflicts detected - safe to proceed
# OR
# ⚠ 1 conflict detected with TASK-001 - coordinate or wait
```

**2. Sprint Planning with Safe Order**
```bash
# New in v0.9.0-beta:
clauxton conflict order TASK-001 TASK-002 TASK-003

# Output shows optimal execution order:
# Recommended Order:
#   1. TASK-001 (Critical, no conflicts)
#   2. TASK-003 (High, depends on TASK-001)
#   3. TASK-002 (Medium, conflicts with TASK-001)
```

**3. File Availability Check**
```bash
# Before editing a file:
clauxton conflict check src/api/auth.py

# Output:
# ⚠ 1 task(s) editing these files:
#   TASK-001 (in_progress)
# OR
# ✅ All files available for editing
```

### Recommended Workflow Updates

#### Solo Developer Workflow

**Before (v0.8.0)**:
```bash
1. clauxton task next
2. Start coding
3. Discover conflicts during merge (if any)
```

**After (v0.9.0-beta)**:
```bash
1. clauxton task next
2. clauxton conflict detect <TASK_ID>  # NEW: Check first!
3. If no conflicts → Start coding
4. If conflicts → Coordinate or complete conflicting task first
```

**Benefit**: Prevent merge conflicts before they happen

#### Team Workflow

**Before (v0.8.0)**:
```bash
1. Ask team: "Is anyone editing auth.py?"
2. Manual coordination
3. Start work (hope for no conflicts)
```

**After (v0.9.0-beta)**:
```bash
1. clauxton conflict check src/api/auth.py  # NEW: Instant check!
2. If available → Start work
3. If locked → See which task/person is editing it
```

**Benefit**: Instant file availability check

#### Sprint Planning Workflow

**Before (v0.8.0)**:
```bash
1. List tasks manually
2. Manually determine order based on priorities
3. Hope files don't conflict
```

**After (v0.9.0-beta)**:
```bash
1. clauxton task list --status pending
2. clauxton conflict order TASK-001 TASK-002 ... TASK-N  # NEW!
3. Execute tasks in recommended order
```

**Benefit**: Automated conflict-aware task ordering

### MCP Integration

If using MCP with Claude Code, three new tools are automatically available:

**New Tools** (no configuration needed):
- `detect_conflicts` - Check conflicts for a task
- `recommend_safe_order` - Get optimal execution order
- `check_file_conflicts` - Check file availability

**Example MCP Usage**:
```json
{
  "tool": "detect_conflicts",
  "arguments": {"task_id": "TASK-002"},
  "returns": {
    "conflict_count": 1,
    "status": "conflicts_detected",
    "max_risk_level": "medium"
  }
}
```

Claude Code can now proactively check for conflicts and suggest safe execution orders.

### Configuration Changes

**None required** - v0.9.0-beta uses the same configuration as v0.8.0.

Your existing `.clauxton/` directory structure remains unchanged:
```
.clauxton/
├── config.yaml         # No changes
├── knowledge/          # No changes
│   └── kb-*.yaml
└── tasks/              # No changes (conflict detection reads existing data)
    └── task-*.yaml
```

### Data Migration

**None required** - Conflict detection reads your existing task data.

The `files_to_edit` field you've been using since v0.8.0 is now used for conflict detection. No changes to task files needed.

### Backward Compatibility

✅ **100% backward compatible**:
- All v0.8.0 commands work unchanged
- All v0.8.0 task data formats work unchanged
- All v0.8.0 KB data formats work unchanged
- All v0.8.0 MCP tools work unchanged

New features are additive only - nothing is removed or changed.

### Performance Notes

Conflict detection is fast:
- Detect conflicts (10 tasks): <500ms
- Recommend order (20 tasks): <1s
- Check files (10 files): <100ms

**No performance impact** on existing v0.8.0 commands.

### Troubleshooting

If you encounter issues after upgrading:

**Issue**: `clauxton conflict` command not found
```bash
# Solution: Verify installation
pip show clauxton | grep Version
# Should show: Version: 0.9.0-beta

# If showing old version, force reinstall
pip install --force-reinstall clauxton
```

**Issue**: Conflicts not detected
```bash
# Solution: Ensure tasks have `files_to_edit` field
clauxton task get TASK-001
# Should show: files_to_edit: [...]

# If missing, update task:
clauxton task update TASK-001 --files src/file1.py src/file2.py
```

**Issue**: MCP tools not available
```bash
# Solution: Restart MCP server
# (Specific steps depend on your MCP setup)
```

For more troubleshooting, see `docs/conflict-detection.md` → Troubleshooting section (10 detailed issues).

### Learning Resources

After upgrading, learn more about conflict detection:

📚 **Documentation**:
- `docs/conflict-detection.md` - Complete guide (35KB+)
- `docs/quick-start.md` - Quick workflows
- `docs/RELEASE_NOTES_v0.9.0-beta.md` - This document

🎯 **Quick Start**:
```bash
# 1. Check what conflicts exist
clauxton conflict detect TASK-002

# 2. Get optimal task order
clauxton conflict order TASK-001 TASK-002 TASK-003

# 3. Check file before editing
clauxton conflict check src/api/auth.py
```

💡 **Best Practices**:
- Run `conflict detect` before starting any task
- Use `conflict order` during sprint planning
- Check `conflict check` before editing shared files
- Review risk levels: 🔴 HIGH (>70%), 🟡 MEDIUM (40-70%), 🔵 LOW (<40%)

### Rollback (if needed)

If you need to rollback to v0.8.0:

```bash
# Rollback installation
pip install clauxton==0.8.0

# Verify
clauxton --version
# Should show: clauxton, version 0.8.0
```

Your data remains unchanged - you can upgrade again anytime.

---

## 🎯 Use Cases

### 1. Pre-Start Conflict Check

**Before**:
```bash
# Start work blindly, discover conflicts later
clauxton task update TASK-002 --status in_progress
# ... hours later: merge conflict!
```

**After**:
```bash
# Check first
clauxton conflict detect TASK-002
# ⚠ MEDIUM risk conflict with TASK-001
# Decision: Wait for TASK-001 or coordinate
```

### 2. Sprint Planning

**Before**:
```bash
# Assign tasks randomly, hope for the best
TASK-001 → Developer A
TASK-002 → Developer B
# ... merge conflicts during integration
```

**After**:
```bash
# Get optimal order
clauxton conflict order TASK-001 TASK-002 TASK-003 TASK-004
# Assign based on recommended order
# Minimize conflicts, maximize parallel work
```

### 3. Team Coordination

**Before**:
```bash
# Start editing file, discover someone else is working on it
vim src/api/auth.py
# ... conflict during commit
```

**After**:
```bash
# Check first
clauxton conflict check src/api/auth.py
# ⚠ Locked by TASK-001 (in_progress)
# Coordinate with team before editing
```

---

## 🛠️ Technical Details

### Architecture

**ConflictDetector Module** (`clauxton/core/conflict_detector.py`)
- Standalone module with clear API
- No external dependencies beyond TaskManager
- Extensible design for future enhancements

**Algorithm**:
- Pairwise task comparison (O(n²))
- Early termination for performance
- Risk calculation: `overlap_count / unique_files`
- Topological sort for safe ordering

**Integration Points**:
- CLI: `clauxton/cli/conflicts.py`
- MCP: `clauxton/mcp/server.py`
- Core: `clauxton/core/conflict_detector.py`

### Data Models

**ConflictRisk**:
```python
@dataclass
class ConflictRisk:
    task_a_id: str
    task_b_id: str
    risk_level: Literal["low", "medium", "high"]
    risk_score: float  # 0.0 - 1.0
    overlapping_files: List[str]
    details: str
    recommendation: str
```

---

## 🚧 Known Limitations

### Beta Release Constraints

1. **File-level Detection Only**
   - Detects file overlap, not line-level conflicts
   - Future: Line-level analysis (Phase 3)

2. **Static Analysis**
   - No git diff integration yet
   - Future: Git branch comparison (Phase 3)

3. **Heuristic Risk Scoring**
   - Risk scores based on file count
   - Future: ML-based scoring (Phase 4)

### Workarounds

**Line-level conflicts**:
- Use `--verbose` for file lists
- Manually check file sections
- Coordinate with team members

**Git integration**:
- Check git status separately
- Use git diff to compare branches
- Combine with Clauxton recommendations

---

## 🐛 Bug Fixes

This release includes several bug fixes from v0.8.0:

- Fixed TaskManager dependency validation edge case
- Improved error messages for invalid task IDs
- Enhanced Unicode support in file paths
- Better handling of special characters in task names

---

## 📈 Statistics

### Development Timeline (Week 12)

| Day | Focus | Deliverables |
|-----|-------|--------------|
| Day 1 | Core | ConflictDetector + 18 tests |
| Day 2 | MCP | 3 tools + 14 tests |
| Day 3-4 | Integration | 10 tests + tuning |
| Day 5 | CLI | 3 commands + 13 tests |
| Day 6 | Polish | +8 tests + docs |
| Day 7 | Release | Version bump + notes |

### Code Metrics

| Metric | v0.8.0 | v0.9.0-beta | Change |
|--------|--------|-------------|--------|
| Total Lines of Code | ~5,500 | ~8,000 | +45% |
| Total Tests | 269 | **322** | +53 |
| Test Coverage | 94% | **94%** | Maintained |
| CLI Commands | 17 | **20** | +3 |
| MCP Tools | 12 | **15** | +3 |
| Documentation Files | 21 | **25** | +4 |

---

## 🗺️ Roadmap

### Phase 2 (Weeks 13-15)

**Week 13**: Drift Detection
- Track task scope expansion
- Detect when tasks deviate from plan
- Automatic scope change alerts

**Week 14**: Event Logging
- Complete audit trail (events.jsonl)
- Replay capability
- Historical conflict analysis

**Week 15**: Lifecycle Hooks
- Pre-commit conflict check
- Post-edit dependency update
- Automated workflow integration

### Phase 3 (Q1 2026)

- Line-level conflict analysis
- Git diff integration
- LLM-based dependency inference
- Team collaboration features

### v1.0 Target

**Q2 2026**: Stable release with:
- ✅ Knowledge Base (Phase 0-1)
- ✅ Task Management (Phase 1)
- ✅ Conflict Detection (Phase 2)
- 🔄 Drift Detection (Phase 2)
- 🔄 Event Logging (Phase 2)
- 📋 Team Features (Phase 3)

---

## 🙏 Acknowledgments

### Contributors

- Lead Development: Nakishiyama
- Testing: Automated CI/CD + Manual QA
- Documentation: Community feedback
- Architecture: Technical design reviews

### Beta Testers

Thank you to our beta testing community for feedback on:
- CLI usability
- MCP tool integration
- Performance optimization
- Documentation clarity

---

## 📞 Support

### Getting Help

- **Documentation**: https://github.com/nakishiyaman/clauxton/tree/main/docs
- **Issues**: https://github.com/nakishiyaman/clauxton/issues
- **Discussions**: https://github.com/nakishiyaman/clauxton/discussions

### Reporting Bugs

Found a bug in v0.9.0-beta? Please report:

1. **Check existing issues**: Search for similar reports
2. **Create detailed report**: Include steps to reproduce
3. **Provide context**: Version, OS, Python version
4. **Expected vs. actual**: What you expected vs. what happened

### Feature Requests

Want a feature? Submit an enhancement request:

1. **Describe use case**: Why you need it
2. **Propose solution**: How you envision it working
3. **Alternatives considered**: Other approaches
4. **Willingness to help**: Can you contribute?

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🎊 Thank You!

Thank you for using Clauxton v0.9.0-beta! We're excited to bring conflict prevention to your development workflow.

**Happy coding, and may your merges be conflict-free!** 🚀

---

**Release**: v0.9.0-beta
**Date**: October 20, 2025
**Project**: Clauxton - Context that persists for Claude Code
**Website**: https://github.com/nakishiyaman/clauxton
