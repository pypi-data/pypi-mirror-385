"""CLI entry point for daily report workflow.

Usage:
    python -m mcp_n8n.workflows.daily_report
    python -m mcp_n8n.workflows.daily_report --date 2025-10-19
    python -m mcp_n8n.workflows.daily_report --since-hours 48
    python -m mcp_n8n.workflows.daily_report --format html

NOTE: This CLI is a legacy interface. The workflow now requires backend_registry
and event_log parameters. This CLI needs to be updated to work with the new API.
"""
# mypy: disable-error-code="no-untyped-def,index,call-arg"

import argparse
import asyncio
import logging
import sys

from mcp_n8n.workflows.daily_report import run_daily_report


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate daily engineering report from git commits and " "gateway events"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report for today
  python -m mcp_n8n.workflows.daily_report

  # Generate report for specific date
  python -m mcp_n8n.workflows.daily_report --date 2025-10-19

  # Generate report with 48-hour time range
  python -m mcp_n8n.workflows.daily_report --since-hours 48

  # Generate HTML format output
  python -m mcp_n8n.workflows.daily_report --format html

  # Specify custom repository path
  python -m mcp_n8n.workflows.daily_report --repository /path/to/repo

Exit Codes:
  0  Success - Report generated
  1  Failure - Git repository error
  2  Failure - Chora-compose not available
  3  Failure - Invalid parameters
  4  Failure - Event log access error
""",
    )

    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="ISO date string for report (YYYY-MM-DD). Default: today",
    )

    parser.add_argument(
        "--repository",
        "--repo",
        type=str,
        default=None,
        help="Path to git repository. Default: current directory",
    )

    parser.add_argument(
        "--since-hours",
        type=int,
        default=24,
        help="Hours to look back for commits and events. Default: 24",
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "html"],
        default="markdown",
        help="Output format. Default: markdown",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


async def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    setup_logging(verbose=args.verbose)

    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting daily report generation...")
        logger.debug(f"Arguments: {vars(args)}")

        # Run workflow
        result = await run_daily_report(
            date=args.date,
            repository_path=args.repository,
            since_hours=args.since_hours,
            output_format=args.format,
        )

        # Handle result
        if result["status"] == "success":
            # Print report path to stdout
            print("✅ Report generated successfully!")
            print(f"📄 Report path: {result['report_path']}")
            print()

            # Print summary statistics
            summary = result["summary"]
            print("📊 Summary:")
            print(f"  - Commits: {summary['commit_count']}")
            print(f"  - Events: {summary['event_count']}")
            print(f"  - Tool Calls: {summary['tool_calls']}")
            print(f"  - Success Rate: {summary['success_rate']:.1f}%")
            print(f"  - Backends: {', '.join(summary['backends_active']) or 'none'}")

            return 0

        else:
            # Print error to stderr
            error = result["error"] or "Unknown error"
            print("❌ Report generation failed!", file=sys.stderr)
            print(f"Error: {error}", file=sys.stderr)

            # Determine exit code based on error type
            if "repository not found" in error.lower():
                return 1
            elif "chora" in error.lower():
                return 2
            elif "event log" in error.lower():
                return 4
            else:
                return 1

    except ValueError as e:
        # Invalid parameters
        print(f"❌ Invalid parameters: {e}", file=sys.stderr)
        return 3

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        return 130  # Standard exit code for Ctrl+C

    except Exception as e:
        # Unexpected error
        logger.exception("Unexpected error")
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
