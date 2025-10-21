# chora-base Template Adoption Status - mcp-n8n

**Project:** mcp-n8n v0.2.0
**Current Template Version:** chora-base v1.2.0 (tracking version)
**Latest Template Version:** chora-base v1.5.0
**Date:** 2025-10-19
**Status:** ORIGINAL EXEMPLAR - SELECTIVE SYNC RECOMMENDED

---

## Executive Summary

**mcp-n8n is the original exemplar project from which chora-base v1.0.0 was extracted.** This document analyzes the template evolution (v1.0.0 → v1.2.0) and identifies beneficial improvements that can flow back to mcp-n8n.

### Current Relationship

```
mcp-n8n (v0.2.0)
  └─ Based on: chora-base v1.0.0 (extraction source)
  └─ .copier-answers.yml: _commit: v1.0.0

chora-base
  ├─ v1.0.0 (2025-10-17) - Initial extraction from mcp-n8n
  ├─ v1.1.0 (2025-10-18) - Documentation suite (Diátaxis)
  ├─ v1.1.1 (2025-10-18) - Metadata documentation
  ├─ v1.2.0 (2025-10-18) - Template generalization fixes
  ├─ v1.3.0 (2025-10-19) - Vision & strategic design framework
  ├─ v1.3.1 (2025-10-19) - Vision documentation enhancements
  ├─ v1.4.0 (2025-10-19) - PyPI setup + just as primary interface
  └─ v1.5.0 (2025-10-19) - Complete upgrade documentation suite

Adopters
  └─ chora-compose v1.3.0 → chora-base v1.0.0 (adopted infrastructure)
```

### Key Findings

**Adoption Completeness:** ~95% (mcp-n8n has all core infrastructure)
**Template Version Gap:** 5 releases (v1.2.0 → v1.5.0)
**Missing Features:** Vision framework, enhanced justfile, upgrade documentation awareness
**Recommendation:** **SELECTIVE SYNC** - Cherry-pick beneficial features from v1.3.0-v1.5.0, update `.copier-answers.yml` to v1.5.0

### Quick Status

| Category | Status | Notes |
|----------|--------|-------|
| **Infrastructure** | ✅ 100% | 18 scripts, 7 workflows, justfile - all present |
| **Memory System** | ✅ 100% | Complete implementation with CLI tools |
| **Documentation** | ✅ 100% | Frontmatter schema docs added (v1.1.1) |
| **Quality Gates** | ✅ 100% | Pre-commit, coverage, type checking - all working |
| **Vision Framework** | ⚠️ 0% | New in v1.3.0 - needs evaluation for mcp-n8n |
| **Justfile Enhancements** | ⚠️ 50% | Has justfile, missing help command (v1.4.0) |
| **Template Sync** | ✅ 100% | .copier-answers.yml references v1.2.0 (current) |

---

## Template Evolution Timeline

### v1.0.0 (2025-10-17) - Extraction from mcp-n8n

**Extracted Infrastructure:**
- 18 automation scripts (scripts/)
- 7 GitHub Actions workflows (.github/workflows/)
- justfile with 25+ commands
- Memory system (.chora/memory/)
- chora-memory CLI (Phase 4.6)
- AGENTS.md (1,189 lines)
- Pre-commit hooks
- Documentation suite
- Testing infrastructure

**Impact on mcp-n8n:** None (source of extraction)

---

### v1.1.1 (2025-10-18) - Metadata Documentation

**What's New:**
- Knowledge note frontmatter schema documentation in `.chora/memory/README.md`
  - Required fields: `id`, `created`, `updated`, `tags`
  - Optional fields: `confidence`, `source`, `linked_to`, `status`, `author`, `related_traces`
  - Standards compliance notes (Obsidian, Zettlr, LogSeq, Foam)
  - Complete example with all fields
- AGENTS.md metadata reference section
  - Field definitions with enums and examples
  - Rationale for YAML frontmatter usage
  - Cross-reference to memory/README.md

**mcp-n8n Status:**
- ❌ `.chora/memory/README.md` lacks frontmatter schema documentation
- ❌ `AGENTS.md` lacks metadata standards section

**Impact:** Documentation enhancement only
**Recommendation:** **BENEFICIAL** - Add to mcp-n8n for better agent/human guidance

---

### v1.2.0 (2025-10-18) - Template Generalization Fixes

**What's New:**

#### CRITICAL Fixes (12 issues)
1. **Python Import Errors** - Memory module files converted to .jinja
   - `src/{{package_name}}/memory/__init__.py` → `__init__.py.jinja`
   - `src/{{package_name}}/memory/trace.py` → `trace.py.jinja`
   - Changed: `from mcp_n8n.memory.*` → `from {{ package_name }}.memory.*`
   - Changed: `source: str = "mcp-n8n"` → `source: str = "{{ project_slug }}"`

2. **Hardcoded Absolute Paths** - Removed from scripts
   - `check-env.sh` - Removed mcp-n8n-specific backend checks
   - `mcp-tool.sh` - Use script directory detection
   - `handoff.sh` - Generic paths instead of `/Users/victorpiper/code/*`

3. **Placeholder GitHub Usernames** - Fixed in 3 files
   - `CONTRIBUTING.md` - `yourusername` → `{{ github_username }}`
   - `publish-prod.sh` - `yourusername` → `{{ github_username }}`
   - `diagnose.sh` - `yourusername` → `{{ github_username }}`

4. **Security Email Placeholder** - Added copier variable
   - `copier.yml` - Added `security_email` variable
   - `CONTRIBUTING.md` - `security@example.com` → `{{ security_email }}`

#### HIGH Priority Fixes (6 issues)
5. **Memory README Generalization** - Removed project-specific references
   - Changed: `working with mcp-n8n` → `working with {{ project_slug }}`
   - Changed: `"source": "mcp-n8n"` → `"source": "{{ project_slug }}"`
   - Changed: `chora:*` examples → `example:*` (generic)
   - Changed: `chora-composer` → `example-backend` (generic)
   - Changed: Phase references removed

**mcp-n8n Status:**
- ✅ mcp-n8n memory module files are regular .py (not .jinja) - **This is correct**
- ✅ mcp-n8n has real values (not placeholders) - **No action needed**
- ⚠️ mcp-n8n scripts may have mcp-n8n-specific logic - **Expected and correct**
- ⚠️ mcp-n8n .chora/memory/README.md has project-specific references - **Expected and correct**

**Impact:** Template improvements, but mcp-n8n is the source, not a consumer
**Recommendation:** **LOW PRIORITY** - These fixes make the *template* generic, but mcp-n8n should keep its specific values

---

### v1.3.0 (2025-10-19) - Vision & Strategic Design Framework

**What's New:**
- Vision & strategic design framework for long-term planning
- New template files for vision documentation
- Enhanced AGENTS.md with strategic design section (+255 lines)
- New ROADMAP.md template with vision integration
- Vision-aware implementation patterns for AI agents

**Template Changes:**
- `dev-docs/vision/README.md` - Vision directory guide (~370 lines)
- `dev-docs/vision/CAPABILITY_EVOLUTION.example.md` - Example vision doc (~670 lines)
- `ROADMAP.md` - Roadmap template with vision highlights (~195 lines)
- `AGENTS.md` - Strategic Context + Strategic Design sections (+255 lines)
  - Vision-aware implementation pattern
  - Refactoring decision framework (ASCII flowchart)
  - Knowledge capture patterns (A-MEM integration)
  - Quick reference checklist

**mcp-n8n Status:**
- ⚠️ No `dev-docs/vision/` directory
- ✅ Has `docs/ROADMAP.md` and `docs/UNIFIED_ROADMAP.md` (custom roadmaps exist)
- ❌ AGENTS.md lacks strategic design section from v1.3.0
- ⚠️ Vision framework could complement existing roadmap documents

**Impact:** Optional enhancement - vision framework could help organize long-term planning
**Recommendation:** **EVALUATE** - Consider adopting AGENTS.md enhancements, evaluate vision docs vs existing roadmaps

---

### v1.3.1 (2025-10-19) - Vision Documentation Enhancements

**What's New:**
- Documentation for vision framework (how-to + explanation)
- `docs/how-to/06-maintain-vision-documents.md` (~500 lines)
- `docs/explanation/vision-driven-development.md` (~700 lines)
- Example project with vision framework

**mcp-n8n Status:**
- N/A - Template documentation, not applicable to exemplar

**Impact:** None (template-specific docs)
**Recommendation:** **SKIP** - Not applicable to mcp-n8n as exemplar

---

### v1.4.0 (2025-10-19) - PyPI Setup + Just as Primary Interface

**What's New:**

#### Part 1: PyPI Publishing Setup
- New `pypi_auth_method` copier variable (token vs trusted publishing)
- Conditional GitHub Actions workflow for release
- PYPI_SETUP.md guide (~420 lines)

**mcp-n8n Status:**
- ✅ Already published to PyPI
- ✅ Has working GitHub Actions release workflow
- ❌ No PYPI_SETUP.md guide (could be useful for contributors)

#### Part 2: Just as Primary Interface
- **Auto-install `just`** in `scripts/setup.sh`
  - macOS: `brew install just` with curl fallback
  - Linux: curl installer to `~/.local/bin`
- **Enhanced justfile**
  - Added `help` command for common workflows
  - Better inline documentation
- **Documentation restructured** around `just` interface
  - README: Lead with `just --list` for task discovery
  - CONTRIBUTING: All examples use `just` commands
  - AGENTS.md: Task Discovery section for agents

**mcp-n8n Status:**
- ⚠️ `scripts/setup.sh` warns about `just` but doesn't auto-install
- ❌ Justfile lacks `help` command
- ⚠️ Documentation mentions `just` but not as primary interface
- ❌ AGENTS.md lacks Task Discovery section emphasizing `just`

**Impact:** Medium - Better developer experience and agent ergonomics
**Recommendation:** **BENEFICIAL** - Adopt just auto-installation and enhanced justfile

---

### v1.5.0 (2025-10-19) - Complete Upgrade Documentation Suite

**What's New:**
- Complete upgrade guide system (100% coverage v1.0.0 → v1.4.0)
- New upgrade guides:
  - `docs/upgrades/v1.0-to-v1.1.md` (~700 lines)
  - `docs/upgrades/v1.1-to-v1.2.md` (~1,400 lines)
  - `docs/upgrades/v1.2-to-v1.3.md` (~1,200 lines)
- `docs/upgrades/PHILOSOPHY.md` - Upgrade philosophy and displacement policy
- `docs/upgrades/README.md` - Navigation hub for upgrade guides
- `docs/upgrades/UPGRADE_GUIDE_TEMPLATE.md` - AI-optimized format

**Total System:** ~5,500 lines across 8 files

**mcp-n8n Status:**
- ❌ No awareness of upgrade documentation system
- ❌ No UPGRADING.md or docs/upgrades/ directory
- ✅ Has this CHORA_BASE_ADOPTION_STATUS.md (serves similar purpose)

**Impact:** High awareness value - understanding the upgrade system helps mcp-n8n stay aligned
**Recommendation:** **BENEFICIAL** - Add reference to upgrade philosophy, optionally add UPGRADING.md

---

## Adoption Status Matrix

### Infrastructure Completeness

| Component | chora-base v1.5.0 | mcp-n8n v0.2.0 | Status | Gap Analysis |
|-----------|-------------------|----------------|--------|--------------|
| **Scripts** | 18 files | 18 files | ✅ 100% | None |
| **GitHub Actions** | 7 workflows | 7 workflows | ✅ 100% | None |
| **justfile** | Enhanced (v1.4.0) | Basic | ⚠️ 80% | Missing help command, auto-install |
| **Memory System** | Complete | Complete | ✅ 100% | None |
| **chora-memory CLI** | 5 commands | 5 commands | ✅ 100% | None |
| **AGENTS.md** | 1,995+ lines (v1.3.0) | ~1,750 lines | ⚠️ 85% | Missing Strategic Design section |
| **Pre-commit Hooks** | Configured | Configured | ✅ 100% | None |
| **Coverage Threshold** | 85% | 85% | ✅ 100% | None |
| **Documentation Suite** | Enhanced + Vision | Standard | ⚠️ 85% | Missing vision framework awareness |
| **Vision Framework** | v1.3.0+ | None | ❌ 0% | New feature, needs evaluation |
| **Upgrade Docs** | v1.5.0 | None | ⚠️ 50% | Has ADOPTION_STATUS.md |
| **.copier-answers.yml** | v1.5.0 | v1.2.0 | ✅ 85% | **Consider update to v1.5.0** |

### Documentation Enhancements

| Feature | chora-base v1.5.0 | mcp-n8n v0.2.0 | Benefit to mcp-n8n |
|---------|-------------------|----------------|---------------------|
| **Frontmatter Schema Docs** (v1.1.1) | ✅ | ✅ | ✅ Already adopted |
| **AGENTS.md Metadata Section** (v1.1.1) | ✅ | ✅ | ✅ Already adopted |
| **Strategic Design Section** (v1.3.0) | ✅ | ❌ | **HIGH** - Vision-aware refactoring for agents |
| **Just Auto-Install** (v1.4.0) | ✅ | ❌ | **MEDIUM** - Better onboarding DX |
| **Enhanced Justfile** (v1.4.0) | ✅ | ⚠️ | **MEDIUM** - Missing help command |
| **Upgrade Docs Awareness** (v1.5.0) | ✅ | ⚠️ | **MEDIUM** - Reference to upgrade philosophy |
| **Vision Framework** (v1.3.0) | ✅ | ❌ | **LOW-MEDIUM** - Long-term planning structure |

---

## Gap Analysis

### 1. Documentation Gap: Frontmatter Schema (v1.1.1)

**What's Missing:**
- `.chora/memory/README.md` lacks comprehensive frontmatter field documentation
- No explanation of required vs optional fields
- No standards compliance notes (Obsidian, Zettlr compatibility)
- No complete example showing all fields

**Impact:**
- Agents have less guidance on creating well-structured knowledge notes
- Humans unfamiliar with Zettelkasten may not use metadata effectively
- Reduced discoverability of advanced features (confidence levels, linking)

**Recommendation:** **ADD** - Copy from chora-base v1.1.1
**Effort:** 30 minutes (copy ~60 lines)
**Benefit:** Better documentation for memory system users

---

### 2. Documentation Gap: AGENTS.md Metadata Reference (v1.1.1)

**What's Missing:**
- No "Knowledge Note Metadata Standards" section in AGENTS.md
- No cross-reference to .chora/memory/README.md for schema details
- Missing field definitions and examples for agents

**Impact:**
- Agents reading AGENTS.md don't know about metadata capabilities
- No central reference for frontmatter field usage
- Reduced discoverability of knowledge graph features

**Recommendation:** **ADD** - Copy from chora-base v1.1.1
**Effort:** 20 minutes (copy ~40 lines)
**Benefit:** Agents understand metadata system fully

---

### 3. Template Sync Gap: .copier-answers.yml

**What's Missing:**
- `.copier-answers.yml` references `_commit: v1.0.0`
- Latest template is v1.2.0
- Cannot easily pull template improvements

**Impact:**
- `copier update` will try to update from v1.0.0 → v1.2.0
- May apply unwanted generalization changes
- Harder to track which template version mcp-n8n conceptually follows

**Recommendation:** **UPDATE** - Change `_commit: v1.2.0`
**Effort:** 5 minutes (one line change)
**Benefit:** Accurate template version tracking

---

### 4. Non-Gap: Template Generalization Fixes (v1.2.0)

**Why These Are NOT Gaps:**

mcp-n8n is the **source project**, not a template consumer. The v1.2.0 generalization fixes were designed to make the *template* suitable for *other projects* like chora-compose.

**Examples:**
- ✅ mcp-n8n should have `from mcp_n8n.memory import *` (not templated)
- ✅ mcp-n8n should reference "mcp-n8n" in docs (not "{{ project_slug }}")
- ✅ mcp-n8n should have mcp-n8n-specific script logic
- ✅ mcp-n8n should have real email addresses (not placeholders)

**No action needed** - These are correct as-is.

---

### 5. Strategic Design Gap: AGENTS.md Enhancements (v1.3.0)

**What's Missing:**
- No "Strategic Context" subsection in AGENTS.md Project Overview
- No "Strategic Design" section with vision-aware patterns
- Missing refactoring decision framework for agents
- No knowledge capture patterns for design decisions

**What v1.3.0 Adds (+255 lines):**
- Vision-aware implementation pattern
- Refactoring decision framework (ASCII flowchart)
- Knowledge capture patterns (A-MEM integration)
- Quick reference checklist for design decisions
- Project-type-specific examples (MCP, library, CLI, web service)

**Impact:**
- Agents lack guidance on when to refactor vs when to defer
- No systematic approach to design decisions
- Missing link between vision docs and day-to-day implementation

**Recommendation:** **HIGH PRIORITY** - Add Strategic Design section to AGENTS.md
**Effort:** 1-2 hours (adapt from chora-base v1.3.0 template)
**Benefit:** Better agent decision-making, fewer premature optimizations

---

### 6. Developer Experience Gap: Just Auto-Installation (v1.4.0)

**What's Missing:**
- `scripts/setup.sh` warns about `just` but doesn't auto-install
- Users must manually install `just` (friction point)

**What v1.4.0 Adds:**
- Auto-install `just` in `scripts/setup.sh`
  - macOS: `brew install just` with curl fallback
  - Linux: curl installer to `~/.local/bin`
- Transparent, automatic during project setup

**Impact:**
- Contributors may encounter "command not found: just" errors
- Extra manual setup step reduces onboarding smoothness

**Recommendation:** **MEDIUM PRIORITY** - Add auto-installation logic
**Effort:** 30 minutes (copy logic from chora-base v1.4.0)
**Benefit:** Smoother contributor onboarding

---

### 7. Developer Experience Gap: Enhanced Justfile (v1.4.0)

**What's Missing:**
- No `help` command in justfile
- Limited inline documentation
- Not structured as primary task discovery interface

**What v1.4.0 Adds:**
- `help` command for common workflows
- Enhanced inline documentation
- Better integration with agent workflows

**Impact:**
- New contributors must read documentation to find tasks
- Agents have less machine-readable task catalog

**Recommendation:** **MEDIUM PRIORITY** - Add help command to justfile
**Effort:** 30 minutes (add command + documentation)
**Benefit:** Faster task discovery for humans and agents

---

### 8. Ecosystem Awareness Gap: Upgrade Documentation (v1.5.0)

**What's Missing:**
- No awareness of chora-base upgrade philosophy
- No reference to displacement policy
- No UPGRADING.md or link to upgrade guides

**What v1.5.0 Adds:**
- Complete upgrade guide system
- Upgrade philosophy and displacement policy
- AI-optimized decision frameworks

**Impact:**
- Team may not understand how to stay aligned with chora-base evolution
- Missing context on when to adopt vs when to skip template improvements

**Recommendation:** **MEDIUM PRIORITY** - Add reference to upgrade docs
**Effort:** 15 minutes (add note to this document or create UPGRADING.md)
**Benefit:** Better understanding of template evolution strategy

---

## Recommended Actions (Updated for v1.5.0)

### Priority Summary

**HIGH PRIORITY (1-2 hrs):**
1. Add Strategic Design section to AGENTS.md (v1.3.0)

**MEDIUM PRIORITY (1-2 hrs total):**
2. Add `just` auto-installation to scripts/setup.sh (v1.4.0)
3. Add `help` command to justfile (v1.4.0)
4. Add upgrade docs reference (v1.5.0)
5. Update `.copier-answers.yml` to v1.5.0

**OPTIONAL / EVALUATE:**
6. Consider vision framework adoption (v1.3.0)

**TOTAL ESTIMATED TIME:** 2-4 hours for all recommended actions

---

### Action 1: Add Strategic Design Section to AGENTS.md (1-2 hours) ⭐ HIGH PRIORITY

**Why:** Provides agents with decision frameworks for refactoring and design choices

**What to Add:** ~255 lines from chora-base v1.3.0

**Steps:**

1. **Fetch the template content from chora-base v1.3.0:**
   ```bash
   gh api repos/liminalcommons/chora-base/contents/template/AGENTS.md.jinja --jq '.download_url' | \
     xargs curl -s > /tmp/chora-base-agents.md
   ```

2. **Extract the Strategic Design section** (approximately lines 100-350)
   - Strategic Context subsection
   - Strategic Design section with:
     - Vision-aware implementation pattern
     - Refactoring decision framework (ASCII flowchart)
     - Knowledge capture patterns
     - Quick reference checklist

3. **Adapt for mcp-n8n specifics:**
   - Replace template variables with mcp-n8n values
   - Customize MCP server examples
   - Link to existing ROADMAP.md and UNIFIED_ROADMAP.md

4. **Insert into AGENTS.md** after Project Structure section (around line 697)

5. **Test:**
   ```bash
   # Verify markdown formatting
   markdownlint AGENTS.md

   # Verify line count increased appropriately
   wc -l AGENTS.md  # Should be ~2000+ lines
   ```

6. **Commit:**
   ```bash
   git add AGENTS.md
   git commit -m "docs: Add Strategic Design section to AGENTS.md from chora-base v1.3.0

Adds vision-aware implementation patterns, refactoring decision framework,
and knowledge capture patterns for AI agents.

Benefits:
- Clear guidance on when to refactor vs defer
- Systematic approach to design decisions
- Better integration with roadmap and vision docs
- Reduces premature optimization

Ref: chora-base v1.3.0"
   ```

**Expected Outcome:** AGENTS.md grows from ~1,750 to ~2,000 lines

---

### Action 2: Add Just Auto-Installation to setup.sh (30 minutes)

**Why:** Eliminates "command not found: just" errors for new contributors

**Steps:**

1. **Fetch the auto-install logic from chora-base v1.4.0:**
   ```bash
   gh api repos/liminalcommons/chora-base/contents/template/scripts/setup.sh.jinja --jq '.download_url' | \
     xargs curl -s | grep -A 30 "just command runner" > /tmp/just-install-snippet.sh
   ```

2. **Update scripts/setup.sh** - Replace the warning-only section with auto-install:
   ```bash
   # Check for just command runner
   echo -e "${YELLOW}Checking for 'just' command runner...${NC}"
   if ! command -v just &> /dev/null; then
       echo -e "${YELLOW}Installing 'just' command runner...${NC}"

       if [[ "$OSTYPE" == "darwin"* ]]; then
           # macOS
           if command -v brew &> /dev/null; then
               brew install just
           else
               # Fallback to curl installer
               curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin
           fi
       else
           # Linux
           curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin
           echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
       fi

       echo -e "${GREEN}✓ just installed${NC}"
   else
       echo -e "${GREEN}✓ just found${NC}"
   fi
   echo ""
   ```

3. **Test:**
   ```bash
   # In a fresh environment without just:
   ./scripts/setup.sh
   # Should auto-install just

   just --version
   # Should show version
   ```

4. **Commit:**
   ```bash
   git add scripts/setup.sh
   git commit -m "feat: Auto-install just command runner in setup.sh

Based on chora-base v1.4.0 - eliminates manual installation step.

- macOS: brew install just (with curl fallback)
- Linux: curl installer to ~/.local/bin
- Transparent, automatic during project setup

Ref: chora-base v1.4.0"
   ```

---

### Action 3: Add Help Command to Justfile (30 minutes)

**Why:** Faster task discovery for contributors and agents

**Steps:**

1. **Add help command to justfile:**
   ```bash
   # Show common development workflows
   help:
       @echo "Common workflows:"
       @echo ""
       @echo "  just install      - Install all dependencies"
       @echo "  just test         - Run full test suite"
       @echo "  just smoke        - Quick validation tests"
       @echo "  just pre-merge    - Run all quality checks before merge"
       @echo ""
       @echo "  just --list       - Show all available commands"
       @echo ""
       @echo "For full command list: just --list"
   ```

2. **Update default recipe** (if needed):
   ```bash
   # Default recipe (show help)
   default:
       @just help
   ```

3. **Enhance inline documentation** throughout justfile with comments

4. **Test:**
   ```bash
   just help
   just --list
   just  # Should show help
   ```

5. **Commit:**
   ```bash
   git add justfile
   git commit -m "feat: Add help command to justfile for task discovery

Based on chora-base v1.4.0 - improves developer experience.

- Common workflows at a glance
- Better inline documentation
- Agent-friendly task catalog

Ref: chora-base v1.4.0"
   ```

---

### Action 4: Add Upgrade Docs Reference (15 minutes)

**Why:** Team awareness of template evolution strategy

**Option A: Update this document (quickest):**

Add to the end of this document before "References":

```markdown
## Understanding chora-base Upgrades

**For mcp-n8n as Exemplar:**

mcp-n8n is the original source from which chora-base was extracted. However, the template has evolved with improvements that can benefit mcp-n8n.

**Upgrade Philosophy:**
- Read: https://github.com/liminalcommons/chora-base/blob/main/docs/upgrades/PHILOSOPHY.md
- Understand displacement types (Required, Optional, Additive)
- Cherry-pick beneficial improvements selectively

**When to Adopt Template Changes:**
- ✅ Documentation enhancements (almost always)
- ✅ Script improvements (review and test)
- ✅ Workflow optimizations (evaluate benefits)
- ❌ Generalization fixes (mcp-n8n should stay specific)

**Process:**
1. Monitor chora-base releases
2. Review CHANGELOG for each release
3. Categorize changes (this document does this)
4. Apply beneficial changes via manual cherry-pick
5. Update `.copier-answers.yml` to track version
```

**Option B: Create UPGRADING.md (more comprehensive):**

Create a new [UPGRADING.md](UPGRADING.md) linking to chora-base upgrade docs.

**Commit:**
```bash
git add docs/CHORA_BASE_ADOPTION_STATUS.md  # or UPGRADING.md
git commit -m "docs: Add reference to chora-base upgrade philosophy

Helps team understand template evolution strategy and when to adopt
vs skip template improvements.

Ref: chora-base v1.5.0"
```

---

### Action 5: Update .copier-answers.yml to v1.5.0 (5 minutes)

**Why:** Track latest template version

**Steps:**

1. **Edit `.copier-answers.yml`:**
   ```yaml
   _commit: v1.5.0
   ```

2. **Commit:**
   ```bash
   git add .copier-answers.yml
   git commit -m "chore: Update chora-base template tracking to v1.5.0

Tracking latest template version. mcp-n8n has selectively adopted
beneficial improvements from v1.3.0-v1.5.0.

See docs/CHORA_BASE_ADOPTION_STATUS.md for alignment details."
   ```

---

## Upgrade Procedure (For Reference - See Recommended Actions Above)

```markdown
#### Frontmatter Schema

All knowledge notes use standardized YAML frontmatter for machine-readable metadata:

**Required Fields:**
- `id` (string): Unique note identifier in kebab-case (e.g., `backend-timeout-fix`)
- `created` (ISO 8601): Creation timestamp (e.g., `2025-01-17T12:00:00Z`)
- `updated` (ISO 8601): Last modification timestamp
- `tags` (array[string]): Topical tags for search and organization (e.g., `[troubleshooting, backend]`)

**Optional Fields:**
- `confidence` (enum): Solution reliability - `low` | `medium` | `high`
  - `low`: Untested hypothesis or early exploration
  - `medium`: Tested in limited scenarios
  - `high`: Production-validated, multiple confirmations
- `source` (string): Knowledge origin - `agent-learning` | `human-curated` | `external` | `research`
- `linked_to` (array[string]): Related note IDs for bidirectional linking (knowledge graph)
- `status` (enum): Note lifecycle - `draft` | `validated` | `deprecated`
- `author` (string): Agent or human who created the note
- `related_traces` (array[string]): Trace IDs that led to this learning

**Standards Compliance:**
- ✅ Compatible with Obsidian, Zettlr, LogSeq, Foam
- ✅ Follows Zettelkasten methodology (atomic notes, bidirectional linking)
- ✅ Enables semantic search and confidence-based filtering
- ✅ Supports knowledge graph visualization and traversal

**Example:**
\`\`\`markdown
---
id: backend-timeout-fix
created: 2025-01-17T12:00:00Z
updated: 2025-01-17T14:30:00Z
tags: [troubleshooting, backend, timeout]
confidence: high
source: agent-learning
linked_to: [trace-context-pattern, error-handling-best-practices]
status: validated
author: claude-code
related_traces: [abc123, def456]
---

# Backend Timeout Fix

## Problem
API calls to chora-composer were timing out after 30s...

## Solution
Increased timeout to 60s in config...

## Evidence
- Trace abc123: Successful completion at 45s
- Trace def456: Successful completion at 52s
- Load test: 98% success rate with new settings
\`\`\`
```

**Commit:**
```bash
git add .chora/memory/README.md
git commit -m "docs: Add frontmatter schema documentation for knowledge notes

Backport from chora-base v1.1.1 - provides comprehensive metadata
field documentation for agents and humans using the knowledge graph.

Benefits:
- Clear required vs optional field definitions
- Standards compliance notes (Obsidian, Zettlr, etc.)
- Complete example showing all fields in use
- Improved discoverability of advanced features

Ref: chora-base v1.1.1 release"
```

---

### Action 3: Add AGENTS.md Metadata Reference (20 minutes)

**Priority:** MEDIUM
**Effort:** 20 minutes
**Benefit:** Agents discover metadata capabilities

**Source:** `chora-base/template/AGENTS.md.jinja` (lines 642-699 in v1.1.1)

**Add to `AGENTS.md` after Project Structure section (around line 640):**

```markdown
### Knowledge Note Metadata Standards

Knowledge notes (`.chora/memory/knowledge/notes/*.md`) use **YAML frontmatter** following Zettelkasten best practices for machine-readable metadata.

**Required Frontmatter Fields:**
- `id`: Unique note identifier (kebab-case)
- `created`: ISO 8601 timestamp
- `updated`: ISO 8601 timestamp
- `tags`: Array of topic tags for search/organization

**Optional Frontmatter Fields:**
- `confidence`: `low` | `medium` | `high` - Solution reliability
- `source`: `agent-learning` | `human-curated` | `external` | `research`
- `linked_to`: Array of related note IDs (bidirectional linking)
- `status`: `draft` | `validated` | `deprecated`
- `author`: Agent or human creator
- `related_traces`: Array of trace IDs that led to this knowledge

**Example Knowledge Note:**
\`\`\`markdown
---
id: api-timeout-solution
created: 2025-01-17T10:00:00Z
updated: 2025-01-17T12:30:00Z
tags: [troubleshooting, api, performance]
confidence: high
source: agent-learning
linked_to: [connection-pool-tuning, retry-patterns]
status: validated
author: claude-code
related_traces: [abc123, def456]
---

# API Timeout Solution

## Problem
API calls timing out after 30s during high load...

## Solution
Increase timeout to 60s and implement retry with exponential backoff...

## Evidence
- Trace abc123: Successful completion at 45s
- Trace def456: Successful completion at 52s
- Load test: 98% success rate with new settings
\`\`\`

**Why YAML Frontmatter?**
- ✅ **Semantic Search**: Query by confidence, tags, or date (`grep "confidence: high"`)
- ✅ **Tool Compatibility**: Works with Obsidian, Zettlr, LogSeq, Foam
- ✅ **Knowledge Graph**: Enables bidirectional linking and visualization
- ✅ **Agent Decision-Making**: Filter by confidence level for solution reliability

**Reference:** See [.chora/memory/README.md](.chora/memory/README.md) for complete schema documentation.
```

**Commit:**
```bash
git add AGENTS.md
git commit -m "docs: Add metadata standards section to AGENTS.md

Backport from chora-base v1.1.1 - provides agents with comprehensive
understanding of knowledge note metadata capabilities.

Benefits:
- Agents discover metadata system from AGENTS.md
- Field definitions and examples directly accessible
- Cross-reference to full schema documentation
- Better knowledge graph utilization

Ref: chora-base v1.1.1 release"
```

---

## Upgrade Procedure (If Desired)

### Option A: Manual Cherry-Pick (Recommended)

**Best for:** Selective adoption of beneficial changes

```bash
# 1. Update .copier-answers.yml
# Edit file manually, change _commit: v1.0.0 → v1.2.0
git add .copier-answers.yml
git commit -m "chore: Update chora-base template tracking to v1.2.0"

# 2. Add frontmatter schema docs (see Action 2 above)
# Copy content from chora-base v1.1.1
git add .chora/memory/README.md
git commit -m "docs: Add frontmatter schema documentation"

# 3. Add AGENTS.md metadata section (see Action 3 above)
# Copy content from chora-base v1.1.1
git add AGENTS.md
git commit -m "docs: Add metadata standards to AGENTS.md"

# 4. Verify no regressions
just test
just lint
just smoke

# Done! mcp-n8n now has v1.1.1 docs + tracks v1.2.0
```

---

### Option B: Copier Update (Advanced)

**Best for:** Comparing template changes systematically

**Note:** This requires a clean git working directory.

```bash
# 1. Ensure clean working directory
git status
# If dirty: commit or stash changes

# 2. Run copier update in pretend mode
copier update --pretend --trust gh:liminalcommons/chora-base

# 3. Review proposed changes carefully
# Look for:
# - Documentation improvements (GOOD - likely want)
# - Script changes (REVIEW - may conflict with mcp-n8n specifics)
# - Generalization changes (SKIP - mcp-n8n should stay specific)

# 4. If changes look good, apply
copier update --trust gh:liminalcommons/chora-base

# 5. Review diffs
git diff

# 6. Revert unwanted changes
# e.g., if copier tries to generalize mcp-n8n-specific code:
git checkout -- path/to/unwanted/change

# 7. Commit desired changes
git add -p  # Stage changes selectively
git commit -m "chore: Update from chora-base v1.2.0 (selective)"

# 8. Test
just test
just lint
```

**Caution:** Copier may try to apply generalization fixes that aren't appropriate for mcp-n8n. Manual cherry-pick (Option A) is safer.

---

## Long-Term Maintenance Strategy

### Principle: Bidirectional Benefits

```
mcp-n8n (Exemplar)
    ↓ Infrastructure Extraction
chora-base (Template)
    ↓ Apply to Projects
chora-compose, future-projects (Adopters)
    ↓ Improvements Flow Back
chora-base (Template)
    ↓ Beneficial Enhancements
mcp-n8n (Exemplar) ← YOU ARE HERE
```

**mcp-n8n should benefit from template improvements that are:**
- ✅ Documentation enhancements (AGENTS.md, memory system docs)
- ✅ Script improvements discovered by other adopters
- ✅ Workflow optimizations (GitHub Actions)
- ✅ Testing patterns that improve quality

**mcp-n8n should NOT adopt changes that are:**
- ❌ Generalization fixes (mcp-n8n should stay specific)
- ❌ Breaking changes to core architecture
- ❌ Features irrelevant to MCP gateway use case

### Recommended Cadence

**Check for updates:** Quarterly or with major chora-base releases

**Process:**
1. Monitor chora-base releases (GitHub watch)
2. Read CHANGELOG for each release
3. Categorize changes:
   - **Documentation:** Almost always beneficial
   - **Scripts/Workflows:** Review for improvements
   - **Generalization:** Usually skip
   - **New Features:** Evaluate on case-by-case basis
4. Apply beneficial changes via manual cherry-pick
5. Update `.copier-answers.yml` to track version
6. Test thoroughly

---

## Parity Checklist

### To achieve 100% feature parity with chora-base v1.2.0:

**Infrastructure (Already Complete):**
- [x] 18 automation scripts
- [x] 7 GitHub Actions workflows
- [x] justfile with 25+ commands
- [x] Memory system (.chora/memory/)
- [x] chora-memory CLI (5 commands)
- [x] AGENTS.md (1,189 lines)
- [x] Pre-commit hooks
- [x] 85% coverage threshold
- [x] Documentation suite

**Template Sync:**
- [ ] Update `.copier-answers.yml` to reference v1.2.0 **(Recommended - 5 min)**

**Documentation Enhancements (v1.1.1):**
- [ ] Add frontmatter schema to `.chora/memory/README.md` **(Beneficial - 30 min)**
- [ ] Add metadata standards to `AGENTS.md` **(Beneficial - 20 min)**

**Generalization Fixes (v1.2.0):**
- [x] ~~Python imports as .jinja~~ - Not applicable (mcp-n8n is source)
- [x] ~~Remove hardcoded paths~~ - Not applicable (mcp-n8n should have specific paths)
- [x] ~~Fix placeholder usernames~~ - Not applicable (mcp-n8n has real values)
- [x] ~~Add security_email variable~~ - Not applicable (mcp-n8n has real email)
- [x] ~~Generalize memory README~~ - Not applicable (mcp-n8n should stay specific)

**Total Recommended Actions:** 3 (1 critical, 2 beneficial)
**Total Estimated Time:** ~55 minutes
**Expected Benefit:** Better documentation, easier template sync

---

## Benefits of Staying in Sync

### Why mcp-n8n should track chora-base versions:

1. **Documentation Improvements Flow Back**
   - v1.1.1 frontmatter schema helps mcp-n8n users
   - Future doc improvements benefit mcp-n8n

2. **Script Enhancements from Other Adopters**
   - chora-compose may discover script improvements
   - mcp-n8n can cherry-pick beneficial changes

3. **Consistency Across Ecosystem**
   - mcp-n8n, chora-compose, future projects share patterns
   - Easier for developers working across projects

4. **Easy Selective Sync**
   - `copier update --pretend` shows what's new
   - Manual cherry-pick gives full control

5. **Template Validation**
   - mcp-n8n serves as test case for template changes
   - Ensures template stays practical and useful

---

## Comparison with chora-compose Adoption

**chora-compose Adoption Guide:** Shows how to adopt chora-base into an existing project

**mcp-n8n Status Document:** Shows how the source project can benefit from template evolution

| Aspect | chora-compose | mcp-n8n |
|--------|---------------|---------|
| **Relationship** | Adopter | Source/Exemplar |
| **Version Gap** | None → v1.0.0 | v1.0.0 → v1.2.0 |
| **Infrastructure** | 0% → 100% | 100% → 100% |
| **Missing Features** | Many | Documentation only |
| **Effort to Parity** | 8-12 hours | ~1 hour |
| **Primary Benefit** | Gain infrastructure | Gain doc improvements |
| **Risk Level** | Medium | Low |
| **Recommendation** | Full adoption | Selective sync |

---

## Next Steps

### Immediate (2-4 hours total) - Updated for v1.5.0

**HIGH PRIORITY:**
1. **Add Strategic Design section to AGENTS.md** (1-2 hours) - v1.3.0
   - Vision-aware refactoring frameworks for agents
   - Better design decision-making
   - See detailed steps in "Recommended Actions" section above

**MEDIUM PRIORITY:**
2. **Enhance developer experience** (1-1.5 hours) - v1.4.0
   - Add `just` auto-installation to scripts/setup.sh (30 min)
   - Add `help` command to justfile (30 min)
   - Update `.copier-answers.yml` to v1.5.0 (5 min)

3. **Add upgrade docs awareness** (15 min) - v1.5.0
   - Reference chora-base upgrade philosophy
   - Help team understand template evolution

### Ongoing (Quarterly)

4. **Monitor chora-base releases**
   - Watch GitHub repo for new releases
   - Read CHANGELOG for each release
   - Evaluate beneficial improvements
   - Update this CHORA_BASE_ADOPTION_STATUS.md

5. **Cherry-pick improvements**
   - ✅ Documentation enhancements: Almost always
   - ✅ Script improvements: Review and test
   - ✅ Workflow optimizations: Evaluate benefits
   - ❌ Generalization fixes: mcp-n8n should stay specific

---

## Conclusion

**mcp-n8n has strong chora-base alignment (~95%)** as the original exemplar source. The template has evolved with improvements (v1.3.0-v1.5.0) that can benefit mcp-n8n.

**Key Findings:**
- ✅ v1.1.1 documentation improvements already adopted
- ⚠️ v1.3.0 Strategic Design section highly beneficial for agents
- ⚠️ v1.4.0 DX improvements (just auto-install, help command) recommended
- ✅ v1.5.0 upgrade documentation provides valuable context

**Recommended action:** Spend ~2-4 hours to:
1. Add Strategic Design section to AGENTS.md (HIGH - better agent decision-making)
2. Enhance developer experience with v1.4.0 improvements (MEDIUM - smoother onboarding)
3. Add upgrade docs awareness (LOW - better ecosystem understanding)
4. Continue quarterly sync process for future template improvements

**Long-term strategy:** mcp-n8n and chora-base have a bidirectional relationship. Infrastructure flows from mcp-n8n → chora-base, and beneficial improvements flow back chora-base → mcp-n8n.

---

## References

- **chora-base Repository:** https://github.com/liminalcommons/chora-base
- **chora-base Releases:**
  - v1.0.0: https://github.com/liminalcommons/chora-base/releases/tag/v1.0.0
  - v1.1.0: https://github.com/liminalcommons/chora-base/releases/tag/v1.1.0
  - v1.1.1: https://github.com/liminalcommons/chora-base/releases/tag/v1.1.1
  - v1.2.0: https://github.com/liminalcommons/chora-base/releases/tag/v1.2.0
  - v1.3.0: https://github.com/liminalcommons/chora-base/releases/tag/v1.3.0
  - v1.3.1: https://github.com/liminalcommons/chora-base/releases/tag/v1.3.1
  - v1.4.0: https://github.com/liminalcommons/chora-base/releases/tag/v1.4.0
  - v1.5.0: https://github.com/liminalcommons/chora-base/releases/tag/v1.5.0
- **chora-base CHANGELOG:** https://github.com/liminalcommons/chora-base/blob/main/CHANGELOG.md
- **chora-base Upgrade Documentation:**
  - Philosophy: https://github.com/liminalcommons/chora-base/blob/main/docs/upgrades/PHILOSOPHY.md
  - Upgrade Guides: https://github.com/liminalcommons/chora-base/tree/main/docs/upgrades
- **chora-base BENEFITS:** https://github.com/liminalcommons/chora-base/blob/main/docs/BENEFITS.md
- **chora-compose Adoption Guide:** /Users/victorpiper/code/chora-compose/docs/CHORA_BASE_ADOPTION_HANDOFF.md

---

**Last Updated:** 2025-10-19
**Next Review:** 2026-01-19 (quarterly)
**Status:** REVIEW RECOMMENDED - v1.3.0-v1.5.0 improvements available
