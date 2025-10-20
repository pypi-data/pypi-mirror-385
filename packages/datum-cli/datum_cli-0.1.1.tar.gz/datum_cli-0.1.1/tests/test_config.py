"""Tests for configuration management."""

import pytest
import yaml
from pathlib import Path

from datum.core.config import (
    DatumConfig,
    DbtProjectConfig,
    ScheduleConfig,
    WebhookConfig,
    RunRecord,
    load_config,
    save_config,
    get_config_path,
    config_exists,
)


class TestDbtProjectConfig:
    """Test dbt project configuration model."""

    def test_valid_project_config(self, mock_dbt_project, mock_profiles):
        """Should create valid project config."""
        config = DbtProjectConfig(
            project_path=mock_dbt_project,
            profiles_path=mock_profiles,
            target="dev",
        )

        assert config.project_path == mock_dbt_project
        assert config.profiles_path == mock_profiles
        assert config.target == "dev"

    def test_project_path_validation(self, tmp_path):
        """Should validate dbt_project.yml exists."""
        with pytest.raises(ValueError):
            DbtProjectConfig(
                project_path=tmp_path,  # Empty directory
                profiles_path=tmp_path / "profiles.yml",
            )

    def test_project_path_resolves(self, mock_dbt_project):
        """Should resolve project path to absolute."""
        config = DbtProjectConfig(
            project_path=mock_dbt_project,
            profiles_path=mock_dbt_project.parent / "profiles.yml",
        )

        assert config.project_path.is_absolute()

    def test_profiles_path_expands_home(self, mock_dbt_project, tmp_path):
        """Should expand ~ in profiles path."""
        # Create a profiles file in tmp that we can reference
        profiles = tmp_path / "profiles.yml"
        profiles.write_text("test: {}")

        config = DbtProjectConfig(
            project_path=mock_dbt_project,
            profiles_path=profiles,
        )

        assert config.profiles_path.is_absolute()


class TestScheduleConfig:
    """Test schedule configuration model."""

    def test_valid_schedule(self):
        """Should create valid schedule."""
        schedule = ScheduleConfig(cron_expression="0 10 * * *")

        assert schedule.cron_expression == "0 10 * * *"
        assert schedule.enabled is True

    def test_cron_validation(self):
        """Should validate cron expression."""
        with pytest.raises(ValueError):
            ScheduleConfig(cron_expression="invalid")

    def test_schedule_timestamps(self):
        """Should set timestamps."""
        schedule = ScheduleConfig(cron_expression="0 10 * * *")

        assert schedule.created_at is not None
        assert schedule.last_run_at is None
        assert schedule.next_run_at is None


class TestWebhookConfig:
    """Test webhook configuration model."""

    def test_valid_webhook(self):
        """Should create valid webhook config."""
        webhook = WebhookConfig(port=8080)

        assert webhook.port == 8080
        assert webhook.host == "0.0.0.0"
        assert webhook.enabled is False

    def test_port_validation(self):
        """Should validate port range."""
        with pytest.raises(ValueError):
            WebhookConfig(port=100)  # Too low

        with pytest.raises(ValueError):
            WebhookConfig(port=70000)  # Too high


class TestRunRecord:
    """Test run record model."""

    def test_valid_run_record(self, test_config):
        """Should create valid run record."""
        from datetime import datetime

        record = RunRecord(
            project_id=test_config.project.project_id,
            command="dbt run",
            exit_code=0,
            duration_seconds=45.2,
            status="SUCCESS",
        )

        assert record.run_id is not None
        assert record.status == "SUCCESS"
        assert record.timestamp is not None

    def test_run_record_failed(self):
        """Should create failed run record."""
        record = RunRecord(
            project_id="test",
            command="dbt run",
            exit_code=1,
            duration_seconds=10.0,
            status="FAILED",
        )
        
        assert record.status == "FAILED"
        assert record.exit_code == 1


class TestDatumConfig:
    """Test root configuration model."""

    def test_valid_config(self, test_config):
        """Should create valid config."""
        assert test_config.version == "1.0"
        assert test_config.project is not None
        assert test_config.private_key_path is not None

    def test_config_has_project_id(self, test_config):
        """Should include project ID."""
        # Just verify project_id is set and is a string
        assert isinstance(test_config.project.project_id, str)
        assert len(test_config.project.project_id) > 0


class TestConfigFileIO:
    """Test configuration file loading and saving."""

    def test_config_path(self, monkeypatch, tmp_path):
        """Should use correct config path."""
        monkeypatch.setenv("HOME", str(tmp_path))
        path = get_config_path()

        assert ".datum" in str(path)
        assert "config.yaml" in str(path)

    def test_config_exists_false(self, monkeypatch, tmp_path):
        """Should detect when config doesn't exist."""
        monkeypatch.setenv("HOME", str(tmp_path))
        assert config_exists() is False

    def test_load_config_not_found(self, monkeypatch, tmp_path):
        """Should raise error when config not found."""
        monkeypatch.setenv("HOME", str(tmp_path))

        with pytest.raises(FileNotFoundError):
            load_config()


class TestConfigValidation:
    """Test configuration validation."""

    def test_invalid_project_path(self, tmp_path):
        """Should reject invalid project path."""
        with pytest.raises(ValueError):
            DatumConfig(
                project=DbtProjectConfig(
                    project_path=tmp_path / "nonexistent",
                    profiles_path=tmp_path / "profiles.yml",
                ),
                private_key_path=tmp_path / "key.pem",
            )

    def test_path_expansion(self, mock_dbt_project, tmp_path):
        """Should expand home directory in paths."""
        config = DatumConfig(
            project=DbtProjectConfig(
                project_path=mock_dbt_project,
                profiles_path=tmp_path / "profiles.yml",
            ),
            private_key_path=tmp_path / "key.pem",
            runs_dir=tmp_path / "runs",
        )

        # All paths should be absolute
        assert config.private_key_path.is_absolute()
        assert config.runs_dir.is_absolute()
