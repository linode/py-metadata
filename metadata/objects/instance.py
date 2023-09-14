from dataclasses import dataclass, field
from typing import Optional, List

from .response_base import ResponseBase


@dataclass(init=False)
class InstanceBackups(ResponseBase):
    enabled: bool
    status: Optional[List[str]]


@dataclass(init=False)
class InstanceResponse(ResponseBase):
    host_uuid: str
    label: str
    id: int
    tags: str
    region: str
    type: str
    machine: str
    
    cpus: int
    memory: int
    disk: int
    backups: InstanceBackups