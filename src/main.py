from client.todoist_client import TodoistClient
from config.settings import NONSCHEDULED_TASKS_LABEL


def main():
    todoist_client = TodoistClient()

    print("\n== TAREAS SIN AGENDAR ==")
    tasks = todoist_client.get_tasks(label=NONSCHEDULED_TASKS_LABEL)
    todoist_client.show_task_table(tasks)

if __name__ == "__main__":
    main()
