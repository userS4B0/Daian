from todoist_api_python.api import TodoistAPI
from config.settings import TODOIST_API_TOKEN, DEFAULT_TABLEFORMAT
from tabulate import tabulate
from utils.time_utils import normalize_datetime


class TodoistClient(TodoistAPI):
    def __init__(self):
        super().__init__(TODOIST_API_TOKEN)

    @staticmethod
    def show_task_table(tasks):
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

        headers = ["Priority", "ID", "Task", "Due Date", "Completed"]
        print(tabulate(table_data, headers=headers, tablefmt=DEFAULT_TABLEFORMAT))

