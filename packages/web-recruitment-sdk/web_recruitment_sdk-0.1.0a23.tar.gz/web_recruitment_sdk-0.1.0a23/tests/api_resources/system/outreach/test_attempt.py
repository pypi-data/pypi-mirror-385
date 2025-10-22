# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.system.outreach import (
    AttemptCompleteOutreachAttemptResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAttempt:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_complete_outreach_attempt_overload_1(self, client: WebRecruitmentSDK) -> None:
        attempt = client.system.outreach.attempt.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="PHONE_CALL",
        )
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_complete_outreach_attempt_with_all_params_overload_1(self, client: WebRecruitmentSDK) -> None:
        attempt = client.system.outreach.attempt.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="PHONE_CALL",
            duration_seconds=0,
            transcript_url="transcriptUrl",
        )
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_complete_outreach_attempt_overload_1(self, client: WebRecruitmentSDK) -> None:
        response = client.system.outreach.attempt.with_raw_response.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="PHONE_CALL",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        attempt = response.parse()
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_complete_outreach_attempt_overload_1(self, client: WebRecruitmentSDK) -> None:
        with client.system.outreach.attempt.with_streaming_response.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="PHONE_CALL",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            attempt = response.parse()
            assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_complete_outreach_attempt_overload_1(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.outreach.attempt.with_raw_response.complete_outreach_attempt(
                attempt_id=0,
                tenant_db_name="",
                type="PHONE_CALL",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_complete_outreach_attempt_overload_2(self, client: WebRecruitmentSDK) -> None:
        attempt = client.system.outreach.attempt.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="SMS",
        )
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_complete_outreach_attempt_with_all_params_overload_2(self, client: WebRecruitmentSDK) -> None:
        attempt = client.system.outreach.attempt.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="SMS",
            message="message",
        )
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_complete_outreach_attempt_overload_2(self, client: WebRecruitmentSDK) -> None:
        response = client.system.outreach.attempt.with_raw_response.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="SMS",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        attempt = response.parse()
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_complete_outreach_attempt_overload_2(self, client: WebRecruitmentSDK) -> None:
        with client.system.outreach.attempt.with_streaming_response.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="SMS",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            attempt = response.parse()
            assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_complete_outreach_attempt_overload_2(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.outreach.attempt.with_raw_response.complete_outreach_attempt(
                attempt_id=0,
                tenant_db_name="",
                type="SMS",
            )


class TestAsyncAttempt:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_complete_outreach_attempt_overload_1(self, async_client: AsyncWebRecruitmentSDK) -> None:
        attempt = await async_client.system.outreach.attempt.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="PHONE_CALL",
        )
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_complete_outreach_attempt_with_all_params_overload_1(
        self, async_client: AsyncWebRecruitmentSDK
    ) -> None:
        attempt = await async_client.system.outreach.attempt.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="PHONE_CALL",
            duration_seconds=0,
            transcript_url="transcriptUrl",
        )
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_complete_outreach_attempt_overload_1(
        self, async_client: AsyncWebRecruitmentSDK
    ) -> None:
        response = await async_client.system.outreach.attempt.with_raw_response.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="PHONE_CALL",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        attempt = await response.parse()
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_complete_outreach_attempt_overload_1(
        self, async_client: AsyncWebRecruitmentSDK
    ) -> None:
        async with async_client.system.outreach.attempt.with_streaming_response.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="PHONE_CALL",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            attempt = await response.parse()
            assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_complete_outreach_attempt_overload_1(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.outreach.attempt.with_raw_response.complete_outreach_attempt(
                attempt_id=0,
                tenant_db_name="",
                type="PHONE_CALL",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_complete_outreach_attempt_overload_2(self, async_client: AsyncWebRecruitmentSDK) -> None:
        attempt = await async_client.system.outreach.attempt.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="SMS",
        )
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_complete_outreach_attempt_with_all_params_overload_2(
        self, async_client: AsyncWebRecruitmentSDK
    ) -> None:
        attempt = await async_client.system.outreach.attempt.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="SMS",
            message="message",
        )
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_complete_outreach_attempt_overload_2(
        self, async_client: AsyncWebRecruitmentSDK
    ) -> None:
        response = await async_client.system.outreach.attempt.with_raw_response.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="SMS",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        attempt = await response.parse()
        assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_complete_outreach_attempt_overload_2(
        self, async_client: AsyncWebRecruitmentSDK
    ) -> None:
        async with async_client.system.outreach.attempt.with_streaming_response.complete_outreach_attempt(
            attempt_id=0,
            tenant_db_name="tenant_db_name",
            type="SMS",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            attempt = await response.parse()
            assert_matches_type(AttemptCompleteOutreachAttemptResponse, attempt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_complete_outreach_attempt_overload_2(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.outreach.attempt.with_raw_response.complete_outreach_attempt(
                attempt_id=0,
                tenant_db_name="",
                type="SMS",
            )
