# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.outreach.campaigns import PatientListResponse, PatientRetrieveAttemptsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPatients:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        patient = client.outreach.campaigns.patients.list(
            0,
        )
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.campaigns.patients.with_raw_response.list(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.campaigns.patients.with_streaming_response.list(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientListResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_attempts(self, client: WebRecruitmentSDK) -> None:
        patient = client.outreach.campaigns.patients.retrieve_attempts(
            patient_id="patient_id",
            campaign_id=0,
        )
        assert_matches_type(PatientRetrieveAttemptsResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_attempts(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.campaigns.patients.with_raw_response.retrieve_attempts(
            patient_id="patient_id",
            campaign_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientRetrieveAttemptsResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_attempts(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.campaigns.patients.with_streaming_response.retrieve_attempts(
            patient_id="patient_id",
            campaign_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientRetrieveAttemptsResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_attempts(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `patient_id` but received ''"):
            client.outreach.campaigns.patients.with_raw_response.retrieve_attempts(
                patient_id="",
                campaign_id=0,
            )


class TestAsyncPatients:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.outreach.campaigns.patients.list(
            0,
        )
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.campaigns.patients.with_raw_response.list(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.campaigns.patients.with_streaming_response.list(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientListResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_attempts(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.outreach.campaigns.patients.retrieve_attempts(
            patient_id="patient_id",
            campaign_id=0,
        )
        assert_matches_type(PatientRetrieveAttemptsResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_attempts(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.campaigns.patients.with_raw_response.retrieve_attempts(
            patient_id="patient_id",
            campaign_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientRetrieveAttemptsResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_attempts(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.campaigns.patients.with_streaming_response.retrieve_attempts(
            patient_id="patient_id",
            campaign_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientRetrieveAttemptsResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_attempts(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `patient_id` but received ''"):
            await async_client.outreach.campaigns.patients.with_raw_response.retrieve_attempts(
                patient_id="",
                campaign_id=0,
            )
