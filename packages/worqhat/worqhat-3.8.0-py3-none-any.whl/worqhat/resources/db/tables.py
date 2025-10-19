# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.db import table_list_params, table_get_row_count_params, table_retrieve_schema_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.db.table_list_response import TableListResponse
from ...types.db.table_get_row_count_response import TableGetRowCountResponse
from ...types.db.table_retrieve_schema_response import TableRetrieveSchemaResponse

__all__ = ["TablesResource", "AsyncTablesResource"]


class TablesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TablesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return TablesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TablesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return TablesResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        schema: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TableListResponse:
        """
        Returns a list of all tables in the database that are accessible to your
        organization. Optionally filter by schema and environment.

        Args:
          environment: Environment to query (development, staging, production)

          schema: Database schema to filter tables

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/db/tables",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "environment": environment,
                        "schema": schema,
                    },
                    table_list_params.TableListParams,
                ),
            ),
            cast_to=TableListResponse,
        )

    def get_row_count(
        self,
        table_name: str,
        *,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TableGetRowCountResponse:
        """
        Returns the total number of rows in the specified table for your organization.

        Args:
          environment: Environment to query

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_name:
            raise ValueError(f"Expected a non-empty value for `table_name` but received {table_name!r}")
        return self._get(
            f"/db/tables/{table_name}/count",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"environment": environment}, table_get_row_count_params.TableGetRowCountParams),
            ),
            cast_to=TableGetRowCountResponse,
        )

    def retrieve_schema(
        self,
        table_name: str,
        *,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TableRetrieveSchemaResponse:
        """
        Returns detailed schema information for a specific table, including column
        names, types, and constraints.

        Args:
          environment: Environment to query

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_name:
            raise ValueError(f"Expected a non-empty value for `table_name` but received {table_name!r}")
        return self._get(
            f"/db/tables/{table_name}/schema",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"environment": environment}, table_retrieve_schema_params.TableRetrieveSchemaParams
                ),
            ),
            cast_to=TableRetrieveSchemaResponse,
        )


class AsyncTablesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTablesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncTablesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTablesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return AsyncTablesResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        schema: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TableListResponse:
        """
        Returns a list of all tables in the database that are accessible to your
        organization. Optionally filter by schema and environment.

        Args:
          environment: Environment to query (development, staging, production)

          schema: Database schema to filter tables

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/db/tables",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "environment": environment,
                        "schema": schema,
                    },
                    table_list_params.TableListParams,
                ),
            ),
            cast_to=TableListResponse,
        )

    async def get_row_count(
        self,
        table_name: str,
        *,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TableGetRowCountResponse:
        """
        Returns the total number of rows in the specified table for your organization.

        Args:
          environment: Environment to query

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_name:
            raise ValueError(f"Expected a non-empty value for `table_name` but received {table_name!r}")
        return await self._get(
            f"/db/tables/{table_name}/count",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"environment": environment}, table_get_row_count_params.TableGetRowCountParams
                ),
            ),
            cast_to=TableGetRowCountResponse,
        )

    async def retrieve_schema(
        self,
        table_name: str,
        *,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TableRetrieveSchemaResponse:
        """
        Returns detailed schema information for a specific table, including column
        names, types, and constraints.

        Args:
          environment: Environment to query

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not table_name:
            raise ValueError(f"Expected a non-empty value for `table_name` but received {table_name!r}")
        return await self._get(
            f"/db/tables/{table_name}/schema",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"environment": environment}, table_retrieve_schema_params.TableRetrieveSchemaParams
                ),
            ),
            cast_to=TableRetrieveSchemaResponse,
        )


class TablesResourceWithRawResponse:
    def __init__(self, tables: TablesResource) -> None:
        self._tables = tables

        self.list = to_raw_response_wrapper(
            tables.list,
        )
        self.get_row_count = to_raw_response_wrapper(
            tables.get_row_count,
        )
        self.retrieve_schema = to_raw_response_wrapper(
            tables.retrieve_schema,
        )


class AsyncTablesResourceWithRawResponse:
    def __init__(self, tables: AsyncTablesResource) -> None:
        self._tables = tables

        self.list = async_to_raw_response_wrapper(
            tables.list,
        )
        self.get_row_count = async_to_raw_response_wrapper(
            tables.get_row_count,
        )
        self.retrieve_schema = async_to_raw_response_wrapper(
            tables.retrieve_schema,
        )


class TablesResourceWithStreamingResponse:
    def __init__(self, tables: TablesResource) -> None:
        self._tables = tables

        self.list = to_streamed_response_wrapper(
            tables.list,
        )
        self.get_row_count = to_streamed_response_wrapper(
            tables.get_row_count,
        )
        self.retrieve_schema = to_streamed_response_wrapper(
            tables.retrieve_schema,
        )


class AsyncTablesResourceWithStreamingResponse:
    def __init__(self, tables: AsyncTablesResource) -> None:
        self._tables = tables

        self.list = async_to_streamed_response_wrapper(
            tables.list,
        )
        self.get_row_count = async_to_streamed_response_wrapper(
            tables.get_row_count,
        )
        self.retrieve_schema = async_to_streamed_response_wrapper(
            tables.retrieve_schema,
        )
