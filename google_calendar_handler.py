from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from dotenv import load_dotenv

from typing import Any, Final, Literal

from httplib2 import parse_uri

from datetime_range import DateTimeRange

import os
import datetime as dt

class CalendarGoogleHandler:
    def __init__(self) -> None:
        self._SCOPES: Final[list[str]] = ['https://www.googleapis.com/auth/calendar']
        self._creds: Credentials | None = None
        self._get_credentials()

        self._service: Resource = build('calendar', 'v3', credentials=self._creds)

        self._CALENDAR: Final[dict[str, str]] = self._get_calendars_ids()

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

    def _get_calendars_ids(self) -> dict[str, str]:
        calendars_result: dict[str, Any] = self._service.calendarList().list().execute()
        calendars: list[dict[str, Any]] = calendars_result.get('items', [])

        result: dict[str, str] = dict()
        for calendar in calendars:
            if calendar['accessRole'] == 'owner':
                result[calendar['summary']] = calendar['id']

        return result

    # def get_events(self,
    #                calendar_name: Literal['Praca', 'Korepetycje', 'Prywatne'],
    #                date: str | dt.datetime) -> list[dict[str, Any]]:
    #
    #     now: str = dt.datetime.now(dt.timezone.utc).isoformat()  # ISO 8601
    #     events_result: dict[str, Any] = self._service.events().list(calendarId=self._CALENDAR[calendar_name],
    #                                                                 timeMin=now, maxResults=1,
    #                                                                 singleEvents=True, orderBy='startTime').execute()
    #     events: list[dict[str, Any]] = events_result.get('items', [])
    #
    #     return events

    def get_next_lesson(self, now: dt.datetime, pupil_dc_id: int) -> Literal[False] | DateTimeRange:
        response: dict[str, Any] = self._service.events().list(calendarId=self._CALENDAR['Korepetycje'],
                                                               timeMin=now.isoformat(),
                                                               maxResults=1,
                                                               singleEvents=True,
                                                               q=pupil_dc_id).execute()
        if event := response.get('items', []):
            return DateTimeRange(start=dt.datetime.fromisoformat(event[0]['start'].get('dateTime')),
                                 end=dt.datetime.fromisoformat(event[0]['end'].get('dateTime')))
        else:
            return False

    def check_availability(self, date: dt.datetime) -> Literal[True] | dt.datetime:
        pass
