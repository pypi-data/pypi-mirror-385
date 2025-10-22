# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AttemptCompleteOutreachAttemptParams", "PhoneCallAttemptUpdate", "SMSAttemptUpdate"]


class PhoneCallAttemptUpdate(TypedDict, total=False):
    tenant_db_name: Required[str]

    type: Required[Literal["PHONE_CALL"]]

    duration_seconds: Annotated[Optional[int], PropertyInfo(alias="durationSeconds")]

    transcript_url: Annotated[Optional[str], PropertyInfo(alias="transcriptUrl")]


class SMSAttemptUpdate(TypedDict, total=False):
    tenant_db_name: Required[str]

    type: Required[Literal["SMS"]]

    message: Optional[str]


AttemptCompleteOutreachAttemptParams: TypeAlias = Union[PhoneCallAttemptUpdate, SMSAttemptUpdate]
