# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SystemSearchEntitiesParams"]


class SystemSearchEntitiesParams(TypedDict, total=False):
    search_text: Required[Annotated[str, PropertyInfo(alias="searchText")]]
    """Text to search for similar entities"""

    entity_types: Annotated[
        Optional[List[Literal["condition", "medication", "allergy", "procedure", "lab_result", "social_history"]]],
        PropertyInfo(alias="entityTypes"),
    ]
    """Restrict results to the provided entity types.

    Defaults to excluding lab results unless explicitly requested.
    """

    limit: int
    """Maximum number of results to return"""

    similarity_threshold: Annotated[Optional[float], PropertyInfo(alias="similarityThreshold")]
    """Minimum similarity score for returned entities"""
