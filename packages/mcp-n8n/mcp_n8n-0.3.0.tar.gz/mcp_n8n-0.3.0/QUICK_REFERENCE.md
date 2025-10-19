# mcp-n8n Quick Reference

## Installation

```bash
# Install mcp-n8n
pip install -e ".[dev]"

# Install backends
cd chora-composer && pip install -e .
# Coda MCP is optional - install separately if needed

# Configure
cp .env.example .env
# Edit .env with your API keys
```

## Running

```bash
# Start gateway
mcp-n8n

# With debug logging
MCP_N8N_DEBUG=1 mcp-n8n
```

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...    # For Chora Composer
CODA_API_KEY=...                # For Coda MCP

# Optional
CODA_FOLDER_ID=...              # For Coda write ops
MCP_N8N_LOG_LEVEL=INFO          # Log level
MCP_N8N_DEBUG=0                 # Debug mode
MCP_N8N_BACKEND_TIMEOUT=30      # Timeout (seconds)
```

## Available Tools

### Chora Composer (`chora:*`)

```bash
chora:generate_content          # Generate from template
chora:assemble_artifact         # PRIMARY ARTIFACT TOOL
chora:list_generators           # List generators
chora:validate_content          # Validate config
```

### Coda MCP (`coda:*`)

```bash
coda:list_docs                  # List documents
coda:list_tables                # List tables
coda:list_rows                  # List rows
coda:create_hello_doc_in_folder # Create sample doc
```

### Gateway (`gateway_status`)

```bash
gateway_status                  # Health check
```

## Tool Call Examples

### Assemble Artifact

```json
{
  "name": "chora:assemble_artifact",
  "arguments": {
    "artifact_config_id": "user-documentation",
    "output_path": "/output/docs.md",
    "force": false
  }
}
```

### List Coda Documents

```json
{
  "name": "coda:list_docs",
  "arguments": {
    "query": "project",
    "limit": 10
  }
}
```

### Gateway Status

```json
{
  "name": "gateway_status",
  "arguments": {}
}
```

## Client Configuration

### Claude Desktop (macOS)

File: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-n8n": {
      "command": "mcp-n8n",
      "args": [],
      "env": {}
    }
  }
}
```

### Cursor

File: `~/.cursor/mcp.json`

```json
{
  "servers": {
    "mcp-n8n": {
      "type": "stdio",
      "command": "mcp-n8n",
      "args": [],
      "env": {}
    }
  }
}
```

## Development

```bash
# Run tests
pytest

# With coverage
pytest --cov=mcp_n8n

# Type check
mypy src/mcp_n8n

# Lint
ruff check src/mcp_n8n
black src/mcp_n8n

# Format
black src/mcp_n8n
```

## Architecture

```
Client
  ↓ JSON-RPC/STDIO
Gateway (mcp-n8n)
  ↓
Backend Registry
  ↓
┌─────────┬─────────┐
│ Chora   │ Coda    │
│Composer │ MCP     │
└─────────┴─────────┘
```

## Common Workflows

### 1. Create Artifact

```
1. chora:generate_content (sections)
2. chora:assemble_artifact (combine)
3. coda:create_row (log metadata)
```

### 2. Document Coda DB

```
1. coda:list_docs (find doc)
2. coda:list_tables (get schemas)
3. chora:generate_content (document)
4. chora:assemble_artifact (final docs)
```

## Troubleshooting

### Backend Won't Start

```bash
# Check command exists
which chora-compose
which coda-mcp

# Check API keys
grep ANTHROPIC_API_KEY .env
grep CODA_API_KEY .env

# Test backend directly
chora-compose  # Should wait for input
```

### Tool Not Found

```bash
# Use namespaced name
✅ chora:assemble_artifact
❌ assemble_artifact

# Check backend status
# Use gateway_status tool
```

### Permission Error

```bash
# Check output directory
ls -la /output/

# Check Coda API key permissions
# Verify in Coda settings
```

## File Structure

```
mcp-n8n/
├── src/mcp_n8n/
│   ├── gateway.py        # Main server
│   ├── config.py         # Config management
│   └── backends/
│       ├── base.py       # Abstract backend
│       ├── registry.py   # Backend registry
│       ├── chora_composer.py
│       └── coda_mcp.py
└── tests/
    ├── test_config.py
    └── test_registry.py
```

## Key Concepts

### Tool Namespacing

All tools prefixed by backend:
- `chora:*` → Chora Composer
- `coda:*` → Coda MCP
- No prefix → Gateway tools

### Backend Lifecycle

```
STOPPED → STARTING → RUNNING
                  ↓
                FAILED
```

### Routing

```
chora:assemble_artifact
  │
  ├─ Parse namespace: "chora"
  ├─ Lookup backend: ChoraComposerBackend
  ├─ Strip namespace: "assemble_artifact"
  └─ Forward to subprocess
```

## Logging

```bash
# Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
MCP_N8N_LOG_LEVEL=DEBUG mcp-n8n

# Logs go to stderr
mcp-n8n 2> gateway.log
```

## Adding a Backend

```python
# 1. Create backend class
class MyBackend(StdioSubprocessBackend):
    async def _initialize(self):
        self._tools = [...]

# 2. Add to config.py
def get_my_backend_config(self) -> BackendConfig:
    return BackendConfig(name="my-backend", ...)

# 3. Register
def get_all_backend_configs(self):
    return [..., self.get_my_backend_config()]
```

## Resources

- Architecture: `ARCHITECTURE.md`
- Setup Guide: `GETTING_STARTED.md`
- Summary: `INTEGRATION_SUMMARY.md`
- Chora Composer: `chora-composer/README.md`
- Coda MCP: Optional backend (see Coda MCP documentation)

## Support

- Issues: GitHub Issues
- Docs: Source code docstrings
- MCP Spec: https://modelcontextprotocol.io/
