from test.integration.helpers import inspect_ssh_keys_response

import pytest

from linode_metadata import AsyncMetadataClient, MetadataClient


def test_get_ssh_keys(client: MetadataClient):
    ssh_keys = client.get_ssh_keys()
    inspect_ssh_keys_response(ssh_keys)


@pytest.mark.asyncio(scope="session")
async def test_get_ssh_keys(async_client: AsyncMetadataClient):
    ssh_keys = await async_client.get_ssh_keys()
    inspect_ssh_keys_response(ssh_keys)
