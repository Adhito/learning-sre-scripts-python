import paramiko
import os
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION VARIABLES - Modify these as needed
# ============================================================================

SFTP_HOST = "sftp.example.com"
SFTP_PORT = 22
SFTP_USERNAME = "your_username"
SFTP_PASSWORD = "your_password"  # Use SSH key authentication in production
SFTP_PRIVATE_KEY_PATH = None  # Path to private key file (optional)

# Single file download (legacy support)
REMOTE_FILE_PATH = "/home/sftpuser/Laporan_10_2025_Part_01.txt"
LOCAL_DOWNLOAD_PATH = "./Laporan_10_2025_Part_01.txt"

# Multiple files/folders configuration
# Format: List of tuples (remote_path, local_path)
DOWNLOAD_LIST = [
    ("/home/sftpuser/Laporan_10_2025_Part_01.txt", "./downloads/Laporan_10_2025_Part_01.txt"),
    ("/home/sftpuser/Laporan_10_2025_Part_02.txt", "./downloads/Laporan_10_2025_Part_02.txt"),
    ("/home/sftpuser/reports/", "./downloads/reports/"),  # Download entire folder
    ("/home/sftpuser/data/file.csv", "./downloads/data.csv"),
]

# Set to True to use DOWNLOAD_LIST, False to use single file mode
USE_DOWNLOAD_LIST = False

# Connection timeout in seconds
CONNECTION_TIMEOUT = 30


# ============================================================================
# SFTP CLIENT CLASS
# ============================================================================

class SFTPClient:
    """Robust SFTP client for file operations"""
    
    def __init__(self, host: str, port: int, username: str, 
                 password: Optional[str] = None, 
                 private_key_path: Optional[str] = None,
                 timeout: int = 30):
        """
        Initialize SFTP client
        
        Args:
            host: SFTP server hostname or IP
            port: SFTP server port
            username: Username for authentication
            password: Password for authentication (optional)
            private_key_path: Path to private key file (optional)
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.private_key_path = private_key_path
        self.timeout = timeout
        self.transport = None
        self.sftp = None
    
    def connect(self) -> bool:
        """
        Establish SFTP connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to {self.host}:{self.port}...")
            
            # Create SSH transport
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.set_keepalive(30)
            
            # Authenticate
            if self.private_key_path:
                # Use private key authentication
                private_key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
                self.transport.connect(username=self.username, pkey=private_key)
                logger.info("Authenticated using private key")
            elif self.password:
                # Use password authentication
                self.transport.connect(username=self.username, password=self.password)
                logger.info("Authenticated using password")
            else:
                logger.error("No authentication method provided")
                return False
            
            # Create SFTP session
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logger.info("SFTP connection established successfully")
            return True
            
        except paramiko.AuthenticationException:
            logger.error("Authentication failed")
            return False
        except paramiko.SSHException as e:
            logger.error(f"SSH connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close SFTP connection"""
        try:
            if self.sftp:
                self.sftp.close()
                logger.info("SFTP connection closed")
            if self.transport:
                self.transport.close()
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download a file from SFTP server
        
        Args:
            remote_path: Path to remote file
            local_path: Path where file should be saved locally
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            # Convert to absolute path and normalize
            local_path = os.path.abspath(local_path)
            
            # Ensure local directory exists
            local_dir = os.path.dirname(local_path)
            if local_dir:
                Path(local_dir).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading {remote_path} to {local_path}...")
            
            # Download file with callback for progress
            def progress_callback(transferred, total):
                percent = (transferred / total) * 100 if total > 0 else 0
                logger.debug(f"Progress: {percent:.1f}% ({transferred}/{total} bytes)")
            
            self.sftp.get(remote_path, local_path, callback=progress_callback)
            
            # Verify file was created
            if os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                logger.info(f"File downloaded successfully to {local_path}")
                logger.info(f"File size: {file_size} bytes")
            else:
                logger.error(f"File was not created at {local_path}")
                return False
            
            return True
            
        except FileNotFoundError:
            logger.error(f"Remote file not found: {remote_path}")
            return False
        except PermissionError:
            logger.error(f"Permission denied: {local_path}")
            return False
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Upload a file to SFTP server
        
        Args:
            local_path: Path to local file
            remote_path: Path where file should be saved on server
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            if not os.path.exists(local_path):
                logger.error(f"Local file not found: {local_path}")
                return False
            
            logger.info(f"Uploading {local_path} to {remote_path}...")
            self.sftp.put(local_path, remote_path)
            logger.info(f"File uploaded successfully to {remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    def list_directory(self, remote_path: str = ".") -> Optional[List[str]]:
        """
        List files in a remote directory
        
        Args:
            remote_path: Path to remote directory
            
        Returns:
            List of filenames or None if failed
        """
        try:
            logger.info(f"Listing directory: {remote_path}")
            files = self.sftp.listdir(remote_path)
            return files
        except Exception as e:
            logger.error(f"Failed to list directory: {e}")
            return None
    
    def is_directory(self, remote_path: str) -> bool:
        """
        Check if a remote path is a directory
        
        Args:
            remote_path: Path to check
            
        Returns:
            bool: True if directory, False otherwise
        """
        try:
            import stat
            file_stat = self.sftp.stat(remote_path)
            return stat.S_ISDIR(file_stat.st_mode)
        except Exception as e:
            logger.error(f"Error checking if path is directory: {e}")
            return False
    
    def download_directory(self, remote_dir: str, local_dir: str) -> bool:
        """
        Recursively download an entire directory
        
        Args:
            remote_dir: Path to remote directory
            local_dir: Path to local directory
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            # Create local directory
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"Downloading directory {remote_dir} to {local_dir}...")
            
            # List all items in remote directory
            items = self.sftp.listdir_attr(remote_dir)
            
            for item in items:
                remote_item_path = os.path.join(remote_dir, item.filename).replace("\\", "/")
                local_item_path = os.path.join(local_dir, item.filename)
                
                # Check if item is a directory
                import stat
                if stat.S_ISDIR(item.st_mode):
                    # Recursively download subdirectory
                    self.download_directory(remote_item_path, local_item_path)
                else:
                    # Download file
                    logger.info(f"  Downloading file: {item.filename}")
                    self.sftp.get(remote_item_path, local_item_path)
            
            logger.info(f"Directory downloaded successfully to {local_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download directory: {e}")
            return False
    
    def download_with_wildcard(self, remote_pattern: str, local_dir: str) -> bool:
        """
        Download multiple files matching a pattern
        
        Args:
            remote_pattern: Pattern like "/path/to/*.txt"
            local_dir: Directory to save files
            
        Returns:
            bool: True if at least one file downloaded
        """
        try:
            import fnmatch
            
            # Split pattern into directory and filename pattern
            remote_dir = os.path.dirname(remote_pattern)
            pattern = os.path.basename(remote_pattern)
            
            # Create local directory
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Searching for files matching: {remote_pattern}")
            
            # List files in remote directory
            files = self.sftp.listdir(remote_dir)
            matched_files = [f for f in files if fnmatch.fnmatch(f, pattern)]
            
            if not matched_files:
                logger.warning(f"No files matched pattern: {remote_pattern}")
                return False
            
            logger.info(f"Found {len(matched_files)} matching files")
            
            # Download each matched file
            success_count = 0
            for filename in matched_files:
                remote_path = os.path.join(remote_dir, filename).replace("\\", "/")
                local_path = os.path.join(local_dir, filename)
                
                if self.download_file(remote_path, local_path):
                    success_count += 1
            
            logger.info(f"Downloaded {success_count}/{len(matched_files)} files")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Wildcard download failed: {e}")
            return False
    def file_exists(self, remote_path: str) -> bool:
        """
        Check if a file exists on the server
        
        Args:
            remote_path: Path to remote file
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            self.sftp.stat(remote_path)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error checking file existence: {e}")
            return False
    
    def download_items(self, download_list: List[tuple]) -> dict:
        """
        Download multiple files/folders from a list
        
        Args:
            download_list: List of tuples (remote_path, local_path)
            
        Returns:
            dict: Statistics of downloads (success, failed, total)
        """
        stats = {"success": 0, "failed": 0, "total": len(download_list)}
        
        for idx, (remote_path, local_path) in enumerate(download_list, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing item {idx}/{stats['total']}")
            logger.info(f"{'='*60}")
            
            try:
                # Check if remote path exists
                if not self.file_exists(remote_path):
                    logger.error(f"Remote path does not exist: {remote_path}")
                    stats["failed"] += 1
                    continue
                
                # Check if it's a wildcard pattern
                if '*' in remote_path or '?' in remote_path:
                    success = self.download_with_wildcard(remote_path, local_path)
                # Check if it's a directory
                elif self.is_directory(remote_path):
                    success = self.download_directory(remote_path, local_path)
                # It's a file
                else:
                    success = self.download_file(remote_path, local_path)
                
                if success:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing {remote_path}: {e}")
                stats["failed"] += 1
        
        return stats


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to download file(s) from SFTP server"""
    
    # Create SFTP client
    client = SFTPClient(
        host=SFTP_HOST,
        port=SFTP_PORT,
        username=SFTP_USERNAME,
        password=SFTP_PASSWORD,
        private_key_path=SFTP_PRIVATE_KEY_PATH,
        timeout=CONNECTION_TIMEOUT
    )
    
    try:
        # Connect to server
        if not client.connect():
            logger.error("Failed to establish connection")
            return
        
        # Multiple files/folders mode
        if USE_DOWNLOAD_LIST:
            logger.info(f"Starting download of {len(DOWNLOAD_LIST)} items...")
            stats = client.download_items(DOWNLOAD_LIST)
            
            logger.info(f"\n{'='*60}")
            logger.info("DOWNLOAD SUMMARY")
            logger.info(f"{'='*60}")
            logger.info(f"Total items: {stats['total']}")
            logger.info(f"Successful: {stats['success']}")
            logger.info(f"Failed: {stats['failed']}")
            logger.info(f"{'='*60}")
        
        # Single file mode
        else:
            # Check if remote file exists
            if not client.file_exists(REMOTE_FILE_PATH):
                logger.error(f"Remote file does not exist: {REMOTE_FILE_PATH}")
                return
            
            # Check if it's a directory or file
            if client.is_directory(REMOTE_FILE_PATH):
                success = client.download_directory(REMOTE_FILE_PATH, LOCAL_DOWNLOAD_PATH)
            else:
                success = client.download_file(REMOTE_FILE_PATH, LOCAL_DOWNLOAD_PATH)
            
            if success:
                logger.info("File transfer completed successfully!")
            else:
                logger.error("File transfer failed")
    
    finally:
        # Always disconnect
        client.disconnect()


if __name__ == "__main__":
    main()
