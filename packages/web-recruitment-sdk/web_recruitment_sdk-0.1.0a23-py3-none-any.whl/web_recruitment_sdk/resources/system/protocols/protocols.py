# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from .matching_jobs import (
    MatchingJobsResource,
    AsyncMatchingJobsResource,
    MatchingJobsResourceWithRawResponse,
    AsyncMatchingJobsResourceWithRawResponse,
    MatchingJobsResourceWithStreamingResponse,
    AsyncMatchingJobsResourceWithStreamingResponse,
)
from ...._base_client import make_request_options
from ....types.system import protocol_refresh_patient_matches_params
from ....types.protocol_read import ProtocolRead
from ....types.system.protocol_list_response import ProtocolListResponse
from ....types.system.protocol_get_criteria_response import ProtocolGetCriteriaResponse

__all__ = ["ProtocolsResource", "AsyncProtocolsResource"]


class ProtocolsResource(SyncAPIResource):
    @cached_property
    def matching_jobs(self) -> MatchingJobsResource:
        return MatchingJobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ProtocolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return ProtocolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProtocolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return ProtocolsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        protocol_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProtocolRead:
        """
        Get a protocol for a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not protocol_id:
            raise ValueError(f"Expected a non-empty value for `protocol_id` but received {protocol_id!r}")
        return self._get(
            f"/system/{tenant_db_name}/protocols/{protocol_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
        )

    def list(
        self,
        tenant_db_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProtocolListResponse:
        """
        Get all protocols for a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._get(
            f"/system/{tenant_db_name}/protocols",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolListResponse,
        )

    def get_criteria(
        self,
        protocol_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProtocolGetCriteriaResponse:
        """
        Get Protocol Criteria

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not protocol_id:
            raise ValueError(f"Expected a non-empty value for `protocol_id` but received {protocol_id!r}")
        return self._get(
            f"/system/{tenant_db_name}/protocols/{protocol_id}/criteria",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolGetCriteriaResponse,
        )

    def refresh_patient_matches(
        self,
        tenant_db_name: str,
        *,
        force_refresh: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Refresh the materialized view of protocol patient matches.

        NOTE: This endpoint
        could take several minutes to complete for large datasets.

        Args: force_refresh: If True, the view will be refreshed without any checks.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/protocols/refresh-patient-matches",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"force_refresh": force_refresh},
                    protocol_refresh_patient_matches_params.ProtocolRefreshPatientMatchesParams,
                ),
            ),
            cast_to=object,
        )


class AsyncProtocolsResource(AsyncAPIResource):
    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResource:
        return AsyncMatchingJobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncProtocolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncProtocolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProtocolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncProtocolsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        protocol_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProtocolRead:
        """
        Get a protocol for a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not protocol_id:
            raise ValueError(f"Expected a non-empty value for `protocol_id` but received {protocol_id!r}")
        return await self._get(
            f"/system/{tenant_db_name}/protocols/{protocol_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
        )

    async def list(
        self,
        tenant_db_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProtocolListResponse:
        """
        Get all protocols for a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._get(
            f"/system/{tenant_db_name}/protocols",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolListResponse,
        )

    async def get_criteria(
        self,
        protocol_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProtocolGetCriteriaResponse:
        """
        Get Protocol Criteria

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not protocol_id:
            raise ValueError(f"Expected a non-empty value for `protocol_id` but received {protocol_id!r}")
        return await self._get(
            f"/system/{tenant_db_name}/protocols/{protocol_id}/criteria",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolGetCriteriaResponse,
        )

    async def refresh_patient_matches(
        self,
        tenant_db_name: str,
        *,
        force_refresh: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Refresh the materialized view of protocol patient matches.

        NOTE: This endpoint
        could take several minutes to complete for large datasets.

        Args: force_refresh: If True, the view will be refreshed without any checks.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/protocols/refresh-patient-matches",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"force_refresh": force_refresh},
                    protocol_refresh_patient_matches_params.ProtocolRefreshPatientMatchesParams,
                ),
            ),
            cast_to=object,
        )


class ProtocolsResourceWithRawResponse:
    def __init__(self, protocols: ProtocolsResource) -> None:
        self._protocols = protocols

        self.retrieve = to_raw_response_wrapper(
            protocols.retrieve,
        )
        self.list = to_raw_response_wrapper(
            protocols.list,
        )
        self.get_criteria = to_raw_response_wrapper(
            protocols.get_criteria,
        )
        self.refresh_patient_matches = to_raw_response_wrapper(
            protocols.refresh_patient_matches,
        )

    @cached_property
    def matching_jobs(self) -> MatchingJobsResourceWithRawResponse:
        return MatchingJobsResourceWithRawResponse(self._protocols.matching_jobs)


class AsyncProtocolsResourceWithRawResponse:
    def __init__(self, protocols: AsyncProtocolsResource) -> None:
        self._protocols = protocols

        self.retrieve = async_to_raw_response_wrapper(
            protocols.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            protocols.list,
        )
        self.get_criteria = async_to_raw_response_wrapper(
            protocols.get_criteria,
        )
        self.refresh_patient_matches = async_to_raw_response_wrapper(
            protocols.refresh_patient_matches,
        )

    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResourceWithRawResponse:
        return AsyncMatchingJobsResourceWithRawResponse(self._protocols.matching_jobs)


class ProtocolsResourceWithStreamingResponse:
    def __init__(self, protocols: ProtocolsResource) -> None:
        self._protocols = protocols

        self.retrieve = to_streamed_response_wrapper(
            protocols.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            protocols.list,
        )
        self.get_criteria = to_streamed_response_wrapper(
            protocols.get_criteria,
        )
        self.refresh_patient_matches = to_streamed_response_wrapper(
            protocols.refresh_patient_matches,
        )

    @cached_property
    def matching_jobs(self) -> MatchingJobsResourceWithStreamingResponse:
        return MatchingJobsResourceWithStreamingResponse(self._protocols.matching_jobs)


class AsyncProtocolsResourceWithStreamingResponse:
    def __init__(self, protocols: AsyncProtocolsResource) -> None:
        self._protocols = protocols

        self.retrieve = async_to_streamed_response_wrapper(
            protocols.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            protocols.list,
        )
        self.get_criteria = async_to_streamed_response_wrapper(
            protocols.get_criteria,
        )
        self.refresh_patient_matches = async_to_streamed_response_wrapper(
            protocols.refresh_patient_matches,
        )

    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResourceWithStreamingResponse:
        return AsyncMatchingJobsResourceWithStreamingResponse(self._protocols.matching_jobs)
