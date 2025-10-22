# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .outreach import (
    OutreachResource,
    AsyncOutreachResource,
    OutreachResourceWithRawResponse,
    AsyncOutreachResourceWithRawResponse,
    OutreachResourceWithStreamingResponse,
    AsyncOutreachResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["SitesResource", "AsyncSitesResource"]


class SitesResource(SyncAPIResource):
    @cached_property
    def outreach(self) -> OutreachResource:
        return OutreachResource(self._client)

    @cached_property
    def with_raw_response(self) -> SitesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return SitesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SitesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return SitesResourceWithStreamingResponse(self)


class AsyncSitesResource(AsyncAPIResource):
    @cached_property
    def outreach(self) -> AsyncOutreachResource:
        return AsyncOutreachResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSitesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSitesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSitesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncSitesResourceWithStreamingResponse(self)


class SitesResourceWithRawResponse:
    def __init__(self, sites: SitesResource) -> None:
        self._sites = sites

    @cached_property
    def outreach(self) -> OutreachResourceWithRawResponse:
        return OutreachResourceWithRawResponse(self._sites.outreach)


class AsyncSitesResourceWithRawResponse:
    def __init__(self, sites: AsyncSitesResource) -> None:
        self._sites = sites

    @cached_property
    def outreach(self) -> AsyncOutreachResourceWithRawResponse:
        return AsyncOutreachResourceWithRawResponse(self._sites.outreach)


class SitesResourceWithStreamingResponse:
    def __init__(self, sites: SitesResource) -> None:
        self._sites = sites

    @cached_property
    def outreach(self) -> OutreachResourceWithStreamingResponse:
        return OutreachResourceWithStreamingResponse(self._sites.outreach)


class AsyncSitesResourceWithStreamingResponse:
    def __init__(self, sites: AsyncSitesResource) -> None:
        self._sites = sites

    @cached_property
    def outreach(self) -> AsyncOutreachResourceWithStreamingResponse:
        return AsyncOutreachResourceWithStreamingResponse(self._sites.outreach)
