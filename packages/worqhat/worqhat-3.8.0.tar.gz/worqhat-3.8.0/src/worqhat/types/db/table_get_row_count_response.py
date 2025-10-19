# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["TableGetRowCountResponse"]


class TableGetRowCountResponse(BaseModel):
    count: Optional[int] = None

    success: Optional[bool] = None

    table: Optional[str] = None
