from resources.mrcookie import instance as bot
import discord

from resources.checks import lookup_database, new_database

@bot.command(aliases = ["bal", "balance"])
async def stats(ctx, userID = '0'):
    try:
        ## if another user was mentioned, check if they're legit, else use sender ID
        if userID == '0':
            userID = str(ctx.author.id)
        else:
            userID = userID.strip("<@!>")
            if userID.isdigit() == False or len(userID) < 17 or ctx.guild.get_member(int(userID)) is None:
                raise Exception("Invalid user or not in the guild.")
        
        ## set vars
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)
        user = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))
        
        ## this block fetches their data from the database
        userData = await lookup_database(userID, guildID) 
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        userStreaks = userData["users"][userID]["Streaks"]
        userCookies = userData["users"][userID]["Cookies"]
        userDailyMultiplier = userData["users"][userID]["DailyMultiplier"]

        ## send the embed
        stats_embed = discord.Embed(
            title = str(user.display_name) + "'s Cookie Stats",
            color = 0x7289da,
            )
    
        stats_embed.add_field(name = "Cookies", value = userCookies, inline = True)
        if userStreaks == 1:
            dayTerm = "Day"
        else:
            dayTerm = "Days"
        stats_embed.add_field(name = "Streaks", value = str(userStreaks) + " " + dayTerm, inline = True)
        if userDailyMultiplier != 0:
            stats_embed.add_field(name = "Daily Multiplier", value = str(userDailyMultiplier) + " Cookie Multiplier Active!", inline = False)
        stats_embed.add_field(name = "Inventory", value = "WIP", inline = False)

        stats_embed.set_thumbnail(url = user.display_avatar)
        await ctx.send(embed=stats_embed)
    
    except Exception as Error:
        await ctx.send(Error)