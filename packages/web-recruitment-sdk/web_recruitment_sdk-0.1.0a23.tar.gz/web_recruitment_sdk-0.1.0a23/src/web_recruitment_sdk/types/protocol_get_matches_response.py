# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .patient_match import PatientMatch

__all__ = ["ProtocolGetMatchesResponse"]


class ProtocolGetMatchesResponse(BaseModel):
    items: List[PatientMatch]

    limit: int

    offset: int

    total: int
