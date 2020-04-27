# SevenBot.py

import os
import io
import random
import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
RANDOM_CHANNEL = os.getenv("RANDOM_CHANNEL")
RANDOM_TEXT = os.getenv("RANDOM_TEXT")
RANDOM_TOPICS = ["What hobbies have you been working on lately?",
                 "Send your favorite meme!", "Send a selfie!", "Share a picture of a pet/other animal!"]
random_message = None


async def sendMessage(channel_id, message_body):
    channel = await bot.fetch_channel(channel_id)
    await channel.send(message_body)


async def sendRandomThemeMessage():
    global random_message
    channel = await bot.fetch_channel(RANDOM_CHANNEL)
    await channel.send(RANDOM_TEXT + " *" + (random.choice(RANDOM_TOPICS) if random_message == None else random_message) + "*")
    random_message = None

bot = commands.Bot(command_prefix='!')
scheduler = AsyncIOScheduler()


@bot.event
async def on_ready():
    await refresh_scheduled_messages()

    scheduler.start()

    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )


@bot.command(name="setsundaytheme", help="Sets the theme for Random-Theme Sunday!")
@commands.has_role("Bot Admin")
async def set_sunday_theme(ctx, *, arg):
    global random_message
    if random_message != None:
        await ctx.send("The theme for this Sunday has already been set! Use `!changesundaytheme` to override!")
    else:
        random_message = arg
        await ctx.send("This Sunday's theme has been set to: `" + arg + "`")


@bot.command(name="sundaytheme", help="Replies with the theme for Random-Theme Sunday!")
@commands.has_role("Bot Admin")
async def get_sunday_theme(ctx):
    global random_message
    if random_message != None:
        await ctx.send("This Sunday's theme will be: `" + random_message + "`")
    else:
        await ctx.send("This Sunday's theme has not been set! Use `!setsundaytheme` to set it!")


@bot.command(name="changesundaytheme", help="Changes the theme for Random-Theme Sunday!")
@commands.has_role("Bot Admin")
async def change_sunday_theme(ctx, *, arg):
    global random_message
    if random_message == None:
        await ctx.send("The theme for this Sunday not yet been set! Use `!setsundaytheme` to set it!")
    else:
        temp = random_message
        random_message = arg
        await ctx.send("This Sunday's theme has been changed from `" + temp + "` to `" + arg + "`.")


@bot.command(name="refresh", help="Refreshes all scheduled messages")
@commands.has_role("Bot Admin")
async def refresh(ctx):
    await refresh_scheduled_messages()
    await ctx.send("Schedule log refreshed!")


@bot.command(name="listschedule", help="Lists all scheduled messages")
@commands.has_role("Bot Admin")
async def listschedule(ctx):
    f = io.StringIO()
    scheduler.print_jobs(out=f)
    f.seek(0)
    await ctx.send(f.read())
    f.close()


async def refresh_scheduled_messages():
    scheduler.remove_all_jobs()
    f = open("messageinfo.json")
    message_info = json.load(f)

    for msg in message_info["scheduled_messages"]:
        scheduler.add_job(sendMessage, 'cron', args=[
                          msg["channel_id"], msg["message_body"]], day_of_week=msg["day_of_week"], hour=msg["hour"], minute=msg["minute"])

    f.close()
    scheduler.add_job(sendRandomThemeMessage, 'cron',
                      day_of_week="sun", hour=11)


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
