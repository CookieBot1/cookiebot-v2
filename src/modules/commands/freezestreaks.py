from resources.mrcookie import instance as bot
from discord.ext import commands
from resources.checks import is_admin, lookup_old_database
from datetime import datetime, timedelta

@bot.command()
async def freezestreaks(ctx):
    try:
        if await is_admin(ctx.author.id) == False: raise Exception("You don't have permission to run this command.")

        guild_id = ctx.guild.id
        guild = ctx.bot.get_guild(guild_id)
        sender_id = ctx.author.id
        
        ## this block fetches user data from the database
        guild_data = await lookup_old_database(sender_id, guild_id)

        await ctx.send("Freezing all streaks... This may take a moment.")
        for userid in guild_data["users"]:
            if guild_data["users"][userid]["Streaks"] > 1:
                if datetime.now() < guild_data["users"][userid]["ExpTime"] or datetime.now() - guild_data["users"][userid]["ExpTime"] < timedelta(hours = 24):
                    await ctx.send("Found a user with an active streak")
                    user = guild.get_member(int(userid)) or await guild.fetch_member(int(userid))
                    if user.global_name == None: the_name = userid
                    else: the_name = user.global_name
                    await ctx.send("User is: " + the_name)     
        await ctx.send("Cycle finished.")

        

    except Exception as Error:
        await ctx.send(Error)
