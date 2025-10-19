# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["TableGetRowCountParams"]


class TableGetRowCountParams(TypedDict, total=False):
    environment: Literal["development", "staging", "production"]
    """Environment to query"""
