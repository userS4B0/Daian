from client.todoist_client import TodoistClient
from config.user_settings import NONSCHEDULED_TASKS_LABEL

from client.gcal_client import GCalClient

from config.user_settings import (
    GCAL_ID_MYTASKS,
    GCAL_ID_PERSONALEVENTS,
    GCAL_ID_TIMEMANAGE,
    GCAL_ID_WORK
)


def main():
    todoist_client = TodoistClient()

    print(f"\n[INFO] Fetching tasks for label: {NONSCHEDULED_TASKS_LABEL}\n")
    tasks = todoist_client.get_tasks(label=NONSCHEDULED_TASKS_LABEL)
    todoist_client.show_task_table(tasks)

    gcal_client = GCalClient()

    print("\n[INFO] Scheduled events:")
    events = gcal_client.list_events(5, GCAL_ID_WORK)
    gcal_client.show_event_table(events)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Program interrupted by user. Exiting cleanly...\n")
