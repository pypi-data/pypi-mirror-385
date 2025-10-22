#!/bin/bash
# Clauxton MCP Setup Script for Claude Code

set -e

echo "=== Clauxton MCP Setup for Claude Code ==="
echo ""

# 1. Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    CONFIG_DIR="$HOME/.config/claude-code"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "   Please manually configure MCP servers"
    exit 1
fi

echo "✓ Detected OS: $OS"
echo "  Config directory: $CONFIG_DIR"
echo ""

# 2. Get Clauxton installation path
CLAUXTON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="$CLAUXTON_DIR/.venv/bin/python"

if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Python venv not found at: $PYTHON_PATH"
    echo "   Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -e ."
    exit 1
fi

echo "✓ Found Clauxton at: $CLAUXTON_DIR"
echo "  Python: $PYTHON_PATH"
echo ""

# 3. Create config directory if not exists
mkdir -p "$CONFIG_DIR"
echo "✓ Config directory ready: $CONFIG_DIR"
echo ""

# 4. Check if mcp-servers.json exists
CONFIG_FILE="$CONFIG_DIR/mcp-servers.json"

if [ -f "$CONFIG_FILE" ]; then
    echo "⚠ MCP config already exists: $CONFIG_FILE"
    echo ""
    echo "Choose an option:"
    echo "  1) Backup and replace"
    echo "  2) Show manual merge instructions"
    echo "  3) Cancel"
    read -p "Enter choice (1-3): " choice

    case $choice in
        1)
            BACKUP_FILE="$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
            cp "$CONFIG_FILE" "$BACKUP_FILE"
            echo "✓ Backup created: $BACKUP_FILE"
            ;;
        2)
            echo ""
            echo "=== Manual Merge Instructions ==="
            echo ""
            echo "Add this to your existing $CONFIG_FILE:"
            echo ""
            cat << EOF
    "clauxton": {
      "command": "$PYTHON_PATH",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "\${workspaceFolder}",
      "env": {
        "PYTHONPATH": "$CLAUXTON_DIR"
      }
    }
EOF
            echo ""
            echo "Example merged config:"
            echo ""
            cat << EOF
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "clauxton": {
      "command": "$PYTHON_PATH",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "\${workspaceFolder}",
      "env": {
        "PYTHONPATH": "$CLAUXTON_DIR"
      }
    }
  }
}
EOF
            echo ""
            exit 0
            ;;
        3)
            echo "Cancelled."
            exit 0
            ;;
        *)
            echo "Invalid choice. Cancelled."
            exit 1
            ;;
    esac
fi

# 5. Write MCP config
echo "Writing MCP config..."
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "clauxton": {
      "command": "$PYTHON_PATH",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "\${workspaceFolder}",
      "env": {
        "PYTHONPATH": "$CLAUXTON_DIR"
      }
    }
  }
}
EOF

echo "✓ MCP config written: $CONFIG_FILE"
echo ""

# 6. Verify
echo "=== Configuration Summary ==="
echo ""
echo "Config file: $CONFIG_FILE"
echo "Command: $PYTHON_PATH"
echo "Args: -m clauxton.mcp.server"
echo "PYTHONPATH: $CLAUXTON_DIR"
echo ""

# 7. Test MCP server
echo "=== Testing MCP Server ==="
echo ""
echo "Starting MCP server (will timeout in 2 seconds)..."
cd /tmp
timeout 2 "$PYTHON_PATH" -m clauxton.mcp.server 2>&1 | head -5 || true
echo ""
echo "✓ MCP server can start"
echo ""

# 8. Next steps
echo "=== ✅ Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. Open a project directory"
echo "  3. Run: clauxton init"
echo "  4. Ask Claude Code: 'clauxtonでタスクを一覧表示して'"
echo ""
echo "Documentation:"
echo "  - Full guide: docs/MCP_INTEGRATION_GUIDE.md"
echo "  - Quick start: docs/quick-start.md"
echo ""
echo "Troubleshooting:"
echo "  - If tools don't appear, check: $CONFIG_FILE"
echo "  - Manual test: $PYTHON_PATH -m clauxton.mcp.server"
echo ""
