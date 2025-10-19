# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["StorageRetrieveFileByIDResponse", "File"]


class File(BaseModel):
    id: Optional[str] = None

    content_type: Optional[str] = FieldInfo(alias="contentType", default=None)

    filename: Optional[str] = None

    path: Optional[str] = None

    size: Optional[int] = None

    uploaded_at: Optional[datetime] = FieldInfo(alias="uploadedAt", default=None)

    url: Optional[str] = None
    """Signed URL for downloading the file (expires in 1 hour)"""


class StorageRetrieveFileByIDResponse(BaseModel):
    file: Optional[File] = None

    success: Optional[bool] = None
