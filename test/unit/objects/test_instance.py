from typing import Any, Dict

from linode_metadata.objects.instance import (
    InstanceBackups,
    InstanceResponse,
    InstanceSpecs,
)

# Mocked JSON data for testing
instance_backups_data: Dict[str, Any] = {
    "enabled": True,
    "status": ["successful", "ready"],
}

instance_specs_data: Dict[str, Any] = {
    "vcpus": 2,
    "disk": 81920,
    "memory": 4096,
    "transfer": 4000,
    "gpus": 1,
}

instance_response_data: Dict[str, Any] = {
    "id": 123,
    "host_uuid": "3a3ddd59d9a78bb8de041391075df44de62bfec8",
    "label": "my-linode",
    "region": "us-east",
    "tags": "web-server",
    "type": "g6-standard-2",
    "specs": instance_specs_data,
    "backups": instance_backups_data,
}


def test_instance_backups():
    instance_backups = InstanceBackups(instance_backups_data)

    assert instance_backups.enabled is True
    assert instance_backups.status == ["successful", "ready"]


def test_instance_specs():
    instance_specs = InstanceSpecs(instance_specs_data)

    assert instance_specs.vcpus == 2
    assert instance_specs.disk == 81920
    assert instance_specs.memory == 4096
    assert instance_specs.transfer == 4000
    assert instance_specs.gpus == 1


def test_instance_response():
    instance_response = InstanceResponse(instance_response_data)

    assert instance_response.id == 123
    assert (
        instance_response.host_uuid
        == "3a3ddd59d9a78bb8de041391075df44de62bfec8"
    )
    assert instance_response.label == "my-linode"
    assert instance_response.region == "us-east"
    assert instance_response.tags == "web-server"
    assert instance_response.type == "g6-standard-2"

    assert instance_response.specs.vcpus == 2
    assert instance_response.backups.enabled is True
