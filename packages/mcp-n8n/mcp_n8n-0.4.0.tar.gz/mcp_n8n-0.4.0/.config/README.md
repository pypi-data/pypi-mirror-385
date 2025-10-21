# MCP Configuration Guide

This directory contains sample configurations for connecting Claude Desktop and Cursor to mcp-n8n with both stable (published) and development (local) backends.

---

## Quick Start

### For Claude Desktop (macOS)

1. **Copy template to config location:**
   ```bash
   cp .config/claude-desktop.example.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Edit the config:**
   ```bash
   # Open in your editor
   code ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

3. **Choose stable OR dev** (comment out the one you don't want)

4. **Add your API keys:**
   - Replace `your_key_here` with actual API keys
   - `ANTHROPIC_API_KEY` - from https://console.anthropic.com/
   - `CODA_API_KEY` - from https://coda.io/account

5. **Restart Claude Desktop**

### For Cursor

1. **Copy template:**
   ```bash
   cp .config/cursor-mcp.example.json ~/.cursor/mcp.json
   ```

2. **Edit and configure** (same steps as Claude Desktop)

3. **Restart Cursor**

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `claude-desktop.example.json` | Sample config for Claude Desktop with stable + dev servers |
| `cursor-mcp.example.json` | Sample config for Cursor with stable + dev servers |
| `dev-vs-stable.md` | Detailed guide on toggling between configurations |
| `README.md` | This file - setup instructions |

---

## Configuration Modes

### Stable Mode (Recommended for Most Users)

**Uses:** Published package from PyPI
**When to use:** Production work, reliability needed
**Setup:** Just have `mcp-n8n` installed via `pip install mcp-n8n`

**Example:**
```json
{
  "mcpServers": {
    "mcp-n8n": {
      "command": "mcp-n8n",
      "args": [],
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key"
      }
    }
  }
}
```

### Dev Mode (For Contributors/Developers)

**Uses:** Local editable install (`pip install -e`)
**When to use:** Active development on mcp-n8n itself
**Setup:** Clone repo, create venv, install editable

**Example:**
```json
{
  "mcpServers": {
    "mcp-n8n-dev": {
      "command": "/path/to/mcp-n8n/.venv/bin/python",
      "args": ["-m", "mcp_n8n.gateway"],
      "cwd": "/path/to/mcp-n8n",
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key",
        "MCP_N8N_DEBUG": "1",
        "PYTHONPATH": "/path/to/mcp-n8n/src"
      }
    }
  }
}
```

**Setup for dev mode:**
```bash
cd /path/to/mcp-n8n
just venv-create      # Create virtual environment
source .venv/bin/activate
just check-env        # Verify setup
just smoke            # Run smoke tests
```

---

## Environment Variables

### Required

| Variable | Purpose | Where to Get |
|----------|---------|--------------|
| `ANTHROPIC_API_KEY` | Chora Composer backend | https://console.anthropic.com/ |
| `CODA_API_KEY` | Coda MCP backend | https://coda.io/account |

### Optional (Dev Mode)

| Variable | Purpose | Default |
|----------|---------|---------|
| `MCP_N8N_LOG_LEVEL` | Logging verbosity | `INFO` |
| `MCP_N8N_DEBUG` | Enable debug mode | `0` (off) |
| `MCP_N8N_BACKEND_TIMEOUT` | Backend timeout (seconds) | `30` |
| `PYTHONPATH` | Python module search path | Not set |

---

## Verification

### After Configuration

1. **Restart** your MCP client (Claude Desktop or Cursor)

2. **Check connection** in client:
   - Claude Desktop: Look for mcp-n8n in available tools
   - Cursor: Check MCP inspector panel

3. **Test a tool call:**
   ```
   # In Claude/Cursor, try:
   "List available generators using chora:list_generators"
   ```

4. **Check logs** if issues:
   - Claude Desktop: `~/Library/Logs/Claude/mcp*.log`
   - Cursor: Output panel → MCP

### Validation Commands

```bash
# Validate environment
just check-env

# Run smoke tests
just smoke

# Check backend connectivity
# (manual test via Claude/Cursor)
```

---

## Common Issues & Solutions

### Issue: "Command not found: mcp-n8n"

**Cause:** Package not installed
**Solution:**
```bash
pip install mcp-n8n
# OR for dev:
cd /path/to/mcp-n8n && pip install -e .[dev]
```

### Issue: "Module not found" errors

**Cause:** PYTHONPATH not set correctly in dev mode
**Solution:** Update `PYTHONPATH` in config to point to `src/` directory

### Issue: "Authentication failed"

**Cause:** Invalid or missing API keys
**Solution:**
1. Verify API keys in config
2. Check they're not expired
3. Ensure no extra spaces/quotes

### Issue: Tools not appearing

**Cause:** Server not starting or connection failed
**Solution:**
1. Check Claude/Cursor logs for errors
2. Verify config file is valid JSON
3. Try restarting client
4. Run `just check-env` to validate setup

### Issue: "Backend timeout"

**Cause:** chora-composer or coda-mcp not responding
**Solution:**
1. Verify backend services are running
2. Check backend paths in Claude Desktop config
3. Increase timeout: `MCP_N8N_BACKEND_TIMEOUT=60`

---

## Switching Between Stable and Dev

See [dev-vs-stable.md](./dev-vs-stable.md) for detailed instructions on:
- When to use each mode
- How to toggle between configurations
- Quick rollback procedure
- Troubleshooting toggle issues

**Quick toggle:**
```bash
# In your MCP config, comment/uncomment server entries:

# STABLE (enabled)
"mcp-n8n-stable": { ... }

# DEV (disabled)
// "mcp-n8n-dev": { ... }

# Then restart Claude/Cursor
```

---

## Advanced Configuration

### Custom Backend Paths

If your backend services are not in standard locations:

```json
{
  "mcpServers": {
    "mcp-n8n-dev": {
      ...
      "env": {
        ...
        "CHORA_COMPOSER_PATH": "/custom/path/to/chora-compose",
        "CODA_MCP_PATH": "/custom/path/to/coda-mcp"
      }
    }
  }
}
```

### Multiple Instances

You can run multiple mcp-n8n instances with different configs:

```json
{
  "mcpServers": {
    "mcp-n8n-prod": { "command": "mcp-n8n", ... },
    "mcp-n8n-staging": { "command": "/path/to/staging/mcp-n8n", ... },
    "mcp-n8n-dev": { "command": "/path/to/dev/.venv/bin/python", ... }
  }
}
```

**Note:** Tools will be namespaced by server name.

### Logging Configuration

For detailed logging:

```json
{
  "mcpServers": {
    "mcp-n8n-dev": {
      ...
      "env": {
        ...
        "MCP_N8N_LOG_LEVEL": "DEBUG",
        "MCP_N8N_LOG_FILE": "/tmp/mcp-n8n-debug.log"
      }
    }
  }
}
```

---

## Security Notes

### API Keys

- **Never commit** config files with real API keys to git
- Use environment variables or secure credential managers
- Rotate keys regularly
- Use separate keys for dev/prod environments

### File Permissions

Ensure config files are readable only by you:

```bash
chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json
chmod 600 ~/.cursor/mcp.json
```

---

## Getting Help

If you're stuck:

1. **Check logs:**
   - Claude Desktop: `~/Library/Logs/Claude/`
   - Cursor: Output panel
   - mcp-n8n: `logs/mcp-n8n.log` (if configured)

2. **Run diagnostics:**
   ```bash
   just check-env    # Environment validation
   just smoke        # Quick smoke test
   ```

3. **Consult docs:**
   - [Troubleshooting Guide](../docs/TROUBLESHOOTING.md) (Phase 4)
   - [Quick Reference](../docs/QUICK_REFERENCE.md) (Phase 4)

4. **Report issues:**
   - GitHub Issues: https://github.com/yourusername/mcp-n8n/issues

---

## See Also

- [dev-vs-stable.md](./dev-vs-stable.md) - Toggle between configurations
- [../README.md](../README.md) - Project overview
- [../ARCHITECTURE.md](../ARCHITECTURE.md) - How mcp-n8n works
- [../docs/UNIFIED_ROADMAP.md](../docs/UNIFIED_ROADMAP.md) - Development roadmap
