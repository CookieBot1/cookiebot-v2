from discord.ext import commands
from resources.mrcookie import instance as bot
from resources.checks import lookup_server, new_server

## this command ignores **ALL** commands
@bot.command(aliases = ["disabledrops"])
async def ignoredrops(ctx):
    await ctx.send("hi")