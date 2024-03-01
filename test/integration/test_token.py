import asyncio
import time
from datetime import datetime

import pytest

import linode_metadata
from linode_metadata import MetadataClient
from linode_metadata.metadata_client import MetadataAsyncClient
from linode_metadata.objects.error import ApiError
from linode_metadata.objects.token import MetadataToken


@pytest.fixture
def invalid_token():
    return "1234randominvalidtoken"


def inspect_token(token: MetadataToken):
    assert isinstance(token.token, bytes)
    assert isinstance(token.expiry_seconds, int)
    assert isinstance(token.created, datetime)

    assert len(token.token) == 64

    assert token.expiry_seconds == 3600


def test_generate_and_use_new_metadata_token(client_unmanaged: MetadataClient):
    client = client_unmanaged

    new_token = client.generate_token()
    inspect_token(new_token)

    client.set_token(token=new_token.token)

    # try sending api request using new token
    network = client.get_network()
    assert network is not None


@pytest.mark.asyncio
async def test_generate_and_use_new_metadata_token_async(
    async_client_unmanaged: MetadataAsyncClient,
):
    client = async_client_unmanaged

    new_token = await client.generate_token()
    inspect_token(new_token)

    client.set_token(token=new_token.token)

    # try sending api request using new token
    network = await client.get_network()
    assert network is not None


def test_verify_error_thrown_when_using_invalid_api_token(
    client_unmanaged: MetadataClient,
    invalid_token: str,
):
    client = client_unmanaged

    client.set_token(token=invalid_token)

    with pytest.raises(ApiError) as excinfo:
        client.get_network()

    assert excinfo.value.status == 401
    assert "Unauthorized" in str(excinfo.value.json)

    # refresh token and verify connection don't throw error after
    client.refresh_token()

    network = client.get_network()
    assert network is not None


@pytest.mark.asyncio
async def test_verify_error_thrown_when_using_invalid_api_token_async(
    async_client_unmanaged: MetadataAsyncClient, invalid_token: str
):
    client = async_client_unmanaged

    client.set_token(token=invalid_token)

    with pytest.raises(ApiError) as excinfo:
        await client.get_network()

    assert excinfo.value.status == 401
    assert "Unauthorized" in str(excinfo.value.json)

    # refresh token and verify connection don't throw error after
    await client.refresh_token()

    network = await client.get_network()
    assert network is not None


def test_unmanaged_token_expire(client_unmanaged: MetadataClient):
    client = client_unmanaged

    client.refresh_token(expiry_seconds=1)

    time.sleep(2)

    with pytest.raises(ApiError) as excinfo:
        client.get_network()

    assert excinfo.value.status == 401
    assert "Unauthorized" in str(excinfo.value.json)


@pytest.mark.asyncio
async def test_unmanaged_token_expire_async(
    async_client_unmanaged: MetadataAsyncClient,
):
    client = async_client_unmanaged

    await client.refresh_token(expiry_seconds=1)
    await asyncio.sleep(2)

    with pytest.raises(ApiError) as excinfo:
        await client.get_network()

    assert excinfo.value.status == 401
    assert "Unauthorized" in str(excinfo.value.json)


def test_managed_token_auto_refresh():
    client = linode_metadata.MetadataClient(
        managed_token_expiry_seconds=1,
    )

    # Ensure the initial token is generated properly
    instance = client.get_instance()
    assert instance is not None

    time.sleep(2)

    # Ensure the token is automatically refreshed
    networking = client.get_network()
    assert networking is not None


@pytest.mark.asyncio
async def test_managed_token_auto_refresh_async():
    client = linode_metadata.MetadataAsyncClient(
        managed_token_expiry_seconds=1,
    )

    # Ensure the initial token is generated properly
    instance = await client.get_instance()
    assert instance is not None

    asyncio.sleep(2)

    # Ensure the token is automatically refreshed
    networking = await client.get_network()
    assert networking is not None
