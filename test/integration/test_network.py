import re

from linode_metadata.objects.networking import IPv4Networking, IPv6Networking


def test_get_network_info(metadata_client):
    network = metadata_client.get_network()

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
