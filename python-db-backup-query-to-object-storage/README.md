# Database Backup Query to Object Storage

A Python package that queries a database table with a configurable date range, exports results to CSV, encrypts with PGP (AES-256), and uploads to S3-compatible object storage.

## Features

- **Multi-database support**: PostgreSQL and MySQL
- **Parameterized queries**: Table name, date column, and date range are all configurable
- **Memory efficient**: Chunked CSV export for large tables
- **Secure encryption**: AES-256 symmetric PGP encryption
- **S3-compatible storage**: Works with MinIO, AWS S3, GCP Cloud Storage, and more
- **Flexible configuration**: Environment variables, config file, or command-line arguments
- **Modular design**: Clean separation of concerns for maintainability

## Project Structure

```
python-db-backup-query-to-object-storage/
├── db_backup/                    # Main package
│   ├── __init__.py              # Package initialization
│   ├── __main__.py              # Entry point for python -m
│   ├── cli.py                   # Command-line interface
│   ├── config.py                # Configuration management
│   │
│   ├── database/                # Database module
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract base class
│   │   ├── postgresql.py        # PostgreSQL implementation
│   │   ├── mysql.py             # MySQL implementation
│   │   └── factory.py           # Factory function
│   │
│   ├── backup/                  # Backup module
│   │   ├── __init__.py
│   │   └── orchestrator.py      # Backup workflow orchestration
│   │
│   ├── export/                  # Export module
│   │   ├── __init__.py
│   │   └── csv_exporter.py      # CSV export functionality
│   │
│   ├── crypto/                  # Encryption module
│   │   ├── __init__.py
│   │   └── pgp.py               # PGP encryption
│   │
│   ├── storage/                 # Storage module
│   │   ├── __init__.py
│   │   └── s3.py                # S3-compatible storage
│   │
│   └── utils/                   # Utility module
│       ├── __init__.py
│       ├── dates.py             # Date parsing utilities
│       └── logging_config.py    # Logging configuration
│
├── python-db-backup-query-to-object-storage.py  # Legacy single-file script
├── setup.py                     # Package setup
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## Requirements

- Python 3.10+
- GPG (GnuPG) installed on the system
- Access to a PostgreSQL or MySQL database
- Access to S3-compatible object storage

## Installation

### Option 1: Install as Package (Recommended)

```bash
# Clone the repository
cd python-db-backup-query-to-object-storage

# Install in development mode
pip install -e .

# Or regular install
pip install .
```

### Option 2: Install Dependencies Only

```bash
cd python-db-backup-query-to-object-storage
pip install -r requirements.txt
```

### GPG Installation

Ensure GPG is installed:
- **Windows**: Install [Gpg4win](https://www.gpg4win.org/)
- **macOS**: `brew install gnupg`
- **Linux**: `apt install gnupg` or `yum install gnupg2`

## Configuration

Configuration can be provided in three ways (in order of precedence):

1. **Command-line arguments** (highest priority)
2. **Environment variables**
3. **Default values in config.py** (lowest priority)

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
# Edit .env with your settings
```

Key environment variables:
```bash
# Database
DB_BACKUP_DB_TYPE=postgresql
DB_BACKUP_DB_HOST=localhost
DB_BACKUP_DB_PORT=5432
DB_BACKUP_DB_NAME=your_database
DB_BACKUP_DB_USER=your_username
DB_BACKUP_DB_PASSWORD=your_password

# Query
DB_BACKUP_TABLE_NAME=transactions
DB_BACKUP_DATE_COLUMN=created_at
DB_BACKUP_START_DATETIME=yesterday
DB_BACKUP_END_DATETIME=today

# Encryption
DB_BACKUP_PGP_PASSWORD=your_secure_password

# Storage (MinIO example)
DB_BACKUP_S3_ENDPOINT=http://localhost:9000
DB_BACKUP_S3_ACCESS_KEY=minioadmin
DB_BACKUP_S3_SECRET_KEY=minioadmin
DB_BACKUP_S3_BUCKET=db-backups
```

## Usage

### As Installed Package

```bash
# After pip install
db-backup --help

# Run backup with defaults
db-backup

# With custom parameters
db-backup --table orders --date-column order_date --start yesterday --end today
```

### As Python Module

```bash
# Run as module
python -m db_backup --help

# Run backup with defaults
python -m db_backup

# PostgreSQL example
python -m db_backup \
    --db-type postgresql \
    --db-host localhost --db-port 5432 \
    --db-name production --db-user backup_user \
    --table transactions --date-column created_at \
    --start "2025-01-01" --end "2025-01-02"

# MySQL example
python -m db_backup \
    --db-type mysql \
    --db-host mysql.example.com --db-port 3306 \
    --db-name production --db-user backup_user \
    --table orders --date-column order_date \
    --start yesterday --end today
```

### Legacy Single-File Script

The original single-file script is still available:

```bash
python python-db-backup-query-to-object-storage.py --help
```

### With Custom WHERE Clause

```bash
python -m db_backup \
    --table transactions \
    --date-column created_at \
    --start yesterday --end today \
    --where "status = 'completed' AND amount > 100"
```

### Upload to AWS S3

```bash
python -m db_backup \
    --s3-endpoint "" \
    --s3-access-key "AKIAIOSFODNN7EXAMPLE" \
    --s3-secret-key "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
    --s3-bucket "my-backups" \
    --s3-region "us-west-2"
```

## Date Format Options

The `--start` and `--end` arguments accept:

| Format | Example | Description |
|--------|---------|-------------|
| `yesterday` | `--start yesterday` | Start of yesterday (00:00:00) |
| `today` | `--end today` | Start of today (00:00:00) |
| `now` | `--end now` | Current datetime |
| ISO 8601 date | `--start 2025-01-01` | Specific date at 00:00:00 |
| ISO 8601 datetime | `--start 2025-01-01T10:30:00` | Specific datetime |

## Decrypting Backup Files

To decrypt a backup file using GPG:

```bash
# Interactive (prompts for password)
gpg --decrypt --output backup.csv backup.csv.gpg

# Non-interactive (password in environment variable)
echo "$BACKUP_PASSWORD" | gpg --batch --yes --passphrase-fd 0 \
    --decrypt --output backup.csv backup.csv.gpg
```

## Command-Line Arguments Reference

```
Database Configuration:
  --db-type       Database type (postgresql or mysql)
  --db-host       Database host
  --db-port       Database port
  --db-name       Database name
  --db-user       Database username
  --db-password   Database password

Query Configuration:
  --table         Table name to export
  --date-column   Date column name for filtering
  --start         Start datetime
  --end           End datetime
  --where         Additional WHERE clause
  --chunk-size    Rows per chunk for large exports (default: 10000)

Encryption Configuration:
  --pgp-password  PGP encryption password
  --gpg-home      GPG home directory
  --cipher        Encryption cipher (AES256, AES192, AES128, TWOFISH, CAMELLIA256)

Object Storage Configuration:
  --s3-endpoint   S3 endpoint URL (empty string for AWS S3)
  --s3-access-key S3 access key
  --s3-secret-key S3 secret key
  --s3-bucket     S3 bucket name
  --s3-region     S3 region
  --s3-prefix     S3 path prefix

Output Configuration:
  --temp-dir      Temporary directory for files
  --keep-local    Keep local files after upload
  --output-pattern Output filename pattern

Logging Configuration:
  --log-level     Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

## Programmatic Usage

You can also use the package programmatically:

```python
from db_backup import BackupOrchestrator, get_database_client

# Create configuration
config = {
    'db_type': 'postgresql',
    'db_host': 'localhost',
    'db_port': 5432,
    'db_name': 'mydb',
    'db_user': 'user',
    'db_password': 'password',
    'table_name': 'transactions',
    'date_column': 'created_at',
    'start_datetime': 'yesterday',
    'end_datetime': 'today',
    'pgp_password': 'secret',
    's3_endpoint_url': 'http://localhost:9000',
    's3_access_key': 'minioadmin',
    's3_secret_key': 'minioadmin',
    's3_bucket_name': 'backups',
    'temp_dir': './temp',
}

# Run backup
orchestrator = BackupOrchestrator(config)
orchestrator.initialize_components()
success = orchestrator.run_backup()
```

## Workflow

1. **Connect** to the database (PostgreSQL or MySQL)
2. **Execute query** with date range filter on the specified date column
3. **Export to CSV** in chunks for memory efficiency
4. **Encrypt** the CSV file with AES-256 symmetric encryption
5. **Upload** the encrypted file to S3-compatible storage
6. **Cleanup** local files (optional)

## Development

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black db_backup/
```

### Type Checking

```bash
mypy db_backup/
```

### Linting

```bash
flake8 db_backup/
```

## Troubleshooting

### GPG Not Found

Ensure GPG is installed and in your PATH:
```bash
gpg --version
```

### Database Connection Failed

- Verify database credentials
- Check if the database server is accessible
- Ensure the database port is not blocked by firewall

### S3 Upload Failed

- Verify S3 credentials
- Check if the bucket exists or create it manually
- For MinIO, ensure the service is running at the specified endpoint

### Import Errors

If you see import errors, make sure you've installed the package:
```bash
pip install -e .
```

## License

MIT License
