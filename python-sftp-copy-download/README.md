# SFTP Download Script

A robust, feature-rich Python script for downloading files and folders from SFTP servers with support for date-based organization, wildcards, and automatic log rotation.

## Requirements

- Python 3.6+
- `paramiko` library

## Installation

1. Install the required library:
```bash
pip install paramiko
```

2. Download the script and save it as `sftp_download.py`

## Quick Start

### Basic Configuration

Edit the configuration section at the top of the script:

```python
# SFTP Server Configuration
SFTP_HOST = "your-sftp-server.com"
SFTP_PORT = 22
SFTP_USERNAME = "your_username"
SFTP_PASSWORD = "your_password"

# Date Configuration
DOWNLOAD_DATE = "today"  # Options: today, yesterday, tomorrow, +N, -N, YYYY-MM-DD

# Download Configuration
USE_DOWNLOAD_LIST = True  # Set to False for single file mode
```

### Run the Script

```bash
python sftp_download.py
```

## Configuration Reference

### 1. SFTP Server Configuration

| Parameter | Description | Example |
|-----------|-------------|---------|
| `SFTP_HOST` | SFTP server hostname or IP address | `"sftp.example.com"` or `"192.168.1.100"` |
| `SFTP_PORT` | SFTP server port | `22` (default) |
| `SFTP_USERNAME` | Username for authentication | `"sftpuser"` |
| `SFTP_PASSWORD` | Password for authentication | `"your_password"` |
| `SFTP_PRIVATE_KEY_PATH` | Path to SSH private key (optional) | `"/home/user/.ssh/id_rsa"` or `None` |
| `CONNECTION_TIMEOUT` | Connection timeout in seconds | `30` |

**Note:** For production use, SSH key authentication is recommended over password authentication.

### 2. Date Configuration

| Parameter | Description | Example |
|-----------|-------------|---------|
| `DOWNLOAD_DATE` | Target date for downloads | See options below |
| `DATE_FORMAT` | Format for date folders | `"%Y-%m-%d"` (2025-10-14) |
| `BASE_DOWNLOAD_DIR` | Base directory for downloads | `"./sftp_downloads"` |
