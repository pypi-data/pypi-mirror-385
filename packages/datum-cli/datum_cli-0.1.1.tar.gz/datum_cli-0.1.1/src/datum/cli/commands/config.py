"""Manage datum configuration."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from datum.core.config import config_exists, load_config, save_config

console = Console()


def config_command(
    show: bool = typer.Option(
        False,
        "--show",
        help="Show current configuration",
    ),
    project_path: str | None = typer.Option(
        None,
        "--project-path",
        help="Update project path",
    ),
    profiles_path: str | None = typer.Option(
        None,
        "--profiles-path",
        help="Update profiles.yml path",
    ),
    target: str | None = typer.Option(
        None,
        "--target",
        "-t",
        help="Update dbt target",
    ),
) -> None:
    """Manage datum configuration.

    Show current configuration:
      datum dbt config --show

    Update configuration:
      datum dbt config --project-path /path/to/project
      datum dbt config --target prod
      datum dbt config --profiles-path ~/.dbt/profiles.yml

    Examples:
      # View current config
      datum dbt config --show

      # Change target
      datum dbt config --target production

      # Update project path
      datum dbt config --project-path ./my-dbt-project
    """
    console.print("\n[bold blue]Configuration[/bold blue]\n")

    # Load config
    if not config_exists():
        console.print(
            "[red]✗ No datum configuration found[/red]\n"
            "  Initialize with: [cyan]datum dbt init --repo-path .[/cyan]"
        )
        raise typer.Exit(1)

    config = load_config()

    # Show mode
    if show:
        table = Table(title="Current Configuration", show_header=False)
        table.add_column("Key", style="bold")
        table.add_column("Value", style="cyan")

        table.add_row("Project ID", config.project.project_id)
        table.add_row("Project Path", str(config.project.project_path))
        table.add_row("Profiles Path", str(config.project.profiles_path))
        table.add_row("Target", config.project.target)
        table.add_row("Private Key", str(config.private_key_path))
        table.add_row("Runs Directory", str(config.runs_dir))

        if config.schedule:
            table.add_row("Schedule", config.schedule.cron_expression)

        console.print(table)
        console.print()
        return

    # Update mode
    if not any([project_path, profiles_path, target]):
        console.print("[yellow]No updates specified[/yellow]")
        console.print("[dim]Use flags like --target, --project-path, etc.[/dim]")
        console.print("[dim]Or use --show to view configuration[/dim]\n")
        return

    # Apply updates
    if project_path:
        new_path = Path(project_path).resolve()
        if not (new_path / "dbt_project.yml").exists():
            console.print(f"[yellow]⚠ dbt_project.yml not found at {new_path}[/yellow]")
            if not typer.confirm("Continue anyway?", default=False):
                raise typer.Exit(0)
        config.project.project_path = new_path
        console.print(f"[green]✓[/green] Project path: {new_path}")

    if profiles_path:
        new_path = Path(profiles_path).expanduser().resolve()
        if not new_path.exists():
            console.print(f"[yellow]⚠ profiles.yml not found at {new_path}[/yellow]")
            if not typer.confirm("Continue anyway?", default=False):
                raise typer.Exit(0)
        config.project.profiles_path = new_path
        console.print(f"[green]✓[/green] Profiles path: {new_path}")

    if target:
        config.project.target = target
        console.print(f"[green]✓[/green] Target: {target}")

    # Save updated config
    try:
        save_config(config)
        console.print(f"\n[green]✓ Configuration updated[/green]\n")
    except Exception as e:
        console.print(f"\n[red]✗ Failed to save configuration: {e}[/red]")
        raise typer.Exit(1)
