import typer
from rich import print

calendar_app = typer.Typer(help="Calendar commands")


@calendar_app.command("show")
def show_calendar(days: int = 1):
    from client.gcal_client import GCalClient

    gc = GCalClient()
    events = gc.get_events(next_n_days=days)

    print(f"[bold cyan]Calendar for next {days} day(s):[/bold cyan]\n")
    for e in events:
        print(f"- {e['start']} -> {e['end']} | {e['summary']}")
