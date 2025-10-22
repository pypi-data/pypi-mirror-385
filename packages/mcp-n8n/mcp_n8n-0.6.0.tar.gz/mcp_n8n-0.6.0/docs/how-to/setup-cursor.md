# How to Setup mcp-n8n with Cursor

---
title: "How to Setup mcp-n8n with Cursor"
type: how-to
audience: intermediate
category: configuration
tags: ["cursor", "mcp-configuration", "vscode"]
source: ".config/cursor-mcp.example.json"
last_updated: 2025-10-21
---

## Problem

You want to connect mcp-n8n to Cursor editor so the AI assistant can use MCP tools for artifact creation and data operations.

**Common scenarios:**
- "I installed mcp-n8n but Cursor doesn't see the tools"
- "I want to switch between stable (PyPI) and dev (local) modes"
- "Cursor isn't loading mcp-n8n"

## Solution Overview

Configure Cursor's MCP settings to load mcp-n8n, with options for:
- **Production mode**: Uses published package from PyPI
- **Development mode**: Uses local editable install
- **Dual configuration**: Easy toggle between stable and dev

## Prerequisites

- [ ] **Cursor editor installed**
- [ ] **mcp-n8n installed** (`pip install mcp-n8n` or dev install)
- [ ] **API keys** (Anthropic, optionally Coda)
- [ ] **Text editor** (for editing JSON config)

---

## Approach 1: Production Setup (Recommended)

**When to use:** You want to use mcp-n8n with the stable PyPI release

**Pros:**
- ✅ Simple configuration
- ✅ Stable, tested release
- ✅ Easy to update (`pip install --upgrade mcp-n8n`)
- ✅ No local source code needed

**Cons:**
- ❌ Can't modify source code
- ❌ Can't test unreleased features

### Steps

**1. Locate Cursor MCP config file:**

```bash
# Config file location
~/.cursor/mcp.json

# Create directory if it doesn't exist
mkdir -p ~/.cursor

# Open in default editor
open ~/.cursor/mcp.json

# OR open in VS Code
code ~/.cursor/mcp.json

# OR open in Cursor itself
cursor ~/.cursor/mcp.json
```

**2. Add mcp-n8n server entry:**

If the file doesn't exist, create it with:

```json
{
  "servers": {
    "mcp-n8n": {
      "type": "stdio",
      "command": "mcp-n8n",
      "args": [],
      "env": {
        "ANTHROPIC_API_KEY": "your_anthropic_key_here",
        "CODA_API_KEY": "your_coda_key_here",
        "MCP_N8N_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

If the file exists, add the `mcp-n8n` entry to the existing `servers` object.

**3. Replace API keys:**

- **ANTHROPIC_API_KEY**: Get from https://console.anthropic.com/
- **CODA_API_KEY**: Get from https://coda.io/account (optional)

**4. Save the file**

**5. Reload Cursor:**

Open Command Palette (Cmd+Shift+P / Ctrl+Shift+P):
- Type: "Developer: Reload Window"
- Press Enter

### Verification

In Cursor, test the connection:

**Open Cursor AI chat and ask:**
> "What MCP tools are available?"

**Expected response:**
```
I can see several MCP tools:

Gateway tools:
- gateway_status
- get_events

Chora Composer tools (chora:*):
- chora:generate_content
- chora:assemble_artifact
- chora:list_generators
- chora:validate_content

Coda MCP tools (coda:*):
- coda:list_docs
- coda:list_tables
- coda:list_rows
- coda:create_hello_doc_in_folder
```

**Test gateway status:**
> "Check the gateway status"

Expected: JSON response showing gateway running with 2 backends active

---

## Approach 2: Development Setup

**When to use:** You're developing mcp-n8n or need to test local changes

**Pros:**
- ✅ Test local code changes immediately
- ✅ Debug mode enabled
- ✅ Detailed logging

**Cons:**
- ❌ More complex configuration
- ❌ Requires local clone of repository
- ❌ Must update paths if repo moves

### Steps

**1. Install mcp-n8n in development mode:**

```bash
# Clone and setup (if not already done)
git clone --recurse-submodules https://github.com/yourusername/mcp-n8n.git
cd mcp-n8n
./scripts/setup.sh

# OR manually
pip install -e ".[dev]"
```

**2. Get absolute paths:**

```bash
# Get Python path
which python
# Example: /Users/you/code/mcp-n8n/.venv/bin/python

# Get project directory
pwd
# Example: /Users/you/code/mcp-n8n
```

**3. Configure Cursor:**

```json
{
  "servers": {
    "mcp-n8n-dev": {
      "type": "stdio",
      "command": "/Users/you/code/mcp-n8n/.venv/bin/python",
      "args": ["-m", "mcp_n8n.gateway"],
      "cwd": "/Users/you/code/mcp-n8n",
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key",
        "MCP_N8N_LOG_LEVEL": "DEBUG",
        "MCP_N8N_DEBUG": "1",
        "PYTHONPATH": "/Users/you/code/mcp-n8n/src"
      }
    }
  }
}
```

**Replace:**
- `/Users/you/code/mcp-n8n/.venv/bin/python` with your Python path
- `/Users/you/code/mcp-n8n` with your project path

**4. Reload Cursor window** (Cmd+Shift+P → "Developer: Reload Window")

### Verification

Same as production setup, but with debug logging enabled.

**Check if debug logging is active:**
Ask Cursor:
> "Check gateway status"

The response should include debug-level details.

---

## Approach 3: Dual Configuration (Stable + Dev)

**When to use:** You want to easily switch between stable and development modes

**Pros:**
- ✅ Quick toggle between modes
- ✅ Rollback to stable if dev breaks
- ✅ Test changes while keeping stable backup

**Cons:**
- ❌ Must manually switch entries
- ❌ Only one can be active at a time

### Steps

**1. Configure both entries:**

```json
{
  "servers": {
    "mcp-n8n-stable": {
      "type": "stdio",
      "command": "mcp-n8n",
      "args": [],
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key",
        "MCP_N8N_LOG_LEVEL": "INFO"
      }
    },
    "_mcp-n8n-dev": {
      "comment": "DISABLED: Rename to enable (remove underscore)",
      "type": "stdio",
      "command": "/Users/you/code/mcp-n8n/.venv/bin/python",
      "args": ["-m", "mcp_n8n.gateway"],
      "cwd": "/Users/you/code/mcp-n8n",
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key",
        "MCP_N8N_LOG_LEVEL": "DEBUG",
        "MCP_N8N_DEBUG": "1",
        "PYTHONPATH": "/Users/you/code/mcp-n8n/src"
      }
    }
  }
}
```

**2. Toggle between modes:**

**To use dev mode:**
- Rename `mcp-n8n-stable` to `_mcp-n8n-stable` (prefix with `_`)
- Rename `_mcp-n8n-dev` to `mcp-n8n-dev` (remove `_`)
- Reload Cursor window

**To use stable mode:**
- Rename `mcp-n8n-dev` to `_mcp-n8n-dev` (prefix with `_`)
- Rename `_mcp-n8n-stable` to `mcp-n8n-stable` (remove `_`)
- Reload Cursor window

**3. Quick toggle with sed:**

```bash
# Switch to dev mode
sed -i '' 's/"mcp-n8n-stable"/"_mcp-n8n-stable"/' ~/.cursor/mcp.json
sed -i '' 's/"_mcp-n8n-dev"/"mcp-n8n-dev"/' ~/.cursor/mcp.json

# Switch to stable mode
sed -i '' 's/"mcp-n8n-dev"/"_mcp-n8n-dev"/' ~/.cursor/mcp.json
sed -i '' 's/"_mcp-n8n-stable"/"mcp-n8n-stable"/' ~/.cursor/mcp.json

# Reload Cursor (Cmd+Shift+P → "Developer: Reload Window")
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Cursor doesn't show mcp-n8n tools | Config not loaded | Verify JSON syntax, reload window |
| "command not found: mcp-n8n" | Package not in PATH | Use absolute path to mcp-n8n |
| No backends active | Missing API keys | Add `ANTHROPIC_API_KEY` to env |
| Config changes not applied | Window not reloaded | Cmd+Shift+P → "Developer: Reload Window" |
| Invalid JSON error | Syntax error in config | Validate JSON: `python -m json.tool mcp.json` |

### Common Issues

**Problem:** Cursor shows "mcp-n8n server failed to start"

**Diagnosis:**
```bash
# Test mcp-n8n command manually
mcp-n8n

# OR for dev mode
/path/to/.venv/bin/python -m mcp_n8n.gateway

# Check for errors in output
```

**Solution:**
```bash
# If command fails, reinstall
pip install --upgrade mcp-n8n

# If dev mode fails, verify paths
which python  # Should be in .venv
pwd           # Should be project directory

# Update config with correct paths
```

---

**Problem:** Tools appear but calls fail

**Diagnosis:**
```bash
# In Cursor AI chat, ask:
# "Check gateway status"
# Look for backend status = "failed" or "stopped"
```

**Solution:**
```bash
# Verify API keys are set
cat ~/.cursor/mcp.json | grep API_KEY

# Ensure keys are valid (not "your_key_here")
# Update config and reload window
```

---

**Problem:** Cursor MCP config location not found

**Diagnosis:**
```bash
# Check if directory exists
ls -la ~/.cursor/

# If doesn't exist, create it
mkdir -p ~/.cursor
```

**Solution:**
```bash
# Create config file
cat > ~/.cursor/mcp.json << 'EOF'
{
  "servers": {
    "mcp-n8n": {
      "type": "stdio",
      "command": "mcp-n8n",
      "args": [],
      "env": {
        "ANTHROPIC_API_KEY": "your_key"
      }
    }
  }
}
EOF

# Reload Cursor window
```

---

**Problem:** Dev mode doesn't pick up code changes

**Diagnosis:**
```bash
# Check if install is editable
pip show mcp-n8n | grep Location
# Should show: Location: /path/to/mcp-n8n (editable)
```

**Solution:**
```bash
# Reinstall in editable mode
cd /path/to/mcp-n8n
pip install -e ".[dev]"

# Verify editable install
pip show mcp-n8n | grep "Editable project location"

# Reload Cursor window after code changes
```

---

## Best Practices

### ✅ DO

**1. Use absolute paths for dev mode:**
```json
{
  "command": "/Users/you/code/mcp-n8n/.venv/bin/python",  // Absolute
  "cwd": "/Users/you/code/mcp-n8n"                        // Absolute
}
```

**2. Validate JSON before saving:**
```bash
# Validate syntax
python -m json.tool ~/.cursor/mcp.json
```

**3. Keep backup of working config:**
```bash
cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup
```

**4. Test after config changes:**
```bash
# Reload window (Cmd+Shift+P → "Developer: Reload Window")
# Ask Cursor: "What MCP tools are available?"
```

**5. Use INFO log level for production:**
```json
{
  "env": {
    "MCP_N8N_LOG_LEVEL": "INFO"  // Not DEBUG in production
  }
}
```

### ❌ DON'T

**1. Don't use relative paths:**
```json
// ❌ BAD
{
  "command": "./.venv/bin/python"  // Relative path
}

// ✅ GOOD
{
  "command": "/Users/you/code/mcp-n8n/.venv/bin/python"  // Absolute
}
```

**2. Don't forget to reload window:**
```bash
# ❌ BAD: Save config but don't reload
# Changes won't apply

# ✅ GOOD: Always reload after config changes
# Cmd+Shift+P → "Developer: Reload Window"
```

**3. Don't expose API keys in shared configs:**
```json
// ❌ BAD: Real API key in shared file
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-real-key"  // Don't commit this!
  }
}

// ✅ GOOD: Use placeholder in example
{
  "env": {
    "ANTHROPIC_API_KEY": "your_anthropic_key_here"
  }
}
```

**4. Don't run multiple mcp-n8n instances:**
```json
// ❌ BAD: Both enabled (will conflict)
{
  "servers": {
    "mcp-n8n-stable": { ... },
    "mcp-n8n-dev": { ... }  // Conflict!
  }
}

// ✅ GOOD: Only one enabled
{
  "servers": {
    "mcp-n8n-stable": { ... },
    "_mcp-n8n-dev": { ... }  // Disabled with underscore
  }
}
```

---

## Configuration Templates

### Minimal Configuration

```json
{
  "servers": {
    "mcp-n8n": {
      "type": "stdio",
      "command": "mcp-n8n",
      "args": [],
      "env": {
        "ANTHROPIC_API_KEY": "your_key"
      }
    }
  }
}
```

### Full Configuration (All Options)

```json
{
  "servers": {
    "mcp-n8n": {
      "type": "stdio",
      "command": "mcp-n8n",
      "args": [],
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key",
        "MCP_N8N_LOG_LEVEL": "INFO",
        "MCP_N8N_DEBUG": "0",
        "MCP_N8N_BACKEND_TIMEOUT": "30",
        "N8N_EVENT_WEBHOOK_URL": "http://localhost:5678/webhook/events"
      }
    }
  }
}
```

### Development Configuration

```json
{
  "servers": {
    "mcp-n8n-dev": {
      "type": "stdio",
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "mcp_n8n.gateway"],
      "cwd": "/absolute/path/to/mcp-n8n",
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key",
        "MCP_N8N_LOG_LEVEL": "DEBUG",
        "MCP_N8N_DEBUG": "1",
        "PYTHONPATH": "/absolute/path/to/mcp-n8n/src"
      }
    }
  }
}
```

---

## Platform-Specific Notes

### macOS

```bash
# Config location
~/.cursor/mcp.json

# Python venv location (typical)
~/code/mcp-n8n/.venv/bin/python
```

### Linux

```bash
# Config location (same as macOS)
~/.cursor/mcp.json

# Python venv location (typical)
~/code/mcp-n8n/.venv/bin/python
```

### Windows

```bash
# Config location
%USERPROFILE%\.cursor\mcp.json

# Python venv location (typical)
C:\Users\YourName\code\mcp-n8n\.venv\Scripts\python.exe

# Use double backslashes or forward slashes in JSON
"command": "C:\\Users\\YourName\\code\\mcp-n8n\\.venv\\Scripts\\python.exe"
# OR
"command": "C:/Users/YourName/code/mcp-n8n/.venv/Scripts/python.exe"
```

---

## Related Documentation

- **[How-To: Install mcp-n8n](install.md)** - Installation guide
- **[How-To: Setup Claude Desktop](setup-claude-desktop.md)** - Claude Desktop config
- **[Tutorial: Getting Started](../tutorials/getting-started.md)** - Quick start
- **[Reference: Configuration](../reference/configuration.md)** - All environment variables
- **[How-To: Debug Gateway](debug-gateway.md)** - Troubleshooting guide

---

**Source:** .config/cursor-mcp.example.json
**Last Updated:** 2025-10-21
