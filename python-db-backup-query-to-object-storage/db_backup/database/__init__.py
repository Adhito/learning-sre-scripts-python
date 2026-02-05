"""
Database module - provides database client abstraction.

This module contains:
- BaseDatabaseClient: Abstract base class defining the interface
- PostgreSQLClient: PostgreSQL implementation
- MySQLClient: MySQL implementation
- get_database_client: Factory function for creating appropriate client
"""

from db_backup.database.base import BaseDatabaseClient
from db_backup.database.postgresql import PostgreSQLClient
from db_backup.database.mysql import MySQLClient
from db_backup.database.factory import get_database_client

__all__ = [
    "BaseDatabaseClient",
    "PostgreSQLClient",
    "MySQLClient",
    "get_database_client",
]
