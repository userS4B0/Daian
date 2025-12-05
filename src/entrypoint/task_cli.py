import typer
from rich import print

tasks_app = typer.Typer(help="Task-related commands")

@tasks_app.command("list-toschedule")
def list_tasks(label: str = typer.Option("Agendar", help="Filter task list by label")):
    from client.todoist_client import TodoistClient

    client = TodoistClient()
    tasks = client.get_tasks(label=label)

    print(f"[bold cyan]Showing tasks[/bold cyan]\n\n{client.tasks_totable(tasks)}")
    
  
@tasks_app.command("estimate")
def estimate_task(task_id: str):
    from client.todoist_client import TodoistClient
    from core.heuristic_estimator import HeuristicEstimator

    client = TodoistClient()
    task = client.get_task(task_id)

    estimator = HeuristicEstimator()
    result = estimator.estimate(task)

    print("\n[bold green]Estimation result:[/bold green]")
    print(result)
