"""Tests for the validation system."""

import os
import pytest

from datum.core.validators import ProjectValidator, Issue


class TestValidators:
    """Test all validation checks."""

    def test_validate_dbt_project_exists(self, test_config):
        """Should pass when dbt_project.yml exists."""
        validator = ProjectValidator(test_config)
        issue = validator.validate_dbt_project()
        assert issue is None

    def test_validate_dbt_project_missing(self, test_config):
        """Should fail when dbt_project.yml is missing."""
        import shutil

        shutil.rmtree(test_config.project.project_path)

        validator = ProjectValidator(test_config)
        issue = validator.validate_dbt_project()

        assert issue is not None
        assert issue.severity == "error"
        assert "dbt_project.yml" in issue.description

    def test_validate_profiles_exists(self, test_config):
        """Should pass when profiles.yml exists and is valid."""
        validator = ProjectValidator(test_config)
        issue = validator.validate_profiles_file()
        assert issue is None

    def test_validate_profiles_missing(self, test_config):
        """Should fail when profiles.yml is missing."""
        test_config.project.profiles_path = test_config.project.profiles_path.parent / "missing.yml"

        validator = ProjectValidator(test_config)
        issue = validator.validate_profiles_file()

        assert issue is not None
        assert issue.severity == "error"
        assert "profiles.yml" in issue.description

    def test_validate_profiles_invalid_yaml(self, test_config, tmp_path):
        """Should fail when profiles.yml has invalid YAML."""
        bad_profile = tmp_path / "bad.yml"
        bad_profile.write_text("invalid: [yaml: content")

        test_config.project.profiles_path = bad_profile

        validator = ProjectValidator(test_config)
        issue = validator.validate_profiles_file()

        assert issue is not None
        assert issue.severity == "error"

    def test_validate_ssh_key_exists(self, test_config_with_key):
        """Should pass when SSH key exists."""
        validator = ProjectValidator(test_config_with_key)
        issue = validator.validate_ssh_key_exists()
        assert issue is None

    def test_validate_ssh_key_missing(self, test_config):
        """Should fail when SSH key is missing."""
        validator = ProjectValidator(test_config)
        issue = validator.validate_ssh_key_exists()

        assert issue is not None
        assert issue.severity == "error"
        assert "key" in issue.description.lower()

    def test_validate_key_permissions_correct(self, test_config_with_key):
        """Should pass when SSH key has 600 permissions."""
        validator = ProjectValidator(test_config_with_key)
        issue = validator.validate_key_permissions()
        assert issue is None

    def test_validate_key_permissions_wrong(self, test_config_with_key):
        """Should fail when SSH key has wrong permissions."""
        # Set wrong permissions
        os.chmod(test_config_with_key.private_key_path, 0o644)

        validator = ProjectValidator(test_config_with_key)
        issue = validator.validate_key_permissions()

        assert issue is not None
        assert issue.severity == "error"
        assert "permissions" in issue.description.lower()
        assert issue.auto_fix is not None

    def test_auto_fix_permissions(self, test_config_with_key):
        """Should auto-fix key permissions."""
        # Set wrong permissions
        os.chmod(test_config_with_key.private_key_path, 0o644)

        validator = ProjectValidator(test_config_with_key)
        issue = validator.validate_key_permissions()

        assert issue.auto_fix is not None
        issue.auto_fix()

        # Verify fixed
        stat_info = os.stat(test_config_with_key.private_key_path)
        perms = stat_info.st_mode & 0o777
        assert perms == 0o600

    def test_validate_target_exists(self, test_config):
        """Should pass when target exists in profiles."""
        validator = ProjectValidator(test_config)
        issue = validator.validate_target_exists()
        assert issue is None

    def test_validate_target_missing(self, test_config):
        """Should fail when target doesn't exist in profiles."""
        test_config.project.target = "nonexistent"

        validator = ProjectValidator(test_config)
        issue = validator.validate_target_exists()

        assert issue is not None
        assert issue.severity == "error"
        assert "target" in issue.description.lower()

    def test_validate_cron_expression_valid(self, test_config):
        """Should pass for valid cron expressions."""
        validator = ProjectValidator(test_config)

        valid_expressions = [
            "0 10 * * *",      # Every day at 10 AM
            "*/5 * * * *",     # Every 5 minutes
            "0 0 1 * *",       # First day of month
            "0 9 * * 1",       # Every Monday at 9 AM
        ]

        for expr in valid_expressions:
            issue = validator.validate_cron_expression(expr)
            assert issue is None, f"Valid expression '{expr}' should not produce issue"

    def test_validate_cron_expression_invalid(self, test_config):
        """Should fail for invalid cron expressions."""
        validator = ProjectValidator(test_config)

        invalid_expressions = [
            "invalid",
            "60 * * * *",       # Invalid minute (0-59)
            "* 25 * * *",       # Invalid hour (0-23)
            "* * 32 * *",       # Invalid day (1-31)
            "* * * 13 *",       # Invalid month (1-12)
        ]

        for expr in invalid_expressions:
            issue = validator.validate_cron_expression(expr)
            assert issue is not None, f"Invalid expression '{expr}' should produce issue"
            assert issue.severity == "error"

    def test_validate_all_passes(self, test_config_with_key):
        """Should pass all checks with valid config."""
        validator = ProjectValidator(test_config_with_key)
        issues = validator.validate_all()
        assert len(issues) == 0

    def test_validate_all_finds_multiple_issues(self, test_config):
        """Should find multiple issues."""
        # Remove project
        import shutil
        shutil.rmtree(test_config.project.project_path)

        # Remove profiles
        test_config.project.profiles_path.unlink()

        validator = ProjectValidator(test_config)
        issues = validator.validate_all()

        assert len(issues) >= 2  # At least project and profiles

    def test_has_fixable_issues(self, test_config_with_key):
        """Should detect fixable issues."""
        import os
        os.chmod(test_config_with_key.private_key_path, 0o644)

        validator = ProjectValidator(test_config_with_key)
        assert validator.has_fixable_issues() is True

    def test_auto_fix_all(self, test_config_with_key):
        """Should fix all auto-fixable issues."""
        import os
        os.chmod(test_config_with_key.private_key_path, 0o644)

        validator = ProjectValidator(test_config_with_key)
        fixed_count = validator.auto_fix_all()

        assert fixed_count >= 1

        # Verify permissions fixed
        stat_info = os.stat(test_config_with_key.private_key_path)
        perms = stat_info.st_mode & 0o777
        assert perms == 0o600


class TestIssueModel:
    """Test Issue dataclass."""

    def test_issue_creation(self):
        """Should create Issue with all fields."""
        issue = Issue(
            severity="error",
            description="Test issue",
            remediation="Fix this",
            auto_fix=None,
        )

        assert issue.severity == "error"
        assert issue.description == "Test issue"
        assert issue.remediation == "Fix this"

    def test_issue_string_representation(self):
        """Should format Issue nicely."""
        issue = Issue(
            severity="error",
            description="Test issue",
            remediation="Fix this",
        )

        issue_str = str(issue)
        assert "✗" in issue_str
        assert "Test issue" in issue_str
        assert "Fix this" in issue_str

    def test_issue_warning_representation(self):
        """Should format warning Issues with warning icon."""
        issue = Issue(
            severity="warning",
            description="Test warning",
            remediation="Fix this",
        )

        issue_str = str(issue)
        assert "⚠" in issue_str
