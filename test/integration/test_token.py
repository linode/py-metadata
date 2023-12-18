import time
from datetime import datetime

import pytest

import linode_metadata
from linode_metadata.objects.error import ApiError


def test_generate_and_use_new_metadata_token(metadata_client_unmanaged):
    client = metadata_client_unmanaged

    new_token = client.generate_token()

    assert isinstance(new_token.token, bytes)
    assert isinstance(new_token.expiry_seconds, int)
    assert isinstance(new_token.created, datetime)

    assert len(new_token.token) == 64

    assert new_token.expiry_seconds == 3600

    client.set_token(token=new_token.token)

    # try sending api request using new token
    try:
        network = client.get_network()
        assert network is not None
    except ApiError as err:
        raise err


def test_verify_error_thrown_when_using_invalid_api_token(
    metadata_client_unmanaged,
):
    invalid_token = "1234randominvalidtoken"

    client = metadata_client_unmanaged

    client.set_token(token=invalid_token)

    with pytest.raises(ApiError) as excinfo:
        client.get_network()

    assert excinfo.value.status == 401
    assert "Unauthorized" in str(excinfo.value.json)

    # refresh token and verify connection don't throw error after
    client.refresh_token()

    try:
        network = client.get_network()
        assert network is not None
    except ApiError as err:
        raise err


def test_unmanaged_token_expire(metadata_client_unmanaged):
    client = metadata_client_unmanaged

    client.refresh_token(expiry_seconds=1)

    time.sleep(2)

    with pytest.raises(ApiError) as excinfo:
        client.get_network()

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
