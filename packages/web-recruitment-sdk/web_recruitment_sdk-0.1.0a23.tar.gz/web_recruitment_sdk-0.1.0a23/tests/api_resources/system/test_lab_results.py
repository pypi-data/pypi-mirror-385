# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.system import LabResultSearchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLabResults:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search(self, client: WebRecruitmentSDK) -> None:
        lab_result = client.system.lab_results.search(
            tenant_db_name="tenant_db_name",
            search_text="x",
        )
        assert_matches_type(LabResultSearchResponse, lab_result, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search_with_all_params(self, client: WebRecruitmentSDK) -> None:
        lab_result = client.system.lab_results.search(
            tenant_db_name="tenant_db_name",
            search_text="x",
            limit=1,
            similarity_threshold=0,
        )
        assert_matches_type(LabResultSearchResponse, lab_result, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_search(self, client: WebRecruitmentSDK) -> None:
        response = client.system.lab_results.with_raw_response.search(
            tenant_db_name="tenant_db_name",
            search_text="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lab_result = response.parse()
        assert_matches_type(LabResultSearchResponse, lab_result, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_search(self, client: WebRecruitmentSDK) -> None:
        with client.system.lab_results.with_streaming_response.search(
            tenant_db_name="tenant_db_name",
            search_text="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lab_result = response.parse()
            assert_matches_type(LabResultSearchResponse, lab_result, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_search(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.lab_results.with_raw_response.search(
                tenant_db_name="",
                search_text="x",
            )


class TestAsyncLabResults:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        lab_result = await async_client.system.lab_results.search(
            tenant_db_name="tenant_db_name",
            search_text="x",
        )
        assert_matches_type(LabResultSearchResponse, lab_result, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        lab_result = await async_client.system.lab_results.search(
            tenant_db_name="tenant_db_name",
            search_text="x",
            limit=1,
            similarity_threshold=0,
        )
        assert_matches_type(LabResultSearchResponse, lab_result, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.lab_results.with_raw_response.search(
            tenant_db_name="tenant_db_name",
            search_text="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lab_result = await response.parse()
        assert_matches_type(LabResultSearchResponse, lab_result, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.lab_results.with_streaming_response.search(
            tenant_db_name="tenant_db_name",
            search_text="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lab_result = await response.parse()
            assert_matches_type(LabResultSearchResponse, lab_result, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.lab_results.with_raw_response.search(
                tenant_db_name="",
                search_text="x",
            )
