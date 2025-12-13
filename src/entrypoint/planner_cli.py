import typer
from rich import print

from core.planner import Planner
from core.td_engine.task_duration_engine import TaskDurationEngine

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

    td_engine = TaskDurationEngine(config)
    estimation_result = td_engine.estimate(task)

    print(
        f"\n[bold green]Estimation result:[/bold green]\n{td_engine.estimation_totable(estimation_result)}"
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


@planner_app.command(
    "record-completion",
    help="Record task completion minutes to add history to Daian so it can pull Appends overdue tasks to nonscheduled query for re-scheduling",
)
def record_completion(task_id: str, minutes: float):
    todoist_client = TodoistClient(config)
    task = todoist_client.get_task(task_id)

    td_engine = TaskDurationEngine(config)
    td_engine.record_actual_duration(task, minutes)

    print("[bold green]Actual duration recorded for learning.[/bold green]")
