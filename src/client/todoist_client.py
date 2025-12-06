from todoist_api_python.api import TodoistAPI
from tabulate import tabulate

from utils.time_utils import normalize_datetime, is_expired_by_days

from config.app_settings import TODOIST_API_TOKEN, DEF_TABLE_FMT
from config.user_settings import NONSCHEDULED_TASKS_LABEL
from config.log.logger import setup_logger

logger = setup_logger(__name__)


# FEATURE: Implement task retrieving cache
# Issue URL: https://github.com/userS4B0/my-daily-planner/issues/8
# Ensure minimizing API request by defining local cache
# assignees: userS4B0
# labels: priority_low, todoist, model_side, feature
# milestone: v1.0.1
class TodoistClient(TodoistAPI):
    """
    Client wrapper for interacting with the Todoist API
    """

    # BUG: Handle connection failed errors
    # Issue URL: https://github.com/userS4B0/my-daily-planner/issues/6
    # Handle program errors when connection to todoist API fails
    # assignees: userS4B0
    # labels: priority_medium, todoist, model_side, bug
    # milestone: v1.0.0

    # ----- Main Constructor -----------------------------------------------
    def __init__(self):
        """
        Initialize the TodoistClient with the API token.
        """
        super().__init__(TODOIST_API_TOKEN)

    # ----- Retrieve expired tasks -----------------------------------------
    def get_expired_tasks(self) -> list[object]:
        """
        Return tasks whose due date expired more than 1 day ago.

        Returns:
            list[object]: List of overdue tasks (more than 1 day old)
        """
        expired_tasks = []

        all_tasks = self.get_tasks()

        for task in all_tasks:
            if not task.due:
                continue

            # Skip recurrent tasks
            if task.due.is_recurring:
                continue

            # Now offload the comparison to utility function
            if is_expired_by_days(task.due.date, days=1):
                expired_tasks.append(task)

        return expired_tasks

    # ----- Retrieve nonshceduled tasks ------------------------------------
    def get_nonscheduled_tasks(self) -> list[object]:
        """
        Return tasks to re-schedule (Tasks with label "NONSCHEDULED_TASKS_LABEL").

        Returns:
            list[object]: List of nonscheduled tasks
        """

        return self.get_tasks(label=NONSCHEDULED_TASKS_LABEL)

    # ----- Retrieve nonshceduled tasks ------------------------------------
    def get_all_tasks(self, limit: int = 10) -> list[object]:
        """
        Return all tasks & trim task list by limit.

        Args:
            limit[int]: limits how many tasks it retrieves.
        Returns:
            list[object]: List of nonscheduled tasks
        """
        all_tasks = self.get_tasks()

        if limit:
            return all_tasks[:limit]
        
        return all_tasks

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
                        task.id,
                        task.priority,
                        task.content,
                        task.labels,
                        formatted_due,
                    ]
                )

            except Exception as e:
                logger.error(f"Failed to process task: {e}")

        headers = ["ID", "Priority", "Task", "Labels", "Due Date"]

        return tabulate(tasks_table, headers=headers, tablefmt=DEF_TABLE_FMT)
