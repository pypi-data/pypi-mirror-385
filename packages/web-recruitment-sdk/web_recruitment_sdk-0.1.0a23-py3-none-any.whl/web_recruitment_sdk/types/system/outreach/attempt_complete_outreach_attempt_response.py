# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from ...._utils import PropertyInfo
from ...._models import BaseModel

__all__ = [
    "AttemptCompleteOutreachAttemptResponse",
    "PhoneCallAttemptRead",
    "PhoneCallAttemptReadOutreachAction",
    "PhoneCallAttemptReadOutreachActionPhoneCallActionRead",
    "PhoneCallAttemptReadOutreachActionSMSActionRead",
    "SMSAttemptRead",
    "SMSAttemptReadOutreachAction",
    "SMSAttemptReadOutreachActionPhoneCallActionRead",
    "SMSAttemptReadOutreachActionSMSActionRead",
]


class PhoneCallAttemptReadOutreachActionPhoneCallActionRead(BaseModel):
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


class PhoneCallAttemptReadOutreachActionSMSActionRead(BaseModel):
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


PhoneCallAttemptReadOutreachAction: TypeAlias = Annotated[
    Union[PhoneCallAttemptReadOutreachActionPhoneCallActionRead, PhoneCallAttemptReadOutreachActionSMSActionRead],
    PropertyInfo(discriminator="type"),
]


class PhoneCallAttemptRead(BaseModel):
    id: int

    attempt_type: Literal["PHONE_CALL"] = FieldInfo(alias="attemptType")

    patient_campaign_id: int = FieldInfo(alias="patientCampaignId")

    task_id: int = FieldInfo(alias="taskId")

    caller_phone_number: Optional[str] = FieldInfo(alias="callerPhoneNumber", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    duration_seconds: Optional[int] = FieldInfo(alias="durationSeconds", default=None)

    outreach_actions: Optional[List[PhoneCallAttemptReadOutreachAction]] = FieldInfo(
        alias="outreachActions", default=None
    )

    recipient_phone_number: Optional[str] = FieldInfo(alias="recipientPhoneNumber", default=None)

    transcript_url: Optional[str] = FieldInfo(alias="transcriptUrl", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


class SMSAttemptReadOutreachActionPhoneCallActionRead(BaseModel):
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


class SMSAttemptReadOutreachActionSMSActionRead(BaseModel):
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


SMSAttemptReadOutreachAction: TypeAlias = Annotated[
    Union[SMSAttemptReadOutreachActionPhoneCallActionRead, SMSAttemptReadOutreachActionSMSActionRead],
    PropertyInfo(discriminator="type"),
]


class SMSAttemptRead(BaseModel):
    id: int

    attempt_type: Literal["SMS"] = FieldInfo(alias="attemptType")

    patient_campaign_id: int = FieldInfo(alias="patientCampaignId")

    task_id: int = FieldInfo(alias="taskId")

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    outreach_actions: Optional[List[SMSAttemptReadOutreachAction]] = FieldInfo(alias="outreachActions", default=None)

    recipient_phone_number: Optional[str] = FieldInfo(alias="recipientPhoneNumber", default=None)

    sender_phone_number: Optional[str] = FieldInfo(alias="senderPhoneNumber", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


AttemptCompleteOutreachAttemptResponse: TypeAlias = Annotated[
    Union[PhoneCallAttemptRead, SMSAttemptRead], PropertyInfo(discriminator="attempt_type")
]
