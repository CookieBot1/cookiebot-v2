from discord.ext import commands
from resources.mrcookie import instance as bot
from resources.checks import lookup_server, new_server

## this command ignores **ALL** commands
@bot.command(aliases = ["ignorechannel"])
async def ignore(ctx):
    try:
        guildID = ctx.guild.id

        serverData = await lookup_server(guildID)
        if serverData is False:
            new_server(guildID)
            serverData = await lookup_server(guildID)

        ignoredList = serverData["settings"]["server"]["IgnoredChannels"]

        



    except Exception as Error:
        await ctx.send(Error)