# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from worqhat import Worqhat, AsyncWorqhat
from tests.utils import assert_matches_type
from worqhat.types.db import (
    TableListResponse,
    TableGetRowCountResponse,
    TableRetrieveSchemaResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTables:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Worqhat) -> None:
        table = client.db.tables.list()
        assert_matches_type(TableListResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Worqhat) -> None:
        table = client.db.tables.list(
            environment="production",
            schema="public",
        )
        assert_matches_type(TableListResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Worqhat) -> None:
        response = client.db.tables.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableListResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Worqhat) -> None:
        with client.db.tables.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableListResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_row_count(self, client: Worqhat) -> None:
        table = client.db.tables.get_row_count(
            table_name="users",
        )
        assert_matches_type(TableGetRowCountResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_row_count_with_all_params(self, client: Worqhat) -> None:
        table = client.db.tables.get_row_count(
            table_name="users",
            environment="production",
        )
        assert_matches_type(TableGetRowCountResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_row_count(self, client: Worqhat) -> None:
        response = client.db.tables.with_raw_response.get_row_count(
            table_name="users",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableGetRowCountResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_row_count(self, client: Worqhat) -> None:
        with client.db.tables.with_streaming_response.get_row_count(
            table_name="users",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableGetRowCountResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_row_count(self, client: Worqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_name` but received ''"):
            client.db.tables.with_raw_response.get_row_count(
                table_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_schema(self, client: Worqhat) -> None:
        table = client.db.tables.retrieve_schema(
            table_name="users",
        )
        assert_matches_type(TableRetrieveSchemaResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_schema_with_all_params(self, client: Worqhat) -> None:
        table = client.db.tables.retrieve_schema(
            table_name="users",
            environment="production",
        )
        assert_matches_type(TableRetrieveSchemaResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_schema(self, client: Worqhat) -> None:
        response = client.db.tables.with_raw_response.retrieve_schema(
            table_name="users",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = response.parse()
        assert_matches_type(TableRetrieveSchemaResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_schema(self, client: Worqhat) -> None:
        with client.db.tables.with_streaming_response.retrieve_schema(
            table_name="users",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = response.parse()
            assert_matches_type(TableRetrieveSchemaResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_schema(self, client: Worqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_name` but received ''"):
            client.db.tables.with_raw_response.retrieve_schema(
                table_name="",
            )


class TestAsyncTables:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWorqhat) -> None:
        table = await async_client.db.tables.list()
        assert_matches_type(TableListResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncWorqhat) -> None:
        table = await async_client.db.tables.list(
            environment="production",
            schema="public",
        )
        assert_matches_type(TableListResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.db.tables.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableListResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWorqhat) -> None:
        async with async_client.db.tables.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableListResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_row_count(self, async_client: AsyncWorqhat) -> None:
        table = await async_client.db.tables.get_row_count(
            table_name="users",
        )
        assert_matches_type(TableGetRowCountResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_row_count_with_all_params(self, async_client: AsyncWorqhat) -> None:
        table = await async_client.db.tables.get_row_count(
            table_name="users",
            environment="production",
        )
        assert_matches_type(TableGetRowCountResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_row_count(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.db.tables.with_raw_response.get_row_count(
            table_name="users",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableGetRowCountResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_row_count(self, async_client: AsyncWorqhat) -> None:
        async with async_client.db.tables.with_streaming_response.get_row_count(
            table_name="users",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableGetRowCountResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_row_count(self, async_client: AsyncWorqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_name` but received ''"):
            await async_client.db.tables.with_raw_response.get_row_count(
                table_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_schema(self, async_client: AsyncWorqhat) -> None:
        table = await async_client.db.tables.retrieve_schema(
            table_name="users",
        )
        assert_matches_type(TableRetrieveSchemaResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_schema_with_all_params(self, async_client: AsyncWorqhat) -> None:
        table = await async_client.db.tables.retrieve_schema(
            table_name="users",
            environment="production",
        )
        assert_matches_type(TableRetrieveSchemaResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_schema(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.db.tables.with_raw_response.retrieve_schema(
            table_name="users",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        table = await response.parse()
        assert_matches_type(TableRetrieveSchemaResponse, table, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_schema(self, async_client: AsyncWorqhat) -> None:
        async with async_client.db.tables.with_streaming_response.retrieve_schema(
            table_name="users",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            table = await response.parse()
            assert_matches_type(TableRetrieveSchemaResponse, table, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_schema(self, async_client: AsyncWorqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `table_name` but received ''"):
            await async_client.db.tables.with_raw_response.retrieve_schema(
                table_name="",
            )
