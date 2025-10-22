# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.integrations.bank import TransactionSyncResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTransactions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_sync(self, client: SampleHealthcare) -> None:
        transaction = client.v2.integrations.bank.transactions.sync(
            slug="slug",
        )
        assert_matches_type(TransactionSyncResponse, transaction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_sync_with_all_params(self, client: SampleHealthcare) -> None:
        transaction = client.v2.integrations.bank.transactions.sync(
            slug="slug",
            cursor="cursor",
        )
        assert_matches_type(TransactionSyncResponse, transaction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_sync(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.bank.transactions.with_raw_response.sync(
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transaction = response.parse()
        assert_matches_type(TransactionSyncResponse, transaction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_sync(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.bank.transactions.with_streaming_response.sync(
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transaction = response.parse()
            assert_matches_type(TransactionSyncResponse, transaction, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTransactions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_sync(self, async_client: AsyncSampleHealthcare) -> None:
        transaction = await async_client.v2.integrations.bank.transactions.sync(
            slug="slug",
        )
        assert_matches_type(TransactionSyncResponse, transaction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_sync_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        transaction = await async_client.v2.integrations.bank.transactions.sync(
            slug="slug",
            cursor="cursor",
        )
        assert_matches_type(TransactionSyncResponse, transaction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_sync(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.bank.transactions.with_raw_response.sync(
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transaction = await response.parse()
        assert_matches_type(TransactionSyncResponse, transaction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_sync(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.bank.transactions.with_streaming_response.sync(
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transaction = await response.parse()
            assert_matches_type(TransactionSyncResponse, transaction, path=["response"])

        assert cast(Any, response.is_closed) is True
