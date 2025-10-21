---
title: "How to Debug the Gateway"
type: how-to
audience: intermediate
category: troubleshooting
tags: [debugging, troubleshooting, logs, diagnostics]
source: "docs/TROUBLESHOOTING.md, src/mcp_n8n/gateway.py"
last_updated: 2025-10-21
---

# How to Debug the Gateway

## Problem

You need to diagnose and fix issues with the mcp-n8n gateway not starting, backends failing, or tool calls not working.

**Common scenarios:**
- Gateway won't start
- Backends fail to initialize
- Tool calls timeout or fail
- Event monitoring not working
- Logs show errors but unclear cause

## Solution Overview

Three-step debugging approach:
1. **Quick checks** - Verify status, check logs
2. **Debug mode** - Enable verbose logging
3. **Systematic diagnosis** - Follow issue-specific steps

## Prerequisites

- [ ] mcp-n8n installed
- [ ] Understanding of [Configuration Reference](../reference/configuration.md)
- [ ] Access to log files

---

## Approach 1: Quick Health Checks

**When to use:** First step for any issue

**Steps:**

1. **Check gateway status:**
   ```bash
   # Try to call gateway_status tool via Claude Desktop
   # Or check if gateway process is running
   ps aux | grep mcp-n8n
   ```

2. **Review startup output:**
   ```bash
   # Start gateway and watch stderr
   mcp-n8n 2>&1 | tee gateway-startup.log
   ```

   **Look for:**
   - `✓` marks for successful backend initialization
   - `⚠️` warnings for missing API keys
   - `✗` errors for failed backends

3. **Check log file:**
   ```bash
   # View recent logs
   tail -50 logs/mcp-n8n.log

   # Follow logs in real-time
   tail -f logs/mcp-n8n.log

   # Filter for errors
   grep ERROR logs/mcp-n8n.log

   # Pretty-print JSON logs
   tail -f logs/mcp-n8n.log | jq .
   ```

4. **Verify environment variables:**
   ```bash
   # Check API keys are set
   echo $ANTHROPIC_API_KEY  # Should output key, not empty
   echo $CODA_API_KEY

   # Check log level
   echo $MCP_N8N_LOG_LEVEL  # INFO, DEBUG, etc.
   ```

---

## Approach 2: Enable Debug Mode

**When to use:** Need detailed diagnostic information

**Steps:**

1. **Set debug environment variables:**
   ```bash
   export MCP_N8N_LOG_LEVEL=DEBUG
   export MCP_N8N_DEBUG=true
   ```

2. **Restart gateway:**
   ```bash
   mcp-n8n
   ```

3. **Observe verbose output:**
   - Backend subprocess commands
   - JSON-RPC messages
   - Tool call arguments and results
   - Event emissions
   - Timing information

4. **Review detailed logs:**
   ```bash
   # Debug logs are much more verbose
   tail -100 logs/mcp-n8n.log | jq 'select(.level == "DEBUG")'
   ```

### Debug Output Example

```
Starting backend chora-composer with command: /usr/bin/python3.12
Args: ['-m', 'chora_compose.mcp.server']
Env: {'ANTHROPIC_API_KEY': '***', 'LOG_LEVEL': 'DEBUG'}

Sent JSON-RPC: {"jsonrpc": "2.0", "id": 1, "method": "initialize", ...}
Received JSON-RPC: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": ...}}

Discovered 4 tools from chora-composer:
  - chora:generate_content
  - chora:assemble_artifact
  - chora:list_generators
  - chora:validate_content
```

---

## Approach 3: Systematic Diagnosis

**When to use:** Specific issues requiring targeted debugging

### Issue 1: Gateway Won't Start

**Symptoms:**
```
ImportError: No module named 'mcp_n8n'
```
Or:
```
Command not found: mcp-n8n
```

**Debug steps:**

1. **Verify installation:**
   ```bash
   pip list | grep mcp-n8n
   # Should show: mcp-n8n    0.4.0
   ```

2. **Check virtual environment:**
   ```bash
   which python
   # Should show path to .venv/bin/python

   echo $VIRTUAL_ENV
   # Should show path to .venv
   ```

3. **Reinstall if needed:**
   ```bash
   pip install --force-reinstall mcp-n8n
   ```

4. **Use absolute path:**
   ```bash
   # If PATH issues
   ~/.local/bin/mcp-n8n
   # Or
   python -m mcp_n8n.gateway
   ```

---

### Issue 2: Backend Initialization Failure

**Symptoms:**
```
✗ chora-composer (chora:*) - Failed to start
Backend 'chora-composer': Failed to start: ...
```

**Debug steps:**

1. **Check API key:**
   ```bash
   echo $ANTHROPIC_API_KEY
   # Must be set and valid
   ```

2. **Verify backend package installed:**
   ```bash
   # For chora-composer
   python -m chora_compose.mcp.server --help
   # Should show help, not ModuleNotFoundError

   # For coda-mcp
   which coda-mcp
   # Should show path to executable
   ```

3. **Test backend subprocess manually:**
   ```bash
   # Test chora-composer
   python -m chora_compose.mcp.server
   # Should start (Ctrl+C to exit)

   # Test coda-mcp
   coda-mcp
   # Should start
   ```

4. **Check backend logs:**
   ```bash
   # Enable debug and look for subprocess stderr
   export MCP_N8N_DEBUG=true
   mcp-n8n 2>&1 | grep -A 10 "Backend subprocess"
   ```

5. **Increase timeout:**
   ```bash
   # If backend is slow to start
   export MCP_N8N_BACKEND_TIMEOUT=120
   mcp-n8n
   ```

---

### Issue 3: Tool Call Failures

**Symptoms:**
```
Error: Tool call chora:generate_content failed: timeout
```
Or:
```
Error: Backend 'chora-composer' is not running
```

**Debug steps:**

1. **Verify backend is running:**
   ```json
   {
     "tool": "gateway_status",
     "arguments": {}
   }
   ```

   Check response:
   ```json
   {
     "backends": {
       "chora-composer": {
         "status": "running",  ← Should be "running"
         "tool_count": 4       ← Should be > 0
       }
     }
   }
   ```

2. **Check tool exists:**
   ```bash
   # List all tools
   # Via gateway_status, check tool_count > 0
   ```

3. **Test tool directly:**
   ```python
   # Test tool call programmatically
   import asyncio
   from mcp_n8n.backends import BackendRegistry

   async def test_tool():
       registry = BackendRegistry()
       await registry.start_all()

       backend = registry._backends.get("chora-composer")
       if backend:
           result = await backend.call_tool(
               "list_generators",
               {}
           )
           print(result)

   asyncio.run(test_tool())
   ```

4. **Check for timeout:**
   ```bash
   # Increase timeout for slow tools
   export MCP_N8N_BACKEND_TIMEOUT=120
   ```

5. **Review tool call logs:**
   ```bash
   # Filter logs for specific tool
   tail -f logs/mcp-n8n.log | grep "chora:generate_content"
   ```

---

### Issue 4: Event Monitoring Not Working

**Symptoms:**
- `get_events` returns empty array
- EventWatcher not starting
- No events in `.chora/memory/events/`

**Debug steps:**

1. **Check EventWatcher started:**
   ```bash
   # Look in startup output
   mcp-n8n 2>&1 | grep "EventWatcher"
   # Should see: "EventWatcher started successfully"
   ```

2. **Verify events directory:**
   ```bash
   ls -la .chora/memory/events/
   # Should show monthly directories (e.g., 2025-10/)

   # Check for event files
   find .chora/memory/events/ -name "*.jsonl"
   ```

3. **Test event emission:**
   ```python
   from mcp_n8n.memory import emit_event

   # Emit test event
   emit_event(
       "test.event",
       status="success",
       message="Testing event system"
   )

   # Check if file created
   # ls .chora/memory/events/$(date +%Y-%m)/events.jsonl
   ```

4. **Query events:**
   ```bash
   # Via CLI
   chora-memory query --since 1h

   # Via MCP tool
   # Call get_events with since="1h"
   ```

---

### Issue 5: High Memory/CPU Usage

**Symptoms:**
- Gateway consuming excessive resources
- System slowdown

**Debug steps:**

1. **Check process stats:**
   ```bash
   # Memory usage
   ps aux | grep mcp-n8n

   # Detailed stats
   top -p $(pgrep -f mcp-n8n)
   ```

2. **Check backend subprocesses:**
   ```bash
   # List all related processes
   pgrep -a -f "mcp|chora|coda"

   # Kill stuck backends
   pkill -f "chora_compose"
   ```

3. **Reduce event retention:**
   ```bash
   # Set shorter retention (future config)
   # For now, manually clean old events
   find .chora/memory/events/ -mtime +7 -delete
   ```

4. **Disable unused backends:**
   ```bash
   # Don't set API keys for unused backends
   unset CODA_API_KEY  # Disables Coda backend
   mcp-n8n
   ```

---

### Issue 6: Configuration Not Loading

**Symptoms:**
- Environment variables ignored
- .env file not read

**Debug steps:**

1. **Check .env file location:**
   ```bash
   ls -la .env
   # Should be in current working directory
   ```

2. **Verify .env syntax:**
   ```bash
   cat .env
   # Should be KEY=VALUE format
   # No spaces around =
   # No quotes unless needed
   ```

3. **Test env vars directly:**
   ```bash
   # Set directly (bypasses .env)
   export ANTHROPIC_API_KEY="sk-ant-..."
   mcp-n8n
   ```

4. **Check precedence:**
   ```bash
   # OS env overrides .env
   env | grep MCP_N8N
   # If set, will override .env file
   ```

---

## Common Error Messages

### Error: "Backend not found"

**Cause:** Tool call to non-existent backend

**Solution:**
```bash
# Check available backends
# Via gateway_status

# Verify namespace is correct
# chora:tool (not just "tool")
```

### Error: "EventLog not initialized"

**Cause:** Calling get_events before gateway initialized EventLog

**Solution:** Only use get_events via MCP protocol (not directly)

### Error: "YAML parsing error"

**Cause:** Invalid event_mappings.yaml syntax

**Solution:**
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('config/event_mappings.yaml'))"

# Check for common issues:
# - Indentation (use spaces, not tabs)
# - Missing colons
# - Unquoted special characters
```

---

## Debug Checklist

When debugging any issue, go through this checklist:

- [ ] Gateway process running?
- [ ] API keys set?
- [ ] Backends showing "running" status?
- [ ] Tools discovered (tool_count > 0)?
- [ ] Log file exists and readable?
- [ ] Debug mode enabled if needed?
- [ ] Recent errors in logs?
- [ ] Event monitoring working?
- [ ] Correct Python version (3.12+)?
- [ ] Virtual environment activated?

---

## Getting Help

If you're still stuck:

1. **Gather diagnostic info:**
   ```bash
   # System info
   echo "Python: $(python --version)"
   echo "mcp-n8n: $(pip show mcp-n8n | grep Version)"

   # Environment
   env | grep -E "MCP_N8N|ANTHROPIC|CODA" | sed 's/=.*/=***/'

   # Recent logs
   tail -100 logs/mcp-n8n.log > debug-log.txt
   ```

2. **Create GitHub issue:**
   - Include error messages
   - Attach debug-log.txt (remove sensitive info)
   - Describe steps to reproduce
   - Share configuration (without secrets)

3. **Check existing issues:**
   - https://github.com/anthropics/mcp-n8n/issues

---

## Related Documentation

- [Configuration Reference](../reference/configuration.md) - All settings
- [CLI Reference](../reference/cli-reference.md) - Gateway commands
- [How-To: Configure Backends](configure-backends.md) - Backend setup
- [How-To: Query Events](query-events.md) - Event debugging

---

**Source:** [docs/TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md), [src/mcp_n8n/gateway.py](../../src/mcp_n8n/gateway.py)
**Last Updated:** 2025-10-21
