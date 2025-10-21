---
title: "How to Configure Backends"
type: how-to
audience: intermediate
category: configuration
tags: [backends, configuration, chora-composer, coda-mcp]
source: "src/mcp_n8n/config.py, src/mcp_n8n/backends/base.py, src/mcp_n8n/backends/registry.py"
last_updated: 2025-10-21
---

# How to Configure Backends

## Problem

You need to enable, disable, or customize MCP backend servers (like chora-composer, coda-mcp) that the gateway integrates with.

**Common scenarios:**
- Enable/disable specific backends
- Adjust backend timeouts for slow operations
- Add a new custom backend
- Change backend subprocess commands
- Configure backend-specific environment variables

## Solution Overview

mcp-n8n supports three approaches to backend configuration:
1. **Environment variables** (production - recommended)
2. **Programmatic BackendConfig** (development/testing)
3. **Disable backends** (by omitting API keys)

## Prerequisites

- [ ] mcp-n8n installed
- [ ] Understanding of [Configuration Reference](../reference/configuration.md)
- [ ] API keys for backends you want to enable

---

## Approach 1: Via Environment Variables (Recommended)

**When to use:** Production deployments, standard configurations

**Pros:**
- ✅ No code changes required
- ✅ Works with standard installation
- ✅ Follows 12-factor app principles

**Cons:**
- ❌ Limited customization (predefined backends only)

### Steps

1. **Set required API keys:**
   ```bash
   # For Chora Composer backend
   export ANTHROPIC_API_KEY="sk-ant-api03-..."

   # For Coda MCP backend
   export CODA_API_KEY="your_coda_key"
   ```

2. **Configure optional settings:**
   ```bash
   # Backend timeout (default: 30 seconds)
   export MCP_N8N_BACKEND_TIMEOUT=60

   # Coda folder for document creation
   export CODA_FOLDER_ID="fl_abc123"
   ```

3. **Start gateway:**
   ```bash
   mcp-n8n
   ```

4. **Verify backends are enabled:**
   Check stderr output for backend status:
   ```
   Backends configured: 2
     ✓ chora-composer (chora:*) - ['artifacts', 'content_generation']
     ✓ coda-mcp (coda:*) - ['data_operations', 'documents']
   ```

### Verification

Use `gateway_status` tool to check backend health:
```json
{
  "tool": "gateway_status",
  "arguments": {}
}
```

Expected response includes:
```json
{
  "backends": {
    "chora-composer": {
      "status": "running",
      "namespace": "chora",
      "tool_count": 4
    },
    "coda-mcp": {
      "status": "running",
      "namespace": "coda",
      "tool_count": 4
    }
  }
}
```

---

## Approach 2: Programmatic Configuration

**When to use:** Development, testing, custom backends

**Pros:**
- ✅ Full control over backend configuration
- ✅ Can add custom backends
- ✅ Useful for testing

**Cons:**
- ❌ Requires code changes
- ❌ More verbose

### Steps

1. **Import configuration classes:**
   ```python
   from mcp_n8n.config import BackendConfig, BackendType
   from mcp_n8n.backends import BackendRegistry
   import sys
   ```

2. **Create custom backend config:**
   ```python
   # Example: Chora Composer with custom timeout
   chora_config = BackendConfig(
       name="chora-composer",
       type=BackendType.STDIO_SUBPROCESS,
       command=sys.executable,
       args=["-m", "chora_compose.mcp.server"],
       enabled=True,
       namespace="chora",
       capabilities=["artifacts", "content_generation"],
       env={"ANTHROPIC_API_KEY": "sk-ant-..."},
       timeout=120  # Custom 120s timeout
   )
   ```

3. **Register backend:**
   ```python
   import asyncio

   async def main():
       # Create registry
       registry = BackendRegistry()

       # Register backend
       registry.register(chora_config)

       # Start all backends
       await registry.start_all()

       print(f"Backends running: {len(registry._backends)}")

   asyncio.run(main())
   ```

### Full Example: Custom Backend

```python
import asyncio
import sys
from mcp_n8n.config import BackendConfig, BackendType
from mcp_n8n.backends import BackendRegistry

async def configure_custom_backend():
    """Configure a custom MCP backend."""

    # Define custom backend configuration
    custom_backend = BackendConfig(
        name="my-custom-backend",
        type=BackendType.STDIO_SUBPROCESS,
        command="path/to/my-mcp-server",
        args=["--option", "value"],
        enabled=True,
        namespace="custom",  # Tools will be custom:tool_name
        capabilities=["data", "processing"],
        env={
            "MY_API_KEY": "custom_key",
            "CUSTOM_OPTION": "value"
        },
        timeout=45
    )

    # Create and configure registry
    registry = BackendRegistry()
    registry.register(custom_backend)

    # Start backend
    await registry.start_all()

    # Check status
    status = registry.get_status()
    print(f"Backend status: {status}")

asyncio.run(configure_custom_backend())
```

### Verification

Check backend registered successfully:
```python
# Get all backends
backends = registry._backends
print(f"Registered backends: {list(backends.keys())}")

# Get tools from custom backend
tools = backends['my-custom-backend'].get_tools()
print(f"Tools: {[t['name'] for t in tools]}")
```

---

## Approach 3: Disable Specific Backend

**When to use:** Don't need a particular backend, reduce resource usage

**Pros:**
- ✅ Simple (just omit API key)
- ✅ Reduces startup time
- ✅ Saves resources

**Cons:**
- ❌ Tools from disabled backend unavailable

### Steps

1. **To disable Chora Composer:**
   ```bash
   # Don't set ANTHROPIC_API_KEY
   # Only set Coda API key
   export CODA_API_KEY="your_coda_key"

   mcp-n8n
   ```

   **Expected output:**
   ```
   ⚠️  Warnings:
     - ANTHROPIC_API_KEY not set - Chora Composer will be disabled

   Backends configured: 1
     ✗ chora-composer (chora:*) - ['artifacts']
     ✓ coda-mcp (coda:*) - ['data_operations']
   ```

2. **To disable Coda MCP:**
   ```bash
   # Only set Anthropic API key
   export ANTHROPIC_API_KEY="sk-ant-..."
   # Don't set CODA_API_KEY

   mcp-n8n
   ```

3. **To disable all backends (gateway only):**
   ```bash
   # Don't set any API keys
   mcp-n8n
   ```

   **Result:** Only gateway tools available (`gateway_status`, `get_events`)

### Verification

Check which backends are running:
```bash
# Via gateway_status tool
# Or check logs for enabled backends
```

Expected: Only backends with API keys configured are running

---

## Common Configuration Tasks

### Task 1: Increase Backend Timeout

**Problem:** Tool calls timing out after 30 seconds

**Solution:**
```bash
# Set global timeout for all backends
export MCP_N8N_BACKEND_TIMEOUT=120  # 120 seconds

mcp-n8n
```

Or programmatically for specific backend:
```python
config = BackendConfig(
    name="chora-composer",
    timeout=120,  # Override global timeout
    # ... other config
)
```

---

### Task 2: Change Backend Command

**Problem:** Need to use development version of backend

**Solution:**
```python
# Use local development build
dev_config = BackendConfig(
    name="chora-composer-dev",
    command="/path/to/dev/python",
    args=["-m", "chora_compose.mcp.server"],
    namespace="chora-dev",  # Different namespace
    # ... rest of config
)
```

---

### Task 3: Add Environment Variables to Backend

**Problem:** Backend needs additional configuration

**Solution:**
```python
config = BackendConfig(
    name="chora-composer",
    env={
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "CHORA_DEBUG": "1",  # Additional env var
        "CHORA_TEMPLATE_DIR": "/custom/templates",
        "LOG_LEVEL": "DEBUG"
    },
    # ... rest of config
)
```

---

### Task 4: Run Multiple Instances of Same Backend

**Problem:** Need staging and production backends simultaneously

**Solution:**
```python
# Production backend
prod_config = BackendConfig(
    name="chora-composer-prod",
    namespace="chora",
    env={"ANTHROPIC_API_KEY": "sk-ant-prod-..."},
    # ...
)

# Staging backend
staging_config = BackendConfig(
    name="chora-composer-staging",
    namespace="chora-staging",  # Different namespace
    env={"ANTHROPIC_API_KEY": "sk-ant-staging-..."},
    # ...
)

# Register both
registry.register(prod_config)
registry.register(staging_config)

# Tools will be:
# chora:generate_content (prod)
# chora-staging:generate_content (staging)
```

---

## Backend Configuration Reference

### BackendConfig Fields

**Required:**
- `name` (str) - Unique backend identifier
- `namespace` (str) - Tool namespace prefix
- `command` (str | None) - Executable for subprocess backends

**Optional:**
- `type` (BackendType) - Integration method (default: STDIO_SUBPROCESS)
- `args` (list[str]) - Command arguments (default: [])
- `enabled` (bool) - Whether backend is active (default: True)
- `capabilities` (list[str]) - Capability categories (default: [])
- `env` (dict) - Environment variables (default: {})
- `timeout` (int) - Operation timeout in seconds (default: 30)

### BackendType Values

- `STDIO_SUBPROCESS` - Spawn as subprocess (default, recommended)
- `STDIO_EXTERNAL` - Connect to external server (future)
- `HTTP_SSE` - HTTP+SSE protocol (future)

---

## Troubleshooting

### Problem: Backend won't start

**Symptoms:**
```
Failed to start backend 'chora-composer': ...
```

**Debug steps:**

1. **Check API key is set:**
   ```bash
   echo $ANTHROPIC_API_KEY
   # Should output your key, not empty
   ```

2. **Check backend is installed:**
   ```bash
   python -m chora_compose.mcp.server --help
   # Should show help, not ModuleNotFoundError
   ```

3. **Check logs for details:**
   ```bash
   # Look in logs/mcp-n8n.log
   tail -f logs/mcp-n8n.log | grep ERROR
   ```

4. **Increase timeout if slow:**
   ```bash
   export MCP_N8N_BACKEND_TIMEOUT=120
   ```

---

### Problem: Backend enabled but no tools

**Symptoms:**
```
{
  "backends": {
    "chora-composer": {
      "status": "running",
      "tool_count": 0  ← No tools!
    }
  }
}
```

**Causes:**
- Backend started but failed tool discovery
- Backend version incompatible
- Backend returned no tools

**Solution:**
```bash
# Check backend logs
# Enable debug mode
export MCP_N8N_DEBUG=true
mcp-n8n

# Look for tool discovery errors in logs
```

---

### Problem: Namespace collision

**Symptoms:**
```
ValueError: Namespace 'chora' already used by backend 'chora-composer'
```

**Cause:** Trying to register two backends with same namespace

**Solution:**
```python
# Use different namespaces
config1 = BackendConfig(namespace="chora-v1", ...)
config2 = BackendConfig(namespace="chora-v2", ...)
```

---

### Problem: Backend subprocess fails

**Symptoms:**
```
subprocess.CalledProcessError: Command 'python -m...' returned non-zero exit code
```

**Debug:**
```python
# Test backend command directly
import subprocess

result = subprocess.run(
    ["python", "-m", "chora_compose.mcp.server"],
    capture_output=True,
    text=True
)

print("stdout:", result.stdout)
print("stderr:", result.stderr)
print("returncode:", result.returncode)
```

---

## Related Documentation

- [Configuration Reference](../reference/configuration.md) - All environment variables
- [How-To: Debug Gateway](debug-gateway.md) - Debugging backend issues
- [Tools Reference](../reference/tools.md) - Available backend tools
- [CLI Reference](../reference/cli-reference.md) - Gateway commands

---

**Source:** [src/mcp_n8n/config.py](../../src/mcp_n8n/config.py), [src/mcp_n8n/backends/base.py](../../src/mcp_n8n/backends/base.py), [src/mcp_n8n/backends/registry.py](../../src/mcp_n8n/backends/registry.py)
**Last Updated:** 2025-10-21
