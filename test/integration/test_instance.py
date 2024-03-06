import re

import pytest

from linode_metadata import MetadataAsyncClient, MetadataClient
from linode_metadata.objects.instance import InstanceResponse


def test_get_instance_info(client: MetadataClient):
    instance = client.get_instance()
    inspect_instance_response(instance)


@pytest.mark.asyncio
async def test_async_get_instance_info(async_client: MetadataAsyncClient):
    instance = await async_client.get_instance()
    inspect_instance_response(instance)


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
    assert instance.backups.status is None
    assert re.match(r"^[a-f\d]+$", instance.host_uuid)
    assert isinstance(instance.tags, list)
