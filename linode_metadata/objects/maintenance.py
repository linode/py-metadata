"""Maintenance event response objects."""

from dataclasses import dataclass
from typing import List

from .response_base import ResponseBase

__all__ = ["MaintenanceEvent", "MaintenanceEventsResponse"]


@dataclass(init=False)
class MaintenanceEvent(ResponseBase):
    """A maintenance event affecting the current instance."""

    maintenance_id: int
    applied_maintenance_policy: str
    selected_maintenance_policy: str
    schedule_type: str
    description: str
    source: str
    not_before: str
    event_status: str


@dataclass(init=False)
class MaintenanceEventsResponse(ResponseBase):
    """A page of maintenance events, including pagination metadata."""

    data: List[MaintenanceEvent]
    page: int
    pages: int
    results: int
