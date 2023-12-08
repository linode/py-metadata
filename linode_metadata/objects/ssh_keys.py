"""
Data classes related to SSH Keys.
"""
from dataclasses import dataclass
from typing import List

from .response_base import ResponseBase


@dataclass(init=False)
class SSHKeysUser(ResponseBase):
    """
    A user's SSH Key information.
    """

    root: List[str]


@dataclass(init=False)
class SSHKeysResponse(ResponseBase):
    """
    The users' and their SSH Keys associated with a Linode instance.
    """

    users: SSHKeysUser
