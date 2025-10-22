# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional

import httpx

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
from ....types.system.carequality import export_export_patients_params
from ....types.system.carequality.export_export_patients_response import ExportExportPatientsResponse

__all__ = ["ExportResource", "AsyncExportResource"]


class ExportResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExportResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return ExportResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExportResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return ExportResourceWithStreamingResponse(self)

    def export_patients(
        self,
        tenant_db_name: str,
        *,
        site_ids: Optional[Iterable[int]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExportExportPatientsResponse:
        """
        Export eligible patients to CSV for CareQuality/Innovar integration.

        This endpoint:

        - Queries patients from CareQuality-enabled sites
        - Filters for patients with recent encounters or upcoming appointments
        - Excludes patients with existing CareQuality documents
        - Encrypts patient IDs for CareQuality format
        - Generates CSV with required fields
        - Uploads to Innovar SFTP server

        Returns a response with the export status.

        Args:
          site_ids: Optional list of site IDs to filter the export. If not provided, exports from
              all CareQuality-enabled sites.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/carequality/export/patients",
            body=maybe_transform({"site_ids": site_ids}, export_export_patients_params.ExportExportPatientsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExportExportPatientsResponse,
        )


class AsyncExportResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExportResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncExportResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExportResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncExportResourceWithStreamingResponse(self)

    async def export_patients(
        self,
        tenant_db_name: str,
        *,
        site_ids: Optional[Iterable[int]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExportExportPatientsResponse:
        """
        Export eligible patients to CSV for CareQuality/Innovar integration.

        This endpoint:

        - Queries patients from CareQuality-enabled sites
        - Filters for patients with recent encounters or upcoming appointments
        - Excludes patients with existing CareQuality documents
        - Encrypts patient IDs for CareQuality format
        - Generates CSV with required fields
        - Uploads to Innovar SFTP server

        Returns a response with the export status.

        Args:
          site_ids: Optional list of site IDs to filter the export. If not provided, exports from
              all CareQuality-enabled sites.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/carequality/export/patients",
            body=await async_maybe_transform(
                {"site_ids": site_ids}, export_export_patients_params.ExportExportPatientsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExportExportPatientsResponse,
        )


class ExportResourceWithRawResponse:
    def __init__(self, export: ExportResource) -> None:
        self._export = export

        self.export_patients = to_raw_response_wrapper(
            export.export_patients,
        )


class AsyncExportResourceWithRawResponse:
    def __init__(self, export: AsyncExportResource) -> None:
        self._export = export

        self.export_patients = async_to_raw_response_wrapper(
            export.export_patients,
        )


class ExportResourceWithStreamingResponse:
    def __init__(self, export: ExportResource) -> None:
        self._export = export

        self.export_patients = to_streamed_response_wrapper(
            export.export_patients,
        )


class AsyncExportResourceWithStreamingResponse:
    def __init__(self, export: AsyncExportResource) -> None:
        self._export = export

        self.export_patients = async_to_streamed_response_wrapper(
            export.export_patients,
        )
