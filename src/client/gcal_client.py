from __future__ import annotations

import pathlib

from typing import List, Dict, Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from utils.time_utils import get_current_week, normalize_datetime
from utils.str_utils import generate_datatable

from config.log.logger import setup_logger

logger = setup_logger(__name__)

# Necessary scope for complete read/write operations in Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GCalClient:
    """
    Client Wrapper to work with Google Calendar API
    """

    # ----- Main Constructor -----------------------------------------------
    def __init__(self, config: Dict[str, Any] = None):
        """Path initialization, credential containerization and authentication."""

        logger.debug("Initializing GcalClient instance...")
        self.gcal_client_cfg = config.get("google", {})

        _GOOGLE_CREDENTIALS_PATH = self.gcal_client_cfg.get("credentials_path", "")
        _GOOGLE_TOKEN_PATH = self.gcal_client_cfg.get("token_path", "")

        if not _GOOGLE_CREDENTIALS_PATH:
            logger.error("google_credentials_path not found in config.")
            raise ValueError("google_credentials_path not found in config.")

        if not _GOOGLE_TOKEN_PATH:
            logger.error("google_token_path not found in config.")
            raise ValueError("google_token_path not found in config.")

        self.creds_path = pathlib.Path(_GOOGLE_CREDENTIALS_PATH)
        self.token_path = pathlib.Path(_GOOGLE_TOKEN_PATH)

        self.credentials = None
        self.service = None

        self.calendars = self.gcal_client_cfg.get("calendars", [])

        if not self.calendars:
            logger.error("No calendars found in config under google.calendars")
            raise ValueError("No calendars found in config under google.calendars")

        logger.debug("Attempting Google Oauth...")

        try:
            self._authenticate()
            logger.info("Daian successfuly authenticated to Google Calendar API")

        except Exception as e:
            logger.error(f"Google Authentication failed: {e}")

        logger.debug("GCalClient initialized")

    # ----- OAuth2 Authentication ------------------------------------------
    def _authenticate(self):
        """
        Handles OAuth2 authentication cycle.
        """

        # Load existing token if it's present
        logger.debug("Attempting to fetch google token file...")

        if self.token_path.exists():
            self.credentials = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )

        # If token isn't present, executes full authentication flow
        logger.debug("Google Token not found, executing full authentication flow")

        if not self.credentials or not self.credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.creds_path), SCOPES
            )
            self.credentials = flow.run_local_server(port=0)

            # Save new token
            logger.debug("Google Token generated & saved")

            with open(self.token_path, "w") as token:
                token.write(self.credentials.to_json())

        # Build Google Calendar API Client
        logger.debug("Building Google Calendar API...")

        self.service = build("calendar", "v3", credentials=self.credentials)

    # ----- List specific number of events ---------------------------------
    def get_numberof_events(self, max_results: int = 10) -> List[Dict]:
        """
        Retrieves a number of events (default: 10) from all Google Calendars
        defined in the configuration under google.calendars.

        Returns:
            list[dict]: Combined list of events with calendar metadata.
        """

        logger.debug("Fetching calendar list from configuration...")

        retrieved_events = []

        for calendar in self.calendars:
            calendar_id = calendar.get("id")
            calendar_role = calendar.get("role", "unknown")
            calendar_name = calendar.get("name", "unknown")

            if not calendar_id:
                logger.warning(f"Skipping calendar with missing ID: {calendar_name}")
                continue

            try:
                logger.debug(
                    f"Fetching up to {max_results} events from calendar '{calendar_name}'"
                    f"(role: {calendar_role})"
                )

                fetched = (
                    self.service.events()
                    .list(
                        calendarId=calendar_id,
                        maxResults=max_results,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )

                events = fetched.get("items", [])

                # Add metadata to each event
                for event in events:
                    event["_calendar_name"] = calendar_name
                    event["_calendar_id"] = calendar_id
                    event["_calendar_role"] = calendar_role

                retrieved_events.extend(events)

            except Exception as e:
                logger.error(f"Failed to fetch events from {calendar_name}: {e}")

        return self._sort_events_by_date(retrieved_events)

    # ----- List this week's events ----------------------------------------
    def get_thisweek_events(self) -> List[Dict]:
        """
        Retrieve all events from the current week across all calendars
        defined in google.calendars from the configuration.

        Returns:
            list[dict]: Combined list of all events from the current week.
        """

        logger.debug("Fetching this week's events...")

        # Get ISO 8601 start and end of the current week
        week_start_str, week_end_str = get_current_week()

        logger.debug(f"Week boundaries → start: {week_start_str} | end: {week_end_str}")

        retrieved_events = []

        for calendar in self.calendars:
            calendar_id = calendar.get("id")
            calendar_role = calendar.get("role", "unknown")
            calendar_name = calendar.get("name", "unknown")

            if not calendar_id:
                logger.warning(f"Skipping calendar with missing ID: {calendar_name}")
                continue

            try:
                logger.debug(
                    f"Fetching weekly events from calendar '{calendar_name}' "
                    f"(role: {calendar_role})"
                )

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

                # Metadata injection
                for event in events:
                    event["_calendar_id"] = calendar_id
                    event["_calendar_role"] = calendar_role
                    event["_calendar_name"] = calendar_name

                retrieved_events.extend(events)

            except Exception as e:
                logger.error(f"Failed to process calendar '{calendar_name}': {e}")

        return self._sort_events_by_date(retrieved_events)

    # ----- Build event table ----------------------------------------------
    @staticmethod
    def events_totable(events: list[dict]) -> str:
        """Formats a list of Google calendar events in a formatted table.

        Args:
            events (list[dict]): A list of Google calendar events.

        Returns:
            str: formatted tabulate string table with all Google Calendar events
        """
        events_data = []

        if not events:
            logger.warning("No events found")
            return

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

            events_data.append([title, start_fmt, end_fmt])

        events_headers = ["Title", "Start time", "End Time"]

        return generate_datatable(events_data, events_headers)

    # ----- Sort Events ----------------------------------------------------
    @staticmethod
    def _sort_events_by_date(events: list[dict]) -> list[dict]:
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
