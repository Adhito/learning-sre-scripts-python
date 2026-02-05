"""
Setup script for the db_backup package.

This allows the package to be installed via pip:
    pip install -e .  # Development mode
    pip install .     # Regular install
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="db-backup",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Database backup tool with PGP encryption and S3-compatible storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/python-db-backup-query-to-object-storage",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.10",
    install_requires=[
        "psycopg2-binary>=2.9.9",
        "mysql-connector-python>=8.3.0",
        "boto3>=1.34.0",
        "python-gnupg>=0.5.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "db-backup=db_backup.cli:main",
        ],
    },
)
