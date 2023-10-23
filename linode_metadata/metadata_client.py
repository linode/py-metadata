"""
This class provides functions for interacting with the Linode Metadata service.
It includes methods for retrieving and updating metadata information.
"""
import base64
import datetime
import json
from datetime import datetime
from importlib.metadata import version
from typing import Any, Union

import requests
from requests import ConnectTimeout, Response

from linode_metadata import NetworkResponse
from linode_metadata.objects.error import ApiError
from linode_metadata.objects.instance import InstanceResponse
from linode_metadata.objects.ssh_keys import SSHKeysResponse
from linode_metadata.objects.token import MetadataToken


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
        base_url="http://169.254.169.254/v1",
        user_agent=None,
        token=None,
        init_token=True,
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
        """

        self.base_url = base_url
        self.session = requests.Session()
        self._append_user_agent = user_agent
        self._token = token

        self.check_connection()

        if init_token:
            self.refresh_token()

    @property
    def _user_agent(self):
        append_user_agent = (
            f"{self._append_user_agent} " if self._append_user_agent else ""
        )
        default_user_agent = requests.utils.default_user_agent()
        return f"{append_user_agent}python-linode_api4/{package_version} {default_user_agent}"

    def check_connection(self):
        """
        Checks for a connection to the Metadata Service, ensuring customer is inside a Linode.
        """
        try:
            requests.get(self.base_url, timeout=10)
        except ConnectTimeout:
            raise ConnectTimeout(
                "Can't access Metadata service. Please verify that you are inside a Linode."
            )

    def _api_call(
        self,
        method: str,
        endpoint: str,
        content_type="application/json",
        body=None,
        additional_headers=None,
        authenticated=True,
    ) -> Union[str, dict]:
        if authenticated and self._token is None:
            raise RuntimeError(
                "No token provided. Please use MetadataClient.refresh_token() to create new token."
            )

        method_map = {
            "GET": self.session.get,
            "POST": self.session.post,
            "PUT": self.session.put,
            "DELETE": self.session.delete,
        }

        method = method.upper()

        if method not in method_map:
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
        body = body if body is None else json.dumps(body)

        resp = method_map[method](url, headers=headers, data=body)

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
            "application/json": lambda: response.json(),
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
        """
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
            token=resp, expiry_seconds=expiry_seconds, created=datetime.now()
        )

    def refresh_token(self, expiry_seconds: int = 3600):
        """
        Regenerates a Metadata Service token.
        """
        result = self.generate_token(expiry_seconds=expiry_seconds)
        self.set_token(result.token)

    def set_token(self, token: str):
        """
        Sets the passed token as token for client.
        """
        self._token = token

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
