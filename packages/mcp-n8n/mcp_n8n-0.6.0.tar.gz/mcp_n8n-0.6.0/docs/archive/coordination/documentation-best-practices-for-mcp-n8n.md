# Documentation Best Practices: Lessons from chora-compose

**For:** mcp-n8n development team
**From:** chora-compose team
**Date:** 2025-10-19
**Context:** Sprint 2-5 planning (n8n workflow implementation)

---

## Executive Summary

Through our Jinja2Generator feature development, we discovered a powerful approach: **Documentation-Driven Development (DDD)**. By writing comprehensive documentation *before* code, we achieved:

**Results:**
- ✅ **Zero API drift** - Implementation matched documentation exactly
- ✅ **Zero bugs** - All tests passing on first run, zero production issues
- ✅ **Same timeline** - 6 hours total (vs. 6-9 hours traditional approach)
- ✅ **High confidence** - Feature worked exactly as documented

**The Problem DDD Solves:**
- API drift (docs lag behind code changes)
- Late-stage design issues (costly to fix)
- Incomplete test coverage (missing user scenarios)
- Stale examples (documentation doesn't match reality)

**The DDD Solution:**
1. Write complete documentation **first** (before any code)
2. Extract test cases directly from documentation examples
3. Implement the feature to pass the documentation-derived tests
4. **Result:** Implementation guaranteed to match documentation

This guide shares our process, templates, and specific applications for your mcp-n8n Sprint 2-5 work.

---

## Table of Contents

1. [Quick Start: Apply DDD in 3 Steps](#quick-start-apply-ddd-in-3-steps)
2. [The DDD Pilot: Real-World Results](#the-ddd-pilot-real-world-results)
3. [The DDD Process](#the-ddd-process)
4. [Diátaxis Framework Lite](#diataxis-framework-lite)
5. [Adaptation Guide for mcp-n8n](#adaptation-guide-for-mcp-n8n)
6. [Templates](#templates)
7. [FAQ & Tips](#faq--tips)

---

## Quick Start: Apply DDD in 3 Steps

### Step 1: Write Documentation First (User Perspective)

**Before writing any code**, create:
- **Tutorial**: "How to [accomplish goal]" with step-by-step walkthrough
- **How-To Guides**: 2-3 practical scenarios showing different use cases
- **Reference**: API specifications (if building an API/library)

**Example for mcp-n8n Sprint 2 (Validation Workflow):**
```markdown
# Tutorial: Validate Content with mcp-n8n

## What You'll Build
- An n8n workflow that calls chora:validate_content
- Event correlation using trace_id
- Error handling for validation failures

## Step 1: Create Workflow
[Workflow diagram showing HTTP trigger → chora node → event watcher]

## Step 2: Configure chora Validation Node
Parameters:
- content_config_id: "weekly-report-intro"
- trace_id: {{$node["Generate Trace ID"].json["trace_id"]}}

## Step 3: Watch for Events
Configure event file watcher:
- Path: var/telemetry/events.jsonl
- Filter: trace_id matches request

## Step 4: Return Result
[Expected validation result format]
```

### Step 2: Extract Test Cases from Examples

**From your documentation examples**, create tests:

```javascript
// Test extracted from Tutorial Step 1-4
describe('Validation Workflow', () => {
  it('should validate content and correlate events', async () => {
    // Step 1: Create workflow (from tutorial)
    const workflow = createValidationWorkflow();

    // Step 2: Execute with trace_id
    const trace_id = generateTraceId();
    const result = await workflow.execute({
      content_config_id: 'weekly-report-intro',
      trace_id
    });

    // Step 3-4: Verify event correlation (from tutorial)
    const events = await readEvents('var/telemetry/events.jsonl');
    const correlatedEvent = events.find(e => e.trace_id === trace_id);

    expect(correlatedEvent).toBeDefined();
    expect(correlatedEvent.event_type).toBe('chora.validation_completed');
    expect(result.status).toBe('valid');
  });
});
```

**Why this works:**
- Tests validate tutorial actually works
- Real user scenarios (not artificial test cases)
- If tutorial changes, tests fail (forces docs to stay current)

### Step 3: Implement to Pass Tests

**Now write the code** that makes your documentation examples work:

- Implementation must match documented API
- All examples must run successfully
- No surprises (design already validated in docs)

**Result:** Your implementation is guaranteed to match your documentation because tests enforce the contract.

---

## The DDD Pilot: Real-World Results

### Feature: Jinja2Generator

**What we built:** AI-powered content generation using Jinja2 templates

**Timeline:**
- Documentation writing: 3 hours (6 docs, ~28,800 words)
- Test extraction: 30 minutes (16 tests from doc examples)
- Implementation: 1.5 hours (170 lines of code)
- Integration & examples: 1 hour
- **Total: 6 hours**

**Traditional approach would have been:**
- Implementation: 2-3 hours
- Writing tests: 1-2 hours
- Writing docs: 2-3 hours
- Fixing API drift: 1 hour
- **Total: 6-9 hours**

### Quantitative Results

| Metric | Value |
|--------|-------|
| Lines of implementation | 170 |
| Lines of tests | ~900 |
| Test coverage | 100% of public API |
| Documentation examples | 25+ |
| Test cases extracted | 16 |
| **Bugs in development** | **0** |
| **Bugs in testing** | **0** |
| **Bugs post-release** | **0** |
| **Test pass rate (first run)** | **100%** |

### What Worked Exceptionally Well

**1. Zero API Drift**
- Problem: Docs usually lag code changes → confusion and bugs
- Solution: Tests extracted from docs → implementation MUST match
- Evidence: All 16 doc examples worked exactly as written

**2. Better API Design**
- Problem: API evolves messily during coding → inconsistent interface
- Solution: Writing docs first forces user perspective
- Evidence: Clean API (`generate(config, context=...)`), clear errors, sensible defaults

**3. Faster Test Creation**
- Problem: Writing comprehensive tests is time-consuming
- Solution: Documentation examples ARE the tests
- Evidence: 30 minutes to extract 16 tests (vs. 2 hours to write from scratch)

**4. High Confidence**
- Problem: Worry about edge cases, untested paths
- Solution: Comprehensive docs → comprehensive tests
- Evidence: 100% passing on first complete run

**5. Built-in Working Examples**
- Problem: Examples often go stale
- Solution: Doc examples are tested → must work
- Evidence: Example ran successfully on first try (copied from docs)

### Key Insight

> **Writing documentation first reveals design issues early, when they're cheap to fix.**

When you write "Step 1: Configure the validation node with parameters X, Y, Z" you immediately discover:
- Do we need all three parameters?
- Are the parameter names intuitive?
- Is the configuration overly complex?
- What defaults make sense?

Fixing these issues in documentation takes minutes. Fixing them after implementation takes hours.

---

## The DDD Process

### Overview: 6 Phases

```
Phase 1: Tutorial (Learning Goal)
   ↓
Phase 2: How-To Guides (Scenarios)
   ↓
Phase 3: Reference (API Contract)
   ↓
Phase 4: Explanation (Why It Works)
   ↓
Phase 5: Extract Tests (from docs)
   ↓
Phase 6: Implement (to pass tests)
```

### Phase 1: Tutorial (Learning Goal)

**Purpose:** Establish what users will accomplish

**Create:** Tutorial document showing feature in action

**Key Elements:**
- **Learning goal:** "By the end, you'll have..."
- **Step-by-step:** Incremental, completable
- **Working examples:** With expected output
- **Success criteria:** User can verify they succeeded

**Example Structure:**
```markdown
# Tutorial: [Accomplish Specific Goal]

## What You'll Build
- [Concrete outcome]

## Step 1: [First Action]
[What to do]
**Expected output:** [Exact result]

## Step 2: [Build On It]
[Next action]
**Expected output:** [Exact result]

## Success!
You've just [what they accomplished]
```

**Test Extraction:**
```javascript
// End-to-end test from tutorial
it('should complete tutorial workflow', async () => {
  // Step 1
  const result1 = await doStep1();
  expect(result1).toEqual(expectedOutput1);

  // Step 2
  const result2 = await doStep2();
  expect(result2).toEqual(expectedOutput2);

  // Final success check
  expect(finalState).toMatchDocumented();
});
```

### Phase 2: How-To Guides (Scenarios)

**Purpose:** Document real-world use cases

**Create:** 3+ How-To guides for different scenarios

**Key Elements:**
- **Goal-oriented:** Solve specific problems
- **Practical:** Real scenarios users will face
- **Solution-focused:** Step-by-step solutions
- **Variations:** Show different approaches

**Example Structure:**
```markdown
# How to [Solve Specific Problem]

## When to Use This
[Scenario description]

## Solution
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Result
[What you achieved]

## Variations
- **Variation A:** [Different approach]
- **Variation B:** [Alternative method]
```

**Test Extraction:**
```javascript
// Scenario tests from how-to guides
describe('How-To Scenarios', () => {
  it('should handle scenario A', async () => {
    // From "How to Handle Validation Errors"
    const result = await handleErrorScenario();
    expect(result).toMatchHowToGuide();
  });

  it('should handle scenario B', async () => {
    // From "How to Correlate Events"
    const result = await correlateEvents();
    expect(result).toMatchHowToGuide();
  });
});
```

### Phase 3: Reference (API Contract)

**Purpose:** Define exact API before implementation

**Create:** Complete API reference documentation

**Key Elements:**
- **Function signatures:** Exact parameters and return types
- **Parameter descriptions:** What each parameter does
- **Return values:** What the function returns
- **Error conditions:** When and why errors occur
- **Examples:** Usage examples for each function

**Example Structure:**
```markdown
# API Reference: [Component Name]

## Function: `validateContent()`

```javascript
async function validateContent(
  contentConfigId: string,
  options?: ValidationOptions
): Promise<ValidationResult>
```

**Parameters:**
- `contentConfigId` (string, required): ID of content config to validate
- `options` (ValidationOptions, optional): Validation options
  - `trace_id` (string): Trace ID for correlation
  - `strict` (boolean): Enable strict validation (default: false)

**Returns:** `ValidationResult`
```javascript
{
  status: 'valid' | 'invalid',
  errors: ValidationError[],
  trace_id: string
}
```

**Errors:**
- `ConfigNotFoundError`: Content config doesn't exist
- `ValidationError`: Validation failed (check .errors array)

**Example:**
```javascript
const result = await validateContent('weekly-report', {
  trace_id: 'abc123',
  strict: true
});
console.log(result.status); // 'valid'
```
```

**Test Extraction:**
```javascript
// API contract tests from reference
describe('validateContent API', () => {
  it('should match documented signature', async () => {
    const result = await validateContent('test-config', {
      trace_id: 'test123',
      strict: true
    });

    // Verify return type matches reference
    expect(result).toHaveProperty('status');
    expect(result).toHaveProperty('errors');
    expect(result).toHaveProperty('trace_id');
    expect(['valid', 'invalid']).toContain(result.status);
  });

  it('should throw documented errors', async () => {
    // From error conditions in reference
    await expect(
      validateContent('nonexistent-config')
    ).rejects.toThrow(ConfigNotFoundError);
  });
});
```

### Phase 4: Explanation (Why It Works)

**Purpose:** Provide conceptual understanding

**Create:** Explanation document covering design decisions

**Key Elements:**
- **Conceptual background:** Why feature exists
- **Design decisions:** Why we chose this approach
- **Trade-offs:** What we optimized for
- **When to use:** Guidance on appropriate use

**Example Structure:**
```markdown
# Explanation: Why Event Correlation Matters

## The Problem
Distributed workflows lose request context...

## The Solution
Trace IDs propagate context across services...

## Design Decisions
**Why trace_id instead of request_id?**
[Reasoning]

**Why JSONL for events instead of database?**
[Trade-offs]

## When to Use
Use event correlation when:
- [Scenario 1]
- [Scenario 2]

Don't use when:
- [Anti-pattern 1]
```

**Note:** Explanations don't usually generate tests directly, but they inform implementation decisions.

### Phase 5: Extract Tests

**Now that documentation is complete**, extract tests:

**From Tutorials:**
- End-to-end integration tests
- Complete workflow tests

**From How-To Guides:**
- Scenario-specific tests
- Edge case handling

**From Reference:**
- API contract tests
- Parameter validation
- Error condition tests

**Pattern:**
```javascript
// File: tests/integration/from_documentation.test.js

describe('Documentation Examples', () => {
  describe('Tutorial: Validation Workflow', () => {
    it('completes end-to-end', async () => {
      // Exact code from tutorial
    });
  });

  describe('How-To: Handle Errors', () => {
    it('handles validation errors', async () => {
      // Exact code from how-to
    });
  });

  describe('Reference: validateContent', () => {
    it('matches API contract', async () => {
      // Tests from reference examples
    });
  });
});
```

**Time estimate:** 30-60 minutes for 15-20 tests

### Phase 6: Implement

**Now write the implementation** that makes your tests pass:

**Benefits at this stage:**
- API already designed (from Reference docs)
- User scenarios clear (from Tutorial/How-To)
- Tests ready (extracted from examples)
- No design ambiguity

**Process:**
1. Run tests (they fail - no implementation yet)
2. Implement to make tests pass
3. Implementation matches docs (because tests enforce it)
4. Done! Feature documented, tested, implemented

**No surprises:**
- You already validated the API design (writing Reference)
- You already validated user workflows (writing Tutorial)
- You already validated scenarios (writing How-To guides)

---

## Diátaxis Framework Lite

DDD uses the **Diátaxis framework** for documentation structure. Four document types, four purposes:

### 1. Tutorial - Learning Oriented

**Goal:** Teach through hands-on experience
**Format:** Step-by-step, incremental
**Audience:** Beginners learning the feature
**Analogy:** Teaching a child to cook

**Characteristics:**
- Starts with simple example
- Builds complexity gradually
- Every step works and shows progress
- User feels accomplished at end

**Example Titles:**
- "Build Your First n8n Validation Workflow"
- "Get Started with Event Correlation"
- "Create a Multi-Step Content Generation Workflow"

**Key Sections:**
- What You'll Build
- Prerequisites
- Step-by-step instructions
- Expected output at each step
- Success criteria

### 2. How-To Guide - Task Oriented

**Goal:** Solve specific problems
**Format:** Recipe-style solutions
**Audience:** Users with specific needs
**Analogy:** Recipe in a cookbook

**Characteristics:**
- Assumes basic knowledge
- Focused on one task
- Practical and actionable
- Shows variations/alternatives

**Example Titles:**
- "How to Call chora-compose from n8n Node"
- "How to Debug Event Correlation Issues"
- "How to Handle Validation Errors"

**Key Sections:**
- When to Use This
- Solution (step-by-step)
- Variations
- Troubleshooting

### 3. Reference - Information Oriented

**Goal:** Technical specifications
**Format:** Structured, comprehensive
**Audience:** Users looking up details
**Analogy:** Encyclopedia entry

**Characteristics:**
- Complete and accurate
- Organized systematically
- Describes what exists
- No explanation of why

**Example Titles:**
- "n8n chora-compose Node Parameters"
- "Event Schema Reference"
- "Validation Error Codes"

**Key Sections:**
- Function signatures
- Parameter descriptions
- Return values
- Error conditions
- Examples (brief, focused)

### 4. Explanation - Understanding Oriented

**Goal:** Illuminate concepts
**Format:** Discussion, background
**Audience:** Users seeking deeper understanding
**Analogy:** History book or essay

**Characteristics:**
- Provides context
- Discusses alternatives
- Explains decisions
- Connects concepts

**Example Titles:**
- "Why Event Correlation Matters for Distributed Workflows"
- "Understanding chora-compose Gateway Integration"
- "Event-Driven vs. Polling Approaches"

**Key Sections:**
- The problem
- The solution
- Design decisions
- Trade-offs
- When to use / when not to

### Quick Reference: Which Type When?

| User Wants To... | Use This Type | Example |
|-----------------|---------------|---------|
| **Learn** the feature | Tutorial | "Build your first workflow" |
| **Solve** a specific problem | How-To | "How to handle errors" |
| **Look up** technical details | Reference | "Parameter reference" |
| **Understand** why/how it works | Explanation | "Why trace_id matters" |

---

## Adaptation Guide for mcp-n8n

### Applying DDD to n8n Workflows

n8n workflows are inherently visual and user-facing - perfect for DDD! Here's how to apply it to your Sprint 2-5 work.

### Sprint 2: Validation Workflow (Phase 0)

**Goal:** Prove mcp-n8n can call chora-compose and handle events

**DDD Application:**

**Phase 1: Tutorial**
```markdown
# Tutorial: Build a Content Validation Workflow

## What You'll Build
An n8n workflow that:
- Calls chora:validate_content via MCP
- Generates and propagates trace_id
- Watches events.jsonl for correlation
- Returns validation result

## Step 1: Create Basic Workflow
[Screenshot of n8n canvas with 4 nodes]

Nodes:
1. HTTP Trigger (webhook)
2. Generate Trace ID (function node)
3. chora:validate_content (MCP node)
4. Watch Events (file watcher node)

## Step 2: Configure Trace ID Generation
[Node configuration screenshot]

```javascript
// Generate Trace ID node
const trace_id = crypto.randomUUID();
return { trace_id };
```

## Step 3: Configure chora Validation Node
[Node configuration screenshot]

Parameters:
- content_config_id: {{$json.content_config_id}}
- CHORA_TRACE_ID: {{$node["Generate Trace ID"].json["trace_id"]}}

## Step 4: Configure Event Watcher
[Node configuration screenshot]

Watch: var/telemetry/events.jsonl
Filter: trace_id === {{$node["Generate Trace ID"].json["trace_id"]}}
Event: chora.validation_completed

## Step 5: Test the Workflow
Trigger with:
```json
{
  "content_config_id": "weekly-report-intro"
}
```

Expected result:
```json
{
  "status": "valid",
  "trace_id": "...",
  "event": {
    "event_type": "chora.validation_completed",
    "timestamp": "...",
    "status": "success"
  }
}
```

## Success!
You've built an event-correlated validation workflow!
```

**Phase 2: How-To Guides**
- "How to Handle Validation Failures"
- "How to Debug Event Correlation"
- "How to Configure Timeout Handling"

**Phase 3: Reference**
- "chora:validate_content Node Parameters"
- "Event Schema for validation_completed"
- "Error Codes and Meanings"

**Phase 4: Extract Tests**
```javascript
describe('Sprint 2: Validation Workflow', () => {
  it('completes tutorial workflow', async () => {
    // Execute workflow from tutorial
    const result = await executeWorkflow('validation-tutorial', {
      content_config_id: 'weekly-report-intro'
    });

    // Verify tutorial's expected result
    expect(result.status).toBe('valid');
    expect(result.trace_id).toBeDefined();
    expect(result.event.event_type).toBe('chora.validation_completed');
  });

  it('handles validation failures', async () => {
    // From "How to Handle Validation Failures"
    const result = await executeWorkflow('validation-tutorial', {
      content_config_id: 'invalid-config'
    });

    expect(result.status).toBe('invalid');
    expect(result.event.error_message).toContain('validation failed');
  });
});
```

**Phase 5: Implement**
- Build n8n workflow matching documented steps
- All tests pass (implementation = documentation)

### Sprint 3: Content Generation (Phase 1)

**DDD Application:**

**Tutorial:** "Generate Content with chora-compose and n8n"
- Multi-node workflow
- Credential validation (using generator dependencies)
- Content generation
- Event correlation

**How-To Guides:**
- "How to Pre-Validate Credentials"
- "How to Handle Generation Failures"
- "How to Implement Retry Logic"

**Reference:**
- "chora:generate_content Node Parameters"
- "capabilities://generators Resource Schema"
- "chora.content_generated Event Schema"

**Extract Tests:**
- End-to-end generation workflow
- Credential pre-validation
- Error handling scenarios
- Concurrent request handling

### Sprint 4: Gateway-Aware Features (chora v1.4.0)

**DDD Application:**

**Tutorial:** "Preview Artifacts Before Assembly"
- Use preview_artifact tool
- Dry-run workflow
- Review before commit

**How-To Guides:**
- "How to Use Context-Aware Capabilities"
- "How to Implement Streaming Progress Updates"
- "How to Query Historical Events"

**Reference:**
- "chora:preview_artifact Node Parameters"
- "capabilities://generators (Context-Aware) Schema"
- "Telemetry Query API"

### Sprint 5: Artifact Assembly (Phase 2)

**DDD Application:**

**Tutorial:** "Build Multi-Step Artifact Workflows"
- Generate multiple content pieces
- Preview assembled artifact
- Assemble and retrieve

**How-To Guides:**
- "How to Handle Multi-Section Artifacts"
- "How to Validate Before Assembly"
- "How to Retrieve Assembled Artifacts"

**Reference:**
- "chora:assemble_artifact Node Parameters"
- "chora.artifact_assembled Event Schema"
- "Multi-Step Workflow Patterns"

### Common Patterns for n8n Documentation

**1. Screenshots + Code**
n8n is visual - include:
- Workflow canvas screenshots
- Node configuration screenshots
- Expected output screenshots
- Code for function nodes

**2. Working Workflow Files**
Provide `.json` workflow exports:
```markdown
## Download This Workflow
[Link to validation-tutorial.json]

Import into n8n: Settings → Import Workflow
```

**3. Test Data**
Include test payloads:
```markdown
## Test This Workflow
Trigger with:
```json
{"content_config_id": "weekly-report-intro"}
```
```

**4. Troubleshooting Sections**
n8n has specific failure modes:
- Node execution errors
- Missing credentials
- Event correlation timeouts
- File permission issues

### DDD Timeline for Each Sprint

| Sprint | Docs | Tests | Impl | Total |
|--------|------|-------|------|-------|
| Sprint 2 (2-3 days) | 1 day | 1 hour | 1-2 days | 2-3 days |
| Sprint 3 (8-10 days) | 2-3 days | 2-3 hours | 5-7 days | 8-10 days |
| Sprint 4 (9-10 days) | 3 days | 3 hours | 6-7 days | 9-10 days |
| Sprint 5 (8-10 days) | 2-3 days | 2-3 hours | 5-7 days | 8-10 days |

**Note:** Timeline *includes* documentation time (vs. documenting after sprint)

---

## Templates

### Tutorial Template (Condensed)

```markdown
# Tutorial: [Accomplish Specific Goal]

> **Learning Goal:** By the end, you'll have [specific outcome]

## What You'll Build
- [Specific achievement 1]
- [Specific achievement 2]
- [Final accomplishment]

## Prerequisites
- [ ] [Required item 1]
- [ ] [Required item 2]

## Time Required
Approximately [X] minutes

---

## Step 1: [First Action]

[What to do]

[Code/config example]

**Expected output:**
```
[Exact output user should see]
```

---

## Step 2: [Build on Previous]

[Next action]

---

## Success!
You've just [what they accomplished]

## What You Learned
- ✅ [Concept 1]
- ✅ [Concept 2]

## Next Steps
- [Related tutorial]
- [How-to guide]
```

**Full template:** https://github.com/liminalcommons/chora-compose/blob/main/dev-docs/templates/TUTORIAL_TEMPLATE.md

### How-To Template (Condensed)

```markdown
# How to [Solve Specific Problem]

> **Goal:** [What this accomplishes]

## When to Use This
[Scenario description]

## Prerequisites
- [Requirement 1]
- [Requirement 2]

## Solution

### Step 1: [Action]
[Instructions]

### Step 2: [Action]
[Instructions]

## Result
[What you achieved]

## Variations

**Variation A:** [Alternative approach]
**Variation B:** [Different method]

## Troubleshooting

**Problem:** [Common issue]
**Solution:** [How to fix]
```

**Full template:** https://github.com/liminalcommons/chora-compose/blob/main/dev-docs/templates/HOWTO_TEMPLATE.md

### Reference Template (Condensed)

```markdown
# API Reference: [Component Name]

## Function: `functionName()`

```language
function functionName(
  param1: Type1,
  param2: Type2
): ReturnType
```

**Parameters:**
- `param1` (Type1, required): Description
- `param2` (Type2, optional): Description

**Returns:** `ReturnType`
```language
{
  field1: Type1,
  field2: Type2
}
```

**Errors:**
- `ErrorType1`: When this error occurs
- `ErrorType2`: When this error occurs

**Example:**
```language
const result = functionName(value1, value2);
console.log(result);
// Expected output
```

## Error Reference

### `ErrorName`

**Thrown when:** [Condition]
**Message:** `"error message"`
**How to handle:** [Solution]
```

**Full template:** https://github.com/liminalcommons/chora-compose/blob/main/dev-docs/templates/REFERENCE_TEMPLATE.md

### Explanation Template (Condensed)

```markdown
# Explanation: [Concept or Decision]

## Overview
[High-level summary]

## The Problem
[What problem this solves]

## The Solution
[How the solution works]

## Design Decisions

**Decision 1: [Choice Made]**
- **Why:** [Reasoning]
- **Trade-offs:** [What we gave up]
- **Alternatives considered:** [Other options]

**Decision 2: [Choice Made]**
- **Why:** [Reasoning]

## When to Use
Use this when:
- [Scenario 1]
- [Scenario 2]

Don't use when:
- [Anti-pattern 1]
- [Better alternative]

## Related Concepts
- [Concept 1]: [How it relates]
- [Concept 2]: [How it relates]
```

**Full template:** https://github.com/liminalcommons/chora-compose/blob/main/dev-docs/templates/EXPLANATION_TEMPLATE.md

---

## FAQ & Tips

### Frequently Asked Questions

**Q: Is DDD slower than traditional development?**

**A:** No. Total time is the same (6 hours) or faster.
- Traditional: Code (2-3h) + Tests (1-2h) + Docs (2-3h) + Fix drift (1h) = 6-9h
- DDD: Docs (3h) + Tests extraction (0.5h) + Code (1.5h) + Integration (1h) = 6h

Plus DDD has zero bugs and zero API drift.

**Q: When should I NOT use DDD?**

**A:** Skip DDD for:
- **Trivial features** - Single function, obvious API
- **Prototypes** - Experimenting, API not settled
- **Internal utilities** - No external users
- **Refactoring** - Improving existing code (docs already exist)

Use DDD for:
- **User-facing features** - APIs, workflows, integrations
- **Complex features** - Multiple scenarios, edge cases
- **Team projects** - Multiple people need to understand
- **Long-lived features** - Will be maintained over time

**Q: What if the API needs to change during implementation?**

**A:** Update docs → update tests → update implementation.

The key: Tests enforce docs/code sync. If you change implementation without updating docs, tests fail. This is GOOD - it forces you to keep them in sync.

**Q: How detailed should documentation be?**

**A:** Detailed enough that someone could implement the feature from docs alone.

Test: Could another developer implement your feature using only your documentation (without seeing your code)? If yes, it's detailed enough.

**Q: Do I need all 4 document types?**

**A:** Minimum viable:
- **Tutorial** (always) - Users need to learn
- **Reference** (for APIs) - Developers need specs
- **How-To** (1-2 guides) - Users need scenarios

Optional but valuable:
- **More How-To guides** - More scenarios covered
- **Explanation** - Deeper understanding

**Q: Can I write docs and code simultaneously?**

**A:** You CAN, but you lose the main benefits:
- No early design validation
- Risk of docs drifting from code
- Harder to extract tests cleanly

Better: Strict separation ensures validation before coding.

### Tips for Success

**Start Small**
- Pick one feature for first DDD experiment
- See if process works for your team
- Refine before scaling

**Test Extraction is Fast**
- 30-60 minutes for 15-20 tests
- Just copy examples from docs
- Add assertions for expected outputs

**Working Examples = Confidence**
- Every code example should run
- Include expected output
- Test examples as part of CI

**Docs Force Clear Design**
- If API is hard to document, it's poorly designed
- If tutorial feels awkward, rethink the flow
- If reference has many special cases, simplify

**Screenshots for n8n**
- Workflows are visual
- Include canvas screenshots
- Show node configurations
- Demonstrate expected results

**Version Control Docs**
- Treat docs like code
- Review doc PRs carefully
- Update docs = update tests

**Celebrate Wins**
- Track bugs found AFTER documentation (should be zero)
- Measure API drift incidents (should be zero)
- Share success stories with team

### Anti-Patterns to Avoid

❌ **Skipping test extraction** - "I'll just implement from docs"
- Result: Docs drift, bugs appear

❌ **Vague documentation** - "Configure as needed"
- Result: Can't extract tests, poor UX

❌ **Broken examples** - Untested code blocks
- Result: Users frustrated, tests fail

❌ **Implementation first, docs later** - "I'll document when done"
- Result: Back to traditional approach, lose DDD benefits

❌ **Incomplete tutorials** - Missing steps, assumes knowledge
- Result: Users stuck, incomplete tests

✅ **Do this instead:**
- Extract all tests before coding
- Be specific in every step
- Test every example
- Docs truly first, no code
- Hand-holdable tutorials

---

## Resources & Support

### Full Documentation (chora-compose repo)

**Detailed Case Study:**
https://github.com/liminalcommons/chora-compose/blob/main/dev-docs/meta/DDD_LESSONS.md

**Complete Process Guide:**
https://github.com/liminalcommons/chora-compose/blob/main/dev-docs/meta/DOCUMENTATION_DRIVEN_DEVELOPMENT.md

**Full Templates:**
- Tutorial: https://github.com/liminalcommons/chora-compose/blob/main/dev-docs/templates/TUTORIAL_TEMPLATE.md
- How-To: https://github.com/liminalcommons/chora-compose/blob/main/dev-docs/templates/HOWTO_TEMPLATE.md
- Reference: https://github.com/liminalcommons/chora-compose/blob/main/dev-docs/templates/REFERENCE_TEMPLATE.md
- Explanation: https://github.com/liminalcommons/chora-compose/blob/main/dev-docs/templates/EXPLANATION_TEMPLATE.md

### External Resources

**Diátaxis Framework:**
https://diataxis.fr/

**Why Documentation-Driven Development:**
https://gist.github.com/zsup/9434452

### Support

**Questions or feedback?**
- Open an issue in mcp-n8n repo tagged "documentation"
- Ask during sprint planning
- Request doc review before implementation

**We're happy to:**
- Review your Sprint 2 docs before implementation
- Answer questions about DDD process
- Share more templates if needed

---

## Conclusion

Documentation-Driven Development transformed our feature development:
- **Zero API drift** - Tests enforce docs/code sync
- **Zero bugs** - Comprehensive tests from comprehensive docs
- **Better design** - Writing docs first reveals issues early
- **Same timeline** - 6 hours vs. 6-9 hours traditional

As you start Sprint 2-5, consider applying DDD:
1. **Sprint 2:** Document validation workflow first, then implement
2. **Sprint 3:** Document content generation scenarios, extract tests, implement
3. **Sprint 4:** Document gateway-aware features with chora v1.4.0
4. **Sprint 5:** Document multi-step artifact workflows

The key insight: **Documentation is not overhead - it's the design phase.**

Good luck with your sprints! We're excited to see what you build.

---

**Document Version:** 1.0
**Last Updated:** 2025-10-19
**Authors:** chora-compose development team
**License:** CC-BY-4.0 (share freely, attribute source)
