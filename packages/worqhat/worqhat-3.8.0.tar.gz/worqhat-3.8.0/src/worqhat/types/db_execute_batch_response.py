# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DBExecuteBatchResponse", "Result"]


class Result(BaseModel):
    data: Optional[Dict[str, object]] = None

    operation: Optional[str] = None

    success: Optional[bool] = None


class DBExecuteBatchResponse(BaseModel):
    executed_count: Optional[int] = FieldInfo(alias="executedCount", default=None)
    """Number of operations executed"""

    results: Optional[List[Result]] = None
    """Results from each operation"""

    success: Optional[bool] = None
