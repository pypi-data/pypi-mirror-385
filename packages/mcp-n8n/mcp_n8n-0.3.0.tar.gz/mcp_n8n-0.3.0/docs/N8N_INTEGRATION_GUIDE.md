# mcp-n8n + n8n Integration Guide

**Version:** 1.0
**Date:** 2025-10-17
**Status:** Active
**Prerequisites:** Docker Desktop, mcp-n8n v0.2.0+

---

## Overview

This guide explains how to integrate mcp-n8n with your local n8n instance running in Docker Desktop. n8n is a workflow automation tool that can orchestrate calls to MCP servers (like mcp-n8n) to build complex, multi-step automation workflows.

**Architecture:**
```
n8n Workflow
    ↓ (HTTP or Execute Command)
mcp-n8n Gateway
    ├── chora:generate_content
    ├── chora:assemble_artifact
    └── coda:list_docs
```

---

## Table of Contents

1. [Current Setup Verification](#current-setup-verification)
2. [Integration Patterns](#integration-patterns)
3. [Pattern 1: HTTP Endpoint (Simple)](#pattern-1-http-endpoint-simple)
4. [Pattern 2: Execute Command (Direct)](#pattern-2-execute-command-direct)
5. [Pattern 3: Custom n8n Node (Advanced)](#pattern-3-custom-n8n-node-advanced)
6. [Example Workflows](#example-workflows)
7. [Troubleshooting](#troubleshooting)

---

## Current Setup Verification

### 1. Verify n8n is Running

```bash
# Check Docker container
docker ps | grep n8n

# Expected output:
# mcp-n8n-n8n-1   n8nio/n8n:latest   Up X hours   0.0.0.0:5678->5678/tcp
```

**Access n8n UI:** http://localhost:5678

### 2. Verify mcp-n8n is Installed

```bash
# Navigate to mcp-n8n directory
cd /Users/victorpiper/code/mcp-n8n

# Verify installation
just check-env

# Or manually:
python -c "import mcp_n8n; print('mcp-n8n installed')"
```

### 3. Test mcp-n8n Gateway

```bash
# Option A: Test via Python
python -c "from mcp_n8n.gateway import main; print('Gateway importable')"

# Option B: Run smoke tests
just smoke
```

---

## Integration Patterns

### Pattern Comparison

| Pattern | Complexity | Use Case | MCP Tools Available |
|---------|-----------|----------|---------------------|
| **HTTP Endpoint** | Low | Quick prototyping | Limited (tool wrapper needed) |
| **Execute Command** | Medium | Direct MCP access | All (via JSON-RPC) |
| **Custom n8n Node** | High | Production workflows | All (native integration) |

**Recommendation for v0.2.0:** Start with **Pattern 2 (Execute Command)** for simplicity and full MCP access.

---

## Pattern 1: HTTP Endpoint (Simple)

**Status:** ⚠️ Not implemented in v0.2.0

mcp-n8n currently uses STDIO transport (for Claude Desktop/Cursor compatibility). To use HTTP, we would need to add an HTTP wrapper.

**Future Feature (v0.3.0+):**
```bash
# Start HTTP server (planned)
mcp-n8n serve --transport http --port 8080
```

**Skip to Pattern 2 for current version.**

---

## Pattern 2: Execute Command (Direct)

**Status:** ✅ Works with v0.2.0

This pattern uses n8n's "Execute Command" node to run mcp-n8n commands directly.

### Setup

#### Step 1: Create MCP Tool Wrapper Script

Create a script that wraps MCP JSON-RPC calls for n8n:

```bash
# File: /Users/victorpiper/code/mcp-n8n/scripts/mcp-tool.sh
#!/bin/bash
set -e

TOOL_NAME="$1"
ARGUMENTS_JSON="$2"

# Construct JSON-RPC request
REQUEST=$(cat <<EOF
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "$TOOL_NAME",
    "arguments": $ARGUMENTS_JSON
  }
}
EOF
)

# Call mcp-n8n via STDIO
cd /Users/victorpiper/code/mcp-n8n
source .venv/bin/activate 2>/dev/null || true
echo "$REQUEST" | python -m mcp_n8n.gateway 2>/dev/null | jq -r '.result.content[0].text'
```

Make it executable:
```bash
chmod +x /Users/victorpiper/code/mcp-n8n/scripts/mcp-tool.sh
```

#### Step 2: Test the Script

```bash
# Test list_generators tool
./scripts/mcp-tool.sh "chora:list_generators" '{}'

# Expected output: List of available generators
```

### n8n Workflow Example

**Workflow: Simple Content Generation**

1. **Manual Trigger** node
   - Starts workflow manually

2. **Set Context** node
   - Type: `Function`
   - Code:
     ```javascript
     return {
       content_config_id: "welcome-message",
       context: {
         user: { name: "Alice" },
         timestamp: new Date().toISOString()
       }
     };
     ```

3. **Generate Content** node
   - Type: `Execute Command`
   - Command: `/Users/victorpiper/code/mcp-n8n/scripts/mcp-tool.sh`
   - Arguments:
     - `chora:generate_content`
     - `{{ JSON.stringify($json.context) }}`

4. **Log Output** node
   - Type: `Function`
   - Code:
     ```javascript
     console.log('Generated content:', $input.all());
     return $input.all();
     ```

**Import JSON:**
```json
{
  "nodes": [
    {
      "parameters": {},
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "functionCode": "return {\n  content_config_id: \"welcome-message\",\n  context: {\n    user: { name: \"Alice\" },\n    timestamp: new Date().toISOString()\n  }\n};"
      },
      "name": "Set Context",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "command": "/Users/victorpiper/code/mcp-n8n/scripts/mcp-tool.sh chora:generate_content",
        "arguments": "{{ JSON.stringify($json) }}"
      },
      "name": "Generate Content",
      "type": "n8n-nodes-base.executeCommand",
      "typeVersion": 1,
      "position": [650, 300]
    },
    {
      "parameters": {
        "functionCode": "console.log('Generated content:', $input.all());\nreturn $input.all();"
      },
      "name": "Log Output",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [850, 300]
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{"node": "Set Context", "type": "main", "index": 0}]]
    },
    "Set Context": {
      "main": [[{"node": "Generate Content", "type": "main", "index": 0}]]
    },
    "Generate Content": {
      "main": [[{"node": "Log Output", "type": "main", "index": 0}]]
    }
  }
}
```

---

## Pattern 3: Custom n8n Node (Advanced)

**Status:** 📋 Planned for Phase 3 (Week 12)

This pattern creates a custom n8n node package `@chora/mcp-tool-call` that provides native MCP integration.

**Features (Planned):**
- Dynamic tool discovery from mcp-n8n
- Auto-generated input forms based on tool schemas
- Credential management for MCP servers
- Support for both STDIO and HTTP transports

**Timeline:** Phase 3 Week 12 (per UNIFIED_ROADMAP.md)

**Preview:**
```typescript
// @chora/mcp-tool-call node
{
  "name": "MCP Tool Call",
  "properties": [
    {
      "displayName": "MCP Server",
      "name": "server",
      "type": "options",
      "options": [
        { "name": "mcp-n8n Gateway", "value": "mcp-n8n" }
      ]
    },
    {
      "displayName": "Tool",
      "name": "tool",
      "type": "options",
      "options": [] // Dynamically loaded from server
    }
  ]
}
```

**Implementation Effort:** ~8-12 hours

---

## Example Workflows

### Workflow 1: "Hello World" Artifact Assembly

**Purpose:** Generate a simple artifact using chora-composer

**Steps:**
1. **Manual Trigger**
2. **HTTP Request** - Fetch sample data from httpbin.org/json
3. **Function** - Format data for chora
4. **Execute Command** - Call `chora:assemble_artifact`
5. **Slack Notification** - Send notification with artifact link

**Export:** `workflows/hello-world.json` (to be created)

---

### Workflow 2: Daily Standup Notes (Future)

**Purpose:** Automatically generate daily standup notes from GitHub/Jira

**Requirements:**
- chora-compose v1.3.0+ (with event emission)
- mcp-n8n v0.3.0+ (with event monitoring)

**Steps:**
1. **Schedule Trigger** - Daily at 8am
2. **GitHub API** - Fetch yesterday's commits
3. **Jira API** - Fetch tickets updated yesterday
4. **chora:generate_content** - Generate standup notes
5. **chora:assemble_artifact** - Create markdown artifact
6. **Slack** - Post to #standup

**Status:** ⏳ Blocked by chora-compose event emission (see CHORA_ROADMAP_ALIGNMENT.md)

---

### Workflow 3: Weekly Engineering Report (Strategic Focus)

**Purpose:** Pattern N5 validation workflow from UNIFIED_ROADMAP

**Requirements:**
- chora-compose v1.3.0+ (with event emission)
- mcp-n8n v0.3.0+ (with event monitoring)
- Phase 1 Week 6 completion

**Steps:**
1. **Schedule Trigger** - Monday 9am
2. **Parallel Data Gathering:**
   - GitHub API: Commits (last 7 days)
   - Jira API: Closed tickets (last 7 days)
   - DataDog API: Deployment metrics
3. **Aggregate Data**
4. **chora:generate_content** - Report intro
5. **chora:generate_content** - GitHub summary
6. **chora:generate_content** - Jira summary
7. **chora:generate_content** - Metrics analysis
8. **chora:assemble_artifact** - Weekly report
9. **coda:create_row** - Store metadata
10. **Slack** - Post to #engineering

**Status:** ⏳ Planned for Phase 1 Week 6

**Export:** `workflows/weekly-engineering-report.json` (to be created)

---

## Troubleshooting

### Issue: n8n can't execute mcp-tool.sh script

**Symptoms:**
- Error: "Permission denied"
- Error: "Command not found"

**Solution:**
```bash
# Make script executable
chmod +x /Users/victorpiper/code/mcp-n8n/scripts/mcp-tool.sh

# Verify it runs
./scripts/mcp-tool.sh "chora:list_generators" '{}'
```

---

### Issue: mcp-n8n gateway not responding

**Symptoms:**
- Script hangs
- No output from gateway

**Diagnosis:**
```bash
# Test gateway directly
cd /Users/victorpiper/code/mcp-n8n
source .venv/bin/activate
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python -m mcp_n8n.gateway
```

**Expected:** JSON response with server capabilities

**If fails:**
- Check `ANTHROPIC_API_KEY` is set
- Check chora-compose is installed at `/Users/victorpiper/code/chora-compose`
- Check Python virtual environment activated

---

### Issue: chora:generate_content fails

**Symptoms:**
- Error: "Backend not available"
- Error: "Tool not found"

**Diagnosis:**
```bash
# Check backend status
cd /Users/victorpiper/code/mcp-n8n
python -c "from mcp_n8n.config import GatewayConfig; c = GatewayConfig(); print(c.get_chora_composer_config())"

# Expected: BackendConfig with enabled=True if API key present
```

**Solutions:**
1. Set `ANTHROPIC_API_KEY` environment variable
2. Verify chora-compose installed: `pip list | grep chora`
3. Check backend timeout: increase if needed

---

### Issue: n8n container networking

**Symptoms:**
- n8n can't reach localhost services
- Scripts work outside Docker but not in n8n

**Solution:**
Use host networking or Docker internal networking:
```bash
# Option 1: Run n8n with host network
docker run -d --network host --name n8n n8nio/n8n

# Option 2: Use Docker internal DNS
# Access mcp-n8n via container name if both in same network
```

---

## Current Limitations (v0.2.0)

1. **STDIO Transport Only:** No HTTP endpoint yet
   - **Workaround:** Use Execute Command pattern
   - **Timeline:** HTTP transport in v0.3.0+

2. **No Event Monitoring:** Cannot track workflow progress
   - **Impact:** Can't correlate multi-step workflows
   - **Blocker:** chora-compose v1.3.0 (event emission)
   - **Timeline:** Phase 1 Week 5-6

3. **Manual Tool Calls:** No native n8n node
   - **Workaround:** Use wrapper script
   - **Timeline:** Custom node in Phase 3 Week 12

4. **No Credential Pre-Validation:** May fail mid-workflow
   - **Impact:** Unexpected failures
   - **Timeline:** Phase 1 Week 3

---

## Next Steps

### Immediate (This Week)

1. ☐ Test mcp-tool.sh script with your n8n instance
2. ☐ Import "Hello World" workflow (once created)
3. ☐ Create first test artifact

### Phase 1 (Weeks 3-6)

1. ☐ Implement credential pre-validation
2. ☐ Add event monitoring foundation (waiting on chora-compose v1.3.0)
3. ☐ Build "Weekly Engineering Report" workflow

### Phase 3 (Weeks 11-14)

1. ☐ Develop custom n8n node package
2. ☐ Publish `@chora/mcp-tool-call` to npm
3. ☐ Create advanced workflow templates

---

## Resources

**Documentation:**
- [mcp-n8n README](../README.md)
- [mcp-n8n Architecture](../ARCHITECTURE.md)
- [UNIFIED_ROADMAP](UNIFIED_ROADMAP.md)
- [chora-compose Documentation](../vendors/chora-compose/docs/)

**n8n Documentation:**
- [n8n Docs](https://docs.n8n.io/)
- [Execute Command Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)
- [Custom Nodes](https://docs.n8n.io/integrations/creating-nodes/)

**Examples:**
- `workflows/` directory (to be created)
- `examples/` in chora-compose

---

**Status:** v1.0 - Initial guide for v0.2.0
**Next Update:** After Phase 1 Week 3 (credential validation)
**Maintainer:** victor@example.com
