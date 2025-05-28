from datetime import time
from typing import Final, Any
from time_range import TimeRange

GOOGLE_API_SCOPES: Final[list[str]] = ['https://www.googleapis.com/auth/calendar']
GOOGLE_API_TOKEN_PATH: Final[str] = 'token.json'
GOOGLE_API_CREDS_PATH: Final[str] = 'credential.json'
GOOGLE_API_REQ_JSON_NEW_EVENT: Final[dict[str, Any]] = {
    'summary': None,
    'location': None,
    'description': None,
    'start': {
        'dateTime': None,
        'timeZone': 'Europe/Warsaw'
    },
    'end': {
        'dateTime': None,
        'timeZone': 'Europe/Warsaw',
    },
    'reminders': {
        'useDefault': True
    }
}
GOOGLE_API_REQ_JSON_IF_BUSY: Final[dict[str, Any]] = {
    "timeMin": None,
    "timeMax": None,
    "items": None
}

AVAILABLE_HOURS: Final[dict[int, TimeRange]] = {
    0: TimeRange(start=time(15), end=time(20)),
    1: TimeRange(start=time(15), end=time(20)),
    2: TimeRange(start=time(15), end=time(20)),
    3: TimeRange(start=time(15), end=time(20)),
    4: TimeRange(start=time(15), end=time(20)),
    5: TimeRange(start=time(10), end=time(20)),
    6: TimeRange(start=time(10), end=time(20))
}
