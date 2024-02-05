"""
Data classes related to SSH Keys.
"""

from dataclasses import dataclass
from typing import Dict, List

from .response_base import ResponseBase


@dataclass(init=False)
class SSHKeysResponse(ResponseBase):
    """
    The users' and their SSH Keys associated with a Linode instance.
    """

    users: Dict[str, List[str]]
