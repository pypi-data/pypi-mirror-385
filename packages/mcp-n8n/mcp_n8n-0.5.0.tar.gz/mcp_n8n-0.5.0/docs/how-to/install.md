# How to Install mcp-n8n

---
title: "How to Install mcp-n8n"
type: how-to
audience: intermediate
category: installation
tags: ["installation", "pip", "development", "virtual-environment"]
source: "README.md"
last_updated: 2025-10-21
---

## Problem

You need to install mcp-n8n to use it as an MCP gateway server, and you're deciding between:
- **Production install** from PyPI (for using mcp-n8n)
- **Development install** from source (for contributing to mcp-n8n)
- **Virtual environment install** (for isolated environments)

**Common scenarios:**
- "I want to use mcp-n8n with Claude Desktop"
- "I want to contribute code to mcp-n8n"
- "I need multiple versions for different projects"

## Solution Overview

mcp-n8n supports three installation approaches:
1. **Production Install** (pip) - Recommended for most users
2. **Development Install** (editable) - For contributors
3. **Virtual Environment Install** - For isolation

## Prerequisites

- [ ] **Python 3.12+** installed (`python --version`)
- [ ] **pip** package manager available (`pip --version`)
- [ ] **git** (for development install)
- [ ] **just** (optional, for development - `brew install just`)

---

## Approach 1: Production Install (Recommended)

**When to use:** You want to use mcp-n8n as an MCP server with Claude Desktop or Cursor

**Pros:**
- ✅ Fastest installation (one command)
- ✅ Stable release from PyPI
- ✅ All dependencies handled automatically
- ✅ Easy to update (`pip install --upgrade mcp-n8n`)

**Cons:**
- ❌ Can't modify source code
- ❌ No development tools included

### Steps

**1. Install from PyPI:**

```bash
pip install mcp-n8n
```

**2. Verify installation:**

```bash
# Check version
mcp-n8n --version

# Show package info
pip show mcp-n8n
```

**Expected output:**
```
Name: mcp-n8n
Version: 0.4.0
Summary: Pattern P5 (Gateway & Aggregator) MCP server
...
```

**3. Configure environment variables:**

```bash
# Create .env file or export variables
export ANTHROPIC_API_KEY=your_anthropic_key
export CODA_API_KEY=your_coda_key  # Optional
```

**4. Run the gateway:**

```bash
mcp-n8n
```

### Verification

Test that mcp-n8n works:

```bash
# In a separate terminal, test import
python -c "import mcp_n8n; print(mcp_n8n.__version__)"
```

Expected output:
```
0.4.0
```

---

## Approach 2: Development Install

**When to use:** You want to contribute code, modify mcp-n8n, or test unreleased features

**Pros:**
- ✅ Editable source code (changes take effect immediately)
- ✅ Development tools included (pytest, ruff, mypy, pre-commit)
- ✅ Access to tests and documentation source
- ✅ Can run tests and pre-commit hooks

**Cons:**
- ❌ Longer setup time
- ❌ More disk space required
- ❌ Requires git

### Steps

**1. Clone repository with submodules:**

```bash
# Clone with submodules (includes chora-composer)
git clone --recurse-submodules https://github.com/yourusername/mcp-n8n.git
cd mcp-n8n

# If you already cloned, initialize submodules
git submodule update --init --recursive
```

**2. Automated setup (recommended):**

```bash
# One-command setup (creates venv, installs deps, sets up hooks)
./scripts/setup.sh
```

This script will:
- Create virtual environment (`.venv/`)
- Install development dependencies
- Install pre-commit hooks
- Run smoke tests

**3. Manual setup (alternative):**

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

**4. Verify development environment:**

```bash
# Run smoke tests
just smoke
# OR
pytest tests/smoke/ -v

# Run linting
just lint

# Check that mcp-n8n command works
mcp-n8n --version
```

### Verification

Test development setup:

```bash
# Verify editable install
pip show mcp-n8n
# Should show: Location: /path/to/mcp-n8n/src

# Run full test suite
just test

# Check pre-commit hooks
pre-commit run --all-files
```

Expected: All checks pass ✅

---

## Approach 3: Virtual Environment Install

**When to use:** You need isolated environments for different projects or Python versions

**Pros:**
- ✅ Isolated from system Python
- ✅ Different versions per project
- ✅ No conflicts with other packages
- ✅ Easy to delete/recreate

**Cons:**
- ❌ Must activate venv before using
- ❌ Separate install per environment

### Steps

**1. Create virtual environment:**

```bash
# Create venv in project directory
python -m venv mcp-n8n-env

# OR create in centralized location
python -m venv ~/.virtualenvs/mcp-n8n
```

**2. Activate virtual environment:**

```bash
# macOS/Linux
source mcp-n8n-env/bin/activate

# Windows
mcp-n8n-env\Scripts\activate

# Verify activation (prompt should change)
which python  # Should point to venv python
```

**3. Install mcp-n8n:**

```bash
# Production install in venv
pip install mcp-n8n

# OR development install in venv
pip install -e ".[dev]"
```

**4. Use mcp-n8n:**

```bash
# Run gateway (venv must be activated)
mcp-n8n

# Or use full path without activation
/path/to/mcp-n8n-env/bin/mcp-n8n
```

**5. Deactivate when done:**

```bash
deactivate
```

### Verification

```bash
# Check venv is active
echo $VIRTUAL_ENV
# Should show: /path/to/mcp-n8n-env

# Verify mcp-n8n installed in venv
pip list | grep mcp-n8n
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `command not found: mcp-n8n` | Not in PATH or venv not activated | Activate venv or reinstall |
| `ModuleNotFoundError: No module named 'mcp_n8n'` | Package not installed | `pip install mcp-n8n` |
| `Permission denied` | Installing to system Python | Use `pip install --user mcp-n8n` or venv |
| `git: command not found` | Git not installed | Install git first: `brew install git` |
| Submodule errors | Submodules not initialized | `git submodule update --init --recursive` |
| Pre-commit hook failures | Code doesn't meet standards | `just lint-fix` to auto-fix |

### Common Issues

**Problem:** "pip install mcp-n8n" fails with dependency conflicts

**Diagnosis:**
```bash
pip install mcp-n8n --verbose
# Check error messages for conflicting packages
```

**Solution:**
```bash
# Option 1: Use fresh venv
python -m venv fresh-env
source fresh-env/bin/activate
pip install mcp-n8n

# Option 2: Upgrade pip
pip install --upgrade pip setuptools wheel
pip install mcp-n8n
```

---

**Problem:** Development install fails during `./scripts/setup.sh`

**Diagnosis:**
```bash
# Run setup script with verbose output
bash -x ./scripts/setup.sh
```

**Solution:**
```bash
# Manual setup instead
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install
```

---

**Problem:** "mcp-n8n" command works in terminal but not in Claude Desktop config

**Cause:** Claude Desktop doesn't use your shell's PATH

**Solution:**
```bash
# Use absolute path in Claude Desktop config
which mcp-n8n
# Copy the full path, e.g., /Users/you/.local/bin/mcp-n8n

# Update claude_desktop_config.json:
{
  "mcpServers": {
    "mcp-n8n": {
      "command": "/Users/you/.local/bin/mcp-n8n",  # Full path
      "args": []
    }
  }
}
```

---

## Best Practices

### ✅ DO

**1. Use virtual environments:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install mcp-n8n
```

**2. Pin versions in requirements:**
```bash
# requirements.txt
mcp-n8n==0.4.0
```

**3. Upgrade regularly:**
```bash
pip install --upgrade mcp-n8n
```

**4. Verify after install:**
```bash
mcp-n8n --version
python -c "import mcp_n8n; print(mcp_n8n.__version__)"
```

**5. Use justfile for development:**
```bash
just setup   # One-command setup
just verify  # Verify installation
```

### ❌ DON'T

**1. Don't install to system Python (macOS):**
```bash
# ❌ BAD (modifies system Python)
sudo pip install mcp-n8n

# ✅ GOOD (use venv or --user)
pip install --user mcp-n8n
```

**2. Don't mix pip and poetry/conda:**
```bash
# ❌ BAD
conda install mcp-n8n  # Not available
pip install mcp-n8n    # May conflict

# ✅ GOOD (pick one)
pip install mcp-n8n    # In pip environment
```

**3. Don't skip pre-commit hooks (dev install):**
```bash
# ❌ BAD
git commit --no-verify

# ✅ GOOD
pre-commit run --all-files  # Fix issues first
git commit
```

**4. Don't forget to activate venv:**
```bash
# ❌ BAD
# (venv not activated, installs to wrong location)
pip install mcp-n8n

# ✅ GOOD
source .venv/bin/activate  # Activate first
pip install mcp-n8n
```

---

## Upgrading

### Production Upgrade

```bash
# Upgrade to latest version
pip install --upgrade mcp-n8n

# Upgrade to specific version
pip install --upgrade mcp-n8n==0.5.0

# Verify upgrade
pip show mcp-n8n | grep Version
```

### Development Upgrade

```bash
# Pull latest changes
git pull origin main

# Update submodules
git submodule update --remote

# Reinstall dependencies (in case they changed)
pip install -e ".[dev]"

# Run tests to verify
just test
```

---

## Uninstalling

### Remove Production Install

```bash
# Uninstall package
pip uninstall mcp-n8n

# Verify removal
pip show mcp-n8n
# Should show: WARNING: Package(s) not found: mcp-n8n
```

### Remove Development Install

```bash
# Uninstall package
pip uninstall mcp-n8n

# Remove repository (optional)
cd ..
rm -rf mcp-n8n/

# Deactivate and remove venv (if not in repo)
deactivate
rm -rf ~/.virtualenvs/mcp-n8n  # If you created it there
```

---

## Related Documentation

- **[Tutorial: Getting Started](../tutorials/getting-started.md)** - Quick start guide
- **[How-To: Setup Claude Desktop](setup-claude-desktop.md)** - Claude Desktop configuration
- **[How-To: Setup Cursor](setup-cursor.md)** - Cursor editor configuration
- **[Reference: Configuration](../reference/configuration.md)** - Environment variables
- **[dev-docs/DEVELOPMENT.md](../../dev-docs/DEVELOPMENT.md)** - Developer deep dive

---

**Source:** README.md
**Last Updated:** 2025-10-21
