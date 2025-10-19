# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["DBDeleteRecordsResponse"]


class DBDeleteRecordsResponse(BaseModel):
    count: Optional[int] = None
    """Number of records deleted"""

    data: Optional[List[Dict[str, object]]] = None

    message: Optional[str] = None

    success: Optional[bool] = None
