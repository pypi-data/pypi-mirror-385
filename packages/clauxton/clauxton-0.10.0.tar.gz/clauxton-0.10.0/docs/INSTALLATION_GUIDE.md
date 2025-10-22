# Clauxton Installation Guide

**Version**: v0.9.0-beta
**Date**: 2025-10-20

---

## 📋 Table of Contents

1. [Understanding Clauxton's Deployment Model](#understanding-clauxtons-deployment-model)
2. [Installation Methods](#installation-methods)
3. [Shell Alias Setup (Recommended)](#shell-alias-setup-recommended)
4. [Virtual Environment Isolation Explained](#virtual-environment-isolation-explained)
5. [Troubleshooting](#troubleshooting)

---

## Understanding Clauxton's Deployment Model

Clauxton is a **tool** (like `git`, `npm`, or `docker`), not a **library** (like `requests` or `pandas`).

### Tool vs Library

| Type | Examples | Installation | Usage |
|------|----------|--------------|-------|
| **Library** | requests, pandas, flask | Per-project venv | `import requests` in code |
| **Tool** | git, npm, clauxton | One installation, globally accessible | CLI command from any directory |

**Key difference**:
- **Libraries**: Each project has its own venv with its own copy
- **Tools**: One installation shared across all projects

---

## Installation Methods

### Method 1: Shell Alias (Recommended)

Best for: Development, multiple projects, MCP integration

```bash
# For bash users
echo "alias clauxton='/home/kishiyama-n/workspace/projects/clauxton/.venv/bin/clauxton'" >> ~/.bashrc
source ~/.bashrc

# For zsh users
echo "alias clauxton='/home/kishiyama-n/workspace/projects/clauxton/.venv/bin/clauxton'" >> ~/.zshrc
source ~/.zshrc
```

**Advantages**:
- ✅ Works from any directory
- ✅ No need to activate venv
- ✅ No impact on project environments
- ✅ Fully compatible with MCP integration

**Verification**:
```bash
cd ~/workspace/projects/any-project
clauxton --version
# Output: clauxton, version 0.9.0-beta
```

### Method 2: System-Wide Install

Best for: Single-user systems, production servers

```bash
cd /home/kishiyama-n/workspace/projects/clauxton
pip install --user -e .
```

**Advantages**:
- ✅ `clauxton` command globally available
- ✅ Installed in `~/.local/bin/clauxton`

**Verification**:
```bash
which clauxton
# Output: /home/kishiyama-n/.local/bin/clauxton
```

### Method 3: Activate Venv Each Time

Best for: Development work on Clauxton itself

```bash
cd /home/kishiyama-n/workspace/projects/clauxton
source .venv/bin/activate
clauxton --version
```

**Disadvantages**:
- ❌ Must activate venv in each terminal session
- ❌ Not convenient for MCP integration

---

## Shell Alias Setup (Recommended)

### Step-by-Step Instructions

#### 1. Determine Your Shell

```bash
echo $SHELL
# Output: /bin/bash  → Use ~/.bashrc
# Output: /bin/zsh   → Use ~/.zshrc
```

#### 2. Get Clauxton Path

```bash
cd /home/kishiyama-n/workspace/projects/clauxton
echo "$(pwd)/.venv/bin/clauxton"
# Copy this path
```

#### 3. Add Alias

**For bash**:
```bash
echo "alias clauxton='/home/kishiyama-n/workspace/projects/clauxton/.venv/bin/clauxton'" >> ~/.bashrc
source ~/.bashrc
```

**For zsh**:
```bash
echo "alias clauxton='/home/kishiyama-n/workspace/projects/clauxton/.venv/bin/clauxton'" >> ~/.zshrc
source ~/.zshrc
```

#### 4. Verify Installation

```bash
# Test from any directory
cd ~/workspace/projects/todo
clauxton --version

# Expected output:
# clauxton, version 0.9.0-beta
```

#### 5. Initialize Project

```bash
cd ~/workspace/projects/todo
clauxton init

# Expected output:
# ✓ Initialized Clauxton
#   Location: /home/kishiyama-n/workspace/projects/todo/.clauxton
#   Knowledge Base: /home/kishiyama-n/workspace/projects/todo/.clauxton/knowledge-base.yml
```

---

## Virtual Environment Isolation Explained

### Common Concern

> "Won't Clauxton's venv be polluted by project dependencies?"

**Answer**: No, because of complete code/data separation.

### How It Works

```
# Clauxton Installation (ONE location)
/home/kishiyama-n/workspace/projects/clauxton/
├── .venv/                          # Clauxton's isolated venv
│   └── lib/python3.*/site-packages/
│       ├── clauxton/               # Clauxton code
│       ├── pydantic/               # Clauxton dependency
│       ├── click/                  # Clauxton dependency
│       └── pyyaml/                 # Clauxton dependency
└── clauxton/                       # Source code

# Project A (DATA only, NO code)
~/workspace/projects/todo/
├── .venv/                          # Project A's venv (IGNORED by Clauxton)
│   └── django, requests, ...       # Project A's dependencies
└── .clauxton/
    ├── knowledge-base.yml          # YAML data only
    └── tasks.yml                   # YAML data only

# Project B (DATA only, NO code)
~/workspace/projects/shopping-app/
├── .venv/                          # Project B's venv (IGNORED by Clauxton)
│   └── flask, sqlalchemy, ...      # Project B's dependencies
└── .clauxton/
    ├── knowledge-base.yml          # YAML data only
    └── tasks.yml                   # YAML data only
```

### Execution Flow

```bash
# You run Clauxton in Project A
cd ~/workspace/projects/todo
clauxton task list

# What happens:
1. /home/kishiyama-n/workspace/projects/clauxton/.venv/bin/python starts
2. Loads clauxton package from Clauxton's venv
3. Reads ~/workspace/projects/todo/.clauxton/tasks.yml (DATA only)
4. Displays results

# Project A's code is NEVER executed
# Project A's venv is NEVER accessed
# Project A's dependencies are NEVER imported
```

### MCP Integration with Multiple Projects

The `${workspaceFolder}` variable in MCP config provides automatic project switching:

```json
{
  "mcpServers": {
    "clauxton": {
      "command": "/home/kishiyama-n/workspace/projects/clauxton/.venv/bin/python",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}",  // ← Auto-switches per project
      "env": {
        "PYTHONPATH": "/home/kishiyama-n/workspace/projects/clauxton"
      }
    }
  }
}
```

**How it works**:

```
Claude Code opens ~/workspace/projects/todo
  → cwd = ~/workspace/projects/todo
  → Clauxton uses todo/.clauxton/

Claude Code opens ~/workspace/projects/shopping-app
  → cwd = ~/workspace/projects/shopping-app
  → Clauxton uses shopping-app/.clauxton/
```

### Why No Pollution Risk

1. **Code Separation**: Projects contain only `.clauxton/` data directory (YAML files)
2. **Venv Isolation**: Clauxton runs in its own venv, never accesses project venvs
3. **Data-Only Operations**: Clauxton only reads/writes YAML files, doesn't import project code
4. **No Cross-Contamination**: Each project's `.clauxton/` is independent

---

## Troubleshooting

### Q1: `clauxton: command not found` after adding alias

**Cause**: Shell config not reloaded

**Solution**:
```bash
# Reload shell config
source ~/.bashrc  # or ~/.zshrc

# Or open a new terminal
```

### Q2: Alias doesn't work in new terminal

**Cause**: Alias not saved to shell config file

**Solution**:
```bash
# Check if alias is in config file
grep "alias clauxton" ~/.bashrc

# If not found, add it again
echo "alias clauxton='/home/kishiyama-n/workspace/projects/clauxton/.venv/bin/clauxton'" >> ~/.bashrc
source ~/.bashrc
```

### Q3: Different Python version in project

**Concern**: "My project uses Python 3.11, but Clauxton uses Python 3.10. Will this cause issues?"

**Answer**: No, because:
- Clauxton runs in its own venv with its own Python
- Project runs in its own venv with its own Python
- They never interact or share dependencies

**Example**:
```
Clauxton: /home/kishiyama-n/workspace/projects/clauxton/.venv/bin/python (3.10)
Project A: ~/workspace/projects/todo/.venv/bin/python (3.11)
Project B: ~/workspace/projects/shopping-app/.venv/bin/python (3.9)

All work independently ✅
```

### Q4: Project has a package with the same name as Clauxton's dependency

**Scenario**:
```
Clauxton's venv: pydantic==2.5.0
Project's venv: pydantic==1.10.0 (old version)
```

**Answer**: No conflict, because:
- Clauxton uses `/home/kishiyama-n/workspace/projects/clauxton/.venv/lib/python3.*/site-packages/pydantic` (2.5.0)
- Project uses `~/workspace/projects/todo/.venv/lib/python3.*/site-packages/pydantic` (1.10.0)
- They are in separate directories and never imported together

### Q5: Can I have multiple Clauxton installations?

**Answer**: Possible but not recommended

**One installation (recommended)**:
```
/home/kishiyama-n/workspace/projects/clauxton/
  → All projects use this via alias or MCP config
```

**Multiple installations (not recommended)**:
```
/home/kishiyama-n/workspace/clauxton-v1/
/home/kishiyama-n/workspace/clauxton-v2/
  → Confusing, no benefit
```

---

## Summary

### Key Takeaways

1. **Clauxton is a tool, not a library** - Installed once, used everywhere
2. **Shell alias is the recommended method** - Convenient, clean, compatible
3. **No pollution risk** - Complete code/data separation
4. **Each project has only data** - `.clauxton/` contains YAML files only
5. **MCP automatically switches projects** - `${workspaceFolder}` handles isolation

### Next Steps

After installation:

1. ✅ Verify: `clauxton --version`
2. ✅ Initialize project: `cd your-project && clauxton init`
3. ✅ Set up MCP integration: See [MCP_INTEGRATION_GUIDE.md](MCP_INTEGRATION_GUIDE.md)
4. ✅ Start using: See [HOW_TO_USE_v0.9.0-beta.md](HOW_TO_USE_v0.9.0-beta.md)

---

## Related Documentation

- **[MCP Integration Guide](MCP_INTEGRATION_GUIDE.md)** - Claude Code integration (23KB)
- **[How to Use v0.9.0-beta](HOW_TO_USE_v0.9.0-beta.md)** - Complete usage guide (15KB)
- **[Quick Start](quick-start.md)** - Quick introduction (18KB)
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions (26KB)

---

**Clauxton v0.9.0-beta - Production Ready** ✅

*Generated: 2025-10-20*
*Status: Beta Release*
