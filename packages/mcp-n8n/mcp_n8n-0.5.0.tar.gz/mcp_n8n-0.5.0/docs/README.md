---
title: mcp-n8n Documentation
type: project
status: current
last_updated: 2025-10-21
---

# mcp-n8n Documentation

Welcome to the **mcp-n8n** product documentation! This documentation follows the [Diátaxis framework](https://diataxis.fr/), organizing content by your intent: learning, solving problems, looking up information, or understanding concepts.

---

## 🚀 Getting Started

**New to mcp-n8n?** Start here:

1. **[Getting Started Tutorial](tutorials/getting-started.md)** (5 minutes)
   - Install mcp-n8n
   - Configure Claude Desktop or Cursor
   - Make your first tool call

2. **[First Workflow Tutorial](tutorials/first-workflow.md)** (30 minutes)
   - Build a daily report workflow
   - Aggregate git commits and telemetry
   - Generate formatted reports

3. **[Event-Driven Workflow Tutorial](tutorials/event-driven-workflow.md)** (30 minutes)
   - Route events to workflows automatically
   - Configure YAML event mappings
   - Enable hot-reload for rapid iteration

---

## 📖 Documentation by Type

### [Tutorials](tutorials/) - Learning-Oriented

**Step-by-step lessons** to build confidence through hands-on practice.

| Tutorial | Time | Level | Description |
|----------|------|-------|-------------|
| [Getting Started](tutorials/getting-started.md) | 5 min | Beginner | Install and configure mcp-n8n |
| [First Workflow](tutorials/first-workflow.md) | 30 min | Beginner | Build daily report workflow |
| [Event-Driven Workflow](tutorials/event-driven-workflow.md) | 30 min | Intermediate | Event routing with YAML config |

### [How-To Guides](how-to/) - Problem-Oriented

**Task-focused guides** to solve specific problems.

**Installation & Setup:**
- [Install mcp-n8n](how-to/install.md) - Production vs. development install
- [Setup Claude Desktop](how-to/setup-claude-desktop.md) - Claude Desktop configuration
- [Setup Cursor](how-to/setup-cursor.md) - Cursor IDE configuration

**Configuration:**
- [Configure Backends](how-to/configure-backends.md) - Add/remove/customize backends
- [Query Events](how-to/query-events.md) - Query telemetry events (MCP tool, CLI, Python API)

**Workflows:**
- [Build Custom Workflow](how-to/build-custom-workflow.md) - Workflow patterns and templates
- [Debug Gateway](how-to/debug-gateway.md) - Systematic troubleshooting

**Troubleshooting:**
- [Troubleshoot](how-to/troubleshoot.md) - Common issues and solutions
- [Rollback Backend](how-to/rollback-backend.md) - Switch to stable backend

### [Reference](reference/) - Information-Oriented

**Specifications and API documentation** for looking up details.

| Reference | Description |
|-----------|-------------|
| [Tools](reference/tools.md) | Complete MCP tool catalog with examples |
| [API](reference/api.md) | MCP protocol reference for mcp-n8n |
| [Event Schema](reference/event-schema.md) | Telemetry event structure (v1.0) |
| [Configuration](reference/configuration.md) | Environment variables and settings |
| [CLI Reference](reference/cli-reference.md) | chora-memory command reference |
| [Specifications](reference/specs/) | Ecosystem integration specs (event schema, telemetry) |

### [Explanation](explanation/) - Understanding-Oriented

**Conceptual documentation** to understand why and how things work.

| Explanation | Description |
|-------------|-------------|
| [Architecture](explanation/architecture.md) | Pattern P5 Gateway & Aggregator explained |
| [Memory System](explanation/memory-system.md) | Event log, knowledge graph, agent profiles |
| [Integration Patterns](explanation/integration-patterns.md) | P5, N2, N3, N5 patterns |
| [Workflows](explanation/workflows.md) | Workflow types and design principles |

---

## 🎯 Find What You Need

### By Task

**I want to...**
- **Install mcp-n8n** → [How-To: Install](how-to/install.md)
- **Configure Claude Desktop** → [How-To: Setup Claude Desktop](how-to/setup-claude-desktop.md)
- **Build my first workflow** → [Tutorial: First Workflow](tutorials/first-workflow.md)
- **Query telemetry events** → [How-To: Query Events](how-to/query-events.md)
- **Debug gateway issues** → [How-To: Debug Gateway](how-to/debug-gateway.md)
- **Understand architecture** → [Explanation: Architecture](explanation/architecture.md)
- **Look up tool parameters** → [Reference: Tools](reference/tools.md)

### By Role

**I'm a...**
- **First-time user** → Start with [Getting Started](tutorials/getting-started.md)
- **Developer building workflows** → See [Build Custom Workflow](how-to/build-custom-workflow.md)
- **AI agent** → Read [dev-docs/AGENTS.md](../dev-docs/AGENTS.md)
- **Architect** → Review [Explanation: Architecture](explanation/architecture.md)
- **Contributor** → See [Development Documentation](../dev-docs/)

---

## 🔧 Development Documentation

For developers working **on** mcp-n8n (not just using it):

**[dev-docs/](../dev-docs/)** - Development documentation
- [ARCHITECTURE.md](../dev-docs/ARCHITECTURE.md) - System architecture (Pattern P5 deep dive)
- [DEVELOPMENT.md](../dev-docs/DEVELOPMENT.md) - Development setup and workflow
- [TESTING.md](../dev-docs/TESTING.md) - Testing strategy (BDD/TDD)
- [RELEASE.md](../dev-docs/RELEASE.md) - Release process and checklist
- [AGENTS.md](../dev-docs/AGENTS.md) - Machine-readable instructions for AI agents

**[project/](../project/)** - Project status and planning
- [ROADMAP.md](../project/ROADMAP.md) - Development roadmap (Sprints 1-8)
- [SPRINT_STATUS.md](../project/SPRINT_STATUS.md) - Current sprint status
- [CHANGELOG.md](../project/CHANGELOG.md) - Version history (v0.1 → v0.5)

---

## 📚 Additional Resources

### Standards & Processes

- [Documentation Standard](process/DOCUMENTATION_STANDARD.md) - How docs are organized and written
- [Development Lifecycle](process/development-lifecycle.md) - DDD/BDD/TDD workflow
- [BDD Workflow](process/bdd-workflow.md) - Behavior-Driven Development
- [TDD Workflow](process/tdd-workflow.md) - Test-Driven Development

### Archived Documentation

Historical documentation preserved for reference:

**[archive/](archive/)** - Historical documentation
- [Sprints](archive/sprints/) - Sprint-specific documentation
- [Chora Alignment](archive/chora-alignment/) - Historical alignment analyses
- [Integration Strategies](archive/integration-strategies/) - Draft integration guides
- [Ecosystem](archive/ecosystem/) - Original ecosystem architecture docs

**Note:** Archive documentation is deprecated. Use current docs above for up-to-date information.

---

## 🤝 Contributing

Found an error? Want to improve the docs?

1. **Small fixes:** Open a PR with changes
2. **New documentation:** Follow [Documentation Standard](process/DOCUMENTATION_STANDARD.md)
3. **Questions:** Open an issue in the repository

**Documentation Guidelines:**
- All docs follow [Diátaxis framework](https://diataxis.fr/)
- Code examples must be executable
- Use appropriate document type (tutorial/how-to/reference/explanation)
- See [.github/DOCUMENTATION_STANDARD.md](../.github/DOCUMENTATION_STANDARD.md)

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/anthropics/mcp-n8n/issues)
- **Discussions:** [GitHub Discussions](https://github.com/anthropics/mcp-n8n/discussions)
- **Documentation:** You're here!

---

**Last Updated:** 2025-10-21
**Version:** v0.5.0 (Sprint 5 complete)
**Documentation Status:** 36/43 tasks complete (84%)
