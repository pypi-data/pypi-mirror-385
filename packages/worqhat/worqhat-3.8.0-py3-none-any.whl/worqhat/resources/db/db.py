# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal

import httpx

from .tables import (
    TablesResource,
    AsyncTablesResource,
    TablesResourceWithRawResponse,
    AsyncTablesResourceWithRawResponse,
    TablesResourceWithStreamingResponse,
    AsyncTablesResourceWithStreamingResponse,
)
from ...types import (
    db_execute_batch_params,
    db_execute_query_params,
    db_insert_record_params,
    db_delete_records_params,
    db_update_records_params,
    db_process_nl_query_params,
)
from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.db_execute_batch_response import DBExecuteBatchResponse
from ...types.db_execute_query_response import DBExecuteQueryResponse
from ...types.db_insert_record_response import DBInsertRecordResponse
from ...types.db_delete_records_response import DBDeleteRecordsResponse
from ...types.db_update_records_response import DBUpdateRecordsResponse
from ...types.db_process_nl_query_response import DBProcessNlQueryResponse

__all__ = ["DBResource", "AsyncDBResource"]


class DBResource(SyncAPIResource):
    @cached_property
    def tables(self) -> TablesResource:
        return TablesResource(self._client)

    @cached_property
    def with_raw_response(self) -> DBResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return DBResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DBResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return DBResourceWithStreamingResponse(self)

    def delete_records(
        self,
        *,
        table: str,
        where: Dict[str, object],
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBDeleteRecordsResponse:
        """
        Deletes records from the specified table that match the where conditions.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          table: Table name to delete from

          where: Where conditions

          environment: Environment to delete from (development, staging, production)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            "/db/delete",
            body=maybe_transform(
                {
                    "table": table,
                    "where": where,
                    "environment": environment,
                },
                db_delete_records_params.DBDeleteRecordsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBDeleteRecordsResponse,
        )

    def execute_batch(
        self,
        *,
        operations: Iterable[db_execute_batch_params.Operation],
        environment: Literal["development", "staging", "production"] | Omit = omit,
        transactional: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBExecuteBatchResponse:
        """
        Executes multiple database operations (queries, inserts, updates, deletes) in a
        single transaction. If transactional is true, all operations will be rolled back
        if any operation fails.

        Args:
          operations: Array of database operations to execute

          environment: Environment to execute operations in

          transactional: Whether to execute all operations in a single transaction

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/db/batch",
            body=maybe_transform(
                {
                    "operations": operations,
                    "environment": environment,
                    "transactional": transactional,
                },
                db_execute_batch_params.DBExecuteBatchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBExecuteBatchResponse,
        )

    def execute_query(
        self,
        *,
        query: str,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        params: Dict[str, object] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBExecuteQueryResponse:
        """Executes a raw SQL query directly against ClickHouse (WorqDB).

        This endpoint
        provides direct SQL access with security guardrails to prevent destructive
        operations.

        Args:
          query: SQL query to execute

          environment: Environment to query (development, staging, production)

          params: Optional query parameters

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/db/query",
            body=maybe_transform(
                {
                    "query": query,
                    "environment": environment,
                    "params": params,
                },
                db_execute_query_params.DBExecuteQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBExecuteQueryResponse,
        )

    def insert_record(
        self,
        *,
        data: Dict[str, object],
        table: str,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBInsertRecordResponse:
        """Inserts a new record into the specified table.

        Organization ID is automatically
        added for multi-tenant security.

        Args:
          data: Data to insert

          table: Table name to insert into

          environment: Environment to insert into (development, staging, production)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/db/insert",
            body=maybe_transform(
                {
                    "data": data,
                    "table": table,
                    "environment": environment,
                },
                db_insert_record_params.DBInsertRecordParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBInsertRecordResponse,
        )

    def process_nl_query(
        self,
        *,
        question: str,
        table: str,
        context: Dict[str, object] | Omit = omit,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBProcessNlQueryResponse:
        """
        Converts a natural language question into a SQL query and executes it.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          question: Natural language question

          table: Table name to query

          context: Optional context for the query

          environment: Environment to query (development, staging, production)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/db/nl-query",
            body=maybe_transform(
                {
                    "question": question,
                    "table": table,
                    "context": context,
                    "environment": environment,
                },
                db_process_nl_query_params.DBProcessNlQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBProcessNlQueryResponse,
        )

    def update_records(
        self,
        *,
        data: Dict[str, object],
        table: str,
        where: Dict[str, object],
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBUpdateRecordsResponse:
        """
        Updates records in the specified table that match the where conditions.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          data: Data to update

          table: Table name to update

          where: Where conditions

          environment: Environment to update in (development, staging, production)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/db/update",
            body=maybe_transform(
                {
                    "data": data,
                    "table": table,
                    "where": where,
                    "environment": environment,
                },
                db_update_records_params.DBUpdateRecordsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBUpdateRecordsResponse,
        )


class AsyncDBResource(AsyncAPIResource):
    @cached_property
    def tables(self) -> AsyncTablesResource:
        return AsyncTablesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDBResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDBResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDBResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return AsyncDBResourceWithStreamingResponse(self)

    async def delete_records(
        self,
        *,
        table: str,
        where: Dict[str, object],
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBDeleteRecordsResponse:
        """
        Deletes records from the specified table that match the where conditions.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          table: Table name to delete from

          where: Where conditions

          environment: Environment to delete from (development, staging, production)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            "/db/delete",
            body=await async_maybe_transform(
                {
                    "table": table,
                    "where": where,
                    "environment": environment,
                },
                db_delete_records_params.DBDeleteRecordsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBDeleteRecordsResponse,
        )

    async def execute_batch(
        self,
        *,
        operations: Iterable[db_execute_batch_params.Operation],
        environment: Literal["development", "staging", "production"] | Omit = omit,
        transactional: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBExecuteBatchResponse:
        """
        Executes multiple database operations (queries, inserts, updates, deletes) in a
        single transaction. If transactional is true, all operations will be rolled back
        if any operation fails.

        Args:
          operations: Array of database operations to execute

          environment: Environment to execute operations in

          transactional: Whether to execute all operations in a single transaction

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/db/batch",
            body=await async_maybe_transform(
                {
                    "operations": operations,
                    "environment": environment,
                    "transactional": transactional,
                },
                db_execute_batch_params.DBExecuteBatchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBExecuteBatchResponse,
        )

    async def execute_query(
        self,
        *,
        query: str,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        params: Dict[str, object] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBExecuteQueryResponse:
        """Executes a raw SQL query directly against ClickHouse (WorqDB).

        This endpoint
        provides direct SQL access with security guardrails to prevent destructive
        operations.

        Args:
          query: SQL query to execute

          environment: Environment to query (development, staging, production)

          params: Optional query parameters

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/db/query",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "environment": environment,
                    "params": params,
                },
                db_execute_query_params.DBExecuteQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBExecuteQueryResponse,
        )

    async def insert_record(
        self,
        *,
        data: Dict[str, object],
        table: str,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBInsertRecordResponse:
        """Inserts a new record into the specified table.

        Organization ID is automatically
        added for multi-tenant security.

        Args:
          data: Data to insert

          table: Table name to insert into

          environment: Environment to insert into (development, staging, production)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/db/insert",
            body=await async_maybe_transform(
                {
                    "data": data,
                    "table": table,
                    "environment": environment,
                },
                db_insert_record_params.DBInsertRecordParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBInsertRecordResponse,
        )

    async def process_nl_query(
        self,
        *,
        question: str,
        table: str,
        context: Dict[str, object] | Omit = omit,
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBProcessNlQueryResponse:
        """
        Converts a natural language question into a SQL query and executes it.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          question: Natural language question

          table: Table name to query

          context: Optional context for the query

          environment: Environment to query (development, staging, production)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/db/nl-query",
            body=await async_maybe_transform(
                {
                    "question": question,
                    "table": table,
                    "context": context,
                    "environment": environment,
                },
                db_process_nl_query_params.DBProcessNlQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBProcessNlQueryResponse,
        )

    async def update_records(
        self,
        *,
        data: Dict[str, object],
        table: str,
        where: Dict[str, object],
        environment: Literal["development", "staging", "production"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DBUpdateRecordsResponse:
        """
        Updates records in the specified table that match the where conditions.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          data: Data to update

          table: Table name to update

          where: Where conditions

          environment: Environment to update in (development, staging, production)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/db/update",
            body=await async_maybe_transform(
                {
                    "data": data,
                    "table": table,
                    "where": where,
                    "environment": environment,
                },
                db_update_records_params.DBUpdateRecordsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBUpdateRecordsResponse,
        )


class DBResourceWithRawResponse:
    def __init__(self, db: DBResource) -> None:
        self._db = db

        self.delete_records = to_raw_response_wrapper(
            db.delete_records,
        )
        self.execute_batch = to_raw_response_wrapper(
            db.execute_batch,
        )
        self.execute_query = to_raw_response_wrapper(
            db.execute_query,
        )
        self.insert_record = to_raw_response_wrapper(
            db.insert_record,
        )
        self.process_nl_query = to_raw_response_wrapper(
            db.process_nl_query,
        )
        self.update_records = to_raw_response_wrapper(
            db.update_records,
        )

    @cached_property
    def tables(self) -> TablesResourceWithRawResponse:
        return TablesResourceWithRawResponse(self._db.tables)


class AsyncDBResourceWithRawResponse:
    def __init__(self, db: AsyncDBResource) -> None:
        self._db = db

        self.delete_records = async_to_raw_response_wrapper(
            db.delete_records,
        )
        self.execute_batch = async_to_raw_response_wrapper(
            db.execute_batch,
        )
        self.execute_query = async_to_raw_response_wrapper(
            db.execute_query,
        )
        self.insert_record = async_to_raw_response_wrapper(
            db.insert_record,
        )
        self.process_nl_query = async_to_raw_response_wrapper(
            db.process_nl_query,
        )
        self.update_records = async_to_raw_response_wrapper(
            db.update_records,
        )

    @cached_property
    def tables(self) -> AsyncTablesResourceWithRawResponse:
        return AsyncTablesResourceWithRawResponse(self._db.tables)


class DBResourceWithStreamingResponse:
    def __init__(self, db: DBResource) -> None:
        self._db = db

        self.delete_records = to_streamed_response_wrapper(
            db.delete_records,
        )
        self.execute_batch = to_streamed_response_wrapper(
            db.execute_batch,
        )
        self.execute_query = to_streamed_response_wrapper(
            db.execute_query,
        )
        self.insert_record = to_streamed_response_wrapper(
            db.insert_record,
        )
        self.process_nl_query = to_streamed_response_wrapper(
            db.process_nl_query,
        )
        self.update_records = to_streamed_response_wrapper(
            db.update_records,
        )

    @cached_property
    def tables(self) -> TablesResourceWithStreamingResponse:
        return TablesResourceWithStreamingResponse(self._db.tables)


class AsyncDBResourceWithStreamingResponse:
    def __init__(self, db: AsyncDBResource) -> None:
        self._db = db

        self.delete_records = async_to_streamed_response_wrapper(
            db.delete_records,
        )
        self.execute_batch = async_to_streamed_response_wrapper(
            db.execute_batch,
        )
        self.execute_query = async_to_streamed_response_wrapper(
            db.execute_query,
        )
        self.insert_record = async_to_streamed_response_wrapper(
            db.insert_record,
        )
        self.process_nl_query = async_to_streamed_response_wrapper(
            db.process_nl_query,
        )
        self.update_records = async_to_streamed_response_wrapper(
            db.update_records,
        )

    @cached_property
    def tables(self) -> AsyncTablesResourceWithStreamingResponse:
        return AsyncTablesResourceWithStreamingResponse(self._db.tables)
