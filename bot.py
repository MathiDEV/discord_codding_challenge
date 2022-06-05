import discord
from discord.ext import commands
from discord.ext import tasks
from evalc import cExercises
import json
import datetime

bot = commands.Bot("/")

guild = None
channel = None
exercise = None
checking = False

schedule = {}

submissions = []

with open("config.json", "r") as f:
    config = json.load(f)

with open(config["schedule"], "r") as f:
    schedule = json.load(f)


async def can_submit():
    today = await get_day()
    return not (schedule[today]["winner"] and schedule[today]["win_time"] + config["after_win"] * 60 < int(datetime.datetime.now().timestamp()))


async def check_submission():
    global checking
    global submissions
    global exercise
    if not exercise or checking or len(submissions) == 0:
        return
    checking = True
    subm = submissions[0]
    exercise.check_exercise(subm[1])
    today = await get_day()
    if exercise.status["passed"]:
        if (schedule[today]["winner"]):
            await channel.send(config["messages"]["winner_already"].format(mention="<@%s>" % subm[0]))
        else:
            await channel.send(config["messages"]["win"].format(mention="<@%s>" % subm[0], after_win=config["after_win"]))
            await set_winner(subm[0])
    else:
        await channel.send(config["messages"]["error"].format(mention="<@%s>" % subm[0], message=exercise.status["message"]))
    submissions.pop(0)
    if len(submissions) > 0:
        await check_submission()
    else:
        checking = False


async def start_game(file, send=False):
    global exercise
    exercise = cExercises()
    exercise.set_exercise(file)
    if send:
        await channel.send(config["messages"]["exercise"].format(badge=config["badges"][exercise.exercise["difficulty"]], title=exercise.exercise["title"], description=exercise.exercise["description"]))


async def get_day():
    now = datetime.datetime.today()
    today = now.strftime("%d/%m/%Y")
    if int(now.strftime("%H")) < config["hour"]:
        today = (now - datetime.timedelta(days=1)).strftime("%d/%m/%Y")
    return today


async def set_exercise():
    global schedule
    today = await get_day()
    if today not in schedule:
        return
    if not await can_submit():
        return
    if exercise and exercise.file == schedule[today]["file"]:
        return
    await start_game(schedule[today]["file"], not schedule[today]["announced"])
    with open(config["schedule"], "w") as f:
        schedule[today]["announced"] = True
        json.dump(schedule, f)


async def set_winner(id):
    global schedule
    today = await get_day()
    if schedule[today]["winner"]:
        return
    schedule[today]["winner"] = id
    schedule[today]["win_time"] = int(datetime.datetime.now().timestamp())
    with open(config["schedule"], "w") as f:
        json.dump(schedule, f)


@bot.event
async def on_ready():
    global guild, channel
    guild = bot.guilds[0]
    channel = guild.get_channel(config["channel"])
    hourly_check.start()
    check_if_stucked.start()
    print("Bot is ready")


@tasks.loop(seconds=10, count=None)
async def check_if_stucked():
    await check_submission()


@tasks.loop(minutes=10, count=None)
async def hourly_check():
    await set_exercise()


@bot.event
async def on_message(ctx):
    if not exercise:
        return
    today = await get_day()
    if today not in schedule:
        return
    if not await can_submit():
        return
    if ctx.channel.id == channel.id and ctx.author.id != 913715917526007809:
        if not ctx.content.startswith("```") or not ctx.content.endswith("```"):
            return
        for sub in submissions:
            if sub[0] == ctx.author.id:
                await ctx.channel.send(config["messages"]["wait"].format(mention="<@%s>" % sub[0]))
                return
        submissions.append(
            (ctx.author.id, ctx.content.strip("```c").strip("```").strip()))
        await check_submission()


bot.run(config["bot_token"])
