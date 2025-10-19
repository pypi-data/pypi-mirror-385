# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TableRetrieveSchemaResponse", "Column"]


class Column(BaseModel):
    default: Optional[str] = None

    is_primary_key: Optional[bool] = FieldInfo(alias="isPrimaryKey", default=None)

    name: Optional[str] = None

    nullable: Optional[bool] = None

    type: Optional[str] = None


class TableRetrieveSchemaResponse(BaseModel):
    columns: Optional[List[Column]] = None

    success: Optional[bool] = None

    table: Optional[str] = None
