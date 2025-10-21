"""Custom Click extensions for VCP CLI.

This module provides custom Click components for improved command discoverability
and user experience, particularly for handling optional dependencies.
"""

import click
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel

from .dependencies import get_extra_requirements, get_install_command


class VCPCommandGroup(click.Group):
    """Custom Click Group that displays commands in sections based on availability.

    This group separates available commands from unavailable (stub) commands,
    displaying them in distinct sections in the help output. This improves
    discoverability by showing users all possible commands, even those that
    require additional installation.
    """

    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """Format commands into 'Commands' and 'Additional Commands' sections.

        Args:
            ctx: Click context
            formatter: Help formatter instance
        """
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None:
                continue

            # Get help text
            help_text = cmd.get_short_help_str(limit=60)

            # Categorize as available or stub
            is_stub = is_stub_command(cmd)
            commands.append((subcommand, cmd, help_text, is_stub))

        if not commands:
            return

        # Separate into available and unavailable
        available = [
            (name, help_text) for name, cmd, help_text, stub in commands if not stub
        ]
        unavailable = [
            (name, help_text, getattr(cmd, "__extra_name__", name))
            for name, cmd, help_text, stub in commands
            if stub
        ]

        # Format available commands section
        if available:
            with formatter.section("Commands"):
                self.format_commands_list(formatter, available)

        # Format unavailable commands section with install hints
        if unavailable:
            with formatter.section("Additional Commands (require installation)"):
                self.format_unavailable_commands(formatter, unavailable)

    def format_commands_list(
        self, formatter: click.HelpFormatter, commands: list[tuple[str, str]]
    ) -> None:
        """Format a list of commands as rows.

        Args:
            formatter: Help formatter instance
            commands: List of (name, help_text) tuples
        """
        rows = []
        for name, help_text in commands:
            rows.append((name, help_text))

        if rows:
            formatter.write_dl(rows)

    def format_unavailable_commands(
        self, formatter: click.HelpFormatter, commands: list[tuple[str, str, str]]
    ) -> None:
        """Format unavailable commands with installation hints.

        Args:
            formatter: Help formatter instance
            commands: List of (name, help_text, extra_name) tuples
        """
        rows = []
        for name, help_text, extra_name in commands:
            # Get the install command for this extra
            install_cmd = get_install_command(extra_name)
            # Format as: "command    description\n              → install command"
            combined_help = f"{help_text}\n→ {install_cmd}"
            rows.append((name, combined_help))

        if rows:
            formatter.write_dl(rows)


def create_stub_command(
    command_name: str, extra_name: str, description: str
) -> click.Command:
    """Create a stub command that shows installation instructions.

    Stub commands are placeholders for commands that require optional dependencies.
    When invoked, they display a helpful message with installation instructions
    instead of failing with an import error.

    Args:
        command_name: Name of the command (e.g., "model")
        extra_name: Name of the pip extra (e.g., "model")
        description: Short description of the command

    Returns:
        A Click command that shows installation instructions
    """

    @click.command(
        name=command_name,
        short_help=description,
        help=f"{description}\n\nThis command requires additional packages to be installed.",
    )
    @click.pass_context
    def stub_command(ctx: click.Context) -> None:
        """Display installation instructions for this feature."""
        console = Console()

        # Get requirements dynamically from package metadata
        requirements = get_extra_requirements(extra_name)
        install_cmd = get_install_command(extra_name)
        all_install_cmd = get_install_command("all")

        # Escape square brackets for Rich markup (Rich uses [] for styling)
        install_cmd_escaped = escape(install_cmd)
        all_install_cmd_escaped = escape(all_install_cmd)

        # Format requirements list
        if requirements:
            req_list = "\n".join(
                f"  • {req.name} {req.specifier}" for req in requirements
            )
        else:
            req_list = "  (requirements list unavailable)"

        # Create rich formatted panel
        message = (
            f"[yellow]The '{command_name}' command requires additional packages.[/yellow]\n\n"
            f"[bold]Install with:[/bold]\n"
            f"  $ {install_cmd_escaped}\n\n"
            f"[bold]This will install:[/bold]\n"
            f"{req_list}\n\n"
            f"[bold]Or install all features:[/bold]\n"
            f"  $ {all_install_cmd_escaped}"
        )

        console.print(
            Panel.fit(
                message,
                title="Feature Not Installed",
                border_style="yellow",
            )
        )

        ctx.exit(1)

    # Mark as stub command for identification and store extra name
    stub_command.__stub_command__ = True  # type: ignore[attr-defined]
    stub_command.__extra_name__ = extra_name  # type: ignore[attr-defined]

    return stub_command


def is_stub_command(cmd: click.Command) -> bool:
    """Check if a command is a stub command.

    Args:
        cmd: Click command to check

    Returns:
        True if the command is a stub, False otherwise
    """
    return getattr(cmd, "__stub_command__", False)
