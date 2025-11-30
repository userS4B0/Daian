from todoist_api_python.api import TodoistAPI
from tabulate import tabulate

from utils.time_utils import normalize_datetime

from config.app_settings import TODOIST_API_TOKEN, DEF_TABLE_FMT

from config.log.logger import setup_logger

logger = setup_logger(__name__)


class TodoistClient(TodoistAPI):
    """
    Client wrapper for interacting with the Todoist API
    """

    # BUG: Handle connection failed errors
    # Issue URL: https://github.com/userS4B0/my-daily-planner/issues/6
    # Issue URL: https://github.com/userS4B0/my-daily-planner/issues/5
    # Handle program errors when connection to todoist API fails
    # assignees: userS4B0
    # labels: priority_medium, todoist, model_side
    # milestone: v1.0.0

    # ----- Main Constructor -----------------------------------------------
    def __init__(self):
        """
        Initialize the TodoistClient with the API token.
        """
        super().__init__(TODOIST_API_TOKEN)

    # ----- Build task table -----------------------------------------------
    @staticmethod
    def tasks_totable(tasks: list[object]) -> str:
        """
        Builds a table of Todoist tasks

        Args:
            tasks (list[object]): A list of Todoist task objects

        Returns:
            str: formatted tabulate string table with all Todoist tasks
        """
        logger.info("Preparing task table for display")

        tasks_table = []

        if not tasks:
            logger.warning("No tasks found!")
            return

        for task in tasks:
            try:
                logger.debug("Processing task entry")

                formatted_due = (
                    normalize_datetime(task.due.datetime)
                    if task.due and task.due.datetime
                    else "—"
                )

                tasks_table.append(
                    [
                        task.priority,
                        task.content,
                        task.description,
                        task.labels,
                        formatted_due,
                        "Yes" if task.is_completed else "No",
                    ]
                )

            except Exception as e:
                logger.error(f"Failed to process task: {e}")

        headers = ["Priority", "Task", "Description", "Labels", "Due Date", "Completed"]

        return tabulate(tasks_table, headers=headers, tablefmt=DEF_TABLE_FMT)
