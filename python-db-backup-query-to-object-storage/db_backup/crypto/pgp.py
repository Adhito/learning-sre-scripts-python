"""
PGP/GPG encryption module.

Provides symmetric encryption using GPG with support for
various cipher algorithms (AES256, AES192, AES128, etc.).
"""

from pathlib import Path
from typing import Optional

import gnupg

from db_backup.utils.logging_config import get_logger

logger = get_logger(__name__)


class PGPEncryptor:
    """Encrypt files using PGP/GPG symmetric encryption."""

    def __init__(self, password: str, gpg_home: Optional[str] = None,
                 cipher_algo: str = "AES256"):
        """
        Initialize PGP encryptor.

        Args:
            password: Encryption password
            gpg_home: GPG home directory (None for system default)
            cipher_algo: Cipher algorithm (AES256 recommended)
        """
        self.password = password
        self.cipher_algo = cipher_algo

        # Initialize GPG
        self.gpg = gnupg.GPG(gnupghome=gpg_home)
        self.gpg.encoding = 'utf-8'

    def encrypt_file(self, input_path: str,
                     output_path: Optional[str] = None) -> Optional[str]:
        """
        Encrypt a file using symmetric encryption.

        Args:
            input_path: Path to input file
            output_path: Path for encrypted file (optional, defaults to input + .gpg)

        Returns:
            Path to encrypted file or None if failed
        """
        try:
            input_path = Path(input_path)

            if not input_path.exists():
                logger.error(f"Input file not found: {input_path}")
                return None

            if output_path is None:
                output_path = str(input_path) + ".gpg"

            logger.info(f"Encrypting file: {input_path}")
            logger.info(f"Output: {output_path}")
            logger.info(f"Cipher: {self.cipher_algo}")

            with open(input_path, 'rb') as f:
                encrypted_data = self.gpg.encrypt_file(
                    f,
                    recipients=None,  # Symmetric encryption (no recipient)
                    symmetric=self.cipher_algo,
                    passphrase=self.password,
                    output=output_path,
                    armor=False  # Binary output for smaller file size
                )

            if encrypted_data.ok:
                encrypted_size = Path(output_path).stat().st_size
                original_size = input_path.stat().st_size
                logger.info(
                    f"Encryption completed: {original_size:,} -> {encrypted_size:,} bytes"
                )
                return output_path
            else:
                logger.error(f"Encryption failed: {encrypted_data.status}")
                return None

        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None

    def decrypt_file(self, input_path: str,
                     output_path: Optional[str] = None) -> Optional[str]:
        """
        Decrypt a file using symmetric encryption.

        Args:
            input_path: Path to encrypted file
            output_path: Path for decrypted file (optional)

        Returns:
            Path to decrypted file or None if failed
        """
        try:
            input_path = Path(input_path)

            if not input_path.exists():
                logger.error(f"Input file not found: {input_path}")
                return None

            if output_path is None:
                # Remove .gpg extension if present
                if str(input_path).endswith('.gpg'):
                    output_path = str(input_path)[:-4]
                else:
                    output_path = str(input_path) + ".decrypted"

            logger.info(f"Decrypting file: {input_path}")
            logger.info(f"Output: {output_path}")

            with open(input_path, 'rb') as f:
                decrypted_data = self.gpg.decrypt_file(
                    f,
                    passphrase=self.password,
                    output=output_path
                )

            if decrypted_data.ok:
                decrypted_size = Path(output_path).stat().st_size
                logger.info(f"Decryption completed: {decrypted_size:,} bytes")
                return output_path
            else:
                logger.error(f"Decryption failed: {decrypted_data.status}")
                return None

        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None
