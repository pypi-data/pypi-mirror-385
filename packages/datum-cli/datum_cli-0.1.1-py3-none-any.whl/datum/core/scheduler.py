"""Cron scheduling for dbt runs.

Handles adding/removing/querying cron jobs for automated dbt execution.
"""

from datetime import datetime
from typing import Optional

from croniter import croniter
from crontab import CronTab


class CronScheduler:
    """Manages cron-based scheduling for dbt projects."""

    def __init__(self, project_id: str):
        """Initialize scheduler for a project.

        Args:
            project_id: Unique project identifier (used as crontab comment)
        """
        self.project_id = project_id
        self.cron = CronTab(user=True)

    @staticmethod
    def validate_expression(cron_expr: str) -> bool:
        """Validate a cron expression.

        Args:
            cron_expr: Cron expression to validate

        Returns:
            True if valid, False otherwise
        """
        return croniter.is_valid(cron_expr)

    def add_schedule(
        self,
        cron_expr: str,
        command: str,
    ) -> bool:
        """Add a cron job to the user's crontab.

        Args:
            cron_expr: Cron expression (e.g., "0 10 * * *")
            command: Full command to execute

        Returns:
            True if added successfully

        Raises:
            ValueError: If cron expression is invalid
        """
        if not self.validate_expression(cron_expr):
            raise ValueError(f"Invalid cron expression: {cron_expr}")

        # Remove any existing schedules for this project
        self.remove_schedule()

        # Create new job
        job = self.cron.new(command=command, comment=self.project_id)
        job.setall(cron_expr)

        # Write to crontab
        self.cron.write()

        return True

    def remove_schedule(self) -> bool:
        """Remove all cron entries for this project.

        Returns:
            True if removed, False if none existed
        """
        # Find and remove jobs with this project_id in comment
        removed = False
        for job in list(self.cron):
            if job.comment and self.project_id in job.comment:
                self.cron.remove(job)
                removed = True

        if removed:
            self.cron.write()

        return removed

    def get_schedule(self) -> Optional[str]:
        """Get the cron expression for this project.

        Returns:
            Cron expression if scheduled, None otherwise
        """
        for job in self.cron:
            if job.comment and self.project_id in job.comment:
                return self.get_cron_expression()

        return None

    def get_scheduled_command(self) -> Optional[str]:
        """Get the command scheduled for this project.

        Returns:
            Scheduled command if exists, None otherwise
        """
        for job in self.cron:
            if job.comment and self.project_id in job.comment:
                return job.command

        return None

    def get_next_run(self) -> Optional[datetime]:
        """Calculate next scheduled run time.

        Returns:
            Next run datetime if scheduled, None otherwise
        """
        cron_expr = self.get_cron_expression()

        if not cron_expr:
            return None

        try:
            cron_iter = croniter(cron_expr, datetime.now())
            return cron_iter.get_next(datetime)
        except Exception:
            return None

    def get_cron_expression(self) -> Optional[str]:
        """Get cron expression as a single string.

        Returns:
            Cron expression (e.g., "0 10 * * *") or None
        """
        for job in self.cron:
            if job.comment and self.project_id in job.comment:
                # Extract cron fields from the job
                # Job str format: "minute hour day month weekday command [#comment]"
                parts = str(job).split()
                if len(parts) >= 5:
                    return " ".join(parts[:5])

        return None

    def is_scheduled(self) -> bool:
        """Check if project has an active schedule.

        Returns:
            True if scheduled, False otherwise
        """
        for job in self.cron:
            if job.comment and self.project_id in job.comment:
                return True
        return False

    def get_last_run_from_cron(self) -> Optional[datetime]:
        """Get when the cron job was last modified.

        Note: Crontab doesn't track execution time, only modification time.

        Returns:
            Datetime of last crontab modification
        """
        cron_expr = self.get_cron_expression()

        if not cron_expr:
            return None

        try:
            cron_iter = croniter(cron_expr, datetime.now())
            # Get previous run (would have been before now)
            prev_time = cron_iter.get_prev(datetime)
            return prev_time
        except Exception:
            return None
