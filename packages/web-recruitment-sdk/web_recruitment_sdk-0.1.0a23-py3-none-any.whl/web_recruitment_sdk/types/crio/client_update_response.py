# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ClientUpdateResponse"]


class ClientUpdateResponse(BaseModel):
    id: int

    external_client_id: str = FieldInfo(alias="externalClientId")

    name: str
