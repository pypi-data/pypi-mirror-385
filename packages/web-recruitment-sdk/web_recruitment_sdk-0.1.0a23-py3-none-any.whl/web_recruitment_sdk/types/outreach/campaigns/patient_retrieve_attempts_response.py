# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from ...._utils import PropertyInfo
from ...._models import BaseModel

__all__ = [
    "PatientRetrieveAttemptsResponse",
    "PatientRetrieveAttemptsResponseItem",
    "PatientRetrieveAttemptsResponseItemPhoneCallAttemptRead",
    "PatientRetrieveAttemptsResponseItemPhoneCallAttemptReadOutreachAction",
    "PatientRetrieveAttemptsResponseItemPhoneCallAttemptReadOutreachActionPhoneCallActionRead",
    "PatientRetrieveAttemptsResponseItemPhoneCallAttemptReadOutreachActionSMSActionRead",
    "PatientRetrieveAttemptsResponseItemSMSAttemptRead",
    "PatientRetrieveAttemptsResponseItemSMSAttemptReadOutreachAction",
    "PatientRetrieveAttemptsResponseItemSMSAttemptReadOutreachActionPhoneCallActionRead",
    "PatientRetrieveAttemptsResponseItemSMSAttemptReadOutreachActionSMSActionRead",
]


class PatientRetrieveAttemptsResponseItemPhoneCallAttemptReadOutreachActionPhoneCallActionRead(BaseModel):
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


class PatientRetrieveAttemptsResponseItemPhoneCallAttemptReadOutreachActionSMSActionRead(BaseModel):
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


PatientRetrieveAttemptsResponseItemPhoneCallAttemptReadOutreachAction: TypeAlias = Annotated[
    Union[
        PatientRetrieveAttemptsResponseItemPhoneCallAttemptReadOutreachActionPhoneCallActionRead,
        PatientRetrieveAttemptsResponseItemPhoneCallAttemptReadOutreachActionSMSActionRead,
    ],
    PropertyInfo(discriminator="type"),
]


class PatientRetrieveAttemptsResponseItemPhoneCallAttemptRead(BaseModel):
    id: int

    attempt_type: Literal["PHONE_CALL"] = FieldInfo(alias="attemptType")

    patient_campaign_id: int = FieldInfo(alias="patientCampaignId")

    task_id: int = FieldInfo(alias="taskId")

    caller_phone_number: Optional[str] = FieldInfo(alias="callerPhoneNumber", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    duration_seconds: Optional[int] = FieldInfo(alias="durationSeconds", default=None)

    outreach_actions: Optional[List[PatientRetrieveAttemptsResponseItemPhoneCallAttemptReadOutreachAction]] = FieldInfo(
        alias="outreachActions", default=None
    )

    recipient_phone_number: Optional[str] = FieldInfo(alias="recipientPhoneNumber", default=None)

    transcript_url: Optional[str] = FieldInfo(alias="transcriptUrl", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


class PatientRetrieveAttemptsResponseItemSMSAttemptReadOutreachActionPhoneCallActionRead(BaseModel):
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


class PatientRetrieveAttemptsResponseItemSMSAttemptReadOutreachActionSMSActionRead(BaseModel):
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


PatientRetrieveAttemptsResponseItemSMSAttemptReadOutreachAction: TypeAlias = Annotated[
    Union[
        PatientRetrieveAttemptsResponseItemSMSAttemptReadOutreachActionPhoneCallActionRead,
        PatientRetrieveAttemptsResponseItemSMSAttemptReadOutreachActionSMSActionRead,
    ],
    PropertyInfo(discriminator="type"),
]


class PatientRetrieveAttemptsResponseItemSMSAttemptRead(BaseModel):
    id: int

    attempt_type: Literal["SMS"] = FieldInfo(alias="attemptType")

    patient_campaign_id: int = FieldInfo(alias="patientCampaignId")

    task_id: int = FieldInfo(alias="taskId")

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    outreach_actions: Optional[List[PatientRetrieveAttemptsResponseItemSMSAttemptReadOutreachAction]] = FieldInfo(
        alias="outreachActions", default=None
    )

    recipient_phone_number: Optional[str] = FieldInfo(alias="recipientPhoneNumber", default=None)

    sender_phone_number: Optional[str] = FieldInfo(alias="senderPhoneNumber", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


PatientRetrieveAttemptsResponseItem: TypeAlias = Annotated[
    Union[PatientRetrieveAttemptsResponseItemPhoneCallAttemptRead, PatientRetrieveAttemptsResponseItemSMSAttemptRead],
    PropertyInfo(discriminator="attempt_type"),
]

PatientRetrieveAttemptsResponse: TypeAlias = List[PatientRetrieveAttemptsResponseItem]
