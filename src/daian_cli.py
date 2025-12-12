import typer

from entrypoint.task_cli import tasks_app
from entrypoint.calendar_cli import calendar_app
from entrypoint.planner_cli import planner_app
from entrypoint.config_cli import config_app

app = typer.Typer(
    help="DAIAN – Digital Assistant for Intelligent Agenda & Notifications"
)

# Subcommands
app.add_typer(tasks_app, name="tasks", help="Manage and inspect Todoist tasks")
app.add_typer(calendar_app, name="calendar", help="Interact with Google Calendar")
app.add_typer(planner_app, name="planner", help="Task and calendar arrangements planner")
app.add_typer(config_app, name="config", help="Interact with Daian configruation")

def main():
    app()


if __name__ == "__main__":
    main()
