from resources.mrcookie import instance as bot
from resources.checks import lookup_counter, update_counter
import discord

@bot.listen()
async def on_message(message):
    counterData = await lookup_counter(message.guild.id)

    channelID = counterData["settings"]["counter"]["Channel"]
    channel = bot.get_channel(channelID)
    savedCounter = counterData["settings"]["counter"]["Counter"]
    lastUser = counterData["settings"]["counter"]["lastUser"]
    try:
        if channelID != 0:
            if message.content.isdigit():
                if message.channel.id == channelID:
                    if int(message.content) == savedCounter + 1:
                        if message.author.id != lastUser:
                            savedCounter = int(message.content)
                            lastUser = message.author.id
                            await update_counter(message.channel.id, "Counter", savedCounter)
                            await update_counter(message.channel.id, "lastUser", lastUser)
                            await message.reply("saved, keep counting!")
                        else:
                            raise ValueError("You failed, counter reset")
                    else:
                        raise ValueError("You failed, counter reset")
    except ValueError as Error:
        lastUser = 0
        savedCounter = 0
        await channel.send(Error)