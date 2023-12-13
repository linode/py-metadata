import pytest

import linode_metadata


@pytest.fixture(scope="function")
def metadata_client():
    client = linode_metadata.MetadataClient()
    return client

@pytest.fixture(scope="function")
def metadata_client_unmanaged():
    client = linode_metadata.MetadataClient(
        managed_token=False,
    )
    return client
