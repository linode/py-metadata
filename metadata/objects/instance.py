from dataclasses import dataclass, field
from typing import Optional, List

from .response_base import ResponseBase


@dataclass(init=False)
class InstanceBackups(ResponseBase):
    enabled: bool
    status: Optional[List[str]]


@dataclass(init=False)
class InstanceResponse(ResponseBase):
    local_hostname: str = field(metadata={"json": "local-hostname"})
    region: str
    type: str
    machine: str
    id: int
    instance_id: int = field(metadata={"json": "instance-id"})
    cpus: int
    memory: int
    disk: int
    backups: InstanceBackups