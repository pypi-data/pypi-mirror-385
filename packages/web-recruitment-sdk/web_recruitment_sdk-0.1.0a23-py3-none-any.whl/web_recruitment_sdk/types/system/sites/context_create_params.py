# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["ContextCreateParams"]


class ContextCreateParams(TypedDict, total=False):
    tenant_db_name: Required[str]

    instructions: Optional[str]
    """Specific instructions for AI agent behavior, tone, and response guidelines"""

    knowledge: Optional[str]
    """
    All factual site information: address, hours, contact info, parking, services,
    FAQ answers, directions, visit details, etc.
    """
