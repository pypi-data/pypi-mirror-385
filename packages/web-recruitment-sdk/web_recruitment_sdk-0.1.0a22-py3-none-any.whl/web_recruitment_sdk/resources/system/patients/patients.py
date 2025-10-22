# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import date
from typing_extensions import Literal

import httpx

from .bulk import (
    BulkResource,
    AsyncBulkResource,
    BulkResourceWithRawResponse,
    AsyncBulkResourceWithRawResponse,
    BulkResourceWithStreamingResponse,
    AsyncBulkResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.system import patient_create_params, patient_update_params
from ....types.patient_read import PatientRead

__all__ = ["PatientsResource", "AsyncPatientsResource"]


class PatientsResource(SyncAPIResource):
    @cached_property
    def bulk(self) -> BulkResource:
        return BulkResource(self._client)

    @cached_property
    def with_raw_response(self) -> PatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return PatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return PatientsResourceWithStreamingResponse(self)

    def create(
        self,
        tenant_db_name: str,
        *,
        dob: Union[str, date, None],
        email: Optional[str],
        family_name: str,
        given_name: str,
        site_id: int,
        trially_patient_id: str,
        cell_phone: Optional[str] | Omit = omit,
        city: Optional[str] | Omit = omit,
        do_not_call: Optional[bool] | Omit = omit,
        home_phone: Optional[str] | Omit = omit,
        is_interested_in_research: Optional[bool] | Omit = omit,
        last_encounter_date: Union[str, date, None] | Omit = omit,
        last_patient_activity: Union[str, date, None] | Omit = omit,
        middle_name: Optional[str] | Omit = omit,
        phone: Optional[str] | Omit = omit,
        preferred_language: Literal["ENGLISH", "SPANISH"] | Omit = omit,
        primary_provider: Optional[str] | Omit = omit,
        provider_first_name: Optional[str] | Omit = omit,
        provider_last_name: Optional[str] | Omit = omit,
        source: Literal["EHR", "CSV"] | Omit = omit,
        state: Optional[
            Literal[
                "AL",
                "AK",
                "AS",
                "AZ",
                "AR",
                "CA",
                "CO",
                "CT",
                "DE",
                "DC",
                "FL",
                "FM",
                "GA",
                "GU",
                "HI",
                "ID",
                "IL",
                "IN",
                "IA",
                "KS",
                "KY",
                "LA",
                "ME",
                "MD",
                "MA",
                "MH",
                "MI",
                "MN",
                "MS",
                "MO",
                "MT",
                "NE",
                "NV",
                "NH",
                "NJ",
                "NM",
                "NY",
                "NC",
                "ND",
                "MP",
                "OH",
                "OK",
                "OR",
                "PW",
                "PA",
                "PR",
                "RI",
                "SC",
                "SD",
                "TN",
                "TX",
                "TT",
                "UT",
                "VT",
                "VA",
                "VI",
                "WA",
                "WV",
                "WI",
                "WY",
            ]
        ]
        | Omit = omit,
        street_address: Optional[str] | Omit = omit,
        zip_code: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PatientRead:
        """
        Create Patient

        Args:
          state: US state codes and territories.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/patients",
            body=maybe_transform(
                {
                    "dob": dob,
                    "email": email,
                    "family_name": family_name,
                    "given_name": given_name,
                    "site_id": site_id,
                    "trially_patient_id": trially_patient_id,
                    "cell_phone": cell_phone,
                    "city": city,
                    "do_not_call": do_not_call,
                    "home_phone": home_phone,
                    "is_interested_in_research": is_interested_in_research,
                    "last_encounter_date": last_encounter_date,
                    "last_patient_activity": last_patient_activity,
                    "middle_name": middle_name,
                    "phone": phone,
                    "preferred_language": preferred_language,
                    "primary_provider": primary_provider,
                    "provider_first_name": provider_first_name,
                    "provider_last_name": provider_last_name,
                    "source": source,
                    "state": state,
                    "street_address": street_address,
                    "zip_code": zip_code,
                },
                patient_create_params.PatientCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRead,
        )

    def update(
        self,
        patient_id: int,
        *,
        tenant_db_name: str,
        do_not_call: bool,
        city: Optional[str] | Omit = omit,
        state: Optional[str] | Omit = omit,
        street_address: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PatientRead:
        """
        Patch Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._patch(
            f"/system/{tenant_db_name}/patients/{patient_id}",
            body=maybe_transform(
                {
                    "do_not_call": do_not_call,
                    "city": city,
                    "state": state,
                    "street_address": street_address,
                },
                patient_update_params.PatientUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRead,
        )


class AsyncPatientsResource(AsyncAPIResource):
    @cached_property
    def bulk(self) -> AsyncBulkResource:
        return AsyncBulkResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncPatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncPatientsResourceWithStreamingResponse(self)

    async def create(
        self,
        tenant_db_name: str,
        *,
        dob: Union[str, date, None],
        email: Optional[str],
        family_name: str,
        given_name: str,
        site_id: int,
        trially_patient_id: str,
        cell_phone: Optional[str] | Omit = omit,
        city: Optional[str] | Omit = omit,
        do_not_call: Optional[bool] | Omit = omit,
        home_phone: Optional[str] | Omit = omit,
        is_interested_in_research: Optional[bool] | Omit = omit,
        last_encounter_date: Union[str, date, None] | Omit = omit,
        last_patient_activity: Union[str, date, None] | Omit = omit,
        middle_name: Optional[str] | Omit = omit,
        phone: Optional[str] | Omit = omit,
        preferred_language: Literal["ENGLISH", "SPANISH"] | Omit = omit,
        primary_provider: Optional[str] | Omit = omit,
        provider_first_name: Optional[str] | Omit = omit,
        provider_last_name: Optional[str] | Omit = omit,
        source: Literal["EHR", "CSV"] | Omit = omit,
        state: Optional[
            Literal[
                "AL",
                "AK",
                "AS",
                "AZ",
                "AR",
                "CA",
                "CO",
                "CT",
                "DE",
                "DC",
                "FL",
                "FM",
                "GA",
                "GU",
                "HI",
                "ID",
                "IL",
                "IN",
                "IA",
                "KS",
                "KY",
                "LA",
                "ME",
                "MD",
                "MA",
                "MH",
                "MI",
                "MN",
                "MS",
                "MO",
                "MT",
                "NE",
                "NV",
                "NH",
                "NJ",
                "NM",
                "NY",
                "NC",
                "ND",
                "MP",
                "OH",
                "OK",
                "OR",
                "PW",
                "PA",
                "PR",
                "RI",
                "SC",
                "SD",
                "TN",
                "TX",
                "TT",
                "UT",
                "VT",
                "VA",
                "VI",
                "WA",
                "WV",
                "WI",
                "WY",
            ]
        ]
        | Omit = omit,
        street_address: Optional[str] | Omit = omit,
        zip_code: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PatientRead:
        """
        Create Patient

        Args:
          state: US state codes and territories.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/patients",
            body=await async_maybe_transform(
                {
                    "dob": dob,
                    "email": email,
                    "family_name": family_name,
                    "given_name": given_name,
                    "site_id": site_id,
                    "trially_patient_id": trially_patient_id,
                    "cell_phone": cell_phone,
                    "city": city,
                    "do_not_call": do_not_call,
                    "home_phone": home_phone,
                    "is_interested_in_research": is_interested_in_research,
                    "last_encounter_date": last_encounter_date,
                    "last_patient_activity": last_patient_activity,
                    "middle_name": middle_name,
                    "phone": phone,
                    "preferred_language": preferred_language,
                    "primary_provider": primary_provider,
                    "provider_first_name": provider_first_name,
                    "provider_last_name": provider_last_name,
                    "source": source,
                    "state": state,
                    "street_address": street_address,
                    "zip_code": zip_code,
                },
                patient_create_params.PatientCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRead,
        )

    async def update(
        self,
        patient_id: int,
        *,
        tenant_db_name: str,
        do_not_call: bool,
        city: Optional[str] | Omit = omit,
        state: Optional[str] | Omit = omit,
        street_address: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PatientRead:
        """
        Patch Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._patch(
            f"/system/{tenant_db_name}/patients/{patient_id}",
            body=await async_maybe_transform(
                {
                    "do_not_call": do_not_call,
                    "city": city,
                    "state": state,
                    "street_address": street_address,
                },
                patient_update_params.PatientUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRead,
        )


class PatientsResourceWithRawResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.create = to_raw_response_wrapper(
            patients.create,
        )
        self.update = to_raw_response_wrapper(
            patients.update,
        )

    @cached_property
    def bulk(self) -> BulkResourceWithRawResponse:
        return BulkResourceWithRawResponse(self._patients.bulk)


class AsyncPatientsResourceWithRawResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.create = async_to_raw_response_wrapper(
            patients.create,
        )
        self.update = async_to_raw_response_wrapper(
            patients.update,
        )

    @cached_property
    def bulk(self) -> AsyncBulkResourceWithRawResponse:
        return AsyncBulkResourceWithRawResponse(self._patients.bulk)


class PatientsResourceWithStreamingResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.create = to_streamed_response_wrapper(
            patients.create,
        )
        self.update = to_streamed_response_wrapper(
            patients.update,
        )

    @cached_property
    def bulk(self) -> BulkResourceWithStreamingResponse:
        return BulkResourceWithStreamingResponse(self._patients.bulk)


class AsyncPatientsResourceWithStreamingResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.create = async_to_streamed_response_wrapper(
            patients.create,
        )
        self.update = async_to_streamed_response_wrapper(
            patients.update,
        )

    @cached_property
    def bulk(self) -> AsyncBulkResourceWithStreamingResponse:
        return AsyncBulkResourceWithStreamingResponse(self._patients.bulk)
