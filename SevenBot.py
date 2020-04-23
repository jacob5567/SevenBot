# SevenBot.py

import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

client = discord.Client()


class CustomClient(discord.Client):

    async def on_ready(self):
        guild = discord.utils.get(self.guilds, name=GUILD)
        print(
            f'{self.user} is connected to the following guild:\n'
            f'{guild.name} (id: {guild.id})'
        )

client = CustomClient()
client.run(TOKEN)
