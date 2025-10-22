# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ExportExportPatientsParams"]


class ExportExportPatientsParams(TypedDict, total=False):
    site_ids: Annotated[Optional[Iterable[int]], PropertyInfo(alias="siteIds")]
    """Optional list of site IDs to filter the export.

    If not provided, exports from all CareQuality-enabled sites.
    """
