# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BulkUpdateVitalsParams", "Body"]


class BulkUpdateVitalsParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    observed_at: Required[Annotated[Union[str, datetime], PropertyInfo(alias="observedAt", format="iso8601")]]

    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]

    unit: Required[Literal["kg/m2", "mmHg", "cm", "kg", "bpm", "breaths/min"]]

    value: Required[float]

    vital_kind: Required[
        Annotated[
            Literal["bmi", "bp_diastolic", "bp_systolic", "height", "weight", "pulse_rate", "respiration_rate"],
            PropertyInfo(alias="vitalKind"),
        ]
    ]
