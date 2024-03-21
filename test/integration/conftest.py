import time
from datetime import timedelta

import pytest
import pytest_asyncio

from linode_metadata import AsyncMetadataClient, MetadataClient


@pytest.fixture(scope="session")
def client():
    with MetadataClient() as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def async_client():
    async with AsyncMetadataClient() as async_client:
        yield async_client


@pytest.fixture(scope="session")
def client_unmanaged():
    with MetadataClient(managed_token=False) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def async_client_unmanaged():
    async with AsyncMetadataClient(managed_token=False) as async_client:
        yield async_client


@pytest.fixture(scope="session")
def watcher(client: MetadataClient):
    return client.get_watcher(timedelta(minutes=1))


@pytest_asyncio.fixture(scope="session")
async def async_watcher(async_client: AsyncMetadataClient):
    return async_client.get_watcher(timedelta(minutes=1))


# Slow down tests to prevent 429 Too Many Requests errors
@pytest.fixture(autouse=True)
def slow_down_tests():
    time.sleep(5)
