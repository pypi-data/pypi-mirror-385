# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ClientListResponse", "ClientListResponseItem"]


class ClientListResponseItem(BaseModel):
    id: int

    external_client_id: str = FieldInfo(alias="externalClientId")

    name: str


ClientListResponse: TypeAlias = List[ClientListResponseItem]
