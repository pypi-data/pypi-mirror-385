# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import CriteriaType, custom_criterion_list_params
from .._types import Body, Query, Headers, NotGiven, not_given
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
from ..types.custom_criterion_list_response import CustomCriterionListResponse

__all__ = ["CustomCriteriaResource", "AsyncCustomCriteriaResource"]


class CustomCriteriaResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CustomCriteriaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return CustomCriteriaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CustomCriteriaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return CustomCriteriaResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        criterion_type: CriteriaType,
        free_text: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomCriterionListResponse:
        """
        Get custom criteria fields from free text

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/custom-criteria",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "criterion_type": criterion_type,
                        "free_text": free_text,
                    },
                    custom_criterion_list_params.CustomCriterionListParams,
                ),
            ),
            cast_to=CustomCriterionListResponse,
        )


class AsyncCustomCriteriaResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCustomCriteriaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCustomCriteriaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCustomCriteriaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncCustomCriteriaResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        criterion_type: CriteriaType,
        free_text: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomCriterionListResponse:
        """
        Get custom criteria fields from free text

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/custom-criteria",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "criterion_type": criterion_type,
                        "free_text": free_text,
                    },
                    custom_criterion_list_params.CustomCriterionListParams,
                ),
            ),
            cast_to=CustomCriterionListResponse,
        )


class CustomCriteriaResourceWithRawResponse:
    def __init__(self, custom_criteria: CustomCriteriaResource) -> None:
        self._custom_criteria = custom_criteria

        self.list = to_raw_response_wrapper(
            custom_criteria.list,
        )


class AsyncCustomCriteriaResourceWithRawResponse:
    def __init__(self, custom_criteria: AsyncCustomCriteriaResource) -> None:
        self._custom_criteria = custom_criteria

        self.list = async_to_raw_response_wrapper(
            custom_criteria.list,
        )


class CustomCriteriaResourceWithStreamingResponse:
    def __init__(self, custom_criteria: CustomCriteriaResource) -> None:
        self._custom_criteria = custom_criteria

        self.list = to_streamed_response_wrapper(
            custom_criteria.list,
        )


class AsyncCustomCriteriaResourceWithStreamingResponse:
    def __init__(self, custom_criteria: AsyncCustomCriteriaResource) -> None:
        self._custom_criteria = custom_criteria

        self.list = async_to_streamed_response_wrapper(
            custom_criteria.list,
        )
