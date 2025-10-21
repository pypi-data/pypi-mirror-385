# Development vs Stable Configuration Guide

## Overview

mcp-n8n supports two distinct configurations to enable safe development while maintaining a stable fallback:

- **Stable**: Uses published package from PyPI (production-ready)
- **Dev**: Uses local editable install with `pip install -e` (for active development)

---

## When to Use Each Configuration

### Use **Stable** when:
- You need reliability for actual work
- Testing integrations with other tools
- Not actively developing mcp-n8n itself
- Giving demos or presentations
- Your dev backend is broken and you need a quick rollback

### Use **Dev** when:
- Actively developing mcp-n8n features
- Testing unreleased changes
- Debugging issues with live code edits
- Contributing to the project
- Experimenting with new integrations

---

## Configuration Files

### Claude Desktop

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Template:** [claude-desktop.example.json](./claude-desktop.example.json)

### Cursor

**Location:** `~/.cursor/mcp.json`
**Template:** [cursor-mcp.example.json](./cursor-mcp.example.json)

---

## How to Toggle Between Configurations

### Method 1: Comment/Uncomment (Recommended)

**In your MCP config file, keep both entries but comment out the one you're not using:**

```json
{
  "mcpServers": {
    // ACTIVE: Stable configuration
    "mcp-n8n-stable": {
      "command": "mcp-n8n",
      ...
    }

    // INACTIVE: Dev configuration (commented out)
    // "mcp-n8n-dev": {
    //   "command": "/Users/you/code/mcp-n8n/.venv/bin/python",
    //   ...
    // }
  }
}
```

**To switch:**
1. Comment out the active configuration
2. Uncomment the desired configuration
3. Save the file
4. Restart Claude Desktop or Cursor

### Method 2: Complete Removal

Only keep one server entry at a time. Copy from templates when switching.

---

## Quick Rollback Procedure

**If dev backend breaks and you need to get back to stable immediately:**

```bash
# 1. Run rollback script (when implemented in Phase 2)
just rollback

# OR manually:

# 2. Edit your MCP config:
#    - macOS Claude: ~/Library/Application Support/Claude/claude_desktop_config.json
#    - Cursor: ~/.cursor/mcp.json

# 3. Enable stable server, disable dev server

# 4. Restart Claude Desktop or Cursor

# 5. Verify stable works:
just verify-stable
```

**Recovery time:** < 1 minute

---

## Environment Variable Differences

### Stable Configuration

```bash
MCP_N8N_LOG_LEVEL=INFO          # Less verbose
MCP_N8N_DEBUG=0                 # Debugging off
# No PYTHONPATH needed
```

### Dev Configuration

```bash
MCP_N8N_LOG_LEVEL=DEBUG         # Verbose logging
MCP_N8N_DEBUG=1                 # Debugging on
PYTHONPATH=/path/to/src         # Points to local src/
```

---

## Validation Commands

### Before Switching to Dev

```bash
# Ensure dev environment is ready
just check-env

# Run smoke tests
just smoke

# Verify installation
pip show mcp-n8n
```

### After Switching

```bash
# Verify backend responds
# (Test by making a tool call in Claude/Cursor)

# Check logs for errors
# Claude Desktop: ~/Library/Logs/Claude/
# Cursor: Check Cursor output panel
```

---

## Troubleshooting

### Dev backend not responding

**Symptoms:**
- Tools not showing up
- Connection errors
- Import errors

**Solutions:**
1. Check venv is activated: `which python` should show `.venv/bin/python`
2. Reinstall in editable mode: `pip install -e .[dev]`
3. Verify paths in config match your system
4. Check PYTHONPATH points to `src/` directory
5. Look for errors in Claude/Cursor logs

### Stable backend outdated

**Symptoms:**
- Missing new features you just developed
- Old version reported

**Solutions:**
1. You're using stable, which is expected
2. To test new features, switch to dev configuration
3. Or publish new version and `pip install --upgrade mcp-n8n`

### Both configurations broken

**Symptoms:**
- Neither stable nor dev works
- API keys invalid
- Backend services down

**Solutions:**
1. Check API keys in config (ANTHROPIC_API_KEY, CODA_API_KEY)
2. Verify backend services are running (chora-composer, coda-mcp)
3. Check network connectivity
4. Review error logs for specific issues

---

## Best Practices

1. **Always keep stable config** as a fallback in comments
2. **Test dev changes with smoke tests** before switching: `just smoke`
3. **Use dev for development only** - don't rely on it for production work
4. **Document breaking changes** in CHANGELOG.md before switching
5. **Run `just verify`** after any configuration change
6. **Keep .env updated** with correct API keys for both environments

---

## Advanced: Dual Instances

You can run both stable and dev simultaneously by:

1. Using different server names in config
2. Both enabled at once
3. Tools prefixed differently (e.g., `mcp-n8n-dev:tool_name`)

**Not recommended** - can cause confusion about which backend is responding.

---

## See Also

- [Configuration README](./README.md) - Complete setup guide
- [Rollback Procedure](../docs/ROLLBACK_PROCEDURE.md) - Emergency recovery (Phase 2)
- [Troubleshooting Guide](../docs/TROUBLESHOOTING.md) - Common issues (Phase 4)
