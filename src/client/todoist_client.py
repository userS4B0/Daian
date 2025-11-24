from todoist_api_python.api import TodoistAPI
from config.settings import TODOIST_API_TOKEN, DEFAULT_TABLEFORMAT
from tabulate import tabulate
from utils.time_utils import normalize_datetime


class TodoistClient(TodoistAPI):
    """Client wrapper for interacting with the Todoist API.

    Extends the TodoistAPI class to provide utility functions such as
    displaying tasks in a CLI table format.
    """

    def __init__(self):
        """Initialize the TodoistClient with the API token."""
        super().__init__(TODOIST_API_TOKEN)

    @staticmethod
    def show_task_table(tasks):
        """Print a list of Todoist tasks in a formatted table.

        This method is static because it does not rely on instance attributes.

        Args:
            tasks (list): A list of Todoist task objects.

        The table includes the following columns:
            - Priority: Task priority level
            - Content: Main task description
            - Description: Extended task description
            - Labels: Associated label IDs
            - Due Date: Normalized due date or '—' if not set
            - Completed: 'Yes' if the task is completed, otherwise 'No'
        """
        table_data = []

        for task in tasks:
            formatted_due = (
                normalize_datetime(task.due.datetime)
                if task.due and task.due.datetime
                else "—"
            )

            table_data.append(
                [
                    task.priority,
                    task.content,
                    task.description,
                    task.labels,
                    formatted_due,
                    "Yes" if task.is_completed else "No",
                ]
            )

        headers = ["Priority", "Task", "Description", "Labels", "Due Date", "Completed"]
        print(tabulate(table_data, headers=headers, tablefmt=DEFAULT_TABLEFORMAT))
