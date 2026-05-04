from resources.mrcookie import instance as bot
import discord
from datetime import datetime, timedelta, timezone

from resources.checks import lookup_database, new_database, update_database, lookup_bot_central
from resources.helpers import get_latest_active_alert

async def send_dev_alert(ctx, userData, userID):
    # respect per-guild subscription toggle
    u = userData["users"][userID]
    if not bool(u.get("DevAlerts", False)):
        return

    latest_alert = get_latest_active_alert()
    if not latest_alert:
        return

    current_id = latest_alert.get("date")
    state = u.get("AlertState", {})
    read_id = state.get("readId")
    ping_for = state.get("pingForId")
    ping_count = int(state.get("pingCount", 0))

    # if new alert, reset ping tracking
    if ping_for != current_id:
        ping_for = current_id
        ping_count = 0

    # If unread for this alert and under 2 reminders
    if read_id != current_id and ping_count < 2:
        await ctx.send("Hey, <@!" + str(ctx.author.id) + ">! There's a 🔔 **New Developer Alert!** Run `.alert` to view it.")
        ping_count += 1

    u["AlertState"] = {
        "readId": read_id,
        "pingForId": ping_for,
        "pingCount": ping_count
    }

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


        dbUser = userData["users"][userID]

        userCookies = dbUser.get("Cookies", 0)
        userStreaks = dbUser.get("Streaks", 0)
        userDailyMultiplier = dbUser.get("DailyMultiplier", 0)

        userMultExpire = dbUser.get("DailyMultExpire")
        if userMultExpire is None:
            userMultExpire = datetime.now() - timedelta(days=1)

        userDailyExpire = dbUser.get("DailyExpire")
        if userDailyExpire is None:
            userDailyExpire = datetime.now() - timedelta(days=1)
        

        ## this checks if they have a cooldown
        if datetime.now() < userDailyExpire:
            timer = int(userDailyExpire.timestamp())

            cooldown_embed = discord.Embed(
                description = "You can collect your cookies again " + "<t:" + str(timer) + ":R>",
                color = 0x992d22
            )
            cooldown_embed.set_footer(
                text = "Tomorrow at " + userDailyExpire.strftime("%I:%M %p")
            )   
            cooldown_embed.set_author(name = "Not yet " + str(user.display_name) + "!", icon_url = user.display_avatar)
            await ctx.send(embed=cooldown_embed)
            return

        ## calculate and give daily cookies
        BaseCookies = 15
        Multiplier = 0
        StreakCookies = int((userStreaks/14) * 1.5)

        if userDailyMultiplier > 0:
            if userMultExpire and userMultExpire >= datetime.now():
                Multiplier = userDailyMultiplier
            else:
                userDailyMultiplier = 0
        
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

        await send_dev_alert(ctx, userData, userID) ## check for dev alert and ping if unread

        ## update the database
        userData["users"][userID]["Cookies"] = userCookies
        userData["users"][userID]["Streaks"] = userStreaks
        userData["users"][userID]["DailyMultiplier"] = userDailyMultiplier
        userData["users"][userID]["DailyMultExpire"] = userMultExpire
        userData["users"][userID]["DailyExpire"] = userDailyExpire
        
        await update_database(userID, guildID, userData["users"][userID])
        
    except Exception as Error:
        await ctx.send(Error)