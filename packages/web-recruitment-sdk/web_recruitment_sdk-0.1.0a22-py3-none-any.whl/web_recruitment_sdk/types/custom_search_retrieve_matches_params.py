# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import TypedDict

__all__ = ["CustomSearchRetrieveMatchesParams"]


class CustomSearchRetrieveMatchesParams(TypedDict, total=False):
    limit: int

    matching_criteria_ids: Optional[Iterable[int]]

    offset: int

    search: Optional[str]

    site_ids: Optional[Iterable[int]]
