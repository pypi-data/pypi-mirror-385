# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Role"]


class Role(BaseModel):
    id: str

    is_primary: bool = FieldInfo(alias="isPrimary")

    name: str

    description: Optional[str] = None
