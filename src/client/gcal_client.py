from __future__ import annotations

import pathlib

from tabulate import tabulate

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from utils.time_utils import get_current_week, normalize_datetime

from config.app_settings import (
    GOOGLE_CREDENTIALS_PATH,
    GOOGLE_TOKEN_PATH,
    DEF_TABLE_FMT,
)

from config.log.logger import setup_logger

logger = setup_logger(__name__)

# Necessaroy scope for complete read/write operations in Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GCalClient:
    """
    Client Wrapper to work with Google Calendar API
    """

    # ----- Main Constructor -----------------------------------------------
    def __init__(self):
        """Path initialization, credential containerization and authentication."""

        creds_raw = GOOGLE_CREDENTIALS_PATH or "/dev/null"
        token_raw = GOOGLE_TOKEN_PATH or "/dev/null"

        self.creds_path = pathlib.Path(creds_raw)
        self.token_path = pathlib.Path(token_raw)

        self.creds = None
        self.service = None

        self._authenticate()
        logger.debug("GcalClient initialized")

    # ----- OAuth2 Authentication ------------------------------------------
    def _authenticate(self):
        """
        Handles OAuth2 authentication cycle.
        """

        # Load existing token if it's present
        logger.debug("Attempting to fetch google token file")
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )

        # If token isn't present, executes full authentication flow
        logger.debug("Google Token not found, executing full authentication flow")
        if not self.creds or not self.creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.creds_path), SCOPES
            )
            self.creds = flow.run_local_server(port=0)

            # Save new token
            logger.debug("Google Token generated & saved")
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())

        # Build Google Calendar API Client
        logger.debug("Building Google Calendar API")
        self.service = build("calendar", "v3", credentials=self.creds)

    # ----- List specific number of events ---------------------------------
    def get_numberof_events(
        self, calendar_ids: list[str], max_results: int = 10
    ) -> list[dict]:
        """
        Returns a list of a desired number (defaults 10 events) of events from different calendars.

        Args:
            calendar_ids (list[str]): List of calendar IDs to fetch events from.
            max_results (int): Max number of events to retrieve.

        Returns:
            list[dict]: Event list (dict) retrieved from API.
        """
        retrieved_events = []

        for calendar_id in calendar_ids:
            try:
                logger.debug("Processing calendar events")

                fetched_events = (
                    self.service.events()
                    .list(
                        calendarId=calendar_id,
                        maxResults=max_results,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                events = fetched_events.get("items", [])

                # Adds Calendar ID to every event for references
                for event in events:
                    event["_calendar_id"] = calendar_id

                # Add events to the combined list
                retrieved_events.extend(events)

            except Exception as e:
                logger.error(f"Failed to process calendar: {e}")

        return self.sort_events_by_date(retrieved_events)

    # ----- List this week's events ----------------------------------------
    def get_thisweek_events(self, calendar_ids: list[str]) -> list[dict]:
        """
        Retrieve all events from the current week across multiple calendars.

        Args:
            calendar_ids (list[str]): List of calendar IDs to fetch events from.

        Returns:
            list[dict]: Combined list of all events from the current week.
        """
        retrieved_events = []

        # Get ISO 8601 start and end of current week
        week_start_str, week_end_str = get_current_week()

        for calendar_id in calendar_ids:
            try:
                logger.debug("Processing calendar events")

                # Fetch events for the calendar within the week range
                fetched_events = (
                    self.service.events()
                    .list(
                        calendarId=calendar_id,
                        timeMin=week_start_str,
                        timeMax=week_end_str,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )

                events = fetched_events.get("items", [])

                # Adds Calendar ID to every event for references
                for event in events:
                    event["_calendar_id"] = calendar_id

                # Add events to the combined list
                retrieved_events.extend(events)

            except Exception as e:
                logger.error(f"Failed to process calendar: {e}")

        return self.sort_events_by_date(retrieved_events)

    # ----- Build event table ----------------------------------------------
    @staticmethod
    def events_totable(events: list[dict]) -> str:
        """Formats a list of Google calendar events in a formatted table.

        Args:
            events (list[dict]): A list of Google calendar events.

        Returns:
            str: formatted tabulate string table with all Google Calendar events
        """
        logger.info("Preparing events table for display")

        if not events:
            logger.warning("No events found!")
            return

        events_table = []
        # Build table rows

        for event in events:
            logger.debug("Processing event entry")

            title = event.get("summary", "No Title")
            start = event.get("start", {}).get("dateTime") or event.get(
                "start", {}
            ).get("date")
            end = event.get("end", {}).get("dateTime") or event.get("end", {}).get(
                "date"
            )

            # Format datetime
            start_fmt = normalize_datetime(start)
            end_fmt = normalize_datetime(end)

            events_table.append([title, start_fmt, end_fmt])

        # Print table with headers
        logger.debug("Rendering event table for console output")

        return tabulate(
            events_table,
            headers=["Title", "Start time", "End time"],
            tablefmt=DEF_TABLE_FMT,
        )

    # ----- Sort Events ----------------------------------------------------
    @staticmethod
    def sort_events_by_date(events: list[dict]) -> list[dict]:
        """
        Sorts a list of Google calendar events by start date & time.

        Args:
            events (list[dict]): A list of Google Calendar events.

        Returns:
            list[dict]: A list of Google Calendar events sorted by date & time.
        """
        return sorted(
            events,
            key=lambda e: e.get("start", {}).get("dateTime")
            or e.get("start", {}).get("date"),
        )
