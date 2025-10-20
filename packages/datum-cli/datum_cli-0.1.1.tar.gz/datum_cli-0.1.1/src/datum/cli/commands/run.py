"""Execute dbt runs with full logging and pre-flight checks."""

import json
from pathlib import Path

import typer
from rich.console import Console

from datum.core.config import config_exists, load_config
from datum.core.executor import DbtExecutor
from datum.core.validators import ProjectValidator

console = Console()


def run_command(
    target: str | None = typer.Option(
        None,
        "--target",
        "-t",
        help="Override dbt target (defaults to config value)",
    ),
    profiles_dir: str | None = typer.Option(
        None,
        "--profiles-dir",
        help="Override profiles directory",
    ),
    vars: str | None = typer.Option(
        None,
        "--vars",
        help="dbt variables as JSON string (e.g., '{\"key\": \"value\"}')",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would run without executing",
    ),
    timeout: int = typer.Option(
        3600,
        "--timeout",
        help="Maximum execution time in seconds (default: 3600)",
    ),
    skip_validation: bool = typer.Option(
        False,
        "--skip-validation",
        help="Skip pre-flight checks (not recommended)",
    ),
) -> None:
    """Execute dbt run with full logging and real-time output.

    This command:
    - Validates project setup (unless --skip-validation)
    - Executes: dbt run --target <target> --profiles-dir <dir>
    - Streams output to terminal with timestamps
    - Saves run record to ~/.datum/runs/{run_id}/
    - Exits with dbt's exit code

    Examples:
      # Run with default config
      datum dbt run

      # Run specific target
      datum dbt run --target prod

      # Pass dbt variables
      datum dbt run --vars '{"key": "value"}'

      # Dry run to see what would execute
      datum dbt run --dry-run

      # Custom timeout (in seconds)
      datum dbt run --timeout 7200
    """
    console.print("\n[bold blue]dbt Run[/bold blue]\n")

    # Check if config exists
    if not config_exists():
        console.print(
            "[red]✗ No datum configuration found[/red]\n"
            "  Initialize with: [cyan]datum dbt init --repo-path .[/cyan]"
        )
        raise typer.Exit(1)

    # Load config
    try:
        config = load_config()
    except Exception as e:
        console.print(f"[red]✗ Failed to load configuration: {e}[/red]")
        raise typer.Exit(1)

    # Validate setup (unless skipped)
    if not skip_validation:
        console.print("[dim]Running pre-flight checks...[/dim]")
        validator = ProjectValidator(config)
        issues = validator.validate_all()

        if issues:
            console.print(f"\n[yellow]⚠ {len(issues)} validation issue(s):[/yellow]\n")
            for issue in issues:
                icon = "[red]✗[/red]" if issue.severity == "error" else "[yellow]⚠[/yellow]"
                console.print(f"  {icon} {issue.description}")
                console.print(f"     {issue.remediation}\n")

            # Allow override for power users
            if typer.confirm(
                "Continue anyway?",
                default=False,
            ):
                console.print("[yellow]Proceeding with validation issues...[/yellow]\n")
            else:
                console.print("[red]Aborted.[/red]")
                raise typer.Exit(1)
        else:
            console.print("[green]✓ All checks passed[/green]\n")

    # Parse variables if provided
    vars_dict = None
    if vars:
        try:
            vars_dict = json.loads(vars)
        except json.JSONDecodeError as e:
            console.print(f"[red]✗ Invalid JSON for --vars: {e}[/red]")
            console.print("  Example: --vars '{\"key\": \"value\"}'")
            raise typer.Exit(1)

    # Create executor
    executor = DbtExecutor(config)

    # Convert profiles_dir to Path if provided
    profiles_dir_path = Path(profiles_dir) if profiles_dir else None

    # Execute
    try:
        run_record = executor.run(
            target=target,
            profiles_dir=profiles_dir_path,
            vars_dict=vars_dict,
            timeout=timeout,
            dry_run=dry_run,
        )
    except TimeoutError:
        console.print(
            f"\n[red]✗ Execution timeout after {timeout}s[/red]\n"
            "[dim]Increase with: --timeout <seconds>[/dim]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Execution failed: {e}[/red]")
        raise typer.Exit(1)

    # Exit with dbt's exit code
    if run_record.status != "SUCCESS":
        raise typer.Exit(1)
