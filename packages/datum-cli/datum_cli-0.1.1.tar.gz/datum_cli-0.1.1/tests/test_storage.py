"""Tests for run record storage and retrieval."""

import pytest
from datetime import datetime, timedelta

from datum.core.storage import RunStorage
from datum.core.config import RunRecord


class TestRunStorage:
    """Test run storage functionality."""

    def test_get_run_exists(self, test_config, mock_run_record, tmp_path):
        """Should retrieve existing run record."""
        storage = RunStorage(tmp_path / "runs")

        # Save run
        run_dir = tmp_path / "runs" / mock_run_record.run_id
        run_dir.mkdir(parents=True)
        import json
        (run_dir / "metadata.json").write_text(
            json.dumps(mock_run_record.model_dump(mode="json"), default=str)
        )

        # Retrieve
        run = storage.get_run(mock_run_record.run_id)
        assert run is not None
        assert run.run_id == mock_run_record.run_id
        assert run.status == "SUCCESS"

    def test_get_run_not_exists(self, tmp_path):
        """Should return None for nonexistent run."""
        storage = RunStorage(tmp_path / "runs")
        run = storage.get_run("nonexistent")
        assert run is None

    def test_list_runs_empty(self, tmp_path):
        """Should return empty list when no runs exist."""
        storage = RunStorage(tmp_path / "runs")
        runs = storage.list_runs()
        assert runs == []

    def test_list_runs_returns_recent(self, test_config, tmp_path):
        """Should return runs sorted by timestamp (newest first)."""
        from datum.core.config import RunRecord

        storage = RunStorage(tmp_path / "runs")

        # Create 3 runs with different timestamps
        import json
        for i in range(3):
            run = RunRecord(
                run_id=f"run{i}",
                project_id=test_config.project.project_id,
                timestamp=datetime.now() - timedelta(hours=i),
                command="dbt run",
                exit_code=0,
                duration_seconds=10.0,
                status="SUCCESS",
            )

            run_dir = tmp_path / "runs" / run.run_id
            run_dir.mkdir(parents=True)
            (run_dir / "metadata.json").write_text(
                json.dumps(run.model_dump(mode="json"), default=str)
            )

        # Retrieve
        runs = storage.list_runs(limit=10)
        assert len(runs) == 3
        # Newest first
        assert runs[0].run_id == "run0"
        assert runs[1].run_id == "run1"
        assert runs[2].run_id == "run2"

    def test_list_runs_respects_limit(self, test_config, tmp_path):
        """Should respect limit parameter."""
        from datum.core.config import RunRecord

        storage = RunStorage(tmp_path / "runs")

        # Create 5 runs
        import json
        for i in range(5):
            run = RunRecord(
                run_id=f"run{i}",
                project_id=test_config.project.project_id,
                timestamp=datetime.now(),
                command="dbt run",
                exit_code=0,
                duration_seconds=10.0,
                status="SUCCESS",
            )

            run_dir = tmp_path / "runs" / run.run_id
            run_dir.mkdir(parents=True)
            (run_dir / "metadata.json").write_text(
                json.dumps(run.model_dump(mode="json"), default=str)
            )

        # Retrieve with limit
        runs = storage.list_runs(limit=2)
        assert len(runs) == 2

    def test_list_runs_filter_by_status(self, test_config, tmp_path):
        """Should filter runs by status."""
        from datum.core.config import RunRecord

        storage = RunStorage(tmp_path / "runs")

        # Create success and failed runs
        import json
        for i, status in enumerate(["SUCCESS", "FAILED", "SUCCESS"]):
            run = RunRecord(
                run_id=f"run{i}",
                project_id=test_config.project.project_id,
                timestamp=datetime.now(),
                command="dbt run",
                exit_code=0 if status == "SUCCESS" else 1,
                duration_seconds=10.0,
                status=status,
            )

            run_dir = tmp_path / "runs" / run.run_id
            run_dir.mkdir(parents=True)
            (run_dir / "metadata.json").write_text(
                json.dumps(run.model_dump(mode="json"), default=str)
            )

        # Filter for failed only
        runs = storage.list_runs(limit=10, status_filter="FAILED")
        assert len(runs) == 1
        assert runs[0].status == "FAILED"

    def test_get_run_logs(self, test_config, tmp_path):
        """Should retrieve all log files."""
        from datum.core.config import RunRecord

        storage = RunStorage(tmp_path / "runs")

        run_id = "test-logs"
        run_dir = tmp_path / "runs" / run_id
        run_dir.mkdir(parents=True)

        # Create log files
        (run_dir / "stdout.log").write_text("standard output")
        (run_dir / "stderr.log").write_text("error output")
        (run_dir / "output.log").write_text("combined output")

        # Retrieve
        logs = storage.get_run_logs(run_id)
        assert logs["stdout"] == "standard output"
        assert logs["stderr"] == "error output"
        assert logs["output"] == "combined output"

    def test_get_run_logs_partial(self, tmp_path):
        """Should handle missing log files gracefully."""
        storage = RunStorage(tmp_path / "runs")

        run_id = "partial-logs"
        run_dir = tmp_path / "runs" / run_id
        run_dir.mkdir(parents=True)

        # Create only stdout
        (run_dir / "stdout.log").write_text("output")

        # Retrieve
        logs = storage.get_run_logs(run_id)
        assert "stdout" in logs
        assert "stderr" not in logs
        assert "output" not in logs

    def test_delete_run(self, test_config, tmp_path):
        """Should delete run directory."""
        from datum.core.config import RunRecord

        storage = RunStorage(tmp_path / "runs")

        run_id = "delete-me"
        run_dir = tmp_path / "runs" / run_id
        run_dir.mkdir(parents=True)
        (run_dir / "metadata.json").write_text("{}")

        # Delete
        result = storage.delete_run(run_id)
        assert result is True
        assert not run_dir.exists()

    def test_delete_run_not_exists(self, tmp_path):
        """Should return False when run doesn't exist."""
        storage = RunStorage(tmp_path / "runs")
        result = storage.delete_run("nonexistent")
        assert result is False

    def test_cleanup_old_runs(self, test_config, tmp_path):
        """Should delete old runs keeping most recent."""
        from datum.core.config import RunRecord

        storage = RunStorage(tmp_path / "runs")

        # Create 5 runs with staggered times
        import json
        for i in range(5):
            run = RunRecord(
                run_id=f"run{i}",
                project_id=test_config.project.project_id,
                timestamp=datetime.now() - timedelta(hours=i),
                command="dbt run",
                exit_code=0,
                duration_seconds=10.0,
                status="SUCCESS",
            )

            run_dir = tmp_path / "runs" / run.run_id
            run_dir.mkdir(parents=True)
            (run_dir / "metadata.json").write_text(
                json.dumps(run.model_dump(mode="json"), default=str)
            )

        # Keep only 2 most recent
        deleted = storage.cleanup_old_runs(keep_last=2)
        assert deleted == 3

        # Verify only 2 remain
        runs = storage.list_runs(limit=10)
        assert len(runs) == 2

    def test_cleanup_old_runs_keep_all(self, test_config, tmp_path):
        """Should not delete if within keep threshold."""
        from datum.core.config import RunRecord

        storage = RunStorage(tmp_path / "runs")

        # Create 3 runs
        import json
        for i in range(3):
            run = RunRecord(
                run_id=f"run{i}",
                project_id=test_config.project.project_id,
                timestamp=datetime.now(),
                command="dbt run",
                exit_code=0,
                duration_seconds=10.0,
                status="SUCCESS",
            )

            run_dir = tmp_path / "runs" / run.run_id
            run_dir.mkdir(parents=True)
            (run_dir / "metadata.json").write_text(
                json.dumps(run.model_dump(mode="json"), default=str)
            )

        # Keep 5 (more than we have)
        deleted = storage.cleanup_old_runs(keep_last=5)
        assert deleted == 0

        # All should remain
        runs = storage.list_runs(limit=10)
        assert len(runs) == 3
