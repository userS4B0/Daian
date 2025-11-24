from todoist_api_python.api import TodoistAPI
from config.settings import TODOIST_API_TOKEN, NONSCHEDULED_TASKS_LABEL
from tabulate import tabulate
from utils.time_utils import normalize_datetime


class TodoistClient(TodoistAPI):
    def __init__(self):
        super().__init__(TODOIST_API_TOKEN)

    def get_nonscheduled_tasks(self):
        print(
            f"[DEBUG] Obteniendo lista de tareas con label {NONSCHEDULED_TASKS_LABEL}"
        )

        try:
            return self.get_tasks(label=NONSCHEDULED_TASKS_LABEL)
        except Exception as e:
            raise RuntimeError(f"Error in Todoist communication: {e}")

    def show_task_table(tasks: list):

        for task in tasks:
            formatted_due = (
                normalize_datetime(task.due.datetime)
                if task.due and task.due.datetime
                else None
            )
        table_data = [
            [
                task.id,
                task.content,
                formatted_due if (task.due and task.due.date) else "—",
                "Yes" if task.is_completed else "No",
            ]
        ]

        headers = ["ID", "Task", "Due Date", "Completed"]
        return tabulate(table_data, headers=headers, tablefmt="github")

    def show_task_list(tasks: list):
        print("[DEBUG] Mostrando tareas en formato lista")

        for task in tasks:
            formatted_due = (
                normalize_datetime(task.due.datetime)
                if task.due and task.due.datetime
                else None
            )
            print(f"[P{task.priority}] {task.content}")
            print(f"  ID:  {task.id}")
            print(f"  Due: {formatted_due}\n")
