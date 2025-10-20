"""Validate dbt project setup and datum configuration.

Provides pre-flight checks before running dbt or scheduling.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from datum.core.config import config_exists, load_config
from datum.core.validators import ProjectValidator

console = Console()


def validate_command(
    auto_fix: bool = typer.Option(
        False,
        "--auto-fix",
        help="Automatically fix any fixable issues",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed check descriptions",
    ),
) -> None:
    """Validate dbt project setup and datum configuration.

    Performs 5 pre-flight checks:
      1. dbt_project.yml exists
      2. profiles.yml exists and is valid
      3. SSH key exists
      4. SSH key has correct permissions (600)
      5. dbt target exists in profiles

    Exits with code 0 if all checks pass, 1 if any fail.
    """
    console.print("\n[bold blue]Validating datum setup...[/bold blue]\n")

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

    # Validate
    validator = ProjectValidator(config)
    issues = validator.validate_all()

    # No issues found
    if not issues:
        console.print(
            "[bold green]✓ All checks passed![/bold green]\n"
            "[dim]Your setup is ready for scheduling and execution.[/dim]\n"
        )
        raise typer.Exit(0)

    # Issues found - display them
    console.print(f"[yellow]⚠ {len(issues)} issue(s) found:[/yellow]\n")

    # Create table of issues
    table = Table(title="Validation Issues", show_header=False)
    table.add_column("", width=60, style="dim")

    for i, issue in enumerate(issues, 1):
        icon = "[red]✗[/red]" if issue.severity == "error" else "[yellow]⚠[/yellow]"
        
        # Format issue text
        issue_text = f"{icon} {issue.description}\n"
        issue_text += f"[dim]  Fix: {issue.remediation}[/dim]"
        
        if issue.auto_fix:
            issue_text += "\n[green]  (Auto-fixable)[/green]"
        
        table.add_row(issue_text)

    console.print(table)

    # Handle auto-fix
    if auto_fix:
        if validator.has_fixable_issues():
            console.print("\n[bold]Applying auto-fixes...[/bold]\n")
            fixed_count = validator.auto_fix_all()
            console.print(f"[green]✓ Fixed {fixed_count} issue(s)[/green]\n")
            
            # Re-validate after fixes
            issues_after = validator.validate_all()
            if not issues_after:
                console.print(
                    "[bold green]✓ All checks now pass![/bold green]\n"
                    "[dim]Your setup is ready.[/dim]\n"
                )
                raise typer.Exit(0)
            else:
                console.print(
                    f"[yellow]⚠ {len(issues_after)} issue(s) still remain:[/yellow]\n"
                )
                for issue in issues_after:
                    console.print(f"  {issue.description}")
                    console.print(f"  {issue.remediation}\n")
        else:
            console.print("\n[yellow]⚠ No auto-fixable issues found[/yellow]\n")
    else:
        # Show hint about auto-fix
        if validator.has_fixable_issues():
            console.print("\n[dim]Hint: Use [cyan]--auto-fix[/cyan] to fix automatically[/dim]\n")

    # Exit with error code
    raise typer.Exit(1)
