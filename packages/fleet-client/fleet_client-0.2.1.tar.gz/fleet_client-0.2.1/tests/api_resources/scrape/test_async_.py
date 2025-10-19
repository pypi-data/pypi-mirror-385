# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fleet import Fleet, AsyncFleet
from tests.utils import assert_matches_type
from fleet.types.scrape import (
    AsyncListResponse,
    AsyncCreateResponse,
    AsyncDeleteResponse,
    AsyncRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAsync:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fleet) -> None:
        async_ = client.scrape.async_.create(
            url="url",
        )
        assert_matches_type(AsyncCreateResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fleet) -> None:
        async_ = client.scrape.async_.create(
            url="url",
            wait_until="load",
        )
        assert_matches_type(AsyncCreateResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fleet) -> None:
        response = client.scrape.async_.with_raw_response.create(
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        async_ = response.parse()
        assert_matches_type(AsyncCreateResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fleet) -> None:
        with client.scrape.async_.with_streaming_response.create(
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            async_ = response.parse()
            assert_matches_type(AsyncCreateResponse, async_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Fleet) -> None:
        async_ = client.scrape.async_.retrieve(
            "job_id",
        )
        assert_matches_type(AsyncRetrieveResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Fleet) -> None:
        response = client.scrape.async_.with_raw_response.retrieve(
            "job_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        async_ = response.parse()
        assert_matches_type(AsyncRetrieveResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Fleet) -> None:
        with client.scrape.async_.with_streaming_response.retrieve(
            "job_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            async_ = response.parse()
            assert_matches_type(AsyncRetrieveResponse, async_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.scrape.async_.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fleet) -> None:
        async_ = client.scrape.async_.list()
        assert_matches_type(AsyncListResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fleet) -> None:
        response = client.scrape.async_.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        async_ = response.parse()
        assert_matches_type(AsyncListResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fleet) -> None:
        with client.scrape.async_.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            async_ = response.parse()
            assert_matches_type(AsyncListResponse, async_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fleet) -> None:
        async_ = client.scrape.async_.delete(
            "job_id",
        )
        assert_matches_type(AsyncDeleteResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fleet) -> None:
        response = client.scrape.async_.with_raw_response.delete(
            "job_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        async_ = response.parse()
        assert_matches_type(AsyncDeleteResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fleet) -> None:
        with client.scrape.async_.with_streaming_response.delete(
            "job_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            async_ = response.parse()
            assert_matches_type(AsyncDeleteResponse, async_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.scrape.async_.with_raw_response.delete(
                "",
            )


class TestAsyncAsync:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFleet) -> None:
        async_ = await async_client.scrape.async_.create(
            url="url",
        )
        assert_matches_type(AsyncCreateResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFleet) -> None:
        async_ = await async_client.scrape.async_.create(
            url="url",
            wait_until="load",
        )
        assert_matches_type(AsyncCreateResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFleet) -> None:
        response = await async_client.scrape.async_.with_raw_response.create(
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        async_ = await response.parse()
        assert_matches_type(AsyncCreateResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFleet) -> None:
        async with async_client.scrape.async_.with_streaming_response.create(
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            async_ = await response.parse()
            assert_matches_type(AsyncCreateResponse, async_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFleet) -> None:
        async_ = await async_client.scrape.async_.retrieve(
            "job_id",
        )
        assert_matches_type(AsyncRetrieveResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFleet) -> None:
        response = await async_client.scrape.async_.with_raw_response.retrieve(
            "job_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        async_ = await response.parse()
        assert_matches_type(AsyncRetrieveResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFleet) -> None:
        async with async_client.scrape.async_.with_streaming_response.retrieve(
            "job_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            async_ = await response.parse()
            assert_matches_type(AsyncRetrieveResponse, async_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.scrape.async_.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFleet) -> None:
        async_ = await async_client.scrape.async_.list()
        assert_matches_type(AsyncListResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFleet) -> None:
        response = await async_client.scrape.async_.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        async_ = await response.parse()
        assert_matches_type(AsyncListResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFleet) -> None:
        async with async_client.scrape.async_.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            async_ = await response.parse()
            assert_matches_type(AsyncListResponse, async_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFleet) -> None:
        async_ = await async_client.scrape.async_.delete(
            "job_id",
        )
        assert_matches_type(AsyncDeleteResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFleet) -> None:
        response = await async_client.scrape.async_.with_raw_response.delete(
            "job_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        async_ = await response.parse()
        assert_matches_type(AsyncDeleteResponse, async_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFleet) -> None:
        async with async_client.scrape.async_.with_streaming_response.delete(
            "job_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            async_ = await response.parse()
            assert_matches_type(AsyncDeleteResponse, async_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.scrape.async_.with_raw_response.delete(
                "",
            )
