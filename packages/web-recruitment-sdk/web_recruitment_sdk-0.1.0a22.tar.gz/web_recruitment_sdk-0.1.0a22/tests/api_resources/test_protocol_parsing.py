# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import (
    ProtocolRead,
    ProtocolParsingGetStatusesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProtocolParsing:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_statuses(self, client: WebRecruitmentSDK) -> None:
        protocol_parsing = client.protocol_parsing.get_statuses()
        assert_matches_type(ProtocolParsingGetStatusesResponse, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_statuses_with_all_params(self, client: WebRecruitmentSDK) -> None:
        protocol_parsing = client.protocol_parsing.get_statuses(
            limit=1,
            offset=0,
        )
        assert_matches_type(ProtocolParsingGetStatusesResponse, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_statuses(self, client: WebRecruitmentSDK) -> None:
        response = client.protocol_parsing.with_raw_response.get_statuses()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol_parsing = response.parse()
        assert_matches_type(ProtocolParsingGetStatusesResponse, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_statuses(self, client: WebRecruitmentSDK) -> None:
        with client.protocol_parsing.with_streaming_response.get_statuses() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol_parsing = response.parse()
            assert_matches_type(ProtocolParsingGetStatusesResponse, protocol_parsing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload(self, client: WebRecruitmentSDK) -> None:
        protocol_parsing = client.protocol_parsing.upload(
            file=b"raw file contents",
            title="title",
        )
        assert_matches_type(ProtocolRead, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_with_all_params(self, client: WebRecruitmentSDK) -> None:
        protocol_parsing = client.protocol_parsing.upload(
            file=b"raw file contents",
            title="title",
            site_ids=[0],
        )
        assert_matches_type(ProtocolRead, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload(self, client: WebRecruitmentSDK) -> None:
        response = client.protocol_parsing.with_raw_response.upload(
            file=b"raw file contents",
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol_parsing = response.parse()
        assert_matches_type(ProtocolRead, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload(self, client: WebRecruitmentSDK) -> None:
        with client.protocol_parsing.with_streaming_response.upload(
            file=b"raw file contents",
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol_parsing = response.parse()
            assert_matches_type(ProtocolRead, protocol_parsing, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncProtocolParsing:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_statuses(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol_parsing = await async_client.protocol_parsing.get_statuses()
        assert_matches_type(ProtocolParsingGetStatusesResponse, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_statuses_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol_parsing = await async_client.protocol_parsing.get_statuses(
            limit=1,
            offset=0,
        )
        assert_matches_type(ProtocolParsingGetStatusesResponse, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_statuses(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocol_parsing.with_raw_response.get_statuses()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol_parsing = await response.parse()
        assert_matches_type(ProtocolParsingGetStatusesResponse, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_statuses(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocol_parsing.with_streaming_response.get_statuses() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol_parsing = await response.parse()
            assert_matches_type(ProtocolParsingGetStatusesResponse, protocol_parsing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol_parsing = await async_client.protocol_parsing.upload(
            file=b"raw file contents",
            title="title",
        )
        assert_matches_type(ProtocolRead, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol_parsing = await async_client.protocol_parsing.upload(
            file=b"raw file contents",
            title="title",
            site_ids=[0],
        )
        assert_matches_type(ProtocolRead, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocol_parsing.with_raw_response.upload(
            file=b"raw file contents",
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol_parsing = await response.parse()
        assert_matches_type(ProtocolRead, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocol_parsing.with_streaming_response.upload(
            file=b"raw file contents",
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol_parsing = await response.parse()
            assert_matches_type(ProtocolRead, protocol_parsing, path=["response"])

        assert cast(Any, response.is_closed) is True
