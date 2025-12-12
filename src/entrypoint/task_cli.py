import typer
from rich import print

from client.todoist_client import TodoistClient

from config.config_loader import ConfigLoader

config = ConfigLoader.load_and_validate()

tasks_app = typer.Typer(help="Task-related commands")

# ----- List tasks -----------------------------------------------------
@tasks_app.command("list-all", help="Lists all tasks & filter quantity by limit.")
def list_all(limit: int = typer.Option(10, help="Limit number of tasks")):
    """List all tasks."""
    todoist_client = TodoistClient(config)

    all_tasks = todoist_client.get_all_tasks(limit)

    print(
        f"[bold cyan]Showing first {limit} task(s)[/bold cyan]\n{todoist_client.tasks_totable(all_tasks)}"
    )


@tasks_app.command("list-expired", help="List tasks with expired due date by 24h.")
def list_expired():
    """Show all expired tasks."""
    todoist_client = TodoistClient(config)

    expired_tasks = todoist_client.get_expired_tasks()

    print(
        f"[bold red]Expired tasks:[/bold red]\n{todoist_client.tasks_totable(expired_tasks)}"
    )


@tasks_app.command("list-nonscheduled", help="List tasks ready to re-schedule.")
def list_nonscheduled():
    """Show tasks with no due date assigned."""
    todoist_client = TodoistClient(config)

    nonscheduled_tasks = todoist_client.get_nonscheduled_tasks()

    print(
        f"[bold yellow]Tasks without schedule:[/bold yellow]\n{todoist_client.tasks_totable(nonscheduled_tasks)}"
    )
