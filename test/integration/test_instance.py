from test.integration.helpers import inspect_instance_response

import pytest

from linode_metadata import AsyncMetadataClient, MetadataClient


def test_get_instance_info(client: MetadataClient):
    instance = client.get_instance()
    inspect_instance_response(instance)


@pytest.mark.asyncio(scope="session")
async def test_async_get_instance_info(async_client: AsyncMetadataClient):
    instance = await async_client.get_instance()
    inspect_instance_response(instance)
