# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.outreach.sites import (
    OutreachCreateResponse,
    OutreachUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOutreach:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        outreach = client.outreach.sites.outreach.create(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        )
        assert_matches_type(OutreachCreateResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.sites.outreach.with_raw_response.create(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        outreach = response.parse()
        assert_matches_type(OutreachCreateResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.sites.outreach.with_streaming_response.create(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            outreach = response.parse()
            assert_matches_type(OutreachCreateResponse, outreach, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        outreach = client.outreach.sites.outreach.update(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        )
        assert_matches_type(OutreachUpdateResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.sites.outreach.with_raw_response.update(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        outreach = response.parse()
        assert_matches_type(OutreachUpdateResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.sites.outreach.with_streaming_response.update(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            outreach = response.parse()
            assert_matches_type(OutreachUpdateResponse, outreach, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOutreach:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        outreach = await async_client.outreach.sites.outreach.create(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        )
        assert_matches_type(OutreachCreateResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.sites.outreach.with_raw_response.create(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        outreach = await response.parse()
        assert_matches_type(OutreachCreateResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.sites.outreach.with_streaming_response.create(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            outreach = await response.parse()
            assert_matches_type(OutreachCreateResponse, outreach, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        outreach = await async_client.outreach.sites.outreach.update(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        )
        assert_matches_type(OutreachUpdateResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.sites.outreach.with_raw_response.update(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        outreach = await response.parse()
        assert_matches_type(OutreachUpdateResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.sites.outreach.with_streaming_response.update(
            site_id=0,
            outbound_phone_number="outboundPhoneNumber",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            outreach = await response.parse()
            assert_matches_type(OutreachUpdateResponse, outreach, path=["response"])

        assert cast(Any, response.is_closed) is True
