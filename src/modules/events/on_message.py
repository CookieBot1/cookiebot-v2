from resources.checks import is_blacklisted
from resources.mrcookie import instance as bot
import discord

from resources.checks import lookup_counter
from modules.commands.counter.counter import safe_eval_int


@bot.event
async def on_message(message):
    if message.author.bot or await is_blacklisted(message.author.id) == True:
        return
    await bot.process_commands(message)

@bot.listen()
async def on_message_delete(message: discord.Message):
    if message.guild is None:
        return

    # ignore bot messages
    if message.author and message.author.bot:
        return

    counterData = await lookup_counter(message.guild.id)
    if counterData is False:
        return

    channelID = counterData["settings"]["counter"].get("Channel", 0)
    if channelID == 0:
        return

    # only care about the counting channel
    if message.channel.id != channelID:
        return

    # if message content is missing (uncached), we can't know what it was
    if not message.content:
        return

    raw = message.content.strip()

    # check if it was a number
    parsed = int(raw) if raw.isdigit() else None

    # optionally allow math expressions
    allow_math = counterData["settings"]["counter"].get("AllowMath", False)
    if parsed is None and allow_math:
        parsed = safe_eval_int(raw)

    # if it wasn't a valid counting attempt, ignore
    if parsed is None:
        return

    # it WAS a counting attempt — warn users
    savedCounter = counterData["settings"]["counter"].get("Counter", 0)
    next_count = savedCounter + 1

    if message.author:
        who = message.author.mention
    else:
        who = "Someone"

    await message.channel.send(
        f"⚠️ {who} deleted a counting message!! Next count is **{next_count}**"
    )

