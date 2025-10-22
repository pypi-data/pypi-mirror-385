# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AttemptCreateOutreachActionParams", "PhoneCallActionCreate", "SMSActionCreate"]


class PhoneCallActionCreate(TypedDict, total=False):
    tenant_db_name: Required[str]

    body_attempt_id: Required[Annotated[int, PropertyInfo(alias="attemptId")]]

    status: Required[
        Literal[
            "STARTED",
            "NO_ANSWER",
            "VOICEMAIL_LEFT",
            "WRONG_NUMBER",
            "HANGUP",
            "INTERESTED",
            "NOT_INTERESTED",
            "SCHEDULED",
            "DO_NOT_CALL",
            "ENDED",
        ]
    ]
    """Status values specific to phone call actions"""

    type: Required[Literal["PHONE_CALL"]]


class SMSActionCreate(TypedDict, total=False):
    tenant_db_name: Required[str]

    body_attempt_id: Required[Annotated[int, PropertyInfo(alias="attemptId")]]

    message: Required[str]

    status: Required[
        Literal[
            "SENT",
            "FAILED_TO_SEND",
            "REPLIED",
            "INTERESTED",
            "NOT_INTERESTED",
            "BOOKING_LINK_SENT",
            "SCHEDULED",
            "DO_NOT_CALL",
        ]
    ]
    """Status values specific to SMS actions"""

    type: Required[Literal["SMS"]]


AttemptCreateOutreachActionParams: TypeAlias = Union[PhoneCallActionCreate, SMSActionCreate]
