"""
PostgreSQL database client implementation.
"""

from typing import Optional, List, Tuple, Generator

from db_backup.database.base import BaseDatabaseClient
from db_backup.utils.logging_config import get_logger

logger = get_logger(__name__)

# Check if psycopg2 is available
try:
    import psycopg2
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False


class PostgreSQLClient(BaseDatabaseClient):
    """PostgreSQL database client."""

    def connect(self) -> bool:
        """
        Establish PostgreSQL connection.

        Returns:
            bool: True if connection successful, False otherwise
        """
        if not POSTGRESQL_AVAILABLE:
            logger.error(
                "psycopg2 is not installed. "
                "Install with: pip install psycopg2-binary"
            )
            return False

        try:
            logger.info(
                f"Connecting to PostgreSQL {self.database}@{self.host}:{self.port}..."
            )

            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()

            logger.info("PostgreSQL connection established successfully")
            return True

        except psycopg2.OperationalError as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to PostgreSQL: {e}")
            return False

    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                logger.info("PostgreSQL connection closed")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    def get_column_names(self) -> List[str]:
        """
        Get column names from last query.

        Returns:
            List of column names
        """
        if self.cursor and self.cursor.description:
            return [desc[0] for desc in self.cursor.description]
        return []

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> bool:
        """
        Execute a query.

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Executing PostgreSQL query...")
            logger.debug(f"Query: {query}")

            self.cursor.execute(query, params)
            return True

        except psycopg2.Error as e:
            logger.error(f"PostgreSQL query execution failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {e}")
            return False

    def fetch_rows_chunked(self, chunk_size: int = 10000) -> Generator:
        """
        Generator to fetch rows in chunks (memory efficient).

        Args:
            chunk_size: Number of rows per chunk

        Yields:
            List of rows
        """
        while True:
            rows = self.cursor.fetchmany(chunk_size)
            if not rows:
                break
            yield rows
