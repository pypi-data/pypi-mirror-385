import importlib.metadata
import sys

import click
from testpulcli.utils.help import RecursiveHelpGroup

# Import the new command groups
from testpulcli.cli.auth import auth
from testpulcli.cli.key import key
from testpulcli.cli.pool import pool
from testpulcli.cli.wallet import wallet

@click.group(invoke_without_command=True)
@click.option("-v", "--version", "show_version", is_flag=True, help="Show version and exit")
@click.option("--commands", is_flag=True, help="Show available commands and exit")
@click.pass_context
def cli(ctx, show_version: bool, commands: bool) -> None:
    """
    🌊 testpulcli: A CLI for managing Bittensor subnet pool operations.
    """
    if show_version:
        click.echo("This is for test purposes only!")
        click.echo(f"testpulcli {importlib.metadata.version('testpulcli')}")
        ctx.exit(0)
    elif commands:
        # Temporarily use RecursiveHelpGroup for recursive help
        original_cls = cli.__class__
        try:
            cli.__class__ = RecursiveHelpGroup
            click.echo(cli.get_help(ctx))
        finally:
            cli.__class__ = original_cls
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)

# Register the command groups with the main CLI
cli.add_command(auth)
cli.add_command(wallet)
cli.add_command(key)
cli.add_command(pool)

if __name__ == "__main__":
    try:
        cli(standalone_mode=False)
    except SystemExit:
        sys.exit(0)