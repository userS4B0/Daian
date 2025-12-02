from core.duration_engine import DurationEngine

from config.log.logger import setup_logger
from config.user_settings import NONSCHEDULED_TASKS_LABEL

logger = setup_logger(__name__)

# FEATURE: Implement basic google calendar event functions
# Implement rearranging Google Calendar Events
# assignees: userS4B0
# labels: priority_medium, core, controller_side
# milestone: v1.0.0
class Planner:
    """
    High-level controller for task and event management logic.
    Handles classification, updates, and synchronization across services.
    """

    def __init__(self, todoist_client, history_path=None):
        logger.debug("Planner initialized")

        self.todoist = todoist_client
        self.duration_engine = DurationEngine(history_path)

    def remove_task_duedate(self, tasks: list[object]) -> None:
        """
        Remove due date to all provided Todoist tasks.
        """
        for task in tasks:
            if not task.id:
                continue

            self.todoist.update_task(task_id=task.id, due_string="no date")

    def apply_label_to_tasks(self, tasks: list[object], new_label: str) -> None:
        """
        Assign the specified label to all provided Todoist tasks.
        """
        for task in tasks:
            if not task.id:
                continue

            # Copy existing labels and add new one if missing
            task_labels = task.labels
            if new_label not in task_labels:
                task_labels.append(new_label)

            self.todoist.update_task(task_id=task.id, labels=task_labels)

    def add_to_nonscheduled_queue(self, tasks: list[object]) -> None:
        """
        Adds a list of Todoist tasks to the nonscheduled tasks queue for future re-scheduling
        """

        self.remove_task_duedate(tasks)
        self.apply_label_to_tasks(tasks, NONSCHEDULED_TASKS_LABEL)

    def estimate_duration(self, task):
        return self.duration_engine.estimate(task)