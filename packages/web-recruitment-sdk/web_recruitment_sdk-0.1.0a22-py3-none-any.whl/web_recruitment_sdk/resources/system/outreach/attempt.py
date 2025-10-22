# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Optional, cast
from typing_extensions import Literal, overload

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import required_args, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.system.outreach import attempt_complete_outreach_attempt_params
from ....types.system.outreach.attempt_complete_outreach_attempt_response import AttemptCompleteOutreachAttemptResponse

__all__ = ["AttemptResource", "AsyncAttemptResource"]


class AttemptResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AttemptResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AttemptResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AttemptResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AttemptResourceWithStreamingResponse(self)

    @overload
    def complete_outreach_attempt(
        self,
        attempt_id: int,
        *,
        tenant_db_name: str,
        type: Literal["PHONE_CALL"],
        duration_seconds: Optional[int] | Omit = omit,
        transcript_url: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCompleteOutreachAttemptResponse:
        """
        Complete an outreach attempt

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def complete_outreach_attempt(
        self,
        attempt_id: int,
        *,
        tenant_db_name: str,
        type: Literal["SMS"],
        message: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCompleteOutreachAttemptResponse:
        """
        Complete an outreach attempt

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["tenant_db_name", "type"])
    def complete_outreach_attempt(
        self,
        attempt_id: int,
        *,
        tenant_db_name: str,
        type: Literal["PHONE_CALL"] | Literal["SMS"],
        duration_seconds: Optional[int] | Omit = omit,
        transcript_url: Optional[str] | Omit = omit,
        message: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCompleteOutreachAttemptResponse:
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return cast(
            AttemptCompleteOutreachAttemptResponse,
            self._post(
                f"/system/{tenant_db_name}/outreach/attempt/{attempt_id}/complete",
                body=maybe_transform(
                    {
                        "type": type,
                        "duration_seconds": duration_seconds,
                        "transcript_url": transcript_url,
                        "message": message,
                    },
                    attempt_complete_outreach_attempt_params.AttemptCompleteOutreachAttemptParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, AttemptCompleteOutreachAttemptResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncAttemptResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAttemptResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAttemptResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAttemptResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncAttemptResourceWithStreamingResponse(self)

    @overload
    async def complete_outreach_attempt(
        self,
        attempt_id: int,
        *,
        tenant_db_name: str,
        type: Literal["PHONE_CALL"],
        duration_seconds: Optional[int] | Omit = omit,
        transcript_url: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCompleteOutreachAttemptResponse:
        """
        Complete an outreach attempt

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def complete_outreach_attempt(
        self,
        attempt_id: int,
        *,
        tenant_db_name: str,
        type: Literal["SMS"],
        message: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCompleteOutreachAttemptResponse:
        """
        Complete an outreach attempt

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["tenant_db_name", "type"])
    async def complete_outreach_attempt(
        self,
        attempt_id: int,
        *,
        tenant_db_name: str,
        type: Literal["PHONE_CALL"] | Literal["SMS"],
        duration_seconds: Optional[int] | Omit = omit,
        transcript_url: Optional[str] | Omit = omit,
        message: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCompleteOutreachAttemptResponse:
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return cast(
            AttemptCompleteOutreachAttemptResponse,
            await self._post(
                f"/system/{tenant_db_name}/outreach/attempt/{attempt_id}/complete",
                body=await async_maybe_transform(
                    {
                        "type": type,
                        "duration_seconds": duration_seconds,
                        "transcript_url": transcript_url,
                        "message": message,
                    },
                    attempt_complete_outreach_attempt_params.AttemptCompleteOutreachAttemptParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, AttemptCompleteOutreachAttemptResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AttemptResourceWithRawResponse:
    def __init__(self, attempt: AttemptResource) -> None:
        self._attempt = attempt

        self.complete_outreach_attempt = to_raw_response_wrapper(
            attempt.complete_outreach_attempt,
        )


class AsyncAttemptResourceWithRawResponse:
    def __init__(self, attempt: AsyncAttemptResource) -> None:
        self._attempt = attempt

        self.complete_outreach_attempt = async_to_raw_response_wrapper(
            attempt.complete_outreach_attempt,
        )


class AttemptResourceWithStreamingResponse:
    def __init__(self, attempt: AttemptResource) -> None:
        self._attempt = attempt

        self.complete_outreach_attempt = to_streamed_response_wrapper(
            attempt.complete_outreach_attempt,
        )


class AsyncAttemptResourceWithStreamingResponse:
    def __init__(self, attempt: AsyncAttemptResource) -> None:
        self._attempt = attempt

        self.complete_outreach_attempt = async_to_streamed_response_wrapper(
            attempt.complete_outreach_attempt,
        )
