# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import TypedDict

__all__ = ["ProtocolGetFunnelParams"]


class ProtocolGetFunnelParams(TypedDict, total=False):
    matching_criteria_ids: Optional[Iterable[int]]

    site_ids: Optional[Iterable[int]]
