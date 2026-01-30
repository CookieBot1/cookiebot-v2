import discord
from discord.ext import commands

from resources.mrcookie import instance as bot
from resources.checks import lookup_server, new_server, update_server
from resources.constants import JUNO_ID

@bot.command(aliases = ["juno"])
async def diddy(ctx):
    try:
        guildID = ctx.guild.id

        if ctx.guild is None:
            return await ctx.message.reply(content="This commands only works in servers!", delete_after=5)
        await ctx.send("https://tenor.com/view/ill-be-missing-you-missing-you-p-diddy-puff-daddy-big-gif-22616397")

        

    except Exception as Error:
        await ctx.send(Error)