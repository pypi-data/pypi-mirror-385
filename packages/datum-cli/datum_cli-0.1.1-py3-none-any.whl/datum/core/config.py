"""Configuration models and file I/O for datum-dbt.

All configuration is stored in ~/.datum/config.yaml and validated with Pydantic v2.
"""

from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
from uuid import uuid4

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


class DbtProjectConfig(BaseModel):
    """Configuration for a dbt project."""

    project_id: str = Field(default_factory=lambda: str(uuid4()))
    project_path: Path
    profiles_path: Path = Field(default=Path.home() / ".dbt" / "profiles.yml")
    target: str = "dev"
    dbt_version: Optional[str] = None

    @field_validator("project_path", mode="after")
    @classmethod
    def validate_project_path(cls, v: Path) -> Path:
        """Ensure project path exists and contains dbt_project.yml."""
        if not v.exists():
            raise ValueError(f"Project path does not exist: {v}")
        if not (v / "dbt_project.yml").exists():
            raise ValueError(f"No dbt_project.yml found in {v}")
        return v.resolve()

    @field_validator("profiles_path", mode="after")
    @classmethod
    def validate_profiles_path(cls, v: Path) -> Path:
        """Convert to absolute path."""
        return v.expanduser().resolve()


class ScheduleConfig(BaseModel):
    """Cron-based scheduling configuration."""

    cron_expression: str
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, v: str) -> str:
        """Validate cron expression syntax using croniter."""
        from croniter import croniter

        if not croniter.is_valid(v):
            raise ValueError(f"Invalid cron expression: {v}")
        return v


class WebhookConfig(BaseModel):
    """Webhook server configuration."""

    enabled: bool = False
    port: int = Field(default=8080, ge=1024, le=65535)
    host: str = "0.0.0.0"
    token: Optional[str] = None

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Ensure port is in valid range."""
        if not 1024 <= v <= 65535:
            raise ValueError(f"Port must be between 1024 and 65535, got {v}")
        return v


class RunRecord(BaseModel):
    """Record of a single dbt run execution."""

    run_id: str = Field(default_factory=lambda: str(uuid4())[:8])
    project_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    command: str
    exit_code: int
    duration_seconds: float
    status: Literal["SUCCESS", "FAILED", "TIMEOUT"]
    stdout: str = ""
    stderr: str = ""

    @model_validator(mode="after")
    def validate_status_matches_exit_code(self) -> "RunRecord":
        """Ensure status is consistent with exit code."""
        if self.exit_code == 0 and self.status != "SUCCESS":
            raise ValueError("Exit code 0 must have SUCCESS status")
        if self.exit_code != 0 and self.status == "SUCCESS":
            raise ValueError("Non-zero exit code cannot have SUCCESS status")
        return self


class DatumConfig(BaseModel):
    """Root configuration for datum-dbt stored in ~/.datum/config.yaml."""

    version: str = "1.0"
    project: DbtProjectConfig
    schedule: Optional[ScheduleConfig] = None
    webhook: Optional[WebhookConfig] = None
    private_key_path: Path = Field(default=Path.home() / ".datum" / "keys" / "default.pem")
    runs_dir: Path = Field(default=Path.home() / ".datum" / "runs")

    @field_validator("private_key_path", "runs_dir", mode="after")
    @classmethod
    def expand_paths(cls, v: Path) -> Path:
        """Expand user home directory in paths."""
        return v.expanduser().resolve()

    @model_validator(mode="after")
    def sync_key_path_with_project_id(self) -> "DatumConfig":
        """Set key path based on project ID if using default."""
        if "default.pem" in str(self.private_key_path):
            self.private_key_path = (
                Path.home() / ".datum" / "keys" / f"{self.project.project_id}.pem"
            )
        return self


# Config file I/O functions

def get_config_path() -> Path:
    """Get the path to the datum config file."""
    return Path.home() / ".datum" / "config.yaml"


def load_config() -> DatumConfig:
    """Load configuration from ~/.datum/config.yaml.

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"No datum configuration found at {config_path}. "
            "Run 'datum dbt init' to initialize."
        )
    
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    
    return DatumConfig.model_validate(data)


def save_config(config: DatumConfig) -> None:
    """Save configuration to ~/.datum/config.yaml.

    Creates parent directories if they don't exist.
    """
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to dict and handle Path serialization
    data = config.model_dump(mode="json")
    
    with open(config_path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def config_exists() -> bool:
    """Check if a datum config file exists."""
    return get_config_path().exists()