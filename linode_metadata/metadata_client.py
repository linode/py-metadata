import base64
import datetime
import json
from typing import Any, Union

import pkg_resources
import requests
from requests import Response

from datetime import datetime

from requests import ConnectTimeout

from linode_metadata import NetworkResponse
from linode_metadata.objects.error import ApiError
from linode_metadata.objects.instance import InstanceResponse
from linode_metadata.objects.ssh_keys import SSHKeysResponse
from linode_metadata.objects.token import MetadataToken

package_version = pkg_resources.require("linode_api4")[0].version


class MetadataClient:
    def __init__(self, base_url="http://169.254.169.254/v1", user_agent=None, token=None, init_token=True):
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
        return "{}python-linode_api4/{} {}".format(
                "{} ".format(self._append_user_agent) if self._append_user_agent else "",
                package_version,
                requests.utils.default_user_agent()
        )
    
    def check_connection(self):
        try:
            requests.get(self.base_url, timeout=10)
        except ConnectTimeout:
            raise ConnectTimeout("Unable to reach Metadata service. Please check that you are running from inside a Linode.")

    def _api_call(self, method: str, endpoint: str, content_type="application/json", body=None, additional_headers=None, authenticated=True) -> Union[str, dict]:
        if authenticated and self._token is None:
            raise RuntimeError("No token has been provided. Please use MetadataClient.refresh_token() to generate a new token.")

        method_map = {
            "GET": self.session.get,
            "POST": self.session.post,
            "PUT": self.session.put,
            "DELETE": self.session.delete
        }

        method = method.upper()

        if method not in method_map:
            raise ValueError(f"Invalid API request method: {method}")

        headers = {
            "Content-Type": content_type,
            "Accept": content_type,
            "User-Agent": self._user_agent
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
                    error_fragments = [f"{e['reason']};" for e in j["errors"] if "reason" in e]
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
        resp = self._api_call(
            "PUT",
            "/token",
            content_type="text/plain",
            additional_headers={
                "Metadata-Token-Expiry-Seconds": str(expiry_seconds)
            },
            authenticated=False
        )

        return MetadataToken(
            token=resp,
            expiry_seconds=expiry_seconds,
            created=datetime.now()
        )

    def refresh_token(self, expiry_seconds: int = 3600):
        result = self.generate_token(expiry_seconds=expiry_seconds)
        self.set_token(result.token)

    def set_token(self, token: str):
        self._token = token

    def get_user_data(self) -> str:
        resp = self._api_call(
            "GET",
            "/user-data",
            content_type="text/plain"
        )
        return base64.b64decode(resp).decode('utf-8')

    def get_instance(self) -> InstanceResponse:
        resp = self._api_call(
            "GET",
            "/instance"
        )
        return resp #InstanceResponse(json_data=resp)

    def get_network(self) -> NetworkResponse:
        resp = self._api_call(
            "GET",
            "/network"
        )
        return NetworkResponse(json_data=resp)

    def get_ssh_keys(self) -> SSHKeysResponse:
        resp = self._api_call(
            "GET",
            "/ssh-keys"
        )
        return SSHKeysResponse(json_data=resp)