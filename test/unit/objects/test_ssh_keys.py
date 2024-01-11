from typing import Any, Dict

from linode_metadata.objects.ssh_keys import SSHKeysUser


def test_ssh_keys_user():
    root_keys: Dict[str, Any] = {
        "root": "ssh-randomkeyforunittestas;ldkjfqweeru"
    }
    ssh_keys_user = SSHKeysUser(root_keys)
    assert (
        ssh_keys_user.root == "ssh-randomkeyforunittestas;ldkjfqweeru"
    ), "SSHKeysUser initialization failed"
