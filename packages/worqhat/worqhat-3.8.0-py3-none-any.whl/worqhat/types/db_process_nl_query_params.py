# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DBProcessNlQueryParams"]


class DBProcessNlQueryParams(TypedDict, total=False):
    question: Required[str]
    """Natural language question"""

    table: Required[str]
    """Table name to query"""

    context: Dict[str, object]
    """Optional context for the query"""

    environment: Literal["development", "staging", "production"]
    """Environment to query (development, staging, production)"""
