# Linode Metadata Client for Python

This package contains a client to interact with the Linode Metadata service in Python.

## Usage

Run ```make install``` to install the metadata client onto your machine. After doing so, the following code sample can help you quickly get started using this package.

```python
import linode_metadata

client = MetadataClient()
# All of these responses are handled as DataClasses,
# allowing IDEs to properly use completions.
instance_info = client.get_instance()
network_info = client.get_network()
ssh_info = client.get_ssh_keys()
user_data = client.get_user_data()
print("Instance ID:", instance_info.id)
print("Public IPv4:", network_info.ipv4.public[0])
print("SSH Keys:", "; ".join(ssh_info.users.root))
print("User Data:", user_data)
```