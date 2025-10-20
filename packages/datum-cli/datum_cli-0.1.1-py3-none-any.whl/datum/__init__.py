# src/datum/__init__.py
"""datum-dbt: Schedule dbt projects locally with datum cloud reporting."""

__version__ = "0.1.0"

# src/datum/cli/__init__.py
"""CLI interface for datum-dbt."""

# src/datum/cli/commands/__init__.py
"""CLI commands for datum-dbt."""

# src/datum/core/__init__.py
"""Core functionality for datum-dbt."""

# src/datum/__main__.py
"""Allow running datum as a module: python -m datum"""

from datum.cli.main import app

if __name__ == "__main__":
    app()
