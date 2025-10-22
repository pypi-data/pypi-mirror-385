# Known Issues

**Purpose:** Track known problems, workarounds, and resolution status.

**Note:** This registry helps maintain awareness of ongoing issues and prevents duplicate debugging efforts. Update this file whenever you discover, workaround, or resolve an issue.

---

## Issue Template

When adding a new issue, use this format:

```markdown
### [SEVERITY] Brief description

**Status:** Open | In Progress | Resolved
**Affects:** Component/feature name
**Discovered:** YYYY-MM-DD
**Resolved:** YYYY-MM-DD (if resolved)

**Description:**
Detailed description of the issue.

**Reproduction:**
1. Step-by-step reproduction
2. Expected behavior
3. Actual behavior

**Workaround:**
Temporary solution or mitigation steps.

**Root Cause:**
Technical explanation (if known).

**Resolution:**
How it was fixed (if resolved).

**Next Steps:**
- [ ] Action item 1
- [ ] Action item 2
```

**Severity Levels:**
- `[CRITICAL]` - System unusable, data loss, security issue
- `[HIGH]` - Major functionality broken, no workaround
- `[MEDIUM]` - Functionality impaired, workaround exists
- `[LOW]` - Minor inconvenience, cosmetic issue
- `[INFO]` - Not a bug, but important to document

---

## Current Issues

### [INFO] No known issues at this time

**Status:** N/A
**Discovered:** 2025-10-17

The project is currently in its initial implementation phase. As issues are discovered during development and testing, they will be documented here.

**Guidelines for reporting:**
- Document all issues that block development or testing
- Include reproduction steps and error messages
- Note any workarounds discovered
- Update status as work progresses
- Move resolved issues to "Resolved Issues" section below

---

## Resolved Issues

*No resolved issues yet.*

When issues are resolved, move them to this section with:
- Resolution date
- How it was fixed
- Link to commit/PR if applicable

---

## See Also

- [Rollback Procedure](docs/ROLLBACK_PROCEDURE.md) - Recovery from dev backend issues
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common problems (Phase 4)
- [GitHub Issues](https://github.com/yourusername/mcp-n8n/issues) - Public issue tracker

---

## Maintenance

- **Review frequency:** Weekly (or when blocked by an issue)
- **Cleanup policy:** Move resolved issues older than 90 days to archive
- **Escalation:** Create GitHub issue for problems requiring external help

**Last reviewed:** 2025-10-17
