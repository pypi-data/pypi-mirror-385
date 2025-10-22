# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["SystemGetPatientMatchDataParams"]


class SystemGetPatientMatchDataParams(TypedDict, total=False):
    criteria_id: Required[Annotated[int, PropertyInfo(alias="criteriaId")]]

    patient_ids: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="patientIds")]]
