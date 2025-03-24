import discord

class Assistant(discord.Client):
    def __init__(self) -> None:
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True  # NOQA

        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self) -> None:
        await self.tree.sync()
        print('Assistant is ready!')