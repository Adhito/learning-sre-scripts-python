"""
Backup Orchestrator.

Coordinates the complete backup workflow:
1. Connect to database
2. Execute query
3. Export to CSV
4. Encrypt with PGP
5. Upload to object storage
6. Cleanup (optional)
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from db_backup.database import get_database_client, BaseDatabaseClient
from db_backup.export import CSVExporter
from db_backup.crypto import PGPEncryptor
from db_backup.storage import ObjectStorageClient
from db_backup.utils.dates import parse_datetime_config, format_filename
from db_backup.utils.logging_config import get_logger

logger = get_logger(__name__)


class BackupOrchestrator:
    """Orchestrates the complete backup workflow."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize backup orchestrator.

        Args:
            config: Configuration dictionary containing all backup parameters
        """
        self.config = config
        self.db_client: Optional[BaseDatabaseClient] = None
        self.csv_exporter: Optional[CSVExporter] = None
        self.pgp_encryptor: Optional[PGPEncryptor] = None
        self.storage_client: Optional[ObjectStorageClient] = None

    def initialize_components(self) -> bool:
        """
        Initialize all components.

        Returns:
            bool: True if all components initialized successfully
        """
        try:
            # Database client
            self.db_client = get_database_client(
                db_type=self.config['db_type'],
                host=self.config['db_host'],
                port=self.config['db_port'],
                database=self.config['db_name'],
                user=self.config['db_user'],
                password=self.config['db_password']
            )

            # CSV exporter
            self.csv_exporter = CSVExporter(self.config['temp_dir'])

            # PGP encryptor
            self.pgp_encryptor = PGPEncryptor(
                password=self.config['pgp_password'],
                gpg_home=self.config.get('gpg_home'),
                cipher_algo=self.config.get('gpg_cipher_algo', 'AES256')
            )

            # Object storage client
            self.storage_client = ObjectStorageClient(
                endpoint_url=self.config.get('s3_endpoint_url'),
                access_key=self.config['s3_access_key'],
                secret_key=self.config['s3_secret_key'],
                bucket_name=self.config['s3_bucket_name'],
                region=self.config.get('s3_region', 'us-east-1')
            )

            return True

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False

    def run_backup(self) -> bool:
        """
        Execute the complete backup workflow.

        Returns:
            bool: True if backup completed successfully
        """
        csv_path = None
        encrypted_path = None

        try:
            logger.info("=" * 60)
            logger.info("DATABASE BACKUP STARTED")
            logger.info("=" * 60)

            # Parse date range
            start_dt = parse_datetime_config(self.config['start_datetime'])
            end_dt = parse_datetime_config(self.config['end_datetime'])

            logger.info(f"Database Type: {self.config['db_type']}")
            logger.info(f"Table: {self.config['table_name']}")
            logger.info(f"Date Column: {self.config['date_column']}")
            logger.info(f"Date Range: {start_dt} to {end_dt}")
            logger.info("=" * 60)

            # Step 1: Connect to database
            logger.info("\n[Step 1/5] Connecting to database...")
            if not self.db_client.connect():
                return False

            # Step 2: Execute query
            logger.info("\n[Step 2/5] Executing export query...")
            query, params = self.db_client.build_export_query(
                table=self.config['table_name'],
                date_column=self.config['date_column'],
                start_dt=start_dt,
                end_dt=end_dt,
                custom_where=self.config.get('custom_where_clause')
            )

            if not self.db_client.execute_query(query, params):
                return False

            # Step 3: Export to CSV
            logger.info("\n[Step 3/5] Exporting to CSV...")
            output_filename = format_filename(
                self.config.get('output_filename_pattern', '{table}_{start}_{end}'),
                self.config['table_name'],
                start_dt,
                end_dt
            )

            csv_path = self.csv_exporter.export_to_csv(
                self.db_client,
                output_filename,
                self.config.get('chunk_size', 10000)
            )

            if not csv_path:
                return False

            # Step 4: Encrypt CSV
            logger.info("\n[Step 4/5] Encrypting CSV file...")
            encrypted_path = self.pgp_encryptor.encrypt_file(csv_path)

            if not encrypted_path:
                return False

            # Step 5: Upload to object storage
            logger.info("\n[Step 5/5] Uploading to object storage...")

            # Ensure bucket exists
            if not self.storage_client.create_bucket():
                return False

            # Build S3 key
            s3_prefix = self.config.get(
                's3_path_prefix',
                'backups/{table}/{date}/'
            ).format(
                table=self.config['table_name'],
                date=datetime.now().strftime('%Y-%m-%d'),
                datetime=datetime.now().strftime('%Y%m%d_%H%M%S')
            )
            s3_key = s3_prefix + Path(encrypted_path).name

            if not self.storage_client.upload_file(encrypted_path, s3_key):
                return False

            # Cleanup local files if configured
            if not self.config.get('keep_local_files', False):
                logger.info("\nCleaning up local files...")
                if csv_path and Path(csv_path).exists():
                    Path(csv_path).unlink()
                    logger.info(f"  Deleted: {csv_path}")
                if encrypted_path and Path(encrypted_path).exists():
                    Path(encrypted_path).unlink()
                    logger.info(f"  Deleted: {encrypted_path}")

            logger.info("\n" + "=" * 60)
            logger.info("BACKUP COMPLETED SUCCESSFULLY")
            logger.info(f"Location: s3://{self.config['s3_bucket_name']}/{s3_key}")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

        finally:
            # Cleanup
            if self.db_client:
                self.db_client.disconnect()
