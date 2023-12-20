# Linode Metadata Client for Python

This package allows Python projects to easily interact with the [Linode Metadata Service](https://www.linode.com/docs/products/compute/compute-instances/guides/metadata/?tabs=linode-api).

## Getting Started

### Prerequisites 

- Python >= 3.8
- A running [Linode Instance](https://www.linode.com/docs/api/linode-instances/)

### Installation

```bash
pip install linode_metadata
```

### Building from Source
To build and install this package:

- Clone this repository
- `make install`

### Basic Example

The following sample shows a simple Python project that initializes a new metadata client and retrieves various information
about the current Linode.


```python
from linode_metadata import MetadataClient

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

## Testing

Before running tests on this project, please ensure you have a 
[Linode Personal Access Token](https://www.linode.com/docs/products/tools/api/guides/manage-api-tokens/)
exported under the `LINODE_TOKEN` environment variable.

### End-to-End Testing Using Ansible

This project contains an Ansible playbook to automatically deploy the necessary infrastructure 
and run end-to-end tests on it.

To install the dependencies for this playbook, ensure you have Python 3 installed and run the following:

```bash
make test-deps
```

After all dependencies have been installed, you can run the end-to-end test suite by running the following:

```bash
make e2e
```

If your local SSH public key is stored in a location other than `~/.ssh/id_rsa.pub`, 
you may need to override the `TEST_PUBKEY` argument:

```bash
make TEST_PUBKEY=/path/to/my/pubkey e2e
```

**NOTE: To speed up subsequent test runs, the infrastructure provisioned for testing will persist after the test run is complete. 
This infrastructure is safe to manually remove.**

### Manual End-to-End Testing

End-to-end tests can also be manually run using the `make e2e-local` target.
This test suite is expected to run from within a Linode instance and will likely 
fail in other environments.

## License

This software is Copyright Akamai Technologies, Inc. and is released under the [Apache 2.0 license](./LICENSE).
