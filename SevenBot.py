# SevenBot.py

import os
import io
import re
import random
import discord
import datetime
import pytz
from discord.ext import commands
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler


f = open("config.json", "r")
config = json.load(f)
f.close()
TOKEN = config["DISCORD_TOKEN"]
GUILD = config["DISCORD_GUILD"]
TZ = config["timeZone"]
SCHEDULING = config["features"]["scheduling"]
TZCONVERSION = config["features"]["timeZoneConversion"]
COMMAND_PREFIX = config["commandPrefix"]

bot = commands.Bot(command_prefix=COMMAND_PREFIX)
if SCHEDULING:
    scheduler = AsyncIOScheduler(timezone=TZ)
if TZCONVERSION:
    time_zones = {}


@bot.event
async def on_ready():
    global time_zones
    if SCHEDULING:
        await refresh_scheduled_messages()
        scheduler.start()

    if TZCONVERSION:
        if os.path.exists("zonesdict.json"):
            f = open("zonesdict.json", "r")
            time_zones_loaded = json.load(f)
            time_zones = {int(key): pytz.timezone(
                value) for key, value in time_zones_loaded.items()}
            f.close()

    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f"{bot.user} is connected to the following guild:\n"
        f"{guild.name} (id: {guild.id})"
    )


async def send_message(channel_id, message_body):
    channel = await bot.fetch_channel(channel_id)
    await channel.send(message_body)


##############
# SCHEDULING #
##############


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
        scheduler.add_job(send_message, "cron", args=[
            msg["channel_id"], msg["message_body"]], day_of_week=msg["day_of_week"], hour=msg["hour"], minute=msg["minute"])

    f.close()


###################
# TIME ZONE STUFF #
###################

async def process_time_zones(message):
    text = message.content
    date_regex = re.compile(r"(1[0-2]|[1-9])(:[0-5][0-9])? ?([paPA][mM])")
    if date_regex.search(text):
        regex_results = date_regex.search(text)
        hour = regex_results[1]
        if regex_results[3].lower() == "pm":
            if hour != "12":
                hour = str(int(hour) + 12)
        elif regex_results[3].lower() == "am":
            if hour == "12":
                hour = "0"
        today = datetime.date.today()
        found_datetime = datetime.datetime(
            year=today.year, month=today.month, day=today.day, hour=int(hour), minute=int(
                regex_results[2][1:] if ":" in regex_results[0] else 0))

        ouput_format = "%-I:%M%p"
        send_string = ""
        for tz in set(time_zones.values()):
            send_string += tz.zone + ": " + time_zones.get(message.author.id, pytz.timezone(
                TZ)).localize(found_datetime).astimezone(tz).strftime(ouput_format) + "\n"
        await message.channel.send(send_string)


@bot.command(name="settimezone", help="Set your personal time zone")
async def set_time_zone(ctx, user_zone):
    try:
        _ = pytz.timezone(user_zone)
    except:
        await ctx.send("`{}` is not a valid time zone".format(user_zone))
    else:
        time_zones[ctx.author.id] = pytz.timezone(user_zone)
        await ctx.send("{}'s time zone set to `{}`".format(ctx.author, user_zone))
        # write to file
        writeable_zones_dict = {
            str(key): value.zone for key, value in time_zones.items()}
        json_text = json.dumps(writeable_zones_dict)
        with open("zonesdict.json", "w") as f:
            f.write(json_text)


@bot.command(name="timezones", help="List all time zones")
async def list_zones(ctx):
    await ctx.send("<https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>")


@bot.command(name="mytimezone", help="View your personal time zone")
async def user_time_zone(ctx):
    await ctx.send(time_zones[ctx.author.id])


@bot.command(name="listuserzones", help="List all the users and their time zones, if set")
@commands.has_role("Bot Admin")
async def list_user_zones(ctx):
    send_string = ""
    for key, value in time_zones.items():
        send_string += str(bot.get_user(key))
        send_string += ": "
        send_string += str(value.zone)
        send_string += "\n"
    if send_string:
        await ctx.send(send_string)


@bot.command(name="savezonesdict", help="Save all user zones to a json file")
@commands.has_role("Bot Admin")
async def save_zones(ctx):
    writeable_zones_dict = {
        key: value.zone for key, value in time_zones.items()}
    json_text = json.dumps(writeable_zones_dict)
    with open("zonesdict.json", "w") as f:
        f.write(json_text)
    await ctx.send("Wrote JSON")

#########
# LINKS #
#########


@bot.command(name="repository", help="The code repository for this bot")
async def get_repo_link(ctx):
    await ctx.send("https://github.com/jacob5567/SevenBot")


##############
# ON MESSAGE #
##############


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if TZCONVERSION:
        await process_time_zones(message)

    if "scissors autumn" in message.content.lower():
        response = "https://cdn.discordapp.com/attachments/689717787890810880/742982616851939358/scissors_autumn.jpg"
        await message.channel.send(response)

    await bot.process_commands(message)

if not SCHEDULING:
    bot.remove_command("refresh")
    bot.remove_command("listschedule")
if not TZCONVERSION:
    bot.remove_command("settimezone")
    bot.remove_command("timezones")
    bot.remove_command("mytimezone")
    bot.remove_command("listuserzones")
    bot.remove_command("savezonesdict")

bot.run(TOKEN)
