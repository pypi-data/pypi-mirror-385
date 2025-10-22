# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["PatientImportCsvResponse", "ImportResult", "ImportResultFailedImport"]


class ImportResultFailedImport(BaseModel):
    patient_data: Dict[str, str] = FieldInfo(alias="patientData")

    reason: str

    row_number: int = FieldInfo(alias="rowNumber")


class ImportResult(BaseModel):
    failed_imports: List[ImportResultFailedImport] = FieldInfo(alias="failedImports")

    successful_imports: int = FieldInfo(alias="successfulImports")

    total_rows: int = FieldInfo(alias="totalRows")

    skipped_duplicates: Optional[int] = FieldInfo(alias="skippedDuplicates", default=None)

    successful_patient_ids: Optional[List[str]] = FieldInfo(alias="successfulPatientIds", default=None)


class PatientImportCsvResponse(BaseModel):
    import_result: ImportResult = FieldInfo(alias="importResult")
    """Result of a CSV patient import operation."""

    message: str

    storage_url: str = FieldInfo(alias="storageUrl")
