import time
from linode_metadata import MetadataClient

client = MetadataClient(
    managed_token_expiry_seconds=1
)

for i in range(10):
    # Make an arbitrary MDS API request
    client.get_instance()
    print(f"Iteration {i}: {client.token}")

    # Wait for the token to expire
    time.sleep(2)