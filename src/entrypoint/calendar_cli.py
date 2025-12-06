import typer
from rich import print

from client.gcal_client import GCalClient

from config.user_settings import GCAL_ID_TASKS, GCAL_ID_PERSONALEVENTS, GCAL_ID_TIMEMANAGE, GCAL_ID_WORK

calendar_ids = [GCAL_ID_TASKS, GCAL_ID_PERSONALEVENTS, GCAL_ID_TIMEMANAGE, GCAL_ID_WORK]

calendar_app = typer.Typer(help="Google Calendar interactions.")

@calendar_app.command("show-all", help="Prints all events & filters quantity from `limit` flag.")
def show_all_events(limit: int = 5, help="limits number of events to show."):
    
    gcal_client = GCalClient()
    
    events = gcal_client.get_numberof_events(calendar_ids, limit)

    print(f"[bold cyan] Next {limit} events(s):[/bold cyan]\n{gcal_client.events_totable(events)}")

@calendar_app.command("show-thisweek", help="Shows current week events.")
def show_thisweek_events():
    
    gcal_client = GCalClient()
    
    thisweek_events = gcal_client.get_thisweek_events(calendar_ids)

    print(f"[bold cyan] This week's events(s):[/bold cyan]\n{gcal_client.events_totable(thisweek_events)}")

@calendar_app.command("show-avaliability", help="Shows current week avaliability.")
def show_avaliability():

    from core.scheduler import Scheduler

    gcal_client = GCalClient()
    scheduler = Scheduler()
    
    thisweek_events = gcal_client.get_thisweek_events(calendar_ids)
    free_slots = scheduler.get_free_slots(thisweek_events)

    print(f"[bold cyan] This week's avaliability:[/bold cyan]\n{scheduler.free_slots_totable(free_slots)}")