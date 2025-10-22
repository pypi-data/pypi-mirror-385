# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["OutreachUpdateParams"]


class OutreachUpdateParams(TypedDict, total=False):
    outbound_phone_number: Required[Annotated[str, PropertyInfo(alias="outboundPhoneNumber")]]
