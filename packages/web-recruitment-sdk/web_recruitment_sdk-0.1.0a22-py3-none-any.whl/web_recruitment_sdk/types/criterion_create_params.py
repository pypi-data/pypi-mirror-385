# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .criteria_type import CriteriaType
from .custom_searches.criteria_status import CriteriaStatus

__all__ = [
    "CriterionCreateParams",
    "MatchingPayload",
    "MatchingPayloadRoutingMetadata",
    "MatchingPayloadRoutingMetadataHandlerPayload",
]


class CriterionCreateParams(TypedDict, total=False):
    summary: Required[str]

    type: Required[CriteriaType]

    criteria_protocol_metadata_id: Annotated[Optional[int], PropertyInfo(alias="criteriaProtocolMetadataId")]

    custom_search_id: Annotated[Optional[int], PropertyInfo(alias="customSearchId")]

    description: Optional[str]

    matching_payload: Annotated[Optional[MatchingPayload], PropertyInfo(alias="matchingPayload")]

    protocol_id: Annotated[Optional[int], PropertyInfo(alias="protocolId")]

    status: CriteriaStatus

    user_raw_input: Annotated[Optional[str], PropertyInfo(alias="userRawInput")]


class MatchingPayloadRoutingMetadataHandlerPayload(TypedDict, total=False):
    payload: Required[object]

    payload_model: Required[Annotated[str, PropertyInfo(alias="payloadModel")]]
    """The string representation of the pydantic model of the payload."""


class MatchingPayloadRoutingMetadata(TypedDict, total=False):
    agent_signature: Required[
        Annotated[
            Literal["SEMANTIC_RETRIEVAL", "QUANTITATIVE_LOGIC", "ADVANCED_LOGIC", "PROCEDURAL_INTENT"],
            PropertyInfo(alias="agentSignature"),
        ]
    ]

    handler_payload: Required[
        Annotated[Optional[MatchingPayloadRoutingMetadataHandlerPayload], PropertyInfo(alias="handlerPayload")]
    ]

    handler_signature: Required[
        Annotated[
            Optional[Literal["AGE_QUESTION", "SIMPLE_MEDICAL_HISTORY_QUESTION"]], PropertyInfo(alias="handlerSignature")
        ]
    ]


class MatchingPayload(TypedDict, total=False):
    data_type: Required[
        Annotated[
            List[Literal["LAB", "MEDICATION", "DIAGNOSIS", "PROCEDURE", "VITALS", "DEMOGRAPHICS", "ALLERGY"]],
            PropertyInfo(alias="dataType"),
        ]
    ]

    routing_metadata: Annotated[Optional[MatchingPayloadRoutingMetadata], PropertyInfo(alias="routingMetadata")]

    schema_version: Annotated[Literal["v1"], PropertyInfo(alias="schemaVersion")]
