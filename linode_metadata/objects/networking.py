"""
Data classes related to Networking.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .response_base import ResponseBase


@dataclass(init=False)
class InterfaceVPCIPv4(ResponseBase):
    """IPv4 configuration of an interface's VPC subnet."""

    instance_address: str
    instance_ranges: List[str]
    nat_1_1: Optional[str]
    subnet_range: str


@dataclass(init=False)
class InterfaceVPCIPv6SLAAC(ResponseBase):
    """An IPv6 SLAAC assignment within a VPC subnet."""

    instance_address: str
    instance_range: str


@dataclass(init=False)
class InterfaceVPCIPv6(ResponseBase):
    """IPv6 configuration of an interface's VPC subnet."""

    instance_ranges: List[str]
    is_public: bool
    slaac: List[InterfaceVPCIPv6SLAAC]
    subnet_range: str


@dataclass(init=False)
class InterfaceVPCSubnet(ResponseBase):
    """The VPC subnet associated with an interface."""

    id: int
    label: str
    ipv4: Optional[InterfaceVPCIPv4]
    ipv6: Optional[InterfaceVPCIPv6]


@dataclass(init=False)
class InterfaceVPC(ResponseBase):
    """The VPC associated with an interface."""

    id: int
    label: str
    subnet: InterfaceVPCSubnet


@dataclass(init=False)
class Interfaces(ResponseBase):
    """
    A network interface attached to a Linode instance.
    """

    id: int
    label: Optional[str]
    purpose: str
    ipam_address: Optional[str]
    vpc: Optional[InterfaceVPC]


@dataclass(init=False)
class IPv4Networking(ResponseBase):
    """
    Information regarding IPv4 addresses.
    """

    public: List[str]
    private: List[str]
    shared: List[str]
    vpc: List[str]


@dataclass(init=False)
class IPv6Networking(ResponseBase):
    """
    Information regarding IPv6 addresses.
    """

    slaac: Optional[str]
    link_local: Optional[str] = field(metadata={"json": "link_local"})
    ranges: List[str]
    shared_ranges: List[str] = field(metadata={"json": "shared_ranges"})
    vpc: List[str]


@dataclass(init=False)
class NetworkResponse(ResponseBase):
    """
    The networking information associated with a Linode instance.
    """

    interfaces: List[Interfaces] = field(metadata={"json": "interfaces"})
    ipv4: IPv4Networking
    ipv6: IPv6Networking
