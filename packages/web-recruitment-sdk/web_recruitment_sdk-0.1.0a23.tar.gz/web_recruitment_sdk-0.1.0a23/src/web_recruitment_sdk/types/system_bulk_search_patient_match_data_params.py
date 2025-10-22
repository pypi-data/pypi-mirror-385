# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["SystemBulkSearchPatientMatchDataParams"]


class SystemBulkSearchPatientMatchDataParams(TypedDict, total=False):
    search_text: Required[Annotated[str, PropertyInfo(alias="searchText")]]

    trially_patient_ids: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="triallyPatientIds")]]
