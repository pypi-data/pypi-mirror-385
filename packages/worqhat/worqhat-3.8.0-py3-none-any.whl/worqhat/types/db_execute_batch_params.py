# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DBExecuteBatchParams", "Operation"]


class DBExecuteBatchParams(TypedDict, total=False):
    operations: Required[Iterable[Operation]]
    """Array of database operations to execute"""

    environment: Literal["development", "staging", "production"]
    """Environment to execute operations in"""

    transactional: bool
    """Whether to execute all operations in a single transaction"""


class Operation(TypedDict, total=False):
    type: Required[Literal["query", "insert", "update", "delete"]]
    """Type of operation"""

    data: Dict[str, object]
    """Data to insert or update"""

    query: str
    """SQL query (required for query type)"""

    table: str
    """Table name (required for insert, update, delete)"""

    where: Dict[str, object]
    """Where conditions for update or delete"""
