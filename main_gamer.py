import locale

import discord as dc
from assistant import Assistant
from google_calendar_handler import CalendarGoogleHandler
from dotenv import load_dotenv
from os import getenv
from datetime_range import DateTimeRange

import datetime as dt

class MainGamer:
    def __init__(self) -> None:
        locale.setlocale(locale.LC_TIME, 'Polish_Poland')

        self._calendar: CalendarGoogleHandler = CalendarGoogleHandler()
        self._assistant: Assistant = Assistant()
        self._prepare_commands()

        load_dotenv()
        self._assistant.run(getenv('DC_TOKEN'))

    def _prepare_commands(self) -> None:
        @self._assistant.tree.command(name='najblizsza', description='Pokaże Ci na kiedy jesteśmy umówieni na kolejne zajęcia')
        async def closest_lesson(interaction: dc.Interaction) -> None:
            closest: DateTimeRange = self._calendar.get_next_lesson(dt.datetime.now(dt.UTC), interaction.user.id)
            day_name: str = closest.start.strftime('%A')
            message: str = (f'Twoja najbliższa lekcja odbędzie się {closest.start.strftime('%d.%m.%Y')} ({day_name})'
                            f' od {closest.start.strftime('%H:%M')} do {closest.end.strftime('%H:%M')}')

            await interaction.response.send_message(message) # NOQA

