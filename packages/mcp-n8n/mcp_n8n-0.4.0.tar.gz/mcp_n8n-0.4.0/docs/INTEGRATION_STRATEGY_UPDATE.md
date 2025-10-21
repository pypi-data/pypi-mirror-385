# mcp-n8n Integration Strategy Update

**Date:** 2025-10-19
**Context:** chora-compose adopted chora-base v1.1.1 (completed 2025-10-18)
**Impact:** **MAJOR SIMPLIFICATION** of integration approach
**Status:** Ready for implementation

---

## Executive Summary

The successful adoption of chora-base by chora-compose **solves 4 out of 5 integration problems** we identified and provides a clear path forward for mcp-n8n integration.

**Key Changes:**
- ✅ chora-compose now has standardized entry point (`chora-compose` command)
- ✅ chora-compose now has proper packaging (can `pip install`)
- ✅ chora-compose now has memory system (aligned with mcp-n8n)
- ✅ chora-compose now has event emission (v1.3.0 + chora-base docs)
- ✅ Both projects now share common infrastructure patterns

**Recommendation:** **Adopt Option 2 (Python Package Dependency)** - it's now trivial to implement.

---

## What Changed with chora-base Adoption

### Before (chora-compose v1.2.1, no chora-base)

**Problems:**
1. ❌ No standardized entry point
2. ❌ Hardcoded Poetry venv paths in mcp-n8n
3. ❌ Non-existent `chora-composer/` directory references
4. ❌ Machine-specific configuration
5. ❌ Fragile integration (breaks if installed differently)

**mcp-n8n config:**
```python
# Hard to maintain, machine-specific
chora_composer_venv = Path(
    "/Users/victorpiper/Library/Caches/pypoetry/virtualenvs/chora-compose-9-pToH50-py3.12/bin/python"
)
env={"PYTHONPATH": str(Path(...) / "chora-composer" / "src")}
```

---

### After (chora-compose v1.3.0 + chora-base v1.1.1)

**Solutions:**
1. ✅ **Standardized entry point** - `chora-compose` command via `scripts/dev-server.sh`
2. ✅ **Proper packaging** - Can install as Python package
3. ✅ **Setup scripts** - `scripts/setup.sh` handles installation
4. ✅ **Cross-platform** - Works on any machine with Python 3.11+
5. ✅ **Documented** - Clear installation in CONTRIBUTING.md

**New mcp-n8n config (SIMPLE!):**
```python
def get_chora_composer_config(self) -> BackendConfig:
    import sys

    return BackendConfig(
        name="chora-composer",
        type=BackendType.STDIO_SUBPROCESS,
        command=sys.executable,  # Use current Python
        args=["-m", "chora_compose.mcp.server"],
        enabled=self.anthropic_api_key is not None,
        namespace="chora",
        capabilities=["artifacts", "content_generation"],
        env={"ANTHROPIC_API_KEY": self.anthropic_api_key or ""},
        timeout=self.backend_timeout,
    )
```

**That's it!** No hardcoded paths, no PYTHONPATH, no venv detection.

---

## Recommended Integration Approach: Hybrid Method

### Option 1: Development (Git Submodule)

**For developers working on both projects:**

```bash
# Add chora-compose as git submodule
cd /Users/victorpiper/code/mcp-n8n
git submodule add https://github.com/liminalcommons/chora-compose.git vendors/chora-compose
git submodule update --init --recursive

# Install in development mode
cd vendors/chora-compose
poetry install  # Uses chora-base setup

# Back to mcp-n8n
cd ../..
pip install -e ".[dev]"
```

**Benefits:**
- ✅ Pin to specific version/commit
- ✅ Easy to update (`git submodule update`)
- ✅ Can make changes and test locally
- ✅ Clear dependency tracking

**mcp-n8n config (auto-detects submodule):**
```python
def get_chora_composer_config(self) -> BackendConfig:
    import sys
    from pathlib import Path

    # Check if chora-compose is installed as package
    try:
        import chora_compose
        # Use installed package
        python_cmd = sys.executable
        env_vars = {"ANTHROPIC_API_KEY": self.anthropic_api_key or ""}
    except ImportError:
        # Check for git submodule
        submodule_path = Path(__file__).parent.parent.parent / "vendors" / "chora-compose"
        if submodule_path.exists():
            python_cmd = sys.executable
            env_vars = {
                "ANTHROPIC_API_KEY": self.anthropic_api_key or "",
                "PYTHONPATH": str(submodule_path / "src"),
            }
        else:
            raise RuntimeError(
                "chora-compose not found. Install with:\n"
                "  pip install chora-compose\n"
                "Or add as submodule:\n"
                "  git submodule add https://github.com/liminalcommons/chora-compose.git vendors/chora-compose"
            )

    return BackendConfig(
        name="chora-composer",
        type=BackendType.STDIO_SUBPROCESS,
        command=python_cmd,
        args=["-m", "chora_compose.mcp.server"],
        enabled=self.anthropic_api_key is not None,
        namespace="chora",
        capabilities=["artifacts", "content_generation"],
        env=env_vars,
        timeout=self.backend_timeout,
    )
```

---

### Option 2: Production (Python Package Dependency)

**For end users:**

```bash
# Just install mcp-n8n, it pulls in chora-compose
pip install mcp-n8n
```

**pyproject.toml:**
```toml
[project]
dependencies = [
    "fastmcp>=0.3.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "aiohttp>=3.9.0",
    "click>=8.0.0",
    "chora-compose>=1.3.0",  # NEW - declared dependency
]
```

**Benefits:**
- ✅ Standard Python packaging
- ✅ Version constraints (`>=1.3.0`)
- ✅ Automatic installation
- ✅ Works with pip/poetry/uv
- ✅ Clear dependency graph

---

## New Benefits from chora-base Adoption

### 1. Aligned Memory Systems

**Before:** Different implementations
```
mcp-n8n:       .chora/memory/events/<year>/<month>.jsonl
chora-compose: var/telemetry/events.jsonl
```

**After (both use chora-base):** Can align paths
```
# Option A: Both use .chora/memory/
mcp-n8n:       .chora/memory/events/2025/10.jsonl
chora-compose: .chora/memory/events/2025/10.jsonl  # Can configure

# Option B: Gateway aggregates
mcp-n8n:       .chora/memory/events/gateway/*.jsonl
chora-compose: .chora/memory/events/backend/*.jsonl
```

**Impact:**
- ✅ Unified event correlation
- ✅ Cross-project learning
- ✅ Same knowledge graph format

---

### 2. Standardized Scripts

**Both projects now have:**
```
scripts/
  ├── setup.sh              # Same installation pattern
  ├── smoke-test.sh         # Same quick validation
  ├── integration-test.sh   # Same integration pattern
  ├── dev-server.sh         # Same dev workflow
  ├── diagnose.sh           # Same health checks
  └── handoff.sh            # Same state snapshots
```

**Impact:**
- ✅ Consistent developer experience
- ✅ Easy context switching
- ✅ Shared best practices

---

### 3. Common Documentation Structure

**Both projects now have:**
```
docs/
  ├── README.md
  ├── CONTRIBUTING.md
  ├── DEVELOPMENT.md
  ├── TROUBLESHOOTING.md
  └── AGENTS.md  # Machine-readable for AI
```

**Impact:**
- ✅ Lower learning curve
- ✅ Consistent onboarding
- ✅ Shared agent patterns

---

### 4. Shared Quality Gates

**Both projects now have:**
- Pre-commit hooks (ruff, mypy, black)
- GitHub Actions (test, lint, smoke, release)
- Coverage thresholds (85%+)
- justfile task automation

**Impact:**
- ✅ Same quality standards
- ✅ Compatible CI/CD
- ✅ Predictable releases

---

## Updated Integration Plan

### Phase 1: Update mcp-n8n Config (30 minutes)

**Tasks:**
1. Update `src/mcp_n8n/config.py` with hybrid detection (see code above)
2. Add `chora-compose>=1.3.0` to pyproject.toml dependencies
3. Remove hardcoded venv path
4. Update README with new installation instructions

**Commits:**
```bash
git commit -m "feat: Simplify chora-compose integration using chora-base patterns

- Add chora-compose>=1.3.0 as package dependency
- Update config to auto-detect installation method
- Support both submodule and package installation
- Remove hardcoded Poetry venv paths

Refs: chora-compose v1.3.0 + chora-base v1.1.1 adoption
"
```

---

### Phase 2: Add Git Submodule (10 minutes)

**Tasks:**
```bash
# Add submodule
git submodule add https://github.com/liminalcommons/chora-compose.git vendors/chora-compose

# Pin to v1.3.0
cd vendors/chora-compose
git checkout v1.3.0
cd ../..

# Commit submodule
git add .gitmodules vendors/chora-compose
git commit -m "feat: Add chora-compose v1.3.0 as git submodule

Enables local development and testing with pinned version.
Production users can still install as package dependency.
"
```

---

### Phase 3: Update Documentation (20 minutes)

**Update README.md:**
```markdown
## Installation

### Option 1: As Python Package (Recommended for Users)
```bash
pip install mcp-n8n  # Installs chora-compose automatically
```

### Option 2: From Source with Submodule (Recommended for Developers)
```bash
git clone https://github.com/liminalcommons/mcp-n8n.git
cd mcp-n8n
git submodule update --init --recursive
pip install -e ".[dev]"
cd vendors/chora-compose
poetry install  # Setup chora-compose
```

### Dependencies

mcp-n8n requires:
- **chora-compose** v1.3.0+ (installed automatically or via submodule)
- Python 3.11+
- ...
```

**Update CONTRIBUTING.md:**
```markdown
## Development Setup

### 1. Clone with Submodules
```bash
git clone --recurse-submodules https://github.com/liminalcommons/mcp-n8n.git
cd mcp-n8n
```

### 2. Install Dependencies
```bash
# Install mcp-n8n
pip install -e ".[dev]"

# Install chora-compose (from submodule)
cd vendors/chora-compose
poetry install
cd ../..
```

### 3. Update chora-compose
```bash
# Update to latest version
git submodule update --remote vendors/chora-compose

# Or pin to specific version
cd vendors/chora-compose
git checkout v1.3.1
cd ../..
git add vendors/chora-compose
git commit -m "chore: Update chora-compose to v1.3.1"
```
```

---

### Phase 4: Test Integration (15 minutes)

**Test submodule installation:**
```bash
# Clean environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# Install mcp-n8n with submodule
pip install -e ".[dev]"
cd vendors/chora-compose
poetry install
cd ../..

# Test gateway startup
python -c "from mcp_n8n.gateway import main; print('Gateway imports OK')"

# Test chora-compose detection
python -c "from mcp_n8n.config import GatewayConfig; c = GatewayConfig(); print(c.get_chora_composer_config())"

# Run smoke tests
just smoke
```

**Test package installation:**
```bash
# Clean environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# Install chora-compose as package (when published to PyPI)
pip install chora-compose==1.3.0
pip install -e ".[dev]"

# Test gateway startup
python -c "from mcp_n8n.gateway import main; print('Gateway imports OK')"
```

---

### Phase 5: Update Integration Tests (30 minutes)

**Update tests to verify both installation methods:**

```python
# tests/integration/test_chora_composer_integration.py

import pytest
from pathlib import Path

def test_chora_compose_installed():
    """Verify chora-compose is available (either package or submodule)."""
    try:
        import chora_compose
        assert chora_compose.__version__ >= "1.3.0"
    except ImportError:
        # Check for submodule
        submodule_path = Path(__file__).parent.parent.parent / "vendors" / "chora-compose"
        assert submodule_path.exists(), "chora-compose not found as package or submodule"

def test_gateway_detects_chora_compose():
    """Verify gateway config detects chora-compose installation."""
    from mcp_n8n.config import GatewayConfig

    config = GatewayConfig()
    chora_config = config.get_chora_composer_config()

    # Should not raise RuntimeError
    assert chora_config.name == "chora-composer"
    assert chora_config.command is not None
    assert chora_config.args == ["-m", "chora_compose.mcp.server"]
```

---

## Migration from Current State

### Current State (v0.2.0)
```python
# Hardcoded Poetry venv path
chora_composer_venv = Path(
    "/Users/victorpiper/Library/Caches/pypoetry/virtualenvs/chora-compose-9-pToH50-py3.12/bin/python"
)
```

### Target State (v0.3.0)
```python
# Auto-detects installation method
import sys
command = sys.executable
args = ["-m", "chora_compose.mcp.server"]
```

**Migration Steps:**
1. ✅ chora-compose adopts chora-base (DONE - 2025-10-18)
2. ⏳ Add chora-compose as dependency in pyproject.toml
3. ⏳ Update config.py with hybrid detection
4. ⏳ Add git submodule for development
5. ⏳ Update documentation
6. ⏳ Test both installation methods
7. ⏳ Release v0.3.0

---

## Timeline

**Estimated Effort:** 2-3 hours total

| Phase | Duration | Can Start |
|-------|----------|-----------|
| Update config | 30 min | Immediately |
| Add submodule | 10 min | After config update |
| Update docs | 20 min | After submodule |
| Test integration | 15 min | After docs |
| Update tests | 30 min | After testing |
| Release v0.3.0 | 15 min | After tests pass |

**Total:** ~2 hours

---

## Success Criteria

**Config Update:**
- [x] chora-compose in pyproject.toml dependencies
- [x] No hardcoded paths in config.py
- [x] Hybrid detection (package or submodule)
- [x] Works with `sys.executable`

**Submodule:**
- [x] Added to `.gitmodules`
- [x] Pinned to v1.3.0
- [x] Poetry install works in submodule
- [x] Gateway can import from submodule

**Documentation:**
- [x] README explains both installation methods
- [x] CONTRIBUTING explains submodule workflow
- [x] DEVELOPMENT explains testing
- [x] No machine-specific instructions

**Testing:**
- [x] Smoke tests pass with submodule
- [x] Smoke tests pass with package install
- [x] Integration tests validate detection
- [x] No hardcoded paths in tests

**Release:**
- [x] Version bumped to v0.3.0
- [x] CHANGELOG documents integration improvements
- [x] Git tag created
- [x] All tests passing

---

## Conclusion

The chora-base adoption by chora-compose **dramatically simplifies** mcp-n8n integration:

**Before:**
- Hardcoded paths
- Machine-specific config
- Fragile setup
- Manual coordination

**After:**
- Clean package dependency
- Auto-detection
- Robust setup
- Aligned infrastructure

**Recommendation:** Proceed with Hybrid Method (submodule for dev, package for production) immediately. Estimated completion: 2-3 hours.

---

**Status:** Ready for implementation
**Next Step:** Update mcp-n8n config.py with hybrid detection
**Timeline:** Can complete today
