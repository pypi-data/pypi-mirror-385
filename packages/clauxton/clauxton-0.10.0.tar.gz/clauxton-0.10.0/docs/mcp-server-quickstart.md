# MCP Server Quick Start

**Get started with Clauxton MCP Server in 5 minutes**

This guide will walk you through setting up and using the Clauxton MCP Server with Claude Code.

---

## Prerequisites

- Python 3.11+
- Claude Code installed
- Clauxton installed (`pip install -e .`)

---

## Step 1: Initialize Your Project

```bash
# Navigate to your project
cd your-project

# Initialize Clauxton
clauxton init
```

**Output:**
```
✓ Initialized Clauxton
  Location: /path/to/your-project/.clauxton
  Knowledge Base: /path/to/your-project/.clauxton/knowledge-base.yml
```

---

## Step 2: Add Initial Knowledge

Let's add some architecture decisions to your Knowledge Base:

```bash
clauxton kb add
```

**Interactive prompts:**
```
Title: Use FastAPI framework
Category: architecture
Content: All backend APIs use FastAPI for async support and automatic OpenAPI docs.
Tags (comma-separated): backend,api,fastapi

✓ Added entry: KB-20251019-001
```

Add a few more:

```bash
# Database decision
clauxton kb add
# Title: PostgreSQL for production
# Category: decision
# Content: Use PostgreSQL 15+ for all production databases.
# Tags: database,postgresql

# Constraint
clauxton kb add
# Title: Support Python 3.11+
# Category: constraint
# Content: Minimum Python version is 3.11 for modern type hints.
# Tags: python,version
```

---

## Step 3: Configure Claude Code

Create `.claude-plugin/mcp-servers.json` in your project root:

```json
{
  "mcpServers": {
    "clauxton-kb": {
      "command": "python",
      "args": [
        "-m",
        "clauxton.mcp.server"
      ],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

---

## Step 4: Restart Claude Code

Restart Claude Code to load the MCP Server configuration.

---

## Step 5: Test the Integration

### Example 1: Ask About Architecture

**You**: "What's our API architecture?"

**Claude Code**:
1. Uses `kb_search(query="API architecture", category="architecture")`
2. Retrieves: KB-20251019-001 (FastAPI framework)
3. Responds: "According to your Knowledge Base (KB-20251019-001), all backend APIs use FastAPI for async support and automatic OpenAPI documentation."

---

### Example 2: Add New Decision

**You**: "Remember that we decided to use Redis for caching."

**Claude Code**:
1. Uses `kb_add(title="Redis for caching", category="decision", content="Use Redis for application caching to improve performance.", tags=["cache", "redis"])`
2. Returns: Entry ID KB-20251019-004
3. Responds: "I've added this decision to your Knowledge Base as entry KB-20251019-004."

---

### Example 3: List Constraints

**You**: "What constraints do we have in this project?"

**Claude Code**:
1. Uses `kb_list(category="constraint")`
2. Retrieves all constraint entries
3. Responds:
   ```
   You have 1 constraint in your Knowledge Base:

   KB-20251019-003: Support Python 3.11+
   - Minimum Python version is 3.11 for modern type hints.
   - Tags: python, version
   ```

---

### Example 4: Search by Tag

**You**: "Show me all database-related entries."

**Claude Code**:
1. Uses `kb_search(query="database")`
2. Retrieves entries with "database" in title, content, or tags
3. Responds:
   ```
   Found 1 database-related entry:

   KB-20251019-002: PostgreSQL for production
   - Category: decision
   - Use PostgreSQL 15+ for all production databases.
   - Tags: database, postgresql
   ```

---

## Step 6: Verify Server is Running

You can manually test the MCP Server:

```bash
# Start server (stdio mode)
python -m clauxton.mcp.server

# Server is now waiting for JSON-RPC requests
# Press Ctrl+C to stop
```

If the server starts without errors, the integration is working!

---

## Common Usage Patterns

### 1. Onboarding New Team Members

**Scenario**: New developer joins the project.

**Solution**: Ask Claude to summarize the Knowledge Base:

**You**: "Summarize our architecture decisions and constraints."

**Claude Code**:
- Uses `kb_list()` to get all entries
- Filters by `architecture` and `constraint` categories
- Provides a comprehensive summary

---

### 2. Making Decisions

**Scenario**: Discussing whether to use GraphQL or REST.

**Steps**:
1. Research options (Claude provides information)
2. Make decision: "We decided to use REST for simplicity"
3. Claude automatically saves: `kb_add(title="Use REST over GraphQL", category="decision", ...)`
4. Decision is now in Knowledge Base for future reference

---

### 3. Maintaining Consistency

**Scenario**: Working on a new feature, unsure about code patterns.

**You**: "What patterns should I follow for data access?"

**Claude Code**:
- Searches: `kb_search(query="data access", category="pattern")`
- Returns relevant patterns from your Knowledge Base
- Ensures consistency across the codebase

---

## Troubleshooting

### Issue: Claude doesn't seem to be using the Knowledge Base

**Solutions**:
1. Check `.claude-plugin/mcp-servers.json` exists
2. Restart Claude Code
3. Verify server works: `python -m clauxton.mcp.server`
4. Check `.clauxton/` directory exists: `clauxton init`

---

### Issue: "ModuleNotFoundError: No module named 'mcp'"

**Solution**:
```bash
pip install mcp
```

---

### Issue: "Knowledge Base not initialized"

**Solution**:
```bash
clauxton init
```

---

### Issue: Server starts but tools don't work

**Checklist**:
- [ ] `.clauxton/knowledge-base.yml` exists
- [ ] File permissions are correct (600/700)
- [ ] No YAML syntax errors in knowledge-base.yml
- [ ] Working directory is correct (should be project root)

**Verify**:
```bash
ls -la .clauxton/
cat .clauxton/knowledge-base.yml
```

---

## Next Steps

- [MCP Server Guide](mcp-server.md) - Complete documentation
- [YAML Format Reference](yaml-format.md) - Knowledge Base structure
- [Phase 1 Plan](phase-1-plan.md) - Upcoming features

---

## Tips

1. **Be Specific**: "Add this architecture decision" → Claude saves it
2. **Use Categories**: Organize by architecture, constraint, decision, pattern, convention
3. **Tag Everything**: Tags improve searchability
4. **Review Regularly**: `kb list` to see what's in your Knowledge Base
5. **Version Control**: Commit `.clauxton/` to Git for team sharing

---

**Ready to use Clauxton MCP Server with Claude Code!** 🚀

If you encounter issues, see the [Troubleshooting](#troubleshooting) section or [file an issue](https://github.com/nakishiyaman/clauxton/issues).
