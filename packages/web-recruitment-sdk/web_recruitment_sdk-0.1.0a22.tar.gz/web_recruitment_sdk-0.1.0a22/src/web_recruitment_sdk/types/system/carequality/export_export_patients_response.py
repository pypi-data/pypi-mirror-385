# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["ExportExportPatientsResponse"]


class ExportExportPatientsResponse(BaseModel):
    message: str
    """Status message or additional information"""

    status: str
    """Current status of the export job"""

    file_name: Optional[str] = FieldInfo(alias="fileName", default=None)
    """Name of the exported file (available after successful export)"""

    patient_count: Optional[int] = FieldInfo(alias="patientCount", default=None)
    """Number of patients exported (available after successful export)"""
