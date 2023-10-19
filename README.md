# Linode Metadata Client for Python

This package allows Python projects to easily interact with the [Linode Metadata Service](https://www.linode.com/docs/products/compute/compute-instances/guides/metadata/?tabs=linode-api).

## Getting Started

### Prerequisites 

- Python >= 3.8
- A running [Linode Instance](https://www.linode.com/docs/api/linode-instances/)

### Installation

```bash
pip install linode-metadata
```

### Building from Source
To build and install this package:

- Clone this repository
- `make install`

### Basic Example

The follow sample shows a simple Python project that initializes a new metadata client and retrieves various information
about the current Linode.


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