import os
import uuid
import polars as pl
import pandas as pd
from typing import Literal, Union
from .query_manager import QueryManager


# Get configuration from environment variables (required)
_DEFAULT_BUCKET = os.getenv("HYPER_ATHENA_BUCKET")
_DEFAULT_PREFIX = os.getenv("HYPER_ATHENA_PREFIX", "query_results/")

if _DEFAULT_BUCKET is None:
    raise ValueError(
        "HYPER_ATHENA_BUCKET environment variable is required. "
        "Set it before importing hyper_python_utils:\n"
        "  os.environ['HYPER_ATHENA_BUCKET'] = 'your-bucket-name'\n"
        "Or use a .env file with the variable defined."
    )

# Global QueryManager instance
_query_manager = QueryManager(
    bucket=_DEFAULT_BUCKET,
    result_prefix=_DEFAULT_PREFIX,
    auto_cleanup=True
)


def query(database: str, query: str, option: Literal["pandas", "polars"] = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Execute a simple Athena query and return results as a DataFrame.

    Args:
        database: Athena database name
        query: SQL query string (e.g., "SELECT * FROM my_table LIMIT 100")
        option: Output format - "pandas" (default) or "polars"

    Returns:
        pd.DataFrame or pl.DataFrame: Query results. Returns empty DataFrame if no results.

    Example:
        >>> import hyper_python_utils as hp
        >>> # Returns pandas DataFrame (default)
        >>> df = hp.query(database="my_database", query="SELECT * FROM my_table LIMIT 100")
        >>> # Returns polars DataFrame
        >>> df = hp.query(database="my_database", query="SELECT * FROM my_table LIMIT 100", option="polars")
    """
    return _query_manager.query(query=query, database=database, output_format=option)


def query_unload(database: str, query: str, key: str = None) -> str:
    """
    Execute an Athena UNLOAD query and return the S3 directory path where files are stored.

    This is the first step in a three-step process:
    1. query_unload() - Execute query and get S3 directory path
    2. load_unload_data() - Load data from the S3 directory
    3. cleanup_unload_data() - (Optional) Delete files from S3

    Args:
        database: Athena database name
        query: SQL SELECT query (only the inner SELECT part, without UNLOAD TO syntax)
               Example: "SELECT * FROM my_table WHERE date > '2024-01-01'"
        key: S3 key prefix (default: uses HYPER_UNLOAD_PREFIX env var or "query_results_for_unload")

    Returns:
        str: S3 directory path where the unloaded files are stored
             Format: s3://{bucket}/{key}/{uuid}/

    Example:
        >>> import hyper_python_utils as hp
        >>> # Step 1: Execute UNLOAD query and get S3 path
        >>> s3_path = hp.query_unload(
        ...     database="my_database",
        ...     query="SELECT * FROM large_table WHERE date > '2024-01-01'"
        ... )
        >>>
        >>> # Step 2: Load data from S3
        >>> df = hp.load_unload_data(s3_path, option="pandas")
        >>>
        >>> # Step 3: Clean up files (optional)
        >>> hp.cleanup_unload_data(s3_path)

    Note:
        - The function automatically wraps your query with UNLOAD syntax
        - Uses Parquet format with GZIP compression (best performance and compression ratio)
        - Files are NOT automatically deleted - use cleanup_unload_data() to remove them
        - Configure bucket via HYPER_ATHENA_BUCKET environment variable
    """
    if key is None:
        key = os.getenv("HYPER_UNLOAD_PREFIX", "query_results_for_unload")

    unique_dir = str(uuid.uuid4())
    unload_prefix = f"{key}/{unique_dir}/"
    s3_location = f"s3://{_DEFAULT_BUCKET}/{unload_prefix}"

    unload_query = f"""
    UNLOAD ({query})
    TO '{s3_location}'
    WITH (format='PARQUET', compression='GZIP')
    """

    query_id = _query_manager.execute(query=unload_query, database=database)
    _query_manager.wait_for_completion(query_id)

    print(f"[UNLOAD] Files created at: {s3_location}")
    return s3_location


def load_unload_data(s3_directory: str, option: Literal["pandas", "polars"] = "pandas") -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Load data from an S3 directory created by query_unload().

    Args:
        s3_directory: S3 directory path returned by query_unload()
        option: Output format - "pandas" (default) or "polars"

    Returns:
        pd.DataFrame or pl.DataFrame: Data loaded from the Parquet files

    Example:
        >>> import hyper_python_utils as hp
        >>> s3_path = hp.query_unload(database="my_db", query="SELECT * FROM table")
        >>> df = hp.load_unload_data(s3_path, option="pandas")

    Note:
        - Reads all .parquet and .parquet.gz files from the specified directory
        - Returns empty DataFrame if no files are found
    """
    unloaded_files = _query_manager.unload(unload_location=s3_directory)

    if not unloaded_files:
        print("[UNLOAD] No files found (empty result set)")
        return pd.DataFrame() if option == "pandas" else pl.DataFrame()

    print(f"[UNLOAD] Loading {len(unloaded_files)} file(s)")

    try:
        df_polars = pl.read_parquet(unloaded_files)
        print(f"[UNLOAD] Loaded {df_polars.height:,} rows")

        return df_polars.to_pandas() if option == "pandas" else df_polars
    except Exception as e:
        raise Exception(f"Failed to read Parquet files: {str(e)}")


def cleanup_unload_data(s3_directory: str) -> None:
    """
    Delete all files in the S3 directory created by query_unload().

    Args:
        s3_directory: S3 directory path returned by query_unload()

    Example:
        >>> import hyper_python_utils as hp
        >>> s3_path = hp.query_unload(database="my_db", query="SELECT * FROM table")
        >>> df = hp.load_unload_data(s3_path)
        >>> hp.cleanup_unload_data(s3_path)

    Note:
        - This operation is irreversible
        - All files under the specified directory will be permanently deleted
    """
    _query_manager.delete_query_results_by_prefix(s3_directory)
    print(f"[UNLOAD] Cleaned up: {s3_directory}")
