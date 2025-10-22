---
title: "Configuration Reference"
type: reference
audience: all
version: 0.4.0
test_extraction: yes
category: configuration
source: "src/mcp_n8n/config.py, .env.example"
last_updated: 2025-10-21
---

# Configuration Reference

## Overview

Complete reference for mcp-n8n gateway environment variables, backend configuration, and runtime settings.

**Status:** ✅ Stable
**Version:** 0.4.0
**Last Updated:** 2025-10-21

---

## Gateway Configuration

### MCP_N8N_LOG_LEVEL

**Type:** string
**Default:** `"INFO"`
**Valid Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
**Description:** Gateway logging verbosity

**Example:**
```bash
export MCP_N8N_LOG_LEVEL=DEBUG
```

**Used in:** [config.py:57-60](../../src/mcp_n8n/config.py#L57-L60), [gateway.py:28-32](../../src/mcp_n8n/gateway.py#L28-L32)

---

### MCP_N8N_DEBUG

**Type:** boolean
**Default:** `false`
**Valid Values:** `true`, `false`, `1`, `0`
**Description:** Enable debug mode for verbose logging and diagnostics

**Example:**
```bash
export MCP_N8N_DEBUG=true
```

**Used in:** [config.py:61](../../src/mcp_n8n/config.py#L61)

**Effects:**
- Enables detailed JSON-RPC protocol logging
- Shows backend subprocess output
- Logs all tool call arguments/results
- Writes debug info to stderr

---

### MCP_N8N_BACKEND_TIMEOUT

**Type:** integer
**Default:** `30`
**Unit:** seconds
**Range:** 1-300 (recommended)
**Description:** Default timeout for backend operations

**Example:**
```bash
export MCP_N8N_BACKEND_TIMEOUT=60
```

**Used in:** [config.py:89-91](../../src/mcp_n8n/config.py#L89-L91)

**Note:** Individual backends can override this with their own timeout setting

---

### MCP_N8N_MAX_RETRIES

**Type:** integer
**Default:** `3`
**Range:** 0-10 (recommended)
**Description:** Maximum retry attempts for failed backend calls

**Example:**
```bash
export MCP_N8N_MAX_RETRIES=5
```

**Used in:** [config.py:92-94](../../src/mcp_n8n/config.py#L92-L94)

**Behavior:**
- Retries on transient failures (network, timeout)
- Does not retry on permanent errors (auth, invalid params)
- Uses exponential backoff between retries

---

### MCP_N8N_CONFIG_DIR

**Type:** path
**Default:** `./configs`
**Description:** Directory for backend configuration files (future use)

**Example:**
```bash
export MCP_N8N_CONFIG_DIR=/etc/mcp-n8n/configs
```

**Used in:** [config.py:97-100](../../src/mcp_n8n/config.py#L97-L100)

**Status:** 🚧 Reserved for future backend config file support

---

## Backend API Keys

### ANTHROPIC_API_KEY

**Type:** string
**Required:** Yes (for Chora Composer backend)
**Format:** `sk-ant-api03-...`
**Description:** Anthropic API key for Claude access via Chora Composer

**How to Get:** Visit [https://console.anthropic.com/](https://console.anthropic.com/)

**Example:**
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

**Used in:** [config.py:65-69](../../src/mcp_n8n/config.py#L65-L69), [config.py:136](../../src/mcp_n8n/config.py#L136)

**Validation Alias:** Can be set as `ANTHROPIC_API_KEY` or `MCP_N8N_ANTHROPIC_API_KEY`

**Security:**
- Never commit to version control
- Rotate keys regularly
- Use separate keys for dev/prod
- Store in secure vaults (1Password, AWS Secrets Manager, etc.)

**Backend Impact:**
- If not set: Chora Composer backend will be disabled
- If invalid: Backend will fail to initialize

---

### CODA_API_KEY

**Type:** string
**Required:** Yes (for Coda MCP backend)
**Format:** UUID or token from Coda
**Description:** Coda API key for document operations

**How to Get:** Visit [https://coda.io/account](https://coda.io/account) → Account Settings → API

**Example:**
```bash
export CODA_API_KEY="your_coda_api_key_here"
```

**Used in:** [config.py:70-74](../../src/mcp_n8n/config.py#L70-L74), [config.py:142](../../src/mcp_n8n/config.py#L142)

**Validation Alias:** Can be set as `CODA_API_KEY` or `MCP_N8N_CODA_API_KEY`

**Backend Impact:**
- If not set: Coda MCP backend will be disabled
- If invalid: Backend will fail to initialize

---

### CODA_FOLDER_ID

**Type:** string
**Required:** No
**Default:** None
**Description:** Default Coda folder ID for document creation

**Example:**
```bash
export CODA_FOLDER_ID="fl_abc123xyz"
```

**Used in:** [config.py:75-79](../../src/mcp_n8n/config.py#L75-L79), [config.py:143-144](../../src/mcp_n8n/config.py#L143-L144)

**Validation Alias:** Can be set as `CODA_FOLDER_ID` or `MCP_N8N_CODA_FOLDER_ID`

**Behavior:**
- If set: New documents created in this folder by default
- If not set: Documents created in root of workspace

---

## Event Monitoring

### N8N_EVENT_WEBHOOK_URL

**Type:** URL
**Required:** No
**Default:** None
**Description:** n8n webhook URL for real-time event forwarding

**Example:**
```bash
export N8N_EVENT_WEBHOOK_URL="https://your-n8n.com/webhook/events"
```

**Used in:** [config.py:82-86](../../src/mcp_n8n/config.py#L82-L86), [gateway.py:69](../../src/mcp_n8n/gateway.py#L69)

**Validation Alias:** Can be set as `N8N_EVENT_WEBHOOK_URL` or `MCP_N8N_N8N_EVENT_WEBHOOK_URL`

**Behavior:**
- If set: EventWatcher forwards events to webhook in real-time
- If not set: Events only stored locally in EventLog
- Webhook format: JSON POST with event payload

**Use Cases:**
- Real-time monitoring dashboards
- Workflow automation triggers
- Error alerting
- Usage analytics

---

## Backend Configuration

### BackendConfig Fields

Backends are configured programmatically via [BackendConfig](../../src/mcp_n8n/config.py#L22-L50) class:

**name** (string)
- Backend identifier (e.g., "chora-composer", "coda-mcp")
- Must be unique within gateway

**type** (BackendType enum)
- `stdio_subprocess` - Spawn as subprocess, communicate via STDIO (default)
- `stdio_external` - Connect to external STDIO server (future)
- `http_sse` - Connect via HTTP+SSE (future)

**command** (string | None)
- Command to execute for subprocess backends
- Example: `"python"`, `"coda-mcp"`, `sys.executable`

**args** (list[string])
- Arguments to pass to command
- Example: `["-m", "chora_compose.mcp.server"]`

**enabled** (boolean)
- Whether backend is active
- Auto-disabled if required credentials missing

**namespace** (string)
- Tool namespace prefix
- Example: `"chora"` → tools are `chora:generate_content`, etc.

**capabilities** (list[string])
- Capability categories for documentation
- Example: `["artifacts", "content_generation"]`

**env** (dict[string, string])
- Environment variables to pass to backend subprocess
- Includes API keys and backend-specific config

**timeout** (integer)
- Timeout in seconds for this backend
- Overrides `MCP_N8N_BACKEND_TIMEOUT` if specified

---

## Configuration Loading

### Load Order

Configuration is loaded in this order (later overrides earlier):

1. **Default Values** - Hard-coded in [config.py:53-100](../../src/mcp_n8n/config.py#L53-L100)
2. **.env File** - Read from `.env` in current directory
3. **Environment Variables** - OS environment with `MCP_N8N_` prefix
4. **Unprefixed Variables** - Special aliases (e.g., `ANTHROPIC_API_KEY`)

**Example:**
```python
# Default: log_level = "INFO"
# .env file: MCP_N8N_LOG_LEVEL=WARNING
# Environment: export MCP_N8N_LOG_LEVEL=DEBUG
# Result: DEBUG (environment wins)
```

### Prefix Rules

The gateway uses `MCP_N8N_` prefix for most environment variables:

**Prefixed Variables:**
- `MCP_N8N_LOG_LEVEL`
- `MCP_N8N_DEBUG`
- `MCP_N8N_BACKEND_TIMEOUT`
- `MCP_N8N_MAX_RETRIES`

**Unprefixed Variables (with validation aliases):**
- `ANTHROPIC_API_KEY` (also accepts `MCP_N8N_ANTHROPIC_API_KEY`)
- `CODA_API_KEY` (also accepts `MCP_N8N_CODA_API_KEY`)
- `CODA_FOLDER_ID` (also accepts `MCP_N8N_CODA_FOLDER_ID`)
- `N8N_EVENT_WEBHOOK_URL` (also accepts `MCP_N8N_N8N_EVENT_WEBHOOK_URL`)

This design allows sharing API keys with other tools while supporting scoped overrides.

---

## Configuration Files

### .env File

**Location:** Current working directory
**Format:** KEY=VALUE (one per line)
**Encoding:** UTF-8

**Example:**
```bash
# Gateway Settings
MCP_N8N_LOG_LEVEL=INFO
MCP_N8N_DEBUG=false

# Backend Credentials
ANTHROPIC_API_KEY=sk-ant-api03-...
CODA_API_KEY=your_coda_key

# Optional Settings
CODA_FOLDER_ID=fl_abc123
N8N_EVENT_WEBHOOK_URL=https://n8n.example.com/webhook/events
```

**Template:** See [.env.example](../../.env.example) for complete template

---

## Examples

### Example 1: Minimal Production Config

Bare minimum to run both backends:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export CODA_API_KEY="your_coda_key"
mcp-n8n
```

### Example 2: Debug Configuration

Full debugging enabled:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export CODA_API_KEY="your_coda_key"
export MCP_N8N_LOG_LEVEL=DEBUG
export MCP_N8N_DEBUG=true
export MCP_N8N_BACKEND_TIMEOUT=120
mcp-n8n
```

### Example 3: Single Backend Only

Run only Chora Composer (disable Coda):

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
# CODA_API_KEY not set → Coda backend disabled
mcp-n8n
```

### Example 4: Event Monitoring Enabled

Forward events to n8n webhook:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export CODA_API_KEY="your_coda_key"
export N8N_EVENT_WEBHOOK_URL="https://n8n.example.com/webhook/events"
mcp-n8n
```

### Example 5: Using .env File

Create `.env` file:
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-...
CODA_API_KEY=your_coda_key
MCP_N8N_LOG_LEVEL=INFO
```

Run gateway (automatically loads .env):
```bash
mcp-n8n
```

---

## Validation

The gateway validates configuration on startup using Pydantic Settings:

**Validation Checks:**
1. **Type Checking** - Ensures correct types (string, int, bool)
2. **Enum Validation** - Validates log level against allowed values
3. **Dependency Checking** - Warns if required backends missing credentials
4. **Range Validation** - Checks timeout/retry values are reasonable

**Startup Output:**
```
Configuration:
  Log Level: INFO
  Debug: False
  Backend Timeout: 30s

Backends configured: 2
  ✓ chora-composer (chora:*) - ['artifacts', 'content_generation']
  ✓ coda-mcp (coda:*) - ['data_operations', 'documents']
```

**Warnings:**
```
⚠️  Warnings:
  - ANTHROPIC_API_KEY not set - Chora Composer will be disabled
  - CODA_API_KEY not set - Coda MCP will be disabled
```

---

## Troubleshooting

### Problem: Backend won't enable

**Symptoms:** Backend shows `✗` in startup output

**Cause:** Missing required API key

**Solution:**
```bash
# Verify keys are set
echo $ANTHROPIC_API_KEY
echo $CODA_API_KEY

# Set missing keys
export ANTHROPIC_API_KEY="sk-ant-..."
export CODA_API_KEY="your_key"
```

### Problem: Config not loading from .env

**Symptoms:** Environment variables ignored

**Causes & Solutions:**

1. **.env file not in current directory**
   ```bash
   # Check location
   ls -la .env

   # Create if missing
   cp .env.example .env
   ```

2. **Variables need MCP_N8N_ prefix**
   ```bash
   # Wrong (unless using validation alias)
   LOG_LEVEL=DEBUG

   # Correct
   MCP_N8N_LOG_LEVEL=DEBUG
   ```

3. **OS environment overrides .env**
   ```bash
   # Unset OS variable to use .env
   unset MCP_N8N_LOG_LEVEL
   ```

### Problem: Invalid log level

**Symptoms:**
```
ValidationError: log_level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Cause:** Typo or invalid value

**Solution:**
```bash
# Use exact uppercase value
export MCP_N8N_LOG_LEVEL=INFO  # ✅ Correct
export MCP_N8N_LOG_LEVEL=info  # ❌ Wrong (case-sensitive)
```

---

## Related Documentation

- [CLI Reference](cli-reference.md) - Command-line usage
- [How-To: Install](../how-to/install.md) - Installation guide
- [How-To: Setup Claude Desktop](../how-to/setup-claude-desktop.md) - Client configuration
- [How-To: Debug Gateway](../how-to/debug-gateway.md) - Debugging tips
- [Event Schema Reference](event-schema.md) - Event configuration

---

**Source:** [src/mcp_n8n/config.py](../../src/mcp_n8n/config.py), [.env.example](../../.env.example)
**Test Extraction:** Yes (from config validation tests)
**Last Updated:** 2025-10-21
