# Linode Metadata Client for Python

This package contains a client to interact with the Linode Metadata service in Python.

## Usage

```python
from metadata import MetadataClient
client = MetadataClient()
# All of these responses are handled as DataClasses,
# allowing IDEs to properly use completions.
instance_info = client.get_instance()
network_info = client.get_network()
ssh_info = client.get_ssh_keys()
user_data = client.get_user_data()
print("Instance ID:", instance_info.instance_id)
print("Public IPv4:", network_info.ipv4.public[0])
print("SSH Keys:", "; ".join(ssh_info.users.root))
print("User Data:", user_data)
```