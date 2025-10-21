---
title: "Build Your First Workflow"
type: tutorial
audience: intermediate
estimated_time: "30 minutes"
prerequisites: ["mcp-n8n installed", "chora-compose v1.3.0+", "API keys configured"]
test_extraction: yes
source: "src/mcp_n8n/workflows/daily_report.py, tests/features/daily_report.feature"
last_updated: 2025-10-21
---

# Tutorial: Build Your First Workflow

## What You'll Build

An automated **Daily Engineering Report** workflow that aggregates Git commits and gateway telemetry events into a formatted report. This is a real production workflow used in the mcp-n8n project.

**Sample output:**
```
# Daily Engineering Report - 2025-10-21

## Summary
- 5 commits
- 127 events
- 95.2% success rate
- 2 backends active

## Recent Commits
1. [8d0ee040] feat(chora-base): Add Strategic Design framework
2. [85049363] feat(sprint-3): Complete event monitoring
...
```

## What You'll Learn

- How to run a workflow programmatically
- How to pass parameters to workflows
- How to handle workflow results and errors
- How to interpret workflow execution statistics
- How to customize workflows for different use cases

## Prerequisites

- [x] mcp-n8n installed (`pip install mcp-n8n`)
- [x] chora-compose v1.3.0+ installed (`pip install chora-compose>=1.3.0`)
- [x] Environment variables configured (ANTHROPIC_API_KEY)
- [x] Gateway has run at least once (to generate events)
- [x] Located in a git repository

## Time Required

Approximately 30 minutes

---

## Step 1: Understand the Workflow

**What we're doing:** Learn what the Daily Report workflow does and why it's useful

The Daily Report workflow (`run_daily_report`) is a production workflow that:
1. **Fetches Git commits** from the last N hours (default: 24h)
2. **Queries gateway events** from telemetry system
3. **Aggregates statistics** (tool usage, success rates, performance)
4. **Generates formatted report** using chora-compose templates
5. **Stores report** in ephemeral storage (7-day retention)

**When to use it:**
- Daily standup preparation
- Sprint reviews
- Performance monitoring
- Debugging multi-day issues

**Workflow location:** [src/mcp_n8n/workflows/daily_report.py](../../src/mcp_n8n/workflows/daily_report.py)

---

## Step 2: Import the Workflow

**What we're doing:** Set up Python environment to run the workflow

**Instructions:**

1. Create a new Python file `my_first_workflow.py`:
   ```python
   import asyncio
   from mcp_n8n.workflows.daily_report import run_daily_report
   from mcp_n8n.backends import BackendRegistry
   from mcp_n8n.memory import EventLog
   from pathlib import Path
   ```

2. Initialize required components:
   ```python
   async def main():
       # Initialize backend registry (for tool calls)
       registry = BackendRegistry()

       # Initialize event log (for querying events)
       event_log = EventLog(base_dir=Path(".chora/memory/events"))

       print("Components initialized successfully!")

   if __name__ == "__main__":
       asyncio.run(main())
   ```

3. Run the file to verify setup:
   ```bash
   python my_first_workflow.py
   ```

**Expected output:**
```
Components initialized successfully!
```

**Explanation:** We're importing the workflow function and setting up the two dependencies it needs:
- `BackendRegistry` - Manages chora-compose and other backends
- `EventLog` - Provides access to gateway telemetry

---

## Step 3: Run the Workflow

**What we're doing:** Execute the Daily Report workflow with default parameters

**Instructions:**

Update your `my_first_workflow.py` to call the workflow:

```python
import asyncio
from mcp_n8n.workflows.daily_report import run_daily_report
from mcp_n8n.backends import BackendRegistry
from mcp_n8n.memory import EventLog
from pathlib import Path

async def main():
    # Initialize components
    registry = BackendRegistry()
    event_log = EventLog(base_dir=Path(".chora/memory/events"))

    print("Running Daily Report workflow...")

    # Run workflow (default: last 24 hours)
    result = await run_daily_report(
        backend_registry=registry,
        event_log=event_log,
        repo_path=".",          # Current directory
        since_hours=24          # Last 24 hours
    )

    # Display results
    print(f"\nWorkflow completed!")
    print(f"Status: {result.status}")
    print(f"Commit count: {result.commit_count}")
    print(f"Event count: {result.event_count}")
    print(f"\nReport content:\n{result.content[:500]}...")  # First 500 chars

if __name__ == "__main__":
    asyncio.run(main())
```

**Run it:**
```bash
python my_first_workflow.py
```

**Expected output:**
```
Running Daily Report workflow...

Workflow completed!
Status: success
Commit count: 5
Event count: 127

Report content:
# Daily Engineering Report - 2025-10-21

## Summary
- Commits: 5
- Events: 127
- Tool Calls: 42
- Success Rate: 95.2%...
```

**What just happened:**
- The workflow queried your git repository for commits
- It queried the event log for gateway telemetry
- It aggregated statistics (tool usage, success rates)
- It generated a formatted Markdown report
- It returned a `DailyReportResult` with metrics

---

## Step 4: Customize the Time Range

**What we're doing:** Change the time window to analyze different periods

**Instructions:**

Let's generate a report for the last 48 hours instead of 24:

```python
# Run workflow for last 48 hours
result = await run_daily_report(
    backend_registry=registry,
    event_log=event_log,
    repo_path=".",
    since_hours=48  # Extended time range
)

print(f"Report covers last 48 hours")
print(f"Commits: {result.commit_count}")
print(f"Events: {result.event_count}")
```

**Try different time ranges:**

```python
# Last 1 hour (recent activity only)
result_1h = await run_daily_report(
    backend_registry=registry,
    event_log=event_log,
    since_hours=1
)

# Last 7 days (weekly report)
result_7d = await run_daily_report(
    backend_registry=registry,
    event_log=event_log,
    since_hours=168  # 7 days * 24 hours
)
```

**Explanation:** The `since_hours` parameter controls how far back to look for commits and events. This lets you generate reports for any time window.

---

## Step 5: Handle Edge Cases

**What we're doing:** Learn how the workflow handles missing data and errors

### Scenario 1: No Recent Commits

**Situation:** Your repository has no commits in the last 24 hours

**What happens:**
```python
result = await run_daily_report(
    backend_registry=registry,
    event_log=event_log,
    since_hours=24
)

# result.commit_count = 0
# result.content will include "No commits in the last 24 hours"
```

**The workflow gracefully handles this** by:
- Setting `commit_count` to 0
- Including a "No commits" message in the report
- Still processing events and generating statistics

---

### Scenario 2: No Recent Events

**Situation:** Gateway hasn't run or no events were logged

**What happens:**
```python
# If event log is empty
result = await run_daily_report(
    backend_registry=registry,
    event_log=event_log,
    since_hours=24
)

# result.event_count = 0
# result.statistics will show zero metrics
# result.content will include "No events recorded"
```

---

### Scenario 3: Invalid Repository Path

**Situation:** Specified path is not a git repository

**What happens:**
```python
try:
    result = await run_daily_report(
        backend_registry=registry,
        event_log=event_log,
        repo_path="/nonexistent/repo",  # Invalid path
        since_hours=24
    )
except FileNotFoundError as e:
    print(f"Error: {e}")
    # Error: Git repository not found at /nonexistent/repo
```

**The workflow raises an exception** that you can catch and handle:
- `FileNotFoundError` - Path doesn't exist
- `ValueError` - Path exists but isn't a git repo
- `RuntimeError` - Git command failed

---

### Scenario 4: Complete Error Handling Example

```python
import asyncio
from mcp_n8n.workflows.daily_report import run_daily_report
from mcp_n8n.backends import BackendRegistry
from mcp_n8n.memory import EventLog
from pathlib import Path

async def run_report_safely():
    """Run daily report with comprehensive error handling."""
    try:
        # Initialize components
        registry = BackendRegistry()
        event_log = EventLog()

        # Run workflow
        result = await run_daily_report(
            backend_registry=registry,
            event_log=event_log,
            repo_path=".",
            since_hours=24
        )

        # Success path
        print(f"✓ Report generated successfully!")
        print(f"  Commits: {result.commit_count}")
        print(f"  Events: {result.event_count}")

        if result.commit_count == 0:
            print("  ⚠️  No commits found (repository might be inactive)")

        if result.event_count == 0:
            print("  ⚠️  No events found (gateway might not have run)")

        return result

    except FileNotFoundError as e:
        print(f"✗ Repository not found: {e}")
        print("  → Check that you're in a git repository")
        return None

    except ValueError as e:
        print(f"✗ Invalid repository: {e}")
        print("  → Ensure .git directory exists")
        return None

    except RuntimeError as e:
        print(f"✗ Workflow failed: {e}")
        print("  → Check logs for details")
        return None

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None

# Run it
asyncio.run(run_report_safely())
```

**Expected output (success):**
```
✓ Report generated successfully!
  Commits: 5
  Events: 127
```

**Expected output (no data):**
```
✓ Report generated successfully!
  Commits: 0
  Events: 0
  ⚠️  No commits found (repository might be inactive)
  ⚠️  No events found (gateway might not have run)
```

---

## Step 6: Inspect Workflow Statistics

**What we're doing:** Understand the statistics object returned by the workflow

**Code:**
```python
result = await run_daily_report(
    backend_registry=registry,
    event_log=event_log,
    since_hours=24
)

# Access detailed statistics
stats = result.statistics

print("Workflow Statistics:")
print(f"  Total events: {stats['total_events']}")
print(f"  Tool calls: {stats['tool_calls']}")
print(f"  Success rate: {stats['success_rate']}%")
print(f"  Avg duration: {stats.get('avg_duration_ms', 0):.2f}ms")

print("\nBy backend:")
for backend, count in stats.get('by_backend', {}).items():
    print(f"  {backend}: {count} events")
```

**Expected output:**
```
Workflow Statistics:
  Total events: 127
  Tool calls: 42
  Success rate: 95.24%
  Avg duration: 234.56ms

By backend:
  chora-composer: 38 events
  coda-mcp: 4 events
  gateway: 85 events
```

**What these metrics tell you:**
- **Total events** - How active the gateway has been
- **Tool calls** - Number of MCP tool invocations
- **Success rate** - Reliability metric (high is good)
- **Avg duration** - Performance metric (lower is better)
- **By backend** - Which backends are being used most

---

## Step 7: Save the Report to a File

**What we're doing:** Store the generated report for future reference

**Code:**
```python
import asyncio
from pathlib import Path
from datetime import datetime

async def save_daily_report():
    """Generate and save daily report."""
    # ... (initialize components as before)

    result = await run_daily_report(
        backend_registry=registry,
        event_log=event_log,
        since_hours=24
    )

    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    report_file = reports_dir / f"daily-report-{timestamp}.md"

    # Write report
    report_file.write_text(result.content)

    print(f"✓ Report saved to: {report_file}")
    print(f"  Size: {len(result.content)} characters")
    print(f"  Commits: {result.commit_count}")
    print(f"  Events: {result.event_count}")

    return report_file

# Run it
asyncio.run(save_daily_report())
```

**Expected output:**
```
✓ Report saved to: reports/daily-report-2025-10-21.md
  Size: 2847 characters
  Commits: 5
  Events: 127
```

**View the report:**
```bash
cat reports/daily-report-2025-10-21.md
```

---

## What You've Learned

Summary of skills acquired:

- ✅ You can now **run production workflows** programmatically
- ✅ You understand how to **pass parameters** to customize workflow behavior
- ✅ You know how to **handle workflow results** and extract metrics
- ✅ You can **debug workflows** by checking statistics and error messages
- ✅ You understand **edge case handling** (no data, errors, missing repos)
- ✅ You can **save workflow outputs** for later analysis

## Next Steps

Where to go from here:

- [ ] **[Tutorial: Event-Driven Workflow](event-driven-workflow.md)**: Build workflows triggered by events
- [ ] **[How-To: Build Custom Workflow](../how-to/build-custom-workflow.md)**: Create your own workflows
- [ ] **[How-To: Query Events](../how-to/query-events.md)**: Deep dive into event querying
- [ ] **[Reference: Tools](../reference/tools.md)**: Learn about available MCP tools

## Common Patterns

### Daily Automation

```python
# Schedule this to run daily via cron
async def automated_daily_report():
    """Generate and email daily report."""
    result = await run_daily_report(
        backend_registry=registry,
        event_log=event_log,
        since_hours=24
    )

    # Save to file
    Path(f"reports/daily-{datetime.now().date()}.md").write_text(result.content)

    # Email report (pseudo-code)
    # send_email(
    #     to="team@example.com",
    #     subject=f"Daily Report - {datetime.now().date()}",
    #     body=result.content
    # )
```

### Weekly Summary

```python
# Generate weekly summary every Monday
async def weekly_summary():
    """Generate 7-day summary report."""
    result = await run_daily_report(
        backend_registry=registry,
        event_log=event_log,
        since_hours=168  # 7 days
    )

    print(f"Week Summary:")
    print(f"  Total commits: {result.commit_count}")
    print(f"  Total events: {result.event_count}")
    print(f"  Avg success rate: {result.statistics['success_rate']}%")
```

### Performance Monitoring

```python
# Track performance trends over time
async def performance_monitor():
    """Monitor workflow performance over different time windows."""
    windows = [1, 6, 24, 168]  # 1h, 6h, 24h, 7d

    print("Performance by time window:")
    for hours in windows:
        result = await run_daily_report(
            backend_registry=registry,
            event_log=event_log,
            since_hours=hours
        )

        stats = result.statistics
        print(f"\nLast {hours}h:")
        print(f"  Events: {stats['total_events']}")
        print(f"  Success rate: {stats['success_rate']}%")
        print(f"  Avg duration: {stats.get('avg_duration_ms', 0):.2f}ms")
```

---

## Troubleshooting

### Problem: "chora-compose not available"

**Symptoms:**
```
RuntimeError: chora-compose not available. Install with: pip install chora-compose>=1.3.0
```

**Solution:**
```bash
pip install chora-compose>=1.3.0
```

---

### Problem: "Git repository not found"

**Symptoms:**
```
FileNotFoundError: Git repository not found at /path/to/directory
```

**Solution:**
- Ensure you're in a git repository: `git status`
- Or specify correct path: `repo_path="/path/to/repo"`

---

### Problem: No events returned

**Symptoms:** `result.event_count = 0` even though gateway has run

**Solution:**
```bash
# Check if events directory exists
ls -la .chora/memory/events/

# Verify events are being created
chora-memory query --since 24h

# Run gateway to generate events
mcp-n8n
```

---

**Source:** [src/mcp_n8n/workflows/daily_report.py](../../src/mcp_n8n/workflows/daily_report.py), [tests/features/daily_report.feature](../../tests/features/daily_report.feature)
**Test Extraction:** Yes
**Last Updated:** 2025-10-21
