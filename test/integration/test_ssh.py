import re

import pytest

from linode_metadata.objects.ssh_keys import SSHKeysUser


def test_get_ssh_keys(metadata_client):
    ssh = metadata_client.get_ssh_keys()
    assert isinstance(ssh.users, SSHKeysUser)

    # In some cases we may not have an authorized key
    # configured for root
    if ssh.users.root is None:
        pytest.skip(
            "Skipping due to no authorized keys configured for root user"
        )

    for key in ssh.users.root:
        assert isinstance(key, str)

    ssh_key_pattern = re.compile(
        r"^ssh-(?:rsa|ed25519|ecdsa|dss)\s[A-Za-z0-9+/]+[=]*\s\S*$"
    )
    for key in ssh.users.root:
        assert ssh_key_pattern.match(key)
