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
        marriedStatus = userThing.get("Married")
        userProfileColor = userThing.get("ProfileColor")
        userProfileBio = userThing.get("Bio")

        userMarried = 0 if marriedStatus is None else int(marriedStatus)
        userRobCount = 0 if rob_count is None else int(rob_count)
        userRobGains = 0 if rob_gains is None else int(rob_gains)
        userProfileColor = 0x7289da if userProfileColor is None else int(userProfileColor)
        userProfileBio = "No bio set. Run ``.customize profile`` to set one!" if userProfileBio is None else str(userProfileBio)
        ## ------------------------------------------------------------

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

        badges_line = " ".join(badges) if badges else None

        ## build the embed
        stats_embed = discord.Embed(
            title = f"{member.display_name}'s Profile",
            color = userProfileColor,
        )

        default_opts = {"Cookies": True, "Streaks": True, "Counting": True, "Robbery": True, "Inventory": False}
        profile_opts = userThing.get("ProfileOptions") or {}
        # merge so new keys don't break old users
        profile_opts = {**default_opts, **profile_opts}

        def add_spacer():
            stats_embed.add_field(name="\u200b", value="\u200b", inline=True)

        def add_section(name: str, value: str):
            stats_embed.add_field(name=name, value=value, inline=True)

        sections = []

        if badges_line != None:
            stats_embed.set_author(name = badges_line)
        
        ## about section
        desc = ""

        ## MARRIED status section
        if userMarried != 0:
            try:
                partner = guild.get_member(int(userMarried)) or await guild.fetch_member(int(userMarried))
                desc += f"💍 **Married to:** {partner.mention}\n\n"
            except:
                desc += "💍 **Married to:** Unknown\n"
            cookieTitle = "🍪 Personal Cookies"
        else:
            cookieTitle = "🍪 Cookies"

        desc += f"**About:**\n{about}"
        stats_embed.description = desc

        if profile_opts.get("Cookies", True):
            rank_value = f"#{this_user.position}" if this_user else "Unranked"
            sections.append((cookieTitle, f"**{fmt_int(userCookies)}** Cookies\n**Rank** {rank_value}"))

        if profile_opts.get("Streaks", True):
            day_term = "Day" if int(userStreaks) == 1 else "Days"
            streak_value = f"**{fmt_int(userStreaks)}** {day_term}"
            if userDailyMultiplier and int(userDailyMultiplier) != 0:
                streak_value += f"\nMultiplier: x{userDailyMultiplier}"
            sections.append(("🔥 Streaks", streak_value))

        if profile_opts.get("Counting", True):
            sections.append(("🔢 Counting", f"**{fmt_int(userCounter)}** Counted\n**{fmt_int(userFailCounter)}** Fails\n**0** Saves"))

        if profile_opts.get("Robbery", True):
            sections.append(("💰 Robbery", f"**{fmt_int(userRobCount)}** Robberies\n**{fmt_int(userRobGains)}** Gains 🍪\n**{rob_pct}%** Chance"))

        # Render in 2-wide rows with a middle spacer column
        for i in range(0, len(sections), 2):
            left = sections[i]
            right = sections[i+1] if i + 1 < len(sections) else None

            add_section(left[0], left[1])
            add_spacer()
            if right:
                add_section(right[0], right[1])
            else:
                add_section("\u200b", "\u200b")

        stats_embed.set_thumbnail(url=member.display_avatar.url)
        
        await ctx.send(embed=stats_embed)
    
    except Exception as Error:
        await ctx.send(Error)