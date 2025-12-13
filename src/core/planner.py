from typing import Dict, Any, List

from datetime import datetime

from core.td_engine.task_duration_engine import TaskDurationEngine

from config.log.logger import setup_logger
from config.config_loader import ConfigLoader

from utils.time_utils import get_current_week, normalize_datetime
from utils.str_utils import generate_datatable

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

    def __init__(self, todoist_client: object, config: Dict[str, Any] | None = None):
        logger.debug("Planner initialized")

        if config is None:
            logger.debug("No config provided to Planner, loading via ConfigLoader...")
            config = ConfigLoader.load_and_validate()

        self.todoist = todoist_client
        self.duration_engine = TaskDurationEngine(config)

        _DATETIME_FMT = (
            config.get("app", {})
            .get("display", {})
            .get("datetime_fmt", "%Y-%m-%d %H:%M")
        )

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

    # ----- Get free Google Calendar slots ---------------------------------
    @staticmethod
    def get_free_slots(
        events: list[dict],
        week_start: "datetime | None" = None,
        week_end: "datetime | None" = None,
    ) -> list[dict]:
        """
        Identify free time intervals in the weekly calendar.

        Args:
            events (list[dict]): List of calendar events already sorted by start time.
            week_start (datetime | None): Optional start of the week.
                If not provided, will use get_current_week() internally.
            week_end (datetime | None): Optional end of the week.
                If not provided, will use get_current_week() internally.

        Returns:
            list[dict]: List of free time slots as dictionaries with 'start' and 'end' keys.
        """
        logger.debug("Calculating free slots based on provided events")

        free_slots = []

        # Use provided week_start/week_end or fallback to get_current_week()
        if week_start is None or week_end is None:
            week_start_str, week_end_str = get_current_week()
            week_start = normalize_datetime(week_start_str)
            week_end = normalize_datetime(week_end_str)

        current = week_start  # Initial pointer at the start of the week

        for event in events:
            start_str = event.get("start", {}).get("dateTime") or event.get(
                "start", {}
            ).get("date")
            end_str = event.get("end", {}).get("dateTime") or event.get("end", {}).get(
                "date"
            )

            if not start_str or not end_str:
                logger.warning("Event without valid datetime fields detected")
                continue

            event_start = normalize_datetime(start_str)
            event_end = normalize_datetime(end_str)

            # If there is a gap between current pointer and next event, record it
            if event_start > current:
                free_slots.append({"start": current, "end": event_start})

            # Move pointer forward
            if event_end > current:
                current = event_end

        # Final gap until end of week
        if current < week_end:
            free_slots.append({"start": current, "end": week_end})

        logger.debug("Free slots calculated successfully")
        return free_slots

    # ----- Build free slots table -----------------------------------------
    @staticmethod
    def free_slots_totable(free_slots: list[dict]) -> str:
        """
        Convert a list of free slots into a formatted table string.

        Args:
            free_slots (List[Dict]): List of free slot dictionaries.

        Returns:
            str: A printable table generated with tabulate.
        """

        free_slot_data = []

        for slot in free_slots:
            free_slot_data.append(
                [
                    slot["start"].strftime("%Y-%m-%d %H:%M"),
                    slot["end"].strftime("%Y-%m-%d %H:%M"),
                    str(slot["end"] - slot["start"]),
                ]
            )

        free_slots_headers = ["Free From", "Free Until", "Duration"]

        return generate_datatable(free_slot_data, free_slots_headers)

    def estimate_duration(self, task):
        return self.duration_engine.estimate(task)

    def arrange_tasks(self, tasks: List[object]) -> None:
        # Process task list
        # If there's no due date & task labels contain nonscheduled_label, rearrange
        # If there's a pause label, dont arrange
        # If there's an idea label, dont arrange
        # Estimate durations
        # Get calendar free slots
        # Arrange acording to priority and estimation task completion time
        pass
