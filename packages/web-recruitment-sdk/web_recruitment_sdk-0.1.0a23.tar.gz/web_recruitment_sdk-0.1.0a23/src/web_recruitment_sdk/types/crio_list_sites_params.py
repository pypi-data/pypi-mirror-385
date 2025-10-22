# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .._types import SequenceNotStr

__all__ = ["CrioListSitesParams"]


class CrioListSitesParams(TypedDict, total=False):
    client_ids: SequenceNotStr[str]

    tenant_id: str
