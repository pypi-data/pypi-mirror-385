"""
datacatalog
-----------
Data Catalog library for managing physical data sources.

This library provides Dataset, DatasetTransaction, and DatasetBranch models
inspired by Palantir Foundry, enabling versioned, branch-based data management.
"""

from datacatalog.models import (
    ColumnSchema,
    Dataset,
    DatasetBranch,
    DatasetTransaction,
    TransactionType,
)

__all__ = ["Dataset", "DatasetTransaction", "DatasetBranch", "TransactionType", "ColumnSchema"]
