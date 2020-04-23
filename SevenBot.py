# SevenBot.py

import os
import discord
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
# import datetime

load_dotenv()
os.environ['TZ'] = 'America/Los_Angeles'
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
# LOCAL_TIMEZONE = datetime.datetime.now(
#     datetime.timezone(datetime.timedelta(0))).astimezone().tzinfo
general = None

async def testMessage():
    await general.send("test")

client = discord.Client()
scheduler = BackgroundScheduler()
scheduler.add_job(testMessage, 'interval', seconds=10)


@client.event
async def on_ready():
    general = await client.fetch_channel("357933471382896642")
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
