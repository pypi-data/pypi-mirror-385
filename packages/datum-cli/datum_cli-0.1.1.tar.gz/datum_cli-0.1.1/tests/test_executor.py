"""Tests for dbt execution and logging."""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from datum.core.executor import DbtExecutor
from datum.core.config import RunRecord


class TestDbtExecutor:
    """Test dbt command execution."""

    def test_executor_initialization(self, test_config):
        """Should initialize executor with config."""
        executor = DbtExecutor(test_config)
        assert executor.config == test_config

    def test_run_dry_run(self, test_config):
        """Should show command without executing."""
        executor = DbtExecutor(test_config)

        run_record = executor.run(dry_run=True)

        assert run_record.status == "SUCCESS"
        assert run_record.exit_code == 0
        assert "DRY RUN" in run_record.stdout

    def test_run_success(self, test_config):
        """Should execute dbt command successfully."""
        executor = DbtExecutor(test_config)

        # Mock subprocess
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout = iter(["[00:00:00] Running dbt...\n"])
            mock_process.stderr = iter([])
            mock_process.poll.side_effect = [None, 0]  # Second call returns exit code
            mock_process.returncode = 0

            mock_popen.return_value = mock_process

            run_record = executor.run(dry_run=False, timeout=3600)

            assert run_record.status == "SUCCESS"
            assert run_record.exit_code == 0
            assert run_record.duration_seconds > 0

    def test_run_failure(self, test_config):
        """Should handle dbt command failure."""
        executor = DbtExecutor(test_config)

        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout = iter(["Error: Connection failed\n"])
            mock_process.stderr = iter([])
            mock_process.poll.side_effect = [None, 1]  # Exit code 1
            mock_process.returncode = 1

            mock_popen.return_value = mock_process

            run_record = executor.run(dry_run=False)

            assert run_record.status == "FAILED"
            assert run_record.exit_code == 1

    def test_run_with_target(self, test_config):
        """Should use specified target."""
        executor = DbtExecutor(test_config)

        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout = iter([])
            mock_process.stderr = iter([])
            mock_process.poll.side_effect = [None, 0]
            mock_process.returncode = 0

            mock_popen.return_value = mock_process

            executor.run(target="prod", dry_run=False)

            # Check that command includes target
            call_args = mock_popen.call_args
            cmd = call_args[0][0]
            assert "--target" in cmd
            assert "prod" in cmd

    def test_run_with_vars(self, test_config):
        """Should pass dbt variables."""
        executor = DbtExecutor(test_config)

        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout = iter([])
            mock_process.stderr = iter([])
            mock_process.poll.side_effect = [None, 0]
            mock_process.returncode = 0

            mock_popen.return_value = mock_process

            vars_dict = {"key": "value"}
            executor.run(vars_dict=vars_dict, dry_run=False)

            # Check that command includes vars
            call_args = mock_popen.call_args
            cmd = " ".join(call_args[0][0])
            assert "--vars" in cmd
            assert "key" in cmd

    def test_run_timeout(self, test_config):
        """Should handle timeout."""
        executor = DbtExecutor(test_config)

        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout = iter([])
            mock_process.stderr = iter([])
            # Never return from poll (simulate long-running process)
            mock_process.poll.return_value = None
            mock_process.kill = Mock()

            mock_popen.return_value = mock_process

            with pytest.raises(TimeoutError):
                executor.run(timeout=1, dry_run=False)

            # Check that process was killed
            mock_process.kill.assert_called()

    def test_run_sets_working_directory(self, test_config):
        """Should set working directory to project path."""
        executor = DbtExecutor(test_config)

        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout = iter([])
            mock_process.stderr = iter([])
            mock_process.poll.side_effect = [None, 0]
            mock_process.returncode = 0

            mock_popen.return_value = mock_process

            executor.run(dry_run=False)

            # Check cwd parameter
            call_kwargs = mock_popen.call_args[1]
            assert call_kwargs["cwd"] == test_config.project.project_path
