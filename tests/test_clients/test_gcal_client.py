"""
Unit tests for client.gcal_client module.

Covers:
- GCalClient constructor and authentication flow
- events_totable() formatting
- sort_events_by_date() sorting logic
- get_numberof_events() and get_thisweek_events() with mocked API responses
"""

import pytest

from unittest.mock import MagicMock, patch

from client.gcal_client import GCalClient


# ----- Fixture for GCalClient -----------------------------------------
@pytest.fixture
def gcal_client():
    """
    Fixture to create a GCalClient instance with mocked authentication.
    """
    with patch("client.gcal_client.GCalClient._authenticate"):
        client = GCalClient()
        client.service = MagicMock()  # mock API service
        yield client


# ----- Constructor / Auth Tests ---------------------------------------
def test_constructor_initializes_gcal_client(tmp_path):
    """
    Test GCalClient constructor runs without errors.
    Authentication is mocked and credentials env var is faked.
    """
    dummy_creds = tmp_path / "creds.json"
    dummy_token = tmp_path / "token.json"
    dummy_creds.write_text("{}")
    dummy_token.write_text("{}")

    with patch.object(GCalClient, "_authenticate", return_value=None):
        client = GCalClient(
            creds_path=str(dummy_creds),
            token_path=str(dummy_token)
        )

    assert client.creds_path == dummy_creds
    assert client.token_path == dummy_token


# ----- Tests for events_totable ---------------------------------------
def test_events_totable_empty_list():
    """
    Test events_totable with empty list.
    Should return None.
    """
    table = GCalClient.events_totable([])
    assert table is None


def test_events_totable_with_valid_events():
    """
    Test events_totable with sample events.
    Should include title and formatted start/end times.
    """
    events = [
        {
            "summary": "Meeting",
            "start": {"dateTime": "2025-12-01T10:00:00Z"},
            "end": {"dateTime": "2025-12-01T11:00:00Z"},
        },
        {
            "summary": "Call",
            "start": {"date": "2025-12-02"},
            "end": {"date": "2025-12-02"},
        },
    ]

    table = GCalClient.events_totable(events)

    assert "Meeting" in table
    assert "Call" in table
    assert "2025-12-01" in table or "2025-12-01T" in table
    assert "2025-12-02" in table


# ----------------- Tests for sort_events_by_date -----------------
def test_sort_events_by_date():
    """
    Test that sort_events_by_date sorts events correctly by start date/time.
    """
    events = [
        {"summary": "B", "start": {"dateTime": "2025-12-02T10:00:00Z"}},
        {"summary": "A", "start": {"dateTime": "2025-12-01T09:00:00Z"}},
    ]
    sorted_events = GCalClient.sort_events_by_date(events)
    assert sorted_events[0]["summary"] == "A"
    assert sorted_events[1]["summary"] == "B"


# ----------------- Tests for get_numberof_events -----------------
def test_get_numberof_events_merges_and_sorts(gcal_client):
    """
    Test get_numberof_events returns combined and sorted events from multiple calendars.
    """
    mock_execute = MagicMock()
    mock_execute.execute.side_effect = [
        {
            "items": [
                {"summary": "Event1", "start": {"dateTime": "2025-12-01T10:00:00Z"}}
            ]
        },
        {
            "items": [
                {"summary": "Event2", "start": {"dateTime": "2025-12-02T10:00:00Z"}}
            ]
        },
    ]

    gcal_client.service.events.return_value.list.return_value = mock_execute

    calendar_ids = ["cal1", "cal2"]
    events = gcal_client.get_numberof_events(calendar_ids, max_results=1)

    # Should combine and sort both events
    assert len(events) == 2
    assert events[0]["summary"] == "Event1"
    assert events[1]["summary"] == "Event2"
    # Each event should have _calendar_id
    assert all("_calendar_id" in e for e in events)


# ----------------- Tests for get_thisweek_events -----------------
def test_get_thisweek_events_merges_and_sorts(gcal_client):
    """
    Test get_thisweek_events returns combined and sorted events for current week.
    """
    # Mock the API response for both calendars
    mock_execute = MagicMock()
    mock_execute.execute.side_effect = [
        {
            "items": [
                {"summary": "Event1", "start": {"dateTime": "2025-12-01T10:00:00Z"}}
            ]
        },
        {
            "items": [
                {"summary": "Event2", "start": {"dateTime": "2025-12-03T10:00:00Z"}}
            ]
        },
    ]
    gcal_client.service.events.return_value.list.return_value = mock_execute

    calendar_ids = ["cal1", "cal2"]
    events = gcal_client.get_thisweek_events(calendar_ids)

    # Verify combined events
    assert len(events) == 2
    assert events[0]["summary"] == "Event1"
    assert events[1]["summary"] == "Event2"
    # Each event should include _calendar_id
    assert all("_calendar_id" in e for e in events)
