# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestV2:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_protocol_success(self, client: WebRecruitmentSDK) -> None:
        v2 = client.system.protocol_parsing.v2.update_protocol_success(
            job_id="job_id",
            path_tenant_db_name="tenant_db_name",
            criteria_create_with_protocol_metadata=[
                {
                    "criteria_create": [
                        {
                            "summary": "summary",
                            "type": "inclusion",
                        }
                    ],
                    "protocol_metadata": {"original_text": "originalText"},
                }
            ],
            external_protocol_id="externalProtocolId",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )
        assert_matches_type(object, v2, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_protocol_success(self, client: WebRecruitmentSDK) -> None:
        response = client.system.protocol_parsing.v2.with_raw_response.update_protocol_success(
            job_id="job_id",
            path_tenant_db_name="tenant_db_name",
            criteria_create_with_protocol_metadata=[
                {
                    "criteria_create": [
                        {
                            "summary": "summary",
                            "type": "inclusion",
                        }
                    ],
                    "protocol_metadata": {"original_text": "originalText"},
                }
            ],
            external_protocol_id="externalProtocolId",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v2 = response.parse()
        assert_matches_type(object, v2, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_protocol_success(self, client: WebRecruitmentSDK) -> None:
        with client.system.protocol_parsing.v2.with_streaming_response.update_protocol_success(
            job_id="job_id",
            path_tenant_db_name="tenant_db_name",
            criteria_create_with_protocol_metadata=[
                {
                    "criteria_create": [
                        {
                            "summary": "summary",
                            "type": "inclusion",
                        }
                    ],
                    "protocol_metadata": {"original_text": "originalText"},
                }
            ],
            external_protocol_id="externalProtocolId",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v2 = response.parse()
            assert_matches_type(object, v2, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_protocol_success(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_tenant_db_name` but received ''"):
            client.system.protocol_parsing.v2.with_raw_response.update_protocol_success(
                job_id="job_id",
                path_tenant_db_name="",
                criteria_create_with_protocol_metadata=[
                    {
                        "criteria_create": [
                            {
                                "summary": "summary",
                                "type": "inclusion",
                            }
                        ],
                        "protocol_metadata": {"original_text": "originalText"},
                    }
                ],
                external_protocol_id="externalProtocolId",
                task_id=0,
                task_name="taskName",
                body_tenant_db_name="tenantDbName",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.system.protocol_parsing.v2.with_raw_response.update_protocol_success(
                job_id="",
                path_tenant_db_name="tenant_db_name",
                criteria_create_with_protocol_metadata=[
                    {
                        "criteria_create": [
                            {
                                "summary": "summary",
                                "type": "inclusion",
                            }
                        ],
                        "protocol_metadata": {"original_text": "originalText"},
                    }
                ],
                external_protocol_id="externalProtocolId",
                task_id=0,
                task_name="taskName",
                body_tenant_db_name="tenantDbName",
            )


class TestAsyncV2:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_protocol_success(self, async_client: AsyncWebRecruitmentSDK) -> None:
        v2 = await async_client.system.protocol_parsing.v2.update_protocol_success(
            job_id="job_id",
            path_tenant_db_name="tenant_db_name",
            criteria_create_with_protocol_metadata=[
                {
                    "criteria_create": [
                        {
                            "summary": "summary",
                            "type": "inclusion",
                        }
                    ],
                    "protocol_metadata": {"original_text": "originalText"},
                }
            ],
            external_protocol_id="externalProtocolId",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )
        assert_matches_type(object, v2, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_protocol_success(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.protocol_parsing.v2.with_raw_response.update_protocol_success(
            job_id="job_id",
            path_tenant_db_name="tenant_db_name",
            criteria_create_with_protocol_metadata=[
                {
                    "criteria_create": [
                        {
                            "summary": "summary",
                            "type": "inclusion",
                        }
                    ],
                    "protocol_metadata": {"original_text": "originalText"},
                }
            ],
            external_protocol_id="externalProtocolId",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v2 = await response.parse()
        assert_matches_type(object, v2, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_protocol_success(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.protocol_parsing.v2.with_streaming_response.update_protocol_success(
            job_id="job_id",
            path_tenant_db_name="tenant_db_name",
            criteria_create_with_protocol_metadata=[
                {
                    "criteria_create": [
                        {
                            "summary": "summary",
                            "type": "inclusion",
                        }
                    ],
                    "protocol_metadata": {"original_text": "originalText"},
                }
            ],
            external_protocol_id="externalProtocolId",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v2 = await response.parse()
            assert_matches_type(object, v2, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_protocol_success(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_tenant_db_name` but received ''"):
            await async_client.system.protocol_parsing.v2.with_raw_response.update_protocol_success(
                job_id="job_id",
                path_tenant_db_name="",
                criteria_create_with_protocol_metadata=[
                    {
                        "criteria_create": [
                            {
                                "summary": "summary",
                                "type": "inclusion",
                            }
                        ],
                        "protocol_metadata": {"original_text": "originalText"},
                    }
                ],
                external_protocol_id="externalProtocolId",
                task_id=0,
                task_name="taskName",
                body_tenant_db_name="tenantDbName",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.system.protocol_parsing.v2.with_raw_response.update_protocol_success(
                job_id="",
                path_tenant_db_name="tenant_db_name",
                criteria_create_with_protocol_metadata=[
                    {
                        "criteria_create": [
                            {
                                "summary": "summary",
                                "type": "inclusion",
                            }
                        ],
                        "protocol_metadata": {"original_text": "originalText"},
                    }
                ],
                external_protocol_id="externalProtocolId",
                task_id=0,
                task_name="taskName",
                body_tenant_db_name="tenantDbName",
            )
