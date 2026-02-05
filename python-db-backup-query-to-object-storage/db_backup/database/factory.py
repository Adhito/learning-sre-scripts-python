"""
Database client factory.

Provides a factory function to create the appropriate database client
based on the specified database type.
"""

from db_backup.database.base import BaseDatabaseClient
from db_backup.database.postgresql import PostgreSQLClient
from db_backup.database.mysql import MySQLClient
from db_backup.utils.logging_config import get_logger

logger = get_logger(__name__)


def get_database_client(db_type: str, host: str, port: int, database: str,
                        user: str, password: str) -> BaseDatabaseClient:
    """
    Factory function to create the appropriate database client.

    Args:
        db_type: Database type ("postgresql" or "mysql")
        host: Database host
        port: Database port
        database: Database name
        user: Username
        password: Password

    Returns:
        Database client instance

    Raises:
        ValueError: If db_type is not supported
    """
    db_type = db_type.lower()

    if db_type == "postgresql":
        logger.debug("Creating PostgreSQL client")
        return PostgreSQLClient(host, port, database, user, password)
    elif db_type == "mysql":
        logger.debug("Creating MySQL client")
        return MySQLClient(host, port, database, user, password)
    else:
        raise ValueError(
            f"Unsupported database type: {db_type}. "
            "Supported types: 'postgresql', 'mysql'"
        )
