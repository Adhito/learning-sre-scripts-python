"""
S3-compatible object storage client.

Provides functionality to upload files to S3-compatible storage services
including AWS S3, MinIO, GCP Cloud Storage, DigitalOcean Spaces, etc.
"""

from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from db_backup.utils.logging_config import get_logger

logger = get_logger(__name__)


class ProgressCallback:
    """Callback for tracking upload progress."""

    def __init__(self, filename: str, file_size: int):
        """
        Initialize progress callback.

        Args:
            filename: Name of file being uploaded
            file_size: Total file size in bytes
        """
        self.filename = filename
        self.file_size = file_size
        self.uploaded = 0
        self.last_percent = 0

    def __call__(self, bytes_amount: int) -> None:
        """
        Called by boto3 during upload with bytes transferred.

        Args:
            bytes_amount: Number of bytes just transferred
        """
        self.uploaded += bytes_amount
        percent = int((self.uploaded / self.file_size) * 100) if self.file_size > 0 else 100

        # Log every 10%
        if percent >= self.last_percent + 10:
            logger.info(
                f"  Upload progress: {percent}% "
                f"({self.uploaded:,}/{self.file_size:,} bytes)"
            )
            self.last_percent = percent


class ObjectStorageClient:
    """S3-compatible object storage client."""

    def __init__(self, endpoint_url: Optional[str], access_key: str,
                 secret_key: str, bucket_name: str, region: str = "us-east-1"):
        """
        Initialize object storage client.

        Args:
            endpoint_url: S3 endpoint URL (None for AWS S3)
            access_key: Access key ID
            secret_key: Secret access key
            bucket_name: Target bucket name
            region: AWS region
        """
        self.endpoint_url = endpoint_url
        self.bucket_name = bucket_name
        self.region = region

        # Initialize boto3 client
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

    def bucket_exists(self) -> bool:
        """
        Check if the target bucket exists.

        Returns:
            bool: True if bucket exists, False otherwise
        """
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                logger.warning(f"Bucket not found: {self.bucket_name}")
            else:
                logger.error(f"Error checking bucket: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking bucket: {e}")
            return False

    def create_bucket(self) -> bool:
        """
        Create the target bucket if it doesn't exist.

        Returns:
            bool: True if created or already exists, False on error
        """
        try:
            if self.bucket_exists():
                return True

            logger.info(f"Creating bucket: {self.bucket_name}")

            if self.region == 'us-east-1':
                self.client.create_bucket(Bucket=self.bucket_name)
            else:
                self.client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )

            logger.info(f"Bucket created: {self.bucket_name}")
            return True

        except ClientError as e:
            logger.error(f"Failed to create bucket: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating bucket: {e}")
            return False

    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """
        Upload a file to S3.

        Args:
            local_path: Path to local file
            s3_key: S3 object key (path in bucket)

        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            local_path = Path(local_path)

            if not local_path.exists():
                logger.error(f"Local file not found: {local_path}")
                return False

            file_size = local_path.stat().st_size

            logger.info("Uploading to S3...")
            logger.info(f"  Local: {local_path}")
            logger.info(f"  Bucket: {self.bucket_name}")
            logger.info(f"  Key: {s3_key}")
            logger.info(f"  Size: {file_size:,} bytes")

            # Upload with progress callback
            self.client.upload_file(
                str(local_path),
                self.bucket_name,
                s3_key,
                Callback=ProgressCallback(local_path.name, file_size)
            )

            logger.info(f"Upload completed: s3://{self.bucket_name}/{s3_key}")
            return True

        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return False

    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Download a file from S3.

        Args:
            s3_key: S3 object key (path in bucket)
            local_path: Path for local file

        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            local_path = Path(local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info("Downloading from S3...")
            logger.info(f"  Bucket: {self.bucket_name}")
            logger.info(f"  Key: {s3_key}")
            logger.info(f"  Local: {local_path}")

            self.client.download_file(
                self.bucket_name,
                s3_key,
                str(local_path)
            )

            file_size = local_path.stat().st_size
            logger.info(f"Download completed: {file_size:,} bytes")
            return True

        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            return False

    def list_objects(self, prefix: str = "") -> list:
        """
        List objects in the bucket.

        Args:
            prefix: Filter objects by prefix (optional)

        Returns:
            List of object keys
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            objects = []
            for obj in response.get('Contents', []):
                objects.append(obj['Key'])

            return objects

        except ClientError as e:
            logger.error(f"Failed to list objects: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing objects: {e}")
            return []

    def delete_object(self, s3_key: str) -> bool:
        """
        Delete an object from S3.

        Args:
            s3_key: S3 object key to delete

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            logger.info(f"Deleting object: s3://{self.bucket_name}/{s3_key}")

            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )

            logger.info("Object deleted successfully")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete object: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting object: {e}")
            return False
