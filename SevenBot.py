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
time_zones = {}


@bot.event
async def on_ready():
    global time_zones
    await refresh_scheduled_messages()

    scheduler.start()

    if os.path.exists("zonesdict.json"):
        f = open("zonesdict.json", 'r')
        time_zones_loaded = json.load(f)
        time_zones = {bot.get_user(int(key)): pytz.timezone(
            value) for key, value in time_zones_loaded.items()}
        f.close()

    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )

######################
# SUNDAY THEME STUFF #
######################


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

###################
# TIME ZONE STUFF #
###################


async def process_time_zones(message):
    text = message.content
    date_regex = re.compile(r"(1[0-2]|[1-9])(:[0-5][0-9])? ?([paPA][mM])")
    if regex_results := date_regex.search(text):
        hour = regex_results[1]
        if regex_results[3].lower() == 'pm':
            if hour != '12':
                hour = str(int(hour) + 12)
        elif regex_results[3].lower() == 'am':
            if hour == '12':
                hour = '0'
        found_time = datetime.time(hour=int(hour), minute=int(
            regex_results[2][1:] if ':' in regex_results[0] else 0), tzinfo=time_zones.get(message.author, pytz.timezone(os.getenv("TZ"))))
        today = datetime.date.today()
        found_datetime = datetime.datetime(
            year=today.year, month=today.month, day=today.day, hour=found_time.hour, minute=found_time.minute)

        ouput_format = "%-I:%M%p"
        send_string = ""
        for tz in set(time_zones.values()):
            send_string += tz.zone + ": " + \
                found_datetime.astimezone(tz).strftime(ouput_format) + '\n'
        await message.channel.send(send_string)


@bot.command(name="settimezone", help="Set your personal time zone")
async def set_time_zone(ctx, user_zone):
    try:
        _ = pytz.timezone(user_zone)
    except:
        await ctx.send("`{}` is not a valid time zone".format(user_zone))
    else:
        time_zones[ctx.author] = pytz.timezone(user_zone)
        await ctx.send("{}'s time zone set to `{}`".format(ctx.author, user_zone))
        # write to file
        writeable_zones_dict = {
            key.id: value.zone for key, value in time_zones.items()}
        json_text = json.dumps(writeable_zones_dict)
        with open("zonesdict.json", 'w') as f:
            f.write(json_text)


@bot.command(name="timezones", help="List all time zones")
async def list_zones(ctx):
    await ctx.send("https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")


@bot.command(name="mytimezone", help="View your personal time zone")
async def user_time_zone(ctx):
    await ctx.send(time_zones[ctx.author])


@bot.command(name="listuserzones", help="List all the users and their time zones, if set")
async def list_user_zones(ctx):
    send_string = ""
    for key, value in time_zones.items():
        send_string += str(key.name)
        send_string += '#'
        send_string += str(key.discriminator)
        send_string += ': '
        send_string += str(value.zone)
        send_string += '\n'
    if(send_string):
        await ctx.send(send_string)


@bot.command(name="savezonesdict", help="Save all user zones to a json file")
@commands.has_role("Bot Admin")
async def save_zones(ctx):
    writeable_zones_dict = {
        key.id: value.zone for key, value in time_zones.items()}
    json_text = json.dumps(writeable_zones_dict)
    with open("zonesdict.json", 'w') as f:
        f.write(json_text)
    await ctx.send("Wrote JSON")

###############
# VERSE STUFF #
###############


@bot.command(name="verse", help="Responds with the selected Bible verse")
async def get_verse(ctx):
    await ctx.send("Not yet implemented.")

#########
# LINKS #
#########


@bot.command(name="repository", help="The code repository for this bot")
async def get_repo_link(ctx):
    await ctx.send("https://github.com/jacob5567/SevenBot")


@bot.command(name="musicmonday", help="Spotify playlist of Music Monday songs")
async def get_monday_playlist(ctx):
    await ctx.send("https://open.spotify.com/playlist/1N4lnBTUPDlsUhgnob2vxq?si=ZVWLYto5S8q6Y6Ex-1NyMw")

##############
# ON MESSAGE #
##############


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await process_time_zones(message)

    if "hello there" in message.content.lower():
        response = "General Kenobi!"
        await message.channel.send(response)

    await bot.process_commands(message)


bot.run(TOKEN)
