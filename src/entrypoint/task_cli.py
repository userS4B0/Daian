import typer
from rich import print

from client.todoist_client import TodoistClient

from core.td_engine.heuristic_estimator import HeuristicEstimator

from config.config_loader import ConfigLoader

config = ConfigLoader.load_and_validate()

tasks_app = typer.Typer(help="Task-related commands")
todoist_client = TodoistClient(config)


# ----- List tasks -----------------------------------------------------
@tasks_app.command("list-all", help="Lists all tasks & filter quantity by limit.")
def list_all(limit: int = typer.Option(10, help="Limit number of tasks")):
    """List all tasks."""
    all_tasks = todoist_client.get_all_tasks(limit)

    print(
        f"[bold cyan]Showing first {limit} task(s)[/bold cyan]\n{todoist_client.tasks_totable(all_tasks)}"
    )


@tasks_app.command("list-expired", help="List tasks with expired due date by 24h.")
def list_expired():
    """Show all expired tasks."""
    expired_tasks = todoist_client.get_expired_tasks()

    print(
        f"[bold red]Expired tasks:[/bold red]\n{todoist_client.tasks_totable(expired_tasks)}"
    )


@tasks_app.command("list-nonscheduled", help="List tasks ready to re-schedule.")
def list_nonscheduled():
    """Show tasks with no due date assigned."""
    nonscheduled_tasks = todoist_client.get_nonscheduled_tasks()

    print(
        f"[bold yellow]Tasks without schedule:[/bold yellow]\n{todoist_client.tasks_totable(nonscheduled_tasks)}"
    )


@tasks_app.command("estimate", help="Estimates task completion time.")
def estimate_task(task_id: str):
    task = todoist_client.get_task(task_id)

    estimator = HeuristicEstimator(config)
    estimation_result = estimator.estimate(task)

    print(
        f"\n[bold green]Estimation result:[/bold green]\n{estimator.estimation_totable(estimation_result)}"
    )


@tasks_app.command(
    "append-nonschedule",
    help="Appends overdue tasks to nonscheduled query for re-scheduling",
)
def append_nonschedule():
    from core.planner import Planner

    expired_tasks = todoist_client.get_expired_tasks()

    print(
        f"[bold red]Expired tasks:[/bold red]\n{todoist_client.tasks_totable(expired_tasks)}"
    )

    planner = Planner(todoist_client, config)

    planner.add_to_nonscheduled_queue(expired_tasks)

    print("[bold green]New tasks added to re-schedule queue![/bold green]\n")
