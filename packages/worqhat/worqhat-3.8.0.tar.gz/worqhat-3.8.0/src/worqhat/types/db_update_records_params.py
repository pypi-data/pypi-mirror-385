# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DBUpdateRecordsParams"]


class DBUpdateRecordsParams(TypedDict, total=False):
    data: Required[Dict[str, object]]
    """Data to update"""

    table: Required[str]
    """Table name to update"""

    where: Required[Dict[str, object]]
    """Where conditions"""

    environment: Literal["development", "staging", "production"]
    """Environment to update in (development, staging, production)"""
