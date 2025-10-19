# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["DBProcessNlQueryResponse"]


class DBProcessNlQueryResponse(BaseModel):
    data: Optional[List[Dict[str, object]]] = None

    message: Optional[str] = None

    sql: Optional[str] = None
    """The generated SQL query"""

    success: Optional[bool] = None
