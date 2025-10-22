# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import CriteriaType, criterion_create_params, criterion_update_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.criteria_type import CriteriaType
from ..types.custom_searches import CriteriaStatus
from ..types.custom_searches.criteria_read import CriteriaRead
from ..types.custom_searches.criteria_status import CriteriaStatus

__all__ = ["CriteriaResource", "AsyncCriteriaResource"]


class CriteriaResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CriteriaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return CriteriaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CriteriaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return CriteriaResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        summary: str,
        type: CriteriaType,
        criteria_protocol_metadata_id: Optional[int] | Omit = omit,
        custom_search_id: Optional[int] | Omit = omit,
        description: Optional[str] | Omit = omit,
        matching_payload: Optional[criterion_create_params.MatchingPayload] | Omit = omit,
        protocol_id: Optional[int] | Omit = omit,
        status: CriteriaStatus | Omit = omit,
        user_raw_input: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CriteriaRead:
        """
        Create Criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/criteria",
            body=maybe_transform(
                {
                    "summary": summary,
                    "type": type,
                    "criteria_protocol_metadata_id": criteria_protocol_metadata_id,
                    "custom_search_id": custom_search_id,
                    "description": description,
                    "matching_payload": matching_payload,
                    "protocol_id": protocol_id,
                    "status": status,
                    "user_raw_input": user_raw_input,
                },
                criterion_create_params.CriterionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaRead,
        )

    def retrieve(
        self,
        criteria_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CriteriaRead:
        """
        Get Criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/criteria/{criteria_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaRead,
        )

    def update(
        self,
        criterion_id: int,
        *,
        criteria_protocol_metadata_id: Optional[int] | Omit = omit,
        description: Optional[str] | Omit = omit,
        status: Optional[CriteriaStatus] | Omit = omit,
        summary: Optional[str] | Omit = omit,
        user_raw_input: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CriteriaRead:
        """
        Update Protocol Criteria

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            f"/criteria/{criterion_id}",
            body=maybe_transform(
                {
                    "criteria_protocol_metadata_id": criteria_protocol_metadata_id,
                    "description": description,
                    "status": status,
                    "summary": summary,
                    "user_raw_input": user_raw_input,
                },
                criterion_update_params.CriterionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaRead,
        )


class AsyncCriteriaResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCriteriaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCriteriaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCriteriaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncCriteriaResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        summary: str,
        type: CriteriaType,
        criteria_protocol_metadata_id: Optional[int] | Omit = omit,
        custom_search_id: Optional[int] | Omit = omit,
        description: Optional[str] | Omit = omit,
        matching_payload: Optional[criterion_create_params.MatchingPayload] | Omit = omit,
        protocol_id: Optional[int] | Omit = omit,
        status: CriteriaStatus | Omit = omit,
        user_raw_input: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CriteriaRead:
        """
        Create Criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/criteria",
            body=await async_maybe_transform(
                {
                    "summary": summary,
                    "type": type,
                    "criteria_protocol_metadata_id": criteria_protocol_metadata_id,
                    "custom_search_id": custom_search_id,
                    "description": description,
                    "matching_payload": matching_payload,
                    "protocol_id": protocol_id,
                    "status": status,
                    "user_raw_input": user_raw_input,
                },
                criterion_create_params.CriterionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaRead,
        )

    async def retrieve(
        self,
        criteria_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CriteriaRead:
        """
        Get Criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/criteria/{criteria_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaRead,
        )

    async def update(
        self,
        criterion_id: int,
        *,
        criteria_protocol_metadata_id: Optional[int] | Omit = omit,
        description: Optional[str] | Omit = omit,
        status: Optional[CriteriaStatus] | Omit = omit,
        summary: Optional[str] | Omit = omit,
        user_raw_input: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CriteriaRead:
        """
        Update Protocol Criteria

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            f"/criteria/{criterion_id}",
            body=await async_maybe_transform(
                {
                    "criteria_protocol_metadata_id": criteria_protocol_metadata_id,
                    "description": description,
                    "status": status,
                    "summary": summary,
                    "user_raw_input": user_raw_input,
                },
                criterion_update_params.CriterionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaRead,
        )


class CriteriaResourceWithRawResponse:
    def __init__(self, criteria: CriteriaResource) -> None:
        self._criteria = criteria

        self.create = to_raw_response_wrapper(
            criteria.create,
        )
        self.retrieve = to_raw_response_wrapper(
            criteria.retrieve,
        )
        self.update = to_raw_response_wrapper(
            criteria.update,
        )


class AsyncCriteriaResourceWithRawResponse:
    def __init__(self, criteria: AsyncCriteriaResource) -> None:
        self._criteria = criteria

        self.create = async_to_raw_response_wrapper(
            criteria.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            criteria.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            criteria.update,
        )


class CriteriaResourceWithStreamingResponse:
    def __init__(self, criteria: CriteriaResource) -> None:
        self._criteria = criteria

        self.create = to_streamed_response_wrapper(
            criteria.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            criteria.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            criteria.update,
        )


class AsyncCriteriaResourceWithStreamingResponse:
    def __init__(self, criteria: AsyncCriteriaResource) -> None:
        self._criteria = criteria

        self.create = async_to_streamed_response_wrapper(
            criteria.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            criteria.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            criteria.update,
        )
