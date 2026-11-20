"""
Data classes related to Linode instances.
"""

from dataclasses import dataclass
from typing import List, Optional

from .response_base import ResponseBase


@dataclass(init=False)
class InstanceBackups(ResponseBase):
    """
    The status of the Linode instance's backups enrollment.
    """

    enabled: bool
    status: Optional[str]


@dataclass(init=False)
class InstanceImage(ResponseBase):
    """The image used to provision the instance."""

    id: str
    label: str


@dataclass(init=False)
class InstanceSpecs(ResponseBase):
    """
    The technical specifications of a Linode instance.
    """

    vcpus: int
    disk: int
    memory: int
    transfer: int
    gpus: int


@dataclass(init=False)
class InstanceResponse(ResponseBase):
    """
    A Linode instance.
    """

    id: int
    host_uuid: str
    label: str
    region: str
    tags: List[str]
    type: str
    specs: InstanceSpecs
    backups: InstanceBackups
    account_euuid: str
    image: InstanceImage
