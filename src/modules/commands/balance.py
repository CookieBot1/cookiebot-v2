from resources.mrcookie import instance as bot
import discord

from resources.checks import lookup_database, new_database, validate_user, is_blacklisted

@bot.command(aliases = ["bal", "wallet"])
async def balance(ctx, userID = '0'):
    try:
        ## set vars
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)

        ## if another user was mentioned, check if they're legit, else use sender ID
        if userID != '0':
            userID = await validate_user(userID, guild)
            if userID == None or guild.get_member(int(userID)) is None: raise Exception("Invalid user, try again!")
            if await is_blacklisted(userID): raise Exception("Can't show stats, user is blacklisted.")
        else:
            userID = ctx.author.id
        
        ## set vars
        user = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))
        
        ## this block fetches their data from the database
        userData = await lookup_database(userID, guildID) 
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        
        userID = str(userID)
        userStreaks = userData["users"][userID]["Streaks"]
        userCookies = userData["users"][userID]["Cookies"]
        userDailyMultiplier = userData["users"][userID]["DailyMultiplier"]

        ## send the embed
        stats_embed = discord.Embed(
            title = str(user.display_name) + "'s Cookie Balance",
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

        stats_embed.set_thumbnail(url = user.display_avatar)
        await ctx.send(embed=stats_embed)
    
    except Exception as Error:
        await ctx.send(Error)