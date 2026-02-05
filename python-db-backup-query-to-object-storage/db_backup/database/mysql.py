"""
MySQL database client implementation.
"""

from typing import Optional, List, Tuple, Generator

from db_backup.database.base import BaseDatabaseClient
from db_backup.utils.logging_config import get_logger

logger = get_logger(__name__)

# Check if mysql-connector is available
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


class MySQLClient(BaseDatabaseClient):
    """MySQL database client."""

    def connect(self) -> bool:
        """
        Establish MySQL connection.

        Returns:
            bool: True if connection successful, False otherwise
        """
        if not MYSQL_AVAILABLE:
            logger.error(
                "mysql-connector-python is not installed. "
                "Install with: pip install mysql-connector-python"
            )
            return False

        try:
            logger.info(
                f"Connecting to MySQL {self.database}@{self.host}:{self.port}..."
            )

            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()

            logger.info("MySQL connection established successfully")
            return True

        except mysql.connector.Error as e:
            logger.error(f"MySQL connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MySQL: {e}")
            return False

    def disconnect(self) -> None:
        """Close MySQL connection."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                logger.info("MySQL connection closed")
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
            logger.info("Executing MySQL query...")
            logger.debug(f"Query: {query}")

            self.cursor.execute(query, params)
            return True

        except mysql.connector.Error as e:
            logger.error(f"MySQL query execution failed: {e}")
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
