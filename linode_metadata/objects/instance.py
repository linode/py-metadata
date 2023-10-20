from dataclasses import dataclass
from typing import List, Optional

from .response_base import ResponseBase


@dataclass(init=False)
class InstanceBackups(ResponseBase):
    enabled: bool
    status: Optional[List[str]]


@dataclass(init=False)
class InstanceSpecs(ResponseBase):
    vcpus: int
    disk: int
    memory: int
    transfer: int
    gpus: int


@dataclass(init=False)
class InstanceResponse(ResponseBase):
    host_uuid: str
    id: int
    label: str
    region: str
    tags: str
    type: str
    specs: InstanceSpecs
    backups: InstanceBackups
