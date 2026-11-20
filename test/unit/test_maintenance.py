import httpx
import pytest

from linode_metadata import (
    AsyncMetadataClient,
    MaintenanceEvent,
    MaintenanceEventsResponse,
    MetadataClient,
)

EVENT = {
    "maintenance_id": 171,
    "applied_maintenance_policy": "linode/migrate",
    "selected_maintenance_policy": "linode/migrate",
    "schedule_type": "scheduled",
    "description": "Host operating system upgrade",
    "source": "platform",
    "not_before": "2025-08-16T14:26:27",
    "event_status": "in_progress",
}


@pytest.mark.parametrize("events", [[EVENT], []])
def test_maintenance_response(events):
    payload = {"data": events, "page": 1, "pages": 1, "results": len(events)}
    response = MaintenanceEventsResponse(payload)
    assert response.results == len(events)
    assert response.page == response.pages == 1
    if events:
        assert isinstance(response.data[0], MaintenanceEvent)
        assert response.data[0].maintenance_id == 171
    else:
        assert response.data == []


@pytest.fixture
def maintenance_transport():
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/v1/maintenance/events"
        return httpx.Response(
            200, json={"data": [EVENT], "page": 1, "pages": 1, "results": 1}
        )

    return httpx.MockTransport(handler)


def test_get_maintenance_events(maintenance_transport):
    with httpx.Client(transport=maintenance_transport) as http_client:
        client = MetadataClient(
            client=http_client, token="test-token", managed_token=False
        )
        assert client.get_maintenance_events().data[0].maintenance_id == 171


@pytest.mark.asyncio
async def test_get_maintenance_events_async(maintenance_transport):
    async with httpx.AsyncClient(
        transport=maintenance_transport
    ) as http_client:
        client = AsyncMetadataClient(
            client=http_client, token="test-token", managed_token=False
        )
        response = await client.get_maintenance_events()
        assert response.data[0].maintenance_id == 171
