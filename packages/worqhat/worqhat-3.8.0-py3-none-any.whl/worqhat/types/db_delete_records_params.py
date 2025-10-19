# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DBDeleteRecordsParams"]


class DBDeleteRecordsParams(TypedDict, total=False):
    table: Required[str]
    """Table name to delete from"""

    where: Required[Dict[str, object]]
    """Where conditions"""

    environment: Literal["development", "staging", "production"]
    """Environment to delete from (development, staging, production)"""
