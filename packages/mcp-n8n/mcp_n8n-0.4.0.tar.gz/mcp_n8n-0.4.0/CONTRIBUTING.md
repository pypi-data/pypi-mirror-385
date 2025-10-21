# Contributing to mcp-n8n

Thank you for your interest in contributing to mcp-n8n! This guide will help you get started with contributing code, documentation, bug reports, and feature requests.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style Guide](#code-style-guide)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Architecture Overview](#architecture-overview)
- [Release Process](#release-process)
- [Communication](#communication)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. By participating in this project, you agree to:

- **Be respectful** - Treat everyone with respect and professionalism
- **Be constructive** - Provide helpful feedback and criticism
- **Be collaborative** - Work together toward common goals
- **Be patient** - Remember that everyone has different experience levels

**Unacceptable behavior includes:**
- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

**Reporting:** If you experience or witness unacceptable behavior, please contact the maintainers at security@example.com.

---

## Getting Started

### Prerequisites

- **Python 3.11+** (check with `python --version`)
- **Git** for version control
- **Just** task runner (optional but recommended)

### First-Time Setup

1. **Fork and clone the repository:**

```bash
# Fork on GitHub first, then clone your fork with submodules
git clone --recurse-submodules https://github.com/YOUR_USERNAME/mcp-n8n.git
cd mcp-n8n

# Add upstream remote
git remote add upstream https://github.com/yourusername/mcp-n8n.git

# If you forgot --recurse-submodules, initialize them now:
git submodule update --init --recursive
```

2. **Create virtual environment:**

```bash
# Using our automated script (recommended)
./scripts/venv-create.sh

# Or manually
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

4. **Verify installation:**

```bash
# Run environment checks
just check-env

# Run smoke tests
just smoke

# Run full test suite
just test
```

5. **Configure environment:**

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
# ANTHROPIC_API_KEY=your_key_here
# CODA_API_KEY=your_key_here
```

**Troubleshooting:** If you encounter issues, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

---

## Dependency Management

mcp-n8n uses standard Python packaging for all dependencies:
- `chora-compose>=1.3.0` - Installed via pip/PyPI for artifact generation

All dependencies are declared in [pyproject.toml](pyproject.toml) and automatically installed when you run:
```bash
pip install -e ".[dev]"
```

---

## Development Workflow

### Branch Strategy

We follow a simplified Git workflow:

- **`main`** - Production-ready code, protected branch
- **`develop`** - Integration branch for features (if used)
- **`feature/xyz`** - New features or enhancements
- **`bugfix/xyz`** - Bug fixes
- **`hotfix/xyz`** - Urgent production fixes
- **`release/vX.Y.Z`** - Release preparation

### Creating a Feature Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/add-backend-xyz

# Make changes, commit, push
git add .
git commit -m "feat: add XYZ backend integration"
git push origin feature/add-backend-xyz
```

### Commit Message Format

We follow a conventional commit style with Claude Code attribution:

```
<type>: <subject>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring (no behavior change)
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks (dependencies, build, etc.)
- `perf:` - Performance improvements
- `ci:` - CI/CD changes

**Examples:**

```
feat: add n8n workflow backend integration

Implement N8NBackend class for executing n8n workflows via API.
Adds namespace n8n:* for workflow tools.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

```
fix: resolve tool routing for nested namespaces

Fixes issue where nested namespace (e.g., chora:sub:tool) would
fail to route correctly. Updated regex pattern in registry.

Resolves #42

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Keeping Your Branch Updated

```bash
# Fetch latest changes
git fetch upstream

# Rebase your branch on main
git rebase upstream/main

# If conflicts occur, resolve them, then:
git add .
git rebase --continue

# Force push to your fork (only for your feature branches!)
git push origin feature/xyz --force-with-lease
```

---

## Code Style Guide

We enforce code style automatically with pre-commit hooks. Follow these guidelines:

### Python Style

- **PEP 8** compliance (enforced by ruff)
- **Type hints** on all functions (enforced by mypy --strict)
- **Docstrings** on public classes and functions
- **Line length:** 88 characters (black default)
- **Imports:** Sorted and organized (isort via ruff)

**Example:**

```python
from typing import Any

def process_tool_call(
    tool_name: str,
    arguments: dict[str, Any],
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Process a tool call and return the result.

    Args:
        tool_name: Namespaced tool name (e.g., "chora:generate_content")
        arguments: Tool arguments as key-value pairs
        trace_id: Optional trace ID for correlation

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool_name format is invalid
        BackendError: If backend execution fails
    """
    # Implementation...
```

### Code Organization

- **One class per file** (for major classes)
- **Group related functions** in modules
- **Avoid deep nesting** (max 3-4 levels)
- **Use descriptive names** (readability over brevity)

### Configuration

- **Use pydantic** for configuration models
- **Environment variables** for secrets
- **Type-safe** config access

### Error Handling

```python
# Good: Specific exceptions
try:
    result = backend.call_tool(tool_name, args)
except BackendNotFoundError as e:
    logger.error(f"Backend not found: {e}")
    raise
except BackendTimeoutError as e:
    logger.warning(f"Backend timeout, retrying: {e}")
    # Retry logic...

# Bad: Bare except
try:
    result = backend.call_tool(tool_name, args)
except:  # ❌ Too broad
    pass
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use structured logging
logger.info("Tool call started", extra={
    "tool_name": tool_name,
    "trace_id": trace_id,
})

# Avoid f-strings in log messages (use % formatting)
logger.debug("Received %d arguments", len(arguments))
```

---

## Testing Requirements

All code changes must include tests and pass existing tests.

### Test Coverage

- **Minimum coverage:** 85% (enforced)
- **All new functions** must have tests
- **Bug fixes** must include regression tests

### Running Tests

```bash
# Quick smoke tests (<30 seconds)
just smoke

# Full test suite with coverage
just test

# Coverage report (HTML)
pytest --cov=src/mcp_n8n --cov-report=html
open htmlcov/index.html
```

### Writing Tests

Tests go in `tests/` directory, mirroring `src/` structure:

```
src/mcp_n8n/
  backends/
    registry.py
tests/
  test_registry.py     # Unit tests
  smoke/
    test_routing.py    # Smoke tests
```

**Example test:**

```python
import pytest
from mcp_n8n.backends.registry import BackendRegistry

def test_registry_add_backend():
    """Test adding a backend to registry."""
    registry = BackendRegistry()
    backend = MockBackend(name="test", namespace="test")

    registry.add(backend)

    assert "test" in registry.list_backends()
    assert registry.get("test") == backend

def test_registry_duplicate_namespace():
    """Test that duplicate namespaces raise ValueError."""
    registry = BackendRegistry()
    backend1 = MockBackend(name="test1", namespace="same")
    backend2 = MockBackend(name="test2", namespace="same")

    registry.add(backend1)

    with pytest.raises(ValueError, match="namespace.*already exists"):
        registry.add(backend2)
```

### Smoke Tests

Smoke tests are fast validation tests using mocks:

```python
# tests/smoke/test_new_feature.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_backend():
    backend = MagicMock()
    backend.name = "test"
    backend.namespace = "test"
    backend.call_tool = AsyncMock(return_value={"success": True})
    return backend

async def test_feature_works(mock_backend):
    """Smoke test: feature basic functionality."""
    result = await mock_backend.call_tool("test:tool", {})
    assert result["success"] is True
```

---

## Pull Request Process

### Before Submitting

1. **Run pre-merge checks:**

```bash
just pre-merge
```

This runs:
- Pre-commit hooks (ruff, mypy, black)
- Smoke tests
- Full test suite with ≥85% coverage
- CHANGELOG.md validation

2. **Update CHANGELOG.md:**

Add entry under `## [Unreleased]`:

```markdown
## [Unreleased]

### Added
- New XYZ backend integration (#123)

### Fixed
- Tool routing for nested namespaces (#42)
```

3. **Review your changes:**

```bash
git diff main...feature/xyz
```

### Submitting PR

1. **Push to your fork:**

```bash
git push origin feature/xyz
```

2. **Create Pull Request on GitHub:**

- **Title:** Short, descriptive summary
- **Description:** Use the template below

**PR Template:**

```markdown
## Description

Brief description of what this PR does.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Checklist

- [ ] I have run `just pre-merge` and all checks pass
- [ ] I have updated CHANGELOG.md
- [ ] I have added tests that prove my fix/feature works
- [ ] I have updated documentation if needed
- [ ] My code follows the project's style guide
- [ ] All new and existing tests pass

## Related Issues

Closes #42
Related to #30

## Screenshots (if applicable)

(Add screenshots for UI changes)

## Additional Context

Any additional information reviewers should know.
```

### During Review

- **Respond to feedback** promptly
- **Make requested changes** in new commits
- **Rebase if requested** to clean up history
- **Be patient** - reviews may take a few days

### After Approval

- **Squash commits** if requested by maintainers
- **Wait for merge** - maintainers will merge when ready
- **Delete your branch** after merge (optional)

```bash
# After PR is merged
git checkout main
git pull upstream main
git branch -d feature/xyz
git push origin --delete feature/xyz
```

---

## Issue Guidelines

### Reporting Bugs

Use the **Bug Report** template on GitHub Issues:

**Include:**
- **Description:** What went wrong?
- **Reproduction steps:** How to trigger the bug
- **Expected behavior:** What should happen
- **Actual behavior:** What actually happened
- **Environment:** Python version, OS, mcp-n8n version
- **Logs:** Relevant error messages or stack traces

**Example:**

```markdown
## Bug Report

**Description:**
Gateway fails to start when CODA_API_KEY is missing.

**Steps to Reproduce:**
1. Remove CODA_API_KEY from .env
2. Run `mcp-n8n`
3. Observe error

**Expected:**
Gateway starts, Coda backend disabled with warning.

**Actual:**
Gateway crashes with KeyError.

**Environment:**
- Python: 3.11.9
- OS: macOS 14.5
- mcp-n8n: 0.1.0

**Error Log:**
```
KeyError: 'CODA_API_KEY'
  File "src/mcp_n8n/backends/coda_mcp.py", line 42
```
```

### Requesting Features

Use the **Feature Request** template:

**Include:**
- **Use case:** Why is this feature needed?
- **Proposed solution:** How should it work?
- **Alternatives:** What other approaches did you consider?
- **Additional context:** Examples, mockups, references

### Asking Questions

- **Check existing issues** first
- **Search documentation** (README, docs/)
- **Use GitHub Discussions** for questions (not Issues)
- **Provide context** when asking for help

---

## Architecture Overview

For detailed architecture information, see:

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - P5 Gateway pattern implementation
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Developer deep dive (Phase 4)
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - User-focused setup guide

### Key Concepts

**Pattern P5 (Gateway & Aggregator):**
- Single MCP server aggregating multiple backends
- Tool namespacing for routing (e.g., `chora:*`, `coda:*`)
- Subprocess-based backend execution

**Backend System:**
- `BackendRegistry` - Manages backend lifecycle
- `BaseBackend` - Abstract backend interface
- Backend implementations in `src/mcp_n8n/backends/`

**Configuration:**
- Pydantic models in `src/mcp_n8n/config.py`
- Environment variables via `.env`
- Backend-specific config sections

---

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH).

**For maintainers only:**
- See [RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) for full process
- **NEW:** Use `just release patch` for fully automated releases (1 command!)
- Or use `just release-draft patch` to review changes before pushing

**For contributors:**
- Focus on features and bug fixes
- Maintainers handle version bumps and releases
- Check [CHANGELOG.md](CHANGELOG.md) for latest changes

---

## Communication

### Where to Ask

- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - Questions, ideas, show & tell
- **Pull Requests** - Code review, implementation discussion
- **Email** - security@example.com for security issues

### Response Times

- **Security issues:** 24 hours
- **Bug reports:** 2-3 days
- **Feature requests:** 1 week
- **Pull requests:** 3-5 days for initial review

### Community

- **Be respectful** of everyone's time
- **Search before asking** - issue may already be addressed
- **Provide context** - help us help you
- **Give back** - help others when you can

---

## Recognition

Contributors are recognized in:
- **CHANGELOG.md** - Major contributions noted
- **GitHub Contributors** - Automatic recognition
- **Release Notes** - Significant features highlighted

Thank you for contributing to mcp-n8n! 🎉

---

## Quick Reference

**Common Commands:**

```bash
just check-env      # Validate environment
just smoke          # Quick tests (<30 sec)
just test           # Full test suite
just pre-merge      # Pre-PR validation
just lint           # Check code style
just format         # Auto-format code
just typecheck      # Type checking
```

**Useful Links:**

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Deep dive (Phase 4)
- [SECURITY.md](SECURITY.md) - Security policy

---

**Last updated:** 2025-10-17
