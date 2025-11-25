from client.todoist_client import TodoistClient
from config.settings import NONSCHEDULED_TASKS_LABEL

from client.gcal_client import GCalClient


def main():
    todoist_client = TodoistClient()

    print(f"\n[INFO] Fetching tasks for label: {NONSCHEDULED_TASKS_LABEL}\n")
    tasks = todoist_client.get_tasks(label=NONSCHEDULED_TASKS_LABEL)
    todoist_client.show_task_table(tasks)

    gcal_client = GCalClient()

    print("[INFO] Scheduled events:")
    for evt in gcal_client.list_events(5):
        print(f"- {evt.get('summary')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Program interrupted by user. Exiting cleanly...\n")
