import typer
from rich import print

from core.planner import Planner

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


@planner_app.command("estimate", help="Estimate task completion time.")
def estimate_task(
    task_id: str,
    no_learn: bool = typer.Option(
        False,
        "--no-learn",
        help="Do not record estimation result for learning.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Run estimation without side effects (implies --no-learn).",
    ),
):
    todoist_client = TodoistClient(config)
    planner = Planner(todoist_client, config)

    task = todoist_client.get_task(task_id)

    estimation = planner.estimate_duration(
        task,
        learn=not (no_learn or dry_run),
        dry_run=dry_run,
    )

    print(
        f"\n[bold green]Estimation result ({task.content}):[/bold green]\n"
        f"{planner.duration_engine.estimation_totable(estimation)}"
    )

    if dry_run:
        print("[dim]Dry-run: no learning data recorded.[/dim]")
    elif no_learn:
        print("[dim]Learning disabled for this estimation.[/dim]")


@planner_app.command("estimate-nonscheduled", help="Estimate all nonscheduled tasks.")
def estimate_nonscheduled_tasks(
    no_learn: bool = typer.Option(
        False,
        "--no-learn",
        help="Do not record estimation result for learning.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Run estimation without side effects (implies --no-learn).",
    ),
):
    todoist_client = TodoistClient(config)
    planner = Planner(todoist_client, config)

    nonscheduled_tasks = todoist_client.get_nonscheduled_tasks()

    for task in nonscheduled_tasks:
        estimation = planner.estimate_duration(
            task,
            learn=not (no_learn or dry_run),
            dry_run=dry_run,
        )

        print(
            f"\n[bold green]Estimation result ({task.content}):[/bold green]\n"
            f"{planner.duration_engine.estimation_totable(estimation)}"
        )

    if dry_run:
        print("[dim]Dry-run: no learning data recorded.[/dim]")
    elif no_learn:
        print("[dim]Learning disabled for this estimation.[/dim]")


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
    help="Record actual task duration so DAIAN can learn from it.",
)
def record_completion(task_id: str, minutes: float):
    todoist_client = TodoistClient(config)
    planner = Planner(todoist_client, config)

    task = todoist_client.get_task(task_id)
    planner.record_task_completion(task, minutes)

    print("[bold green]✔ Actual duration recorded for learning.[/bold green]")
