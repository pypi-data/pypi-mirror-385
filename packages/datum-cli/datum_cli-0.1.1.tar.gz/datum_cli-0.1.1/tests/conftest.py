"""Pytest configuration and shared fixtures for datum tests."""

import json
from pathlib import Path

import pytest

from datum.core.config import DatumConfig, DbtProjectConfig


@pytest.fixture
def tmp_home(tmp_path):
    """Provide a temporary home directory for testing.

    This isolates tests from the user's actual ~/.datum directory.
    """
    home = tmp_path / "home"
    home.mkdir()
    return home


@pytest.fixture
def mock_dbt_project(tmp_path):
    """Create a mock dbt project with minimal files."""
    project = tmp_path / "dbt_project"
    project.mkdir()

    # Create dbt_project.yml
    (project / "dbt_project.yml").write_text(
        "name: test_project\n"
        "version: 1.0\n"
        "config-version: 2\n"
    )

    # Create basic directory structure
    (project / "models").mkdir()
    (project / "tests").mkdir()
    (project / "seeds").mkdir()
    (project / "macros").mkdir()
    (project / "analysis").mkdir()

    return project


@pytest.fixture
def mock_profiles(tmp_path):
    """Create a mock profiles.yml file."""
    profiles_dir = tmp_path / "dbt"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.yml"

    profiles_content = {
        "test_project": {
            "outputs": {
                "dev": {
                    "type": "postgres",
                    "host": "localhost",
                    "user": "dbt",
                    "password": "password",
                    "port": 5432,
                    "dbname": "analytics_dev",
                    "schema": "public",
                    "threads": 4,
                },
                "prod": {
                    "type": "postgres",
                    "host": "prod-db.internal",
                    "user": "dbt",
                    "password": "password",
                    "port": 5432,
                    "dbname": "analytics_prod",
                    "schema": "public",
                    "threads": 8,
                },
            },
            "target": "dev",
        }
    }

    import yaml

    with open(profiles_file, "w") as f:
        yaml.safe_dump(profiles_content, f)

    return profiles_file


@pytest.fixture
def test_config(mock_dbt_project, mock_profiles, tmp_path):
    """Create a test DatumConfig."""
    config = DatumConfig(
        project=DbtProjectConfig(
            project_path=mock_dbt_project,
            profiles_path=mock_profiles,
            target="dev",
        ),
        private_key_path=tmp_path / "key.pem",
        runs_dir=tmp_path / "runs",
    )
    return config


@pytest.fixture
def test_config_with_key(test_config, tmp_path):
    """Create a test DatumConfig with a generated SSH key."""
    from datum.core.auth import generate_ssh_keypair

    key_path = tmp_path / "test.pem"
    generate_ssh_keypair(key_path)

    test_config.private_key_path = key_path
    return test_config


@pytest.fixture
def mock_run_record(test_config):
    """Create a mock run record."""
    from datum.core.config import RunRecord
    from datetime import datetime

    return RunRecord(
        run_id="test123",
        project_id=test_config.project.project_id,
        timestamp=datetime.now(),
        command="dbt run",
        exit_code=0,
        duration_seconds=45.2,
        status="SUCCESS",
        stdout="[00:00:00] Running dbt...\n[00:00:45] Success!",
        stderr="",
    )


@pytest.fixture
def mock_failed_run_record(test_config):
    """Create a mock failed run record."""
    from datum.core.config import RunRecord
    from datetime import datetime

    return RunRecord(
        run_id="fail456",
        project_id=test_config.project.project_id,
        timestamp=datetime.now(),
        command="dbt run",
        exit_code=1,
        duration_seconds=12.5,
        status="FAILED",
        stdout="[00:00:00] Running dbt...",
        stderr="Error: Connection failed",
    )
