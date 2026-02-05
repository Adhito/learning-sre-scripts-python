"""
Entry point for running the package as a module.

Usage:
    python -m db_backup [options]

This allows the package to be executed directly using:
    python -m db_backup --table users --date-column created_at --start yesterday --end today
"""

from db_backup.cli import main

if __name__ == "__main__":
    exit(main())
