"""Main CLI entry point for chora-memory command."""

import click

from mcp_n8n.cli import commands


@click.group()
@click.version_option()
def cli() -> None:
    """Chora Memory - Agent memory system CLI.

    Query events, search knowledge, manage agent profiles.
    """
    pass


# Register command groups
cli.add_command(commands.query)
cli.add_command(commands.trace)
cli.add_command(commands.knowledge)
cli.add_command(commands.stats)
cli.add_command(commands.profile)


if __name__ == "__main__":
    cli()
