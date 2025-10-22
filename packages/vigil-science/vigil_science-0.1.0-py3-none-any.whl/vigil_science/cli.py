"""
Vigil Science CLI Entry Point

This module provides a unified CLI that combines vigil-core and vigil-client commands.
"""

import sys
import importlib.util
import typer

# Load vigil-core CLI dynamically to avoid circular imports
spec = importlib.util.find_spec("vigil.cli.__main__")
if spec and spec.origin:
    # Import from the installed vigil-core package
    vigil_core_module = importlib.util.module_from_spec(spec)
    sys.modules["vigil.cli.__main__"] = vigil_core_module
    spec.loader.exec_module(vigil_core_module)
    app = vigil_core_module.app
else:
    # Fallback: create a basic Typer app
    app = typer.Typer(help="Vigil CLI: observable, collaborative, reproducible science.")

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
        set_remote,
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
    app.command("config-set-remote")(set_remote)

except ImportError:
    # Platform commands not available if vigil-client is not installed
    pass

if __name__ == "__main__":
    app()
