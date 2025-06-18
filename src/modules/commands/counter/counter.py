import discord

from resources.checks import lookup_counter, update_counter, update_value, lookup_database, new_database
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

    guild = bot.get_guild(message.guild.id)
    userID = str(message.author.id)
    user = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))
    guildID = message.guild.id
    try:
        if message.channel.id != channelID or not message.content.isdigit():
            return

        ## setting vars
        savedCounter = counterData["settings"]["counter"]["Counter"]  # last accepted number
        lastUser = counterData["settings"]["counter"]["lastUser"]  # user who sent last message
        userData = await lookup_database(userID, guildID) 
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        userCounter = userData["users"][userID]["Counter"]
        userFailCounter = userData["users"][userID]["FailCounter"]

        if int(message.content) == savedCounter + 1:
            if userID != lastUser:
                savedCounter = int(message.content)
                userCounter += 1
                await update_counter(guildID, "Counter", savedCounter)
                await update_counter(guildID, "lastUser", userID)
                await update_value(userID, guildID, "Counter", userCounter)
                await message.add_reaction("✅")
            else:
                raise ValueError(user.mention + " FAILED AT **" + str(savedCounter) + "**!! You can't count two times in a row.")
        else:
            raise ValueError(user.mention + " FAILED AT **" + str(savedCounter) + "**!! You said the wrong number.")
    
    except ValueError as Error:
        userFailCounter += 1
        await update_value(userID, guildID, "FailCounter", userFailCounter)
        await channel.send(str(Error))

        failedCount_embed = discord.Embed(
            title = "❌ Counter Reset",
            description = "Start counting back at **1** again. Want to save the count? You can buy saves with cookies in ``.shop``",
            color = 0x992d22
            )

        failedCount_embed.set_footer(text = 'Want to see a leaderboard of who failed the most? Run ".failboard"')
        await channel.send(embed=failedCount_embed)

        await update_counter(guildID, "highScore", savedCounter)
        await update_counter(guildID, "Counter", 0)
        await update_counter(guildID, "lastUser", 0)
