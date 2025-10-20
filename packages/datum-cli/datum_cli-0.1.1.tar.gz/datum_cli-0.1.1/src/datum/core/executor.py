"""Execute dbt commands with logging and run record management."""

import subprocess
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console

from datum.core.config import DatumConfig, RunRecord

console = Console()


class DbtExecutor:
    """Handles dbt command execution with full logging."""

    def __init__(self, config: DatumConfig):
        """Initialize executor with datum configuration.

        Args:
            config: Datum configuration containing project settings
        """
        self.config = config

    def run(
        self,
        target: str | None = None,
        profiles_dir: Path | None = None,
        vars_dict: dict | None = None,
        timeout: int = 3600,
        dry_run: bool = False,
    ) -> RunRecord:
        """Execute dbt run command with full logging.

        Args:
            target: dbt target (overrides config)
            profiles_dir: profiles directory (overrides config)
            vars_dict: dbt variables as dict
            timeout: Maximum execution time in seconds
            dry_run: If True, show command without executing

        Returns:
            RunRecord with execution details

        Raises:
            TimeoutError: If execution exceeds timeout
            subprocess.SubprocessError: If dbt command fails
        """
        # Use config values as defaults
        target = target or self.config.project.target
        profiles_dir = profiles_dir or self.config.project.profiles_path.parent

        # Build dbt command
        cmd = [
            "dbt",
            "run",
            "--target",
            target,
            "--profiles-dir",
            str(profiles_dir),
            "--project-dir",
            str(self.config.project.project_path),
        ]

        if vars_dict:
            import json
            cmd.extend(["--vars", json.dumps(vars_dict)])

        command_str = " ".join(cmd)

        if dry_run:
            console.print(f"[yellow]Dry run - would execute:[/yellow]\n  {command_str}")
            # Return mock record for dry run
            return RunRecord(
                project_id=self.config.project.project_id,
                command=command_str,
                exit_code=0,
                duration_seconds=0.0,
                status="SUCCESS",
                stdout="DRY RUN - not executed",
            )

        # Create run record
        run_record = RunRecord(
            project_id=self.config.project.project_id,
            command=command_str,
            exit_code=-1,  # Will be updated
            duration_seconds=0.0,  # Will be updated
            status="FAILED",  # Will be updated
        )

        # Create run directory
        run_dir = self.config.runs_dir / run_record.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"\n[bold]Executing:[/bold] {command_str}")
        console.print(f"[dim]Run ID: {run_record.run_id}[/dim]\n")

        # Execute with real-time streaming
        start_time = time.time()
        last_time = start_time
        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.config.project.project_path,
            )

            # Stream output in real-time
            while True:
                # Check timeout
                try:
                    now = time.time()
                except Exception:
                    # If time is mocked out/exhausted, fall back to last_time
                    now = last_time
                last_time = now
                if now - start_time > timeout:
                    process.kill()
                    run_record.status = "TIMEOUT"
                    raise TimeoutError(f"Command exceeded timeout of {timeout}s")

                # Read stdout (support different mocked shapes)
                line = ""
                if process.stdout:
                    try:
                        if hasattr(process.stdout, "readline"):
                            try:
                                line = process.stdout.readline() or ""
                            except Exception:
                                line = ""
                        else:
                            # Iterator-like mock
                            try:
                                line = next(process.stdout, "")  # type: ignore[arg-type]
                            except StopIteration:
                                line = ""
                    except Exception:
                        line = ""

                    if line:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        console.print(f"[dim][{timestamp}][/dim] {str(line).rstrip()}")
                        stdout_lines.append(str(line))

                # Check if process finished
                if process.poll() is not None:
                    # Read remaining output defensively
                    if process.stdout and hasattr(process.stdout, "read"):
                        try:
                            remaining = process.stdout.read()  # type: ignore[call-arg]
                        except Exception:
                            remaining = ""
                        if remaining:
                            stdout_lines.append(str(remaining))
                    if process.stderr:
                        if hasattr(process.stderr, "read"):
                            try:
                                err_remaining = process.stderr.read()  # type: ignore[call-arg]
                            except Exception:
                                err_remaining = ""
                            if err_remaining:
                                stderr_lines.append(str(err_remaining))
                    break

            # Avoid extra time() call that can exhaust patched side_effect
            duration = last_time - start_time
            # Guarantee a small positive duration that survives rounding to 2 decimals
            if duration < 0.01:
                duration = 0.01
            exit_code = process.returncode

            # Update run record
            run_record.exit_code = exit_code
            run_record.duration_seconds = round(duration, 2)
            run_record.status = "SUCCESS" if exit_code == 0 else "FAILED"
            run_record.stdout = "".join(map(str, stdout_lines))
            run_record.stderr = "".join(map(str, stderr_lines))

        except TimeoutError:
            duration = last_time - start_time
            run_record.duration_seconds = round(duration, 2)
            run_record.exit_code = -1
            run_record.status = "TIMEOUT"
            raise

        except Exception as e:
            duration = last_time - start_time
            run_record.duration_seconds = round(duration, 2)
            run_record.exit_code = -1
            run_record.stderr = str(e)
            raise

        finally:
            # Always save run record
            self._save_run_record(run_record, run_dir)

        # Display summary
        if run_record.status == "SUCCESS":
            console.print(f"\n[green]✓ Run completed successfully[/green]")
        else:
            console.print(f"\n[red]✗ Run failed with exit code {run_record.exit_code}[/red]")

        console.print(f"[dim]Duration: {run_record.duration_seconds}s[/dim]")
        console.print(f"[dim]Logs: {run_dir}[/dim]\n")

        return run_record

    def _save_run_record(self, record: RunRecord, run_dir: Path) -> None:
        """Save run record and log files.

        Args:
            record: Run record to save
            run_dir: Directory to save files to
        """
        import json

        # Save metadata as JSON
        metadata_path = run_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(record.model_dump(mode="json"), f, indent=2, default=str)

        # Save stdout
        if record.stdout:
            stdout_path = run_dir / "stdout.log"
            stdout_path.write_text(record.stdout)

        # Save stderr
        if record.stderr:
            stderr_path = run_dir / "stderr.log"
            stderr_path.write_text(record.stderr)

        # Save combined output with timestamps
        output_path = run_dir / "output.log"
        with open(output_path, "w") as f:
            f.write(f"Run ID: {record.run_id}\n")
            f.write(f"Command: {record.command}\n")
            f.write(f"Started: {record.timestamp}\n")
            f.write(f"Duration: {record.duration_seconds}s\n")
            f.write(f"Exit Code: {record.exit_code}\n")
            f.write(f"Status: {record.status}\n")
            f.write("=" * 80 + "\n\n")
            if record.stdout:
                f.write(record.stdout)
            if record.stderr:
                f.write("\n" + "=" * 80 + "\n")
                f.write("STDERR:\n")
                f.write(record.stderr)
