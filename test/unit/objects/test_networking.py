from typing import Any, Dict

from linode_metadata.objects.networking import (
    Interfaces,
    InterfaceVPC,
    InterfaceVPCIPv4,
    InterfaceVPCIPv6,
    InterfaceVPCIPv6SLAAC,
    InterfaceVPCSubnet,
    IPv4Networking,
    IPv6Networking,
    NetworkResponse,
)


def test_interfaces():
    interface_data: Dict[str, Any] = {
        "id": 1,
        "label": "eth0",
        "purpose": "public",
        "ipam_address": "192.168.1.1/24",
        "vpc": None,
    }
    interface = Interfaces(interface_data)

    assert interface.label == "eth0"
    assert interface.purpose == "public"
    assert interface.ipam_address == "192.168.1.1/24"


def test_ipv4_networking():
    ipv4_data: Dict[str, Any] = {
        "public": ["192.168.1.2"],
        "private": ["10.0.0.1"],
        "shared": ["172.16.0.1"],
        "vpc": [],
    }
    ipv4 = IPv4Networking(ipv4_data)

    assert ipv4.public == ["192.168.1.2"]
    assert ipv4.private == ["10.0.0.1"]
    assert ipv4.shared == ["172.16.0.1"]


def test_ipv6_networking():
    ipv6_data: Dict[str, Any] = {
        "slaac": "2001:db8::1:2a4f:8c7b:9d2e",
        "link_local": "fe80::1",
        "ranges": ["2001:db8::1"],
        "shared_ranges": ["fd00::1"],
        "vpc": [],
    }
    ipv6 = IPv6Networking(ipv6_data)

    assert ipv6.slaac == "2001:db8::1:2a4f:8c7b:9d2e"
    assert ipv6.link_local == "fe80::1"
    assert ipv6.ranges == ["2001:db8::1"]
    assert ipv6.shared_ranges == ["fd00::1"]


def test_network_response():
    interfaces_data: Dict[str, Any] = [
        {
            "id": 1,
            "label": "eth0",
            "purpose": "public",
            "ipam_address": "192.168.1.1",
            "vpc": None,
        }
    ]
    ipv4_data: Dict[str, Any] = {
        "public": ["192.168.1.2"],
        "private": ["10.0.0.1"],
        "shared": ["172.16.0.1"],
        "vpc": [],
    }
    ipv6_data: Dict[str, Any] = {
        "slaac": "2001:db8::1:2a4f:8c7b:9d2e",
        "link_local": "fe80::1",
        "ranges": ["2001:db8::1"],
        "shared_ranges": ["fd00::1"],
        "vpc": [],
    }

    network_data = {
        "interfaces": interfaces_data,
        "ipv4": ipv4_data,
        "ipv6": ipv6_data,
    }
    network_response = NetworkResponse(network_data)

    assert isinstance(network_response.interfaces[0], Interfaces)
    assert network_response.ipv4.public == ["192.168.1.2"]
    assert network_response.ipv6.slaac == "2001:db8::1:2a4f:8c7b:9d2e"


def test_network_vpc_fields():
    network = NetworkResponse(
        {
            "interfaces": [
                {
                    "id": 101,
                    "label": None,
                    "purpose": "vpc",
                    "ipam_address": None,
                    "vpc": {
                        "id": 202,
                        "label": "vpc-label",
                        "subnet": {
                            "id": 303,
                            "label": "subnet-label",
                            "ipv4": {
                                "instance_address": "10.0.0.2",
                                "instance_ranges": ["10.0.1.0/24"],
                                "nat_1_1": "192.0.2.2",
                                "subnet_range": "10.0.0.0/16",
                            },
                            "ipv6": {
                                "instance_ranges": ["2001:db8:1::/64"],
                                "is_public": False,
                                "slaac": [
                                    {
                                        "instance_address": "2001:db8::2",
                                        "instance_range": "2001:db8::/64",
                                    }
                                ],
                                "subnet_range": "2001:db8::/48",
                            },
                        },
                    },
                }
            ],
            "ipv4": {
                "public": [],
                "private": [],
                "shared": [],
                "vpc": ["10.0.0.2"],
            },
            "ipv6": {
                "slaac": None,
                "link_local": None,
                "ranges": [],
                "shared_ranges": [],
                "vpc": ["2001:db8::2"],
            },
        }
    )
    interface = network.interfaces[0]
    assert interface.id == 101
    assert isinstance(interface.vpc, InterfaceVPC)
    subnet = interface.vpc.subnet
    assert isinstance(subnet, InterfaceVPCSubnet)
    assert subnet.id == 303
    assert isinstance(subnet.ipv4, InterfaceVPCIPv4)
    assert subnet.ipv4.instance_address == "10.0.0.2"
    assert isinstance(subnet.ipv6, InterfaceVPCIPv6)
    assert isinstance(subnet.ipv6.slaac[0], InterfaceVPCIPv6SLAAC)
    assert subnet.ipv6.slaac[0].instance_address == "2001:db8::2"
    assert network.ipv4.vpc == ["10.0.0.2"]
    assert network.ipv6.vpc == ["2001:db8::2"]


def test_network_nullable_vpc_fields():
    subnet = InterfaceVPCSubnet(
        {"id": 303, "label": "subnet-label", "ipv4": None, "ipv6": None}
    )
    assert subnet.ipv4 is None
    assert subnet.ipv6 is None
    ipv4 = InterfaceVPCIPv4(
        {
            "instance_address": "10.0.0.2",
            "instance_ranges": [],
            "nat_1_1": None,
            "subnet_range": "10.0.0.0/16",
        }
    )
    assert ipv4.nat_1_1 is None
