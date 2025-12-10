import typer
from rich import print

from client.gcal_client import GCalClient

from config.config_loader import ConfigLoader

config = ConfigLoader.load_and_validate()

calendar_app = typer.Typer(help="Google Calendar interactions.")
gcal_client = GCalClient(config)

@calendar_app.command("show-all", help="Prints all events & filters quantity from `limit` flag.")
def show_all_events(limit: int = 5, help="limits number of events to show."):
    
    events = gcal_client.get_numberof_events(limit)

    print(f"[bold cyan] Next {limit} events(s):[/bold cyan]\n{gcal_client.events_totable(events)}")

@calendar_app.command("show-thisweek", help="Shows current week events.")
def show_thisweek_events():
    
    thisweek_events = gcal_client.get_thisweek_events()

    print(f"[bold cyan] This week's events(s):[/bold cyan]\n{gcal_client.events_totable(thisweek_events)}")

@calendar_app.command("show-avaliability", help="Shows current week avaliability.")
def show_avaliability():

    from core.scheduler import Scheduler

    scheduler = Scheduler(config)
    
    thisweek_events = gcal_client.get_thisweek_events()
    free_slots = scheduler.get_free_slots(thisweek_events)

    print(f"[bold cyan] This week's avaliability:[/bold cyan]\n{scheduler.free_slots_totable(free_slots)}")