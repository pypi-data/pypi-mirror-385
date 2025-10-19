# mcp-n8n: MCP Gateway & Aggregator

[![Template](https://img.shields.io/badge/template-chora--base-blue)](https://github.com/liminalcommons/chora-base)

A **Pattern P5 (Gateway & Aggregator)** MCP server that provides a unified interface to multiple specialized MCP servers, with **Chora Composer** as the exclusive artifact creation mechanism.

**🎯 This project's infrastructure has been extracted to [chora-base](https://github.com/liminalcommons/chora-base)** - a reusable Python project template for LLM-intelligent development. See the chora-base repo for adoption guides (works with existing repos, no submodule required).

## Overview

mcp-n8n follows the **Meta-MCP Server** pattern from the MCP Server Patterns Catalog, aggregating:

- **Chora Composer MCP** - Exclusive artifact generation and assembly
- **Coda MCP** - Data operations (list, read, write to Coda docs)
- **Future integrations** - n8n workflows, additional data sources

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         AI Client (Claude Desktop / Cursor)             │
└────────────────────┬────────────────────────────────────┘
                     │ JSON-RPC / stdio
                     ▼
┌─────────────────────────────────────────────────────────┐
│              mcp-n8n Gateway/Aggregator                 │
│                                                          │
│  Routes by namespace:                                   │
│  - chora:* → Chora Composer (artifacts)                 │
│  - coda:* → Coda MCP (data operations)                  │
└──────┬────────────────┬────────────────────────────────┘
       │                │
       ▼                ▼
┌──────────────┐ ┌─────────────┐
│ Chora        │ │ Coda MCP    │
│ Composer     │ │ Server      │
└──────────────┘ └─────────────┘
```

## Features

- **Tool Namespacing**: All tools namespaced by backend (e.g., `chora:assemble_artifact`, `coda:list_docs`)
- **Unified Interface**: Single MCP server connection for multiple capabilities
- **Artifact Enforcement**: All artifact creation routed exclusively to Chora Composer
- **STDIO Transport**: Compatible with Claude Desktop and Cursor
- **DRSO-Aligned**: Telemetry and change signals following Chora Platform patterns
- **Agent Memory System** (Phase 4.5): Cross-session learning with event log, knowledge graph, and trace correlation
- **CLI Tools** (Phase 4.6): `chora-memory` command for querying events, managing knowledge, and tracking agent profiles
- **Production-Ready Integration** (Phase 0): Real chora-composer backend integration validated with 19 passing tests
- **Performance Validated** (Phase 0): Gateway overhead < 0.001ms per call, 2500x faster than targets

## Installation

### Production Install (Recommended)

```bash
# Install from PyPI (includes chora-compose dependency)
pip install mcp-n8n

# Set environment variables
export ANTHROPIC_API_KEY=your_key
export CODA_API_KEY=your_key

# Run the gateway
mcp-n8n
```

### Development Install

#### Option 1: With Submodules (Recommended for Development)

```bash
# Clone repository with submodules
git clone --recurse-submodules https://github.com/yourusername/mcp-n8n.git
cd mcp-n8n

# Initialize submodules if not already done
git submodule update --init --recursive

# One-command setup (installs dependencies, hooks, and runs checks)
./scripts/setup.sh
```

#### Option 2: Manual Setup

```bash
# Clone repository
git clone https://github.com/yourusername/mcp-n8n.git
cd mcp-n8n

# Initialize submodules (for chora-compose v1.3.0)
git submodule update --init --recursive

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Using Just (Recommended)

Install [just](https://github.com/casey/just) for easier task management:

```bash
# macOS
brew install just

# Other platforms: https://github.com/casey/just#installation
```

## Dependencies

### Core Dependencies

mcp-n8n depends on:
- **chora-compose** (>= 1.3.0) - Artifact generation and assembly backend
- **fastmcp** - MCP server framework
- **pydantic** - Configuration management
- **aiohttp** - Async HTTP client

### Dependency Installation Methods

mcp-n8n supports **two methods** for accessing chora-compose:

- **Package Dependency:** Automatically installed when you `pip install mcp-n8n`
- Managed by pip/PyPI (currently pinned to v1.3.0+)
- Recommended for all use cases

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Gateway configuration
MCP_N8N_LOG_LEVEL=INFO

# Backend: Chora Composer
ANTHROPIC_API_KEY=your_anthropic_key

# Backend: Coda MCP
CODA_API_KEY=your_coda_key
CODA_FOLDER_ID=your_folder_id  # Optional, for write operations
```

### Configuration Management

mcp-n8n supports **dual configurations** for safe development:

- **Stable**: Uses published package from PyPI (for production)
- **Dev**: Uses local editable install (for development)

**Quick setup:**

```bash
# For Claude Desktop
cp .config/claude-desktop.example.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# For Cursor
cp .config/cursor-mcp.example.json ~/.cursor/mcp.json

# Edit config to:
# 1. Choose stable OR dev mode
# 2. Add your API keys
# 3. Update paths to match your system

# Restart Claude Desktop or Cursor
```

**Detailed guides:**
- [Configuration README](.config/README.md) - Complete setup instructions
- [Dev vs Stable Guide](.config/dev-vs-stable.md) - Toggle between modes

### Client Configuration

#### Claude Desktop (macOS)

**Stable (Production):**
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

**Dev (Local Development):**
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
        "MCP_N8N_DEBUG": "1"
      }
    }
  }
}
```

#### Cursor

See [.config/cursor-mcp.example.json](.config/cursor-mcp.example.json) for complete examples.

## Available Tools

### Chora Composer (Artifacts)

- `chora:generate_content` - Generate content from templates
- `chora:assemble_artifact` - Assemble artifacts from content pieces
- `chora:list_generators` - List available content generators
- `chora:validate_content` - Validate content or configurations

### Coda MCP (Data Operations)

- `coda:list_docs` - List Coda documents
- `coda:list_tables` - List tables in a document
- `coda:list_rows` - List rows from a table
- `coda:create_hello_doc_in_folder` - Create a sample document

## Usage Example

```python
# Client requests artifact assembly
tools/call {
  "name": "chora:assemble_artifact",
  "arguments": {
    "artifact_config_id": "user-documentation",
    "output_path": "/output/docs.md"
  }
}

# Gateway routes to Chora Composer
# Returns assembled artifact details
{
  "success": true,
  "artifact_id": "user-documentation",
  "output_path": "/output/docs.md",
  "content_count": 5,
  "size_bytes": 15234
}
```

## Development

### Using Just (Recommended)

```bash
# Show all available commands
just --list

# Environment management
just venv-create    # Create virtual environment
just venv-clean     # Clean rebuild venv
just check-env      # Validate environment setup

# Testing
just test           # Run all tests
just smoke          # Quick smoke tests (<30s)
just test-coverage  # Run tests with coverage

# Quality checks
just check          # Run all quality checks (lint + typecheck + format)
just pre-commit     # Run pre-commit hooks on all files
just verify         # Full verification (pre-commit + smoke + tests)

# Running the gateway
just run            # Start the gateway server
just run-debug      # Start with debug logging

# Utilities
just clean          # Clean build artifacts
just info           # Show environment info
```

### Manual Commands

```bash
# Run tests
pytest

# Type checking
mypy src/mcp_n8n

# Linting
ruff check src/mcp_n8n
black --check src/mcp_n8n

# Run gateway directly
mcp-n8n
```

### Development Workflow Scripts

For single-developer multi-instance workflow (context-switching between mcp-n8n and chora-composer):

```bash
# Setup new project clone
./scripts/setup.sh

# Run integration tests (Sprint 2 Day 3 checkpoint)
./scripts/integration-test.sh

# Prepare context switch to another codebase
./scripts/handoff.sh chora-composer
# (Follow instructions to complete handoff)
```

### CI/CD

GitHub Actions run automatically on push and PR:
- **Test Workflow** (`.github/workflows/test.yml`) - Runs tests on Python 3.11 and 3.12
- **Lint Workflow** (`.github/workflows/lint.yml`) - Runs linting checks

## Architecture Details

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed implementation of the P5 Gateway & Aggregator pattern.

---

## For Contributors

We welcome contributions! Here's how to get started:

### Quick Start

1. **Read the contributing guide:** [CONTRIBUTING.md](CONTRIBUTING.md)
2. **Set up your environment:** `./scripts/venv-create.sh`
3. **Run tests:** `just smoke`
4. **Make your changes** and submit a PR

### Documentation

**For Human Contributors:**
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines, code style, PR process
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Developer deep dive, architecture, debugging
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)** - Release process (maintainers)

**For AI Coding Agents:**
- **[AGENTS.md](AGENTS.md)** - Machine-readable project instructions (OpenAI/Google/Sourcegraph standard)

### Development Tools

```bash
# Automated diagnostics
just diagnose

# Development server (auto-reload, verbose logging)
just dev-server

# Pre-merge checks (before submitting PR)
just pre-merge

# VSCode configuration
# Open project in VSCode - debug configs already set up!
```

### Troubleshooting

Having issues? Try these:

1. **Environment check:** `just check-env`
2. **Diagnostics:** `just diagnose`
3. **Common issues:** See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
4. **Ask for help:** [GitHub Discussions](https://github.com/yourusername/mcp-n8n/discussions)

---

## Project Principles

This project follows DRSO (Development, Release, Security, Operations) principles:

- Value scenarios define all features
- BDD scenarios validate behavior
- Telemetry tracks all operations
- Change signals coordinate releases

## License

MIT License - see [LICENSE](LICENSE)

## Template Origin

This project's infrastructure was extracted to **[chora-base](https://github.com/liminalcommons/chora-base)** v1.0.0 - a reusable Python project template for LLM-intelligent development.

### Template-Derived Files (45 files)

**Boilerplate extracted to chora-base:**
- **Scripts** (`scripts/*.sh`) - 18 automation scripts (setup, test, CI/CD helpers)
- **GitHub Actions** (`.github/workflows/*.yml`) - 7 CI/CD workflows
- **Memory System** (`src/mcp_n8n/memory/`) - event_log.py, knowledge_graph.py, trace.py
- **Config Files** - `.pre-commit-config.yaml`, `.editorconfig`, `justfile`, `.env.example`
- **Documentation** - `CONTRIBUTING.md`, `.chora/memory/README.md`, boilerplate sections in `AGENTS.md`

### mcp-n8n-Specific Files (12+ core files)

**Gateway logic (NOT in template):**
- `src/mcp_n8n/gateway.py` - FastMCP server, main entry point
- `src/mcp_n8n/config.py` - Gateway configuration with backend factory methods
- `src/mcp_n8n/logging_config.py` - Structured logging setup
- `src/mcp_n8n/backends/` - Backend integration (base.py, registry.py, chora_composer.py, coda_mcp.py)
- `src/mcp_n8n/memory/profiles.py` - Agent profiles (Phase 4.6)
- `src/mcp_n8n/cli/commands.py` - mcp-n8n-specific CLI commands
- `tests/` - Gateway-specific tests (integration, config, registry)
- `chora-composer/`, `vendors/` - Submodules
- **Project docs** - ARCHITECTURE.md, UNIFIED_ROADMAP.md, PERFORMANCE_BASELINE.md, etc.

### Updating from Template

```bash
# Review template updates (do not auto-apply)
copier update --dry-run gh:liminalcommons/chora-base

# Selectively cherry-pick useful improvements
# Example: Copy improved CI workflow from template
copier copy gh:liminalcommons/chora-base /tmp/template-check
cp /tmp/template-check/.github/workflows/release.yml .github/workflows/
git commit -m "chore: Sync release.yml from chora-base v1.1.0"
```

**Sync Cadence:** Review chora-base releases quarterly, cherry-pick improvements as needed.

## Related Projects

- **[chora-base](https://github.com/liminalcommons/chora-base)** - Python project template (extracted from this project's Phase 4.5/4.6)
- **[chora-compose](https://github.com/liminalcommons/chora-compose)** - Configuration-driven artifact generation (PyPI package)
