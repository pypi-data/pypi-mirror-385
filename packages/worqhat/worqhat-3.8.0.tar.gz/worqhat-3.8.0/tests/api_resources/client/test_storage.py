# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from worqhat import Worqhat, AsyncWorqhat
from tests.utils import assert_matches_type
from worqhat.types.client import (
    StorageUploadFileResponse,
    StorageDeleteFileByIDResponse,
    StorageRetrieveFileByIDResponse,
    StorageRetrieveFileByPathResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStorage:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_file_by_id(self, client: Worqhat) -> None:
        storage = client.client.storage.delete_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )
        assert_matches_type(StorageDeleteFileByIDResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_file_by_id(self, client: Worqhat) -> None:
        response = client.client.storage.with_raw_response.delete_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(StorageDeleteFileByIDResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_file_by_id(self, client: Worqhat) -> None:
        with client.client.storage.with_streaming_response.delete_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(StorageDeleteFileByIDResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_file_by_id(self, client: Worqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            client.client.storage.with_raw_response.delete_file_by_id(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_file_by_id(self, client: Worqhat) -> None:
        storage = client.client.storage.retrieve_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )
        assert_matches_type(StorageRetrieveFileByIDResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_file_by_id(self, client: Worqhat) -> None:
        response = client.client.storage.with_raw_response.retrieve_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(StorageRetrieveFileByIDResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_file_by_id(self, client: Worqhat) -> None:
        with client.client.storage.with_streaming_response.retrieve_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(StorageRetrieveFileByIDResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_file_by_id(self, client: Worqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            client.client.storage.with_raw_response.retrieve_file_by_id(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_file_by_path(self, client: Worqhat) -> None:
        storage = client.client.storage.retrieve_file_by_path(
            filepath="documents/invoices/invoice_2025.pdf",
        )
        assert_matches_type(StorageRetrieveFileByPathResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_file_by_path(self, client: Worqhat) -> None:
        response = client.client.storage.with_raw_response.retrieve_file_by_path(
            filepath="documents/invoices/invoice_2025.pdf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(StorageRetrieveFileByPathResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_file_by_path(self, client: Worqhat) -> None:
        with client.client.storage.with_streaming_response.retrieve_file_by_path(
            filepath="documents/invoices/invoice_2025.pdf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(StorageRetrieveFileByPathResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_file(self, client: Worqhat) -> None:
        storage = client.client.storage.upload_file(
            file=b"raw file contents",
        )
        assert_matches_type(StorageUploadFileResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_file_with_all_params(self, client: Worqhat) -> None:
        storage = client.client.storage.upload_file(
            file=b"raw file contents",
            path="documents/invoices/",
        )
        assert_matches_type(StorageUploadFileResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload_file(self, client: Worqhat) -> None:
        response = client.client.storage.with_raw_response.upload_file(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(StorageUploadFileResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload_file(self, client: Worqhat) -> None:
        with client.client.storage.with_streaming_response.upload_file(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(StorageUploadFileResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncStorage:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_file_by_id(self, async_client: AsyncWorqhat) -> None:
        storage = await async_client.client.storage.delete_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )
        assert_matches_type(StorageDeleteFileByIDResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_file_by_id(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.client.storage.with_raw_response.delete_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(StorageDeleteFileByIDResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_file_by_id(self, async_client: AsyncWorqhat) -> None:
        async with async_client.client.storage.with_streaming_response.delete_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(StorageDeleteFileByIDResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_file_by_id(self, async_client: AsyncWorqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            await async_client.client.storage.with_raw_response.delete_file_by_id(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_file_by_id(self, async_client: AsyncWorqhat) -> None:
        storage = await async_client.client.storage.retrieve_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )
        assert_matches_type(StorageRetrieveFileByIDResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_file_by_id(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.client.storage.with_raw_response.retrieve_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(StorageRetrieveFileByIDResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_file_by_id(self, async_client: AsyncWorqhat) -> None:
        async with async_client.client.storage.with_streaming_response.retrieve_file_by_id(
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(StorageRetrieveFileByIDResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_file_by_id(self, async_client: AsyncWorqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            await async_client.client.storage.with_raw_response.retrieve_file_by_id(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_file_by_path(self, async_client: AsyncWorqhat) -> None:
        storage = await async_client.client.storage.retrieve_file_by_path(
            filepath="documents/invoices/invoice_2025.pdf",
        )
        assert_matches_type(StorageRetrieveFileByPathResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_file_by_path(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.client.storage.with_raw_response.retrieve_file_by_path(
            filepath="documents/invoices/invoice_2025.pdf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(StorageRetrieveFileByPathResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_file_by_path(self, async_client: AsyncWorqhat) -> None:
        async with async_client.client.storage.with_streaming_response.retrieve_file_by_path(
            filepath="documents/invoices/invoice_2025.pdf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(StorageRetrieveFileByPathResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_file(self, async_client: AsyncWorqhat) -> None:
        storage = await async_client.client.storage.upload_file(
            file=b"raw file contents",
        )
        assert_matches_type(StorageUploadFileResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_file_with_all_params(self, async_client: AsyncWorqhat) -> None:
        storage = await async_client.client.storage.upload_file(
            file=b"raw file contents",
            path="documents/invoices/",
        )
        assert_matches_type(StorageUploadFileResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload_file(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.client.storage.with_raw_response.upload_file(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(StorageUploadFileResponse, storage, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload_file(self, async_client: AsyncWorqhat) -> None:
        async with async_client.client.storage.with_streaming_response.upload_file(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(StorageUploadFileResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True
