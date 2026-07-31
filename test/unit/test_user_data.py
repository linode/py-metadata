import base64
import gzip
import io

from linode_metadata.metadata_client import BaseMetadataClient


def test_decode_user_data_plain():
    encoded = base64.b64encode(b"mock-user-data")
    assert BaseMetadataClient._decode_user_data(encoded) == "mock-user-data"


def test_decode_user_data_gzip():
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb") as gz_file:
        gz_file.write(b"mock-user-data")

    encoded = base64.b64encode(buffer.getvalue())
    assert BaseMetadataClient._decode_user_data(encoded) == "mock-user-data"
