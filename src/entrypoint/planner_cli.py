import typer
from rich import print

from core.planner import Planner
from core.td_engine.heuristic_estimator import HeuristicEstimator

from client.gcal_client import GCalClient
from client.todoist_client import TodoistClient

from config.config_loader import ConfigLoader

config = ConfigLoader.load_and_validate()

planner_app = typer.Typer(help="Planning commands")


@planner_app.command("show-avaliability", help="Shows current week avaliability.")
def show_avaliability():
    gcal_client = GCalClient(config)

    todoist_client = None
    
    planner = Planner(todoist_client, config)

    thisweek_events = gcal_client.get_thisweek_events()
    free_slots = planner.get_free_slots(thisweek_events)

    print(
        f"[bold cyan] This week's avaliability:[/bold cyan]\n{planner.free_slots_totable(free_slots)}"
    )


@planner_app.command("estimate", help="Estimates task completion time.")
def estimate_task(task_id: str):
    todoist_client = TodoistClient(config)

    task = todoist_client.get_task(task_id)

    estimator = HeuristicEstimator(config)
    estimation_result = estimator.estimate(task)

    print(
        f"\n[bold green]Estimation result:[/bold green]\n{estimator.estimation_totable(estimation_result)}"
    )


@planner_app.command(
    "append-nonschedule",
    help="Appends overdue tasks to nonscheduled query for re-scheduling",
)
def append_nonschedule():
    from core.planner import Planner

    todoist_client = TodoistClient(config)

    expired_tasks = todoist_client.get_expired_tasks()

    print(
        f"[bold red]Expired tasks:[/bold red]\n{todoist_client.tasks_totable(expired_tasks)}"
    )

    planner = Planner(todoist_client, config)

    planner.add_to_nonscheduled_queue(expired_tasks)

    print("[bold green]New tasks added to re-schedule queue![/bold green]\n")
