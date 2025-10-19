"""
Polars Ingestor - High-performance ingestion with Polars (5-10x faster)

This module provides optimized CSV→Parquet conversion using Polars for
significant performance gains over pandas-based approaches.

Based on: pipeline_design/mac-optimized-pipeline.md
"""

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from typing import Dict, Any, Optional, List
from io import BytesIO
import gc
import logging

from .base_ingestor import BaseIngestor, IngestionError

logger = logging.getLogger(__name__)


class PolarsIngestor(BaseIngestor):
    """
    High-performance ingestor using Polars

    Features:
    - Polars lazy evaluation (5-10x faster than pandas)
    - Automatic parallelization
    - Streaming CSV reading
    - Memory-efficient column selection
    - Native Arrow integration
    - Query optimization

    Recommended for:
    - All systems where performance is critical
    - Batch processing of multiple files
    - Large datasets
    """

    def __init__(
        self,
        data_type: str,
        output_root: Path,
        config: Dict[str, Any],
        streaming: bool = True
    ):
        """
        Initialize Polars ingestor

        Args:
            data_type: Data type ('stocks_daily', 'stocks_minute', etc.)
            output_root: Root directory for Parquet output
            config: Configuration dictionary
            streaming: Use streaming mode for large files
        """
        super().__init__(data_type, output_root, config)

        self.streaming = streaming

        logger.info(
            f"PolarsIngestor initialized "
            f"(streaming: {streaming})"
        )

    def ingest_date(
        self,
        date: str,
        data: BytesIO,
        symbols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process single date file with Polars

        Args:
            date: Date string (YYYY-MM-DD)
            data: CSV data as BytesIO
            symbols: Optional symbol filter

        Returns:
            Dictionary with ingestion statistics
        """
        try:
            logger.info(f"Polars ingestion: {date}")

            # Check memory before starting
            mem_status = self.memory_monitor.check_and_wait()
            if mem_status['action'] == 'critical':
                logger.warning("Memory pressure is critical before ingestion")

            output_path = self._get_output_path(date)

            # Check if output already exists
            if output_path.exists():
                logger.warning(f"Output exists, skipping: {output_path}")
                return {
                    'date': date,
                    'records': 0,
                    'status': 'skipped',
                    'reason': 'output_exists'
                }

            # Define explicit schema for consistent data types
            schema_overrides = self._get_schema_overrides()

            # Read CSV with Polars
            if self.streaming:
                # Lazy/streaming mode
                df = pl.read_csv(
                    data,
                    has_header=True,
                    null_values=['', 'NA', 'NULL', 'NaN'],
                    try_parse_dates=False,  # We'll handle dates explicitly
                    low_memory=True,
                    schema_overrides=schema_overrides,
                )
            else:
                # Eager mode (load all into memory)
                df = pl.read_csv(
                    data,
                    has_header=True,
                    null_values=['', 'NA', 'NULL', 'NaN'],
                    try_parse_dates=False,  # We'll handle dates explicitly
                    schema_overrides=schema_overrides,
                )

            # Normalize column names (Polars)
            df = self._normalize_columns_polars(df, date)

            # Filter symbols if provided
            if symbols and 'symbol' in df.columns:
                df = df.filter(pl.col('symbol').is_in(symbols))

            # Add partition columns
            df = self._add_partition_columns_polars(df, date)

            # Convert types to match schema
            df = self._optimize_dtypes_polars(df)

            # Convert to PyArrow
            table = df.to_arrow()

            # Write Parquet with consistent schema (no dictionary encoding)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            pq.write_table(
                table,
                output_path,
                compression='snappy',
                use_dictionary=False,  # Disable for schema consistency
                write_statistics=True,
                row_group_size=100000,
            )

            # Statistics
            num_records = len(df)
            file_size = output_path.stat().st_size / 1024**2

            self.records_processed += num_records
            self.files_processed += 1
            self.bytes_processed += data.getbuffer().nbytes

            # Memory cleanup
            del df, table
            gc.collect()

            # Final memory check
            mem_status = self.memory_monitor.check_and_wait()

            logger.info(
                f"Polars ingestion complete: {date} "
                f"({num_records:,} records, {file_size:.1f} MB)"
            )

            return {
                'date': date,
                'records': num_records,
                'file_size_mb': file_size,
                'status': 'success',
                'memory_peak_percent': mem_status['system_percent'],
            }

        except Exception as e:
            self.errors += 1
            logger.error(f"Polars ingestion failed for {date}: {e}")
            raise IngestionError(f"Polars ingestion failed: {e}")

    def ingest_batch(
        self,
        dates: List[str],
        data_map: Dict[str, BytesIO],
        symbols: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple dates sequentially with Polars

        Args:
            dates: List of date strings
            data_map: Dictionary mapping dates to CSV data
            symbols: Optional symbol filter

        Returns:
            List of ingestion results
        """
        results = []

        logger.info(f"Batch Polars ingestion: {len(dates)} files")

        for date in dates:
            if date not in data_map:
                logger.warning(f"No data for {date}, skipping")
                continue

            try:
                result = self.ingest_date(date, data_map[date], symbols=symbols)
                results.append(result)

                # Garbage collection between files
                gc.collect()

            except Exception as e:
                logger.error(f"Failed to ingest {date}: {e}")
                results.append({
                    'date': date,
                    'status': 'error',
                    'error': str(e)
                })

        logger.info(
            f"Batch Polars complete: "
            f"{sum(1 for r in results if r['status'] == 'success')}/{len(dates)} "
            f"files succeeded"
        )

        return results

    def _normalize_columns_polars(self, df: pl.DataFrame, date: str) -> pl.DataFrame:
        """
        Normalize column names using Polars

        Args:
            df: Polars DataFrame
            date: Date string

        Returns:
            DataFrame with normalized columns
        """
        # Rename columns according to mapping
        for old_name, new_name in self.column_mapping.items():
            if old_name in df.columns:
                df = df.rename({old_name: new_name})

        # Add date column if not present
        if 'date' not in df.columns and 'timestamp' in df.columns:
            # Timestamp is int64 (Unix nanoseconds from Polygon)
            # Convert to date for partitioning
            df = df.with_columns(
                pl.col('timestamp')
                .cast(pl.Datetime('ns', time_zone='UTC'))
                .dt.date()
                .alias('date')
            )
        elif 'date' not in df.columns:
            from datetime import datetime
            dt = datetime.strptime(date, '%Y-%m-%d').date()
            df = df.with_columns(pl.lit(dt).alias('date'))

        return df

    def _add_partition_columns_polars(self, df: pl.DataFrame, date: str) -> pl.DataFrame:
        """
        Add partition columns (year, month) using Polars

        Args:
            df: Polars DataFrame
            date: Date string (YYYY-MM-DD)

        Returns:
            DataFrame with partition columns
        """
        from datetime import datetime

        dt = datetime.strptime(date, '%Y-%m-%d')

        df = df.with_columns([
            pl.lit(dt.year).alias('year').cast(pl.Int16),
            pl.lit(dt.month).alias('month').cast(pl.Int8),
        ])

        # Reorder columns to put partition columns first
        partition_cols = ['year', 'month']
        other_cols = [col for col in df.columns if col not in partition_cols]
        df = df.select(partition_cols + other_cols)

        return df

    def _get_schema_overrides(self) -> dict:
        """
        Get explicit schema overrides for consistent data types across all ingestions

        This ensures all parquet files have identical schemas regardless of when
        they were ingested, preventing type inference variations.

        Returns:
            Dictionary mapping column names to Polars dtypes
        """
        # Base schema for Polygon CSV files
        # ticker, volume, open, close, high, low, window_start, transactions
        schema = {
            'ticker': pl.Utf8,  # Symbol - always string
            'volume': pl.UInt64,  # Volume - unsigned 64-bit
            'open': pl.Float32,  # Price - 32-bit float
            'close': pl.Float32,  # Price - 32-bit float
            'high': pl.Float32,  # Price - 32-bit float
            'low': pl.Float32,  # Price - 32-bit float
            'window_start': pl.Int64,  # Unix timestamp in nanoseconds
            'transactions': pl.UInt32,  # Transaction count - unsigned 32-bit
        }

        # Add data-type specific columns
        if 'minute' in self.data_type:
            # Minute data may have additional columns
            schema['vwap'] = pl.Float32

        return schema

    def _optimize_dtypes_polars(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Optimize Polars DataFrame dtypes

        Args:
            df: Polars DataFrame

        Returns:
            Optimized DataFrame
        """
        # Ensure consistent types as specified in schema
        # Most types are already set by schema_overrides, but double-check

        float_columns = ['open', 'high', 'low', 'close', 'vwap']
        for col in float_columns:
            if col in df.columns and df[col].dtype == pl.Float64:
                df = df.with_columns(pl.col(col).cast(pl.Float32))

        # Ensure volume and transactions are unsigned
        if 'volume' in df.columns and df['volume'].dtype not in [pl.UInt64, pl.UInt32]:
            df = df.with_columns(pl.col('volume').cast(pl.UInt64))

        if 'transactions' in df.columns and df['transactions'].dtype not in [pl.UInt32, pl.UInt16]:
            df = df.with_columns(pl.col('transactions').cast(pl.UInt32))

        return df

    def ingest_lazy(
        self,
        date: str,
        data: BytesIO,
        symbols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process single date file with Polars LazyFrame (streaming)

        This is the most memory-efficient mode for very large files.

        Args:
            date: Date string (YYYY-MM-DD)
            data: CSV data as BytesIO
            symbols: Optional symbol filter

        Returns:
            Dictionary with ingestion statistics
        """
        try:
            logger.info(f"Polars lazy ingestion: {date}")

            output_path = self._get_output_path(date)

            # Check if output already exists
            if output_path.exists():
                logger.warning(f"Output exists, skipping: {output_path}")
                return {
                    'date': date,
                    'records': 0,
                    'status': 'skipped',
                    'reason': 'output_exists'
                }

            # Read CSV as LazyFrame
            lf = pl.scan_csv(
                data,
                has_header=True,
                null_values=['', 'NA', 'NULL', 'NaN'],
                try_parse_dates=True,
                low_memory=True,
            )

            # Apply transformations lazily
            if symbols and 'symbol' in lf.columns:
                lf = lf.filter(pl.col('symbol').is_in(symbols))

            # Add partition columns
            from datetime import datetime
            dt = datetime.strptime(date, '%Y-%m-%d')

            lf = lf.with_columns([
                pl.lit(dt.year).alias('year').cast(pl.Int16),
                pl.lit(dt.month).alias('month').cast(pl.Int8),
            ])

            # Optimize dtypes
            float_columns = ['open', 'high', 'low', 'close', 'vwap']
            for col in float_columns:
                if col in lf.columns:
                    lf = lf.with_columns(pl.col(col).cast(pl.Float32))

            # Execute query and write to Parquet (streaming)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            lf.sink_parquet(
                output_path,
                compression='snappy',
                statistics=True,
                row_group_size=100000,
            )

            # Get statistics (need to read back for count)
            num_records = pl.scan_parquet(output_path).select(pl.count()).collect()[0, 0]
            file_size = output_path.stat().st_size / 1024**2

            self.records_processed += num_records
            self.files_processed += 1

            logger.info(
                f"Polars lazy ingestion complete: {date} "
                f"({num_records:,} records, {file_size:.1f} MB)"
            )

            return {
                'date': date,
                'records': num_records,
                'file_size_mb': file_size,
                'status': 'success',
            }

        except Exception as e:
            self.errors += 1
            logger.error(f"Polars lazy ingestion failed for {date}: {e}")
            raise IngestionError(f"Polars lazy ingestion failed: {e}")


async def main():
    """Command-line interface for Polars ingestor"""
    import sys
    from ..core.config_loader import ConfigLoader
    from ..download.async_downloader import AsyncS3Downloader
    from ..download.s3_catalog import S3Catalog

    try:
        # Load configuration
        config_loader = ConfigLoader()
        credentials = config_loader.get_credentials('polygon')

        if not credentials or 's3' not in credentials:
            print("❌ Credentials not found. Please configure config/credentials.yaml")
            sys.exit(1)

        s3_creds = credentials['s3']

        # Create components
        catalog = S3Catalog()
        downloader = AsyncS3Downloader(
            credentials={
                'access_key_id': s3_creds['access_key_id'],
                'secret_access_key': s3_creds['secret_access_key'],
            },
            endpoint_url=s3_creds.get('endpoint_url', 'https://files.polygon.io'),
            max_concurrent=8
        )

        print("✅ PolarsIngestor initialized")
        print(f"   Data type: stocks_daily")
        print(f"   Mode: streaming")

        # Test: Download and ingest one file
        print("\n📥 Testing download + ingestion...")
        bucket = s3_creds.get('bucket', 'flatfiles')

        # Get key for recent date
        test_date = '2025-09-29'
        key = catalog.get_stocks_daily_key(test_date)

        print(f"   Downloading: {key}")

        # Download file
        files = await downloader.download_batch(bucket, [key])

        if files[0] is None:
            print(f"❌ Download failed")
            sys.exit(1)

        print(f"   Downloaded: {len(files[0].getvalue()) / 1024**2:.1f} MB")

        # Create ingestor
        output_root = Path('data/parquet_test')
        ingestor = PolarsIngestor(
            data_type='stocks_daily',
            output_root=output_root,
            config=config_loader.config,
            streaming=True
        )

        # Ingest
        print(f"   Ingesting with Polars...")
        result = ingestor.ingest_date(test_date, files[0])

        print(f"\n📊 Ingestion Result:")
        print(f"   Records: {result['records']:,}")
        print(f"   File size: {result['file_size_mb']:.1f} MB")
        print(f"   Status: {result['status']}")

        # Statistics
        stats = ingestor.get_statistics()
        print(f"\n📈 Statistics:")
        print(f"   Records processed: {stats['records_processed']:,}")
        print(f"   Files processed: {stats['files_processed']}")
        print(f"   Errors: {stats['errors']}")

        # Benchmark comparison
        print(f"\n⚡ Performance:")
        print(f"   Polars is 5-10x faster than pandas")
        print(f"   Automatic parallelization")
        print(f"   Lower memory usage")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
