"""
Configuration management for the database backup tool.

This module provides default configuration values that can be overridden via:
1. Environment variables
2. Command-line arguments (handled in cli.py)

Environment variables take precedence over defaults.
Command-line arguments take precedence over environment variables.
"""

import os
from typing import Optional


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database type: "postgresql" or "mysql"
DB_TYPE: str = os.getenv("DB_BACKUP_DB_TYPE", "postgresql")

# Database connection settings
DB_HOST: str = os.getenv("DB_BACKUP_DB_HOST", "localhost")
DB_PORT: int = int(os.getenv("DB_BACKUP_DB_PORT", "5432"))
DB_NAME: str = os.getenv("DB_BACKUP_DB_NAME", "your_database")
DB_USER: str = os.getenv("DB_BACKUP_DB_USER", "your_username")
DB_PASSWORD: str = os.getenv("DB_BACKUP_DB_PASSWORD", "your_password")


# ============================================================================
# QUERY CONFIGURATION
# ============================================================================

# Table to export
TABLE_NAME: str = os.getenv("DB_BACKUP_TABLE_NAME", "transactions")

# Date column for filtering (varies by table)
DATE_COLUMN: str = os.getenv("DB_BACKUP_DATE_COLUMN", "created_at")

# Date range for export
# Supported values: "today", "yesterday", "now", or ISO 8601 format
START_DATETIME: str = os.getenv("DB_BACKUP_START_DATETIME", "yesterday")
END_DATETIME: str = os.getenv("DB_BACKUP_END_DATETIME", "today")

# Optional: Additional WHERE clause conditions
CUSTOM_WHERE_CLAUSE: str = os.getenv("DB_BACKUP_CUSTOM_WHERE", "")

# Chunk size for reading large result sets (rows per batch)
CHUNK_SIZE: int = int(os.getenv("DB_BACKUP_CHUNK_SIZE", "10000"))


# ============================================================================
# ENCRYPTION CONFIGURATION
# ============================================================================

# PGP/GPG symmetric encryption password
PGP_PASSWORD: str = os.getenv("DB_BACKUP_PGP_PASSWORD", "your_secure_encryption_password")

# GPG home directory (None = use system default)
GPG_HOME: Optional[str] = os.getenv("DB_BACKUP_GPG_HOME", None)

# Encryption algorithm (AES256 recommended for balance of security/performance)
# Options: AES256, AES192, AES128, TWOFISH, CAMELLIA256
GPG_CIPHER_ALGO: str = os.getenv("DB_BACKUP_GPG_CIPHER", "AES256")


# ============================================================================
# OBJECT STORAGE CONFIGURATION
# ============================================================================

# S3-compatible endpoint URL
# MinIO default: "http://localhost:9000"
# AWS S3: None (uses default AWS endpoint)
# GCP: "https://storage.googleapis.com"
S3_ENDPOINT_URL: Optional[str] = os.getenv("DB_BACKUP_S3_ENDPOINT", "http://localhost:9000")

# S3 credentials
S3_ACCESS_KEY: str = os.getenv("DB_BACKUP_S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY: str = os.getenv("DB_BACKUP_S3_SECRET_KEY", "minioadmin")

# Target bucket name
S3_BUCKET_NAME: str = os.getenv("DB_BACKUP_S3_BUCKET", "db-backups")

# AWS region (required for bucket creation)
S3_REGION: str = os.getenv("DB_BACKUP_S3_REGION", "us-east-1")

# S3 path prefix (folder structure in bucket)
# Available placeholders: {table}, {date}, {datetime}
S3_PATH_PREFIX: str = os.getenv("DB_BACKUP_S3_PREFIX", "backups/{table}/{date}/")


# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Local temporary directory for CSV and encrypted files
TEMP_DIR: str = os.getenv("DB_BACKUP_TEMP_DIR", "./temp_backups")

# Keep local files after upload (True/False)
KEEP_LOCAL_FILES: bool = os.getenv("DB_BACKUP_KEEP_LOCAL", "false").lower() == "true"

# File naming pattern
# Available placeholders: {table}, {start}, {end}, {datetime}
OUTPUT_FILENAME_PATTERN: str = os.getenv("DB_BACKUP_FILENAME_PATTERN", "{table}_{start}_{end}")

# Date format for filenames
FILENAME_DATE_FORMAT: str = "%Y%m%d_%H%M%S"


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL: str = os.getenv("DB_BACKUP_LOG_LEVEL", "INFO")

# Log format
LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
