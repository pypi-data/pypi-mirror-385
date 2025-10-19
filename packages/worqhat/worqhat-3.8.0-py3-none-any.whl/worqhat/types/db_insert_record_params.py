# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DBInsertRecordParams"]


class DBInsertRecordParams(TypedDict, total=False):
    data: Required[Dict[str, object]]
    """Data to insert"""

    table: Required[str]
    """Table name to insert into"""

    environment: Literal["development", "staging", "production"]
    """Environment to insert into (development, staging, production)"""
