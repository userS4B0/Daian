from typing import Dict, Any, List

from core.duration_engine import DurationEngine

from config.log.logger import setup_logger

logger = setup_logger(__name__)

# FEATURE: Implement basic google calendar event functions
# Implement rearranging Google Calendar Events
# assignees: userS4B0
# labels: priority_medium, core, controller_side, feature
# milestone: v1.0.0
class Planner:
    """
    High-level controller for task and event management logic.
    Handles classification, updates, and synchronization across services.
    """

    def __init__(self, todoist_client: object, config: Dict[str, Any] = None):
        logger.debug("Planner initialized")

        self.todoist = todoist_client
        self.duration_engine = DurationEngine(config)

    def remove_task_duedate(self, tasks: List[object]) -> None:
        """
        Remove due date to all provided Todoist tasks.
        """
        for task in tasks:
            if not task.id:
                continue

            self.todoist.update_task(task_id=task.id, due_string="no date")

    def apply_label_to_tasks(self, tasks: List[object], new_label: str) -> None:
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

    def add_to_nonscheduled_queue(self, tasks: List[object], nonsch_label: str) -> None:
        """
        Adds a list of Todoist tasks to the nonscheduled tasks queue for future re-scheduling
        """

        self.remove_task_duedate(tasks)
        self.apply_label_to_tasks(tasks, nonsch_label)

    def estimate_duration(self, task):
        return self.duration_engine.estimate(task)