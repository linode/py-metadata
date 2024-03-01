import pytest
import pytest_asyncio

from linode_metadata import MetadataAsyncClient, MetadataClient


@pytest.fixture(scope="session")
def client():
    with MetadataClient() as client:
        yield client


@pytest_asyncio.fixture()
async def async_client():
    async with MetadataAsyncClient() as async_client:
        yield async_client


@pytest.fixture(scope="session")
def client_unmanaged():
    with MetadataClient(managed_token=False) as client:
        yield client


@pytest_asyncio.fixture()
async def async_client_unmanaged():
    async with MetadataAsyncClient(managed_token=False) as async_client:
        yield async_client
