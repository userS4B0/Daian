import typer
from rich import print

tasks_app = typer.Typer(help="Task-related commands")

@tasks_app.command("list-expired")
def list_tasks():
    from client.todoist_client import TodoistClient

    client = TodoistClient()
    tasks = client.get_expired_tasks()


    print(f"[bold cyan]Showing expired tasks[/bold cyan]\n{client.tasks_totable(tasks)}")
    
  
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
