# Getting Started with mcp-n8n

This guide will help you set up and use the mcp-n8n gateway to integrate Chora Composer and Coda MCP through a unified MCP interface.

## Prerequisites

- **Python 3.11+** installed
- **API Keys**:
  - Anthropic API key (for Chora Composer)
  - Coda API key (for Coda MCP)
- **MCP Client**: Claude Desktop or Cursor with Roo Code

## Installation

### 1. Clone the Repository

```bash
cd /path/to/mcp-n8n
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- `mcp-n8n` package in editable mode
- FastMCP and dependencies
- Development tools (pytest, mypy, ruff)

### 4. Install Backend Servers

#### Chora Composer

```bash
cd chora-composer
pip install -e .
```

Verify installation:
```bash
which chora-compose
chora-compose --version
```

#### Coda MCP

```bash
# Coda MCP is an optional backend - install separately if needed
pip install -e .
```

Verify installation:
```bash
which coda-mcp
coda-mcp --help
```

## Configuration

### 1. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Set API Keys

Edit `.env` and add your credentials:

```env
# Required for Chora Composer
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Required for Coda MCP
CODA_API_KEY=your-coda-api-key-here

# Optional: For Coda write operations
CODA_FOLDER_ID=your-folder-id-here

# Optional: Gateway settings
MCP_N8N_LOG_LEVEL=INFO
MCP_N8N_DEBUG=0
```

### 3. Verify Configuration

Test that the gateway can load configuration:

```bash
python -c "from mcp_n8n.config import load_config; c = load_config(); print(f'Backends: {len(c.get_all_backend_configs())}')"
```

Expected output: `Backends: 2` (if both API keys are set)

## Usage

### Running the Gateway

Start the gateway server:

```bash
mcp-n8n
```

You should see output like:

```
============================================================
mcp-n8n Gateway v0.1.0
Pattern P5: Gateway & Aggregator
============================================================

Configuration:
  Log Level: INFO
  Debug: False
  Backend Timeout: 30s

Backends configured: 2
  ✓ chora-composer (chora:*) - ['artifacts', 'content_generation']
  ✓ coda-mcp (coda:*) - ['data_operations', 'documents']

Starting gateway on STDIO transport...
------------------------------------------------------------
```

### Testing the Gateway

#### 1. Check Gateway Status

The gateway exposes a `gateway_status` tool:

```bash
# Using mcp-cli or similar tool
mcp-cli call gateway_status
```

#### 2. List Available Tools

Send a `tools/list` request to see all aggregated tools:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

Expected response includes:
- `chora:generate_content`
- `chora:assemble_artifact`
- `chora:list_generators`
- `chora:validate_content`
- `coda:list_docs`
- `coda:list_tables`
- `coda:list_rows`
- `coda:create_hello_doc_in_folder`

## Integrating with AI Clients

### Claude Desktop (macOS)

1. **Locate config file**:
   ```bash
   open ~/Library/Application\ Support/Claude/
   ```

2. **Edit `claude_desktop_config.json`**:
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

3. **Restart Claude Desktop**

4. **Verify integration**:
   - Open Claude Desktop
   - Look for MCP icon in corner
   - Check that `mcp-n8n` appears in server list
   - Verify tools are available

### Cursor (Roo Code)

1. **Locate config file**:
   ```bash
   code ~/.cursor/mcp.json
   ```

2. **Edit `mcp.json`**:
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

3. **Restart Cursor**

4. **Verify integration**:
   - Open Cursor
   - Check Roo Code extension
   - Verify `mcp-n8n` server is connected

## Example Workflows

### Workflow 1: Create an Artifact

1. **Generate content pieces** using Chora Composer:
   ```
   Use chora:generate_content to create:
   - Introduction section
   - Features section
   - Usage guide section
   ```

2. **Assemble into artifact**:
   ```
   Use chora:assemble_artifact with config:
   - artifact_config_id: "user-documentation"
   - output_path: "/output/user-guide.md"
   ```

3. **Store metadata** in Coda:
   ```
   Use coda:create_row to log:
   - Artifact ID
   - Creation timestamp
   - Output path
   ```

### Workflow 2: Document a Coda Database

1. **List documents**:
   ```
   Use coda:list_docs to find target doc
   ```

2. **List tables**:
   ```
   Use coda:list_tables with doc_id
   ```

3. **Generate documentation**:
   ```
   Use chora:generate_content with template:
   - Input: table schemas
   - Output: markdown documentation
   ```

4. **Assemble final docs**:
   ```
   Use chora:assemble_artifact to combine:
   - Overview
   - Table schemas
   - Usage examples
   ```

## Troubleshooting

### Backend Not Starting

**Symptom**: Gateway shows backend as FAILED

**Solutions**:
1. Check API keys are set correctly in `.env`
2. Verify backend command is in PATH: `which chora-compose`
3. Test backend directly: `chora-compose` (should start and wait for input)
4. Check logs for errors

### Tool Not Found

**Symptom**: Client reports tool doesn't exist

**Solutions**:
1. Verify tool name includes namespace: `chora:assemble_artifact` not `assemble_artifact`
2. Check backend is running: use `gateway_status` tool
3. Verify backend registered tools: check gateway startup logs

### Permission Errors

**Symptom**: Cannot write artifacts or access Coda

**Solutions**:
1. Check API key permissions
2. Verify output directory exists and is writable
3. For Coda: verify API key has write access to folder

### Gateway Crashes on Startup

**Symptom**: Gateway exits immediately

**Solutions**:
1. Check Python version: `python --version` (need 3.11+)
2. Reinstall dependencies: `pip install -e ".[dev]"`
3. Run with debug: `MCP_N8N_DEBUG=1 mcp-n8n`
4. Check for conflicting packages: `pip list | grep mcp`

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=mcp_n8n --cov-report=html

# Specific test file
pytest tests/test_config.py

# Verbose output
pytest -v
```

### Type Checking

```bash
mypy src/mcp_n8n
```

### Linting

```bash
# Check
ruff check src/mcp_n8n

# Fix
ruff check --fix src/mcp_n8n

# Format
black src/mcp_n8n
```

### Adding a New Backend

See [ARCHITECTURE.md](ARCHITECTURE.md#adding-a-new-backend) for detailed instructions.

Quick steps:
1. Create backend class in `src/mcp_n8n/backends/`
2. Add configuration helper in `config.py`
3. Register in `get_all_backend_configs()`
4. Test and document

## Next Steps

- **Read the Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Explore Examples**: Check example workflows above
- **Add Custom Backends**: Integrate your own MCP servers
- **Configure Telemetry**: Set up DRSO-aligned observability

## Getting Help

- **Issues**: Report bugs on GitHub
- **Questions**: Open a discussion
- **Documentation**: Read the source code docstrings

## Related Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Chora Composer Documentation](./chora-composer/README.md)
- Coda MCP Documentation (optional backend)
- [FastMCP SDK](https://github.com/anthropics/mcp-python)
