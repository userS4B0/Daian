from todoist_api_python.api import TodoistAPI

from tabulate import tabulate

from utils.time_utils import normalize_datetime, is_expired_by_days

from config.app_settings import TODOIST_API_TOKEN, DEF_TABLE_FMT
from config.user_settings import NONSCHEDULED_TASKS_LABEL

from config.config_loader import ConfigLoader
from config.log.logger import setup_logger

logger = setup_logger(__name__)

config = ConfigLoader._deep_merge(
    ConfigLoader.load("user_settings"), ConfigLoader.load("app_settings")
)


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

    # ----- Main Constructor -----------------------------------------------
    def __init__(self):
        """
        Initialize the TodoistClient with the API token.
        """
        logger.debug("Initializing TodoistClient instance...")

        todoist_api_token = config.get("todoist", {}).get("api_token", {})

        if not todoist_api_token:
            logger.error("Todoist API Token not set in configuration")

        logger.debug("Authenticating to Todoist API...")

        try:
            super().__init__(todoist_api_token)
            logger.info("Daian succesfully authenticated to Todoist API")

        except Exception as e:
            logger.error(f"Todoist authentication failed: {e}")
            raise RuntimeError("Unable to authenticate to Todoist API") from e

        logger.debug("TodoistClient initialized...")

    # ----- Get tasks wrapper ----------------------------------------------
    def get_tasks_wrapper(self, **kwargs):
        """
        Wrapper around get_tasks() to handle API errors gracefully.
        """
        try:
            return self.get_tasks(**kwargs)

        except Exception as e:
            if getattr(e, "status_code", None) == 401:
                logger.error("Unauthorized: check your Todoist API token")
            else:
                logger.error(f"Todoist API error: {e}")
                
            return []

    # ----- Retrieve expired tasks -----------------------------------------
    def get_expired_tasks(self) -> list[object]:
        """
        Return tasks whose due date expired more than 1 day ago.

        Returns:
            list[object]: List of overdue tasks (more than 1 day old)
        """
        expired_tasks = []
        all_tasks = self.get_tasks_wrapper()

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
        nonscheduled_tasks_label = (
            config.get("todoist", {}).get("labels", {}).get("nonscheduled_tasks", {})
        )

        if not nonscheduled_tasks_label:
            logger.error("nonscheduled_tasks_label not set in configuration")

        return self.get_tasks_wrapper(label=nonscheduled_tasks_label)

    # ----- Retrieve all tasks --------------------------------------------
    def get_all_tasks(self, limit: int = 10) -> list[object]:
        """
        Return all tasks & trim task list by limit.

        Args:
            limit[int]: limits how many tasks it retrieves.
        Returns:
            list[object]: List of nonscheduled tasks
        """
        all_tasks = self.get_tasks_wrapper()

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
        table_fmt = config.get("app", {}).get("display", {}).get("table_fmt", {})
        tasks_table = []

        if not table_fmt:
            logger.warning("table_fmt not set in configuration")
            table_fmt = "rounded_outline"

        if not tasks:
            logger.warning("No tasks found!")
            return

        for task in tasks:
            try:
                logger.debug(f"Processing task entry: id {task.id}")

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

        return tabulate(
            tasks_table,
            headers=headers,
            tablefmt=table_fmt,
        )
