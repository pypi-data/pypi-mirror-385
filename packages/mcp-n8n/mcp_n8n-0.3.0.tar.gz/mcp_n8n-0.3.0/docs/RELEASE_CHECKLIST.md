# Release Checklist

**Purpose:** Step-by-step guide for releasing a new version of mcp-n8n to PyPI.

This checklist ensures all critical steps are completed for a safe, successful release.

---

## Pre-Release Validation

### 1. Environment Check
Ensure your development environment is ready:

```bash
# Verify environment is healthy
just check-env

# Ensure no uncommitted changes
git status

# Ensure you're on the main branch
git branch --show-current

# Pull latest changes
git pull origin main
```

**Expected:** Clean working directory, up-to-date main branch.

---

### 2. Code Quality Verification

Run all verification checks:

```bash
# Pre-merge verification (includes all tests, linting, coverage)
just pre-merge
```

**Expected:** All checks pass with ≥85% coverage.

**If checks fail:**
- Fix issues before proceeding
- Run `just pre-merge` again until clean
- Do not proceed with release if checks fail

---

### 3. Documentation Review

Verify documentation is current:

- [ ] README.md reflects current features
- [ ] CHANGELOG.md has entries in [Unreleased] section
- [ ] API documentation is up-to-date (if applicable)
- [ ] Configuration examples are accurate

---

## Version & CHANGELOG

### 4. Determine Version Bump

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.X.0): New features, backward-compatible
- **PATCH** (0.0.X): Bug fixes, backward-compatible

**Examples:**
- Adding new MCP backend → MINOR
- Fixing routing bug → PATCH
- Changing configuration format → MAJOR

---

### 5. Prepare Release

Use automated release preparation:

```bash
# For patch release (0.1.0 → 0.1.1)
just prepare-release patch

# For minor release (0.1.0 → 0.2.0)
just prepare-release minor

# For major release (0.1.0 → 1.0.0)
just prepare-release major
```

This script will:
1. Bump version in `pyproject.toml`
2. Update `CHANGELOG.md` (move [Unreleased] → [version])
3. Run pre-merge checks
4. Create release commit

**Expected:** Release commit created with updated version and CHANGELOG.

**If script fails:**
- Review error messages
- Fix issues (usually CHANGELOG or test failures)
- Rollback: `git reset --hard HEAD~1`
- Try again

---

### 6. Review Release Commit

Inspect the automated commit:

```bash
# View the release commit
git show HEAD

# Check version was bumped correctly
grep "^version = " pyproject.toml

# Check CHANGELOG was updated correctly
grep -A 10 "## \[" CHANGELOG.md | head -20
```

**Expected:**
- Version in `pyproject.toml` matches intention
- CHANGELOG has new version section with date
- Commit message follows format

---

## Build & Test

### 7. Build Distribution Packages

```bash
# Build wheel and source distribution
just build
```

**Expected:**
- Creates `dist/mcp_n8n-X.Y.Z-py3-none-any.whl`
- Creates `dist/mcp-n8n-X.Y.Z.tar.gz`
- Twine check passes

**If build fails:**
- Review error messages
- Fix issues in `pyproject.toml` or source code
- Clean and rebuild: `just clean && just build`

---

### 8. Test on TestPyPI (Recommended)

Publish to TestPyPI first to validate:

```bash
# Upload to TestPyPI
just publish-test
```

**Expected:** Package uploaded to test.pypi.org

**Then test installation:**

```bash
# Create clean test environment
python -m venv test-install
source test-install/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  mcp-n8n==X.Y.Z

# Test the package
mcp-n8n --help

# Test basic functionality
# (Add project-specific smoke tests here)

# Cleanup
deactivate
rm -rf test-install
```

**Expected:** Package installs and runs correctly.

**If installation fails:**
- Check dependencies in `pyproject.toml`
- Verify version number
- Fix and rebuild: `just build`

---

## Production Release

### 9. Publish to PyPI

**⚠️ WARNING: This step is IRREVERSIBLE. Double-check everything!**

```bash
# Final check before publishing
git log -1
grep "^version = " pyproject.toml

# Publish to production PyPI
just publish-prod
```

You will be prompted for confirmation. Type `yes` to proceed.

This script will:
1. Upload to pypi.org
2. Create git tag `vX.Y.Z`
3. Push tag to remote

**Expected:**
- Package on PyPI: https://pypi.org/project/mcp-n8n/
- Git tag created and pushed

**If upload fails:**
- Review error (likely credentials or existing version)
- Fix issue and try `just publish-prod` again
- Tag is only created after successful upload

---

### 10. Verify Production Release

```bash
# Create clean environment
python -m venv verify-release
source verify-release/bin/activate

# Install from PyPI (production)
pip install mcp-n8n==X.Y.Z

# Verify installation
mcp-n8n --help
pip show mcp-n8n

# Cleanup
deactivate
rm -rf verify-release
```

**Expected:** Package installs from PyPI without issues.

---

## Post-Release Tasks

### 11. Create GitHub Release (Optional)

If using GitHub:

1. Go to: https://github.com/yourusername/mcp-n8n/releases
2. Click "Draft a new release"
3. Select tag: `vX.Y.Z`
4. Title: `vX.Y.Z - Brief description`
5. Body: Copy from CHANGELOG.md
6. Attach distribution files (optional)
7. Publish release

---

### 12. Update Stable Configuration

If you use stable/dev dual configuration:

```bash
# Update your stable MCP config to use new version
# See: .config/dev-vs-stable.md

# Verify stable works
just verify-stable
```

---

### 13. Announce Release

Communicate the release:

- [ ] Update project documentation site
- [ ] Post to relevant communities (Discord, forums, etc.)
- [ ] Update dependent projects
- [ ] Send notifications to stakeholders
- [ ] Update social media (if applicable)

---

### 14. Start Next Development Cycle

Prepare for next version:

```bash
# Ensure CHANGELOG has [Unreleased] section
# (prepare-release.sh should have added this)
grep "## \[Unreleased\]" CHANGELOG.md

# Push release commit if not already pushed
git push origin main
```

**Plan next version:**
- Review roadmap
- Create GitHub milestones
- Update project board
- Document known issues

---

## Rollback Procedure

If you need to yank a release:

### PyPI Release (Cannot Delete, Can Yank)

```bash
# Yank the release (hides from pip install)
pip install twine
twine yank <package-name> <version>

# Example:
twine yank mcp-n8n 0.2.0 --reason "Critical bug in routing"
```

**Note:** Yanked releases remain visible but pip won't install by default.

### Git Tag Rollback

```bash
# Delete local tag
git tag -d vX.Y.Z

# Delete remote tag
git push origin :refs/tags/vX.Y.Z

# Revert release commit
git revert HEAD
git push origin main
```

---

## Release Automation Summary

**Automated commands:**
- `just prepare-release <type>` - Bump version, update CHANGELOG, commit
- `just build` - Build distribution packages
- `just publish-test` - Upload to TestPyPI
- `just publish-prod` - Upload to PyPI, create tag, push

**Manual steps:**
- Pre-release validation
- Documentation review
- TestPyPI testing
- Post-release communication

---

## Checklist Summary

Use this quick checklist for releases:

- [ ] 1. Clean environment (`just check-env`, `git status`)
- [ ] 2. All tests pass (`just pre-merge`)
- [ ] 3. Documentation updated (README, CHANGELOG)
- [ ] 4. Version bumped (`just prepare-release <type>`)
- [ ] 5. Reviewed release commit (`git show HEAD`)
- [ ] 6. Built packages (`just build`)
- [ ] 7. Tested on TestPyPI (`just publish-test`)
- [ ] 8. Verified TestPyPI installation
- [ ] 9. Published to PyPI (`just publish-prod`)
- [ ] 10. Verified PyPI installation
- [ ] 11. Created GitHub release (optional)
- [ ] 12. Updated stable config
- [ ] 13. Announced release
- [ ] 14. Started next cycle

---

## Common Issues

### Issue: "Version already exists on PyPI"
**Solution:** You cannot overwrite. Bump to a new version and release again.

### Issue: "Twine upload failed - Invalid credentials"
**Solution:** Configure `~/.pypirc` with API token or set `TWINE_PASSWORD` env var.

### Issue: "Pre-merge checks fail"
**Solution:** Fix issues before releasing. Do not skip validation.

### Issue: "Git tag already exists"
**Solution:** Delete tag or bump version higher than existing tag.

### Issue: "Package installed but command not found"
**Solution:** Check `[project.scripts]` in `pyproject.toml` and rebuild.

---

## Resources

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)

---

**Last updated:** 2025-10-17
