import sys

import click
from rich.console import Console

from vcp.config.config import Config

from .commands.cache import cache_command
from .commands.config import config_command
from .commands.login import login_command
from .commands.logout import logout_command
from .commands.version import version_command
from .utils.click_extensions import VCPCommandGroup, create_stub_command
from .utils.dependencies import EXTRA_DESCRIPTIONS, check_extra_dependencies
from .utils.version_check import check_for_updates_with_cache


@click.group(cls=VCPCommandGroup)
@click.pass_context
def cli(ctx):
    """VCP CLI - A command-line interface (CLI) to the Chan Zuckerberg Initiative's Virtual Cells Platform (VCP)"""
    # Check for updates on every CLI invocation (only if cache TTL expired)
    # Skip automatic check if user is explicitly running version command
    try:
        # Don't show automatic update check if user is running version command
        # Check both sys.argv (for real CLI) and Click context (for tests)

        is_version_command = (len(sys.argv) > 1 and sys.argv[1] == "version") or (
            hasattr(ctx, "invoked_subcommand") and ctx.invoked_subcommand == "version"
        )

        if is_version_command:
            return

        update_info = check_for_updates_with_cache()
        if update_info:
            is_update_available, message = update_info
            if is_update_available:
                console = Console()
                console.print(f"⚠️  {message}", style="yellow")
                console.print(
                    "   Run 'pip install --upgrade vcp-cli' to update",
                    style="dim yellow",
                )
                console.print()  # Add blank line after update notice
    except Exception:
        # Silently fail if version check has issues
        pass


config = Config.load()

cli.add_command(config_command, name="config")
cli.add_command(login_command, name="login")
cli.add_command(logout_command)
cli.add_command(cache_command, name="cache")
cli.add_command(version_command, name="version")


# Register optional commands based on feature flags and dependencies
# Commands are either registered as fully functional (if deps installed)
# or as stubs that show installation instructions (if deps missing)

if config.feature_flags.model_command:
    if check_extra_dependencies("model"):
        from .commands.model import model_command

        cli.add_command(model_command)
    else:
        # Register stub command that shows installation instructions
        cli.add_command(
            create_stub_command("model", "model", EXTRA_DESCRIPTIONS["model"])
        )

if config.feature_flags.data_command:
    if check_extra_dependencies("data"):
        from .commands.data import data_command

        cli.add_command(data_command)
    else:
        cli.add_command(create_stub_command("data", "data", EXTRA_DESCRIPTIONS["data"]))

if config.feature_flags.benchmarks_command:
    if check_extra_dependencies("benchmarks"):
        from .commands.benchmarks import benchmarks_command

        cli.add_command(benchmarks_command, name="benchmarks")
    else:
        cli.add_command(
            create_stub_command(
                "benchmarks", "benchmarks", EXTRA_DESCRIPTIONS["benchmarks"]
            )
        )


if __name__ == "__main__":
    cli()
