from os import getenv
from typing import Final, Any

GOOGLE_API_SCOPES: Final[list[str]] = ['https://www.googleapis.com/auth/calendar']
GOOGLE_API_TOKEN_PATH: Final[str] = 'token.json'
GOOGLE_API_CREDS_PATH: Final[str] = 'credential.json'
GOOGLE_API_REQ_JSON_NEW_EVENT: dict[str, Any] = {
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
GOOGLE_API_REQ_JSON_IF_BUSY: dict[str, Any] =  {
    "timeMin": None,
    "timeMax": None,
    "items": None
}
