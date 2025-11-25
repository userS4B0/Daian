from __future__ import annotations
import pathlib
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config.settings import GOOGLE_CREDENTIALS_PATH, GOOGLE_TOKEN_PATH

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GCalClient:
    """
    Cliente compacto para Google Calendar:
    - Autenticación OAuth2
    - Generación y uso de google_token.json
    - Crear y listar eventos
    """

    def __init__(self):
        self.creds_path = pathlib.Path(GOOGLE_CREDENTIALS_PATH)
        self.token_path = pathlib.Path(GOOGLE_TOKEN_PATH, "google_token.json")

        self.creds = None
        self.service = None

        self._authenticate()

    # -------------------------------------------------------
    # 🔐 Autenticación
    # -------------------------------------------------------
    def _authenticate(self):
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )

        if not self.creds or not self.creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.creds_path), SCOPES
            )
            self.creds = flow.run_local_server(port=0)

            # Guardar token renovado en la ruta deseada
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())

        self.service = build("calendar", "v3", credentials=self.creds)

    # -------------------------------------------------------
    # 📆 Listar eventos
    # -------------------------------------------------------
    def list_events(self, max_results=10):
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get("items", [])

    # -------------------------------------------------------
    # 📝 Crear evento
    # -------------------------------------------------------
    def create_event(
        self, summary: str, start_dt: datetime, end_dt: datetime, description: str = ""
    ):
        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "Europe/Madrid",
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "Europe/Madrid",
            },
        }

        created = (
            self.service.events().insert(calendarId="primary", body=event).execute()
        )

        return created
