import paramiko
import os
import logging
from pathlib import Path
from typing import Optional, List

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

REMOTE_FILE_PATH = "/home/sftpuser/sample_file_part_01.txt"
LOCAL_DOWNLOAD_PATH = "./sample_file_part_01.txt"  # Will save in current directory

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


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to download file from SFTP server"""
    
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
        
        # Check if remote file exists
        if not client.file_exists(REMOTE_FILE_PATH):
            logger.error(f"Remote file does not exist: {REMOTE_FILE_PATH}")
            return
        
        # Download file
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
