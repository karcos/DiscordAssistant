from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from typing import Any, Final, Literal, get_args

import os
import datetime as dt

class CalendarGoogleHandler:
    def __init__(self) -> None:
        self._SCOPES: Final[list[str]] = ['https://www.googleapis.com/auth/calendar']
        self._creds: Credentials | None = None
        self._get_credentials()

        self._service: Resource = build('calendar', 'v3', credentials=self._creds)

        self._CALENDAR: Final[dict[str, str]] = {
            'Praca': os.getenv('PRACA_ID'),
            'Korepetycje': os.getenv('KOREPETYCJE_ID'),
            'Prywatne': os.getenv('PRYWATNE_ID')
        }

        self._show_all_calendars()

    def _get_credentials(self) -> None:
        if os.path.exists('token.json'):
            self._creds = Credentials.from_authorized_user_file('token.json', self._SCOPES)

        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            else:
                flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file('credential.json',
                                                                                   self._SCOPES)
                self._creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(self._creds.to_json())

    def _show_all_calendars(self) -> None:
        calendars_result: dict[str, Any] = self._service.calendarList().list().execute()
        calendars: list[dict[str, Any]] = calendars_result.get('items', [])

        if not calendars:
            print("Nie znaleziono żadnych kalendarzy.")
        else:
            print("Dostępne kalendarze:")
            for calendar in calendars:
                print(f"Nazwa: {calendar['summary']}, ID: {calendar['id']}")

    def get_events(self,
                   calendar_name: Literal['Praca', 'Korepetycje', 'Prywatne'],
                   date: str | dt.datetime) -> list[dict[str, Any]]:

        now: str = dt.datetime.now(dt.timezone.utc).isoformat()  # ISO 8601
        events_result: dict[str, Any] = self._service.events().list(calendarId=self._CALENDAR[calendar_name],
                                                                    timeMin=now, maxResults=1,
                                                                    singleEvents=True, orderBy='startTime').execute()
        events: list[dict[str, Any]] = events_result.get('items', [])

        return events