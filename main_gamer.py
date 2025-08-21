import calendar
from typing import Literal, Final

import discord as dc
from discord import app_commands
from assistant import Assistant
from google_calendar_handler import CalendarGoogleHandler
from dotenv import load_dotenv
from os import getenv
from datetime_range import DateTimeRange
from consts import TIME_ZONES, WORKING_TIME_RANGE
from zoneinfo import ZoneInfo

import datetime as dt

class MainGamer:
    def __init__(self) -> None:

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
        @app_commands.choices(
            minute=[
                app_commands.Choice(name="00", value=0),
                app_commands.Choice(name="30", value=30)
            ]
        )
        async def arrange_meeting(interaction: dc.Interaction,
                                  day: app_commands.Range[int, 1, 31],
                                  month: app_commands.Range[int, 1, 12],
                                  year: app_commands.Range[int, 2025, 2026],
                                  hour: app_commands.Range[int, 0, 23],
                                  minute: app_commands.Choice[int],
                                  duration: app_commands.Range[float, 1, 5],
                                  time_zone: str) -> None:

            if not (duration * 2).is_integer():
                await interaction.response.send_message('Podaj proszę czas trwania lekcji jako liczba pełna, lub z połówką, np 1, 1.5, 2, 2.5', # NOQA
                                                        ephemeral=True)
                return

            try:
                date: dt.datetime = dt.datetime(year, month, day, hour, minute.value)
            except ValueError as e:
                await interaction.response.send_message('Ten miesiąc nie ma tyle dni :face_with_raised_eyebrow:', # NOQA
                                                        ephemeral=True)
                return

            date: DateTimeRange = DateTimeRange(start=date.replace(tzinfo=ZoneInfo(time_zone)),
                                                end=date.replace(tzinfo=ZoneInfo(time_zone)) + dt.timedelta(hours=duration))

            availability: int = self._calendar.check_availability(date)

            if availability == 1:
                try:
                    self._calendar.new_event(date, interaction.user.display_name, interaction.user.id)
                    message = 'Udało się zapisać na zajęcia! :star_struck:'
                except Exception as e:
                    message = f'Wystąpił dziwny błąd {e.args}'

            elif availability == -2:
                message = f'Niestety nie pracuję w podanych godzinach :confounded: Pracuję od {WORKING_TIME_RANGE.start} do {WORKING_TIME_RANGE.end}'
            elif availability == -1:
                message = 'Czy ta data nie jest z przeszłości? :woozy_face:'
            elif availability == 0:
                message = 'Niestety mam już inne spotkanie o tej godzinie :disappointed:'
            else:
                raise ValueError(f'Function CalendarGoogleHandler()._check_availability() returns unexpected value: {availability}')

            await interaction.response.send_message(message, ephemeral=True) # NOQA

        @arrange_meeting.autocomplete('month_name')
        async def month_autocomplete(interaction: dc.Interaction, current: str) -> list[app_commands.Choice[str]]:

            return [
                app_commands.Choice(name=month_name, value=i)
                for i, month_name in enumerate(calendar.month_name[1:], start=1)
                if current.lower() in month_name.lower()
            ]

        @arrange_meeting.autocomplete('time_zone')
        async def time_zone_autocomplete(interaction: dc.Interaction, current: str) -> list[app_commands.Choice[str]]:

            return [
                app_commands.Choice(name=time_zone, value=time_zone)
                for time_zone in TIME_ZONES
                if current.lower() in time_zone.lower()
            ]

        @self._assistant.tree.command(name='usun',
                                      description='Usuń umówione spotkanie!')
        @app_commands.rename(day='dzień', month='miesiąc', year='rok')
        async def delete_event(interaction: dc.Interaction,
                               day: app_commands.Range[int, 1, 31],
                               month: app_commands.Range[int, 1, 12],
                               year: app_commands.Range[int, 2025, 2026]) -> None:

            try:
                date: dt.datetime = dt.datetime(year, month, day)
            except ValueError as e:
                await interaction.response.send_message('Ten miesiąc nie ma tyle dni :face_with_raised_eyebrow:', # NOQA
                                                        ephemeral=True)
                return
