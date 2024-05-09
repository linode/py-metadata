import re

import pytest

from linode_metadata.objects.instance import InstanceResponse
from linode_metadata.objects.networking import (
    IPv4Networking,
    IPv6Networking,
    NetworkResponse,
)
from linode_metadata.objects.ssh_keys import SSHKeysResponse


def inspect_instance_response(instance: InstanceResponse):
    assert isinstance(instance.id, int)
    assert re.match(r"^[A-Za-z\-0-9]+$", instance.label)
    assert re.match(r"^[a-z\-]+$", instance.region)
    assert re.match(r"^[a-z\d\-]+$", instance.type)
    assert isinstance(instance.specs.vcpus, int)
    assert isinstance(instance.specs.memory, int)
    assert isinstance(instance.specs.gpus, int)
    assert isinstance(instance.specs.transfer, int)
    assert isinstance(instance.specs.disk, int)
    assert isinstance(instance.backups.enabled, bool)
    assert instance.backups.status in (None, 'pending')
    assert re.match(r"^[a-f\d]+$", instance.host_uuid)
    assert isinstance(instance.tags, list)


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


def inspect_ssh_keys_response(ssh_keys: SSHKeysResponse):
    # In some cases we may not have an authorized key
    # configured for root
    if len(ssh_keys.users) < 1:
        pytest.skip(
            "The current instance does not have any any SSH keys configured, skipping..."
        )

    ssh_key_pattern = re.compile(
        r"^ssh-(?:rsa|ed25519|ecdsa|dss)\s[A-Za-z0-9+/]+[=]*\s\S*$"
    )

    for name, user in ssh_keys.users.items():
        assert isinstance(name, str)

        for key in user:
            assert isinstance(key, str)
            assert ssh_key_pattern.match(key)
