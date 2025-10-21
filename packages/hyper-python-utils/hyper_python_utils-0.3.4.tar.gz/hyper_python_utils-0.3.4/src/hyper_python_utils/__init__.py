"""
Hyper Python Utils - AWS S3 and Athena utilities for data processing with Polars
"""

from .file_handler import FileHandler
from .query_manager import QueryManager, EmptyResultError, AthenaQueryError
from .wrapper import query, query_unload, load_unload_data, cleanup_unload_data

__version__ = "0.3.4"
__all__ = [
    "FileHandler",
    "QueryManager",
    "EmptyResultError",
    "AthenaQueryError",
    "query",
    "query_unload",
    "load_unload_data",
    "cleanup_unload_data"
]