# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Dict, Mapping, cast
from typing_extensions import Self, Literal, override

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
from .resources import devices, releases, webhooks, deployments, config_instances
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import MiruError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Miru",
    "AsyncMiru",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "prod": "https://configs.api.miruml.com/v1",
    "uat": "https://uat.api.miruml.com/v1",
    "staging": "https://configs.dev.api.miruml.com/v1",
    "local": "http://localhost:8080/v1",
}


class Miru(SyncAPIClient):
    config_instances: config_instances.ConfigInstancesResource
    deployments: deployments.DeploymentsResource
    devices: devices.DevicesResource
    releases: releases.ReleasesResource
    webhooks: webhooks.WebhooksResource
    with_raw_response: MiruWithRawResponse
    with_streaming_response: MiruWithStreamedResponse

    # client options
    api_key: str
    host: str
    version: str

    _environment: Literal["prod", "uat", "staging", "local"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        host: str | None = None,
        version: str | None = None,
        environment: Literal["prod", "uat", "staging", "local"] | NotGiven = not_given,
        base_url: str | httpx.URL | None | NotGiven = not_given,
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
        """Construct a new synchronous Miru client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `MIRU_SERVER_API_KEY`
        - `host` from `MIRU_SERVER_HOST`
        - `version` from `MIRU_SERVER_VERSION`
        """
        if api_key is None:
            api_key = os.environ.get("MIRU_SERVER_API_KEY")
        if api_key is None:
            raise MiruError(
                "The api_key client option must be set either by passing api_key to the client or by setting the MIRU_SERVER_API_KEY environment variable"
            )
        self.api_key = api_key

        if host is None:
            host = os.environ.get("MIRU_SERVER_HOST") or "configs.api.miruml.com"
        self.host = host

        if version is None:
            version = os.environ.get("MIRU_SERVER_VERSION") or "v1"
        self.version = version

        self._environment = environment

        base_url_env = os.environ.get("MIRU_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `MIRU_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "prod"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

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

        self.config_instances = config_instances.ConfigInstancesResource(self)
        self.deployments = deployments.DeploymentsResource(self)
        self.devices = devices.DevicesResource(self)
        self.releases = releases.ReleasesResource(self)
        self.webhooks = webhooks.WebhooksResource(self)
        self.with_raw_response = MiruWithRawResponse(self)
        self.with_streaming_response = MiruWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"X-API-Key": api_key}

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
        host: str | None = None,
        version: str | None = None,
        environment: Literal["prod", "uat", "staging", "local"] | None = None,
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
            host=host or self.host,
            version=version or self.version,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
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


class AsyncMiru(AsyncAPIClient):
    config_instances: config_instances.AsyncConfigInstancesResource
    deployments: deployments.AsyncDeploymentsResource
    devices: devices.AsyncDevicesResource
    releases: releases.AsyncReleasesResource
    webhooks: webhooks.AsyncWebhooksResource
    with_raw_response: AsyncMiruWithRawResponse
    with_streaming_response: AsyncMiruWithStreamedResponse

    # client options
    api_key: str
    host: str
    version: str

    _environment: Literal["prod", "uat", "staging", "local"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        host: str | None = None,
        version: str | None = None,
        environment: Literal["prod", "uat", "staging", "local"] | NotGiven = not_given,
        base_url: str | httpx.URL | None | NotGiven = not_given,
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
        """Construct a new async AsyncMiru client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `MIRU_SERVER_API_KEY`
        - `host` from `MIRU_SERVER_HOST`
        - `version` from `MIRU_SERVER_VERSION`
        """
        if api_key is None:
            api_key = os.environ.get("MIRU_SERVER_API_KEY")
        if api_key is None:
            raise MiruError(
                "The api_key client option must be set either by passing api_key to the client or by setting the MIRU_SERVER_API_KEY environment variable"
            )
        self.api_key = api_key

        if host is None:
            host = os.environ.get("MIRU_SERVER_HOST") or "configs.api.miruml.com"
        self.host = host

        if version is None:
            version = os.environ.get("MIRU_SERVER_VERSION") or "v1"
        self.version = version

        self._environment = environment

        base_url_env = os.environ.get("MIRU_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `MIRU_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "prod"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

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

        self.config_instances = config_instances.AsyncConfigInstancesResource(self)
        self.deployments = deployments.AsyncDeploymentsResource(self)
        self.devices = devices.AsyncDevicesResource(self)
        self.releases = releases.AsyncReleasesResource(self)
        self.webhooks = webhooks.AsyncWebhooksResource(self)
        self.with_raw_response = AsyncMiruWithRawResponse(self)
        self.with_streaming_response = AsyncMiruWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"X-API-Key": api_key}

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
        host: str | None = None,
        version: str | None = None,
        environment: Literal["prod", "uat", "staging", "local"] | None = None,
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
            host=host or self.host,
            version=version or self.version,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
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


class MiruWithRawResponse:
    def __init__(self, client: Miru) -> None:
        self.config_instances = config_instances.ConfigInstancesResourceWithRawResponse(client.config_instances)
        self.deployments = deployments.DeploymentsResourceWithRawResponse(client.deployments)
        self.devices = devices.DevicesResourceWithRawResponse(client.devices)
        self.releases = releases.ReleasesResourceWithRawResponse(client.releases)


class AsyncMiruWithRawResponse:
    def __init__(self, client: AsyncMiru) -> None:
        self.config_instances = config_instances.AsyncConfigInstancesResourceWithRawResponse(client.config_instances)
        self.deployments = deployments.AsyncDeploymentsResourceWithRawResponse(client.deployments)
        self.devices = devices.AsyncDevicesResourceWithRawResponse(client.devices)
        self.releases = releases.AsyncReleasesResourceWithRawResponse(client.releases)


class MiruWithStreamedResponse:
    def __init__(self, client: Miru) -> None:
        self.config_instances = config_instances.ConfigInstancesResourceWithStreamingResponse(client.config_instances)
        self.deployments = deployments.DeploymentsResourceWithStreamingResponse(client.deployments)
        self.devices = devices.DevicesResourceWithStreamingResponse(client.devices)
        self.releases = releases.ReleasesResourceWithStreamingResponse(client.releases)


class AsyncMiruWithStreamedResponse:
    def __init__(self, client: AsyncMiru) -> None:
        self.config_instances = config_instances.AsyncConfigInstancesResourceWithStreamingResponse(
            client.config_instances
        )
        self.deployments = deployments.AsyncDeploymentsResourceWithStreamingResponse(client.deployments)
        self.devices = devices.AsyncDevicesResourceWithStreamingResponse(client.devices)
        self.releases = releases.AsyncReleasesResourceWithStreamingResponse(client.releases)


Client = Miru

AsyncClient = AsyncMiru
