import re

from linode_metadata.objects.ssh_keys import SSHKeysUser


def test_get_ssh_keys(metadata_client):
    ssh = metadata_client.get_ssh_keys()
    assert isinstance(ssh.users, SSHKeysUser)

    for key in ssh.users.root:
        assert isinstance(key, str)

    ssh_key_pattern = re.compile(
        r"^ssh-(?:rsa|ed25519|ecdsa|dss)\s[A-Za-z0-9+/]+[=]*\s\S*$"
    )
    for key in ssh.users.root:
        assert ssh_key_pattern.match(key)
