# Installation Guide

Complete installation instructions for Clauxton.

---

## System Requirements

### Required

- **Python**: 3.11 or later
- **pip**: Latest version recommended

### Recommended

- **Git**: For version control integration
- **Virtual Environment**: venv or conda

### Supported Platforms

- ✅ Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+)
- ✅ macOS (macOS 11 Big Sur or later)
- ✅ Windows (Windows 10/11 with WSL2 recommended)

---

## Installation Methods

### Method 1: Install from PyPI (Recommended)

**Production-ready v0.8.0 - Stable Release**

#### Quick Install

```bash
# Install latest stable version
pip install clauxton
```

#### Verify Installation

```bash
clauxton --version
```

Expected output:
```
clauxton, version 0.8.0
```

#### Install Specific Version

```bash
# Install specific version
pip install clauxton==0.8.0

# Upgrade to latest
pip install --upgrade clauxton
```

**What's Included**:
- ✅ Knowledge Base management (CRUD + TF-IDF search)
- ✅ Task Management with auto-dependencies
- ✅ MCP Server (12 tools for Claude Code)
- ✅ All dependencies (scikit-learn, numpy, pydantic, click, pyyaml, mcp, gitpython)

---

### Method 2: Install from Source (Development)

**For contributors and development purposes**

#### Step 1: Clone Repository

```bash
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton
```

#### Step 2: Create Virtual Environment (Recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (CMD):**
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

#### Step 3: Install in Editable Mode

```bash
pip install -e .
```

#### Step 4: Verify Installation

```bash
clauxton --version
```

Expected output:
```
clauxton, version 0.8.0
```

---

## Post-Installation Setup

### Verify Installation

Check that all components are working:

```bash
# Check version
clauxton --version

# View help
clauxton --help

# View Knowledge Base commands
clauxton kb --help
```

### Initialize Your First Project

Navigate to your project directory:

```bash
cd /path/to/your-project
clauxton init
```

This creates `.clauxton/` directory with Knowledge Base.

---

## Development Installation

For contributors who want to modify Clauxton:

### Step 1: Clone and Setup

```bash
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install with Dev Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- Core dependencies (pydantic, click, pyyaml, gitpython)
- Dev tools (pytest, mypy, ruff, pytest-cov)

### Step 3: Verify Dev Setup

```bash
# Run tests
pytest

# Type checking
mypy clauxton --strict

# Linting
ruff check .

# View coverage
pytest --cov=clauxton --cov-report=html
open htmlcov/index.html  # View coverage report
```

---

## Dependency Management

### Core Dependencies

Clauxton requires these packages (auto-installed with pip):

```
pydantic>=2.0       # Data validation
click>=8.1          # CLI framework
pyyaml>=6.0         # YAML processing
gitpython>=3.1      # Git integration
mcp>=1.0            # MCP server framework
scikit-learn>=1.3   # TF-IDF search algorithm
numpy>=1.24         # Required by scikit-learn
```

### Optional Dependencies

Development tools (install with `pip install -e ".[dev]"`):

```
pytest>=7.4         # Testing framework
pytest-cov>=4.1     # Coverage reporting
pytest-asyncio>=0.21  # Async test support
mypy>=1.5           # Type checking
ruff>=0.1           # Linting
types-pyyaml>=6.0   # Type stubs for PyYAML
```

---

## Platform-Specific Instructions

### macOS

#### Using Homebrew Python

```bash
# Install Python 3.11+ via Homebrew
brew install python@3.11

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Clauxton
pip install -e .
```

#### Using System Python

macOS comes with Python 3.x, but it's recommended to use Homebrew Python for better package management.

---

### Linux

#### Ubuntu/Debian

```bash
# Ensure Python 3.11+ is installed
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Clone and install
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton
python3.11 -m venv venv
source venv/bin/activate
pip install -e .
```

#### Fedora/RHEL

```bash
# Install Python 3.11+
sudo dnf install python3.11 python3-pip

# Clone and install
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton
python3.11 -m venv venv
source venv/bin/activate
pip install -e .
```

---

### Windows

#### Using WSL2 (Recommended)

Windows Subsystem for Linux provides the best experience:

1. **Install WSL2** (if not already):
   ```powershell
   wsl --install
   ```

2. **Open Ubuntu terminal** and follow Linux instructions above

#### Using Native Windows

```powershell
# Clone repository
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install
pip install -e .

# Verify
clauxton --version
```

**Note**: Some features may have limited support on native Windows. WSL2 is recommended for best experience.

---

## Troubleshooting

### "Command not found: clauxton"

**Issue**: Shell can't find the `clauxton` command.

**Solution**:
1. Ensure you've activated your virtual environment:
   ```bash
   source venv/bin/activate  # macOS/Linux
   .\venv\Scripts\Activate.ps1  # Windows
   ```

2. Check that installation succeeded:
   ```bash
   pip list | grep clauxton
   ```

3. Try running with python -m:
   ```bash
   python -m clauxton.cli.main --help
   ```

---

### "ModuleNotFoundError: No module named 'pydantic'"

**Issue**: Dependencies not installed.

**Solution**:
```bash
pip install -e .
```

Or install dependencies manually:
```bash
pip install pydantic click pyyaml gitpython
```

---

### "Permission denied" on macOS/Linux

**Issue**: Need write permissions for installation.

**Solution**:
Use a virtual environment (recommended) or install with `--user`:
```bash
pip install --user -e .
```

---

### Python Version Issues

**Issue**: System Python is too old (< 3.11).

**Solutions**:

**Option 1: Install newer Python via package manager**
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Fedora
sudo dnf install python3.11
```

**Option 2: Use pyenv**
```bash
# Install pyenv (macOS/Linux)
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.5
pyenv global 3.11.5
```

---

### Virtual Environment Activation Issues

**Issue**: Can't activate virtual environment on Windows.

**Solution (PowerShell Execution Policy)**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:
```powershell
.\venv\Scripts\Activate.ps1
```

---

## Uninstallation

### Remove Clauxton

If installed from source in editable mode:
```bash
pip uninstall clauxton
```

If installed from PyPI:
```bash
pip uninstall clauxton
```

### Clean Up Project Data

To remove Clauxton data from your projects:
```bash
# From each project directory
rm -rf .clauxton/
```

**Warning**: This will delete your Knowledge Base entries. Commit to Git first if you want to preserve them!

---

## Upgrading

### Upgrade from PyPI (Recommended)

```bash
# Upgrade to latest version
pip install --upgrade clauxton

# Check current version
clauxton --version

# Upgrade to specific version
pip install --upgrade clauxton==0.8.0
```

### Upgrade from Source

```bash
cd clauxton
git pull origin main
pip install -e . --upgrade
```

### Check Current Version

```bash
clauxton --version
```

### Version History

- **v0.8.0** (2025-10-19): TF-IDF search, Phase 1 complete
- **v0.7.0**: Task management with auto-dependencies
- **v0.1.0**: Initial release with Knowledge Base

---

## Next Steps

- [Quick Start Guide](quick-start.md) - Get started in 5 minutes
- [YAML Format Reference](yaml-format.md) - Understanding the data structure
- [Architecture](architecture.md) - How Clauxton works
- [Contributing](../CONTRIBUTING.md) - Help improve Clauxton

---

## Getting Help

- **Documentation**: [GitHub Wiki](https://github.com/nakishiyaman/clauxton/wiki)
- **Issues**: [GitHub Issues](https://github.com/nakishiyaman/clauxton/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nakishiyaman/clauxton/discussions)

---

**Ready to install?** Follow the [source installation](#method-1-install-from-source-current) to get started!
