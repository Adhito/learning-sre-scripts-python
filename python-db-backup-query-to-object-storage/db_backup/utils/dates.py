"""
Date parsing and formatting utilities.

Provides functions for parsing datetime configuration strings
and formatting filenames with date placeholders.
"""

from datetime import datetime, timedelta

from db_backup import config
from db_backup.utils.logging_config import get_logger

logger = get_logger(__name__)


def parse_datetime_config(dt_config: str) -> datetime:
    """
    Parse datetime configuration string to datetime object.

    Supported formats:
        - "today": Start of today (00:00:00)
        - "yesterday": Start of yesterday (00:00:00)
        - "now": Current datetime
        - ISO 8601 date: "YYYY-MM-DD" (at 00:00:00)
        - ISO 8601 datetime: "YYYY-MM-DDTHH:MM:SS"

    Args:
        dt_config: Datetime string

    Returns:
        datetime object

    Raises:
        ValueError: If datetime format is invalid
    """
    now = datetime.now()

    if dt_config.lower() == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif dt_config.lower() == "yesterday":
        return (now.replace(hour=0, minute=0, second=0, microsecond=0)
                - timedelta(days=1))
    elif dt_config.lower() == "now":
        return now
    else:
        # Try to parse as ISO 8601
        try:
            return datetime.fromisoformat(dt_config)
        except ValueError:
            pass

        # Try common formats
        for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
            try:
                return datetime.strptime(dt_config, fmt)
            except ValueError:
                continue

        logger.error(f"Invalid datetime format: {dt_config}")
        raise ValueError(f"Cannot parse datetime: {dt_config}")


def format_filename(pattern: str, table: str, start_dt: datetime,
                    end_dt: datetime) -> str:
    """
    Format filename using pattern and placeholders.

    Available placeholders:
        - {table}: Table name
        - {start}: Start datetime (formatted using FILENAME_DATE_FORMAT)
        - {end}: End datetime (formatted using FILENAME_DATE_FORMAT)
        - {datetime}: Current datetime (formatted using FILENAME_DATE_FORMAT)
        - {date}: Current date (YYYY-MM-DD)

    Args:
        pattern: Filename pattern with placeholders
        table: Table name
        start_dt: Start datetime
        end_dt: End datetime

    Returns:
        Formatted filename
    """
    return pattern.format(
        table=table,
        start=start_dt.strftime(config.FILENAME_DATE_FORMAT),
        end=end_dt.strftime(config.FILENAME_DATE_FORMAT),
        datetime=datetime.now().strftime(config.FILENAME_DATE_FORMAT),
        date=datetime.now().strftime("%Y-%m-%d")
    )
