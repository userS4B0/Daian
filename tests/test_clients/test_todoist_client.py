"""
Unit tests for client.todoist_client module.

Covers:
- TodoistClient constructor
- tasks_totable() method with:
  - empty list
  - tasks with valid due date
  - tasks with missing due date
"""

from unittest.mock import MagicMock
import pytest

from client.todoist_client import TodoistClient


# ----- Fixture for TodoistClient --------------------------------------
@pytest.fixture
def todoist_client():
    """
    Fixture to create a TodoistClient instance.
    """
    return TodoistClient()


# ----- Constructor Tests ----------------------------------------------
def test_constructor_initializes_client(todoist_client):
    """
    Test that the TodoistClient constructor initializes correctly.
    """
    assert isinstance(todoist_client, TodoistClient)


# ----- Tests for tasks_totable ----------------------------------------
def test_tasks_totable_empty_list():
    """
    Test tasks_totable with an empty list.
    Should return None.
    """
    result = TodoistClient.tasks_totable([])
    assert result is None


def test_tasks_totable_with_valid_tasks():
    """
    Test tasks_totable with a valid Todoist task.
    Should generate a table including task details and 'No' for completion.
    """
    # Simulate a Todoist Task object
    task_mock = MagicMock()
    task_mock.priority = 4
    task_mock.content = "Test task"
    task_mock.description = "A test description"
    task_mock.labels = ["work"]
    task_mock.is_completed = False

    # Simulate due date
    due_mock = MagicMock()
    due_mock.datetime = "2025-11-30T12:00:00"
    task_mock.due = due_mock

    table = TodoistClient.tasks_totable([task_mock])

    # Check table content
    assert "Test task" in table
    assert "A test description" in table
    assert "work" in table
    assert "No" in table  # Completion status


def test_tasks_totable_with_missing_due():
    """
    Test tasks_totable with a task missing due date.
    Should include '—' for due date and 'Yes' for completion.
    """
    task_mock = MagicMock()
    task_mock.priority = 1
    task_mock.content = "No due task"
    task_mock.description = None
    task_mock.labels = []
    task_mock.due = None
    task_mock.is_completed = True

    table = TodoistClient.tasks_totable([task_mock])

    # Validate table content
    assert "No due task" in table
    assert "Yes" in table  # Completed
    assert "—" in table  # Missing due date
