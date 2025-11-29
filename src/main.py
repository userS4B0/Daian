import sys

from core.scheduler import Scheduler

from client.todoist_client import TodoistClient
from client.gcal_client import GCalClient

from config.user_settings import NONSCHEDULED_TASKS_LABEL
from config.user_settings import (
    GCAL_ID_TASKS,
    GCAL_ID_PERSONALEVENTS,
    GCAL_ID_TIMEMANAGE,
    GCAL_ID_WORK,
)

from config.log.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """
    Entry point for My Daily Planner.
    Fetches Todoist tasks, Google Calendar events,
    computes free weekly slots and prints outputs.
    """

    # --- Todoist tasks ---
    todoist_client = TodoistClient()

    logger.info(f"Fetching tasks for label: {NONSCHEDULED_TASKS_LABEL}")
    print(f"\nFetching tasks for label: {NONSCHEDULED_TASKS_LABEL}\n")

    tasks = todoist_client.get_tasks(label=NONSCHEDULED_TASKS_LABEL)
    todoist_client.show_task_table(tasks)

    # --- Google Calendar events ---
    gcal_client = GCalClient()

    calendars = [
        GCAL_ID_TASKS,
        GCAL_ID_PERSONALEVENTS,
        GCAL_ID_TIMEMANAGE,
        GCAL_ID_WORK,
    ]

    logger.info("Fetching events from calendars")
    print("\nShowing this week's events from all calendars:")

    events = gcal_client.get_thisweek_events(calendars)
    gcal_client.show_event_table(events)

    # --- Scheduler operations ---
    scheduler = Scheduler()

    logger.info("Computing free slots for the current week")
    print("\nDetected free slots for this week:\n")

    free_slots = scheduler.get_free_slots(events)

    free_slots_table = scheduler.free_slots_totable(free_slots) 
    print(free_slots_table)


if __name__ == "__main__":
    logger.info("My Daily Planner App Started")

    try:
        main()

    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Exiting cleanly...")
        print("\n[INFO] Program interrupted by user. Exiting cleanly...\n")
        sys.exit(0)

    except ValueError as e:
        logger.warning(f"ValueError: {e}")
        sys.exit(0)

    except RuntimeError as e:
        logger.warning(f"RuntimeError: {e}")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unhandled Error: {e}")
        sys.exit(0)

    finally:
        logger.info("My Daily Planner App Terminated")
