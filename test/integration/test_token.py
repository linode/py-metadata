import pytest
from datetime import datetime
from linode_metadata.objects.error import ApiError


def test_generate_and_use_new_metadata_token(get_client):
    new_token = get_client.generate_token()

    assert isinstance(new_token.token, bytes)
    assert isinstance(new_token.expiry_seconds, int)
    assert isinstance(new_token.created, datetime)

    assert len(new_token.token) == 64

    assert new_token.expiry_seconds == 3600

    get_client.set_token(token=new_token.token)

    # try sending api request using new token
    try:
        network = get_client.get_network()
        assert network is not None
    except ApiError as err:
        raise err


def test_verify_error_thrown_when_using_invalid_api_token(get_client):
    invalid_token = "1234randominvalidtoken"

    get_client.set_token(token=invalid_token)

    with pytest.raises(ApiError) as excinfo:
        get_client.get_network()

    assert excinfo.value.status == 401
    assert "Unauthorized" in str(excinfo.value.json)

    # refresh token and verify connection don't throw error after
    get_client.refresh_token()

    try:
        network = get_client.get_network()
        assert network is not None
    except ApiError as err:
        raise err



