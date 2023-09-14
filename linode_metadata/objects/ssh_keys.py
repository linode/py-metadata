from dataclasses import dataclass
from typing import List

from .response_base import ResponseBase


@dataclass(init=False)
class SSHKeysUser(ResponseBase):
    root: List[str]
    

@dataclass(init=False)
class SSHKeysResponse(ResponseBase):
    users: SSHKeysUser