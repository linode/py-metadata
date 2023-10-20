import pytest
import linode_metadata


@pytest.fixture(scope="session")
def get_client():
    client = linode_metadata.MetadataClient()
    return client
