"""
Command-line interface for the database backup tool.

Provides argument parsing and the main entry point for the application.
"""

import argparse
from typing import Dict, Any

from db_backup import config
from db_backup.backup import BackupOrchestrator
from db_backup.utils.logging_config import setup_logging, get_logger

logger = get_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Database Backup to Object Storage with PGP Encryption',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Use configuration defaults
  python -m db_backup

  # PostgreSQL: Override table and date range
  python -m db_backup \\
      --db-type postgresql \\
      --table orders --date-column order_date \\
      --start "2025-01-01" --end "2025-01-02"

  # MySQL example
  python -m db_backup \\
      --db-type mysql --db-port 3306 \\
      --table transactions --date-column created_at \\
      --start yesterday --end today

  # Full custom configuration
  python -m db_backup \\
      --db-type postgresql \\
      --db-host db.example.com --db-port 5432 \\
      --db-name production --db-user backup_user \\
      --table transactions --date-column created_at \\
      --start yesterday --end today \\
      --pgp-password "secure_password" \\
      --s3-endpoint "http://localhost:9000" \\
      --s3-bucket "my-backups"

Environment Variables:
  All configuration options can also be set via environment variables
  with the prefix DB_BACKUP_. For example:
    DB_BACKUP_DB_TYPE, DB_BACKUP_DB_HOST, DB_BACKUP_PGP_PASSWORD, etc.
        '''
    )

    # Database arguments
    db_group = parser.add_argument_group('Database Configuration')
    db_group.add_argument(
        '--db-type', type=str, choices=['postgresql', 'mysql'],
        help='Database type (postgresql or mysql)'
    )
    db_group.add_argument('--db-host', type=str, help='Database host')
    db_group.add_argument('--db-port', type=int, help='Database port')
    db_group.add_argument('--db-name', type=str, help='Database name')
    db_group.add_argument('--db-user', type=str, help='Database username')
    db_group.add_argument('--db-password', type=str, help='Database password')

    # Query arguments
    query_group = parser.add_argument_group('Query Configuration')
    query_group.add_argument('--table', type=str, help='Table name to export')
    query_group.add_argument(
        '--date-column', type=str,
        help='Date column name for filtering'
    )
    query_group.add_argument(
        '--start', type=str,
        help='Start datetime (ISO 8601, "yesterday", "today", "now")'
    )
    query_group.add_argument(
        '--end', type=str,
        help='End datetime (ISO 8601, "yesterday", "today", "now")'
    )
    query_group.add_argument(
        '--where', type=str,
        help='Additional WHERE clause'
    )
    query_group.add_argument(
        '--chunk-size', type=int,
        help='Rows per chunk for large exports'
    )

    # Encryption arguments
    enc_group = parser.add_argument_group('Encryption Configuration')
    enc_group.add_argument(
        '--pgp-password', type=str,
        help='PGP encryption password'
    )
    enc_group.add_argument(
        '--gpg-home', type=str,
        help='GPG home directory'
    )
    enc_group.add_argument(
        '--cipher', type=str, default=None,
        choices=['AES256', 'AES192', 'AES128', 'TWOFISH', 'CAMELLIA256'],
        help='Encryption cipher algorithm'
    )

    # Storage arguments
    s3_group = parser.add_argument_group('Object Storage Configuration')
    s3_group.add_argument(
        '--s3-endpoint', type=str,
        help='S3 endpoint URL (empty string for AWS S3)'
    )
    s3_group.add_argument(
        '--s3-access-key', type=str,
        help='S3 access key'
    )
    s3_group.add_argument(
        '--s3-secret-key', type=str,
        help='S3 secret key'
    )
    s3_group.add_argument(
        '--s3-bucket', type=str,
        help='S3 bucket name'
    )
    s3_group.add_argument(
        '--s3-region', type=str,
        help='S3 region'
    )
    s3_group.add_argument(
        '--s3-prefix', type=str,
        help='S3 path prefix'
    )

    # Output arguments
    out_group = parser.add_argument_group('Output Configuration')
    out_group.add_argument(
        '--temp-dir', type=str,
        help='Temporary directory for files'
    )
    out_group.add_argument(
        '--keep-local', action='store_true',
        help='Keep local files after upload'
    )
    out_group.add_argument(
        '--output-pattern', type=str,
        help='Output filename pattern'
    )

    # Logging arguments
    log_group = parser.add_argument_group('Logging Configuration')
    log_group.add_argument(
        '--log-level', type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level'
    )

    return parser.parse_args()


def build_config(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Build configuration dictionary from arguments and defaults.

    Command-line arguments take precedence over environment variables,
    which take precedence over default values in config.py.

    Args:
        args: Parsed command-line arguments

    Returns:
        Configuration dictionary
    """
    return {
        # Database
        'db_type': args.db_type or config.DB_TYPE,
        'db_host': args.db_host or config.DB_HOST,
        'db_port': args.db_port or config.DB_PORT,
        'db_name': args.db_name or config.DB_NAME,
        'db_user': args.db_user or config.DB_USER,
        'db_password': args.db_password or config.DB_PASSWORD,

        # Query
        'table_name': args.table or config.TABLE_NAME,
        'date_column': args.date_column or config.DATE_COLUMN,
        'start_datetime': args.start or config.START_DATETIME,
        'end_datetime': args.end or config.END_DATETIME,
        'custom_where_clause': args.where or config.CUSTOM_WHERE_CLAUSE,
        'chunk_size': args.chunk_size or config.CHUNK_SIZE,

        # Encryption
        'pgp_password': args.pgp_password or config.PGP_PASSWORD,
        'gpg_home': args.gpg_home or config.GPG_HOME,
        'gpg_cipher_algo': args.cipher or config.GPG_CIPHER_ALGO,

        # Storage
        's3_endpoint_url': (
            args.s3_endpoint
            if args.s3_endpoint is not None
            else config.S3_ENDPOINT_URL
        ),
        's3_access_key': args.s3_access_key or config.S3_ACCESS_KEY,
        's3_secret_key': args.s3_secret_key or config.S3_SECRET_KEY,
        's3_bucket_name': args.s3_bucket or config.S3_BUCKET_NAME,
        's3_region': args.s3_region or config.S3_REGION,
        's3_path_prefix': args.s3_prefix or config.S3_PATH_PREFIX,

        # Output
        'temp_dir': args.temp_dir or config.TEMP_DIR,
        'keep_local_files': args.keep_local or config.KEEP_LOCAL_FILES,
        'output_filename_pattern': (
            args.output_pattern or config.OUTPUT_FILENAME_PATTERN
        ),
    }


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    setup_logging(args.log_level)

    # Build configuration
    backup_config = build_config(args)

    # Create and run orchestrator
    orchestrator = BackupOrchestrator(backup_config)

    if not orchestrator.initialize_components():
        logger.error("Failed to initialize backup components")
        return 1

    if orchestrator.run_backup():
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
