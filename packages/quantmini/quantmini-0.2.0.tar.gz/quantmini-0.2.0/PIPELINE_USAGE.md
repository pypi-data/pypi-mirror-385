# Unified Pipeline Usage

## Single Command for Complete Data Processing

Instead of running three separate commands (download, ingest, enrich), you can use the unified **`quantmini pipeline run`** command:

### Full Pipeline (Download → Parquet → Enrich)

```bash
# Process stocks daily data for a date range
uv run quantmini pipeline run \
  --data-type stocks_daily \
  --start-date 2025-10-07 \
  --end-date 2025-10-10 \
  --skip-convert

# Process options minute data
uv run quantmini pipeline run \
  --data-type options_minute \
  --start-date 2025-10-07 \
  --end-date 2025-10-07 \
  --skip-convert
```

### Skip Certain Steps

```bash
# Skip download/ingest (only enrich existing data)
uv run quantmini pipeline run \
  --data-type stocks_daily \
  --start-date 2024-01-01 \
  --end-date 2024-01-10 \
  --skip-ingest \
  --skip-convert

# Skip enrichment (only download and convert to Parquet)
uv run quantmini pipeline run \
  --data-type options_daily \
  --start-date 2025-01-01 \
  --end-date 2025-01-31 \
  --skip-enrich \
  --skip-convert
```

## Pipeline Stages (Medallion Architecture)

The pipeline follows the **Medallion Architecture** pattern with three data quality layers:

1. **Ingest** (Landing → Bronze Layer)
   - Downloads from Polygon.io S3 to landing layer
   - Converts to validated Parquet format (bronze layer)
   - Validates schema and data types
   - **Output**: `$DATA_ROOT/bronze/{data_type}/`

2. **Enrich** (Bronze → Silver Layer)
   - Reads validated Parquet from bronze layer
   - Computes technical indicators
   - Adds alpha factors using DuckDB
   - **Output**: `$DATA_ROOT/silver/{data_type}/`

3. **Convert** (Silver → Gold Layer)
   - Converts enriched silver data to Qlib binary format
   - Creates ML-ready datasets in gold layer
   - **Output**: `$DATA_ROOT/gold/qlib/{data_type}/`

## Medallion Architecture Layers

- **Landing**: Raw CSV.GZ files organized by source (`landing/polygon-s3/`)
- **Bronze**: Validated Parquet files with schema enforcement (`bronze/`)
- **Silver**: Feature-enriched Parquet with calculated indicators (`silver/`)
- **Gold**: ML-ready binary format optimized for backtesting (`gold/qlib/`)

**Data Access Limitations:**
- Stocks: 5-year access (2020-10-18 to present)
- Options: 2-year access (2023-10-18 to present)

(Where `$DATA_ROOT` is configured via environment variable or `config/pipeline_config.yaml`)

## Benefits

✅ Single command for entire workflow
✅ Automatic incremental processing (skips already processed dates)
✅ Trading day filtering (skips weekends/holidays automatically)
✅ Memory-optimized streaming for large datasets
✅ Atomic operations with proper error handling

## Daily Update Example

```bash
# Update all data types for the latest trading day
TODAY=$(date +%Y-%m-%d)

for dtype in stocks_daily options_daily stocks_minute options_minute; do
  uv run quantmini pipeline run \
    --data-type $dtype \
    --start-date $TODAY \
    --end-date $TODAY \
    --skip-convert
done
```

## Historical Backfill Example

```bash
# Backfill missing data (automatically skips existing dates with incremental mode)
uv run quantmini pipeline run \
  --data-type stocks_daily \
  --start-date 2024-01-01 \
  --end-date 2025-10-03 \
  --skip-convert
```

The pipeline automatically:
- Filters to trading days only
- Skips weekends and market holidays  
- Uses incremental mode (skips already processed dates)
- Handles errors gracefully with detailed logging
