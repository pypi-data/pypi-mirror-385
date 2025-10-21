# Tutorial: Getting Started with mcp-n8n

---
title: "Getting Started with mcp-n8n"
type: tutorial
audience: beginners
estimated_time: "5 minutes"
prerequisites: ["Python 3.12+", "pip", "Terminal/command line"]
test_extraction: true
source: "README.md, tests/smoke/test_gateway_startup.py"
last_updated: 2025-10-21
---

## What You'll Build

You'll install mcp-n8n and connect it to Claude Desktop or Cursor, giving your AI assistant access to unified MCP tools for artifact creation and data operations.

## What You'll Learn

- How to install mcp-n8n from PyPI
- How to configure environment variables for backends
- How to verify the installation works correctly
- How to connect mcp-n8n to your AI client

## Prerequisites

- [ ] **Python 3.12+** installed (`python --version`)
- [ ] **pip** package manager available
- [ ] **Terminal/command line** access
- [ ] **Claude Desktop** or **Cursor** installed (for client configuration)
- [ ] **API keys** (optional, for backends):
  - Anthropic API key (for Chora Composer backend)
  - Coda API key (for Coda MCP backend)

## Time Required

Approximately **5 minutes**

---

## Step 1: Install mcp-n8n

**What we're doing:** Installing the mcp-n8n package from PyPI, which includes all dependencies including chora-compose.

**Instructions:**

Open your terminal and run:

```bash
pip install mcp-n8n
```

**Expected output:**
```
Successfully installed mcp-n8n-0.4.0 chora-compose-1.3.0 fastmcp-...
```

**Verification:**

```bash
# Check that mcp-n8n is installed
pip show mcp-n8n

# Verify the command is available
mcp-n8n --help
```

**Expected output:**
```
Name: mcp-n8n
Version: 0.4.0
Summary: Pattern P5 (Gateway & Aggregator) MCP server
...
```

**Explanation:**

mcp-n8n is now installed globally (or in your current virtual environment). The `mcp-n8n` command starts the gateway server, and all required dependencies including `chora-compose` are automatically installed.

---

## Step 2: Configure Environment Variables

**What we're doing:** Setting up API keys so mcp-n8n can communicate with backend services.

**Instructions:**

Create a `.env` file in your working directory (or set environment variables in your shell):

```bash
# Create .env file
cat > .env << 'EOF'
# Gateway configuration
MCP_N8N_LOG_LEVEL=INFO

# Backend: Chora Composer (required for artifact operations)
ANTHROPIC_API_KEY=your_anthropic_key_here

# Backend: Coda MCP (optional for data operations)
CODA_API_KEY=your_coda_key_here
EOF
```

**Replace the placeholder values:**
- Get an Anthropic API key from: https://console.anthropic.com/
- Get a Coda API key from: https://coda.io/account (optional)

**Explanation:**

mcp-n8n uses these environment variables to configure backends:
- **ANTHROPIC_API_KEY**: Enables Chora Composer for artifact creation
- **CODA_API_KEY**: Enables Coda MCP for document operations (optional)

Without any API keys, mcp-n8n will still start but won't have active backends.

---

## Step 3: Test the Gateway

**What we're doing:** Starting mcp-n8n to verify it works correctly.

**Instructions:**

Run the gateway:

```bash
# If using .env file
mcp-n8n

# OR export variables directly
export ANTHROPIC_API_KEY=your_key
mcp-n8n
```

**Expected output:**
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "mcp-n8n",
      "version": "0.4.0"
    }
  }
}
```

**What just happened:**

The gateway:
1. Loaded configuration from environment variables
2. Started backend servers (Chora Composer if ANTHROPIC_API_KEY is set)
3. Initialized the MCP protocol
4. Sent an initialization notification

**Tip:** The gateway runs in the foreground and communicates via STDIO. Press `Ctrl+C` to stop it.

---

## Step 4: Connect to Claude Desktop (macOS)

**What we're doing:** Configuring Claude Desktop to use mcp-n8n as an MCP server.

**Instructions:**

1. Open Claude Desktop configuration:
   ```bash
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Add mcp-n8n server entry:
   ```json
   {
     "mcpServers": {
       "mcp-n8n": {
         "command": "mcp-n8n",
         "args": [],
         "env": {
           "ANTHROPIC_API_KEY": "your_anthropic_key",
           "CODA_API_KEY": "your_coda_key"
         }
       }
     }
   }
   ```

3. **Save the file**

4. **Restart Claude Desktop** (Quit completely with Cmd+Q, then reopen)

**Verification:**

In Claude Desktop, try:
> "What MCP tools are available?"

You should see tools like:
- `gateway_status` - Gateway health monitoring
- `get_events` - Query telemetry events
- `chora:*` tools (if Anthropic key configured)
- `coda:*` tools (if Coda key configured)

**Expected response:**
```
I can see several MCP tools available:

Gateway tools:
- gateway_status: Get status of gateway and backends
- get_events: Query gateway telemetry events

Chora Composer tools:
- chora:generate_content
- chora:assemble_artifact
... (full list)
```

---

## Step 5: Verify Gateway Status

**What we're doing:** Checking that backends are running and healthy.

**Instructions:**

In Claude Desktop or your AI client, ask:

> "Check the gateway status"

This will call the `gateway_status` tool.

**Expected output:**
```json
{
  "gateway": {
    "name": "mcp-n8n",
    "version": "0.4.0",
    "status": "running"
  },
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
  },
  "capabilities": {
    "total_tools": 10,
    "total_resources": 0,
    "total_prompts": 0
  }
}
```

**What this tells you:**
- **Gateway is running**: mcp-n8n is active
- **Backends are healthy**: Both Chora Composer and Coda MCP are operational
- **Tools are available**: 10 total tools registered (2 gateway + 4 chora + 4 coda)

---

## What You've Learned

Congratulations! You can now:
- ✅ Install mcp-n8n from PyPI
- ✅ Configure environment variables for backends
- ✅ Start the mcp-n8n gateway
- ✅ Connect AI clients (Claude Desktop) to mcp-n8n
- ✅ Verify backend health with `gateway_status`

## Next Steps

Now that mcp-n8n is running, explore its capabilities:

- [ ] **[Tutorial: Your First Workflow](first-workflow.md)**: Build a daily report workflow
- [ ] **[How-To: Configure Backends](../how-to/configure-backends.md)**: Customize backend settings
- [ ] **[Reference: Tools](../reference/tools.md)**: Complete tool reference
- [ ] **Try it:** Ask Claude to "List available Chora generators" or "Show my Coda documents"

## Troubleshooting

### Problem: "command not found: mcp-n8n"

**Cause:** mcp-n8n not in PATH or installed in wrong environment

**Solution:**
```bash
# Check if installed
pip show mcp-n8n

# If not installed
pip install mcp-n8n

# If in venv, ensure it's activated
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

---

### Problem: Gateway starts but no backends are running

**Cause:** Missing API keys

**Solution:**
```bash
# Check environment variables
echo $ANTHROPIC_API_KEY
echo $CODA_API_KEY

# Set missing keys
export ANTHROPIC_API_KEY=your_key
export CODA_API_KEY=your_key

# Restart gateway
mcp-n8n
```

---

### Problem: "ModuleNotFoundError: No module named 'mcp_n8n'"

**Cause:** Import error, package not properly installed

**Solution:**
```bash
# Reinstall package
pip uninstall mcp-n8n
pip install mcp-n8n

# Verify installation
python -c "import mcp_n8n; print(mcp_n8n.__version__)"
```

---

### Problem: Claude Desktop doesn't show mcp-n8n tools

**Cause:** Configuration not loaded or syntax error in config

**Solution:**
```bash
# 1. Verify config file syntax (must be valid JSON)
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 2. Check for common errors:
#    - Missing commas between entries
#    - Trailing commas (not allowed in JSON)
#    - Unescaped quotes in strings

# 3. Restart Claude Desktop completely
#    (Cmd+Q to quit, then reopen)

# 4. Check Claude Desktop logs
tail -f ~/Library/Logs/Claude/mcp*.log
```

---

## Related Documentation

- **[How-To: Install mcp-n8n](../how-to/install.md)** - Detailed installation options
- **[How-To: Setup Claude Desktop](../how-to/setup-claude-desktop.md)** - Complete Claude Desktop configuration
- **[How-To: Setup Cursor](../how-to/setup-cursor.md)** - Cursor editor configuration
- **[Reference: Configuration](../reference/configuration.md)** - All environment variables
- **[Explanation: Architecture](../explanation/architecture.md)** - How mcp-n8n works

---

**Source:** README.md, tests/smoke/test_gateway_startup.py
**Test Extraction:** Yes (examples verified in smoke tests)
**Last Updated:** 2025-10-21
