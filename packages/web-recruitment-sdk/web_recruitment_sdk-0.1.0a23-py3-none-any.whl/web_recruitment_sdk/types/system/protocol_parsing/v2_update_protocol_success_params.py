# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from ...custom_searches.criteria_create_param import CriteriaCreateParam

__all__ = [
    "V2UpdateProtocolSuccessParams",
    "CriteriaCreateWithProtocolMetadata",
    "CriteriaCreateWithProtocolMetadataProtocolMetadata",
]


class V2UpdateProtocolSuccessParams(TypedDict, total=False):
    path_tenant_db_name: Required[Annotated[str, PropertyInfo(alias="tenant_db_name")]]

    criteria_create_with_protocol_metadata: Required[
        Annotated[
            Iterable[CriteriaCreateWithProtocolMetadata], PropertyInfo(alias="criteriaCreateWithProtocolMetadata")
        ]
    ]

    external_protocol_id: Required[Annotated[str, PropertyInfo(alias="externalProtocolId")]]

    task_id: Required[Annotated[int, PropertyInfo(alias="taskId")]]
    """The ID of the task as it exists in the database"""

    task_name: Required[Annotated[str, PropertyInfo(alias="taskName")]]
    """The name of the task"""

    body_tenant_db_name: Required[Annotated[str, PropertyInfo(alias="tenantDbName")]]


class CriteriaCreateWithProtocolMetadataProtocolMetadata(TypedDict, total=False):
    original_text: Required[Annotated[str, PropertyInfo(alias="originalText")]]

    id: Optional[int]

    created_at: Annotated[Union[str, datetime], PropertyInfo(alias="createdAt", format="iso8601")]

    protocol_order_index: Annotated[Optional[int], PropertyInfo(alias="protocolOrderIndex")]

    updated_at: Annotated[Union[str, datetime], PropertyInfo(alias="updatedAt", format="iso8601")]


class CriteriaCreateWithProtocolMetadata(TypedDict, total=False):
    criteria_create: Required[Annotated[Iterable[CriteriaCreateParam], PropertyInfo(alias="criteriaCreate")]]

    protocol_metadata: Required[
        Annotated[CriteriaCreateWithProtocolMetadataProtocolMetadata, PropertyInfo(alias="protocolMetadata")]
    ]
