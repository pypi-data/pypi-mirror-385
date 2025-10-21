# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .run import (
    RunResource,
    AsyncRunResource,
    RunResourceWithRawResponse,
    AsyncRunResourceWithRawResponse,
    RunResourceWithStreamingResponse,
    AsyncRunResourceWithStreamingResponse,
)
from ...types import task_list_params, task_create_params
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
from ...types.task_list_response import TaskListResponse
from ...types.task_create_response import TaskCreateResponse

__all__ = ["TaskResource", "AsyncTaskResource"]


class TaskResource(SyncAPIResource):
    @cached_property
    def run(self) -> RunResource:
        return RunResource(self._client)

    @cached_property
    def with_raw_response(self) -> TaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return TaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return TaskResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        language: Literal["typescript"],
        name: str,
        browser_configuration: task_create_params.BrowserConfiguration | Omit = omit,
        code: str | Omit = omit,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskCreateResponse:
        """Creates a new task or updates an existing task with the same name.

        Tasks are
        reusable code snippets that can be executed in browser sessions. Tasks support
        versioning with draft and published versions.

        Args:
          language: Programming language for the task

          name: Task name (letters, numbers, hyphens, and underscores only)

          browser_configuration: Browser configuration for task execution

          code: Base64 encoded task code (optional)

          description: Optional description of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/task",
            body=maybe_transform(
                {
                    "language": language,
                    "name": name,
                    "browser_configuration": browser_configuration,
                    "code": code,
                    "description": description,
                },
                task_create_params.TaskCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskCreateResponse,
        )

    def list(
        self,
        *,
        limit: str | Omit = omit,
        page: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskListResponse:
        """Retrieves a paginated list of all tasks for the authenticated team.

        Tasks are
        returned with their latest version information and metadata.

        Args:
          limit: Number of tasks per page

          page: Page number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/task",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            cast_to=TaskListResponse,
        )


class AsyncTaskResource(AsyncAPIResource):
    @cached_property
    def run(self) -> AsyncRunResource:
        return AsyncRunResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return AsyncTaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return AsyncTaskResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        language: Literal["typescript"],
        name: str,
        browser_configuration: task_create_params.BrowserConfiguration | Omit = omit,
        code: str | Omit = omit,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskCreateResponse:
        """Creates a new task or updates an existing task with the same name.

        Tasks are
        reusable code snippets that can be executed in browser sessions. Tasks support
        versioning with draft and published versions.

        Args:
          language: Programming language for the task

          name: Task name (letters, numbers, hyphens, and underscores only)

          browser_configuration: Browser configuration for task execution

          code: Base64 encoded task code (optional)

          description: Optional description of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/task",
            body=await async_maybe_transform(
                {
                    "language": language,
                    "name": name,
                    "browser_configuration": browser_configuration,
                    "code": code,
                    "description": description,
                },
                task_create_params.TaskCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskCreateResponse,
        )

    async def list(
        self,
        *,
        limit: str | Omit = omit,
        page: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskListResponse:
        """Retrieves a paginated list of all tasks for the authenticated team.

        Tasks are
        returned with their latest version information and metadata.

        Args:
          limit: Number of tasks per page

          page: Page number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/task",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            cast_to=TaskListResponse,
        )


class TaskResourceWithRawResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.create = to_raw_response_wrapper(
            task.create,
        )
        self.list = to_raw_response_wrapper(
            task.list,
        )

    @cached_property
    def run(self) -> RunResourceWithRawResponse:
        return RunResourceWithRawResponse(self._task.run)


class AsyncTaskResourceWithRawResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.create = async_to_raw_response_wrapper(
            task.create,
        )
        self.list = async_to_raw_response_wrapper(
            task.list,
        )

    @cached_property
    def run(self) -> AsyncRunResourceWithRawResponse:
        return AsyncRunResourceWithRawResponse(self._task.run)


class TaskResourceWithStreamingResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.create = to_streamed_response_wrapper(
            task.create,
        )
        self.list = to_streamed_response_wrapper(
            task.list,
        )

    @cached_property
    def run(self) -> RunResourceWithStreamingResponse:
        return RunResourceWithStreamingResponse(self._task.run)


class AsyncTaskResourceWithStreamingResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.create = async_to_streamed_response_wrapper(
            task.create,
        )
        self.list = async_to_streamed_response_wrapper(
            task.list,
        )

    @cached_property
    def run(self) -> AsyncRunResourceWithStreamingResponse:
        return AsyncRunResourceWithStreamingResponse(self._task.run)
