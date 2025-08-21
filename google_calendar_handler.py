import datetime as dt
import os
import copy
from typing import Any, Final, Literal
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from consts import (GOOGLE_API_REQ_JSON_NEW_EVENT, GOOGLE_API_SCOPES, GOOGLE_API_TOKEN_PATH, GOOGLE_API_CREDS_PATH,
                    GOOGLE_API_REQ_JSON_IF_BUSY, WORKING_TIME_RANGE)
from datetime_range import DateTimeRange


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
        calendars_result: dict[str, Any] = self._service.calendarList().list().execute() # NOQA
        calendars: list[dict[str, Any]] = calendars_result.get('items', [])

        result: dict[str, str] = dict()
        for calendar in calendars:
            if calendar['accessRole'] == 'owner':
                result[calendar['summary']] = calendar['id']

        return result

    def get_date_next_event(self, now: dt.datetime, pupil_dc_id: int) -> Literal[False] | DateTimeRange:

        response: dict[str, Any] = self._service.events().list(calendarId=self._CALENDAR['Korepetycje'], # NOQA
                                                               timeMin=now.isoformat(),
                                                               maxResults=1,
                                                               singleEvents=True,
                                                               q=pupil_dc_id).execute()
        if event := response.get('items', []):
            return DateTimeRange(start=dt.datetime.fromisoformat(event[0]['start'].get('dateTime')),
                                 end=dt.datetime.fromisoformat(event[0]['end'].get('dateTime')))
        else:
            return False

    def check_availability(self, date: DateTimeRange) -> int:

        if date.start < dt.datetime.now(tz=ZoneInfo('Europe/Berlin')):
            return -1
        elif date.start.time() not in WORKING_TIME_RANGE or date.end.time() not in WORKING_TIME_RANGE:
            return -2

        start_date = date.start - dt.timedelta(minutes=31)
        end_date = date.end + dt.timedelta(minutes=31)

        req_template: dict[str, Any] = copy.deepcopy(GOOGLE_API_REQ_JSON_IF_BUSY)

        req_template['timeMin'] = start_date.isoformat()
        req_template['timeMax'] = end_date.isoformat()
        req_template['items'] = [{'id': cal_id} for _, cal_id in self._CALENDAR.items()]

        result: dict[str, Any] = self._service.freebusy().query(body=req_template).execute() # NOQA

        busy_dict: list[dict[str, str]] = [result['calendars'][cal_id]['busy'] for cal_id in self._CALENDAR.values()]

        return int(not any(busy_dict))

    def new_event(self, date: DateTimeRange, nick: str, user_id: int) -> None:

        json_query: dict[str, Any] = copy.deepcopy(GOOGLE_API_REQ_JSON_NEW_EVENT)

        json_query['summary'] = f'{nick} {user_id}'

        json_query['start']['dateTime'] = date.start.isoformat()
        json_query['end']['dateTime'] = date.end.isoformat()

        self._service.events().insert(calendarId=self._CALENDAR['Korepetycje'], body=json_query).execute() # NOQA

    def delete_event(self, date: dt.datetime, user_id: int) -> None:

        user_events = self._service.events().list(calendarId=self._CALENDAR['Korepetycje'], # NOQA
                                                  timeMin=date.isoformat(),
                                                  timeMax=date.replace(hour=WORKING_TIME_RANGE.end.hour,
                                                                       minute=WORKING_TIME_RANGE.end.minute).isoformat(),
                                                  q=user_id,
                                                  singleEvents=True,
                                                  orderBy="startTime",
                                                  pageToken=None,
                                                  maxResults=2500,
                                                  ).execute()

        for event in user_events['items']:
            print(event)
            self._service.events().delete(calendarId=self._CALENDAR['Korepetycje'], eventId=event['id'], sendUpdates=None).execute()





