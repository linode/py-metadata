import re

import pytest

from linode_metadata import MetadataAsyncClient, MetadataClient
from linode_metadata.objects.networking import (
    IPv4Networking,
    IPv6Networking,
    NetworkResponse,
)


def test_get_network_info(client: MetadataClient):
    network = client.get_network()
    inspect_network_response(network)


@pytest.mark.asyncio
async def test_async_get_network_info(async_client: MetadataAsyncClient):
    network = await async_client.get_network()
    inspect_network_response(network)


def inspect_network_response(network: NetworkResponse):

    assert isinstance(network.interfaces, list)
    assert isinstance(network.ipv4, IPv4Networking)
    assert isinstance(network.ipv6, IPv6Networking)

    ipv4_pattern = re.compile(r"^\d{1,3}(\.\d{1,3}){3}/\d+$")
    ipv6_pattern = re.compile(r"^[0-9a-fA-F:]+/\d+$")

    for ip in network.ipv4.public:
        assert ipv4_pattern.match(ip)

    for ip in [network.ipv6.slaac, network.ipv6.link_local]:
        if ip is not None:
            assert ipv6_pattern.match(ip)
