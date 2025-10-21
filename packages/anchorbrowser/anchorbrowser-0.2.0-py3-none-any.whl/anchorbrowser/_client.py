# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import agent, tools, events, browser, profiles, extensions, batch_sessions
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, AnchorbrowserError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.task import task
from .resources.sessions import sessions

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Anchorbrowser",
    "AsyncAnchorbrowser",
    "Client",
    "AsyncClient",
]


class Anchorbrowser(SyncAPIClient):
    profiles: profiles.ProfilesResource
    sessions: sessions.SessionsResource
    tools: tools.ToolsResource
    extensions: extensions.ExtensionsResource
    browser: browser.BrowserResource
    agent: agent.AgentResource
    events: events.EventsResource
    batch_sessions: batch_sessions.BatchSessionsResource
    task: task.TaskResource
    with_raw_response: AnchorbrowserWithRawResponse
    with_streaming_response: AnchorbrowserWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Anchorbrowser client instance.

        This automatically infers the `api_key` argument from the `ANCHORBROWSER_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("ANCHORBROWSER_API_KEY")
        if api_key is None:
            raise AnchorbrowserError(
                "The api_key client option must be set either by passing api_key to the client or by setting the ANCHORBROWSER_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("ANCHORBROWSER_BASE_URL")
        if base_url is None:
            base_url = f"https://api.anchorbrowser.io"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.profiles = profiles.ProfilesResource(self)
        self.sessions = sessions.SessionsResource(self)
        self.tools = tools.ToolsResource(self)
        self.extensions = extensions.ExtensionsResource(self)
        self.browser = browser.BrowserResource(self)
        self.agent = agent.AgentResource(self)
        self.events = events.EventsResource(self)
        self.batch_sessions = batch_sessions.BatchSessionsResource(self)
        self.task = task.TaskResource(self)
        self.with_raw_response = AnchorbrowserWithRawResponse(self)
        self.with_streaming_response = AnchorbrowserWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"anchor-api-key": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncAnchorbrowser(AsyncAPIClient):
    profiles: profiles.AsyncProfilesResource
    sessions: sessions.AsyncSessionsResource
    tools: tools.AsyncToolsResource
    extensions: extensions.AsyncExtensionsResource
    browser: browser.AsyncBrowserResource
    agent: agent.AsyncAgentResource
    events: events.AsyncEventsResource
    batch_sessions: batch_sessions.AsyncBatchSessionsResource
    task: task.AsyncTaskResource
    with_raw_response: AsyncAnchorbrowserWithRawResponse
    with_streaming_response: AsyncAnchorbrowserWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncAnchorbrowser client instance.

        This automatically infers the `api_key` argument from the `ANCHORBROWSER_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("ANCHORBROWSER_API_KEY")
        if api_key is None:
            raise AnchorbrowserError(
                "The api_key client option must be set either by passing api_key to the client or by setting the ANCHORBROWSER_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("ANCHORBROWSER_BASE_URL")
        if base_url is None:
            base_url = f"https://api.anchorbrowser.io"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.profiles = profiles.AsyncProfilesResource(self)
        self.sessions = sessions.AsyncSessionsResource(self)
        self.tools = tools.AsyncToolsResource(self)
        self.extensions = extensions.AsyncExtensionsResource(self)
        self.browser = browser.AsyncBrowserResource(self)
        self.agent = agent.AsyncAgentResource(self)
        self.events = events.AsyncEventsResource(self)
        self.batch_sessions = batch_sessions.AsyncBatchSessionsResource(self)
        self.task = task.AsyncTaskResource(self)
        self.with_raw_response = AsyncAnchorbrowserWithRawResponse(self)
        self.with_streaming_response = AsyncAnchorbrowserWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"anchor-api-key": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AnchorbrowserWithRawResponse:
    def __init__(self, client: Anchorbrowser) -> None:
        self.profiles = profiles.ProfilesResourceWithRawResponse(client.profiles)
        self.sessions = sessions.SessionsResourceWithRawResponse(client.sessions)
        self.tools = tools.ToolsResourceWithRawResponse(client.tools)
        self.extensions = extensions.ExtensionsResourceWithRawResponse(client.extensions)
        self.browser = browser.BrowserResourceWithRawResponse(client.browser)
        self.agent = agent.AgentResourceWithRawResponse(client.agent)
        self.events = events.EventsResourceWithRawResponse(client.events)
        self.batch_sessions = batch_sessions.BatchSessionsResourceWithRawResponse(client.batch_sessions)
        self.task = task.TaskResourceWithRawResponse(client.task)


class AsyncAnchorbrowserWithRawResponse:
    def __init__(self, client: AsyncAnchorbrowser) -> None:
        self.profiles = profiles.AsyncProfilesResourceWithRawResponse(client.profiles)
        self.sessions = sessions.AsyncSessionsResourceWithRawResponse(client.sessions)
        self.tools = tools.AsyncToolsResourceWithRawResponse(client.tools)
        self.extensions = extensions.AsyncExtensionsResourceWithRawResponse(client.extensions)
        self.browser = browser.AsyncBrowserResourceWithRawResponse(client.browser)
        self.agent = agent.AsyncAgentResourceWithRawResponse(client.agent)
        self.events = events.AsyncEventsResourceWithRawResponse(client.events)
        self.batch_sessions = batch_sessions.AsyncBatchSessionsResourceWithRawResponse(client.batch_sessions)
        self.task = task.AsyncTaskResourceWithRawResponse(client.task)


class AnchorbrowserWithStreamedResponse:
    def __init__(self, client: Anchorbrowser) -> None:
        self.profiles = profiles.ProfilesResourceWithStreamingResponse(client.profiles)
        self.sessions = sessions.SessionsResourceWithStreamingResponse(client.sessions)
        self.tools = tools.ToolsResourceWithStreamingResponse(client.tools)
        self.extensions = extensions.ExtensionsResourceWithStreamingResponse(client.extensions)
        self.browser = browser.BrowserResourceWithStreamingResponse(client.browser)
        self.agent = agent.AgentResourceWithStreamingResponse(client.agent)
        self.events = events.EventsResourceWithStreamingResponse(client.events)
        self.batch_sessions = batch_sessions.BatchSessionsResourceWithStreamingResponse(client.batch_sessions)
        self.task = task.TaskResourceWithStreamingResponse(client.task)


class AsyncAnchorbrowserWithStreamedResponse:
    def __init__(self, client: AsyncAnchorbrowser) -> None:
        self.profiles = profiles.AsyncProfilesResourceWithStreamingResponse(client.profiles)
        self.sessions = sessions.AsyncSessionsResourceWithStreamingResponse(client.sessions)
        self.tools = tools.AsyncToolsResourceWithStreamingResponse(client.tools)
        self.extensions = extensions.AsyncExtensionsResourceWithStreamingResponse(client.extensions)
        self.browser = browser.AsyncBrowserResourceWithStreamingResponse(client.browser)
        self.agent = agent.AsyncAgentResourceWithStreamingResponse(client.agent)
        self.events = events.AsyncEventsResourceWithStreamingResponse(client.events)
        self.batch_sessions = batch_sessions.AsyncBatchSessionsResourceWithStreamingResponse(client.batch_sessions)
        self.task = task.AsyncTaskResourceWithStreamingResponse(client.task)


Client = Anchorbrowser

AsyncClient = AsyncAnchorbrowser
