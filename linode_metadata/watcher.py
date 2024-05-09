from __future__ import annotations

import asyncio
import logging
import time
import traceback
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from dataclasses import asdict
from datetime import timedelta
from logging import Logger
from typing import TYPE_CHECKING, Optional, Union

from linode_metadata.constants import LOGGER_NAME

if TYPE_CHECKING:
    from linode_metadata.metadata_client import (
        AsyncMetadataClient,
        MetadataClient,
    )

from linode_metadata.objects import InstanceResponse, NetworkResponse
from linode_metadata.objects.ssh_keys import SSHKeysResponse

DEFAULT_POLL_INTERVAL = timedelta(minutes=1)


class BaseMetadataWatcher(ABC):
    _logger: Logger

    def __init__(
        self,
        default_poll_interval: Union[
            timedelta, float, int
        ] = DEFAULT_POLL_INTERVAL,
        debug: bool = False,
    ):
        """
        The constructor of the base metadata watcher. This should not be used
        directly by the end users.

        :param default_poll_interval: The default time interval for polling Linode
                                        metadata services. Defaults to 1 minute.
        :type default_poll_interval: Optional[Union[timedelta, float, int]]
        :param debug: Enables debug mode if set to True.
        :type debug: bool
        """
        self.set_default_poll_interval(default_poll_interval)

        self._logger = logging.getLogger(LOGGER_NAME)
        self.debug = debug

    @abstractmethod
    def watch_network(
        self,
        poll_interval: Optional[Union[timedelta, float, int]],
        ignore_error: bool = False,
    ):
        pass

    @abstractmethod
    def watch_instance(
        self,
        poll_interval: Optional[Union[timedelta, float, int]],
        ignore_error: bool = False,
    ):  # pylint: disable-all
        pass

    @abstractmethod
    def watch_ssh_keys(
        self,
        poll_interval: Optional[Union[timedelta, float, int]],
        ignore_error: bool = False,
    ):
        pass

    @abstractmethod
    def poll(
        self,
        poller: Callable,
        poll_interval: Optional[Union[timedelta, float, int]] = None,
        ignore_error: bool = True,
    ):
        pass

    @staticmethod
    def normalize_poll_interval(
        poll_interval: Union[timedelta, float, int]
    ) -> timedelta:
        """
        Normalize poll_interval to be an instance of datetime.timedelta.
        float and int will be considered as the number of seconds.

        :param poll_interval: The input poll_interval in various types.
        :type poll_interval: Union[timedelta, float, int]
        :return: normalized poll_interval in timedelta type.
        :rtype: timedelta
        """
        if not isinstance(poll_interval, timedelta):
            poll_interval = timedelta(seconds=poll_interval)
        return poll_interval

    @property
    def default_poll_interval(self):
        """
        Get the default_poll_interval in this watcher.
        """
        return self._default_poll_interval

    def set_default_poll_interval(self, interval):
        """
        Set the default_poll_interval to this watcher.

        :param interval: The input poll_interval in various types.
        :type interval: Union[timedelta, float, int]
        """
        self._default_poll_interval = self.normalize_poll_interval(interval)

    def get_poll_interval(
        self, poll_interval: Optional[Union[timedelta, float, int]]
    ) -> timedelta:
        """
        Get the poll_interval in timedelta type. If a None is passed in,
        the default_poll_interval of the watcher will be returned.

        :param poll_interval: The input poll_interval in various types.
        :type poll_interval: Union[timedelta, float, int]
        :return: the normalized poll_interval in timedelta type.
        :rtype: timedelta
        """
        if poll_interval is None:
            poll_interval = self.default_poll_interval

        poll_interval = self.normalize_poll_interval(poll_interval)
        return poll_interval


class MetadataWatcher(BaseMetadataWatcher):
    client: MetadataClient

    def __init__(
        self,
        client: MetadataClient,
        default_poll_interval: Union[
            timedelta, float, int
        ] = DEFAULT_POLL_INTERVAL,
        debug: bool = False,
    ):
        """
        The constructor of the metadata watcher.

        :param client: The metadata client object.
        :type client: MetadataClient
        :param default_poll_interval: The default time interval for polling Linode
                                        metadata services. Defaults to 1 minute.
        :type default_poll_interval: Optional[Union[timedelta, float, int]]
        :param debug: Enables debug mode if set to True.
        :type debug: bool
        """
        self.client = client
        super().__init__(default_poll_interval, debug)

    def watch_network(
        self,
        poll_interval: Optional[Union[timedelta, float, int]] = None,
        ignore_error: bool = False,
    ) -> Generator[NetworkResponse, None, None]:
        """
        Watches the network changes. The new networking information will be
        yielded at the beginning of the iterating or when there is a change
        happened to the networking environment.

        :param poll_interval: The time interval between two polls of the networking
                                info endpoint of the Linode metadata services.
                                Defaults to default_poll_interval setting of the
                                watcher instance.
        :type poll_interval: Optional[Union[timedelta, float, int]]
        :param ignore_error: Whether to ignore the exception happen during the
                                call to the metadata service. If it is set to
                                True, it will print the exception with traceback
                                when it occurs, and if set to False, it will raise
                                the exception instead. Default to False.
        :type ignore_error: bool
        :return: A generator that yields next available networking info.
        :rtype: Generator[NetworkResponse, None, None]
        """
        yield from self.poll(
            self.client.get_network, poll_interval, ignore_error
        )

    def watch_instance(
        self,
        poll_interval: Optional[Union[timedelta, float, int]] = None,
        ignore_error: bool = False,
    ) -> Generator[InstanceResponse, None, None]:
        """
        Watches the instance changes. The new instance information will be
        yielded at the beginning of the iterating or when there is a change
        happened to the instance.

        :param poll_interval: The default time interval for polling the instance
                                info endpoint of the Linode metadata services.
                                Defaults to default_poll_interval setting of the
                                watcher instance.
        :type poll_interval: Optional[Union[timedelta, float, int]]
        :param ignore_error: Whether to ignore the exception happen during the
                                call to the metadata service. If it is set to
                                True, it will print the exception with traceback
                                when it occurs, and if set to False, it will raise
                                the exception instead. Default to False.
        :type ignore_error: bool
        :return: A generator that yields next available instance info.
        :rtype: Generator[InstanceResponse, None, None]
        """
        yield from self.poll(
            self.client.get_instance, poll_interval, ignore_error
        )

    def watch_ssh_keys(
        self,
        poll_interval: Optional[Union[timedelta, float, int]] = None,
        ignore_error: bool = False,
    ) -> Generator[SSHKeysResponse, None, None]:
        """
        Watches the ssh keys changes. The new ssh keys information will be
        yielded at the beginning of the iterating or when there is a change
        happened to the ssh keys.

        :param poll_interval: The default time interval for polling the ssh keys
                                info endpoint of the Linode metadata services.
                                Defaults to default_poll_interval setting of the
                                watcher instance.
        :type poll_interval: Optional[Union[timedelta, float, int]]
        :param ignore_error: Whether to ignore the exception happen during the
                                call to the metadata service. If it is set to
                                True, it will print the exception with traceback
                                when it occurs, and if set to False, it will raise
                                the exception instead. Default to False.
        :type ignore_error: bool
        :return: A generator that yields next available ssh keys info.
        :rtype: Generator[SSHKeysResponse, None, None]
        """
        yield from self.poll(
            self.client.get_ssh_keys, poll_interval, ignore_error
        )

    def poll(
        self,
        poller: Callable[
            [], Union[NetworkResponse, InstanceResponse, SSHKeysResponse]
        ],
        poll_interval: Optional[Union[timedelta, float, int]] = None,
        ignore_error: bool = False,
    ):
        """
        Continuously polling from Linode metadata services via the callable and
        yields a response when it differs from the last response.

        :param poller: The callable that polls from Linode metadata services.
        :type poller: Callable
        :param poll_interval: The default time interval between polls of the
                                linode metadata.
                                Defaults to default_poll_interval setting of the
                                watcher.
        :type poll_interval: Optional[Union[timedelta, float, int]]
        :param ignore_error: Whether to ignore the exception happen during the
                                call to the metadata service. If it is set to
                                True, it will print the exception with traceback
                                when it occurs, and if set to False, it will raise
                                the exception instead. Default to False.
        :type ignore_error: bool
        :return: A generator that yields next available response from linode
                    metadata service.
        :rtype: Generator
        """
        poll_interval = self.get_poll_interval(poll_interval)
        last_result = None
        while True:
            try:
                result = poller()
                if last_result is None or asdict(result) != asdict(last_result):
                    last_result = result
                    yield result
            except Exception as e:
                if ignore_error:
                    traceback.print_exc()
                else:
                    raise RuntimeError(
                        "Failed to poll from Linode Metadata API in the watcher"
                    ) from e
            time.sleep(poll_interval.seconds)


class AsyncMetadataWatcher(BaseMetadataWatcher):
    client: AsyncMetadataClient

    def __init__(
        self,
        client: AsyncMetadataClient,
        default_poll_interval: Union[
            timedelta, float, int
        ] = DEFAULT_POLL_INTERVAL,
        debug: bool = False,
    ):
        self.client = client
        super().__init__(default_poll_interval, debug)

    async def watch_network(
        self,
        poll_interval: Optional[Union[timedelta, float, int]] = None,
        ignore_error: bool = False,
    ) -> AsyncGenerator[NetworkResponse, None]:
        """
        Watches the network changes. The new networking information will be
        yielded asynchronously at the beginning of the iterating or when there
        is a change happened to the networking environment.

        :param poll_interval: The time interval between two polls of the networking
                                info endpoint of the Linode metadata services.
                                Defaults to default_poll_interval setting of the
                                watcher instance.
        :type poll_interval: Optional[Union[timedelta, float, int]]
        :param ignore_error: Whether to ignore the exception happen during the
                                call to the metadata service. If it is set to
                                True, it will print the exception with traceback
                                when it occurs, and if set to False, it will raise
                                the exception instead. Default to False.
        :type ignore_error: bool
        :return: A generator that asynchronously yields next available networking info.
        :rtype: AsyncGenerator[NetworkResponse, None]
        """

        async for response in self.poll(
            self.client.get_network, poll_interval, ignore_error
        ):
            yield response

    async def watch_instance(
        self,
        poll_interval: Optional[Union[timedelta, float, int]] = None,
        ignore_error: bool = False,
    ) -> AsyncGenerator[InstanceResponse, None]:
        """
        Watches the instance changes. The new instance information will be
        yielded asynchronously at the beginning of the iterating or when there
        is a change happened to the instance.

        :param poll_interval: The default time interval for polling the instance
                                info endpoint of the Linode metadata services.
                                Defaults to default_poll_interval setting of the
                                watcher instance.
        :type poll_interval: Optional[Union[timedelta, float, int]]
        :param ignore_error: Whether to ignore the exception happen during the
                                call to the metadata service. If it is set to
                                True, it will print the exception with traceback
                                when it occurs, and if set to False, it will raise
                                the exception instead. Default to False.
        :type ignore_error: bool
        :return: A generator that asynchronously yields next available instance info.
        :rtype: AsyncGenerator[InstanceResponse, None]
        """
        async for response in self.poll(
            self.client.get_instance, poll_interval, ignore_error
        ):
            yield response

    async def watch_ssh_keys(
        self,
        poll_interval: Optional[Union[timedelta, float, int]] = None,
        ignore_error: bool = False,
    ) -> AsyncGenerator[SSHKeysResponse, None]:
        """
        Watches the ssh keys changes. The new ssh keys information will be
        yielded asynchronously at the beginning of the iterating or when there
        is a change happened to the ssh keys.

        :param poll_interval: The default time interval for polling the ssh keys
                                info endpoint of the Linode metadata services.
                                Defaults to default_poll_interval setting of the
                                watcher instance.
        :type poll_interval: Optional[Union[timedelta, float, int]]
        :param ignore_error: Whether to ignore the exception happen during the
                                call to the metadata service. If it is set to
                                True, it will print the exception with traceback
                                when it occurs, and if set to False, it will raise
                                the exception instead. Default to False.
        :type ignore_error: bool
        :return: A generator that asynchronously yields next available ssh keys info.
        :rtype: AsyncGenerator[SSHKeysResponse, None]
        """
        async for response in self.poll(
            self.client.get_ssh_keys,
            poll_interval,
            ignore_error,
        ):
            yield response

    async def poll(
        self,
        poller: Callable[
            [],
            Union[
                Awaitable[NetworkResponse],
                Awaitable[InstanceResponse],
                Awaitable[SSHKeysResponse],
            ],
        ],
        poll_interval: Optional[Union[timedelta, float, int]] = None,
        ignore_error: bool = False,
    ):
        """
        Continuously and asynchronously polling from Linode metadata services
        via the provided callable and yields a response when it differs from
        the last response.

        :param poller: The callable that polls from Linode metadata services.
        :type poller: Callable
        :param poll_interval: The default time interval between polls of the
                                linode metadata.
                                Defaults to default_poll_interval setting of the
                                watcher.
        :type poll_interval: Optional[Union[timedelta, float, int]]
        :param ignore_error: Whether to ignore the exception happen during the
                                call to the metadata service. If it is set to
                                True, it will print the exception with traceback
                                when it occurs, and if set to False, it will raise
                                the exception instead. Default to False.
        :type ignore_error: bool
        :return: A generator that yields next available response from linode
                    metadata service.
        :rtype: AsyncGenerator
        """
        poll_interval = self.get_poll_interval(poll_interval)
        last_result = None
        while True:
            try:
                result = await poller()
                if last_result is None or asdict(result) != asdict(last_result):
                    last_result = result
                    yield result

            except Exception as e:
                if ignore_error:
                    traceback.print_exc()
                else:
                    raise RuntimeError(
                        "Failed to poll from Linode Metadata API in the watcher"
                    ) from e

            await asyncio.sleep(poll_interval.seconds)
