from todoist_api_python.api import TodoistAPI
from utils.time_utils import normalize_datetime
# from client.todoist_client import TodoistClient


from config.settings import TODOIST_API_TOKEN

def main():
    todoist_client = TodoistAPI(TODOIST_API_TOKEN)

    try:
        # print("== PROYECTOS ==")
        # for p in todoist_client.get_projects():
        #     print(f"- {p.name} (ID: {p.id})")

        print("\n== TAREAS SIN AGENDAR ==")
        tasks = todoist_client.get_tasks(label="Agendar")

        if not tasks:
            print("No hay tareas sin agendar.")
            return

        for t in tasks:
            due = normalize_datetime(t.due.datetime) if t.due and t.due.datetime else None
            print(f"| P{t.priority} | {t.content} | ID:  {t.id} | Due: {due}")

    except Exception as e:
        print("❌ Error en la comunicación con Todoist:", e)


if __name__ == "__main__":
    main()
