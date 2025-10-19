# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["StorageUploadFileResponse", "File"]


class File(BaseModel):
    id: Optional[str] = None

    content_type: Optional[str] = FieldInfo(alias="contentType", default=None)

    filename: Optional[str] = None

    path: Optional[str] = None

    size: Optional[int] = None
    """File size in bytes"""

    uploaded_at: Optional[datetime] = FieldInfo(alias="uploadedAt", default=None)

    url: Optional[str] = None


class StorageUploadFileResponse(BaseModel):
    file: Optional[File] = None

    success: Optional[bool] = None
