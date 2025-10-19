# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..._types import FileTypes

__all__ = ["StorageUploadFileParams"]


class StorageUploadFileParams(TypedDict, total=False):
    file: Required[FileTypes]
    """File to upload (max 50MB)"""

    path: str
    """Optional custom path within organization storage"""
