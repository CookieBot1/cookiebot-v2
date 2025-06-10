import discord

from resources.checks import lookup_counter, update_counter
from resources.mrcookie import instance as bot


@bot.listen()
async def on_message(message: discord.Message):
    if message.guild is None or message.author.bot:
        return

    counterData = await lookup_counter(message.guild.id)
    if counterData is False:
        return

    channelID = counterData["settings"]["counter"]["Channel"]
    channel = bot.get_channel(channelID) or await bot.fetch_channel(channelID)
    if not channel:
        return  # Channel could not be found.

    savedCounter = counterData["settings"]["counter"]["Counter"]  # last accepted number
    lastUser = counterData["settings"]["counter"]["lastUser"]  # user who sent last message
    guild_id = message.guild.id
    try:
        if message.channel.id != channelID or not message.content.isdigit():
            return

        if int(message.content) == savedCounter + 1:
            if message.author.id != lastUser:
                savedCounter = int(message.content)
                lastUser = message.author.id
                await update_counter(guild_id, "Counter", savedCounter)
                await update_counter(guild_id, "lastUser", lastUser)
                await message.reply("saved, keep counting!")
            else:
                raise ValueError("You failed, counter reset")
        else:
            raise ValueError("You failed, counter reset")
    except ValueError as Error:
        await update_counter(guild_id, "highScore", savedCounter)
        await update_counter(guild_id, "Counter", 0)
        await update_counter(guild_id, "lastUser", 0)

        await channel.send(str(Error))
