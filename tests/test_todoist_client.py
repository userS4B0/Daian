from src.client.todoist_client import TodoistClient


def test_todoist_client_import():
    """Verify that the TodoistClient can be imported successfully."""
    client = TodoistClient()
    assert client is not None
