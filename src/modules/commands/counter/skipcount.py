from resources.mrcookie import instance as bot
from resources.checks import update_counter, lookup_counter
import discord

@bot.command(aliases = ["skip"])
async def skipcount(ctx):
    await ctx.send("WIP")