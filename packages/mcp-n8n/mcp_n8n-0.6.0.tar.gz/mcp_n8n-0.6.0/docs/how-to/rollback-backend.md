# Rollback Procedure

**Version:** 1.0
**Last Updated:** 2025-10-17
**Purpose:** Quick recovery from dev backend issues

---

## When to Rollback

Rollback from dev to stable backend when:

- ✅ Dev backend is broken or unresponsive
- ✅ Critical bug discovered in dev code
- ✅ Need stable environment for important work
- ✅ Integration tests failing repeatedly
- ✅ Can't debug issue quickly (>15 minutes stuck)
- ✅ Demo or presentation coming up

**Rule of thumb:** If you're blocked for >15 minutes, rollback and debug later.

---

## Quick Rollback (< 1 minute)

### Automated Script (Recommended)

```bash
just rollback
```

This script will:
1. Backup your current MCP config
2. Guide you through switching to stable
3. Verify stable backend works
4. Show next steps

### Manual Rollback (If Script Fails)

**For Claude Desktop (macOS):**

```bash
# 1. Open config file
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 2. Find and comment out dev server:
# "mcp-n8n-dev": { ... }  →  // "mcp-n8n-dev": { ... }

# 3. Uncomment stable server:
# // "mcp-n8n": { ... }  →  "mcp-n8n": { ... }

# 4. Save file

# 5. Restart Claude Desktop
# Quit completely (Cmd+Q) and reopen

# 6. Verify
just verify-stable
```

**For Cursor:**

```bash
# 1. Open config file
code ~/.cursor/mcp.json

# 2. Follow same comment/uncomment steps as above

# 3. Reload window
# Cmd+Shift+P → "Developer: Reload Window"

# 4. Verify
just verify-stable
```

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

---

## Verification Steps

After rollback, verify stable works:

```bash
# Run automated verification
just verify-stable

# This checks:
# 1. mcp-n8n package is installed
# 2. Environment variables are set
# 3. Smoke tests pass
```

### Manual Verification (If Needed)

1. **Test basic tool call:**
   - Open Claude Desktop or Cursor
   - Try: "List available chora generators"
   - Should respond without errors

2. **Check logs:**
   ```bash
   tail -f logs/mcp-n8n.log
   # Should show successful tool calls
   ```

3. **Test both backends:**
   - Chora: "Generate a test document with chora"
   - Coda: "List my Coda documents"

---

## Post-Rollback Actions

### 1. Document What Broke

Add to `KNOWN_ISSUES.md`:

```markdown
### [SEVERITY] Brief description

**Status:** Open
**Affects:** Dev mode
**Discovered:** YYYY-MM-DD

**Description:**
What broke?

**Reproduction:**
1. Steps to reproduce
2. Expected vs actual behavior

**Workaround:**
Rolled back to stable for now.

**Next Steps:**
- [ ] Debug root cause
- [ ] Fix issue
- [ ] Test fix
- [ ] Switch back to dev
```

### 2. Create GitHub Issue (If Needed)

```bash
# If issue is significant, create GitHub issue:
gh issue create --title "Dev backend: <brief description>" \
  --body "See KNOWN_ISSUES.md for details"
```

### 3. Don't Switch Back Until Fixed

**Important:** Don't switch back to dev until:
- ✅ Root cause identified
- ✅ Fix implemented
- ✅ Smoke tests pass
- ✅ Integration test passes

---

## Rollback Scenarios & Solutions

### Scenario 1: Dev Backend Won't Start

**Symptoms:**
- MCP client shows "Connection failed"
- No tools appear
- Logs show "Backend not found"

**Quick Fix:**
```bash
just rollback
```

**Root Cause:**
- Wrong path in config
- Missing venv
- Import errors

### Scenario 2: Dev Backend Slow/Hanging

**Symptoms:**
- Tool calls timeout
- Long response times (>30s)
- Claude/Cursor becomes unresponsive

**Quick Fix:**
```bash
just rollback
```

**Root Cause:**
- Infinite loop in code
- Deadlock
- Resource exhaustion

### Scenario 3: Wrong Responses

**Symptoms:**
- Tools return unexpected data
- Errors in responses
- Missing fields

**Quick Fix:**
```bash
just rollback
```

**Root Cause:**
- Logic bug
- Schema mismatch
- Integration issue

### Scenario 4: Can't Edit Config

**Symptoms:**
- Config file locked
- Permission denied
- JSON syntax error

**Solution:**
```bash
# Backup first
cp "$HOME/Library/Application Support/Claude/claude_desktop_config.json" \
   /tmp/config_backup.json

# Use example config
cp .config/claude-desktop.example.json \
   "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Edit with proper JSON
# Then restart Claude
```

---

## Rollback Safety

### What Rollback Does

✅ **SAFE** - No data loss:
- Backs up current config
- Switches MCP server entry
- Verifies stable works

✅ **SAFE** - No code changes:
- Dev code remains untouched
- Can switch back anytime
- Git state unchanged

✅ **SAFE** - No API impact:
- Same API keys used
- Same backends available
- Just routing changes

### What Rollback Doesn't Do

❌ Does NOT:
- Delete dev code
- Uninstall dev environment
- Lose work-in-progress
- Affect other projects

---

## Recovery Time

| Scenario | Time to Stable |
|----------|----------------|
| Automated rollback | < 1 minute |
| Manual rollback | 2-3 minutes |
| With verification | 3-5 minutes |
| Worst case (config rebuild) | 5-10 minutes |

**Goal:** Back to working state in <5 minutes, 95% of the time.

---

## Prevention

### Avoid Rollback by:

1. **Test before switching:**
   ```bash
   just smoke    # Quick validation
   just test     # Full test suite
   ```

2. **Use feature branches:**
   ```bash
   git checkout -b feature/new-thing
   # Test thoroughly before merging
   ```

3. **Small changes:**
   - Make incremental changes
   - Test after each change
   - Easy to identify what broke

4. **Keep stable config ready:**
   - Always have stable config in comments
   - Don't delete stable server entry
   - Quick to uncomment and rollback

---

## Emergency Contacts

**For single-developer workflow:**

- **Primary:** You (this is a self-recovery procedure)
- **Documentation:** See `.config/README.md` for config help
- **Troubleshooting:** See `docs/TROUBLESHOOTING.md` (Phase 4)
- **GitHub Issues:** https://github.com/yourusername/mcp-n8n/issues

---

## See Also

- [Configuration Management](.config/README.md) - Dual config setup
- [Dev vs Stable Guide](.config/dev-vs-stable.md) - Toggle details
- [Quick Reference](QUICK_REFERENCE.md) - Common commands (Phase 4)
- [Known Issues](../KNOWN_ISSUES.md) - Documented problems

---

## Version History

- **v1.0** (2025-10-17): Initial rollback procedure
  - Automated script
  - Manual fallback
  - Decision tree
  - Verification steps
