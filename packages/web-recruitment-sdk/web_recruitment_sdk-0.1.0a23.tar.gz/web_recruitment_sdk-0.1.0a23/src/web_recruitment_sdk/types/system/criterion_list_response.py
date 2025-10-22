# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from ..criteria_type import CriteriaType
from ..custom_searches.criteria_status import CriteriaStatus

__all__ = [
    "CriterionListResponse",
    "CriterionListResponseItem",
    "CriterionListResponseItemMatchingPayload",
    "CriterionListResponseItemMatchingPayloadRoutingMetadata",
    "CriterionListResponseItemMatchingPayloadRoutingMetadataHandlerPayload",
]


class CriterionListResponseItemMatchingPayloadRoutingMetadataHandlerPayload(BaseModel):
    payload: object

    payload_model: str = FieldInfo(alias="payloadModel")
    """The string representation of the pydantic model of the payload."""


class CriterionListResponseItemMatchingPayloadRoutingMetadata(BaseModel):
    agent_signature: Literal["SEMANTIC_RETRIEVAL", "QUANTITATIVE_LOGIC", "ADVANCED_LOGIC", "PROCEDURAL_INTENT"] = (
        FieldInfo(alias="agentSignature")
    )

    handler_payload: Optional[CriterionListResponseItemMatchingPayloadRoutingMetadataHandlerPayload] = FieldInfo(
        alias="handlerPayload", default=None
    )

    handler_signature: Optional[Literal["AGE_QUESTION", "SIMPLE_MEDICAL_HISTORY_QUESTION"]] = FieldInfo(
        alias="handlerSignature", default=None
    )


class CriterionListResponseItemMatchingPayload(BaseModel):
    data_type: List[Literal["LAB", "MEDICATION", "DIAGNOSIS", "PROCEDURE", "VITALS", "DEMOGRAPHICS", "ALLERGY"]] = (
        FieldInfo(alias="dataType")
    )

    routing_metadata: Optional[CriterionListResponseItemMatchingPayloadRoutingMetadata] = FieldInfo(
        alias="routingMetadata", default=None
    )

    schema_version: Optional[Literal["v1"]] = FieldInfo(alias="schemaVersion", default=None)


class CriterionListResponseItem(BaseModel):
    parent_type: Literal["PROTOCOL", "CUSTOM_SEARCH"] = FieldInfo(alias="parentType")

    summary: str

    type: CriteriaType

    id: Optional[int] = None

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    created_by: Optional[int] = FieldInfo(alias="createdBy", default=None)

    created_from_id: Optional[int] = FieldInfo(alias="createdFromId", default=None)

    criteria_protocol_metadata_id: Optional[int] = FieldInfo(alias="criteriaProtocolMetadataId", default=None)

    custom_search_id: Optional[int] = FieldInfo(alias="customSearchId", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    description: Optional[str] = None

    matching_payload: Optional[CriterionListResponseItemMatchingPayload] = FieldInfo(
        alias="matchingPayload", default=None
    )

    protocol_id: Optional[int] = FieldInfo(alias="protocolId", default=None)

    status: Optional[CriteriaStatus] = None

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

    user_raw_input: Optional[str] = FieldInfo(alias="userRawInput", default=None)


CriterionListResponse: TypeAlias = List[CriterionListResponseItem]
