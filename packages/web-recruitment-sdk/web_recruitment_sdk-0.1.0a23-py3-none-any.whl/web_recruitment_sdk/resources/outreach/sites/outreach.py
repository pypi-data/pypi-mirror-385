# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Query, Headers, NotGiven, not_given
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
from ....types.outreach.sites import outreach_create_params, outreach_update_params
from ....types.outreach.sites.outreach_create_response import OutreachCreateResponse
from ....types.outreach.sites.outreach_update_response import OutreachUpdateResponse

__all__ = ["OutreachResource", "AsyncOutreachResource"]


class OutreachResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OutreachResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return OutreachResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OutreachResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return OutreachResourceWithStreamingResponse(self)

    def create(
        self,
        site_id: int,
        *,
        outbound_phone_number: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OutreachCreateResponse:
        """
        Create site outreach configuration

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            f"/outreach/sites/{site_id}/outreach",
            body=maybe_transform(
                {"outbound_phone_number": outbound_phone_number}, outreach_create_params.OutreachCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OutreachCreateResponse,
        )

    def update(
        self,
        site_id: int,
        *,
        outbound_phone_number: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OutreachUpdateResponse:
        """
        Update site outreach configuration

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            f"/outreach/sites/{site_id}/outreach",
            body=maybe_transform(
                {"outbound_phone_number": outbound_phone_number}, outreach_update_params.OutreachUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OutreachUpdateResponse,
        )


class AsyncOutreachResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOutreachResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncOutreachResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOutreachResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncOutreachResourceWithStreamingResponse(self)

    async def create(
        self,
        site_id: int,
        *,
        outbound_phone_number: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OutreachCreateResponse:
        """
        Create site outreach configuration

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            f"/outreach/sites/{site_id}/outreach",
            body=await async_maybe_transform(
                {"outbound_phone_number": outbound_phone_number}, outreach_create_params.OutreachCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OutreachCreateResponse,
        )

    async def update(
        self,
        site_id: int,
        *,
        outbound_phone_number: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OutreachUpdateResponse:
        """
        Update site outreach configuration

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            f"/outreach/sites/{site_id}/outreach",
            body=await async_maybe_transform(
                {"outbound_phone_number": outbound_phone_number}, outreach_update_params.OutreachUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OutreachUpdateResponse,
        )


class OutreachResourceWithRawResponse:
    def __init__(self, outreach: OutreachResource) -> None:
        self._outreach = outreach

        self.create = to_raw_response_wrapper(
            outreach.create,
        )
        self.update = to_raw_response_wrapper(
            outreach.update,
        )


class AsyncOutreachResourceWithRawResponse:
    def __init__(self, outreach: AsyncOutreachResource) -> None:
        self._outreach = outreach

        self.create = async_to_raw_response_wrapper(
            outreach.create,
        )
        self.update = async_to_raw_response_wrapper(
            outreach.update,
        )


class OutreachResourceWithStreamingResponse:
    def __init__(self, outreach: OutreachResource) -> None:
        self._outreach = outreach

        self.create = to_streamed_response_wrapper(
            outreach.create,
        )
        self.update = to_streamed_response_wrapper(
            outreach.update,
        )


class AsyncOutreachResourceWithStreamingResponse:
    def __init__(self, outreach: AsyncOutreachResource) -> None:
        self._outreach = outreach

        self.create = async_to_streamed_response_wrapper(
            outreach.create,
        )
        self.update = async_to_streamed_response_wrapper(
            outreach.update,
        )
