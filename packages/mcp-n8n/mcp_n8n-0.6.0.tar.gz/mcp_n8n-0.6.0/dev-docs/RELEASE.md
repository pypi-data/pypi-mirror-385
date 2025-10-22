# Release Guide

Complete guide for releasing new versions of mcp-n8n to PyPI and managing releases.

---

## Table of Contents

- [Overview](#overview)
- [Approach 1: Automated Release (Recommended)](#approach-1-automated-release-recommended)
- [Approach 2: Manual Review Release](#approach-2-manual-review-release)
- [Approach 3: Legacy Manual Release](#approach-3-legacy-manual-release)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

mcp-n8n supports **three release workflows**:

1. **Automated Release (Recommended)** - One command, 5 minutes, fully automated
2. **Manual Review Release** - Prepare locally, review, then push
3. **Legacy Manual Release** - Step-by-step manual process (rarely needed)

**Which approach to use:**
- ✅ **Automated**: For routine releases, patch/minor versions
- 🔍 **Manual Review**: For major versions, first-time releases
- 🛠️ **Legacy**: Only if automation fails

---

## Prerequisites

Before any release:

- [ ] **Clean environment**
  ```bash
  git status      # No uncommitted changes
  git branch --show-current  # On main branch
  git pull origin main       # Up to date
  ```

- [ ] **All tests pass**
  ```bash
  just pre-merge  # Runs all checks
  ```
  **Must pass:** Tests, linting, type checking, coverage ≥15%

- [ ] **Documentation updated**
  - [ ] README.md reflects current features
  - [ ] CHANGELOG.md has entries in `[Unreleased]` section
  - [ ] Configuration examples are accurate

- [ ] **Version decision made**
  Follow [Semantic Versioning](https://semver.org/):
  - **MAJOR** (X.0.0): Breaking changes
  - **MINOR** (0.X.0): New features (backward-compatible)
  - **PATCH** (0.0.X): Bug fixes (backward-compatible)

---

## Approach 1: Automated Release (Recommended)

**When to use:**
- Routine releases (patch/minor)
- Confident in changes
- CI pipeline is working

**Pros:**
- ✅ Fast: ~5 minutes total (1 command + CI wait)
- ✅ Consistent: Same process every time
- ✅ Safe: Automated checks prevent bad releases
- ✅ Complete: Handles git, PyPI, and GitHub release

**Cons:**
- ❌ Less control: No manual review before push
- ❌ Requires CI: Depends on GitHub Actions

### Steps

**1. Run automated release command:**

```bash
# For patch release (0.4.0 → 0.4.1)
just release patch

# For minor release (0.4.0 → 0.5.0)
just release minor

# For major release (0.4.0 → 1.0.0)
just release major
```

**What this does:**
1. Bumps version in `pyproject.toml`
2. Updates `CHANGELOG.md` (moves `[Unreleased]` → `[version]`)
3. Runs pre-merge checks (tests, linting, coverage)
4. Creates release commit
5. **Creates git tag** `vX.Y.Z`
6. **Pushes commit and tag to GitHub**
7. **Triggers GitHub Actions**

**2. Monitor GitHub Actions (~5 minutes):**

```bash
# View workflow status
# https://github.com/YOUR_USERNAME/mcp-n8n/actions
```

**GitHub Actions workflow:**
1. **Build** - Creates wheel + tarball (~1 min)
2. **Test** - Runs full test suite (~2 min)
3. **Publish PyPI** - Uploads to pypi.org (~30 sec)
4. **GitHub Release** - Creates release with CHANGELOG (~30 sec)

**3. Verify release:**

```bash
# Create clean environment
python -m venv verify-release
source verify-release/bin/activate

# Install from PyPI
pip install mcp-n8n==X.Y.Z

# Verify
mcp-n8n --help
pip show mcp-n8n

# Cleanup
deactivate
rm -rf verify-release
```

**4. Verify online:**

- 📦 PyPI: https://pypi.org/project/mcp-n8n/X.Y.Z/
- 🐙 GitHub Release: https://github.com/YOUR_USERNAME/mcp-n8n/releases/tag/vX.Y.Z

**🎉 Done! Release complete.**

### Verification

**Success indicators:**
```bash
✓ Git tag vX.Y.Z created
✓ GitHub Actions workflow passed
✓ Package visible on PyPI
✓ GitHub release created
✓ Installation from PyPI works
```

**If GitHub Actions fails:**
- Check logs at https://github.com/YOUR_USERNAME/mcp-n8n/actions
- Fix issue, delete tag, retry:
  ```bash
  git tag -d vX.Y.Z
  git push origin :refs/tags/vX.Y.Z
  # Fix issue, then retry
  just release patch
  ```

---

## Approach 2: Manual Review Release

**When to use:**
- First release to PyPI
- Major version bumps
- Want to review before pushing
- Cautious about automation

**Pros:**
- ✅ Review before push: See exactly what will be released
- ✅ Control: Manual approval step
- ✅ Learning: Understand each step

**Cons:**
- ❌ Slower: 10-15 minutes total
- ❌ Manual steps: More room for error

### Steps

**1. Prepare release locally (no push):**

```bash
# Prepare but don't push
just release-draft patch  # or minor/major
```

**What this does:**
1. Bumps version in `pyproject.toml`
2. Updates `CHANGELOG.md`
3. Runs pre-merge checks
4. Creates release commit
5. **Stops** (no tag, no push)

**2. Review changes:**

```bash
# View the commit
git show HEAD

# Check version bump
grep "^version = " pyproject.toml

# Check CHANGELOG
git diff HEAD~1 CHANGELOG.md

# Verify tests passed
echo "All pre-merge checks passed ✓"
```

**3. Create tag and push:**

```bash
# Get version from pyproject.toml
VERSION=$(grep "^version = " pyproject.toml | cut -d'"' -f2)

# Create tag
git tag v$VERSION

# Push commit and tag
git push origin main
git push origin v$VERSION
```

**4. Monitor GitHub Actions:**

Same as Approach 1, step 2 - GitHub Actions triggers automatically on tag push.

**5. Verify release:**

Same as Approach 1, step 3-4.

### Verification

**Before pushing:**
```bash
# Review commit
git show HEAD

# Check diff
git diff HEAD~1 pyproject.toml CHANGELOG.md
```

**After pushing:**
Same verification as Approach 1.

---

## Approach 3: Legacy Manual Release

**When to use:**
- GitHub Actions unavailable
- PyPI upload issues
- Testing release process
- Local-only release

**Pros:**
- ✅ Complete control: Every step manual
- ✅ No CI dependency: Works offline

**Cons:**
- ❌ Slow: 20-30 minutes
- ❌ Error-prone: Many manual steps
- ❌ Tedious: Not recommended

### Steps

**1. Prepare release:**

```bash
# Bump version manually
just bump-patch  # or bump-minor, bump-major

# Update CHANGELOG manually
# Edit CHANGELOG.md: Move [Unreleased] → [version]

# Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): Bump version to X.Y.Z"
```

**2. Create tag:**

```bash
VERSION=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
git tag v$VERSION
```

**3. Build distribution:**

```bash
# Build packages
just build

# Verify build
ls -lh dist/
# Should see: mcp_n8n-X.Y.Z-py3-none-any.whl and mcp_n8n-X.Y.Z.tar.gz
```

**4. Test on TestPyPI (optional):**

```bash
# Upload to TestPyPI
just publish-test

# Test installation
pip install --index-url https://test.pypi.org/simple/ mcp-n8n==X.Y.Z
```

**5. Publish to PyPI:**

```bash
# Upload to production PyPI
just publish-prod

# Verify
pip install mcp-n8n==X.Y.Z
```

**6. Push git changes:**

```bash
git push origin main
git push origin vX.Y.Z
```

**7. Create GitHub Release manually:**

1. Go to: https://github.com/yourusername/mcp-n8n/releases
2. Click "Draft a new release"
3. Select tag: `vX.Y.Z`
4. Title: `vX.Y.Z - Brief description`
5. Body: Copy from CHANGELOG.md
6. Publish release

---

## Rollback Procedures

### Scenario 1: Bad Release on PyPI

**Problem:** Released version has critical bug

**Solution: Yank the release (hide from pip)**

```bash
# Install twine
pip install twine

# Yank the version
twine yank mcp-n8n X.Y.Z --reason "Critical bug in routing"

# Release fix as X.Y.Z+1
just release patch
```

**Note:**
- Yanked releases remain visible but won't install by default
- Users with pinned version can still install
- Cannot delete from PyPI, only yank

### Scenario 2: Bad Git Tag

**Problem:** Tag points to wrong commit or wrong version

**Solution: Delete and recreate tag**

```bash
# Delete local tag
git tag -d vX.Y.Z

# Delete remote tag
git push origin :refs/tags/vX.Y.Z

# Fix issue, create correct tag
git tag vX.Y.Z <correct-commit-sha>
git push origin vX.Y.Z
```

### Scenario 3: Accidental Release

**Problem:** Released too early or to wrong branch

**Solution: Yank + revert**

```bash
# 1. Yank from PyPI
twine yank mcp-n8n X.Y.Z --reason "Accidental release"

# 2. Delete tags
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z

# 3. Revert release commit
git revert HEAD
git push origin main

# 4. Delete GitHub release
# Go to releases page and delete manually
```

### Scenario 4: Failed GitHub Actions

**Problem:** CI fails after tag push

**Solution: Fix and re-tag**

```bash
# 1. Delete failed tag
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z

# 2. Fix the issue
git add <fixed-files>
git commit -m "fix: Issue that broke CI"

# 3. Re-create tag and push
git tag vX.Y.Z
git push origin main
git push origin vX.Y.Z
```

### Scenario 5: Rollback Dev Environment

**Problem:** Dev backend broken, need stable

**Solution: Quick rollback to stable**

```bash
# Automated rollback
just rollback

# This will:
# 1. Backup current config
# 2. Switch to stable backend
# 3. Verify stable works
```

**Manual rollback (if script fails):**

```bash
# For Claude Desktop (macOS)
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Comment out dev, uncomment stable
# Save and restart Claude

# For Cursor
code ~/.cursor/mcp.json
# Comment/uncomment, reload window
```

**Verification:**
```bash
just verify-stable
```

**See:** [Rollback Decision Tree](#rollback-decision-tree) below for when to rollback.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| "Version already exists on PyPI" | Cannot overwrite PyPI releases | Bump to new version: `just bump-patch` |
| "Twine upload failed - Invalid credentials" | Missing PyPI token | Set `TWINE_PASSWORD` env var or configure `~/.pypirc` |
| "Pre-merge checks fail" | Tests/linting failing | Fix issues: `just pre-merge` must pass before release |
| "Git tag already exists" | Tag conflict | Delete tag: `git tag -d vX.Y.Z` or bump version higher |
| "Package installed but command not found" | Missing entry point | Check `[project.scripts]` in `pyproject.toml` |
| "GitHub Actions stuck" | CI timeout or failure | Check logs, cancel workflow, fix issue, retry |
| "CHANGELOG not updated" | Forgot to move [Unreleased] | Update manually or use `just release-draft` |

### Common Issues

**Issue: Pre-merge checks fail**

**Diagnosis:**
```bash
just pre-merge
# Check which step fails: lint, typecheck, test, coverage
```

**Solution:**
```bash
# Fix linting
just lint-fix

# Fix type errors
just typecheck
# Manually fix issues

# Fix test failures
pytest -x  # Stop on first failure
# Fix test, rerun

# Fix coverage
just test-coverage
# Add tests for uncovered code
```

**Issue: GitHub Actions timeout**

**Diagnosis:**
Check workflow logs at https://github.com/YOUR_USERNAME/mcp-n8n/actions

**Solution:**
```bash
# Cancel stuck workflow
gh run cancel <run-id>

# Fix issue (usually test hanging)
# Then re-trigger by re-pushing tag:
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
git tag vX.Y.Z
git push origin vX.Y.Z
```

**Issue: Can't install from PyPI**

**Diagnosis:**
```bash
pip install mcp-n8n==X.Y.Z -vvv
# Check error message
```

**Solution:**
- **404 Not Found**: Package not published yet, wait 5-10 minutes for PyPI propagation
- **Version not found**: Check version exists: https://pypi.org/project/mcp-n8n/#history
- **Dependency conflict**: Check dependencies in `pyproject.toml`

---

## Rollback Decision Tree

```
Is dev backend broken?
  │
  ├─ YES → Can you fix it in <15 minutes?
  │   │
  │   ├─ YES → Fix and test with `just smoke`
  │   │
  │   └─ NO → ROLLBACK NOW
  │       │
  │       ├─ Run: just rollback
  │       ├─ Document issue in KNOWN_ISSUES.md
  │       └─ Debug later when not blocked
  │
  └─ NO → Do you need stable for important work?
      │
      ├─ YES → ROLLBACK NOW (proactive)
      │
      └─ NO → Continue with dev
```

**Rollback criteria:**
- ✅ Dev backend unresponsive (>30s timeouts)
- ✅ Critical bug discovered
- ✅ Can't debug quickly (>15 min blocked)
- ✅ Demo or presentation coming up
- ✅ Integration tests failing repeatedly

**Recovery time:**
- Automated: <1 minute
- Manual: 2-3 minutes
- With verification: 3-5 minutes

---

## Best Practices

### ✅ DO

**1. Test before releasing:**
```bash
just pre-merge  # Must pass
```

**2. Use semantic versioning:**
- Breaking change → Major
- New feature → Minor
- Bug fix → Patch

**3. Update CHANGELOG:**
- Add entries to `[Unreleased]` as you work
- Release script moves them to `[version]`

**4. Automate when possible:**
```bash
just release patch  # Preferred over manual
```

**5. Verify after release:**
```bash
pip install mcp-n8n==X.Y.Z  # Test in clean env
```

**6. Keep stable config ready:**
- Always maintain stable server entry in MCP config
- Comment out, don't delete
- Quick rollback if dev breaks

### ❌ DON'T

**1. Don't skip pre-merge checks:**
```bash
# ❌ BAD
just build && just publish-prod  # No testing!

# ✅ GOOD
just pre-merge && just release patch
```

**2. Don't release with uncommitted changes:**
```bash
# ❌ BAD
git status  # Shows modified files
just release patch  # Will fail

# ✅ GOOD
git status  # Clean
just release patch
```

**3. Don't manually edit version:**
```bash
# ❌ BAD
vim pyproject.toml  # Edit version by hand

# ✅ GOOD
just bump-patch  # Automated bump
```

**4. Don't release on broken CI:**
- Fix CI first
- Never force-push to skip CI

**5. Don't delete PyPI releases:**
- Use `twine yank` instead
- Cannot delete, only hide

**6. Don't stay on broken dev:**
- Rollback if blocked >15 minutes
- Debug later when not blocked

---

## Post-Release Tasks

### 1. Announce Release

- [ ] Update project documentation site
- [ ] Post to relevant communities
- [ ] Update dependent projects
- [ ] Send notifications to stakeholders

### 2. Start Next Development Cycle

```bash
# Verify CHANGELOG has [Unreleased] section
grep "## \[Unreleased\]" CHANGELOG.md

# Plan next version
# - Review roadmap
# - Create GitHub milestones
# - Update project board
```

### 3. Monitor for Issues

```bash
# Watch GitHub issues
gh issue list

# Monitor PyPI download stats
# https://pypistats.org/packages/mcp-n8n
```

---

## Release Automation Summary

**Comparison:**

| Approach | Time | Commands | CI Required | Review Step |
|----------|------|----------|-------------|-------------|
| **Automated** | ~5 min | 1 | Yes | No |
| **Manual Review** | ~10 min | 3 | Yes | Yes |
| **Legacy Manual** | ~20 min | 7+ | No | Manual |

**Recommended workflow:**
1. **Routine releases:** `just release patch` (Approach 1)
2. **Major releases:** `just release-draft major` → review → push (Approach 2)
3. **CI broken:** Legacy manual (Approach 3)

**Time savings:**
- Before automation: 15-20 minutes, 6+ manual commands
- After automation: 5 minutes, 1 command
- **83% reduction in steps!**

---

## Resources

- **[Semantic Versioning](https://semver.org/)** - Version numbering
- **[Keep a Changelog](https://keepachangelog.com/)** - CHANGELOG format
- **[Python Packaging Guide](https://packaging.python.org/)** - Official guide
- **[PyPI Help](https://pypi.org/help/)** - PyPI documentation
- **[Twine Documentation](https://twine.readthedocs.io/)** - Upload tool
- **[GitHub Actions](https://docs.github.com/en/actions)** - CI/CD platform

---

**Source Files:**
- [docs/RELEASE_CHECKLIST.md](../docs/RELEASE_CHECKLIST.md)
- [docs/ROLLBACK_PROCEDURE.md](../docs/ROLLBACK_PROCEDURE.md)
- [scripts/prepare-release.sh](../scripts/prepare-release.sh)
- [.github/workflows/release.yml](../.github/workflows/release.yml)

**Last Updated:** 2025-10-21
