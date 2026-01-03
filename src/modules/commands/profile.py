from resources.mrcookie import instance as bot
import discord
from typing import Optional
from attrs import define, field

from resources.checks import lookup_database, new_database, validate_user, is_blacklisted

@define()
class SimpleUser:
    uid: str
    cookies: int
    position: Optional[int] = field(default=0, kw_only=True)

    async def lb_output(self) -> str:
        user = bot.get_user(int(self.uid)) or await bot.fetch_user(int(self.uid))
        if user.global_name == None: lb_user = user.name
        else: lb_user = user.global_name

        return (
        f"**#{self.position}. {lb_user}**"
        f"\n{self.cookies} Cookie{'s' if self.cookies != 1 else ''}"
        )

@bot.command(aliases = ["whoami", "mystats"])
async def profile(ctx, userID = '0'):
    try:
        ## set vars
        guildID = ctx.guild.id
        guild = ctx.bot.get_guild(guildID)

        ## if another user was mentioned, check if they're legit, else use sender ID
        if userID != '0':
            userID = await validate_user(userID)
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
        userCounter = userData["users"][userID]["Counter"]
        userFailCounter = userData["users"][userID]["FailCounter"]
        userRobChances = userData["users"][userID]["RobChances"]

        ## THIS IS TEMPORARY SINCE OLD DB MIGHT HAVE NO RobCount/RobGains, REMOVE LATER!!!!!!
        user = userData["users"].get(userID, {})
        rob_count = user.get("RobCount")
        rob_gains = user.get("RobGains")

        if rob_count is None or rob_gains is None:
            userRobCount = 0
            userRobGains = 0
        else:
            userRobCount = rob_count
            userRobGains = rob_gains
        ## ------------------------------------------------------------

        ## get user ranking by cookies (from leaderboard)
        guild_users: dict = userData.get("users", {})
    
        simplified_users: list[SimpleUser] = [
            SimpleUser(uid, data["Cookies"]) for uid, data in guild_users.items()
        ]
        simplified_users.sort(key=(lambda x: x.cookies), reverse=True)

        this_user = None
        for n, su in enumerate(simplified_users):
            su.position = n + 1
            if su.uid == str(userID):
                this_user = su



        ## build the embed
        stats_embed = discord.Embed(
            title = str(user.display_name) + "'s Profile",
            description = "Bio coming soon!",
            color = 0x7289da,
            )
    
        stats_embed.add_field(name = "Cookies", value = userCookies, inline = True)
        if userStreaks == 1: dayTerm = "Day"
        else: dayTerm = "Days"
        stats_embed.add_field(name = "Streaks", value = str(userStreaks) + " " + dayTerm, inline = True)
        if userDailyMultiplier != 0:
            stats_embed.add_field(name = "Daily Multiplier", value = str(userDailyMultiplier) + " Cookie Multiplier Active!", inline = False)

        rank_value = this_user.position if this_user else "Unranked"
        stats_embed.add_field(name = "Rank", value = rank_value, inline = True)
        
        stats_embed.add_field(name = "Num's Counted", value = str(userCounter) + " Numbers", inline = True)
        stats_embed.add_field(name = "Count Fails", value = str(userFailCounter) + " Fails", inline = True)
        stats_embed.add_field(name = "Count Saves", value = "WIP", inline = True)

        stats_embed.add_field(name = "Rob Count", value = f"{userRobCount} Robber{'ies' if userRobCount != 1 else 'y'}", inline = True)
        stats_embed.add_field(name = "Rob Gains", value = f"{userRobGains} Cookie{'s' if userRobGains != 1 else ''}", inline = True)
        stats_embed.add_field(name = "Rob Chances", value = str((int(userRobChances)/10) * 100) + "%", inline = True)

        stats_embed.set_thumbnail(url = user.display_avatar)
        stats_embed.set_footer(text = "Customization coming soon!")
        
        await ctx.send(embed=stats_embed)
    
    except Exception as Error:
        await ctx.send(Error)