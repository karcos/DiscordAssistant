import datetime as dt
import os
from typing import Any, Final, Literal

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from datetime_range import DateTimeRange
from consts import GOOGLE_API_SCOPES, GOOGLE_API_TOKEN_PATH, GOOGLE_API_CREDS_PATH, GOOGLE_API_REQ_JSON_IF_BUSY


class CalendarGoogleHandler:
    def __init__(self) -> None:
        self._SCOPES: Final[list[str]] = GOOGLE_API_SCOPES
        self._creds: Credentials | None = None
        self._get_credentials()

        self._service: Resource = build('calendar', 'v3', credentials=self._creds)

        self._CALENDAR: Final[dict[str, str]] = self._get_calendars_ids()

    def _get_credentials(self) -> None:
        if os.path.exists(GOOGLE_API_TOKEN_PATH):
            self._creds = Credentials.from_authorized_user_file(GOOGLE_API_TOKEN_PATH, self._SCOPES)

        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            else:
                flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(GOOGLE_API_CREDS_PATH,
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

    def get_date_next_event(self, now: dt.datetime, pupil_dc_id: int) -> Literal[False] | DateTimeRange:
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

    def check_availability(self, date: dt.datetime, end_date: dt.datetime) -> bool:
        req_template: dict[str, Any] = GOOGLE_API_REQ_JSON_IF_BUSY

        req_template['timeMin'] = date.isoformat()
        req_template['timeMax'] = end_date.isoformat()
        req_template['items'] = [{'id': id[1]} for id in self._get_calendars_ids().items()]

        result: dict[str, Any] = self._service.freebusy().query(body=req_template).execute()

        for id in self._get_calendars_ids().items():
            busy_times = result['calendars'][id]['busy']
            print(busy_times)

