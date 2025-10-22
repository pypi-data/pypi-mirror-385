# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .task import (
    TaskResource,
    AsyncTaskResource,
    TaskResourceWithRawResponse,
    AsyncTaskResourceWithRawResponse,
    TaskResourceWithStreamingResponse,
    AsyncTaskResourceWithStreamingResponse,
)
from .attempt import (
    AttemptResource,
    AsyncAttemptResource,
    AttemptResourceWithRawResponse,
    AsyncAttemptResourceWithRawResponse,
    AttemptResourceWithStreamingResponse,
    AsyncAttemptResourceWithStreamingResponse,
)
from .attempts import (
    AttemptsResource,
    AsyncAttemptsResource,
    AttemptsResourceWithRawResponse,
    AsyncAttemptsResourceWithRawResponse,
    AttemptsResourceWithStreamingResponse,
    AsyncAttemptsResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["OutreachResource", "AsyncOutreachResource"]


class OutreachResource(SyncAPIResource):
    @cached_property
    def task(self) -> TaskResource:
        return TaskResource(self._client)

    @cached_property
    def attempts(self) -> AttemptsResource:
        return AttemptsResource(self._client)

    @cached_property
    def attempt(self) -> AttemptResource:
        return AttemptResource(self._client)

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


class AsyncOutreachResource(AsyncAPIResource):
    @cached_property
    def task(self) -> AsyncTaskResource:
        return AsyncTaskResource(self._client)

    @cached_property
    def attempts(self) -> AsyncAttemptsResource:
        return AsyncAttemptsResource(self._client)

    @cached_property
    def attempt(self) -> AsyncAttemptResource:
        return AsyncAttemptResource(self._client)

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


class OutreachResourceWithRawResponse:
    def __init__(self, outreach: OutreachResource) -> None:
        self._outreach = outreach

    @cached_property
    def task(self) -> TaskResourceWithRawResponse:
        return TaskResourceWithRawResponse(self._outreach.task)

    @cached_property
    def attempts(self) -> AttemptsResourceWithRawResponse:
        return AttemptsResourceWithRawResponse(self._outreach.attempts)

    @cached_property
    def attempt(self) -> AttemptResourceWithRawResponse:
        return AttemptResourceWithRawResponse(self._outreach.attempt)


class AsyncOutreachResourceWithRawResponse:
    def __init__(self, outreach: AsyncOutreachResource) -> None:
        self._outreach = outreach

    @cached_property
    def task(self) -> AsyncTaskResourceWithRawResponse:
        return AsyncTaskResourceWithRawResponse(self._outreach.task)

    @cached_property
    def attempts(self) -> AsyncAttemptsResourceWithRawResponse:
        return AsyncAttemptsResourceWithRawResponse(self._outreach.attempts)

    @cached_property
    def attempt(self) -> AsyncAttemptResourceWithRawResponse:
        return AsyncAttemptResourceWithRawResponse(self._outreach.attempt)


class OutreachResourceWithStreamingResponse:
    def __init__(self, outreach: OutreachResource) -> None:
        self._outreach = outreach

    @cached_property
    def task(self) -> TaskResourceWithStreamingResponse:
        return TaskResourceWithStreamingResponse(self._outreach.task)

    @cached_property
    def attempts(self) -> AttemptsResourceWithStreamingResponse:
        return AttemptsResourceWithStreamingResponse(self._outreach.attempts)

    @cached_property
    def attempt(self) -> AttemptResourceWithStreamingResponse:
        return AttemptResourceWithStreamingResponse(self._outreach.attempt)


class AsyncOutreachResourceWithStreamingResponse:
    def __init__(self, outreach: AsyncOutreachResource) -> None:
        self._outreach = outreach

    @cached_property
    def task(self) -> AsyncTaskResourceWithStreamingResponse:
        return AsyncTaskResourceWithStreamingResponse(self._outreach.task)

    @cached_property
    def attempts(self) -> AsyncAttemptsResourceWithStreamingResponse:
        return AsyncAttemptsResourceWithStreamingResponse(self._outreach.attempts)

    @cached_property
    def attempt(self) -> AsyncAttemptResourceWithStreamingResponse:
        return AsyncAttemptResourceWithStreamingResponse(self._outreach.attempt)
