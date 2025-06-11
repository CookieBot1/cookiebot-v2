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
    if channelID == 0:
        return  # Channel could not be found.
    channel = bot.get_channel(channelID) or await bot.fetch_channel(channelID)
    if not channel:
        return  # Channel could not be found.

    savedCounter = counterData["settings"]["counter"]["Counter"]  # last accepted number
    lastUser = counterData["settings"]["counter"]["lastUser"]  # user who sent last message
    guild = bot.get_guild(message.guild.id)
    user = guild.get_member(int(message.author.id)) or await guild.fetch_member(int(message.author.id))
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
                await message.add_reaction("✅")
            else:
                raise ValueError(user.mention + " FAILED AT **" + str(savedCounter) + "**!! You can't count two times in a row.")
        else:
            raise ValueError(user.mention + " FAILED AT **" + str(savedCounter) + "**!! You said the wrong number.")
    
    except ValueError as Error:
        await channel.send(str(Error))

        failedCount_embed = discord.Embed(
            title = "❌ Counter Reset",
            description = "Start counting back at **1** again. Want to save the count? You can buy saves with cookies in ``.shop``",
            color = 0x992d22
            )

        failedCount_embed.set_footer(text = 'Want to see a leaderboard of who failed the most? Run ".failboard"')
        await channel.send(embed=failedCount_embed)

        await update_counter(guild_id, "highScore", savedCounter)
        await update_counter(guild_id, "Counter", 0)
        await update_counter(guild_id, "lastUser", 0)
