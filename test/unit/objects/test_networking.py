from typing import Any, Dict

from linode_metadata.objects.networking import (
    Interfaces,
    IPv4Networking,
    IPv6Networking,
    NetworkResponse,
)


def test_interfaces():
    interface_data: Dict[str, Any] = {
        "label": "eth0",
        "purpose": "public",
        "ipam_address": "192.168.1.1/24",
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
    }
    ipv6 = IPv6Networking(ipv6_data)

    assert ipv6.slaac == "2001:db8::1:2a4f:8c7b:9d2e"
    assert ipv6.link_local == "fe80::1"
    assert ipv6.ranges == ["2001:db8::1"]
    assert ipv6.shared_ranges == ["fd00::1"]


def test_network_response():
    interfaces_data: Dict[str, Any] = [
        {"label": "eth0", "purpose": "public", "ipam_address": "192.168.1.1"}
    ]
    ipv4_data: Dict[str, Any] = {
        "public": ["192.168.1.2"],
        "private": ["10.0.0.1"],
        "shared": ["172.16.0.1"],
    }
    ipv6_data: Dict[str, Any] = {
        "slaac": "2001:db8::1:2a4f:8c7b:9d2e",
        "link_local": "fe80::1",
        "ranges": ["2001:db8::1"],
        "shared_ranges": ["fd00::1"],
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
