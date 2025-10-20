"""Main CLI entry point for datum-dbt.

This module defines the Typer app and command routing.
"""

import typer
from rich.console import Console

from datum.cli.commands import init, run, validate, logs, config
from datum.cli.commands.schedule import schedule_app

# Create console for rich output
console = Console()

# Create main Typer app
app = typer.Typer(
    name="datum",
    help="Schedule dbt projects locally with datum cloud reporting",
    add_completion=False,
    rich_markup_mode="rich",
)

# Create dbt subcommand group
dbt_app = typer.Typer(
    name="dbt",
    help="Manage dbt project scheduling and execution",
    rich_markup_mode="rich",
)

# Register dbt commands
dbt_app.command(name="init")(init.init_command)
dbt_app.command(name="validate")(validate.validate_command)
dbt_app.command(name="run")(run.run_command)
dbt_app.command(name="logs")(logs.logs_command)
dbt_app.command(name="config")(config.config_command)

# Add schedule subcommand group
dbt_app.add_typer(schedule_app, name="schedule")

# Add dbt subcommand to main app
app.add_typer(dbt_app, name="dbt")


@app.callback()
def main_callback(
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
) -> None:
    """datum - Schedule dbt projects locally with datum cloud reporting."""
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    app()
