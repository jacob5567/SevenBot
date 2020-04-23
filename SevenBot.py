# SevenBot.py

import os
import discord
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
CHANNEL = os.getenv("DISCORD_CHANNEL")
general = None


async def testMessage():
    global general
    await general.send("test")


client = discord.Client()
scheduler = AsyncIOScheduler()
scheduler.add_job(testMessage, 'interval', seconds=10, id="testID")


@client.event
async def on_ready():
    global general
    general = await client.fetch_channel(CHANNEL)
    scheduler.start()

    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "hello there" in message.content.lower():
        response = "General Kenobi!"
        await message.channel.send(response)


client.run(TOKEN)
