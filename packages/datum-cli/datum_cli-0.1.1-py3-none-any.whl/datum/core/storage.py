"""Storage and retrieval of run records."""

import json
from pathlib import Path

from datum.core.config import RunRecord


class RunStorage:
    """Handles saving and loading run records from filesystem."""

    def __init__(self, runs_dir: Path):
        """Initialize storage with runs directory.

        Args:
            runs_dir: Directory where run records are stored
        """
        self.runs_dir = runs_dir
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def get_run(self, run_id: str) -> RunRecord | None:
        """Load a specific run record by ID.

        Args:
            run_id: Run ID to load

        Returns:
            RunRecord if found, None otherwise
        """
        metadata_path = self.runs_dir / run_id / "metadata.json"
        
        if not metadata_path.exists():
            return None

        with open(metadata_path, "r") as f:
            data = json.load(f)

        return RunRecord.model_validate(data)

    def list_runs(
        self,
        limit: int = 10,
        status_filter: str | None = None,
    ) -> list[RunRecord]:
        """List recent run records.

        Args:
            limit: Maximum number of runs to return
            status_filter: Filter by status (SUCCESS, FAILED, TIMEOUT)

        Returns:
            List of RunRecords sorted by timestamp (newest first)
        """
        runs = []

        # Iterate through run directories
        for run_dir in self.runs_dir.iterdir():
            if not run_dir.is_dir():
                continue

            metadata_path = run_dir / "metadata.json"
            if not metadata_path.exists():
                continue

            try:
                with open(metadata_path, "r") as f:
                    data = json.load(f)
                
                record = RunRecord.model_validate(data)
                
                # Apply status filter
                if status_filter and record.status != status_filter:
                    continue

                runs.append(record)
            except Exception:
                # Skip corrupted records
                continue

        # Sort by timestamp (newest first)
        runs.sort(key=lambda r: r.timestamp, reverse=True)

        return runs[:limit]

    def get_run_logs(self, run_id: str) -> dict[str, str]:
        """Get all log files for a run.

        Args:
            run_id: Run ID to get logs for

        Returns:
            Dict with keys: stdout, stderr, output (combined)
        """
        run_dir = self.runs_dir / run_id
        logs = {}

        stdout_path = run_dir / "stdout.log"
        if stdout_path.exists():
            logs["stdout"] = stdout_path.read_text()

        stderr_path = run_dir / "stderr.log"
        if stderr_path.exists():
            logs["stderr"] = stderr_path.read_text()

        output_path = run_dir / "output.log"
        if output_path.exists():
            logs["output"] = output_path.read_text()

        return logs

    def delete_run(self, run_id: str) -> bool:
        """Delete a run record and all associated files.

        Args:
            run_id: Run ID to delete

        Returns:
            True if deleted, False if not found
        """
        run_dir = self.runs_dir / run_id

        if not run_dir.exists():
            return False

        import shutil
        shutil.rmtree(run_dir)
        return True

    def cleanup_old_runs(self, keep_last: int = 100) -> int:
        """Delete old run records, keeping only the most recent.

        Args:
            keep_last: Number of most recent runs to keep

        Returns:
            Number of runs deleted
        """
        all_runs = self.list_runs(limit=999999)  # Get all runs

        if len(all_runs) <= keep_last:
            return 0

        runs_to_delete = all_runs[keep_last:]
        deleted_count = 0

        for run in runs_to_delete:
            if self.delete_run(run.run_id):
                deleted_count += 1

        return deleted_count
