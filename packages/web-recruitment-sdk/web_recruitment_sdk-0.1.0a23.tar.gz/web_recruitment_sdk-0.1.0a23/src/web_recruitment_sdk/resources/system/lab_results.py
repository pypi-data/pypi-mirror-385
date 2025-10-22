# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.system import lab_result_search_params
from ...types.system.lab_result_search_response import LabResultSearchResponse

__all__ = ["LabResultsResource", "AsyncLabResultsResource"]


class LabResultsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LabResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return LabResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LabResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return LabResultsResourceWithStreamingResponse(self)

    def search(
        self,
        tenant_db_name: str,
        *,
        search_text: str,
        limit: int | Omit = omit,
        similarity_threshold: Optional[float] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LabResultSearchResponse:
        """
        Retrieve lab results along with metadata about result counts and units.

        Args:
          search_text: Text to search for similar entities

          limit: Maximum number of results to return

          similarity_threshold: Minimum similarity score for returned entities

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/lab-results/search",
            body=maybe_transform(
                {
                    "search_text": search_text,
                    "limit": limit,
                    "similarity_threshold": similarity_threshold,
                },
                lab_result_search_params.LabResultSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LabResultSearchResponse,
        )


class AsyncLabResultsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLabResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncLabResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLabResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncLabResultsResourceWithStreamingResponse(self)

    async def search(
        self,
        tenant_db_name: str,
        *,
        search_text: str,
        limit: int | Omit = omit,
        similarity_threshold: Optional[float] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LabResultSearchResponse:
        """
        Retrieve lab results along with metadata about result counts and units.

        Args:
          search_text: Text to search for similar entities

          limit: Maximum number of results to return

          similarity_threshold: Minimum similarity score for returned entities

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/lab-results/search",
            body=await async_maybe_transform(
                {
                    "search_text": search_text,
                    "limit": limit,
                    "similarity_threshold": similarity_threshold,
                },
                lab_result_search_params.LabResultSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LabResultSearchResponse,
        )


class LabResultsResourceWithRawResponse:
    def __init__(self, lab_results: LabResultsResource) -> None:
        self._lab_results = lab_results

        self.search = to_raw_response_wrapper(
            lab_results.search,
        )


class AsyncLabResultsResourceWithRawResponse:
    def __init__(self, lab_results: AsyncLabResultsResource) -> None:
        self._lab_results = lab_results

        self.search = async_to_raw_response_wrapper(
            lab_results.search,
        )


class LabResultsResourceWithStreamingResponse:
    def __init__(self, lab_results: LabResultsResource) -> None:
        self._lab_results = lab_results

        self.search = to_streamed_response_wrapper(
            lab_results.search,
        )


class AsyncLabResultsResourceWithStreamingResponse:
    def __init__(self, lab_results: AsyncLabResultsResource) -> None:
        self._lab_results = lab_results

        self.search = async_to_streamed_response_wrapper(
            lab_results.search,
        )
