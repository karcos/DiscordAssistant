from datetime import time
from typing import Final, Any
from datetime_range import DateTimeRange

GOOGLE_API_SCOPES: Final[list[str]] = ['https://www.googleapis.com/auth/calendar']
GOOGLE_API_TOKEN_PATH: Final[str] = 'token.json'
GOOGLE_API_CREDS_PATH: Final[str] = 'credential.json'
GOOGLE_API_REQ_JSON_NEW_EVENT: Final[dict[str, Any]] = {
    'summary': None,
    'location': None,
    'description': None,
    'start': {
        'dateTime': None,
        'timeZone': None
    },
    'end': {
        'dateTime': None,
        'timeZone': None,
    },
    'reminders': {
        'useDefault': True
    }
}
GOOGLE_API_REQ_JSON_IF_BUSY: Final[dict[str, Any]] = {
    'timeMin': None,
    'timeMax': None,
    'items': None
}

AVAILABLE_HOURS: Final[dict[int, DateTimeRange]] = {
    0: DateTimeRange(start=time(9), end=time(22)),
    1: DateTimeRange(start=time(9), end=time(22)),
    2: DateTimeRange(start=time(9), end=time(22)),
    3: DateTimeRange(start=time(9), end=time(22)),
    4: DateTimeRange(start=time(9), end=time(22)),
    5: DateTimeRange(start=time(9), end=time(22)),
    6: DateTimeRange(start=time(9), end=time(22))
}

TIME_ZONES: Final[tuple[str, ...]] = (
    'Pacific/Pago_Pago',
    'Pacific/Honolulu',
    'America/Anchorage',
    'America/Los_Angeles',
    'America/Denver',
    'America/Chicago',
    'America/New_York',
    'America/Puerto_Rico',
    'America/Sao_Paulo',
    'Atlantic/South_Georgia',
    'Atlantic/Azores',
    'UTC',
    'Europe/Berlin',
    'Africa/Johannesburg',
    'Europe/Moscow',
    'Asia/Dubai',
    'Asia/Karachi',
    'Asia/Dhaka',
    'Asia/Bangkok',
    'Asia/Shanghai',
    'Asia/Tokyo',
    'Australia/Brisbane',
    'Pacific/Guadalcanal',
    'Pacific/Tarawa',
)
