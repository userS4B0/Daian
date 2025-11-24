from client.todoist_client import TodoistClient

def main():
    todoist_client = TodoistClient()

    print("\n== TAREAS SIN AGENDAR ==")
    tasks = todoist_client.get_nonscheduled_tasks()
    print("[DEBUG] Lista de tareas con label Obtenida")
    todoist_client.show_task_list(tasks)
    print("[DEBUG] Tareas en formato lista mostradas")



if __name__ == "__main__":
    main()
