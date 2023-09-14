from dataclasses import dataclass, field
from typing import List, Optional

from .response_base import ResponseBase


@dataclass(init=False)
class Interfaces(ResponseBase):
    label: str
    purpose: str
    ipam_address: Optional[str]


@dataclass(init=False)
class IPv4Networking(ResponseBase):
    public: List[str]
    private: List[str]
    shared: List[str]


@dataclass(init=False)
class IPv6Networking(ResponseBase):
    slaac: str
    link_local: List[str] = field(metadata={"json": "link-local"})
    ranges: List[str]
    shared_ranges: List[str] = field(metadata={"json": "shared-ranges"})


@dataclass(init=False)
class NetworkResponse(ResponseBase):
    interfaces: List[Interfaces] = field(metadata={"json": "interfaces"})
    ipv4: IPv4Networking
    ipv6: IPv6Networking