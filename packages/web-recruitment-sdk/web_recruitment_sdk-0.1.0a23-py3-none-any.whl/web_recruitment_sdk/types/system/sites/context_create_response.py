# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["ContextCreateResponse"]


class ContextCreateResponse(BaseModel):
    id: int

    site_id: int = FieldInfo(alias="siteId")

    instructions: Optional[str] = None
    """Specific instructions for AI agent behavior, tone, and response guidelines"""

    knowledge: Optional[str] = None
    """
    All factual site information: address, hours, contact info, parking, services,
    FAQ answers, directions, visit details, etc.
    """
