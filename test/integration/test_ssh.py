import re

import pytest


def test_get_ssh_keys(metadata_client):
    ssh = metadata_client.get_ssh_keys()

    # In some cases we may not have an authorized key
    # configured for root
    if len(ssh.users) < 1:
        pytest.skip(
            "The current instance does not have any any SSH keys configured, skipping..."
        )

    ssh_key_pattern = re.compile(
        r"^ssh-(?:rsa|ed25519|ecdsa|dss)\s[A-Za-z0-9+/]+[=]*\s\S*$"
    )

    for name, user in ssh.users.items():
        assert isinstance(name, str)

        for key in user:
            assert isinstance(key, str)
            assert ssh_key_pattern.match(key)
