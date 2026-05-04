from resources.mrcookie import instance as bot
from resources.checks import update_counter, lookup_counter
import discord

@bot.command(aliases = ["information"])
async def info(ctx):
    await ctx.send("WIP")