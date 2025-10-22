# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.outreach import PatientCampaignCancelResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPatientCampaigns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cancel(self, client: WebRecruitmentSDK) -> None:
        patient_campaign = client.outreach.patient_campaigns.cancel(
            0,
        )
        assert_matches_type(PatientCampaignCancelResponse, patient_campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cancel(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.patient_campaigns.with_raw_response.cancel(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient_campaign = response.parse()
        assert_matches_type(PatientCampaignCancelResponse, patient_campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cancel(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.patient_campaigns.with_streaming_response.cancel(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient_campaign = response.parse()
            assert_matches_type(PatientCampaignCancelResponse, patient_campaign, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPatientCampaigns:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cancel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient_campaign = await async_client.outreach.patient_campaigns.cancel(
            0,
        )
        assert_matches_type(PatientCampaignCancelResponse, patient_campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.patient_campaigns.with_raw_response.cancel(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient_campaign = await response.parse()
        assert_matches_type(PatientCampaignCancelResponse, patient_campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.patient_campaigns.with_streaming_response.cancel(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient_campaign = await response.parse()
            assert_matches_type(PatientCampaignCancelResponse, patient_campaign, path=["response"])

        assert cast(Any, response.is_closed) is True
