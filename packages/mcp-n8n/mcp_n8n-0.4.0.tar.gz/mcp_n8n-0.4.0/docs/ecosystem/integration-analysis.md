# Chora Compose in the Chora Ecosystem: Architecture & Integration Analysis

**Date:** 2025-10-12
**Version:** 1.0.0
**Status:** Strategic Analysis

---

## Executive Summary

Chora Compose (Chora Compose) is a **configuration-driven content and artifact generation framework** that should serve as a **foundational capability** in the Chora ecosystem, not own infrastructure concerns like storage backends. This analysis examines how Chora Compose fits into the broader ecosystem and identifies complementary projects needed for full value realization.

**Key Insight:** Chora Compose's strength is **workflow orchestration and content generation logic** - it should delegate storage, discovery, orchestration, and telemetry to specialized ecosystem components.

---

## Table of Contents

1. [What Chora Compose Is & Isn't](#what-hawf-is--isnt)
2. [Ecosystem Context](#ecosystem-context)
3. [Storage Architecture Recommendations](#storage-architecture-recommendations)
4. [Integration Points](#integration-points)
5. [Ecosystem Projects Analysis](#ecosystem-projects-analysis)
6. [Recommended Architecture](#recommended-architecture)
7. [Implementation Roadmap](#implementation-roadmap)

---

## What Chora Compose Is & Isn't

### Chora Compose's Core Responsibilities ✅

**What Chora Compose SHOULD Own:**

1. **Configuration Schema & Validation**
   - Content config structure (v3.1)
   - Artifact config structure (v3.1)
   - JSON Schema validation
   - Pydantic models

2. **Content Generation Logic**
   - Generator implementations (Demonstration, Jinja2)
   - Template rendering
   - Element composition
   - Context resolution (Phase 2)

3. **Data Transformation Pipeline**
   - Data selectors (JSONPath, line ranges, markdown sections, code extraction)
   - Input source resolution
   - Context passing to generators

4. **Artifact Composition**
   - Multiple content assembly
   - Composition strategies (concat, merge, etc.)
   - Output file generation

5. **Workflow Orchestration**
   - Config loading pipeline
   - Generation pipeline
   - Dependency resolution

### What Chora Compose Should NOT Own ❌

**Delegate to Ecosystem:**

1. **Storage Management**
   - ❌ PostgreSQL connection/schema management
   - ❌ Vector database operations
   - ❌ LAN/network file storage
   - ❌ S3/blob storage
   - ❌ Cache eviction policies
   - ✅ **Instead:** Define storage interfaces, let ecosystem provide implementations

2. **Discovery & Registry**
   - ❌ Service discovery logic
   - ❌ MCP server registry
   - ❌ Capability catalog
   - ✅ **Instead:** Emit manifests, let chora-platform discover

3. **Orchestration**
   - ❌ Workflow scheduling (cron, event-driven)
   - ❌ Parallel execution management
   - ❌ Long-running job management
   - ✅ **Instead:** Expose CLI/API, let mcp-n8n orchestrate

4. **Telemetry Collection**
   - ❌ Metrics database
   - ❌ Log aggregation
   - ❌ Tracing backend
   - ✅ **Instead:** Emit events, let chora-platform collect

---

## Ecosystem Context

### The Chora Ecosystem Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     chora-workspace                             │
│                  (Development Coordination)                      │
│  - Cross-cutting documentation                                  │
│  - Shared tooling coordination                                  │
│  - Submodule orchestration                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ chora-platform   │  │ mcp-orchestration│  │   mcp-n8n        │
│  (Standards &    │  │  (MCP Registry & │  │  (Workflow       │
│   Governance)    │  │   Lifecycle)     │  │   Automation)    │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ • Standards      │  │ • MCP server     │  │ • n8n runtime    │
│ • Validators     │  │   registry       │  │ • DRSO workflows │
│ • Discovery      │  │ • Server         │  │ • Event-driven   │
│ • Telemetry      │  │   lifecycle      │  │   automation     │
│ • Change signals │  │ • Manifest mgmt  │  │ • Ambient intel  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Chora Compose (Future)  │
                    │  (Content Gen)   │
                    ├──────────────────┤
                    │ • Config schemas │
                    │ • Generators     │
                    │ • Composition    │
                    │ • Data transform │
                    └──────────────────┘
```

### Key Ecosystem Principles (from solution-neutral-intent.md)

1. **Manifested Capabilities** - Every reusable asset declares metadata
2. **Capability Discovery** - Participants can search "Who provides X?"
3. **Change Signaling** - Structured notifications for cross-project coordination
4. **DRSO Workflow** - Development, Release, Security, Operations as capability
5. **Modular Boundaries** - Clear responsibilities per repo type

### DRSO Workflow (STD-003)

All capability repos follow gate-based progression:

1. **Status Gate** - Validate lifecycle readiness
2. **Coverage Gate** - Ensure value scenarios tested (≥80% coverage)
3. **Security Gate** - Generate SBOM, audit dependencies, sign artifacts
4. **Release Gate** - Create manifest, publish artifacts, emit telemetry
5. **Ack Gate** - Verify consumer ingestion

**Chora Compose Impact:** Chora Compose should be a **capability repo** following full DRSO workflow.

---

## Storage Architecture Recommendations

### Current State: EphemeralStorageManager

**What exists today:**
```python
class EphemeralStorageManager:
    """Manages ephemeral storage with versioning and retention."""

    def __init__(self, base_path: Path, retention_days: int = 30):
        self.base_path = base_path  # Local filesystem only

    def save(self, content_id: str, content: str, format: str = "txt"):
        # Saves to: base_path/content_id/v1_timestamp.txt
        pass

    def retrieve(self, content_id: str, strategy: str = "latest"):
        # Retrieves from filesystem
        pass
```

**Problems:**
- ❌ Hardcoded to local filesystem
- ❌ No support for PostgreSQL
- ❌ No support for S3/network storage
- ❌ No vector database integration
- ❌ Each storage type would require new EphemeralStorageManager subclass

### Recommended: Storage Adapter Pattern

**Design Philosophy:**
> "Chora Compose defines WHAT to store and HOW to retrieve it. Ecosystem provides WHERE to store it."

**Interface-Based Architecture:**

```python
# Chora Compose defines the interface
class StorageBackend(Protocol):
    """Storage backend interface that ecosystem can implement."""

    def save(
        self,
        artifact_id: str,
        content_id: str,
        content: str | bytes,
        metadata: dict[str, Any],
        format: str = "txt"
    ) -> StorageVersion:
        """Save content with versioning."""
        ...

    def retrieve(
        self,
        artifact_id: str,
        content_id: str,
        strategy: str = "latest"
    ) -> str | bytes | list[str | bytes]:
        """Retrieve content by strategy."""
        ...

    def list_versions(
        self,
        artifact_id: str,
        content_id: str
    ) -> list[StorageVersion]:
        """List all versions."""
        ...

    def cleanup(
        self,
        retention_days: int,
        dry_run: bool = False
    ) -> CleanupResult:
        """Remove old versions."""
        ...

# Chora Compose provides reference implementation
class FilesystemStorageBackend(StorageBackend):
    """Local filesystem implementation (current EphemeralStorageManager)."""
    pass

# Ecosystem provides additional implementations
class PostgresStorageBackend(StorageBackend):
    """PostgreSQL implementation with JSONB storage."""

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self._ensure_schema()

    def save(self, artifact_id: str, content_id: str, content: str, ...):
        # INSERT INTO hawf_storage (artifact_id, content_id, version, content, metadata, created_at)
        pass

class VectorStorageBackend(StorageBackend):
    """Vector database for semantic search (pgvector, Pinecone, etc)."""

    def save(self, artifact_id: str, content_id: str, content: str, ...):
        # Embed content and store in vector DB
        # Store original content + embedding
        pass

    def retrieve(self, artifact_id: str, content_id: str, strategy: str):
        # If strategy starts with "semantic:", do vector search
        # Otherwise, retrieve by ID
        pass

class S3StorageBackend(StorageBackend):
    """S3-compatible object storage."""

    def save(self, artifact_id: str, content_id: str, content: str, ...):
        # PUT to s3://bucket/artifact_id/content_id/v{version}_{timestamp}.{format}
        pass
```

**Usage in Chora Compose:**

```python
class ArtifactComposer:
    def __init__(
        self,
        storage_backend: StorageBackend | None = None,  # ← Accept interface
        ...
    ):
        # Default to filesystem, but accept any backend
        self.storage_backend = storage_backend or FilesystemStorageBackend(
            base_path=Path("ephemeral")
        )

        self.context_resolver = ContextResolver(
            storage_backend=self.storage_backend,  # ← Pass to resolver
            ...
        )
```

**Benefits:**
- ✅ Chora Compose owns interface definition
- ✅ Ecosystem provides backend implementations
- ✅ Users choose backend at runtime
- ✅ No Chora Compose code changes for new backends
- ✅ Testing easier (mock backends)
- ✅ Clear separation of concerns

---

## Integration Points

### 1. Chora Compose → chora-platform Integration

**Chora Compose Provides:**
- Manifest describing Chora Compose capabilities
- Value scenarios with automated tests
- Telemetry events for generation pipeline
- Standard-compliant documentation

**chora-platform Provides:**
- Standards for manifest structure
- Validators for manifest compliance
- Discovery indexing
- Change signal coordination
- Telemetry collection endpoint

**Integration Mechanism:**

```yaml
# chora-compose/manifest.yaml
capability:
  id: hawf-content-generation
  name: Chora Compose Content Generation
  version: 0.6.0
  owner: hawf-team
  repository: https://github.com/liminalcommons/chora-compose

intent:
  id: CONTENT-GEN-FROM-CONFIG
  title: Configuration-Driven Content Generation
  summary: >
    Generate artifacts from declarative configs with versioning,
    composition, and data transformation capabilities.

behaviors:
  - id: compose-artifact
    description: Assemble artifact from multiple content configs
    automated_test: tests/test_composer.py::test_assemble_kernel_artifact

  - id: resolve-external-sources
    description: Resolve external file, config, and ephemeral sources
    automated_test: tests/test_context_resolver.py

  - id: apply-data-selectors
    description: Transform source data with JSONPath, line ranges, etc.
    automated_test: tests/test_data_selector.py

interfaces:
  cli:
    - command: hawf generate <artifact-id>
      description: Generate artifact from config

  python:
    - class: ArtifactComposer
      method: assemble
      signature: "assemble(artifact_id: str, ...) -> Path"

  mcp:  # Future Phase 4
    - tool: hawf_generate_artifact
      description: Generate artifact via MCP

dependencies:
  - pydantic: ^2.0
  - jinja2: ^3.0
  - jsonschema: ^4.0
  - jsonpath-ng: ^1.6

telemetry_events:
  - artifact.generation.started
  - artifact.generation.completed
  - artifact.generation.failed
  - content.loaded
  - source.resolved
  - selector.applied

value_scenarios:
  - id: VS-Chora Compose-001
    title: Generate Documentation Artifact
    guide: docs/how-to/generate-artifact.md
    automated_test: tests/integration/test_phase2_workflow.py
    status: ready

drso:
  gates: [status, coverage, security, release, ack]
  coverage_target: 95%
  test_suite: pytest
```

**Validation:**
```bash
# chora-platform validates Chora Compose manifest
chora-cli validate manifest chora-compose/manifest.yaml

# chora-platform discovers Chora Compose capability
chora-cli discover --query "content generation"
# Returns: hawf-content-generation (v0.6.0)
```

---

### 2. Chora Compose → mcp-orchestration Integration

**Chora Compose Provides:**
- CLI for generation
- Python API for programmatic use
- Future: MCP server with generation tools

**mcp-orchestration Provides:**
- MCP server registry
- Server lifecycle management
- Manifest publication

**Integration (Phase 4):**

```python
# chora-compose/src/chora_compose/mcp/server.py
from mcp.server import Server
from chora_compose.core.composer import ArtifactComposer

app = Server("hawf-content-generation")

@app.tool()
def generate_artifact(
    artifact_id: str,
    artifact_path: str | None = None,
    output_path: str | None = None,
    storage_backend: str = "filesystem"
) -> dict:
    """Generate artifact from configuration.

    Args:
        artifact_id: ID of artifact to generate
        artifact_path: Optional path to artifact config
        output_path: Optional output override
        storage_backend: Backend to use (filesystem, postgres, s3)

    Returns:
        {
            "success": true,
            "output_path": "/path/to/output.md",
            "duration_ms": 1234
        }
    """
    # Create composer with specified backend
    backend = get_storage_backend(storage_backend)
    composer = ArtifactComposer(storage_backend=backend)

    # Generate
    output = composer.assemble(artifact_id, artifact_path, output_path)

    return {
        "success": True,
        "output_path": str(output),
        "artifact_id": artifact_id
    }

@app.tool()
def resolve_context(
    sources: list[dict],
    base_path: str | None = None
) -> dict:
    """Resolve input sources and return context dict."""
    resolver = ContextResolver(base_path=base_path)
    context = resolver.resolve(sources)
    return context

@app.resource("hawf://configs/{artifact_id}")
def get_config(artifact_id: str) -> str:
    """Retrieve artifact config as JSON."""
    loader = ConfigLoader()
    config = loader.load_artifact_config(artifact_id)
    return config.model_dump_json()
```

**MCP Server Manifest:**
```json
{
  "name": "hawf-content-generation",
  "version": "0.6.0",
  "description": "Generate artifacts from declarative configs",
  "tools": [
    {
      "name": "generate_artifact",
      "description": "Generate artifact from configuration",
      "inputSchema": {
        "type": "object",
        "properties": {
          "artifact_id": {"type": "string"},
          "artifact_path": {"type": "string"},
          "storage_backend": {
            "type": "string",
            "enum": ["filesystem", "postgres", "s3", "vector"]
          }
        },
        "required": ["artifact_id"]
      }
    }
  ],
  "resources": [
    {
      "uriTemplate": "hawf://configs/{artifact_id}",
      "name": "Artifact Configuration",
      "description": "Retrieve artifact config by ID"
    }
  ]
}
```

**Registration:**
```bash
# Register Chora Compose MCP server with mcp-orchestration
mcp-registry register \
  --manifest chora-compose/mcp-manifest.json \
  --server-path chora-compose/src/chora_compose/mcp/server.py
```

---

### 3. Chora Compose → mcp-n8n Integration

**Chora Compose Provides:**
- CLI commands for n8n to execute
- Webhook endpoints for generation triggers
- Status endpoints for workflow monitoring

**mcp-n8n Provides:**
- Workflow orchestration (scheduled, event-driven)
- Integration with other services
- Ambient intelligence coordination

**Use Cases:**

#### Use Case 1: Scheduled Documentation Generation
```
[n8n Schedule Trigger: Daily 2am]
    ↓
[Execute Command: hawf generate changelog --output docs/CHANGELOG.md]
    ↓
[Check Exit Code]
    ↓ success
[Git Commit + Push]
    ↓
[Emit Telemetry: artifact.generated]
    ↓
[Notify Team: Slack webhook]
```

#### Use Case 2: PR-Triggered Release Notes
```
[GitHub Webhook: PR merged to main]
    ↓
[Extract PR metadata]
    ↓
[Create release data JSON]
    ↓
[Execute: hawf generate release-notes --data pr-data.json]
    ↓
[Post release notes as GitHub comment]
    ↓
[Emit Telemetry: release.notes.generated]
```

#### Use Case 3: Multi-Artifact Pipeline
```
[Change Signal: SIG-release-ready]
    ↓
[Parallel Execution]
    ├─ [hawf generate changelog]
    ├─ [hawf generate api-reference]
    ├─ [hawf generate status-report]
    └─ [hawf generate release-notes]
    ↓ (wait for all)
[Aggregate outputs]
    ↓
[Create release bundle]
    ↓
[Emit: release.bundle.ready]
```

**n8n Workflow Definition:**
```json
{
  "name": "Chora Compose Documentation Pipeline",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "value": "0 2 * * *"}]
        }
      }
    },
    {
      "name": "Generate Changelog",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "hawf generate changelog --artifact-path configs/artifacts/changelog.json"
      }
    },
    {
      "name": "Check Success",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [
            {"value1": "={{$node.Generate Changelog.exitCode}}", "value2": 0}
          ]
        }
      }
    },
    {
      "name": "Emit Telemetry",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://chora-platform:9000/telemetry",
        "method": "POST",
        "body": {
          "event_type": "artifact.generated",
          "source": {"repo": "docs", "artifact": "changelog"},
          "data": {"version": "{{$workflow.version}}"}
        }
      }
    }
  ]
}
```

---

### 4. Storage Backend Ecosystem Integration

**PostgreSQL Backend (Ecosystem Project)**

New repo: `hawf-storage-postgres`

```python
# hawf-storage-postgres/src/hawf_postgres/backend.py
from sqlalchemy import create_engine, Table, Column, String, Text, DateTime, Integer
from chora_compose.storage.base import StorageBackend

class PostgresStorageBackend(StorageBackend):
    """PostgreSQL storage backend for Chora Compose."""

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self._ensure_schema()

    def _ensure_schema(self):
        """Create tables if they don't exist."""
        # CREATE TABLE hawf_artifacts (...)
        # CREATE TABLE hawf_content (...)
        # CREATE INDEX idx_artifact_content ON hawf_content(artifact_id, content_id)
        pass

    def save(self, artifact_id, content_id, content, metadata, format):
        # INSERT with versioning
        # Use PostgreSQL's SERIAL for version numbers
        pass

    def retrieve(self, artifact_id, content_id, strategy):
        # SELECT based on strategy
        # "latest": ORDER BY version DESC LIMIT 1
        # "all": ORDER BY version DESC
        # "version:N": WHERE version = N
        pass
```

**Usage:**
```python
from chora_compose.core.composer import ArtifactComposer
from hawf_postgres.backend import PostgresStorageBackend

# Use PostgreSQL for storage
backend = PostgresStorageBackend(
    connection_string="postgresql://user:pass@localhost/hawf"
)

composer = ArtifactComposer(storage_backend=backend)
```

**Vector Storage Backend (Ecosystem Project)**

New repo: `hawf-storage-vector`

```python
# hawf-storage-vector/src/hawf_vector/backend.py
from pgvector.sqlalchemy import Vector
from chora_compose.storage.base import StorageBackend

class VectorStorageBackend(StorageBackend):
    """Vector database storage with semantic search."""

    def __init__(self, connection_string: str, embedding_model: str = "openai"):
        self.engine = create_engine(connection_string)
        self.embedder = get_embedder(embedding_model)

    def save(self, artifact_id, content_id, content, metadata, format):
        # Generate embedding
        embedding = self.embedder.embed(content)

        # Store with vector
        # INSERT INTO hawf_vectors (artifact_id, content_id, content, embedding, ...)
        pass

    def retrieve(self, artifact_id, content_id, strategy):
        if strategy.startswith("semantic:"):
            # Extract query from strategy: "semantic:search for documentation"
            query = strategy.split(":", 1)[1]
            return self._semantic_search(query, artifact_id)
        else:
            # Regular retrieval by ID
            return self._retrieve_by_id(artifact_id, content_id, strategy)

    def _semantic_search(self, query: str, artifact_id: str) -> list[str]:
        """Find content by semantic similarity."""
        query_embedding = self.embedder.embed(query)

        # SELECT content FROM hawf_vectors
        # WHERE artifact_id = ?
        # ORDER BY embedding <-> query_embedding
        # LIMIT 5
        pass
```

**Configuration:**
```python
# Use vector storage with semantic retrieval
backend = VectorStorageBackend(
    connection_string="postgresql://localhost/hawf",
    embedding_model="openai"
)

# Content config can use semantic search
{
  "inputs": {
    "sources": [{
      "id": "related_docs",
      "type": "ephemeral_output",
      "artifact_id": "documentation",
      "content_id": "all",
      "retrieval_strategy": "semantic:find documentation about Phase 2"
    }]
  }
}
```

---

## Ecosystem Projects Analysis

### Existing Projects

#### 1. chora-workspace
**Role:** Development coordination workspace
**Responsibilities:**
- Cross-cutting documentation
- Submodule coordination
- Shared tooling hosting

**Chora Compose Relationship:**
- Chora Compose could be added as submodule
- chora-workspace docs could use Chora Compose for generation
- Tutorial: "Use Chora Compose to generate your capability docs"

#### 2. chora-platform
**Role:** Standards, discovery, telemetry
**Responsibilities:**
- Standards curation (STD-001, STD-003, etc.)
- Manifest validation
- Discovery indexing
- Telemetry collection
- Change signal coordination

**Chora Compose Relationship:**
- **Chora Compose depends on chora-platform** for:
  - Manifest schema (STD-001)
  - DRSO workflow (STD-003)
  - Telemetry schema (STD-005)
- **chora-platform could use Chora Compose** for:
  - Generating standard documentation
  - Generating capability catalogs
  - Generating release manifests

**Integration Example:**
```python
# chora-platform uses Chora Compose to generate capability catalog
from chora_compose.core.composer import ArtifactComposer

def generate_capability_catalog():
    """Generate ecosystem capability catalog."""
    composer = ArtifactComposer()

    # Use Chora Compose to generate from discovery data
    composer.assemble(
        artifact_id="capability-catalog",
        artifact_path=Path("configs/artifacts/capability-catalog.json")
    )
```

#### 3. mcp-orchestration
**Role:** MCP registry and lifecycle management
**Responsibilities:**
- MCP server registry
- Server manifest management
- Lifecycle coordination

**Chora Compose Relationship:**
- **Chora Compose will register as MCP server** (Phase 4)
- **mcp-orchestration manages Chora Compose MCP server**
- **Chora Compose could generate MCP manifests** for other servers

**Future Enhancement:**
```bash
# Use Chora Compose to generate MCP server manifest
hawf generate mcp-manifest \
  --data my-server-info.json \
  --output mcp-manifest.json

# Register with mcp-orchestration
mcp-registry register --manifest mcp-manifest.json
```

#### 4. mcp-n8n
**Role:** Workflow automation via n8n
**Responsibilities:**
- n8n runtime hosting
- DRSO workflow automation
- Ambient intelligence orchestration

**Chora Compose Relationship:**
- **mcp-n8n orchestrates Chora Compose** via CLI/API
- **n8n workflows trigger Chora Compose generation**
- **Chora Compose generates n8n workflow configs** (meta!)

**Use Cases:**
- Scheduled artifact generation
- PR-triggered documentation updates
- Multi-artifact pipelines
- Event-driven content generation

---

### Missing Ecosystem Projects

#### 1. hawf-storage-postgres ⚠️ **NEEDED**
**Purpose:** PostgreSQL storage backend for Chora Compose

**Responsibilities:**
- Implement `StorageBackend` interface
- Manage PostgreSQL schema
- Version management in SQL
- Query optimization

**Why Separate Repo:**
- Chora Compose stays storage-agnostic
- PostgreSQL experts own optimization
- Different release cycle
- Optional dependency

**Interfaces:**
```python
from hawf_postgres import PostgresStorageBackend

backend = PostgresStorageBackend("postgresql://localhost/hawf")
composer = ArtifactComposer(storage_backend=backend)
```

---

#### 2. hawf-storage-vector ⚠️ **NEEDED**
**Purpose:** Vector database backend with semantic search

**Responsibilities:**
- Implement `StorageBackend` interface
- Embedding generation (OpenAI, local models)
- Vector similarity search
- Hybrid search (vector + metadata)

**Why Separate Repo:**
- Complex ML dependencies
- Multiple embedding model options
- Performance tuning
- Cost optimization

---

#### 3. hawf-cli-tools 🟡 **USEFUL**
**Purpose:** CLI utilities for Chora Compose workflows

**Responsibilities:**
- Rich CLI with typer/click
- Interactive config generation
- Config validation
- Artifact preview
- Batch generation

**Commands:**
```bash
hawf init               # Interactive config creation
hawf validate           # Validate configs
hawf preview            # Preview without generating
hawf generate           # Generate artifact
hawf batch              # Generate multiple artifacts
hawf watch              # Watch configs and regenerate
```

**Why Separate Repo:**
- CLI can evolve independently
- Rich dependencies (rich, typer, click)
- User-facing UX decisions
- Cross-platform testing

---

#### 4. hawf-mcp-server 🟡 **PLANNED (Phase 4)**
**Purpose:** MCP server exposing Chora Compose capabilities

**Responsibilities:**
- Implement MCP protocol
- Expose generation tools
- Provide config resources
- Handle streaming outputs

**Tools:**
- `generate_artifact`
- `resolve_context`
- `apply_selector`
- `validate_config`

**Resources:**
- `hawf://configs/{id}`
- `hawf://outputs/{artifact_id}`
- `hawf://templates/{type}`

**Why Separate Repo:**
- Different protocol concerns
- MCP SDK dependencies
- Server lifecycle management
- Can be versioned independently

---

#### 5. hawf-integrations 🟢 **OPTIONAL**
**Purpose:** Pre-built integrations with common tools

**Integrations:**
- **GitHub Actions** - Workflow for artifact generation
- **GitLab CI** - Pipeline templates
- **Pre-commit hooks** - Generate docs on commit
- **VSCode Extension** - Config editor + preview
- **Jupyter Notebooks** - Generate from notebook cells

**Example: GitHub Action**
```yaml
# .github/workflows/generate-docs.yml
name: Generate Documentation
on: [push]
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: hawf-integrations/github-action@v1
        with:
          artifacts: changelog,api-reference,status-report
          storage-backend: postgres
          postgres-url: ${{ secrets.POSTGRES_URL }}
      - uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "docs: regenerate artifacts"
```

---

#### 6. hawf-templates 🟢 **OPTIONAL**
**Purpose:** Community templates and examples

**Contents:**
- Common artifact templates
- Content config examples
- Generator templates
- Best practices
- Patterns library

**Structure:**
```
hawf-templates/
├── artifacts/
│   ├── changelog/
│   ├── release-notes/
│   ├── api-reference/
│   └── status-report/
├── content/
│   ├── documentation/
│   ├── code-generation/
│   └── test-generation/
├── generators/
│   ├── openapi-generator/
│   ├── graphql-generator/
│   └── markdown-processor/
└── examples/
    ├── documentation-site/
    ├── api-docs/
    └── living-documentation/
```

---

## Recommended Architecture

### System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User / Developer                         │
└────────────┬────────────────────────────────────────────────────┘
             │ Uses
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Chora Compose CLI / API                             │
│  - hawf generate                                                │
│  - hawf validate                                                │
│  - hawf preview                                                 │
└────────────┬────────────────────────────────────────────────────┘
             │ Calls
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Chora Compose Core (chora-compose)                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ ArtifactComposer                                          │ │
│  │  ├─ ConfigLoader                                          │ │
│  │  ├─ ContextResolver ──→ StorageBackend (interface)       │ │
│  │  ├─ DataSelector                                          │ │
│  │  └─ Generators (Demonstration, Jinja2, ...)              │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────┬────────────────────────────────────────────────────┘
             │ Uses
             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Storage Backend Implementations                     │
│  (User chooses at runtime)                                      │
├─────────────────────────────────────────────────────────────────┤
│ FilesystemBackend  │ PostgresBackend  │ VectorBackend │ S3...  │
│ (chora-compose)      │ (ecosystem)      │ (ecosystem)   │        │
└─────────────────────────────────────────────────────────────────┘
             │ Orchestrated by
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ecosystem Services                           │
├─────────────────────────────────────────────────────────────────┤
│ mcp-n8n            │ chora-platform    │ mcp-orchestration     │
│ - Workflow trigger │ - Discovery       │ - MCP registry        │
│ - Scheduling       │ - Telemetry       │ - Lifecycle mgmt      │
│ - Orchestration    │ - Validation      │                       │
└─────────────────────────────────────────────────────────────────┘
```

### Dependency Flow

```
chora-compose (core)
  ├─ Defines: StorageBackend interface
  ├─ Provides: FilesystemBackend (reference)
  ├─ Depends on: pydantic, jinja2, jsonschema
  └─ Integrates with: chora-platform (standards)

hawf-storage-postgres (ecosystem)
  ├─ Implements: StorageBackend
  ├─ Depends on: chora-compose, sqlalchemy, psycopg2
  └─ Manages: PostgreSQL schema

hawf-storage-vector (ecosystem)
  ├─ Implements: StorageBackend
  ├─ Depends on: chora-compose, pgvector, openai/transformers
  └─ Manages: Vector embeddings

hawf-mcp-server (ecosystem, Phase 4)
  ├─ Uses: chora-compose API
  ├─ Depends on: chora-compose, mcp-sdk
  ├─ Registers with: mcp-orchestration
  └─ Orchestrated by: mcp-n8n

mcp-n8n (ecosystem)
  ├─ Calls: hawf CLI/API
  ├─ Triggers: Artifact generation
  └─ Monitors: Generation status

chora-platform (ecosystem)
  ├─ Provides: Standards for Chora Compose
  ├─ Validates: Chora Compose manifests
  ├─ Discovers: Chora Compose capabilities
  └─ Collects: Chora Compose telemetry
```

---

## Implementation Roadmap

### Phase 1: Storage Abstraction (1 week)

**Goal:** Refactor Chora Compose to use storage backend interface

**Tasks:**
1. Define `StorageBackend` protocol in `chora_compose/storage/base.py`
2. Refactor `EphemeralStorageManager` → `FilesystemStorageBackend`
3. Update `ContextResolver` to accept `StorageBackend`
4. Update `ArtifactComposer` to accept `StorageBackend`
5. Add documentation: "Implementing Storage Backends"
6. Update all tests

**Deliverable:**
```python
# Clean interface separation
from chora_compose.storage.base import StorageBackend
from chora_compose.storage.filesystem import FilesystemStorageBackend

# Users can implement their own
class MyCustomBackend(StorageBackend):
    pass
```

---

### Phase 2: Ecosystem Storage Backends (2 weeks)

**Goal:** Create PostgreSQL and S3 backend implementations

**Tasks:**

**Week 1: hawf-storage-postgres**
1. Create new repo: `hawf-storage-postgres`
2. Implement `PostgresStorageBackend`
3. Design schema (artifacts, content, versions)
4. Add connection pooling
5. Implement all StorageBackend methods
6. Write comprehensive tests
7. Document usage and configuration

**Week 2: hawf-storage-s3**
1. Create new repo: `hawf-storage-s3`
2. Implement `S3StorageBackend`
3. Support S3-compatible services (MinIO, etc.)
4. Add multipart upload for large artifacts
5. Implement versioning with S3 versions
6. Write comprehensive tests
7. Document usage and configuration

**Deliverables:**
- `hawf-storage-postgres` package on PyPI
- `hawf-storage-s3` package on PyPI
- Documentation for each

---

### Phase 3: Chora Platform Integration (1 week)

**Goal:** Register Chora Compose as capability in chora-platform

**Tasks:**
1. Create Chora Compose manifest following STD-001
2. Define value scenarios (STD-004)
3. Implement DRSO workflow (STD-003)
4. Add telemetry events (STD-005)
5. Register with chora-platform discovery
6. Document integration patterns

**Deliverable:**
```bash
# Chora Compose discoverable in ecosystem
chora-cli discover --query "content generation"
# → hawf-content-generation (v0.6.0)

# Chora Compose follows DRSO workflow
chora-cli drso status --repo chora-compose
# → All gates passing
```

---

### Phase 4: MCP Server (2 weeks)

**Goal:** Expose Chora Compose capabilities via MCP protocol

**Tasks:**
1. Create `hawf-mcp-server` repo
2. Implement MCP tools
3. Implement MCP resources
4. Add streaming support for large artifacts
5. Register with mcp-orchestration
6. Create Claude Desktop integration
7. Write comprehensive documentation

**Deliverable:**
- MCP server exposing Chora Compose via tools
- Registered in MCP registry
- Usable by Claude Desktop and other MCP clients

---

### Phase 5: n8n Integration (1 week)

**Goal:** Create n8n workflows for common Chora Compose use cases

**Tasks:**
1. Design workflow templates
2. Implement scheduled generation
3. Implement event-driven generation
4. Create webhook endpoints
5. Add status monitoring
6. Document workflows

**Deliverable:**
- Pre-built n8n workflows for Chora Compose
- Documentation: "Orchestrating Chora Compose with n8n"

---

### Phase 6: Vector Storage (2 weeks)

**Goal:** Add semantic search capabilities

**Tasks:**
1. Create `hawf-storage-vector` repo
2. Implement `VectorStorageBackend`
3. Add embedding generation
4. Implement semantic search
5. Support multiple embedding models
6. Add hybrid search (vector + metadata)
7. Optimize performance

**Deliverable:**
- Vector storage backend with semantic search
- Documentation: "Semantic Content Retrieval"

---

## Conclusion

### Key Recommendations

1. **Keep Chora Compose Focused**
   - ✅ Own: Configuration, generation, composition
   - ❌ Don't own: Storage backends, orchestration, discovery

2. **Use Adapter Pattern for Storage**
   - Define `StorageBackend` interface
   - Provide filesystem reference implementation
   - Let ecosystem provide specialized backends

3. **Integrate with Chora Platform**
   - Follow STD-001, STD-003, STD-004, STD-005
   - Emit telemetry events
   - Publish manifest for discovery

4. **Enable Orchestration**
   - Provide CLI for mcp-n8n to call
   - Expose MCP server (Phase 4)
   - Support event-driven generation

5. **Create Ecosystem Projects**
   - `hawf-storage-postgres` - PostgreSQL backend
   - `hawf-storage-vector` - Vector search
   - `hawf-mcp-server` - MCP protocol
   - `hawf-cli-tools` - Rich CLI
   - `hawf-integrations` - GitHub Actions, CI/CD

### Value Proposition

**Chora Compose becomes the "content generation engine" of the Chora ecosystem:**

- 📝 **Generation:** Chora Compose generates artifacts from configs
- 🗄️ **Storage:** Ecosystem backends (PostgreSQL, vector, S3)
- 🔍 **Discovery:** chora-platform indexes Chora Compose capabilities
- 🔄 **Orchestration:** mcp-n8n triggers Chora Compose workflows
- 🔌 **Integration:** MCP server exposes to AI agents
- 📊 **Observability:** Telemetry flows to chora-platform

**Result:** Composable, discoverable, orchestrated content generation that integrates seamlessly with the broader ecosystem.

---

**Document Status:** Strategic Analysis Complete
**Next Steps:** Review with team, prioritize phases, begin Phase 1
**Last Updated:** 2025-10-12
