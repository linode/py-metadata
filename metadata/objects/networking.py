from dataclasses import dataclass, field
from typing import List

from .response_base import ResponseBase


@dataclass(init=False)
class VLAN(ResponseBase):
    label: str
    purpose: str
    ipam_address: str


@dataclass(init=False)
class IPv4Networking(ResponseBase):
    public: List[str]
    private: List[str]
    shared: List[str]


@dataclass(init=False)
class IPv6Networking(ResponseBase):
    slaac: str
    link_local: str = field(metadata={"json": "link-local"})
    ranges: List[str]
    shared_ranges: List[str] = field(metadata={"json": "shared-ranges"})


@dataclass(init=False)
class NetworkResponse(ResponseBase):
    vlans: List[VLAN] = field(metadata={"json": "vlans"})
    ipv4: IPv4Networking
    ipv6: IPv6Networking