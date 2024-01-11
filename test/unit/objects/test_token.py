from datetime import datetime

from linode_metadata.objects.token import MetadataToken


def test_metadata_token():
    created_time = datetime.utcnow()

    metadata_token = MetadataToken(
        token="random_token_value", expiry_seconds=3600, created=created_time
    )

    assert metadata_token.token == "random_token_value", "Token value mismatch"
    assert metadata_token.expiry_seconds == 3600, "Expiry seconds mismatch"
    assert metadata_token.created == created_time, "Created time mismatch"
