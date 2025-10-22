# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from ..criteria_type import CriteriaType
from .criteria_status import CriteriaStatus

__all__ = [
    "CriteriaRead",
    "MatchingPayload",
    "MatchingPayloadRoutingMetadata",
    "MatchingPayloadRoutingMetadataHandlerPayload",
]


class MatchingPayloadRoutingMetadataHandlerPayload(BaseModel):
    payload: object

    payload_model: str = FieldInfo(alias="payloadModel")
    """The string representation of the pydantic model of the payload."""


class MatchingPayloadRoutingMetadata(BaseModel):
    agent_signature: Literal["SEMANTIC_RETRIEVAL", "QUANTITATIVE_LOGIC", "ADVANCED_LOGIC", "PROCEDURAL_INTENT"] = (
        FieldInfo(alias="agentSignature")
    )

    handler_payload: Optional[MatchingPayloadRoutingMetadataHandlerPayload] = FieldInfo(
        alias="handlerPayload", default=None
    )

    handler_signature: Optional[Literal["AGE_QUESTION", "SIMPLE_MEDICAL_HISTORY_QUESTION"]] = FieldInfo(
        alias="handlerSignature", default=None
    )


class MatchingPayload(BaseModel):
    data_type: List[Literal["LAB", "MEDICATION", "DIAGNOSIS", "PROCEDURE", "VITALS", "DEMOGRAPHICS", "ALLERGY"]] = (
        FieldInfo(alias="dataType")
    )

    routing_metadata: Optional[MatchingPayloadRoutingMetadata] = FieldInfo(alias="routingMetadata", default=None)

    schema_version: Optional[Literal["v1"]] = FieldInfo(alias="schemaVersion", default=None)


class CriteriaRead(BaseModel):
    id: int

    summary: str

    type: CriteriaType

    criteria_protocol_metadata_id: Optional[int] = FieldInfo(alias="criteriaProtocolMetadataId", default=None)

    custom_search_id: Optional[int] = FieldInfo(alias="customSearchId", default=None)

    description: Optional[str] = None

    is_pending_matching: Optional[bool] = FieldInfo(alias="isPendingMatching", default=None)

    matching_payload: Optional[MatchingPayload] = FieldInfo(alias="matchingPayload", default=None)

    protocol_id: Optional[int] = FieldInfo(alias="protocolId", default=None)

    status: Optional[CriteriaStatus] = None

    user_raw_input: Optional[str] = FieldInfo(alias="userRawInput", default=None)
