import discord as dc
from assistant import Assistant
from google_calendar_handler import CalendarGoogleHandler
from dotenv import load_dotenv
from os import getenv

class MainGamer:
    def __init__(self) -> None:
        calendar: CalendarGoogleHandler = CalendarGoogleHandler()
        self._assistant: Assistant = Assistant()
        self._prepare_commands()

        load_dotenv()
        self._assistant.run(getenv('DC_TOKEN'))

    def _prepare_commands(self) -> None:
        @self._assistant.tree.command(name="nowa", description="test")
        async def nowa(interaction: dc.Interaction):
            print("cos")

