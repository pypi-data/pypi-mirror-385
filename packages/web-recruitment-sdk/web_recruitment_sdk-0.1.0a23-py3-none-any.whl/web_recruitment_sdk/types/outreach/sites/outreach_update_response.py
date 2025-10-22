# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["OutreachUpdateResponse"]


class OutreachUpdateResponse(BaseModel):
    id: int

    outbound_phone_number: str = FieldInfo(alias="outboundPhoneNumber")

    site_id: int = FieldInfo(alias="siteId")
