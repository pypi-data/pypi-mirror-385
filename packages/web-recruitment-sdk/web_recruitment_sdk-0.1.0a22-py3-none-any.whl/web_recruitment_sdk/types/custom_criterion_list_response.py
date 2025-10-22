# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .criteria_type import CriteriaType

__all__ = [
    "CustomCriterionListResponse",
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


class CustomCriterionListResponse(BaseModel):
    description: str

    summary: str

    type: CriteriaType

    matching_payload: Optional[MatchingPayload] = FieldInfo(alias="matchingPayload", default=None)
