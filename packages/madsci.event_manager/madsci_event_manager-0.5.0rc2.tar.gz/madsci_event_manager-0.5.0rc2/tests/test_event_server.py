"""
Test the Event Manager's REST server.

Uses pytest-mock-resources to create a MongoDB fixture. Note that this _requires_
a working docker installation.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from madsci.common.types.event_types import (
    EmailAlertsConfig,
    Event,
    EventManagerDefinition,
    EventManagerSettings,
    EventType,
)
from madsci.event_manager.event_server import EventManager
from pymongo.synchronous.database import Database
from pytest_mock_resources import MongoConfig, create_mongo_fixture

event_manager_def = EventManagerDefinition(
    name="test_event_manager",
)
event_manager_settings = EventManagerSettings(
    email_alerts=EmailAlertsConfig(email_addresses=["test@example.com"]),
)


@pytest.fixture(scope="session")
def pmr_mongo_config() -> MongoConfig:
    """Configure the MongoDB fixture."""
    return MongoConfig(image="mongo:8.0")


db_connection = create_mongo_fixture()


@pytest.fixture
def test_client(db_connection: Database) -> TestClient:
    """Event Server Test Client Fixture"""
    manager = EventManager(
        settings=event_manager_settings,
        definition=event_manager_def,
        db_connection=db_connection,
    )
    app = manager.create_server()
    return TestClient(app)


def test_root(test_client: TestClient) -> None:
    """
    Test the root endpoint for the Event_Manager's server.
    Should return an EventManagerDefinition.
    """
    result = test_client.get("/").json()
    EventManagerDefinition.model_validate(result)


def test_roundtrip_event(test_client: TestClient) -> None:
    """
    Test that we can send and then retrieve an event by ID.
    """
    test_event = Event(
        event_type=EventType.TEST,
        event_data={"test": "data"},
    )
    result = test_client.post("/event", json=test_event.model_dump(mode="json")).json()
    assert Event.model_validate(result) == test_event
    result = test_client.get(f"/event/{test_event.event_id}").json()
    assert Event.model_validate(result) == test_event


def test_get_events(test_client: TestClient) -> None:
    """
    Test that we can retrieve all events and they are returned as a dictionary in reverse-chronological order, with the correct number of events.
    """
    for i in range(10):
        test_event = Event(
            event_type=EventType.TEST,
            event_data={"test": i},
        )
        test_client.post("/event", json=test_event.model_dump(mode="json"))
    query_number = 5
    result = test_client.get("/events", params={"number": query_number}).json()
    # * Check that the number of events returned is correct
    assert len(result) == query_number
    previous_timestamp = float("inf")
    for _, value in result.items():
        event = Event.model_validate(value)
        # * Check that the events are in reverse-chronological order
        assert event.event_data["test"] in range(5, 10)
        assert previous_timestamp >= event.event_timestamp.timestamp()
        previous_timestamp = event.event_timestamp.timestamp()


def test_query_events(test_client: TestClient) -> None:
    """
    Test querying events based on a selector.
    """
    for i in range(10, 20):
        test_event = Event(
            event_type=EventType.TEST,
            event_data={"test": i},
        )
        test_client.post("/event", json=test_event.model_dump(mode="json"))
    test_val = 10
    selector = {"event_data.test": {"$gte": test_val}}
    result = test_client.post("/events/query", json=selector).json()
    assert len(result) == test_val
    for _, value in result.items():
        event = Event.model_validate(value)
        assert event.event_data["test"] >= test_val


def test_event_alert(test_client: TestClient) -> None:
    """
    Test that an alert is triggered when an event meets the alert criteria.
    """
    # Create an event that should trigger an alert
    alert_event = Event(
        event_type=EventType.TEST,
        log_level=event_manager_settings.alert_level,
        alert=True,
        event_data={"alert": "This is a test alert"},
    )

    # Post the event to the server
    with patch(
        "madsci.event_manager.notifications.EmailAlerts.send_email"
    ) as mock_send_email:
        test_client.post("/event", json=alert_event.model_dump(mode="json"))

        # Assert that the email alert was sent
        mock_send_email.assert_called()
        assert mock_send_email.call_count == len(
            event_manager_settings.email_alerts.email_addresses
        )


def test_health_endpoint(test_client: TestClient) -> None:
    """Test the health endpoint of the Event Manager."""
    response = test_client.get("/health")
    assert response.status_code == 200

    health_data = response.json()
    assert "healthy" in health_data
    assert "description" in health_data
    assert "db_connected" in health_data
    assert "total_events" in health_data

    # Health should be True when database is working
    assert health_data["healthy"] is True
    assert health_data["db_connected"] is True
    assert isinstance(health_data["total_events"], int)
    assert health_data["total_events"] >= 0
