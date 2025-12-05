import sys

from core.scheduler import Scheduler
from core.planner import Planner
from core.duration_engine import DurationEngine

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

    # ----- Todoist Client -------------------------------------------------
    todoist_client = TodoistClient()

    logger.info(f"Fetching tasks for label: {NONSCHEDULED_TASKS_LABEL}")

    nonscheduled_tasks = todoist_client.get_tasks(label=NONSCHEDULED_TASKS_LABEL)
    print(
        f"\nTareas por {NONSCHEDULED_TASKS_LABEL}:\n{todoist_client.tasks_totable(nonscheduled_tasks)}"
    )

    logger.info("Fetching expired tasks")

    expired_tasks = todoist_client.get_expired_tasks()
    print(f"\nTareas expiradas:\n{todoist_client.tasks_totable(expired_tasks)}")

    # # ----- Planner Operations ---------------------------------------------
    # planner = Planner(todoist_client)

    # # Add expired tasks to re-scheduler query
    # planner.add_to_nonscheduled_queue(expired_tasks)
    # logger.info("New tasks added to re-schedule queue")

    print("\n=== DurationEngine Proof of Concept ===\n")

    duration_engine = DurationEngine()  # usa el .timeflow_history.json por defecto

    # Dummy task para pruebas iniciales
    task = {
        "content": "Write monthly financial report",
        "description": "Review KPIs, gather data, prepare charts and summary",
        "priority": 3,
        "labels": ["deepwork"],
    }

    for task in nonscheduled_tasks:
        result = duration_engine.estimate(task)
        print(f"\nEstimated duration for task: {task.content}")
        print(result)

        # Prueba registrar duración real
        print("\nRegistering actual duration...")
        duration_engine.register_actual(task, actual_minutes=95)

        # Recalcular tras registrar histórico
        result2 = duration_engine.estimate(task)

        print(f"\nEstimated duration after updating history for task: {task.content}")
        print(result2)
    
    # ----- Google Calendar Client -----------------------------------------
    gcal_client = GCalClient()

    calendars = [
        GCAL_ID_TASKS,
        GCAL_ID_PERSONALEVENTS,
        GCAL_ID_TIMEMANAGE,
        GCAL_ID_WORK,
    ]

    logger.info("Fetching events from calendars")

    events = gcal_client.get_thisweek_events(calendars)
    print(f"\nThis week's events:\n{gcal_client.events_totable(events)}")

    # ----- Scheduler Operations -------------------------------------------
    scheduler = Scheduler()

    logger.info("Computing free slots for the current week")

    free_slots = scheduler.get_free_slots(events)

    print(f"\nThis week's avalible slots:\n{scheduler.free_slots_totable(free_slots)}")


if __name__ == "__main__":
    logger.info("My Daily Planner App Started")

    try:
        main()

    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Exiting cleanly...")
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
