# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["PatientImportCsvParams"]


class PatientImportCsvParams(TypedDict, total=False):
    fallback_zip_code: Required[str]
    """Default zip code if not provided in CSV"""

    file: Required[FileTypes]
    """CSV file containing patient data to upload and import"""

    site_id: Required[int]
    """Site ID for the patients"""
