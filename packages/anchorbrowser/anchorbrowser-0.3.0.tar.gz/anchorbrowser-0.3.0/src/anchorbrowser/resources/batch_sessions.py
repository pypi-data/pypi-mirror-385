# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ..types import batch_session_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.batch_session_create_response import BatchSessionCreateResponse
from ..types.batch_session_retrieve_response import BatchSessionRetrieveResponse

__all__ = ["BatchSessionsResource", "AsyncBatchSessionsResource"]


class BatchSessionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BatchSessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return BatchSessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BatchSessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return BatchSessionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        count: int,
        configuration: batch_session_create_params.Configuration | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchSessionCreateResponse:
        """Creates multiple browser sessions in a single batch operation.

        This endpoint
        allows you to create up to 5,000 browser sessions simultaneously with the same
        configuration.

        The batch will be processed asynchronously, and you can monitor progress using
        the batch status endpoint.

        Args:
          count: Number of sessions to create in the batch (1-1000)

          configuration: Configuration that applies to all sessions in the batch

          metadata: Optional batch-level metadata for identification and organization

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/batch-sessions",
            body=maybe_transform(
                {
                    "count": count,
                    "configuration": configuration,
                    "metadata": metadata,
                },
                batch_session_create_params.BatchSessionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchSessionCreateResponse,
        )

    def retrieve(
        self,
        batch_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchSessionRetrieveResponse:
        """
        Retrieves detailed status information for a specific batch, including progress,
        individual session details, and any errors that occurred.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        return self._get(
            f"/v1/batch-sessions/{batch_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchSessionRetrieveResponse,
        )


class AsyncBatchSessionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBatchSessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return AsyncBatchSessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBatchSessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return AsyncBatchSessionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        count: int,
        configuration: batch_session_create_params.Configuration | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchSessionCreateResponse:
        """Creates multiple browser sessions in a single batch operation.

        This endpoint
        allows you to create up to 5,000 browser sessions simultaneously with the same
        configuration.

        The batch will be processed asynchronously, and you can monitor progress using
        the batch status endpoint.

        Args:
          count: Number of sessions to create in the batch (1-1000)

          configuration: Configuration that applies to all sessions in the batch

          metadata: Optional batch-level metadata for identification and organization

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/batch-sessions",
            body=await async_maybe_transform(
                {
                    "count": count,
                    "configuration": configuration,
                    "metadata": metadata,
                },
                batch_session_create_params.BatchSessionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchSessionCreateResponse,
        )

    async def retrieve(
        self,
        batch_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchSessionRetrieveResponse:
        """
        Retrieves detailed status information for a specific batch, including progress,
        individual session details, and any errors that occurred.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        return await self._get(
            f"/v1/batch-sessions/{batch_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchSessionRetrieveResponse,
        )


class BatchSessionsResourceWithRawResponse:
    def __init__(self, batch_sessions: BatchSessionsResource) -> None:
        self._batch_sessions = batch_sessions

        self.create = to_raw_response_wrapper(
            batch_sessions.create,
        )
        self.retrieve = to_raw_response_wrapper(
            batch_sessions.retrieve,
        )


class AsyncBatchSessionsResourceWithRawResponse:
    def __init__(self, batch_sessions: AsyncBatchSessionsResource) -> None:
        self._batch_sessions = batch_sessions

        self.create = async_to_raw_response_wrapper(
            batch_sessions.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            batch_sessions.retrieve,
        )


class BatchSessionsResourceWithStreamingResponse:
    def __init__(self, batch_sessions: BatchSessionsResource) -> None:
        self._batch_sessions = batch_sessions

        self.create = to_streamed_response_wrapper(
            batch_sessions.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            batch_sessions.retrieve,
        )


class AsyncBatchSessionsResourceWithStreamingResponse:
    def __init__(self, batch_sessions: AsyncBatchSessionsResource) -> None:
        self._batch_sessions = batch_sessions

        self.create = async_to_streamed_response_wrapper(
            batch_sessions.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            batch_sessions.retrieve,
        )
