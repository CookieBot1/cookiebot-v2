from resources.mrcookie import instance as bot
import discord
from typing import Optional
from attrs import define, field

from resources.checks import lookup_database, new_database, validate_user, is_blacklisted
from resources.constants import JUNO_ID

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
        member = guild.get_member(int(userID)) or await guild.fetch_member(int(userID))
        
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
        rob_pct = int(round(float(userRobChances) * 10))


        ## THIS IS TEMPORARY SINCE OLD DB MIGHT HAVE NO RobCount/RobGains/Bio/ProfileColor, REMOVE LATER!!!!!!
        userThing = userData["users"].get(userID, {})

        rob_count = userThing.get("RobCount")
        rob_gains = userThing.get("RobGains")
        userProfileColor = userThing.get("ProfileColor")
        userProfileBio = userThing.get("Bio")

        userRobCount = 0 if rob_count is None else int(rob_count)
        userRobGains = 0 if rob_gains is None else int(rob_gains)
        userProfileColor = 0x7289da if userProfileColor is None else int(userProfileColor)
        userProfileBio = "This user has no bio set." if userProfileBio is None else str(userProfileBio)
        ## ------------------------------------------------------------

        default_opts = {"Cookies": True, "Streaks": True, "Counting": True, "Robbery": True, "Inventory": False}
        profile_opts = userThing.get("ProfileOptions") or {}
        # merge so new keys don't break old users
        profile_opts = {**default_opts, **profile_opts}

        show_cookies  = profile_opts.get("Cookies", True)
        show_streaks  = profile_opts.get("Streaks", True)
        show_counting = profile_opts.get("Counting", True)
        show_robbery  = profile_opts.get("Robbery", True)
        # show_inventory = profile_opts.get("Inventory", False)

        ## -------------------------------------------------------------

        def clamp(text: str, n: int = 140) -> str:
            text = (text or "").strip()
            if not text:
                return "No bio set yet. Use `.customize profile` ✏️"
            return text[:n] + ("…" if len(text) > n else "")

        def fmt_int(x) -> str:
            try:
                return f"{int(x):,}"
            except Exception:
                return str(x)

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

        about = clamp(userProfileBio, 160)
        badges = []

        # cookies badges
        '''if userCookies >= 1000:
            badges.append("💰 Cookie Wealthy")
        if userCookies >= 5000:
            badges.append("🏦 Cookie Monster")
        # streak badges
        if userStreaks >= 7:
            badges.append("🔥 Streaking")
        if userStreaks >= 30:
            badges.append("👑 Streak Legend")
        # counting badges
        if userCounter >= 500:
            badges.append("🔢 Counter Main")
        if userFailCounter == 0 and userCounter >= 50:
            badges.append("🧼 Clean Counter")
        # robbery badges
        if userRobCount >= 25:
            badges.append("🦹 Notorious")
        if userRobGains >= 100:
            badges.append("🍪 Heist Profits")'''
        if str(userID) == str(JUNO_ID):
            badges.append("💅")

        badges_line = " ".join(badges) if badges else None

        ## build the embed
        stats_embed = discord.Embed(
            title = f"{member.display_name}'s Profile",
            color = userProfileColor,
        )

        if badges_line != None:
            stats_embed.set_author(name = badges_line)
        # about section
        stats_embed.description = f"**About:**\n{about}"

        # cookie part
        rank_value = f"#{this_user.position}" if this_user else "Unranked"
        stats_embed.add_field(
            name="🍪 Cookies",
            value=f"**Cookies:** {userCookies}\n**Rank:** {rank_value}",
            inline=True
        )

        # spacer column
        stats_embed.add_field(name="\u200b", value="\u200b", inline=True)

        # streak part
        day_term = "Day" if int(userStreaks) == 1 else "Days"
        streak_line = f"**Daily:** {fmt_int(userStreaks)} {day_term}"
        if userDailyMultiplier and int(userDailyMultiplier) != 0:
            streak_line += f"\n**Multiplier:** x{userDailyMultiplier}"
        stats_embed.add_field(
            name="🔥 Streaks",
            value=f"**Daily:** {userStreaks} Day",
            inline=True
        )

        # counting part
        stats_embed.add_field(
            name="🔢 Counting",
            value=f"**Numbers:** {fmt_int(userCounter)}\n**Fails:** {fmt_int(userFailCounter)}\n**Saves:** WIP",
            inline=True
        )

        stats_embed.add_field(name="\u200b", value="\u200b", inline=True)

        # rob part
        stats_embed.add_field(
            name="🦹 Robbery",
            value=f"**Robberies:** {fmt_int(userRobCount)}\n**Gains:** {fmt_int(userRobGains)} 🍪\n**Chance:** {rob_pct}%",
            inline=True
        )

        stats_embed.set_thumbnail(url=member.display_avatar.url)
        
        await ctx.send(embed=stats_embed)
    
    except Exception as Error:
        await ctx.send(Error)