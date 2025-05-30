from resources.mrcookie import instance as bot
import discord

from resources.checks import lookup_database, new_database, update_database, is_blacklisted

@bot.command(aliases = ["steal"])
async def rob(ctx, userID = '0', amount = "0"):
    try:
        await ctx.send("WIP")

    except Exception as Error:
        await ctx.send(Error)