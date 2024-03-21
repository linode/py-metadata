from test.integration.helpers import inspect_network_response

import pytest

from linode_metadata import AsyncMetadataClient, MetadataClient


def test_get_network_info(client: MetadataClient):
    network = client.get_network()
    inspect_network_response(network)


@pytest.mark.asyncio(scope="session")
async def test_async_get_network_info(async_client: AsyncMetadataClient):
    network = await async_client.get_network()
    inspect_network_response(network)
