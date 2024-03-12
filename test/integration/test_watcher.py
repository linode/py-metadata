from test.integration.helpers import (
    inspect_instance_response,
    inspect_network_response,
    inspect_ssh_keys_response,
)

import pytest

from linode_metadata.watcher import AsyncMetadataWatcher, MetadataWatcher


@pytest.mark.asyncio(scope="session")
async def test_watch_instance_async(async_watcher: AsyncMetadataWatcher):
    instance_watcher = async_watcher.watch_instance()
    inspect_instance_response(await anext(instance_watcher))


@pytest.mark.asyncio(scope="session")
async def test_watch_network_async(async_watcher: AsyncMetadataWatcher):
    network_watcher = async_watcher.watch_network()
    inspect_network_response(await anext(network_watcher))


@pytest.mark.asyncio(scope="session")
async def test_watch_ssh_keys_async(async_watcher: AsyncMetadataWatcher):
    ssh_keys_watcher = async_watcher.watch_ssh_keys()
    inspect_ssh_keys_response(await anext(ssh_keys_watcher))


def test_watch_instance(watcher: MetadataWatcher):
    instance_watcher = watcher.watch_instance()
    inspect_instance_response(next(instance_watcher))


def test_watch_network(watcher: MetadataWatcher):
    network_watcher = watcher.watch_network()
    inspect_network_response(next(network_watcher))


def test_watch_ssh_keys(watcher: MetadataWatcher):
    ssh_keys_watcher = watcher.watch_ssh_keys()
    inspect_ssh_keys_response(next(ssh_keys_watcher))
