# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...types import crio_list_sites_params
from .clients import (
    ClientsResource,
    AsyncClientsResource,
    ClientsResourceWithRawResponse,
    AsyncClientsResourceWithRawResponse,
    ClientsResourceWithStreamingResponse,
    AsyncClientsResourceWithStreamingResponse,
)
from ..._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
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
from ...types.crio_list_sites_response import CrioListSitesResponse

__all__ = ["CrioResource", "AsyncCrioResource"]


class CrioResource(SyncAPIResource):
    @cached_property
    def clients(self) -> ClientsResource:
        return ClientsResource(self._client)

    @cached_property
    def with_raw_response(self) -> CrioResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return CrioResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CrioResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return CrioResourceWithStreamingResponse(self)

    def list_sites(
        self,
        *,
        client_ids: SequenceNotStr[str] | Omit = omit,
        tenant_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CrioListSitesResponse:
        """
        Get CRIO sites with their associated studies and referral sources.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/crio/sites",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "client_ids": client_ids,
                        "tenant_id": tenant_id,
                    },
                    crio_list_sites_params.CrioListSitesParams,
                ),
            ),
            cast_to=CrioListSitesResponse,
        )


class AsyncCrioResource(AsyncAPIResource):
    @cached_property
    def clients(self) -> AsyncClientsResource:
        return AsyncClientsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCrioResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCrioResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCrioResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncCrioResourceWithStreamingResponse(self)

    async def list_sites(
        self,
        *,
        client_ids: SequenceNotStr[str] | Omit = omit,
        tenant_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CrioListSitesResponse:
        """
        Get CRIO sites with their associated studies and referral sources.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/crio/sites",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "client_ids": client_ids,
                        "tenant_id": tenant_id,
                    },
                    crio_list_sites_params.CrioListSitesParams,
                ),
            ),
            cast_to=CrioListSitesResponse,
        )


class CrioResourceWithRawResponse:
    def __init__(self, crio: CrioResource) -> None:
        self._crio = crio

        self.list_sites = to_raw_response_wrapper(
            crio.list_sites,
        )

    @cached_property
    def clients(self) -> ClientsResourceWithRawResponse:
        return ClientsResourceWithRawResponse(self._crio.clients)


class AsyncCrioResourceWithRawResponse:
    def __init__(self, crio: AsyncCrioResource) -> None:
        self._crio = crio

        self.list_sites = async_to_raw_response_wrapper(
            crio.list_sites,
        )

    @cached_property
    def clients(self) -> AsyncClientsResourceWithRawResponse:
        return AsyncClientsResourceWithRawResponse(self._crio.clients)


class CrioResourceWithStreamingResponse:
    def __init__(self, crio: CrioResource) -> None:
        self._crio = crio

        self.list_sites = to_streamed_response_wrapper(
            crio.list_sites,
        )

    @cached_property
    def clients(self) -> ClientsResourceWithStreamingResponse:
        return ClientsResourceWithStreamingResponse(self._crio.clients)


class AsyncCrioResourceWithStreamingResponse:
    def __init__(self, crio: AsyncCrioResource) -> None:
        self._crio = crio

        self.list_sites = async_to_streamed_response_wrapper(
            crio.list_sites,
        )

    @cached_property
    def clients(self) -> AsyncClientsResourceWithStreamingResponse:
        return AsyncClientsResourceWithStreamingResponse(self._crio.clients)
