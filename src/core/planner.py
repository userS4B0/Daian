from config.log.logger import setup_logger
from config.user_settings import NONSCHEDULED_TASKS_LABEL

logger = setup_logger(__name__)


class Planner:
    """
    High-level controller for task and event management logic.
    Handles classification, updates, and synchronization across services.
    """

    def __init__(self, todoist_client):
        logger.debug("Planner initialized")

        self.todoist = todoist_client

    def remove_task_duedate(self, tasks: list[object]) -> None:
        """
        Remove due date to all provided Todoist tasks.
        """
        for task in tasks:
            if not task.id:
                continue

            self.todoist.update_task(task_id=task.id, due_string="no date")

    def apply_label_to_tasks(self, tasks: list[object], label: str) -> None:
        """
        Assign the specified label to all provided Todoist tasks.
        """
        for task in tasks:
            if not task.id:
                continue

            self.todoist.update_task(task_id=task.id, labels=[label])

    def add_to_nonscheduled_queue(self, tasks: list[object]) -> None:
        """
        Adds a list of Todoist tasks to the nonscheduled tasks queue for future re-scheduling
        """

        self.remove_task_duedate(tasks)
        self.apply_label_to_tasks(tasks, NONSCHEDULED_TASKS_LABEL)
