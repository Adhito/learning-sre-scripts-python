"""
Database Backup Query to Object Storage

A Python package for backing up database query results to S3-compatible object storage
with PGP encryption support.

Features:
    - Multi-database support (PostgreSQL, MySQL)
    - Parameterized queries with date range filtering
    - Memory-efficient chunked CSV export
    - AES-256 symmetric PGP encryption
    - S3-compatible object storage (MinIO, AWS S3, GCP, etc.)
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from db_backup.backup.orchestrator import BackupOrchestrator
from db_backup.database.factory import get_database_client

__all__ = [
    "BackupOrchestrator",
    "get_database_client",
    "__version__",
]
