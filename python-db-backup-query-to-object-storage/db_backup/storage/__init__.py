"""
Storage module - provides object storage functionality.

This module contains:
- ObjectStorageClient: S3-compatible object storage client
"""

from db_backup.storage.s3 import ObjectStorageClient

__all__ = [
    "ObjectStorageClient",
]
