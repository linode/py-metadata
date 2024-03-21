"""
This class provides functions for interacting with the Linode Metadata service.
It includes methods for retrieving and updating metadata information.
"""

from __future__ import annotations

import base64
import json
import logging
from abc import ABC
from collections.abc import Awaitable
from datetime import datetime, timedelta
from importlib.metadata import version
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, Optional, Type, Union

import httpx
from httpx import Response, TimeoutException

from linode_metadata.constants import LOGGER_NAME
from linode_metadata.objects.error import ApiError, ApiTimeoutError
from linode_metadata.objects.instance import InstanceResponse
from linode_metadata.objects.networking import NetworkResponse
from linode_metadata.objects.ssh_keys import SSHKeysResponse
from linode_metadata.objects.token import MetadataToken
from linode_metadata.watcher import AsyncMetadataWatcher, MetadataWatcher

BASE_URL = "http://169.254.169.254/v1"
DEFAULT_API_TIMEOUT = 10.0


class BaseMetadataClient(ABC):
    """
    The base client of Linode Metadata Service that holds shared components
    between MetadataClient and AsyncMetadataClient.
    """

    watcher: Optional[Union[AsyncMetadataWatcher, MetadataWatcher]]
    _watcher_cls: Type[Union[AsyncMetadataWatcher, MetadataWatcher]]
    _managed_token_expiry: Optional[datetime]

    def __init__(
        self,
        client: Union[httpx.AsyncClient, httpx.Client],
        base_url: str = BASE_URL,
        user_agent: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = DEFAULT_API_TIMEOUT,
        managed_token: bool = True,
        managed_token_expiry_seconds: float = 3600.0,
        debug: bool = False,
        debug_file: Optional[Union[Path, str]] = None,
    ):
        """
        The constructor of the base client of Linode Metadata Service. This
        client should not be used directly, please use MetadataClient or
        AsyncMetadataClient instead.

        :param base_url: The base URL for Metadata API requests.  Generally, you shouldn't
                         change this.
        :type base_url: str
        :param user_agent: What to append to the User Agent of all requests made
                           by this client.  Setting this allows Linode's internal
                           monitoring applications to track the usage of your
                           application.  Setting this is not necessary, but some
                           applications may desire this behavior.
        :type user_agent: str
        :param token: An existing token to use with this client. This field cannot
                      be specified when token management is enabled.
        :type token: Optional[str]
        :param timeout: Timeout of an API call in seconds.
        :type timeout: float
        :param managed_token: If true, the token for this client will be automatically
                              generated and refreshed.
        :type managed_token: bool
        :type managed_token_expiry_seconds: The number of seconds until a managed token
                                            should expire. (Default 3600)
        :type managed_token_expiry_seconds: int
        :param debug: Enables debug mode if set to True.
        :type debug: bool
        :param debug_file: The file location to output the debug logs.
                            Default to sys.stderr if not specified.
        :type debug_file: str
        """

        if token is not None and managed_token:
            raise ValueError(
                "Token cannot be specified with token management is enabled"
            )

        self.base_url = base_url
        self._append_user_agent = user_agent
        self.timeout = timeout
        self._debug = debug
        if debug:
            self._logger = logging.getLogger(LOGGER_NAME)
            self._logger.setLevel(logging.DEBUG)
            handler: logging.Handler = (
                logging.FileHandler(debug_file)
                if debug_file
                else logging.StreamHandler()
            )
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

        self._token = token
        self.client = client

        self._managed_token = managed_token
        self._managed_token_expiry_seconds = managed_token_expiry_seconds
        self._managed_token_expiry = None

    @staticmethod
    def _parse_response_body(response: Response, content_type: str) -> Any:
        handlers = {
            "application/json": response.json,
            "text/plain": lambda: response.content,
        }

        if response.status_code == 204:
            return None

        handler = handlers.get(content_type.lower())
        if handler is None:
            raise ValueError(f"Invalid Content-Type: {content_type}")

        return handler()

    def _get_http_method(
        self, method: str
    ) -> Optional[Callable[..., Union[Response, Awaitable[Response]]]]:
        """
        Return a callable for making the API call.
        """
        if not self.client:
            raise RuntimeError("HTTP client is not defined")

        method_map = {
            "GET": self.client.get,
            "POST": self.client.post,
            "PUT": self.client.put,
            "DELETE": self.client.delete,
        }
        return method_map.get(method.upper())

    def _prepare_headers(
        self,
        method: str,
        content_type: str,
        additional_headers: dict,
        authenticated: bool,
    ):
        headers = {
            "Accept": content_type,
            "User-Agent": self._user_agent,
        }

        if method.lower() in ("put", "post"):
            headers["Content-Type"] = content_type

        if authenticated:
            headers["Metadata-Token"] = self._token

        if additional_headers is not None:
            headers.update(additional_headers)

        return headers

    def _prepare_url(self, endpoint: str):
        return f"{self.base_url}{endpoint}"

    def _get_api_call_params(
        self, url: str, headers: dict, method: str, body: dict
    ):
        request_params = {
            "url": url,
            "headers": headers,
            "timeout": self.timeout,
        }

        if method.lower() in ("put", "post") and body:
            request_params["data"] = json.dumps(body)

        return request_params

    def _check_response(self, response: Response):
        if 399 < response.status_code < 600:
            j = None
            error_msg = f"{response.status_code}: "

            # Don't raise if we don't get JSON back
            try:
                j = response.json()
                if "errors" in j:
                    error_fragments = [
                        f"{e['reason']};" for e in j["errors"] if "reason" in e
                    ]
                    error_msg += " ".join(error_fragments)
            except:
                pass

            raise ApiError(error_msg, status=response.status_code, json=j)

    def set_token(self, token: str):
        """
        Sets the passed token as token for client.
        """
        self._token = token

    @property
    def token(self):
        """
        Gets the token currently used by this client.
        """
        return self._token

    @property
    def _user_agent(self):
        append_user_agent = (
            f"{self._append_user_agent} " if self._append_user_agent else ""
        )
        return (
            f"{append_user_agent} "
            f"linode-py-metadata/{version('linode_metadata')}"
        ).strip()

    def get_watcher(
        self,
        default_poll_interval: Optional[Union[timedelta, float, int]] = None,
    ) -> Union[AsyncMetadataWatcher, MetadataWatcher]:
        """
        Get a watcher instance with this metadata client.

        :param default_poll_interval: The default time interval for polling Linode
                                        metadata services.
        :type default_poll_interval: Optional[Union[timedelta, float, int]]
        :return: A watcher instance.
        :rtype: Union[AsyncMetadataWatcher, MetadataWatcher]
        """
        if default_poll_interval is None:
            default_poll_interval = timedelta(minutes=1)

        if not hasattr(self, "watcher") or self.watcher is None:
            self.watcher = self._watcher_cls(
                client=self,  # type: ignore
                default_poll_interval=default_poll_interval,
                debug=self._debug,
            )
        else:
            self.watcher.set_default_poll_interval(default_poll_interval)

        return self.watcher

    def _log_request_debug_info(self, request_params: dict):
        """
        Logging debug info for an HTTP request
        """
        for k, v in request_params.items():
            if k == "headers":
                for hk, hv in v.items():
                    self._logger.debug("> %s: %s", hk, hv)
            else:
                self._logger.debug("> %s: %s", k, v)

        self._logger.debug("> ")

    def _log_response_debug_info(self, response: Response):
        """
        Logging debug info for a response from requests
        """
        self._logger.debug(
            "< %s %s %s",
            response.http_version,
            response.status_code,
            response.reason_phrase,
        )
        for k, v in response.headers.items():
            self._logger.debug("< %s: %s", k, v)

        self._logger.debug("< ")


class MetadataClient(BaseMetadataClient):
    """
    The main sync client of the Linode Metadata Service.
    """

    watcher: Optional[MetadataWatcher]
    _watcher_cls: Type[MetadataWatcher]
    client: httpx.Client

    def __init__(
        self,
        client: Optional[httpx.Client] = None,
        base_url=BASE_URL,
        user_agent=None,
        token=None,
        timeout=DEFAULT_API_TIMEOUT,
        managed_token=True,
        managed_token_expiry_seconds=3600,
        debug=False,
        debug_file=None,
    ):
        """
        The constructor of the client of Linode Metadata Service.

        :param base_url: The base URL for Metadata API requests.  Generally, you shouldn't
                         change this.
        :type base_url: str
        :param user_agent: What to append to the User Agent of all requests made
                           by this client.  Setting this allows Linode's internal
                           monitoring applications to track the usage of your
                           application.  Setting this is not necessary, but some
                           applications may desire this behavior.
        :type user_agent: str
        :param token: An existing token to use with this client. This field cannot
                      be specified when token management is enabled.
        :type token: Optional[str]
        :param timeout: Timeout of an API call in seconds.
        :type timeout: float
        :param managed_token: If true, the token for this client will be automatically
                              generated and refreshed.
        :type managed_token: bool
        :param managed_token_expiry_seconds: The number of seconds until a managed token
                                            should expire. (Default 3600)
        :type managed_token_expiry_seconds: int
        :param debug: Enables debug mode if set to True.
        :type debug: bool
        :param debug_file: The file location to output the debug logs.
                            Default to sys.stderr if not specified.
        :type debug_file: str
        """

        if not client:
            client = httpx.Client()

        self._watcher_cls = MetadataWatcher

        super().__init__(
            client=client,
            base_url=base_url,
            user_agent=user_agent,
            token=token,
            timeout=timeout,
            managed_token=managed_token,
            managed_token_expiry_seconds=managed_token_expiry_seconds,
            debug=debug,
            debug_file=debug_file,
        )

    def check_connection(self):
        """
        Checks for a connection to the Metadata Service, ensuring customer is inside a Linode.
        """
        try:
            self.client.get(self.base_url, timeout=self.timeout)
        except TimeoutException as e:
            raise ApiTimeoutError(
                "Can't access Metadata service. "
                "Please verify that you are inside a Linode."
            ) from e

    def _validate_token(self):
        """
        Check whether the token is valid. Refresh the token if
        it's expired and managed by this package.
        """
        # We should implicitly refresh the token if the user is enrolled in
        # token management and the token has expired.
        if self._managed_token and (
            self._token is None
            or (
                self._managed_token_expiry
                and datetime.now() >= self._managed_token_expiry
            )
        ):
            self.refresh_token(
                expiry_seconds=self._managed_token_expiry_seconds
            )

        if self._token is None:
            raise RuntimeError(
                "No token provided. Please use "
                "MetadataClient.refresh_token() to create new token."
            )

    def _api_call(
        self,
        method: str,
        endpoint: str,
        content_type="application/json",
        body=None,
        additional_headers=None,
        authenticated=True,
    ) -> Any:
        if authenticated:
            self._validate_token()

        method_func = self._get_http_method(method)
        if method_func is None:
            raise ValueError(f"Invalid API request method: {method}")

        headers = self._prepare_headers(
            method,
            content_type,
            additional_headers,
            authenticated,
        )

        url = self._prepare_url(endpoint)
        request_params = self._get_api_call_params(url, headers, method, body)

        if self._debug:
            self._log_request_debug_info(request_params)

        response = method_func(**request_params)

        if self._debug:
            self._log_response_debug_info(response)

        self._check_response(response)

        return self._parse_response_body(response, content_type)

    def generate_token(self, expiry_seconds=3600) -> MetadataToken:
        """
        Generates a token for accessing Metadata Service.
        NOTE: The generated token will NOT be implicitly
        applied to the MetadataClient.
        """

        created = datetime.now()

        response = self._api_call(
            "PUT",
            "/token",
            content_type="text/plain",
            additional_headers={
                "Metadata-Token-Expiry-Seconds": str(expiry_seconds)
            },
            authenticated=False,
        )

        return MetadataToken(
            token=response, expiry_seconds=expiry_seconds, created=created
        )

    def refresh_token(self, expiry_seconds: int = 3600) -> MetadataToken:
        """
        Regenerates a Metadata Service token.
        """

        result = self.generate_token(expiry_seconds=expiry_seconds)

        self.set_token(result.token)
        self._managed_token_expiry = result.created + timedelta(
            seconds=expiry_seconds
        )

        return result

    def get_user_data(self) -> str:
        """
        Returns the user data configured on your running Linode instance.
        """
        response = self._api_call(
            "GET", "/user-data", content_type="text/plain"
        )
        return base64.b64decode(response).decode("utf-8")

    def get_instance(self) -> InstanceResponse:
        """
        Returns information about the running Linode instance.
        """
        response = self._api_call("GET", "/instance")
        return InstanceResponse(json_data=response)

    def get_network(self) -> NetworkResponse:
        """
        Returns information about the running Linode instance’s network configuration.
        """
        response = self._api_call("GET", "/network")
        return NetworkResponse(json_data=response)

    def get_ssh_keys(self) -> SSHKeysResponse:
        """
        Get a mapping of public SSH Keys configured on your running Linode instance.
        """
        response = self._api_call("GET", "/ssh-keys")
        return SSHKeysResponse(json_data=response)

    def close(self):
        """
        Close the embedded HTTP client in this metadata client.
        """
        self.client.close()

    def __enter__(self) -> MetadataClient:
        self.client.__enter__()
        if self._managed_token:
            self.refresh_token()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        self._token = None
        self.client.__exit__(exc_type, exc_value, traceback)


class AsyncMetadataClient(BaseMetadataClient):
    """
    The main async client of the Linode Metadata Service.
    """

    watcher: Optional[AsyncMetadataWatcher]
    _watcher_cls: Type[AsyncMetadataWatcher]
    client: httpx.AsyncClient

    def __init__(
        self,
        client: Optional[httpx.AsyncClient] = None,
        base_url: str = BASE_URL,
        user_agent: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = DEFAULT_API_TIMEOUT,
        managed_token: bool = True,
        managed_token_expiry_seconds: float = 3600.0,
        debug: bool = False,
        debug_file: Optional[Union[Path, str]] = None,
    ):
        """
        The constructor of the async client of Linode Metadata Service.

        :param base_url: The base URL for Metadata API requests. Generally, you shouldn't
                         change this.
        :type base_url: str
        :param user_agent: What to append to the User Agent of all requests made
                           by this client.  Setting this allows Linode's internal
                           monitoring applications to track the usage of your
                           application.  Setting this is not necessary, but some
                           applications may desire this behavior.
        :type user_agent: str
        :param token: An existing token to use with this client. This field cannot
                      be specified when token management is enabled.
        :type token: Optional[str]
        :param timeout: Timeout of an API call in seconds.
        :type timeout: float
        :param managed_token: If true, the token for this client will be automatically
                              generated and refreshed.
        :type managed_token: bool
        :param managed_token_expiry_seconds: The number of seconds until a managed token
                                            should expire. (Default 3600)
        :type managed_token_expiry_seconds: int
        :param debug: Enables debug mode if set to True.
        :type debug: bool
        :param debug_file: The file location to output the debug logs.
                            Default to sys.stderr if not specified.
        :type debug_file: str
        """

        if not client:
            client = httpx.AsyncClient()

        self._watcher_cls = AsyncMetadataWatcher

        super().__init__(
            client=client,
            base_url=base_url,
            user_agent=user_agent,
            token=token,
            timeout=timeout,
            managed_token=managed_token,
            managed_token_expiry_seconds=managed_token_expiry_seconds,
            debug=debug,
            debug_file=debug_file,
        )

    async def check_connection(self) -> None:
        """
        Checks for a connection to the Metadata Service, ensuring customer is inside a Linode.
        """
        try:
            await self.client.get(self.base_url, timeout=self.timeout)
        except TimeoutException as e:
            raise ApiTimeoutError(
                "Can't access Metadata service. "
                "Please verify that you are inside a Linode."
            ) from e

    async def _validate_token(self) -> None:
        """
        Check whether the token is valid. Refresh the token if
        it's expired and managed by this package.
        """
        # We should implicitly refresh the token if the user is enrolled in
        # token management and the token has expired.
        if self._managed_token and (
            self._token is None
            or (
                self._managed_token_expiry
                and datetime.now() >= self._managed_token_expiry
            )
        ):
            await self.refresh_token(
                expiry_seconds=self._managed_token_expiry_seconds
            )

        if self._token is None:
            raise RuntimeError(
                "No token provided. Please use "
                "MetadataClient.refresh_token() to create new token."
            )

    async def _api_call(
        self,
        method: str,
        endpoint: str,
        content_type="application/json",
        body=None,
        additional_headers=None,
        authenticated=True,
    ) -> Any:
        if authenticated:
            await self._validate_token()

        method_func = self._get_http_method(method)
        if method_func is None:
            raise ValueError(f"Invalid API request method: {method}")

        headers = self._prepare_headers(
            method,
            content_type,
            additional_headers,
            authenticated,
        )

        url = self._prepare_url(endpoint)
        request_params = self._get_api_call_params(url, headers, method, body)

        if self._debug:
            self._log_request_debug_info(request_params)

        response: Response = await method_func(**request_params)

        if self._debug:
            self._log_response_debug_info(response)

        self._check_response(response)

        return self._parse_response_body(response, content_type)

    async def generate_token(self, expiry_seconds=3600) -> MetadataToken:
        """
        Generates a token for accessing Metadata Service.
        NOTE: The generated token will NOT be implicitly
        applied to the MetadataClient.
        """

        created = datetime.now()

        response = await self._api_call(
            "PUT",
            "/token",
            content_type="text/plain",
            additional_headers={
                "Metadata-Token-Expiry-Seconds": str(expiry_seconds)
            },
            authenticated=False,
        )

        return MetadataToken(
            token=response, expiry_seconds=expiry_seconds, created=created
        )

    async def refresh_token(self, expiry_seconds: int = 3600) -> MetadataToken:
        """
        Regenerates a Metadata Service token.
        """

        result = await self.generate_token(expiry_seconds=expiry_seconds)

        self.set_token(result.token)
        self._managed_token_expiry = result.created + timedelta(
            seconds=expiry_seconds
        )

        return result

    async def get_user_data(self) -> str:
        """
        Returns the user data configured on your running Linode instance.
        """
        response = await self._api_call(
            "GET", "/user-data", content_type="text/plain"
        )
        return base64.b64decode(response).decode("utf-8")

    async def get_instance(self) -> InstanceResponse:
        """
        Returns information about the running Linode instance.
        """
        response = await self._api_call("GET", "/instance")
        return InstanceResponse(json_data=response)

    async def get_network(self) -> NetworkResponse:
        """
        Returns information about the running Linode instance’s network configuration.
        """
        response = await self._api_call("GET", "/network")
        return NetworkResponse(json_data=response)

    async def get_ssh_keys(self) -> SSHKeysResponse:
        """
        Get a mapping of public SSH Keys configured on your running Linode instance.
        """
        response = await self._api_call("GET", "/ssh-keys")
        return SSHKeysResponse(json_data=response)

    async def close(self):
        """
        Close the embedded HTTP client in this metadata client.
        """
        self.client.aclose()

    async def __aenter__(self) -> AsyncMetadataClient:
        await self.client.__aenter__()
        if self._managed_token:
            await self.refresh_token()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ):
        self._token = None
        await self.client.__aexit__(exc_type, exc_value, traceback)
