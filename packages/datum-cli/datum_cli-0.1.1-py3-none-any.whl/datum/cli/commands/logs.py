"""View execution history and run logs."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from datum.core.config import config_exists, load_config
from datum.core.storage import RunStorage

console = Console()


def logs_command(
    run_id: str | None = typer.Argument(
        None,
        help="Specific run ID to view (omit to list recent runs)",
    ),
    last: int = typer.Option(
        10,
        "--last",
        "-n",
        help="Number of recent runs to show",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        help="Filter by status (SUCCESS, FAILED, TIMEOUT)",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        help="Show raw log output without formatting",
    ),
) -> None:
    """View execution history and detailed logs.

    List recent runs:
      datum dbt logs

    Show specific run:
      datum dbt logs abc12345

    Filter by status:
      datum dbt logs --status FAILED

    Show more runs:
      datum dbt logs --last 20

    Show raw output:
      datum dbt logs abc12345 --raw

    Examples:
      # Show last 10 runs
      datum dbt logs

      # Show last 20 runs
      datum dbt logs --last 20

      # Show only failed runs
      datum dbt logs --status FAILED

      # View specific run details
      datum dbt logs abc12345

      # View raw log output
      datum dbt logs abc12345 --raw
    """
    # Load config
    if not config_exists():
        console.print(
            "[yellow]⚠ No datum configuration found[/yellow]\n"
            "  Initialize with: [cyan]datum dbt init --repo-path .[/cyan]"
        )
        raise typer.Exit(1)

    config = load_config()
    storage = RunStorage(config.runs_dir)

    # Show details for specific run
    if run_id:
        run_record = storage.get_run(run_id)

        if not run_record:
            console.print(f"[red]✗ Run not found: {run_id}[/red]")
            raise typer.Exit(1)

        console.print(f"\n[bold blue]Run Details: {run_id}[/bold blue]\n")

        # Show metadata
        metadata_table = Table(show_header=False)
        metadata_table.add_column("Field", style="bold")
        metadata_table.add_column("Value", style="cyan")

        status_color = "green" if run_record.status == "SUCCESS" else "red"
        metadata_table.add_row("Status", f"[{status_color}]{run_record.status}[/{status_color}]")
        metadata_table.add_row("Timestamp", run_record.timestamp.isoformat())
        metadata_table.add_row("Duration", f"{run_record.duration_seconds}s")
        metadata_table.add_row("Exit Code", str(run_record.exit_code))
        metadata_table.add_row("Command", run_record.command)

        console.print(metadata_table)
        console.print()

        # Show output
        if raw:
            # Raw output
            console.print("[bold]STDOUT:[/bold]")
            if run_record.stdout:
                console.print(run_record.stdout)
            else:
                console.print("[dim]No output[/dim]")

            if run_record.stderr:
                console.print("\n[bold red]STDERR:[/bold red]")
                console.print(run_record.stderr)
        else:
            # Formatted output
            logs = storage.get_run_logs(run_id)

            if "output" in logs:
                console.print("[bold]Output:[/bold]")
                console.print(logs["output"])
            else:
                if "stdout" in logs:
                    console.print("[bold]STDOUT:[/bold]")
                    console.print(logs["stdout"])

                if "stderr" in logs:
                    console.print("\n[bold red]STDERR:[/bold red]")
                    console.print(logs["stderr"])

        # Show log file location
        run_dir = config.runs_dir / run_id
        console.print(f"\n[dim]Log files: {run_dir}[/dim]\n")

    else:
        # List recent runs
        console.print(f"\n[bold blue]Recent Runs (last {last})[/bold blue]\n")

        runs = storage.list_runs(limit=last, status_filter=status)

        if not runs:
            console.print(
                "[yellow]No runs found[/yellow]\n"
                "[dim]Run 'datum dbt run' to execute a run[/dim]\n"
            )
            raise typer.Exit(0)

        # Create table
        table = Table(show_header=True, title="Run History")
        table.add_column("Run ID", style="cyan", no_wrap=True)
        table.add_column("Timestamp", style="white")
        table.add_column("Status", style="white")
        table.add_column("Duration", style="dim")
        table.add_column("Exit Code", style="dim")

        for run in runs:
            # Color status
            if run.status == "SUCCESS":
                status_display = "[green]SUCCESS[/green]"
            elif run.status == "FAILED":
                status_display = "[red]FAILED[/red]"
            else:
                status_display = "[yellow]TIMEOUT[/yellow]"

            table.add_row(
                run.run_id[:8],
                run.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                status_display,
                f"{run.duration_seconds}s",
                str(run.exit_code),
            )

        console.print(table)
        console.print(f"\n[dim]Use 'datum dbt logs <run-id>' to view full details[/dim]\n")
