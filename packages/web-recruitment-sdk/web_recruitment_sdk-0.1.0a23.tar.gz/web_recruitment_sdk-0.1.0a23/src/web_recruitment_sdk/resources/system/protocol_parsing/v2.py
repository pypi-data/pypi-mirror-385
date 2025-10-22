# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from ....types.system.protocol_parsing import v2_update_protocol_success_params

__all__ = ["V2Resource", "AsyncV2Resource"]


class V2Resource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> V2ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return V2ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> V2ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return V2ResourceWithStreamingResponse(self)

    def update_protocol_success(
        self,
        job_id: str,
        *,
        path_tenant_db_name: str,
        criteria_create_with_protocol_metadata: Iterable[
            v2_update_protocol_success_params.CriteriaCreateWithProtocolMetadata
        ],
        external_protocol_id: str,
        task_id: int,
        task_name: str,
        body_tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Update Protocol With V2 Parsed Criteria And Set Success

        Args:
          task_id: The ID of the task as it exists in the database

          task_name: The name of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_tenant_db_name:
            raise ValueError(
                f"Expected a non-empty value for `path_tenant_db_name` but received {path_tenant_db_name!r}"
            )
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._post(
            f"/system/{path_tenant_db_name}/protocol-parsing-v2/{job_id}/success",
            body=maybe_transform(
                {
                    "criteria_create_with_protocol_metadata": criteria_create_with_protocol_metadata,
                    "external_protocol_id": external_protocol_id,
                    "task_id": task_id,
                    "task_name": task_name,
                    "body_tenant_db_name": body_tenant_db_name,
                },
                v2_update_protocol_success_params.V2UpdateProtocolSuccessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncV2Resource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncV2ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncV2ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncV2ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncV2ResourceWithStreamingResponse(self)

    async def update_protocol_success(
        self,
        job_id: str,
        *,
        path_tenant_db_name: str,
        criteria_create_with_protocol_metadata: Iterable[
            v2_update_protocol_success_params.CriteriaCreateWithProtocolMetadata
        ],
        external_protocol_id: str,
        task_id: int,
        task_name: str,
        body_tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Update Protocol With V2 Parsed Criteria And Set Success

        Args:
          task_id: The ID of the task as it exists in the database

          task_name: The name of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_tenant_db_name:
            raise ValueError(
                f"Expected a non-empty value for `path_tenant_db_name` but received {path_tenant_db_name!r}"
            )
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._post(
            f"/system/{path_tenant_db_name}/protocol-parsing-v2/{job_id}/success",
            body=await async_maybe_transform(
                {
                    "criteria_create_with_protocol_metadata": criteria_create_with_protocol_metadata,
                    "external_protocol_id": external_protocol_id,
                    "task_id": task_id,
                    "task_name": task_name,
                    "body_tenant_db_name": body_tenant_db_name,
                },
                v2_update_protocol_success_params.V2UpdateProtocolSuccessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class V2ResourceWithRawResponse:
    def __init__(self, v2: V2Resource) -> None:
        self._v2 = v2

        self.update_protocol_success = to_raw_response_wrapper(
            v2.update_protocol_success,
        )


class AsyncV2ResourceWithRawResponse:
    def __init__(self, v2: AsyncV2Resource) -> None:
        self._v2 = v2

        self.update_protocol_success = async_to_raw_response_wrapper(
            v2.update_protocol_success,
        )


class V2ResourceWithStreamingResponse:
    def __init__(self, v2: V2Resource) -> None:
        self._v2 = v2

        self.update_protocol_success = to_streamed_response_wrapper(
            v2.update_protocol_success,
        )


class AsyncV2ResourceWithStreamingResponse:
    def __init__(self, v2: AsyncV2Resource) -> None:
        self._v2 = v2

        self.update_protocol_success = async_to_streamed_response_wrapper(
            v2.update_protocol_success,
        )
