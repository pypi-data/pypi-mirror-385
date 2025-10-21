"""Commands module for the VCP CLI."""

# Core commands (always available)
from .config import config_command
from .login import login_command
from .logout import logout_command

# Optional commands (model, data, benchmarks) are imported conditionally in cli.py
# to avoid loading their dependencies when not installed

__all__ = [
    "login_command",
    "logout_command",
    "config_command",
]
