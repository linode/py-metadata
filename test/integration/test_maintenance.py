from test.integration.helpers import inspect_maintenance_events_response

import pytest

from linode_metadata import AsyncMetadataClient, MetadataClient


def test_get_maintenance_events(client: MetadataClient):
    response = client.get_maintenance_events()
    inspect_maintenance_events_response(response)


@pytest.mark.asyncio(scope="session")
async def test_async_get_maintenance_events(async_client: AsyncMetadataClient):
    response = await async_client.get_maintenance_events()
    inspect_maintenance_events_response(response)
