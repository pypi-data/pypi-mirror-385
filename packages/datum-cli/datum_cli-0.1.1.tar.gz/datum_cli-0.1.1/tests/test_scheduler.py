"""Tests for the cron scheduling system."""

import pytest
from datetime import datetime

from datum.core.scheduler import CronScheduler


class TestCronScheduler:
    """Test cron scheduling functionality."""

    def test_validate_expression_valid(self):
        """Should validate correct cron expressions."""
        valid_expressions = [
            "0 10 * * *",      # Every day at 10 AM
            "*/5 * * * *",     # Every 5 minutes
            "0 0 1 * *",       # First day of month
            "0 9 * * 1",       # Every Monday at 9 AM
            "0 0 * * 0",       # Every Sunday at midnight
        ]

        for expr in valid_expressions:
            assert CronScheduler.validate_expression(expr) is True

    def test_validate_expression_invalid(self):
        """Should reject invalid cron expressions."""
        invalid_expressions = [
            "invalid",
            "60 * * * *",      # Invalid minute
            "* 25 * * *",      # Invalid hour
            "* * 32 * *",      # Invalid day
            "* * * 13 *",      # Invalid month
            "",                 # Empty
        ]

        for expr in invalid_expressions:
            assert CronScheduler.validate_expression(expr) is False

    def test_add_schedule(self):
        """Should add schedule to crontab."""
        scheduler = CronScheduler("test-project-123")
        cmd = "/usr/local/bin/datum dbt run"

        # Clean up any existing entries first
        scheduler.remove_schedule()

        # Add schedule
        result = scheduler.add_schedule("0 10 * * *", cmd)
        assert result is True

        # Verify it was added
        assert scheduler.is_scheduled() is True

        # Clean up
        scheduler.remove_schedule()

    def test_add_schedule_invalid_expression(self):
        """Should reject invalid cron expression."""
        scheduler = CronScheduler("test-project-123")

        with pytest.raises(ValueError):
            scheduler.add_schedule("invalid", "command")

    def test_remove_schedule(self):
        """Should remove schedule from crontab."""
        scheduler = CronScheduler("test-project-456")
        cmd = "/usr/local/bin/datum dbt run"

        # Add first
        scheduler.add_schedule("0 10 * * *", cmd)
        assert scheduler.is_scheduled() is True

        # Remove
        result = scheduler.remove_schedule()
        assert result is True
        assert scheduler.is_scheduled() is False

    def test_remove_schedule_when_none_exists(self):
        """Should handle removing when no schedule exists."""
        scheduler = CronScheduler("nonexistent-project-xyz")

        # Clean up any existing
        scheduler.remove_schedule()

        # Try to remove again
        result = scheduler.remove_schedule()
        assert result is False

    def test_get_schedule(self):
        """Should retrieve cron expression."""
        scheduler = CronScheduler("test-project-789")
        cmd = "/usr/local/bin/datum dbt run"

        # Clean up first
        scheduler.remove_schedule()

        # Add schedule
        scheduler.add_schedule("0 10 * * *", cmd)

        # Get it back
        expr = scheduler.get_cron_expression()
        assert expr is not None
        assert "10" in expr  # Should contain hour

        # Clean up
        scheduler.remove_schedule()

    def test_get_schedule_when_none_exists(self):
        """Should return None when no schedule exists."""
        scheduler = CronScheduler("no-schedule-project")
        scheduler.remove_schedule()

        expr = scheduler.get_cron_expression()
        assert expr is None

    def test_get_scheduled_command(self):
        """Should retrieve scheduled command."""
        scheduler = CronScheduler("cmd-test-project")
        cmd = "/usr/local/bin/datum dbt run --target prod"

        # Clean up first
        scheduler.remove_schedule()

        # Add schedule
        scheduler.add_schedule("0 10 * * *", cmd)

        # Get command
        retrieved_cmd = scheduler.get_scheduled_command()
        assert retrieved_cmd is not None
        assert "datum" in retrieved_cmd
        assert "prod" in retrieved_cmd

        # Clean up
        scheduler.remove_schedule()

    def test_is_scheduled(self):
        """Should detect if project is scheduled."""
        scheduler = CronScheduler("scheduled-check-project")

        # Clean up first
        scheduler.remove_schedule()

        # Not scheduled
        assert scheduler.is_scheduled() is False

        # Add schedule
        scheduler.add_schedule("0 10 * * *", "command")
        assert scheduler.is_scheduled() is True

        # Remove
        scheduler.remove_schedule()
        assert scheduler.is_scheduled() is False

    def test_get_next_run(self):
        """Should calculate next run time."""
        scheduler = CronScheduler("next-run-project")

        # Clean up first
        scheduler.remove_schedule()

        # Add schedule for today at specific time (future or past)
        scheduler.add_schedule("0 10 * * *", "command")

        # Get next run
        next_run = scheduler.get_next_run()
        assert next_run is not None
        assert isinstance(next_run, datetime)
        assert next_run > datetime.now()

        # Clean up
        scheduler.remove_schedule()

    def test_get_next_run_when_not_scheduled(self):
        """Should return None if not scheduled."""
        scheduler = CronScheduler("no-next-run-project")
        scheduler.remove_schedule()

        next_run = scheduler.get_next_run()
        assert next_run is None

    def test_multiple_projects_isolated(self):
        """Should isolate schedules between projects."""
        scheduler1 = CronScheduler("project-a")
        scheduler2 = CronScheduler("project-b")

        # Clean up
        scheduler1.remove_schedule()
        scheduler2.remove_schedule()

        # Add to project-a
        scheduler1.add_schedule("0 10 * * *", "cmd-a")
        assert scheduler1.is_scheduled() is True

        # Project-b should not be affected
        assert scheduler2.is_scheduled() is False

        # Add to project-b
        scheduler2.add_schedule("0 11 * * *", "cmd-b")
        assert scheduler2.is_scheduled() is True

        # Verify still separate
        expr1 = scheduler1.get_cron_expression()
        expr2 = scheduler2.get_cron_expression()
        assert expr1 != expr2

        # Clean up
        scheduler1.remove_schedule()
        scheduler2.remove_schedule()

    def test_replace_schedule(self):
        """Should replace existing schedule."""
        scheduler = CronScheduler("replace-project")

        # Clean up
        scheduler.remove_schedule()

        # Add initial
        scheduler.add_schedule("0 10 * * *", "cmd")
        expr1 = scheduler.get_cron_expression()

        # Replace with new
        scheduler.add_schedule("0 14 * * *", "cmd")
        expr2 = scheduler.get_cron_expression()

        assert expr1 != expr2
        assert "14" in expr2

        # Clean up
        scheduler.remove_schedule()
