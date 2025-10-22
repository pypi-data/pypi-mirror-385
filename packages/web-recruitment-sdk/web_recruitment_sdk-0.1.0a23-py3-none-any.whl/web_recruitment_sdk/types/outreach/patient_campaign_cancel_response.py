# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from ..._utils import PropertyInfo
from ..._models import BaseModel
from ..patient_read import PatientRead

__all__ = [
    "PatientCampaignCancelResponse",
    "OutreachAttempt",
    "OutreachAttemptPhoneCallAttemptRead",
    "OutreachAttemptPhoneCallAttemptReadOutreachAction",
    "OutreachAttemptPhoneCallAttemptReadOutreachActionPhoneCallActionRead",
    "OutreachAttemptPhoneCallAttemptReadOutreachActionSMSActionRead",
    "OutreachAttemptSMSAttemptRead",
    "OutreachAttemptSMSAttemptReadOutreachAction",
    "OutreachAttemptSMSAttemptReadOutreachActionPhoneCallActionRead",
    "OutreachAttemptSMSAttemptReadOutreachActionSMSActionRead",
]


class OutreachAttemptPhoneCallAttemptReadOutreachActionPhoneCallActionRead(BaseModel):
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


class OutreachAttemptPhoneCallAttemptReadOutreachActionSMSActionRead(BaseModel):
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


OutreachAttemptPhoneCallAttemptReadOutreachAction: TypeAlias = Annotated[
    Union[
        OutreachAttemptPhoneCallAttemptReadOutreachActionPhoneCallActionRead,
        OutreachAttemptPhoneCallAttemptReadOutreachActionSMSActionRead,
    ],
    PropertyInfo(discriminator="type"),
]


class OutreachAttemptPhoneCallAttemptRead(BaseModel):
    id: int

    attempt_type: Literal["PHONE_CALL"] = FieldInfo(alias="attemptType")

    patient_campaign_id: int = FieldInfo(alias="patientCampaignId")

    task_id: int = FieldInfo(alias="taskId")

    caller_phone_number: Optional[str] = FieldInfo(alias="callerPhoneNumber", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    duration_seconds: Optional[int] = FieldInfo(alias="durationSeconds", default=None)

    outreach_actions: Optional[List[OutreachAttemptPhoneCallAttemptReadOutreachAction]] = FieldInfo(
        alias="outreachActions", default=None
    )

    recipient_phone_number: Optional[str] = FieldInfo(alias="recipientPhoneNumber", default=None)

    transcript_url: Optional[str] = FieldInfo(alias="transcriptUrl", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


class OutreachAttemptSMSAttemptReadOutreachActionPhoneCallActionRead(BaseModel):
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


class OutreachAttemptSMSAttemptReadOutreachActionSMSActionRead(BaseModel):
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


OutreachAttemptSMSAttemptReadOutreachAction: TypeAlias = Annotated[
    Union[
        OutreachAttemptSMSAttemptReadOutreachActionPhoneCallActionRead,
        OutreachAttemptSMSAttemptReadOutreachActionSMSActionRead,
    ],
    PropertyInfo(discriminator="type"),
]


class OutreachAttemptSMSAttemptRead(BaseModel):
    id: int

    attempt_type: Literal["SMS"] = FieldInfo(alias="attemptType")

    patient_campaign_id: int = FieldInfo(alias="patientCampaignId")

    task_id: int = FieldInfo(alias="taskId")

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    outreach_actions: Optional[List[OutreachAttemptSMSAttemptReadOutreachAction]] = FieldInfo(
        alias="outreachActions", default=None
    )

    recipient_phone_number: Optional[str] = FieldInfo(alias="recipientPhoneNumber", default=None)

    sender_phone_number: Optional[str] = FieldInfo(alias="senderPhoneNumber", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


OutreachAttempt: TypeAlias = Annotated[
    Union[OutreachAttemptPhoneCallAttemptRead, OutreachAttemptSMSAttemptRead],
    PropertyInfo(discriminator="attempt_type"),
]


class PatientCampaignCancelResponse(BaseModel):
    id: int

    campaign_id: int = FieldInfo(alias="campaignId")

    trially_patient_id: str = FieldInfo(alias="triallyPatientId")

    outreach_attempts: Optional[List[OutreachAttempt]] = FieldInfo(alias="outreachAttempts", default=None)

    patient: Optional[PatientRead] = None

    status: Optional[Literal["NOT_STARTED", "IN_PROGRESS", "SUCCESSFUL", "UNSUCCESSFUL"]] = None
    """Patient's journey state within a campaign"""
