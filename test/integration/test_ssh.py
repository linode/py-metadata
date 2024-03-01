import re

import pytest

from linode_metadata import MetadataAsyncClient, MetadataClient
from linode_metadata.objects.ssh_keys import SSHKeysResponse


def test_get_ssh_keys(client: MetadataClient):
    ssh_keys = client.get_ssh_keys()
    inspect_ssh_keys_response(ssh_keys)


@pytest.mark.asyncio
async def test_get_ssh_keys(async_client: MetadataAsyncClient):
    ssh_keys = await async_client.get_ssh_keys()
    inspect_ssh_keys_response(ssh_keys)


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
