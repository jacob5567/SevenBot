# SevenBot.py

import os
import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
CHANNEL = os.getenv("DISCORD_CHANNEL")


async def sendMessage(channel_id, message_body):
    channel = await bot.fetch_channel(channel_id)
    await channel.send(message_body)


# client = discord.Client()
bot = commands.Bot(command_prefix='!')
scheduler = AsyncIOScheduler()


@bot.event
async def on_ready():
    f = open("messageinfo.json")
    message_info = json.load(f)

    for msg in message_info["scheduled_messages"]:
        scheduler.add_job(sendMessage, 'cron', args=[
                          msg["channel_id"], msg["message_body"]], day_of_week=msg["day_of_week"], hour=msg["hour"], minute=msg["minute"])

    f.close()

    scheduler.start()

    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )

@bot.command(name="verse", help="Responds with the selected Bible verse")
async def get_verse(ctx):
    await ctx.send("Not yet implemented.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "hello there" in message.content.lower():
        response = "General Kenobi!"
        await message.channel.send(response)

    await bot.process_commands(message)


bot.run(TOKEN)
