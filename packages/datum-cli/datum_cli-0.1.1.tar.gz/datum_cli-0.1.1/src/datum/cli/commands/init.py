"""Initialize a dbt project for datum scheduling."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from datum.core.auth import generate_ssh_keypair, read_public_key
from datum.core.config import (
    DatumConfig,
    DbtProjectConfig,
    config_exists,
    save_config,
)

console = Console()


def init_command(
    repo_path: Path = typer.Option(
        Path.cwd(),
        "--repo-path",
        "-p",
        help="Path to dbt project root (containing dbt_project.yml)",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    profiles_path: Path | None = typer.Option(
        None,
        "--profiles-path",
        help="Path to profiles.yml (defaults to ~/.dbt/profiles.yml)",
        exists=True,
        file_okay=True,
        resolve_path=True,
    ),
    target: str = typer.Option(
        "dev",
        "--target",
        "-t",
        help="dbt target to use (e.g., dev, prod)",
    ),
) -> None:
    """Initialize a new dbt project for datum scheduling.

    This command:
    - Validates dbt_project.yml exists
    - Generates SSH key pair (~/.datum/keys/{project-id}.pem)
    - Creates configuration file (~/.datum/config.yaml)
    - Sets up logging directory
    """
    console.print("\n[bold blue]Initializing datum for dbt project...[/bold blue]\n")

    # Check if already initialized
    if config_exists():
        console.print(
            "[yellow]⚠ datum is already initialized for this project.[/yellow]"
        )
        if not typer.confirm("Overwrite existing configuration?", default=False):
            console.print("[red]Aborted.[/red]")
            raise typer.Exit(1)

    # Validate dbt project
    dbt_project_yml = repo_path / "dbt_project.yml"
    if not dbt_project_yml.exists():
        console.print(
            f"[red]✗[/red] No dbt_project.yml found in {repo_path}\n"
            f"  Please run this command from your dbt project root."
        )
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Found dbt_project.yml at {dbt_project_yml}")

    # Determine profiles path
    if profiles_path is None:
        profiles_path = Path.home() / ".dbt" / "profiles.yml"
        if not profiles_path.exists():
            console.print(
                f"[yellow]⚠[/yellow] profiles.yml not found at {profiles_path}"
            )
            custom_path = typer.prompt(
                "Enter path to profiles.yml (or press Enter to continue anyway)"
            )
            if custom_path:
                profiles_path = Path(custom_path).resolve()

    if profiles_path.exists():
        console.print(f"[green]✓[/green] Found profiles.yml at {profiles_path}")
    else:
        console.print(
            f"[yellow]⚠[/yellow] profiles.yml not found at {profiles_path} "
            "(you can set this later)"
        )

    # Create project config
    try:
        project_config = DbtProjectConfig(
            project_path=repo_path,
            profiles_path=profiles_path,
            target=target,
        )
    except ValueError as e:
        console.print(f"[red]✗[/red] Invalid configuration: {e}")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Project ID: {project_config.project_id}")

    # Generate SSH key pair
    console.print("\n[bold]Generating SSH key pair...[/bold]")
    key_dir = Path.home() / ".datum" / "keys"
    private_key_path = key_dir / f"{project_config.project_id}.pem"

    try:
        private_key, public_key = generate_ssh_keypair(private_key_path)
        console.print(f"[green]✓[/green] Private key: {private_key} (permissions: 600)")
        console.print(f"[green]✓[/green] Public key: {public_key}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to generate keys: {e}")
        raise typer.Exit(1)

    # Create config
    config = DatumConfig(
        project=project_config,
        private_key_path=private_key_path,
    )

    # Save config
    try:
        save_config(config)
        console.print(
            f"\n[green]✓[/green] Configuration saved to ~/.datum/config.yaml"
        )
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to save configuration: {e}")
        raise typer.Exit(1)

    # Create runs directory
    config.runs_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Runs directory: {config.runs_dir}")

    # Show public key for cloud setup (future)
    public_key_content = read_public_key(public_key)
    
    console.print("\n" + "="*70)
    console.print(Panel.fit(
        public_key_content,
        title="[bold]Your Public Key[/bold]",
        subtitle="Save this for datum cloud integration",
        border_style="green",
    ))
    console.print("="*70)

    # Next steps
    console.print("\n[bold green]✓ Initialization complete![/bold green]\n")
    console.print("[bold]Next steps:[/bold]")
    console.print("  1. Run [cyan]datum dbt validate[/cyan] to check your setup")
    console.print("  2. Test with [cyan]datum dbt run[/cyan]")
    console.print("  3. Schedule with [cyan]datum dbt schedule --cron '0 10 * * *'[/cyan]\n")
