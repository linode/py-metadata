from typing import Any, Dict

from linode_metadata.objects.ssh_keys import SSHKeysResponse


def test_ssh_keys():
    TEST_USERNAME = "myuser"
    TEST_SSH_KEY = "my-pub-key"
    ssh_keys_data: Dict[str, Any] = {"users": {TEST_USERNAME: [TEST_SSH_KEY]}}
    ssh_keys = SSHKeysResponse(ssh_keys_data)

    assert len(ssh_keys.users) == 1 and TEST_USERNAME in ssh_keys.users
    assert len(
        ssh_keys.users.get(TEST_USERNAME)
    ) == 1 and TEST_SSH_KEY in ssh_keys.users.get(TEST_USERNAME)
