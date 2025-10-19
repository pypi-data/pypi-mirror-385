# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, FileTypes, omit, not_given
from ..._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.client import storage_upload_file_params, storage_retrieve_file_by_path_params
from ...types.client.storage_upload_file_response import StorageUploadFileResponse
from ...types.client.storage_delete_file_by_id_response import StorageDeleteFileByIDResponse
from ...types.client.storage_retrieve_file_by_id_response import StorageRetrieveFileByIDResponse
from ...types.client.storage_retrieve_file_by_path_response import StorageRetrieveFileByPathResponse

__all__ = ["StorageResource", "AsyncStorageResource"]


class StorageResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StorageResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return StorageResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StorageResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return StorageResourceWithStreamingResponse(self)

    def delete_file_by_id(
        self,
        file_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageDeleteFileByIDResponse:
        """Permanently deletes a file from storage by its unique ID.

        This action cannot be
        undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        return self._delete(
            f"/storage/delete/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageDeleteFileByIDResponse,
        )

    def retrieve_file_by_id(
        self,
        file_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageRetrieveFileByIDResponse:
        """Retrieves a file from storage by its unique ID.

        Returns the file metadata and a
        download URL.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        return self._get(
            f"/storage/fetch/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageRetrieveFileByIDResponse,
        )

    def retrieve_file_by_path(
        self,
        *,
        filepath: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageRetrieveFileByPathResponse:
        """
        Retrieves a file from storage by its path within the organization's storage.
        Returns the file metadata and a download URL.

        Args:
          filepath: Path to the file within organization storage

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/storage/fetch-by-path",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"filepath": filepath}, storage_retrieve_file_by_path_params.StorageRetrieveFileByPathParams
                ),
            ),
            cast_to=StorageRetrieveFileByPathResponse,
        )

    def upload_file(
        self,
        *,
        file: FileTypes,
        path: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageUploadFileResponse:
        """Uploads a file to S3 storage and returns the file ID and metadata.

        Optionally
        specify a custom path within the organization's storage bucket.

        Args:
          file: File to upload (max 50MB)

          path: Optional custom path within organization storage

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "path": path,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/storage/upload",
            body=maybe_transform(body, storage_upload_file_params.StorageUploadFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageUploadFileResponse,
        )


class AsyncStorageResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStorageResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncStorageResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStorageResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return AsyncStorageResourceWithStreamingResponse(self)

    async def delete_file_by_id(
        self,
        file_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageDeleteFileByIDResponse:
        """Permanently deletes a file from storage by its unique ID.

        This action cannot be
        undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        return await self._delete(
            f"/storage/delete/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageDeleteFileByIDResponse,
        )

    async def retrieve_file_by_id(
        self,
        file_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageRetrieveFileByIDResponse:
        """Retrieves a file from storage by its unique ID.

        Returns the file metadata and a
        download URL.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        return await self._get(
            f"/storage/fetch/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageRetrieveFileByIDResponse,
        )

    async def retrieve_file_by_path(
        self,
        *,
        filepath: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageRetrieveFileByPathResponse:
        """
        Retrieves a file from storage by its path within the organization's storage.
        Returns the file metadata and a download URL.

        Args:
          filepath: Path to the file within organization storage

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/storage/fetch-by-path",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"filepath": filepath}, storage_retrieve_file_by_path_params.StorageRetrieveFileByPathParams
                ),
            ),
            cast_to=StorageRetrieveFileByPathResponse,
        )

    async def upload_file(
        self,
        *,
        file: FileTypes,
        path: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageUploadFileResponse:
        """Uploads a file to S3 storage and returns the file ID and metadata.

        Optionally
        specify a custom path within the organization's storage bucket.

        Args:
          file: File to upload (max 50MB)

          path: Optional custom path within organization storage

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "path": path,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/storage/upload",
            body=await async_maybe_transform(body, storage_upload_file_params.StorageUploadFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageUploadFileResponse,
        )


class StorageResourceWithRawResponse:
    def __init__(self, storage: StorageResource) -> None:
        self._storage = storage

        self.delete_file_by_id = to_raw_response_wrapper(
            storage.delete_file_by_id,
        )
        self.retrieve_file_by_id = to_raw_response_wrapper(
            storage.retrieve_file_by_id,
        )
        self.retrieve_file_by_path = to_raw_response_wrapper(
            storage.retrieve_file_by_path,
        )
        self.upload_file = to_raw_response_wrapper(
            storage.upload_file,
        )


class AsyncStorageResourceWithRawResponse:
    def __init__(self, storage: AsyncStorageResource) -> None:
        self._storage = storage

        self.delete_file_by_id = async_to_raw_response_wrapper(
            storage.delete_file_by_id,
        )
        self.retrieve_file_by_id = async_to_raw_response_wrapper(
            storage.retrieve_file_by_id,
        )
        self.retrieve_file_by_path = async_to_raw_response_wrapper(
            storage.retrieve_file_by_path,
        )
        self.upload_file = async_to_raw_response_wrapper(
            storage.upload_file,
        )


class StorageResourceWithStreamingResponse:
    def __init__(self, storage: StorageResource) -> None:
        self._storage = storage

        self.delete_file_by_id = to_streamed_response_wrapper(
            storage.delete_file_by_id,
        )
        self.retrieve_file_by_id = to_streamed_response_wrapper(
            storage.retrieve_file_by_id,
        )
        self.retrieve_file_by_path = to_streamed_response_wrapper(
            storage.retrieve_file_by_path,
        )
        self.upload_file = to_streamed_response_wrapper(
            storage.upload_file,
        )


class AsyncStorageResourceWithStreamingResponse:
    def __init__(self, storage: AsyncStorageResource) -> None:
        self._storage = storage

        self.delete_file_by_id = async_to_streamed_response_wrapper(
            storage.delete_file_by_id,
        )
        self.retrieve_file_by_id = async_to_streamed_response_wrapper(
            storage.retrieve_file_by_id,
        )
        self.retrieve_file_by_path = async_to_streamed_response_wrapper(
            storage.retrieve_file_by_path,
        )
        self.upload_file = async_to_streamed_response_wrapper(
            storage.upload_file,
        )
