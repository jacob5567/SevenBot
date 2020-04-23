# SevenBot.py

import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

client = discord.Client()


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "hello":
        response = "there!"
        await message.channel.send(response)

client.run(TOKEN)
