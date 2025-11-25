from __future__ import annotations

import pathlib
from datetime import datetime
from tabulate import tabulate

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config.app_settings import (
    GOOGLE_CREDENTIALS_PATH,
    GOOGLE_TOKEN_PATH,
    DEFAULT_TABLEFORMAT,
)
from config.user_settings import GCAL_ID_PERSONALEVENTS, TZ

# Necessaroy scope for complete read/write operations in Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# TODO: Event Movement
# Descr.: Implement proper functionality for event movement & rescheduling


class GCalClient:
    """
    Simple Wrapper to work with google calendar

    Functionality:
        - OAuth2 authentication using user credentials
        - Auto generate & update of `google_token.json`
        - Event Listing
        - Event Creation
        - Event Deletion
        - Event Movement

    This client is designed to integrate in ETL flows,
    personal tasks automation and syncronizing with other APIs.
    """

    def __init__(self):
        """Path initialization, credential containerization and authentication."""
        self.creds_path = pathlib.Path(GOOGLE_CREDENTIALS_PATH)
        self.token_path = pathlib.Path(GOOGLE_TOKEN_PATH)

        self.creds = None
        self.service = None

        self._authenticate()

    # ----------------------------------------------------------------------
    # OAuth2 Authentication
    # ----------------------------------------------------------------------
    def _authenticate(self):
        """
        Handles OAuth2 authentication cycle:
            - If `google_token.json` exists, tries to load it.
            - If it's not valid, it loads an OAuth2 flow on web browser.
            - Saves received token in specific path defined in .env
            - Builds the Google Calendar API client.
        Maneja el ciclo completo de autenticación OAuth2:
        """
        # Load existing token if it's present
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )

        # If token isn't present, executes full authentication flow
        if not self.creds or not self.creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.creds_path), SCOPES
            )
            self.creds = flow.run_local_server(port=0)

            # Save new token
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())

        # Build Google Calendar API Client
        self.service = build("calendar", "v3", credentials=self.creds)

    # ----------------------------------------------------------------------
    # Event listing
    # ----------------------------------------------------------------------
    def list_events(self, calendar_ids: list[str], max_results: int = 10) -> list[dict]:
        """
        Returns a list of calendar events from the desired calendar

        Args:
            max_results (int): Max number of events to retrieve.
            calendar_id (str): ID of Google Calendar to work with.

        Returns:
            list: Event list (dict) retrieved from API.
        """
        events = []

        for calendar_id in calendar_ids:
            try:
                events_result = (
                    self.service.events()
                    .list(
                        calendarId=calendar_id,
                        maxResults=max_results,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                events = events_result.get("items", [])

                # Adds Calendar ID to every event for references
                for e in events:
                    e["_calendar_id"] = calendar_id
                events.extend(events)

            except Exception as e:
                # Raise a new exception with context
                raise RuntimeError(
                    f"Error fetching events from calendar {calendar_id}"
                ) from e

        # Sort all events by start date/time
        events.sort(
            key=lambda e: e.get("start", {}).get("dateTime")
            or e.get("start", {}).get("date")
        )

        return events

    # ----------------------------------------------------------------------
    # Event creation
    # ----------------------------------------------------------------------
    def create_event(
        self,
        summary: str,
        start_dt: datetime,
        end_dt: datetime,
        description: str = "",
        calendar_id=GCAL_ID_PERSONALEVENTS,
    ):
        """
        Creates new event on desired calendar.

        Args:
            summary (str): Event title.
            start_dt (datetime): Event initial Date/Time.
            end_dt (datetime): Event final Date/Time.
            description (str): Event description.
            calendar_id (str): ID of Google Calendar to work

        Returns:
            dict: Created event.
        """
        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": TZ,
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": TZ,
            },
        }

        created = (
            self.service.events().insert(calendarId=calendar_id, body=event).execute()
        )

        return created

    # ----------------------------------------------------------------------
    # Print event table
    # ----------------------------------------------------------------------
    @staticmethod
    def show_event_table(events):
        """Print a list of Google calendar events in a formatted table.

        This method is static because it does not rely on instance attributes.

        Args:
            events (list): A list of Google calendar events.

        The table includes the following columns:
            - Calendar: Calendar associated to the event
            - Title: Event title
            - Start time: Event start date/time
            - End time: Event end date/time
        """
        if not events:
            print("[INFO] No events found.")
            return

        # Build table rows
        table = []
        for event in events:
            title = event.get("summary", "No Title")
            start = event.get("start", {}).get("dateTime") or event.get(
                "start", {}
            ).get("date")
            end = event.get("end", {}).get("dateTime") or event.get("end", {}).get(
                "date"
            )

            # Format datetime
            try:
                if start and "T" in start:
                    start = datetime.fromisoformat(start).strftime("%Y-%m-%d %H:%M")
                if end and "T" in end:
                    end = datetime.fromisoformat(end).strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass

            table.append([title, start, end])

        # Print table with headers
        print(
            tabulate(
                table,
                headers=["Title", "Start time", "End time"],
                tablefmt=DEFAULT_TABLEFORMAT,
            )
        )
