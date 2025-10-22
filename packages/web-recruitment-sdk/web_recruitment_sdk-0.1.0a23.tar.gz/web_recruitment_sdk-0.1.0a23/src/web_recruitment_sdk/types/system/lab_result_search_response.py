# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["LabResultSearchResponse", "Result"]


class Result(BaseModel):
    entity: str

    entity_id: str = FieldInfo(alias="entityId")

    entity_type: Literal["condition", "medication", "allergy", "procedure", "lab_result", "social_history"] = FieldInfo(
        alias="entityType"
    )

    lab_result_count: int = FieldInfo(alias="labResultCount")
    """Number of lab results found for the entity"""

    similarity_score: float = FieldInfo(alias="similarityScore")
    """Similarity score between 0 and 1"""

    used_units: Optional[List[str]] = FieldInfo(alias="usedUnits", default=None)
    """Distinct lab result units observed in the returned results"""


class LabResultSearchResponse(BaseModel):
    result_count: int = FieldInfo(alias="resultCount")

    results: List[Result]
    """List of lab results search results"""

    search_text: str = FieldInfo(alias="searchText")
