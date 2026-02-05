"""
Crypto module - provides encryption functionality.

This module contains:
- PGPEncryptor: Encrypt files using PGP/GPG symmetric encryption
"""

from db_backup.crypto.pgp import PGPEncryptor

__all__ = [
    "PGPEncryptor",
]
