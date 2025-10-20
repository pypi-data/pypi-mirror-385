"""Manage dbt scheduling via cron or webhook."""

from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from datum.core.config import config_exists, load_config, save_config, ScheduleConfig
from datum.core.scheduler import CronScheduler

console = Console()

# Create schedule subcommand group
schedule_app = typer.Typer(help="Manage dbt scheduling")


@schedule_app.command(name="cron")
def add_cron_schedule(
    cron: str = typer.Option(
        ...,
        "--expr",
        "-e",
        help="Cron expression (e.g., '0 10 * * *' for daily 10 AM)",
    ),
    target: str | None = typer.Option(
        None,
        "--target",
        "-t",
        help="dbt target (defaults to config value)",
    ),
    project_dir: Path | None = typer.Option(
        None,
        "--project-dir",
        help="dbt project directory (defaults to config value)",
    ),
) -> None:
    """Add a cron-based schedule for dbt runs.

    Examples:
      # Every day at 10 AM
      datum dbt schedule cron --expr "0 10 * * *"

      # Every Monday at 9 AM
      datum dbt schedule cron --expr "0 9 * * 1"

      # Every 5 minutes
      datum dbt schedule cron --expr "*/5 * * * *"

      # With specific target
      datum dbt schedule cron --expr "0 10 * * *" --target prod
    """
    console.print("\n[bold blue]Adding cron schedule...[/bold blue]\n")

    # Load config
    if not config_exists():
        console.print(
            "[red]✗ No datum configuration found[/red]\n"
            "  Initialize with: [cyan]datum dbt init --repo-path .[/cyan]"
        )
        raise typer.Exit(1)

    config = load_config()

    # Validate cron expression
    scheduler = CronScheduler(config.project.project_id)
    if not scheduler.validate_expression(cron):
        console.print(
            f"[red]✗ Invalid cron expression:[/red] {cron}\n"
            "Examples:\n"
            "  0 10 * * *     = Every day at 10:00 AM\n"
            "  */5 * * * *    = Every 5 minutes\n"
            "  0 0 1 * *      = First day of month at midnight\n"
            "  0 9 * * 1      = Every Monday at 9:00 AM\n"
            "See: https://crontab.guru"
        )
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Valid cron expression: {cron}\n")

    # Use config target if not specified
    target = target or config.project.target
    project_dir = project_dir or config.project.project_path

    # Build command
    cmd = f"/usr/local/bin/datum dbt run --project-dir {project_dir}"
    if target != config.project.target:
        cmd += f" --target {target}"

    # Show preview
    console.print("[bold]Crontab Entry:[/bold]")
    console.print(f"  {cron} {cmd}\n")

    if not typer.confirm("Add this schedule?", default=True):
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(0)

    # Add to crontab
    try:
        scheduler.add_schedule(cron, cmd)
        console.print("[green]✓ Schedule added to crontab[/green]\n")
    except Exception as e:
        console.print(f"[red]✗ Failed to add schedule: {e}[/red]")
        raise typer.Exit(1)

    # Update config
    config.schedule = ScheduleConfig(cron_expression=cron)
    try:
        save_config(config)
        console.print("[green]✓ Configuration updated[/green]\n")
    except Exception as e:
        console.print(f"[red]✗ Failed to update config: {e}[/red]")
        raise typer.Exit(1)

    # Show next run time
    next_run = scheduler.get_next_run()
    if next_run:
        console.print(
            Panel.fit(
                f"[cyan]{next_run.strftime('%Y-%m-%d %H:%M:%S')}[/cyan]",
                title="Next Scheduled Run",
                border_style="green",
            )
        )

    console.print("[dim]View schedule: datum dbt schedule status[/dim]\n")


@schedule_app.command(name="status")
def show_schedule_status() -> None:
    """Show current schedule status.

    Displays:
      - Current cron expression (if scheduled)
      - Next scheduled run time
      - Command that will execute
    """
    console.print("\n[bold blue]Schedule Status[/bold blue]\n")

    # Load config
    if not config_exists():
        console.print(
            "[yellow]⚠ No datum configuration found[/yellow]\n"
            "  Initialize with: [cyan]datum dbt init --repo-path .[/cyan]"
        )
        raise typer.Exit(1)

    config = load_config()
    scheduler = CronScheduler(config.project.project_id)

    # Check if scheduled
    if not scheduler.is_scheduled():
        console.print(
            "[yellow]Not scheduled[/yellow]\n"
            "[dim]Add a schedule with:[/dim]\n"
            "  datum dbt schedule cron --expr '0 10 * * *'"
        )
        raise typer.Exit(0)

    # Show schedule table
    table = Table(show_header=False)
    table.add_column("Label", style="bold")
    table.add_column("Value", style="cyan")

    project_id = config.project.project_id
    cron_expr = scheduler.get_cron_expression()
    command = scheduler.get_scheduled_command()
    next_run = scheduler.get_next_run()
    last_run = scheduler.get_last_run_from_cron()

    table.add_row("Project", project_id)

    if cron_expr:
        table.add_row("Cron Expression", cron_expr)

    if command:
        table.add_row("Command", command)

    if next_run:
        table.add_row("Next Run", next_run.strftime("%Y-%m-%d %H:%M:%S"))

    if last_run:
        table.add_row("Previous Run", last_run.strftime("%Y-%m-%d %H:%M:%S"))

    console.print(table)
    console.print()


@schedule_app.command(name="remove")
def remove_schedule(
    confirm: bool = typer.Option(
        False,
        "--confirm",
        "-y",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Remove the current schedule.

    This will delete the cron entry and clear schedule configuration.
    """
    console.print("\n[bold blue]Removing schedule...[/bold blue]\n")

    # Load config
    if not config_exists():
        console.print(
            "[yellow]⚠ No datum configuration found[/yellow]\n"
            "  Initialize with: [cyan]datum dbt init --repo-path .[/cyan]"
        )
        raise typer.Exit(1)

    config = load_config()
    scheduler = CronScheduler(config.project.project_id)

    # Check if scheduled
    if not scheduler.is_scheduled():
        console.print("[yellow]⚠ No schedule found[/yellow]\n")
        raise typer.Exit(0)

    # Show what will be removed
    cron_expr = scheduler.get_cron_expression()
    command = scheduler.get_scheduled_command()

    console.print("[yellow]Will remove:[/yellow]")
    if cron_expr:
        console.print(f"  Cron: {cron_expr}")
    if command:
        console.print(f"  Command: {command}\n")

    if not confirm and not typer.confirm("Continue?", default=False):
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(0)

    # Remove from crontab
    try:
        scheduler.remove_schedule()
        console.print("[green]✓ Removed from crontab[/green]\n")
    except Exception as e:
        console.print(f"[red]✗ Failed to remove schedule: {e}[/red]")
        raise typer.Exit(1)

    # Update config
    config.schedule = None
    try:
        save_config(config)
        console.print("[green]✓ Configuration updated[/green]\n")
    except Exception as e:
        console.print(f"[red]✗ Failed to update config: {e}[/red]")
        raise typer.Exit(1)

    console.print("[dim]Schedule removed successfully[/dim]\n")


def schedule_command() -> None:
    """Manage dbt scheduling (cron or webhook)."""
    pass


# Wire up subcommands to main schedule_command
schedule_app.command(name="cron")(add_cron_schedule)
schedule_app.command(name="status")(show_schedule_status)
schedule_app.command(name="remove")(remove_schedule)
