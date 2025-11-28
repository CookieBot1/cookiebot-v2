from resources.mrcookie import instance as bot
from discord.ext import commands
from resources.checks import is_admin, validate_user, lookup_database, new_database

@bot.command()
async def freezestreaks(ctx):
    try:
        if await is_admin(ctx.author.id) == False: raise Exception("You don't have permission to run this command.")

        guild_id = ctx.guild.id
        guild = ctx.bot.get_guild(guild_id)
        sender_id = ctx.author.id
        
        ## this block fetches user data from the database
        guild_data = await lookup_database(sender_id, guild_id)
        if guild_data == False:
            await new_database(sender_id, guild_id)
            guild_data = await lookup_database(sender_id, guild_id)

        for userID in guild_data["users"]:
            guild_data["users"][userID]["Cookies"]


        

    except Exception as Error:
        await ctx.send(Error)
