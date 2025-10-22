"""
Vigil Science CLI Entry Point

This module provides a unified CLI that combines vigil-core and vigil-client commands.
"""

import sys
import importlib.util
import typer
from vigil_science import __version__

# Create our own CLI app instead of importing vigil-core's
app = typer.Typer(
    name="vigil",
    help="Vigil Science: Complete reproducible science platform",
    add_completion=False,
    no_args_is_help=True,
)

# Add version callback
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit")
):
    """Vigil Science: Complete reproducible science platform"""
    if version:
        typer.echo(f"Vigil Science version {__version__}")
        raise typer.Exit()
    elif ctx.invoked_subcommand is None:
        typer.echo("Vigil Science: Complete reproducible science platform")
        typer.echo("Use 'vigil --help' for available commands.")

# Load vigil-core commands dynamically
try:
    # Import vigil-core commands directly
    from vigil.tools.promote import main as promote_command
    from vigil.tools.signing import generate_keypair
    from vigil.tools.doctor import main as doctor_command

    # For modules without main functions, use their cli functions
    from vigil.tools.verify import verify_attestation as verify_command
    from vigil.tools.export import cli as export_command
    from vigil.tools.env import cli as env_command

    app.command("promote")(promote_command)
    app.command("verify")(verify_command)
    app.command("keygen")(generate_keypair)
    app.command("export")(export_command)
    app.command("env")(env_command)
    app.command("doctor")(doctor_command)

except ImportError as e:
    # vigil-core not available
    pass
except Exception as e:
    # Error loading core commands
    pass

# Import platform commands from vigil-client
try:
    from vigil_client.cli.platform_app import (
        login_command,
        logout,
        whoami,
        push_command,
        pull_command,
        link_command,
        list_artifacts,
        get_artifact,
        search_artifacts,
        get_config,
        set_project,
    )

    # Add platform commands to the main app
    app.command("login")(login_command)
    app.command("logout")(logout)
    app.command("whoami")(whoami)
    app.command("push")(push_command)
    app.command("pull")(pull_command)
    app.command("link")(link_command)
    app.command("artifacts")(list_artifacts)
    app.command("artifacts-get")(get_artifact)
    app.command("artifacts-search")(search_artifacts)
    app.command("config")(get_config)
    app.command("config-set")(set_project)

except ImportError:
    # Platform commands not available if vigil-client is not installed
    pass

if __name__ == "__main__":
    app()
