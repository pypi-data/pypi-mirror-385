"""Validation system for dbt project setup and configuration.

Provides pre-flight checks that catch setup issues before execution.
Each issue includes a description and remediation steps.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import yaml
from croniter import croniter

from datum.core.auth import validate_key_permissions, fix_key_permissions
from datum.core.config import DatumConfig


@dataclass
class Issue:
    """Represents a single validation issue with remediation."""

    severity: str  # "error" | "warning"
    description: str
    remediation: str
    auto_fix: Optional[Callable[[], None]] = None

    def __str__(self) -> str:
        """Format issue for display."""
        icon = "✗" if self.severity == "error" else "⚠"
        return f"{icon} {self.description}\n  → {self.remediation}"


class ProjectValidator:
    """Validates dbt project setup and datum configuration."""

    def __init__(self, config: DatumConfig):
        """Initialize validator with datum config.

        Args:
            config: DatumConfig to validate
        """
        self.config = config

    def validate_dbt_project(self) -> Optional[Issue]:
        """Check if dbt_project.yml exists.

        Returns:
            Issue if project not found, None if valid
        """
        project_yml = self.config.project.project_path / "dbt_project.yml"

        if not project_yml.exists():
            return Issue(
                severity="error",
                description="dbt_project.yml not found",
                remediation=(
                    f"Check project path: {self.config.project.project_path}\n"
                    "  Or initialize with: datum dbt init --repo-path <correct-path>"
                ),
            )

        return None

    def validate_profiles_file(self) -> Optional[Issue]:
        """Check if profiles.yml exists and is readable.

        Returns:
            Issue if profiles not found, None if valid
        """
        profiles_path = self.config.project.profiles_path

        if not profiles_path.exists():
            return Issue(
                severity="error",
                description=f"profiles.yml not found at {profiles_path}",
                remediation=(
                    f"Create profiles.yml or update path:\n"
                    f"  datum dbt config --profiles-path /path/to/profiles.yml"
                ),
            )

        # Try to parse YAML to verify it's valid
        try:
            with open(profiles_path, "r") as f:
                yaml.safe_load(f)
        except Exception as e:
            return Issue(
                severity="error",
                description=f"profiles.yml is invalid YAML: {e}",
                remediation=f"Fix YAML syntax in {profiles_path}",
            )

        return None

    def validate_ssh_key_exists(self) -> Optional[Issue]:
        """Check if SSH private key file exists.

        Returns:
            Issue if key not found, None if valid
        """
        key_path = self.config.private_key_path

        if not key_path.exists():
            return Issue(
                severity="error",
                description=f"SSH private key not found at {key_path}",
                remediation=(
                    f"Re-initialize to generate keys:\n"
                    f"  datum dbt init --repo-path {self.config.project.project_path}"
                ),
            )

        return None

    def validate_key_permissions(self) -> Optional[Issue]:
        """Check if SSH key has correct permissions (600).

        Returns:
            Issue if permissions wrong, None if valid
        """
        key_path = self.config.private_key_path

        if not key_path.exists():
            return None  # Will be caught by validate_ssh_key_exists

        is_valid, error_msg = validate_key_permissions(key_path)

        if not is_valid:
            return Issue(
                severity="error",
                description="SSH key has incorrect permissions",
                remediation=error_msg,
                auto_fix=lambda: fix_key_permissions(key_path),
            )

        return None

    def validate_target_exists(self) -> Optional[Issue]:
        """Check if target exists in profiles.yml.

        Returns:
            Issue if target not found, None if valid
        """
        profiles_path = self.config.project.profiles_path

        if not profiles_path.exists():
            return None  # Will be caught by validate_profiles_file

        try:
            with open(profiles_path, "r") as f:
                profiles = yaml.safe_load(f) or {}

            # Get project name from dbt_project.yml
            project_yml = self.config.project.project_path / "dbt_project.yml"
            if not project_yml.exists():
                return None

            with open(project_yml, "r") as f:
                project_config = yaml.safe_load(f) or {}

            project_name = project_config.get("name", "default")
            target_name = self.config.project.target

            # Check if project exists in profiles
            if project_name not in profiles:
                return Issue(
                    severity="error",
                    description=f"Project '{project_name}' not found in profiles.yml",
                    remediation=(
                        f"Add '{project_name}' section to {profiles_path}\n"
                        f"  See: https://docs.getdbt.com/reference/dbt-commands/parse"
                    ),
                )

            project_profile = profiles[project_name]
            if isinstance(project_profile, dict):
                # Check if target exists
                if "outputs" in project_profile:
                    outputs = project_profile["outputs"]
                    if target_name not in outputs:
                        available = ", ".join(outputs.keys())
                        return Issue(
                            severity="error",
                            description=(
                                f"Target '{target_name}' not found in "
                                f"'{project_name}' profile"
                            ),
                            remediation=(
                                f"Available targets: {available}\n"
                                f"  Update with: datum dbt config --target <target-name>"
                            ),
                        )

        except Exception:
            # If we can't parse, it will be caught by validate_profiles_file
            pass

        return None

    def validate_cron_expression(self, expr: str) -> Optional[Issue]:
        """Validate a cron expression.

        Args:
            expr: Cron expression to validate

        Returns:
            Issue if invalid, None if valid
        """
        if not croniter.is_valid(expr):
            return Issue(
                severity="error",
                description=f"Invalid cron expression: '{expr}'",
                remediation=(
                    "Cron format: minute hour day month weekday\n"
                    "  Examples:\n"
                    "    0 10 * * * = every day at 10:00 AM\n"
                    "    */5 * * * * = every 5 minutes\n"
                    "    0 0 1 * * = first day of month at midnight\n"
                    "  See: https://crontab.guru for validation"
                ),
            )

        return None

    def validate_all(self) -> list[Issue]:
        """Run all validation checks.

        Returns:
            List of issues found (empty if all valid)
        """
        checks = [
            self.validate_dbt_project(),
            self.validate_profiles_file(),
            self.validate_ssh_key_exists(),
            self.validate_key_permissions(),
            self.validate_target_exists(),
        ]

        return [issue for issue in checks if issue is not None]

    def has_fixable_issues(self) -> bool:
        """Check if there are auto-fixable issues.

        Returns:
            True if any issues have auto_fix functions
        """
        issues = self.validate_all()
        return any(issue.auto_fix is not None for issue in issues)

    def auto_fix_all(self) -> int:
        """Apply auto-fixes to all fixable issues.

        Returns:
            Number of issues fixed
        """
        issues = self.validate_all()
        fixed_count = 0

        for issue in issues:
            if issue.auto_fix is not None:
                try:
                    issue.auto_fix()
                    fixed_count += 1
                except Exception as e:
                    print(f"Failed to auto-fix: {issue.description} - {e}")

        return fixed_count
