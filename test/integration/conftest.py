import pytest

import linode_metadata


@pytest.fixture(scope="session")
def metadata_client():
    client = linode_metadata.MetadataClient()
    return client
