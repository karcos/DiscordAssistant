import calendar
import locale
from typing import Literal, Final

import discord as dc
from discord import app_commands
from assistant import Assistant
from google_calendar_handler import CalendarGoogleHandler
from dotenv import load_dotenv
from os import getenv
from datetime_range import DateTimeRange
from consts import TIME_ZONES
from zoneinfo import ZoneInfo

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
        @self._assistant.tree.command(name='najblizsza',
                                      description='Pokażę Ci na kiedy jesteśmy umówieni na kolejne zajęcia')
        async def closest_lesson(interaction: dc.Interaction) -> None:
            closest: DateTimeRange | Literal[False] = self._calendar.get_date_next_event(dt.datetime.now(dt.UTC),
                                                                                         interaction.user.id)
            if closest:
                day_name: Final[str] = closest.start.strftime('%A')
                message: Final[str] = (f'Twoja najbliższa lekcja odbędzie się {closest.start.strftime('%d.%m.%Y')}'
                                f' ({day_name}) od {closest.start.strftime('%H:%M')}'
                                f' do {closest.end.strftime('%H:%M')}')

                await interaction.response.send_message(message, ephemeral=True) # NOQA
            else:
                await interaction.response.send_message('Nie mogę znaleźć jakiejkolwiek umówionej lekcji :sob:', # NOQA
                                                        ephemeral=True)

        @self._assistant.tree.command(name='umow',
                                      description='Umów spotkanie!')
        @app_commands.rename(day='dzień', month='miesiąc', year='rok', hour='godzina', minute='minuta',
                             duration='czas_trwania', time_zone='strefa_czasowa')
        async def arrange_meeting(interaction: dc.Interaction,
                                  day: app_commands.Range[int, 1, 31],
                                  month: app_commands.Range[int, 1, 12],
                                  year: app_commands.Range[int, 2025, 2026],
                                  hour: app_commands.Range[int, 0, 23],
                                  minute: app_commands.Range[int, 0, 59],
                                  duration: app_commands.Range[int, 1, 5],
                                  time_zone: str) -> None:

            try:
                date: dt.datetime = dt.datetime(year, month, day, hour, minute)
            except ValueError as e:
                await interaction.response.send_message('Ten miesiąc nie ma tyle dni :face_with_raised_eyebrow:', # NOQA
                                                        ephemeral=True)
                return

            availability: bool = self._calendar.check_availability(date.replace(tzinfo=ZoneInfo(time_zone)),
                                                                   date.replace(hour=date.hour + duration,
                                                                                tzinfo=ZoneInfo(time_zone)))

            if availability:
                pass # TODO: make sure that space between event are not-less than 30 mins and then make new event



        @arrange_meeting.autocomplete('month')
        async def month_autocomplete(interaction: dc.Interaction, current: str) -> list[app_commands.Choice[str]]:
            months: tuple[str, ...] = tuple(calendar.month_name[1:])

            return [
                app_commands.Choice(name=month, value=i)
                for i, month in enumerate(months, start=1)
                if current.lower() in month.lower()
            ]

        @arrange_meeting.autocomplete('time_zone')
        async def time_zone_autocomplete(interaction: dc.Interaction, current: str) -> list[app_commands.Choice[str]]:

            return [
                app_commands.Choice(name=time_zone, value=time_zone)
                for time_zone in TIME_ZONES
                if current.lower() in time_zone.lower()
            ]