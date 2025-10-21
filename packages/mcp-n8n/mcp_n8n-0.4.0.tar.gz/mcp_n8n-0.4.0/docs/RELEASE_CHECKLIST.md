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

### 5. Release (Automated - Recommended)

**NEW: Single-command automated release!** 🚀

```bash
# For patch release (0.1.0 → 0.1.1)
just release patch

# For minor release (0.1.0 → 0.2.0)
just release minor

# For major release (0.1.0 → 1.0.0)
just release major
```

This **fully automated** command will:
1. Bump version in `pyproject.toml`
2. Update `CHANGELOG.md` (move [Unreleased] → [version])
3. Run pre-merge checks (tests, linting, coverage)
4. Create release commit
5. **Create git tag** `vX.Y.Z`
6. **Push commit and tag to GitHub**

Then **GitHub Actions automatically**:
- Builds distribution packages (wheel + tarball)
- Runs tests on Python 3.12
- Publishes to PyPI
- Creates GitHub release with CHANGELOG notes

**Expected:** Complete release in ~5 minutes (mostly CI wait time).

**If script fails:**
- Review error messages
- Fix issues (usually CHANGELOG or test failures)
- Rollback: `git checkout pyproject.toml CHANGELOG.md`
- Try again

**🎉 That's it! Your release is complete.**

---

### 5a. Release (Manual Review Mode)

**Prefer to review before pushing?** Use draft mode:

```bash
# Prepare release but don't push (for review)
just release-draft patch
```

This will:
1. Bump version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run pre-merge checks
4. Create release commit
5. **Stop** (no tag, no push)

**Then review and push manually:**

```bash
# Review the changes
git show HEAD

# Check version was bumped correctly
grep "^version = " pyproject.toml

# Create tag and push when ready
git tag vX.Y.Z
git push origin main && git push origin vX.Y.Z
```

GitHub Actions will trigger automatically on tag push.

---

## Monitor Release (Automated Mode)

### 6. Monitor GitHub Actions

After running `just release patch`, monitor the automated workflow:

```bash
# Check GitHub Actions status
# https://github.com/YOUR_USERNAME/mcp-n8n/actions
```

**Expected workflow:**
1. **Build** - Creates distribution packages (~1 min)
2. **Test** - Runs full test suite (~2 min)
3. **Publish PyPI** - Uploads to pypi.org (~30 sec)
4. **GitHub Release** - Creates release with CHANGELOG (~30 sec)

**Total time:** ~5 minutes

---

### 7. Verify Production Release

Once GitHub Actions completes:

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

**Verify online:**
- 📦 PyPI: https://pypi.org/project/mcp-n8n/X.Y.Z/
- 🐙 GitHub Release: https://github.com/YOUR_USERNAME/mcp-n8n/releases/tag/vX.Y.Z

---

## Post-Release Tasks

### 8. Create GitHub Release

**Automated mode:** GitHub Actions creates this automatically! ✅

**Manual mode (if needed):**

1. Go to: https://github.com/yourusername/mcp-n8n/releases
2. Click "Draft a new release"
3. Select tag: `vX.Y.Z`
4. Title: `vX.Y.Z - Brief description`
5. Body: Copy from CHANGELOG.md
6. Attach distribution files (optional)
7. Publish release

---

### 9. Update Stable Configuration

If you use stable/dev dual configuration:

```bash
# Update your stable MCP config to use new version
# See: .config/dev-vs-stable.md

# Verify stable works
just verify-stable
```

---

### 10. Announce Release

Communicate the release:

- [ ] Update project documentation site
- [ ] Post to relevant communities (Discord, forums, etc.)
- [ ] Update dependent projects
- [ ] Send notifications to stakeholders
- [ ] Update social media (if applicable)

---

### 11. Start Next Development Cycle

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

**Fully Automated Release (NEW - Recommended):**
- `just release <type>` - **ONE COMMAND** does everything:
  - Bump version, update CHANGELOG, commit
  - Create and push git tag
  - Trigger GitHub Actions (build, test, publish to PyPI, create GitHub release)
  - **Total: ~5 minutes** (mostly CI wait time)

**Manual Review Release:**
- `just release-draft <type>` - Prepare locally without pushing
  - Review changes with `git show HEAD`
  - Push manually when ready: `git push origin main && git push origin vX.Y.Z`

**Legacy Commands (rarely needed):**
- `just build` - Build distribution packages locally
- `just publish-test` - Upload to TestPyPI for testing
- `just publish-prod` - Upload to PyPI manually

**Before/After Comparison:**
- **Before:** 6+ manual commands, ~15-20 minutes
- **After:** 1 command, ~5 minutes (83% reduction in steps!)

---

## Checklist Summary

**Automated Release (Recommended):**

- [ ] 1. Clean environment (`just check-env`, `git status`)
- [ ] 2. All tests pass (`just pre-merge`)
- [ ] 3. Documentation updated (README, CHANGELOG)
- [ ] 4. **Run automated release (`just release <type>`)** 🚀
- [ ] 5. Monitor GitHub Actions (~5 min wait)
- [ ] 6. Verify PyPI installation
- [ ] 7. Update stable config
- [ ] 8. Announce release

**Manual Review Release:**

- [ ] 1-3. Same as above
- [ ] 4. Run draft release (`just release-draft <type>`)
- [ ] 5. Review changes (`git show HEAD`)
- [ ] 6. Push manually (`git push origin main && git push origin vX.Y.Z`)
- [ ] 7-8. Same as automated (steps 5-8)

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

**Last updated:** 2025-10-20 (Automated release workflow added)
