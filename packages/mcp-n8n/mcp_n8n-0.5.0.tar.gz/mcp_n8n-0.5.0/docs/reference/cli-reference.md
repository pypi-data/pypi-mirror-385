---
title: "CLI Reference"
type: reference
audience: all
version: 0.4.0
test_extraction: yes
category: cli
source: "src/mcp_n8n/gateway.py, pyproject.toml"
last_updated: 2025-10-21
---

# CLI Reference

## Overview

Command-line interface reference for mcp-n8n gateway and utilities.

**Status:** ✅ Stable
**Version:** 0.4.0
**Last Updated:** 2025-10-21

---

## Commands

### mcp-n8n

**Description:** Start the mcp-n8n gateway server

**Usage:**
```bash
mcp-n8n [OPTIONS]
```

**Options:**
- None currently supported (version and help may be added in future releases)

**Transport:**
- STDIO (standard input/output) - Required for MCP protocol compatibility

**Environment Variables:**
Configuration is done entirely through environment variables. See [Configuration Reference](configuration.md) for complete details.

**Key Environment Variables:**
- `ANTHROPIC_API_KEY` - Required for Chora Composer backend
- `CODA_API_KEY` - Required for Coda MCP backend
- `MCP_N8N_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `MCP_N8N_DEBUG` - Enable debug mode (true/false)
- `MCP_N8N_BACKEND_TIMEOUT` - Backend timeout in seconds (default: 30)

**Exit Codes:**
- `0` - Clean shutdown (success)
- `1` - Error during startup or runtime (check logs)
- `130` - Interrupted by signal (Ctrl+C)

---

## Examples

### Example 1: Start with Default Configuration

Start the gateway with default settings:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export CODA_API_KEY="your_coda_key"
mcp-n8n
```

**Expected Output (stderr):**
```
============================================================
mcp-n8n Gateway v0.4.0
Pattern P5: Gateway & Aggregator
============================================================

Configuration:
  Log Level: INFO
  Debug: False
  Backend Timeout: 30s

Backends configured: 2
  ✓ chora-composer (chora:*) - ['tools']
  ✓ coda-mcp (coda:*) - ['tools', 'resources']

Starting gateway on STDIO transport...
------------------------------------------------------------
```

### Example 2: Debug Mode

Start with debug logging enabled:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export CODA_API_KEY="your_coda_key"
export MCP_N8N_LOG_LEVEL="DEBUG"
mcp-n8n
```

**Expected Output:**
- Additional debug logs showing backend initialization
- Tool registration details
- Event monitoring startup
- Detailed transport messages

### Example 3: Single Backend Only

Disable Coda backend by omitting its API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# CODA_API_KEY not set - Coda backend will be disabled
mcp-n8n
```

**Expected Output (stderr):**
```
⚠️  Warnings:
  - CODA_API_KEY not set - Coda MCP will be disabled

Backends configured: 1
  ✓ chora-composer (chora:*) - ['tools']
  ✗ coda-mcp (coda:*) - ['tools', 'resources']
```

### Example 4: Custom Backend Timeout

Set longer timeout for slow backends:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export CODA_API_KEY="your_coda_key"
export MCP_N8N_BACKEND_TIMEOUT=60
mcp-n8n
```

**Configuration:**
```
Configuration:
  Log Level: INFO
  Debug: False
  Backend Timeout: 60s
```

---

## chora-memory

**Description:** CLI utilities for managing chora memory and events (experimental)

**Usage:**
```bash
chora-memory [COMMAND]
```

**Status:** 🚧 Experimental
**Note:** This command is currently under development. See [src/mcp_n8n/cli/main.py](../../src/mcp_n8n/cli/main.py) for implementation details.

---

## Startup Sequence

Understanding what happens when you run `mcp-n8n`:

1. **Configuration Loading** - Reads environment variables ([config.py:21-54](../../src/mcp_n8n/config.py#L21-L54))
2. **Logging Setup** - Configures structured logging ([gateway.py:28-32](../../src/mcp_n8n/gateway.py#L28-L32))
3. **FastMCP Initialization** - Creates MCP server instance ([gateway.py:36-45](../../src/mcp_n8n/gateway.py#L36-L45))
4. **Backend Registry** - Initializes backend manager ([gateway.py:48](../../src/mcp_n8n/gateway.py#L48))
5. **Event Monitoring** - Starts EventLog and EventWatcher ([gateway.py:51-76](../../src/mcp_n8n/gateway.py#L51-L76))
6. **Backend Registration** - Registers all enabled backends ([gateway.py:89-108](../../src/mcp_n8n/gateway.py#L89-L108))
7. **Backend Startup** - Starts backend subprocesses ([gateway.py:111](../../src/mcp_n8n/gateway.py#L111))
8. **Tool Aggregation** - Collects all available tools ([gateway.py:129-132](../../src/mcp_n8n/gateway.py#L129-L132))
9. **STDIO Transport** - Listens on stdin/stdout for MCP protocol ([gateway.py:293](../../src/mcp_n8n/gateway.py#L293))

---

## Shutdown Sequence

When the gateway receives SIGINT (Ctrl+C) or terminates:

1. **Backend Shutdown** - Stops all backend subprocesses gracefully ([gateway.py:135-138](../../src/mcp_n8n/gateway.py#L135-L138))
2. **EventWatcher Stop** - Stops event monitoring ([gateway.py:140-144](../../src/mcp_n8n/gateway.py#L140-L144))
3. **Final Event** - Emits gateway.stopped event ([gateway.py:147](../../src/mcp_n8n/gateway.py#L147))
4. **Cleanup** - Closes file handles and logs ([gateway.py:296-299](../../src/mcp_n8n/gateway.py#L296-L299))

---

## Logging

**Log File Location:** `logs/mcp-n8n.log` (created automatically)

**Log Format:** Structured JSON logging (configurable)

**Log Levels:**
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages (default)
- `WARNING` - Warning messages for potential issues
- `ERROR` - Error messages for failures

**View Logs:**
```bash
# Tail the log file
tail -f logs/mcp-n8n.log

# Pretty-print JSON logs (requires jq)
tail -f logs/mcp-n8n.log | jq .

# Filter for errors only
tail -f logs/mcp-n8n.log | jq 'select(.level == "ERROR")'
```

---

## Troubleshooting

### Problem: Gateway won't start

**Symptoms:**
```
ModuleNotFoundError: No module named 'mcp_n8n'
```

**Cause:** Package not installed or not in PATH

**Solution:**
```bash
# Verify installation
pip list | grep mcp-n8n

# Reinstall if missing
pip install mcp-n8n

# Or use absolute path
~/.local/bin/mcp-n8n
```

### Problem: Backend initialization fails

**Symptoms:**
```
⚠️  Warnings:
  - ANTHROPIC_API_KEY not set - Chora Composer will be disabled
```

**Cause:** Missing required environment variables

**Solution:**
```bash
# Set required API keys
export ANTHROPIC_API_KEY="sk-ant-..."
export CODA_API_KEY="your_coda_key"

# Verify they're set
echo $ANTHROPIC_API_KEY
```

### Problem: No output after starting

**Symptoms:** Gateway starts but produces no output

**Cause:** STDIO transport only responds to MCP protocol messages

**Solution:** This is expected behavior. The gateway communicates via MCP protocol on stdin/stdout. To verify it's running:

1. Check the stderr output for startup messages
2. Use Claude Desktop or Cursor to connect
3. Call the `gateway_status` tool to verify

### Problem: High memory usage

**Symptoms:** Gateway consuming excessive RAM

**Cause:** Event log retention or backend subprocess issues

**Solution:**
```bash
# Set shorter event retention
export MCP_N8N_EVENT_RETENTION_DAYS=1

# Check backend status
# (use gateway_status tool from Claude Desktop)
```

---

## Related Documentation

- [Configuration Reference](configuration.md) - All environment variables
- [How-To: Install](../how-to/install.md) - Installation guide
- [How-To: Setup Claude Desktop](../how-to/setup-claude-desktop.md) - Client configuration
- [How-To: Debug Gateway](../how-to/debug-gateway.md) - Debugging tips
- [Tools Reference](tools.md) - Available MCP tools

---

**Source:** [src/mcp_n8n/gateway.py](../../src/mcp_n8n/gateway.py), [pyproject.toml](../../pyproject.toml)
**Test Extraction:** Yes (from smoke tests)
**Last Updated:** 2025-10-21
