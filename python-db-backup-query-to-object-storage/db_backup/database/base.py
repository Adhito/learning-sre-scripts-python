"""
Base database client abstract class.

Defines the interface that all database clients must implement.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Tuple, Generator

from db_backup.utils.logging_config import get_logger

logger = get_logger(__name__)


class BaseDatabaseClient(ABC):
    """Abstract base class for database clients."""

    def __init__(self, host: str, port: int, database: str,
                 user: str, password: str):
        """
        Initialize database client.

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Username
            password: Password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish database connection.

        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    def get_column_names(self) -> List[str]:
        """
        Get column names from last query.

        Returns:
            List of column names
        """
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> bool:
        """
        Execute a query.

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abstractmethod
    def fetch_rows_chunked(self, chunk_size: int = 10000) -> Generator:
        """
        Generator to fetch rows in chunks (memory efficient).

        Args:
            chunk_size: Number of rows per chunk

        Yields:
            List of rows
        """
        pass

    def build_export_query(self, table: str, date_column: str,
                           start_dt: datetime, end_dt: datetime,
                           custom_where: Optional[str] = None) -> Tuple[str, Tuple]:
        """
        Build the export query with date range filter.

        Args:
            table: Table name
            date_column: Date column for filtering
            start_dt: Start datetime
            end_dt: End datetime
            custom_where: Additional WHERE conditions

        Returns:
            Tuple of (SQL query string, parameters tuple)
        """
        # Base query with placeholders
        query = f"SELECT * FROM {table} WHERE {date_column} >= %s AND {date_column} < %s"

        # Add custom WHERE clause if provided
        if custom_where and custom_where.strip():
            query += f" AND ({custom_where})"

        # Order by date column
        query += f" ORDER BY {date_column}"

        return query, (start_dt, end_dt)
