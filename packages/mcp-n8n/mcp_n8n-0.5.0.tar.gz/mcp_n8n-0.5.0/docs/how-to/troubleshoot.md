# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with mcp-n8n. Use the quick diagnostic commands first, then check the relevant section for your specific problem.

---

## Quick Diagnostics

Run these commands to identify issues:

```bash
# Full environment check (recommended first step)
just check-env

# Quick health check
just smoke

# System information
just info

# Automated diagnostics (Phase 4)
just diagnose
```

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Issues](#configuration-issues)
3. [Runtime Issues](#runtime-issues)
4. [Testing Issues](#testing-issues)
5. [Release Issues](#release-issues)
6. [Performance Issues](#performance-issues)

---

## Installation Issues

### Problem: Python version mismatch

**Symptoms:**
```
ERROR: This package requires Python >=3.11
Your Python version: 3.9.x
```

**Diagnosis:**
```bash
python --version
```

**Solution:**
1. Install Python 3.11 or higher
2. Create virtual environment with correct version:

```bash
# macOS/Linux
python3.11 -m venv .venv
source .venv/bin/activate

# Windows
py -3.11 -m venv .venv
.venv\Scripts\activate
```

3. Verify version:
```bash
python --version  # Should show 3.11.x or higher
```

**Prevention:**
- Use `.python-version` file (enforces 3.11.9)
- Use `pyenv` or `asdf` for version management

---

### Problem: Virtual environment not activated

**Symptoms:**
- Packages not found after installation
- `mcp-n8n` command not found
- Wrong Python version

**Diagnosis:**
```bash
which python  # Should show path to .venv/bin/python
echo $VIRTUAL_ENV  # Should show path to .venv
```

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate  # Windows

# Verify activation
which python  # Should include .venv
```

**Prevention:**
- Add activation to shell profile (`.bashrc`, `.zshrc`)
- Use direnv for automatic activation
- Check `just check-env` before working

---

### Problem: Dependency installation fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement fastmcp>=0.3.0
```

**Diagnosis:**
```bash
pip --version  # Check pip is up to date
pip install --dry-run -e ".[dev]"  # Test installation
```

**Solution:**
1. Update pip:
```bash
python -m pip install --upgrade pip
```

2. Clear pip cache:
```bash
pip cache purge
```

3. Reinstall:
```bash
pip install -e ".[dev]"
```

**Alternative - Clean rebuild:**
```bash
just venv-clean
just venv-create
```

**Prevention:**
- Always update pip before installing
- Use pinned versions (already in pyproject.toml)
- Check internet connection

---

### Problem: Pre-commit hooks fail to install

**Symptoms:**
```
ERROR: Failed to install pre-commit hooks
```

**Diagnosis:**
```bash
pre-commit --version
which pre-commit
```

**Solution:**
1. Ensure pre-commit is installed:
```bash
pip install pre-commit==4.0.1
```

2. Install hooks:
```bash
pre-commit install
```

3. Test hooks:
```bash
pre-commit run --all-files
```

**Prevention:**
- Install dev dependencies: `pip install -e ".[dev]"`
- Run `just setup` for complete setup

---

## Configuration Issues

### Problem: Missing API keys

**Symptoms:**
```
KeyError: 'ANTHROPIC_API_KEY'
ERROR: Required environment variable not set
```

**Diagnosis:**
```bash
# Check if .env exists
ls -la .env

# Check environment variables
env | grep -E "ANTHROPIC|CODA"
```

**Solution:**
1. Create `.env` file from template:
```bash
cp .env.example .env
```

2. Add your API keys:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
CODA_API_KEY=your-coda-key-here
```

3. Load environment:
```bash
# If using dotenv
source .env  # Or restart shell

# Verify
echo $ANTHROPIC_API_KEY  # Should show your key
```

**Prevention:**
- Never commit `.env` (already in .gitignore)
- Use `.env.example` as template
- Run `just check-env` to verify

---

### Problem: Invalid backend paths

**Symptoms:**
```
ERROR: Backend executable not found: /path/to/chora-composer
FileNotFoundError: [Errno 2] No such file or directory
```

**Diagnosis:**
```bash
# Check if backend paths exist
ls -la vendors/chora-platform/chora-composer

# Check environment variables
echo $CHORA_COMPOSER_PATH
```

**Solution:**
1. Verify backend is cloned:
```bash
git submodule update --init --recursive
```

2. Check backend paths in config:
```python
# In .env or config
CHORA_COMPOSER_PATH=/absolute/path/to/chora-composer
```

3. Test backend manually:
```bash
python -m chora_composer.mcp_server
```

**Prevention:**
- Use absolute paths in configuration
- Run `just check-env` to validate paths
- Ensure submodules are initialized

---

### Problem: Namespace conflicts

**Symptoms:**
```
ValueError: Backend namespace 'chora' already registered
```

**Diagnosis:**
Check backend registry in logs:
```bash
grep "Registered backend" logs/mcp-n8n.log
```

**Solution:**
1. Review backend configurations
2. Ensure unique namespaces per backend
3. Update config if needed:

```python
# Each backend needs unique namespace
ChoraComposerBackend(namespace="chora")
CodaMCPBackend(namespace="coda")
# Not: Both using "data"
```

**Prevention:**
- Follow namespace conventions (backend-name:*)
- Document namespaces in README
- Use `just smoke` to catch conflicts early

---

### Problem: Environment variables not loading

**Symptoms:**
- Variables set in `.env` but not accessible
- Gateway uses default values instead

**Diagnosis:**
```bash
# Check .env file exists
cat .env

# Check if dotenv is working
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

**Solution:**
1. Ensure python-dotenv is installed:
```bash
pip show python-dotenv
```

2. Load manually in development:
```bash
export $(cat .env | xargs)
```

3. Restart application after changing .env

**Prevention:**
- Use `load_dotenv()` in code (already done)
- Set environment variables at OS level for production
- Check `.env` file permissions (should be readable)

---

## Runtime Issues

### Problem: Gateway startup fails

**Symptoms:**
```
ERROR: Failed to start MCP gateway
Traceback (most recent call last):
  ...
```

**Diagnosis:**
```bash
# Try starting in debug mode
MCP_N8N_DEBUG=1 MCP_N8N_LOG_LEVEL=DEBUG mcp-n8n

# Check logs
tail -f logs/mcp-n8n.log
```

**Solution:**
1. Check all environment variables are set:
```bash
just check-env
```

2. Verify backend paths:
```bash
ls -la $(grep CHORA_COMPOSER_PATH .env | cut -d= -f2)
```

3. Test backends individually:
```bash
# Test Chora Composer
cd vendors/chora-platform/chora-composer
python -m chora_composer.mcp_server
```

4. Check for port conflicts (if using network transport)

**Prevention:**
- Run `just smoke` before starting
- Use `just check-env` regularly
- Check logs for warnings

---

### Problem: Backend connection errors

**Symptoms:**
```
ERROR: Failed to connect to backend: chora-composer
TimeoutError: Backend did not respond
```

**Diagnosis:**
```bash
# Check backend process
ps aux | grep chora-composer

# Check logs
grep "chora-composer" logs/mcp-n8n.log
```

**Solution:**
1. Restart gateway:
```bash
# Stop existing process
pkill -f mcp-n8n

# Start fresh
mcp-n8n
```

2. Check backend dependencies:
```bash
cd vendors/chora-platform/chora-composer
pip list | grep -E "fastmcp|anthropic"
```

3. Increase timeout (if needed):
```python
# In config
backend_timeout = 30  # seconds
```

**Prevention:**
- Ensure backends are healthy before starting gateway
- Monitor backend logs
- Use health checks

---

### Problem: Tool routing problems

**Symptoms:**
```
ERROR: Tool 'generate_content' not found
ValueError: Invalid tool name format
```

**Diagnosis:**
```bash
# Check tool name format
# Should be: namespace:tool_name
# Example: chora:generate_content

# List available tools
grep "Registered tool" logs/mcp-n8n.log
```

**Solution:**
1. Verify tool name includes namespace:
```python
# Correct
tool_name = "chora:generate_content"

# Wrong
tool_name = "generate_content"  # ❌ Missing namespace
```

2. Check tool is registered:
```bash
# In logs, should see:
# "Registered tool: chora:generate_content"
```

3. Verify backend is loaded:
```bash
grep "Backend loaded" logs/mcp-n8n.log
```

**Prevention:**
- Always use namespaced tool names
- Check tool list before calling
- Use `just smoke` to validate routing

---

### Problem: Logging/trace issues

**Symptoms:**
- No logs generated
- Logs missing trace IDs
- Cannot correlate events

**Diagnosis:**
```bash
# Check log file exists
ls -la logs/mcp-n8n.log

# Check log level
echo $MCP_N8N_LOG_LEVEL

# Check recent logs
tail -20 logs/mcp-n8n.log
```

**Solution:**
1. Verify log directory exists:
```bash
mkdir -p logs
```

2. Check log level:
```bash
# Set to DEBUG for verbose logging
export MCP_N8N_LOG_LEVEL=DEBUG
```

3. Check file permissions:
```bash
chmod 644 logs/mcp-n8n.log
```

4. For trace correlation, set CHORA_TRACE_ID:
```bash
export CHORA_TRACE_ID=$(uuidgen)
```

**Prevention:**
- Use structured logging (already implemented)
- Set appropriate log levels per environment
- Rotate logs regularly

---

## Testing Issues

### Problem: Smoke test failures

**Symptoms:**
```bash
$ just smoke
FAILED tests/smoke/test_gateway_startup.py::test_gateway_imports
```

**Diagnosis:**
```bash
# Run smoke tests with verbose output
pytest tests/smoke/ -v

# Check for import errors
python -c "import mcp_n8n; print('OK')"
```

**Solution:**
1. Ensure package is installed:
```bash
pip install -e ".[dev]"
```

2. Check for missing dependencies:
```bash
pip check
```

3. Re-run specific test:
```bash
pytest tests/smoke/test_gateway_startup.py::test_gateway_imports -v
```

**Prevention:**
- Run `just smoke` before committing
- Keep dependencies up to date
- Use `just check-env` before testing

---

### Problem: Coverage below threshold

**Symptoms:**
```
FAILED: coverage threshold not met (actual: 82%, required: 85%)
```

**Diagnosis:**
```bash
# Generate coverage report
pytest --cov=src/mcp_n8n --cov-report=html
open htmlcov/index.html

# Check which files need coverage
pytest --cov=src/mcp_n8n --cov-report=term-missing
```

**Solution:**
1. Identify uncovered lines (in HTML report)
2. Add tests for uncovered code
3. Re-run tests:
```bash
pytest --cov=src/mcp_n8n --cov-fail-under=85
```

**Alternative - Temporary exclusion:**
```python
# Add to code that doesn't need testing
if __name__ == "__main__":  # pragma: no cover
    main()
```

**Prevention:**
- Write tests as you code
- Run coverage locally: `just test-coverage`
- Check coverage in PR before submitting

---

### Problem: Type checking errors

**Symptoms:**
```
src/mcp_n8n/backends/registry.py:42: error: Missing return statement
```

**Diagnosis:**
```bash
# Run mypy
just typecheck

# Or directly
mypy src/mcp_n8n
```

**Solution:**
1. Add type hints:
```python
# Before
def process(data):
    return data

# After
def process(data: dict[str, Any]) -> dict[str, Any]:
    return data
```

2. Fix type errors:
```python
# Use type narrowing
if isinstance(value, str):
    return value.upper()  # mypy knows value is str here
```

3. Add type: ignore for third-party issues:
```python
from external_lib import foo  # type: ignore[import]
```

**Prevention:**
- Enable mypy in editor (VSCode)
- Run `just typecheck` before committing
- Pre-commit hooks catch type errors

---

### Problem: Linting failures

**Symptoms:**
```
src/mcp_n8n/gateway.py:123:80: E501 line too long (92 > 88 characters)
```

**Diagnosis:**
```bash
# Check linting errors
just lint

# Or with auto-fix
just lint-fix
```

**Solution:**
1. Auto-fix most issues:
```bash
just format  # Black formatting
just lint-fix  # Ruff auto-fix
```

2. Manual fixes for remaining issues
3. Re-run linting:
```bash
just lint
```

**Prevention:**
- Use editor plugins (ruff, black)
- Format on save (VSCode setting)
- Pre-commit hooks prevent commits

---

## Release Issues

### Problem: Version bump problems

**Symptoms:**
```
ERROR: Invalid version format in pyproject.toml
```

**Diagnosis:**
```bash
# Check current version
grep "^version = " pyproject.toml

# Test version bump (dry run)
./scripts/bump-version.sh patch --dry-run
```

**Solution:**
1. Ensure version follows semver:
```toml
# Correct
version = "0.1.0"

# Wrong
version = "v0.1.0"  # ❌ No 'v' prefix
version = "0.1"     # ❌ Missing patch
```

2. Use bump script:
```bash
just bump-patch  # 0.1.0 → 0.1.1
```

**Prevention:**
- Always use `just bump-*` commands
- Don't edit version manually
- Follow semver strictly

---

### Problem: Build failures

**Symptoms:**
```
ERROR: build failed
error: invalid command 'bdist_wheel'
```

**Diagnosis:**
```bash
# Check build dependencies
pip list | grep -E "build|twine"

# Try build with verbose
python -m build --verbose
```

**Solution:**
1. Install build dependencies:
```bash
pip install -e ".[release]"
```

2. Clean old build artifacts:
```bash
just clean
```

3. Rebuild:
```bash
just build
```

**Prevention:**
- Use `just build` (has validation)
- Install release dependencies
- Clean before building

---

### Problem: PyPI publishing errors

**Symptoms:**
```
ERROR: Failed to upload to PyPI
403 Forbidden: Invalid or expired API token
```

**Diagnosis:**
```bash
# Check if token is set
echo $TWINE_PASSWORD | head -c 20

# Test connection
twine check dist/*
```

**Solution:**
1. Create/update PyPI token:
   - Go to https://pypi.org/manage/account/token/
   - Create token with scope: "Entire account" or specific project
   - Copy token

2. Configure credentials:
```bash
# Option 1: Environment variable
export TWINE_PASSWORD=pypi-AgEI...

# Option 2: ~/.pypirc
cat > ~/.pypirc <<EOF
[pypi]
username = __token__
password = pypi-AgEI...
EOF
chmod 600 ~/.pypirc
```

3. Re-attempt upload:
```bash
just publish-prod
```

**Prevention:**
- Store token securely
- Use GitHub Actions for releases
- Test on TestPyPI first

---

### Problem: Git tag conflicts

**Symptoms:**
```
ERROR: tag 'v0.2.0' already exists
```

**Diagnosis:**
```bash
# Check existing tags
git tag -l

# Check remote tags
git ls-remote --tags origin
```

**Solution:**
1. Delete local tag (if incorrect):
```bash
git tag -d v0.2.0
```

2. Delete remote tag (if incorrect):
```bash
git push origin :refs/tags/v0.2.0
```

3. Bump version higher:
```bash
just bump-patch  # Creates v0.2.1 instead
```

**Prevention:**
- Use `just prepare-release` (handles tags)
- Don't create tags manually
- Follow release checklist

---

## Performance Issues

### Problem: Slow test execution

**Symptoms:**
- Tests take >5 minutes
- Timeout errors in CI

**Diagnosis:**
```bash
# Profile tests
pytest --durations=10

# Check for blocking operations
pytest -v --log-cli-level=DEBUG
```

**Solution:**
1. Use smoke tests for quick validation:
```bash
just smoke  # <30 seconds
```

2. Run specific test files:
```bash
pytest tests/test_specific.py
```

3. Parallelize tests (if many):
```bash
pytest -n auto  # Requires pytest-xdist
```

**Prevention:**
- Keep smoke tests fast (use mocks)
- Avoid network calls in tests
- Use pytest markers for slow tests

---

### Problem: High memory usage

**Symptoms:**
- Gateway crashes with OOM
- System becomes sluggish

**Diagnosis:**
```bash
# Monitor memory
ps aux | grep mcp-n8n

# Check log file size
du -h logs/mcp-n8n.log
```

**Solution:**
1. Enable log rotation (already configured)
2. Limit backend concurrency
3. Restart gateway periodically

**Prevention:**
- Monitor resource usage
- Set appropriate log retention
- Use log rotation

---

## Still Having Issues?

If your problem isn't covered here:

1. **Check the logs:**
```bash
tail -100 logs/mcp-n8n.log
```

2. **Run diagnostics:**
```bash
just diagnose  # Automated diagnostics (Phase 4)
```

3. **Search GitHub Issues:**
   - https://github.com/yourusername/mcp-n8n/issues

4. **Create an Issue:**
   - Include output from `just diagnose`
   - Provide steps to reproduce
   - Include error messages and logs

5. **Ask for Help:**
   - GitHub Discussions
   - Community channels

---

**Last updated:** 2025-10-17
