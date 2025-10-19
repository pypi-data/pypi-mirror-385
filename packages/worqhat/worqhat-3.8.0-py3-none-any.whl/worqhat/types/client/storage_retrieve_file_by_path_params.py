# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["StorageRetrieveFileByPathParams"]


class StorageRetrieveFileByPathParams(TypedDict, total=False):
    filepath: Required[str]
    """Path to the file within organization storage"""
