"""
This class provides functions for interacting with the Linode Metadata service.
It includes methods for retrieving and updating metadata information.
"""

import base64
import datetime
import json
from datetime import datetime, timedelta
from importlib.metadata import version
from typing import Any, Callable, Optional, Union
import sys

import httpx
from httpx import Response, TimeoutException

from linode_metadata import NetworkResponse
from linode_metadata.objects.error import ApiError, ApiTimeoutError
from linode_metadata.objects.instance import InstanceResponse
from linode_metadata.objects.ssh_keys import SSHKeysResponse
from linode_metadata.objects.token import MetadataToken

BASE_URL = "http://169.254.169.254/v1"
DEFAULT_API_TIMEOUT = 10


class MetadataClient:
    """
    The main interface to the Linode Metadata Service.

    :param base_url: The base URL for Metadata API requests.  Generally, you shouldn't
                     change this.
    :type base_url: str
    :param user_agent: What to append to the User Agent of all requests made
                       by this client.  Setting this allows Linode's internal
                       monitoring applications to track the usage of your
                       application.  Setting this is not necessary, but some
                       applications may desire this behavior.
    :type user_agent: str
    """

    def __init__(
        self,
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
        The main interface to the Linode Metadata Service.

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
        self.session = httpx.Client()
        self._append_user_agent = user_agent
        self.timeout = timeout

        self._token = token

        self._managed_token = managed_token
        self._managed_token_expiry_seconds = managed_token_expiry_seconds
        self._managed_token_expiry = None

        self.check_connection()

        if managed_token:
            self.refresh_token(
                expiry_seconds=self._managed_token_expiry_seconds,
            )

        self.debug = debug
        self.debug_file = sys.stderr if debug_file is None else open(debug_file, "w")

    @property
    def _user_agent(self):
        append_user_agent = (
            f"{self._append_user_agent} " if self._append_user_agent else ""
        )
        return (
            f"{append_user_agent} "
            f"linode-py-metadata/{version('linode_metadata')}"
        ).strip()

    def check_connection(self):
        """
        Checks for a connection to the Metadata Service, ensuring customer is inside a Linode.
        """
        try:
            httpx.get(self.base_url, timeout=self.timeout)
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
            self._token is None or datetime.now() >= self._managed_token_expiry
        ):
            self.refresh_token(
                expiry_seconds=self._managed_token_expiry_seconds
            )

        if self._token is None:
            raise RuntimeError(
                "No token provided. Please use "
                "MetadataClient.refresh_token() to create new token."
            )

    def _get_http_method(
        self, method: str
    ) -> Optional[Callable[..., Response]]:
        """
        Return a callable for making the API call.
        """
        method_map = {
            "GET": self.session.get,
            "POST": self.session.post,
            "PUT": self.session.put,
            "DELETE": self.session.delete,
        }
        return method_map.get(method.upper())

    def _api_call(
        self,
        method: str,
        endpoint: str,
        content_type="application/json",
        body=None,
        additional_headers=None,
        authenticated=True,
    ) -> Union[str, dict]:
        if authenticated:
            self._validate_token()

        method_func = self._get_http_method(method)
        if method_func is None:
            raise ValueError(f"Invalid API request method: {method}")

        headers = {
            "Content-Type": content_type,
            "Accept": content_type,
            "User-Agent": self._user_agent,
        }

        if authenticated:
            headers["Metadata-Token"] = self._token

        if additional_headers is not None:
            headers.update(additional_headers)

        url = f"{self.base_url}{endpoint}"

        request_params = {
            "url": url,
            "headers": headers,
            "timeout": self.timeout,
        }

        if method.lower() in ("put", "post") and body:
            request_params["data"] = json.dumps(body)

        if self.debug:
            self._print_request_debug_info(request_params)

        resp = method_func(**request_params)

        if self.debug:
            self._print_response_debug_info(resp)

        if 399 < resp.status_code < 600:
            j = None
            error_msg = f"{resp.status_code}: "

            # Don't raise if we don't get JSON back
            try:
                j = resp.json()
                if "errors" in j:
                    error_fragments = [
                        f"{e['reason']};" for e in j["errors"] if "reason" in e
                    ]
                    error_msg += " ".join(error_fragments)
            except:
                pass

            raise ApiError(error_msg, status=resp.status_code, json=j)

        return self._parse_response_body(resp, content_type)

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

    def generate_token(self, expiry_seconds=3600) -> MetadataToken:
        """
        Generates a token for accessing Metadata Service.
        NOTE: The generated token will NOT be implicitly
        applied to the MetadataClient.
        """

        created = datetime.now()

        resp = self._api_call(
            "PUT",
            "/token",
            content_type="text/plain",
            additional_headers={
                "Metadata-Token-Expiry-Seconds": str(expiry_seconds)
            },
            authenticated=False,
        )

        return MetadataToken(
            token=resp, expiry_seconds=expiry_seconds, created=created
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

    def get_user_data(self) -> str:
        """
        Returns the user data configured on your running Linode instance.
        """
        resp = self._api_call("GET", "/user-data", content_type="text/plain")
        return base64.b64decode(resp).decode("utf-8")

    def get_instance(self) -> InstanceResponse:
        """
        Returns information about the running Linode instance.
        """
        resp = self._api_call("GET", "/instance")
        return InstanceResponse(json_data=resp)

    def get_network(self) -> NetworkResponse:
        """
        Returns information about the running Linode instance’s network configuration.
        """
        resp = self._api_call("GET", "/network")
        return NetworkResponse(json_data=resp)

    def get_ssh_keys(self) -> SSHKeysResponse:
        """
        Get a mapping of public SSH Keys configured on your running Linode instance.
        """
        resp = self._api_call("GET", "/ssh-keys")
        return SSHKeysResponse(json_data=resp)

    def _print_request_debug_info(self, request_params):
        """
        Prints debug info for an HTTP request
        """
        for k,v in request_params.items():
            if k == "headers":
                for hk, hv in v.items():
                    print(f"> {hk}: {hv}", file=self.debug_file)
            else:
                print(f"> {k}: {v}", file=self.debug_file)

        print("> ", file=self.debug_file)

    def _print_response_debug_info(self, response):
        """
        Prints debug info for a response from requests
        """
        # these come back as ints, convert to HTTP version
        http_version = response.raw.version / 10

        print(
            f"< HTTP/{http_version:.1f} {response.status_code} {response.reason}",
            file=self.debug_file,
        )
        for k, v in response.headers.items():
            print(f"< {k}: {v}", file=self.debug_file)
        print("< ", file=self.debug_file)