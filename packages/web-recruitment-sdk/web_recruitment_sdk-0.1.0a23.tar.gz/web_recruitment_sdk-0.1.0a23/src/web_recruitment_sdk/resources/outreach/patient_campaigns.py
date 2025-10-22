# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import Body, Query, Headers, NotGiven, not_given
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.outreach.patient_campaign_cancel_response import PatientCampaignCancelResponse

__all__ = ["PatientCampaignsResource", "AsyncPatientCampaignsResource"]


class PatientCampaignsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PatientCampaignsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return PatientCampaignsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PatientCampaignsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return PatientCampaignsResourceWithStreamingResponse(self)

    def cancel(
        self,
        patient_campaign_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PatientCampaignCancelResponse:
        """
        Cancel a specific patient campaign, marking it as UNSUCCESSFUL and cancelling
        all active tasks

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            f"/outreach/patient-campaigns/{patient_campaign_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientCampaignCancelResponse,
        )


class AsyncPatientCampaignsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPatientCampaignsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncPatientCampaignsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPatientCampaignsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncPatientCampaignsResourceWithStreamingResponse(self)

    async def cancel(
        self,
        patient_campaign_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PatientCampaignCancelResponse:
        """
        Cancel a specific patient campaign, marking it as UNSUCCESSFUL and cancelling
        all active tasks

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            f"/outreach/patient-campaigns/{patient_campaign_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientCampaignCancelResponse,
        )


class PatientCampaignsResourceWithRawResponse:
    def __init__(self, patient_campaigns: PatientCampaignsResource) -> None:
        self._patient_campaigns = patient_campaigns

        self.cancel = to_raw_response_wrapper(
            patient_campaigns.cancel,
        )


class AsyncPatientCampaignsResourceWithRawResponse:
    def __init__(self, patient_campaigns: AsyncPatientCampaignsResource) -> None:
        self._patient_campaigns = patient_campaigns

        self.cancel = async_to_raw_response_wrapper(
            patient_campaigns.cancel,
        )


class PatientCampaignsResourceWithStreamingResponse:
    def __init__(self, patient_campaigns: PatientCampaignsResource) -> None:
        self._patient_campaigns = patient_campaigns

        self.cancel = to_streamed_response_wrapper(
            patient_campaigns.cancel,
        )


class AsyncPatientCampaignsResourceWithStreamingResponse:
    def __init__(self, patient_campaigns: AsyncPatientCampaignsResource) -> None:
        self._patient_campaigns = patient_campaigns

        self.cancel = async_to_streamed_response_wrapper(
            patient_campaigns.cancel,
        )
