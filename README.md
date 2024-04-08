# Linode Metadata Client for Python

[![Unit Tests](https://github.com/linode/py-metadata/actions/workflows/unit-tests.yml/badge.svg?branch=main)](https://github.com/linode/py-metadata/actions/workflows/unit-tests.yml)
[![E2E Tests](https://github.com/linode/py-metadata/actions/workflows/e2e-suite.yml/badge.svg?branch=main)](https://github.com/linode/py-metadata/actions/workflows/e2e-suite.yml)
[![PyPI version](https://badge.fury.io/py/linode-metadata.svg)](https://badge.fury.io/py/linode-metadata)
[![Documentation Status](https://readthedocs.org/projects/linode-metadata/badge/?version=latest)](https://linode-metadata.readthedocs.io/en/latest/?badge=latest)

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

## Examples

The following code snippets show multiple different ways to use the metadata
client and retrieves various metadata of the current Linode.

### Basic Usage

```python
from linode_metadata import MetadataClient

client = MetadataClient()

instance_info = client.get_instance()
network_info = client.get_network()
ssh_info = client.get_ssh_keys()
user_data = client.get_user_data()

print("Instance ID:", instance_info.id)
print("Public IPv4:", network_info.ipv4.public[0])
print("SSH Keys:", "; ".join(ssh_info.users))
print("User Data:", user_data)
```

### Asynchronous I/O and Context Manager Support

You can also use the context manager to ensure the HTTP client will be properly closed, and the
`asyncio` enabled client is also available.

```python
import asyncio
from linode_metadata import AsyncMetadataClient

async def get_metadata():
    with AsyncMetadataClient() as client:
        instance_info = await client.get_instance()
        print("Instance ID:", instance_info.id)

asyncio.run(get_metadata())
```

### Watchers

Watchers are useful for monitor changes in the metadata, e.g. newly added IP address to the Linode.

```python
import asyncio
from linode_metadata import AsyncMetadataClient

async def get_metadata():
    async with AsyncMetadataClient() as client:
        watcher = client.get_watcher()
        async for new_network_info in watcher.watch_network():
            print(new_network_info)

asyncio.run(get_metadata())
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
make int-test
```

If your local SSH public key is stored in a location other than `~/.ssh/id_rsa.pub`,
you may need to override the `TEST_PUBKEY` argument:

```bash
make TEST_PUBKEY=/path/to/my/pubkey int-test
```

**NOTE: To speed up subsequent test runs, the infrastructure provisioned for testing will persist after the test run is complete.
This infrastructure is safe to manually remove.**

### Manual End-to-End Testing

End-to-end tests can also be manually run using the `make int-test-local` target.
This test suite is expected to run from within a Linode instance and will likely 
fail in other environments.

## License

This software is Copyright Akamai Technologies, Inc. and is released under the [Apache 2.0 license](./LICENSE).
