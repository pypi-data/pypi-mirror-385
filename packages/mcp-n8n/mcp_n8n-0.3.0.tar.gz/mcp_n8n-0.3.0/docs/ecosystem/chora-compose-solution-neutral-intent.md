# Chora-Compose Solution-Neutral Intent Document

**Version:** 1.1.0
**Date:** 2025-10-16
**Status:** Draft
**Document Type:** Solution-Neutral Intent
**Scope:** Chora-Compose Integration Patterns within Chora Ecosystem
**Supersedes:** None (initial version)
**Related:**
- [docs/ecosystem/ecosystem-intent.md](ecosystem-intent.md) - Ecosystem architecture
- [docs/ecosystem/drso-integrated-intent.md](drso-integrated-intent.md) - DRSO workflow
- [docs/ecosystem/n8n-solution-neutral-intent.md](n8n-solution-neutral-intent.md) - n8n integration patterns
- [docs/mcp/tool-reference.md](../mcp/tool-reference.md) - MCP tool specifications
- [docs/reference/architecture/ADR-0008-modularization-boundaries.md](../reference/architecture/ADR-0008-modularization-boundaries.md)

---

## Executive Summary

This document defines the **solution-neutral intent** for **Chora-Compose** as a modular content generation and artifact assembly capability within the Chora ecosystem. Chora-Compose serves as an **AI-powered documentation engine** that can function as:

1. **Content Generator** - Create documentation from templates and context via LLM
2. **Artifact Assembler** - Compose multi-section artifacts from configs
3. **MCP Server** - Expose 17 tools to AI agents for autonomous documentation (v1.1.0)
4. **Config Lifecycle Manager** - Enable conversational workflow authoring through draft/test/save cycle (v1.1.0)
5. **Capability Discovery Hub** - Provide 5 resources for agent self-configuration (v1.1.0)
6. **Template Ecosystem** - Provide reusable Jinja2 templates with composability
7. **Validation Layer** - Ensure generated content meets quality standards
8. **Self-Documenting System** - Uses its own tools to generate its documentation (virtuous cycle)

The intent is to establish Chora-Compose as a **flexible, config-driven content generation platform** that enables rapid documentation development while maintaining DRSO (Development → Release → Security → Operations) principles and alignment with the 3-layer Chora Platform architecture.

### Core Principles

1. **Documentation-Driven** - Templates and configs written FIRST, generation follows
2. **Config-First Design** - YAML configs drive all generation (no hardcoded logic)
3. **Template Composability** - Jinja2 templates can include/extend other templates
4. **Type Safety** - Pydantic models validate all inputs/outputs
5. **MCP-Native** - Primary interface is Model Context Protocol tools
6. **Self-Validation** - System generates its own documentation (dogfooding)

### Chora-Compose Value Proposition

**Chora-Compose** is an **AI-native documentation platform** that provides:

- **17 MCP Tools** - Comprehensive content generation and config lifecycle capabilities (v1.1.0)
  - 13 core tools: generate_content, assemble_artifact, list_generators, validate_content, regenerate_content, preview_generation, batch_generate, list_content_configs, list_artifacts, cleanup_ephemeral, delete_content, trace_dependencies, list_artifact_configs
  - 4 config lifecycle tools: draft_config, test_config, save_config, modify_config
- **5 MCP Resources** - Dynamic capability discovery (v1.1.0)
  - capabilities://server, capabilities://tools, capabilities://resources, capabilities://generators
  - Legacy: config://, schema://, content://, generator://
- **Type-Safe Models** - Comprehensive Pydantic type system with validation
- **Template Hierarchy** - Jinja2 templates + YAML configs + JSON schemas
- **Multi-Format Output** - Markdown, HTML, PDF, JSON
- **Virtuous Cycles** - Self-generates documentation to prove correctness
- **Extensible** - Custom generators and validators via plugins

**Strategic Fit in Ecosystem:**

- **Accelerates Documentation** - AI-powered generation vs. manual writing
- **Ensures Consistency** - Templates enforce standards across projects
- **Enables Automation** - MCP tools integrate with n8n, CI/CD, agents
- **Supports DRSO** - Documentation-driven design aligns with DRSO Gate 1-5
- **Aligns with 3-Layer Architecture** - Functions as Platform-layer capability

### Relationship to Ecosystem

```
Chora Ecosystem Architecture
    ├─ Ecosystem Intent (high-level architecture)
    ├─ DRSO Intent (workflow specifics)
    ├─ n8n Intent (workflow orchestration)
    └─ Chora-Compose Intent (content generation) ← THIS DOCUMENT
```

**Chora-Compose complements:**

- **n8n** - Can be invoked FROM n8n workflows (Pattern N3 MCP client)
- **DRSO** - Generates documentation for DRSO gates (ADRs, CRs, Features)
- **MCP Ecosystem** - Provides content generation tools for other MCP servers
- **Platform Tools** - Generates repo overviews, capability catalogs, release notes

---

## Part 1: Foundation

### 1.1 Motivation

Development teams require **comprehensive, up-to-date documentation** to onboard contributors, coordinate changes, and maintain quality. Traditional documentation approaches create several problems:

**Current Gaps:**

1. **Manual Documentation Burden** - Writing docs by hand is time-consuming and error-prone
2. **Documentation Drift** - Docs fall out of sync with code as projects evolve
3. **Inconsistent Standards** - Each project has unique documentation structure and style
4. **Poor Discoverability** - Generated content not indexed or searchable
5. **No Automation** - Documentation generation not integrated with CI/CD
6. **Limited AI Integration** - AI agents can't autonomously generate documentation

**Chora-Compose addresses these problems** by providing:

1. **Template-Driven Generation** - Write templates once, generate docs many times
2. **Config-Based Consistency** - YAML configs ensure standardized structure
3. **AI-Powered Content** - LLM generates content from context and examples
4. **MCP Integration** - AI agents can trigger generation autonomously
5. **Multi-Source Aggregation** - Combine data from APIs, files, databases
6. **Quality Validation** - Automated checks ensure generated content meets standards

### 1.2 Problem Statement

Modern software ecosystems require **documentation infrastructure** that can:

- **Generate** - Create content from templates and context (AI-powered)
- **Assemble** - Compose multi-section artifacts from reusable components
- **Validate** - Ensure generated content meets quality standards
- **Integrate** - Work with CI/CD, n8n workflows, MCP agents
- **Scale** - Support multiple projects with shared templates

**Current Gap:**

- Manual documentation scales poorly across multi-repo ecosystems
- AI agents lack standardized tools for documentation generation
- No ecosystem-wide template library for common documentation types
- Quality validation happens manually (if at all)
- Documentation workflows disconnected from development workflows

### 1.3 Chora-Compose Solution

**Chora-Compose** is a **config-driven content generation platform** that provides:

#### 17 MCP Tools (v1.1.0)

**Core Generation Tools:**
1. **generate_content** - Generate content from template and context
2. **assemble_artifact** - Assemble multi-section artifact from config
3. **regenerate_content** - Force regeneration bypassing cache
4. **preview_generation** - Preview without persistence
5. **batch_generate** - Parallel content generation

**Config Management Tools:**
6. **list_generators** - Query available generators and validators
7. **validate_content** - Validate generated content against rules
8. **list_content_configs** - Browse content configurations
9. **list_artifact_configs** - Browse artifact configurations
10. **list_artifacts** - List available artifacts
11. **trace_dependencies** - Analyze artifact dependencies

**Storage Management Tools:**
12. **cleanup_ephemeral** - Manage ephemeral storage retention
13. **delete_content** - Remove generated content

**Config Lifecycle Tools (v1.1.0):**
14. **draft_config** - Create ephemeral draft configs
15. **test_config** - Preview draft output
16. **modify_config** - Update draft configurations
17. **save_config** - Persist drafts to filesystem

#### 14 Pydantic Models

Comprehensive type system for:
- Generator configs, template metadata, content requests/responses
- Artifact assembly configs, section configs
- Registry queries, validation rules
- Error responses with detailed context

#### Template Ecosystem

- **Jinja2 Templates** - Composable, reusable, extensible
- **YAML Configs** - Drive generation without code changes
- **JSON Schemas** - Validate configs and outputs
- **Example Data** - Provide reference context for templates

#### Multi-Format Output

- **Markdown** - Primary format for documentation
- **HTML** - Rendered docs with styling
- **PDF** - Print-ready reports
- **JSON** - Structured data for programmatic consumption

#### Virtuous Cycles

- **Self-Documentation** - Chora-Compose generates its own docs
- **Template Validation** - Uses own tools to validate templates
- **DRSO Integration** - Passes all 5 gates using self-generated evidence

### 1.4 Scope of This Document

This document describes **what Chora-Compose integration should achieve** and **why**, not **how** to implement it technically. It covers:

**In Scope:**

- Integration patterns and use cases
- Architectural role in Chora ecosystem
- DRSO alignment and gate requirements
- Value scenarios and success criteria
- Deployment models and lifecycle management
- MCP tool specifications (conceptual)
- Template ecosystem design principles

**Out of Scope:**

- Specific template implementations (those belong in template library)
- Chora-Compose internal architecture (documented in code)
- Detailed API specifications (those belong in ADRs)
- LLM provider comparisons (Claude, GPT, etc.)
- Jinja2 tutorial (external resource)

---

## Part 2: Chora-Compose Integration Patterns

Chora-Compose can be integrated into the Chora ecosystem through **six distinct patterns**, each providing different value and complexity. These patterns are **modular** - implement them independently based on need.

### 2.1 Pattern C1: Standalone Content Generator

**Intent:** Run Chora-Compose as a CLI tool for local content generation, separate from MCP concerns.

**Capabilities:**

- Generate content from command line (`chora-compose generate`)
- Assemble artifacts from configs (`chora-compose assemble`)
- List available generators (`chora-compose list`)
- Validate generated content (`chora-compose validate`)

**Example Use Case:**

> **Scenario:** Developer needs to create API documentation from OpenAPI spec.
>
> **Command:**
> ```bash
> chora-compose generate \
>   --template api-reference \
>   --context openapi.yaml \
>   --output docs/api/reference.md
> ```
>
> **Output:** Markdown file with API endpoints, parameters, examples

**Architecture Position:**

```
Developer (manual invocation)
         ↕
    CLI Commands
         ↕
    Content Generation Engine
         ↕
    LLM Provider (Claude/GPT)
```

**Value:**

- ✅ Rapid prototyping of documentation
- ✅ No infrastructure required (local execution)
- ✅ Immediate feedback (see output instantly)

**Limitations:**

- ❌ Not accessible by AI agents (no MCP interface)
- ❌ No integration with n8n or CI/CD
- ❌ Manual execution only

**When to Use:**

- Quick one-off documentation tasks
- Local development and testing
- Learning Chora-Compose capabilities

---

### 2.2 Pattern C2: MCP Server

**Intent:** Expose Chora-Compose content generation as **MCP tools**, allowing AI agents to generate documentation on demand.

**Capabilities:**

- **generate_content** - AI agents request content generation
- **assemble_artifact** - AI agents compose multi-section docs
- **list_generators** - AI agents discover available templates
- **validate_content** - AI agents check content quality

**Example Use Case:**

> **AI Agent:** "Please generate a user guide for the new authentication feature."
>
> **Claude (via MCP):** Calls `generate_content` with:
> ```json
> {
>   "generator_id": "user-guide-feature",
>   "context": {
>     "feature_name": "Authentication",
>     "description": "OAuth2 + JWT tokens",
>     "endpoints": ["/login", "/logout", "/refresh"]
>   }
> }
> ```
>
> **Chora-Compose:** Generates markdown user guide from template
>
> **Claude:** "Here's your user guide: [content]"

**Architecture Position:**

```
AI Client (Claude Desktop, Cursor)
         ↓ JSON-RPC/MCP
    Chora-Compose MCP Server
         ↓ Python API
    Content Generation Engine
         ↓ HTTP/API
    LLM Provider
```

**Implementation Requirements:**

- MCP server wrapper around Chora-Compose core
- Tool schemas for all 4 MCP tools (inputSchema + output types)
- Handle async generation (content may take seconds)
- Stream progress as MCP resources (optional)
- Error handling with detailed context

**Value:**

- ✅ AI agents can autonomously generate documentation
- ✅ Templates become "skills" for AI agents
- ✅ Integration with Claude Desktop, Cursor, etc.

**Limitations:**

- ❌ Templates must be pre-created (AI can't write templates yet)
- ❌ Limited parameter validation (relies on Pydantic models)
- ❌ LLM costs for every generation

**When to Use:**

- Exposing documentation generation to AI agents
- Providing AI agents with content creation capabilities
- Automating documentation in AI-driven workflows

---

### 2.3 Pattern C3: MCP Client (Consuming Other Tools)

**Intent:** Allow Chora-Compose to **consume MCP tools** from other servers to gather context for generation.

**Capabilities:**

- Query **Coda MCP** for structured data (tables, docs)
- Query **Filesystem MCP** for code snippets
- Query **GitHub MCP** for issues, PRs, commits
- Combine data from multiple sources in single artifact

**Example Use Case:**

> **Scenario:** Generate weekly engineering report combining data from GitHub, Jira, and DataDog.
>
> **Config:**
> ```yaml
> artifact_config_id: weekly-engineering-report
> sections:
>   - id: commits
>     generator: github-commits-summary
>     mcp_tool: github:list_commits
>     mcp_args:
>       repo: chora-compose
>       since: "7 days ago"
>   - id: tickets
>     generator: jira-tickets-summary
>     mcp_tool: jira:search_issues
>     mcp_args:
>       jql: "status=Done AND updated >= -7d"
> ```
>
> **Chora-Compose:**
> 1. Calls `github:list_commits` via MCP
> 2. Calls `jira:search_issues` via MCP
> 3. Generates summary for each section
> 4. Assembles final report

**Architecture Position:**

```
Chora-Compose (MCP Client)
    ├─ Calls: GitHub MCP (list commits)
    ├─ Calls: Jira MCP (search issues)
    ├─ Calls: Coda MCP (fetch tables)
    └─ Generates: Combined artifact
```

**Implementation Requirements:**

- MCP client library (JSON-RPC over STDIO/HTTP)
- Support for async MCP calls (tools may take time)
- Error handling for MCP protocol errors
- Credential management for MCP servers
- Template integration (pass MCP results to Jinja2)

**Value:**

- ✅ Multi-source data aggregation in single artifact
- ✅ Leverage existing MCP ecosystem (40+ tools)
- ✅ Decoupled data fetching from content generation

**Limitations:**

- ❌ Requires MCP servers to be running
- ❌ Network latency for remote MCP calls
- ❌ Debugging across multiple MCP layers

**When to Use:**

- Artifacts requiring data from multiple systems
- Workflows leveraging existing MCP tools
- Complex reporting with external data sources

---

### 2.4 Pattern C4: Artifact Assembly Pipeline

**Intent:** Use Chora-Compose to **orchestrate multi-stage artifact creation**, combining template generation, validation, and output formatting.

**Capabilities:**

- Multi-section artifacts with distinct generators
- Sequential or parallel section generation
- Cross-section references (e.g., TOC from headings)
- Post-processing (Markdown → HTML → PDF)
- Validation at each stage

**Example Use Case:**

> **Scenario:** Generate comprehensive API documentation with 5 sections.
>
> **Pipeline:**
> ```yaml
> artifact_config_id: api-documentation-full
> sections:
>   - id: overview
>     generator: api-overview
>     depends_on: []  # No dependencies, can run first
>   - id: authentication
>     generator: api-auth-guide
>     depends_on: [overview]  # Needs overview context
>   - id: endpoints
>     generator: api-endpoint-reference
>     depends_on: [authentication]  # References auth schemes
>   - id: examples
>     generator: api-code-examples
>     depends_on: [endpoints]  # Uses endpoint definitions
>   - id: changelog
>     generator: api-changelog
>     depends_on: []  # Independent
> post_processing:
>   - type: validate
>     rules: [no-broken-links, proper-headings]
>   - type: convert
>     format: html
>   - type: convert
>     format: pdf
> ```
>
> **Execution:**
> 1. Generate overview and changelog (parallel)
> 2. Generate authentication (depends on overview)
> 3. Generate endpoints (depends on authentication)
> 4. Generate examples (depends on endpoints)
> 5. Validate combined artifact
> 6. Convert to HTML and PDF

**Architecture Position:**

```
Artifact Config (YAML)
    ↓
Pipeline Orchestrator
    ├─ Section 1 (generate)
    ├─ Section 2 (generate)
    ├─ Section 3 (generate)
    └─ Post-Processing
        ├─ Validate
        ├─ Convert (HTML)
        └─ Convert (PDF)
```

**Implementation Requirements:**

- Dependency resolution (topological sort of sections)
- Parallel execution where possible (no dependencies)
- Context passing between sections
- Post-processing plugins (validators, converters)
- Error recovery (retry failed sections)

**Value:**

- ✅ Complex multi-section artifacts with dependencies
- ✅ Parallel generation for speed
- ✅ Automated validation and conversion

**Limitations:**

- ❌ Config complexity grows with section count
- ❌ Debugging multi-stage failures requires detailed logs
- ❌ Performance depends on LLM API latency

**When to Use:**

- Large documentation projects (100+ pages)
- Artifacts with complex dependencies
- Workflows requiring validation and conversion

---

### 2.5 Pattern C5: Template Ecosystem

**Intent:** Provide a **reusable template library** with composability, versioning, and sharing across projects.

**Capabilities:**

- **Template Registry** - Centralized catalog of templates
- **Template Inheritance** - Jinja2 extends/includes for reuse
- **Template Versioning** - Semantic versions for templates
- **Template Sharing** - Publish/consume templates across repos
- **Template Testing** - Validate templates with example data

**Example Use Case:**

> **Scenario:** Create company-wide API documentation standard.
>
> **Template Hierarchy:**
> ```
> templates/
>   └─ base/
>       ├─ document-base.md.jinja  # Base layout
>       └─ api-base.md.jinja       # API-specific base
>           ├─ api-rest.md.jinja   # REST API variant
>           ├─ api-graphql.md.jinja # GraphQL API variant
>           └─ api-grpc.md.jinja   # gRPC API variant
> ```
>
> **Usage:**
> ```yaml
> # Product A uses REST template
> generator_id: product-a-api-docs
> template: api-rest.md.jinja  # Inherits from api-base, document-base
>
> # Product B uses GraphQL template
> generator_id: product-b-api-docs
> template: api-graphql.md.jinja  # Inherits same base
> ```
>
> **Benefit:** All products share base structure, diverge only where needed

**Architecture Position:**

```
Template Registry (catalog)
    ├─ base/
    │   ├─ document-base.md.jinja
    │   └─ api-base.md.jinja
    ├─ api/
    │   ├─ api-rest.md.jinja
    │   └─ api-graphql.md.jinja
    └─ reports/
        └─ weekly-report.md.jinja

Projects (consume templates)
    ├─ Product A → api-rest.md.jinja
    ├─ Product B → api-graphql.md.jinja
    └─ Product C → weekly-report.md.jinja
```

**Implementation Requirements:**

- Template metadata (version, author, dependencies)
- Dependency resolution (templates referencing other templates)
- Version compatibility checks
- Template testing framework (example data → expected output)
- Template documentation (usage guide, parameters)

**Value:**

- ✅ Reusable templates across ecosystem
- ✅ Consistent documentation standards
- ✅ Reduced template maintenance burden

**Limitations:**

- ❌ Template sprawl if not curated
- ❌ Breaking changes in base templates affect all consumers
- ❌ Governance needed for template approval

**When to Use:**

- Multi-project organizations
- Enforcing documentation standards
- Building reusable template library

---

### 2.6 Pattern C6: Validation Layer

**Intent:** Ensure generated content meets **quality standards** through automated validation rules.

**Capabilities:**

- **Structural Validation** - Check heading hierarchy, TOC, links
- **Content Validation** - Check spelling, grammar, tone
- **Compliance Validation** - Check required sections, metadata
- **Reference Validation** - Check cross-references, citations
- **Custom Validators** - Extensible validation rules

**Example Use Case:**

> **Scenario:** Validate generated API documentation meets company standards.
>
> **Validation Rules:**
> ```yaml
> validation_config:
>   rules:
>     - id: proper-headings
>       type: structural
>       check: heading_hierarchy  # No skipped levels (H1→H3)
>     - id: no-broken-links
>       type: reference
>       check: all_links_resolve
>     - id: required-sections
>       type: compliance
>       required: [overview, authentication, endpoints, examples]
>     - id: api-standards
>       type: content
>       checks:
>         - all_endpoints_documented
>         - all_parameters_typed
>         - all_errors_documented
> ```
>
> **Execution:**
> ```bash
> chora-compose validate \
>   --content docs/api/reference.md \
>   --rules validation_config.yaml
> ```
>
> **Output:**
> ```
> ✅ proper-headings: PASS
> ✅ no-broken-links: PASS
> ❌ required-sections: FAIL (missing 'examples' section)
> ✅ api-standards: PASS (all checks passed)
>
> Overall: FAIL (1 of 4 rules failed)
> ```

**Architecture Position:**

```
Generated Content (Markdown)
    ↓
Validation Engine
    ├─ Structural Validators
    ├─ Content Validators
    ├─ Compliance Validators
    └─ Custom Validators
    ↓
Validation Report (JSON)
```

**Implementation Requirements:**

- Validator plugin system (register custom validators)
- Markdown AST parsing (for structural validation)
- Link resolution (check URLs, internal references)
- Configurable severity (error, warning, info)
- Detailed error messages with line numbers

**Value:**

- ✅ Automated quality enforcement
- ✅ Catch issues before publication
- ✅ Consistent standards across projects

**Limitations:**

- ❌ False positives (overly strict rules)
- ❌ Validator maintenance burden
- ❌ May slow down generation workflow

**When to Use:**

- Quality-critical documentation (compliance, legal)
- Large teams with varying skill levels
- Enforcing documentation standards

---

### 2.7 Pattern C7: Conversational Config Development

**Intent:** Enable **iterative, conversational creation and refinement of configs** through draft/test/modify/save lifecycle without manual file editing.

**Capabilities:**

- **Draft Creation** - Create ephemeral config drafts from conversation
- **Preview Testing** - Test drafts with real data before persistence
- **Iterative Refinement** - Modify drafts based on preview feedback
- **Persistence Control** - Save validated drafts to filesystem only when ready
- **30-Day Retention** - Automatic cleanup of abandoned drafts

**Example Use Case:**

> **Scenario:** Product manager wants to create weekly OKR report without touching JSON files.
>
> **Conversation with Claude:**
>
> **User:** "Create a config for weekly OKR reports from Coda"
>
> **Claude (via MCP):**
> ```json
> draft_config({
>   "config_type": "content",
>   "config_data": {
>     "id": "weekly-okr-report",
>     "generation": {
>       "patterns": [{
>         "type": "jinja2",
>         "template": "okr-report.md.jinja"
>       }]
>     }
>   }
> })
> ```
> Returns: `draft_id: "draft_abc123"`
>
> **Claude:** "I've created a draft. Let me test it with this week's data..."
> ```json
> test_config({
>   "draft_id": "draft_abc123",
>   "context": {"week": "2025-W42"}
> })
> ```
>
> **Claude:** "The preview shows [summary]. Should I adjust the template or save this config?"
>
> **User:** "Add a section for blockers"
>
> **Claude:** "Updating the draft..."
> ```json
> modify_config({
>   "draft_id": "draft_abc123",
>   "updates": {
>     "generation.patterns[0].template": "okr-report-with-blockers.md.jinja"
>   }
> })
> ```
>
> **User:** "Perfect, save it"
>
> **Claude:**
> ```json
> save_config({
>   "draft_id": "draft_abc123",
>   "destination_path": "configs/content/weekly-okr-report.json"
> })
> ```
>
> **Claude:** "Saved! You can now generate reports with `generate_content` using config ID 'weekly-okr-report'."

**Architecture Position:**

```
User (Natural Language)
    ↓
AI Agent (Claude Desktop, Cursor)
    ↓ MCP Tools
EphemeralConfigManager
    ├─ draft_config → ephemeral/drafts/{content|artifact}/draft_*.json
    ├─ test_config → Preview with ConfigLoader + Generators
    ├─ modify_config → Update draft in ephemeral storage
    └─ save_config → Atomic copy to configs/{content|artifact}/
```

**Implementation Requirements:**

- Chora Compose v1.1.0+ with config lifecycle tools
- EphemeralConfigManager (30-day retention)
- JSON Schema validation on draft creation
- Atomic file operations for save
- Error handling for schema validation failures

**Value:**

- ✅ Zero IDE context switching (entire workflow in Claude Desktop)
- ✅ Instant feedback through test_config previews
- ✅ Safe experimentation (drafts auto-expire after 30 days)
- ✅ Schema validation before persistence (catch errors early)
- ✅ Non-technical users can create complex configs
- ✅ Conversational iteration (natural language refinement)

**Limitations:**

- ❌ Draft storage cleanup required after 30 days
- ❌ Complex nested configs may be harder to modify conversationally
- ❌ No version control for drafts (only persisted configs)
- ❌ Schema errors require understanding JSON structure

**When to Use:**

- Rapid prototyping of new generators
- Non-developer workflow creation
- Exploratory testing of template variations
- User-driven documentation generation
- Scenarios where IDE access is inconvenient

**Comparison to Traditional Workflow:**

| Traditional (File Editing) | Conversational (Pattern C7) |
|----------------------------|------------------------------|
| 1. Open IDE/editor | 1. Chat with Claude |
| 2. Create JSON file | 2. Claude calls `draft_config` |
| 3. Write config manually | 3. Claude generates config structure |
| 4. Save file | 4. Test with `test_config` |
| 5. Run generate command | 5. Iterate with `modify_config` |
| 6. Check output | 6. Save with `save_config` |
| 7. Fix errors, repeat | 7. Generate immediately |
| **Time:** 20-30 minutes | **Time:** 5-10 minutes |

---

## Part 3: Chora-Compose in 3-Layer Architecture

The Chora ecosystem follows a **3-layer architecture** (per ADR-0008):

1. **Workspace Layer** (R&D) - Development, testing, experimentation
2. **Platform Layer** (Distribution) - Stable packages, tooling, standards
3. **Capabilities Layer** (Consumption) - Production deployments, end-user services

### 3.1 Layer 1: Workspace (Development)

**Repository:** `chora-compose` (this repo)

**Role:** Development laboratory for content generation capabilities

**Contains:**

- Source code (`src/chora_compose/`)
- Tests (`tests/`)
- Templates (`templates/`)
- Configs (`configs/`)
- Documentation (`docs/`)
- DRSO infrastructure (`.drso/`)

**DRSO Self-Hosting:**

Chora-Compose **DOES** run DRSO on itself to:
- Validate that DRSO workflow works for content generation tools
- Generate its own documentation (virtuous cycle)
- Prove templates work in real scenarios
- Test MCP tools before ecosystem adoption

**Example Virtuous Cycle:**

```
VS-COMPOSE-001: MCP Tool Documentation
    ↓
Develop: chora-compose generate (content generator)
    ↓
Use: Generate docs/mcp/tool-reference.md using own tool
    ↓
Validate: If tool works, docs are generated
    ↓
Evidence: Documentation proves tool correctness
```

**Analogy:** The workshop where content generation tools are built and tested

---

### 3.2 Layer 2: Platform (Distribution)

**Repository:** `chora-platform`

**Role:** Distribute stable, versioned content generation capabilities

**Contains (future):**

- `chora_platform_tools/compose/` - Stable content generation tools
- `templates/` - Curated template library (base templates)
- `configs/` - Standard generator configs
- CLI integration: `chora-cli compose generate`

**Published as:** PyPI package `chora-platform>=0.7.0` (with Compose integration)

**OR Separate Package:** `chora-compose>=1.0.0` (if kept independent)

**DRSO Full Validation:**

Before platform integration:
- Gate 1: Tests for all 4 MCP tools
- Gate 2: 80%+ coverage (currently working toward this)
- Gate 3: 0 critical/high vulnerabilities
- Gate 4: Valid SBOM, manifest, package buildable
- Gate 5: Stakeholder approval, downstream integration tests

**Analogy:** The tool store where finished content generation tools are packaged

---

### 3.3 Layer 3: Capabilities (Consumption)

**Examples:**

- `mcp-orchestration` - Uses Chora-Compose to generate MCP server docs
- `chora-liminal` - Uses Chora-Compose for personal knowledge base
- Future: Any repo needing documentation automation

**Role:** Consume stable content generation capabilities

**Each contains:**

- Dependency: `chora-compose>=1.0.0` (or via `chora-platform`)
- Custom templates (project-specific)
- Generator configs (artifact assembly)
- Integration with CI/CD (auto-generate docs on commit)

**DRSO Independent Validation:**

Each capability repo:
- Can use Chora-Compose to generate DRSO evidence docs
- Runs own 5 gates independently
- Produces documentation using Chora-Compose tools

**Analogy:** Products built with content generation tools from the tool store

---

### 3.4 Flow: R&D → Stabilization → Consumption

```
┌──────────────────────────────────────────────────────────────┐
│              CHORA-COMPOSE LAYER FLOW                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  LAYER 1 (Workspace: chora-compose)                          │
│     ├─ Develop: 4 MCP tools + template system               │
│     ├─ Test: Run 5 gates on chora-compose itself            │
│     ├─ Validate: Self-generate documentation                │
│     └─ Stabilize: Tools + templates ready for release       │
│           ↓                                                  │
│  LAYER 2 (Platform: chora-platform)                          │
│     ├─ Integrate: Add chora-compose to platform tools       │
│     ├─ Version: Tag as chora-platform v0.7.0                │
│     ├─ Package: Build PyPI package (or separate)            │
│     ├─ Release: Publish to PyPI                             │
│     └─ Document: Update platform docs with Compose tools    │
│           ↓                                                  │
│  LAYER 3 (Capabilities: mcp-*, chora-*)                      │
│     ├─ Install: pip install chora-compose>=1.0.0            │
│     ├─ Use: Generate docs via MCP or CLI                    │
│     ├─ Customize: Add project-specific templates            │
│     └─ Release: Documentation included in capability release │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Example: Capability Repo Uses Chora-Compose**

1. **mcp-orchestration** needs API documentation
2. Install: `pip install chora-compose>=1.0.0`
3. Create config: `configs/mcp-api-docs.yaml`
4. Generate: `chora-compose assemble --config mcp-api-docs.yaml`
5. Output: `docs/api/reference.md` (auto-generated)
6. CI/CD: Regenerate on every commit (keep docs fresh)

---

## Part 4: DRSO Integration

Chora-Compose follows the **DRSO (Development → Release → Security → Operations)** lifecycle with 5 validation gates.

### 4.1 DRSO Lifecycle for Content Generation

```
┌──────────────────────────────────────────────────────────────┐
│           DRSO LIFECYCLE FOR CHORA-COMPOSE                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  DEVELOPMENT PHASE                                           │
│     ├─ Write: Templates + configs (Documentation-First)     │
│     ├─ Write: BDD features (4 tools, 20+ scenarios)         │
│     ├─ Write: TDD tests (pytest with Pydantic models)       │
│     ├─ Implement: 4 MCP tools + generation engine           │
│     └─ Gate 1: Status (tests exist for all features)        │
│           ↓                                                  │
│  RELEASE PHASE                                               │
│     ├─ Run: pytest with coverage                            │
│     ├─ Generate: Coverage report (target: 80%+)             │
│     └─ Gate 2: Coverage (≥80% coverage)                     │
│           ↓                                                  │
│  SECURITY PHASE                                              │
│     ├─ Run: bandit (Python security linter)                 │
│     ├─ Run: pip-audit (dependency vulnerabilities)          │
│     ├─ Generate: SBOM (CycloneDX format)                    │
│     └─ Gate 3: Security (0 critical/high issues)            │
│           ↓                                                  │
│  RELEASE PHASE (continued)                                   │
│     ├─ Generate: Release manifest (using own tools!)        │
│     ├─ Validate: star.yaml manifest schema                  │
│     └─ Gate 4: Release (valid artifacts)                    │
│           ↓                                                  │
│  OPERATIONS PHASE                                            │
│     ├─ Deploy: Publish to PyPI                              │
│     ├─ Monitor: Usage telemetry from MCP calls              │
│     ├─ Collect: Stakeholder feedback                        │
│     └─ Gate 5: Acknowledgement (value confirmed)            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Gate Requirements for Chora-Compose

#### Gate 1: Status (Development Phase)

**Requirements:**

- ✓ Tests exist for all 4 MCP tools (generate_content, assemble_artifact, list_generators, validate_content)
- ✓ Tests exist for template engine (Jinja2 rendering)
- ✓ Tests exist for Pydantic models (14 models)
- ✓ BDD features documented (20+ scenarios across 4 tools)

**Test Files:**

- `tests/mcp/test_generate_content.py`
- `tests/mcp/test_assemble_artifact.py`
- `tests/mcp/test_list_generators.py`
- `tests/mcp/test_validate_content.py`
- `tests/core/test_template_engine.py`
- `tests/types/test_pydantic_models.py`

**Gate 1 Output:** `.drso/gates/status/CR-compose-mcp-tools.json`

---

#### Gate 2: Coverage (Release Phase)

**Requirements:**

- ✓ Test coverage ≥ 80%
- ✓ All tests passing (0 failures)
- ✓ Coverage report generated (HTML + JSON)

**Current Status:** Working toward 80% (infrastructure in place)

**Gate 2 Output:** `.drso/gates/coverage/gate-2.json`

---

#### Gate 3: Security (Security Phase)

**Requirements:**

- ✓ 0 critical vulnerabilities (bandit + pip-audit)
- ✓ 0 high-severity issues
- ✓ Secrets externalized (ANTHROPIC_API_KEY in .env)
- ✓ SBOM generated (CycloneDX format)

**Security Considerations for Content Generation:**

- **LLM API Keys** - Must be externalized, never hardcoded
- **Template Injection** - Validate templates before rendering
- **Output Sanitization** - Prevent code injection in generated content
- **Rate Limiting** - Prevent abuse of LLM APIs

**Gate 3 Output:** `.drso/gates/security/gate-3.json`

---

#### Gate 4: Release (Release Phase)

**Requirements:**

- ✓ star.yaml manifest valid
- ✓ SBOM attached
- ✓ Coverage report attached
- ✓ Package buildable (`pip install .`)

**Virtuous Cycle (Self-Validation):**

Gate 4 uses **Chora-Compose's own tools** to generate release artifacts:

```bash
# Generate release manifest using Chora-Compose
chora-compose generate \
  --template release-manifest \
  --context .drso/gates/ \
  --output var/releases/chora-compose-v1.0.0-manifest.yaml
```

**Why This Matters:**

- If release manifest generation fails → Gate 4 fails
- Tool proven by actual usage (not just tests)
- Every release re-validates content generation works

**Gate 4 Output:** `.drso/gates/release/gate-4.json`

---

#### Gate 5: Acknowledgement (Operations Phase)

**Requirements:**

- ✓ Stakeholders confirm value delivered
- ✓ Downstream consumers notified (mcp-orchestration, etc.)
- ✓ No critical alerts in first 24 hours
- ✓ Telemetry shows usage (MCP tool calls)

**Stakeholder Approval Criteria:**

- All 4 MCP tools working as documented
- Templates generate correct output
- Validation rules catch quality issues
- Self-documentation cycle successful

**Gate 5 Output:** `.drso/gates/acknowledgement/gate-5-v1.0.0.json`

---

### 4.3 Documentation-Driven Design (ADR-0006)

Chora-Compose follows **Documentation-Driven Design**:

#### Diataxis → DRSO Gate Mapping

| Diataxis Quadrant | DRSO Phase | Chora-Compose Artifact |
|-------------------|------------|------------------------|
| **Explanation** | Development | `docs/explanation/why-content-generation.md` |
| **Reference** | Development | `docs/mcp/tool-reference.md` (2,053 lines) |
| **Reference** | Security | `docs/reference/security-model.md` |
| **How-to** | Release | `docs/how-to/create-template.md` |
| **Tutorial** | Operations | `docs/tutorials/first-artifact.md` |

#### Documentation-First Workflow

**BEFORE writing code:**

1. **Write Tool Reference** (Reference)
   - Define all 4 MCP tools with full specifications
   - Document parameters, return types, error codes
   - Provide usage examples for each tool
   - **Status:** ✅ Complete (docs/mcp/tool-reference.md)

2. **Write Pydantic Models** (Reference)
   - Define all 14 models with docstrings
   - Specify validation rules and constraints
   - Include examples for each model
   - **Status:** ✅ Complete (src/chora_compose/mcp/types.py)

3. **Write BDD Features** (from Reference)
   - Convert tool specs to BDD scenarios
   - 20+ scenarios across 4 tools
   - **Status:** 🚧 Next step (extract from docs)

**DURING implementation:**

4. **Implement Code** (Green phase)
   - Code satisfies documented tool contracts
   - Tests pass (extracted from documentation)

5. **Write How-to Guides** (How-to)
   - Template creation guide
   - Artifact assembly guide
   - MCP server deployment guide

**AFTER implementation:**

6. **Write Tutorials** (Tutorial)
   - First-time user onboarding
   - Value scenario walkthroughs
   - Template library tour

7. **Run DRSO Gates** (validate everything)

---

### 4.4 Self-Validation Virtuous Cycle

**Chora-Compose validates itself** by generating its own documentation:

```
┌──────────────────────────────────────────────────────────────┐
│          CHORA-COMPOSE VIRTUOUS CYCLE                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Feature: MCP Tool Documentation                          │
│     ↓                                                        │
│  2. Implement: generate_content + assemble_artifact          │
│     ↓                                                        │
│  3. Use: Generate docs/mcp/tool-reference.md                 │
│     ├─ Template: tool-reference.md.jinja                     │
│     ├─ Context: src/chora_compose/mcp/types.py               │
│     └─ Output: 2,053 lines of documentation                  │
│     ↓                                                        │
│  4. Gate 4: Uses own tools to create release manifest        │
│     ↓                                                        │
│  5. Validation: If docs generated → tools work               │
│     ↓                                                        │
│  6. Evidence: Documentation proves correctness               │
│     ↓                                                        │
│  7. Release: Tools proven by actual usage                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Benefits:**

- **Continuous Validation** - Every doc regeneration proves tools work
- **Real-World Testing** - Tools used in actual documentation workflow
- **Dogfooding** - Team experiences what users experience
- **Trust Building** - Ecosystem trusts tools proven by self-use

---

## Part 5: Integration Examples

### 5.1 Example 1: AI-Triggered Documentation Generation

**Scenario:** User asks Claude to generate API documentation from OpenAPI spec.

**Pattern:** C2 (Chora-Compose as MCP Server)

**Flow:**

1. **User:** "Generate API documentation from our OpenAPI spec."
2. **Claude:** Calls `generate_content` with:
   ```json
   {
     "generator_id": "api-reference-openapi",
     "context": {
       "openapi_spec_path": "openapi.yaml",
       "output_format": "markdown"
     }
   }
   ```
3. **Chora-Compose MCP Server:**
   - Loads template: `templates/api-reference-openapi.md.jinja`
   - Reads OpenAPI spec
   - Calls LLM to generate endpoint descriptions
   - Renders final markdown
4. **Claude:** "Here's your API documentation: [content]"

**Value:** AI agent autonomously generates documentation without human intervention.

---

### 5.2 Example 2: Event-Driven Documentation Updates

**Scenario:** Automatically update API docs when OpenAPI spec changes.

**Pattern:** C2 (MCP Server) + C4 (Artifact Pipeline)

**Flow:**

1. **Event:** GitHub push to `main` modifying `openapi.yaml`
2. **GitHub Webhook → n8n**
3. **n8n Workflow:**
   - Parse webhook payload
   - If `openapi.yaml` changed:
     - Call `chora-compose:assemble_artifact` via MCP
     - Config: `api-documentation-full`
     - Output: `docs/api/reference.md`
   - Commit updated docs to repo
   - Create PR with docs changes
   - Send Slack notification to #api-team
4. **Developer:** Reviews and merges docs PR

**Value:** Documentation stays in sync with code automatically.

---

### 5.3 Example 3: Multi-Source Artifact Assembly

**Scenario:** Generate monthly engineering report combining GitHub, Jira, and DataDog data.

**Pattern:** C3 (MCP Client) + C4 (Artifact Pipeline)

**Flow:**

1. **Trigger:** Monthly schedule (n8n cron)
2. **Chora-Compose Artifact Config:**
   ```yaml
   artifact_config_id: monthly-engineering-report
   sections:
     - id: commits
       generator: github-commits-summary
       mcp_tool: github:list_commits
       mcp_args:
         repo: chora-compose
         since: "30 days ago"
     - id: prs
       generator: github-prs-summary
       mcp_tool: github:list_pull_requests
       mcp_args:
         repo: chora-compose
         state: merged
         since: "30 days ago"
     - id: deployments
       generator: datadog-deployments-summary
       mcp_tool: datadog:query_events
       mcp_args:
         query: "deployment"
         timeframe: "30d"
   ```
3. **Chora-Compose:**
   - Calls `github:list_commits` → 47 commits
   - Calls `github:list_pull_requests` → 12 PRs
   - Calls `datadog:query_events` → 8 deployments
   - Generates summary for each section
   - Assembles final report
4. **Output:** `reports/2025-10-monthly-report.md` (Markdown)

**Value:** Automated multi-source reporting without manual data collection.

---

### 5.4 Example 4: Template-Based Content Standardization

**Scenario:** Enforce consistent API documentation across 10 microservices.

**Pattern:** C5 (Template Ecosystem)

**Setup:**

1. **Platform Team:** Creates base API template
   ```
   templates/base/api-reference-base.md.jinja
   ```
2. **Platform Team:** Publishes template to registry
3. **Each Microservice:**
   - Creates config referencing base template
   - Adds service-specific context
   - Generates docs using standard template

**Flow for Service A:**

```yaml
# Service A config
generator_id: service-a-api-docs
template: api-reference-base.md.jinja  # Reuses base
context:
  service_name: "Authentication Service"
  openapi_spec: "openapi.yaml"
  custom_sections:
    - id: authentication
      content: "OAuth2 + JWT tokens"
```

**Flow for Service B:**

```yaml
# Service B config (same template, different context)
generator_id: service-b-api-docs
template: api-reference-base.md.jinja  # Reuses base
context:
  service_name: "Payment Service"
  openapi_spec: "openapi.yaml"
  custom_sections:
    - id: payment-methods
      content: "Credit card, PayPal, crypto"
```

**Result:**

- All 10 services have consistent documentation structure
- Updates to base template propagate to all services
- Each service adds service-specific content

**Value:** Consistency across ecosystem with minimal maintenance.

---

## Part 6: Deployment Options

Chora-Compose can be deployed in multiple configurations based on scale, security, and operational requirements.

### 6.1 Local Development (CLI)

**Use Case:** Developers generating docs locally during development.

**Setup:**

```bash
# Install Chora-Compose
pip install chora-compose

# Set LLM API key
export ANTHROPIC_API_KEY=sk-ant-...

# Generate content
chora-compose generate \
  --template user-guide \
  --context feature.yaml \
  --output docs/user-guide.md
```

**MCP Integration:** None (CLI only)

**Pros:**

- ✅ Fast iteration
- ✅ No infrastructure required
- ✅ Immediate feedback

**Cons:**

- ❌ No AI agent access
- ❌ Manual execution only

---

### 6.2 MCP Server (STDIO)

**Use Case:** AI agents (Claude Desktop, Cursor) generating docs via MCP.

**Setup:**

**1. Install Chora-Compose:**

```bash
pip install chora-compose
```

**2. Configure Claude Desktop:**

```json
{
  "mcpServers": {
    "chora-compose": {
      "command": "chora-compose",
      "args": ["mcp", "server"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

**3. Restart Claude Desktop**

**4. Use MCP Tools:**

User: "Generate API documentation from openapi.yaml"

Claude: Calls `chora-compose:generate_content` via MCP

**MCP Integration:** Full (STDIO transport)

**Pros:**

- ✅ AI agent access
- ✅ No infrastructure (local execution)
- ✅ Secure (no network exposure)

**Cons:**

- ❌ Single-user (no sharing)
- ❌ No web UI
- ❌ Limited to local files

---

### 6.3 MCP Server (HTTP)

**Use Case:** Remote AI agents or web applications accessing Chora-Compose.

**Setup:**

**1. Run MCP Server:**

```bash
# Start HTTP MCP server
chora-compose mcp server --http --port 8080

# Or with Docker
docker run -p 8080:8080 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  chora-compose:latest mcp server --http
```

**2. Configure Remote Client:**

```json
{
  "mcpServers": {
    "chora-compose-remote": {
      "transport": "http",
      "url": "http://chora-compose.example.com:8080"
    }
  }
}
```

**MCP Integration:** Full (HTTP/SSE transport)

**Pros:**

- ✅ Multi-user access
- ✅ Remote execution
- ✅ Scalable (load balanced)

**Cons:**

- ❌ Requires server infrastructure
- ❌ Security considerations (authentication)
- ❌ Network latency

---

### 6.4 Docker Containerized

**Use Case:** Isolated execution, reproducible environments.

**Dockerfile:**

```dockerfile
FROM python:3.12-slim

# Install Chora-Compose
RUN pip install chora-compose

# Copy templates and configs
COPY templates/ /app/templates/
COPY configs/ /app/configs/

# Set working directory
WORKDIR /app

# Expose MCP server port
EXPOSE 8080

# Run MCP server
CMD ["chora-compose", "mcp", "server", "--http", "--port", "8080"]
```

**Docker Compose:**

```yaml
services:
  chora-compose:
    image: chora-compose:latest
    ports:
      - "8080:8080"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./templates:/app/templates
      - ./configs:/app/configs
      - ./output:/app/output
```

**Pros:**

- ✅ Isolated environment
- ✅ Reproducible builds
- ✅ Easy deployment

**Cons:**

- ❌ Container overhead
- ❌ Requires Docker knowledge

---

### 6.5 Serverless Functions

**Use Case:** On-demand execution, zero idle cost.

**AWS Lambda Example:**

```python
# lambda_handler.py
import json
from chora_compose import generate_content

def lambda_handler(event, context):
    """AWS Lambda handler for Chora-Compose"""

    # Parse request
    body = json.loads(event['body'])

    # Generate content
    result = generate_content(
        generator_id=body['generator_id'],
        context=body['context']
    )

    # Return response
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

**Deployment:**

```bash
# Package function
zip lambda.zip lambda_handler.py

# Upload to AWS Lambda
aws lambda create-function \
  --function-name chora-compose-generate \
  --runtime python3.12 \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda.zip
```

**Pros:**

- ✅ Zero idle cost
- ✅ Auto-scaling
- ✅ Serverless simplicity

**Cons:**

- ❌ Cold start latency
- ❌ Vendor lock-in
- ❌ Complexity for state management

---

## Part 7: MCP Tool Deep Dive

Chora-Compose exposes **4 MCP tools** for content generation. This section provides conceptual specifications (full details in [docs/mcp/tool-reference.md](../mcp/tool-reference.md)).

### 7.1 Tool: generate_content

**Purpose:** Generate content from a template and context using LLM.

**Tool Schema:**

```json
{
  "name": "generate_content",
  "description": "Generate content from a template and context using LLM",
  "inputSchema": {
    "type": "object",
    "properties": {
      "generator_id": {
        "type": "string",
        "description": "Unique identifier for the generator"
      },
      "context": {
        "type": "object",
        "description": "Context data for template rendering",
        "additionalProperties": true
      },
      "output_format": {
        "type": "string",
        "enum": ["markdown", "html", "json"],
        "default": "markdown"
      }
    },
    "required": ["generator_id"]
  }
}
```

**Return Type:**

```json
{
  "content": "Generated markdown content...",
  "metadata": {
    "generator_id": "api-reference-openapi",
    "tokens_used": 1234,
    "generation_time_ms": 2500
  }
}
```

**Example Usage:**

```python
# Via Python API
from chora_compose.mcp import generate_content

result = generate_content(
    generator_id="user-guide-feature",
    context={
        "feature_name": "Authentication",
        "description": "OAuth2 + JWT tokens"
    }
)

print(result.content)  # Generated markdown
```

**Error Codes:**

- `GENERATOR_NOT_FOUND` - Generator ID doesn't exist in registry
- `TEMPLATE_NOT_FOUND` - Template file missing
- `CONTEXT_INVALID` - Context missing required fields
- `LLM_ERROR` - LLM API call failed
- `RENDERING_ERROR` - Template rendering failed

---

### 7.2 Tool: assemble_artifact

**Purpose:** Assemble multi-section artifact from config and context.

**Tool Schema:**

```json
{
  "name": "assemble_artifact",
  "description": "Assemble multi-section artifact from config",
  "inputSchema": {
    "type": "object",
    "properties": {
      "artifact_config_id": {
        "type": "string",
        "description": "Unique identifier for artifact config"
      },
      "context": {
        "type": "object",
        "description": "Global context available to all sections",
        "additionalProperties": true
      },
      "output_path": {
        "type": "string",
        "description": "Optional output file path"
      }
    },
    "required": ["artifact_config_id"]
  }
}
```

**Return Type:**

```json
{
  "content": "# Multi-section artifact...",
  "metadata": {
    "artifact_config_id": "monthly-report",
    "sections_count": 5,
    "total_tokens": 3456,
    "generation_time_ms": 12000
  },
  "sections": [
    {
      "section_id": "overview",
      "generator_id": "report-overview",
      "tokens_used": 500
    }
  ]
}
```

**Example Usage:**

```python
from chora_compose.mcp import assemble_artifact

result = assemble_artifact(
    artifact_config_id="api-documentation-full",
    context={
        "project_name": "Chora-Compose",
        "version": "1.0.0"
    },
    output_path="docs/api/reference.md"
)

print(f"Generated {result.metadata.sections_count} sections")
```

---

### 7.3 Tool: list_generators

**Purpose:** Query available generators and validators from registry.

**Tool Schema:**

```json
{
  "name": "list_generators",
  "description": "List available generators and validators",
  "inputSchema": {
    "type": "object",
    "properties": {
      "category": {
        "type": "string",
        "enum": ["all", "generators", "validators"],
        "default": "all"
      },
      "search": {
        "type": "string",
        "description": "Optional search query"
      }
    }
  }
}
```

**Return Type:**

```json
{
  "generators": [
    {
      "generator_id": "api-reference-openapi",
      "description": "Generate API docs from OpenAPI spec",
      "template_path": "templates/api-reference-openapi.md.jinja",
      "required_context": ["openapi_spec_path"]
    }
  ],
  "validators": [
    {
      "validator_id": "proper-headings",
      "description": "Check heading hierarchy",
      "rule_type": "structural"
    }
  ]
}
```

**Example Usage:**

```python
from chora_compose.mcp import list_generators

result = list_generators(
    category="generators",
    search="api"
)

for gen in result.generators:
    print(f"{gen.generator_id}: {gen.description}")
```

---

### 7.4 Tool: validate_content

**Purpose:** Validate generated content against quality rules.

**Tool Schema:**

```json
{
  "name": "validate_content",
  "description": "Validate content against rules",
  "inputSchema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Content to validate (Markdown)"
      },
      "rules": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Rule IDs to check"
      }
    },
    "required": ["content"]
  }
}
```

**Return Type:**

```json
{
  "valid": false,
  "results": [
    {
      "rule_id": "proper-headings",
      "passed": true,
      "message": "Heading hierarchy is correct"
    },
    {
      "rule_id": "no-broken-links",
      "passed": false,
      "message": "Found 2 broken links",
      "details": [
        {
          "line": 45,
          "link": "/missing-page.md",
          "error": "File not found"
        }
      ]
    }
  ]
}
```

**Example Usage:**

```python
from chora_compose.mcp import validate_content

result = validate_content(
    content=generated_markdown,
    rules=["proper-headings", "no-broken-links"]
)

if not result.valid:
    print("Validation failed:")
    for r in result.results:
        if not r.passed:
            print(f"  {r.rule_id}: {r.message}")
```

---

### 7.5 Config Lifecycle Tools (v1.1.0)

**Purpose:** Enable conversational, iterative config development without manual file editing.

The config lifecycle tools implement **Pattern C7 (Conversational Config Development)**, allowing AI agents and users to create, test, refine, and save configuration files through conversation.

#### Tool: draft_config

**Purpose:** Create ephemeral draft config for experimentation.

**Tool Schema:**

```json
{
  "name": "draft_config",
  "description": "Create ephemeral draft configuration",
  "inputSchema": {
    "type": "object",
    "properties": {
      "config_type": {
        "type": "string",
        "enum": ["content", "artifact"],
        "description": "Type of configuration to draft"
      },
      "config_data": {
        "type": "object",
        "description": "Configuration JSON (validated against schema)",
        "additionalProperties": true
      }
    },
    "required": ["config_type", "config_data"]
  }
}
```

**Return Type:**

```json
{
  "draft_id": "draft_abc123def456",
  "config_type": "content",
  "created_at": "2025-10-16T14:30:00Z",
  "storage_path": "ephemeral/drafts/content/draft_abc123def456.json",
  "validation_status": "valid",
  "expires_at": "2025-11-15T14:30:00Z"
}
```

**Example Usage:**

```python
from chora_compose.mcp import draft_config

result = draft_config(
    config_type="content",
    config_data={
        "id": "weekly-report",
        "generation": {
            "patterns": [{
                "type": "jinja2",
                "template": "report.md.jinja"
            }]
        }
    }
)

print(f"Draft created: {result.draft_id}")
print(f"Expires: {result.expires_at}")
```

**Error Codes:**
- `SCHEMA_VALIDATION_ERROR` - Config violates JSON Schema
- `STORAGE_ERROR` - Failed to write draft to ephemeral storage

---

#### Tool: test_config

**Purpose:** Preview generation output from draft config without side effects.

**Tool Schema:**

```json
{
  "name": "test_config",
  "description": "Test draft config and preview output",
  "inputSchema": {
    "type": "object",
    "properties": {
      "draft_id": {
        "type": "string",
        "description": "Draft ID from draft_config"
      },
      "context": {
        "type": "object",
        "description": "Optional context for generation preview",
        "additionalProperties": true
      }
    },
    "required": ["draft_id"]
  }
}
```

**Return Type:**

```json
{
  "draft_id": "draft_abc123def456",
  "preview": "# Weekly Report\n\nGenerated content preview...",
  "preview_length": 1234,
  "generation_successful": true,
  "warnings": [],
  "metadata": {
    "generator_type": "jinja2",
    "template_used": "report.md.jinja",
    "generation_time_ms": 150
  }
}
```

**Example Usage:**

```python
from chora_compose.mcp import test_config

result = test_config(
    draft_id="draft_abc123def456",
    context={"week": "2025-W42", "team": "Engineering"}
)

print("Preview:")
print(result.preview[:200])  # First 200 chars
```

---

#### Tool: modify_config

**Purpose:** Update specific fields in draft config.

**Tool Schema:**

```json
{
  "name": "modify_config",
  "description": "Modify existing draft configuration",
  "inputSchema": {
    "type": "object",
    "properties": {
      "draft_id": {
        "type": "string",
        "description": "Draft ID to modify"
      },
      "updates": {
        "type": "object",
        "description": "Fields to update (JSON path notation)",
        "additionalProperties": true
      }
    },
    "required": ["draft_id", "updates"]
  }
}
```

**Return Type:**

```json
{
  "draft_id": "draft_abc123def456",
  "updated_at": "2025-10-16T14:35:00Z",
  "fields_modified": 2,
  "validation_status": "valid",
  "preview_invalidated": true
}
```

**Example Usage:**

```python
from chora_compose.mcp import modify_config

result = modify_config(
    draft_id="draft_abc123def456",
    updates={
        "generation.patterns[0].template": "detailed-report.md.jinja",
        "id": "weekly-detailed-report"
    }
)

print(f"Modified {result.fields_modified} fields")
```

---

#### Tool: save_config

**Purpose:** Persist validated draft to filesystem.

**Tool Schema:**

```json
{
  "name": "save_config",
  "description": "Save draft config to filesystem",
  "inputSchema": {
    "type": "object",
    "properties": {
      "draft_id": {
        "type": "string",
        "description": "Draft ID to save"
      },
      "destination_path": {
        "type": "string",
        "description": "Optional filesystem path (defaults to configs/{type}/{id}.json)"
      }
    },
    "required": ["draft_id"]
  }
}
```

**Return Type:**

```json
{
  "draft_id": "draft_abc123def456",
  "saved_path": "configs/content/weekly-report.json",
  "config_id": "weekly-report",
  "config_type": "content",
  "saved_at": "2025-10-16T14:40:00Z",
  "draft_retained": false
}
```

**Example Usage:**

```python
from chora_compose.mcp import save_config

result = save_config(
    draft_id="draft_abc123def456",
    destination_path="configs/content/my-reports/weekly.json"
)

print(f"Saved to: {result.saved_path}")
print(f"Use config ID: {result.config_id}")
```

**Error Codes:**
- `DRAFT_NOT_FOUND` - Draft ID doesn't exist or expired
- `VALIDATION_ERROR` - Draft failed final validation
- `FILE_EXISTS` - Destination path already exists (won't overwrite)
- `PERMISSION_ERROR` - Cannot write to destination path

---

### 7.6 Execution Models

#### Synchronous Execution

**Use Case:** Fast templates (<5 seconds), immediate results needed

**Flow:**

1. Client calls MCP tool
2. MCP server blocks until generation complete
3. Returns result directly

**Suitable For:**

- Short templates (<1000 words)
- Simple generation (no MCP client calls)
- Interactive AI agent sessions

---

#### Asynchronous Execution

**Use Case:** Long templates (>5 seconds), multi-section artifacts

**Flow:**

1. Client calls MCP tool with `async: true`
2. MCP server returns `execution_id` immediately
3. Client polls `get_execution_status` for result
4. Result available when `status: "completed"`

**Suitable For:**

- Multi-section artifacts (5+ sections)
- Complex generation (MCP client calls)
- Batch processing

---

#### Streaming Execution (Future)

**Use Case:** Real-time progress updates, large artifacts

**Flow:**

1. Client subscribes to MCP resource `/execution/{id}/progress`
2. Server streams progress events:
   - `section_started`
   - `section_completed`
   - `artifact_completed`

**Suitable For:**

- User-facing applications (show progress bar)
- Debugging long-running generations
- Real-time monitoring

---

### 7.6 Error Handling

**Error Response Format:**

```json
{
  "error": {
    "code": "TEMPLATE_NOT_FOUND",
    "message": "Template 'invalid-template.md.jinja' not found",
    "details": {
      "generator_id": "invalid-generator",
      "template_path": "templates/invalid-template.md.jinja",
      "searched_paths": [
        "/app/templates",
        "/app/custom-templates"
      ]
    },
    "retry_allowed": false
  }
}
```

**Error Codes:**

| Code | Description | Retryable |
|------|-------------|-----------|
| `GENERATOR_NOT_FOUND` | Generator ID not in registry | No |
| `TEMPLATE_NOT_FOUND` | Template file missing | No |
| `CONTEXT_INVALID` | Missing required context fields | No |
| `LLM_ERROR` | LLM API call failed | Yes |
| `RENDERING_ERROR` | Jinja2 rendering failed | No |
| `VALIDATION_ERROR` | Content validation failed | No |
| `MCP_CLIENT_ERROR` | MCP tool call failed | Yes |
| `TIMEOUT` | Generation exceeded time limit | Yes |

**Retry Strategy:**

- Retryable errors (LLM_ERROR, MCP_CLIENT_ERROR): Exponential backoff
- Non-retryable errors: Fail immediately with detailed context

---

## Part 8: Telemetry & Observability

Chora-Compose integrates with platform telemetry to track usage, quality, and performance.

### 8.1 Metrics

**Generation Metrics:**

- `chora_compose_generations_total{generator_id, status}` - Counter
- `chora_compose_generation_duration_seconds{generator_id}` - Histogram
- `chora_compose_generation_tokens{generator_id, type}` - Counter (input/output tokens)
- `chora_compose_generation_errors_total{generator_id, error_code}` - Counter

**Validation Metrics:**

- `chora_compose_validations_total{rule_id, status}` - Counter
- `chora_compose_validation_failures_total{rule_id}` - Counter

**MCP Metrics:**

- `chora_compose_mcp_calls_total{tool, status}` - Counter
- `chora_compose_mcp_call_duration_seconds{tool}` - Histogram

**Template Metrics:**

- `chora_compose_template_renders_total{template, status}` - Counter
- `chora_compose_template_cache_hits_total{template}` - Counter (if caching enabled)

---

### 8.2 Logs

**Structured Logging Format:**

```json
{
  "timestamp": "2025-10-15T10:30:00Z",
  "level": "info",
  "service": "chora-compose",
  "event_type": "generation_started",
  "generator_id": "api-reference-openapi",
  "template_path": "templates/api-reference-openapi.md.jinja",
  "context_keys": ["openapi_spec_path", "output_format"],
  "trace_id": "abc123"
}
```

**Log Levels:**

- **DEBUG** - Template rendering details, LLM prompts
- **INFO** - Generation start/complete, validation results
- **WARN** - Validation warnings, deprecated template usage
- **ERROR** - Generation failures, LLM errors

---

### 8.3 Traces

**OpenTelemetry Integration:**

```
Trace: generate_content (2.5s)
  ├─ Span: load_generator (50ms)
  ├─ Span: load_template (30ms)
  ├─ Span: render_template (100ms)
  ├─ Span: call_llm (2.2s)
  │   └─ Span: llm_api_request (2.15s)
  └─ Span: post_process (120ms)
```

**Trace Context Propagation:**

- MCP calls include `trace_id` and `span_id`
- Downstream MCP tools (if supporting OpenTelemetry) continue trace
- End-to-end visibility: AI agent → MCP → Chora-Compose → LLM

---

### 8.4 Dashboards

**Grafana Dashboard: "Chora-Compose Generation"**

- Generation success rate (last 24h)
- Top 10 most-used generators
- Average generation time by template
- LLM token usage over time
- Error rate by error code

**Grafana Dashboard: "Chora-Compose Validation"**

- Validation pass rate by rule
- Top validation failures
- Content quality trends

---

## Part 9: Value Scenarios

### 9.1 Scenario: Accelerated Documentation Workflows

**Problem:** Manual documentation takes 4-8 hours per feature.

**Without Chora-Compose:**

- Developer writes API docs by hand
- Manually formats endpoints, parameters, examples
- Manually updates TOC, cross-references
- Time: 4-8 hours

**With Chora-Compose:**

- Developer creates generator config
- Runs `chora-compose generate`
- Reviews and tweaks generated content
- Time: 30-60 minutes

**Value:** **80-90% time reduction** for documentation tasks.

---

### 9.2 Scenario: Content Quality Improvement

**Problem:** Inconsistent documentation quality across projects.

**Without Chora-Compose:**

- Each developer writes docs in their own style
- Varying levels of detail and completeness
- No automated quality checks
- Inconsistent structure

**With Chora-Compose:**

- Shared templates enforce consistent structure
- Validation rules catch common issues
- All docs follow Diataxis framework
- Automated completeness checks

**Value:** **Consistent quality** across ecosystem with **reduced review time**.

---

### 9.3 Scenario: Multi-Source Data Aggregation

**Problem:** Manual data collection from multiple systems for reports.

**Without Chora-Compose:**

- Developer manually queries GitHub API
- Developer manually queries Jira API
- Developer manually queries DataDog API
- Developer manually formats data into report
- Time: 2-3 hours

**With Chora-Compose + MCP Client:**

- Create artifact config with MCP tool calls
- Run `chora-compose assemble`
- Automated data fetching and formatting
- Time: 10-15 minutes

**Value:** **~10x faster** for multi-source reporting.

---

### 9.4 Scenario: Template Reuse Across Projects

**Problem:** Duplication of documentation effort across microservices.

**Without Chora-Compose:**

- 10 microservices, each with custom docs
- Inconsistent structure and content
- Updates require changing 10 repos manually
- High maintenance burden

**With Chora-Compose + Template Ecosystem:**

- Single base template for all microservices
- Each service uses same template with service-specific context
- Updates to template propagate to all services
- Low maintenance burden

**Value:** **~5x reduction** in template maintenance effort.

---

## Part 10: Risks & Mitigations

### 10.1 Risk: LLM Dependency and Costs

**Description:** Chora-Compose relies on LLM APIs (Claude, GPT), which have costs and availability risks.

**Mitigations:**

- ✅ Support multiple LLM providers (Claude, GPT, local models)
- ✅ Caching of LLM responses (reduce redundant calls)
- ✅ Template-only mode (generate without LLM for simple cases)
- ✅ Token usage tracking and budget alerts
- ✅ Fallback to simpler models for non-critical content

**Fallback:** Can generate documentation using templates alone (without LLM enhancement) for cost-sensitive scenarios.

---

### 10.2 Risk: Content Quality Variance

**Description:** LLM-generated content may vary in quality, accuracy, and tone.

**Mitigations:**

- ✅ Validation rules catch common quality issues
- ✅ Example-driven prompts (provide high-quality examples)
- ✅ Human review workflow (generated content reviewed before publication)
- ✅ Template constraints (limit LLM freedom via structured templates)
- ✅ Feedback loop (track quality issues, refine prompts)

**Tooling:** `validate_content` tool flags quality issues before publication.

---

### 10.3 Risk: Template Maintenance Burden

**Description:** Large template library becomes difficult to maintain and evolve.

**Mitigations:**

- ✅ Template inheritance (reuse base templates)
- ✅ Template versioning (semantic versions, compatibility tracking)
- ✅ Template testing (example data → expected output)
- ✅ Template documentation (usage guides, parameter descriptions)
- ✅ Governance (curated template library, approval process)

**Governance:** Platform team maintains curated base templates; projects contribute domain-specific templates.

---

### 10.4 Risk: Security Vulnerabilities (Template Injection)

**Description:** Malicious templates could execute arbitrary code during rendering.

**Mitigations:**

- ✅ Jinja2 sandboxing (restrict dangerous operations)
- ✅ Template validation (static analysis before rendering)
- ✅ Input sanitization (escape user-provided context)
- ✅ Template source verification (signed templates)
- ✅ Security scanning (bandit, pip-audit in Gate 3)

**Compliance:** Follow security baseline from ecosystem intent (Gate 3 requirements).

---

### 10.5 Risk: Documentation Drift

**Description:** Generated docs fall out of sync with code over time.

**Mitigations:**

- ✅ CI/CD integration (regenerate docs on code changes)
- ✅ Git hooks (warn if code changed but docs didn't)
- ✅ Staleness detection (flag docs not updated in N days)
- ✅ Automated validation (check docs match current API schema)
- ✅ Event-driven regeneration (GitHub webhooks → n8n → Chora-Compose)

**Best Practice:** Regenerate docs on every commit to keep them fresh.

---

## Part 11: Release Roadmap

### Phase 1: Foundation (Q1 2025) ✅ COMPLETE

**Goal:** Establish core content generation and MCP server capabilities.

**Deliverables:**

- ✅ 17 MCP tools implemented (v1.1.0)
  - v1.0.0: 13 core tools (generate_content, assemble_artifact, list_generators, validate_content, regenerate_content, preview_generation, batch_generate, list_content_configs, list_artifacts, cleanup_ephemeral, delete_content, trace_dependencies, list_artifact_configs)
  - v1.1.0: 4 config lifecycle tools (draft_config, test_config, modify_config, save_config)
- ✅ 5 MCP resources (v1.1.0)
  - capabilities://server, capabilities://tools, capabilities://resources, capabilities://generators
  - Legacy: config://, schema://, content://, generator://
- ✅ Type-safe Pydantic models (comprehensive type system)
- ✅ Template engine (Jinja2 with sandboxing)
- ✅ MCP server (STDIO transport)
- ✅ CLI commands (generate, assemble, list, validate)
- ✅ Documentation (tool reference, E2E test suites)
- ✅ Config lifecycle infrastructure (EphemeralConfigManager, 30-day retention)

**Success Criteria:**

- ✅ AI agents can generate content via MCP
- ✅ Templates render correctly with context
- ✅ Validation rules catch quality issues
- ✅ Self-documentation cycle successful
- ✅ Conversational workflow authoring enabled (v1.1.0)
- ✅ Dynamic capability discovery (v1.1.0)

**Status:** ✅ **COMPLETE** (v1.1.0 released 2025-10-16)

---

### Phase 2: Template Ecosystem (Q2 2025)

**Goal:** Build reusable template library and enable template sharing.

**Deliverables:**

- ✅ Template registry (catalog of available templates)
- ✅ Base templates (API docs, user guides, reports)
- ✅ Template inheritance (Jinja2 extends/includes)
- ✅ Template versioning (semantic versions)
- ✅ Template testing framework (example data → expected output)
- ✅ Template documentation (usage guides)

**Success Criteria:**

- ≥10 base templates available
- ≥3 projects using shared templates
- Template updates propagate to consumers
- Zero breaking changes without migration guide

**Risks:**

- Template sprawl (ungoverned growth)
- Breaking changes in base templates

---

### Phase 3: Advanced Patterns (Q3 2025)

**Goal:** Implement MCP client, artifact pipelines, advanced validation.

**Deliverables:**

- ✅ MCP client (consume other MCP tools)
- ✅ Artifact pipelines (multi-stage generation)
- ✅ Dependency resolution (topological sort of sections)
- ✅ Post-processing plugins (validators, converters)
- ✅ Async execution (long-running generations)
- ✅ HTTP transport (remote MCP server)

**Success Criteria:**

- Multi-source artifacts (≥3 MCP tools per artifact)
- Pipelines with ≥5 sections execute successfully
- Async execution handles ≥30 second generations
- HTTP server supports ≥10 concurrent clients

**Risks:**

- MCP client complexity (protocol compatibility)
- Pipeline debugging difficulty

---

### Phase 4: Platform-Wide Adoption (Q4 2025)

**Goal:** Integrate with ecosystem, achieve production stability.

**Deliverables:**

- ✅ Integration with chora-platform (PyPI package)
- ✅ BDD-DRSO validation (all 5 gates passing)
- ✅ Ecosystem adoption (≥5 capability repos using Chora-Compose)
- ✅ Telemetry integration (OpenTelemetry export)
- ✅ Production monitoring (Grafana dashboards)

**Success Criteria:**

- ≥5 production workflows using Chora-Compose
- <1% generation failure rate
- Sub-5-second p95 latency for simple templates
- ≥80% test coverage (Gate 2 passing)

**Risks:**

- Ecosystem adoption resistance
- Performance issues at scale

---

## Part 12: Success Criteria

### 12.1 Technical Success Criteria

**Generation:**

- ✅ All 17 MCP tools working as documented (v1.1.0)
  - 13 core generation/management tools (v1.0.x)
  - 4 config lifecycle tools (v1.1.0)
- ✅ Templates render correctly with valid context
- ✅ Validation rules catch ≥90% of quality issues
- ✅ End-to-end latency: p95 < 5s for simple templates
- ✅ Uptime: ≥99.5% for MCP server

**Config Lifecycle (v1.1.0):**

- ✅ Draft configs validate against JSON Schema
- ✅ test_config previews match final generation
- ✅ save_config atomic operations (no partial writes)
- ✅ 30-day draft retention enforced
- ✅ <2s round-trip for draft → test → modify cycle

**Capability Discovery (v1.1.0):**

- ✅ 5 capability resources expose server metadata
- ✅ Plugin generators automatically discovered
- ✅ Dynamic tool/resource introspection
- ✅ <50ms response time for capability queries

**Quality:**

- ✅ ≥80% test coverage (Gate 2 requirement)
- ✅ ≥95% generation success rate
- ✅ 0 critical/high security vulnerabilities (Gate 3)
- ✅ All Pydantic models validated with examples

**Integration:**

- ✅ MCP tools callable from Claude Desktop, Cursor
- ✅ Works with n8n workflows (Pattern N3 MCP client, N7 conversational authoring)
- ✅ Integrates with CI/CD (GitHub Actions, GitLab CI)

---

### 12.2 Business Success Criteria

**Adoption:**

- ✅ ≥5 capability repos using Chora-Compose
- ✅ ≥3 teams actively generating documentation
- ✅ ≥10 templates in shared library

**Efficiency:**

- ✅ Documentation time reduced by ≥80%
- ✅ Content quality variance reduced by ≥50%
- ✅ Template maintenance burden reduced by ≥70%

**Value:**

- ✅ ≥10 business processes automated via Chora-Compose
- ✅ ROI positive within 6 months (time saved > LLM costs)

---

### 12.3 User Experience Success Criteria

**Developer Experience:**

- ✅ Template creation time: <1 hour for simple template
- ✅ Generation time: <30 seconds for typical content
- ✅ Debugging: root cause identified within 10 minutes
- ✅ Documentation: ≥90% developers rate as "helpful"

**AI Agent Experience:**

- ✅ MCP tool calls succeed ≥95% of the time
- ✅ Error messages provide actionable guidance
- ✅ Async generations return status within 5 seconds

**Stakeholder Experience:**

- ✅ Generated content meets quality standards ≥90% of time
- ✅ Documentation stays in sync with code (≤1 week lag)
- ✅ Consistent structure across projects

---

## Part 13: Conclusion

This document defines the **solution-neutral intent** for **Chora-Compose** as a modular content generation and artifact assembly capability within the Chora ecosystem.

### Key Takeaways:

1. **Seven Integration Patterns** - From CLI tool to MCP server to conversational config authoring (v1.1.0)
2. **DRSO Alignment** - Follows full 5-gate validation lifecycle
3. **3-Layer Architecture** - Functions as Platform-layer capability
4. **MCP-Native** - 17 MCP tools + 5 resources for comprehensive AI agent integration (v1.1.0)
5. **Conversational Workflow Authoring** - Draft/test/modify/save cycle eliminates IDE context switching (v1.1.0)
6. **Dynamic Capability Discovery** - Agents self-configure via capabilities:// resources (v1.1.0)
7. **Self-Validation** - Uses own tools to generate documentation (virtuous cycle)
8. **Template Ecosystem** - Reusable Jinja2 templates with composability

### Strategic Value:

Chora-Compose addresses a critical gap in the ecosystem: **automated, AI-powered documentation generation with conversational workflow authoring**. By providing:

- **17 MCP Tools** - Comprehensive content generation and config lifecycle management (v1.1.0)
  - 13 core tools for generation, validation, storage management
  - 4 config lifecycle tools for draft/test/modify/save workflows
- **5 MCP Resources** - Dynamic capability discovery for agent self-configuration (v1.1.0)
- **Template Library** - Reusable templates ensure consistency
- **Validation Layer** - Quality enforcement without manual review
- **Multi-Source Aggregation** - Combine data from multiple systems
- **DRSO Integration** - Documentation-first workflow aligns with gates
- **Zero-Friction Config Creation** - Conversational iteration without file editing (v1.1.0)

### Next Steps:

1. **Phase 2: Template Ecosystem** - Build reusable template library
2. **Phase 3: Advanced Patterns** - MCP client, artifact pipelines
3. **Phase 4: Ecosystem Adoption** - Integration with ≥5 capability repos
4. **Continuous Improvement** - Refine based on telemetry and feedback

### Open Questions:

1. **Template Governance:** Who approves new templates in shared library?
2. **LLM Costs:** What budget limits for production usage?
3. **Quality Thresholds:** What validation pass rate is acceptable?
4. **Adoption Timeline:** Does 4-phase roadmap align with ecosystem needs?

---

## Appendix A: Glossary of Terms

**Artifact** - Multi-section document assembled from multiple generators (e.g., API documentation with 5 sections).

**Artifact Config** - YAML configuration defining sections, dependencies, and post-processing for an artifact.

**Context** - Data provided to templates for rendering (e.g., OpenAPI spec, feature descriptions).

**Generator** - Configuration defining a template, required context, and output format for content generation.

**Generator ID** - Unique identifier for a generator (e.g., `api-reference-openapi`).

**Jinja2** - Template engine used by Chora-Compose for content generation.

**MCP (Model Context Protocol)** - Standard protocol for AI agent-to-service communication.

**MCP Client** - Chora-Compose consuming other MCP tools (e.g., GitHub MCP, Coda MCP).

**MCP Server** - Chora-Compose exposing 4 tools to AI agents.

**Pydantic** - Python library for data validation using type annotations.

**Template** - Jinja2 template file (e.g., `api-reference.md.jinja`) used for content generation.

**Template Inheritance** - Jinja2 feature allowing templates to extend/include other templates.

**Validation Rule** - Quality check applied to generated content (e.g., proper heading hierarchy).

**Virtuous Cycle** - Self-reinforcing pattern where tools validate themselves through actual usage.

---

## Appendix B: Relationship to Ecosystem Documents

This document complements and references the following ecosystem documents:

### Ecosystem Intent (v2.0.0)

**What it covers:**
- Ecosystem-wide architecture (discovery, manifests, change signals)
- Governance processes (RACI, SLAs, appeals)
- Security baseline (SBOM, vulnerabilities, secrets)
- Observability requirements (telemetry, metrics, traces)

**How Chora-Compose aligns:**
- Publishes `star.yaml` manifest for discovery
- Follows change signal workflow for breaking changes
- Meets security baseline (Gate 3 requirements)
- Emits telemetry events (generation, validation)

### DRSO Intent (v1.0.0)

**What it covers:**
- DRSO 4-phase lifecycle (Development → Release → Security → Operations)
- 5 validation gates (Status, Coverage, Security, Release, Acknowledgement)
- Documentation-Driven Design (Diataxis framework)
- Virtuous cycles (self-validation patterns)

**How Chora-Compose aligns:**
- Follows full DRSO lifecycle (all 5 gates)
- Documentation-first workflow (tool-reference.md written before code)
- Self-validates via virtuous cycle (generates own docs)
- BDD-aligned Features (20+ scenarios across 4 tools)

### n8n Intent (v1.0.0)

**What it covers:**
- n8n integration patterns (workflow orchestration)
- MCP server/client patterns
- Event-driven automation
- Deployment models

**How Chora-Compose complements:**
- Can be invoked FROM n8n workflows (Pattern N3 MCP client)
- Provides content generation tools for n8n-orchestrated workflows
- Enables event-driven documentation (GitHub webhook → n8n → Chora-Compose)

---

## Appendix C: References

### Related Documents

- **Ecosystem Intent:** [docs/ecosystem/ecosystem-intent.md](ecosystem-intent.md)
- **DRSO Intent:** [docs/ecosystem/drso-integrated-intent.md](drso-integrated-intent.md)
- **n8n Intent:** [docs/ecosystem/n8n-solution-neutral-intent.md](n8n-solution-neutral-intent.md)
- **Tool Reference:** [docs/mcp/tool-reference.md](../mcp/tool-reference.md)
- **Type Definitions:** [src/chora_compose/mcp/types.py](../../src/chora_compose/mcp/types.py)
- **ADR-0008:** [Modularization Boundaries](../reference/architecture/ADR-0008-modularization-boundaries.md)

### External Standards

- **Jinja2:** https://jinja.palletsprojects.com/
- **Pydantic:** https://docs.pydantic.dev/
- **MCP Specification:** https://modelcontextprotocol.io/
- **OpenTelemetry:** https://opentelemetry.io/
- **CycloneDX SBOM:** https://cyclonedx.org/
- **Diataxis Framework:** https://diataxis.fr/

### Example Implementations

- **MCP Tools:** [src/chora_compose/mcp/tools.py](../../src/chora_compose/mcp/tools.py)
- **Pydantic Models:** [src/chora_compose/mcp/types.py](../../src/chora_compose/mcp/types.py)
- **Templates:** [templates/](../../templates/)
- **Configs:** [configs/](../../configs/)

---

**END OF DOCUMENT**

**Document ID:** COMPOSE-INT-2025-10-15
**Version:** 1.0.0
**Status:** Draft
**Last Updated:** 2025-10-15
**Maintained by:** Victor Piper + Claude
**Feedback:** Submit change signals or create issues in chora-compose repository
**Next Document:** `chora-compose-adr-001-mcp-architecture.md` (Architecture Decision Record for MCP implementation)
