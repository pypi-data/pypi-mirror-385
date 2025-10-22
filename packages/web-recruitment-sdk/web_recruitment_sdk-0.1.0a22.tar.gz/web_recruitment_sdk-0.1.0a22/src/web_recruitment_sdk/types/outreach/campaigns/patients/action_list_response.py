# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from ....._utils import PropertyInfo
from ....._models import BaseModel

__all__ = [
    "ActionListResponse",
    "ActionListResponseItem",
    "ActionListResponseItemPhoneCallActionRead",
    "ActionListResponseItemSMSActionRead",
]


class ActionListResponseItemPhoneCallActionRead(BaseModel):
    id: int

    outreach_attempt_id: int = FieldInfo(alias="outreachAttemptId")

    type: Literal["PHONE_CALL"]

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    status: Optional[
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
    ] = None
    """Status values specific to phone call actions"""

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


class ActionListResponseItemSMSActionRead(BaseModel):
    id: int

    outreach_attempt_id: int = FieldInfo(alias="outreachAttemptId")

    type: Literal["SMS"]

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    message: Optional[str] = None

    status: Optional[
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
    ] = None
    """Status values specific to SMS actions"""

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


ActionListResponseItem: TypeAlias = Annotated[
    Union[ActionListResponseItemPhoneCallActionRead, ActionListResponseItemSMSActionRead],
    PropertyInfo(discriminator="type"),
]

ActionListResponse: TypeAlias = List[ActionListResponseItem]
