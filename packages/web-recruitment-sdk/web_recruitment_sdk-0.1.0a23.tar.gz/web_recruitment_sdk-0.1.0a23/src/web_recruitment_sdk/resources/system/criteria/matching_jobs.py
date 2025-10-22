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
from ....types.system.criteria import matching_job_create_params

__all__ = ["MatchingJobsResource", "AsyncMatchingJobsResource"]


class MatchingJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MatchingJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return MatchingJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MatchingJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return MatchingJobsResourceWithStreamingResponse(self)

    def create(
        self,
        criterion_id: int,
        *,
        tenant_db_name: str,
        site_ids: Optional[Iterable[int]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Create matching jobs for a specific criterion across specified sites

        Args:
          site_ids: List of site IDs to create matching jobs for. If not provided, jobs will be
              created for all sites.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/criteria/{criterion_id}/matching_jobs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"site_ids": site_ids}, matching_job_create_params.MatchingJobCreateParams),
            ),
            cast_to=object,
        )

    def delete(
        self,
        criterion_id: int,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Cancel all matching jobs for a specific criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._delete(
            f"/system/{tenant_db_name}/criteria/{criterion_id}/matching_jobs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncMatchingJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMatchingJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMatchingJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMatchingJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncMatchingJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        criterion_id: int,
        *,
        tenant_db_name: str,
        site_ids: Optional[Iterable[int]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Create matching jobs for a specific criterion across specified sites

        Args:
          site_ids: List of site IDs to create matching jobs for. If not provided, jobs will be
              created for all sites.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/criteria/{criterion_id}/matching_jobs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"site_ids": site_ids}, matching_job_create_params.MatchingJobCreateParams
                ),
            ),
            cast_to=object,
        )

    async def delete(
        self,
        criterion_id: int,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Cancel all matching jobs for a specific criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._delete(
            f"/system/{tenant_db_name}/criteria/{criterion_id}/matching_jobs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class MatchingJobsResourceWithRawResponse:
    def __init__(self, matching_jobs: MatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.create = to_raw_response_wrapper(
            matching_jobs.create,
        )
        self.delete = to_raw_response_wrapper(
            matching_jobs.delete,
        )


class AsyncMatchingJobsResourceWithRawResponse:
    def __init__(self, matching_jobs: AsyncMatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.create = async_to_raw_response_wrapper(
            matching_jobs.create,
        )
        self.delete = async_to_raw_response_wrapper(
            matching_jobs.delete,
        )


class MatchingJobsResourceWithStreamingResponse:
    def __init__(self, matching_jobs: MatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.create = to_streamed_response_wrapper(
            matching_jobs.create,
        )
        self.delete = to_streamed_response_wrapper(
            matching_jobs.delete,
        )


class AsyncMatchingJobsResourceWithStreamingResponse:
    def __init__(self, matching_jobs: AsyncMatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.create = async_to_streamed_response_wrapper(
            matching_jobs.create,
        )
        self.delete = async_to_streamed_response_wrapper(
            matching_jobs.delete,
        )
