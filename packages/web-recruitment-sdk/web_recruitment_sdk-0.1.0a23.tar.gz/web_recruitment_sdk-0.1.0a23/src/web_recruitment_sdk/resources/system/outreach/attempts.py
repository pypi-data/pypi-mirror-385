# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, cast
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
from ....types.system.outreach import attempt_create_outreach_action_params
from ....types.system.outreach.attempt_create_outreach_action_response import AttemptCreateOutreachActionResponse

__all__ = ["AttemptsResource", "AsyncAttemptsResource"]


class AttemptsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AttemptsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AttemptsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AttemptsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AttemptsResourceWithStreamingResponse(self)

    @overload
    def create_outreach_action(
        self,
        path_attempt_id: int,
        *,
        tenant_db_name: str,
        body_attempt_id: int,
        status: Literal[
            "STARTED",
            "NO_ANSWER",
            "VOICEMAIL_LEFT",
            "WRONG_NUMBER",
            "HANGUP",
            "INTERESTED",
            "NOT_INTERESTED",
            "SCHEDULED",
            "DO_NOT_CALL",
            "ENDED",
        ],
        type: Literal["PHONE_CALL"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCreateOutreachActionResponse:
        """
        Create a new outreach action for an attempt

        Args:
          status: Status values specific to phone call actions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create_outreach_action(
        self,
        path_attempt_id: int,
        *,
        tenant_db_name: str,
        body_attempt_id: int,
        message: str,
        status: Literal[
            "SENT",
            "FAILED_TO_SEND",
            "REPLIED",
            "INTERESTED",
            "NOT_INTERESTED",
            "BOOKING_LINK_SENT",
            "SCHEDULED",
            "DO_NOT_CALL",
        ],
        type: Literal["SMS"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCreateOutreachActionResponse:
        """
        Create a new outreach action for an attempt

        Args:
          status: Status values specific to SMS actions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(
        ["tenant_db_name", "body_attempt_id", "status", "type"],
        ["tenant_db_name", "body_attempt_id", "message", "status", "type"],
    )
    def create_outreach_action(
        self,
        path_attempt_id: int,
        *,
        tenant_db_name: str,
        body_attempt_id: int,
        status: Literal[
            "STARTED",
            "NO_ANSWER",
            "VOICEMAIL_LEFT",
            "WRONG_NUMBER",
            "HANGUP",
            "INTERESTED",
            "NOT_INTERESTED",
            "SCHEDULED",
            "DO_NOT_CALL",
            "ENDED",
        ]
        | Literal[
            "SENT",
            "FAILED_TO_SEND",
            "REPLIED",
            "INTERESTED",
            "NOT_INTERESTED",
            "BOOKING_LINK_SENT",
            "SCHEDULED",
            "DO_NOT_CALL",
        ],
        type: Literal["PHONE_CALL"] | Literal["SMS"],
        message: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCreateOutreachActionResponse:
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return cast(
            AttemptCreateOutreachActionResponse,
            self._post(
                f"/system/{tenant_db_name}/outreach/attempts/{path_attempt_id}/actions",
                body=maybe_transform(
                    {
                        "body_attempt_id": body_attempt_id,
                        "status": status,
                        "type": type,
                        "message": message,
                    },
                    attempt_create_outreach_action_params.AttemptCreateOutreachActionParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, AttemptCreateOutreachActionResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncAttemptsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAttemptsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAttemptsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAttemptsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncAttemptsResourceWithStreamingResponse(self)

    @overload
    async def create_outreach_action(
        self,
        path_attempt_id: int,
        *,
        tenant_db_name: str,
        body_attempt_id: int,
        status: Literal[
            "STARTED",
            "NO_ANSWER",
            "VOICEMAIL_LEFT",
            "WRONG_NUMBER",
            "HANGUP",
            "INTERESTED",
            "NOT_INTERESTED",
            "SCHEDULED",
            "DO_NOT_CALL",
            "ENDED",
        ],
        type: Literal["PHONE_CALL"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCreateOutreachActionResponse:
        """
        Create a new outreach action for an attempt

        Args:
          status: Status values specific to phone call actions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create_outreach_action(
        self,
        path_attempt_id: int,
        *,
        tenant_db_name: str,
        body_attempt_id: int,
        message: str,
        status: Literal[
            "SENT",
            "FAILED_TO_SEND",
            "REPLIED",
            "INTERESTED",
            "NOT_INTERESTED",
            "BOOKING_LINK_SENT",
            "SCHEDULED",
            "DO_NOT_CALL",
        ],
        type: Literal["SMS"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCreateOutreachActionResponse:
        """
        Create a new outreach action for an attempt

        Args:
          status: Status values specific to SMS actions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(
        ["tenant_db_name", "body_attempt_id", "status", "type"],
        ["tenant_db_name", "body_attempt_id", "message", "status", "type"],
    )
    async def create_outreach_action(
        self,
        path_attempt_id: int,
        *,
        tenant_db_name: str,
        body_attempt_id: int,
        status: Literal[
            "STARTED",
            "NO_ANSWER",
            "VOICEMAIL_LEFT",
            "WRONG_NUMBER",
            "HANGUP",
            "INTERESTED",
            "NOT_INTERESTED",
            "SCHEDULED",
            "DO_NOT_CALL",
            "ENDED",
        ]
        | Literal[
            "SENT",
            "FAILED_TO_SEND",
            "REPLIED",
            "INTERESTED",
            "NOT_INTERESTED",
            "BOOKING_LINK_SENT",
            "SCHEDULED",
            "DO_NOT_CALL",
        ],
        type: Literal["PHONE_CALL"] | Literal["SMS"],
        message: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttemptCreateOutreachActionResponse:
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return cast(
            AttemptCreateOutreachActionResponse,
            await self._post(
                f"/system/{tenant_db_name}/outreach/attempts/{path_attempt_id}/actions",
                body=await async_maybe_transform(
                    {
                        "body_attempt_id": body_attempt_id,
                        "status": status,
                        "type": type,
                        "message": message,
                    },
                    attempt_create_outreach_action_params.AttemptCreateOutreachActionParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, AttemptCreateOutreachActionResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AttemptsResourceWithRawResponse:
    def __init__(self, attempts: AttemptsResource) -> None:
        self._attempts = attempts

        self.create_outreach_action = to_raw_response_wrapper(
            attempts.create_outreach_action,
        )


class AsyncAttemptsResourceWithRawResponse:
    def __init__(self, attempts: AsyncAttemptsResource) -> None:
        self._attempts = attempts

        self.create_outreach_action = async_to_raw_response_wrapper(
            attempts.create_outreach_action,
        )


class AttemptsResourceWithStreamingResponse:
    def __init__(self, attempts: AttemptsResource) -> None:
        self._attempts = attempts

        self.create_outreach_action = to_streamed_response_wrapper(
            attempts.create_outreach_action,
        )


class AsyncAttemptsResourceWithStreamingResponse:
    def __init__(self, attempts: AsyncAttemptsResource) -> None:
        self._attempts = attempts

        self.create_outreach_action = async_to_streamed_response_wrapper(
            attempts.create_outreach_action,
        )
