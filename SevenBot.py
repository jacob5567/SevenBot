# SevenBot.py

import os
import discord
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
CHANNEL = os.getenv("DISCORD_CHANNEL")


async def sendMessage(channel_id, message_body):
    await client.fetch_channel(channel_id).send(message_body)


client = discord.Client()
scheduler = AsyncIOScheduler()
scheduler.add_job(sendMessage, 'cron', day_of_week="mon", hour=10)


@client.event
async def on_ready():
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
