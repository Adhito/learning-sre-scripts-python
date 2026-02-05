"""
CSV Exporter for database query results.

Provides functionality to export database query results to CSV files
with support for chunked writing to handle large datasets efficiently.
"""

import csv
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from db_backup.utils.logging_config import get_logger

if TYPE_CHECKING:
    from db_backup.database.base import BaseDatabaseClient

logger = get_logger(__name__)


class CSVExporter:
    """Export database results to CSV files."""

    def __init__(self, output_dir: str):
        """
        Initialize CSV exporter.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_csv(self, db_client: "BaseDatabaseClient",
                      output_filename: str,
                      chunk_size: int = 10000) -> Optional[str]:
        """
        Export query results to CSV file.

        Args:
            db_client: Database client with executed query
            output_filename: Output filename (without extension)
            chunk_size: Rows per chunk for memory efficiency

        Returns:
            Path to CSV file or None if failed
        """
        try:
            csv_path = self.output_dir / f"{output_filename}.csv"

            # Get column names
            columns = db_client.get_column_names()
            if not columns:
                logger.error("No columns found in query result")
                return None

            logger.info(f"Exporting to CSV: {csv_path}")
            logger.info(f"Columns: {', '.join(columns)}")

            total_rows = 0

            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(columns)

                # Write data in chunks
                for chunk_num, rows in enumerate(db_client.fetch_rows_chunked(chunk_size), 1):
                    writer.writerows(rows)
                    total_rows += len(rows)
                    logger.info(
                        f"  Chunk {chunk_num}: Wrote {len(rows)} rows "
                        f"(Total: {total_rows})"
                    )

            file_size = csv_path.stat().st_size
            logger.info(
                f"CSV export completed: {total_rows} rows, {file_size:,} bytes"
            )

            return str(csv_path)

        except IOError as e:
            logger.error(f"Failed to write CSV file: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during CSV export: {e}")
            return None
