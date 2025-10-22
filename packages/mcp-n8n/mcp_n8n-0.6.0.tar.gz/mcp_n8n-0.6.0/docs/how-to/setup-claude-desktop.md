# How to Setup mcp-n8n with Claude Desktop

---
title: "How to Setup mcp-n8n with Claude Desktop"
type: how-to
audience: intermediate
category: configuration
tags: ["claude-desktop", "macos", "mcp-configuration"]
source: ".config/claude-desktop.example.json"
last_updated: 2025-10-21
---

## Problem

You want to connect mcp-n8n to Claude Desktop (macOS) so Claude can use MCP tools for artifact creation and data operations.

**Common scenarios:**
- "I installed mcp-n8n but Claude doesn't see the tools"
- "I want to switch between stable (PyPI) and dev (local) modes"
- "Claude Desktop isn't loading mcp-n8n"

## Solution Overview

Configure Claude Desktop's MCP server settings to load mcp-n8n, with options for:
- **Production mode**: Uses published package from PyPI
- **Development mode**: Uses local editable install
- **Dual configuration**: Easy toggle between stable and dev

## Prerequisites

- [ ] **Claude Desktop installed** (macOS)
- [ ] **mcp-n8n installed** (`pip install mcp-n8n` or dev install)
- [ ] **API keys** (Anthropic, optionally Coda)
- [ ] **Text editor** (VS Code, TextEdit, nano, etc.)

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

**1. Locate Claude Desktop config file:**

```bash
# Config file location (macOS)
~/Library/Application Support/Claude/claude_desktop_config.json

# Open in default editor
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# OR open in VS Code
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**2. Add mcp-n8n server entry:**

If the file doesn't exist, create it with:

```json
{
  "mcpServers": {
    "mcp-n8n": {
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

If the file exists, add the `mcp-n8n` entry to the existing `mcpServers` object.

**3. Replace API keys:**

- **ANTHROPIC_API_KEY**: Get from https://console.anthropic.com/
- **CODA_API_KEY**: Get from https://coda.io/account (optional)

**4. Save the file**

**5. Restart Claude Desktop:**

- Quit Claude Desktop completely (Cmd+Q)
- Reopen Claude Desktop

### Verification

In Claude Desktop, test the connection:

**Ask Claude:**
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

**3. Configure Claude Desktop:**

```json
{
  "mcpServers": {
    "mcp-n8n-dev": {
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

**4. Restart Claude Desktop**

### Verification

Same as production setup, but with debug logging enabled.

**Check logs:**
```bash
# Claude Desktop logs location
tail -f ~/Library/Logs/Claude/mcp*.log
```

Expected: Detailed DEBUG-level logging from mcp-n8n

---

## Approach 3: Dual Configuration (Stable + Dev)

**When to use:** You want to easily switch between stable and development modes

**Pros:**
- ✅ Quick toggle between modes
- ✅ Rollback to stable if dev breaks
- ✅ Test changes while keeping stable backup

**Cons:**
- ❌ Only one can be active at a time
- ❌ Requires commenting/uncommenting entries

### Steps

**1. Configure both entries:**

```json
{
  "mcpServers": {
    "mcp-n8n-stable": {
      "command": "mcp-n8n",
      "args": [],
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key",
        "MCP_N8N_LOG_LEVEL": "INFO"
      }
    },
    "_mcp-n8n-dev": {
      "comment": "DISABLED: Prefix with _ to disable",
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
- Restart Claude Desktop

**To use stable mode:**
- Rename `mcp-n8n-dev` to `_mcp-n8n-dev` (prefix with `_`)
- Rename `_mcp-n8n-stable` to `mcp-n8n-stable` (remove `_`)
- Restart Claude Desktop

**3. Quick toggle script (optional):**

```bash
# Save as ~/bin/toggle-mcp-mode.sh
#!/bin/bash
CONFIG=~/Library/Application\ Support/Claude/claude_desktop_config.json

if grep -q '"mcp-n8n-dev"' "$CONFIG"; then
  echo "Switching to stable..."
  sed -i '' 's/"mcp-n8n-dev"/"_mcp-n8n-dev"/' "$CONFIG"
  sed -i '' 's/"_mcp-n8n-stable"/"mcp-n8n-stable"/' "$CONFIG"
else
  echo "Switching to dev..."
  sed -i '' 's/"mcp-n8n-stable"/"_mcp-n8n-stable"/' "$CONFIG"
  sed -i '' 's/"_mcp-n8n-dev"/"mcp-n8n-dev"/' "$CONFIG"
fi

echo "Restart Claude Desktop to apply changes"
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Claude doesn't show mcp-n8n tools | Config not loaded | Verify JSON syntax, restart Claude completely |
| "command not found: mcp-n8n" | Package not in PATH | Use absolute path: `/path/to/bin/mcp-n8n` |
| No backends active | Missing API keys | Add `ANTHROPIC_API_KEY` to env |
| Config changes not applied | Claude not restarted | Quit with Cmd+Q, reopen |
| Invalid JSON error | Syntax error in config | Validate JSON: `python -m json.tool config.json` |

### Common Issues

**Problem:** Claude Desktop shows "mcp-n8n server failed to start"

**Diagnosis:**
```bash
# Check Claude logs
tail -n 100 ~/Library/Logs/Claude/mcp*.log | grep -i error

# Test mcp-n8n command manually
mcp-n8n
# OR for dev mode
/path/to/.venv/bin/python -m mcp_n8n.gateway
```

**Solution:**
```bash
# If command fails, reinstall
pip install --upgrade mcp-n8n

# If dev mode fails, verify paths
which python  # Should be in .venv
pwd           # Should be project directory
```

---

**Problem:** Tools appear but calls fail

**Diagnosis:**
```bash
# Check backend status via Claude:
# Ask: "Check gateway status"
# Look for backend status = "failed" or "stopped"
```

**Solution:**
```bash
# Verify API keys are set
echo $ANTHROPIC_API_KEY  # Should not be empty

# Update config with valid keys
# Restart Claude Desktop
```

---

**Problem:** Config file gets overwritten

**Cause:** Claude Desktop may reset config on updates

**Solution:**
```bash
# Backup config
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.backup.json

# After Claude update, restore
cp ~/Library/Application\ Support/Claude/claude_desktop_config.backup.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

---

## Best Practices

### ✅ DO

**1. Use absolute paths for dev mode:**
```json
{
  "command": "/Users/you/code/mcp-n8n/.venv/bin/python",  // Absolute path
  "cwd": "/Users/you/code/mcp-n8n"                        // Absolute path
}
```

**2. Validate JSON before saving:**
```bash
# Use online validator or
python -m json.tool claude_desktop_config.json
```

**3. Keep backup of working config:**
```bash
cp claude_desktop_config.json claude_desktop_config.backup
```

**4. Test configuration after changes:**
```bash
# Ask Claude: "What MCP tools are available?"
# Should list mcp-n8n tools
```

**5. Use INFO log level for production:**
```json
{
  "env": {
    "MCP_N8N_LOG_LEVEL": "INFO"  // Not DEBUG
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
  "command": "/Users/you/code/mcp-n8n/.venv/bin/python"
}
```

**2. Don't forget to restart Claude:**
```bash
# ❌ BAD: Save config but don't restart
# Changes won't apply

# ✅ GOOD: Always restart after config changes
# Cmd+Q then reopen
```

**3. Don't expose API keys in screenshots:**
```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-..."  // Don't share this!
  }
}
```

**4. Don't run multiple instances:**
```json
// ❌ BAD: Both enabled
{
  "mcp-n8n-stable": { ... },
  "mcp-n8n-dev": { ... }  // Conflict!
}

// ✅ GOOD: Only one enabled
{
  "mcp-n8n-stable": { ... },
  "_mcp-n8n-dev": { ... }  // Disabled with _
}
```

---

## Configuration Templates

### Minimal Configuration

```json
{
  "mcpServers": {
    "mcp-n8n": {
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
  "mcpServers": {
    "mcp-n8n": {
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

---

## Related Documentation

- **[How-To: Install mcp-n8n](install.md)** - Installation guide
- **[Tutorial: Getting Started](../tutorials/getting-started.md)** - Quick start
- **[Reference: Configuration](../reference/configuration.md)** - All environment variables
- **[How-To: Debug Gateway](debug-gateway.md)** - Troubleshooting guide
- **[dev-docs/RELEASE.md](../../dev-docs/RELEASE.md)** - Rollback procedures

---

**Source:** .config/claude-desktop.example.json
**Last Updated:** 2025-10-21
