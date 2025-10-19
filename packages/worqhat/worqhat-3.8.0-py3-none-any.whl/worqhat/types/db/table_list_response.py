# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TableListResponse", "Table"]


class Table(BaseModel):
    name: Optional[str] = None

    schema_: Optional[str] = FieldInfo(alias="schema", default=None)

    type: Optional[str] = None


class TableListResponse(BaseModel):
    count: Optional[int] = None
    """Total number of tables"""

    success: Optional[bool] = None

    tables: Optional[List[Table]] = None
