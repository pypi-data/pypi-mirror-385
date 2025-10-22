# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["PatientGetProtocolMatchesResponse", "PatientGetProtocolMatchesResponseItem"]


class PatientGetProtocolMatchesResponseItem(BaseModel):
    id: int

    match_last_updated: Optional[datetime] = FieldInfo(alias="matchLastUpdated", default=None)

    match_percentage: float = FieldInfo(alias="matchPercentage")

    title: str


PatientGetProtocolMatchesResponse: TypeAlias = List[PatientGetProtocolMatchesResponseItem]
