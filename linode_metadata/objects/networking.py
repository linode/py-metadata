"""
Data classes related to Networking.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .response_base import ResponseBase


@dataclass(init=False)
class Interfaces(ResponseBase):
    """
    A network interface attached to a Linode instance.
    """

    label: str
    purpose: str
    ipam_address: Optional[str]


@dataclass(init=False)
class IPv4Networking(ResponseBase):
    """
    Information regarding IPv4 addresses.
    """

    public: List[str]
    private: List[str]
    shared: List[str]


@dataclass(init=False)
class IPv6Networking(ResponseBase):
    """
    Information regarding IPv6 addresses.
    """

    slaac: str
    link_local: str = field(metadata={"json": "link_local"})
    ranges: List[str]
    shared_ranges: List[str] = field(metadata={"json": "shared_ranges"})


@dataclass(init=False)
class NetworkResponse(ResponseBase):
    """
    The networking information associated with a Linode instance.
    """

    interfaces: List[Interfaces] = field(metadata={"json": "interfaces"})
    ipv4: IPv4Networking
    ipv6: IPv6Networking
