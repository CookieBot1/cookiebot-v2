from resources.mrcookie import instance as bot
import discord
from datetime import datetime, timedelta

from resources.checks import lookup_database, new_database, update_database

@bot.command()
async def daily(ctx):
    try:
        userID = str(ctx.author.id)
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)
        user = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))

        ## this block fetches user data from the database
        userData = await lookup_database(userID, guildID) 
        if userData == False:
            await new_database(userID, guildID)
            userData = await lookup_database(userID, guildID)
        userCookies = userData["users"][userID]["Cookies"]
        userStreaks = userData["users"][userID]["Streaks"]
        userDailyMultiplier = userData["users"][userID]["DailyMultiplier"]
        userMultExpire = userData["users"][userID]["DailyMultExpire"]
        userDailyExpire = userData["users"][userID]["DailyExpire"]

        ## this checks if they have a cooldown
        if datetime.now() < userDailyExpire:
            timer = int(userDailyExpire.timestamp())

            cooldown_embed = discord.Embed(
                description = "You can collect your cookies again " + "<t:" + str(timer) + ":R>",
                color = 0x992d22,
                timestamp = userDailyExpire
                )
            cooldown_embed.set_author(name = "Not yet " + str(user.display_name) + "!", icon_url = user.display_avatar)
            await ctx.send(embed=cooldown_embed)
            return
        
        ## calculate and give daily cookies
        BaseCookies = 15
        Multiplier = 0
        StreakCookies = int((userStreaks/14) * 1.5)
        if userDailyMultiplier > 0:
            if userMultExpire >= datetime.now(): Multiplier = userDailyMultiplier
            else: userDailyMultiplier = 0
        
        Temp = (BaseCookies + StreakCookies) * Multiplier
        TotalCookies = BaseCookies + StreakCookies + Temp
        userCookies += TotalCookies

        ## this block updates their streak and daily cooldown
        if datetime.now() > userDailyExpire + timedelta(hours = 24): ## reset cooldown if 24 hours past expiration
            userStreaks = 1
        else:
            userStreaks += 1
        
        userDailyExpire = datetime.now() + timedelta(hours = 23)

        ## send the final embed
        dailyembed = discord.Embed(
            description = "You have collected your daily ``" + str(TotalCookies) + "`` cookies!" + "\n" + 
            "You now have a streak of ``" + str(userStreaks) + "``.", 
            color = 0x2ecc71,
            timestamp = userDailyExpire
            )

        dailyembed.set_author(name = "Daily Cookies - " + str(user.display_name), icon_url = user.display_avatar)
        dailyembed.set_footer(text = "You can collect again in 23 hours.")
        await ctx.send(embed=dailyembed)

        ## update the database
        userData["users"][userID]["Cookies"] = userCookies
        userData["users"][userID]["Streaks"] = userStreaks
        userData["users"][userID]["DailyMultiplier"] = userDailyMultiplier
        userData["users"][userID]["DailyMultExpire"] = userMultExpire
        userData["users"][userID]["DailyExpire"] = userDailyExpire
        
        await update_database(userID, guildID, userData["users"][userID])
        
    except Exception as Error:
        await ctx.send(Error)