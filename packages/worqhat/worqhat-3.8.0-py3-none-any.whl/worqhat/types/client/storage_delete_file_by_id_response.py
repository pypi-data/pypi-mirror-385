# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["StorageDeleteFileByIDResponse"]


class StorageDeleteFileByIDResponse(BaseModel):
    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    message: Optional[str] = None

    success: Optional[bool] = None
