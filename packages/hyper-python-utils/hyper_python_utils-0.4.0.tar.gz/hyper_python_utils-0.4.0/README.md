# Hyper Python Utils

![Version](https://img.shields.io/badge/version-0.4.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![PyPI](https://img.shields.io/pypi/v/hyper-python-utils.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

AWS S3 and Athena utilities for data processing with Pandas and Polars.

## Installation

```bash
pip install hyper-python-utils
```

## Features

- **Simple Query Functions (New in v0.2.0)**: Easy-to-use wrapper functions
  - `query()`: Execute Athena queries with minimal setup
  - `query_unload()`: Execute UNLOAD query and return S3 path
  - `load_unload_data()`: Load DataFrame from UNLOAD results
  - `cleanup_unload_data()`: Clean up S3 files (optional)
  - Support for both Pandas and Polars DataFrames
  - Optimized performance with Parquet + GZIP

- **FileHandler**: S3 file operations with Polars DataFrames
  - Upload/download CSV and Parquet files
  - Parallel loading of multiple files
  - Partitioned uploads by range or date
  - Support for compressed formats

- **QueryManager**: Advanced Athena query execution and management
  - Execute queries with result monitoring
  - Clean up query result files
  - Error handling and timeouts
  - Full control over query execution

## Quick Start

### Simple Query Functions (Recommended for Most Use Cases)

The easiest way to query Athena data:

```python
import hyper_python_utils as hp

# Execute a simple query (returns pandas DataFrame by default)
df = hp.query(
    database="my_database",
    query="SELECT * FROM my_table LIMIT 100"
)
print(df)
print(type(df))  # <class 'pandas.core.frame.DataFrame'>

# Get results as polars DataFrame
df = hp.query(
    database="my_database",
    query="SELECT * FROM my_table LIMIT 100",
    option="polars"
)
print(type(df))  # <class 'polars.dataframe.frame.DataFrame'>

# For large datasets, use UNLOAD (3-step process for better control)
# Step 1: Execute query and get S3 path
s3_path = hp.query_unload(
    database="my_database",
    query="SELECT * FROM large_table WHERE date > '2024-01-01'"
)
# Step 2: Load data from S3
df = hp.load_unload_data(s3_path, option="pandas")  # or option="polars"
# Step 3: Clean up (optional)
hp.cleanup_unload_data(s3_path)

# Queries with semicolons are automatically handled
df = hp.query(database="my_database", query="SELECT * FROM table;")  # Works fine!
```

**Key Features:**
- Pre-configured with optimal settings (bucket: `athena-query-results-for-hyper`)
- Automatic cleanup of temporary files (for `query()` only)
- No exceptions on empty results (returns empty DataFrame)
- Query execution time displayed in logs
- `query_unload()` uses Parquet + GZIP for 4x performance boost
- Three-step UNLOAD process for better control: execute, load, cleanup

**When to use which?**
- `query()`: Normal queries, small to medium datasets (< 1M rows)
- `query_unload()` + `load_unload_data()`: Large datasets (> 1M rows), when performance matters

**UNLOAD Process:**
1. `query_unload()`: Execute query and get S3 directory path
2. `load_unload_data()`: Load DataFrame from S3 files
3. `cleanup_unload_data()`: (Optional) Delete files from S3

## Requirements

- Python >= 3.8
- boto3 >= 1.26.0
- polars >= 0.18.0
- pandas >= 1.5.0

## Configuration

### AWS Credentials

Make sure your AWS credentials are configured either through:
- AWS CLI (`aws configure`)
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- IAM roles (when running on EC2)

Required permissions:
- S3: `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, `s3:DeleteObject`
- Athena: `athena:StartQueryExecution`, `athena:GetQueryExecution`

### Required Environment Variables

**IMPORTANT:** You must set the `HYPER_ATHENA_BUCKET` environment variable before using this library.

```bash
# REQUIRED: Set your S3 bucket for Athena query results
export HYPER_ATHENA_BUCKET="your-athena-results-bucket"

# OPTIONAL: Set custom query result prefix (default: "query_results/")
export HYPER_ATHENA_PREFIX="my-custom-prefix/"

# OPTIONAL: Set custom UNLOAD prefix (default: "query_results_for_unload")
export HYPER_UNLOAD_PREFIX="my-unload-prefix"
```

**Python Example:**
```python
import os

# REQUIRED: Set bucket before importing the library
os.environ["HYPER_ATHENA_BUCKET"] = "my-company-athena-results"

# OPTIONAL: Customize prefixes
os.environ["HYPER_ATHENA_PREFIX"] = "analytics/queries/"
os.environ["HYPER_UNLOAD_PREFIX"] = "analytics/unload"

import hyper_python_utils as hp

# Now you can use the library
df = hp.query(database="my_db", query="SELECT * FROM table")
```

**Using .env file:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and set your bucket name
# HYPER_ATHENA_BUCKET=your-actual-bucket-name

# Then use python-dotenv to load it
```

```python
from dotenv import load_dotenv
load_dotenv()  # Load .env file

import hyper_python_utils as hp
df = hp.query(database="my_db", query="SELECT * FROM table")
```

## Changelog

### v0.3.2 (Latest)
- **Fixed**: Improved file filtering for UNLOAD to only include Parquet files (.parquet, .parquet.gz)
- **Improved**: Added debug logging to show which files are being read during UNLOAD

### v0.3.1
- **Fixed**: Removed automatic cleanup for UNLOAD files to prevent timing issues
- **Improved**: UNLOAD files now kept in S3 for reliable access

### v0.3.0
- **New**: Added `query()` and `query_unload()` wrapper functions for simplified usage
- **New**: Support for both Pandas and Polars DataFrames (Pandas is default)
- **Improved**: UNLOAD queries now use Parquet + GZIP (4x performance improvement)
- **Improved**: Empty query results return empty DataFrame instead of throwing exception
- **Improved**: Query execution time now displayed in logs
- **Improved**: Automatic removal of trailing semicolons in queries
- **Improved**: Silent cleanup (removed unnecessary log messages)

### v0.1.2
- Initial stable release
- FileHandler for S3 operations
- QueryManager for Athena queries

## License

MIT License