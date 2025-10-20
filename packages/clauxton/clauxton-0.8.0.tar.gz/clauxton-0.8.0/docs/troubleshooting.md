# Troubleshooting Guide

Common issues and solutions for Clauxton users.

---

## Installation Issues

### "Command not found: clauxton"

**Problem**: After installation, `clauxton` command is not recognized.

**Solutions**:

1. **Check installation**:
   ```bash
   pip list | grep clauxton
   ```
   If not listed, reinstall:
   ```bash
   pip install -e .
   ```

2. **Check PATH**:
   ```bash
   which clauxton
   ```
   If not in PATH, add Python scripts directory:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **Use module syntax**:
   ```bash
   python -m clauxton.cli.main --help
   ```

### "ModuleNotFoundError: No module named 'clauxton'"

**Problem**: Python cannot find the clauxton module.

**Solutions**:

1. **Verify installation directory**:
   ```bash
   pip show clauxton
   ```

2. **Check Python version**:
   ```bash
   python --version  # Should be 3.9+
   ```

3. **Reinstall with correct Python**:
   ```bash
   python3 -m pip install -e .
   ```

---

## Initialization Issues

### "Error: .clauxton/ already exists"

**Problem**: Trying to initialize in an already-initialized project.

**Solutions**:

1. **Skip initialization** (already initialized):
   ```bash
   # Just start using clauxton
   clauxton kb list
   ```

2. **Force re-initialization** (WARNING: overwrites existing data):
   ```bash
   clauxton init --force
   ```

3. **Check if .clauxton is from another project**:
   ```bash
   cat .clauxton/knowledge-base.yml
   ```

### "Permission denied: .clauxton/"

**Problem**: Cannot create or access .clauxton directory.

**Solutions**:

1. **Check directory permissions**:
   ```bash
   ls -la .clauxton/
   ```

2. **Fix permissions**:
   ```bash
   chmod 700 .clauxton/
   chmod 600 .clauxton/knowledge-base.yml
   chmod 600 .clauxton/tasks.yml
   ```

3. **Check ownership**:
   ```bash
   ls -l .clauxton/
   # Should be owned by your user
   ```

---

## Knowledge Base Issues

### "Error: .clauxton/ not found"

**Problem**: Running commands in non-initialized directory.

**Solution**:
```bash
clauxton init
```

### "No results found" when searching

**Problem**: Search query returns no results.

**Solutions**:

1. **Try broader keywords**:
   ```bash
   # Instead of "FastAPI framework async"
   clauxton kb search "FastAPI"
   ```

2. **Check spelling**:
   ```bash
   # List all entries first
   clauxton kb list
   ```

3. **Search without category filter**:
   ```bash
   # Remove --category to search all
   clauxton kb search "API"
   ```

### "Error: Entry not found: KB-YYYYMMDD-NNN"

**Problem**: Entry ID doesn't exist.

**Solutions**:

1. **List all entries to find correct ID**:
   ```bash
   clauxton kb list
   ```

2. **Search by keyword instead**:
   ```bash
   clauxton kb search "keyword"
   ```

3. **Check YAML file directly**:
   ```bash
   cat .clauxton/knowledge-base.yml
   ```

### "YAML file corrupted" or parsing errors

**Problem**: knowledge-base.yml has syntax errors.

**Solutions**:

1. **Restore from backup**:
   ```bash
   cp .clauxton/knowledge-base.yml.bak .clauxton/knowledge-base.yml
   ```

2. **Validate YAML syntax**:
   ```bash
   python -c "import yaml; yaml.safe_load(open('.clauxton/knowledge-base.yml'))"
   ```

3. **Manual fix** (if you know YAML):
   ```bash
   # Edit with proper YAML editor
   nano .clauxton/knowledge-base.yml
   ```

---

## Task Management Issues

### "Error: Task not found: TASK-NNN"

**Problem**: Task ID doesn't exist.

**Solutions**:

1. **List all tasks**:
   ```bash
   clauxton task list
   ```

2. **Check task ID format** (must be TASK-001, TASK-002, etc.):
   ```bash
   # ❌ Wrong
   clauxton task get task-1

   # ✅ Correct
   clauxton task get TASK-001
   ```

### "Error: Circular dependency detected"

**Problem**: Task dependencies form a cycle.

**Example**:
```
TASK-001 depends on TASK-002
TASK-002 depends on TASK-001  # Circular!
```

**Solutions**:

1. **Remove circular dependency**:
   ```bash
   # List dependencies
   clauxton task get TASK-001
   clauxton task get TASK-002

   # Identify and break the cycle
   # (Currently requires manual YAML edit)
   ```

2. **Redesign task dependencies**:
   - Task A → Task B → Task C (linear)
   - Not: Task A → Task B → Task A (circular)

### "Error: Cannot delete task with dependents"

**Problem**: Trying to delete a task that other tasks depend on.

**Solution**:

1. **Find dependent tasks**:
   ```bash
   clauxton task list
   # Look for tasks with "Depends on: TASK-XXX"
   ```

2. **Delete dependents first**:
   ```bash
   clauxton task delete TASK-002 --yes  # Dependent task
   clauxton task delete TASK-001 --yes  # Original task
   ```

3. **Or update dependencies**:
   ```bash
   # Remove dependency from TASK-002
   # (Currently requires manual YAML edit)
   ```

### "No tasks ready to work on" but tasks exist

**Problem**: `clauxton task next` shows no tasks, but `clauxton task list` shows pending tasks.

**Possible Causes**:

1. **All tasks have unmet dependencies**:
   ```bash
   clauxton task list --status pending
   # Check "Depends on" field
   ```

2. **All tasks are in_progress or completed**:
   ```bash
   clauxton task list --status pending
   # Should show only pending tasks
   ```

**Solution**:
- Complete blocking tasks first, or
- Mark blocking tasks as completed if already done

---

## MCP Server Issues

### "MCP server not found"

**Problem**: Claude Code cannot find the Clauxton MCP server.

**Solutions**:

1. **Verify installation**:
   ```bash
   python -m clauxton.mcp.server --help
   ```

2. **Check MCP config** (`.claude-plugin/mcp-servers.json`):
   ```json
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

3. **Restart Claude Code** after config changes.

### "MCP server crashes on startup"

**Problem**: MCP server starts but immediately crashes.

**Solutions**:

1. **Check Python version**:
   ```bash
   python --version  # Must be 3.9+
   ```

2. **Check dependencies**:
   ```bash
   pip install mcp pydantic click pyyaml
   ```

3. **Test server manually**:
   ```bash
   python -m clauxton.mcp.server
   # Should wait for JSON-RPC input
   ```

### "MCP tools return errors"

**Problem**: MCP tools execute but return errors.

**Solutions**:

1. **Initialize project**:
   ```bash
   cd /path/to/project
   clauxton init
   ```

2. **Check working directory**:
   - MCP server uses current working directory
   - Ensure `.clauxton/` exists in CWD

3. **Check file permissions**:
   ```bash
   ls -la .clauxton/
   ```

---

## Performance Issues

### "Commands are slow"

**Problem**: CLI commands take several seconds.

**Possible Causes**:

1. **Large Knowledge Base** (100+ entries):
   - Search is O(n) linear scan
   - Expected in Phase 1

2. **Large task.yml file** (50+ tasks):
   - Loading and parsing takes time

**Solutions**:

1. **Use filters**:
   ```bash
   # Instead of listing all
   clauxton kb list --category architecture
   ```

2. **Clean up old entries**:
   ```bash
   # Delete completed tasks
   clauxton task list --status completed
   clauxton task delete TASK-XXX --yes
   ```

3. **Wait for Phase 2** (TF-IDF search optimization)

---

## Data Issues

### "Lost data after crash"

**Problem**: Data lost or corrupted after system crash.

**Solutions**:

1. **Restore from .bak file**:
   ```bash
   cp .clauxton/knowledge-base.yml.bak .clauxton/knowledge-base.yml
   cp .clauxton/tasks.yml.bak .clauxton/tasks.yml
   ```

2. **Restore from git** (if committed):
   ```bash
   git checkout .clauxton/
   ```

3. **Prevention**: Commit `.clauxton/` to git regularly:
   ```bash
   git add .clauxton/
   git commit -m "Update Knowledge Base and tasks"
   ```

### "Duplicate entry IDs"

**Problem**: Two entries have the same ID.

**Cause**: Manual YAML editing or concurrent access.

**Solution**:

1. **Edit YAML manually** to fix duplicate IDs:
   ```bash
   nano .clauxton/knowledge-base.yml
   # Find duplicates and renumber
   ```

2. **Or restore from backup**:
   ```bash
   cp .clauxton/knowledge-base.yml.bak .clauxton/knowledge-base.yml
   ```

---

## Git and Version Control

### "Should I commit .clauxton/?"

**Answer**: **Yes!** The Knowledge Base and tasks should be version-controlled.

**Recommended .gitignore**:
```gitignore
# Clauxton backups (no need to commit these)
.clauxton/*.bak
```

**Recommended workflow**:
```bash
# After adding KB entries or tasks
git add .clauxton/
git commit -m "docs: Add API architecture decisions to KB"
git push
```

### "Merge conflicts in .clauxton/"

**Problem**: Two team members edited Knowledge Base simultaneously.

**Solutions**:

1. **Accept both changes**:
   ```bash
   # Manually merge YAML
   git checkout --ours .clauxton/knowledge-base.yml
   # Then manually add entries from --theirs
   ```

2. **Use conflict resolution**:
   ```bash
   git mergetool
   # Use YAML-aware merge tool
   ```

3. **Prevention**: Coordinate KB updates with team

---

## FAQ

### How do I back up my Knowledge Base?

```bash
# Manual backup
cp .clauxton/knowledge-base.yml ~/backups/kb-backup-$(date +%Y%m%d).yml

# Or use git
git add .clauxton/
git commit -m "Backup Knowledge Base"
```

### Can I use Clauxton with multiple projects?

Yes! Each project has its own `.clauxton/` directory. Just run `clauxton init` in each project.

### How do I export my Knowledge Base?

The Knowledge Base is already in YAML format:
```bash
# Copy the file
cp .clauxton/knowledge-base.yml ~/exported-kb.yml

# Or convert to JSON
python -c "import yaml, json; print(json.dumps(yaml.safe_load(open('.clauxton/knowledge-base.yml')), indent=2))" > kb.json
```

### Can I edit .clauxton/ files manually?

Yes, but be careful:
- ✅ **Safe**: Adding entries, editing content
- ⚠️ **Careful**: Changing IDs, modifying structure
- ❌ **Dangerous**: Breaking YAML syntax

Always back up before manual edits:
```bash
cp .clauxton/knowledge-base.yml .clauxton/knowledge-base.yml.backup
```

### How do I reset Clauxton?

```bash
# Delete .clauxton directory
rm -rf .clauxton/

# Re-initialize
clauxton init
```

**WARNING**: This deletes all data! Back up first.

### What's the maximum number of KB entries?

No hard limit, but performance degrades:
- ✅ **1-50 entries**: Fast
- ⚠️ **50-200 entries**: Acceptable
- ❌ **200+ entries**: Slow search (wait for Phase 2 optimization)

### Can I use Clauxton without Claude Code?

Yes! Clauxton CLI works standalone:
```bash
clauxton kb add
clauxton task list
# etc.
```

MCP server is optional for Claude Code integration.

---

## Getting Help

- **GitHub Issues**: https://github.com/nakishiyaman/clauxton/issues
- **Documentation**: See `docs/` directory
- **Quick Start**: `docs/quick-start.md`
- **MCP Server Guide**: `docs/mcp-server.md`

---

## Search Issues

### "ModuleNotFoundError: No module named 'sklearn'"

**Problem**: `scikit-learn` not installed.

```
ImportError: scikit-learn is required for TF-IDF search.
Install with: pip install scikit-learn
```

**Solution**:
```bash
pip install scikit-learn
```

**Workaround**: Clauxton automatically falls back to simple keyword search. No action needed unless you want TF-IDF search features (relevance ranking).

---

### "Search results seem random or in wrong order"

**Problem**: Expecting alphabetical or date order, but getting relevance order.

**Cause**: Clauxton uses **TF-IDF relevance ranking**. Results are sorted by how relevant they are to your query, not by title or date.

**Example**:
- Entry A: "FastAPI" mentioned 5 times → Higher relevance score
- Entry B: "FastAPI" mentioned 1 time → Lower relevance score
- Result: Entry A appears first (more relevant)

**Solution**: This is expected behavior! TF-IDF finds the most relevant entries first.

**Details**:
- **Relevance factors**:
  - Keyword frequency in entry (how often term appears)
  - Keyword rarity across all entries (rare terms score higher)
  - Multiple occurrences boost score

See [Search Algorithm](search-algorithm.md) for technical details.

---

### "Empty search results for valid query"

**Problem**: Search returns no results even though keyword exists.

**Possible causes**:

1. **All stopwords**: Query contains only common words
   ```bash
   clauxton kb search "the a an is"  # Returns empty (all filtered out)
   ```

2. **Wrong category**: Category filter too restrictive
   ```bash
   clauxton kb search "API" --category decision  # May be in "architecture" instead
   ```

3. **Case mismatch** (unlikely - search is case-insensitive)

**Debug**:
```bash
# Try without category filter
clauxton kb search "your query"

# List all entries to verify content
clauxton kb list

# Search with broader terms
clauxton kb search "api"  # Instead of specific framework name
```

---

### "Search is slow with large Knowledge Base"

**Problem**: Search takes > 1 second with 200+ entries.

**Expected performance**:
- Small KB (< 50 entries): Search < 5ms
- Medium KB (50-200 entries): Search < 10ms
- Large KB (200+ entries): Search < 20ms

**If slower than expected**:

1. **Check scikit-learn is installed**:
   ```bash
   python -c "import sklearn; print(f'scikit-learn {sklearn.__version__} installed')"
   ```

2. **Verify TF-IDF is being used**:
   - Check for fallback warnings in output
   - Simple search is slower on large datasets

3. **Consider KB size**:
   - 1000+ entries may need performance tuning (future enhancement)

---

## Debug Mode

Enable verbose output for troubleshooting:

```bash
# Set environment variable
export CLAUXTON_DEBUG=1

# Run command
clauxton kb add

# Check logs
# (Currently no structured logging - coming in Phase 2)
```

---

**Last Updated**: Phase 1 Week 9 (v0.8.0+)
