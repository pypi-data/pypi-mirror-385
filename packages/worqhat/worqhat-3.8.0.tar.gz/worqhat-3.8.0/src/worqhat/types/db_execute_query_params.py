# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DBExecuteQueryParams"]


class DBExecuteQueryParams(TypedDict, total=False):
    query: Required[str]
    """SQL query to execute"""

    environment: Literal["development", "staging", "production"]
    """Environment to query (development, staging, production)"""

    params: Dict[str, object]
    """Optional query parameters"""
